"""OpenStreetMap (Overpass) → data/offices.json: Toshkent shahridagi sudlar, IIB (102) boʻlimlari va FHDYO lar.
Har yozuv: tur, nom, manzil, tuman, lat/lon. Manzillar oʻylab topilmaydi — faqat OSM dagi haqiqiy obyektlar.
usage: python tools/build_offices.py"""
import json, pathlib, sys, urllib.parse, urllib.request

sys.stdout.reconfigure(encoding='utf-8')
OUT = pathlib.Path(__file__).resolve().parent.parent / 'data' / 'offices.json'
URL = 'https://overpass-api.de/api/interpreter'
QUERY = r'''[out:json][timeout:180];
area["name:en"="Tashkent"]["admin_level"="4"]->.city;
rel(area.city)["boundary"="administrative"]["admin_level"~"^(6|8)$"];
map_to_area->.ds;
foreach.ds->.d(
  .d out tags;
  ( nwr(area.d)["amenity"~"^(courthouse|police)$"];
    nwr(area.d)["name"~"ФҲДЁ|ФХДЁ|ЗАГС|FHDY|ZAGS|holati dalolatnomalarini|актов гражданского",i]; );
  out center tags;
);'''


SKIP = ('прокурат', 'prokurat', 'архив', 'arxiv', 'третейск', 'oliy sud', 'верховн', 'konstitutsiya', 'конституц',
        'департамент', 'област', 'облост', 'viloyat', 'гаи', 'радар', 'паспорт', 'батальон', 'батальён', 'оввиог', 'dyhxx')


def has(name: str, *words: str) -> bool:
    return any(w in name for w in words)


def kind(tags: dict) -> tuple[str, str] | None:
    """(tur, kichik tur) yoki None — ariza berish uchun yaroqsiz obyektlar tashlab ketiladi."""
    name = (tags.get('name') or tags.get('name:uz') or tags.get('name:ru') or '').lower()
    if not name or has(name, *SKIP):
        return None
    if has(name, 'фҳдё', 'фхдё', 'загс', 'fhdy', 'zags', 'holati dalolatnomalarini', 'актов гражданского'):
        return 'fhdyo', ''
    if tags.get('amenity') == 'courthouse' or ' sud' in f' {name}' or 'суд' in name:
        sub = ('fuqarolik' if has(name, 'fuqaro', 'граждан') else 'jinoyat' if has(name, 'jino', 'уголов') else
               'mamuriy' if has(name, "ma'muriy", 'maʼmuriy', 'админ') else 'iqtisodiy' if has(name, 'iqtisod', 'эконом') else '')
        return 'sud', sub
    if tags.get('amenity') == 'police':
        if has(name, 'ровд', 'рувд', 'ииб', 'iib', 'иио', 'ички ишлар', 'ichki ishlar', 'гом', 'отделение', 'отдел', "bo'lim", 'boʻlim'):
            return 'iib', 'bolim'
        if has(name, 'опорн', 'tayanch', 'участк', 'учаск', 'оп-', 'militsiya punkti', 'милиц'):
            return 'iib', 'tayanch'
    return None


def main() -> None:
    req = urllib.request.Request(URL, data=urllib.parse.urlencode({'data': QUERY}).encode(),
                                 headers={'User-Agent': 'lexcode-hackathon/1.0'})
    data = json.load(urllib.request.urlopen(req, timeout=200))
    out, seen, district = [], set(), None
    for e in data['elements']:
        t = e.get('tags', {})
        if e['type'] == 'area':
            district = t.get('name:uz') or t.get('name') or t.get('name:ru')
            continue
        k = kind(t)
        lat = e.get('lat') or (e.get('center') or {}).get('lat')
        lon = e.get('lon') or (e.get('center') or {}).get('lon')
        key = (e['type'], e['id'])
        if not k or lat is None or key in seen:
            continue
        seen.add(key)
        addr = ', '.join(x for x in (t.get('addr:street'), t.get('addr:housenumber')) if x)
        k, sub = k
        out.append({'tur': k, 'sub': sub, 'nom': t.get('name:uz') or t.get('name') or t.get('name:ru') or '',
                    'nom_ru': t.get('name:ru') or '', 'manzil': addr, 'tuman': district,
                    'tel': t.get('phone') or t.get('contact:phone') or '', 'lat': round(lat, 6), 'lon': round(lon, 6),
                    'osm': f"{e['type']}/{e['id']}"})
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')
    by = {}
    for o in out:
        by.setdefault(o['tur'], []).append(o)
    for k, v in by.items():
        subs = {}
        for o in v:
            subs[o['sub'] or '-'] = subs.get(o['sub'] or '-', 0) + 1
        print(f"{k}: {len(v)} ta {subs}, tumanlar {len({o['tuman'] for o in v})}")
    print('tumanlar:', sorted({o['tuman'] for o in out if o['tuman']}))
    print('→', OUT)


if __name__ == '__main__':
    main()
