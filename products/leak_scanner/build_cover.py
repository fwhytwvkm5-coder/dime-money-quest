"""Gumroad images for the Leak Scanner: cover 1280x720 and thumbnail 600x600. Run: python3 build_cover.py"""
import math
from PIL import Image, ImageDraw
STUDIO = "/home/claude/dime-money-quest/studio"
exec(open(f"{STUDIO}/render_guy.py").read().split("\ndef frame(t):")[0])

T = 0.4
def mood_at(t): return "happy"
def guy_state(t): return GUY_X, GROUND_Y, None, 0, "up", 1.0
WATER = (90, 190, 255)

def backdrop(w, h, ground):
    top, bot = sky_colors(5)
    im = Image.new("RGB", (w, h), top); d = ImageDraw.Draw(im); d.fontmode = "1"
    for y in range(h):
        d.line([0, y, w, y], fill=mixc(top, bot, y / ground))
    for (sx, sy) in STARS:
        if sy < ground - 60: d.point((sx % w, sy - 30), fill=(255, 255, 220))
    for (hx, hh) in HILLS[:8]:
        x = int(hx * 0.6)
        d.ellipse([x - 50, ground - hh - 30, x + 50, ground + 40], fill=mixc(bot, (40, 90, 80), 0.5))
    for (bx, bw, bh, wins) in BUILD[:30]:
        if bx > w: break
        d.rectangle([bx, ground - bh, bx + bw, ground], fill=(55, 50, 95))
        for (wx, wy) in wins: d.point((bx + wx, ground - bh + wy), fill=(255, 210, 90))
    for tx in range(0, w + 12, 12):
        d.rectangle([tx, ground, tx + 11, ground + 6], fill=GREEN); d.line([tx, ground, tx + 11, ground], fill=(160, 255, 180))
        d.rectangle([tx, ground + 7, tx + 11, h], fill=(120, 74, 44)); d.point((tx + 3, ground + 11), fill=(150, 100, 60))
    return im

def dime(im, cx, ground):
    """Dime 2x, happy, magnifying glass raised"""
    layer = Image.new("RGBA", (LW, LH), (0, 0, 0, 0)); ld = ImageDraw.Draw(layer)
    gx, ghcy = guy(ld, T)
    hxp, hyp = gx + 10, GROUND_Y - 26
    ex, ey = hxp + 6, hyp - 6
    ld.line([hxp, hyp, ex, ey], fill=(120, 80, 50), width=2)
    lx, ly = ex + 4, ey - 4
    ld.ellipse([lx - 6, ly - 6, lx + 6, ly + 6], fill=INK); ld.ellipse([lx - 5, ly - 5, lx + 5, ly + 5], fill=(200, 205, 220))
    ld.ellipse([lx - 3, ly - 3, lx + 3, ly + 3], fill=(170, 225, 250)); ld.point((lx - 2, ly - 2), fill=WHITE)
    spr = layer.crop((GUY_X - 30, GROUND_Y - 62, GUY_X + 30, GROUND_Y + 1)).resize((120, 126), Image.NEAREST)
    im.paste(spr, (cx - 60, ground - 125), spr)

def drop(d, cx, by, k, s=1.0):
    w = int(18 * s); h = int(22 * s); r = w // 2; y0 = by - h; bt = y0 + h - w
    d.polygon([(cx, y0 - 1), (cx - r - 1, bt + r), (cx + r + 1, bt + r)], fill=INK)
    d.ellipse([cx - r - 1, bt - 1, cx + r + 1, by + 1], fill=INK)
    d.polygon([(cx, y0), (cx - r, bt + r), (cx + r, bt + r)], fill=WATER); d.ellipse([cx - r, bt, cx + r, by], fill=WATER)
    ey = bt + r // 2 + 1
    for sg in (-1, 1):
        ex = cx + sg * 4
        d.rectangle([ex - 1, ey, ex + 1, ey + 3], fill=WHITE); d.point((ex, ey + 2), fill=INK)
        d.line([ex - 3 * sg, ey - 3, ex + sg, ey - 1], fill=INK)
    d.rectangle([cx - 3, ey + 6, cx + 3, ey + 7], fill=INK)

def sheet_icon(d, ix, iy):
    d.rectangle([ix - 15, iy - 19, ix + 15, iy + 19], fill=INK)
    d.rectangle([ix - 14, iy - 18, ix + 14, iy + 18], fill=WHITE)
    d.rectangle([ix - 14, iy - 18, ix + 14, iy - 12], fill=GREEN)
    for k in range(4):
        d.rectangle([ix - 10, iy - 7 + k * 6, ix + 4 - (k % 2) * 6, iy - 6 + k * 6], fill=(150, 150, 170))
        d.rectangle([ix + 7, iy - 8 + k * 6, ix + 9, iy - 6 + k * 6], fill=GREEN if k < 3 else RED)

def badge(d, cx, cy, label, col):
    w = int(d.textlength(label, font=FONT_BIG)) + 12
    d.rectangle([cx - w // 2 - 1, cy - 1, cx + w // 2 + 1, cy + 23], fill=INK)
    d.rectangle([cx - w // 2, cy, cx + w // 2, cy + 22], fill=col)
    d.rectangle([cx - w // 2, cy, cx + w // 2, cy + 1], fill=mixc(col, WHITE, 0.5))
    text(d, label, cx, cy + 4, WHITE, font=FONT_BIG, center=True)

# ---- cover 1280x720 (logical 320x180, x4) ----
G = 152
im = backdrop(320, 180, G); d = ImageDraw.Draw(im); d.fontmode = "1"
d.rectangle([0, 0, 320, 64], fill=INK)
text(d, "DIME'S", 160, 8, (150, 255, 180), center=True)
text(d, "LEAK SCANNER", 160, 22, GOLD, font=FONT_BIG, center=True)
text(d, "FIND YOUR MONEY LEAKS IN 7 DAYS", 160, 46, WHITE, center=True)
for k, x in enumerate((170, 194, 218)): drop(d, x, G, k)
sheet_icon(d, 288, 86)
badge(d, 275, 116, "FREE", RED)
dime(im, 92, G)
d = ImageDraw.Draw(im); d.fontmode = "1"
text(d, "FOUND!", 194, 98, WHITE, font=FONT_BIG, center=True)
text(d, "SPREADSHEET + GUIDE", 160, 166, WHITE, center=True)
im.resize((1280, 720), Image.NEAREST).save("leak_scanner_cover_1280x720.png")

# ---- thumbnail 600x600 (logical 150x150, x4) ----
G2 = 128
im = backdrop(150, 150, G2); d = ImageDraw.Draw(im); d.fontmode = "1"
d.rectangle([0, 0, 150, 46], fill=INK)
text(d, "LEAK", 75, 6, GOLD, font=FONT_BIG, center=True)
text(d, "SCANNER", 75, 26, GOLD, font=FONT_BIG, center=True)
drop(d, 126, G2, 0)
badge(d, 108, 80, "FREE", RED)
dime(im, 52, G2)
im.resize((600, 600), Image.NEAREST).save("leak_scanner_thumb_600.png")
print("saved")
