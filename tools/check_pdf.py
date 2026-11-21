"""Ariza PDF koʻrinishini tekshirish: namunaviy matndan PDF yasaydi (AI chaqirilmaydi)."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from bot.navflow import make_pdf  # noqa: E402

SAMPLE = """Toshkent shahar Chilonzor tumani davlat mehnat inspeksiyasi boshlig'iga
[F.I.Sh.] dan
Manzil: [manzil]
Telefon: [telefon]

ARIZA

Men, [F.I.Sh.], «Namuna» MChJda 2025-yil martidan buyon hisobchi lavozimida ishlayman. Ish beruvchi so'nggi ikki oy davomida ish haqimni to'lamayapti, og'zaki murojaatlarim natija bermadi.

Mehnat kodeksining 151-moddasiga ko'ra ish haqi o'z vaqtida to'lanishi shart. Ish beruvchining harakatlari mening mehnat huquqlarimni buzmoqda.

Yuqoridagilarni inobatga olib, ish beruvchida tekshiruv o'tkazishingizni va to'lanmagan ish haqimni undirishga choralar ko'rishingizni so'rayman.

Ilovalar:
1. Mehnat shartnomasi nusxasi.
2. Ish haqi to'lanmaganini tasdiqlovchi bank ko'chirmasi.

Sana: [sana]
Imzo: [imzo]"""

out = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'logs/sample_ariza.pdf')
out.write_bytes(make_pdf(SAMPLE))
print(out, out.stat().st_size, 'bayt')
