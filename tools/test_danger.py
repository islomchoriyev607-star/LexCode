"""Xavf filtrini sinash: noto'g'ri manfiy (xavfni o'tkazib yuborish) — kritik; noto'g'ri musbat — kichik."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding='utf-8')
from bot.pipeline import is_danger

DANGER = [
    "U meni o'ldiraman dedi", "U meni oldiraman dedi", "Ozimni oldiraman", "O‘zimni o‘ldiraman", "Erim meni urdi",
    "Qo'shnim meni kaltakladi", "Ko'chada do'pposlashdi", "Uyda zo'ravonlik bor", "O'zimni osib qo'yaman", "Osaman o'zimni",
    "Bolamni o'g'irlab ketishdi", "Bolamni ogirlab ketishdi", "Onam hushidan ketdi", "Nafas olmayapti", "Убью тебя сказал",
    "Он меня бьет", "Ўлдираман деди", "пичоқ билан келди", "Hozir eshik oldida pichoq bilan turibdi", "Meni urayapti",
    "Qoni ketyapti, qon ketyapti", "Odam o'g'irlashdi",
]
SAFE = [
    "Telefonimni o'g'irlab ketishdi", "Kvartirani bankka garovga qo'ydim", "Hozir uydaman", "Uyda ishlayman",
    "Hujjatga muhr bosilmagan", "Tugma bosildi", "Qurolli kuchlarda xizmat qilganman", "Ish haqimni bermayapti",
    "Do'kondan telefon oldim, buzildi", "Dekanat javob bermayapti", "Kartamdan pul yechib olishdi",
    "Ish beruvchi meni ishdan bo'shatdi", "Telefonda meni so'kdi",
]
fn = [t for t in DANGER if not is_danger(t)]
fp = [t for t in SAFE if is_danger(t)]
print(f'Xavf: {len(DANGER) - len(fn)}/{len(DANGER)} topildi. O\'tkazib yuborildi (KRITIK): {fn}')
print(f'Xavfsiz: {len(SAFE) - len(fp)}/{len(SAFE)} to\'g\'ri. Ortiqcha signal: {fp}')
sys.exit(1 if fn else 0)
