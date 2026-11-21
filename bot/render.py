"""Tahlil natijasini Telegram HTML kartasiga aylantirish (foydalanuvchi tilida). AI matni doim html.escape dan oʻtadi.
Qonun havolalari va ogohlantirish HECH QACHON kesilmaydi; joy yetmasa, ixtiyoriy boʻlimlar qisqartiriladi."""
import html

from .i18n import law_name, t
from .pipeline import Result

MAX_LEN = 4000   # Telegram chegarasi 4096
ITEM = 250       # har bandning eng koʻp uzunligi


def _e(s, limit: int = ITEM) -> str:
    s = str(s or '').strip()
    if len(s) > limit:
        s = s[:limit].rsplit(' ', 1)[0] + '…'
    return html.escape(s, quote=False)


def _href(s) -> str:
    return html.escape(str(s or ''), quote=True)


def _items(items) -> list[str]:
    return [i for i in (items or []) if isinstance(i, str) and i.strip()]


def _section(title: str, items: list[str], n: int, bullet: str = '•') -> str:
    return title + '\n' + '\n'.join(f'{bullet} {_e(i)}' for i in items[:n]) if items[:n] else ''


def card(r: Result, role_label: str, lang: str = 'uz') -> str:
    a = r.answer
    head = [f'<b>{t(lang, "LEVELS").get(r.level, r.level)}</b> · {_e(role_label)}']
    if r.danger:
        head.append(t(lang, 'EMERGENCY_SHORT'))
    if a.get('vaziyat'):
        head.append(f'{t(lang, "H_SITUATION")} {_e(a["vaziyat"], 400)}')

    steps = [s for s in (a.get('murojaat') or []) if isinstance(s, dict)]
    lines = []
    for i, s in enumerate(steps[:3], 1):
        line = f'{i}. <b>{_e(s.get("kimga"), 120)}</b>'
        if s.get('qanday'):
            line += f' — {_e(s["qanday"], 150)}'
        if s.get('qachon'):
            line += f' (⏱ {_e(s["qachon"], 120)})'
        lines.append(line)
    where = t(lang, 'H_WHERE') + '\n' + '\n'.join(lines) if lines else ''

    src = [f'• <a href="{_href(art.link)}">{_e(law_name(lang, art.abbr, art.law), 90)}, {_e(t(lang, "ARTICLE", num=art.num))}</a>'
           f' — {_e(why, 200)}' for art, why in r.cited[:5]]
    tail = [t(lang, 'H_LAW') + '\n' + '\n'.join(src) if src else '', f'<i>{t(lang, "DISCLAIMER")}</i>']

    rights, duties, proofs = _items(a.get('huquqlar')), _items(a.get('majburiyatlar')), _items(a.get('dalillar'))
    asks = _items(a.get('aniqlashtirish'))
    # Joy yetmasa: avval savollar, keyin bandlar soni 5 → 1 gacha kamayadi
    for n, with_asks in ((5, True), (4, True), (3, False), (2, False), (1, False)):
        body = [_section(t(lang, 'H_RIGHTS'), rights, n), _section(t(lang, 'H_DUTIES'), duties, n),
                where, _section(t(lang, 'H_PROOF'), proofs, n)]
        if with_asks:
            body.append(_section(t(lang, 'H_ASK'), asks, 3, '❔'))
        out = '\n\n'.join(p for p in head + body + tail if p)
        if len(out) <= MAX_LEN:
            return out
    return '\n\n'.join(p for p in head + [where] + tail if p)[:MAX_LEN]
