# Ikki noutbukda ishlash tartibi (qatʼiy)

Bitta GitHub akkaunt, ikki noutbuk, har birida alohida Claude Code. Claude'lar bir-birining suhbatini koʻrmaydi. Ular faqat shu fayl, `CLAUDE.md` va `jurnal/` orqali "gaplashadi".

## 1. Kim nima qiladi — boshqasining ishiga aralashilmaydi

| | 1-noutbuk | 2-noutbuk |
|---|---|---|
| **Vazifa** | Hujjatlar | Kod + **bot serveri** |
| **Bot ishlaydimi?** | ❌ **Yoʻq — hech qachon ishga tushirilmaydi** | ✅ Ha, yagona server (`tools\run_demo.py`) |
| **Tarmoq (branch)** | `hujjat-qism` | `kod-qism` |
| **Faqat shu fayllarni oʻzgartiradi** | `README.md`, `HANDOFF.md`, `BUILD_PLAN.md`, `docs/`, `prezentatsiya/`, `brand/`, `jurnal/1-noutbuk.md` | `bot/`, `webapp/`, `tools/`, `data/`, `eval/`, `requirements.txt`, `.env.example`, `jurnal/2-noutbuk.md` |

**Umumiy fayllar** (`CLAUDE.md`, `ISH_TARTIBI.md`, `.gitignore`) faqat kelishib oʻzgartiriladi. Kim oʻzgartirsa, oʻz jurnaliga yozadi.

Claude uchun qoida: **oʻz noutbukiga tegishli boʻlmagan faylni oʻzgartirma.** Kerak boʻlsa, oʻz jurnalingga "2-noutbukdan soʻrov: …" deb yoz va toʻxta.

### Bot faqat bitta joyda ishlaydi
Bot faqat **2-noutbukda** ishga tushiriladi.
- Bitta token bilan ikki kompyuterda bot yoqilsa, Telegram `TelegramConflictError` beradi va xabarlar yoʻqoladi.
- 1-noutbukdagi Claude `run_demo.py` va `bot.main` ni ishga tushirmaydi.
- `.env` faqat 2-noutbukda toʻliq boʻladi.
- Tunnel manzili har ishga tushganda oʻzgaradi; menyu tugmalari avtomatik yangilanadi.

## 2. Ishni boshlashdan oldin (har safar)
```bash
git checkout main
git pull origin main
git checkout <oʻz-tarmogʻing>        # hujjat-qism yoki kod-qism
git merge main                        # boshqa noutbukning tayyor ishi keladi
```
Keyin **ikkala jurnalni oʻqi** (`jurnal/1-noutbuk.md`, `jurnal/2-noutbuk.md`): kim nima qildi, nima kutilmoqda.

## 3. Har bir tayyor ishdan keyin — darhol
1. Oʻz jurnalingga yozuvni **eng yuqoriga** qoʻsh (namuna pastda).
2. Commit va push:
   ```bash
   git add <oʻzgargan fayllar>
   git commit -m "Qisqa va aniq: nima qilindi"
   git push origin <oʻz-tarmogʻing>
   ```
3. GitHub'da Pull Request oching (`<oʻz-tarmogʻing>` → `main`) va birlashtiring (merge).

Kichik va tez-tez commit qilish kerak: hakamlar commit tarixini koʻradi.

## 4. Jurnal yozuvi namunasi
```markdown
## 2026-11-21 15:40 — Mini App: ovoz yozish tuzatildi
- Nima qilindi: …
- Qaysi fayllar: webapp/index.html
- Sinaldi: test_navapi.py ✅, telefonda ✅
- Keyingi noutbuk uchun: … (yoki "yoʻq")
- Ochiq savol / xavf: …
```

## 5. Xavfsizlik (repo PUBLIC)
- `.env` hech qachon yuklanmaydi; haqiqiy kalitlar faqat har noutbukning oʻz `.env` faylida turadi. GitHub'da faqat boʻsh `.env.example`.
- `data/app.db` (foydalanuvchilar), `logs/`, `.venv/` yuklanmaydi (`.gitignore`).
- Push qilishdan oldin tekshiring: `git status` va `git diff --cached`. Kalit (`gsk_…`, `AIza…`, `…:AA…` bot tokeni) koʻrinsa — toʻxtang.

## 6. Merge conflict chiqsa
Claude Code'ga yozing: *"merge conflict'larni ikkala tomonning oʻzgarishini saqlagan holda hal qil"*. Hal qilingach testlarni ishga tushiring.

## Muddatlar (21-noyabr)
- 14:00 — checkpoint, hamma universitetda; MVP va prototip tayyor boʻlishi kerak.
- 19:00 gacha — PDF prezentatsiya va GitHub'dagi loyiha tayyor.
