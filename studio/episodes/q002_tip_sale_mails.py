# Quick format: 10-SECOND TIP. Sale emails -> 2 extra €25 buys a month = €50/month = €600/year. Tip: unsubscribe from 5 today.
exec(open("/home/claude/dime-money-quest/studio/quick.py").read())

NAME = "q002_tip_sale_mails"
DUR, T_CTA = 12.0, 9.5
HITS = [0.06, 0.6]
T_DMG, T_BOX, T_GRAB, T_ZAP, T_PAY = 3.4, 4.4, 5.0, 5.8, 6.9
T_HIT = T_ZAP
N_MAIL = 5
DIALOG = [(2.0, "2 EXTRA €25 BUYS A MONTH FROM SALE MAILS..."),
          (T_DMG, "...IS €50 A MONTH. €600 A YEAR."),
          (T_BOX, "TIP: UNSUBSCRIBE FROM 5 SHOP EMAILS TODAY"),
          (T_PAY, "NO SALE MAIL, NO 'JUST ONE MORE'. KEEP €600 A YEAR.")]
EVENTS = [(0.0, "slam"), (0.1, "slam"), (0.2, "slam")] + [(h, "punch") for h in HITS] + [(h + 0.04, "coinrain") for h in HITS] + \
         [(T_DMG, "womp"), (T_GRAB - 0.6, "riser"), (T_GRAB, "item"), (T_ZAP, "stamp")] + \
         [(T_ZAP + 0.12 * k, "poof") for k in range(N_MAIL)] + [(T_ZAP + 0.6, "coinrain"), (T_PAY + 0.2, "register"), (T_PAY + 0.25, "jump")]

def mood_at(t):
    if t < 1.6: return "shock"
    if t < T_ZAP + 0.2: return "sad"
    return "happy"

def knock(t):
    k = 0.0
    for h in HITS:
        d = t - h
        if 0 <= d < 0.4: k = max(k, 9 * (1 - d / 0.4))
    return k

def guy_state(t):
    x = GUY_X - int(knock(t))
    for (j0, jd, hgt) in ((T_GRAB - 0.45, 0.5, 22), (T_PAY + 0.25, 0.35, 14), (T_PAY + 0.8, 0.35, 14)):
        if j0 <= t < j0 + jd:
            p = (t - j0) / jd
            return x, GROUND_Y, None, int(hgt * 4 * p * (1 - p)), "up", 1.0
    arms = "down"
    if T_GRAB <= t < T_ZAP + 0.5: arms = "up"
    if mood_at(t) == "happy" and t > T_PAY: arms = "up" if int(t * 4) % 2 else "down"
    return x, GROUND_Y, None, 0, arms, 1.0

MAIL_HOME = [(118, 214), (140, 196), (162, 220), (128, 180), (156, 172)]

def mail_pos(t, k):
    x, y = MAIL_HOME[k]
    x += int(3 * math.sin(t * 5 + k)); y += int(3 * math.cos(t * 6 + k * 1.7))
    if k < len(HITS):                       # the first two swoop into Dime
        d = t - (HITS[k] - 0.12)
        if 0 <= d < 0.36:
            s = math.sin(math.pi * d / 0.36); x = int(lerp(x, 80, s)); y = int(lerp(y, 214, s))
    return x, y

def envelope(d, cx, cy, t, k):
    w, h = 18, 12
    d.rectangle([cx - w // 2 - 1, cy - h // 2 - 1, cx + w // 2 + 1, cy + h // 2 + 1], fill=INK)
    d.rectangle([cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2], fill=(245, 240, 230))
    d.line([cx - w // 2, cy - h // 2, cx, cy + 1, cx + w // 2, cy - h // 2], fill=(170, 160, 180))
    for sgn in (-1, 1):                      # angry eyes
        ex = cx + sgn * 4
        d.rectangle([ex - 1, cy + 1, ex, cy + 3], fill=INK)
        d.line([ex - 2 * sgn, cy - 1, ex + 1 * sgn, cy], fill=INK)
    d.rectangle([cx + w // 2 - 6, cy - h // 2 - 4, cx + w // 2 + 2, cy - h // 2 + 4], fill=RED)   # % sale sticker
    text(d, "%", cx + w // 2 - 6, cy - h // 2 - 4, WHITE, shadow=False)
    if int(t * 8 + k) % 2:                   # wing flaps
        d.line([cx - w // 2 - 4, cy - 4, cx - w // 2 - 1, cy - 1], fill=WHITE)
        d.line([cx + w // 2 + 1, cy - 1, cx + w // 2 + 4, cy - 4], fill=WHITE)

def stamp_tool(ld, gx, ghcy, t):
    """red 'X' unsubscribe stamp in the raised hand"""
    if not (T_GRAB + 0.15 <= t < T_PAY): return
    hx, hy = gx + 10, GROUND_Y - 19 - 7
    down = 3 if T_ZAP - 0.05 <= t < T_ZAP + 0.2 else 0
    ld.rectangle([hx - 1, hy - 8 + down, hx + 1, hy], fill=(120, 80, 50))
    ld.rectangle([hx - 5, hy - 12 + down, hx + 5, hy - 8 + down], fill=INK)
    ld.rectangle([hx - 4, hy - 11 + down, hx + 4, hy - 9 + down], fill=RED)

def frame(t):
    im, d = scene(t, sky=3)
    for k in range(N_MAIL):
        t_off = T_ZAP + 0.12 * k
        cx, cy = mail_pos(t, k)
        if t >= t_off:
            pp = prog(t, t_off, t_off + 0.4)
            if pp < 1:
                for a in range(8):
                    ang = a * math.pi / 4; r = int(3 + pp * 12)
                    d.rectangle([cx + int(math.cos(ang) * r) - 1, cy + int(math.sin(ang) * r) - 1,
                                 cx + int(math.cos(ang) * r) + 1, cy + int(math.sin(ang) * r) + 1], fill=WHITE if a % 2 else RED)
            continue
        envelope(d, cx, cy, t, k)
    # coins knocked out on each hit, coins back after the zap
    for h in HITS:
        for k in range(6):
            p = prog(t, h + k * 0.02, h + 0.55 + k * 0.02)
            if 0 < p < 1:
                ang = -2.2 + k * 0.45
                coin_sprite(d, GUY_X - 6 + int(math.cos(ang) * 40 * p), GROUND_Y - 50 - int(46 * math.sin(math.pi * p * 0.8)) + int(30 * p * p), 3, t * 14 + k)
    for k in range(8):
        p = prog(t, T_ZAP + 0.6 + k * 0.07, T_ZAP + 1.2 + k * 0.07)
        if 0 < p < 1:
            coin_sprite(d, int(lerp(140, GUY_X, p)), int(lerp(200, GROUND_Y - 50, p) - 26 * math.sin(math.pi * p)), 3, t * 12 + k)
    item_box(d, t, GUY_X, 140, T_BOX, T_GRAB)
    hurt = any(0 <= t - h < 0.45 for h in HITS) and int(t * 20) % 2 == 0
    hx, hcy = paste_dime(im, t, GUY_X, tint=hurt, extra=stamp_tool)
    d = ImageDraw.Draw(im); d.fontmode = "1"
    for h in HITS:
        p = prog(t, h, h + 0.9)
        if 0 < p < 1: text(d, "-€25", hx - 14, hcy - 40 - int(20 * p), RED)
    if 0.6 <= t < 1.8 and int(t * 8) % 4: text(d, "x2 COMBO!", 128, 150, GOLD, center=True)
    if T_DMG + 0.2 <= t < T_BOX:
        text(d, "-€600", 90, 100, RED, font=FONT_BIG, center=True)
        text(d, "EVERY YEAR", 90, 122, WHITE, center=True)
    if T_ZAP <= t < T_ZAP + 1.2:
        text(d, "POOF!", 132, 140 - int(6 * prog(t, T_ZAP, T_ZAP + 0.15)), WHITE, font=FONT_BIG, center=True)
    if T_PAY + 0.2 <= t < T_CTA:
        text(d, "+€600", 100, 96, GOLD, font=FONT_BIG, center=True)
        text(d, "A YEAR", 100, 118, WHITE, center=True)
    whp = 0.9 - 0.15 * sum(ease_out(prog(t, h, h + 0.3)) for h in HITS) + 0.3 * ease_out(prog(t, T_ZAP + 0.6, T_ZAP + 1.6))
    hud(d, t, whp, mood_at(t), tag="10-SECOND TIP")
    headline(d, t, ["SALE MAILS", "COST YOU", "€600/YEAR"], [WHITE, WHITE, RED], y0=66, t_end=2.0)
    dialog_box(d, t, DIALOG, T_CTA)
    if t >= T_CTA: im = end_card(im, t, T_CTA)
    return post_fx(im, t, DUR, shakes=HITS + [T_ZAP], red=HITS, white=[T_ZAP])

run_quick(NAME, frame, DUR, T_CTA, EVENTS, DIALOG, cover_t=0.47, music="battle", check=(0, 30, 110, 150, 175, 200, 230, 290))
