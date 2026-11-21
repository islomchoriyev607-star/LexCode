"""Navigator oqimini Telegram'siz sinash: soxta Bot xabarlarni yigʻadi. Haqiqiy AI chaqiriladi (3-4 soʻrov).
usage: python tools/test_navflow.py [uz|ru|en]"""
import asyncio, re, sys, time, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding='utf-8')
from bot import config, llm, navflow, store

LANG = sys.argv[1] if len(sys.argv) > 1 else 'uz'
UID = 999000222


class Msg:
    def __init__(self, bot, text, kb=None):
        self.bot, self.text, self.kb = bot, text, kb
    async def edit_text(self, text, reply_markup=None, **kw):
        self.bot.log('EDIT', text, reply_markup)
        return self
    async def delete(self):
        pass


class FakeBot:
    def __init__(self):
        self.out = []
    def log(self, kind, text, kb):
        btns = [[getattr(b, 'text', '') for b in row] for row in (getattr(kb, 'inline_keyboard', None) or getattr(kb, 'keyboard', None) or [])]
        self.out.append((kind, text, kb))
        print(f'[{kind}] ' + re.sub(r'<[^>]+>', '', text)[:400].replace('\n', ' ⏎ ') + (f'\n   tugmalar: {btns}' if btns else ''))
    async def send_message(self, uid, text, reply_markup=None, **kw):
        self.log('MSG', text, reply_markup); return Msg(self, text, reply_markup)
    async def send_chat_action(self, *a, **kw):
        pass
    async def send_document(self, uid, doc, caption=None, **kw):
        self.log('PDF', f'{doc.filename} ({len(doc.data)} bayt) — {caption}', None)


async def main():
    bot = FakeBot()
    store.set_lang(UID, LANG); store.set_consent(UID)
    texts = {'uz': "Ish beruvchi 2 oydan beri ish haqimni bermayapti, so'rasam ishdan haydayman deyapti.",
             'ru': 'Работодатель 2 месяца не платит зарплату, а если спрашиваю — грозит уволить.',
             'en': "My employer hasn't paid my salary for 2 months and threatens to fire me if I ask."}
    cid = store.create_case(UID, texts[LANG], 'text'); store.set_case_role(cid, UID, 'xodim')
    t0 = time.time()
    await navflow.start_after_role(bot, UID, cid, 'xodim', LANG)
    case = store.nav_case(cid, UID)
    for i in range(len(case['questions'])):  # har savolga birinchi variant bilan javob
        await navflow.record_answer(bot, UID, cid, i, (case['questions'][i]['opts'] or ['Ha'])[0], LANG)
    store.nav_update(cid, district='Toshkent, Chilonzor')
    await navflow.run_analysis(bot, UID, cid, LANG)
    case = store.nav_case(cid, UID)
    print(f'\n== tahlilgacha {time.time() - t0:.1f}s; yoʻllar: {[r["nom"] for r in case["routes"]]}')
    assert case['routes'], 'yoʻl topilmadi'
    store.nav_update(cid, route=0, step=0, status='nav')
    await navflow.send_step(bot, UID, cid, LANG)
    # qadamni bajarish: muddatli boʻlsa — waiting, aks holda keyingisi
    for _ in range(6):
        case = store.nav_case(cid, UID)
        if case['status'] != 'nav':
            break
        s = case['routes'][0]['steps'][case['step']]
        if s['kun']:
            store.nav_update(cid, status='waiting', next_check=time.time() - 1)
            print(f'== {case["step"] + 1}-qadam muddatli ({s["kun"]} kun) → waiting; watcher tekshiradi')
            break
        await navflow.advance(bot, UID, case, LANG)
    due = store.due_checks(time.time()); print('== muddati kelgan:', due)
    # PDF
    pdf_text = 'Test ariza\nMehnat kodeksining 333-moddasi'
    print('== PDF:', len(navflow.make_pdf(pdf_text)), 'bayt')
    store.con().execute('DELETE FROM cases WHERE user_id = ?', (UID,)); store.con().execute('DELETE FROM users WHERE user_id = ?', (UID,)); store.con().commit()
    await llm.client().aclose()

asyncio.run(main())
