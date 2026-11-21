"""lex.uz da hujjatni nomi bo'yicha qidiradi va ID larini chiqaradi.
usage: python lex_search.py "Jinoyat kodeksi" ["boshqa nom" ...]
lang=4 — o'zbek lotin. So'rovlar orasida 2 soniya."""
import sys, re, time, html, urllib.request, urllib.parse
sys.stdout.reconfigure(encoding='utf-8')
UA = {'User-Agent': 'Mozilla/5.0 (research client)'}
for i, q in enumerate(sys.argv[1:]):
    if i:
        time.sleep(2)
    url = 'https://lex.uz/uz/search/nat?lang=4&searchtitle=' + urllib.parse.quote(q)
    s = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read().decode('utf-8', 'replace')
    print(f'===== {q}')
    seen = set()
    for href, txt in re.findall(r'<a[^>]+href="(/uz/docs/-?\d+)"[^>]*>(.*?)</a>', s, re.S):
        t = html.unescape(re.sub(r'<[^>]+>|\s+', ' ', txt)).strip()
        if href in seen or len(t) < 8:
            continue
        seen.add(href)
        print(' ', href, '|', t[:140])
        if len(seen) >= 8:
            break
