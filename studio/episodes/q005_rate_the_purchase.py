# Quick format: RATE THE PURCHASE (rarity ranking, common waste to legendary buy).
# GADGET €35, used once = €35 per use -> COMMON · JACKET €60, worn 60 times = €1 per wear -> EPIC ·
# LUNCHBOX €15: 3 home lunches a week at €3 instead of €8 takeout = €5 x 3 = €15 a week; x 52 = €780 a year -> LEGENDARY.
# Tip: before a buy, do price / uses (the times you'll really use it).
exec(open("/home/claude/dime-money-quest/studio/quick.py").read())

NAME = "q005_rate_the_purchase"
SCENE = "mall"          # shopping -> mall (previous reel q004 used the classic sky; next reel ep009 uses rain)
DUR, T_CTA = 12.0, 9.6
COMMON, EPIC, LEGEND = (185, 185, 200), (190, 120, 255), GOLD
# (card label, price line, value line, rarity, colour, dialog)
ITEMS = [("GADGET", "€35", "€35/USE", "COMMON", COMMON, "LIGHT-UP GADGET: €35. USED ONCE. €35 PER USE."),
         ("JACKET", "€60", "€1/WEAR", "EPIC", EPIC, "WINTER JACKET: €60. WORN 60 TIMES. €1 PER WEAR."),
         ("LUNCHBOX", "€15", "+€15/WEEK", "LEGENDARY", LEGEND, "LUNCHBOX: €15. 3 HOME LUNCHES A WEEK: €3, NOT €8.")]
T_ITEM = [0.0, 1.9, 3.8]
T_STAMP = [1.2, 3.1, 5.0]
T_SUM, T_TIP = 5.8, 7.4
DIALOG = [(T_ITEM[k], ITEMS[k][5]) for k in range(3)] + \
         [(T_SUM, "€5 X 3 = €15 A WEEK. X52 = €780 A YEAR."),
          (T_TIP, "TIP: BEFORE A BUY, DO PRICE / USES.")]
EVENTS = [(0.0, "slam"), (0.1, "slam"), (0.2, "slam")] + [(t, "tick") for t in T_ITEM[1:]] + \
         [(T_STAMP[0], "stamp"), (T_STAMP[0] + 0.05, "buzz"), (T_STAMP[1], "stamp"), (T_STAMP[1] + 0.05, "coin"),
          (T_STAMP[2], "stamp"), (T_STAMP[2] + 0.05, "ding"), (T_SUM, "register"), (T_SUM + 0.1, "coinrain"),
          (T_TIP - 0.6, "riser"), (T_TIP, "item"), (T_TIP + 0.3, "coinrain"), (T_TIP + 0.9, "jump")]


def mood_at(t):
    if t < T_STAMP[0]: return "neutral"
    if t < T_STAMP[1]: return "shock"
    return "happy"


def guy_state(t):
    for (j0, jd, hgt) in ((T_STAMP[2] + 0.05, 0.35, 12), (T_TIP - 0.45, 0.5, 14), (T_TIP + 0.9, 0.35, 12)):
        if j0 <= t < j0 + jd:
            p = (t - j0) / jd
            return GUY_X, GROUND_Y, None, int(hgt * 4 * p * (1 - p)), "up", 1.0
    arms = "down"
    if t >= T_SUM: arms = "up" if int(t * 4) % 2 else "down"
    return GUY_X, GROUND_Y, None, 0, arms, 1.0


def draw_icon(k, t):
    """small RGBA sprite (36x30), scaled 2x when pasted. Generic items, no brands, no logos."""
    im = Image.new("RGBA", (36, 30), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if k == 0:   # light-up desk gadget: a cube with an antenna and a blinking bulb
        d.rectangle([9, 10, 27, 28], fill=INK); d.rectangle([10, 11, 26, 27], fill=(120, 200, 220))
        d.rectangle([12, 14, 16, 18], fill=INK); d.rectangle([20, 14, 24, 18], fill=INK)
        d.rectangle([14, 22, 22, 23], fill=INK)
        d.line([18, 10, 18, 4], fill=INK, width=2)
        d.ellipse([15, 0, 21, 6], fill=(255, 90, 120) if int(t * 6) % 2 else (255, 220, 90))
    elif k == 1:  # winter jacket
        d.polygon([(10, 4), (26, 4), (33, 12), (30, 15), (28, 13), (28, 28), (8, 28), (8, 13), (6, 15), (3, 12)], fill=INK)
        d.polygon([(11, 5), (25, 5), (31, 12), (30, 13), (27, 11), (27, 27), (9, 27), (9, 11), (6, 13), (5, 12)], fill=(200, 70, 80))
        d.line([18, 6, 18, 27], fill=INK)
        for yy in (12, 17, 22): d.point((20, yy), fill=GOLD)
        d.polygon([(13, 5), (18, 9), (23, 5)], fill=(240, 230, 220))
    else:         # lunchbox with handle and a little apple sticker
        d.arc([11, 2, 25, 14], 180, 360, fill=INK, width=2)
        d.rectangle([5, 8, 31, 28], fill=INK); d.rectangle([6, 9, 30, 27], fill=(90, 190, 140))
        d.rectangle([6, 15, 30, 16], fill=INK)
        d.ellipse([22, 19, 28, 25], fill=RED); d.point((25, 18), fill=GREEN)
    return im.resize((72, 60), Image.NEAREST)


def frame(t):
    im, d = scene(t, name=SCENE)
    cur = max(k for k in range(3) if t >= T_ITEM[k])
    if t < T_SUM:
        k = cur
        slide = 0 if k == 0 else int((1 - ease_out(prog(t, T_ITEM[k], T_ITEM[k] + 0.25))) * 80)
        cx = 126 + slide
        name, price, value, rarity, col, _ = ITEMS[k]
        d.rectangle([cx - 44, 134, cx + 44, 236], fill=INK)
        d.rectangle([cx - 43, 135, cx + 43, 235], fill=(70, 60, 110))
        d.rectangle([cx - 43, 135, cx + 43, 137], fill=(120, 110, 170))
        text(d, name, cx, 141, WHITE, center=True)
        text(d, price, cx, 153, GOLD, center=True)
        text(d, value, cx, 164, (150, 255, 180) if k == 2 else (210, 210, 225), center=True)
        spr = draw_icon(k, t)
        bob = int(abs(math.sin(t * 4)) * 2)
        im.paste(spr, (cx - 36, 174 - bob), spr)
        d = ImageDraw.Draw(im); d.fontmode = "1"
        if t >= T_STAMP[k]:
            p = prog(t, T_STAMP[k], T_STAMP[k] + 0.12)
            grow = int((1 - p) * 6)
            d.rectangle([cx - 41 - grow, 206 - grow, cx + 41 + grow, 222 + grow], fill=INK)
            d.rectangle([cx - 40 - grow, 207 - grow, cx + 40 + grow, 221 + grow], fill=col)
            text(d, rarity, cx, 211, INK, shadow=False, center=True)
            if k == 2:   # legendary sparkle
                for q in range(8):
                    a = t * 4 + q * 0.785
                    if int(t * 10 + q) % 2: d.point((cx + int(math.cos(a) * 50), 214 + int(math.sin(a) * 18)), fill=GOLD_L)
    else:
        if t >= T_SUM + 0.2:
            im = plate(im, 98, 148, 0.72); d = ImageDraw.Draw(im); d.fontmode = "1"
            text(d, "+€780", 90, 102, GOLD, font=FONT_BIG, center=True)
            text(d, "A YEAR", 90, 122, WHITE, center=True)
            text(d, "LEGENDARY BUY", 90, 134, GOLD, center=True)
    # coins into the wallet with the sum and the tip
    for base_t in (T_SUM + 0.1, T_TIP + 0.3):
        for k in range(8):
            p = prog(t, base_t + k * 0.07, base_t + 0.6 + k * 0.07)
            if 0 < p < 1:
                coin_sprite(d, int(lerp(140, GUY_X, p)), int(lerp(200, GROUND_Y - 50, p) - 26 * math.sin(math.pi * p)), 3, t * 12 + k)
    item_box(d, t, GUY_X, 150, T_TIP - 0.6, T_TIP)
    paste_dime(im, t, GUY_X)
    d = ImageDraw.Draw(im); d.fontmode = "1"
    whp = 0.55 - 0.1 * (t >= T_STAMP[0]) + 0.1 * (t >= T_STAMP[1]) + 0.2 * (t >= T_STAMP[2]) + 0.15 * ease_out(prog(t, T_TIP + 0.3, T_TIP + 1.2))
    hud(d, t, whp, mood_at(t), tag="RATE THE PURCHASE")
    if t < T_SUM:
        im = plate(im, 64, 126, 0.45); d = ImageDraw.Draw(im); d.fontmode = "1"
    headline(d, t, ["WHICH BUY", "IS", "LEGENDARY?"], [WHITE, WHITE, GOLD], y0=67, step=20, t_end=T_SUM)
    if T_SUM <= t < T_CTA:
        text(d, "PRICE / USES", 90, 70, WHITE, center=True)
        text(d, "= REAL PRICE", 90, 82, (150, 255, 180), center=True)
    dialog_box(d, t, DIALOG, T_CTA)
    if t >= T_CTA: im = end_card(im, t, T_CTA)
    return post_fx(im, t, DUR, shakes=T_STAMP, white=[T_TIP])


run_quick(NAME, frame, DUR, T_CTA, EVENTS, DIALOG, cover_t=0.3, music="quiz", check=())
