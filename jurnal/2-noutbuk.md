# 2-noutbuk jurnali — kod (`kod-qism`)

Yangi yozuv eng yuqoriga yoziladi. Tartib: `ISH_TARTIBI.md`. Ishni boshlashdan oldin `jurnal/1-noutbuk.md` ni oʻqing.

## 2026-11-21 — Mini App UI, transport va idoralar bazasi, kutish ekrani
- **Nima qilindi:**
  - **Mini App UI:** 3D shar (Three.js) olib tashlandi; ekran chetida ong osti darajasidagi neon nur (Weber ΔL/L ≈ 0.02, σ = 9px, 14 s aylanish); bitta shrift — Inter (Manrope/Unbounded da қ, ғ, ҳ, ў yoʻq edi); `viewport` meta qoʻshildi — telefonda ekrandan chiqib ketish tuzatildi.
  - **Idoralar bazasi:** `tools/build_offices.py` → `data/offices.json` (OpenStreetMap): Toshkent, 25 sud (fuqarolik/jinoyat/maʼmuriy/iqtisodiy), 116 IIB (boʻlim/tayanch punkti), 15 FHDYO. Prokuratura, GAI, arxiv, viloyat idoralari chiqarib tashlangan.
  - **Transport:** navigator qadamida sud/IIB/FHDYO boʻlsa — eng yaqin idora (joylashuv yoki tuman boʻyicha), "Qayerga"da aniq nom va manzil, "Qanday boraman" → koordinatagacha jamoat transporti marshruti (Yandex, `rtt=mt`). Boshqa idoralar — atrofdagi joylar qidiruvi.
  - **Chop etish joylari:** "hali qoʻshilmagan" oʻrniga atrofdagi haqiqiy nusxa markazlari (Yandex qidiruvi).
  - **Kutish ekrani (Mini App):** xarita, chop etish, PDF bosilganda "qidiryapmiz… / chatga yuboryapman…" va ✓.
  - **3 kalit:** `CLINIC_CHAT_ID`, `AUTHORITY_CHAT_ID` `.env` ga ulandi (guruhlar: KLINIKA YURISTI, IDORA).
  - `tools/test_pipeline.py`: `t` oʻzgaruvchisi `t()` funksiyasini yopib qoʻyardi — tuzatildi.
- **Qaysi fayllar:** `webapp/index.html`, `bot/navflow.py`, `tools/build_offices.py`, `data/offices.json`, `tools/test_pipeline.py`
- **Sinaldi:** test_danger, test_script, test_validate, test_navflow, test_webapi, test_navapi, test_pipeline ✅; Mini App 360px da ✅; Yandex marshrut havolasi ✅.
- **Keyingi noutbuk uchun:** prezentatsiya uchun yangiliklar: idoralar bazasi (156 ta haqiqiy manzil), aniq transport marshruti, kutish ekrani. Skrinshot kerak boʻlsa — bot shu noutbukda ishlaydi.
- **Ochiq savol / xavf:** 3 kalit zanjiri Telegram'da oxirigacha hali sinalmagan. Yangi hayot va Yangi Toshkent tumanlari OSM da yoʻq. Tumanlararo sud faqat binosi joylashgan tumanga bogʻlangan.
