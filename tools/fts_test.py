"""MD fayllarni modda bo'yicha bo'lib SQLite FTS5 ga joylaydi va qidiruvni o'lchaydi."""
import sqlite3, glob, re, sys, time, json
sys.stdout.reconfigure(encoding='utf-8')
md_dir, db = sys.argv[1], sys.argv[2]
t = time.time()
con = sqlite3.connect(db)
con.execute('DROP TABLE IF EXISTS m')
con.execute("CREATE VIRTUAL TABLE m USING fts5(doc, title, body, link UNINDEXED, tokenize='unicode61 remove_diacritics 2')")
n = 0
for f in glob.glob(md_dir + '/*.md'):
    s = open(f, encoding='utf-8').read()
    doc = json.loads(re.search(r'^title: (.*)$', s, re.M).group(1))
    for part in re.split(r'\n### ', s)[1:]:
        head, _, rest = part.partition('\n')
        link = re.search(r'<!-- (\S+) -->', rest)
        body = re.sub(r'<!--.*?-->', '', rest.split('\n## ')[0]).strip()
        con.execute('INSERT INTO m VALUES (?,?,?,?)', (doc, head, body, link.group(1) if link else ''))
        n += 1
con.commit()
print(f'{n} modda indekslandi, {time.time()-t:.2f}s')
for q in ['ish haqi kechiktirilsa', 'mehnat shartnomasini bekor qilish ish beruvchi tashabbusi',
          'ijara shartnomasi muddatidan oldin bekor qilish', 'neustoyka kamaytirish', 'sifatsiz tovar qaytarish']:
    t = time.time()
    words = ' OR '.join(w + '*' for w in re.findall(r'\w{4,}', q))
    rows = con.execute('SELECT doc, title, link FROM m WHERE m MATCH ? ORDER BY bm25(m, 1.0, 4.0, 1.0) LIMIT 3', (words,)).fetchall()
    print(f'\nQ: {q}  ({(time.time()-t)*1000:.0f} ms)')
    for d, ti, l in rows:
        print('  -', d[12:60], '|', ti[:90])
