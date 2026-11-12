import math, random, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw

# reuse the arcade + Dime helpers (everything above render_guy's frame function)
src = open("/home/claude/dime-money-quest/studio/render_guy.py").read().split("\ndef frame(t):")[0]
exec(src)

import sys
CTA_MODE = sys.argv[1] if len(sys.argv) > 1 else 'comment'
DUR = 19.5
N = int(FPS * DUR)
OUT = "/home/claude/dime-money-quest/studio/ep002_silent.mp4"
HITS = [0.06, 0.56, 1.06]
T_BOX, T_GRAB, T_WHACK, T_PAY, T_CTA = 6.3, 8.0, 8.6, 10.6, 14.0
BAG_HOME = 128

DIALOG = [(1.5, "4 SUBSCRIPTIONS AT €9.99 EACH..."),
          (3.6, "...IS €480 A YEAR. GONE."),
          (T_BOX, "TIP: CANCEL ANY YOU HAVEN'T OPENED IN 30 DAYS"),
          (T_PAY, "CUT 2 OF 4: +€20 A MONTH. +€240 A YEAR.")]

def mood_at(t):
    if t < 1.6: return "shock"
    if t < T_WHACK + 0.2: return "sad"
    return "happy"

def knock(t):
    k = 0.0
    for h in HITS:
        d = t - h
        if 0 <= d < 0.4: k = max(k, 9 * (1 - d / 0.4))
    return k

def guy_state(t):
    feet = GROUND_Y
    x = GUY_X - int(knock(t))
    for (j0, jd, hgt) in ((T_GRAB - 0.45, 0.5, 22), (T_PAY + 0.2, 0.35, 14), (T_PAY + 0.7, 0.35, 14)):
        if j0 <= t < j0 + jd:
            p = (t - j0) / jd
            return x, feet, None, int(hgt * 4 * p * (1 - p)), "up", 1.0
    arms = "down"
    if T_GRAB <= t < T_WHACK + 0.5: arms = "up"
    if mood_at(t) == "happy" and t > T_PAY: arms = "up" if int(t * 4) % 2 else "down"
    if t >= T_CTA + 0.4: arms = "wave"
    return x, feet, None, 0, arms, 1.0

def bag_scale(t):
    return 1.0 - 0.45 * ease_out(prog(t, T_WHACK, T_WHACK + 0.5))

def bag_x(t):
    x = BAG_HOME
    for h in HITS:
        d = t - (h - 0.12)
        if 0 <= d < 0.36:   # lunge in, bite, back off
            x -= int(30 * math.sin(math.pi * d / 0.36))
    d = t - T_WHACK
    if 0 <= d < 0.6: x += int(20 * math.sin(math.pi * d / 0.6))
    return x

MCOLS = [BLUE, RED, GREEN, PURPLE]
MXS = [100, 120, 140, 160]
CUT = (1, 3)

def mon_x(t, k):
    x = MXS[k]
    if k < 3:
        h = HITS[k]; d = t - (h - 0.12)
        if 0 <= d < 0.36: x -= int(26 * math.sin(math.pi * d / 0.36))
    return x

def big_monster(d, cx, by, col, s, t, k, attacking):
    w = int(20 * s); h = int(20 * s)
    bob = int(abs(math.sin(t * 8 + k)) * 3)
    y0 = by - h - bob
    x0 = cx - w // 2
    d.rectangle([x0 - 1, y0 - 1, x0 + w + 1, y0 + h + 1], fill=INK)
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=col)
    d.rectangle([x0, y0, x0 + w, y0 + max(1, h // 8)], fill=mixc(col, WHITE, 0.45))
    d.rectangle([x0 + w - max(2, w // 6), y0, x0 + w, y0 + h], fill=mixc(col, INK, 0.3))
    for sgn in (-1, 1):
        ex = cx + sgn * max(3, w // 4)
        d.rectangle([ex - 2, y0 + h // 4, ex + 1, y0 + h // 4 + 3], fill=WHITE)
        d.point((ex - 1, y0 + h // 4 + 2), fill=INK); d.point((ex, y0 + h // 4 + 2), fill=INK)
        d.line([ex - 3 * sgn, y0 + h // 4 - 3, ex + 1 * sgn, y0 + h // 4 - 1], fill=INK)
    mh = 3 + (4 if attacking else 0)
    my = y0 + int(h * 0.58)
    d.rectangle([cx - w // 3, my, cx + w // 3, my + mh], fill=INK)
    for q in range(-w // 3 + 1, w // 3, 3):
        d.rectangle([cx + q, my, cx + q + 1, my + 1], fill=WHITE)
        d.rectangle([cx + q + 1, my + mh - 1, cx + q + 2, my + mh], fill=WHITE)
    d.text((cx - 9, y0 - 10), "9.99", font=FONT, fill=WHITE) if False else None
    return y0

def draw_bag(d, t):
    top = GROUND_Y
    for k in range(4):
        cx = mon_x(t, k)
        if k in CUT and t >= T_WHACK:
            pp = prog(t, T_WHACK, T_WHACK + 0.45)
            if pp < 1:
                r = int(3 + pp * 10)
                for a in range(8):
                    ang = a * math.pi / 4
                    d.rectangle([cx + int(math.cos(ang) * r) - 1, GROUND_Y - 12 + int(math.sin(ang) * r) - 1,
                                 cx + int(math.cos(ang) * r) + 1, GROUND_Y - 12 + int(math.sin(ang) * r) + 1], fill=WHITE)
            continue
        s = 1.0 - (0.3 * ease_out(prog(t, T_WHACK, T_WHACK + 0.5)) if t > T_WHACK else 0)
        attacking = k < 3 and 0 <= t - (HITS[k] - 0.12) < 0.36
        y0 = big_monster(d, cx, GROUND_Y, MCOLS[k], s, t, k, attacking)
        top = min(top, y0)
        if t > T_WHACK:
            for q in range(2):
                a = t * 6 + q * 3.1 + k
                d.point((cx + int(math.cos(a) * 7), y0 - 4 + int(math.sin(a) * 2)), fill=GOLD_L)
    return 120, top

def frame(t):
    top, bot = sky_colors(5)
    im = Image.new("RGB", (LW, LH), top)
    d = ImageDraw.Draw(im); d.fontmode = "1"
    for y in range(34, GROUND_Y):
        d.line([0, y, LW, y], fill=mixc(top, bot, (y - 34) / (GROUND_Y - 34)))
    for (sx, sy) in STARS[:30]:
        if int(t * 3 + sx) % 6: d.point((sx % LW, sy), fill=(255, 255, 220))
    if t >= 1.5: d.ellipse([132, 60, 152, 80], fill=(255, 190, 120))
    for (hx, hh) in HILLS[:6]:
        x = int(hx * 0.6)
        d.ellipse([x - 50, GROUND_Y - hh - 30, x + 50, GROUND_Y + 40], fill=mixc(bot, (40, 90, 80), 0.5))
    for (bx, bw, bh, wins) in BUILD[:14]:
        d.rectangle([bx, GROUND_Y - bh, bx + bw, GROUND_Y], fill=(55, 50, 95))
        for (wx, wy) in wins: d.point((bx + wx, GROUND_Y - bh + wy), fill=(255, 210, 90))
    for tx in range(0, LW + 12, 12):
        d.rectangle([tx, GROUND_Y, tx + 11, GROUND_Y + 6], fill=GREEN); d.line([tx, GROUND_Y, tx + 11, GROUND_Y], fill=(160, 255, 180))
        d.rectangle([tx, GROUND_Y + 7, tx + 11, LH], fill=(120, 74, 44)); d.point((tx + 3, GROUND_Y + 11), fill=(150, 100, 60))

    bx, by0 = draw_bag(d, t)
    # boss nameplate + HP
    hp = 1.0 - 0.5 * ease_out(prog(t, T_WHACK, T_WHACK + 0.5))
    text(d, "SUBSCRIPTIONS", bx, by0 - 22, RED, center=True)
    d.rectangle([bx - 34, by0 - 11, bx + 34, by0 - 7], fill=INK)
    d.rectangle([bx - 33, by0 - 10, bx - 33 + int(66 * hp), by0 - 8], fill=RED)

    # coins knocked out of Dime on each hit
    for i, h in enumerate(HITS):
        for k in range(6):
            p = prog(t, h + k * 0.02, h + 0.55 + k * 0.02)
            if 0 < p < 1:
                ang = -2.2 + k * 0.45
                px = GUY_X - 6 + int(math.cos(ang) * 40 * p); py = GROUND_Y - 50 - int(46 * math.sin(math.pi * p * 0.8)) + int(30 * p * p)
                coin_sprite(d, px, py, 3, t * 14 + k)
    # coins coming back after the whack
    for k in range(10):
        p = prog(t, T_WHACK + 0.2 + k * 0.07, T_WHACK + 0.8 + k * 0.07)
        if 0 < p < 1:
            coin_sprite(d, int(lerp(bx, GUY_X, p)), int(lerp(GROUND_Y - 20, GROUND_Y - 50, p) - 26 * math.sin(math.pi * p)), 3, t * 12 + k)
    # power-up box with frying pan
    if t >= T_BOX:
        drop = ease_out(prog(t, T_BOX, T_BOX + 0.5))
        qx, qy = GUY_X, int(lerp(20, 140, drop))
        qy -= int(4 * math.sin(math.pi * prog(t, T_GRAB, T_GRAB + 0.15)))
        if t < T_GRAB + 0.15:
            d.rectangle([qx - 8, qy - 8, qx + 8, qy + 8], fill=INK)
            d.rectangle([qx - 7, qy - 7, qx + 7, qy + 7], fill=GREEN)
            d.rectangle([qx - 7, qy - 7, qx + 7, qy - 7], fill=(180, 255, 200))
            text(d, "!", qx - 3, qy - 4, WHITE if int(t * 4) % 2 else INK, shadow=False)
        else:
            pp = prog(t, T_GRAB, T_GRAB + 0.5)
            if pp < 1:
                for a in range(12):
                    ang = a * math.pi / 6; r = int(4 + pp * 24)
                    d.rectangle([qx + int(math.cos(ang) * r) - 1, qy + int(math.sin(ang) * r) - 1, qx + int(math.cos(ang) * r) + 1, qy + int(math.sin(ang) * r) + 1], fill=GOLD_L if a % 2 else GREEN)

    # Dime (blinks while hurt), drawn 2x
    hurt_blink = any(0 <= t - h < 0.45 for h in HITS) and int(t * 20) % 2 == 0
    layer = Image.new("RGBA", (LW, LH), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    gx, ghcy = guy(ld, t)
    # scissors in the raised hand
    if T_GRAB + 0.15 <= t < T_PAY:
        snip = int(t * 10) % 2 if T_WHACK - 0.1 <= t < T_WHACK + 0.5 else 0
        hxp, hyp = gx + 10, GROUND_Y - 19 - 7
        ang = -0.9 if t < T_WHACK - 0.1 else 0.1
        ex, ey = hxp + int(math.cos(ang) * 10), hyp + int(math.sin(ang) * 10)
        for sg in (-1, 1):
            spread = (3 if snip else 1) * sg
            ld.line([hxp, hyp, ex + int(-math.sin(ang) * spread), ey + int(math.cos(ang) * spread)], fill=(210, 215, 230), width=2)
        ld.ellipse([hxp - 4, hyp - 1, hxp - 1, hyp + 2], outline=RED)
        ld.ellipse([hxp - 1, hyp + 1, hxp + 2, hyp + 4], outline=RED)
    if hurt_blink:
        layer = Image.eval(layer, lambda v: v)  # keep, but tint red below
        r, g, b, a = layer.split()
        layer = Image.merge("RGBA", (r.point(lambda v: min(255, v + 120)), g.point(lambda v: v // 2), b.point(lambda v: v // 2), a))
    fx, fy = GUY_X, GROUND_Y + 1
    spr = layer.crop((fx - 30, fy - 90, fx + 30, fy)).resize((120, 180), Image.NEAREST)
    im.paste(spr, (fx - 60, fy - 180), spr)
    d = ImageDraw.Draw(im); d.fontmode = "1"
    hx = fx + (gx - fx) * 2; hcy = fy - (fy - ghcy) * 2

    # damage numbers, combo, KO
    for i, h in enumerate(HITS):
        p = prog(t, h, h + 0.9)
        if 0 < p < 1:
            text(d, "-€9.99", hx - 18 + i * 6, hcy - 40 - int(20 * p), RED)
    if 1.06 <= t < 2.4 and int(t * 8) % 4:
        text(d, "x3 COMBO!", 128, 150, GOLD, center=True)
    if T_WHACK <= t < T_WHACK + 1.4:
        p = prog(t, T_WHACK, T_WHACK + 0.15)
        text(d, "SNIP!", bx, 150 - int(6 * p), WHITE, font=FONT_BIG, center=True)
    # big yearly cost / payoff
    if 3.8 <= t < T_BOX:
        if prog(t, 3.8, 3.9) >= 1 and (t > 4.3 or int(t * 10) % 2):
            text(d, "-€480", 90, 100, RED, font=FONT_BIG, center=True)
            text(d, "EVERY YEAR", 90, 122, WHITE, center=True)
    if T_PAY + 0.2 <= t < T_CTA:
        text(d, "+€240", 118, 96, GOLD, font=FONT_BIG, center=True)
        text(d, "A YEAR", 118, 118, WHITE, center=True)
    if t >= 3.8:
        text(d, "EXAMPLE NUMBERS", 90, 256 + 0, (200, 200, 210), shadow=True, center=True) if False else None

    # HUD: wallet HP
    d.rectangle([0, 0, LW, 33], fill=INK)
    whp = 1.0 - 0.13 * sum(ease_out(prog(t, h, h + 0.3)) for h in HITS) + 0.39 * ease_out(prog(t, T_WHACK + 0.2, T_WHACK + 1.2))
    whp = clamp(whp)
    coin_sprite(d, 9, 9, 4, t * 4)
    text(d, "WALLET", 18, 6, GOLD)
    m = mood_at(t)
    text(d, {"happy": "MOOD :)", "sad": "MOOD :(", "shock": "MOOD :O"}[m], 112, 6, (150, 255, 180) if m == "happy" else RED)
    bc = GREEN if whp > 0.7 else (GOLD if whp > 0.5 else RED)
    d.rectangle([6, 20, 173, 28], fill=(60, 50, 80))
    d.rectangle([7, 21, 7 + int(165 * whp), 27], fill=bc); d.line([7, 21, 7 + int(165 * whp), 21], fill=mixc(bc, WHITE, 0.5))
    if t >= 3.6:
        text(d, "EXAMPLE NUMBERS", 90, 38, (210, 210, 225), center=True)

    # hook title slams in immediately
    if t < 1.5:
        for k, ln in enumerate(["YOUR APPS", "ARE EATING", "YOUR MONEY"]):
            st = 0.0 + k * 0.1
            if t >= st:
                dx = int((1 - prog(t, st, st + 0.08)) * 40) * (1 if k % 2 else -1)
                text(d, ln, 90 + dx, 62 + k * 22, RED if k == 1 else WHITE, font=FONT_BIG, center=True)

    # end card
    if t >= T_CTA:
        p = prog(t, T_CTA, T_CTA + 0.3)
        im = Image.blend(im, Image.new("RGB", (LW, LH), INK), 0.94 * p)
        d = ImageDraw.Draw(im); d.fontmode = "1"
        if p >= 1:
            # big Dime head, 3x, bouncing
            hl = Image.new("RGBA", (40, 40), (0, 0, 0, 0)); hd = ImageDraw.Draw(hl)
            head(hd, 20, 20, "happy", t)
            hl = hl.resize((120, 120), Image.NEAREST)
            bounce = int(abs(math.sin(t * 5)) * 6)
            im.paste(hl, (-6, 150 - bounce), hl)
            d = ImageDraw.Draw(im); d.fontmode = "1"
            if CTA_MODE == "comment":
                text(d, "COMMENT", 90, 58, WHITE, font=FONT_BIG, center=True)
                pop = int(prog(t, T_CTA + 0.3, T_CTA + 0.45) * 1)
                if pop:
                    col = GOLD if int(t * 4) % 2 else (255, 240, 140)
                    text(d, '"SCAN"', 90, 84, col, font=FONT_BIG, center=True)
                if t > T_CTA + 0.6:
                    text(d, "TO GET THE FREE", 90, 116, (150, 255, 180), center=True)
                    text(d, "LEAK SCANNER", 90, 128, (150, 255, 180), center=True)
                # the item: a pixel sheet with a check
                ix, iy = 150, 196 - bounce
                d.rectangle([ix - 15, iy - 19, ix + 15, iy + 19], fill=INK)
                d.rectangle([ix - 14, iy - 18, ix + 14, iy + 18], fill=WHITE)
                d.rectangle([ix - 14, iy - 18, ix + 14, iy - 12], fill=GREEN)
                for k in range(4):
                    d.rectangle([ix - 10, iy - 7 + k * 6, ix + 4 - (k % 2) * 6, iy - 6 + k * 6], fill=(150, 150, 170))
                    d.rectangle([ix + 7, iy - 8 + k * 6, ix + 9, iy - 6 + k * 6], fill=GREEN if k < 3 else RED)
                for k in range(8):
                    a = t * 3 + k * 0.8
                    if int(t * 8 + k) % 2: d.point((ix + int(math.cos(a) * 24), iy + int(math.sin(a) * 26)), fill=GOLD_L)
                # comment bubble + arrow
                if int(t * 3) % 2 or t < T_CTA + 1.0:
                    d.rectangle([128, 244, 168, 264], fill=WHITE)
                    d.polygon([(136, 264), (144, 264), (136, 271)], fill=WHITE)
                    for k in range(3): d.rectangle([138 + k * 9, 253, 140 + k * 9, 255], fill=INK)
                    d.polygon([(124, 248), (124, 260), (116, 254)], fill=GOLD)
            else:
                text(d, "FOLLOW", 90, 58, WHITE, font=FONT_BIG, center=True)
                if t > T_CTA + 0.3:
                    text(d, "FOR PART 2", 90, 84, GOLD if int(t * 4) % 2 else (255, 240, 140), font=FONT_BIG, center=True)
                if t > T_CTA + 0.6:
                    text(d, "NEXT LEVEL:", 90, 116, (150, 255, 180), center=True)
                    text(d, "THE LEAK GANG", 90, 128, WHITE, center=True)
                bx0 = 142 + int(math.sin(t * 6) * 2)
                d.rectangle([bx0 - 30, 200, bx0 + 30, 220], fill=INK)
                d.rectangle([bx0 - 29, 201, bx0 + 29, 219], fill=(90, 110, 230))
                d.rectangle([bx0 - 29, 201, bx0 + 29, 202], fill=(160, 175, 255))
                text(d, "+FOLLOW", bx0 - 26, 207, WHITE, shadow=False)
                # little monster silhouette teaser
                for k in range(3):
                    mx = 134 + k * 14; my = 262
                    d.rectangle([mx - 5, my - 5, mx + 5, my + 5], fill=(70, 60, 100))
                    d.point((mx - 2, my - 1), fill=RED); d.point((mx + 2, my - 1), fill=RED)
            if t > T_CTA + 1.2 and int(t * 2) % 2:
                text(d, "@DIMESMONEYQUEST", 90, 292, (200, 200, 220), center=True)
    # dialog
    if DIALOG[0][0] <= t < T_CTA:
        cur = max(k for k in range(len(DIALOG)) if t >= DIALOG[k][0])
        t0, msg = DIALOG[cur]
        n = int((t - t0) * 34)
        lines = wrap(msg, 20)
        d.rectangle([4, 268, LW - 5, 315], fill=INK); d.rectangle([5, 269, LW - 6, 314], outline=WHITE)
        d.rectangle([7, 271, LW - 8, 312], outline=(90, 80, 120))
        left = n
        for k, ln in enumerate(lines[:3]):
            if left <= 0: break
            text(d, ln[:left], 12, 276 + k * 12, WHITE, shadow=False); left -= len(ln) + 1

    # screen shake + red flash on hits, white flash on the whack
    out = im
    sh = 0
    for h in HITS + [T_WHACK]:
        dd = t - h
        if 0 <= dd < 0.18: sh = int(3 * math.sin(dd * 120))
    if sh:
        out = Image.new("RGB", (LW, LH), INK); out.paste(im, (sh, -sh // 2))
    for h in HITS:
        if 0 <= t - h < 0.07: out = Image.blend(out, Image.new("RGB", (LW, LH), (255, 40, 60)), 0.35)
    if 0 <= t - T_WHACK < 0.06: out = Image.blend(out, Image.new("RGB", (LW, LH), WHITE), 0.5)
    if t > DUR - 0.2: out = Image.blend(out, Image.new("RGB", (LW, LH), INK), prog(t, DUR - 0.2, DUR) * 0.6)
    return out.resize((W, H), Image.NEAREST)

proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                         "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264",
                         "-preset", "veryfast", "-crf", "16", "-pix_fmt", "yuv420p", OUT], stdin=subprocess.PIPE)
CHECK = [0, 20, 40, 120, 200, 262, 270, 330, 450, 570]
for i in range(N):
    fr = frame(i / FPS)
    proc.stdin.write(fr.tobytes())
    if i in CHECK: fr.save(f"/home/claude/dime-money-quest/studio/sb_{i:03d}.png")
proc.stdin.close(); proc.wait()

# ---------- audio ----------
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
def noise(dur, vol, decay):
    n = int(SR * dur); rng = np.random.default_rng(int(dur * 1000))
    return vol * rng.uniform(-1, 1, n) * np.exp(-decay * np.arange(n) / SR)
coin = lambda: np.concatenate([sqw(988, 0.06, 0.07), sqw(1319, 0.16, 0.07, decay=10)])
hit = lambda: noise(0.15, 0.35, 30) + sqw(np.array([220, 70]), 0.15, 0.12, 0.5, 12)
beat = 60 / 140
def loop(t0, t1, notes, root, vol=0.045):
    tm = t0; k = 0
    while tm < t1:
        add(tm, sqw(root, beat * 0.4, vol, 0.5, 4))
        add(tm + beat / 2, sqw(notes[k % len(notes)], beat * 0.22, vol * 0.45, 0.25, 8))
        tm += beat; k += 1
loop(0.0, 3.6, [311, 294, 311, 370], 98, 0.05)          # tense battle loop
loop(3.6, T_GRAB, [440, 415, 392, 370], 110)           # sad
loop(T_WHACK, DUR - 0.3, [659, 784, 1046, 784], 165)   # victory
for h in HITS:
    add(h, hit())
    for k in range(4): add(h + 0.05 + k * 0.04, sqw(np.array([900, 400]), 0.08, 0.04, 0.25, 12))
add(3.8, sqw(np.array([392, 196]), 0.7, 0.07, 0.5, 2))
add(T_BOX + 0.5, sqw(np.array([500, 900]), 0.12, 0.05, 0.5, 8))
add(T_GRAB - 0.45, sqw(np.array([300, 800]), 0.2, 0.06, 0.25, 6))
for k, f in enumerate([523, 659, 784, 1046]): add(T_GRAB + k * 0.06, sqw(f, 0.1, 0.05, 0.25, 8))
add(T_WHACK, noise(0.25, 0.3, 40) + sqw(np.array([1200, 600]), 0.25, 0.1, 0.5, 6))
for k in range(10): add(T_WHACK + 0.2 + k * 0.07, coin())
for (t0, msg) in DIALOG:
    for k, ch in enumerate(msg):
        if ch != " " and k % 2 == 0: add(t0 + k / 34, sqw(1600, 0.02, 0.015, 0.5, 60))
audio = np.clip(audio, -0.95, 0.95)
with wave.open("/home/claude/dime-money-quest/studio/ep002_sfx.wav", "wb") as wf:
    wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR)
    wf.writeframes((audio * 32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", OUT, "-i", "/home/claude/dime-money-quest/studio/ep002_sfx.wav",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest", "/home/claude/dime-money-quest/studio/ep002_subscriptions.mp4"])
print("done")
