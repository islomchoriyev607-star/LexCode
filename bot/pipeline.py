"""Tahlil zanjiri: xavf filtri → saralash (tez model) → qonun qidiruvi → javob (kuchli model) → modda tekshiruvi.

CLAUDE.md: modda faqat lex.db dan; har modda havola bilan; bot hukm chiqarmaydi; hayotga xavf → 102/103 birinchi.
"""
import json
import logging
import re
from dataclasses import dataclass, field

from . import config, llm, search
from .i18n import AI_LANG
from .i18n import t as i18n_t
from .textnorm import normalize

log = logging.getLogger('lexnav.pipeline')

# Hayotga xavf belgilari. Normallashtirilgan matnda qidiriladi (oʻ → o1, gʻ → g1, kirill → lotin);
# "o1?" — foydalanuvchi tutuq belgisiz yozsa ham ("oldiraman") topilsin. Sinov: tools/test_danger.py
DANGER = re.compile('|'.join([
    r'\bo1?ldir(aman|amiz|adi|ishadi|ishaman|ishmoqchi|moqchi|ib|di|gan)',
    r'\bo1?zimni\s+(o1?ldir|osib|osaman|kes|tashlay|yo1q qil)', r'\bo1?z\s+joni(ga|mga|dan)', r'\bosib\s+qo1?y',
    r'\bosaman\b', r'\bjonimga\s+qasd',
    r'\b(urdi|urayap|uryap|urib\s+(qo1?y|o1?ldir|tashl)|kaltakla|do1?ppos|tepdi|bo1?g1?(di|ayap|moqchi))',
    r'\bzo1?ravon', r'\bzo1?rla', r'\bpichoq', r'\bbolta\b', r'\bqurol(i|ini|im|ni|bilan)?\b', r'\bo1?q\s*uz',
    r'hushidan\s+ket', r'nafas\s+ol(a)?ma', r'\bqon\s+ket', r'\bzaharla(di|moqchi|sh)',
    r'\bbolam(ni)?\s+(olib\s+qoch|o1?g1?irla|yo1?qol)', r'\bgarovga\s+ol', r'\bodam\s+o1?g1?irla',
    r'\byong1in\s+(chiq|bo1?l|ket)', r'\bportla(di|yap|tib|moqchi)',
    r'\bhozir\s+(eshik(da|ni|im)|uyimga\s+kir|ortimdan|meni\s+(ur|kuzat))', r'\bkuzatib\s+yur',
    r'\b(ubyu|ubit|ubyot|byot|byet|noj(om)?|pomogit|izbiva|izbil|udaril)', r'\bmenya\s+bet\b|\bbet\s+menya\b',
]))

LEVELS = {'oddiy': '🟢 Oddiy', 'muhim': '🟡 Muhim', 'jiddiy': '🔴 Jiddiy', 'xavf': '🚨 Xavf'}

# Rol → birinchi o'rinda qidiriladigan qonunlar (boshqalari chiqarib tashlanmaydi)
ROLE_LAWS = {
    'talaba': ['MurQ', 'FK-2'],
    'xodim': ['MK'],
    'tadbirkor': ['FK-1', 'FK-2'],
    'xaridor': ['IHHQ', 'FK-2'],
    'boshqa': [],
}
ROLE_NAMES = {'talaba': 'talaba', 'xodim': 'xodim (ishchi)', 'tadbirkor': 'tadbirkor',
              'xaridor': 'xaridor (iste\'molchi)', 'boshqa': 'fuqaro'}

TRIAGE_SYSTEM = (
    "Sen O'zbekiston huquqi bo'yicha saralovchisan. Fuqaro vaziyatini o'qib, faqat JSON qaytar. "
    "Huquqiy xulosa chiqarma, modda raqami yozma."
)
TRIAGE_USER = """Fuqaro roli: {role}
Mavjud qonunlar (qisqa nom: nomi): {laws}

Vaziyat:
\"\"\"{text}\"\"\"

JSON:
{{"soha": "mehnat|iste'mol|jinoyat|ma'muriy|fuqarolik|oila|ta'lim|boshqa",
  "daraja": "oddiy|muhim|jiddiy|xavf",
  "mazmun": "vaziyat 1 jumlada, o'zbek lotin",
  "sorovlar": ["qonun matnida uchraydigan rasmiy yuridik atamalar bilan 3-5 ta qisqa qidiruv iborasi, o'zbek lotin (masalan: 'ish haqini to'lash muddati', 'haqorat qilish', 'firibgarlik')"],
  "qonunlar": ["eng tegishli 1-3 ta qisqa nom yuqoridagi ro'yxatdan"]}}
daraja: xavf = hayot/sog'liqqa hozir xavf bor; jiddiy = jinoyat belgisi yoki katta zarar, idoraga murojaat kerak; muhim = huquq buzilgan; oddiy = maslahat yetarli."""

ANSWER_SYSTEM = (
    "Sen 'Huquqiy Navigator' — O'zbekiston fuqarolariga davlat tashkilotlariga murojaat qilishda yo'l ko'rsatuvchisan. "
    "QAT'IY QOIDALAR: 1) Faqat berilgan moddalarga [A1], [A2]… tayan; ulardan tashqari modda, qonun yoki raqam yozma. "
    "2) Matnda modda raqamini yozma — faqat 'manba' maydonida A-id bilan ko'rsat. 3) Hukm chiqarma, aybdorni aniqlama, "
    "sud natijasini bashorat qilma; qonunda belgilangan oqibatni ayt. 4) Idora nomini aniq bilmasang, umumiy ayt "
    "va vaziyatga mosini tanla: mehnat masalasida — davlat mehnat inspeksiyasi yoki sud; jinoyat belgisi yoki tahdidda — "
    "ichki ishlar organlari (politsiya) yoki prokuratura; iste'mol masalasida — avval sotuvchiga yozma talab, so'ng "
    "iste'molchilar huquqlarini himoya qilish organi yoki sud; davlat idorasi javob bermasa — yuqori turuvchi organ yoki "
    "prokuratura. 5) Oddiy, tushunarli tilda yoz; fuqaroga hurmat bilan (siz / вы / you) murojaat qil. "
    "6) Muddat, summa yoki foizni FAQAT berilgan moddalar matnida aniq yozilgan bo'lsa ayt; aks holda 'qachon' maydoniga "
    "'imkon qadar tez' (shu tilda) yoz — muddatni o'ylab topma. "
    "7) Ohang: fuqaro qanday yozgan bo'lsa (rasmiy yoki samimiy), shunga moslash; tinchlantiruvchi, qo'llab-quvvatlovchi "
    "bo'l, qo'rqitma, bosim o'tkazma, qarorni fuqaroning o'ziga qoldir. "
    "8) Faqat JSON qaytar; JSON kalitlari o'zgarmaydi, qiymatlar esa so'ralgan tilda bo'ladi."
)
ANSWER_USER = """JAVOB TILI: {lang} — barcha matn qiymatlarini shu tilda yoz (idora nomlarini ham shu tilda).
Fuqaro roli: {role}. Soha: {soha}. Daraja: {daraja}.
Vaziyat:
\"\"\"{text}\"\"\"

Qonun moddalari (faqat shulardan foydalan):
{articles}

JSON:
{{"vaziyat": "vaziyatning huquqiy mazmuni, 1-2 jumla",
  "huquqlar": ["fuqaroning huquqi, har biri 1 jumla", "..."],
  "majburiyatlar": ["fuqaro nima qilishi yoki nima qilmasligi kerak", "..."],
  "murojaat": [{{"kimga": "idora", "qanday": "yozma ariza / onlayn / shaxsan", "qachon": "muddat yoki 'imkon qadar tez'"}}],
  "dalillar": ["qanday dalilni qanday saqlash kerak", "..."],
  "manbalar": [{{"id": "A1", "nima_uchun": "bu modda vaziyatga qanday tegishli, 1 jumla"}}],
  "ishonch": 0-100,
  "aniqlashtirish": ["javobni aniqlashtirish uchun fuqarodan so'raladigan savol (bo'lmasa bo'sh)"],
  "yollar": [{{"nom": "yo'l nomi, 2-5 so'z (masalan: Davlat mehnat inspeksiyasi orqali)",
              "qisqa": "nima uchun bu yo'l va uning afzalligi, 1 jumla",
              "qadamlar": [{{"nima": "fuqaro bajaradigan bitta aniq harakat, 1 jumla",
                            "idora": "borish kerak bo'lgan idora turi (xaritada qidirish uchun, masalan 'davlat mehnat inspeksiyasi'); idoraga bormasa bo'sh",
                            "olib_borish": ["kerakli hujjat"],
                            "muddat_kun": null,
                            "ariza": false}}]}}]}}
'manbalar' da faqat vaziyatga haqiqatan tegishli 2-5 ta modda bo'lsin.
'yollar': 2-3 ta muqobil yo'l, eng tavsiya qilingani birinchi; har yo'lda 2-5 ta qadam, birinchi qadam — eng oson ish.
'muddat_kun' — javob kutish muddati (kun); FAQAT berilgan moddalarda aniq yozilgan bo'lsa son, aks holda null.
'ariza': true — shu qadamda yozma ariza topshiriladi."""

CLARIFY_SYSTEM = (
    "Sen huquqiy yo'l ko'rsatuvchining suhbatdoshisan. Fuqaro vaziyatini o'qib, to'g'ri yo'l tanlash uchun YETISHMAYOTGAN "
    "ma'lumotni aniqlaysan. Vaziyatni to'liq o'rganish uchun 3-4 ta savol ber (vaziyat juda aniq bo'lsa ham kamida 2 ta), "
    "eng muhimidan boshlab. Mavzular: qachon bo'lgan va qancha vaqt davom etmoqda; kim bilan (tashkilot, shaxs); "
    "yozma hujjat yoki dalil bormi (shartnoma, chek, yozishma, guvoh); summa yoki zarar qancha; oldin qayerga murojaat qilingan "
    "va javob bo'ldimi. Matnda javobi bor narsani so'rama. Bir savolda bitta narsa so'ra, qisqa (12 so'zgacha). "
    "Fuqaroning ohangiga moslash (rasmiy yoki samimiy), xushmuomala bo'l, qo'rqitma. Har savolga 2-3 ta qisqa javob varianti ber "
    "(har biri 1-4 so'z); summa yoki sana so'ralsa — oraliqlar ber (masalan: \"1 mln gacha\", \"1-5 mln\", \"5 mln dan ko'p\"). "
    "Faqat JSON qaytar."
)
CLARIFY_USER = """TIL: {lang}. Fuqaro roli: {role}.
Vaziyat:
\"\"\"{text}\"\"\"
JSON: {{"savollar": [{{"savol": "...", "variantlar": ["...", "..."]}}]}}"""


async def clarify(text: str, role: str, lang: str = 'uz') -> list[dict]:
    """1-2 ta aniqlashtiruvchi savol (yoki boʻsh). Xatoda — boʻsh roʻyxat (oqim toʻxtamasin)."""
    try:
        out = await llm.chat(CLARIFY_SYSTEM, CLARIFY_USER.format(lang=AI_LANG.get(lang, AI_LANG['uz']), role=ROLE_NAMES.get(role, role),
                                                                 text=text[:4000]),
                             model=config.MODEL_FAST, json_mode=True, max_tokens=500)
        qs = llm.parse_json(out).get('savollar') or []
    except (llm.LLMError, ValueError):
        return []
    res = []
    for q in qs[:4]:
        if isinstance(q, dict) and isinstance(q.get('savol'), str) and q['savol'].strip():
            opts = [clean_text(o.strip()[:40], lang)[0] for o in as_list(q.get('variantlar')) if isinstance(o, str) and o.strip()][:3]
            res.append({'q': clean_text(q['savol'].strip()[:300], lang)[0], 'opts': opts})
    return res


# Muddatni moddalar matnidan tekshirish: raqam ("15 kun") yoki soʻz bilan ("oʻn besh kun", "bir oy") yozilgan boʻlishi kerak
_NUM_WORDS = {1: 'bir', 2: 'ikki', 3: 'uch', 5: 'besh', 7: 'yetti', 10: 'o1n', 14: 'o1n to1rt', 15: 'o1n besh', 20: 'yigirma',
              30: 'o1ttiz', 45: 'qirq besh', 60: 'oltmish', 90: 'to1qson'}
_MONTHS = {30: 'bir oy', 60: 'ikki oy', 90: 'uch oy'}
# Ariza yoziladigan qadam (AI belgilamasa ham) va xaritada maʼnosiz "idora" (ish beruvchi, sotuvchi)
_WRITE_RE = re.compile(r'(ariza|talabnoma|shikoyat|da\W?vo|заявлен|жалоб|претензи|\bиск|application|complaint|claim|demand letter)', re.I)
_NOT_PLACE_RE = re.compile(r'(ish\s*beruvchi|sotuvchi|kadrlar|работодат|продав|employer|seller|shop)', re.I)


def _deadline_src(days: int, arts: list[search.Article]) -> search.Article | None:
    """Muddat qaysi moddada yozilgan boʻlsa — oʻsha modda (manba sifatida koʻrsatiladi), aks holda None."""
    pats = [rf'\b{days}\s*(kun|kalendar|ish kuni)', rf'\b{days}\s*(дн|день|дня)']
    if days in _NUM_WORDS:  # "besh kun" ≠ "oʻn besh kun": oldida oʻnlik soʻz boʻlmasligi kerak
        pats.append(rf'(?<!o1n )(?<!yigirma )(?<!o1ttiz )(?<!qirq )\b{_NUM_WORDS[days]}\s+kun')
    if days in _MONTHS:
        pats.append(rf'\b{_MONTHS[days]}')
    for a in arts:
        body = normalize(a.body)
        if any(re.search(p, body) for p in pats):
            return a
    return None


def _deadline_ok(days: int, arts: list[search.Article]) -> bool:
    return _deadline_src(days, arts) is not None


# Erkin matndagi muddatlar ("15 kun ichida", "bir oy", "в течение 10 дней", "within 30 days"): manba moddada
# boʻlmasa "qonunda belgilangan muddatda" bilan almashtiriladi — AI oʻylab topgan muddat foydalanuvchiga yetmaydi.
_APO = "[ʻʼ'‘’`]?"
_WORDNUM = {w.replace('o1', 'o' + _APO).replace('to1', 'to' + _APO): n for n, w in _NUM_WORDS.items()}
_DUR_RE = re.compile(
    r'(?:\b(?:в\s+течение|within|in)\s+)?'
    r'\b(?P<n>\d{1,3}|' + '|'.join(sorted(_WORDNUM, key=len, reverse=True)) + r')\s*[-‑]?\s*'
    r'(?P<u>ish\s+kuni|kalendar\s+kun|kun|oy|hafta|рабочих\s+дн\w*|дн\w*|день|недел\w*|месяц\w*|business\s+days?|days?|weeks?|months?)\b'
    r'(?:\s+(?:ichida|davomida|mobaynida|muddatda))?', re.I)
DEADLINE_REPLACE = {'uz': 'qonunda belgilangan muddatda', 'ru': 'в установленный законом срок', 'en': 'within the time limit set by law'}


def strip_deadlines(s: str, arts: list[search.Article], lang: str = 'uz') -> str:
    def repl(m: re.Match) -> str:
        raw = m.group('n').lower()
        n = int(raw) if raw.isdigit() else next((v for k, v in _WORDNUM.items() if re.fullmatch(k, raw, re.I)), None)
        u = m.group('u').lower()
        if n is None:
            return m.group(0)
        days = n * 30 if u.startswith(('oy', 'месяц', 'month')) else n * 7 if u.startswith(('hafta', 'недел', 'week')) else n
        if _deadline_ok(days, arts) or (u.startswith(('oy', 'месяц', 'month')) and _MONTHS.get(days) and _deadline_ok(days, arts)):
            return m.group(0)
        return DEADLINE_REPLACE.get(lang, DEADLINE_REPLACE['uz'])
    return _DUR_RE.sub(repl, s)


def routes(ans: dict, arts: list[search.Article] | None = None) -> list[dict]:
    """AI javobidagi yoʻllarni tozalab, xavfsiz tuzilmaga keltiradi (matnlar validate() da tozalangan).
    Muddat faqat berilgan moddalar matnida boʻlsa qoladi; ariza qadami va xarita uchun idora qayta tekshiriladi."""
    out = []
    for r in as_list(ans.get('yollar'))[:3]:
        if not isinstance(r, dict) or not str(r.get('nom', '')).strip():
            continue
        steps = []
        for s in as_list(r.get('qadamlar'))[:5]:
            if not isinstance(s, dict) or not str(s.get('nima', '')).strip():
                continue
            d = s.get('muddat_kun')
            d = int(d) if isinstance(d, (int, float)) and 0 < d <= 90 else None
            src = _deadline_src(d, arts or []) if d else None
            if d and src is None:
                log.info('Muddat %s kun moddalarda topilmadi — olib tashlandi', d)
                d = None
            nima, idora = str(s['nima']).strip()[:300], str(s.get('idora') or '').strip()[:80]
            if _NOT_PLACE_RE.search(idora):
                idora = ''  # ish beruvchi / sotuvchi — xaritada qidirib boʻlmaydi
            steps.append({'nima': nima, 'idora': idora,
                          'olib': [str(x)[:80] for x in as_list(s.get('olib_borish')) if isinstance(x, str)][:5],
                          'kun': d, 'manba': {'abbr': src.abbr, 'num': src.num, 'link': src.link} if d else None,
                          'ariza': bool(s.get('ariza')) or bool(_WRITE_RE.search(nima))})
        if steps:
            nom = str(r['nom']).strip()
            if len(nom) > 48:  # tugmaga sigʻishi uchun: soʻz chegarasida qisqartiriladi
                nom = nom[:48].rsplit(' ', 1)[0] + '…'
            out.append({'nom': nom, 'qisqa': str(r.get('qisqa') or '').strip()[:200], 'steps': steps})
    return out

_NUM = r'\d+(?:[⁰¹²³⁴⁵⁶⁷⁸⁹]+)?(?:[ \t]*[-–—‑][ \t]*\d+)?'
# Uch tildagi shakllar: "168-modda", "168 moddasi", "168‑modda", "168-моддаси", "100 va 777-moddalar", "modda 168",
# "JKning 168-m.", "статья 168", "ст. 168", "статьи 22 и 28", "168-я статья", "Article 168", "Art. 168", "articles 22 and 28"
_WORD = r'(?:modda|модда|стать[яиеюй]\w*|ст\.|articles?|art\.)'
MODDA_IN_TEXT = re.compile(
    rf'(?P<nums>{_NUM}(?:\s*(?:,|va|и|and)\s*{_NUM})*)[\s\-–—‑]*(?:-?[яй]\s+)?(?:{_WORD}|m\.)\w*'
    rf'|{_WORD}\s*(?P<num2>{_NUM}(?:\s*(?:,|va|и|and)\s*{_NUM})*)', re.I)
REPLACE = {'uz': 'tegishli modda', 'ru': 'соответствующая статья', 'en': 'the relevant article'}
# Qonun nomi → qisqa nom (arizada "qonun + modda" juftini tekshirish uchun). Matn normalize() dan oʻtgan:
# kirill → lotin (ж→j, щ→sh, х→x), oʻ → o1. Shuning uchun ruscha nomlar ham lotin koʻrinishida.
LAW_ALIASES = [
    (r'mehnat\s+kodeks|\bmk\b|trudov\w*\s+kodeks', {'MK'}),
    (r'fuqarolik\s+kodeks|\bfk\b|grajdansk\w*\s+kodeks', {'FK-1', 'FK-2'}),
    (r'jinoyat\s+kodeks|\bjk\b|ugolovn\w*\s+kodeks', {'JK'}),
    (r'mamuriy\s+javobgarlik|\bmjtk\b|administrativn\w*\s+otvetstvennost', {'MJtK'}),
    (r'murojaatlar(i)?\s+to1g1risida|\bmurq\b|obrasheni\w*\s+fizicheskix', {'MurQ'}),
    (r'istemolchi|\bihhq\b|zashit\w*\s+prav\s+potrebitel', {'IHHQ'}),
]


@dataclass
class Result:
    level: str
    danger: bool
    triage: dict
    answer: dict
    articles: list[search.Article]          # AI ga berilgan moddalar (A1..An)
    cited: list[tuple[search.Article, str]] = field(default_factory=list)  # tekshiruvdan o'tgan manbalar
    removed: list[str] = field(default_factory=list)                        # tekshiruvda olib tashlanganlar


def is_danger(text: str) -> bool:
    return bool(DANGER.search(normalize(text)))


async def triage(text: str, role: str) -> dict:
    laws = '; '.join(f'{a}: {n}' for a, n in search.laws().items())
    out = await llm.chat(TRIAGE_SYSTEM, TRIAGE_USER.format(role=ROLE_NAMES.get(role, role), laws=laws, text=text[:6000]),
                         model=config.MODEL_FAST, json_mode=True, max_tokens=600)
    t = llm.parse_json(out)
    t['daraja'] = t.get('daraja') if t.get('daraja') in LEVELS else 'muhim'
    t['sorovlar'] = [q for q in as_list(t.get('sorovlar')) if isinstance(q, str)][:5]
    t['qonunlar'] = [a for a in as_list(t.get('qonunlar')) if a in search.laws()][:3]
    return t


def as_list(v) -> list:
    """AI ro'yxat o'rniga satr qaytarsa ham bitta element sifatida olinadi (harflarga bo'linib ketmasin)."""
    if isinstance(v, str):
        return [v] if v.strip() else []
    if isinstance(v, list):
        return [x for x in v if isinstance(x, (str, dict))]
    return []


def retrieve(text: str, t: dict, role: str, limit: int = 8) -> list[search.Article]:
    """Rol va saralash tanlagan qonunlar birinchi; keyin butun baza; murojaat tartibi (MurQ 28 + 1) doim qo'shiladi."""
    priority = list(dict.fromkeys(t.get('qonunlar', []) + ROLE_LAWS.get(role, [])))
    queries = t.get('sorovlar') or [text]
    picked: dict[tuple[str, str], search.Article] = {}

    def add(items):
        for a in items:
            picked.setdefault((a.abbr, a.num), a)

    add(search.search(text, 3))  # fuqaroning o'z so'zlari bilan topilgan moddalar birinchi (kesilib qolmasin)
    for q in queries:
        if priority:
            add(search.search(q, 2, laws=priority))
        add(search.search(q, 2))
    out = list(picked.values())[: limit - 2]
    # Rasmiy 1-muammo: qanday murojaat qilish. MurQ 28 (ko'rib chiqish muddatlari) doim + yana 1 ta
    extra = [a for a in [search.get('MurQ', '28')] if a]
    extra += search.search('murojaat berish shakli talablar shikoyat', 3, laws=['MurQ'])
    have = {(x.abbr, x.num) for x in out}
    for a in extra:
        if len(out) >= limit:
            break
        if (a.abbr, a.num) not in have:
            out.append(a)
            have.add((a.abbr, a.num))
    return out


def _articles_block(arts: list[search.Article]) -> str:
    # Groq bepul tarifi: daqiqasiga ~8000 token — har moddadan 900 belgi yetarli
    return '\n\n'.join(f'[A{i}] {a.law}, {a.title}\n{a.body[:900]}' for i, a in enumerate(arts, 1))


# Faqat ichki belgilar: "[A5]", "(A3, A4)", "A5 manba" — "A4 formatdagi qog'oz" ga tegilmaydi
_AID = re.compile(r'\s*[\[(]\s*A\d{1,2}(?:\s*[,;–-]\s*A\d{1,2})*\s*[\])]|\s*\bA\d{1,2}\b(?=\s+(?:manba|modda)\w*)')


def _walk(o, fn, skip=('id',)):
    if isinstance(o, str):
        return fn(o)
    if isinstance(o, list):
        return [_walk(v, fn, skip) for v in o]
    if isinstance(o, dict):
        return {k: (v if k in skip else _walk(v, fn, skip)) for k, v in o.items()}
    return o


def clean_text(s: str, lang: str = 'uz') -> tuple[str, int]:
    """Javob matnidagi BARCHA modda raqamlarini olib tashlaydi: raqamlar faqat kartaning havolali "Qonun"
    bo'limida, bazadan olinib ko'rsatiladi (shu jumladan "nima_uchun" ichida ham). → (toza matn, soni)"""
    n = len(MODDA_IN_TEXT.findall(s))
    s = MODDA_IN_TEXT.sub(REPLACE.get(lang, REPLACE['uz']), s)
    return _AID.sub('', s).strip(), n


def validate(ans: dict, arts: list[search.Article], lang: str = 'uz') -> tuple[dict, list[tuple[search.Article, str]], list[str]]:
    """1) Manbalar faqat A1..An; 2) matndagi har qanday modda raqami va ichki [A5] belgisi olib tashlanadi.
    Qaytaradi: (tozalangan javob, manbalar — "nima_uchun" tozalangan javobdan, olib tashlanganlar)."""
    removed: list[str] = []
    count = 0

    def fn(s: str) -> str:
        nonlocal count
        out, n = clean_text(s, lang)
        count += n
        return out

    ans = _walk(ans if isinstance(ans, dict) else {}, fn)
    for key in ('huquqlar', 'majburiyatlar', 'dalillar', 'aniqlashtirish', 'murojaat', 'manbalar'):
        ans[key] = as_list(ans.get(key))
    if count:
        removed.append(f'matnda {count} ta modda raqami')
    cited: list[tuple[search.Article, str]] = []
    for s in ans['manbalar']:
        sid = str(s.get('id', '')).strip().strip('[]').upper() if isinstance(s, dict) else ''
        m = re.fullmatch(r'A(\d+)', sid)
        if m and 1 <= int(m.group(1)) <= len(arts):
            a = arts[int(m.group(1)) - 1]
            if all((a.abbr, a.num) != (c.abbr, c.num) for c, _ in cited):
                cited.append((a, str(s.get('nima_uchun', ''))))
        else:
            removed.append(f'manba {sid or "?"}')
    return ans, cited, removed


def check_application(text: str, cited: list[tuple[search.Article, str]], lang: str = 'uz') -> str:
    """Arizada modda raqami faqat (qonun, raqam) jufti manbalarda bo'lsa qoladi; qonun aniqlanmasa — "tegishli modda"."""
    pairs = {(a.abbr, search.norm_num(a.num)) for a, _ in cited}

    def repl(m: re.Match) -> str:
        nums = [search.norm_num(x) for x in re.findall(_NUM, m.group('nums') or m.group('num2') or '')]
        # Grammatika: oʻzbekchada qonun nomi moddadan OLDIN ("Mehnat kodeksining 100-moddasi"),
        # ruschada — darhol KEYIN ("статья 100 Трудового кодекса", "ст. 28 Закона «Об обращениях…»").
        laws: set[str] = set()
        if lang == 'ru':
            after = normalize(text[m.end():m.end() + 70])
            best = 16  # nom moddadan keyin 15 belgidan uzoq boʻlmasligi kerak
            for pat, abbrs in LAW_ALIASES:
                mm = re.search(pat, after)
                if mm and mm.start() < best:
                    best, laws = mm.start(), abbrs
        else:
            before = normalize(text[max(0, m.start() - 90):m.start()])
            pos = -1
            for pat, abbrs in LAW_ALIASES:  # eng yaqin (oxirgi tilga olingan) qonun nomi
                for mm in re.finditer(pat, before):
                    if mm.start() > pos:
                        pos, laws = mm.start(), abbrs
        if laws and nums and all(any((ab, n) in pairs for ab in laws) for n in nums):
            return m.group(0)
        return REPLACE.get(lang, REPLACE['uz'])
    return MODDA_IN_TEXT.sub(repl, text)


async def answer(text: str, role: str, t: dict, arts: list[search.Article], lang: str = 'uz') -> dict:
    user = ANSWER_USER.format(lang=AI_LANG.get(lang, AI_LANG['uz']), role=ROLE_NAMES.get(role, role), soha=t.get('soha', ''),
                              daraja=t.get('daraja', ''), text=text[:6000], articles=_articles_block(arts))
    out = await llm.chat(ANSWER_SYSTEM, user, model=config.MODEL_STRONG, json_mode=True, max_tokens=2500)
    return llm.parse_json(out)


async def analyze(text: str, role: str, lang: str = 'uz') -> Result:
    danger = is_danger(text)
    t = await triage(text, role)
    if t['daraja'] == 'xavf':
        danger = True
    arts = retrieve(text, t, role)
    ans, cited, removed = validate(await answer(text, role, t, arts, lang), arts, lang)
    if any(r.startswith('manba') for r in removed) or not cited:
        log.warning('Tekshiruv: %s — qayta so\'raladi', removed)
        ans2, cited2, removed2 = validate(await answer(
            text + f'\n\n(ESLATMA: manbalarda faqat A1…A{len(arts)} id lardan foydalan, matnda modda raqami yozma.)',
            role, t, arts, lang), arts, lang)
        if cited2 and len(removed2) <= len(removed):
            ans, cited, removed = ans2, cited2, removed2
    if not cited:  # karta havolasiz qolmasin: eng yaxshi topilgan 2 ta modda, "yurist tekshirsin" izohi bilan
        cited = [(a, i18n_t(lang, 'AI_FALLBACK_WHY')) for a in arts[:2]]
        removed.append('AI manba tanlamadi, qidiruv natijasi ko\'rsatildi')
    # Matndagi muddatlar faqat tanlangan (tekshirilgan) moddalarda boʻlsa qoladi
    src = [x for x, _ in cited]
    ans = _walk(ans, lambda v: strip_deadlines(v, src, lang), skip=('id', 'yollar'))
    if isinstance(ans.get('yollar'), list):  # yoʻllar ichida ham (raqamli muddat_kun alohida tekshiriladi)
        ans['yollar'] = _walk(ans['yollar'], lambda v: strip_deadlines(v, src, lang))
    return Result(level=t['daraja'], danger=danger, triage=t, answer=ans, articles=arts, cited=cited, removed=removed)


APP_SYSTEM = (
    "Sen O'zbekistonda davlat tashkilotiga beriladigan rasmiy ariza (murojaat) matnini tuzuvchisan. "
    "Ariza 'Jismoniy va yuridik shaxslarning murojaatlari to'g'risida'gi qonun talablariga mos bo'lsin: kimga, kimdan "
    "(F.I.Sh., yashash manzili, telefon), mazmun (faktlar: nima, qachon, qayerda), talab, ilovalar ro'yxati, sana va imzo. "
    "Shaxsiy ma'lumot o'rniga kvadrat qavsda bo'sh joy qoldir: [F.I.Sh.], [manzil], [telefon], [sana], [imzo] "
    "(fuqaro ularni qo'lda to'ldiradi). Tuzilma qat'iy: 1) yuqorida alohida qatorlarda kimga (idora va rahbar) va kimdan; "
    "2) alohida qatorda faqat sarlavha: ARIZA (yoki SHIKOYAT); 3) 2-4 ta xatboshi: faktlar, huquqiy asos, aniq talab; "
    "4) 'Ilovalar:' va ro'yxat; 5) oxirida alohida qatorlarda [sana] va [imzo]. Markdown, ro'yxat belgilari ishlatma. "
    "Faqat berilgan moddalarga havola qil, qonun nomi bilan birga (masalan: «Mehnat kodeksining 333-moddasi»), boshqa "
    "modda raqami yozma. Rasmiy, xushmuomala uslubda, so'ralgan tilda yoz. Faqat ariza matnini qaytar, izohsiz."
)
# Ariza davlat organiga beriladi: oʻzbek yoki rus tilida. Ingliz tilini tanlagan foydalanuvchiga — davlat tilida (oʻzbek).
APP_LANG = {'uz': 'oʻzbek tili (lotin yozuvi)', 'ru': 'rus tili', 'en': 'oʻzbek tili (lotin yozuvi)'}
APP_USER = """ARIZA TILI: {lang}
Vaziyat (fuqaro so'zlari):
\"\"\"{text}\"\"\"

Tahlil: {vaziyat}
Kimga: {kimga}
Fuqaro roli: {role}
Havola qilish mumkin bo'lgan moddalar: {cites}"""


async def application(text: str, role: str, ans: dict, cited: list[tuple[search.Article, str]], lang: str = 'uz') -> str:
    steps = [s for s in (ans.get('murojaat') or []) if isinstance(s, dict)]
    kimga = steps[0].get('kimga', 'tegishli davlat organi') if steps else 'tegishli davlat organi'
    cites = '; '.join(f'{a.law}, {a.num}-modda ({a.title.split(". ", 1)[-1]})' for a, _ in cited) or 'yo\'q'
    out = await llm.chat(APP_SYSTEM, APP_USER.format(lang=APP_LANG.get(lang, APP_LANG['uz']), text=text[:4000],
                                                     vaziyat=ans.get('vaziyat', ''), kimga=kimga,
                                                     role=ROLE_NAMES.get(role, role), cites=cites),
                         model=config.MODEL_STRONG, max_tokens=1500)
    out = re.sub(r'\*\*|__|^#+\s*', '', out, flags=re.M)  # Markdown belgilari <pre> ichida ko'rinib qolmasin
    return check_application(out, cited, 'ru' if lang == 'ru' else 'uz')


def to_json(r: Result) -> str:
    return json.dumps({'triage': r.triage, 'answer': r.answer, 'removed': r.removed,
                       'cited': [{'abbr': a.abbr, 'num': a.num, 'link': a.link, 'why': w} for a, w in r.cited]},
                      ensure_ascii=False)
