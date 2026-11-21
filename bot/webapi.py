"""Mini App uchun veb-server: sahifa (webapp/index.html) va /api/*.

Xavfsizlik: har bir /api so'rovi Telegram initData imzosi bilan tekshiriladi
(HMAC-SHA256, kalit = HMAC("WebAppData", BOT_TOKEN)); imzosiz yoki 24 soatdan eski so'rov — 401.
Tahlil botdagi o'sha zanjirdan (pipeline) o'tadi: xavf filtri, modda tekshiruvchisi, 3 kalit."""
import base64
import hashlib
import hmac
import json
import logging
import time
from urllib.parse import parse_qsl

from aiogram import Bot
from aiohttp import web

from . import config, keys, llm, navflow, pipeline, search, store
from .i18n import LANGS, law_name, t

log = logging.getLogger('lexnav.web')
WEBAPP = config.ROOT / 'webapp' / 'index.html'
MAX_AGE = 24 * 3600
_busy: set[int] = set()  # bir foydalanuvchi bir vaqtda bitta tahlil


def verify_init_data(init_data: str, token: str = None, now: float = None) -> dict | None:
    """Telegram WebApp initData ni tekshiradi. To'g'ri bo'lsa — user dict, aks holda None."""
    if not init_data:
        return None
    pairs = dict(parse_qsl(init_data, keep_blank_values=True))
    got = pairs.pop('hash', '')
    if not got:
        return None
    dcs = '\n'.join(f'{k}={v}' for k, v in sorted(pairs.items()))
    secret = hmac.new(b'WebAppData', (token or config.BOT_TOKEN).encode(), hashlib.sha256).digest()
    calc = hmac.new(secret, dcs.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(calc, got):
        return None
    try:
        if (now or time.time()) - int(pairs.get('auth_date', 0)) > MAX_AGE:
            return None
        user = json.loads(pairs.get('user', '{}'))
    except ValueError:
        return None
    return user if isinstance(user, dict) and user.get('id') else None


def req_lang(request: web.Request, body: dict | None = None) -> str:
    """Til: soʻrovdagi lang → foydalanuvchi tanlovi (bot bilan umumiy) → uz. Ilovada tanlangan til botga ham saqlanadi."""
    raw = (body or {}).get('lang') or request.query.get('lang')
    uid = request.get('uid')
    sc = (body or {}).get('script') or request.query.get('script')
    if uid and raw == 'uz' and sc in ('cyrl', 'latn') and store.script(uid) != sc:
        store.set_script(uid, sc)  # Mini App sozlamasidagi yozuv botga ham oʻtadi
    if raw in LANGS:
        if uid and store.get_lang(uid) != raw:
            store.set_lang(uid, raw)
        return raw
    return store.lang(uid) if uid else 'uz'


def _err(status: int, msg: str, **extra) -> web.Response:
    return web.json_response({'error': msg, **extra}, status=status)


@web.middleware
async def auth(request: web.Request, handler):
    if not request.path.startswith('/api/'):
        return await handler(request)
    user = verify_init_data(request.headers.get('X-Telegram-Init-Data', ''))
    if user is None:
        return _err(401, 'Ilovani Telegram ichida oching.')
    request['uid'] = int(user['id'])
    try:
        return await handler(request)
    except web.HTTPException:
        raise
    except (json.JSONDecodeError, AttributeError):  # yaroqsiz JSON yoki obyekt oʻrniga roʻyxat
        return _err(400, 'Bad request')
    except Exception as e:  # noqa: BLE001 — xato tafsiloti foydalanuvchiga ko'rsatilmaydi
        log.error('API xatosi %s: %s', request.path, type(e).__name__)
        return _err(500, 'Texnik xatolik. Birozdan keyin qayta urinib ko\'ring.')


def _card(case_id: int, r: pipeline.Result, lang: str = 'uz') -> dict:
    a = r.answer
    return {
        'case_id': case_id, 'level': r.level, 'danger': r.danger,
        'vaziyat': a.get('vaziyat', ''), 'huquqlar': a.get('huquqlar', []), 'majburiyatlar': a.get('majburiyatlar', []),
        'murojaat': [m for m in a.get('murojaat', []) if isinstance(m, dict)], 'dalillar': a.get('dalillar', []),
        'cited': [{'law': law_name(lang, x.abbr, x.law), 'num': x.num, 'link': x.link, 'why': w} for x, w in r.cited],
    }


async def consent(request: web.Request) -> web.Response:
    req_lang(request, await request.json())
    store.set_consent(request['uid'])
    return web.json_response({'ok': True})


async def analyze(request: web.Request) -> web.Response:
    uid = request['uid']
    body = await request.json()
    lang = req_lang(request, body)
    if not store.has_consent(uid):
        return _err(403, t(lang, 'CONSENT_NEED'), need_consent=True)
    if uid in _busy:
        return _err(429, '…')
    text = str(body.get('text') or '').strip()[:4000]
    role = body.get('role') if body.get('role') in t('uz', 'ROLES') else 'boshqa'
    _busy.add(uid)
    try:
        if body.get('file'):  # ovoz yoki rasm: xotirada matnga o'giriladi, diskka yozilmaydi
            raw = base64.b64decode(body['file'], validate=False)
            if len(raw) > config.MAX_FILE_MB * 1024 * 1024:
                return _err(413, t(lang, 'TOO_BIG'))
            ftype, name = str(body.get('file_type') or ''), str(body.get('file_name') or 'file')
            if ftype.startswith('audio/') or ftype.startswith('video/'):
                extra = await llm.transcribe(raw, name)
            elif ftype.startswith('image/'):
                from .media import VISION_PROMPT, VISION_SYSTEM
                extra = await llm.chat(VISION_SYSTEM, VISION_PROMPT, model=config.MODEL_VISION, image=raw, mime=ftype, max_tokens=1200)
            else:
                return _err(415, t(lang, 'UNSUPPORTED'))
            del raw
            text = (text + '\n' + extra).strip()
        if not text:
            return _err(400, t(lang, 'NEW'))
        case_id = store.create_case(uid, text, 'webapp')
        store.set_case_role(case_id, uid, role)
        try:
            r = await pipeline.analyze(text, role, lang)
        except Exception:
            store.set_status(case_id, 'awaiting_role')
            raise
        store.save_analysis(case_id, r.level, pipeline.to_json(r), r.answer.get('ishonch'))
        log.info('WebApp case %s: daraja=%s manbalar=%s', case_id, r.level, [f'{a.abbr} {a.num}' for a, _ in r.cited])
        out = _card(case_id, r, lang)
        if text and r.danger is False and pipeline.is_danger(text):
            out['danger'] = True
        return web.json_response(out)
    finally:
        _busy.discard(uid)


# ---------- Navigator (Mini App) ----------
async def _body_text(body: dict, lang: str) -> tuple[str, web.Response | None]:
    """Matn + (ixtiyoriy) ovoz/rasm fayli → matn. Fayl xotirada oʻgiriladi, diskka yozilmaydi."""
    text = str(body.get('text') or '').strip()[:4000]
    if body.get('file'):
        raw = base64.b64decode(body['file'], validate=False)
        if len(raw) > config.MAX_FILE_MB * 1024 * 1024:
            return '', _err(413, t(lang, 'TOO_BIG'))
        ftype, name = str(body.get('file_type') or ''), str(body.get('file_name') or 'file')
        if ftype.startswith(('audio/', 'video/')):
            extra = await llm.transcribe(raw, name)
        elif ftype.startswith('image/'):
            from .media import VISION_PROMPT, VISION_SYSTEM
            extra = await llm.chat(VISION_SYSTEM, VISION_PROMPT, model=config.MODEL_VISION, image=raw, mime=ftype, max_tokens=1200)
        else:
            return '', _err(415, t(lang, 'UNSUPPORTED'))
        del raw
        text = (text + '\n' + extra).strip()
    if not text:
        return '', _err(400, t(lang, 'NEW'))
    return text, None


def _nav(request: web.Request, body: dict) -> dict | None:
    try:
        return store.nav_case(int(body.get('case_id') or request.query.get('id') or 0), request['uid'])
    except (TypeError, ValueError):
        return None


async def nav_start(request: web.Request) -> web.Response:
    """Vaziyat + rol → murojaat yaratiladi va aniqlashtiruvchi savollar qaytariladi."""
    uid = request['uid']
    body = await request.json()
    lang = req_lang(request, body)
    if not store.has_consent(uid):
        return _err(403, t(lang, 'CONSENT_NEED'), need_consent=True)
    if uid in _busy:
        return _err(429, '…')
    role = body.get('role') if body.get('role') in t('uz', 'ROLES') else 'boshqa'
    _busy.add(uid)
    try:
        text, err = await _body_text(body, lang)
        if err:
            return err
        case_id = store.create_case(uid, text, 'webapp')
        store.set_case_role(case_id, uid, role)
        # Hayotga xavf — AI chaqirilmasdan oldin: savollar soʻralmaydi, ilova darhol 112/102/103 ni koʻrsatadi
        if pipeline.is_danger(text):
            store.nav_update(case_id, questions=[], answers=[])
            return web.json_response({'case_id': case_id, 'questions': [], 'danger': True, 'text': text[:1500]})
        qs = await pipeline.clarify(text, role, lang)
        store.nav_update(case_id, questions=qs, answers=[])
        return web.json_response({'case_id': case_id, 'questions': qs, 'danger': False, 'text': text[:1500]})
    finally:
        _busy.discard(uid)


async def nav_navigate(request: web.Request) -> web.Response:
    """Javoblar + tuman/joylashuv → tahlil va yoʻllar."""
    uid = request['uid']
    body = await request.json()
    lang = req_lang(request, body)
    case = _nav(request, body)
    if case is None:
        return _err(404, t(lang, 'CASE_GONE'))
    if uid in _busy:
        return _err(429, '…')
    answers = [{'q': str(a.get('q', ''))[:300], 'a': str(a.get('a', ''))[:500]}
               for a in (body.get('answers') or []) if isinstance(a, dict) and a.get('a')][:4]
    fields = {'answers': answers}
    if str(body.get('district') or '').strip():
        fields['district'] = str(body['district']).strip()[:80]
    try:
        if body.get('lat') is not None and body.get('lon') is not None:
            fields['lat'], fields['lon'] = float(body['lat']), float(body['lon'])
    except (TypeError, ValueError):
        pass
    store.nav_update(case['id'], **fields)
    _busy.add(uid)
    try:
        await navflow.analyze_case(case['id'], uid, lang)
    finally:
        _busy.discard(uid)
    return web.json_response(navflow.state(store.nav_case(case['id'], uid), lang))


async def nav_route(request: web.Request) -> web.Response:
    body = await request.json()
    lang = req_lang(request, body)
    case = _nav(request, body)
    try:
        i = int(body.get('route'))
    except (TypeError, ValueError):
        return _err(400, 'route')
    if case is None or not navflow.do_route(case, i):
        return _err(404, t(lang, 'CASE_GONE'))
    return web.json_response(navflow.state(store.nav_case(case['id'], request['uid']), lang))


async def nav_step(request: web.Request) -> web.Response:
    """action: done | ok | wait | no"""
    body = await request.json()
    lang = req_lang(request, body)
    case = _nav(request, body)
    if case is None:
        return _err(404, t(lang, 'CASE_GONE'))
    action = body.get('action')
    # Ilova koʻrgan qadam bilan serverdagi qadam mos kelmasa (ikki marta bosish, eski ekran) — hech narsa oʻzgarmaydi
    if 'step' in body and body.get('step') != case['step']:
        return web.json_response({**navflow.state(case, lang), 'result': {'kind': 'noop'}})
    r = navflow.do_done(case) if action == 'done' else navflow.do_result(case, action) if action in ('ok', 'wait', 'no') else {'kind': 'noop'}
    return web.json_response({**navflow.state(store.nav_case(case['id'], request['uid']), lang), 'result': r})


async def nav_case_get(request: web.Request) -> web.Response:
    lang = req_lang(request)
    case = _nav(request, {})
    if case is None:
        return _err(404, t(lang, 'CASE_GONE'))
    return web.json_response(navflow.state(case, lang))


async def nav_ask(request: web.Request) -> web.Response:
    body = await request.json()
    lang = req_lang(request, body)
    case = _nav(request, body)
    q = str(body.get('question') or '').strip()
    if case is None or not case.get('analysis') or not q:
        return _err(404, t(lang, 'CASE_GONE'))
    return web.json_response({'answer': await navflow.answer_question(case, q[:800], lang), 'disclaimer': t(lang, 'DISCLAIMER')})


async def nav_pdf(request: web.Request) -> web.Response:
    """Ariza PDF i Telegram chatga yuboriladi (Mini App ichida fayl yuklab olish har doim ishlamaydi)."""
    body = await request.json()
    lang = req_lang(request, body)
    case = _nav(request, body)
    if case is None:
        return _err(404, t(lang, 'CASE_GONE'))
    ok = await navflow.send_pdf(request.app['bot'], request['uid'], case['id'], lang)
    return web.json_response({'ok': ok}, status=200 if ok else 503)


async def application(request: web.Request) -> web.Response:
    uid = request['uid']
    body = await request.json()
    lang = req_lang(request, body)
    case = store.get_case(int(body.get('case_id', 0)), uid)
    if case is None or not case['analysis']:
        return _err(404, t(lang, 'CASE_GONE'))
    if not case['application']:
        data = json.loads(case['analysis'])
        cited = [(a, x.get('why', '')) for x in data.get('cited', []) if (a := search.get(x['abbr'], x['num']))]
        app_text = await pipeline.application(case['text'], case['role'] or 'boshqa', data.get('answer', {}), cited, lang)
        store.save_application(case['id'], app_text)
    else:
        app_text = case['application']
    return web.json_response({'text': app_text})


async def escalate(request: web.Request) -> web.Response:
    """3 kalit faqat bot chatida: K1 uchun Telegram "kontakt ulashish" tugmasi kerak. Bot foydalanuvchiga tugma yuboradi."""
    uid = request['uid']
    body = await request.json()
    lang = req_lang(request, body)
    case = store.get_case(int(body.get('case_id', 0)), uid)
    if case is None or not case['analysis']:
        return _err(404, t(lang, 'CASE_GONE'))
    bot: Bot = request.app['bot']
    from aiogram.types import InlineKeyboardMarkup
    await bot.send_message(uid, t(lang, 'WEBAPP_ESCALATE', id=case['id']),
                           reply_markup=InlineKeyboardMarkup(inline_keyboard=[[keys.escalate_kb(case['id'], lang)]]))
    st = case['status']
    state = {'k1': 'wait', 'k2': 'idle', 'k3': 'idle'}
    if st in ('k3_wait', 'sent', 'rejected'):
        state = {'k1': 'ok', 'k2': 'ok', 'k3': 'ok' if st == 'sent' else 'wait'}
    elif st == 'k2_wait':
        state = {'k1': 'ok', 'k2': 'wait', 'k3': 'idle'}
    return web.json_response({'keys': state, 'score': case.get('score'), 'in_bot': True})


STATUS = {'uz': {'awaiting_role': 'Rol tanlanmagan', 'analyzing': 'Tahlil qilinmoqda', 'answered': 'Javob berildi',
             'k1_wait': '1-kalit kutilmoqda', 'k2_wait': '2-kalit tekshirilmoqda', 'k2_more': '2-kalit: aniqlashtirish kutilmoqda', 'k3_wait': 'Yurist tekshiruvida (3-kalit)',
             'sent': 'Idoraga yuborildi', 'rejected': 'Yurist rad etdi', 'reminded': 'Holati so\'raldi',
             'urgent': 'Klinikada shoshilinch', 'closed': 'Yopildi'},
          'ru': {'awaiting_role': 'Роль не выбрана', 'analyzing': 'Анализируется', 'answered': 'Ответ дан', 'k1_wait': 'Ожидается ключ 1',
                 'k2_wait': 'Проверка ключа 2', 'k2_more': 'Ключ 2: ждём уточнения', 'k3_wait': 'На проверке у юриста (ключ 3)', 'sent': 'Направлено в орган',
                 'rejected': 'Отклонено юристом', 'reminded': 'Запрошен статус', 'urgent': 'Срочно в клинике', 'closed': 'Закрыто'},
          'en': {'awaiting_role': 'Role not chosen', 'analyzing': 'Analysing', 'answered': 'Answered', 'k1_wait': 'Awaiting key 1',
                 'k2_wait': 'Key 2 check', 'k2_more': 'Key 2: clarification needed', 'k3_wait': 'Lawyer review (key 3)', 'sent': 'Sent to the authority',
                 'rejected': 'Declined by lawyer', 'reminded': 'Status requested', 'urgent': 'Urgent at the clinic', 'closed': 'Closed'}}


KEY_STATES = {'k1_wait', 'k2_wait', 'k2_more', 'k3_wait', 'sent', 'rejected', 'urgent', 'reminded'}
NAV_STATUS = {'uz': {'routes': 'Yoʻl tanlanmagan', 'nav': 'Yoʻlda', 'waiting': 'Javob kutilmoqda', 'checking': 'Javob soʻraldi',
                     'route_done': 'Yoʻl yakunlandi', 'closed': 'Hal boʻldi'},
              'ru': {'routes': 'Путь не выбран', 'nav': 'В пути', 'waiting': 'Ожидается ответ', 'checking': 'Запрошен ответ',
                     'route_done': 'Путь пройден', 'closed': 'Решено'},
              'en': {'routes': 'Route not chosen', 'nav': 'On the way', 'waiting': 'Awaiting reply', 'checking': 'Reply requested',
                     'route_done': 'Route finished', 'closed': 'Resolved'}}


async def cases(request: web.Request) -> web.Response:
    rows = store.con().execute('SELECT id, text, level, status, nav_status, created FROM cases WHERE user_id = ? '
                               'AND analysis IS NOT NULL ORDER BY id DESC LIMIT 30', (request['uid'],)).fetchall()
    lang = req_lang(request)

    def label(st, nst):  # 3 kalit jarayoni ustun; boʻlmasa — navigator holati
        if st in KEY_STATES or not nst:
            return STATUS[lang].get(st, st)
        return NAV_STATUS[lang].get(nst, nst)
    out = [{'id': i, 'title': (tx or '').split('\n')[0][:80], 'level': lv or 'muhim', 'status': label(st, nst),
            'date': time.strftime('%d.%m.%Y', time.localtime(c))} for i, tx, lv, st, nst, c in rows]
    return web.json_response({'cases': out})


async def laws(request: web.Request) -> web.Response:
    rows = search.con().execute('SELECT abbr, law, source, articles FROM docs ORDER BY articles DESC').fetchall()
    lang = req_lang(request)
    return web.json_response({'laws': [{'abbr': a, 'name': law_name(lang, a, n), 'link': s, 'articles': c} for a, n, s, c in rows]})


def _page() -> str:
    """index.html (artifakt uslubida, skeletsiz) ni to'liq HTML hujjatga o'raydi va API manzilini qo'shadi."""
    src = WEBAPP.read_text(encoding='utf-8')
    head, _, body = src.partition('</style>')
    return ('<!doctype html><html lang="uz"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'
            "<style>[hidden]{display:none!important}body{margin:0}</style>"
            "<script>window.LEXNAV_API='/api';</script>"
            f'{head}</style></head><body>{body}</body></html>')


async def page(request: web.Request) -> web.Response:
    return web.Response(text=_page(), content_type='text/html', headers={'Cache-Control': 'no-store'})


def make_app(bot: Bot) -> web.Application:
    app = web.Application(middlewares=[auth], client_max_size=30 * 1024 * 1024)
    app['bot'] = bot
    app.router.add_get('/', page)
    app.router.add_post('/api/consent', consent)
    app.router.add_post('/api/analyze', analyze)
    app.router.add_post('/api/application', application)
    app.router.add_post('/api/escalate', escalate)
    app.router.add_get('/api/cases', cases)
    app.router.add_get('/api/laws', laws)
    app.router.add_post('/api/nav/start', nav_start)
    app.router.add_post('/api/nav/navigate', nav_navigate)
    app.router.add_post('/api/nav/route', nav_route)
    app.router.add_post('/api/nav/step', nav_step)
    app.router.add_post('/api/nav/ask', nav_ask)
    app.router.add_post('/api/nav/pdf', nav_pdf)
    app.router.add_get('/api/nav/case', nav_case_get)
    return app


async def start(bot: Bot) -> web.AppRunner:
    runner = web.AppRunner(make_app(bot), access_log=None)
    await runner.setup()
    await web.TCPSite(runner, '127.0.0.1', config.WEB_PORT).start()
    log.info('Mini App server: http://127.0.0.1:%s', config.WEB_PORT)
    return runner
