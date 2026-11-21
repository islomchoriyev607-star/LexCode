"""Mini App navigator API sinovi: start → navigate → route → step(done/ok) → case; begona foydalanuvchi himoyasi."""
import asyncio, sys, time, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding='utf-8')
from aiohttp.test_utils import TestClient, TestServer
import hashlib, hmac, json
from urllib.parse import urlencode
from bot import config, llm, store, webapi


def sign(user_id):
    pairs = {'auth_date': str(int(time.time())), 'user': json.dumps({'id': user_id, 'first_name': 'Test'})}
    dcs = '\n'.join(f'{k}={v}' for k, v in sorted(pairs.items()))
    secret = hmac.new(b'WebAppData', config.BOT_TOKEN.encode(), hashlib.sha256).digest()
    pairs['hash'] = hmac.new(secret, dcs.encode(), hashlib.sha256).hexdigest()
    return urlencode(pairs)

ok = True


def check(name, cond):
    global ok
    ok &= bool(cond)
    print(('✅' if cond else '❌'), name)


async def main():
    UID, LANG = 999000444, (sys.argv[1] if len(sys.argv) > 1 else 'uz')
    store.set_consent(UID)
    H = {'X-Telegram-Init-Data': sign(UID)}
    async with TestClient(TestServer(webapi.make_app(bot=None))) as c:
        t = time.time()
        r = await c.post('/api/nav/start', json={'text': "Do'kondan telefon oldim, 3 kunda buzildi, sotuvchi qaytarib olmayapti.", 'role': 'xaridor', 'lang': LANG}, headers=H)
        d = await r.json()
        check(f'start {time.time() - t:.1f}s → case {d.get("case_id")}, savollar: {[q["q"] for q in d.get("questions", [])]}', r.status == 200 and d.get('case_id'))
        cid = d['case_id']
        answers = [{'q': q['q'], 'a': (q['opts'] or ['Ha'])[0]} for q in d['questions']]
        t = time.time()
        r = await c.post('/api/nav/navigate', json={'case_id': cid, 'answers': answers, 'district': 'Toshkent, Yunusobod', 'lang': LANG}, headers=H)
        s = await r.json()
        check(f'navigate {time.time() - t:.1f}s → {s.get("level")}, yoʻllar: {[x["nom"] for x in s.get("routes", [])]}', r.status == 200 and s.get('routes'))
        r = await c.post('/api/nav/route', json={'case_id': cid, 'route': 0, 'lang': LANG}, headers=H)
        s = await r.json()
        cur = s.get('current') or {}
        check(f'route → {cur.get("i")}/{cur.get("n")}-qadam: {cur.get("nima", "")[:70]} | xarita: {bool(cur.get("map_url"))}', r.status == 200 and cur)
        for _ in range(6):
            r = await c.post('/api/nav/step', json={'case_id': cid, 'action': 'done', 'lang': LANG}, headers=H)
            s = await r.json()
            print('   done →', s['result'], '| holat:', s['status'])
            if s['result']['kind'] != 'next':
                break
        r = await c.post('/api/nav/step', json={'case_id': cid, 'action': 'ok', 'lang': LANG}, headers=H)
        s = await r.json()
        check(f'natija ok → {s["result"]["kind"]}, holat {s["status"]}', s['result']['kind'] == 'closed' and s['status'] == 'closed')
        r = await c.get(f'/api/nav/case?id={cid}&lang={LANG}', headers=H)
        check('case GET → 200', r.status == 200)
        r = await c.get(f'/api/nav/case?id={cid}', headers={'X-Telegram-Init-Data': sign(UID + 1)})
        check('begona foydalanuvchi murojaatni koʻrolmaydi → 404', r.status == 404)
        r = await c.post('/api/nav/step', json={'case_id': cid, 'action': 'done'}, headers={'X-Telegram-Init-Data': sign(UID + 1)})
        check('begona foydalanuvchi qadamni oʻzgartirolmaydi → 404', r.status == 404)
    store.con().execute('DELETE FROM cases WHERE user_id IN (?, ?)', (UID, UID + 1))
    store.con().execute('DELETE FROM users WHERE user_id IN (?, ?)', (UID, UID + 1)); store.con().commit()
    await llm.client().aclose()

asyncio.run(main())
sys.exit(0 if ok else 1)
