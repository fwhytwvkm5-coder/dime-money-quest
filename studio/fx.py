"""Visual upgrade kit (v2) for boss fights and quick formats: scenes, camera punch-ins, Dime moves, particles, quest bar.

Load after render_guy (or quick.py) inside an episode script:

    exec(open("/home/claude/dime-money-quest/studio/fx.py").read())

Scenes  : SCENES[name](im, d, t) paints sky + background + ground on the 180x320 canvas; ground top stays GROUND_Y (250).
          names: city_night, sunset, snow, mall, apartment, synthwave, rain. Pick one per reel that fits the topic and
          never use the same scene in two reels in a row (see CONTENT_RULES.md).
Camera  : world_zoom(im, t, ZOOMS) punches in on the world layer only (call it right after Dime is pasted, before the
          HUD and texts are drawn), so labels never get cropped. ZOOMS = [(t0, t1, zoom, cx, cy), ...].
Dime    : mirror_spin(layer, fx, t, spins) flips the sprite layer for a spin; dash_x(t, t0, t1, dist) for a dash;
          speed_lines(d, t, t0, t1, x, y) and dust(d, t, t0, x) for motion accents; confetti(d, t, t0) for wins.
Story   : quest_bar(d, t, t0, day, plan_before, plan_after, goal) shows Dime's savings quest (content/story.md).
"""
import math, random
from PIL import Image, ImageDraw

_R = random.Random(11)
FX_STARS = [(_R.randrange(0, 180), _R.randrange(36, 170)) for _ in range(50)]
FX_SNOW = [(_R.uniform(0, 180), _R.uniform(0, 320), _R.uniform(8, 20), _R.uniform(0, 6.28)) for _ in range(90)]
FX_RAIN = [(_R.uniform(0, 200), _R.uniform(0, 320), _R.uniform(160, 220)) for _ in range(70)]
FX_CONF = [(_R.uniform(-1, 1), _R.uniform(0.6, 1.3), _R.choice([(255, 80, 100), (255, 200, 40), (80, 220, 120), (80, 140, 255), (170, 110, 255)]))
           for _ in range(40)]


def _vgrad(d, y0, y1, c0, c1):
    for y in range(y0, y1):
        d.line([0, y, 180, y], fill=mixc(c0, c1, (y - y0) / max(1, y1 - y0)))


def _skyline(d, t, speed, col, win, base, scale=1.0, seed_off=0):
    """scrolling building row (parallax). speed in px/s."""
    off = int(t * speed) % 400
    for (bx, bw, bh, wins) in BUILD[seed_off:seed_off + 40]:
        x = (bx - off) % 420 - 40
        if x > 182 or x + bw < -2: continue
        h = int(bh * scale)
        d.rectangle([x, base - h, x + bw, base], fill=col)
        if win:
            for (wx, wy) in wins:
                if wy < h - 2: d.point((x + wx, base - h + wy), fill=win)


def _grass(d, t, top=(80, 220, 120), hi=(160, 255, 180), dirt=(120, 74, 44)):
    off = int(t * 18) % 12
    for tx in range(-12, 192, 12):
        x = tx - off
        d.rectangle([x, GROUND_Y, x + 11, GROUND_Y + 6], fill=top); d.line([x, GROUND_Y, x + 11, GROUND_Y], fill=hi)
        d.rectangle([x, GROUND_Y + 7, x + 11, 320], fill=dirt); d.point((x + 3, GROUND_Y + 11), fill=mixc(dirt, WHITE, 0.15))


def scene_city_night(im, d, t):
    _vgrad(d, 34, GROUND_Y, (30, 20, 70), (120, 60, 120))
    for i, (sx, sy) in enumerate(FX_STARS):
        if int(t * 3 + i) % 7: d.point((sx, sy), fill=(255, 255, 220))
    d.ellipse([136, 58, 156, 78], fill=(255, 235, 190)); d.ellipse([142, 58, 160, 76], fill=(30, 20, 70))   # crescent moon
    _skyline(d, t, 3, (60, 50, 110), (120, 110, 170), GROUND_Y, 1.25, 10)
    _skyline(d, t, 8, (45, 38, 85), (255, 210, 90), GROUND_Y, 1.0)
    _grass(d, t)


def scene_sunset(im, d, t):
    _vgrad(d, 34, 150, (70, 40, 120), (255, 120, 110))
    _vgrad(d, 150, GROUND_Y, (255, 120, 110), (255, 190, 120))
    r = 22
    d.ellipse([90 - r, 165 - r, 90 + r, 165 + r], fill=(255, 225, 140))
    for k in range(4): d.line([60, 168 + k * 5, 120, 168 + k * 5], fill=(255, 170, 120))       # sun stripes
    for (cx, cy, w) in ((30, 80, 34), (130, 100, 40), (70, 120, 26)):
        x = (cx + int(t * 4)) % 220 - 20
        d.rectangle([x, cy, x + w, cy + 4], fill=(255, 170, 160)); d.rectangle([x + 6, cy - 3, x + w - 8, cy], fill=(255, 190, 170))
    _skyline(d, t, 4, (120, 60, 110), None, GROUND_Y, 1.1, 5)
    _skyline(d, t, 10, (70, 40, 90), (255, 200, 120), GROUND_Y, 0.8, 20)
    _grass(d, t, (70, 190, 110), (150, 240, 170))


def scene_snow(im, d, t):
    _vgrad(d, 34, GROUND_Y, (40, 50, 100), (140, 150, 200))
    _skyline(d, t, 3, (80, 85, 140), (200, 200, 240), GROUND_Y, 1.2, 8)
    off = int(t * 8) % 400
    for (bx, bw, bh, wins) in BUILD[:40]:                                       # front row with snowy roofs + warm windows
        x = (bx - off) % 420 - 40
        if x > 182 or x + bw < -2: continue
        d.rectangle([x, GROUND_Y - bh, x + bw, GROUND_Y], fill=(50, 50, 95))
        d.rectangle([x - 1, GROUND_Y - bh - 2, x + bw + 1, GROUND_Y - bh], fill=(240, 245, 255))
        for (wx, wy) in wins: d.point((x + wx, GROUND_Y - bh + wy), fill=(255, 200, 110))
    for (sx, sy, sp, ph) in FX_SNOW:                                            # falling snow
        y = (sy + t * sp) % 290 + 34
        x = (sx + math.sin(t * 1.5 + ph) * 4) % 180
        if y < GROUND_Y: d.point((int(x), int(y)), fill=WHITE)
    d.rectangle([0, GROUND_Y, 180, GROUND_Y + 6], fill=(235, 240, 255)); d.line([0, GROUND_Y, 180, GROUND_Y], fill=WHITE)
    d.rectangle([0, GROUND_Y + 7, 180, 320], fill=(110, 90, 80))


def scene_mall(im, d, t):
    """shopping mall: shop windows with generic SALE signs, string lights, tiled floor (no brands)"""
    _vgrad(d, 34, GROUND_Y, (60, 45, 90), (110, 80, 140))
    for k in range(0, 180, 6): d.line([k, 34, k, 40], fill=(80, 60, 110))
    off = int(t * 10) % 64
    for i in range(5):
        x = i * 64 - off - 10
        d.rectangle([x, 120, x + 56, GROUND_Y], fill=(40, 30, 60))
        d.rectangle([x + 3, 140, x + 53, GROUND_Y - 4], fill=(90, 160, 200))
        d.line([x + 3, 140, x + 53, GROUND_Y - 4], fill=(140, 200, 230))
        d.rectangle([x + 2, 122, x + 54, 136], fill=(255, 80, 100) if (i + int(t * 2)) % 2 else (255, 120, 140))
        tx = x + 22                                    # price-tag pictogram instead of words (no text that could get cut off)
        d.polygon([(tx, 129), (tx + 4, 125), (tx + 14, 125), (tx + 14, 133), (tx + 4, 133)], fill=WHITE)
        d.point((tx + 4, 129), fill=(255, 80, 100))
        for k in range(3):   # boxes and bags in the window
            d.rectangle([x + 8 + k * 15, GROUND_Y - 22 + (k % 2) * 6, x + 18 + k * 15, GROUND_Y - 6], fill=[(255, 200, 40), (170, 110, 255), (80, 220, 120)][k])
    for k in range(18):      # string lights
        x = (k * 11 - int(t * 10)) % 198 - 9
        y = 52 + int(6 * math.sin(k * 0.9))
        d.point((x, y), fill=(255, 230, 120) if (k + int(t * 6)) % 3 else (255, 110, 130))
    for k in range(0, 180, 16):                                                  # tiled floor
        x = (k - int(t * 18)) % 192 - 6
        d.rectangle([x, GROUND_Y, x + 15, 320], fill=(200, 190, 210) if (k // 16) % 2 else (175, 165, 190))
    d.line([0, GROUND_Y, 180, GROUND_Y], fill=WHITE)


def scene_apartment(im, d, t):
    """Dime's room: wallpaper, window with the night city, desk lamp, bills on the wall, wooden floor"""
    _vgrad(d, 34, GROUND_Y, (90, 110, 140), (70, 85, 115))
    for x in range(4, 180, 12):
        for y in range(40, GROUND_Y, 12): d.point((x + (y // 12) % 2 * 6, y), fill=(110, 130, 160))
    d.rectangle([96, 64, 168, 140], fill=INK)
    d.rectangle([99, 67, 165, 137], fill=(30, 25, 70))
    for i, (sx, sy) in enumerate(FX_STARS[:14]): d.point((100 + sx % 64, 68 + sy % 40), fill=(255, 255, 220))
    for (bx, bw, bh, wins) in BUILD[:8]:
        x = 100 + (bx + 40) % 64
        d.rectangle([x, 137 - bh // 2, min(165, x + bw // 2), 137], fill=(55, 50, 95))
    d.line([132, 67, 132, 137], fill=INK); d.line([99, 102, 165, 102], fill=INK)
    d.rectangle([14, 150, 36, 178], fill=WHITE); d.rectangle([16, 152, 34, 156], fill=RED)        # a bill on the wall (low, away from the texts)
    for k in range(4): d.line([17, 160 + k * 4, 32 - k * 3, 160 + k * 4], fill=(150, 150, 170))
    d.rectangle([116, 196, 172, 200], fill=(140, 90, 60)); d.rectangle([120, 200, 124, GROUND_Y], fill=(110, 70, 50)); d.rectangle([164, 200, 168, GROUND_Y], fill=(110, 70, 50))
    d.line([156, 196, 150, 178], fill=INK, width=2); d.polygon([(142, 180), (156, 180), (152, 170), (146, 170)], fill=(255, 210, 90))
    glow = 0.25 + 0.05 * math.sin(t * 4)
    for r in range(18, 4, -4): d.ellipse([149 - r, 182 - r // 2, 149 + r, 182 + r // 2], outline=mixc((70, 85, 115), (255, 220, 140), glow))
    for x in range(0, 180, 20):
        d.rectangle([x, GROUND_Y, x + 19, 320], fill=(150, 100, 65) if (x // 20) % 2 else (135, 90, 58))
        d.line([x, GROUND_Y, x, 320], fill=(100, 65, 40))
    d.line([0, GROUND_Y, 180, GROUND_Y], fill=(190, 140, 95))


def scene_synthwave(im, d, t):
    """retro arcade grid: striped sun, purple sky, moving perspective floor - the loudest look, best for hooks"""
    _vgrad(d, 34, 200, (20, 10, 50), (190, 50, 140))
    for i, (sx, sy) in enumerate(FX_STARS):
        if sy < 140 and int(t * 4 + i) % 5: d.point((sx, sy), fill=(255, 220, 255))
    r = 34
    for y in range(160 - r, 160 + 1):
        w = int(math.sqrt(max(0, r * r - (y - 160) ** 2)))
        if (y // 4) % 3 == 2 and y > 140: continue
        d.line([90 - w, y, 90 + w, y], fill=mixc((255, 230, 90), (255, 80, 140), (y - 126) / r))
    for k, (x, h) in enumerate(((10, 30), (40, 18), (130, 26), (160, 34))):     # mountains
        d.polygon([(x - 30, 200), (x, 200 - h - 10), (x + 30, 200)], fill=(60, 20, 90))
    d.rectangle([0, 200, 180, 320], fill=(25, 8, 45))
    for k in range(9):                                                            # moving horizontal grid lines
        p = ((k + t * 1.5) % 9) / 9
        y = 200 + int(120 * p * p)
        d.line([0, y, 180, y], fill=(255, 60, 200) if y < GROUND_Y + 10 else (190, 40, 160))
    for k in range(-8, 9):
        d.line([90 + k * 6, 200, 90 + k * 40, 320], fill=(200, 40, 170))
    d.line([0, GROUND_Y, 180, GROUND_Y], fill=(120, 240, 255))


def scene_rain(im, d, t):
    _vgrad(d, 34, GROUND_Y, (20, 25, 50), (50, 60, 95))
    _skyline(d, t, 3, (40, 45, 75), (90, 100, 140), GROUND_Y, 1.2, 12)
    _skyline(d, t, 8, (28, 30, 55), None, GROUND_Y, 0.95)
    for i, (x, y, c) in enumerate(((30, 150, (255, 80, 160)), (120, 130, (90, 220, 255)), (160, 170, (255, 200, 60)))):  # neon signs
        xx = (x - int(t * 8)) % 200 - 10
        on = (int(t * 5) + i) % 7 != 0
        d.rectangle([xx - 10, y - 5, xx + 10, y + 5], outline=c if on else (60, 60, 80))
        if on: d.rectangle([xx - 7, y - 2, xx + 7, y + 2], fill=mixc(c, (20, 25, 50), 0.6))
    if int(t * 3) % 17 == 0:                                                      # lightning flash
        d.rectangle([0, 34, 180, 60], fill=(70, 80, 120))
    for (x, y, sp) in FX_RAIN:
        yy = (y + t * sp) % 290 + 34
        xx = (x - t * 30) % 200 - 10
        if yy < GROUND_Y: d.line([int(xx), int(yy), int(xx) - 2, int(yy) + 6], fill=(140, 170, 230))
    d.rectangle([0, GROUND_Y, 180, 320], fill=(45, 45, 70))
    d.line([0, GROUND_Y, 180, GROUND_Y], fill=(120, 130, 170))
    for k in range(6):                                                            # puddle ripples
        x = (k * 37 + 11) % 180; r = int((t * 12 + k * 5) % 10)
        d.ellipse([x - r, GROUND_Y + 8 - r // 3, x + r, GROUND_Y + 8 + r // 3], outline=(110, 120, 170))


SCENES = {"city_night": scene_city_night, "sunset": scene_sunset, "snow": scene_snow, "mall": scene_mall,
          "apartment": scene_apartment, "synthwave": scene_synthwave, "rain": scene_rain}


def paint_scene(name, t):
    im = Image.new("RGB", (LW, LH), INK)
    d = ImageDraw.Draw(im); d.fontmode = "1"
    SCENES[name](im, d, t)
    return im, d


# ---------- camera ----------
def zoom_at(t, zooms):
    z, cx, cy = 1.0, LW / 2, LH / 2
    for (t0, t1, zz, x, y) in zooms:
        if t0 <= t < t1:
            a = ease_out(prog(t, t0, t0 + 0.12)) * (1 - ease_io(prog(t, t1 - 0.25, t1)))
            z = 1 + (zz - 1) * a; cx = lerp(LW / 2, x, a); cy = lerp(LH / 2, y, a)
    return z, cx, cy


def world_zoom(im, t, zooms):
    z, cx, cy = zoom_at(t, zooms)
    if z <= 1.001: return im
    w, h = LW / z, LH / z
    x0 = clamp(cx - w / 2, 0, LW - w); y0 = clamp(cy - h / 2, 0, LH - h)
    return im.crop((int(x0), int(y0), int(x0 + w), int(y0 + h))).resize((LW, LH), Image.NEAREST)


# ---------- Dime moves + particles ----------
def dash_x(t, t0, t1, dist):
    """0 -> dist -> 0: dash toward the enemy in the first 40 % of [t0, t1], hold, hop back"""
    if not (t0 <= t < t1): return 0
    p = (t - t0) / (t1 - t0)
    if p < 0.4: return int(dist * ease_out(p / 0.4))
    if p < 0.7: return dist
    return int(dist * (1 - ease_io((p - 0.7) / 0.3)))


def mirror_spin(layer, fx, t, spins):
    """spins = [(t0, t1), ...]; flips the sprite layer around x = fx every 1/12 s inside each window (a pixel 'spin')"""
    for (t0, t1) in spins:
        if t0 <= t < t1 and int((t - t0) * 12) % 2:
            fl = layer.transpose(Image.FLIP_LEFT_RIGHT)
            out = Image.new("RGBA", layer.size, (0, 0, 0, 0))
            out.paste(fl, (2 * fx - LW, 0))
            return out
    return layer


def speed_lines(d, t, t0, t1, x, y, col=(255, 255, 255)):
    if not (t0 <= t < t1): return
    for k in range(6):
        yy = y - 30 + k * 11 + int(t * 50) % 4
        ln = 10 + (k * 7) % 14
        d.line([x - ln - 6, yy, x - 6, yy], fill=col)


def dust(d, t, t0, x, y=None):
    y = GROUND_Y if y is None else y
    p = prog(t, t0, t0 + 0.35)
    if 0 < p < 1:
        for s in (-1, 1):
            for k in range(3):
                px = x + s * int(4 + p * (8 + k * 4)); py = y - int(3 * math.sin(math.pi * p)) - k
                d.rectangle([px - 1, py - 1, px + 1, py + 1], fill=mixc((230, 220, 210), (120, 110, 100), p))


def confetti(d, t, t0, dur=1.6, cx=90, cy=120):
    p = prog(t, t0, t0 + dur)
    if not (0 < p < 1): return
    for k, (vx, vy, col) in enumerate(FX_CONF):
        x = cx + int(vx * 90 * p); y = cy - int(vy * 120 * p) + int(160 * p * p)
        if 34 < y < LH: d.rectangle([x, y, x + (k % 2), y + 1], fill=col)


def shockwave(d, t, t0, x, y, col=(255, 255, 255)):
    p = prog(t, t0, t0 + 0.3)
    if 0 < p < 1:
        r = int(4 + p * 40)
        d.ellipse([x - r, y - r // 2, x + r, y + r // 2], outline=col)


# ---------- story ----------
def quest_bar(d, t, t0, day, plan_before, plan_after, goal=3000):
    """Dime's savings quest panel (y 52..84). plan_* = what Dime sets aside per month (content/story.md ledger)."""
    if t < t0: return
    p = ease_out(prog(t, t0, t0 + 0.6))
    plan = int(round(lerp(plan_before, plan_after, p)))
    months = math.ceil(goal / max(1, plan))
    d.rectangle([7, 51, LW - 8, 85], fill=INK); d.rectangle([8, 52, LW - 9, 84], outline=(150, 255, 180))
    text(d, f"DIME'S QUEST DAY {day}", 12, 55, (150, 255, 180), shadow=False)
    text(d, f"SAVES €{plan}/MONTH", 12, 65, GOLD, shadow=False)
    text(d, f"€{goal:,} IN {months} MO", 12, 75, WHITE, shadow=False)


def plate(im, y0, y1, a=0.55):
    """darkened band behind big headlines so they stay readable on busy scenes"""
    band = im.crop((0, y0, LW, y1))
    im.paste(Image.blend(band, Image.new("RGB", band.size, INK), a), (0, y0))
    return im
