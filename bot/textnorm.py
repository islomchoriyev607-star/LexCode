"""O'zbek matnini qidiruv uchun normallashtirish. Indeks (tools/build_index.py) va so'rov (bot/search.py)
bir xil funksiyadan o'tadi — shunda oʻ / o' / o‘ / o` / kirill yozuvlari bir-biriga mos keladi."""
import re

_CYR = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo', 'ж': 'j', 'з': 'z', 'и': 'i',
    'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
    'у': 'u', 'ф': 'f', 'х': 'x', 'ц': 's', 'ч': 'ch', 'ш': 'sh', 'щ': 'sh', 'ъ': '', 'ы': 'i', 'ь': '',
    'э': 'e', 'ю': 'yu', 'я': 'ya', 'ў': 'o', 'қ': 'q', 'ғ': 'g', 'ҳ': 'h',
}
_APOS = re.compile(r"[ʻʼ'‘’`´ʹ]")
_WORD = re.compile(r'[a-z0-9]+')

# Ko'p uchraydigan qo'shimchalar (uzundan qisqaga). Ildiz kamida 3 harf qoladi.
_SUFFIXES = sorted("""
laringizni larimizni larining laridan lariga larini larida lardan larga larni larning lari lar
ingizni imizni ingiz imiz ining ingni ning ni dan ga ka qa da ta im ing imni imga imdan
yapti yapman yapsiz moqda moqchi ayapti ayotgan ishdi ishgan ishyapti ishmoqda ildi ilgan ilsa ilib
gan kan qan ib sa di dim dik ding madi magan may mayapti adi aman asiz
lik likni likka chi chilar siz li
""".split(), key=len, reverse=True)

STOP = set("""
va bilan uchun men meni menga mening sen u ular biz bu shu o ham yoki agar lekin ammo deb edi
nima qanday qayerga qaerga qachon kim kimga nega bolsa boladi bolarmi kerak mumkin qilsam qilish
bir ikki juda endi hali yana har hech
""".split())


_CYR.update({'ў': 'o1', 'ғ': 'g1'})
# Yangi lotin alifbosi (OʻRQ–1184, 21.10.2026): ö = oʻ, ğ = gʻ, ş = sh, ç = ch — eski yozuv bilan bir xil normallashadi
_CYR.update({'ö': 'o1', 'ğ': 'g1', 'ş': 'sh', 'ç': 'ch'})
_OG = re.compile(r"([og])[ʻʼ'‘’`´ʹ]")


def normalize(text: str) -> str:
    """Kichik harf, kirill → lotin; oʻ/o'/o‘ → "o1", gʻ → "g1" (o'g'irlik ≠ og'irlik), tutuq belgisi olib tashlanadi."""
    t = text.lower()
    t = ''.join(_CYR.get(ch, ch) for ch in t)
    t = _OG.sub(r'\g<1>1', t)
    return _APOS.sub('', t)


def stem(word: str) -> str:
    for _ in range(3):
        for s in _SUFFIXES:
            if word.endswith(s) and len(word) - len(s) >= 3:
                word = word[: -len(s)]
                break
        else:
            break
    return word


def query_terms(text: str) -> list[str]:
    """So'rov uchun ildizlar (takrorsiz, tartib saqlanadi)."""
    out = []
    for w in _WORD.findall(normalize(text)):
        if w in STOP or len(w) < 3 or w.isdigit():
            continue
        out.append(stem(w))
    return list(dict.fromkeys(out))
