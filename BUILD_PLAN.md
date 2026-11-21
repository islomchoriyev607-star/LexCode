# Huquqiy navigator bot — ish rejasi (START signalidan keyin)

Bu fayl — bajarish tartibi. Strategiya, pitch va biznes: [g'alaba rejasi](https://claude.ai/artifact/J7fJyz2SDXiiWN3LQqcRFB).

**Holat (21-noyabr):** 0–9-bosqichlar bajarildi, joriy holat — `CLAUDE.md` va `jurnal/`.

**Rasmiy muammo (Huquqiy xizmatlar, 1-band):** fuqarolarda davlat tashkilotlariga rasmiy murojaat (ariza, shikoyat, taklif) qilish ko'nikmasi yetarli shakllanmagan.

**Qat'iy muddatlar:**
- 21-noyabr 13:00 — demo muzlatiladi (faqat xato tuzatish).
- 21-noyabr 14:00 — checkpoint.
- 22-noyabr 10:00 — final.

---

## START paytida jamoadan kerak

| # | Nima | Kim beradi | Qayerga |
|---|---|---|---|
| 1 | Telegram bot tokeni (@BotFather) | Islom | `.env` → `BOT_TOKEN` (o'zi yozadi, chatga yubormaydi) |
| 2 | Gemini API kaliti (aistudio.google.com) | Islom | `.env` → `GEMINI_API_KEY` |
| 3 | "Klinika" va "Mas'ul idora (demo)" guruhlari, bot ikkalasida admin | Islom | `.env` → `CLINIC_CHAT_ID`, `AUTHORITY_CHAT_ID` (bot o'zi aniqlab beradi) |
| 4 | Asosiy hujjatlar ro'yxati (20–40 ta, lex.uz ID bilan) | Yuristlar | `data/laws.txt` |
| 5 | 3 ssenariy bo'yicha "kimga, qayerga, qachon" ma'lumoti | Yuristlar | `data/routes.yaml` |
| 6 | 30 ta test savoli + to'g'ri modda/idora | Yuristlar | `eval/questions.yaml` |

4–6 kechiksa ham ish to'xtamaydi: sinalgan 3 kodeks (Mehnat, FK 1–2-qism) bilan boshlaymiz.

---

## Bosqichlar

Har bosqich: **bajarildi** sharti tekshirilmaguncha keyingisiga o'tilmaydi. Har bosqich oxirida `auditor` subagenti ishga tushiriladi.

### 0. Muhit (15 daqiqa)
- `git init`, `.gitignore` (`.env`, `data/*.db`, `data/media/`, `__pycache__`), `.env.example`.
- `python -m venv .venv`; `requirements.txt`: aiogram 3, httpx (Groq va Gemini REST), python-dotenv, beautifulsoup4, lxml, pyyaml.
- Gemini: mavjud modellar ro'yxatini API dan olib, `.env` da `MODEL_FAST` va `MODEL_STRONG` belgilanadi (model nomi taxmin qilinmaydi).
- **Bajarildi:** `python -c "import aiogram, httpx"` xatosiz; `.env` git ga tushmaydi.

### 1. Qonun bazasi (30 daqiqa)
- `tools/lex2md.py` → `data/md/*.md` (lotin, modda bo'yicha, har moddaga lex.uz havolasi).
- `tools/build_index.py` → `data/lex.db` (SQLite FTS5: hujjat, modda sarlavhasi, matn, havola).
- **Bajarildi:** moddalar soni chiqadi; "neustoyka kamaytirish", "mehnat shartnomasini bekor qilish" so'rovlari to'g'ri moddani topadi.

### 2. Bot skeleti (30 daqiqa)
- `bot/main.py`: polling rejimi; `/start` → tanishtiruv + shaxsiy ma'lumotga rozilik tugmasi + ogohlantirish.
- Kod webhook rejimiga ham tayyor (keyin Vercel uchun), lekin hozir faqat polling.
- **Bajarildi:** telefondan `/start` → rozilik → matnli xabarga javob.

### 3. Media → matn (45 daqiqa)
- Ovozli xabar, audio fayl, rasm (skrinshot) → Gemini → matn. Yuborishdan oldin rozilik tugmasi.
- Matn saqlanadi, asl media o'chiriladi. 20 MB dan katta fayl → tushunarli xabar.
- **Bajarildi:** 30 soniyalik o'zbekcha ovozli xabar to'g'ri matnga aylanadi (sheva va so'kinish bilan ham sinaladi).

### 4. Tahlil zanjiri (1,5 soat)
0. **Ijtimoiy soha tanlovi (Islom taklifi, 20-noyabr):** rol foydalanuvchiga emas, **har bir murojaatga** biriktiriladi: vaziyat yuborilgach, bot "Bu vaziyatda siz kimsiz?" deb so'raydi (bitta odam bir murojaatda talaba, boshqasida xaridor bo'lishi mumkin). Tugmalar: Talaba, Xodim (ishchi), Tadbirkor, Xaridor (iste'molchi), Boshqa. Tanlangan soha AI ga kontekst sifatida beriladi va o'sha sohaga oid qonunlar qidiruvda **birinchi o'ringa chiqariladi** (boshqa qonunlar chiqarib tashlanmaydi: talabaning telefoni o'g'irlansa ham Jinoyat kodeksi kerak). Maqsad: javob tezroq va aniqroq. Qonun foydalanuvchiga moslashmaydi va uni oqlamaydi; bot faqat vaziyatni uning sohasidan kelib chiqib tahlil qiladi. Talaba uchun bazaga "Ta'lim to'g'risida"gi qonun qo'shiladi.
   - Har javobda ogohlantirish: "Javob umumiy qonunchilikka asoslangan. Tashkilotning ichki tartib qoidalari (masalan, universitetning ichki tartib qoidalari) hisobga olinmagan."
1. Shoshilinchlik filtri: hayotga xavf → AI siz darhol 102 / 103.
2. Saralash (`MODEL_FAST`): soha, daraja (🟢/🟡/🔴), murakkab bo'lsa `MODEL_STRONG`.
3. Savolni yuridik atamalarga o'girish → FTS qidiruv → 5–8 modda.
4. Javob faqat topilgan moddalar bilan; **tekshiruvchi:** javobdagi har modda `lex.db` da bormi, yo'q bo'lsa qayta yaratiladi.
- **Bajarildi:** 5 test savolida moddalar havola bilan chiqadi, bazada yo'q modda chiqmaydi.

### 5. Natija kartasi va ariza (45 daqiqa) — rasmiy muammoning yechimi
- Karta: vaziyat, huquq, majburiyat, kimga / qayerga / qachon, qanday dalil saqlash, moddalar + havolalar, ogohlantirish.
- "Ariza tayyorlash" tugmasi → rasmiy shakldagi ariza matni (nusxa olish uchun).
- **Bajarildi:** 1- va 2-ssenariy boshidan oxirigacha ishlaydi.

### 6. 3 kalit (1 soat)
- K1: "Kontakt ulashish" tugmasi, kunlik limit. K2: AI ishonchlilik bali 0–100. K3: Klinika guruhida "Tasdiqlash / Rad etish / Aniqlashtirish" (faqat guruh adminlari bosa oladi).
- Tasdiqlansa → "Mas'ul idora (demo)" guruhiga tayyor murojaat; foydalanuvchiga holat xabari.
- Yakunlanmagan 🔴 murojaat: 1–3 kun faollik bo'lmasa → klinikaga "shoshilinch" belgisi (demoda taymer daqiqalarda). Idoraga avtomatik yuborilmaydi.
- **Bajarildi:** 3-ssenariy jonli ishlaydi; adminsiz odam tasdiqlay olmaydi.

### 7. Zaxira va o'lchov (45 daqiqa)
- Demo rejimi: 3 ssenariy uchun tayyor javoblar (Gemini yoki internet ishlamasa).
- `eval/run_eval.py`: 30 savol → "to'g'ri modda topildi" foizi.
- **Bajarildi:** foiz chiqdi; internetsiz demo rejimi ishlaydi.

### 8. Audit va muzlatish (21-noyabr 12:30–13:00)
- `auditor` to'liq tekshiruv → kritik xatolar tuzatiladi → 13:00 muzlatish.

### Checkpointdan keyin (vaqt qolsa)
- Webhook rejimi + Vercel (maxfiy token, takroriy update himoyasi, darhol "qabul qilindi").
- Video tahlili. Holatni kuzatish.

### 9. Navigator: idoraga yetib borish va ariza (20-noyabr, qisman bajarildi)
- [x] **Transport.** Qadamda "🚌 Qanday boraman": Yandex xaritada idora tuman/joylashuv atrofida qidiriladi. Foydalanuvchi idorani bosadi → «Yoʻnalish» → 🚌 va avtobus/metro raqamlarini koʻradi.
- [ ] **Aniq transport yoʻnalishi (kalit kerak).** Yandex Places (Geosearch) API kaliti → idoraning aniq koordinatasi. Keyin toʻgʻridan-toʻgʻri havola `rtext=<foydalanuvchi>~<idora>&rtt=mt` tuziladi, bot avtobus/metro raqamlarini oʻzi yozadi.
  - Matnli manzil bilan sinaldi: geokoder tashkilotni emas, faqat mahallani topadi (masalan, "Chilonzor dahasi"). Shuning uchun koordinatasiz bu yoʻl ishonchsiz.
  - Idoralar roʻyxati (tuman → manzil, koordinata) klinika bilan birga tekshirilib, `data/` ga yoziladi.
- [x] **Ariza PDF.** Times New Roman 14, xatboshi chekinishi, eni boʻyicha tekislash. Shaxsiy maʼlumot joylari qoʻlda toʻldirish uchun chiziq bilan.
- [x] **Chop etish joylari.** PDF ostida va Mini App qadamida "🖨 Chop etish joylari": tuman/joylashuv atrofidagi nusxa koʻchirish xizmatlari xaritada.
- [ ] **Print hamkorlar.** Bir nechta nusxa koʻchirish markazi bilan shartnoma: bot ularning manzilini birinchi koʻrsatadi. Ariza fayli hamkorga toʻgʻridan-toʻgʻri yuboriladi (foydalanuvchi roziligi bilan), foydalanuvchi faqat kelib oladi.
- [ ] **Qogʻoz holida yetkazish.** Chop etilgan arizani manzilga yetkazish (kuryer yoki hamkor orqali). Pullik qoʻshimcha xizmat; narx va hamkor keyin aniqlanadi.

### 10. Daromad modeli (kelajak; hozir faqat ixtiyoriy donat)
- [ ] **Donat — joriy bosqichda ixtiyoriy.** Faqat ish oxirida ("Hal boʻldi" ekrani) yumshoq taklif: "Yordam bergan boʻlsak, loyihani qoʻllab-quvvatlang". Bosim yoʻq, oʻtkazib yuborish oson, xizmat donatsiz ham toʻliq ishlaydi.
  - Variant: Telegram Stars (bot ichida, provayder shart emas). Click/Payme keyinroq.
- [ ] **Pullik tarif — kelajakda.** Ishni toʻliq yechish uchun kuchli modellarga oʻtilganda:
  - bepul qismi: yoʻl koʻrsatish va qonun havolalari;
  - pullik qismi: kuchli modelda chuqur tahlil, ariza yozib berish va kuzatish, yurist tasdigʻi, qogʻoz yetkazish.
  - Narx model xarajatiga qarab hisoblanadi.
  - Qoida oʻzgarmaydi: xavf holatida (112/102/103) va asosiy yoʻl koʻrsatishda pul soʻralmaydi.

---

## Tuzilma (rejalashtirilgan)
```
LexCode/
  bot/        main.py, handlers/, pipeline/ (triage, search, answer, validate), keys.py
  tools/      lex2md.py, build_index.py
  data/       laws.txt, routes.yaml, md/, lex.db
  eval/       questions.yaml, run_eval.py
  demo/       tayyor javoblar
  .env.example  requirements.txt  CLAUDE.md  BUILD_PLAN.md
```
