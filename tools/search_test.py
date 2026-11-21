import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding='utf-8')
from bot.search import search, get
for q in sys.argv[1:]:
    print('Q:', q)
    for a in search(q, 4):
        print(f'   {a.abbr:5} {a.num:>6} | {a.title[:90]}')
print('get(FK-1, 326):', get('FK-1', '326').title if get('FK-1', '326') else None, '| get(FK-1, 9999):', get('FK-1', '9999'))
