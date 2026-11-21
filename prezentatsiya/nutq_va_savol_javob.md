# Huquqiy Navigator — nutq rejasi va hakamlar savollariga javoblar

Prezentatsiya: `Huquqiy_Navigator_LexCode.pdf` (8 slayd, yangi lotin). Slaydda matn kam — qolganini ogʻzaki aytamiz.
Vaqt: har slaydga ~40–60 soniya, jami 5–6 daqiqa.

---

## Nutq rejasi (slaydma-slayd)

**1. Sarlavha (Islom)**
"Assalomu alaykum. Biz — LexCode jamoasi, loyihamiz — Huquqiy Navigator. Huquqi buzilgan odam qayerga, qachon va qanday murojaat qilishni bilmaydi. Biz unga choʻntagidagi yoʻlboshchini beramiz — Telegram bot va Mini App."

**2. Biz kimmiz (Islom)**
"Jamoada yuristlar va dasturchi-dizayner bor. Foydalanuvchi vaziyatini yozadi, gapiradi yoki skrinshot yuboradi. AI uni lex.uz dagi amaldagi qonun bilan solishtiradi va yoʻl koʻrsatadi: eng yaqin idoraning aniq manzili, u yerga qaysi avtobus yoki metro bilan borish, muddat va tayyor ariza PDF koʻrinishida. Har bir modda lex.uz havolasi bilan; bot hukm chiqarmaydi."

**3. Muammo (Shaʼbona)**
"2026-yilning 8 oyida Prezident Xalq qabulxonalariga 557 ming murojaat kelgan. Ularning 14–16 foizi takroriy, 20 foizga yaqini oddiy huquqiy tushuntirish bilan yopiladi. Imtiyozli transport kartasi arizalarining 64,7 foizi rad etilgan. Sabab — odamlar qayerga va qanday yozishni bilmaydi."

**4. Bozor (Shaʼbona)**
"TAM — internetdan foydalanadigan 24,4 mln voyaga yetgan fuqaro. SAM — my.gov.uz dagi 15 mln foydalanuvchi, ular onlayn murojaatga tayyor. SOM — 1-yilda SAM ning 1 foizi (150 ming), 3-yilda 3 foizi (450 ming). Asosiy auditoriya: ishchilar, talabalar, kichik biznes."

**5. Raqobatchilar (Mirsoat)**
"Umumiy AI chatbotlar tez, lekin Oʻzbekiston qonunini bilmaydi va modda raqamini oʻylab topadi. Advokat ishonchli, lekin qimmat va hammaga yetmaydi. Biz ikkalasining kuchini birlashtiramiz: AI tezligi va har modda bazadan tekshiriladi. Ikkalasida ham yoʻq narsa — eng yaqin idoragacha jamoat transporti marshruti."

**6. Monetizatsiya (Shaʼbona)**
"Fuqaro uchun asosiy yoʻl koʻrsatish bepul — xavf holatida hech qachon pul soʻralmaydi. Daromad: premium (oyiga 29 ming soʻm yoki bitta ariza 15 ming soʻm), tashkilotlarga litsenziya (oyiga 1,5–3 mln soʻm) va chop etish hamkorlaridan 10 foiz komissiya."

**7. KPI (Islom)**
"Hozir MVP ishlaydi: bot va Mini App, 7 ta qonun, 2 942 modda, 4 til, Toshkentdagi 156 ta idora manzili. 6 oyda — 10 ming foydalanuvchi va 2 ta universitet bilan pilot. 1 yilda — 150 ming foydalanuvchi, 3 yilda — 450 ming va davlat portallari bilan integratsiya."

**8. Jamoa (Islom)**
"Islom — loyiha rahbari, yurisprudensiya 2-kurs, Yuridik klinikada 1 yil tajriba. Mirsoat — CTO va dizayner, 2 yil dizayn tajribasi. Shaʼbona — biznes analitik va yurist. 3 oydan beri birgamiz. Endi jonli demoni koʻrsatamiz."

---

## Hakamlar savollari va javoblar

### Mahsulot va ishonchlilik

**AI notoʻgʻri modda aytib qoʻysa-chi?**
AI moddani oʻzi oʻylab topa olmaydi. U faqat bazadagi (lex.uz) moddalardan tanlaydi. Javob matnidagi har qanday modda raqami avtomatik olib tashlanadi. Manbalar faqat bazadan, lex.uz havolasi bilan koʻrsatiladi. Muddatlar (masalan, "15 kun") ham faqat tanlangan modda matnida boʻlsa koʻrsatiladi.

**Bot huquqiy maslahat beryaptimi? Javobgarlik kimda?**
Yoʻq. Bot hukm chiqarmaydi va sud natijasini bashorat qilmaydi — qonunda belgilangan yoʻlni koʻrsatadi. Har javob oxirida: "Bu huquqiy maslahat emas, yakuniy baho yurist zimmasida." Jiddiy holatda murojaat faqat Yuridik klinika yuristi tasdiqlagandan keyin idoraga ketadi.

**Soxta yoki yolgʻon murojaatlar koʻpaymaydimi?**
Idoraga yuborish 3 kalit orqali ishlaydi:
1. telefon raqami tasdigʻi;
2. AI bahosi (vaziyat qanchalik asosli);
3. klinika yuristi tasdigʻi.

Avtomatik yuborish yoʻq.

**Hayotga xavf boʻlsa-chi?**
Xavf belgilari (tahdid, zoʻravonlik, oʻz joniga qasd) AI tahlilidan oldin tekshiriladi. Darhol 112 / 102 / 103 raqamlari koʻrsatiladi. Bot vositachi boʻlmaydi.

**Maʼlumotlar xavfsizligi?**
- Ovoz va rasm matnga aylantirilgach oʻchiriladi.
- Kalitlar kodda emas, alohida sozlamada saqlanadi.
- Mini App soʻrovlari Telegram imzosi (HMAC) bilan tekshiriladi: bir foydalanuvchi boshqasining murojaatini koʻra olmaydi.

**Qonun oʻzgarsa-chi?**
Qonunlar lex.uz dan avtomatik yuklab olinadi va bazaga qayta yoziladi (`tools/lex2md.py`, `tools/build_index.py`). Yangilash — bir buyruq.

**Nechta qonun bor? Yetarlimi?**
Hozir 7 ta: Mehnat, Fuqarolik (2 qism), Jinoyat, Maʼmuriy javobgarlik kodekslari, Isteʼmolchilar huquqlari va Murojaatlar toʻgʻrisidagi qonunlar — jami 2 942 modda. Bular eng koʻp uchraydigan murojaatlarni qamraydi. Reja — 50+ qonun.

**Idoralar manzili qayerdan? Transport qanday?**
- Toshkent boʻyicha 156 ta idora bazada: 25 ta sud, 116 ta IIB boʻlimi va tayanch punkti, 15 ta FHDYO. Manba — OpenStreetMap ochiq maʼlumotlari.
- Foydalanuvchi joylashuvini yuborsa yoki tumanini yozsa, bot eng yaqin idorani topadi.
- "Qanday boraman" tugmasi Yandex xaritada shu idoragacha jamoat transporti marshrutini ochadi: avtobus va metro raqamlari bilan.
- Bazada yoʻq idoralar uchun — atrofdagi joylar qidiruvi. Viloyatlar keyingi bosqichda qoʻshiladi.

**Arizani qayerda chop etaman?**
"Chop etish joylari" tugmasi atrofdagi nusxa koʻchirish markazlarini xaritada koʻrsatadi. Rejada — hamkor markazlar bilan shartnoma: ariza ularga toʻgʻridan-toʻgʻri yuboriladi, fuqaro faqat kelib oladi.

**Nega Telegram?**
Oʻzbekistonda eng keng tarqalgan messenjer. Ilova oʻrnatish shart emas, ovozli xabar odatiy.

### Bozor va raqobat

**SOM ni qanday hisobladingiz?**
SAM (my.gov.uz dagi 15 mln foydalanuvchi) ning 1 foizi — 1-yilda, 3 foizi — 3-yilda. Startap uchun konservativ meʼyor. Eng "issiq" auditoriya — arizasi rad etilgan va takroriy murojaat qilayotganlar.

**ChatGPT ham shuni qila oladi-ku?**
Umumiy AI Oʻzbekistonning amaldagi qonunini bilmaydi, eski yoki boshqa davlat qonunini aytishi va modda raqamini oʻylab topishi mumkin. U yoʻlni qadamma-qadam kuzatmaydi va idora talabiga mos ariza bermaydi. Bizda har modda bazadan tekshiriladi va lex.uz havolasi bilan beriladi.

**Advokatdan farqingiz?**
Advokat maslahati taxminan 200–500 ming soʻm turadi va hammaga yetmaydi. Biz oddiy holatlarda daqiqalar ichida bepul yoʻl koʻrsatamiz. Murakkab holatda esa advokat yoki klinikaga yoʻnaltiramiz — raqobatchi emas, birinchi qadammiz.

### Monetizatsiya (biznes savollari)

**Kim toʻlaydi?**
- Fuqaro — premium uchun.
- Tashkilotlar (B2B) — universitetlar (talabalar murojaati), korxonalar HR boʻlimi (xodimlar savollari).
- Davlat (B2G) — hokimliklar, Xalq qabulxonalari: notoʻgʻri va takroriy murojaatlar kamayadi.
- Chop etish hamkorlari — komissiya.

**Narxlar qayerdan?** (taxminiy, 2026-yil noyabr)
- Premium — 29 000 soʻm/oy: bir oylik mobil internet narxiga yaqin, talaba ham toʻlay oladi.
- Bitta ariza — 15 000 soʻm: notarius yoki yozuvchi xizmatidan arzon.
- B2B litsenziya — 1,5–3 mln soʻm/oy: bitta yuristning oylik ish haqidan ancha past.
- Bular taxminiy; pilot paytida foydalanuvchilar bilan sinab aniqlashtiramiz.

**Unit economics?**
- Bitta tahlilning AI xarajati taxminan 0,002–0,005 $ (25–65 soʻm).
- Bitta premium foydalanuvchi oyiga 29 000 soʻm toʻlaydi.
- Shuning uchun marja yuqori: asosiy xarajat — marketing va server.

**1 yil va 3 yil daromadi qanday chiqdi?**
- **1-yil:** 150 ming foydalanuvchidan 1% premium = 1 500 kishi × 29 000 × 12 ≈ 0,52 mlrd soʻm. Unga 5 ta B2B mijoz × 2 mln × 12 ≈ 0,12 mlrd qoʻshiladi. Jami ≈ 0,6 mlrd soʻm.
- **3-yil:** 450 ming foydalanuvchidan 2% premium = 9 000 × 29 000 × 12 ≈ 3,1 mlrd. Unga 30 ta B2B × 2,5 mln × 12 ≈ 0,9 mlrd qoʻshiladi. Jami ≈ 4 mlrd soʻm.

**Nega asosiy xizmat bepul?**
Ijtimoiy loyiha: huquqni bilish hammaga kerak. Bepul qism auditoriyani yigʻadi, daromad esa tashkilotlar va qoʻshimcha xizmatlardan keladi.

**Marketing qanday?**
- Universitet yuridik klinikalari (bizning tarmoq).
- Talabalar va mahalla guruhlari.
- Telegram kanallar.
- Hokimliklar bilan hamkorlik.
- Har bir yopilgan ish — tavsiya.

**Davlat xizmatlari bilan raqobatlashasizmi?**
Yoʻq — toʻldiramiz. my.gov.uz murojaatni qabul qiladi, biz esa odamga qaysi idoraga, nima deb yozishni oʻrgatamiz. Bunda rad etilgan va takroriy arizalar kamayadi.

### Jamoa va reja

**Keyingi 6 oyda nima qilasiz?**
- 50+ qonun.
- Viloyatlardagi idoralar manzili (hozir Toshkent — 156 ta).
- Chop etish hamkorlari bilan shartnoma.
- 2 ta universitet bilan pilot.
- 10 ming foydalanuvchi.

**Eng katta xavf nima?**
AI xatosi va foydalanuvchi ishonchi. Shuning uchun:
- modda tekshiruvi;
- yurist tasdigʻi (3 kalit);
- "huquqiy maslahat emas" ogohlantirishi.

---

> ⚠️ 3-slayddagi statistik raqamlar jamoa yigʻgan manbalardan olingan: Xalq qabulxonalari hisobotlari, gov.uz/mintrans, insonhuquqlari.uz. Taqdimotdan oldin havolalarni bir marta ochib tekshiring — hakamlar manba soʻrashi mumkin.
