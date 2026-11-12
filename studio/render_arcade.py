import math, random, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont

LW, LH, S = 180, 320, 6
W, H = LW * S, LH * S
FPS, DUR = 30, 23.5
N = int(FPS * DUR)
FONT = ImageFont.truetype("/home/claude/dime-money-quest/studio/PressStart2P.ttf", 8)
FONT_BIG = ImageFont.truetype("/home/claude/dime-money-quest/studio/PressStart2P.ttf", 16)
OUT = "/home/claude/dime-money-quest/studio/arcade_silent.mp4"

INK = (24, 18, 34); WHITE = (255, 255, 255); GOLD = (255, 200, 40); GOLD_D = (214, 128, 20); GOLD_L = (255, 245, 170)
RED = (255, 80, 100); GREEN = (80, 220, 120); BLUE = (80, 140, 255); PURPLE = (170, 110, 255); ORANGE = (255, 150, 50)
GROUND_Y = 250
X = [70, 270, 470, 670, 870, 1070]
HIT = 1.6
ARR = [1.9] + [1.9 + 3.3 * i for i in range(1, 6)]
JUMP = 0.6
END = 20.6
AMOUNTS = [2000, -1100, -86, -240, -310, 0]
DAYS = [1, 2, 5, 11, 16, 20]
DIALOG = [(0.0, "WHY IS YOUR MONEY GONE BY DAY 20?"),
          (2.0, "PAYDAY! +€2000 LANDS IN YOUR ACCOUNT"),
          (ARR[1], "RENT + BILLS TAKE €1100. FAIR."),
          (ARR[2], "SUBSCRIPTIONS YOU FORGOT ABOUT: -€86"),
          (ARR[3], "TAKEOUT 'JUST THIS ONCE': -€240"),
          (ARR[4], "IMPULSE BUYS: -€310"),
          (ARR[5], "DAY 20. ONLY €264 LEFT?!"),
          (END, "WHERE DID IT GO? PART 2: PLUG THE LEAKS")]

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def prog(t, a, b): return clamp((t - a) / (b - a))
def lerp(a, b, x): return a + (b - a) * x
def ease_io(x): return 3 * x * x - 2 * x * x * x
def ease_out(x): return 1 - (1 - x) ** 3
def mixc(c1, c2, x): return tuple(int(lerp(a, b, x)) for a, b in zip(c1, c2))

def balance(t):
    b = 2000 * ease_out(prog(t, 1.7, 2.7))
    for i in range(1, 6):
        b += AMOUNTS[i] * ease_out(prog(t, ARR[i] + 0.3, ARR[i] + 1.3))
    return int(round(b))

def hero(t):
    """world x, y (centre), squash"""
    R = 9
    rest = GROUND_Y - R
    if t < 0.9:
        return lerp(-20, X[0] - 30, ease_out(prog(t, 0, 0.9))), rest - abs(math.sin(t * 14)) * 3, 1.0
    if t < 1.9:
        p = prog(t, 1.3, 1.9)
        if p <= 0: return X[0] - 30, rest, 1.0 - 0.2 * prog(t, 1.15, 1.3)
        y = rest - 34 * math.sin(math.pi * p)
        return X[0] - 30, y, 1.0
    for i in range(1, 6):
        t0 = ARR[i] - JUMP
        if t0 <= t < ARR[i]:
            p = (t - t0) / JUMP
            return lerp(X[i - 1] - 30, X[i] - 30, ease_io(p)), rest - 48 * 4 * p * (1 - p), 1.12
    i = max(k for k in range(6) if t >= ARR[k])
    d = t - ARR[i]
    sq = 1 - 0.3 * max(0, 1 - d / 0.2)
    bob = (math.sin(t * 6) > 0) * 1
    return X[i] - 30, rest + (1 - sq) * 6 - bob, sq

def cam(t):
    hx, _, _ = hero(t)
    return clamp(hx - 60, 0, 2000)

def sky_colors(day):
    p = clamp((day - 1) / 19)
    top = mixc(mixc((60, 120, 240), (120, 60, 140), min(1, p * 1.4)), (30, 16, 50), max(0, p - 0.5) * 2)
    bot = mixc(mixc((140, 200, 255), (255, 140, 100), min(1, p * 1.4)), (120, 30, 60), max(0, p - 0.5) * 2)
    return top, bot

def day_at(t):
    i = max([k for k in range(6) if t >= ARR[k] - 0.2] + [0])
    return DAYS[i]

random.seed(5)
STARS = [(random.randrange(0, 400), random.randrange(36, 150)) for _ in range(60)]
BUILD = []
x = -40
while x < 1400:
    bw = random.randint(12, 26); bh = random.randint(30, 85)
    wins = [(wx, wy) for wy in range(4, bh - 4, 8) for wx in range(3, bw - 3, 6) if random.random() < 0.45]
    BUILD.append((x, bw, bh, wins)); x += bw + random.randint(1, 4)
HILLS = [(i * 90 + random.randint(-20, 20), random.randint(18, 34)) for i in range(-2, 30)]
BURST = [(random.uniform(-1, 1), random.uniform(0.8, 1.3)) for _ in range(14)]

def coin_sprite(d, cx, cy, r=3, spin=0.0):
    w = max(1, int(abs(math.cos(spin)) * r))
    d.rectangle([cx - w, cy - r, cx + w, cy + r], fill=GOLD)
    d.rectangle([cx - w, cy - r, cx + w, cy - r], fill=GOLD_L)
    if w > 1: d.rectangle([cx - w, cy + r, cx + w, cy + r], fill=GOLD_D)

def draw_hero(d, cx, cy, sq, mood, t):
    R = 9
    ry = int(R * sq); rx = int(R / max(sq, 0.6) ** 0.5)
    d.ellipse([cx - rx - 1, cy - ry - 1, cx + rx + 1, cy + ry + 1], fill=INK)
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=GOLD)
    d.ellipse([cx - rx + 2, cy - ry + 2, cx + rx - 2, cy + ry - 2], outline=GOLD_D)
    d.rectangle([cx + rx - 1, cy - 3, cx + rx, cy + ry - 3], fill=GOLD_D)
    d.rectangle([cx - rx + 2, cy - ry + 2, cx - rx + 3, cy - ry + 3], fill=GOLD_L)
    blink = (t % 2.7) < 0.1
    ey = cy - 2
    if mood == "happy":
        for s in (-1, 1):
            d.point((cx + s * 3 - 1, ey), fill=INK); d.point((cx + s * 3, ey - 1), fill=INK); d.point((cx + s * 3 + 1, ey), fill=INK)
        d.line([cx - 2, cy + 3, cx + 2, cy + 3], fill=INK); d.point((cx - 3, cy + 2), fill=INK); d.point((cx + 3, cy + 2), fill=INK)
    elif mood == "shock":
        for s in (-1, 1):
            d.rectangle([cx + s * 3 - 1, ey - 2, cx + s * 3, ey + 1], fill=INK)
        d.rectangle([cx - 1, cy + 3, cx + 1, cy + 5], fill=INK)
        if int(t * 4) % 2 == 0:
            d.rectangle([cx + rx + 2, cy - ry, cx + rx + 3, cy - ry + 2], fill=(140, 200, 255))
    else:
        for s in (-1, 1):
            if blink: d.line([cx + s * 3 - 1, ey, cx + s * 3, ey], fill=INK)
            else: d.rectangle([cx + s * 3 - 1, ey - 1, cx + s * 3, ey + 1], fill=INK)
        d.line([cx - 2, cy + 3, cx + 2, cy + 3], fill=INK)
    d.point((cx - 6, cy + 1), fill=(255, 140, 120)); d.point((cx + 5, cy + 1), fill=(255, 140, 120))

def monster(d, cx, cy, col, t, k):
    b = int(abs(math.sin(t * 8 + k)) * 3)
    cy -= b
    d.rectangle([cx - 6, cy - 6, cx + 6, cy + 6], fill=INK)
    d.rectangle([cx - 5, cy - 5, cx + 5, cy + 5], fill=col)
    d.rectangle([cx - 5, cy - 5, cx + 5, cy - 5], fill=mixc(col, WHITE, 0.4))
    d.rectangle([cx - 3, cy - 2, cx - 1, cy], fill=WHITE); d.rectangle([cx + 1, cy - 2, cx + 3, cy], fill=WHITE)
    d.point((cx - 2, cy - 1), fill=INK); d.point((cx + 2, cy - 1), fill=INK)
    open_ = int(t * 6 + k) % 2
    d.rectangle([cx - 2, cy + 2, cx + 2, cy + 2 + open_], fill=INK)
    for j in range(3): d.point((cx - 4 + j * 4, cy + 7), fill=INK)

def text(d, s, x, y, col, shadow=True, font=FONT, center=False):
    if center:
        w = d.textlength(s, font=font); x = int(x - w / 2)
    if shadow: d.text((x + 1, y + 1), s, font=font, fill=INK)
    d.text((x, y), s, font=font, fill=col)

def wrap(s, n=20):
    words, lines, cur = s.split(" "), [], ""
    for w in words:
        if len(cur) + len(w) + (1 if cur else 0) > n: lines.append(cur); cur = w
        else: cur = (cur + " " + w) if cur else w
    lines.append(cur); return lines

def frame(t):
    day = day_at(t)
    top, bot = sky_colors(day)
    im = Image.new("RGB", (LW, LH), top)
    d = ImageDraw.Draw(im); d.fontmode = "1"
    for y in range(34, GROUND_Y):
        if y % 2 == 0 or y > 150:
            d.line([0, y, LW, y], fill=mixc(top, bot, (y - 34) / (GROUND_Y - 34)))
        else:
            d.line([0, y, LW, y], fill=mixc(top, bot, (y - 35) / (GROUND_Y - 34)))
    cx = cam(t)
    shake = 0
    for ht in [HIT] + [a + 0.3 for a in ARR[1:5]]:
        if 0 <= t - ht < 0.2: shake = int(2 * math.sin((t - ht) * 90))
    # stars (only later in month)
    if day >= 11:
        for (sx, sy) in STARS:
            x = int((sx - cx * 0.1) % 200) - 10
            if int(t * 3 + sx) % 7: d.point((x, sy), fill=(255, 255, 220))
    # sun / moon
    sun_y = int(lerp(70, 210, clamp((day - 1) / 19)))
    sc = mixc((255, 240, 150), (255, 120, 90), clamp((day - 1) / 19))
    if t >= 1.5: d.ellipse([130 - 12, sun_y - 12, 130 + 12, sun_y + 12], fill=sc)
    # hills (0.2 parallax)
    for (hx, hh) in HILLS:
        x = int(hx - cx * 0.2)
        if -80 < x < 260:
            d.ellipse([x - 50, GROUND_Y - hh - 30, x + 50, GROUND_Y + 40], fill=mixc(bot, (40, 90, 80), 0.5))
    # city (0.45 parallax)
    for (bx, bw, bh, wins) in BUILD:
        x = int(bx - cx * 0.45)
        if x > LW or x + bw < 0: continue
        bc = mixc((60, 70, 110), (40, 24, 60), clamp((day - 1) / 19))
        d.rectangle([x, GROUND_Y - bh, x + bw, GROUND_Y], fill=bc)
        lit = day >= 5
        for (wx, wy) in wins:
            d.point((x + wx, GROUND_Y - bh + wy), fill=(255, 210, 90) if lit else mixc(bc, WHITE, 0.25))
    # ground
    gy = GROUND_Y + shake
    for tx in range(-int(cx) % 12 - 12, LW + 12, 12):
        d.rectangle([tx, gy, tx + 11, gy + 6], fill=GREEN)
        d.line([tx, gy, tx + 11, gy], fill=(160, 255, 180))
        d.rectangle([tx, gy + 7, tx + 11, LH], fill=(120, 74, 44))
        d.point((tx + 3, gy + 11), fill=(150, 100, 60)); d.point((tx + 8, gy + 17), fill=(150, 100, 60))
        d.line([tx + 11, gy + 1, tx + 11, gy + 6], fill=(50, 160, 90))

    def W2S(wx): return int(wx - cx)
    # ---- station props ----
    # 0: ? block
    bx = W2S(X[0] - 30)
    bump = int(4 * math.sin(math.pi * prog(t, HIT, HIT + 0.15)))
    used = t >= HIT
    by = 186 - bump + shake
    d.rectangle([bx - 8, by - 8, bx + 8, by + 8], fill=INK)
    d.rectangle([bx - 7, by - 7, bx + 7, by + 7], fill=(150, 100, 60) if used else ORANGE)
    if not used:
        d.rectangle([bx - 7, by - 7, bx + 7, by - 7], fill=(255, 220, 140))
        if int(t * 3) % 2: text(d, "?", bx - 3, by - 4, WHITE, shadow=False)
        else: text(d, "?", bx - 3, by - 4, (255, 240, 200), shadow=False)
    for c in [(-6, -6), (6, -6), (-6, 6), (6, 6)]:
        d.point((bx + c[0], by + c[1]), fill=INK)
    # burst coins
    for k, (u, v) in enumerate(BURST):
        p = prog(t, HIT + k * 0.04, HIT + 0.9 + k * 0.04)
        if 0 < p < 1:
            px = bx + int(u * 40 * p); py = by - 10 - int(70 * v * math.sin(math.pi * p * 0.9)) + int(40 * p * p)
            coin_sprite(d, px, py, 3, t * 12 + k)
    # 1: house
    hx = W2S(X[1] + 25)
    d.polygon([(hx - 26, 210 + shake), (hx, 188 + shake), (hx + 26, 210 + shake)], fill=RED, outline=INK)
    d.rectangle([hx - 20, 210 + shake, hx + 20, GROUND_Y - 1 + shake], fill=(240, 220, 190), outline=INK)
    d.rectangle([hx - 5, 230 + shake, hx + 5, GROUND_Y - 1 + shake], fill=(60, 140, 140), outline=INK)
    d.rectangle([hx - 16, 218 + shake, hx - 9, 225 + shake], fill=(160, 220, 255), outline=INK)
    d.rectangle([hx + 9, 218 + shake, hx + 16, 225 + shake], fill=(160, 220, 255), outline=INK)
    d.rectangle([hx + 10, 192 + shake, hx + 15, 202 + shake], fill=(120, 120, 140), outline=INK)
    # 2: monsters
    mcols = [BLUE, RED, GREEN, PURPLE]
    for k in range(4):
        mx = W2S(X[2] + 5 + k * 16)
        my = 236 - (k % 2) * 22
        if t > ARR[2] - 1.0: monster(d, mx, my + shake, mcols[k], t, k)
    # 3: scooter drives through
    sp = prog(t, ARR[3] + 0.1, ARR[3] + 1.8)
    if 0 < sp < 1:
        scx = W2S(X[3] + 110) - int(sp * 230)
        sy = GROUND_Y - 6 + shake
        d.rectangle([scx - 12, sy - 10, scx + 8, sy - 3], fill=RED, outline=INK)
        d.rectangle([scx + 2, sy - 22, scx + 14, sy - 10], fill=ORANGE, outline=INK)
        d.rectangle([scx + 5, sy - 17, scx + 11, sy - 15], fill=(120, 70, 30))
        d.line([scx - 12, sy - 10, scx - 16, sy - 20], fill=INK, width=2)
        for wx in (scx - 9, scx + 6):
            d.ellipse([wx - 4, sy - 4, wx + 4, sy + 4], fill=INK); d.point((wx, sy), fill=(150, 150, 160))
        for k in range(3):
            d.line([scx + 16 + k * 6, sy - 14 + k * 4, scx + 22 + k * 6, sy - 14 + k * 4], fill=WHITE)
    elif t < ARR[3] + 0.1 and t > ARR[3] - 1.2:
        pass
    # 4: cart
    cp = ease_out(prog(t, ARR[4] - 0.9, ARR[4] - 0.1))
    if cp > 0:
        ccx = W2S(X[4] + 30) + int((1 - cp) * 120)
        cy0 = 222 + shake
        d.polygon([(ccx - 20, cy0), (ccx + 20, cy0), (ccx + 16, cy0 + 18), (ccx - 16, cy0 + 18)], fill=(200, 210, 230), outline=INK)
        for k in range(1, 5):
            d.line([ccx - 20 + k * 8, cy0 + 1, ccx - 18 + k * 7, cy0 + 17], fill=(120, 130, 160))
        d.line([ccx + 20, cy0, ccx + 26, cy0 - 8], fill=INK, width=2)
        for wx in (ccx - 12, ccx + 12):
            d.ellipse([wx - 3, cy0 + 19, wx + 3, cy0 + 25], fill=INK)
        items = [(ccx - 12, BLUE), (ccx - 2, RED), (ccx + 8, PURPLE)]
        ip = prog(t, ARR[4] + 0.4, ARR[4] + 1.4)
        for k, (ix, c) in enumerate(items):
            hgt = int(lerp(4, 12, clamp(ip * 3 - k)))
            d.rectangle([ix - 4, cy0 - hgt, ix + 4, cy0 + 2], fill=c, outline=INK)
    # 5: calendar
    if t > ARR[5] - 1.2:
        kx = W2S(X[5] + 30); ky = 190 + shake + int(math.sin(t * 3) * 2)
        d.rectangle([kx - 22, ky, kx + 22, ky + 40], fill=WHITE, outline=INK)
        d.rectangle([kx - 22, ky, kx + 22, ky + 10], fill=RED, outline=INK)
        d.rectangle([kx - 14, ky - 4, kx - 11, ky + 3], fill=(120, 120, 140)); d.rectangle([kx + 11, ky - 4, kx + 14, ky + 3], fill=(120, 120, 140))
        text(d, "20", kx - 16, ky + 16, INK, shadow=False, font=FONT_BIG)

    # ---- coins leaving the hero ----
    hx, hy, sq = hero(t)
    for i in range(1, 5):
        for k in range(10):
            p = prog(t, ARR[i] + 0.3 + k * 0.08, ARR[i] + 0.9 + k * 0.08)
            if 0 < p < 1:
                tx = {1: X[1] + 25, 2: X[2] + 5 + (k % 4) * 16, 3: X[3] + 110 - int(prog(t, ARR[3] + 0.1, ARR[3] + 1.8) * 230), 4: X[4] + 30}[i]
                ty = {1: 238, 2: 236 - ((k % 4) % 2) * 22, 3: 228, 4: 222}[i]
                px = int(lerp(hx, tx, p)) - int(cx); py = int(lerp(hy, ty, p) - 26 * math.sin(math.pi * p)) + shake
                coin_sprite(d, px, py, 3, t * 12 + k)
    # floating amounts
    for i in range(6):
        if AMOUNTS[i] == 0: continue
        st = HIT + 0.1 if i == 0 else ARR[i] + 0.3
        p = prog(t, st, st + 1.4)
        if 0 < p < 1 and int(t * 10) % 3 != 0 or 0.1 < p < 0.8:
            if 0 < p < 1:
                s = (f"+€{AMOUNTS[i]}" if AMOUNTS[i] > 0 else f"-€{-AMOUNTS[i]}")
                text(d, s, int(hx - cx) - 6, int(hy) - 44 - int(18 * p), GREEN if AMOUNTS[i] > 0 else RED)

    # hero
    mood = "neutral"
    if t < 1.3 or 1.6 <= t < ARR[1]: mood = "happy"
    if t >= ARR[4] + 0.4: mood = "shock"
    if 3 <= 3 and any(ARR[k] <= t < ARR[k] + 0.3 for k in range(2, 4)): mood = "shock"
    draw_hero(d, int(hx - cx), int(hy) + shake, sq, mood, t)

    # ---- HUD ----
    d.rectangle([0, 0, LW, 33], fill=INK)
    bal = balance(t)
    coin_sprite(d, 9, 9, 4, t * 4)
    text(d, f"€{max(bal, 0)}", 18, 6, GOLD)
    text(d, f"DAY {day:02d}", 118, 6, (150, 255, 180))
    frac = clamp(bal / 2000)
    bc = GREEN if frac > 0.5 else (GOLD if frac > 0.25 else RED)
    d.rectangle([6, 20, 173, 28], fill=(60, 50, 80))
    if not (frac < 0.15 and t > ARR[5] and int(t * 6) % 2):
        d.rectangle([7, 21, 7 + int(165 * frac), 27], fill=bc)
        d.line([7, 21, 7 + int(165 * frac), 21], fill=mixc(bc, WHITE, 0.5))
    if t > ARR[5] + 0.3 and int(t * 4) % 2 and t < END:
        text(d, "LOW FUNDS!", 90, 160, RED, center=True)

    # big hook title
    if t < 1.5:
        a = prog(t, 0, 0.2)
        if a > 0:
            for k, ln in enumerate(["WHY IS", "YOUR MONEY", "GONE BY", "DAY 20?"]):
                text(d, ln, 90, 62 + k * 22, GOLD if k in (1, 3) else WHITE, font=FONT_BIG, center=True)

    # end screen
    if t >= END:
        p = prog(t, END, END + 0.4)
        ov = Image.new("RGB", (LW, LH), INK)
        im.paste(Image.blend(im.crop((0, 0, LW, LH)), ov, 0.9 * p))
        d = ImageDraw.Draw(im); d.fontmode = "1"
        if p >= 1:
            text(d, "GAME OVER?", 90, 92, RED, font=FONT_BIG, center=True)
            if t > END + 0.7: text(d, "CONTINUE IN", 90, 128, WHITE, center=True)
            if t > END + 1.0: text(d, "PART 2", 90, 144, GOLD, font=FONT_BIG, center=True)
            if t > END + 1.5 and int(t * 3) % 2:
                text(d, "> FOLLOW TO PLAY ON <", 90, 186, (150, 255, 180), center=True)
            draw_hero(d, 90, 222, 1.0, "shock", t)

    # dialog box
    cur = max([k for k in range(len(DIALOG)) if t >= DIALOG[k][0]])
    t0, msg = DIALOG[cur]
    n = int((t - t0) * 32)
    shown = msg[:n]
    lines = wrap(msg, 20)
    d.rectangle([4, 268, LW - 5, 315], fill=INK)
    d.rectangle([5, 269, LW - 6, 314], outline=WHITE)
    d.rectangle([7, 271, LW - 8, 312], outline=(90, 80, 120))
    left = len(shown)
    for k, ln in enumerate(lines[:3]):
        if left <= 0: break
        part = ln[:left]; left -= len(ln) + 1
        text(d, part, 12, 276 + k * 12, WHITE, shadow=False)
    if n > len(msg) and int(t * 3) % 2:
        d.polygon([(LW - 18, 306), (LW - 12, 306), (LW - 15, 309)], fill=WHITE)
    return im.resize((W, H), Image.NEAREST)

proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                         "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264",
                         "-preset", "veryfast", "-crf", "16", "-pix_fmt", "yuv420p", OUT], stdin=subprocess.PIPE)
CHECK = [15, 55, 80, 175, 270, 370, 470, 570, 660]
for i in range(N):
    fr = frame(i / FPS)
    proc.stdin.write(fr.tobytes())
    if i in CHECK: fr.save(f"/home/claude/dime-money-quest/studio/arc_{i:03d}.png")
proc.stdin.close(); proc.wait()

# ---------------- chiptune audio ----------------
SR = 44100
audio = np.zeros(int(SR * DUR))
def add(t0, sig):
    i = int(t0 * SR); n = min(len(sig), len(audio) - i)
    if n > 0: audio[i:i + n] += sig[:n]
def sq(freq, dur, vol=0.1, duty=0.5, decay=0.0):
    tt = np.arange(int(SR * dur)) / SR
    f = np.atleast_1d(freq)
    if f.size == 1: ph = (tt * f[0]) % 1.0
    else: ph = np.cumsum(np.interp(np.linspace(0, 1, len(tt)), np.linspace(0, 1, f.size), f)) / SR % 1.0
    return vol * np.where(ph < duty, 1.0, -1.0) * np.exp(-decay * tt)
def coin_sfx(): return np.concatenate([sq(988, 0.06, 0.08), sq(1319, 0.18, 0.08, decay=10)])
def jump_sfx(): return sq(np.array([300, 700]), 0.18, 0.07, 0.25, 6)
def bump_sfx(): return sq(np.array([180, 90]), 0.1, 0.12, 0.5, 20)
def lose_sfx(): return sq(np.array([700, 200]), 0.25, 0.06, 0.25, 6)
# music: bass + arp loop at 132 bpm
beat = 60 / 132
prog_notes = [(110.0, [440, 523, 659]), (87.31, [349, 440, 523]), (130.81, [523, 659, 784]), (98.0, [392, 494, 587])]
tm = 0.0; bar = 0
while tm < END:
    root, arp = prog_notes[bar % 4]
    if bar >= 6: root, arp = root * 0.94, arp  # tension later in the month
    for b in range(4):
        add(tm + b * beat, sq(root, beat * 0.45, 0.05, 0.5, 4))
        for k in range(2):
            add(tm + b * beat + k * beat / 2, sq(arp[(b * 2 + k) % 3], beat * 0.25, 0.022, 0.25, 8))
    tm += 4 * beat; bar += 1
add(1.3, jump_sfx()); add(HIT, bump_sfx())
for k in range(10): add(HIT + 0.05 + k * 0.09, coin_sfx())
for i in range(1, 6):
    add(ARR[i] - JUMP, jump_sfx())
    add(ARR[i], bump_sfx() * 0.6)
    if AMOUNTS[i] < 0:
        for k in range(10): add(ARR[i] + 0.3 + k * 0.08, lose_sfx() * 0.6)
# typewriter blips
for (t0, msg) in DIALOG:
    for k, ch in enumerate(msg):
        if ch != " " and k % 2 == 0: add(t0 + k / 32, sq(1600, 0.02, 0.02, 0.5, 60))
# low funds alarm + game over jingle
for k in range(4): add(ARR[5] + 0.4 + k * 0.5, sq(880, 0.12, 0.05, 0.5, 4))
for k, f in enumerate([523, 494, 466, 440, 415]): add(END + 0.1 + k * 0.18, sq(f, 0.2, 0.06, 0.5, 5))
add(END + 1.0, sq(np.array([523, 1046]), 0.3, 0.05, 0.25, 3))
audio = np.clip(audio, -0.95, 0.95)
with wave.open("/home/claude/dime-money-quest/studio/arcade_sfx.wav", "wb") as wf:
    wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR)
    wf.writeframes((audio * 32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", OUT, "-i", "/home/claude/dime-money-quest/studio/arcade_sfx.wav",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest", "/home/claude/dime-money-quest/studio/ep1_arcade.mp4"])
print("done")
