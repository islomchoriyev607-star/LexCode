"""Demo ishga tushiruvchi: Cloudflare tunnel (HTTPS) → manzilni botga beradi → botni ishga tushiradi.

usage (LexCode papkasidan):  .venv\\Scripts\\python tools\\run_demo.py
To'xtatish: Ctrl+C (tunnel ham, bot ham yopiladi). Loglar: logs/tunnel.log, logs/bot.log
"""
import os, re, shutil, subprocess, sys, threading, time, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOGS = ROOT / 'logs'; LOGS.mkdir(exist_ok=True)
PORT = os.getenv('WEB_PORT', '8080')
URL_RE = re.compile(r'https://[a-z0-9-]+\.trycloudflare\.com')
sys.stdout.reconfigure(encoding='utf-8')


def find_cloudflared() -> str:
    exe = shutil.which('cloudflared')
    for p in [exe, r'C:\Program Files (x86)\cloudflared\cloudflared.exe', r'C:\Program Files\cloudflared\cloudflared.exe']:
        if p and pathlib.Path(p).exists():
            return p
    sys.exit('cloudflared topilmadi. O\'rnating: winget install --id Cloudflare.cloudflared -e')


def main() -> None:
    cf = find_cloudflared()
    tlog = open(LOGS / 'tunnel.log', 'w', encoding='utf-8')
    # --protocol http2: ko'p tarmoqlar QUIC (UDP 7844) ni to'sadi; HTTP2 oddiy 443-port orqali ishlaydi
    tunnel = subprocess.Popen([cf, 'tunnel', '--no-autoupdate', '--protocol', 'http2', '--url', f'http://127.0.0.1:{PORT}'],
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace')
    url, deadline = None, time.time() + 90
    while time.time() < deadline:
        line = tunnel.stdout.readline()
        if not line:
            if tunnel.poll() is not None:
                break
            continue
        tlog.write(line); tlog.flush()
        m = URL_RE.search(line)
        if m:
            url = m.group(0)
            break
    if not url:
        tunnel.terminate()
        sys.exit('Tunnel manzili olinmadi — logs/tunnel.log ni ko\'ring (internet ulanishini tekshiring).')

    # tunnel logini fon oqimida yozib borish (aks holda bufer to'lib, cloudflared to'xtab qoladi)
    connected = threading.Event()

    def pump():
        for l in tunnel.stdout:
            tlog.write(l); tlog.flush()
            if 'Registered tunnel connection' in l:
                connected.set()
    threading.Thread(target=pump, daemon=True).start()
    if not connected.wait(45):
        print('⚠️ Tunnel Cloudflare ga ulanmadi (45 s) — logs/tunnel.log ni ko\'ring.', flush=True)
    print(f'✅ Mini App manzili: {url}', flush=True)
    env = dict(os.environ, WEBAPP_URL=url, PYTHONIOENCODING='utf-8')
    py = ROOT / '.venv' / 'Scripts' / 'python.exe'
    with open(LOGS / 'bot.log', 'w', encoding='utf-8') as blog:
        bot = subprocess.Popen([str(py), '-m', 'bot.main'], cwd=ROOT, env=env, stdout=blog, stderr=subprocess.STDOUT)
        print('✅ Bot ishga tushdi. Telegram: @lex_nav_bot → pastdagi "Ilova" tugmasi. To\'xtatish: Ctrl+C', flush=True)
        try:
            while bot.poll() is None and tunnel.poll() is None:
                time.sleep(1)
            print('⚠️ Bot yoki tunnel to\'xtadi — loglarni ko\'ring.')
        except KeyboardInterrupt:
            print('To\'xtatilmoqda…')
        finally:
            for p in (bot, tunnel):
                if p.poll() is None:
                    p.terminate()
                    try:
                        p.wait(10)
                    except subprocess.TimeoutExpired:
                        p.kill()


if __name__ == '__main__':
    main()
