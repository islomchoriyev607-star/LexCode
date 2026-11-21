"""BOT_TOKEN ni .env dan o'qib, Telegram getMe orqali tekshiradi (token ekranga chiqarilmaydi)."""
import json, sys, urllib.request, pathlib
sys.stdout.reconfigure(encoding='utf-8')
env = pathlib.Path(__file__).resolve().parent.parent / '.env'
token = next(l.split('=', 1)[1].strip() for l in env.read_text(encoding='utf-8').splitlines() if l.startswith('BOT_TOKEN='))
r = json.load(urllib.request.urlopen(f'https://api.telegram.org/bot{token}/getMe', timeout=20))
b = r['result']
print('ok:', r['ok'], '| username: @' + b['username'], '| name:', b['first_name'],
      '| guruhga qo\'shish mumkin:', b.get('can_join_groups'), '| guruh xabarlarini o\'qiydi:', b.get('can_read_all_group_messages'))
