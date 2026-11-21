import asyncio, sys, time, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding='utf-8')
from bot import llm, media, config
async def main():
    img = pathlib.Path(sys.argv[1]).read_bytes()
    t = time.time()
    out = await llm.chat(media.VISION_SYSTEM, media.VISION_PROMPT, model=config.MODEL_VISION, image=img, mime='image/png')
    print(f'{time.time()-t:.1f}s\n{out}')
    await llm.client().aclose()
asyncio.run(main())
