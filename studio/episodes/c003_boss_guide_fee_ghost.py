# Carousel: BOSS GUIDE — Fee Ghost (pairs with ep007). Account + card + ATM fee, €5 each = €15/month = €180/year;
# switch to a free account + free ATMs = +€15/month = +€180/year.
exec(open("/home/claude/dime-money-quest/studio/carousel.py").read())

NAME = "c003_boss_guide_fee_ghost"
MCOLS, ghost = enemy_from("ep007_fee_ghost.py")


def ghosts(d, ground_y, n=3, attacking=(), x0=104, gap=26, s=1.0, cut=()):
    """the Fee Ghosts float 16 px above the ground (as in ep007); each carries a €5 tag"""
    for k in range(n):
        if k in cut: continue
        ghost(d, x0 + k * gap, ground_y - 16, MCOLS[k % 3], s, 0.3 + k * 0.4, k, k in attacking)


def flashlight(ld, gx, ghcy):
    hxp, hyp = gx + 10, GROUND_Y - 19 - 7
    fx0, fy0 = hxp, hyp - 6
    ld.rectangle([fx0 - 1, fy0 - 3, fx0 + 9, fy0 + 3], fill=INK)
    ld.rectangle([fx0, fy0 - 2, fx0 + 8, fy0 + 2], fill=(90, 90, 110))
    ld.rectangle([fx0 + 8, fy0 - 4, fx0 + 11, fy0 + 4], fill=INK)
    ld.rectangle([fx0 + 9, fy0 - 3, fx0 + 10, fy0 + 3], fill=GOLD_L)
    ld.point((fx0 + 3, fy0 - 1), fill=RED)


def s1(im, d):   # hook
    text(d, "BOSS GUIDE", CW // 2, 23, MINT, center=True)
    y = title(d, "THE FEE GHOST", 35, WHITE)
    para(d, "YOU NEVER SEE IT.", y + 2, GOLD, center=True)
    para(d, "IT TAKES €5. AGAIN.", y + 13, RED, center=True)
    text(d, "EXAMPLE NUMBERS", CW // 2, y + 27, GREY, center=True)   # here, not in the footer: the footer holds SWIPE
    ground(d, 197)
    dime(im, 40, 198, "shock", 2)
    d = ImageDraw.Draw(im); d.fontmode = "1"
    ghosts(d, 190, 3, attacking=(0,), x0=104, gap=26, s=0.9)


def s2(im, d):   # stat card
    y = title(d, "BOSS STATS", 26, GOLD)
    panel(d, 8, y + 2, CW - 9, y + 76)
    yy = y + 8
    yy = stat(d, "TYPE", "SILENT DRAIN", yy, WHITE)
    yy = stat(d, "HIDES IN", "STATEMENT", yy, MINT)
    yy = stat(d, "BITE", "€5/MONTH", yy, RED)
    yy = stat(d, "PACK OF 3", "€15/MONTH", yy, RED)
    yy = stat(d, "HP PER YEAR", "€180", yy, RED)
    ghosts(d, 196, 3, attacking=(1,), x0=58, gap=32, s=1.0)


def s3(im, d):   # how it attacks
    y = title(d, "HOW IT ATTACKS", 26, RED)
    steps(d, ["ACCOUNT FEE: €5 A MONTH",
              "CARD FEE: €5 A MONTH",
              "ATM FEES: €5 A MONTH",
              "NO ALERT. NO NOTICE. JUST GONE."], y + 6)


def s4(im, d):   # the damage, math
    y = title(d, "THE DAMAGE", 26, RED)
    panel(d, 8, y + 2, CW - 9, y + 66)
    para(d, "3 FEES X €5", y + 10, WHITE, center=True)
    para(d, "= €15 A MONTH", y + 24, WHITE, center=True)
    para(d, "€15 X 12 MONTHS", y + 42, WHITE, center=True)
    big(d, "-€180", y + 76, RED)
    para(d, "EVERY YEAR", y + 98, WHITE, center=True)
    dime(im, 30, 205, "sad", 1)


def s5(im, d):   # weak spot / power-up
    text(d, "WEAK SPOT", CW // 2, 26, MINT, center=True)
    y = title(d, "FLASHLIGHT", 40, GOLD)
    steps(d, ["OPEN YOUR BANK APP",
              "SEARCH \"FEE\" IN THE LAST 3 MONTHS",
              "ADD THEM UP. NOW YOU SEE THE GHOST"], y + 4)
    ground(d, 200)
    dime(im, 140, 201, "happy", 1, arms="up", item=flashlight)


def s6(im, d):   # loot
    y = title(d, "THE LOOT", 26, GOLD)
    panel(d, 8, y + 2, CW - 9, y + 52)
    para(d, "FREE ACCOUNT +", y + 10, WHITE, center=True)
    para(d, "FREE ATMS ONLY:", y + 22, WHITE, center=True)
    para(d, "3 X €5 = €15/MONTH", y + 36, WHITE, center=True)
    big(d, "+€180", y + 62, GOLD)
    para(d, "A YEAR, BACK TO YOU", y + 84, WHITE, center=True)
    ground(d, 200)
    dime(im, 50, 201, "happy", 1, arms="up")


def s7(im, d):   # quest for today
    text(d, "TODAY'S QUEST", CW // 2, 26, MINT, center=True)
    y = title(d, "10 MINUTES", 40, GOLD)
    steps(d, ["SEARCH \"FEE\" IN YOUR BANK APP",
              "LIST EVERY FEE + HOW OFTEN",
              "COMPARE 2 FREE ACCOUNTS",
              "NOTE THE FREE ATMS NEAR YOU"], y + 4)


run_carousel(NAME, [s1, s2, s3, s4, s5, s6, s7, end_slide("NEXT BOSS")],
             example=[False, True, True, True, False, True, False, False])   # slide 1 draws its own label
