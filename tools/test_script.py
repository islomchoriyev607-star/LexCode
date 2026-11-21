"""Yozuv oʻgirish testi: kirill / yangi lotin; Telegram soʻrov middleware (xabar, tugma, callback, menyu)."""
import asyncio
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.stdout.reconfigure(encoding='utf-8')

from aiogram.methods import AnswerCallbackQuery, SendMessage, SetChatMenuButton  # noqa: E402
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, MenuButtonWebApp, WebAppInfo  # noqa: E402

from bot import outscript, store  # noqa: E402
from bot.navflow import make_pdf  # noqa: E402
from bot.script import convert  # noqa: E402

ok = True


def check(name, got, want):
    global ok
    good = got == want
    ok &= good
    print(('✅' if good else '❌'), name, '→', got)


check('kirill', convert('Oʻzbekiston, shikoyat, yoʻl, taʼlim, ekran', 'cyrl'), 'Ўзбекистон, шикоят, йўл, таълим, экран')
check('yangi lotin', convert('Oʻzbekiston, gʻisht, shikoyat, chop etish', 'latn'), 'Özbekiston, ğişt, şikoyat, çop etiş')
check('HTML/havola tegilmaydi', convert('<a href="https://lex.uz/docs/1">Mehnat kodeksi</a> {n} kun', 'cyrl'),
      '<a href="https://lex.uz/docs/1">Меҳнат кодекси</a> {n} кун')

U_C, U_L, U_R = 999000501, 999000502, 999000503
store.set_lang(U_C, 'uz'); store.set_script(U_C, 'cyrl')
store.set_lang(U_L, 'uz'); store.set_script(U_L, 'latn')
store.set_lang(U_R, 'ru')
sent = []


async def fake(bot, method):
    sent.append(method)
    return True


async def run():
    mw = outscript.ScriptMiddleware()
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='✅ Bajardim', callback_data='x')]])
    await mw(fake, None, SendMessage(chat_id=U_C, text='<b>Yoʻl</b> tanlang', reply_markup=kb))
    await mw(fake, None, SendMessage(chat_id=U_L, text='Shikoyat yoʻllang', reply_markup=kb))
    await mw(fake, None, SendMessage(chat_id=U_R, text='Shikoyat'))
    await mw(fake, None, SendMessage(chat_id=-100123, text='Shikoyat'))  # klinika guruhi — oʻzgarmaydi
    tok = outscript._UID.set(U_C)
    await mw(fake, None, AnswerCallbackQuery(callback_query_id='1', text='Donat hali mavjud emas', show_alert=True))
    outscript._UID.reset(tok)
    await mw(fake, None, SetChatMenuButton(chat_id=U_C, menu_button=MenuButtonWebApp(text='Ilova', web_app=WebAppInfo(url='https://x.y'))))

asyncio.run(run())
check('xabar kirill', sent[0].text, '<b>Йўл</b> танланг')
check('tugma kirill', sent[0].reply_markup.inline_keyboard[0][0].text, '✅ Бажардим')
check('xabar yangi lotin', sent[1].text, 'Şikoyat yöllang')
check('rus foydalanuvchi — oʻzgarmaydi', sent[2].text, 'Shikoyat')
check('guruh — oʻzgarmaydi', sent[3].text, 'Shikoyat')
check('callback ogohlantirish', sent[4].text, 'Донат ҳали мавжуд эмас')
check('menyu tugmasi', sent[5].menu_button.text, 'Илова')
for u in (U_C, U_L, U_R):
    store.con().execute('DELETE FROM users WHERE user_id = ?', (u,))
store.con().commit()

pdf = make_pdf('Hokimga\n[F.I.Sh.] dan\n\nARIZA\n\nMen ish haqimni olmadim va shikoyat qilaman, chunki bu qonunga zid.\n\nSana: [sana]', 'cyrl')
check('PDF kirill yasaldi', len(pdf) > 5000, True)
print('NATIJA:', 'hammasi oʻtdi' if ok else 'XATO BOR')
