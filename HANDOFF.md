# Huquqiy Navigator — to'liq kontekst (boshqa noutbukda davom ettirish uchun)

Yangilangan: 2026-11-20. Bu fayl shu paytgacha qilingan barcha ishlar, qarorlar va sinov natijalarining xulosasi. Yangi kompyuterda Claude Code'ga birinchi bo'lib shu faylni o'qiting (oxirgi bo'limdagi buyruq).

---

## 1. Loyiha bir jumlada

**Huquqiy Navigator** (@lex_nav_bot) — Telegram bot. Fuqaro vaziyatini matn, ovozli xabar, suhbat yozuvi yoki skrinshot bilan yuboradi. Bot uni lex.uz dagi amaldagi qonun bilan solishtirib, huquq va majburiyatlarni, **kimga, qayerga, qachon** murojaat qilish va qanday dalil saqlashni aytadi, **ariza matnini tayyorlaydi**. Jiddiy holatda murojaat **3 kalitli tekshiruvdan** o'tib, mas'ul idoraga yetkaziladi.

- **Jamoa yetakchisi:** Islom Choriyev (O'zMU yurisprudensiya, 2-kurs; universitet Yuridik klinikasining Bosh koordinatori).
- **Asosiy tamoyil:** bot hukm chiqarmaydi va sud natijasini bashorat qilmaydi. U vaziyatni tushuntiradi, yo'l ko'rsatadi va yuristga ulaydi.

## 2. Tadbir: LexHackathon 2026

- 20–22-noyabr 2026, TDYU, 3-bino. Tashkilotchi: Adliya vazirligi (hamkorlar: TDYU, IT Park, AI Alliance). 54 jamoa, jamoada 3–5 kishi.
- Sovrinlar: 1-o'rin 60 mln, 2-o'rin 40 mln, 3-o'rin 25 mln so'm. G'oliblar uchun Adliya tizimida pilot, inkubatsiya.
- **Baholash:** Yakuniy ball = (Texnik + Biznes + Huquqiy) ÷ 3. Har mentor 5 mezon bo'yicha 1–10 ball qo'yadi.
- **Muddatlar:**
  - 21-noyabr 13:00 — demo muzlatiladi (faqat xato tuzatiladi);
  - 21-noyabr 14:00–17:00 — **checkpoint** (uch mentorning yagona bahosi), 19:00 da natija;
  - 22-noyabr 10:00 — **final pitch**, 15:00 — taqdirlash.

## 3. Trek va tanlangan muammo

- **Trek:** Huquqiy xizmatlar ko'rsatish.
- **Tanlangan rasmiy muammo (1-band):** "Fuqarolarda davlat tashkilotlariga rasmiy murojaat qilish (ariza, shikoyat va taklif berish) ko'nikmasi yetarlicha shakllanmagan."
- Trekning boshqa rasmiy muammolari loyihaga kiritilmadi: notarial ma'lumot, mediatsiya (O'zbekistonda 8%, xorijda 40–80%), shaxsiy hujjatlar bilan tanishish.
- Manba: `materiallar/tashkilotchilar/Treklar - Muammolari.docx`.

## 4. Qabul qilingan qarorlar

| Mavzu | Qaror | Sabab |
|---|---|---|
| Interfeys | Telegram bot | Klinika boti tajribasi; Islom shuni tanladi |
| Stek | Python 3.12 + aiogram 3 + Gemini (bepul kalit) + SQLite FTS5 | Python O'zbekistondagi bot dasturchilariga tanish; qidiruv bepul va AI siz ishlaydi |
| Ishga tushirish | Noutbukda **polling** | Ommaviy server shart emas, bot hammaga baribir ochiq bo'ladi |
| Vercel webhook | Faqat checkpointdan keyin, vaqt qolsa | Funksiya vaqt cheklovi, xotira saqlanmasligi va sozlash vaqti xavf tug'diradi |
| Qonun bazasi | lex.uz → Markdown → SQLite FTS5; AI ga faqat 5–8 modda | Bitta kodeks ~250 ming token, butunlay yuborib bo'lmaydi |
| Aniqlik | Javobdagi har modda bazadan tekshiriladi; har moddaga lex.uz havolasi | Modda o'ylab topilmasligi uchun |
| Sud natijasi | Bashorat qilinmaydi, qonundagi oqibat aytiladi | Sud qarorlarining asosiy qismi ochiq emas |
| Shoshilinch holat | Hayotga xavf bo'lsa → AI dan oldin 102 / 103 | Bot vositachi bo'lmasligi kerak |
| Idoraga yuborish | Faqat **3 kalit** orqali: K1 telefon tasdig'i, K2 AI ishonchlilik bali (0–100), K3 klinika yuristi tasdig'i | Soxta murojaatlarni to'xtatish |
| Javobsiz murojaat | 🔴 murojaat 1–3 kun yopilmasa → klinika yuristiga "shoshilinch" belgisi; idoraga **avtomatik yuborilmaydi** | 3 kalitni chetlab o'tmaslik (Islomning qo'lyozma taklifi asosida) |
| Suhbat yozuvi | Yuborishdan oldin rozilik tugmasi; matnga o'girilgach asl fayl o'chiriladi | Shaxsiy ma'lumot himoyasi |
| Kesh | Faqat moddalar va tushuntirishlar keshlanadi, yakuniy maslahat emas; qonun o'zgarsa tozalanadi | O'xshash holatlar bitta fakt bilan farq qilishi mumkin |
| Video | Checkpointga kirmaydi, finalda vaqt qolsa | Token qimmat (1 daqiqa ≈ 16 ming), vaqt kam |

## 5. Demo ssenariylari

| # | Ssenariy | Kirish | Natija | Checkpoint |
|---|---|---|---|---|
| 1 | Telefonda haqorat va tahdid | Ovozli xabar / suhbat yozuvi | Matn → moddalar → qayerga, muddat, dalil saqlash, **ariza matni** | ✅ |
| 2 | Shubhali SMS | Matn / skrinshot | Firibgarlik belgilari → bank va IIV ga murojaat tartibi, **ariza matni** | ✅ |
| 3 | Jiddiy murojaat | 1-ssenariy davomi | 3 kalit → "Mas'ul idora (demo)" guruhiga tayyor murojaat | ✅ |
| 4 | Ko'chadagi hodisa videosi | Qisqa video | Tasvir → mumkin bo'lgan moddalar → dalil saqlash | Faqat finalda |

**Wow lahzasi:** hakam oldida 30 soniyalik ovozli xabar → 15 soniyada modda havolalari bilan javob → "Murojaat yuborish" → klinika guruhiga tasdiq so'rovi tushadi.

## 6. Biznes-model (qisqa)

Fuqaro uchun bepul. To'lovchilar:
- **advokatlar** — tayyor ish holati uchun;
- **davlat** — tartibli murojaatlar uchun (pilot);
- **banklar va telekom** — firibgarlikka qarshi SMS tekshiruvi;
- **donorlar va NNTlar** — grantlar.

Birinchi 100 foydalanuvchi Yuridik klinika boti orqali keladi.

**Raqobatchilar:**
- **ai.lex.uz (LexAI)** — savollarga javob beradi, lekin media bilan ishlamaydi va murojaatni yetkazmaydi;
- **Lexora** — yuristlar uchun shartnoma tahlili;
- **WakilAI** — eng yaqin raqobatchi: AI yordamchi va yurist-mijoz bozori;
- **ChatGPT** — O'zbekiston qonunchiligini yaxshi bilmaydi.

Tashkilotchilar slaydidagi boshqa mavjud yechimlar: yurxizmat.uz, advice.uz, @adliyaxabaribot, test.adliya.uz.

**Adliya vazirligi infografikasi (taqdimot.pdf):**
- "E-huquqshunos": hujjatni ko'rish vaqti 46 soatdan 2 soatga tushgan, 37 mln hujjat;
- "E-qaror": loyiha tayyorlash 12–15 kundan 5 kunga tushgan.

Pitchda natijani ham vazirlik uslubida, "oldin → keyin" raqami bilan ko'rsatish kerak.

## 7. Bajarilgan ishlar va sinov natijalari

1. **lex.uz o'rganildi.**
   - robots.txt yo'q.
   - Bazada 166 707 hujjat bor (uch tilda).
   - Lotin yozuvidagi versiya: `https://lex.uz/uz/docs/-<ID>` (manfiy ID).
   - HTML tuzilmasi: `CLAUSE_DEFAULT` — modda, `TEXT_HEADER_DEFAULT` — bob, `ACT_TEXT` — matn. `COMMENT`, `CHANGES_ORIGINS` va `INDEXES_ON_REF` olib tashlanadi.
   - "Axborotni taqdim etish shartlari": daromad maqsadida nusxa olish uchun "Adolat" markazining yozma roziligi kerak (normativ hujjatlar uchun istisno bor). Startap bosqichida rasmiy kelishuv kerak bo'ladi.
   - LexUz oflayn bazasi 4,67 GB, litsenziya bilan ishlaydi.
2. **Konvertor** `tools/lex2md.py` ishlaydi. Natijalar:
   - Mehnat kodeksi (`-6257288`): 593 modda;
   - FK 1-qism (`-111189`): 386 modda;
   - FK 2-qism (`-180552`): 811 modda;
   - jami 1790 modda, ~1,85 MB Markdown. Har hujjat ~1–2 soniyada yuklanadi.
3. **Qidiruv** `tools/fts_test.py` (SQLite FTS5):
   - 1790 modda 0,2 soniyada indekslanadi, bitta qidiruv 1–6 ms.
   - 5 savoldan 4 tasida to'g'ri modda topildi. Oddiy so'zlashuvdagi savol ("ish haqi kechiktirilsa") topilmadi, yechim: savolni avval AI bilan yuridik atamalarga o'girish.
4. **Telegram bot:** @lex_nav_bot yaratildi, token tekshirildi (`tools/check_token.py`). Bot guruhga qo'shila oladi, privacy mode yoqilgan.
5. **Gemini kaliti:** AI Studio'da `lex_nav_bot` nomi bilan, bepul tarifda yaratildi. `tools/check_gemini.py` bilan tekshirildi: 50 ta model mavjud.
6. **Gemini sinovi** (`tools/test_gemini.py`):

   | Model | Natija |
   |---|---|
   | gemini-flash-lite-latest | ✅ o'zbekcha savolga 2,6 soniyada javob berdi |
   | gemini-flash-latest | ❌ 503: band |
   | gemini-3.8-flash | ❌ 503: band |
   | gemini-2.5-flash | ❌ 404: yangi foydalanuvchilar uchun yopilgan |

   Xulosa: botda modellar zanjiri bo'lishi shart (qayta urinish → lite model → demo rejimi). Lite model ish haqi nizosi bo'yicha "fuqarolik sudyasi" deb javob berdi; bu yuristlar tomonidan tekshirilishi kerak.
7. **Python 3.12.10, Git 2.56** o'rnatildi (Node 26 oldindan bor edi). PyMuPDF, beautifulsoup4, lxml o'rnatildi.
8. **Rejalar tayyorlandi:** BUILD_PLAN.md, CLAUDE.md, auditor subagenti va Claude Docs'dagi g'alaba rejasi (pastdagi havolalar).
9. **BotFather matnlari va logo promptlari tayyorlandi** (10-bo'lim). `brand/logo.svg` — Claude chizgan qoralama logo (kompas va tarozi), ixtiyoriy.

## 8. Fayllar va havolalar

**Loyiha papkasi** `Desktop\LexCode\`:
```
.env              BOT_TOKEN, GEMINI_API_KEY (maxfiy, git'ga tushmaydi)
.gitignore
CLAUDE.md         loyihaning o'zgarmas qoidalari
BUILD_PLAN.md     START signalidan keyingi 9 bosqich, har birining "bajarildi" sharti
HANDOFF.md        shu fayl
.claude/agents/auditor.md   auditor subagenti (kod va javoblarni tekshiradi, o'zgartirmaydi)
tools/            lex2md.py, fts_test.py, check_token.py, check_gemini.py, test_gemini.py
data/md/          3 kodeks Markdownda
brand/logo.svg    qoralama logo
materiallar/tashkilotchilar/  Treklar - Muammolari.docx, last_HA.pdf, taqdimot.pdf, hackathon_legal_education…pdf
materiallar/oldingi-ishlar/   loyihalar.docx, AI Legal-Check rejasi (md, pdf), LexHack Test Trenajyori (html)
```

**Onlayn hujjatlar:**
- G'alaba rejasi (Claude Docs): https://claude.ai/artifact/J7fJyz2SDXiiWN3LQqcRFB — 14 bo'lim: muammo, yechim, ssenariylar, arxitektura chizmasi, aniqlik, mezonlar, soatma-soat jadval, rollar, biznes, raqobat, pitch, hakamlar savollari, xatarlar, 30 kunlik reja.
- Eski reja (AI Legal-Check, shartnoma tahlili): https://claude.ai/artifact/7bWZCATgzBR2mX9nFjurF3 — arxiv.
- Test trenajyori (saralash uchun, arxiv): https://claude.ai/artifact/R82EpES2y5ZQ6ejxANZeAD

**Manbalar (`materiallar/` ichida):**
- `tashkilotchilar/`: `Treklar - Muammolari.docx` (rasmiy muammolar), `last_HA.pdf` (targ'ibot mentori), `hackathon_legal_education_new_alphabet_2026(1).pdf` (ta'lim mentori), `taqdimot.pdf` (Adliya infografikasi);
- `oldingi-ishlar/`: `loyihalar.docx` (4 ta dastlabki g'oya), AI Legal-Check rejasi, test trenajyori.

## 9. Yangi noutbukda sozlash

1. `LexCode` papkasini butunligicha ko'chiring (zip qilib). **`.env` ham ichida bo'lsin**, unda kalitlar saqlangan.
2. Python 3.12 va Git o'rnating (Windows'da PowerShell orqali):
   ```
   winget install --id Python.Python.3.12 -e --scope user
   ```
   ```
   winget install --id Git.Git -e
   ```
3. Terminalni qayta oching va loyiha papkasida:
   ```
   python -m pip install beautifulsoup4 lxml pymupdf
   ```
4. Kalitlarni tekshiring:
   ```
   python tools/check_token.py
   ```
   ```
   python tools/check_gemini.py
   ```
5. Muhim: **bot bir vaqtda faqat bitta kompyuterda ishga tushirilsin.** Polling rejimida ikki nusxa bir-biriga xalaqit beradi (Telegram "Conflict" xatosini qaytaradi).

## 10. BotFather sozlamalari (o'rnatilmagan bo'lsa)

- **Nomi:** `Huquqiy Navigator`
- **About** (120 belgigacha): `Vaziyatingizni yozing yoki ovoz yuboring: qonun asosida qayerga, qachon va qanday murojaat qilishni aytaman.`
- **Description:**
  ```
  Huquqiy Navigator — davlat tashkilotlariga murojaat qilishda yordamchingiz.

  • Vaziyatingizni matn, ovozli xabar yoki skrinshot bilan yuboring
  • Bot uni amaldagi qonun bilan solishtiradi (lex.uz)
  • Kimga, qayerga, qachon murojaat qilish va qanday dalil saqlashni aytadi
  • Ariza matnini tayyorlab beradi
  • Jiddiy murojaat Yuridik klinika yuristi tekshiruvidan o'tadi

  Bu huquqiy maslahat emas, yakuniy baho yurist zimmasida. Hayotga xavf bo'lsa: 102 / 103.
  ```
- **Buyruqlar** (`/setcommands`):
  ```
  start - Botni ishga tushirish
  yangi - Yangi murojaat
  murojaatlarim - Murojaatlarim holati
  yordam - Qanday foydalanish
  maxfiylik - Shaxsiy ma'lumotlar va rozilik
  ```
- **Logo prompti** (yozuvsiz, odamsiz):
  ```
  Professional minimalist logo icon for a legal-tech assistant named "Huquqiy Navigator". A stylized compass rose whose north needle rises to become the central pillar of a balanced scale of justice, enclosed in a clean circular emblem. Flat vector brand mark, geometric and symmetric, bold simple shapes that stay readable at 64x64 px. Deep navy blue background (#0B2545), warm gold symbol (#C9A227), small white accents. Centered with generous padding for a circular crop. Trustworthy, modern, government-grade fintech style. No people, no faces, no hands, no text, no letters. No gradients, no 3D, no shadows, no photorealism. 1024x1024.
  ```

## 11. Holat va keyingi qadamlar

- **Holat (21-noyabr):** bot va Mini App ishlaydi; bu fayl 20-noyabrdagi boshlangʻich topshiriq. Joriy holat — `CLAUDE.md` va `jurnal/`.
- START kelganda `BUILD_PLAN.md` 0-bosqichdan boshlanadi. Har bosqichdan keyin `auditor` ishga tushiriladi.
- **Jamoadan kerak:**
  - [ ] "Klinika" va "Mas'ul idora (demo)" Telegram guruhlari, bot ikkalasida admin;
  - [ ] asosiy hujjatlar ro'yxati (20–40 ta, lex.uz ID bilan) → `data/laws.txt`;
  - [ ] 3 ssenariy bo'yicha "kimga, qayerga, qachon" ma'lumoti → `data/routes.yaml`;
  - [ ] 30 ta test savoli va to'g'ri javoblar → `eval/questions.yaml`;
  - [ ] klinika statistikasi: oxirgi 3–6 oydagi murojaatlar soni, sohalar, "kimga murojaat qilay?" savollari ulushi; 2–3 ta real (anonim) hikoya;
  - [ ] jamoa tarkibi va rollar.
- **Yuristlar tekshiradigan ochiq savollar:**
  - [ ] telefon suhbatini yozib olish va dalil sifatida ishlatish qonuniymi;
  - [ ] uchinchi shaxs ovozi yoki yuzini AI xizmatiga yuborish shaxsiy ma'lumotlar to'g'risidagi qonunga mosmi;
  - [ ] shaxsiy ma'lumotlarni O'zbekiston hududida saqlash talabi;
  - [ ] murojaatlar to'g'risidagi qonun: anonim murojaat tartibi va ariza shakli;
  - [ ] ish haqi nizolari qaysi sudga tegishli (Gemini javobini tekshirish).

## 12. Xavfsizlik eslatmasi

Bot tokeni va Gemini kaliti chat tarixida qolgan. Hakatondan keyin ikkalasini yangilang:
- bot tokeni: BotFather → `/revoke`;
- Gemini kaliti: AI Studio → kalitni o'chirib, yangisini yaratish.

## 13. Claude Code uchun birinchi buyruq (yangi noutbukda)

> `LexCode` papkasidagi `HANDOFF.md`, `CLAUDE.md` va `BUILD_PLAN.md` ni o'qi. Biz LexHackathon 2026 uchun Huquqiy Navigator Telegram botini quryapmiz. `tools/check_token.py` va `tools/check_gemini.py` bilan kalitlarni tekshir. Keyin men "start" deganda BUILD_PLAN 0-bosqichidan boshla va har bosqichdan keyin `auditor` subagentini ishga tushir.
