"""Builds Dime_Leak_Scanner_Guide.pdf (1-page A4 guide). Run: python3 build_pdf.py"""
import math, os
from PIL import Image, ImageDraw
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader

STUDIO = "/home/claude/dime-money-quest/studio"
src = open(f"{STUDIO}/render_guy.py").read().split("\ndef frame(t):")[0]
exec(src)                                    # Dime helpers: head(), guy(), colours

pdfmetrics.registerFont(TTFont("Pixel", f"{STUDIO}/PressStart2P.ttf"))
OUT = "Dime_Leak_Scanner_Guide.pdf"
W_, H_ = A4
def rgb(c): return tuple(v / 255 for v in c)
INKc, GOLDc, CREAM = rgb(INK), rgb(GOLD), rgb((255, 248, 225))
PURP = rgb((60, 50, 100))

def sprite_head(mood="happy", scale=8):
    im = Image.new("RGBA", (26, 26), (0, 0, 0, 0)); head(ImageDraw.Draw(im), 13, 13, mood, 0.5)
    return im.resize((26 * scale, 26 * scale), Image.NEAREST)

def sprite_drop(scale=8):
    im = Image.new("RGBA", (24, 30), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    cx, r, top, bt = 12, 9, 2, 10
    d.polygon([(cx, top - 1), (cx - r - 1, bt + r), (cx + r + 1, bt + r)], fill=INK)
    d.ellipse([cx - r - 1, bt - 1, cx + r + 1, bt + 2 * r + 1], fill=INK)
    d.polygon([(cx, top), (cx - r, bt + r), (cx + r, bt + r)], fill=(90, 190, 255))
    d.ellipse([cx - r, bt, cx + r, bt + 2 * r], fill=(90, 190, 255))
    for s in (-1, 1):
        ex = cx + s * 4
        d.rectangle([ex - 1, bt + 6, ex + 1, bt + 9], fill=WHITE); d.point((ex, bt + 8), fill=INK)
        d.line([ex - 3 * s, bt + 3, ex + s, bt + 5], fill=INK)
    d.rectangle([cx - 4, bt + 13, cx + 4, bt + 15], fill=INK)
    return im.resize((24 * scale, 30 * scale), Image.NEAREST)

c = canvas.Canvas(OUT, pagesize=A4)
c.setTitle("Dime's Leak Scanner - Guide"); c.setAuthor("@dimesmoneyquest")
c.setFillColorRGB(*CREAM); c.rect(0, 0, W_, H_, fill=1, stroke=0)

# header band
c.setFillColorRGB(*INKc); c.rect(0, H_ - 150, W_, 150, fill=1, stroke=0)
c.drawImage(ImageReader(sprite_head("happy", 8)), 36, H_ - 135, 104, 104, mask="auto")
c.drawImage(ImageReader(sprite_drop(6)), W_ - 92, H_ - 128, 58, 72, mask="auto")
c.setFillColorRGB(*GOLDc); c.setFont("Pixel", 22); c.drawString(156, H_ - 68, "LEAK SCANNER")
c.setFillColorRGB(1, 1, 1); c.setFont("Pixel", 9); c.drawString(158, H_ - 92, "DIME'S MONEY QUEST")
c.setFont("Helvetica", 11.5); c.drawString(158, H_ - 116, "Find where your money drips away. 7 days. Free.")

def section(y, title):
    c.setFillColorRGB(*PURP); c.setFont("Pixel", 11); c.drawString(40, y, title)
    c.setStrokeColorRGB(*GOLDc); c.setLineWidth(2); c.line(40, y - 7, W_ - 40, y - 7)
    return y - 26

def para(y, text, size=10.5, x=40, width=W_ - 80, lead=14.5, font="Helvetica", col=(0, 0, 0)):
    c.setFillColorRGB(*col); c.setFont(font, size)
    words, line = text.split(), ""
    for w in words:
        if c.stringWidth(line + " " + w, font, size) > width and line:
            c.drawString(x, y, line); y -= lead; line = w
        else: line = (line + " " + w).strip()
    c.drawString(x, y, line); return y - lead

y = section(H_ - 182, "WHY LEAKS?")
y = para(y, "Most money isn't lost in one big buy. It drips. A coffee here, a delivery fee there, an app you forgot. "
            "Each one feels too small to matter. Together they are why the money is gone by day 20.")
c.setFillColorRGB(*rgb(RED)); c.setFont("Helvetica-Bold", 12)
c.drawString(40, y - 2, "€8 here, €8 there = €240 a month = €2,880 a year.")
c.setFillColorRGB(0.45, 0.45, 0.5); c.setFont("Helvetica-Oblique", 9); c.drawString(355, y - 2, "(example numbers)")
y -= 30

y = section(y, "HOW TO SCAN")
steps = [("1", "Days 1-7: log every spend in the spreadsheet tab '7-Day Log'. Even €1. Card, cash and apps."),
         ("2", "For each spend pick a leak type and answer one question honestly: did I need this? Yes or No."),
         ("3", "Day 7: open 'Scan Results'. You see every leak per month and per year, and your biggest one."),
         ("4", "Bonus: list your subscriptions in 'Subscription Scan'. Not used in 30+ days = cancel candidate.")]
for n, txt in steps:
    c.setFillColorRGB(*INKc); c.rect(40, y - 5, 18, 18, fill=1, stroke=0)
    c.setFillColorRGB(*GOLDc); c.setFont("Pixel", 9); c.drawString(45, y, n)
    y = para(y + 1, txt, x=68, width=W_ - 108) - 4
y -= 10

y = section(y, "THE 8 LEAKS TO WATCH")
leaks = [("Snacks & coffee", "drinks to go, bakery stops, vending machines"),
         ("Takeout & delivery", "delivery fees, 'too tired to cook' dinners"),
         ("Rides & transport", "short rides you could have walked"),
         ("Subscriptions & apps", "streaming, in-app buys, trials that turned paid"),
         ("Shopping & impulse", "sale emails, 'just because' carts"),
         ("Going out", "rounds, entry fees, late-night food"),
         ("Fees & interest", "account fees, late fees, overdraft"),
         ("Other", "anything that keeps showing up")]
colw = (W_ - 80) / 2
for i, (name, ex) in enumerate(leaks):
    x = 40 + (i % 2) * colw; yy = y - (i // 2) * 34
    c.setFillColorRGB(*rgb((90, 190, 255))); c.circle(x + 5, yy + 3, 4, fill=1, stroke=0)
    c.setFillColorRGB(*INKc); c.setFont("Helvetica-Bold", 10.5); c.drawString(x + 15, yy, name)
    c.setFillColorRGB(0.3, 0.3, 0.38); c.setFont("Helvetica", 9.5); c.drawString(x + 15, yy - 13, ex)
y -= 4 * 34 + 12

y = section(y, "PLUG PLAN: PICK ONE POWER-UP")
plan = [("Subscriptions", "Cancel anything you haven't opened in 30 days."),
        ("Takeout", "Swap 2 of 4 orders a week for a €5 home meal."),
        ("Impulse buys", "Wait 48 hours before buying. Unsubscribe from 5 shop emails."),
        ("Snacks & coffee", "Bring your own 3 days a week."),
        ("Fees", "Check what your account costs; switch to a free one."),
        ("Rides", "Walk anything under 15 minutes.")]
for i, (leak, tip) in enumerate(plan):
    yy = y - i * 21
    if i % 2 == 0:
        c.setFillColorRGB(1, 0.95, 0.8); c.rect(40, yy - 6, W_ - 80, 21, fill=1, stroke=0)
    c.setFillColorRGB(*PURP); c.setFont("Helvetica-Bold", 10.5); c.drawString(48, yy, leak)
    c.setFillColorRGB(0, 0, 0); c.setFont("Helvetica", 10.5); c.drawString(165, yy, tip)
y -= len(plan) * 21 + 10
y = para(y, "One leak, one power-up, this week. Scan again next month and watch your yearly number change.",
         size=10.5, font="Helvetica-Bold", col=rgb((40, 140, 70)))

# footer
c.setFillColorRGB(*INKc); c.rect(0, 0, W_, 46, fill=1, stroke=0)
c.drawImage(ImageReader(sprite_head("happy", 3)), 36, 6, 34, 34, mask="auto")
c.setFillColorRGB(*GOLDc); c.setFont("Pixel", 9); c.drawString(80, 20, "@DIMESMONEYQUEST")
c.setFillColorRGB(0.8, 0.8, 0.85); c.setFont("Helvetica", 8.5)
c.drawRightString(W_ - 36, 25, "Amounts in this guide are example numbers.")
c.drawRightString(W_ - 36, 13, "A tracking tool, not financial advice.")
c.save()
print("saved", OUT, "content ends at y =", round(y))
