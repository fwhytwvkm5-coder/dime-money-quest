import math, random, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw

# reuse helpers from the arcade renderer (everything above its frame function)
src = open("/home/claude/dime-money-quest/studio/render_arcade.py").read().split("def frame(t):")[0]
exec(src)

DUR = 13.0
N = int(FPS * DUR)
OUT = "/home/claude/dime-money-quest/studio/guy_silent.mp4"
SHIRT = (60, 200, 190); SHIRT_D = (30, 130, 130); PANTS = (90, 110, 230); SHOE = (240, 240, 250)
GUY_X = 62
T_PAY, T_MON, T_BOX, T_HIT, T_END = 0.9, 1.9, 5.0, 6.7, 10.6

DIALOG = [(0.0, "THIS IS YOU. PAYDAY JUST HIT!"),
          (2.0, "5 SUBSCRIPTIONS YOU NEVER USE: -€62/MONTH"),
          (T_BOX, "TIP: CANCEL ANY YOU HAVEN'T OPENED IN 30 DAYS"),
          (8.4, "+€62 A MONTH = +€744 A YEAR"),
          (T_END, "BAD HABIT, SAD COIN. GOOD HABIT, HAPPY COIN.")]

def mood_at(t):
    if t < 2.4: return "happy"
    if t < 3.0: return "shock"
    if t < T_HIT + 0.3: return "sad"
    return "happy"

def balance_g(t):
    b = 2000 * ease_out(prog(t, T_PAY, T_PAY + 0.8))
    b -= 62 * ease_out(prog(t, 2.4, 3.8))
    b += 62 * ease_out(prog(t, 7.1, 7.9))
    return int(round(b))

def guy_state(t):
    """screen x, feet y, walk phase (or None), jump offset, arms ('up'|'down'|'wave'), squash"""
    feet = GROUND_Y
    if t < 0.8:
        x = lerp(-20, GUY_X, ease_out(prog(t, 0, 0.8)))
        return x, feet, t * 10, 0, "down", 1.0
    jumps = [(0.95, 0.4, 22), (T_HIT - 0.35, 0.55, 22), (7.4, 0.35, 16), (7.9, 0.35, 16), (8.6, 0.35, 12)]
    for (j0, jd, hgt) in jumps:
        if j0 <= t < j0 + jd:
            p = (t - j0) / jd
            return GUY_X, feet, None, int(hgt * 4 * p * (1 - p)), "up", 1.0
    arms = "down"
    if mood_at(t) == "happy": arms = "up" if int(t * 4) % 2 else "down"
    if t >= T_END + 0.5: arms = "wave"
    return GUY_X, feet, None, 0, arms, 1.0

def head(d, cx, cy, mood, t):
    R = 10
    d.ellipse([cx - R - 1, cy - R - 1, cx + R + 1, cy + R + 1], fill=INK)
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=GOLD)
    d.ellipse([cx - R + 2, cy - R + 2, cx + R - 2, cy + R - 2], outline=GOLD_D)
    d.rectangle([cx + R - 1, cy - 3, cx + R, cy + R - 4], fill=GOLD_D)
    d.rectangle([cx - R + 3, cy - R + 2, cx - R + 4, cy - R + 3], fill=GOLD_L)
    ey = cy - 2
    blink = (t % 2.6) < 0.1
    if mood == "happy":
        for s in (-1, 1):
            d.point((cx + s * 4 - 1, ey), fill=INK); d.point((cx + s * 4, ey - 1), fill=INK); d.point((cx + s * 4 + 1, ey), fill=INK)
        d.line([cx - 3, cy + 4, cx + 3, cy + 4], fill=INK); d.point((cx - 4, cy + 3), fill=INK); d.point((cx + 4, cy + 3), fill=INK)
        d.line([cx - 2, cy + 5, cx + 2, cy + 5], fill=RED)
    elif mood == "sad":
        for s in (-1, 1):
            d.rectangle([cx + s * 4 - 1, ey, cx + s * 4, ey + 1], fill=INK)
            d.line([cx + s * 4 - 2 * s, ey - 3, cx + s * 4 + s, ey - 2], fill=INK)  # worried brows
        d.line([cx - 2, cy + 4, cx + 2, cy + 4], fill=INK); d.point((cx - 3, cy + 5), fill=INK); d.point((cx + 3, cy + 5), fill=INK)
        if int(t * 3) % 2: d.rectangle([cx - 5, ey + 3, cx - 5, ey + 5], fill=(140, 200, 255))
    elif mood == "shock":
        for s in (-1, 1): d.rectangle([cx + s * 4 - 1, ey - 2, cx + s * 4, ey + 1], fill=INK)
        d.rectangle([cx - 1, cy + 3, cx + 1, cy + 6], fill=INK)
    else:
        for s in (-1, 1):
            if blink: d.line([cx + s * 4 - 1, ey, cx + s * 4, ey], fill=INK)
            else: d.rectangle([cx + s * 4 - 1, ey - 1, cx + s * 4, ey + 1], fill=INK)
        d.line([cx - 2, cy + 4, cx + 2, cy + 4], fill=INK)
    d.point((cx - 7, cy + 2), fill=(255, 140, 120)); d.point((cx + 6, cy + 2), fill=(255, 140, 120))

def guy(d, t):
    x, feet, walk, jump, arms, sq = guy_state(t)
    x = int(x); feet = int(feet) - jump
    mood = mood_at(t)
    slump = 1 if mood == "sad" else 0
    # legs
    if walk is not None:
        a = int(math.sin(walk) * 2)
        legs = [(x - 3 + a, x - 2 + a), (x + 2 - a, x + 3 - a)]
    elif jump > 0:
        legs = [(x - 4, x - 3), (x + 3, x + 4)]
    else:
        legs = [(x - 3, x - 2), (x + 2, x + 3)]
    for (l0, l1) in legs:
        d.rectangle([l0 - 1, feet - 9, l1 + 1, feet - 2], fill=INK)
        d.rectangle([l0, feet - 8, l1, feet - 2], fill=PANTS)
        d.rectangle([l0 - 1, feet - 2, l1 + 1, feet], fill=INK)
        d.rectangle([l0 - 1, feet - 2, l1 + 1, feet - 1], fill=SHOE)
    # torso
    ty0 = feet - 19 + slump
    d.rectangle([x - 6, ty0, x + 6, feet - 8], fill=INK)
    d.rectangle([x - 5, ty0 + 1, x + 5, feet - 9], fill=SHIRT)
    d.rectangle([x + 3, ty0 + 1, x + 5, feet - 9], fill=SHIRT_D)
    d.rectangle([x - 2, ty0 + 4, x + 1, ty0 + 7], fill=GOLD)  # little € badge
    # arms
    sh = ty0 + 2
    if arms == "up":
        hands = [(x - 10, sh - 7), (x + 10, sh - 7)]
    elif arms == "wave":
        w = int(math.sin(t * 14) * 3)
        hands = [(x - 9, sh + 8), (x + 10 + w, sh - 8)]
    elif mood == "sad":
        hands = [(x - 7, sh + 11), (x + 7, sh + 11)]
    else:
        hands = [(x - 9, sh + 8), (x + 9, sh + 8)]
    for s, (hx, hy) in zip((-1, 1), hands):
        d.line([x + s * 6, sh, hx, hy], fill=INK, width=3)
        d.line([x + s * 6, sh, hx, hy], fill=SHIRT, width=1)
        d.rectangle([hx - 1, hy - 1, hx + 1, hy + 1], fill=GOLD)
    # head
    hcy = ty0 - 10 + slump
    head(d, x, hcy, mood, t)
    # rain cloud when sad
    if mood == "sad" and t > 3.1:
        cy = hcy - 24
        for (ox, r) in ((-6, 5), (0, 7), (7, 5)):
            d.ellipse([x + ox - r, cy - r, x + ox + r, cy + r], fill=(120, 125, 150))
        d.rectangle([x - 11, cy, x + 12, cy + 4], fill=(120, 125, 150))
        for k in range(4):
            ry = cy + 6 + int((t * 40 + k * 7) % 12)
            d.line([x - 8 + k * 5, ry, x - 8 + k * 5, ry + 2], fill=(140, 200, 255))
    # sparkles when happy after the tip
    if mood == "happy" and t > T_HIT:
        for k in range(6):
            a = t * 3 + k * 1.05
            px = x + int(math.cos(a) * 18); py = hcy + int(math.sin(a) * 14)
            if int(t * 8 + k) % 2:
                d.point((px, py), fill=WHITE); d.point((px - 1, py), fill=GOLD_L); d.point((px + 1, py), fill=GOLD_L)
                d.point((px, py - 1), fill=GOLD_L); d.point((px, py + 1), fill=GOLD_L)
    return x, hcy

MON = [(118, 238), (136, 216), (156, 238), (170, 212), (146, 192)]
MCOL = [BLUE, RED, GREEN, PURPLE, ORANGE]

def frame(t):
    top, bot = sky_colors(5)
    im = Image.new("RGB", (LW, LH), top)
    d = ImageDraw.Draw(im); d.fontmode = "1"
    for y in range(34, GROUND_Y):
        d.line([0, y, LW, y], fill=mixc(top, bot, (y - 34) / (GROUND_Y - 34)))
    d.ellipse([118, 58, 142, 82], fill=(255, 235, 150))
    for (hx, hh) in HILLS[:6]:
        x = int(hx * 0.6)
        d.ellipse([x - 50, GROUND_Y - hh - 30, x + 50, GROUND_Y + 40], fill=mixc(bot, (40, 90, 80), 0.5))
    for (bx, bw, bh, wins) in BUILD[:14]:
        x = int(bx)
        d.rectangle([x, GROUND_Y - bh, x + bw, GROUND_Y], fill=(60, 70, 110))
        for (wx, wy) in wins: d.point((x + wx, GROUND_Y - bh + wy), fill=(255, 210, 90))
    for tx in range(0, LW + 12, 12):
        d.rectangle([tx, GROUND_Y, tx + 11, GROUND_Y + 6], fill=GREEN); d.line([tx, GROUND_Y, tx + 11, GROUND_Y], fill=(160, 255, 180))
        d.rectangle([tx, GROUND_Y + 7, tx + 11, LH], fill=(120, 74, 44))
        d.point((tx + 3, GROUND_Y + 11), fill=(150, 100, 60))

    # payday coin shower
    for k in range(16):
        p = prog(t, T_PAY + k * 0.04, T_PAY + 0.6 + k * 0.04)
        if 0 < p < 1:
            coin_sprite(d, GUY_X - 14 + (k * 7) % 30, int(lerp(36, 205, p)), 3, t * 12 + k)
    # monsters
    for k, (mx, my) in enumerate(MON):
        ap = prog(t, T_MON + k * 0.08, T_MON + 0.25 + k * 0.08)
        if ap <= 0: continue
        if t < T_HIT + 0.3:
            monster(d, mx, my + int((1 - ap) * 30), MCOL[k], t, k)
        else:
            pp = prog(t, T_HIT + 0.3, T_HIT + 0.7)
            if pp < 1:
                r = int(3 + pp * 8)
                for a in range(8):
                    ang = a * math.pi / 4
                    d.point((mx + int(math.cos(ang) * r), my + int(math.sin(ang) * r)), fill=WHITE)
                d.ellipse([mx - 4 + int(pp * 3), my - 4 + int(pp * 3), mx + 4 - int(pp * 3), my + 4 - int(pp * 3)], fill=(230, 230, 240))
    # coins stolen / returned
    gx, gy = GUY_X, GROUND_Y - 50
    for k in range(10):
        mx, my = MON[k % 5]
        p = prog(t, 2.4 + k * 0.12, 3.0 + k * 0.12)
        if 0 < p < 1:
            coin_sprite(d, int(lerp(gx, mx, p)), int(lerp(gy, my, p) - 20 * math.sin(math.pi * p)), 3, t * 12 + k)
        p2 = prog(t, 7.0 + k * 0.08, 7.6 + k * 0.08)
        if 0 < p2 < 1:
            coin_sprite(d, int(lerp(mx, gx, p2)), int(lerp(my, gy, p2) - 24 * math.sin(math.pi * p2)), 3, t * 12 + k)
    # power-up box
    if t >= T_BOX:
        drop = ease_out(prog(t, T_BOX, T_BOX + 0.5))
        bx, by = GUY_X, int(lerp(20, 140, drop))
        bump = int(4 * math.sin(math.pi * prog(t, T_HIT, T_HIT + 0.15)))
        by -= bump
        used = t >= T_HIT
        if not used or t < T_HIT + 0.2:
            d.rectangle([bx - 8, by - 8, bx + 8, by + 8], fill=INK)
            d.rectangle([bx - 7, by - 7, bx + 7, by + 7], fill=GREEN if not used else (150, 100, 60))
            d.rectangle([bx - 7, by - 7, bx + 7, by - 7], fill=(180, 255, 200))
            if not used: text(d, "!", bx - 3, by - 4, WHITE if int(t * 4) % 2 else INK, shadow=False)
        if used:
            pp = prog(t, T_HIT, T_HIT + 0.6)
            if pp < 1:
                for a in range(12):
                    ang = a * math.pi / 6
                    r = int(4 + pp * 26)
                    d.rectangle([bx + int(math.cos(ang) * r) - 1, by + int(math.sin(ang) * r) - 1,
                                 bx + int(math.cos(ang) * r) + 1, by + int(math.sin(ang) * r) + 1], fill=GOLD_L if a % 2 else GREEN)
    # guy, drawn on its own layer and scaled 2x (chunky sprite), anchored at the feet
    layer = Image.new("RGBA", (LW, LH), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    hx, hcy = guy(ld, t)
    fx, fy = GUY_X, GROUND_Y + 1
    box = (fx - 30, fy - 90, fx + 30, fy)
    spr = layer.crop(box).resize((120, 180), Image.NEAREST)
    im.paste(spr, (fx - 60, fy - 180), spr)
    d = ImageDraw.Draw(im); d.fontmode = "1"
    hx = fx + (hx - fx) * 2; hcy = fy - (fy - hcy) * 2
    # floating amounts
    for (st, s, col) in ((T_PAY + 0.2, "+€2000", GREEN), (2.5, "-€62", RED), (7.2, "+€62", GREEN)):
        p = prog(t, st, st + 1.3)
        if 0 < p < 1: text(d, s, hx - 10, hcy - 36 - int(16 * p), col)
    if 8.4 <= t < T_END:
        p = prog(t, 8.4, 8.8)
        if p > 0:
            text(d, "+€744", 128, 96, GOLD, font=FONT_BIG, center=True)
            text(d, "A YEAR", 128, 118, WHITE, center=True)
    # HUD
    d.rectangle([0, 0, LW, 33], fill=INK)
    bal = balance_g(t)
    coin_sprite(d, 9, 9, 4, t * 4)
    text(d, f"€{max(bal, 0)}", 18, 6, GOLD)
    m = mood_at(t)
    mood_txt = {"happy": "MOOD :)", "sad": "MOOD :(", "shock": "MOOD :O"}.get(m, "MOOD :|")
    text(d, mood_txt, 112, 6, (150, 255, 180) if m == "happy" else RED)
    frac = clamp(bal / 2000)
    d.rectangle([6, 20, 173, 28], fill=(60, 50, 80))
    d.rectangle([7, 21, 7 + int(165 * frac), 27], fill=GREEN); d.line([7, 21, 7 + int(165 * frac), 21], fill=(170, 255, 190))
    # end card
    if t >= T_END + 0.6:
        if int(t * 3) % 2: text(d, "FOLLOW FOR MORE TIPS", 90, 150, (150, 255, 180), center=True)
    # dialog
    cur = max(k for k in range(len(DIALOG)) if t >= DIALOG[k][0])
    t0, msg = DIALOG[cur]
    n = int((t - t0) * 32)
    lines = wrap(msg, 20)
    d.rectangle([4, 268, LW - 5, 315], fill=INK); d.rectangle([5, 269, LW - 6, 314], outline=WHITE)
    d.rectangle([7, 271, LW - 8, 312], outline=(90, 80, 120))
    left = n
    for k, ln in enumerate(lines[:3]):
        if left <= 0: break
        text(d, ln[:left], 12, 276 + k * 12, WHITE, shadow=False); left -= len(ln) + 1
    if n > len(msg) and int(t * 3) % 2: d.polygon([(LW - 18, 306), (LW - 12, 306), (LW - 15, 309)], fill=WHITE)
    if t > DUR - 0.2:
        im = Image.blend(im, Image.new("RGB", (LW, LH), INK), prog(t, DUR - 0.2, DUR) * 0.6)
    return im.resize((W, H), Image.NEAREST)

proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                         "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264",
                         "-preset", "veryfast", "-crf", "16", "-pix_fmt", "yuv420p", OUT], stdin=subprocess.PIPE)
CHECK = [10, 45, 110, 140, 190, 215, 245, 280, 350]
for i in range(N):
    fr = frame(i / FPS)
    proc.stdin.write(fr.tobytes())
    if i in CHECK: fr.save(f"/home/claude/dime-money-quest/studio/guy_{i:03d}.png")
proc.stdin.close(); proc.wait()

# audio
SR = 44100
audio = np.zeros(int(SR * DUR))
def add(t0, sig):
    i = int(t0 * SR); n = min(len(sig), len(audio) - i)
    if n > 0: audio[i:i + n] += sig[:n]
def sqw(freq, dur, vol=0.1, duty=0.5, decay=0.0):
    tt = np.arange(int(SR * dur)) / SR
    f = np.atleast_1d(freq)
    ph = (tt * f[0]) % 1.0 if f.size == 1 else np.cumsum(np.interp(np.linspace(0, 1, len(tt)), np.linspace(0, 1, f.size), f)) / SR % 1.0
    return vol * np.where(ph < duty, 1.0, -1.0) * np.exp(-decay * tt)
coin = lambda: np.concatenate([sqw(988, 0.06, 0.07), sqw(1319, 0.16, 0.07, decay=10)])
beat = 60 / 120
# happy loop first, minor sad loop during the bad part, happy again after the tip
def loop(t0, t1, notes, root):
    tm = t0; k = 0
    while tm < t1:
        add(tm, sqw(root, beat * 0.4, 0.045, 0.5, 4))
        add(tm + beat / 2, sqw(notes[k % len(notes)], beat * 0.22, 0.02, 0.25, 8))
        tm += beat / 2 * 2; k += 1
loop(0, 2.4, [523, 659, 784, 659], 131)
loop(3.0, T_HIT, [440, 415, 392, 370], 110)
loop(T_HIT + 0.3, DUR - 0.3, [659, 784, 1046, 784], 165)
for k in range(12): add(T_PAY + k * 0.05, coin())
add(0.95, sqw(np.array([300, 700]), 0.15, 0.06, 0.25, 6))
for k in range(5): add(T_MON + k * 0.08, sqw(np.array([200, 420]), 0.1, 0.06, 0.5, 10))
for k in range(10): add(2.4 + k * 0.12, sqw(np.array([700, 300]), 0.15, 0.04, 0.25, 8))
add(3.0, sqw(np.array([392, 330]), 0.5, 0.06, 0.5, 2))
add(T_BOX + 0.5, sqw(np.array([500, 900]), 0.12, 0.05, 0.5, 8))
add(T_HIT - 0.35, sqw(np.array([300, 800]), 0.2, 0.06, 0.25, 6))
for k, f in enumerate([523, 659, 784, 1046, 1319]): add(T_HIT + k * 0.07, sqw(f, 0.12, 0.06, 0.25, 6))
for k in range(10): add(7.0 + k * 0.08, coin())
for (t0, msg) in DIALOG:
    for k, ch in enumerate(msg):
        if ch != " " and k % 2 == 0: add(t0 + k / 32, sqw(1600, 0.02, 0.015, 0.5, 60))
audio = np.clip(audio, -0.95, 0.95)
with wave.open("/home/claude/dime-money-quest/studio/guy_sfx.wav", "wb") as wf:
    wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR)
    wf.writeframes((audio * 32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", OUT, "-i", "/home/claude/dime-money-quest/studio/guy_sfx.wav",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest", "/home/claude/dime-money-quest/studio/coinhead_test.mp4"])
print("done")
