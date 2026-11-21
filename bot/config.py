"""Sozlamalar faqat .env dan o'qiladi (CLAUDE.md, 6- va 7-qoida)."""
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / '.env')


def _req(name: str) -> str:
    v = os.getenv(name, '').strip()
    if not v:
        raise RuntimeError(f'.env da {name} yo\'q')
    return v


def _opt_int(name: str) -> int | None:
    v = os.getenv(name, '').strip()
    if not v:
        return None
    try:
        return int(v)
    except ValueError:
        raise RuntimeError(f'.env da {name} butun son bo\'lishi kerak (masalan -1001234567890), hozir: {v!r}') from None


BOT_TOKEN = _req('BOT_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '').strip()
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '').strip()

MODEL_FAST = _req('MODEL_FAST')
MODEL_STRONG = _req('MODEL_STRONG')
MODEL_FALLBACK = _req('MODEL_FALLBACK')
MODEL_VISION = _req('MODEL_VISION')
MODEL_STT = _req('MODEL_STT')
MODEL_STT_FALLBACK = os.getenv('MODEL_STT_FALLBACK', '').strip()

CLINIC_CHAT_ID = _opt_int('CLINIC_CHAT_ID')
AUTHORITY_CHAT_ID = _opt_int('AUTHORITY_CHAT_ID')
MODE = os.getenv('MODE', 'polling').strip()
# Navigator: "1 kun" necha soniya (real: 86400; demoda masalan 60 — 15 kunlik muddat 15 daqiqada tekshiriladi)
DAY_SECONDS = int(os.getenv('DAY_SECONDS', '86400') or 86400)
WEB_PORT =int(os.getenv('WEB_PORT', '8080') or 8080)
WEBAPP_URL = os.getenv('WEBAPP_URL', '').strip()  # https://... (tunnel); bo'lmasa menyu tugmasi qo'yilmaydi
# Javobsiz 🔴 murojaat: real hayotda 1–3 kun (1440–4320), demoda 2–3 daqiqa
INACTIVITY_MINUTES = int(os.getenv('INACTIVITY_MINUTES', '1440') or 1440)

DATA = ROOT / 'data'
APP_DB = DATA / 'app.db'
MEDIA_DIR = DATA / 'media'
MAX_FILE_MB = 20  # Telegram Bot API yuklab olish chegarasi
