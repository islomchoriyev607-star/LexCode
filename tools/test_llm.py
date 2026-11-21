"""bot/llm.py ni sinash: zanjir (asosiy → zaxira), JSON rejim, majburan buzilgan model bilan zaxiraga o'tish."""
import asyncio, sys, time, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding='utf-8')
from bot import llm, config


async def main():
    t = time.time()
    out = await llm.chat('Qisqa javob ber, o\'zbek tilida.', 'Salom! Bir jumlada o\'zingni tanishtir.', model=config.MODEL_FAST)
    print(f'FAST {time.time()-t:.1f}s:', out[:200])
    t = time.time()
    js = await llm.chat('Faqat JSON qaytar.', 'Matn: "Qo\'shnim meni so\'kdi va urib qo\'yaman dedi". '
                        'JSON: {"soha": "...", "daraja": "oddiy|muhim|jiddiy|xavf", "kalit_sozlar": ["..."]}', json_mode=True)
    print(f'STRONG json {time.time()-t:.1f}s:', llm.parse_json(js))
    t = time.time()
    out = await llm.chat('Qisqa javob ber.', '2+2 nechchi? Faqat raqam.', model='groq:mavjud-emas-model')
    print(f'Buzuq model → zaxira {time.time()-t:.1f}s:', out)
    await llm.client().aclose()

asyncio.run(main())
