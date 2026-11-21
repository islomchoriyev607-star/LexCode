"""data/md/*.md → data/lex.db (SQLite FTS5, har modda alohida qator).
Qidiruv normallashtirilgan ustunlar (title_n, body_n) bo'yicha ishlaydi — bot/textnorm.py.
usage: python tools/build_index.py"""
import json, os, re, sqlite3, sys, time, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding='utf-8')
from bot.textnorm import normalize  # noqa: E402

MD, DB, LAWS = ROOT / 'data' / 'md', ROOT / 'data' / 'lex.db', ROOT / 'data' / 'laws.txt'
TMP = DB.with_suffix('.db.tmp')
# Hujjat oxiridagi imzo / sana bloki (masalan "**Oʻzbekiston Respublikasi Prezidenti I. KARIMOV**")
SIGNATURE = re.compile(r'\n\*\*[^\n]*(Prezidenti|Toshkent sh\.|Raisi)[^\n]*\*\*.*$', re.S)

short, errors = {}, []
for i, raw in enumerate(LAWS.read_text(encoding='utf-8').splitlines(), 1):
    line = raw.strip()
    if not line or line.startswith('#'):
        continue
    parts = [p.strip() for p in line.split('|', 2)]
    if len(parts) != 3 or not re.fullmatch(r'-?\d+', parts[0]):
        errors.append(f'laws.txt {i}-qator noto\'g\'ri ("ID | qisqa nom | to\'liq nom" kerak): {raw}')
        continue
    doc_id, abbr, name = parts
    if abbr in {a for a, _ in short.values()}:
        errors.append(f'laws.txt {i}-qator: "{abbr}" qisqa nomi takrorlangan')
        continue
    short[doc_id.lstrip('-')] = (abbr, name)
if errors:
    sys.exit('\n'.join(errors))

t = time.time()
TMP.unlink(missing_ok=True)
con = sqlite3.connect(TMP)
con.execute("CREATE VIRTUAL TABLE m USING fts5(abbr UNINDEXED, law UNINDEXED, num UNINDEXED, title UNINDEXED, "
            "body UNINDEXED, link UNINDEXED, title_n, body_n, tokenize='unicode61 remove_diacritics 2')")
con.execute('CREATE TABLE docs (abbr TEXT PRIMARY KEY, law TEXT, source TEXT, fetched TEXT, articles INTEGER)')
total = 0
for f in sorted(MD.glob('*.md')):
    doc_id = f.stem.split('_')[0]
    if doc_id not in short:
        print('  ! laws.txt da yo\'q, o\'tkazildi:', f.name)
        continue
    abbr, name = short[doc_id]
    s = f.read_text(encoding='utf-8')
    meta = {k: json.loads(v) for k, v in re.findall(r'^(\w+): (.*)$', s.split('\n---\n', 1)[0], re.M)}
    n = 0
    for part in re.split(r'\n### ', s)[1:]:
        head, _, rest = part.partition('\n')
        link = re.search(r'<!-- (\S+) -->', rest)
        body = re.sub(r'<!--.*?-->', '', rest.split('\n## ')[0]).strip()
        body = SIGNATURE.sub('', body).strip()
        tail = body.rfind('Prezidenti')
        if tail > len(body) - 300 and tail != -1:  # oxirgi moddaga yopishgan imzo qatori
            body = body[:body.rfind('\n', 0, tail)].strip() if '\n' in body[:tail] else body
        # "184 5 -modda" = 184⁵-modda (lex.uz da yuqori indeks) → "184-5"
        m = re.match(r'(\d+)(?:\s*[-–]?\s*(\d+))?\s*-\s*modda', head.strip())
        num = '-'.join(g for g in m.groups() if g) if m else ''
        if not num:
            print(f'  ! {abbr}: modda raqami aniqlanmadi: {head[:60]}')
        title = re.sub(r'^(\d+)\s+(\d+)\s*-modda', r'\1-\2-modda', head.strip())
        con.execute('INSERT INTO m VALUES (?,?,?,?,?,?,?,?)',
                    (abbr, name, num, title, body, link.group(1) if link else '', normalize(title), normalize(body)))
        n += 1
    con.execute('INSERT INTO docs VALUES (?,?,?,?,?)', (abbr, name, meta.get('source'), meta.get('fetched'), n))
    print(f'  {abbr:5} {n:4} modda | {name}')
    total += n
con.commit()
con.close()
try:
    os.replace(TMP, DB)
except PermissionError:
    sys.exit(f'{DB.name} band (bot ishlayaptimi?). Botni to\'xtatib, qayta ishga tushiring. Yangi baza: {TMP.name}')
print(f'Jami {total} modda, {time.time() - t:.1f} s → {DB.relative_to(ROOT)}')
