"""lex.uz hujjatini Markdown ga o'giradi.
usage: python lex2md.py OUTDIR DOC_ID [DOC_ID ...]
DOC_ID: lotin uchun manfiy (-6257288), kirill uchun musbat.
"""
import sys, time, re, json, urllib.request
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')
UA = {'User-Agent': 'Mozilla/5.0 (research client)'}
SKIP = {'COMMENT', 'CHANGES_ORIGINS', 'INDEXES_ON_REF'}


def fetch(doc_id):
    url = f'https://lex.uz/uz/docs/{doc_id}'
    t = time.time()
    raw = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read()
    return url, raw, time.time() - t


def convert(doc_id, raw, url):
    soup = BeautifulSoup(raw, 'lxml')
    title = soup.title.get_text(strip=True) if soup.title else str(doc_id)
    cont = soup.find(id='divCont')
    lines, n_art, n_head = [], 0, 0
    classifiers = []
    for el in cont.find_all('div', class_=lambda c: c in ('lx_elem', 'lx_no_select')):
        cls = (el.get('class') or [''])[0]
        if cls == 'INDEXES_ON_REF' and not lines:
            v = el.find('span', class_='iorVal')
            if v:
                classifiers.append(v.get_text(' ', strip=True))
        if cls in SKIP or 'lx_elem' not in (el.get('class') or []):
            continue
        body = el.find('div', attrs={'name': re.compile(r'^-?\d+$')})
        if body is None:
            continue
        txt = body.get_text(' ', strip=True)
        txt = re.sub(r'\s+', ' ', txt)
        if not txt:
            continue
        eid = body['name']
        if cls == 'CLAUSE_DEFAULT':
            n_art += 1
            lines.append(f'\n### {txt}\n<!-- {url}#{eid} -->\n')
        elif cls == 'TEXT_HEADER_DEFAULT':
            n_head += 1
            lines.append(f'\n## {txt}\n')
        elif cls.startswith('ACT_') and cls != 'ACT_TEXT':
            lines.append(f'**{txt}**\n')
        else:
            lines.append(txt + '\n')
    fm = {'title': title, 'source': url, 'fetched': time.strftime('%Y-%m-%d'),
          'classifier': classifiers[:3], 'articles': n_art}
    md = '---\n' + '\n'.join(f'{k}: {json.dumps(v, ensure_ascii=False)}' for k, v in fm.items()) + '\n---\n\n'
    md += f'# {title}\n\n' + '\n'.join(lines)
    return title, md, n_art, n_head


out = sys.argv[1]
for i, doc_id in enumerate(sys.argv[2:]):
    if i:
        time.sleep(2)  # saytga yuklama bermaslik uchun
    url, raw, dt = fetch(doc_id)
    t = time.time()
    title, md, n_art, n_head = convert(doc_id, raw, url)
    ct = time.time() - t
    fn = f'{out}/{doc_id.lstrip("-")}_{"lat" if doc_id.startswith("-") else "cyr"}.md'
    open(fn, 'w', encoding='utf-8').write(md)
    words = len(md.split())
    print(f'{doc_id} | {title[:70]} | html {len(raw)/1e6:.2f} MB, yuklash {dt:.1f}s, '
          f'parse {ct:.1f}s | md {len(md.encode())/1e6:.2f} MB, {len(md):,} belgi, {words:,} soz, '
          f'{n_art} modda, {n_head} bob | ~{len(md)//4:,}-{len(md)//3:,} token')
