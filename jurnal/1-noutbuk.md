# 1-noutbuk jurnali — hujjatlar (`hujjat-qism`)

Yangi yozuv eng yuqoriga yoziladi. Tartib: `ISH_TARTIBI.md`.

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
