# 1-noutbuk jurnali — hujjatlar (`hujjat-qism`)

Yangi yozuv eng yuqoriga yoziladi. Tartib: `ISH_TARTIBI.md`.

## 2026-11-21 — Prezentatsiya tayyor (Pitch Day)
- **Nima qilindi:** `prezentatsiya/Huquqiy_Navigator_LexCode.pdf` va `.pptx` — 8 slayd.
  - Tuzilma tashkilotchilar namunasi boʻyicha: sarlavha, biz kimmiz, muammo, bozor, raqobatchilar, monetizatsiya, KPI, jamoa.
  - Dizayn: LexCode ranglari, yangi lotin (OʻRQ–1184), `#LexHackathon #Hackathon #Tashkent #event`.
  - Ogʻzaki nutq va hakamlar savollariga javoblar: `prezentatsiya/nutq_va_savol_javob.md`.
- **Logolar:** `brand/navigator_logo.svg|png` (yangi, LexCode uslubida), `brand/lexcode_logo.png`, `brand/lexhackathon_logo.png`, `brand/adliya_logo.png`.
- **Qayta yasash:** `python prezentatsiya/build_slides.py` (python-pptx, pillow kerak).
- **Ochiq savol:**
  - 3-slayddagi statistika havolalarini taqdimotdan oldin tekshirish kerak.
  - Jamoa tajribasi (8-slayd) — Islom tasdiqladi ✅.
- **2-noutbuk uchun:** kodga taʼsiri yoʻq. Bot 14:00 checkpointda ishlab turishi kerak.

## 2026-11-21 — Bot serveri 2-noutbukka koʻchdi
- **Nima qilindi:** qaror — bot **faqat 2-noutbukda** ishlaydi; 1-noutbukda faqat hujjatlar va prezentatsiya. 1-noutbukda bot va tunnel toʻxtatilgan (tekshirildi). `ISH_TARTIBI.md` ga qoida qoʻshildi.
- **2-noutbuk uchun:**
  - Botni `.venv\Scripts\python tools\run_demo.py` bilan ishga tushiring; `cloudflared` oʻrnatilgan boʻlishi kerak.
  - Checkpoint 14:00 da bot ishlab turishi kerak.
  - Tunnel manzilini oʻz jurnalingizga yozing.
- **Keyingi ish (1-noutbuk):** PDF prezentatsiya (namuna pptx asosida).

## 2026-11-21 — Loyiha GitHub'ga yuklandi
- **Nima qilindi:** loyiha public repozitoriyga yuklandi: https://github.com/islomchoriyev607-star/LexCode ; `hujjat-qism` va `kod-qism` tarmoqlari ochildi. Yangi fayllar: `README.md`, `ISH_TARTIBI.md`, `jurnal/`. Yangilandi: `CLAUDE.md`, `.gitignore`.
- **Shu paytgacha qilingan ish (20-noyabr, shu noutbukda):**
  - **Bot:** navigator (savollar → tuman → yoʻllar → qadamlar → kuzatuv), 3 kalit, xavf → 112/102/103.
  - **Mini App:** navigator ekranlari, ovozli xabar, katta yozuv.
  - **Tillar:** kirill (standart), yangi lotin, rus, ingliz.
  - **Ariza PDF:** Times New Roman 14, xatboshi, qoʻlda toʻldirish uchun chiziqlar.
  - **Auditor topilmalari tuzatildi:** muddatlar manba moddadan tekshiriladi; navigator holati alohida ustunda saqlanadi.
- **Hali qoʻshilmagan** (bot "hali qoʻshilmagan" deb aytadi): transport yoʻnalishi, chop etish joylari, donat.
- **Keyingi noutbuk (kod) uchun:**
  - `.env` ni oʻzingiz yarating: kalitlar GitHub'da yoʻq.
  - `tools/build_index.py` bilan `data/lex.db` ni yasang.
  - Klinika va idora guruh ID lari (`CLINIC_CHAT_ID`, `AUTHORITY_CHAT_ID`) hali boʻsh.
- **Ochiq savol:** "Taʼlim toʻgʻrisida"gi qonun ID si `data/laws.txt` ga qoʻshilmagan (yuristlar topadi).

### 2-noutbukda birinchi marta (bir martalik)
```bash
git clone https://github.com/islomchoriyev607-star/LexCode.git
cd LexCode
git checkout kod-qism
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
copy .env.example .env
.venv\Scripts\python tools\build_index.py
```
Keyin `.env` ga kalitlarni yozing va Claude Code'ni shu papkada oching — u `CLAUDE.md` ni avtomatik oʻqiydi.
