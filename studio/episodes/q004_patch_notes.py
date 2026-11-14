# Quick format: PATCH NOTES. Dime's budget update v1.1:
# NERF takeout €120 -> €80 (-€40/month) · NERF subscriptions €35 -> €15 (-€20/month) · BUFF savings €0 -> €60/month.
# €40 + €20 = €60 a month to savings; €60 x 12 = €720 a year. Tip: nerf 2 costs today, auto-save the difference on payday.
exec(open("/home/claude/dime-money-quest/studio/quick.py").read())

NAME = "q004_patch_notes"
DUR, T_CTA = 12.0, 9.6
# (card label, before, after, verdict, dialog)
ITEMS = [("TAKEOUT", 120, 80, "NERF", "TAKEOUT: €120 A MONTH. NOW €80."),
         ("SUBS", 35, 15, "NERF", "SUBSCRIPTIONS: €35 A MONTH. NOW €15."),
         ("SAVINGS", 0, 60, "BUFF", "SAVINGS: €0 A MONTH. NOW €60.")]
T_ITEM = [0.0, 1.9, 3.8]
T_STAMP = [1.2, 3.1, 5.0]
T_SUM, T_TIP = 5.8, 7.4
DIALOG = [(T_ITEM[k], ITEMS[k][4]) for k in range(3)] + \
         [(T_SUM, "€40 + €20 = €60 A MONTH. X12 = €720 A YEAR."),
          (T_TIP, "TIP: NERF 2 COSTS TODAY. AUTO-SAVE THE GAP ON PAYDAY.")]
EVENTS = [(0.0, "slam"), (0.1, "slam"), (0.2, "slam")] + [(t, "tick") for t in T_ITEM[1:]] + \
         [(T_STAMP[0], "stamp"), (T_STAMP[0] + 0.05, "buzz"), (T_STAMP[1], "stamp"), (T_STAMP[1] + 0.05, "buzz"),
          (T_STAMP[2], "stamp"), (T_STAMP[2] + 0.05, "ding"), (T_SUM, "register"), (T_SUM + 0.1, "coinrain"),
          (T_TIP - 0.6, "riser"), (T_TIP, "item"), (T_TIP + 0.3, "coinrain"), (T_TIP + 0.9, "jump")]


def mood_at(t):
    if t < T_STAMP[0]: return "neutral"
    if t < T_STAMP[2]: return "shock"
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
    """small RGBA sprite (36x30), scaled 2x when pasted. No brands, no logos."""
    im = Image.new("RGBA", (36, 30), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if k == 0:   # takeout bag
        d.polygon([(8, 9), (28, 9), (30, 28), (6, 28)], fill=INK)
        d.polygon([(9, 10), (27, 10), (29, 27), (7, 27)], fill=(200, 150, 90))
        d.arc([12, 2, 24, 14], 180, 360, fill=INK, width=2)
        d.rectangle([12, 16, 24, 20], fill=(150, 100, 60))
    elif k == 1:  # TV screen with a play triangle
        d.rectangle([4, 4, 32, 24], fill=INK); d.rectangle([5, 5, 31, 23], fill=(60, 60, 90))
        d.polygon([(15, 9), (15, 19), (23, 14)], fill=WHITE)
        d.line([14, 25, 10, 29], fill=INK, width=2); d.line([22, 25, 26, 29], fill=INK, width=2)
    else:         # piggy-bank style coin jar
        d.rectangle([9, 6, 27, 28], fill=INK); d.rectangle([10, 7, 26, 27], fill=(170, 220, 255))
        d.rectangle([8, 3, 28, 7], fill=INK); d.rectangle([9, 4, 27, 6], fill=(120, 80, 50))
        n = 1 + int(min(1.0, prog(t, T_STAMP[2], T_STAMP[2] + 0.6)) * 4)
        for q in range(n):
            d.ellipse([12 + (q % 2) * 6, 21 - q * 4, 18 + (q % 2) * 6, 26 - q * 4], fill=GOLD)
    return im.resize((72, 60), Image.NEAREST)


def frame(t):
    im, d = scene(t, sky=7)
    cur = max(k for k in range(3) if t >= T_ITEM[k])
    if t < T_SUM:
        k = cur
        slide = 0 if k == 0 else int((1 - ease_out(prog(t, T_ITEM[k], T_ITEM[k] + 0.25))) * 80)
        cx = 128 + slide
        name, before, after, verdict, _ = ITEMS[k]
        d.rectangle([cx - 40, 134, cx + 40, 236], fill=INK)
        d.rectangle([cx - 39, 135, cx + 39, 235], fill=(70, 60, 110))
        d.rectangle([cx - 39, 135, cx + 39, 137], fill=(120, 110, 170))
        text(d, name, cx, 141, WHITE, center=True)
        text(d, f"€{before}>€{after}", cx, 153, GOLD, center=True)
        text(d, "A MONTH", cx, 163, (200, 200, 215), center=True)
        spr = draw_icon(k, t)
        bob = int(abs(math.sin(t * 4)) * 2)
        im.paste(spr, (cx - 36, 174 - bob), spr)
        d = ImageDraw.Draw(im); d.fontmode = "1"
        if t >= T_STAMP[k]:
            p = prog(t, T_STAMP[k], T_STAMP[k] + 0.12)
            col = RED if verdict == "NERF" else GREEN
            grow = int((1 - p) * 8)
            d.rectangle([cx - 36 - grow, 190 - grow, cx + 36 + grow, 216 + grow], fill=INK)
            d.rectangle([cx - 34 - grow, 192 - grow, cx + 34 + grow, 214 + grow], outline=col, width=2)
            text(d, verdict, cx, 196, col, font=FONT_BIG, center=True)
    else:
        if t >= T_SUM + 0.2:
            text(d, "+€720", 132, 136, GOLD, font=FONT_BIG, center=True)
            text(d, "A YEAR", 132, 156, WHITE, center=True)
            text(d, "TO SAVINGS", 132, 168, (150, 255, 180), center=True)
    # running patch log
    cut = sum(ITEMS[k][1] - ITEMS[k][2] for k in range(2) if t >= T_STAMP[k])
    saved = ITEMS[2][2] if t >= T_STAMP[2] else 0
    text(d, f"CUT €{cut}", 6, 125, RED)
    stxt = f"SAVE €{saved}"
    text(d, stxt, 174 - int(d.textlength(stxt, font=FONT)), 125, (150, 255, 180))
    # coins into the wallet with the sum and the tip
    for base_t in (T_SUM + 0.1, T_TIP + 0.3):
        for k in range(8):
            p = prog(t, base_t + k * 0.07, base_t + 0.6 + k * 0.07)
            if 0 < p < 1:
                coin_sprite(d, int(lerp(140, GUY_X, p)), int(lerp(200, GROUND_Y - 50, p) - 26 * math.sin(math.pi * p)), 3, t * 12 + k)
    item_box(d, t, GUY_X, 150, T_TIP - 0.6, T_TIP)
    paste_dime(im, t, GUY_X)
    d = ImageDraw.Draw(im); d.fontmode = "1"
    whp = 0.55 + 0.1 * (t >= T_STAMP[0]) + 0.05 * (t >= T_STAMP[1]) + 0.15 * (t >= T_STAMP[2]) + 0.1 * ease_out(prog(t, T_TIP + 0.3, T_TIP + 1.2))
    hud(d, t, whp, mood_at(t), tag="PATCH NOTES v1.1")
    headline(d, t, ["BUDGET", "UPDATE", "IS LIVE"], [WHITE, GOLD, (150, 255, 180)], y0=65, step=20, t_end=T_SUM)
    if t >= T_SUM and t < T_CTA:
        text(d, "PATCH v1.1 DONE", 90, 70, WHITE, center=True)
    dialog_box(d, t, DIALOG, T_CTA)
    if t >= T_CTA: im = end_card(im, t, T_CTA)
    return post_fx(im, t, DUR, shakes=T_STAMP, white=[T_TIP])


run_quick(NAME, frame, DUR, T_CTA, EVENTS, DIALOG, cover_t=0.3, music="quiz", check=(0, 45, 100, 160, 190, 240, 288, 303, 350))
