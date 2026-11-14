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
OUT = "/home/claude/dime-money-quest/studio/ep003_silent.mp4"
HITS = [0.0, 0.56, 1.06]   # first hit lands on frame 0
T_BOX, T_GRAB, T_WHACK, T_PAY, T_CTA = 6.3, 8.0, 8.6, 10.6, 14.0
BAG_HOME = 128

DIALOG = [(1.5, "RENT €800, CAR €300, FOOD €400 A MONTH..."),
          (3.6, "...€1,500 OF YOUR €2,000 PAY. 75%. GONE."),
          (T_BOX, "TIP: BIG 3 FIRST. TODAY: PLAN THIS WEEK'S MEALS"),
          (T_PAY, "FOOD €400 TO €300: +€100 A MONTH. +€1,200 A YEAR.")]

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

# the Big Three: stone golems with fixed costs carved in
GOLEMS = [("FOOD", 98, 36, (170, 140, 115), 400), ("CAR", 129, 31, (125, 150, 165), 300), ("RENT", 160, 44, (150, 140, 175), 800)]
HIT_BY = [2, 1, 0]          # which golem lands each hit: RENT, CAR, FOOD (matches the dialog order)
WHACKED = 0                 # the map swat shrinks FOOD (the easiest of the three to cut this week)

def gol_x(t, k):
    x = GOLEMS[k][1]
    for i, h in enumerate(HITS):
        if HIT_BY[i] != k: continue
        d = t - (h - 0.12)
        if 0 <= d < 0.36: x = int(lerp(x, 94, math.sin(math.pi * d / 0.36)))   # leap at Dime
    if k == WHACKED:
        d = t - T_WHACK
        if 0 <= d < 0.6: x += int(12 * math.sin(math.pi * d / 0.6))
    return x

def golem(d, cx, by, col, w, h, t, k, attacking):
    bob = int(abs(math.sin(t * 5 + k * 1.3)) * 2)
    y0 = by - h - bob
    x0 = cx - w // 2
    # legs
    for sx in (-1, 1):
        d.rectangle([cx + sx * w // 4 - 4, by - 6, cx + sx * w // 4 + 4, by], fill=INK)
        d.rectangle([cx + sx * w // 4 - 3, by - 6, cx + sx * w // 4 + 3, by - 1], fill=mixc(col, INK, 0.35))
    # body
    d.rectangle([x0 - 1, y0 - 1, x0 + w + 1, by - 5], fill=INK)
    d.rectangle([x0, y0, x0 + w, by - 6], fill=col)
    d.rectangle([x0, y0, x0 + w, y0 + 2], fill=mixc(col, WHITE, 0.4))
    d.rectangle([x0 + w - 3, y0, x0 + w, by - 6], fill=mixc(col, INK, 0.3))
    # cracks
    d.line([x0 + 3, y0 + h // 2, x0 + 7, y0 + h // 2 + 4, x0 + 5, y0 + h // 2 + 8], fill=mixc(col, INK, 0.5))
    d.line([x0 + w - 6, y0 + 4, x0 + w - 9, y0 + 9], fill=mixc(col, INK, 0.5))
    # glowing eyes + angry brows
    ey = y0 + 6
    for sgn in (-1, 1):
        ex = cx + sgn * 5
        d.rectangle([ex - 2, ey, ex + 1, ey + 2], fill=(255, 120, 60) if int(t * 6 + k) % 3 else (255, 210, 80))
        d.line([ex - 3 * sgn, ey - 3, ex + 1 * sgn, ey - 1], fill=INK)
    # mouth
    mh = 2 + (3 if attacking else 0)
    d.rectangle([cx - 5, ey + 6, cx + 5, ey + 6 + mh], fill=INK)
    # fists; the left one punches forward when attacking
    fx = x0 - (9 if attacking else 4)
    d.rectangle([fx - 1, y0 + h // 2 - 4, fx + 6, y0 + h // 2 + 4], fill=INK)
    d.rectangle([fx, y0 + h // 2 - 3, fx + 5, y0 + h // 2 + 3], fill=mixc(col, WHITE, 0.15))
    d.rectangle([x0 + w, y0 + h // 2 - 3, x0 + w + 4, y0 + h // 2 + 3], fill=INK)
    return y0

def gol_hop(t, k):
    for i, h in enumerate(HITS):
        d = t - (h - 0.12)
        if HIT_BY[i] == k and k > 0 and 0 <= d < 0.36: return int(18 * math.sin(math.pi * d / 0.36))
    return 0

def draw_bag(d, t):
    top = GROUND_Y
    tops = []
    order = sorted(range(3), key=lambda k: gol_hop(t, k))     # a leaping golem is drawn on top
    for k in order:
        name, _, h, col, cost = GOLEMS[k]
        cx = gol_x(t, k)
        s = 1.0
        if k == WHACKED and t > T_WHACK: s = 1.0 - 0.25 * ease_out(prog(t, T_WHACK, T_WHACK + 0.5))   # €400 -> €300
        attacking = any(HIT_BY[i] == k and 0 <= t - (hh - 0.12) < 0.36 for i, hh in enumerate(HITS))
        w = int(24 * (0.85 + 0.15 * s)); hh_ = int(h * s)
        y0 = golem(d, cx, GROUND_Y - gol_hop(t, k), col, w, hh_, t, k, attacking)
        top = min(top, y0 + gol_hop(t, k)); tops.append((GOLEMS[k][1], y0, name))
        if k == WHACKED and t > T_WHACK:
            for q in range(3):
                a = t * 6 + q * 2.1
                d.point((cx + int(math.cos(a) * 9), y0 - 4 + int(math.sin(a) * 3)), fill=GOLD_L)
    for (cx, y0, name) in tops:
        text(d, name, cx, GROUND_Y + 8, mixc(GOLEMS[[g[0] for g in GOLEMS].index(name)][3], WHITE, 0.55), center=True)   # labels on the dirt, under each golem
    return 130, top

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
    # rolled-up budget map in the raised hand, swung like a bat
    if T_GRAB + 0.15 <= t < T_PAY:
        sw = prog(t, T_WHACK - 0.15, T_WHACK)
        ang = lerp(-1.9, 0.2, sw) if t < T_WHACK + 0.3 else lerp(0.2, -1.6, prog(t, T_WHACK + 0.3, T_WHACK + 0.6))
        hxp, hyp = gx + 10, GROUND_Y - 19 - 7
        ex, ey = hxp + int(math.cos(ang) * 13), hyp + int(math.sin(ang) * 13)
        ld.line([hxp, hyp, ex, ey], fill=INK, width=5)
        ld.line([hxp, hyp, ex, ey], fill=(235, 215, 160), width=3)
        ld.point((ex, ey), fill=RED); ld.point(((hxp + ex) // 2, (hyp + ey) // 2), fill=(120, 170, 90))
    if hurt_blink:
        layer = Image.eval(layer, lambda v: v)  # keep, but tint red below
        r, g, b, a = layer.split()
        layer = Image.merge("RGBA", (r.point(lambda v: min(255, v + 120)), g.point(lambda v: v // 2), b.point(lambda v: v // 2), a))
    fx, fy = GUY_X, GROUND_Y + 1
    spr = layer.crop((fx - 30, fy - 90, fx + 30, fy)).resize((120, 180), Image.NEAREST)
    im.paste(spr, (fx - 60, fy - 180), spr)
    d = ImageDraw.Draw(im); d.fontmode = "1"
    hx = fx + (gx - fx) * 2; hcy = fy - (fy - ghcy) * 2
    # boss nameplate + HP
    hp = 1.0 - 0.25 * ease_out(prog(t, T_WHACK, T_WHACK + 0.5))
    text(d, "THE BIG 3", bx, by0 - 34, RED, center=True)
    d.rectangle([bx - 34, by0 - 23, bx + 34, by0 - 19], fill=INK)
    d.rectangle([bx - 33, by0 - 22, bx - 33 + int(66 * hp), by0 - 20], fill=RED)

    # damage numbers, combo, KO
    for i, h in enumerate(HITS):
        p = prog(t, h, h + 0.9)
        if 0 < p < 1:
            text(d, "-€" + str(GOLEMS[HIT_BY[i]][4]), hx - 18 + i * 6, hcy - 40 - int(20 * p), RED)
    if 1.06 <= t < 2.4 and int(t * 8) % 4:
        text(d, "x3 COMBO!", 128, 150, GOLD, center=True)
    if T_WHACK <= t < T_WHACK + 1.4:
        p = prog(t, T_WHACK, T_WHACK + 0.15)
        text(d, "WHAP!", bx, 150 - int(6 * p), WHITE, font=FONT_BIG, center=True)
    # big yearly cost / payoff
    if 3.8 <= t < T_BOX:
        if prog(t, 3.8, 3.9) >= 1 and (t > 4.3 or int(t * 10) % 2):
            text(d, "-€18,000", 90, 100, RED, font=FONT_BIG, center=True)
            text(d, "EVERY YEAR", 90, 122, WHITE, center=True)
    if T_PAY + 0.2 <= t < T_CTA:
        text(d, "+€1,200", 100, 96, GOLD, font=FONT_BIG, center=True)
        text(d, "A YEAR", 100, 118, WHITE, center=True)
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
    text(d, "EXAMPLE NUMBERS", 90, 42, (210, 210, 225), center=True)   # amounts show from the first hit on

    # hook title slams in immediately
    if t < 1.5:
        for k, ln in enumerate(["NOT JUST", "THE LATTE.", "IT'S THEM."]):
            st = 0.0 + k * 0.1
            if t >= st:
                dy = 0 if k == 0 else -int((1 - prog(t, st, st + 0.08)) * 14)  # line 1 sits still on frame 0; others drop in (never cut off sideways)
                text(d, ln, 90, 62 + k * 22 + dy, RED if k == 1 else WHITE, font=FONT_BIG, center=True)

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
            elif CTA_MODE == "more":
                text(d, "FOLLOW", 90, 58, WHITE, font=FONT_BIG, center=True)
                if t > T_CTA + 0.3:
                    text(d, "FOR MORE", 90, 84, GOLD if int(t * 4) % 2 else (255, 240, 140), font=FONT_BIG, center=True)
                    text(d, "TIPS", 90, 106, GOLD if int(t * 4) % 2 else (255, 240, 140), font=FONT_BIG, center=True)
                if t > T_CTA + 0.6:
                    text(d, "NEW LEVEL", 90, 136, (150, 255, 180), center=True)
                    text(d, "EVERY DAY", 90, 148, (150, 255, 180), center=True)
            if CTA_MODE == "more" and t > T_CTA + 0.9:   # open loop: the next boss waits in the dark
                text(d, "NEXT BOSS", 140, 232, (150, 255, 180), center=True)
                for k in range(3):
                    mx = 126 + k * 14; my = 254
                    d.rectangle([mx - 5, my - 5, mx + 5, my + 5], fill=(70, 60, 100))
                    d.point((mx - 2, my - 1), fill=RED); d.point((mx + 2, my - 1), fill=RED)
                bx0 = 142 + int(math.sin(t * 6) * 2)
                d.rectangle([bx0 - 30, 200, bx0 + 30, 220], fill=INK)
                d.rectangle([bx0 - 29, 201, bx0 + 29, 219], fill=(90, 110, 230))
                d.rectangle([bx0 - 29, 201, bx0 + 29, 202], fill=(160, 175, 255))
                text(d, "+FOLLOW", bx0 - 26, 207, WHITE, shadow=False)
            elif CTA_MODE == "follow":
                text(d, "FOLLOW", 90, 58, WHITE, font=FONT_BIG, center=True)
                if t > T_CTA + 0.3:
                    text(d, "FOR PART 2", 90, 84, GOLD if int(t * 4) % 2 else (255, 240, 140), font=FONT_BIG, center=True)
                if t > T_CTA + 0.6:
                    text(d, "NEXT LEVEL:", 90, 116, (150, 255, 180), center=True)
                    text(d, "THE TRIAL TRAP", 90, 128, WHITE, center=True)
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

# cover image: python3 <episode>.py <mode> cover  -> *_cover.png (1080x1920, title area inside the 3:4 grid crop)
COVER_T = 0.47
if len(sys.argv) > 2 and sys.argv[2] == "cover":
    frame(COVER_T).save(OUT.replace("_silent.mp4", "_cover.png"))
    sys.exit(0)

proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                         "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264",
                         "-preset", "veryfast", "-crf", "16", "-pix_fmt", "yuv420p", OUT], stdin=subprocess.PIPE)
CHECK = [0, 20, 40, 120, 200, 262, 270, 330, 450, 570]
for i in range(N):
    fr = frame(i / FPS)
    proc.stdin.write(fr.tobytes())
    if i in CHECK: fr.save(f"/home/claude/dime-money-quest/studio/b3_{i:03d}.png")
proc.stdin.close(); proc.wait()

# ---------- audio ----------
sys.path.insert(0, "/home/claude/dime-money-quest/studio")
from sound import episode_audio
episode_audio("/home/claude/dime-money-quest/studio/ep003_sfx.wav", DUR, HITS, T_BOX, T_GRAB, T_WHACK, T_PAY, T_CTA, DIALOG, weapon="swat")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", OUT, "-i", "/home/claude/dime-money-quest/studio/ep003_sfx.wav",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest", "/home/claude/dime-money-quest/studio/ep003_big_three.mp4"])
print("done")
