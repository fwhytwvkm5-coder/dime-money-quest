# Quick format: DIME REACTS to "€5 a day is nothing".
# €5 x 365 days = €1,825 a year. Tip: pick your €5 daily habit and skip it 2 days a week: €5 x 2 = €10 a week; x 52 = €520 a year.
exec(open("/home/claude/dime-money-quest/studio/quick.py").read())

NAME = "q006_dime_reacts_5_a_day"
SCENE = "synthwave"     # loud hook look (previous reel ep010 uses apartment)
DUR, T_CTA = 11.8, 9.4
T_REACT = 1.0                     # Dime's double take
T_CALC, T_SUM = 2.2, 3.4          # calculator: €5 x 365, then = €1,825
T_BOX, T_GRAB, T_PAY = 5.2, 5.8, 6.9
DIALOG = [(2.0, "€5 A DAY X 365 DAYS..."),
          (T_SUM, "...IS €1,825 A YEAR. NOT NOTHING."),
          (T_BOX, "TIP: PICK YOUR €5 HABIT. SKIP IT 2 DAYS A WEEK."),
          (T_PAY, "€5 X 2 = €10 A WEEK. X52 = €520 A YEAR.")]
EVENTS = [(0.0, "slam"), (0.1, "slam"), (0.2, "slam"), (T_REACT, "buzz"), (T_REACT + 0.05, "punch"),
          (T_CALC, "tick"), (T_CALC + 0.3, "tick"), (T_SUM, "womp"), (T_SUM + 0.05, "register"),
          (T_GRAB - 0.6, "riser"), (T_GRAB, "item"), (T_PAY, "ding"), (T_PAY + 0.1, "coinrain"), (T_PAY + 0.3, "jump")]


def mood_at(t):
    if t < T_REACT: return "neutral"
    if t < T_SUM: return "shock"
    if t < T_GRAB: return "sad"
    return "happy"


def guy_state(t):
    x = GUY_X
    if T_REACT <= t < T_REACT + 0.35:            # double take: a little hop back
        p = (t - T_REACT) / 0.35
        return x - int(6 * math.sin(math.pi * p)), GROUND_Y, None, int(10 * 4 * p * (1 - p)), "up", 1.0
    for (j0, jd, hgt) in ((T_GRAB - 0.45, 0.5, 20), (T_PAY + 0.3, 0.35, 14), (T_PAY + 0.8, 0.35, 12)):
        if j0 <= t < j0 + jd:
            p = (t - j0) / jd
            return x, GROUND_Y, None, int(hgt * 4 * p * (1 - p)), "up", 1.0
    arms = "down"
    if mood_at(t) == "happy" and t > T_PAY: arms = "up" if int(t * 4) % 2 else "down"
    return x, GROUND_Y, None, 0, arms, 1.0


def cup(d, cx, cy, t):
    """a generic paper cup with steam: the daily €5 habit (no brand)"""
    d.polygon([(cx - 9, cy - 12), (cx + 9, cy - 12), (cx + 7, cy + 12), (cx - 7, cy + 12)], fill=INK)
    d.polygon([(cx - 8, cy - 11), (cx + 8, cy - 11), (cx + 6, cy + 11), (cx - 6, cy + 11)], fill=(240, 235, 225))
    d.rectangle([cx - 10, cy - 15, cx + 10, cy - 11], fill=INK); d.rectangle([cx - 9, cy - 14, cx + 9, cy - 12], fill=(120, 80, 60))
    d.rectangle([cx - 7, cy - 3, cx + 7, cy + 3], fill=(150, 100, 70))
    for k in range(3):
        sx = cx - 5 + k * 5; ph = int(t * 6 + k) % 3
        d.line([sx, cy - 18 - ph, sx + 1, cy - 22 - ph], fill=(230, 230, 240))


def frame(t):
    im, d = scene(t, name=SCENE)
    # the habit: a cup with a €5 tag, bobbing on the right
    if t < T_GRAB:
        bob = int(math.sin(t * 4) * 2)
        cup(d, 140, 214 + bob, t)
        d.rectangle([126, 234 + bob, 154, 244 + bob], fill=INK); d.rectangle([127, 235 + bob, 153, 243 + bob], fill=GOLD)
        d.text((133, 236 + bob), "€5", font=FONT, fill=INK)
    elif t < T_GRAB + 0.5:   # skipped: the cup poofs
        pp = prog(t, T_GRAB, T_GRAB + 0.5)
        for a in range(10):
            ang = a * math.pi / 5; r = int(4 + pp * 18)
            d.rectangle([140 + int(math.cos(ang) * r) - 1, 214 + int(math.sin(ang) * r) - 1, 140 + int(math.cos(ang) * r) + 1, 214 + int(math.sin(ang) * r) + 1], fill=WHITE if a % 2 else GOLD)
    # calculator panel
    if T_CALC <= t < T_BOX:
        d.rectangle([14, 70, 166, 122], fill=INK); d.rectangle([15, 71, 165, 121], outline=(150, 255, 180))
        text(d, "€5 X 365 DAYS", 90, 78, WHITE, center=True)
        if t >= T_SUM:
            p = prog(t, T_SUM, T_SUM + 0.1)
            text(d, "= €1,825", 90, 92 - int((1 - p) * 4), RED, font=FONT_BIG, center=True)
            text(d, "A YEAR", 90, 111, WHITE, center=True)
    if T_REACT <= t < T_CALC:
        p = prog(t, T_REACT, T_REACT + 0.12)
        text(d, "WAIT...", 90, 96 - int((1 - p) * 6), GOLD, font=FONT_BIG, center=True)
    if t >= T_PAY + 0.1 and t < T_CTA:
        im = plate(im, 96, 136, 0.55); d = ImageDraw.Draw(im); d.fontmode = "1"
        text(d, "+€520", 90, 100, GOLD, font=FONT_BIG, center=True)
        text(d, "A YEAR", 90, 122, WHITE, center=True)
    for k in range(8):
        p = prog(t, T_PAY + 0.1 + k * 0.07, T_PAY + 0.7 + k * 0.07)
        if 0 < p < 1:
            coin_sprite(d, int(lerp(140, GUY_X, p)), int(lerp(214, GROUND_Y - 50, p) - 26 * math.sin(math.pi * p)), 3, t * 12 + k)
    item_box(d, t, GUY_X, 150, T_BOX, T_GRAB)
    paste_dime(im, t, GUY_X)
    d = ImageDraw.Draw(im); d.fontmode = "1"
    whp = 0.75 - 0.25 * ease_out(prog(t, T_SUM, T_SUM + 0.4)) + 0.3 * ease_out(prog(t, T_PAY + 0.1, T_PAY + 1.0))
    hud(d, t, whp, mood_at(t), tag="DIME REACTS")
    if t < T_REACT:
        im = plate(im, 64, 128, 0.5); d = ImageDraw.Draw(im); d.fontmode = "1"
    headline(d, t, ["\"€5 A DAY", "IS NOTHING", "...RIGHT?\""], [WHITE, WHITE, GOLD], y0=68, step=20, t_end=T_REACT)
    dialog_box(d, t, DIALOG, T_CTA)
    if t >= T_CTA: im = end_card(im, t, T_CTA)
    return post_fx(im, t, DUR, shakes=[T_REACT, T_SUM], red=[T_SUM], white=[T_GRAB])


run_quick(NAME, frame, DUR, T_CTA, EVENTS, DIALOG, cover_t=0.4, music="battle", check=())
