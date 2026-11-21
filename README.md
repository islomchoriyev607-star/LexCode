# Huquqiy Navigator — @lex_nav_bot

**LexHackathon 2026 · "Huquqiy xizmatlar" treki · rasmiy 1-muammo:** fuqarolarda davlat tashkilotlariga ariza, shikoyat va taklif bilan murojaat qilish koʻnikmasi yetishmaydi.

## Muammo
Odamning huquqi buzilganda u qaysi idoraga, qachon va qanday murojaat qilishni bilmaydi. Qonun matni murakkab, ariza yozish qoʻrqinchli, javob kelmasa nima qilishni ham bilmaydi. Natijada murojaat qilinmaydi yoki notoʻgʻri idoraga boriladi.

## Yechim
Telegram bot va Mini App — fuqaro yonida turgan "navigator":

1. **Vaziyatni qabul qiladi:** matn, ovozli xabar yoki skrinshot.
2. **Xavfni tekshiradi:** hayotga xavf boʻlsa, AI tahlilidan **oldin** 112 / 102 / 103 raqamlarini koʻrsatadi.
3. **Aniqlashtiradi:** 3–4 ta qisqa savol (variantli yoki erkin javob).
4. **Qonun bilan solishtiradi:** lex.uz dagi amaldagi moddalar (7 ta kodeks va qonun, 2 942 modda) bilan.
5. **Yoʻllarni koʻrsatadi:** 2–3 ta yoʻl (masalan, inspeksiya, sud, prokuratura). Fuqaro birini tanlaydi va qadamma-qadam boradi.
6. **Ariza tayyorlaydi:** rasmiy PDF (Times New Roman 14, xatboshi, qoʻlda toʻldirish uchun chiziqlar).
7. **Kuzatadi:** muddat tugagach "javob keldimi?" deb soʻraydi va keyingi qadamni taklif qiladi.
8. **Jiddiy holatda — 3 kalit:** idoraga murojaat faqat telefon tasdigʻi, AI bali va Yuridik klinika yuristi tasdigʻidan keyin yuboriladi. Soxta murojaatlarga qarshi; avtomatik yuborish yoʻq.

## Ishonchlilik qoidalari
- **Modda raqami oʻylab topilmaydi.** AI faqat bazadagi moddalarni tanlaydi; matndagi har qanday modda raqami olib tashlanadi. Har bir manba lex.uz havolasi bilan koʻrsatiladi.
- **Muddatlar** (masalan, "15 kun") faqat tanlangan modda matnida boʻlsa koʻrsatiladi, yonida manba moddasi beriladi.
- **Bot hukm chiqarmaydi** va sud natijasini bashorat qilmaydi. Har javob oxirida: "Bu huquqiy maslahat emas, yakuniy baho yurist zimmasida."
- **Maxfiylik:** media fayl matnga aylantirilgach oʻchiriladi; kalitlar faqat `.env` da saqlanadi.

## Tillar
- **Ўзбекча (kirill)** — standart.
- **Özbekça** — yangi lotin alifbosida (OʻRQ–1184, 21.10.2026: ö, ğ, ş, ç).
- **Русский** va **English**.

Ichki matn bitta joyda saqlanadi va chiqishda tanlangan yozuvga oʻgiriladi (`bot/script.py`, `bot/outscript.py`).

## Arxitektura
```
Telegram ──► bot/main.py (aiogram 3, polling)
              ├─ bot/navflow.py    navigator: savollar → tuman → yoʻllar → qadamlar → kuzatuv
              ├─ bot/pipeline.py   xavf → triage → qidiruv → AI javob → tekshiruv (validate)
              ├─ bot/search.py     SQLite FTS5 (data/lex.db) + bot/textnorm.py (oʻ/gʻ, kirill, qoʻshimchalar)
              ├─ bot/llm.py        Groq (tez/kuchli model) → Gemini (zaxira, rasm, ovoz → matn)
              ├─ bot/keys.py       3 kalit: telefon → AI bali → klinika yuristi → idora
              └─ bot/webapi.py     Mini App API (/api/nav/*), Telegram initData HMAC tekshiruvi
Mini App ──► webapp/index.html (bitta fayl: HTML + CSS + JS, Three.js shar)
```

| Papka | Vazifasi |
|---|---|
| `bot/` | Bot, AI zanjiri, navigator, Mini App API |
| `webapp/` | Telegram Mini App (bitta HTML fayl) |
| `tools/` | lex.uz → Markdown, indeks yasash, demo ishga tushirish, testlar |
| `data/md/` | lex.uz dan olingan qonun matnlari (Markdown) |
| `data/laws.txt` | Bazaga kiritilgan qonunlar roʻyxati |
| `eval/samples/` | Test namunalari (ovoz, skrinshot, ariza) |
| `brand/` | Logotip |
| `jurnal/` | Ikki noutbukning ish jurnali (`ISH_TARTIBI.md` ga qarang) |

## Lokal ishga tushirish (Windows)
```bash
git clone https://github.com/islomchoriyev607-star/LexCode.git
cd LexCode
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
copy .env.example .env          # BOT_TOKEN, GEMINI_API_KEY, GROQ_API_KEY ni yozing
.venv\Scripts\python tools\build_index.py      # data/md → data/lex.db (qidiruv bazasi)
.venv\Scripts\python tools\run_demo.py         # Cloudflare tunnel + bot + Mini App
```
- Faqat botning oʻzi kerak boʻlsa: `.venv\Scripts\python -m bot.main`.
- `run_demo.py` uchun `cloudflared` oʻrnatilgan boʻlishi kerak.

**Testlar:**
```bash
.venv\Scripts\python -I tools\test_danger.py     # xavf belgilari (22/22)
.venv\Scripts\python -I tools\test_validate.py   # modda raqami tekshiruvi
.venv\Scripts\python -I tools\test_script.py     # kirill / yangi lotin
.venv\Scripts\python -I tools\test_navflow.py    # navigator (AI chaqiradi)
.venv\Scripts\python -I tools\test_navapi.py     # Mini App API
```

## Stek
Python 3.12, aiogram 3, aiohttp, httpx, SQLite FTS5, fpdf2. AI: Groq (`qwen3`, `gpt-oss-120b`), Google Gemini. Model nomlari `.env` da.

## Jamoa
- Jamoa yetakchisi: Islom Choriyev — Oʻzbekiston Milliy universiteti, yurisprudensiya, 2-kurs; Yuridik klinika Bosh koordinatori.
- Kod Claude Code yordamida yozilgan.
