# Quick format: SPEEDRUN. "Payday speedrun: sort €1,600 pay in 60 seconds" -> 3 key moves:
# 1. BILLS €800 (rent + bills) · 2. SAVE €200 first · 3. SPEND €600 / 4 weeks = €150 a week.  800 + 200 + 600 = 1,600.
# Payoff: €200 x 12 = €2,400 saved a year. Clear time 0:47. Tip: today write down your 3 numbers (bills, save, spend).
exec(open("/home/claude/dime-money-quest/studio/quick.py").read())

NAME = "q007_payday_speedrun"
SCENE = "apartment"      # payday at home (previous reel q006 used synthwave; next reel ep011 uses sunset)
DUR, T_CTA = 11.8, 9.4
T_RUN = 1.0                                  # timer starts
T_MOVE = [1.4, 3.0, 4.6]                     # the three moves slam in
T_CLEAR, T_TIP = 6.2, 7.6
CLEAR_S = 47                                 # in-game clear time 0:47
DX = 150                                     # Dime on the right, the run on the left
ROWS = [("1", "BILLS €800", "RENT+BILLS", GREEN),
        ("2", "SAVE €200", "BEFORE FUN", GOLD),
        ("3", "SPEND €600", "€150/WEEK", (90, 140, 255))]
DIALOG = [(T_MOVE[0], "MOVE 1: BILLS FIRST. RENT + BILLS: €800."),
          (T_MOVE[1], "MOVE 2: SAVE €200 BEFORE YOU SPEND."),
          (T_MOVE[2], "MOVE 3: €600 LEFT / 4 WEEKS = €150 A WEEK."),
          (T_CLEAR, "€200 X 12 = €2,400 SAVED A YEAR."),
          (T_TIP, "TODAY: WRITE DOWN YOUR 3 NUMBERS. 60 SEC.")]
EVENTS = [(0.0, "slam"), (0.1, "slam"), (0.2, "slam")] + \
         [(T_RUN + 0.25 * k, "tick") for k in range(2)] + \
         [(T_MOVE[0], "stamp"), (T_MOVE[0] + 0.05, "coin"), (T_MOVE[1], "stamp"), (T_MOVE[1] + 0.05, "coinrain"),
          (T_MOVE[2], "stamp"), (T_MOVE[2] + 0.05, "coin"), (T_MOVE[2] + 0.8, "tick"), (T_MOVE[2] + 1.1, "tick"),
          (T_CLEAR, "ding"), (T_CLEAR + 0.05, "jump"), (T_CLEAR + 0.1, "register"),
          (T_TIP - 0.6, "riser"), (T_TIP, "item"), (T_TIP + 0.3, "coinrain"), (T_TIP + 1.0, "jump")]


def mood_at(t):
    if t < T_RUN: return "shock"
    if t < T_CLEAR: return "neutral"
    return "happy"


def guy_state(t):
    for (j0, jd, hgt) in [(m - 0.05, 0.3, 8) for m in T_MOVE] + [(T_CLEAR + 0.05, 0.45, 18), (T_TIP - 0.45, 0.5, 14), (T_TIP + 1.0, 0.35, 12)]:
        if j0 <= t < j0 + jd:
            p = (t - j0) / jd
            return GUY_X, GROUND_Y, None, int(hgt * 4 * p * (1 - p)), "up", 1.0
    arms = "down"
    if T_RUN <= t < T_CLEAR: arms = "up" if int(t * 6) % 2 else "down"     # frantic speedrun arms
    if T_CLEAR <= t < T_TIP: arms = "up" if int(t * 4) % 2 else "down"
    return GUY_X, GROUND_Y, None, 0, arms, 1.0


def game_time(t):
    """real 1.0 s .. 6.2 s -> in-game 0:00 .. 0:47"""
    return int(CLEAR_S * prog(t, T_RUN, T_CLEAR))


def row(d, y, k, t):
    num, main, sub, col = ROWS[k]
    p = prog(t, T_MOVE[k], T_MOVE[k] + 0.15)
    slide = int((1 - ease_out(p)) * 70)
    x0, x1 = 4 - slide, 126 - slide
    d.rectangle([x0, y - 1, x1, y + 23], fill=INK)
    d.rectangle([x0 + 1, y, x1 - 1, y + 22], fill=(60, 50, 95))
    d.rectangle([x0 + 1, y, x1 - 1, y + 1], fill=(110, 100, 160))
    d.rectangle([x0 + 4, y + 5, x0 + 15, y + 17], fill=col)
    text(d, num, x0 + 6, y + 7, INK, shadow=False)
    text(d, main, x0 + 20, y + 3, WHITE, shadow=False)
    text(d, sub, x0 + 20, y + 13, col, shadow=False)
    if t >= T_MOVE[k] + 0.2:   # split check mark
        d.line([x1 - 13, y + 11, x1 - 9, y + 15], fill=GREEN, width=2); d.line([x1 - 9, y + 15, x1 - 3, y + 6], fill=GREEN, width=2)


def frame(t):
    im, d = paint_scene(SCENE, t)
    # the pay pile on the left before the run: one big stack of coins
    if t < T_MOVE[2] + 0.2:
        left = 1.0 - 0.33 * sum(1 for m in T_MOVE if t >= m)
        n = max(1, int(8 * left))
        for q in range(n):
            coin_sprite(d, 112 - (q % 2) * 4, 238 - q * 5, 4, t * 3 + q)
    for k in range(3):
        if t >= T_MOVE[k]: row(d, 132 + k * 27, k, t)
    # coins flying from the pile into each row as it lands
    for k in range(3):
        for q in range(5):
            p = prog(t, T_MOVE[k] + q * 0.05, T_MOVE[k] + 0.45 + q * 0.05)
            if 0 < p < 1:
                coin_sprite(d, int(lerp(112, 30, p)), int(lerp(230, 143 + k * 27, p) - 20 * math.sin(math.pi * p)), 3, t * 12 + q)
    item_box(d, t, DX + 20, 120, T_TIP - 0.6, T_TIP)
    paste_dime(im, t, DX)
    d = ImageDraw.Draw(im); d.fontmode = "1"
    whp = 0.5 + 0.12 * sum(1 for m in T_MOVE if t >= m) + 0.14 * ease_out(prog(t, T_CLEAR, T_CLEAR + 0.8))
    hud(d, t, whp, mood_at(t), tag="SPEEDRUN")
    headline(d, t, ["PAYDAY", "SPEEDRUN", "60 SECONDS"], [WHITE, GOLD, WHITE], y0=68, t_end=T_RUN + 0.3)
    if T_RUN + 0.3 <= t < T_CTA:
        gt = game_time(t)
        clear = t >= T_CLEAR
        col = GOLD if clear else (WHITE if gt < 40 else RED)
        text(d, f"0:{gt:02d}", 90, 70, col, font=FONT_BIG, center=True)
        if not clear:
            text(d, "€1,600 PAY", 90, 92, (210, 210, 225), center=True)
            text(d, f"MOVES {sum(1 for m in T_MOVE if t >= m)}/3", 90, 104, (150, 255, 180), center=True)
        else:
            if int(t * 6) % 3 or t > T_CLEAR + 0.6: text(d, "CLEAR!", 90, 88, (150, 255, 180), center=True)
            if t >= T_CLEAR + 0.3:
                text(d, "+€2,400", 66, 98, GOLD, font=FONT_BIG, center=True)
                text(d, "SAVED A YEAR", 66, 116, WHITE, center=True)
    if T_CLEAR <= t < T_CLEAR + 1.6: confetti(d, t, T_CLEAR)
    dialog_box(d, t, DIALOG, T_CTA)
    if t >= T_CTA: im = end_card(im, t, T_CTA)
    return post_fx(im, t, DUR, shakes=[0.0] + T_MOVE, white=[T_CLEAR, T_TIP])


run_quick(NAME, frame, DUR, T_CTA, EVENTS, DIALOG, cover_t=0.3, music="battle", check=())
