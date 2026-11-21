"""Tahlil zanjirini test vaziyatlarda sinaydi: vaqt, daraja, manbalar, tekshiruv natijasi."""
import asyncio, sys, time, pathlib, re
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding='utf-8')
from bot import pipeline, render, llm
from bot.i18n import t

CASES = [
    ('xodim', "Ish beruvchi 2 oydan beri ish haqimni bermayapti, so'rasam ishdan bo'shataman deyapti."),
    ('boshqa', "Telefonda notanish odam meni so'kdi va uyingga borib o'ldiraman deb qo'rqitdi. Suhbatni yozib oldim."),
    ('boshqa', "SMS keldi: kartangiz bloklandi, blokdan chiqarish uchun kelgan kodni shu raqamga yuboring. Kodni yubordim, kartamdan 3 million yechib olishdi."),
    ('xaridor', "Do'kondan telefon oldim, 3 kunda buzildi. Sotuvchi qaytarib olmayapti, pulni qaytarmayman deydi."),
    ('talaba', "Universitetda dekanatga ariza berdim, bir oy bo'ldi javob yo'q. Qayerga shikoyat qilsam bo'ladi?"),
]

async def main():
    sel = [int(x) for x in sys.argv[1:]] or range(len(CASES))
    for i in sel:
        role, text = CASES[i]
        t0 = time.time()
        r = await pipeline.analyze(text, role)
        dt = time.time() - t0
        print(f'\n######## {i+1}. [{role}] {text[:70]}…')
        print(f'vaqt {dt:.1f}s | daraja {r.level} | xavf {r.danger} | so\'rovlar {r.triage.get("sorovlar")} | ishonch {r.answer.get("ishonch")}')
        print('berilgan:', [f'{a.abbr} {a.num}' for a in r.articles])
        print('manba:', [f'{a.abbr} {a.num}' for a, _ in r.cited], '| olib tashlandi:', r.removed)
        print('--- karta ---')
        print(re.sub(r'<[^>]+>', '', render.card(r, t('uz', 'ROLES')[role], 'uz')))
    await llm.client().aclose()

asyncio.run(main())
