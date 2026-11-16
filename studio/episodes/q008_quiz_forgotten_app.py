# Quick format: QUIZ. "€10/month app you forgot. 3 years = ?"  -> B €360 (€10 x 36 months).
# Tip: today search the bank app for repeating payments, cancel one you don't use: +€120 a year (€10 x 12), €360 in 3 years.
exec(open("/home/claude/dime-money-quest/studio/quick.py").read())

NAME = "q008_quiz_forgotten_app"
SCENE = "city_night"     # late-night scroll (previous reel ep012 used rain)
DUR, T_CTA = 11.5, 9.1
T_REV, T_JAR = 4.0, 6.2
T_HIT = T_JAR                      # Dime's happy sparkles start when the money comes back
DX = 150                           # Dime stands on the right, answers on the left
OPTS = [("A", "€120"), ("B", "€360"), ("C", "€990")]
RIGHT = 1
DIALOG = [(0.5, "AN APP YOU FORGOT: €10 A MONTH. 3 YEARS?"),
          (T_REV, "€10 X 36 MONTHS = €360. FOR NOTHING."),
          (T_JAR, "TODAY: SEARCH YOUR BANK APP. CANCEL 1 YOU DON'T USE.")]
EVENTS = [(0.0, "slam"), (0.1, "slam"), (0.2, "slam")] + \
         [(1.0 + k, "tick") for k in range(3)] + [(1.5 + k, "tick") for k in range(3)] + \
         [(T_REV - 0.05, "buzz"), (T_REV, "ding"), (T_REV + 0.1, "womp"),
          (T_JAR - 0.6, "riser"), (T_JAR, "item"), (T_JAR + 0.6, "coinrain"), (T_JAR + 1.3, "register"), (T_JAR + 1.4, "jump")]

def mood_at(t):
    if t < 1.0: return "shock"
    if t < T_REV: return "neutral"
    if t < T_JAR: return "shock"
    return "happy"

def guy_state(t):
    for (j0, jd, hgt) in ((T_REV + 0.05, 0.45, 18), (T_JAR + 1.4, 0.35, 12)):
        if j0 <= t < j0 + jd:
            p = (t - j0) / jd
            return GUY_X, GROUND_Y, None, int(hgt * 4 * p * (1 - p)), "up", 1.0
    arms = "down"
    if T_REV <= t < T_JAR: arms = "down"
    if t >= T_JAR: arms = "down"   # holds the jar at his side
    return GUY_X, GROUND_Y, None, 0, arms, 1.0

def option(d, y, k, t):
    letter, amt = OPTS[k]
    state = "idle" if t < T_REV else ("right" if k == RIGHT else "wrong")
    fill = {"idle": (60, 50, 95), "right": GREEN, "wrong": (80, 45, 70)}[state]
    if state == "right" and t < T_REV + 0.6 and int(t * 10) % 2: fill = GOLD
    x0, x1 = 4, 126
    pop = int(3 * math.sin(math.pi * prog(t, T_REV, T_REV + 0.25))) if state == "right" else 0
    d.rectangle([x0 - pop, y - 1 - pop, x1 + pop, y + 21 + pop], fill=INK)
    d.rectangle([x0 + 1 - pop, y - pop, x1 - 1 + pop, y + 20 + pop], fill=fill)
    d.rectangle([x0 + 1 - pop, y - pop, x1 - 1 + pop, y + 1 - pop], fill=mixc(fill, WHITE, 0.4))
    d.rectangle([x0 + 4, y + 4, x0 + 15, y + 16], fill=INK)
    text(d, letter, x0 + 6, y + 6, GOLD, shadow=False)
    text(d, amt, x0 + 20, y + 3, WHITE if state != "wrong" else (150, 130, 160), font=FONT_BIG)
    if state == "wrong":
        d.line([x0 + 18, y + 3, x1 - 6, y + 18], fill=RED, width=2); d.line([x0 + 18, y + 18, x1 - 6, y + 3], fill=RED, width=2)

def jar(ld, gx, ghcy, t):
    """savings jar held in Dime's left hand (screen side facing the answers) from the power-up on"""
    if t < T_JAR + 0.15: return
    hx, hy = gx - 13, GROUND_Y - 6 - (1 if int(t * 4) % 2 else 0)
    ld.rectangle([hx - 6, hy - 14, hx + 6, hy + 1], fill=INK)
    ld.rectangle([hx - 5, hy - 13, hx + 5, hy], fill=(170, 220, 240))
    ld.rectangle([hx - 4, hy - 16, hx + 4, hy - 14], fill=(150, 100, 60))
    fillh = int(10 * ease_out(prog(t, T_JAR + 0.6, T_JAR + 1.4)))
    if fillh: ld.rectangle([hx - 4, hy - fillh, hx + 4, hy - 1], fill=GOLD)
    ld.point((hx - 3, hy - 11), fill=WHITE)

def frame(t):
    im, d = scene(t, name=SCENE)
    if t < T_JAR:   # the answers clear away when the jar comes in
        for k in range(3): option(d, 134 + k * 26, k, t)
    # countdown 3-2-1 with a draining timer bar
    if 1.0 <= t < T_REV:
        left = 1 - prog(t, 1.0, T_REV)
        d.rectangle([4, 214, 126, 220], fill=INK)
        d.rectangle([5, 215, 5 + int(120 * left), 219], fill=GOLD if left > 0.34 else RED)
        num = str(3 - int((t - 1.0)))
        sc = int(3 * (1 - prog((t - 1.0) % 1.0, 0.0, 0.15)))   # little hop on each new number
        text(d, num, 60, 226 - sc, WHITE, font=FONT_BIG, center=True)
    # thinking bubble
    if 0.6 <= t < T_REV:
        bx, by = DX + 16, 136
        d.ellipse([bx - 12, by - 10, bx + 12, by + 10], fill=WHITE)
        d.ellipse([bx - 18, by + 12, bx - 13, by + 17], fill=WHITE); d.ellipse([bx - 22, by + 20, bx - 19, by + 23], fill=WHITE)
        text(d, "?", bx - 4, by - 4, INK if int(t * 3) % 2 else RED, shadow=False)
    # coins raining into Dime after the right answer and into the jar
    for base in (T_JAR + 0.6,):
        for k in range(8):
            p = prog(t, base + k * 0.07, base + 0.6 + k * 0.07)
            if 0 < p < 1:
                sx = 60 if base == T_REV else 60
                tx, ty = (DX, 170) if base == T_REV else (DX - 26, 226)
                coin_sprite(d, int(lerp(sx + k * 6, tx, p)), int(lerp(150, ty, p) - 30 * math.sin(math.pi * p)), 3, t * 12 + k)
    item_box(d, t, DX + 20, 120, T_JAR - 0.6, T_JAR)
    paste_dime(im, t, DX, extra=jar)
    d = ImageDraw.Draw(im); d.fontmode = "1"
    whp = 0.75 - 0.3 * ease_out(prog(t, T_REV, T_REV + 0.4)) + 0.45 * ease_out(prog(t, T_JAR + 0.6, T_JAR + 1.4))
    if t < T_CTA:   # dark plate behind the headline / math line so the moon never sits behind text
        im = plate(im, 64, 130 if t < T_REV else 132, 0.85); d = ImageDraw.Draw(im); d.fontmode = "1"
        if T_REV + 0.3 <= t < T_JAR:
            text(d, "-€360", 90, 104, RED, font=FONT_BIG, center=True); text(d, "IN 3 YEARS", 90, 122, WHITE, center=True)
        if T_JAR + 0.3 <= t:
            text(d, "+€120", 90, 104, GOLD, font=FONT_BIG, center=True); text(d, "A YEAR BACK", 90, 122, WHITE, center=True)
    hud(d, t, whp, mood_at(t), tag="QUIZ!")
    headline(d, t, ["€10/MONTH", "UNUSED APP", "3 YEARS=?"], [WHITE, WHITE, GOLD], y0=66, t_end=T_REV)
    if T_REV <= t < T_JAR:
        text(d, "€10 A MONTH X 36", 90, 70, WHITE, center=True)
    if T_JAR <= t < T_CTA:
        text(d, "CANCEL 1: €10 X 12", 90, 70, (150, 255, 180), center=True)
    dialog_box(d, t, DIALOG, T_CTA)
    if t >= T_CTA: im = end_card(im, t, T_CTA)
    return post_fx(im, t, DUR, shakes=[0.0, T_REV], red=[T_REV], white=[T_JAR])

run_quick(NAME, frame, DUR, T_CTA, EVENTS, DIALOG, cover_t=0.3, music="quiz", check=())
