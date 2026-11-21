"""Modda tekshiruvchisini auditor topgan teshiklar bilan sinash (AI chaqiruvisiz)."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding='utf-8')
from bot import pipeline, search, render

arts = [search.get('MK', '100'), search.get('JK', '168'), search.get('MurQ', '28')]
ok = True


def check(name, cond):
    global ok
    ok &= cond
    print(('✅' if cond else '❌'), name)


ans = {'vaziyat': "Fuqarolik kodeksining 100-moddasiga ko'ra… [A3] bo'yicha", 'huquqlar': "Bitta satr, ro'yxat emas",
       'majburiyatlar': ['168 moddasi', '168‑modda', '168—modda', '168-моддаси', 'modda 168', '100 va 777-moddalar', '184⁵-modda'],
       'manbalar': [{'id': 'A1', 'nima_uchun': "MK 999-moddasiga ko'ra (A2)"}, {'id': 'A9', 'nima_uchun': 'x'}],
       'murojaat': [{'kimga': 'sud', 'qanday': 'ariza', 'qachon': '10-moddada ko\'rsatilgan muddatda'}]}
clean, cited, removed = pipeline.validate(ans, arts)
flat = str(clean)
check('matnda birorta ham modda raqami qolmadi', not pipeline.MODDA_IN_TEXT.search(flat.replace('tegishli modda', '')))
check('nima_uchun ham tozalandi (999 yo\'q)', '999' not in str(cited))
check('[A3]/(A2) belgilari olib tashlandi', '[A3]' not in flat and '(A2)' not in flat)
check('A9 (mavjud emas) manba sifatida rad etildi', any('A9' in r for r in removed) and len(cited) == 1)
check('satr ro\'yxatga aylandi (harflarga bo\'linmadi)', clean['huquqlar'] == ["Bitta satr, ro'yxat emas"])
check('"A4 formatdagi qog\'oz" saqlanadi', pipeline.clean_text("A4 formatdagi qog'ozga yozing")[0] == "A4 formatdagi qog'ozga yozing")

app = ("Mehnat kodeksining 100-moddasiga asosan… Fuqarolik kodeksining 100-moddasi… Jinoyat kodeksi 168-moddasi… "
       "JKning 999-moddasi… 28-moddaga ko'ra… Murojaatlar to'g'risidagi qonunning 28-moddasi")
cited_all = [(a, '') for a in arts]
out = pipeline.check_application(app, cited_all)
print('  ariza:', out)
check('MK 100 qoladi', 'Mehnat kodeksining 100-moddasiga' in out)
check('FK 100 (berilmagan qonun) olib tashlandi', 'Fuqarolik kodeksining 100' not in out)
check('JK 168 qoladi', 'Jinoyat kodeksi 168-moddasi' in out)
check('JK 999 olib tashlandi', '999' not in out)
check('qonunsiz "28-modda" olib tashlandi', "28-moddaga ko'ra" not in out)
check('MurQ 28 qoladi', "qonunning 28-moddasi" in out)

ru = ("В соответствии со статьёй 100 Трудового кодекса… статья 168 Уголовного кодекса… статья 999 Уголовного кодекса… "
      "ст. 28 Закона «Об обращениях физических и юридических лиц»… статья 28 без закона.")
out = pipeline.check_application(ru, cited_all, 'ru')
print('  ariza (ru):', out)
check('RU: MK 100 qoladi', 'статьёй 100 Трудового' in out)
check('RU: JK 168 qoladi', 'статья 168 Уголовного' in out)
check('RU: JK 999 olib tashlandi', '999' not in out)
check('RU: MurQ 28 qoladi (nom moddadan keyin)', 'ст. 28 Закона' in out)
check('RU: qonunsiz "статья 28" olib tashlandi', 'статья 28 без' not in out)
for s, lang in [('Согласно статье 112 УК вы…', 'ru'), ('Under Article 112 of the Criminal Code…', 'en'), ('По ст. 22 и 28…', 'ru')]:
    c2, n = pipeline.clean_text(s, lang)
    check(f'{lang}: "{s[:28]}…" → raqam qolmadi ({n} ta)', n >= 1 and not any(ch.isdigit() for ch in c2))

r = pipeline.Result(level='muhim', danger=False, triage={}, answer={'vaziyat': 'x' * 300, 'huquqlar': ['y' * 600] * 10,
                    'majburiyatlar': ['z' * 600] * 10, 'dalillar': ['w' * 600] * 10}, articles=arts, cited=cited_all)
card = render.card(r, 'Xodim')
check(f'uzun karta: {len(card)} ≤ 4096, ogohlantirish va havolalar saqlandi',
      len(card) <= 4096 and 'yakuniy baho yurist' in card and 'lex.uz' in card)
sys.exit(0 if ok else 1)
