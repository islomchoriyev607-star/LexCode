"""Gemini ga o'zbekcha test so'rov yuboradi: javob, vaqt va token sarfini ko'rsatadi.
usage: python test_gemini.py MODEL [MODEL ...]"""
import json, sys, time, urllib.request, urllib.error, pathlib
sys.stdout.reconfigure(encoding='utf-8')
env = pathlib.Path(__file__).resolve().parent.parent / '.env'
key = next(l.split('=', 1)[1].strip() for l in env.read_text(encoding='utf-8').splitlines() if l.startswith('GEMINI_API_KEY='))
PROMPT = ("Sen O'zbekiston fuqarolariga yordam beradigan huquqiy yo'l ko'rsatuvchisan. O'zbek tilida (lotin), "
          "3-4 jumlada javob ber. Modda raqamini yozma. Savol: Ish beruvchi 2 oydan beri ish haqimni bermayapti. "
          "Qaysi davlat idorasiga murojaat qilsam bo'ladi?")
for model in sys.argv[1:]:
    body = json.dumps({'contents': [{'parts': [{'text': PROMPT}]}]}).encode()
    req = urllib.request.Request(f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',
                                 data=body, headers={'x-goog-api-key': key, 'Content-Type': 'application/json'})
    t = time.time()
    try:
        r = json.load(urllib.request.urlopen(req, timeout=90))
        txt = r['candidates'][0]['content']['parts'][0]['text'].strip()
        u = r.get('usageMetadata', {})
        print(f'===== {model} | {time.time()-t:.1f} s | kirish {u.get("promptTokenCount")} / chiqish {u.get("candidatesTokenCount")} token')
        print(txt, '\n')
    except urllib.error.HTTPError as e:
        print(f'===== {model} | XATO {e.code}: {e.read().decode()[:300]}\n')
