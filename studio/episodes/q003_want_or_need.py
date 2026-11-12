# Quick format: WANT OR NEED? Jacket €80 (yours ripped) NEED · sneakers €120 (pair no. 4) WANT · phone €900 (yours works) WANT
# Wants: €120 + €900 = €1,020. Tip: list your wants today, buy one a month from fun money.
exec(open("/home/claude/dime-money-quest/studio/quick.py").read())

NAME = "q003_want_or_need"
DUR, T_CTA = 12.0, 10.7
ITEMS = [("JACKET", 80, "NEED", "WINTER JACKET, €80. YOURS RIPPED."),
         ("SNEAKERS", 120, "WANT", "SNEAKERS, €120. PAIR NUMBER 4."),
         ("NEW PHONE", 900, "WANT", "NEW PHONE, €900. YOURS WORKS FINE.")]
T_ITEM = [0.0, 2.1, 4.2]
T_STAMP = [1.4, 3.5, 5.6]
T_SUM, T_TIP = 6.4, 8.2
T_HIT = T_TIP
DIALOG = [(T_ITEM[k], ITEMS[k][3]) for k in range(3)] + \
         [(T_SUM, "WANTS: €120 + €900 = €1,020. FINE, IF PLANNED."),
          (T_TIP, "TIP: LIST YOUR WANTS TODAY. BUY 1 A MONTH FROM FUN MONEY.")]
EVENTS = [(0.0, "slam"), (0.1, "slam"), (0.2, "slam")] + [(t, "tick") for t in T_ITEM[1:]] + \
         [(T_STAMP[0], "stamp"), (T_STAMP[0] + 0.05, "ding"), (T_STAMP[1], "stamp"), (T_STAMP[1] + 0.05, "buzz"),
          (T_STAMP[2], "stamp"), (T_STAMP[2] + 0.05, "buzz"), (T_SUM, "womp"),
          (T_TIP - 0.6, "riser"), (T_TIP, "item"), (T_TIP + 0.3, "coinrain"), (T_TIP + 0.9, "jump")]

def mood_at(t):
    if t < T_STAMP[0]: return "neutral"
    if t < T_STAMP[1]: return "happy"
    if t < T_TIP: return "shock"
    return "happy"

def guy_state(t):
    for (j0, jd, hgt) in ((T_STAMP[0] + 0.05, 0.35, 12), (T_TIP - 0.45, 0.5, 14), (T_TIP + 0.9, 0.35, 12)):
        if j0 <= t < j0 + jd:
            p = (t - j0) / jd
            return GUY_X, GROUND_Y, None, int(hgt * 4 * p * (1 - p)), "up", 1.0
    arms = "down"
    if T_STAMP[0] <= t < T_ITEM[1]: arms = "up"
    if t >= T_TIP: arms = "up" if int(t * 4) % 2 else "down"
    return GUY_X, GROUND_Y, None, 0, arms, 1.0

def draw_item(k, t):
    """small RGBA sprite (36x30) of the item, scaled 2x when pasted"""
    im = Image.new("RGBA", (36, 30), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if k == 0:   # winter jacket with a rip
        c, cd = (220, 70, 80), (160, 40, 55)
        d.polygon([(10, 4), (26, 4), (33, 14), (29, 17), (26, 13), (26, 28), (10, 28), (10, 13), (7, 17), (3, 14)], fill=INK)
        d.polygon([(11, 5), (25, 5), (31, 14), (29, 15), (25, 11), (25, 27), (11, 27), (11, 11), (7, 15), (5, 14)], fill=c)
        d.line([18, 6, 18, 27], fill=(230, 230, 240)); d.rectangle([14, 4, 22, 6], fill=cd)
        d.line([12, 18, 15, 20, 13, 22, 16, 24], fill=INK, width=1)        # the rip
    elif k == 1:  # sneaker, side view
        d.polygon([(4, 14), (14, 10), (20, 14), (31, 18), (33, 23), (4, 23)], fill=INK)
        d.polygon([(5, 15), (14, 11), (20, 15), (30, 19), (32, 22), (5, 22)], fill=(90, 140, 255))
        d.rectangle([4, 22, 33, 26], fill=INK); d.rectangle([5, 23, 32, 25], fill=WHITE)
        for q in range(3): d.line([12 + q * 3, 13 + q, 14 + q * 3, 16 + q], fill=WHITE)
        d.line([22, 18, 28, 20], fill=GOLD)
    else:         # phone, no logo
        d.rectangle([11, 1, 25, 29], fill=INK); d.rectangle([12, 2, 24, 28], fill=(60, 60, 75))
        for y in range(4, 26):
            d.line([13, y, 23, y], fill=mixc((120, 90, 255), (60, 220, 200), (y - 4) / 22))
        d.rectangle([16, 3, 20, 3], fill=INK)
        if int(t * 6) % 2: d.point((15, 8), fill=WHITE); d.point((21, 18), fill=WHITE)
    return im.resize((72, 60), Image.NEAREST)

def frame(t):
    im, d = scene(t, sky=9)
    cur = max(k for k in range(3) if t >= T_ITEM[k])
    if t < T_SUM:
        k = cur
        slide = 0 if k == 0 else int((1 - ease_out(prog(t, T_ITEM[k], T_ITEM[k] + 0.25))) * 80)
        cx = 128 + slide
        name, price, verdict, _ = ITEMS[k]
        d.rectangle([cx - 40, 134, cx + 40, 236], fill=INK)
        d.rectangle([cx - 39, 135, cx + 39, 235], fill=(70, 60, 110))
        d.rectangle([cx - 39, 135, cx + 39, 137], fill=(120, 110, 170))
        text(d, name, cx, 141, WHITE, center=True)
        text(d, f"€{price}", cx, 153, GOLD, font=FONT_BIG, center=True)
        spr = draw_item(k, t)
        bob = int(abs(math.sin(t * 4)) * 2)
        im.paste(spr, (cx - 36, 172 - bob), spr)
        d = ImageDraw.Draw(im); d.fontmode = "1"
        if t >= T_STAMP[k]:
            p = prog(t, T_STAMP[k], T_STAMP[k] + 0.12)
            col = GREEN if verdict == "NEED" else GOLD
            grow = int((1 - p) * 8)
            d.rectangle([cx - 36 - grow, 186 - grow, cx + 36 + grow, 212 + grow], fill=INK)
            d.rectangle([cx - 34 - grow, 188 - grow, cx + 34 + grow, 210 + grow], outline=col, width=2)
            text(d, verdict, cx, 192, col, font=FONT_BIG, center=True)
    else:
        if t >= T_SUM + 0.2:
            text(d, "€1,020", 126, 136, GOLD, font=FONT_BIG, center=True)
            text(d, "IN WANTS", 126, 156, WHITE, center=True)
    # running tally
    need = sum(ITEMS[k][1] for k in range(3) if ITEMS[k][2] == "NEED" and t >= T_STAMP[k])
    want = sum(ITEMS[k][1] for k in range(3) if ITEMS[k][2] == "WANT" and t >= T_STAMP[k])
    text(d, f"NEED €{need}", 6, 122, (150, 255, 180))
    wtxt = f"WANT €{want:,}"
    text(d, wtxt, 174 - int(d.textlength(wtxt, font=FONT)), 122, GOLD)
    # coins back into the wallet with the tip
    for k in range(8):
        p = prog(t, T_TIP + 0.3 + k * 0.07, T_TIP + 0.9 + k * 0.07)
        if 0 < p < 1:
            coin_sprite(d, int(lerp(140, GUY_X, p)), int(lerp(200, GROUND_Y - 50, p) - 26 * math.sin(math.pi * p)), 3, t * 12 + k)
    item_box(d, t, GUY_X, 150, T_TIP - 0.6, T_TIP)
    paste_dime(im, t, GUY_X)
    d = ImageDraw.Draw(im); d.fontmode = "1"
    whp = 0.9 - 0.06 * (t >= T_STAMP[1]) - 0.3 * (t >= T_STAMP[2]) + 0.25 * ease_out(prog(t, T_TIP + 0.3, T_TIP + 1.2))
    hud(d, t, whp, mood_at(t), tag="WANT OR NEED?")
    headline(d, t, ["WANT", "OR", "NEED?"], [GOLD, WHITE, GREEN], y0=67, step=18, t_end=T_SUM)
    if t >= T_SUM and t < T_CTA:
        text(d, "WANT OR NEED?", 90, 70, WHITE, center=True)
    dialog_box(d, t, DIALOG, T_CTA)
    if t >= T_CTA: im = end_card(im, t, T_CTA)
    return post_fx(im, t, DUR, shakes=T_STAMP, white=[T_TIP])

run_quick(NAME, frame, DUR, T_CTA, EVENTS, DIALOG, cover_t=0.3, music="quiz", check=(0, 50, 110, 175, 200, 260, 280, 330))
