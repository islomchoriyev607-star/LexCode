"""Markdown → chop etishga tayyor HTML (prezentatsiya ranglarida). PDF — Chrome headless --print-to-pdf.
Ishga tushirish: python prezentatsiya/md2pdf.py prezentatsiya/nutq_va_savol_javob.md  (kerak: markdown)"""
import re
import sys
from pathlib import Path

import markdown

src = Path(sys.argv[1])
# Ro'yxat paragrafdan keyin bo'sh qatorsiz kelsa ham ro'yxat bo'lib chiqsin (Markdown bo'sh qator talab qiladi)
LIST = re.compile(r'^\s*(?:[-*]|\d+\.)\s')
lines, prev = [], ''
for ln in src.read_text(encoding='utf-8').splitlines():
    if LIST.match(ln) and prev.strip() and not LIST.match(prev) and not prev.startswith((' ', '\t')):
        lines.append('')
    lines.append(ln)
    prev = ln
html_body = markdown.markdown('\n'.join(lines), extensions=['extra', 'sane_lists'])
logo = (Path(__file__).resolve().parents[1] / 'brand' / 'navigator_logo.png').as_uri()

CSS = """
@page { size: A4; margin: 18mm 18mm 18mm 20mm; }
body { font-family: Calibri, 'Segoe UI', Arial, sans-serif; font-size: 11.5pt; line-height: 1.5; color: #1a1f2b; }
.top { display: flex; align-items: center; gap: 14px; border-bottom: 3px solid #1E6BFF; padding-bottom: 10px; margin-bottom: 6px; }
.top img { width: 58px; height: 58px; border-radius: 10px; }
.top .t { font-size: 9.5pt; color: #5b6575; }
h1 { font-size: 19pt; margin: 0; color: #0b1a3a; }
h2 { font-size: 14.5pt; color: #fff; background: #0F2A5C; padding: 6px 12px; border-radius: 6px; margin: 22px 0 10px; }
h3 { font-size: 12.5pt; color: #1E6BFF; margin: 18px 0 6px; border-bottom: 1px solid #dfe5ef; padding-bottom: 3px; }
p { margin: 6px 0; }
strong { color: #0b1a3a; }
ul, ol { margin: 4px 0 8px; padding-left: 22px; }
li { margin: 2px 0; }
hr { border: 0; border-top: 1px solid #dfe5ef; margin: 16px 0; }
code { font-family: Consolas, monospace; font-size: 10pt; background: #eef2f8; padding: 1px 4px; border-radius: 3px; }
blockquote { margin: 14px 0; padding: 8px 14px; background: #fff7e6; border-left: 4px solid #F59E0B; border-radius: 4px; }
h3 + p, h3 + ul { break-before: avoid; }
h2, h3 { break-after: avoid; }
li, p { break-inside: avoid; }
"""

title = src.stem.replace('_', ' ')
html = f"""<!doctype html><html lang="uz"><head><meta charset="utf-8"><title>{title}</title><style>{CSS}</style></head>
<body><div class="top"><img src="{logo}" alt=""><div><div class="t">LexCode jamoasi · LexHackathon 2026 · @lex_nav_bot</div></div></div>
{html_body}</body></html>"""
out = src.with_suffix('.html')
out.write_text(html, encoding='utf-8')
print(out)
