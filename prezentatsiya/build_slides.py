"""Huquqiy Navigator — Pitch Day prezentatsiyasi (namuna shablon tuzilmasi, LexCode ranglari, yangi lotin).
Ishga tushirish: python prezentatsiya/build_slides.py   (kerak: python-pptx, pillow). PDF — PowerPoint'da "Save as PDF"."""
import sys
from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from bot.script import convert  # noqa: E402  (amaldagi lotin → yangi lotin, OʻRQ–1184)

W = Path(__file__).parent
OUT = W / 'Huquqiy_Navigator_LexCode.pptx'

# ---- Ranglar: namuna qorongʻi fon + LexCode koʻk/kumush ----
BG, BG2 = '0D1117', '0A0E1A'
CARD, CARD2, EDGE, LINE = '111827', '0F1520', '1F2937', '1F2937'
BLUE, BLUE_D, SKY, SILVER = '1E6BFF', '0F2A5C', '6FB1FF', 'C9D1DC'
WHITE, MUTED, BODY = 'FFFFFF', '9CA3AF', 'D1D5DB'
GREEN, AMBER, VIOLET = '22C55E', 'F59E0B', 'A855F7'
TINT = '0C1730'          # koʻk tusli karta (namunadagi qizgʻish kartalar oʻrniga)


def rgb(h):
    return RGBColor.from_string(h)


def L(s):
    return convert(s, 'latn')


prs = Presentation()
prs.slide_width, prs.slide_height = Inches(10), Inches(5.625)
BLANK = prs.slide_layouts[6]


def bg(slide, color):
    f = slide.background.fill
    f.solid()
    f.fore_color.rgb = rgb(color)


def rect(slide, x, y, w, h, fill, line=None, shape=MSO_SHAPE.RECTANGLE):
    s = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid()
    s.fill.fore_color.rgb = rgb(fill)
    if line:
        s.line.color.rgb = rgb(line)
        s.line.width = Pt(0.75)
    else:
        s.line.fill.background()
    s.shadow.inherit = False
    return s


def text(slide, x, y, w, h, runs, size=12, color=WHITE, font='Calibri', bold=False, italic=False,
         align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, spacing=None, conv=True):
    """runs: str | list[str (paragraf)] | list[list[(matn, {opts})]]"""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.04)
    tf.margin_top = tf.margin_bottom = Inches(0.02)
    tf.vertical_anchor = anchor
    paras = runs if isinstance(runs, list) else [runs]
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        if spacing:
            p.space_after = Pt(spacing)
        parts = para if isinstance(para, list) else [(para, {})]
        for t, o in parts:
            r = p.add_run()
            r.text = L(t) if conv else t
            f = r.font
            f.name = o.get('font', font)
            f.size = Pt(o.get('size', size))
            f.bold = o.get('bold', bold)
            f.italic = o.get('italic', italic)
            f.color.rgb = rgb(o.get('color', color))
    return tb


def check(slide, x, y, w, h, ok):
    """Jadval belgisi: yashil ✓ yoki binafsha chiziq (namunadagidek)."""
    cx, cy = x + w / 2, y + h / 2
    if ok:
        b = rect(slide, cx - 0.14, cy - 0.14, 0.28, 0.28, GREEN, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
        b.adjustments[0] = 0.18
        text(slide, cx - 0.14, cy - 0.15, 0.28, 0.28, '✓', size=14, bold=True, font='Segoe UI Symbol',
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, conv=False)
    else:
        d = rect(slide, cx - 0.14, cy - 0.035, 0.28, 0.07, '8B5CF6', shape=MSO_SHAPE.ROUNDED_RECTANGLE)
        d.adjustments[0] = 0.5


def header(slide, num, title, sub):
    bg(slide, BG2)
    rect(slide, 0, 5.33, 10, 0.30, BLUE_D)                     # pastki tasma (namunadagidek)
    text(slide, 0.5, 5.36, 9, 0.24, '#LexHackathon   #Hackathon   #Tashkent   #event   2026', size=9,
         color=SKY, font='Consolas', align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, conv=False)
    text(slide, 9.1, 0.15, 0.8, 0.4, f'{num:02d}', size=14, color=BLUE, font='Consolas', bold=True, align=PP_ALIGN.RIGHT)
    text(slide, 0.5, 0.15, 8.5, 0.55, title, size=26, bold=True)
    rect(slide, 0.5, 0.75, 0.06, 0.40, BLUE)
    text(slide, 0.65, 0.76, 8.8, 0.38, sub, size=12, color=MUTED, italic=True, anchor=MSO_ANCHOR.MIDDLE)


def tip(slide, s, y=5.0):
    text(slide, 0.5, y, 9.0, 0.3, s, size=9.5, color=MUTED, italic=True)


# ---- Logotiplar: Adliya gerbining oq foni olib tashlanadi (qorongʻi slaydga) ----
def transparent_white(src, dst, thr=238):
    im = Image.open(src).convert('RGBA')
    px = [(r, g, b, 0 if (r > thr and g > thr and b > thr) else a) for r, g, b, a in im.getdata()]
    im.putdata(px)
    im.save(dst)
    return dst


NAV_LOGO = ROOT / 'brand' / 'navigator_logo.png'
TEAM_LOGO = ROOT / 'brand' / 'lexcode_logo.png'
HACK_LOGO = ROOT / 'brand' / 'lexhackathon_logo.png'
ADL_LOGO = ROOT / 'brand' / 'adliya_logo.png'  # oq foni transparent_white() bilan olib tashlangan

# =========================== 1. Sarlavha ===========================
s = prs.slides.add_slide(BLANK)
bg(s, BG)
rect(s, 0, 0, 10, 0.07, BLUE)
rect(s, 0, 5.555, 10, 0.07, BLUE)
text(s, 0.5, 0.22, 4, 0.4, 'Pitch Day · LexHackathon 2026', size=11, color=BLUE, font='Consolas', bold=True, conv=False)
text(s, 0.5, 0.57, 6, 0.3, '“Huquqiy xizmatlar” treki · Muammo №1', size=10, color=MUTED)
s.shapes.add_picture(str(HACK_LOGO), Inches(8.05), Inches(0.18), Inches(0.75), Inches(0.75))
s.shapes.add_picture(str(ADL_LOGO), Inches(8.85), Inches(0.18), Inches(0.75), Inches(0.75))
rect(s, 0.5, 1.05, 9.0, 3.6, CARD, EDGE)
rect(s, 0.5, 1.05, 9.0, 0.06, BLUE)
s.shapes.add_picture(str(NAV_LOGO), Inches(1.0), Inches(1.4), Inches(2.0), Inches(2.0))
text(s, 3.3, 1.5, 6.0, 0.75, 'Huquqiy Navigator', size=38, bold=True)
rect(s, 3.3, 2.38, 5.8, 0.06, BLUE)
text(s, 3.3, 2.52, 5.8, 0.8, 'Huquqingiz buzilganda — qayerga, qachon va qanday murojaat qilishni qadamma-qadam '
     'koʻrsatuvchi AI navigator', size=13, color=SILVER, italic=True)
text(s, 3.3, 3.42, 5.8, 0.35, [[('Telegram: ', {'color': MUTED}), ('@lex_nav_bot', {'color': SKY, 'bold': True}),
                                ('  ·  bot + Mini App', {'color': MUTED})]], size=12, conv=True)
for i, (big, small) in enumerate([('2 942', 'modda (lex.uz)'), ('156', 'idora manzili · Toshkent'),
                                  ('112·102·103', 'xavfda — AI dan oldin')]):
    cx = 3.3 + i * 1.97
    rect(s, cx, 3.92, 1.85, 0.62, TINT, EDGE)
    text(s, cx, 3.95, 1.85, 0.32, big, size=15, bold=True, color=SKY, align=PP_ALIGN.CENTER, conv=False)
    text(s, cx, 4.25, 1.85, 0.26, small, size=9, color=MUTED, align=PP_ALIGN.CENTER)
s.shapes.add_picture(str(TEAM_LOGO), Inches(1.15), Inches(3.55), Inches(0.95), Inches(0.95))
text(s, 2.15, 3.85, 1.2, 0.35, 'LexCode jamoasi', size=10, color=MUTED)
text(s, 0.55, 5.12, 0.9, 0.35, '>>', size=20, color=BLUE, font='Consolas', bold=True, conv=False)
text(s, 0, 5.18, 10, 0.3, '#LexHackathon   #Hackathon   #Tashkent   #event   2026', size=9, color=MUTED,
     font='Consolas', align=PP_ALIGN.CENTER, conv=False)

# =========================== 2. Biz kimmiz ===========================
s = prs.slides.add_slide(BLANK)
header(s, 2, 'Biz kimmiz?', 'LexCode — huquqni har bir fuqaroga tushunarli qiladigan yuristlar va dasturchilar jamoasi')
rect(s, 0.5, 1.35, 3.2, 3.5, TINT, EDGE)
rect(s, 0.5, 1.35, 3.2, 0.06, BLUE)
s.shapes.add_picture(str(TEAM_LOGO), Inches(0.85), Inches(1.55), Inches(2.5), Inches(2.5))
text(s, 0.6, 4.1, 3.0, 0.6, 'Huquq + AI', size=20, bold=True, align=PP_ALIGN.CENTER)
rect(s, 3.9, 1.35, 5.8, 3.5, CARD, EDGE)
rect(s, 3.9, 1.35, 0.06, 3.5, BLUE)
text(s, 4.1, 1.52, 5.4, 0.5, 'Choʻntakdagi huquqiy yoʻlboshchi', size=16, bold=True)
rect(s, 4.1, 2.08, 5.4, 0.04, EDGE)
bul = [
    ('Gapiring, yozing yoki skrinshot yuboring — ', 'AI vaziyatni lex.uz dagi amaldagi qonun bilan solishtiradi'),
    ('Yoʻl koʻrsatadi — ', 'eng yaqin idora manzili, avtobus/metro marshruti, muddat va tayyor ariza (PDF)'),
    ('Ishonchli — ', 'har modda lex.uz havolasi bilan; jiddiy holatda Yuridik klinika yuristi tasdiqlaydi'),
]
text(s, 4.1, 2.25, 5.45, 2.4, [[('▸  ', {'color': BLUE, 'bold': True}), (a, {'bold': True, 'color': WHITE}),
                                 (b, {'color': BODY})] for a, b in bul], size=13, spacing=10)
tip(s, 'Bot hukm chiqarmaydi va sud natijasini bashorat qilmaydi — qonunda belgilangan yoʻlni koʻrsatadi.', y=4.98)

# =========================== 3. Muammo ===========================
s = prs.slides.add_slide(BLANK)
header(s, 3, 'Biz hal qilayotgan muammo', 'Fuqarolar davlat idoralariga qayerga va qanday murojaat qilishni bilmaydi')
rect(s, 0.5, 1.32, 3.5, 3.5, TINT, EDGE)
rect(s, 0.5, 1.32, 3.5, 0.06, BLUE)
text(s, 0.65, 1.62, 3.2, 0.9, '557 254', size=40, bold=True, color=WHITE, align=PP_ALIGN.CENTER, conv=False)
text(s, 0.65, 2.45, 3.2, 0.6, 'murojaat — Prezident Xalq qabulxonalariga, 2026-yil 8 oyida', size=12, color=SILVER,
     align=PP_ALIGN.CENTER)
rect(s, 0.9, 3.25, 2.7, 0.04, EDGE)
text(s, 0.65, 3.4, 3.2, 1.2, 'Nega bizga ehtiyoj bor?', size=19, bold=True, align=PP_ALIGN.CENTER,
     anchor=MSO_ANCHOR.MIDDLE)
probs = [
    ('Odamlar qayerga murojaat qilishni bilmaydi',
     'Murojaatlarning 14–16% i takroriy, ~20% i oddiy huquqiy tushuntirish bilan yopiladi. '
     'Inson huquqlari markaziga kelganlarning 83% i boshqa idoraga yoʻnaltirilgan.'),
    ('Ariza notoʻgʻri rasmiylashtiriladi',
     'Imtiyozli transport kartasi arizalarining 64,7% i, litsenziya arizalarining 12,7% i rad etilgan — '
     'asosiy sabab: hujjat va talablarni tushunmaslik.'),
]
for i, (t1, t2) in enumerate(probs):
    y = 1.32 + i * 1.78
    rect(s, 4.2, y, 5.5, 1.58, CARD, EDGE)
    rect(s, 4.2, y, 0.06, 1.58, BLUE)
    rect(s, 4.35, y + 0.18, 0.4, 0.4, BLUE)
    text(s, 4.35, y + 0.18, 0.4, 0.4, str(i + 1), size=13, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    text(s, 4.85, y + 0.17, 4.75, 0.42, t1, size=14, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    text(s, 4.35, y + 0.66, 5.25, 0.85, t2, size=11.5, color=BODY)
tip(s, 'Manbalar: Prezident Xalq qabulxonalari (2026), Transport vazirligi (gov.uz), Inson huquqlari milliy markazi.', y=4.98)

# =========================== 4. Bozor ===========================
s = prs.slides.add_slide(BLANK)
header(s, 4, 'Bozor hajmi va maqsadli auditoriya', 'Rasmiy statistika asosida: TAM / SAM / SOM')
rect(s, 0.5, 1.32, 3.2, 3.5, TINT, EDGE)
rect(s, 0.5, 1.32, 3.2, 0.06, BLUE)
rect(s, 0.75, 1.75, 2.7, 1.4, BLUE)
text(s, 0.75, 1.75, 2.7, 1.4, [[('Bozor', {})], [('hajmi', {})]], size=22, bold=True, align=PP_ALIGN.CENTER,
     anchor=MSO_ANCHOR.MIDDLE)
aud = [('Ishchilar', '25–55 yosh · 21,3 mln'), ('Talabalar', '18–25 yosh · 1,5–1,85 mln'),
       ('Kichik biznes, YaTT', '1,26 mln subyekt')]
text(s, 0.7, 3.3, 2.85, 1.45, [[(a + ': ', {'bold': True, 'color': WHITE}), (b, {'color': SILVER})] for a, b in aud],
     size=11, spacing=5)
rows = [
    ('TAM', BLUE, '24,4 mln kishi', 'Internetdan foydalanadigan voyaga yetgan aholi (25,9 mln × 94,2%)', 5.5),
    ('SAM', AMBER, '15 mln kishi', 'my.gov.uz da roʻyxatdan oʻtgan — onlayn murojaatga tayyor auditoriya', 4.5),
    ('SOM', GREEN, '150–450 ming', '1-yilda SAM ning 1%, 3-yilda 3% i — boshlangʻich startap uchun real ulush', 3.5),
]
for i, (k, c, v, d, bw) in enumerate(rows):
    y = 1.42 + i * 1.1
    rect(s, 3.9, y, 5.8, 0.9, CARD, EDGE)
    rect(s, 3.9, y, bw, 0.04, c)
    text(s, 4.05, y + 0.1, 0.8, 0.38, k, size=16, bold=True, color=c, font='Consolas', conv=False)
    text(s, 4.85, y + 0.1, 4.7, 0.38, v, size=16, bold=True)
    text(s, 4.05, y + 0.52, 5.55, 0.3, d, size=10, color=MUTED)
tip(s, 'Manbalar: stat.uz (aholi, 01.10.2026), my.gov.uz (2026-yil aprel), DataReportal Digital 2026, stat.edu.uz.', y=4.98)

# =========================== 5. Yechim + raqobatchilar ===========================
s = prs.slides.add_slide(BLANK)
header(s, 5, 'Yechim va raqobatchilar', 'Advokat sifati + AI tezligi — bepul, 24/7, oʻzbek tilida')
cols = [(0.5, 2.9, 'Xususiyat', EDGE), (3.4, 2.1, 'Huquqiy Navigator', BLUE),
        (5.5, 2.1, 'Umumiy AI chatbotlar', '2D3A50'), (7.6, 2.1, 'Advokat / yurist', '2D3A50')]
for x, w, t, c in cols:
    rect(s, x, 1.30, w, 0.5, c, EDGE)
    text(s, x, 1.30, w, 0.5, t, size=12.5, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
feat = [
    ('Amaldagi Oʻzbekiston qonuni, lex.uz havolasi bilan', (1, 0, 1)),
    ('Qadamma-qadam yoʻl va muddat boʻyicha kuzatuv', (1, 0, 1)),
    ('Idoraga mos tayyor ariza (PDF)', (1, 0, 1)),
    ('Eng yaqin idora va avtobus/metro marshruti', (1, 0, 0)),
    ('Bepul, 24/7, ovoz va oʻzbek tilida', (1, 1, 0)),
]
RH = 0.5  # qator qadami (5 qator sigʻishi uchun)
for i, (name, marks) in enumerate(feat):
    y = 1.80 + i * RH
    f = CARD if i % 2 == 0 else CARD2
    rect(s, 0.5, y, 2.9, RH - 0.03, f, EDGE)
    text(s, 0.6, y, 2.75, RH - 0.03, name, size=10.5, color=BODY, anchor=MSO_ANCHOR.MIDDLE)
    for (x, w, _, _), ok in zip(cols[1:], marks):
        rect(s, x, y, w, RH - 0.03, f, EDGE)
        check(s, x, y, w, RH - 0.03, ok)
rect(s, 0.5, 4.36, 9.2, 0.6, TINT, EDGE)
rect(s, 0.5, 4.36, 9.2, 0.05, BLUE)
text(s, 0.5, 4.38, 9.2, 0.58, [[('Nega biz? ', {'bold': True, 'color': WHITE}),
                               ('AI qonunni oʻylab topmaydi — har modda bazadan tekshiriladi; advokatdan farqli — '
                                'daqiqalar ichida va bepul.', {'color': SILVER})]], size=13, align=PP_ALIGN.CENTER,
     anchor=MSO_ANCHOR.MIDDLE)

# =========================== 6. Monetizatsiya ===========================
s = prs.slides.add_slide(BLANK)
header(s, 6, 'Monetizatsiya modeli', 'Fuqaro uchun asosiy yoʻl koʻrsatish bepul; daromad — premium, B2B va hamkorlardan')
rect(s, 0.5, 1.32, 3.5, 3.5, '0A1A12', EDGE)
rect(s, 0.5, 1.32, 3.5, 0.06, GREEN)
rect(s, 0.75, 2.0, 3.0, 0.05, GREEN)
text(s, 0.75, 2.15, 3.0, 1.0, [[('Freemium', {})], [('+ B2B / B2G', {})]], size=22, bold=True, align=PP_ALIGN.CENTER)
text(s, 0.75, 3.3, 3.0, 1.3, 'Xavf holatida va asosiy yoʻl koʻrsatishda hech qachon pul soʻralmaydi', size=11,
     color=SILVER, italic=True, align=PP_ALIGN.CENTER)
mon = [
    ('Kim toʻlaydi?', 'Fuqaro (premium) · tashkilotlar: universitet, korxona HR (B2B) · hokimlik, '
                      'qabulxonalar (B2G) · chop etish hamkorlari'),
    ('Qancha toʻlaydi?', 'Premium 29 000 soʻm/oy yoki 1 ariza 15 000 soʻm · B2B litsenziya 1,5–3 mln soʻm/oy · '
                         'hamkordan 10% komissiya'),
    ('Nima uchun?', 'Advokat maslahati ~200–500 ming soʻm; bizda — daqiqalarda. Tashkilotda takroriy va '
                    'notoʻgʻri murojaatlar kamayadi'),
]
for i, (t1, t2) in enumerate(mon):
    y = 1.32 + i * 1.15
    rect(s, 4.2, y, 5.5, 1.02, CARD, EDGE)
    rect(s, 4.2, y, 0.06, 1.02, GREEN)
    text(s, 4.35, y + 0.08, 5.2, 0.32, t1, size=13, bold=True, color=GREEN)
    text(s, 4.35, y + 0.42, 5.25, 0.58, t2, size=11, color=BODY)
tip(s, 'Unit economics: 1 tahlilning AI xarajati ≈ 25–65 soʻm; 1 premium foydalanuvchi — 29 000 soʻm/oy. '
       'Narxlar taxminiy (2026-yil noyabr).', y=4.98)

# =========================== 7. Milestones ===========================
s = prs.slides.add_slide(BLANK)
header(s, 7, 'Maqsadlar va KPI', 'Realistik reja: 1–3 yil, SAM ning 1% → 3% i')
rect(s, 0.8, 2.9, 8.4, 0.04, EDGE)
text(s, 9.1, 2.74, 0.3, 0.32, '▶', size=14, color=MUTED, font='Segoe UI Symbol', conv=False)
mil = [  # x, yuqorida?, rang, sarlavha, satrlar
    (0.55, True, BLUE, 'Hozir', ['MVP: bot + Mini App · 4 til', '2 942 modda · 156 idora']),
    (2.75, False, AMBER, '6 oy', ['10 000 foydalanuvchi', '2 universitet bilan pilot']),
    (4.95, True, SKY, '1 yil', ['150 000 foydalanuvchi', '≈ 0,6 mlrd soʻm daromad']),
    (7.15, False, GREEN, '3 yil', ['450 000 foydalanuvchi', '≈ 4 mlrd soʻm · B2G integratsiya']),
]
for x, up, c, t1, lines in mil:
    cx = x + 0.95
    rect(s, cx - 0.15, 2.77, 0.3, 0.3, c, shape=MSO_SHAPE.OVAL)
    if up:
        rect(s, cx - 0.02, 2.12, 0.04, 0.65, c)
        y = 1.22
    else:
        rect(s, cx - 0.02, 3.07, 0.04, 0.65, c)
        y = 3.72
    rect(s, x, y, 1.9, 0.9, CARD, EDGE)
    rect(s, x, y, 1.9, 0.04, c)
    text(s, x, y + 0.06, 1.9, 0.28, t1, size=12, bold=True, color=c, font='Consolas', align=PP_ALIGN.CENTER)
    text(s, x + 0.05, y + 0.36, 1.8, 0.52, lines, size=10, color=BODY, align=PP_ALIGN.CENTER)
tip(s, 'Keyingi qadamlar: 50+ qonun, viloyatlar idoralari, chop etish hamkorlari bilan shartnoma, kuchli AI model.',
    y=4.98)

# =========================== 8. Jamoa ===========================
s = prs.slides.add_slide(BLANK)
header(s, 8, 'Jamoa', 'Huquq + texnologiya + biznes · 2 dasturchi · 3 oydan beri birgamiz')
team = [
    ('IC', BLUE, 'Islom Choriyev', 'Toʻlqin oʻgʻli', 'CEO / Loyiha rahbari',
     'OʻzMU, yurisprudensiya 2-kurs · Yuridik klinika', ['1 yil — huquqiy maslahat', '6 oy — AI dasturlash']),
    ('MX', VIOLET, 'Mirsoat Xolmurodov', 'Gʻulom oʻgʻli', 'CTO va Dizayner',
     'Mahsulot dizayni va texnik yechim', ['2 yil — dizayn', '1 yil — vibe coding']),
    ('ShT', GREEN, 'Shaʼbona Toʻychiyeva', 'Shukurjon qizi', 'Biznes analitik',
     'Yurist · bozor tahlili, biznes-model', ['1 yil — biznes']),
]
cw, gap = 2.8, 0.4
x0 = (10 - (3 * cw + 2 * gap)) / 2
for i, (ini, c, name, father, role, about, exp) in enumerate(team):
    x = x0 + i * (cw + gap)
    rect(s, x, 1.32, cw, 3.55, CARD, EDGE)
    rect(s, x, 1.32, cw, 0.05, c)
    o = rect(s, x + cw / 2 - 0.45, 1.5, 0.9, 0.9, EDGE, c, shape=MSO_SHAPE.OVAL)
    o.line.width = Pt(2)
    text(s, x + cw / 2 - 0.45, 1.5, 0.9, 0.9, ini, size=18, bold=True, color=c, align=PP_ALIGN.CENTER,
         anchor=MSO_ANCHOR.MIDDLE)
    text(s, x + 0.1, 2.5, cw - 0.2, 0.32, name, size=14, bold=True, align=PP_ALIGN.CENTER)
    text(s, x + 0.1, 2.8, cw - 0.2, 0.26, father, size=10, color=MUTED, align=PP_ALIGN.CENTER)
    text(s, x + 0.1, 3.08, cw - 0.2, 0.3, role, size=12, bold=True, color=c, align=PP_ALIGN.CENTER)
    rect(s, x + 0.5, 3.45, cw - 1.0, 0.02, EDGE)
    text(s, x + 0.15, 3.55, cw - 0.3, 0.55, about, size=10, color=SILVER, italic=True, align=PP_ALIGN.CENTER)
    text(s, x + 0.15, 4.12, cw - 0.3, 0.65, exp, size=10.5, color=BODY, align=PP_ALIGN.CENTER)

prs.save(OUT)
print('saqlandi:', OUT)
