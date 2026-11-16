# Boss fight ep012: CRUMB RATS (topic 13, pay yourself first). Plan: save €100 "of what's left" at month end;
# the rats eat it first: €40 + €30 + €30 = €100/month -> €0 saved = -€1,200/year.
# Power-up: auto-transfer €100 on payday, before bills and fun: +€100/month = +€1,200/year.
# Story day 3: Dime adds a €100 payday auto-transfer: plan €460 -> €560 a month (content/story.md).
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
NAME = "ep012_crumb_rats"
OUT = f"/home/claude/dime-money-quest/studio/{NAME}_silent.mp4"
HITS = [0.0, 0.56, 1.06]   # first hit lands on frame 0
T_BOX, T_GRAB, T_WHACK, T_PAY, T_CTA = 6.3, 8.0, 8.6, 10.6, 14.0
BAG_HOME = 128

# ---- v2 look + Dime's story (content/story.md) ----
SCENE = "rain"                      # bank-day gloom (previous reel ep011 uses sunset)
DAY, PLAN_BEFORE, PLAN_AFTER = 3, 460, 560   # story day + Dime's monthly savings before/after this boss (ledger in content/story.md)
DASH = (T_WHACK - 0.35, T_WHACK + 1.0, 17)  # Dime dashes at the boss for the counterattack (low-res px)
SPINS = [(T_GRAB - 0.45, T_GRAB + 0.05), (T_PAY + 0.15, T_PAY + 0.75)]
ZOOMS = [(0.0, 1.45, 1.22, 96, 205),                 # cold open: punched in on the fight
         (T_WHACK - 0.05, T_WHACK + 0.9, 1.35, 112, 205)]   # counterattack (no zoom on the payoff: the big number needs the room)

DIALOG = [(1.5, "SAVING WHAT IS LEFT? RATS EAT IT BY DAY 30..."),
          (3.6, "...€100 A MONTH IS €1,200 A YEAR. GONE."),
          (T_BOX, "TIP: SET A €100 AUTO-TRANSFER FOR PAYDAY. TODAY."),
          (T_PAY, "PAY YOURSELF FIRST: +€100 A MONTH. +€1,200 A YEAR.")]
DMG = ["-€40", "-€30", "-€30"]   # = €100 a month

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

# Crumb Rats: grey rats that nibble the "leftovers" before month end ever comes
MCOLS = [(150, 150, 165), (130, 125, 145), (165, 155, 150)]

def big_monster(d, cx, by, col, s, t, k, attacking):
    """a crumb rat: round grey body, big pink ears, long tail, buck teeth, nibbling a coin"""
    w = int(20 * s); h = int(13 * s)
    hop = int(abs(math.sin(t * 8 + k * 1.3)) * 3)
    y0 = by - h - hop
    x0 = cx - w // 2
    d.ellipse([cx - 9, by - 1, cx + 9, by + 2], fill=(40, 40, 55))       # shadow
    # tail (behind, curling right)
    wig = int(math.sin(t * 9 + k) * 2)
    d.line([x0 + w - 2, y0 + h - 3, x0 + w + 5, y0 + h - 6 + wig, x0 + w + 9, y0 + h - 12 + wig], fill=INK, width=3)
    d.line([x0 + w - 2, y0 + h - 3, x0 + w + 5, y0 + h - 6 + wig, x0 + w + 9, y0 + h - 12 + wig], fill=(240, 150, 170), width=1)
    # feet
    for fx_ in (x0 + 4, x0 + w - 6):
        d.rectangle([fx_ - 1, by - hop - 3, fx_ + 2, by - hop], fill=INK)
        d.rectangle([fx_, by - hop - 2, fx_ + 1, by - hop - 1], fill=(240, 150, 170))
    # body
    d.ellipse([x0 - 1, y0 - 1, x0 + w + 1, y0 + h + 1], fill=INK)
    d.ellipse([x0, y0, x0 + w, y0 + h], fill=col)
    d.rectangle([x0 + 5, y0 + 2, x0 + 8, y0 + 3], fill=mixc(col, WHITE, 0.5))
    # ears
    for ex_ in (x0 + 3, x0 + 11):
        d.ellipse([ex_ - 1, y0 - 6, ex_ + 6, y0 + 1], fill=INK)
        d.ellipse([ex_, y0 - 5, ex_ + 5, y0], fill=(240, 150, 170))
    # face looks left (at Dime): eye, nose, teeth
    ey = y0 + 4
    d.rectangle([x0 + 3, ey, x0 + 5, ey + 2], fill=INK); d.point((x0 + 3, ey), fill=WHITE if not attacking else RED)
    d.rectangle([x0 - 3, y0 + 6, x0 - 1, y0 + 8], fill=(240, 120, 150))   # nose
    d.rectangle([x0, y0 + 9, x0 + 3, y0 + 9 + (3 if attacking else 2)], fill=WHITE)
    d.line([x0 - 1, y0 + 7, x0 - 6, y0 + 5], fill=INK); d.line([x0 - 1, y0 + 8, x0 - 6, y0 + 9], fill=INK)   # whiskers
    if attacking:
        coin_sprite(d, x0 - 5, y0 + 10, 3, t * 10 + k)
    return y0 - 8

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

def payday_order(d, t, t0):
    """the new payday order at the top of the screen while Dime holds the calendar (y 52..92)"""
    rows = [("1. SAVE €100", GOLD, "AUTO"), ("2. BILLS", WHITE, ""), ("3. FUN", WHITE, "")]
    d.rectangle([7, 51, LW - 8, 96], fill=INK); d.rectangle([8, 52, LW - 9, 95], outline=GOLD)
    text(d, "PAYDAY ORDER", 90, 55, (150, 255, 180), shadow=False, center=True)
    for k, (lab, col, tag) in enumerate(rows):
        if t < t0 + 0.15 * k: continue
        text(d, lab, 14, 66 + k * 9, col, shadow=False)
        if tag:
            d.rectangle([130, 65, 166, 74], fill=GREEN); text(d, tag, 148, 66, INK, shadow=False, center=True)

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
    # payday calendar page with a green "auto" arrow: €100 leaves for savings the day the pay lands
    if T_GRAB + 0.15 <= t < T_PAY:
        hxp, hyp = gx + 10, GROUND_Y - 19 - 7
        push = int(6 * math.sin(math.pi * prog(t, T_WHACK - 0.1, T_WHACK + 0.3)))
        cx0, cy0 = hxp + push, hyp - 9
        ld.rectangle([cx0 - 1, cy0 - 1, cx0 + 15, cy0 + 17], fill=INK)
        ld.rectangle([cx0, cy0, cx0 + 14, cy0 + 16], fill=WHITE)
        ld.rectangle([cx0, cy0, cx0 + 14, cy0 + 4], fill=RED)
        for q in (3, 10): ld.rectangle([cx0 + q, cy0 - 2, cx0 + q + 1, cy0 + 1], fill=INK)
        ld.rectangle([cx0 + 4, cy0 + 7, cx0 + 10, cy0 + 13], fill=GOLD)   # coin on payday
        ld.rectangle([cx0 + 6, cy0 + 8, cx0 + 8, cy0 + 12], fill=GOLD_L if 'GOLD_L' in globals() else GOLD)
        # arrow curling up and away into savings
        ax = cx0 + 16; ay = cy0 + 8 - int(3 * math.sin(t * 8))
        ld.polygon([(ax + 10, ay), (ax + 4, ay - 5), (ax + 4, ay - 2), (ax, ay - 2), (ax, ay + 2), (ax + 4, ay + 2), (ax + 4, ay + 5)], fill=GREEN)
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
    if t < T_GRAB + 0.15:   # nameplate steps aside while Dime holds the power-up (never overlaps the item)
        text(d, "CRUMB RATS", bx, by0 - 22, RED, center=True)
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
        im = plate(im, 98, 124, 0.55); d = ImageDraw.Draw(im); d.fontmode = "1"   # dark plate: particles never cross the KO word
        text(d, "AUTO-SAVED", 90, 110 - int(6 * p), WHITE, font=FONT_BIG, center=True)
    # big yearly cost / payoff
    if 3.8 <= t < T_BOX:
        if prog(t, 3.8, 3.9) >= 1 and (t > 4.3 or int(t * 10) % 2):
            text(d, "-€1,200", 90, 100, RED, font=FONT_BIG, center=True)
            text(d, "EVERY YEAR", 90, 122, WHITE, center=True)
    if T_GRAB + 0.2 <= t < T_PAY:
        payday_order(d, t, T_GRAB + 0.2)
    if T_PAY + 0.7 <= t < T_CTA:
        quest_bar(d, t, T_PAY + 0.7, DAY, PLAN_BEFORE, PLAN_AFTER)
    if T_PAY + 0.2 <= t < T_CTA:
        text(d, "+€1,200", 110, 96, GOLD, font=FONT_BIG, center=True)
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
        for k, ln in enumerate(["SAVING", "LEFTOVERS?", "€0 LEFT"]):
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
episode_audio(f"/home/claude/dime-money-quest/studio/{NAME}_sfx.wav", DUR, HITS, T_BOX, T_GRAB, T_WHACK, T_PAY, T_CTA, DIALOG, weapon="transfer")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", OUT, "-i", f"/home/claude/dime-money-quest/studio/{NAME}_sfx.wav",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest", f"/home/claude/dime-money-quest/studio/{NAME}.mp4"])
print("done")
