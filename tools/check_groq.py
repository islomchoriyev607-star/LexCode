"""GROQ_API_KEY ni .env dan o'qib: modellar ro'yxati + o'zbekcha test so'rov (kalit ekranga chiqarilmaydi).
usage: python check_groq.py [MODEL ...]"""
import json, sys, time, urllib.request, urllib.error, pathlib
sys.stdout.reconfigure(encoding='utf-8')
env = pathlib.Path(__file__).resolve().parent.parent / '.env'
key = next(l.split('=', 1)[1].strip() for l in env.read_text(encoding='utf-8').splitlines() if l.startswith('GROQ_API_KEY='))
H = {'Authorization': f'Bearer {key}', 'Content-Type': 'application/json', 'User-Agent': 'lexcode-check/1.0'}
data = json.load(urllib.request.urlopen(urllib.request.Request('https://api.groq.com/openai/v1/models', headers=H), timeout=30))
ids = sorted(m['id'] for m in data['data'] if m.get('active', True))
print(f'Kalit ishlayapti. Modellar ({len(ids)}):', ', '.join(ids))
PROMPT = ("Sen O'zbekiston fuqarolariga yordam beradigan huquqiy yo'l ko'rsatuvchisan. O'zbek tilida (lotin), "
          "3-4 jumlada javob ber. Modda raqamini yozma. Savol: Ish beruvchi 2 oydan beri ish haqimni bermayapti. "
          "Qaysi davlat idorasiga murojaat qilsam bo'ladi?")
for model in sys.argv[1:]:
    body = json.dumps({'model': model, 'messages': [{'role': 'user', 'content': PROMPT}], 'max_tokens': 400}).encode()
    t = time.time()
    try:
        r = json.load(urllib.request.urlopen(urllib.request.Request('https://api.groq.com/openai/v1/chat/completions', data=body, headers=H), timeout=60))
        u = r.get('usage', {})
        print(f'\n===== {model} | {time.time()-t:.1f} s | kirish {u.get("prompt_tokens")} / chiqish {u.get("completion_tokens")} token')
        print(r['choices'][0]['message']['content'].strip())
    except urllib.error.HTTPError as e:
        print(f'\n===== {model} | XATO {e.code}: {e.read().decode()[:300]}')
