# Carousel: SPOT THE LEAK — a made-up bank statement (no real brands). 3 leaks:
# 2nd video app €13 + gym not used since August €30 + account fee €5 = €48 a month; €48 x 12 = €576 a year.
# Today's quest: open your bank app, scroll 30 days, circle doubles, things you stopped using and fees.
exec(open("/home/claude/dime-money-quest/studio/carousel.py").read())

NAME = "c002_spot_the_leak_statement"
ROWS = [("RENT", "-€650"), ("GROCERIES", "-€62"), ("VIDEO APP A", "-€13"), ("PHONE", "-€20"),
        ("VIDEO APP B", "-€13"), ("GYM", "-€30"), ("BUS PASS", "-€49"), ("ACCOUNT FEE", "-€5")]
LEAKS = (4, 5, 7)


def statement(d, y, mark=(), dim=False):
    """the made-up statement: 8 rows, leaks in `mark` get a red box"""
    panel(d, 8, y, CW - 9, y + 106, (235, 232, 222))
    d.rectangle([8, y, CW - 9, y + 10], fill=(70, 80, 130))
    text(d, "MY ACCOUNT  NOV", 12, y + 2, WHITE, shadow=False)
    for i, (lab, amt) in enumerate(ROWS):
        yy = y + 14 + i * 11
        col = (150, 150, 160) if (dim and i not in mark) else INK
        text(d, lab, 12, yy, col, shadow=False)
        text(d, amt, CW - 12 - int(d.textlength(amt, font=FONT)), yy, RED if i in mark else col, shadow=False)
        if i in mark:
            d.rectangle([10, yy - 2, CW - 11, yy + 8], outline=RED)
    return y + 106


def magnifier(ld, gx, ghcy):
    hxp, hyp = gx + 10, GROUND_Y - 19 - 7
    cx_, cy_ = hxp + 6, hyp - 9
    ld.line([hxp, hyp, cx_ - 3, cy_ + 3], fill=(120, 80, 50), width=2)
    ld.ellipse([cx_ - 6, cy_ - 6, cx_ + 6, cy_ + 6], fill=INK)
    ld.ellipse([cx_ - 4, cy_ - 4, cx_ + 4, cy_ + 4], fill=(170, 220, 255))
    ld.point((cx_ - 2, cy_ - 2), fill=WHITE)


def s1(im, d):   # hook
    text(d, "SPOT THE LEAK", CW // 2, 24, MINT, center=True)
    y = title(d, "3 LEAKS HIDE HERE", 36, WHITE)
    para(d, "CAN YOU FIND ALL 3", y + 4, GOLD, center=True)
    para(d, "BEFORE THE ANSWER?", y + 15, GOLD, center=True)
    ground(d, 197)
    dime(im, 48, 198, "shock", 2, arms="up", item=magnifier)
    d = ImageDraw.Draw(im); d.fontmode = "1"
    # a little statement sheet with a question mark
    d.rectangle([111, 131, 161, 195], fill=INK); d.rectangle([112, 132, 160, 194], fill=(235, 232, 222))
    d.rectangle([112, 132, 160, 139], fill=(70, 80, 130))
    for k in range(6):
        d.rectangle([116, 145 + k * 8, 140, 146 + k * 8], fill=(150, 150, 165))
        d.rectangle([146, 145 + k * 8, 156, 146 + k * 8], fill=RED if k in (2, 3, 5) else (150, 150, 165))
    text(d, "?", 130, 113, RED, font=FONT_BIG)


def s2(im, d):   # the statement
    y = title(d, "THE MONTH", 24, GOLD)
    y = statement(d, y + 4)
    para(d, "FIND 3 LEAKS.", y + 6, WHITE, center=True)
    para(d, "THEN SWIPE.", y + 17, MINT, center=True)


def s3(im, d):   # hint
    y = title(d, "HINT", 26, GOLD)
    para(d, "3 KINDS OF LEAKS:", y + 4, WHITE, center=True)
    steps(d, ["2 OF THE SAME THING",
              "SOMETHING YOU STOPPED USING",
              "A FEE FOR NOTHING"], y + 22)
    para(d, "GOT THEM? SWIPE.", 180, MINT, center=True)


def leak(n, mark, head, lines):
    def draw(im, d):
        text(d, f"LEAK {n} OF 3", CW // 2, 24, RED, center=True)
        y = title(d, head, 36, GOLD)
        y = statement(d, y + 2, mark=mark, dim=True)
        for k, ln in enumerate(lines):
            para(d, ln, y + 5 + k * 11, WHITE if k < len(lines) - 1 else MINT, center=True)
    return draw


s4 = leak(1, (2, 4), "DOUBLE APP", ["YOU WATCH ONLY ONE.", "CANCEL B: €13/MONTH"])
s5 = leak(2, (5,), "GHOST GYM", ["LAST VISIT: AUGUST.", "PAUSE IT: €30/MONTH"])
s6 = leak(3, (7,), "THE FEE", ["€5 JUST TO HAVE IT.", "GO FREE: €5/MONTH"])


def s7(im, d):   # answer + math + today's quest
    y = title(d, "THE LOOT", 24, GOLD)
    panel(d, 8, y + 2, CW - 9, y + 38)
    para(d, "€13 + €30 + €5", y + 8, WHITE, center=True)
    para(d, "= €48 A MONTH X 12", y + 22, WHITE, center=True)
    big(d, "+€576", y + 44, GOLD)
    para(d, "A YEAR, BACK TO YOU", y + 64, WHITE, center=True)
    text(d, "TODAY'S QUEST", CW // 2, y + 82, MINT, center=True)
    steps(d, ["OPEN YOUR BANK APP", "SCROLL 30 DAYS: CIRCLE 3 LEAKS"], y + 96)


run_carousel(NAME, [s1, s2, s3, s4, s5, s6, s7, end_slide("NEXT BOSS")],
             example=[False, True, False, True, True, True, True, False])
