"""Carousel engine: Instagram carousel slides (1080x1350, 4:5) in the same arcade look as the videos.

Usage inside a carousel script (studio/episodes/cNNN_<slug>.py):

    exec(open("/home/claude/dime-money-quest/studio/carousel.py").read())
    def s1(im, d): ...           # one function per slide, drawn on a 180x225 canvas (6x upscaled)
    run_carousel("c001_boss_guide_trial_trap", [s1, s2, ...], example=[False, True, ...])

`python3 <script>.py` writes studio/<name>_01.png ... _NN.png plus <name>_cover.png (= slide 1).
Helpers: base(), title(), para(), big(), stat(), dime(), enemy_from(), steps(), end_slide().
Rules: every slide that shows an amount gets example=True ("EXAMPLE NUMBERS" in the footer);
slide 1 carries the hook and a SWIPE arrow; the last slide is the end card from content/status.md.
Keep everything inside x 8..172 (the 3:4 profile-grid crop cuts ~5 px per side at this scale).
"""
import math, sys
from PIL import Image, ImageDraw

STUDIO = "/home/claude/dime-money-quest/studio"
exec(open(f"{STUDIO}/render_guy.py").read().split("\ndef frame(t):")[0])

CW, CH, CS = 180, 225, 6           # low-res canvas, scaled 6x -> 1080x1350
MINT = (150, 255, 180); GREY = (200, 200, 215); PANEL = (40, 32, 62)
CTA_MODE = sys.argv[1] if len(sys.argv) > 1 else "more"
if CTA_MODE == "comment":
    raise SystemExit("Carousels end with Save this + Follow for more tips (mode more); Comment SCAN is for reels only, see content/status.md")

_STARS = [((k * 37) % CW, (k * 53) % CH) for k in range(40)]


def base(page, total, sky=(30, 24, 52), sky2=(70, 50, 110)):
    im = Image.new("RGB", (CW, CH), sky)
    d = ImageDraw.Draw(im); d.fontmode = "1"
    for y in range(CH):
        d.line([0, y, CW, y], fill=mixc(sky, sky2, y / CH))
    for k, (sx, sy) in enumerate(_STARS):
        if k % 3: d.point((sx, sy), fill=(255, 255, 220) if k % 2 else (160, 150, 210))
    # pixel frame
    d.rectangle([3, 3, CW - 4, CH - 4], outline=INK)
    d.rectangle([4, 4, CW - 5, CH - 5], outline=GOLD_D)
    # top bar: brand + page counter
    d.rectangle([5, 5, CW - 6, 17], fill=INK)
    coin_sprite(d, 12, 11, 3, 0.3)
    text(d, "MONEY QUEST", 18, 7, GOLD, shadow=False)
    text(d, f"{page}/{total}", CW - 10 - 8 * len(f"{page}/{total}"), 7, GREY, shadow=False)
    return im, d


def title(d, s, y=24, col=WHITE, big_font=True):
    """centered title; FONT_BIG fits 10 characters per line, FONT 20."""
    n = 10 if big_font else 20
    for k, ln in enumerate(wrap(s, n)):
        text(d, ln, CW // 2, y + k * (20 if big_font else 11), col, font=FONT_BIG if big_font else FONT, center=True)
    return y + len(wrap(s, n)) * (20 if big_font else 11)


def para(d, s, y, col=WHITE, n=20, center=False, x=10):
    for k, ln in enumerate(wrap(s, n)):
        text(d, ln, CW // 2 if center else x, y + k * 11, col, center=center)
    return y + len(wrap(s, n)) * 11


def big(d, s, y, col=GOLD):
    text(d, s, CW // 2, y, col, font=FONT_BIG, center=True)
    return y + 20


def panel(d, x0, y0, x1, y1, col=PANEL):
    d.rectangle([x0 - 1, y0 - 1, x1 + 1, y1 + 1], fill=INK)
    d.rectangle([x0, y0, x1, y1], fill=col)
    d.line([x0, y0, x1, y0], fill=mixc(col, WHITE, 0.25))


def stat(d, label, value, y, vcol=GOLD):
    """a game-wiki stat row: LABEL ........ VALUE"""
    text(d, label, 12, y, GREY, shadow=False)
    vx = CW - 12 - int(d.textlength(value, font=FONT))
    for x in range(12 + int(d.textlength(label, font=FONT)) + 3, vx - 3, 4): d.point((x, y + 6), fill=(110, 100, 140))
    text(d, value, vx, y, vcol, shadow=False)
    return y + 13


def steps(d, items, y, col=WHITE, num_col=GOLD):
    """numbered steps, wrapped to 17 chars after the number"""
    for i, s in enumerate(items):
        text(d, f"{i + 1}.", 10, y, num_col)
        for k, ln in enumerate(wrap(s, 17)):
            text(d, ln, 30, y + k * 11, col)
        y += len(wrap(s, 17)) * 11 + 5
    return y


def dime(im, cx, feet_y, mood="happy", scale=2, arms="down", item=None):
    """full-body Dime (from render_guy) pasted with his feet at (cx, feet_y). item(ld, gx, ghcy) draws a held item."""
    global guy_state
    _gs = guy_state
    guy_state = lambda t: (GUY_X, GROUND_Y, None, 0, arms, 1.0)
    globals()["mood_at"] = lambda t: mood
    layer = Image.new("RGBA", (LW, LH), (0, 0, 0, 0)); ld = ImageDraw.Draw(layer)
    gx, ghcy = guy(ld, 0.5)
    if item: item(ld, gx, ghcy)
    guy_state = _gs
    fx, fy = GUY_X, GROUND_Y + 1
    spr = layer.crop((fx - 30, fy - 90, fx + 30, fy)).resize((60 * scale, 90 * scale), Image.NEAREST)
    im.paste(spr, (cx - 30 * scale, feet_y - 90 * scale), spr)


def dime_head(im, cx, cy, mood="happy", scale=3):
    hl = Image.new("RGBA", (40, 40), (0, 0, 0, 0)); hd = ImageDraw.Draw(hl)
    head(hd, 20, 20, mood, 0.5)
    hl = hl.resize((40 * scale, 40 * scale), Image.NEAREST)
    im.paste(hl, (cx - 20 * scale, cy - 20 * scale), hl)


def enemy_from(episode_file):
    """load MCOLS + big_monster(d, cx, by, col, s, t, k, attacking) from a boss-fight script without rendering it"""
    src = open(f"{STUDIO}/episodes/{episode_file}").read()
    a = src.index("def big_monster"); b = src.index("def draw_bag")
    m = src.rfind("MCOLS = ", 0, a)
    ns = dict(globals())
    exec(src[m:b], ns)
    return ns["MCOLS"], ns["big_monster"]


def ground(d, y=200):
    for tx in range(5, CW - 5, 12):
        d.rectangle([tx, y, min(tx + 11, CW - 6), y + 4], fill=GREEN); d.line([tx, y, min(tx + 11, CW - 6), y], fill=(160, 255, 180))
    d.rectangle([5, y + 5, CW - 6, CH - 6], fill=(120, 74, 44))


def footer(d, page, total, example):
    if example:
        text(d, "EXAMPLE NUMBERS", CW // 2, CH - 16, GREY, center=True)
    if page < total:
        x = CW - 20
        d.polygon([(x, CH - 17), (x + 8, CH - 13), (x, CH - 9)], fill=GOLD)
        if page == 1: text(d, "SWIPE", x - 44, CH - 17, GOLD)


def end_slide(next_boss="NEXT BOSS"):
    """end card that matches the video end card ('more' = Follow for more tips) + a save prompt"""
    def draw(im, d):
        text(d, "SAVE THIS", CW // 2, 28, MINT, center=True)
        text(d, "FOR LATER", CW // 2, 40, MINT, center=True)
        if CTA_MODE == "more":
            text(d, "FOLLOW", CW // 2, 62, WHITE, font=FONT_BIG, center=True)
            text(d, "FOR MORE", CW // 2, 84, GOLD, font=FONT_BIG, center=True)
            text(d, "TIPS", CW // 2, 106, GOLD, font=FONT_BIG, center=True)
        else:
            text(d, "FOLLOW", CW // 2, 62, WHITE, font=FONT_BIG, center=True)
            text(d, "FOR PART 2", CW // 2, 84, GOLD, font=FONT_BIG, center=True)
        dime_head(im, 52, 162, "happy", 3)
        d2 = ImageDraw.Draw(im); d2.fontmode = "1"
        bx0 = 128
        panel(d2, bx0 - 30, 140, bx0 + 30, 158, (90, 110, 230))
        text(d2, "+FOLLOW", bx0 - 26, 145, WHITE, shadow=False)
        text(d2, next_boss, bx0, 170, MINT, center=True)
        for k in range(3):
            mx = bx0 - 14 + k * 14; my = 188
            d2.rectangle([mx - 5, my - 5, mx + 5, my + 5], fill=(70, 60, 100))
            d2.point((mx - 2, my - 1), fill=RED); d2.point((mx + 2, my - 1), fill=RED)
        text(d2, "@DIMESMONEYQUEST", CW // 2, 198, GREY, center=True)
    return draw


def run_carousel(name, slides, example):
    total = len(slides)
    assert 2 <= total <= 20 and len(example) == total
    for i, fn in enumerate(slides, 1):
        im, d = base(i, total)
        fn(im, d)
        d = ImageDraw.Draw(im); d.fontmode = "1"
        footer(d, i, total, example[i - 1])
        out = im.resize((CW * CS, CH * CS), Image.NEAREST)
        out.save(f"{STUDIO}/{name}_{i:02d}.png")
        if i == 1: out.save(f"{STUDIO}/{name}_cover.png")
    print("done", name, total, "slides")
