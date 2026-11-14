# Carousel: BOSS GUIDE — Trial Trap (pairs with ep005). 4 trials x €9 = €36/month = €432/year; cancel 2 = €18/month = €216/year.
exec(open("/home/claude/dime-money-quest/studio/carousel.py").read())

NAME = "c001_boss_guide_trial_trap"
MCOLS, box = enemy_from("ep005_trial_trap.py")


def boxes(d, y, n=4, attacking=(0,), x0=48, gap=28, s=1.0, cut=()):
    for k in range(n):
        if k in cut: continue
        box(d, x0 + k * gap, y, MCOLS[k % 4], s, 0.3, k, k in attacking)


def s1(im, d):   # hook
    text(d, "BOSS GUIDE", CW // 2, 23, MINT, center=True)
    y = title(d, "THE TRIAL TRAP", 35, WHITE)
    para(d, "IT LOOKS FREE.", y + 2, GOLD, center=True)
    para(d, "THEN IT BITES.", y + 13, RED, center=True)
    para(d, "EVERY MONTH.", y + 24, RED, center=True)
    ground(d, 197)
    dime(im, 46, 198, "shock", 2)
    d = ImageDraw.Draw(im); d.fontmode = "1"
    boxes(d, 197, 3, attacking=(0, 1, 2), x0=100, gap=26)


def s2(im, d):   # stat card
    y = title(d, "BOSS STATS", 26, GOLD)
    panel(d, 8, y + 2, CW - 9, y + 76)
    yy = y + 8
    yy = stat(d, "TYPE", "AUTO-RENEW", yy, WHITE)
    yy = stat(d, "DISGUISE", "\"FREE\"", yy, MINT)
    yy = stat(d, "BITE", "€9/MONTH", yy, RED)
    yy = stat(d, "PACK OF 4", "€36/MONTH", yy, RED)
    yy = stat(d, "HP PER YEAR", "€432", yy, RED)
    boxes(d, 196, 4, attacking=(1,), x0=48, gap=28)


def s3(im, d):   # how it attacks
    y = title(d, "HOW IT ATTACKS", 26, RED)
    steps(d, ["YOU ENTER YOUR CARD FOR A \"FREE\" TRIAL",
              "YOU FORGET THE END DATE",
              "DAY 31: €9 GONE. AND NEXT MONTH. AND THE NEXT."], y + 6)


def s4(im, d):   # the damage, math
    y = title(d, "THE DAMAGE", 26, RED)
    panel(d, 8, y + 2, CW - 9, y + 66)
    para(d, "4 TRIALS X €9", y + 10, WHITE, center=True)
    para(d, "= €36 A MONTH", y + 24, WHITE, center=True)
    para(d, "€36 X 12 MONTHS", y + 42, WHITE, center=True)
    big(d, "-€432", y + 76, RED)
    para(d, "EVERY YEAR", y + 98, WHITE, center=True)
    dime(im, 30, 205, "sad", 1)


def clock(ld, gx, ghcy):
    hxp, hyp = gx + 10, GROUND_Y - 19 - 7
    cx_, cy_ = hxp + 6, hyp - 8
    for sgn in (-1, 1):
        ld.ellipse([cx_ + sgn * 5 - 3, cy_ - 9, cx_ + sgn * 5 + 3, cy_ - 4], fill=INK)
        ld.ellipse([cx_ + sgn * 5 - 2, cy_ - 8, cx_ + sgn * 5 + 2, cy_ - 5], fill=GOLD)
    ld.ellipse([cx_ - 7, cy_ - 7, cx_ + 7, cy_ + 7], fill=INK)
    ld.ellipse([cx_ - 6, cy_ - 6, cx_ + 6, cy_ + 6], fill=RED)
    ld.ellipse([cx_ - 4, cy_ - 4, cx_ + 4, cy_ + 4], fill=WHITE)
    ld.line([cx_, cy_, cx_, cy_ - 3], fill=INK); ld.line([cx_, cy_, cx_ + 2, cy_], fill=INK)
    ld.line([hxp, hyp, cx_ - 3, cy_ + 6], fill=(120, 80, 50), width=2)


def s5(im, d):   # weak spot / power-up
    text(d, "WEAK SPOT", CW // 2, 26, MINT, center=True)
    y = title(d, "DAY-ONE ALARM", 40, GOLD)
    steps(d, ["SIGN UP",
              "SAME MINUTE: SET A REMINDER 2 DAYS BEFORE IT ENDS",
              "STILL USING IT? KEEP IT. IF NOT: CANCEL"], y + 4)
    ground(d, 200)
    dime(im, 140, 201, "happy", 1, arms="up", item=clock)


def s6(im, d):   # loot
    y = title(d, "THE LOOT", 26, GOLD)
    panel(d, 8, y + 2, CW - 9, y + 52)
    para(d, "CANCEL THE 2", y + 10, WHITE, center=True)
    para(d, "YOU DON'T USE:", y + 22, WHITE, center=True)
    para(d, "2 X €9 = €18/MONTH", y + 36, WHITE, center=True)
    big(d, "+€216", y + 62, GOLD)
    para(d, "A YEAR, BACK TO YOU", y + 84, WHITE, center=True)
    ground(d, 200)
    boxes(d, 200, 4, attacking=(), x0=86, gap=28, s=0.7, cut=(1, 3))
    dime(im, 50, 201, "happy", 1, arms="up")


def s7(im, d):   # quest for today
    text(d, "TODAY'S QUEST", CW // 2, 26, MINT, center=True)
    y = title(d, "5 MINUTES", 40, GOLD)
    steps(d, ["OPEN YOUR BANK APP",
              "SEARCH \"TRIAL\" AND YOUR LAST 3 MONTHS",
              "LIST EVERY ONE THAT RENEWS + ITS DATE",
              "CANCEL WHAT YOU DON'T USE"], y + 4)


run_carousel(NAME, [s1, s2, s3, s4, s5, s6, s7, end_slide("NEXT BOSS")],
             example=[False, True, True, True, False, True, False, False])
