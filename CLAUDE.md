# Huquqiy navigator bot — loyiha qoidalari

> **Ikki noutbuk — avval shuni oʻqi:** `ISH_TARTIBI.md`.
> - 1-noutbuk — hujjatlar (`hujjat-qism`), 2-noutbuk — kod (`kod-qism`).
> - Oʻz noutbukingga tegishli boʻlmagan faylni oʻzgartirma.
> - Ish boshida: `git pull origin main` va ikkala `jurnal/*.md` ni oʻqi.
> - Har bir tayyor ishdan keyin darhol oʻz jurnalingga yoz, commit va push qil.

LexHackathon 2026, "Huquqiy xizmatlar" treki, rasmiy 1-muammo: fuqarolarning davlat tashkilotlariga murojaat qilish ko'nikmasi. Telegram bot: vaziyat (matn/ovoz/skrinshot) → eng yangi qonun bilan solishtirish → kimga, qayerga, qachon murojaat qilish + ariza matni → jiddiy holatda 3 kalit orqali idoraga.

- Ish tartibi: `BUILD_PLAN.md`. Strategiya va pitch: https://claude.ai/artifact/J7fJyz2SDXiiWN3LQqcRFB
- Muloqot tili: o'zbek (lotin), qisqa va amaliy.

## O'zgarmas qoidalar
1. **Modda raqamini o'ylab topma.** Bot ham, Claude ham faqat `data/lex.db` dagi moddalarga tayanadi. Har javobdagi modda bazadan tekshiriladi.
2. **Har modda lex.uz havolasi bilan.** Havola konvertor yozgan `<!-- url#id -->` dan olinadi.
3. **Bot hukm chiqarmaydi, sud natijasini bashorat qilmaydi.** Qonunda belgilangan oqibatni aytadi. Har javob oxirida: "Bu huquqiy maslahat emas, yakuniy baho yurist zimmasida."
4. **Hayotga xavf → AI tahlilidan oldin 102 / 103.** Bot vositachi bo'lmaydi.
5. **Idoraga hech narsa 3 kalitsiz ketmaydi:** telefon tasdig'i, AI bali, klinika yuristi tasdig'i. Avtomatik yuborish yo'q.
6. **Maxfiylik:** tokenlar faqat `.env` da, hech qachon kod, log yoki chatda emas. Media tahlildan keyin o'chiriladi. Demoda faqat jamoa yozgan test materiallari.
7. **Model nomlari `.env` da** (`MODEL_FAST`, `MODEL_STRONG`), kodda qattiq yozilmaydi.
8. **lex.uz ga muloyim:** so'rovlar orasida kamida 2 soniya.
9. Har bosqich tugagach va 13:00 muzlatishdan oldin `auditor` subagenti ishga tushiriladi; kritik topilmalar tuzatilmaguncha keyingi bosqichga o'tilmaydi.

10. **Yozuv:** ichki matn (lugʻat, AI promptlari va javoblari) amaldagi lotinda (oʻ, gʻ) yoziladi. Foydalanuvchiga chiqishda oʻgiriladi: `bot/outscript.py` (Telegram) va `conv()` (Mini App). Standart — kirill; yangi lotin — OʻRQ–1184. Matnni qoʻlda kirillga yozma.
11. **Repo PUBLIC.** `.env`, `data/app.db`, `logs/` hech qachon commit qilinmaydi.

## Tuzilma
| Fayl | Vazifa |
|---|---|
| `bot/main.py` | Bot kirish nuqtasi, /start (standart kirill), /til, rozilik, xabarlarni yoʻnaltirish |
| `bot/navflow.py` | Navigator: savollar → tuman → yoʻllar → qadamlar → kuzatuv (watcher); ariza PDF (`make_pdf`) |
| `bot/pipeline.py` | `is_danger` → triage → `retrieve` → AI javob → `validate` (modda raqamlari) → `routes` (muddat manbasi) → `strip_deadlines` |
| `bot/search.py`, `bot/textnorm.py` | FTS5 qidiruv; normallashtirish (oʻ/gʻ, kirill, ö/ğ/ş/ç, qoʻshimchalar) |
| `bot/llm.py` | Groq/Gemini chaqiruvlari, zaxira zanjiri, ovoz → matn |
| `bot/keys.py` | 3 kalit (telefon, AI bali, klinika yuristi) |
| `bot/webapi.py` | Mini App API: `/api/nav/*`, initData HMAC, til va yozuvni sinxronlash |
| `bot/script.py`, `bot/outscript.py` | Lotin → kirill / yangi lotin; Telegram soʻrov middleware |
| `bot/store.py` | SQLite `data/app.db`: users (lang, script), cases (`status` — 3 kalit, `nav_status` — navigator) |
| `bot/i18n.py` | Bot matnlari (uz/ru/en) |
| `webapp/index.html` | Mini App (bitta fayl): I18N, `conv()`, navigator ekranlari, ovoz yozish (WAV 16 kHz) |
| `tools/` | `lex2md.py`, `build_index.py`, `run_demo.py` (cloudflared + bot), `test_*.py` |

## Joriy holat (21-noyabr)
- **Ishlaydi:**
  - navigator (bot va Mini App);
  - aniqlashtiruvchi savollar (3–4 ta);
  - muddat tekshiruvi va manba moddasi;
  - ariza PDF (Times 14, chiziqli boʻsh joylar);
  - 3 kalit;
  - 4 til yozuvi;
  - Mini App'da ovozli xabar.
- **"Hali qoʻshilmagan" deb javob beradi:** transport yoʻnalishi, chop etish joylari, donat. Reja: `BUILD_PLAN.md` 9–10-boʻlimlar.
- **Boʻsh:** `CLINIC_CHAT_ID`, `AUTHORITY_CHAT_ID`.

## Muhit
- Windows, PowerShell 5.1. Python 3.12 (`C:\Users\user\AppData\Local\Programs\Python\Python312`), Git 2.56, Node 26.
- Ishga tushirish: polling rejimi, noutbukda: `.venv\Scripts\python tools\run_demo.py`. Tunnel manzili har safar oʻzgaradi; menyu tugmalari avtomatik yangilanadi.
- Bash heredoc `\\` ni buzadi: Python patch skriptlarini Write bilan yozing.
