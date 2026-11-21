"""O'zgartirish kiritgan hujjat ichidan asosiy hujjatga havolalarni topadi (asosiy kodeks/qonun ID sini aniqlash uchun).
usage: python lex_refs.py DOC_ID [DOC_ID ...]"""
import sys, re, time, html, urllib.request, collections
sys.stdout.reconfigure(encoding='utf-8')
UA = {'User-Agent': 'Mozilla/5.0 (research client)'}
for i, d in enumerate(sys.argv[1:]):
    if i:
        time.sleep(2)
    s = urllib.request.urlopen(urllib.request.Request(f'https://lex.uz/uz/docs/{d}', headers=UA), timeout=60).read().decode('utf-8', 'replace')
    title = html.unescape(re.search(r'<title>(.*?)</title>', s, re.S).group(1)).strip()
    body = s[s.find('id="divCont"'):]
    cnt = collections.Counter()
    names = {}
    for href, txt in re.findall(r'<a[^>]+href="/uz/docs/(-?\d+)[^"]*"[^>]*>(.*?)</a>', body, re.S):
        cnt[href] += 1
        names.setdefault(href, html.unescape(re.sub(r'<[^>]+>|\s+', ' ', txt)).strip()[:80])
    print(f'===== {d} | {title[:100]}')
    for href, c in cnt.most_common(5):
        print(f'   {href} x{c} | {names[href]}')
