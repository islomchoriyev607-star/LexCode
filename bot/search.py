"""Qonun bazasidan (data/lex.db) qidiruv va modda mavjudligini tekshirish."""
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from .textnorm import query_terms

DB = Path(__file__).resolve().parent.parent / 'data' / 'lex.db'
_con = None
_SUP = str.maketrans('⁰¹²³⁴⁵⁶⁷⁸⁹', '0123456789')


def con() -> sqlite3.Connection:
    global _con
    if _con is None:
        _con = sqlite3.connect(f'file:{DB}?mode=ro', uri=True, check_same_thread=False)
    return _con


@dataclass
class Article:
    abbr: str
    law: str
    num: str
    title: str
    body: str
    link: str

    def cite(self) -> str:
        return f'{self.law}, {self.num}-modda'


_COLS = 'abbr, law, num, title, body, link'


def search(text: str, limit: int = 8, laws: list[str] | None = None) -> list[Article]:
    terms = query_terms(text)
    if not terms:
        return []
    q = '{title_n body_n}: (' + ' OR '.join(f'"{t}"*' for t in terms[:30]) + ')'
    sql = f'SELECT {_COLS} FROM m WHERE m MATCH ?'
    args: list = [q]
    if laws:
        sql += f' AND abbr IN ({",".join("?" * len(laws))})'
        args += laws
    sql += ' ORDER BY bm25(m, 0, 0, 0, 0, 0, 0, 6.0, 1.0) LIMIT ?'
    args.append(limit)
    return [Article(*r) for r in con().execute(sql, args).fetchall()]


def norm_num(num: str) -> str:
    """'184⁵', '184 5', '184-5', '184-5-modda' → '184-5'."""
    s = re.sub(r'(\d)([⁰¹²³⁴⁵⁶⁷⁸⁹]+)', lambda m: m.group(1) + '-' + m.group(2).translate(_SUP), str(num))
    parts = re.findall(r'\d+', s)
    return '-'.join(parts[:2])


def get(abbr: str, num: str) -> Article | None:
    r = con().execute(f'SELECT {_COLS} FROM m WHERE abbr = ? AND num = ?', (abbr, norm_num(num))).fetchone()
    return Article(*r) if r else None


def laws() -> dict[str, str]:
    return dict(con().execute('SELECT abbr, law FROM docs').fetchall())
