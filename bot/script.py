"""Oʻzbek yozuvini chiqishda oʻgirish. Ichki matn (lugʻat, AI javobi, qonun nomlari) — amaldagi lotin yozuvida;
foydalanuvchiga uning tanlovi boʻyicha koʻrsatiladi:
  cyrl — kirill (standart);
  latn — yangi lotin alifbosi (OʻRQ–1184, 21.10.2026): oʻ→ö, gʻ→ğ, sh→ş, ch→ç; "ng" harfi alohida emas; tutuq qoladi.
HTML teglari, &entity; lar, havolalar, domenlar va {oʻrinbosar}lar oʻgirilmaydi."""
import re

SCRIPTS = ('cyrl', 'latn')
DEFAULT = 'cyrl'

_APO = "ʻʼ'‘’`"
# Oʻgirilmaydigan boʻlaklar: HTML teg, entity, URL, domen/email, {placeholder}, kod nomlari
_SKIP = re.compile(r'(<[^>]*>|&#?\w+;|https?://\S+|\b[\w.+-]+@[\w-]+\.[\w.]+|\b[\w-]+(?:\.[\w-]+)*\.(?:uz|com|ru|org|net|me)\b'
                   r'|\{[^}]*\}|\b(?:PDF|AI|Telegram|Yandex|Groq|Gemini|lex)\b)')

_SINGLE = {
    'a': 'а', 'b': 'б', 'd': 'д', 'e': 'е', 'f': 'ф', 'g': 'г', 'h': 'ҳ', 'i': 'и', 'j': 'ж', 'k': 'к', 'l': 'л',
    'm': 'м', 'n': 'н', 'o': 'о', 'p': 'п', 'q': 'қ', 'r': 'р', 's': 'с', 't': 'т', 'u': 'у', 'v': 'в', 'x': 'х',
    'y': 'й', 'z': 'з', 'c': 'к', 'w': 'в',
}
_VOWELS = set('aeiouAEIOUоаеиуўэёюяОАЕИУЎЭЁЮЯ')
_CYR_TOKEN = re.compile(
    rf"([oOgG][{_APO}])|(sh|Sh|SH|ch|Ch|CH|(?:yo|Yo|YO)(?![{_APO}])|yu|Yu|YU|ya|Ya|YA|ye|Ye|YE)|([{_APO}])|([A-Za-z])")


def _cyrl_segment(s: str) -> str:
    out = []
    pos = 0
    for m in _CYR_TOKEN.finditer(s):
        out.append(s[pos:m.start()])
        pos = m.end()
        og, di, apo, ch = m.groups()
        prev = ''.join(out)[-1:]
        if og:
            low = {'o': 'ў', 'g': 'ғ'}[og[0].lower()]
            out.append(low.upper() if og[0].isupper() else low)
        elif di:
            base = {'sh': 'ш', 'ch': 'ч', 'yo': 'ё', 'yu': 'ю', 'ya': 'я', 'ye': 'е'}[di.lower()]
            out.append(base.upper() if di[0].isupper() else base)
        elif apo:
            # tutuq belgisi (maʼno, taʼlim) → ъ; soʻz boshida/oxirida (qoʻshtirnoq) — oʻzgarmaydi
            nxt = s[m.end():m.end() + 1]
            out.append('ъ' if prev.isalpha() and nxt.isalpha() else apo)
        else:
            lo = ch.lower()
            if lo == 'e' and (not prev.isalpha() or prev in _VOWELS):  # soʻz boshida va unlidan keyin: э
                c = 'э'
            else:
                c = _SINGLE[lo]
            out.append(c.upper() if ch.isupper() else c)
    out.append(s[pos:])
    return ''.join(out)


_NEW = [(re.compile(rf'O[{_APO}]'), 'Ö'), (re.compile(rf'o[{_APO}]'), 'ö'), (re.compile(rf'G[{_APO}]'), 'Ğ'),
        (re.compile(rf'g[{_APO}]'), 'ğ'), (re.compile(r'SH|Sh'), 'Ş'), (re.compile(r'sh'), 'ş'),
        (re.compile(r'CH|Ch'), 'Ç'), (re.compile(r'ch'), 'ç')]


def _latn_segment(s: str) -> str:
    for rx, rep in _NEW:
        s = rx.sub(rep, s)
    return s


def convert(text: str, script: str | None) -> str:
    """Amaldagi lotin → tanlangan yozuv. script None/boshqa — oʻzgarmaydi."""
    if not text or script not in SCRIPTS:
        return text
    fn = _cyrl_segment if script == 'cyrl' else _latn_segment
    out, pos = [], 0
    for m in _SKIP.finditer(text):
        out.append(fn(text[pos:m.start()]))
        out.append(m.group(0))
        pos = m.end()
    out.append(fn(text[pos:]))
    return ''.join(out)
