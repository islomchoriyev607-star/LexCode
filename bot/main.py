"""Huquqiy Navigator — Telegram bot. Ishga tushirish: .venv\\Scripts\\python -m bot.main
Tillar: oʻzbek (asosiy), rus, ingliz — bot/i18n.py. Til /start boshida va /til buyrugʻi orqali tanlanadi."""
import asyncio
import html
import json
import logging

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ChatAction, ChatMemberStatus, ChatType, ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart
from aiogram.types import (BotCommand, CallbackQuery, ChatMemberUpdated, ErrorEvent, InlineKeyboardButton,
                           InlineKeyboardMarkup, MenuButtonCommands, MenuButtonWebApp, Message, ReplyKeyboardRemove,
                           WebAppInfo)

from . import config, keys, llm, media, navflow, outscript, pipeline, search, store, webapi
from .script import convert as convert_script
from .i18n import LANG_CHOICES, LANG_FLAGS, LANG_LABELS, LANGS, norm, t

log = logging.getLogger('lexnav')
router = Router()
private = F.chat.type == ChatType.PRIVATE
_seen_groups: set[str] = set()  # albom (media group) uchun bitta javob
_writing: set[int] = set()      # ariza yozilayotgan murojaatlar
MENU_TEXT = {'uz': 'Ilova', 'ru': 'Приложение', 'en': 'App'}


def L(uid: int) -> str:
    return store.lang(uid)


def lang_kb(then: str = 'start') -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=label, callback_data=f'lang:{code}:{then}')]
                                                 for code, label in LANG_CHOICES])


def consent_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=t(lang, 'CONSENT_YES'), callback_data='consent:yes'),
        InlineKeyboardButton(text=t(lang, 'CONSENT_NO_BTN'), callback_data='consent:no'),
    ]])


async def edit_or_send(c: CallbackQuery, text: str, markup=None) -> None:
    """48 soatdan eski xabarni tahrirlab boʻlmaydi — unda yangi xabar yuboriladi."""
    if isinstance(c.message, Message):
        try:
            await c.message.edit_text(text, reply_markup=markup)
            return
        except TelegramBadRequest:
            pass
    await c.bot.send_message(c.from_user.id, text, reply_markup=markup)


def app_url(uid: int, lang: str) -> str:
    sc = store.script(uid)
    return f'{config.WEBAPP_URL}?lang={lang}' + (f'&script={sc}' if sc else '')


async def set_user_menu(bot: Bot, uid: int, lang: str) -> None:
    """Menyu tugmasi (Mini App) foydalanuvchi tilida."""
    if config.WEBAPP_URL.startswith('https://'):
        try:
            await bot.set_chat_menu_button(chat_id=uid, menu_button=MenuButtonWebApp(
                text=MENU_TEXT[lang], web_app=WebAppInfo(url=app_url(uid, lang))))
        except TelegramBadRequest:
            pass


async def refresh_user_menus(bot: Bot) -> None:
    """Tunnel manzili har ishga tushishda oʻzgaradi: shaxsiy (til boʻyicha) menyu tugmalari eski manzilda qolmasin
    (aks holda Mini App 530 xatosini beradi). Telegram cheklovi uchun soʻrovlar orasida qisqa pauza."""
    users = store.users_with_lang()
    for uid, lang in users:
        try:  # botni bloklagan foydalanuvchi qolganlarini toʻxtatmasin
            await set_user_menu(bot, uid, lang if lang in MENU_TEXT else 'uz')
        except Exception as e:  # noqa: BLE001
            log.warning('Menyu tugmasi (%s): %s', uid, type(e).__name__)
        await asyncio.sleep(0.05)
    log.info('Shaxsiy menyu tugmalari yangilandi: %d ta', len(users))


async def send_start(bot: Bot, uid: int) -> None:
    lang = L(uid)
    open_app = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
        text=t(lang, 'WEBAPP_OPEN'), web_app=WebAppInfo(url=app_url(uid, lang)))]]) \
        if config.WEBAPP_URL.startswith('https://') else None
    await bot.send_message(uid, t(lang, 'START'), reply_markup=open_app)
    if store.has_consent(uid):
        await bot.send_message(uid, t(lang, 'CONSENT_OK'))
    else:
        await bot.send_message(uid, t(lang, 'CONSENT'), reply_markup=consent_kb(lang))


@router.message(CommandStart(), private)
async def on_start(m: Message) -> None:
    # Standart: oʻzbek tili, kirill yozuvi. Boshqa til yoki yangi lotin — /til buyrugʻi yoki Mini App sozlamalarida
    uid = m.from_user.id
    if store.get_lang(uid) is None:
        store.set_lang(uid, 'uz')
        store.set_script(uid, 'cyrl')
        await set_user_menu(m.bot, uid, 'uz')
    await send_start(m.bot, uid)


@router.message(Command('til', 'lang', 'language', 'yazyk'), private)
async def on_lang_cmd(m: Message) -> None:
    await m.answer(t(L(m.from_user.id), 'LANG_ASK'), reply_markup=lang_kb('menu'))


@router.callback_query(F.data.startswith('lang:'))
async def on_lang(c: CallbackQuery) -> None:
    await c.answer()
    try:
        _, lang, then = c.data.split(':', 2)
    except ValueError:
        return
    uid = c.from_user.id
    if lang.startswith('uz-'):
        store.set_script(uid, 'latn' if lang == 'uz-latn' else 'cyrl')
    lang = norm(lang[:2])
    store.set_lang(uid, lang)
    await edit_or_send(c, t(lang, 'LANG_SET'))
    await set_user_menu(c.bot, uid, lang)
    if then == 'start':
        await send_start(c.bot, uid)


@router.callback_query(F.data.startswith('consent:'))
async def on_consent(c: CallbackQuery) -> None:
    await c.answer()
    uid = c.from_user.id
    lang = L(uid)
    if c.data == 'consent:yes':
        store.set_consent(uid)
        await edit_or_send(c, t(lang, 'CONSENT') + '\n\n' + t(lang, 'CONSENT_GIVEN'))
        await c.bot.send_message(uid, t(lang, 'CONSENT_OK'))
    else:
        store.revoke_consent(uid)
        await edit_or_send(c, t(lang, 'CONSENT_NO'))


@router.message(Command('yordam', 'help'), private)
async def on_help(m: Message) -> None:
    await m.answer(t(L(m.from_user.id), 'HELP'))


@router.message(Command('maxfiylik', 'privacy'), private)
async def on_privacy(m: Message) -> None:
    await m.answer(t(L(m.from_user.id), 'PRIVACY'))


@router.message(Command('yangi', 'new'), private)
async def on_new(m: Message) -> None:
    store.set_pending(m.from_user.id, None)
    await m.answer(t(L(m.from_user.id), 'NEW'), reply_markup=ReplyKeyboardRemove())


def _supported(m: Message) -> bool:
    if m.text or m.voice or m.audio or m.video_note or m.video or m.photo:
        return True
    mime = (m.document.mime_type or '') if m.document else ''
    return mime.startswith(('image/', 'audio/', 'text/'))


@router.message(private)
async def on_any(m: Message) -> None:
    uid = m.from_user.id
    lang = store.get_lang(uid) or norm(m.from_user.language_code)
    if not store.has_consent(uid):
        # Rozilik boʻlmasa ham hayotga xavf belgisi boʻlsa 102/103 koʻrsatiladi (matn saqlanmaydi, AI chaqirilmaydi)
        if m.text and pipeline.is_danger(m.text):
            await m.answer(t(lang, 'EMERGENCY'))
        await m.answer(t(lang, 'CONSENT_NEED'))
        return
    if m.text and pipeline.is_danger(m.text) and store.get_pending(uid):
        await m.answer(t(lang, 'EMERGENCY'))  # suhbat oʻrtasida ham xavf belgisi — darhol 112/102/103
    pending = store.get_pending(uid)
    if pending and (m.text or m.location) and await navflow.handle_pending(m, pending, lang):
        return  # navigator kutayotgan javob (savolga javob, tuman, savol)
    if pending:
        store.set_pending(uid, None)  # ovoz yoki rasm yuborildi — yangi murojaat sifatida qabul qilinadi
    if m.location:
        await m.answer(t(lang, 'NEW'))
        return
    if m.media_group_id:
        if m.media_group_id in _seen_groups:
            return
        if len(_seen_groups) > 500:
            _seen_groups.clear()
        _seen_groups.add(m.media_group_id)
    if not _supported(m):
        await m.answer(t(lang, 'UNSUPPORTED'))
        return
    file = m.voice or m.audio or m.video_note or m.video or m.document or (m.photo[-1] if m.photo else None)
    if file is not None and (getattr(file, 'file_size', 0) or 0) > config.MAX_FILE_MB * 1024 * 1024:
        await m.answer(t(lang, 'TOO_BIG'))
        return

    status_key = 'TRANSCRIBING' if (m.voice or m.audio or m.video or m.video_note) else \
        'READING' if (m.photo or m.document) else 'RECEIVED'
    status = await m.answer(t(lang, status_key))
    try:
        ex = await media.extract(m.bot, m)
    except TelegramBadRequest as e:
        log.warning('Faylni yuklab boʻlmadi: %s', e)
        await status.edit_text(t(lang, 'TOO_BIG'))
        return
    except media.MediaError:
        await status.edit_text(t(lang, 'NO_SPEECH' if (m.voice or m.audio) else 'UNSUPPORTED'))
        return
    except llm.LLMError as e:
        log.error('AI xatosi: %s', e)
        await status.edit_text(t(lang, 'ERROR'))
        return

    if ex.kind != 'text':
        await status.edit_text(t(lang, 'UNDERSTOOD', text=html.escape(ex.text[:3500], quote=False)))
    else:
        await status.delete()
    if pipeline.is_danger(ex.text):  # hayotga xavf → AI tahlilidan OLDIN 102/103 (CLAUDE.md, 4-qoida)
        await m.answer(t(lang, 'EMERGENCY'))
    case_id = store.create_case(uid, ex.text, ex.kind)
    await m.answer(t(lang, 'ROLE_ASK'), reply_markup=role_kb(case_id, lang))


def role_kb(case_id: int, lang: str) -> InlineKeyboardMarkup:
    items = list(t(lang, 'ROLES').items())
    rows = [[InlineKeyboardButton(text=label, callback_data=f'role:{case_id}:{key}') for key, label in items[i:i + 2]]
            for i in range(0, len(items), 2)]
    return InlineKeyboardMarkup(inline_keyboard=rows)


@router.callback_query(F.data.startswith('role:'))
async def on_role(c: CallbackQuery) -> None:
    await c.answer()
    uid = c.from_user.id
    lang = L(uid)
    roles = t(lang, 'ROLES')
    try:
        _, case_id, role = c.data.split(':', 2)
        case_id = int(case_id)
    except ValueError:
        return
    if role not in roles:
        return
    case = store.set_case_role(case_id, uid, role)
    if case is None:
        await edit_or_send(c, t(lang, 'CASE_GONE'))
        return
    await edit_or_send(c, t(lang, 'ROLE_CHOSEN', role=roles[role]))
    if case['prev_status'] != 'awaiting_role':
        return  # tugma ikki marta bosilsa, oqim qayta boshlanmasin
    try:
        # Navigator: aniqlashtiruvchi savollar → tuman → yoʻllar → qadamlar (bot/navflow.py)
        await navflow.start_after_role(c.bot, uid, case_id, role, lang)
    except Exception as e:  # noqa: BLE001 — har qanday xatoda murojaat qotib qolmasin
        log.error('Navigator xatosi (case %s): %s', case_id, type(e).__name__)
        store.set_status(case_id, 'awaiting_role')
        await c.bot.send_message(uid, t(lang, 'ANALYSIS_FAILED'), reply_markup=role_kb(case_id, lang))


def card_kb(case_id: int, level: str, lang: str) -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(text=t(lang, 'BTN_APP'), callback_data=f'app:{case_id}')]]
    if level in ('jiddiy', 'xavf'):
        rows.append([keys.escalate_kb(case_id, lang)])
    rows.append([InlineKeyboardButton(text=t(lang, 'BTN_NEW'), callback_data='new')])
    return InlineKeyboardMarkup(inline_keyboard=rows)


@router.callback_query(F.data == 'new')
async def on_new_cb(c: CallbackQuery) -> None:
    await c.answer()
    store.set_pending(c.from_user.id, None)
    await c.bot.send_message(c.from_user.id, t(L(c.from_user.id), 'NEW'))


@router.callback_query(F.data.startswith('app:'))
async def on_application(c: CallbackQuery) -> None:
    await c.answer()
    uid = c.from_user.id
    lang = L(uid)
    try:
        case_id = int(c.data.split(':', 1)[1])
    except ValueError:
        return
    case = store.get_case(case_id, uid)
    if case is None or not case['analysis']:
        await c.bot.send_message(uid, t(lang, 'CASE_GONE'))
        return
    if not case['application']:
        if case_id in _writing:  # tugma tez ikki marta bosilsa, ikkinchi ariza yozilmasin
            return
        _writing.add(case_id)
        try:
            status = await c.bot.send_message(uid, t(lang, 'APP_WRITING'))
            await c.bot.send_chat_action(uid, ChatAction.TYPING)
            data = json.loads(case['analysis'])
            cited = [(a, x.get('why', '')) for x in data.get('cited', []) if (a := search.get(x['abbr'], x['num']))]
            try:
                app_text = await pipeline.application(case['text'], case['role'] or 'boshqa', data.get('answer', {}), cited, lang)
            except llm.LLMError as e:
                log.error('Ariza xatosi (case %s): %s', case_id, type(e).__name__)
                await status.edit_text(t(lang, 'APP_FAILED'))
                return
            store.save_application(case_id, app_text)
            await status.delete()
        finally:
            _writing.discard(case_id)
    else:
        app_text = case['application']
    await c.bot.send_message(uid, t(lang, 'APP_HEADER'))
    await c.bot.send_message(uid, f'<pre>{html.escape(app_text[:3800], quote=False)}</pre>')
    await c.bot.send_message(uid, t(lang, 'APP_FOOTER'))


@router.my_chat_member()
async def on_added(e: ChatMemberUpdated) -> None:
    """Bot guruhga qoʻshilganda guruh ID sini aytadi (CLINIC_CHAT_ID / AUTHORITY_CHAT_ID uchun)."""
    if e.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP) and e.new_chat_member.status in (
            ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR):
        log.info('Guruhga qoʻshildim: %s | id=%s', e.chat.title, e.chat.id)
        await e.bot.send_message(e.chat.id, f'Huquqiy Navigator ulandi.\nGuruh ID: <code>{e.chat.id}</code>')


@router.errors()
async def on_error(ev: ErrorEvent) -> bool:
    log.exception('Xatolik: %s', ev.exception)
    cq = ev.update.callback_query
    if cq is not None:
        try:
            await cq.answer()
        except Exception:  # noqa: BLE001
            pass
    msg = ev.update.message or (cq.message if cq and isinstance(cq.message, Message) else None)
    if msg is not None:
        try:
            await msg.answer(t(L(msg.chat.id), 'ERROR'))
        except Exception:  # noqa: BLE001 — xato xabarini yuborib boʻlmasa ham bot toʻxtamasin
            pass
    return True


async def setup_bot_profile(bot: Bot) -> None:
    """Buyruqlar menyusi, tavsif va qisqa tavsif — har bir til uchun (Telegram ilova tiliga qarab koʻrsatadi)."""
    order = ['start', 'yangi', 'til', 'yordam', 'maxfiylik']
    for lang in LANGS:
        code = None if lang == 'uz' else lang
        tx = (lambda s: convert_script(s, 'cyrl')) if lang == 'uz' else (lambda s: s)  # standart — kirill
        cmds = [BotCommand(command=c, description=tx(t(lang, 'CMD')[c])) for c in order]
        try:
            await bot.set_my_commands(cmds, language_code=code)
            await bot.set_my_short_description(tx(t(lang, 'BOT_SHORT')), language_code=code)
            await bot.set_my_description(tx(t(lang, 'BOT_DESC')), language_code=code)
        except TelegramBadRequest as e:
            log.warning('Bot profilini sozlab boʻlmadi (%s): %s', lang, e)
    # Oʻzbek tilidagi Telegram ham standart (uz) matnni oladi
    try:
        await bot.set_my_commands([BotCommand(command=c, description=convert_script(t('uz', 'CMD')[c], 'cyrl')) for c in order],
                                  language_code='uz')
    except TelegramBadRequest:
        pass


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s')
    logging.getLogger('aiogram.event').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    store.con()
    bot = Bot(config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    bot.session.middleware(outscript.ScriptMiddleware())  # oʻzbekcha chiqish — foydalanuvchi yozuvida
    dp = Dispatcher()
    dp.update.outer_middleware(outscript.remember_user)
    dp.include_router(keys.router)  # 3 kalit (kontakt handleri umumiy on_any dan oldin turishi kerak)
    dp.include_router(navflow.router)
    dp.include_router(router)
    watcher = asyncio.create_task(keys.inactivity_watcher(bot))
    nav_watcher = asyncio.create_task(navflow.watcher(bot))
    me = await bot.get_me()
    log.info('Ishga tushdi: @%s (rejim: %s)', me.username, config.MODE)
    web_runner = await webapi.start(bot)
    await setup_bot_profile(bot)
    if config.WEBAPP_URL.startswith('https://'):
        await bot.set_chat_menu_button(menu_button=MenuButtonWebApp(text=MENU_TEXT['uz'], web_app=WebAppInfo(url=config.WEBAPP_URL)))
        log.info('Mini App menyu tugmasi: %s', config.WEBAPP_URL)
        asyncio.create_task(refresh_user_menus(bot))
    else:
        await bot.set_chat_menu_button(menu_button=MenuButtonCommands())
    # Demo paytida bot qayta ishga tushsa, kelgan xabarlar yoʻqolmasin
    await bot.delete_webhook(drop_pending_updates=False)
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        watcher.cancel()
        nav_watcher.cancel()
        await web_runner.cleanup()
        await llm.client().aclose()


if __name__ == '__main__':
    asyncio.run(main())
