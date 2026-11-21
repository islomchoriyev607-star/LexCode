"""3 kalit: idoraga faqat K1 (telefon) + K2 (AI ishonchlilik bali) + K3 (klinika yuristi tasdig'i) dan keyin
(CLAUDE.md, 5-qoida). Boshqa yo'l yo'q: idora guruhiga xabar faqat on_clinic_decision → approve ichidan ketadi.

Javobsiz 🔴 murojaat: belgilangan vaqtda foydalanuvchidan holat so'raladi; javob bo'lmasa klinikaga
"shoshilinch" belgisi bilan tushadi. Idoraga avtomatik yuborilmaydi."""
import asyncio
import html
import json
import logging
import time
from types import SimpleNamespace

from aiogram import Bot, F, Router
from aiogram.enums import ChatMemberStatus, ChatType
from aiogram.types import (CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, Message,
                           ReplyKeyboardMarkup, ReplyKeyboardRemove)

from . import config, llm, pipeline, search, store
from .i18n import t

log = logging.getLogger('lexnav.keys')
router = Router()
DAILY_LIMIT = 3
MIN_SCORE = 50
K2_MAX_TRIES = 3  # 2-kalit past ball bergach aniqlashtirish soni
ADMIN = (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR)

SCORE_SYSTEM = ("Sen Yuridik klinika uchun murojaatlarni oldindan saralovchisan. Murojaatning ishonchliligini baholaysan: "
                "izchilligi, aniq faktlar (kim, qachon, qayerda), dalil borligi, soxta yoki spam belgilari. "
                "Aybdorlik haqida xulosa chiqarma. Faqat JSON qaytar.")
SCORE_USER = """Murojaat matni:
\"\"\"{text}\"\"\"
Kirish turi: {kind} (voice/audio/image — fuqaro yozuv yoki skrinshot yuborgan)

JSON: {{"ball": 0-100, "sabab": "1 jumla", "yetishmaydi": ["aniqlashtirish kerak bo'lgan fakt", "..."]}}"""


def esc(s) -> str:
    return html.escape(str(s or ''), quote=False)


def escalate_kb(case_id: int, lang: str = 'uz') -> InlineKeyboardButton:
    return InlineKeyboardButton(text=t(lang, 'BTN_ESC'), callback_data=f'esc:{case_id}')


def clinic_kb(case_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='✅ Tasdiqlash', callback_data=f'k3:ok:{case_id}'),
         InlineKeyboardButton(text='❌ Rad etish', callback_data=f'k3:no:{case_id}')],
        [InlineKeyboardButton(text='❔ Aniqlashtirish so\'rash', callback_data=f'k3:ask:{case_id}')],
    ])


# ---------- K1: telefon ----------
@router.callback_query(F.data.startswith('esc:'))
async def on_escalate(c: CallbackQuery) -> None:
    await c.answer()
    uid = c.from_user.id
    lang = store.lang(uid)
    case = store.get_case(int(c.data.split(':', 1)[1]), uid)
    if case is None:
        await c.bot.send_message(uid, t(lang, 'CASE_GONE'))
        return
    if case['status'] in ('k2_wait', 'k3_wait', 'sent', 'rejected'):
        await c.bot.send_message(uid, t(lang, 'ESC_ALREADY'))
        return
    if case['status'] == 'k2_more':
        store.set_pending(uid, None)  # 1-kalitdan qayta boshlanadi
    if config.CLINIC_CHAT_ID is None or config.AUTHORITY_CHAT_ID is None:
        await c.bot.send_message(uid, t(lang, 'ESC_NOT_CONFIGURED'))
        return
    if store.escalations_today(uid) >= DAILY_LIMIT:
        await c.bot.send_message(uid, t(lang, 'ESC_LIMIT', n=DAILY_LIMIT))
        return
    store.set_status(case['id'], 'k1_wait')
    store.set_pending_escalation(uid, case['id'])
    await c.bot.send_message(uid, t(lang, 'K1_ASK'), reply_markup=ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t(lang, 'K1_BUTTON'), request_contact=True)]],
        resize_keyboard=True, one_time_keyboard=True))


@router.message(F.contact, F.chat.type == ChatType.PRIVATE)
async def on_contact(m: Message) -> None:
    uid = m.from_user.id
    lang = store.lang(uid)
    case_id = store.pending_escalation(uid)
    if case_id is None:
        await m.answer(t(lang, 'CASE_GONE'), reply_markup=ReplyKeyboardRemove())
        return
    if m.contact.user_id != uid:  # boshqa odamning kontakti emas, o'zining raqami bo'lishi shart
        await m.answer(t(lang, 'K1_NOT_OWN'))
        return
    store.set_phone(uid, m.contact.phone_number)
    await m.answer(t(lang, 'K1_OK'), reply_markup=ReplyKeyboardRemove())
    await m.answer(t(lang, 'LIABILITY'), reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=t(lang, 'LIABILITY_BTN'), callback_data=f'liab:{case_id}')]]))


# ---------- K2: AI ishonchlilik bali ----------
@router.callback_query(F.data.startswith('liab:'))
async def on_liability(c: CallbackQuery) -> None:
    await c.answer()
    uid = c.from_user.id
    lang = store.lang(uid)
    case = store.get_case(int(c.data.split(':', 1)[1]), uid)
    if case is None or case['status'] != 'k1_wait' or not store.has_phone(uid):
        return
    store.set_status(case['id'], 'k2_wait')
    await run_k2(c.bot, uid, case, lang)


async def add_details(m: Message, case_id: int, lang: str) -> None:
    """2-kalit past ball bergach foydalanuvchi yozgan aniqlashtirish: murojaatga qoʻshiladi va ball qayta hisoblanadi
    (yangi murojaat ochilmaydi)."""
    uid = m.from_user.id
    store.set_pending(uid, None)
    case = store.get_case(case_id, uid)
    if case is None or case['status'] != 'k2_more':
        await m.answer(t(lang, 'CASE_GONE'))
        return
    if case['text'].count('Qoʻshimcha maʼlumot:') >= K2_MAX_TRIES:  # K2 "oʻtguncha urin" eshigiga aylanmasin
        store.set_status(case_id, 'answered')
        await m.answer(t(lang, 'K2_TRIES'))
        return
    store.append_text(case_id, m.text.strip()[:3000])
    store.set_status(case_id, 'k2_wait')
    await run_k2(m.bot, uid, store.get_case(case_id, uid), lang)


async def run_k2(bot: Bot, uid: int, case: dict, lang: str) -> None:
    msg = await bot.send_message(uid, t(lang, 'K2_CHECKING'))
    c = SimpleNamespace(bot=bot)
    try:
        out = await llm.chat(SCORE_SYSTEM, SCORE_USER.format(text=case['text'][:5000], kind=case['kind']),
                             model=config.MODEL_FAST, json_mode=True, max_tokens=400)
        s = llm.parse_json(out)
        score = max(0, min(100, int(s.get('ball', 0))))
    except (llm.LLMError, ValueError, TypeError) as e:
        log.error('K2 xatosi (case %s): %s', case['id'], e)
        store.set_status(case['id'], 'k1_wait')
        await msg.edit_text(t(lang, 'ANALYSIS_FAILED'))
        return
    store.set_score(case['id'], score)
    if score < MIN_SCORE:
        # Murojaat yopilmaydi: keyingi matn shu murojaatga qoʻshiladi va 2-kalit qayta tekshiriladi
        store.set_status(case['id'], 'k2_more')
        store.set_pending(uid, {'case': case['id'], 'stage': 'k2_more'})
        missing = '\n'.join(f'• {esc(x)}' for x in (s.get('yetishmaydi') or [])[:4] if isinstance(x, str))
        await msg.edit_text(t(lang, 'K2_LOW', score=score, reason=esc(s.get('sabab')), missing=missing or '—'))
        return
    await msg.edit_text(t(lang, 'K2_OK', score=score))
    # K3: klinika guruhiga
    store.set_status(case['id'], 'k3_wait')
    await c.bot.send_message(config.CLINIC_CHAT_ID, clinic_card(case, score, s.get('sabab'), urgent=False),
                             reply_markup=clinic_kb(case['id']), disable_web_page_preview=True)
    await c.bot.send_message(uid, t(lang, 'K3_SENT'))


def clinic_card(case: dict, score, reason, urgent: bool) -> str:
    data = json.loads(case['analysis'] or '{}')
    ans = data.get('answer', {})
    cites = ', '.join(f'<a href="{html.escape(x.get("link", ""))}">{esc(x["abbr"])} {esc(x["num"])}</a>'
                      for x in data.get('cited', []))
    head = '🆘 <b>SHOSHILINCH: foydalanuvchi javob bermayapti</b>\n' if urgent else ''
    return (f'{head}📨 <b>Murojaat #{case["id"]}</b> · {pipeline.LEVELS.get(case["level"], "")} · '
            f'{t('uz', 'ROLES').get(case["role"], "")}\n'
            f'🔑 K1 telefon: ✅ · K2 AI bali: <b>{esc(score)}</b>/100 ({esc(reason)})\n\n'
            f'<b>Fuqaro so\'zlari:</b>\n<i>{esc(case["text"][:1500])}</i>\n\n'
            f'<b>Tahlil:</b> {esc(ans.get("vaziyat"))}\n<b>Moddalar:</b> {cites or "—"}\n\n'
            f'K3: yurist, tasdiqlaysizmi?')


# ---------- K3: klinika yuristi ----------
@router.callback_query(F.data.startswith('k3:'))
async def on_clinic_decision(c: CallbackQuery) -> None:
    if c.message is None or c.message.chat.id != config.CLINIC_CHAT_ID:
        await c.answer('Bu tugma faqat klinika guruhida ishlaydi', show_alert=True)
        return
    member = await c.bot.get_chat_member(config.CLINIC_CHAT_ID, c.from_user.id)
    if member.status not in ADMIN:
        await c.answer('Faqat klinika yuristlari (guruh adminlari) qaror qabul qila oladi', show_alert=True)
        return
    _, action, case_id = c.data.split(':', 2)
    case = store.get_case_any(int(case_id))
    if case is None or case['status'] != 'k3_wait':
        await c.answer('Bu murojaat bo\'yicha qaror allaqachon qabul qilingan', show_alert=True)
        return
    await c.answer()
    lawyer = esc(c.from_user.full_name)
    uid = case['user_id']
    lang = store.lang(uid)
    if action == 'ok':
        store.set_status(case['id'], 'sent')
        app_text = case['application'] or await _application(case)
        await c.bot.send_message(config.AUTHORITY_CHAT_ID, authority_card(case, app_text), disable_web_page_preview=True)
        await c.message.edit_text(c.message.html_text + f'\n\n✅ <b>Tasdiqlandi</b> ({lawyer}) va idoraga yuborildi.')
        await c.bot.send_message(uid, t(lang, 'K3_APPROVED', id=case['id']))
    elif action == 'no':
        store.set_status(case['id'], 'rejected')
        await c.message.edit_text(c.message.html_text + f'\n\n❌ <b>Rad etildi</b> ({lawyer}).')
        await c.bot.send_message(uid, t(lang, 'K3_REJECTED', id=case['id']))
    else:
        store.set_status(case['id'], 'answered')
        await c.message.edit_text(c.message.html_text + f'\n\n❔ <b>Aniqlashtirish so\'raldi</b> ({lawyer}).')
        await c.bot.send_message(uid, t(lang, 'K3_ASK', id=case['id']))


async def _application(case: dict) -> str:
    data = json.loads(case['analysis'] or '{}')
    cited = [(a, x.get('why', '')) for x in data.get('cited', []) if (a := search.get(x['abbr'], x['num']))]
    try:
        text = await pipeline.application(case['text'], case['role'] or 'boshqa', data.get('answer', {}), cited)
    except llm.LLMError:
        text = case['text']
    store.save_application(case['id'], text)
    return text


def authority_card(case: dict, app_text: str) -> str:
    return (f'🏛 <b>Yangi murojaat #{case["id"]}</b> (Huquqiy Navigator orqali)\n'
            f'Tekshiruv: K1 telefon ✅ · K2 AI bali {esc(case["score"])}/100 ✅ · K3 Yuridik klinika yuristi ✅\n\n'
            f'<pre>{esc(app_text[:3500])}</pre>')


# ---------- Javobsiz 🔴 murojaat ----------
@router.callback_query(F.data.startswith('close:'))
async def on_close(c: CallbackQuery) -> None:
    await c.answer()
    _, action, case_id = c.data.split(':', 2)
    lang = store.lang(c.from_user.id)
    case = store.get_case(int(case_id), c.from_user.id)
    if case is None:
        return
    if action == 'yes':
        store.set_status(case['id'], 'closed')
        await c.message.edit_text(t(lang, 'CLOSED'))
    else:
        store.touch(case['id'])
        await c.message.edit_text(t(lang, 'NOT_CLOSED'))


async def inactivity_watcher(bot: Bot) -> None:
    """Har daqiqada: 🔴 javob berilgan, lekin yopilmagan murojaatlar.
    1) INACTIVITY_MINUTES dan keyin foydalanuvchidan holat so'raladi;
    2) yana shuncha vaqt javob bo'lmasa — klinikaga "shoshilinch". Idoraga avtomatik yuborilmaydi."""
    wait = config.INACTIVITY_MINUTES * 60
    while True:
        try:
            now = time.time()
            for case in (store.stale_cases(('jiddiy', 'xavf'), 'answered', now - wait)
                         + store.stale_cases(('jiddiy', 'xavf'), 'k2_more', now - wait)):
                lang = store.lang(case['user_id'])
                store.set_status(case['id'], 'reminded')
                await bot.send_message(case['user_id'], t(lang, 'REMINDER', id=case['id']),
                                       reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                                           InlineKeyboardButton(text=t(lang, 'CLOSE_YES'), callback_data=f'close:yes:{case["id"]}'),
                                           InlineKeyboardButton(text=t(lang, 'CLOSE_NO'), callback_data=f'close:no:{case["id"]}')]]))
            for case in store.stale_cases(('jiddiy', 'xavf'), 'reminded', now - wait):
                store.set_status(case['id'], 'urgent')
                if config.CLINIC_CHAT_ID is not None:
                    full = store.get_case_any(case['id'])
                    await bot.send_message(config.CLINIC_CHAT_ID, clinic_card(full, full['score'] or '—', 'foydalanuvchi javob bermadi', urgent=True),
                                           disable_web_page_preview=True)
                log.warning('Case %s: javobsiz, klinikaga shoshilinch belgisi bilan yuborildi', case['id'])
        except Exception:  # noqa: BLE001 — kuzatuvchi to'xtab qolmasin
            log.exception('inactivity_watcher xatosi')
        await asyncio.sleep(60)
