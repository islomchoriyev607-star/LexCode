"""GEMINI_API_KEY ni .env dan o'qib, mavjud modellar ro'yxatini oladi (kalit ekranga chiqarilmaydi)."""
import json, sys, urllib.request, pathlib
sys.stdout.reconfigure(encoding='utf-8')
env = pathlib.Path(__file__).resolve().parent.parent / '.env'
key = next(l.split('=', 1)[1].strip() for l in env.read_text(encoding='utf-8').splitlines() if l.startswith('GEMINI_API_KEY='))
req = urllib.request.Request('https://generativelanguage.googleapis.com/v1beta/models?pageSize=200',
                             headers={'x-goog-api-key': key})
data = json.load(urllib.request.urlopen(req, timeout=30))
models = [m for m in data.get('models', []) if 'generateContent' in m.get('supportedGenerationMethods', [])]
print(f'Kalit ishlayapti. generateContent qo\'llaydigan modellar: {len(models)}')
for m in models:
    if 'gemini' in m['name']:
        print(' ', m['name'].removeprefix('models/'), '|', m.get('inputTokenLimit'))
