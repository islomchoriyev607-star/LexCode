"""Navigator rejimi: vaziyat → aniqlashtiruvchi savollar → tuman → yoʻllar → qadam-baqadam → muddatli eslatma → yopish.

Interfeys qoidasi: har xabarda bitta fikr, eng koʻpi 3-4 tugma. Bot bosim oʻtkazmaydi: qarorni fuqaro qiladi,
eslatmalar faqat qadam muddatiga qarab. Xarita — Yandex qidiruvi (tuman yoki joylashuv + idora turi).
"""
import asyncio
import html
import io
import json
import logging
import pathlib
import re
import time
from urllib.parse import quote

from aiogram import Bot, F, Router
from aiogram.enums import ChatAction, ChatType
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import (BufferedInputFile, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton,
                           LinkPreviewOptions, Message, ReplyKeyboardMarkup, ReplyKeyboardRemove)

from . import config, keys, llm, pipeline, render, search, store
from .i18n import law_name, t
from .script import convert as convert_script
from .textnorm import normalize

log = logging.getLogger('lexnav.nav')
router = Router()
NO_PREVIEW = LinkPreviewOptions(is_disabled=True)
RECHECK_DAYS = 3   # "hali javob yoʻq" desa — yana necha kundan soʻng soʻraladi
FOLLOWUP_DAYS = 7  # qonunda muddat topilmasa, idoraga ariza berilgandan keyingi eslatma (muddat sifatida koʻrsatilmaydi)


def esc(s) -> str:
    return html.escape(str(s or ''), quote=False)


def B(text: str, data: str = None, url: str = None) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=text, url=url) if url else InlineKeyboardButton(text=text, callback_data=data)


def map_url(case: dict, query: str) -> str:
    """Yandex xaritada qidiruv: joylashuv boʻlsa — uning atrofida, aks holda tuman nomi bilan."""
    # Tuman nomi soʻrovga qoʻshilmaydi: sinovda "Chilonzor tumani Mehnat inspeksiyasi" → "Hech narsa topilmadi".
    # Hudud ll (joylashuv) bilan beriladi; boʻlmasa Yandex telefon joylashuvidan foydalanadi.
    url = f'https://yandex.uz/maps/?text={quote(query)}'
    if case.get('lat') is not None and case.get('lon') is not None:
        url += f"&ll={case['lon']:.6f},{case['lat']:.6f}&z=14"
    return url



def route_url(case: dict, dest: str) -> str:
    """Idoraga borish. Bazada (sud / IIB / FHDYO) mos idora topilsa — uning koordinatasigacha jamoat transporti
    marshruti (rtt=mt). Aks holda — atrofdagi idoralar qidiruvi. Matn bilan rtext=~… ishlatilmaydi: sinovda
    "Mehnat inspeksiyasi" Fargʻonadagi "Mehnat mahallasi" deb topildi (12 soatlik yoʻl)."""
    o = find_office(case, dest)
    if o is None:
        return map_url(case, dest)
    frm = f"{case['lat']:.6f},{case['lon']:.6f}" if case.get('lat') is not None and case.get('lon') is not None else ''
    return f"https://yandex.uz/maps/?rtext={frm}~{o['lat']},{o['lon']}&rtt=mt"


# ---------- Idoralar bazasi (tools/build_offices.py: OpenStreetMap, Toshkent) ----------
_OFF_PATH = pathlib.Path(__file__).resolve().parent.parent / 'data' / 'offices.json'
OFFICES: list[dict] = json.loads(_OFF_PATH.read_text(encoding='utf-8')) if _OFF_PATH.exists() else []


def office_kind(idora: str) -> tuple[str, str] | None:
    """AI yozgan idora nomi → (tur, kichik tur). Bazada yoʻq turlar (hokimiyat, inspeksiya…) → None."""
    x = (idora or '').lower()
    if any(w in x for w in ('fhdyo', 'fhdyo', 'fuqarolik holati', 'загс', 'фҳдё', 'фхдё')):
        return 'fhdyo', ''
    if re.search(r'\bsud|суд', x):
        sub = ('fuqarolik' if 'fuqaro' in x or 'граждан' in x else 'jinoyat' if 'jinoy' in x or 'уголов' in x else
               'mamuriy' if 'muriy' in x or 'админ' in x else 'iqtisodiy' if 'iqtisod' in x or 'эконом' in x else '')
        return 'sud', sub
    if any(w in x for w in ('ichki ishlar', 'iib', 'iiv', 'militsiya', 'politsiya', 'профилакт', 'profilaktika', '102', 'милиц', 'ички ишлар')):
        return 'iib', 'tayanch' if any(w in x for w in ('profilaktika', 'inspektor', 'профилакт', 'mahalla')) else 'bolim'
    return None


def find_office(case: dict, idora: str) -> dict | None:
    """Eng yaqin mos idora: joylashuv boʻlsa — masofa boʻyicha, boʻlmasa — tuman nomi boʻyicha. Topilmasa None."""
    k = office_kind(idora)
    if not k or not OFFICES:
        return None
    pool = [o for o in OFFICES if o['tur'] == k[0]]
    if k[1]:
        pool = [o for o in pool if o['sub'] == k[1]] or pool
    if case.get('lat') is not None and case.get('lon') is not None:
        la, lo = case['lat'], case['lon']
        return min(pool, key=lambda o: (o['lat'] - la) ** 2 + ((o['lon'] - lo) * 0.75) ** 2)  # cos(41°) ≈ 0.75
    d = normalize(case.get('district') or '')
    if d:
        for o in pool:
            if o['tuman'] and normalize(o['tuman']).split()[0] in d:
                return o
    return None


def office_info(case: dict, idora: str) -> dict | None:
    o = find_office(case, idora)
    return {'nom': o['nom'], 'manzil': o['manzil'], 'tuman': o['tuman'], 'route_url': route_url(case, idora)} if o else None


# ---------- PDF ----------
FONT_DIRS = [pathlib.Path(r'C:\Windows\Fonts'), pathlib.Path('/usr/share/fonts/truetype/dejavu')]


def _font() -> tuple[str, str | None]:
    for d in FONT_DIRS:
        for reg, bold in (('times.ttf', 'timesbd.ttf'), ('arial.ttf', 'arialbd.ttf'), ('DejaVuSans.ttf', 'DejaVuSans-Bold.ttf')):
            if (d / reg).exists():
                return str(d / reg), str(d / bold) if (d / bold).exists() else None
    raise RuntimeError('PDF uchun shrift topilmadi')


# Qoʻlda toʻldiriladigan joylar: AI "[F.I.Sh.]" kabi belgi qoʻyadi → PDF da pastki chiziq + kichik izoh
_PH_RE = re.compile(r'\[([^\]\n]{1,40})\]')
_TITLE_RE = re.compile(r'^\s*(ariza|shikoyat|talabnoma|taklif|da\W?vo\s+arizasi|murojaat|заявление|жалоба|претензия|'
                       r'обращение|исковое\s+заявление)\s*[.:]?\s*$', re.I)
_DATE_RE = re.compile(r'sana|дата|date', re.I)
_SIGN_RE = re.compile(r'imzo|подпись|signature', re.I)
PT = 14            # Times New Roman 14
LH = 6.4           # qator balandligi, mm (≈1,3 interval)
INDENT = 12.5      # xatboshi chekinishi, mm


def _write_rich(par, pdf, line: str, blank: int, sc: str | None = None) -> None:
    """Qatorni yozadi: [belgi] oʻrniga pastki chiziq, yonida qavs ichida kichik izoh."""
    pos = 0
    for m in _PH_RE.finditer(line):
        par.write(convert_script(line[pos:m.start()], sc))
        label = m.group(1).strip()
        if _DATE_RE.search(label):
            par.write(convert_script('«____» ______________ 20___ y.', sc))
        else:
            par.write('_' * blank)
            if label.lower().rstrip('.') not in line[:m.start()].lower():  # "Imzo: ____" — izoh takrorlanmaydi
                pdf.set_font('Doc', size=9)
                par.write(f' ({convert_script(label, sc)})')
                pdf.set_font('Doc', size=PT)
        pos = m.end()
    par.write(convert_script(line[pos:], sc))


def make_pdf(text: str, sc: str | None = None) -> bytes:
    """Ariza matni → A4 PDF: Times New Roman 14, chegaralar chap 30 / oʻng 15 / yuqori-pastki 20 mm.
    Tuzilma: oʻngda "kimga/kimdan" bloki → markazda sarlavha → xatboshi bilan, eni boʻyicha tekislangan matn →
    sana va imzo. Shaxsiy maʼlumot joylari — qoʻlda toʻldirish uchun chiziq."""
    from fpdf import FPDF
    reg, bold = _font()
    pdf = FPDF(format='A4')
    pdf.set_margins(30, 20, 15)
    pdf.set_auto_page_break(True, 20)
    pdf.add_page()
    pdf.add_font('Doc', '', reg)
    pdf.add_font('Doc', 'B', bold or reg)
    pdf.set_font('Doc', size=PT)
    lines = [ln.strip() for ln in text.replace('\r', '').split('\n')]
    ti = next((i for i, ln in enumerate(lines) if _TITLE_RE.match(ln)), None)
    head, title, body = (lines[:ti], lines[ti], lines[ti + 1:]) if ti else ([], None, lines)
    if head:  # adresat bloki: sahifaning oʻng yarmida
        with pdf.text_columns(text_align='L', l_margin=105, r_margin=15, line_height=LH / (PT * 0.3528)) as cols:
            for ln in head:
                if ln:
                    with cols.paragraph() as par:
                        _write_rich(par, pdf, ln, 22, sc)
        pdf.ln(LH)
    if title:
        pdf.set_font('Doc', 'B', PT)
        pdf.cell(0, LH * 1.5, convert_script(title, sc).upper(), align='C', new_x='LMARGIN', new_y='NEXT')
        pdf.set_font('Doc', size=PT)
        pdf.ln(LH * 0.5)
    with pdf.text_columns(text_align='J', line_height=LH / (PT * 0.3528)) as cols:
        in_list = False
        for ln in body:
            if not ln:
                continue
            item = bool(re.match(r'^(\d+[.)]|[-–•])\s', ln))
            if re.match(r'^(ilova|приложени|attach)', ln, re.I):
                in_list = True
            # Sana, imzo, "Ilovalar:" va roʻyxat bandlari — chekinishsiz, chapga; oddiy xatboshi — chekinish + eni boʻyicha
            plain = item or in_list or len(_PH_RE.sub('', ln)) < 45
            gap = _SIGN_RE.search(ln) or _DATE_RE.search(ln) or re.match(r'^(ilova|приложени|attach)', ln, re.I)
            with cols.paragraph(text_align='L' if plain else 'J', first_line_indent=0 if plain else INDENT,
                                top_margin=LH * 0.6 if gap else 0) as par:
                _write_rich(par, pdf, ln, 30, sc)
    return bytes(pdf.output())


# ---------- Bosqichlar ----------
async def start_after_role(bot: Bot, uid: int, case_id: int, role: str, lang: str) -> None:
    """Rol tanlangach: aniqlashtiruvchi savollar (boʻlsa) → tuman."""
    case = store.nav_case(case_id, uid)
    await bot.send_chat_action(uid, ChatAction.TYPING)
    qs = await pipeline.clarify(case['text'], role, lang)
    store.nav_update(case_id, questions=qs, answers=[])
    if qs:
        await bot.send_message(uid, t(lang, 'CLARIFY_INTRO'))
        await ask_question(bot, uid, case_id, 0, lang)
    else:
        await ask_district(bot, uid, case_id, lang)


async def ask_question(bot: Bot, uid: int, case_id: int, i: int, lang: str) -> None:
    case = store.nav_case(case_id, uid)
    q = case['questions'][i]
    rows = [[B(o, f'qa:{case_id}:{i}:{k}')] for k, o in enumerate(q['opts'])]
    rows.append([B(t(lang, 'BTN_SKIP'), f'qa:{case_id}:{i}:s')])
    store.set_pending(uid, {'case': case_id, 'stage': 'clarify', 'i': i})
    hint = t(lang, 'TYPE_HINT' if q['opts'] else 'TYPE_ONLY')
    n = len(case['questions'])
    head = f'❔ <b>{i + 1}/{n}.</b> ' if n > 1 else '❔ '
    await bot.send_message(uid, f'{head}{esc(q["q"])}\n\n<i>{hint}</i>', reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))


async def record_answer(bot: Bot, uid: int, case_id: int, i: int, answer: str | None, lang: str) -> None:
    case = store.nav_case(case_id, uid)
    if case is None or i >= len(case['questions']):
        return
    answers = case['answers']
    if answer:
        answers.append({'q': case['questions'][i]['q'], 'a': answer[:500]})
    store.nav_update(case_id, answers=answers)
    if i + 1 < len(case['questions']):
        await ask_question(bot, uid, case_id, i + 1, lang)
    else:
        await ask_district(bot, uid, case_id, lang)


async def ask_district(bot: Bot, uid: int, case_id: int, lang: str) -> None:
    store.set_pending(uid, {'case': case_id, 'stage': 'district'})
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=t(lang, 'BTN_LOCATION'), request_location=True)],
                                       [KeyboardButton(text=t(lang, 'BTN_SKIP'))]], resize_keyboard=True, one_time_keyboard=True)
    await bot.send_message(uid, t(lang, 'DISTRICT_ASK'), reply_markup=kb)


# ---------- Umumiy mantiq (bot va Mini App bir xil ishlatadi) ----------
EXTRA_MARK = '\n\n[Aniqlashtirish]'


async def analyze_case(case_id: int, uid: int, lang: str) -> pipeline.Result:
    """Vaziyat + javoblar + tuman → tahlil va yoʻllar; natija bazaga yoziladi. Xatoda istisno (chaqiruvchi ushlaydi)."""
    case = store.nav_case(case_id, uid)
    # Qayta tahlilda javoblar ikki marta qoʻshilmasin: avvalgi qoʻshimcha qism belgidan keyin kesiladi
    base = case['text'].split(EXTRA_MARK)[0]
    extra = ''.join(f"\n{a['q']} — {a['a']}" for a in case['answers'])
    if case['district']:
        extra += f"\nJoylashuv: {case['district']}"
    full = base + (EXTRA_MARK + extra if extra else '')
    try:
        r = await pipeline.analyze(full, case['role'] or 'boshqa', lang)
    except Exception:
        store.set_status(case_id, 'awaiting_role')
        raise
    # Muddatlar faqat tekshiruvdan oʻtgan (AI tanlagan) moddalarga nisbatan tasdiqlanadi
    rts = pipeline.routes(r.answer, [a for a, _ in r.cited])
    store.save_analysis(case_id, r.level, pipeline.to_json(r), r.answer.get('ishonch'))
    # Yangi yoʻllar — eski tanlov (route/step) tashlanadi, aks holda indeks chegaradan chiqishi mumkin
    store.nav_update(case_id, text=full, routes=rts, status='routes', route=None, step=0, next_check=None)
    log.info('Navigator case %s [%s]: daraja=%s yoʻllar=%s manbalar=%s', case_id, lang, r.level,
             [x['nom'] for x in rts], [f'{a.abbr} {a.num}' for a, _ in r.cited])
    return r


def do_route(case: dict, i: int) -> bool:
    if not case['routes'] or not 0 <= i < len(case['routes']):
        return False
    store.nav_update(case['id'], route=i, step=0, status='nav', next_check=None)
    return True


def do_done(case: dict) -> dict:
    """Joriy qadam bajarildi. → {'kind': 'wait', 'days'} | {'kind': 'next'} | {'kind': 'route_done'} | {'kind': 'noop'}"""
    if case['route'] is None or case['status'] != 'nav':
        return {'kind': 'noop'}
    s = case['routes'][case['route']]['steps'][case['step']]
    # Idoraga ariza berilgan qadam: qonundagi muddat (tasdiqlangan) yoki oddiy eslatma (FOLLOWUP_DAYS) — keyin "javob keldimi?"
    days = s['kun'] or (FOLLOWUP_DAYS if (s['ariza'] and s['idora']) else None)
    if days:
        store.nav_update(case['id'], status='waiting', next_check=time.time() + days * config.DAY_SECONDS)
        return {'kind': 'wait', 'days': days}
    return _advance(case)


def _advance(case: dict) -> dict:
    nxt = case['step'] + 1
    if nxt < len(case['routes'][case['route']]['steps']):
        store.nav_update(case['id'], step=nxt, status='nav', next_check=None)
        return {'kind': 'next'}
    store.nav_update(case['id'], status='route_done', next_check=None)
    return {'kind': 'route_done'}


def do_result(case: dict, res: str) -> dict:
    """Natija: ok → yopiladi; wait → RECHECK_DAYS dan soʻng yana soʻraladi; no → keyingi qadam yoki boshqa yoʻl."""
    # Natija faqat kutish holatida qabul qilinadi: eski tugma yoki ikki marta bosish qadamni oʻtkazib yubormasin
    if case['status'] not in ('waiting', 'checking', 'route_done'):
        return {'kind': 'noop'}
    if res == 'ok':
        store.nav_update(case['id'], status='closed', next_check=None)
        return {'kind': 'closed'}
    if res == 'wait':
        store.nav_update(case['id'], status='waiting', next_check=time.time() + RECHECK_DAYS * config.DAY_SECONDS)
        return {'kind': 'wait', 'days': RECHECK_DAYS}
    if case['route'] is not None and case['step'] + 1 < len(case['routes'][case['route']]['steps']):
        store.nav_update(case['id'], step=case['step'] + 1, status='nav', next_check=None)
        return {'kind': 'next'}
    store.nav_update(case['id'], status='routes', next_check=None)
    return {'kind': 'exhausted'}


async def application_pdf(case_id: int, uid: int, lang: str) -> bytes:
    """Ariza matni (boʻlmasa AI bilan tayyorlanadi, modda tekshiruvidan oʻtadi) → PDF."""
    case = store.get_case(case_id, uid)
    app_text = case['application']
    if not app_text:
        data = json.loads(case['analysis'])
        cited = [(a, x.get('why', '')) for x in data.get('cited', []) if (a := search.get(x['abbr'], x['num']))]
        app_text = await pipeline.application(case['text'], case['role'] or 'boshqa', data.get('answer', {}), cited, lang)
        store.save_application(case_id, app_text)
    # Ariza foydalanuvchi yozuvida (kirill yoki yangi lotin); boshqa tilda — oʻzgarishsiz
    return await asyncio.to_thread(make_pdf, app_text, store.script(uid) if lang == 'uz' else None)


def state(case: dict, lang: str) -> dict:
    """Mini App uchun murojaat holati (faqat koʻrsatish uchun kerakli maydonlar)."""
    data = json.loads(case['analysis']) if case.get('analysis') else {}
    ans = data.get('answer', {})
    out = {'case_id': case['id'], 'status': case['status'], 'level': case.get('level') or 'muhim',
           'vaziyat': ans.get('vaziyat', ''),
           # Xavf: matndagi belgilar YOKI AI xavf darajasini bergan boʻlsa — 112/102/103 koʻrsatiladi
           'danger': pipeline.is_danger(case.get('text') or '') or case.get('level') == 'xavf',
           'routes': [{'nom': r['nom'], 'qisqa': r['qisqa'], 'n': len(r['steps'])} for r in case.get('routes') or []],
           'route': case.get('route'), 'step': case.get('step'),
           'lawyer_url': map_url(case, t(lang, 'LAWYER_QUERY')),
           'print_url': map_url(case, t(lang, 'PRINT_QUERY')),
           'lat': case.get('lat'), 'lon': case.get('lon'),
           'next_check': case.get('next_check')}
    cited = data.get('cited', [])
    out['details'] = {'huquqlar': ans.get('huquqlar', []), 'majburiyatlar': ans.get('majburiyatlar', []),
                      'dalillar': ans.get('dalillar', []), 'murojaat': [m for m in ans.get('murojaat', []) if isinstance(m, dict)],
                      'cited': [{'law': law_name(lang, x['abbr'], (a.law if (a := search.get(x['abbr'], x['num'])) else x['abbr'])),
                                 'num': x['num'], 'link': x.get('link', ''), 'why': x.get('why', '')} for x in cited]}
    out['district'] = case.get('district') or ''
    ri, rts = case.get('route'), case.get('routes') or []
    # Joriy qadam faqat yoʻl ustida boʻlganda (yoʻl tugab "routes" ga qaytilsa — qadam ekrani koʻrsatilmaydi)
    if ri is not None and 0 <= ri < len(rts) and case['status'] in ('nav', 'waiting', 'checking', 'route_done', 'closed'):
        rt = rts[ri]
        s = rt['steps'][min(case['step'] or 0, len(rt['steps']) - 1)]
        out['current'] = {**s, 'route_name': rt['nom'], 'n': len(rt['steps']), 'i': (case['step'] or 0) + 1,
                          'map_url': route_url(case, s['idora']) if s['idora'] else None, 'manba': manba_info(s, lang),
                      'office': office_info(case, s['idora']) if s['idora'] else None}
    return out


async def run_analysis(bot: Bot, uid: int, case_id: int, lang: str) -> None:
    store.set_pending(uid, None)
    # Belgisiz yuboriladi: ReplyKeyboardRemove bilan yuborilgan xabarni Telegram tahrirlashga ruxsat bermaydi
    status = await bot.send_message(uid, t(lang, 'ANALYZING'))
    await bot.send_chat_action(uid, ChatAction.TYPING)
    try:
        r = await analyze_case(case_id, uid, lang)
    except Exception as e:  # noqa: BLE001
        log.error('Navigator tahlil xatosi (case %s): %s', case_id, type(e).__name__)
        await _replace(bot, uid, status, t(lang, 'ERROR'))
        return
    rts = store.nav_case(case_id, uid)['routes']
    lead = [f'<b>{t(lang, "LEVELS").get(r.level, r.level)}</b>']
    if r.danger:
        lead.append(t(lang, 'EMERGENCY_SHORT'))
    if r.answer.get('vaziyat'):
        lead.append(esc(r.answer['vaziyat']))
    if rts:
        lead.append(t(lang, 'ROUTES_INTRO', n=len(rts)))
    else:
        lead.append(t(lang, 'NO_ROUTES'))
    await _replace(bot, uid, status, '\n\n'.join(lead), routes_kb(store.nav_case(case_id, uid), r.level, lang))


async def _replace(bot: Bot, uid: int, msg, text: str, kb=None) -> None:
    """Holat xabarini javob bilan almashtiradi; tahrirlab bo'lmasa — yangi xabar yuboradi."""
    try:
        await msg.edit_text(text, reply_markup=kb)
    except TelegramBadRequest:
        await bot.send_message(uid, text, reply_markup=kb)


def routes_kb(case: dict, level: str, lang: str) -> InlineKeyboardMarkup:
    rows = []
    for i, rt in enumerate(case['routes']):
        star = f' · {t(lang, "RECOMMENDED")}' if i == 0 else ''
        rows.append([B(f'{i + 1}. {rt["nom"]}{star}', f'rt:{case["id"]}:{i}')])
    rows.append([B(t(lang, 'BTN_DETAILS'), f'det:{case["id"]}'), B(t(lang, 'BTN_LAWYER'), url=map_url(case, t(lang, 'LAWYER_QUERY')))])
    if level in ('jiddiy', 'xavf'):
        rows.append([keys.escalate_kb(case['id'], lang)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def manba_info(s: dict, lang: str) -> dict | None:
    """Muddat manbasi: qonun nomi, modda raqami, lex.uz havolasi (routes() tasdiqlagan modda)."""
    m = s.get('manba')
    if not s.get('kun') or not isinstance(m, dict):
        return None
    a = search.get(m.get('abbr', ''), m.get('num', ''))
    return {'law': law_name(lang, m['abbr'], a.law if a else m['abbr']), 'num': m['num'], 'link': m.get('link') or (a.link if a else '')}


def _deadline_src(s: dict, lang: str) -> str:
    m = manba_info(s, lang)
    art = {'ru': 'ст. {n}', 'en': 'Art. {n}'}.get(lang, '{n}-modda').format(n=esc(m['num'])) if m else ''
    return f' — <a href="{html.escape(m["link"], quote=True)}">{esc(m["law"])}, {art}</a>' if m and m['link'] else ''


def step_view(case: dict, lang: str) -> tuple[str, InlineKeyboardMarkup]:
    rt = case['routes'][case['route']]
    s = rt['steps'][case['step']]
    lines = [t(lang, 'STEP_HEAD', route=esc(rt['nom']), i=case['step'] + 1, n=len(rt['steps'])), '', f'<b>{esc(s["nima"])}</b>']
    if s['idora']:
        o = find_office(case, s['idora'])
        where = f"{s['idora']} — {o['nom']}" + (f", {o['manzil']}" if o['manzil'] else '') if o else \
            s['idora'] + (f", {case['district']}" if case.get('district') else '')
        lines.append(t(lang, 'STEP_WHERE', x=esc(where)))
    if s['olib']:
        lines.append(t(lang, 'STEP_BRING', x=esc(', '.join(s['olib']))))
    if s['kun']:
        lines.append(t(lang, 'STEP_DEADLINE', n=s['kun']) + _deadline_src(s, lang))
    return '\n'.join(lines), step_kb(case)


def step_kb(case: dict, more: bool = False) -> InlineKeyboardMarkup:
    """Qadam tugmalari: koʻrinadigani — Bajardim, Ariza, Yana; qolganlari "Yana" ichida (element kam, yoʻl koʻp)."""
    lang, cid = store.lang(case['user_id']), case['id']
    s = case['routes'][case['route']]['steps'][case['step']]
    if more:
        rows = [[B(t(lang, 'BTN_MAP'), url=route_url(case, s['idora']))]] if s['idora'] else []
        rows += [[B(t(lang, 'BTN_PRINT'), url=map_url(case, t(lang, 'PRINT_QUERY')))]] if s['ariza'] else []
        rows += [[B(t(lang, 'BTN_ASK'), f'ask:{cid}')], [B(t(lang, 'BTN_ALT'), f'alt:{cid}')], [B(t(lang, 'BTN_LESS'), f'more:{cid}:0')]]
        return InlineKeyboardMarkup(inline_keyboard=rows)
    row2 = [B(t(lang, 'BTN_PDF'), f'pdf:{cid}')] if s['ariza'] else []
    row2.append(B(t(lang, 'BTN_MORE'), f'more:{cid}:1'))
    return InlineKeyboardMarkup(inline_keyboard=[[B(t(lang, 'BTN_DONE'), f'dn:{cid}')], row2])


@router.callback_query(F.data.startswith('more:'))
async def on_more(c: CallbackQuery) -> None:
    await c.answer()
    try:
        case_id, (flag,) = _cid(c)
    except ValueError:
        return
    case = store.nav_case(case_id, c.from_user.id)
    if case is None or case['route'] is None or case['status'] != 'nav':
        return
    try:
        await c.message.edit_reply_markup(reply_markup=step_kb(case, flag == '1'))
    except TelegramBadRequest:
        pass


@router.callback_query(F.data.startswith('soon:'))
async def on_soon(c: CallbackQuery) -> None:
    """Hali qoʻshilmagan xizmatlar (transport, chop etish, donat) — halol aytiladi."""
    key = {'route': 'SOON_ROUTE', 'print': 'SOON_PRINT', 'donate': 'SOON_DONATE'}.get(c.data.split(':', 1)[1], 'SOON_ROUTE')
    await c.answer(t(store.lang(c.from_user.id), key), show_alert=True)


async def send_step(bot: Bot, uid: int, case_id: int, lang: str, prefix: str = '') -> None:
    case = store.nav_case(case_id, uid)
    text, kb = step_view(case, lang)
    await bot.send_message(uid, (prefix + '\n\n' if prefix else '') + text, reply_markup=kb, link_preview_options=NO_PREVIEW)


def res_kb(case_id: int, lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [B(t(lang, 'BTN_RES_OK'), f'rs:{case_id}:ok')],
        [B(t(lang, 'BTN_RES_WAIT'), f'rs:{case_id}:wait'), B(t(lang, 'BTN_RES_NO'), f'rs:{case_id}:no')]])


async def advance(bot: Bot, uid: int, case: dict, lang: str, prefix_key: str = 'NEXT_STEP') -> None:
    if _advance(case)['kind'] == 'next':
        await send_step(bot, uid, case['id'], lang, t(lang, prefix_key))
    else:
        await bot.send_message(uid, t(lang, 'ROUTE_DONE'), reply_markup=res_kb(case['id'], lang))


# ---------- Handlerlar ----------
def _cid(c: CallbackQuery) -> tuple[int, list[str]]:
    parts = c.data.split(':')
    return int(parts[1]), parts[2:]


@router.callback_query(F.data.startswith('qa:'))
async def on_answer(c: CallbackQuery) -> None:
    await c.answer()
    uid, lang = c.from_user.id, store.lang(c.from_user.id)
    case_id, (i, k) = _cid(c)
    case = store.nav_case(case_id, uid)
    if case is None or int(i) >= len(case['questions']):
        return
    q = case['questions'][int(i)]
    ans = None if k == 's' else q['opts'][int(k)] if k.isdigit() and int(k) < len(q['opts']) else None
    try:
        await c.message.edit_text(f'❔ {esc(q["q"])}\n— <b>{esc(ans or t(lang, "BTN_SKIP"))}</b>')
    except Exception:  # noqa: BLE001
        pass
    await record_answer(c.bot, uid, case_id, int(i), ans, lang)


async def handle_pending(m: Message, pending: dict, lang: str) -> bool:
    """Navigator kutayotgan javob (matn yoki joylashuv). True — xabar shu yerda qayta ishlandi."""
    uid, case_id, stage = m.from_user.id, pending.get('case'), pending.get('stage')
    case = store.nav_case(case_id, uid) if case_id else None
    if case is None:
        store.set_pending(uid, None)
        return False
    if stage == 'clarify' and m.text:
        await record_answer(m.bot, uid, case_id, int(pending.get('i', 0)), m.text.strip(), lang)
        return True
    if stage == 'district' and (m.text or m.location):
        if m.location:
            store.nav_update(case_id, lat=m.location.latitude, lon=m.location.longitude)
        elif m.text.strip() != t(lang, 'BTN_SKIP'):
            store.nav_update(case_id, district=m.text.strip()[:80])
        await m.answer(t(lang, 'DISTRICT_OK'), reply_markup=ReplyKeyboardRemove())
        await run_analysis(m.bot, uid, case_id, lang)
        return True
    if stage == 'question' and m.text:
        store.set_pending(uid, None)
        await m.bot.send_chat_action(uid, ChatAction.TYPING)
        answer = await answer_question(case, m.text.strip(), lang)
        await m.answer(esc(answer) + f'\n\n<i>{t(lang, "DISCLAIMER")}</i>', link_preview_options=NO_PREVIEW,
                       reply_markup=InlineKeyboardMarkup(inline_keyboard=[[B(t(lang, 'BTN_BACK_STEP'), f'stp:{case_id}')]]))
        return True
    return False


QA_SYSTEM = ("Sen huquqiy yoʻl koʻrsatuvchisan. Fuqaroning shu murojaati boʻyicha savoliga 2-5 jumlada, oddiy tilda javob ber. "
             "Faqat berilgan moddalar va vaziyatga tayan; modda raqami, muddat yoki summani oʻylab topma. Hukm chiqarma. "
             "Fuqaro ohangiga moslash, tinchlantiruvchi boʻl. Kerak boʻlsa, yurist bilan maslahatlashishni taklif qil.")


async def answer_question(case: dict, question: str, lang: str) -> str:
    data = json.loads(case['analysis'] or '{}')
    arts = [a for x in data.get('cited', []) if (a := search.get(x['abbr'], x['num']))]
    ctx = '\n\n'.join(f'{a.law}, {a.title}\n{a.body[:700]}' for a in arts[:4])
    try:
        out = await llm.chat(QA_SYSTEM, f"JAVOB TILI: {pipeline.AI_LANG.get(lang)}\nVaziyat: {case['text'][:2500]}\n\nModdalar:\n{ctx}\n\nSavol: {question[:800]}",
                             model=config.MODEL_STRONG, max_tokens=600)
    except llm.LLMError:
        return t(lang, 'ERROR')
    return pipeline.clean_text(out, lang)[0]


@router.callback_query(F.data.startswith('rt:'))
async def on_route(c: CallbackQuery) -> None:
    await c.answer()
    uid, lang = c.from_user.id, store.lang(c.from_user.id)
    case_id, (i,) = _cid(c)
    case = store.nav_case(case_id, uid)
    if case is None or not case['routes'] or int(i) >= len(case['routes']):
        await c.bot.send_message(uid, t(lang, 'CASE_GONE'))
        return
    if do_route(case, int(i)):
        await send_step(c.bot, uid, case_id, lang)


@router.callback_query(F.data.startswith('stp:'))
async def on_step_again(c: CallbackQuery) -> None:
    await c.answer()
    uid = c.from_user.id
    case_id, _ = _cid(c)
    case = store.nav_case(case_id, uid)
    if case and case['route'] is not None:
        await send_step(c.bot, uid, case_id, store.lang(uid))


@router.callback_query(F.data.startswith('dn:'))
async def on_done(c: CallbackQuery) -> None:
    await c.answer()
    uid, lang = c.from_user.id, store.lang(c.from_user.id)
    case_id, _ = _cid(c)
    case = store.nav_case(case_id, uid)
    if case is None or case['route'] is None or case['status'] not in ('nav',):
        return
    try:
        await c.message.edit_reply_markup(reply_markup=None)  # bajarilgan qadam tugmalari qayta bosilmasin
    except Exception:  # noqa: BLE001
        pass
    r = do_done(case)
    if r['kind'] == 'wait':
        await c.bot.send_message(uid, t(lang, 'WAIT_SET', n=r['days']))
    elif r['kind'] == 'next':
        await send_step(c.bot, uid, case_id, lang, t(lang, 'NEXT_STEP'))
    elif r['kind'] == 'route_done':
        await c.bot.send_message(uid, t(lang, 'ROUTE_DONE'), reply_markup=res_kb(case_id, lang))


@router.callback_query(F.data.startswith('rs:'))
async def on_result(c: CallbackQuery) -> None:
    await c.answer()
    uid, lang = c.from_user.id, store.lang(c.from_user.id)
    case_id, (res,) = _cid(c)
    case = store.nav_case(case_id, uid)
    if case is None or case['status'] in ('closed',):
        return
    try:
        await c.message.edit_reply_markup(reply_markup=None)
    except Exception:  # noqa: BLE001
        pass
    r = do_result(case, res)
    if r['kind'] == 'closed':
        await c.bot.send_message(uid, t(lang, 'RES_OK'), reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[B(t(lang, 'BTN_NEW'), 'new')], [B(t(lang, 'BTN_DONATE'), 'soon:donate')]]))
    elif r['kind'] == 'wait':
        await c.bot.send_message(uid, t(lang, 'RES_WAIT', n=r['days']))
    elif r['kind'] == 'next':
        await send_step(c.bot, uid, case_id, lang, t(lang, 'RES_NO'))
    elif r['kind'] == 'exhausted':
        await c.bot.send_message(uid, t(lang, 'ROUTE_EXHAUSTED'), reply_markup=routes_kb(case, case['level'] or '', lang))


@router.callback_query(F.data.startswith('alt:'))
async def on_alt(c: CallbackQuery) -> None:
    await c.answer()
    uid, lang = c.from_user.id, store.lang(c.from_user.id)
    case_id, _ = _cid(c)
    case = store.nav_case(case_id, uid)
    if case and case['routes']:
        await c.bot.send_message(uid, t(lang, 'ROUTES_INTRO', n=len(case['routes'])), reply_markup=routes_kb(case, case['level'] or '', lang))


@router.callback_query(F.data.startswith('ask:'))
async def on_ask(c: CallbackQuery) -> None:
    await c.answer()
    uid, lang = c.from_user.id, store.lang(c.from_user.id)
    case_id, _ = _cid(c)
    if store.nav_case(case_id, uid):
        store.set_pending(uid, {'case': case_id, 'stage': 'question'})
        await c.bot.send_message(uid, t(lang, 'ASK_PROMPT'))


@router.callback_query(F.data.startswith('det:'))
async def on_details(c: CallbackQuery) -> None:
    await c.answer()
    uid, lang = c.from_user.id, store.lang(c.from_user.id)
    case_id, _ = _cid(c)
    case = store.nav_case(case_id, uid)
    if not case or not case['analysis']:
        return
    data = json.loads(case['analysis'])
    cited = [(a, x.get('why', '')) for x in data.get('cited', []) if (a := search.get(x['abbr'], x['num']))]
    r = pipeline.Result(level=case['level'] or 'muhim', danger=False, triage=data.get('triage', {}), answer=data.get('answer', {}),
                        articles=[a for a, _ in cited], cited=cited)
    await c.bot.send_message(uid, render.card(r, t(lang, 'ROLES').get(case['role'] or 'boshqa', ''), lang), link_preview_options=NO_PREVIEW,
                             reply_markup=InlineKeyboardMarkup(inline_keyboard=[[B(t(lang, 'BTN_PDF'), f'pdf:{case_id}')]]))


_pdf_busy: set[int] = set()


@router.callback_query(F.data.startswith('pdf:'))
async def on_pdf(c: CallbackQuery) -> None:
    await c.answer()
    uid, lang = c.from_user.id, store.lang(c.from_user.id)
    case_id, _ = _cid(c)
    await send_pdf(c.bot, uid, case_id, lang)


async def send_pdf(bot: Bot, uid: int, case_id: int, lang: str) -> bool:
    """Ariza PDF ini chatga yuboradi (bot tugmasi va Mini App uchun umumiy). False — murojaat topilmadi/band/xato."""
    case = store.get_case(case_id, uid)
    if case is None or not case['analysis'] or case_id in _pdf_busy:
        return False
    _pdf_busy.add(case_id)
    msg = None
    try:
        if not case['application']:
            msg = await bot.send_message(uid, t(lang, 'APP_WRITING'))
        await bot.send_chat_action(uid, ChatAction.UPLOAD_DOCUMENT)
        try:
            pdf = await application_pdf(case_id, uid, lang)
        except llm.LLMError:
            if msg:
                await msg.edit_text(t(lang, 'APP_FAILED'))
            return False
        if msg:
            await msg.delete()
        kb = InlineKeyboardMarkup(inline_keyboard=[[B(t(lang, 'BTN_PRINT'), url=map_url(case, t(lang, 'PRINT_QUERY')))]])
        await bot.send_document(uid, BufferedInputFile(pdf, filename=f'Ariza_{case_id}.pdf'), caption=t(lang, 'PDF_CAPTION', id=case_id),
                                reply_markup=kb)
        return True
    finally:
        _pdf_busy.discard(case_id)


async def watcher(bot: Bot) -> None:
    """Muddati kelgan qadamlar: "javob keldimi?" deb soʻraydi (har murojaat uchun bir marta, keyin foydalanuvchi javobiga qarab)."""
    while True:
        try:
            for row in store.due_checks(time.time()):
                try:  # bitta foydalanuvchidagi xato (masalan, botni bloklagan) qolganlarini toʻxtatmasin
                    case = store.nav_case(row['id'])
                    lang = store.lang(row['user_id'])
                    store.nav_update(row['id'], status='checking', next_check=None)
                    rts, ri = case['routes'], case['route']
                    rt = rts[ri]['nom'] if rts and ri is not None and 0 <= ri < len(rts) else '#' + str(row['id'])
                    await bot.send_message(row['user_id'], t(lang, 'CHECK', route=esc(rt)), reply_markup=res_kb(row['id'], lang))
                except Exception as e:  # noqa: BLE001
                    log.warning('Watcher: case %s — %s', row['id'], type(e).__name__)
        except Exception:  # noqa: BLE001 — kuzatuvchi toʻxtab qolmasin
            log.exception('Navigator watcher xatosi')
        await asyncio.sleep(20)
