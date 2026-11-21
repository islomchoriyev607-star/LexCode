"""Bot holati: rozilik va murojaatlar (data/app.db)."""
import sqlite3
import time

from . import config

_con = None


def con() -> sqlite3.Connection:
    global _con
    if _con is None:
        config.DATA.mkdir(exist_ok=True)
        _con = sqlite3.connect(config.APP_DB, check_same_thread=False)
        _con.executescript(
            '''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY, consent_at REAL, phone TEXT, phone_at REAL);
            CREATE TABLE IF NOT EXISTS cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, created REAL, updated REAL,
                status TEXT, level TEXT, text TEXT, analysis TEXT, score INTEGER, application TEXT);
            CREATE TABLE IF NOT EXISTS seen_updates (update_id INTEGER PRIMARY KEY);
            '''
        )
        for table, col, typ in (('cases', 'role', 'TEXT'), ('cases', 'kind', 'TEXT'), ('users', 'pending_case', 'INTEGER'),
                                ('users', 'lang', 'TEXT'), ('users', 'pending', 'TEXT'),
                                ('cases', 'district', 'TEXT'), ('cases', 'lat', 'REAL'), ('cases', 'lon', 'REAL'),
                                ('cases', 'questions', 'TEXT'), ('cases', 'answers', 'TEXT'), ('cases', 'routes', 'TEXT'),
                                ('cases', 'route', 'INTEGER'), ('cases', 'step', 'INTEGER'), ('cases', 'next_check', 'REAL'),
                                ('cases', 'nav_status', 'TEXT'), ('users', 'script', 'TEXT')):
            if col not in {r[1] for r in _con.execute(f'PRAGMA table_info({table})')}:
                _con.execute(f'ALTER TABLE {table} ADD COLUMN {col} {typ}')
        # Eski yozuvlar: navigator holati `status` da saqlangan edi — alohida ustunga koʻchiriladi
        _con.execute("UPDATE cases SET nav_status = status, status = 'answered' WHERE nav_status IS NULL "
                     "AND status IN ('routes', 'nav', 'waiting', 'checking', 'route_done')")
        _con.commit()
    return _con


def create_case(user_id: int, text: str, kind: str) -> int:
    """Har bir vaziyat — alohida murojaat; rol keyin shu murojaatga biriktiriladi."""
    now = time.time()
    cur = con().execute('INSERT INTO cases(user_id, created, updated, status, text, kind) VALUES(?,?,?,?,?,?)',
                        (user_id, now, now, 'awaiting_role', text, kind))
    con().commit()
    return cur.lastrowid


def set_case_role(case_id: int, user_id: int, role: str) -> dict | None:
    """Faqat murojaat egasi rol tanlay oladi. Murojaat topilmasa yoki egasi boshqa bo'lsa — None."""
    r = con().execute('SELECT id, text, kind, status FROM cases WHERE id = ? AND user_id = ?', (case_id, user_id)).fetchone()
    if not r:
        return None
    if r[3] == 'awaiting_role':  # rol bir marta tanlanadi; keyingi bosishlar hech narsani o'zgartirmaydi
        con().execute('UPDATE cases SET role = ?, status = ?, updated = ? WHERE id = ?', (role, 'analyzing', time.time(), case_id))
        con().commit()
    return {'id': r[0], 'text': r[1], 'kind': r[2], 'role': role, 'prev_status': r[3]}


def set_consent(user_id: int) -> None:
    con().execute('INSERT INTO users(user_id, consent_at) VALUES(?, ?) '
                  'ON CONFLICT(user_id) DO UPDATE SET consent_at = excluded.consent_at', (user_id, time.time()))
    con().commit()


def save_analysis(case_id: int, level: str, analysis_json: str, score) -> None:
    try:
        score = int(score)
    except (TypeError, ValueError):
        score = None
    con().execute('UPDATE cases SET status = ?, level = ?, analysis = ?, score = ?, updated = ? WHERE id = ?',
                  ('answered', level, analysis_json, score, time.time(), case_id))
    con().commit()


def set_status(case_id: int, status: str) -> None:
    con().execute('UPDATE cases SET status = ?, updated = ? WHERE id = ?', (status, time.time(), case_id))
    con().commit()


def save_application(case_id: int, text: str) -> None:
    con().execute('UPDATE cases SET application = ?, updated = ? WHERE id = ?', (text, time.time(), case_id))
    con().commit()


def get_case(case_id: int, user_id: int) -> dict | None:
    r = con().execute('SELECT id, text, kind, role, status, level, analysis, application FROM cases '
                      'WHERE id = ? AND user_id = ?', (case_id, user_id)).fetchone()
    keys = ('id', 'text', 'kind', 'role', 'status', 'level', 'analysis', 'application')
    return dict(zip(keys, r)) if r else None


def get_case_any(case_id: int) -> dict | None:
    """Klinika va kuzatuvchi uchun (egasi tekshirilmaydi — chaqiruvchi o'zi tekshiradi)."""
    r = con().execute('SELECT id, user_id, text, kind, role, status, level, analysis, application, score FROM cases '
                      'WHERE id = ?', (case_id,)).fetchone()
    keys = ('id', 'user_id', 'text', 'kind', 'role', 'status', 'level', 'analysis', 'application', 'score')
    return dict(zip(keys, r)) if r else None


def set_score(case_id: int, score: int) -> None:
    con().execute('UPDATE cases SET score = ?, updated = ? WHERE id = ?', (score, time.time(), case_id))
    con().commit()


def touch(case_id: int) -> None:
    set_status(case_id, 'answered')


def stale_cases(levels: tuple, status: str, before: float) -> list[dict]:
    q = (f'SELECT id, user_id FROM cases WHERE status = ? AND level IN ({",".join("?" * len(levels))}) '
         'AND updated < ?')
    return [{'id': r[0], 'user_id': r[1]} for r in con().execute(q, (status, *levels, before)).fetchall()]


def escalations_today(user_id: int) -> int:
    since = time.time() - 86400
    return con().execute("SELECT COUNT(*) FROM cases WHERE user_id = ? AND status IN ('k3_wait','sent','rejected') "
                         'AND updated > ?', (user_id, since)).fetchone()[0]


def set_pending_escalation(user_id: int, case_id: int) -> None:
    con().execute('INSERT INTO users(user_id, pending_case) VALUES(?, ?) '
                  'ON CONFLICT(user_id) DO UPDATE SET pending_case = excluded.pending_case', (user_id, case_id))
    con().commit()


def pending_escalation(user_id: int) -> int | None:
    r = con().execute('SELECT pending_case FROM users WHERE user_id = ?', (user_id,)).fetchone()
    return r[0] if r and r[0] else None


def set_phone(user_id: int, phone: str) -> None:
    con().execute('UPDATE users SET phone = ?, phone_at = ? WHERE user_id = ?', (phone, time.time(), user_id))
    con().commit()


def has_phone(user_id: int) -> bool:
    r = con().execute('SELECT phone FROM users WHERE user_id = ?', (user_id,)).fetchone()
    return bool(r and r[0])


# ---------- Navigator holati ----------
import json as _json  # noqa: E402


def set_pending(user_id: int, state: dict | None) -> None:
    """Foydalanuvchi suhbatda nimani kutyapti: {'case', 'stage': clarify|district|question, 'i'} yoki None."""
    con().execute('INSERT INTO users(user_id, pending) VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE SET pending = excluded.pending',
                  (user_id, _json.dumps(state) if state else None))
    con().commit()


def get_pending(user_id: int) -> dict | None:
    r = con().execute('SELECT pending FROM users WHERE user_id = ?', (user_id,)).fetchone()
    return _json.loads(r[0]) if r and r[0] else None


# Navigator holati alohida ustunda (nav_status): 3 kalit oqimining `status` i bilan toʻqnashmaydi.
# Navigator kodida u `status` nomi bilan oʻqiladi/yoziladi.
NAV_COLS = ('id', 'user_id', 'text', 'role', 'status', 'level', 'analysis', 'application', 'district', 'lat', 'lon',
            'questions', 'answers', 'routes', 'route', 'step', 'next_check')


def nav_case(case_id: int, user_id: int | None = None) -> dict | None:
    q = f'SELECT {", ".join("nav_status" if c == "status" else c for c in NAV_COLS)} FROM cases WHERE id = ?' + (' AND user_id = ?' if user_id is not None else '')
    r = con().execute(q, (case_id, user_id) if user_id is not None else (case_id,)).fetchone()
    if not r:
        return None
    d = dict(zip(NAV_COLS, r))
    for k in ('questions', 'answers', 'routes'):
        d[k] = _json.loads(d[k]) if d[k] else ([] if k != 'routes' else [])
    return d


def nav_update(case_id: int, **fields) -> None:
    for k in ('questions', 'answers', 'routes'):
        if k in fields and not isinstance(fields[k], str):
            fields[k] = _json.dumps(fields[k], ensure_ascii=False)
    if 'status' in fields:
        fields['nav_status'] = fields.pop('status')
    fields['updated'] = time.time()
    con().execute(f'UPDATE cases SET {", ".join(f"{k} = ?" for k in fields)} WHERE id = ?', (*fields.values(), case_id))
    con().commit()


def due_checks(now: float) -> list[dict]:
    rows = con().execute("SELECT id, user_id FROM cases WHERE nav_status = 'waiting' AND next_check IS NOT NULL AND next_check <= ?",
                         (now,)).fetchall()
    return [{'id': i, 'user_id': u} for i, u in rows]


def set_script(user_id: int, script: str) -> None:
    con().execute('INSERT INTO users(user_id, script) VALUES(?, ?) '
                  'ON CONFLICT(user_id) DO UPDATE SET script = excluded.script', (user_id, script))
    con().commit()


def script(user_id) -> str | None:
    """Oʻzbek tili tanlangan boʻlsa — yozuv (cyrl standart | latn); boshqa tilda yoki nomaʼlum foydalanuvchida — None."""
    if not isinstance(user_id, int) or user_id <= 0:
        return None
    r = con().execute('SELECT lang, script FROM users WHERE user_id = ?', (user_id,)).fetchone()
    if r is None or (r[0] or 'uz') != 'uz':
        return None
    return r[1] if r[1] in ('cyrl', 'latn') else 'cyrl'


def set_lang(user_id: int, lang: str) -> None:
    con().execute('INSERT INTO users(user_id, lang) VALUES(?, ?) '
                  'ON CONFLICT(user_id) DO UPDATE SET lang = excluded.lang', (user_id, lang))
    con().commit()


def get_lang(user_id: int) -> str | None:
    """Foydalanuvchi tanlagan til (uz/ru/en) yoki None — hali tanlanmagan."""
    r = con().execute('SELECT lang FROM users WHERE user_id = ?', (user_id,)).fetchone()
    return r[0] if r and r[0] else None


def lang(user_id: int) -> str:
    return get_lang(user_id) or 'uz'


def users_with_lang() -> list[tuple[int, str]]:
    """Til tanlagan foydalanuvchilar — ularning shaxsiy menyu tugmasi bor (bot qayta ishga tushganda yangilanadi)."""
    return [(u, lg) for u, lg in con().execute('SELECT user_id, lang FROM users WHERE lang IS NOT NULL').fetchall()]


def revoke_consent(user_id: int) -> None:
    con().execute('UPDATE users SET consent_at = NULL WHERE user_id = ?', (user_id,))
    con().commit()


def has_consent(user_id: int) -> bool:
    r = con().execute('SELECT consent_at FROM users WHERE user_id = ?', (user_id,)).fetchone()
    return bool(r and r[0])
