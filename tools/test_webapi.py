"""Mini App API ni lokal sinash: initData imzosi (to'g'ri / soxta / eski), endpointlar, sahifa."""
import asyncio, hashlib, hmac, json, sys, time, pathlib
from urllib.parse import urlencode
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding='utf-8')
from aiohttp.test_utils import TestClient, TestServer
from bot import config, webapi, llm

def sign(user_id, auth_date=None, token=None):
    pairs = {'auth_date': str(auth_date or int(time.time())), 'query_id': 'AAE', 'user': json.dumps({'id': user_id, 'first_name': 'Test'})}
    dcs = '\n'.join(f'{k}={v}' for k, v in sorted(pairs.items()))
    secret = hmac.new(b'WebAppData', (token or config.BOT_TOKEN).encode(), hashlib.sha256).digest()
    pairs['hash'] = hmac.new(secret, dcs.encode(), hashlib.sha256).hexdigest()
    return urlencode(pairs)

ok = True
def check(name, cond):
    global ok; ok &= bool(cond); print(('✅' if cond else '❌'), name)

async def main():
    UID = 999000111
    check('to\'g\'ri imzo qabul qilinadi', webapi.verify_init_data(sign(UID)) is not None)
    check('soxta token bilan imzo rad etiladi', webapi.verify_init_data(sign(UID, token='1:FAKE')) is None)
    check('25 soat oldingi imzo rad etiladi', webapi.verify_init_data(sign(UID, auth_date=int(time.time()) - 90000)) is None)
    check('o\'zgartirilgan user rad etiladi', webapi.verify_init_data(sign(UID).replace('Test', 'Hack')) is None)
    async with TestClient(TestServer(webapi.make_app(bot=None))) as c:
        r = await c.get('/'); html = await r.text()
        check(f'sahifa 200, doctype va API manzili bor ({len(html)} belgi)', r.status == 200 and html.startswith('<!doctype html>') and "LEXNAV_API='/api'" in html)
        r = await c.get('/api/laws'); check('imzosiz /api → 401', r.status == 401)
        H = {'X-Telegram-Init-Data': sign(UID)}
        r = await c.get('/api/laws', headers=H); d = await r.json()
        check(f'/api/laws → {len(d.get("laws", []))} ta qonun', r.status == 200 and len(d['laws']) == 7)
        from bot import store
        store.revoke_consent(UID)
        r = await c.post('/api/analyze', json={'text': 'test', 'role': 'talaba'}, headers=H); d = await r.json()
        check('roziliksiz tahlil → 403 need_consent', r.status == 403 and d.get('need_consent'))
        r = await c.post('/api/consent', json={}, headers=H); check('rozilik → 200', r.status == 200)
        if '--ai' in sys.argv:
            t = time.time()
            r = await c.post('/api/analyze', json={'text': "Universitetda dekanatga ariza berdim, bir oy bo'ldi javob yo'q.", 'role': 'talaba'}, headers=H); d = await r.json()
            check(f'tahlil {time.time()-t:.1f}s → {d.get("level")}, manbalar {[x["law"][:12]+" "+x["num"] for x in d.get("cited", [])]}', r.status == 200 and d.get('cited'))
            r = await c.get('/api/cases', headers=H); d2 = await r.json(); check(f'/api/cases → {len(d2["cases"])} ta', r.status == 200 and d2['cases'])
            r = await c.post('/api/application', json={'case_id': d['case_id']}, headers={'X-Telegram-Init-Data': sign(UID + 1)})
            check('boshqa foydalanuvchi arizani ololmaydi → 404', r.status == 404)
        store.con().execute('DELETE FROM cases WHERE user_id = ?', (UID,)); store.con().execute('DELETE FROM users WHERE user_id = ?', (UID,)); store.con().commit()
    await llm.client().aclose()

asyncio.run(main())
sys.exit(0 if ok else 1)
