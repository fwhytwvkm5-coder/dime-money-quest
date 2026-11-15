# Boss fight ep010: CHAOS BLOBS (topic 11, the 3-jar system). One pot for everything: fun spends €20 + €15 + €15 = €50/month
# of the savings = €600/year. Power-up: 3 jars (bills, fun, save), fill SAVE first on payday: +€50/month = +€600/year.
# Story day 2: Dime's plan €295 -> €345 a month (content/story.md).
import math, random, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw

# reuse the arcade + Dime helpers (everything above render_guy's frame function)
src = open("/home/claude/dime-money-quest/studio/render_guy.py").read().split("\ndef frame(t):")[0]
exec(src)

exec(open("/home/claude/dime-money-quest/studio/fx.py").read())   # v2 visuals: scenes, camera, moves, quest bar

import sys
CTA_MODE = sys.argv[1] if len(sys.argv) > 1 else 'comment'
DUR = 19.5
N = int(FPS * DUR)
NAME = "ep010_chaos_blobs"
OUT = f"/home/claude/dime-money-quest/studio/{NAME}_silent.mp4"
HITS = [0.0, 0.56, 1.06]   # first hit lands on frame 0
T_BOX, T_GRAB, T_WHACK, T_PAY, T_CTA = 6.3, 8.0, 8.6, 10.6, 14.0
BAG_HOME = 128

# ---- v2 look + Dime's story (content/story.md) ----
SCENE = "apartment"                 # budgeting at home (previous reel ep009 uses rain)
DAY, PLAN_BEFORE, PLAN_AFTER = 2, 295, 345   # story day + Dime's monthly savings before/after this boss (ledger in content/story.md)
DASH = (T_WHACK - 0.35, T_WHACK + 1.0, 17)  # Dime dashes at the boss for the counterattack (low-res px)
SPINS = [(T_GRAB - 0.45, T_GRAB + 0.05), (T_PAY + 0.15, T_PAY + 0.75)]
ZOOMS = [(0.0, 1.45, 1.22, 96, 205),                 # cold open: punched in on the fight
         (T_WHACK - 0.05, T_WHACK + 0.9, 1.35, 112, 205)]   # counterattack (no zoom on the payoff: the big number needs the room)

DIALOG = [(1.5, "ONE POT FOR ALL: FUN EATS €50 OF YOUR SAVINGS..."),
          (3.6, "...€50 A MONTH IS €600 A YEAR. GONE."),
          (T_BOX, "TIP: 3 JARS TODAY. BILLS, FUN, SAVE. FILL SAVE FIRST."),
          (T_PAY, "SAVE JAR FIRST: +€50 A MONTH. +€600 A YEAR.")]
DMG = ["-€20", "-€15", "-€15"]   # = €50 a month

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
    x = GUY_X - int(knock(t)) + dash_x(t, *DASH)
    if any(0 <= t - h < 0.12 for h in HITS[-1:]): return x, feet, None, 6, "up", 1.0      # last hit lifts him off his feet
    for (j0, jd, hgt) in ((T_GRAB - 0.45, 0.5, 22), (T_PAY + 0.15, 0.6, 24), (T_PAY + 0.9, 0.35, 12)):
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
MXS = [104, 128, 152]
CUT = (0, 1, 2)   # all three blobs end up in jars

def mon_x(t, k):
    x = MXS[k]
    if True:
        h = HITS[k]; d = t - (h - 0.12)
        if 0 <= d < 0.36: x -= int(26 * math.sin(math.pi * d / 0.36))
    return x

# Chaos Blobs: gooey swirls that live in the one pot and grab whatever money is there
MCOLS = [(170, 90, 220), (90, 200, 150), (230, 120, 170)]

def big_monster(d, cx, by, col, s, t, k, attacking):
    """a chaos blob: wide, wobbly goo with a swirl, one big eye and a gulping mouth"""
    w = int(22 * s); h = int(16 * s)
    sq = int(math.sin(t * 7 + k * 2.1) * 2)
    hop = int(abs(math.sin(t * 6 + k)) * 3)
    y0 = by - h - hop + sq
    x0 = cx - w // 2
    d.ellipse([cx - 9, by - 1, cx + 9, by + 2], fill=(50, 35, 40))
    d.ellipse([x0 - 1 - sq, y0 - 1, x0 + w + 1 + sq, by - hop + 1], fill=INK)
    d.ellipse([x0 - sq, y0, x0 + w + sq, by - hop], fill=col)
    for q in range(3):   # goo drips on the bottom edge
        gx = x0 + 4 + q * 7
        d.rectangle([gx, by - hop - 2, gx + 2, by - hop + 1 + (q + int(t * 6)) % 2], fill=col)
    d.arc([x0 + 3, y0 + 4, x0 + 10, y0 + 11], 0, 270, fill=mixc(col, WHITE, 0.45))   # swirl
    ex, ey = cx + 3, y0 + 5
    d.ellipse([ex - 3, ey - 3, ex + 3, ey + 3], fill=WHITE); d.rectangle([ex - 1 + (1 if attacking else 0), ey - 1, ex, ey + 1], fill=INK)
    mh = 1 + (3 if attacking else 0)
    d.rectangle([cx - 1, y0 + h - 6, cx + 6, y0 + h - 6 + mh], fill=INK)
    if attacking:
        coin_sprite(d, x0 - 3, y0 + h // 2, 3, t * 10 + k)
    return y0 - 6

def draw_bag(d, t):
    top = GROUND_Y
    for k in range(3):
        cx = mon_x(t, k)
        tk = T_WHACK + 0.1 * k
        if k in CUT and t >= tk:
            pp = prog(t, tk, tk + 0.45)
            if pp < 1:
                r = int(3 + pp * 10)
                for a in range(8):
                    ang = a * math.pi / 4
                    d.rectangle([cx + int(math.cos(ang) * r) - 1, GROUND_Y - 12 + int(math.sin(ang) * r) - 1,
                                 cx + int(math.cos(ang) * r) + 1, GROUND_Y - 12 + int(math.sin(ang) * r) + 1], fill=WHITE)
            continue
        s = 1.0 - (0.3 * ease_out(prog(t, T_WHACK, T_WHACK + 0.5)) if t > T_WHACK else 0)
        attacking = 0 <= t - (HITS[k] - 0.12) < 0.36
        y0 = big_monster(d, cx, GROUND_Y, MCOLS[k], s, t, k, attacking)
        top = min(top, y0)
        if t > T_WHACK:
            for q in range(2):
                a = t * 6 + q * 3.1 + k
                d.point((cx + int(math.cos(a) * 7), y0 - 4 + int(math.sin(a) * 2)), fill=GOLD_L)
    return 130, top

def frame(t):
    im, d = paint_scene(SCENE, t)

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
    # power-up box
    if t >= T_BOX:
        drop = ease_out(prog(t, T_BOX, T_BOX + 0.5))
        qx, qy = GUY_X, int(lerp(20, 108, drop))   # above Dime's rain cloud
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
    # glass jar with a gold lid in the raised hand: the SAVE jar
    if T_GRAB + 0.15 <= t < T_PAY:
        hxp, hyp = gx + 10, GROUND_Y - 19 - 7
        push = int(6 * math.sin(math.pi * prog(t, T_WHACK - 0.1, T_WHACK + 0.3)))
        jx, jy = hxp + 1 + push, hyp - 14
        ld.rectangle([jx - 1, jy + 2, jx + 11, jy + 17], fill=INK)
        ld.rectangle([jx, jy + 3, jx + 10, jy + 16], fill=(170, 220, 255))
        ld.rectangle([jx + 1, jy + 4, jx + 2, jy + 12], fill=(230, 245, 255))
        ld.rectangle([jx - 1, jy - 1, jx + 11, jy + 3], fill=INK); ld.rectangle([jx, jy, jx + 10, jy + 2], fill=GOLD)
        n = 1 + int(4 * prog(t, T_WHACK + 0.2, T_WHACK + 1.2))
        for q in range(n):
            ld.ellipse([jx + 2 + (q % 2) * 3, jy + 12 - q * 2, jx + 6 + (q % 2) * 3, jy + 15 - q * 2], fill=GOLD)
    if hurt_blink:
        layer = Image.eval(layer, lambda v: v)  # keep, but tint red below
        r, g, b, a = layer.split()
        layer = Image.merge("RGBA", (r.point(lambda v: min(255, v + 120)), g.point(lambda v: v // 2), b.point(lambda v: v // 2), a))
    layer = mirror_spin(layer, int(gx), t, SPINS)
    fx, fy = GUY_X, GROUND_Y + 1
    spr = layer.crop((fx - 30, fy - 90, fx + 50, fy)).resize((160, 180), Image.NEAREST)
    im.paste(spr, (fx - 60, fy - 180), spr)
    d = ImageDraw.Draw(im); d.fontmode = "1"
    hx = fx + (gx - fx) * 2; hcy = fy - (fy - ghcy) * 2
    # motion accents
    speed_lines(d, t, DASH[0], DASH[0] + 0.3, hx - 14, hcy + 40)
    shockwave(d, t, T_WHACK, hx + 40, GROUND_Y - 20)
    dust(d, t, T_GRAB + 0.05, hx); dust(d, t, T_PAY + 0.75, hx)
    confetti(d, t, T_PAY + 0.15)
    im = world_zoom(im, t, ZOOMS)
    d = ImageDraw.Draw(im); d.fontmode = "1"
    # boss nameplate + HP
    hp = 1.0 - 1.0 * ease_out(prog(t, T_WHACK, T_WHACK + 0.5))
    if t < T_WHACK:   # nameplate leaves when the jar hits
        text(d, "CHAOS BLOBS", bx, by0 - 22, RED, center=True)
        d.rectangle([bx - 34, by0 - 11, bx + 34, by0 - 7], fill=INK)
        d.rectangle([bx - 33, by0 - 10, bx - 33 + int(66 * hp), by0 - 8], fill=RED)

    # damage numbers, combo, KO
    for i, h in enumerate(HITS):
        p = prog(t, h, h + 0.9)
        if 0 < p < 1:
            text(d, DMG[i], 92, 150 + i * 11, RED)   # fixed column right of the head: under the combo, above the nameplate
    if 1.06 <= t < 2.4 and int(t * 8) % 4:
        text(d, "x3 COMBO!", 132, 136, GOLD, center=True)
    if T_WHACK <= t < T_WHACK + 1.4:
        p = prog(t, T_WHACK, T_WHACK + 0.15)
        text(d, "JARRED!", 90, 104 - int(6 * p), WHITE, font=FONT_BIG, center=True)
    # big yearly cost / payoff
    if 3.8 <= t < T_BOX:
        if prog(t, 3.8, 3.9) >= 1 and (t > 4.3 or int(t * 10) % 2):
            text(d, "-€600", 90, 100, RED, font=FONT_BIG, center=True)
            text(d, "EVERY YEAR", 90, 122, WHITE, center=True)
    if T_PAY + 0.7 <= t < T_CTA:
        quest_bar(d, t, T_PAY + 0.7, DAY, PLAN_BEFORE, PLAN_AFTER)
    if T_PAY + 0.2 <= t < T_CTA:
        text(d, "+€600", 110, 96, GOLD, font=FONT_BIG, center=True)
        text(d, "A YEAR", 110, 118, WHITE, center=True)
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
        im = plate(im, 58, 128); d = ImageDraw.Draw(im); d.fontmode = "1"
        for k, ln in enumerate(["ONE POT", "EATS YOUR", "SAVINGS"]):
            st = 0.0 + k * 0.1
            if t >= st:
                dy = 0 if k == 0 else -int((1 - prog(t, st, st + 0.08)) * 14)  # line 1 sits still on frame 0; others drop in (never cut off sideways)
                text(d, ln, 90, 62 + k * 22 + dy, RED if k == 2 else WHITE, font=FONT_BIG, center=True)

    # end card
    if t >= T_CTA:
        p = prog(t, T_CTA, T_CTA + 0.3)
        im = Image.blend(im, Image.new("RGB", (LW, LH), INK), 0.94 * p if p < 1 else 1.0)
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
                    text(d, "THE BIG THREE", 90, 128, WHITE, center=True)
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
    frame(COVER_T).save(f"/home/claude/dime-money-quest/studio/{NAME}_cover.png")
    sys.exit(0)

proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                         "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264",
                         "-preset", "veryfast", "-crf", "16", "-pix_fmt", "yuv420p", OUT], stdin=subprocess.PIPE)
CHECK = [0, 20, 40, 120, 200, 262, 270, 330, 450, 570]
for i in range(N):
    fr = frame(i / FPS)
    proc.stdin.write(fr.tobytes())
    if i in CHECK: fr.save(f"/home/claude/dime-money-quest/studio/{NAME}_{i:03d}.png")
proc.stdin.close(); proc.wait()

# ---------- audio ----------
sys.path.insert(0, "/home/claude/dime-money-quest/studio")
from sound import episode_audio
episode_audio(f"/home/claude/dime-money-quest/studio/{NAME}_sfx.wav", DUR, HITS, T_BOX, T_GRAB, T_WHACK, T_PAY, T_CTA, DIALOG, weapon="clink")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", OUT, "-i", f"/home/claude/dime-money-quest/studio/{NAME}_sfx.wav",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest", f"/home/claude/dime-money-quest/studio/{NAME}.mp4"])
print("done")
