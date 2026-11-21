"""Telegramga ketadigan har bir soʻrovda oʻzbekcha matnni foydalanuvchi yozuviga oʻgiradi (kirill / yangi lotin).
Bot kodi va AI amaldagi lotin yozuvida ishlaydi; oʻgirish faqat chiqishda — bitta joyda, hech narsa tushib qolmaydi.
Qabul qiluvchi: soʻrovdagi chat_id, boʻlmasa (callback javobi) — joriy update foydalanuvchisi."""
import contextvars
from typing import Any

from aiogram.client.session.middlewares.base import BaseRequestMiddleware

from . import store
from .script import convert

_UID: contextvars.ContextVar[int | None] = contextvars.ContextVar('lexnav_uid', default=None)


async def remember_user(handler, event, data: dict[str, Any]):
    """Dispatcher outer middleware: update qaysi foydalanuvchidan kelganini eslab qoladi."""
    user = data.get('event_from_user')
    token = _UID.set(user.id if user else None)
    try:
        return await handler(event, data)
    finally:
        _UID.reset(token)


def _markup(m, sc: str):
    if m is None:
        return m
    rows_attr = 'inline_keyboard' if hasattr(m, 'inline_keyboard') else 'keyboard' if hasattr(m, 'keyboard') else None
    if rows_attr is None:
        upd = {}
        if getattr(m, 'input_field_placeholder', None):
            upd['input_field_placeholder'] = convert(m.input_field_placeholder, sc)
        return m.model_copy(update=upd) if upd else m
    rows = [[b.model_copy(update={'text': convert(b.text, sc)}) for b in row] for row in getattr(m, rows_attr)]
    upd = {rows_attr: rows}
    if getattr(m, 'input_field_placeholder', None):
        upd['input_field_placeholder'] = convert(m.input_field_placeholder, sc)
    return m.model_copy(update=upd)


class ScriptMiddleware(BaseRequestMiddleware):
    async def __call__(self, make_request, bot, method):
        chat = getattr(method, 'chat_id', None)
        uid = chat if isinstance(chat, int) else _UID.get()
        try:
            sc = store.script(uid)
        except Exception:  # noqa: BLE001 — oʻgirish xatosi xabarni toʻxtatmasin
            sc = None
        if sc:
            upd = {}
            for f in ('text', 'caption'):
                v = getattr(method, f, None)
                if isinstance(v, str):
                    upd[f] = convert(v, sc)
            if getattr(method, 'reply_markup', None) is not None:
                upd['reply_markup'] = _markup(method.reply_markup, sc)
            mb = getattr(method, 'menu_button', None)
            if mb is not None and isinstance(getattr(mb, 'text', None), str):
                upd['menu_button'] = mb.model_copy(update={'text': convert(mb.text, sc)})
            if upd:
                method = method.model_copy(update=upd)
        return await make_request(bot, method)
