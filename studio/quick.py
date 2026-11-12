"""Quick-format engine (quiz, 10-second tip, want-or-need, Dime reacts), 8-12 s.

Same arcade look, Dime and sound style as the boss fights, shorter.
Usage inside an episode script:

    exec(open("/home/claude/dime-money-quest/studio/quick.py").read())
    ... define mood_at(t), guy_state(t), DIALOG, T_CTA, DUR, EVENTS, scene_frame(t) ...
    run_quick("q001_quiz_save35", scene_frame, cover_t=0.4, music="quiz")

`python3 <episode>.py more` renders the MP4, `python3 <episode>.py more cover` the cover PNG.
"""
import math, random, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw

STUDIO = "/home/claude/dime-money-quest/studio"
src = open(f"{STUDIO}/render_guy.py").read().split("\ndef frame(t):")[0]
exec(src)

CTA_MODE = sys.argv[1] if len(sys.argv) > 1 else "more"
COVER = len(sys.argv) > 2 and sys.argv[2] == "cover"     # covers never show a half-typed dialog box
if CTA_MODE == "comment":
    raise SystemExit("Comment SCAN end card is off until content/status.md says the Leak Scanner is live")


def scene(t, sky=5, sun=True):
    """sky, stars, hills, city, ground. Returns (im, d)."""
    top, bot = sky_colors(sky)
    im = Image.new("RGB", (LW, LH), top)
    d = ImageDraw.Draw(im); d.fontmode = "1"
    for y in range(34, GROUND_Y):
        d.line([0, y, LW, y], fill=mixc(top, bot, (y - 34) / (GROUND_Y - 34)))
    for (sx, sy) in STARS[:30]:
        if int(t * 3 + sx) % 6: d.point((sx % LW, sy), fill=(255, 255, 220))
    if sun: d.ellipse([150, 52, 168, 70], fill=(255, 190, 120))
    for (hx, hh) in HILLS[:6]:
        x = int(hx * 0.6)
        d.ellipse([x - 50, GROUND_Y - hh - 30, x + 50, GROUND_Y + 40], fill=mixc(bot, (40, 90, 80), 0.5))
    for (bx, bw, bh, wins) in BUILD[:14]:
        d.rectangle([bx, GROUND_Y - bh, bx + bw, GROUND_Y], fill=(55, 50, 95))
        for (wx, wy) in wins: d.point((bx + wx, GROUND_Y - bh + wy), fill=(255, 210, 90))
    for tx in range(0, LW + 12, 12):
        d.rectangle([tx, GROUND_Y, tx + 11, GROUND_Y + 6], fill=GREEN); d.line([tx, GROUND_Y, tx + 11, GROUND_Y], fill=(160, 255, 180))
        d.rectangle([tx, GROUND_Y + 7, tx + 11, LH], fill=(120, 74, 44)); d.point((tx + 3, GROUND_Y + 11), fill=(150, 100, 60))
    return im, d


def paste_dime(im, t, cx=GUY_X, tint=False, extra=None):
    """Draw Dime (2x) with his feet on the ground at screen x = cx. extra(ld, gx, ghcy, t) draws a held item.
    Returns the screen position of his head centre."""
    layer = Image.new("RGBA", (LW, LH), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    gx, ghcy = guy(ld, t)
    if extra: extra(ld, gx, ghcy, t)
    if tint:
        r, g, b, a = layer.split()
        layer = Image.merge("RGBA", (r.point(lambda v: min(255, v + 120)), g.point(lambda v: v // 2), b.point(lambda v: v // 2), a))
    fx, fy = GUY_X, GROUND_Y + 1
    spr = layer.crop((fx - 30, fy - 90, fx + 30, fy)).resize((120, 180), Image.NEAREST)
    im.paste(spr, (cx - 60, fy - 180), spr)
    return cx + (gx - fx) * 2, fy - (fy - ghcy) * 2


def hud(d, t, whp, mood, tag=None):
    d.rectangle([0, 0, LW, 33], fill=INK)
    coin_sprite(d, 9, 9, 4, t * 4)
    text(d, "WALLET", 18, 6, GOLD)
    text(d, {"happy": "MOOD :)", "sad": "MOOD :(", "shock": "MOOD :O", "neutral": "MOOD :|"}[mood], 112, 6,
         (150, 255, 180) if mood == "happy" else (RED if mood in ("sad", "shock") else WHITE))
    whp = clamp(whp)
    bc = GREEN if whp > 0.7 else (GOLD if whp > 0.5 else RED)
    d.rectangle([6, 20, 173, 28], fill=(60, 50, 80))
    d.rectangle([7, 21, 7 + int(165 * whp), 27], fill=bc); d.line([7, 21, 7 + int(165 * whp), 21], fill=mixc(bc, WHITE, 0.5))
    text(d, "EXAMPLE NUMBERS", 90, 42, (210, 210, 225), center=True)   # y 42: inside the 3:4 grid crop
    if tag:   # format badge, e.g. QUIZ! / 10-SECOND TIP
        w = int(d.textlength(tag, font=FONT)) + 8
        d.rectangle([90 - w // 2, 52, 90 + w // 2, 63], fill=INK)
        d.rectangle([90 - w // 2 + 1, 53, 90 + w // 2 - 1, 62], fill=(90, 110, 230))
        text(d, tag, 90, 54, WHITE, shadow=False, center=True)


def headline(d, t, lines, cols, y0=66, t_end=None, step=22):
    """Hook title: every line is on screen from frame 0 (quick formats live or die on the first frame);
    lines 2+ do a small vertical slam so nothing ever leaves the frame sideways."""
    if t_end is not None and t >= t_end: return
    for k, ln in enumerate(lines):
        dy = 0 if k == 0 else -int((1 - prog(t, 0.0, 0.08 + 0.05 * k)) * 4)
        text(d, ln, 90, y0 + k * step + dy, cols[k], font=FONT_BIG, center=True)


def dialog_box(d, t, DIALOG, t_end):
    if COVER or not DIALOG or t < DIALOG[0][0] or t >= t_end: return
    cur = max(k for k in range(len(DIALOG)) if t >= DIALOG[k][0])
    t0, msg = DIALOG[cur]
    n = int((t - t0) * 34)
    lines = wrap(msg, 20)
    d.rectangle([4, 268, LW - 5, 315], fill=INK); d.rectangle([5, 269, LW - 6, 314], outline=WHITE)
    d.rectangle([7, 271, LW - 8, 312], outline=(90, 80, 120))
    left = n
    for k, ln in enumerate(lines[:3]):
        if left <= 0: break
        text(d, ln[:left], 12, 276 + k * 12, WHITE, shadow=False); left -= len(ln) + 1


def item_box(d, t, x, y, t_drop, t_grab, col=GREEN):
    """the "!" power-up block dropping in, bursting into sparkles when grabbed"""
    if t < t_drop: return
    drop = ease_out(prog(t, t_drop, t_drop + 0.4))
    qy = int(lerp(20, y, drop))
    if t < t_grab:
        d.rectangle([x - 8, qy - 8, x + 8, qy + 8], fill=INK)
        d.rectangle([x - 7, qy - 7, x + 7, qy + 7], fill=col)
        d.rectangle([x - 7, qy - 7, x + 7, qy - 7], fill=(180, 255, 200))
        text(d, "!", x - 3, qy - 4, WHITE if int(t * 4) % 2 else INK, shadow=False)
    else:
        pp = prog(t, t_grab, t_grab + 0.5)
        if pp < 1:
            for a in range(12):
                ang = a * math.pi / 6; r = int(4 + pp * 24)
                d.rectangle([x + int(math.cos(ang) * r) - 1, qy + int(math.sin(ang) * r) - 1,
                             x + int(math.cos(ang) * r) + 1, qy + int(math.sin(ang) * r) + 1], fill=GOLD_L if a % 2 else col)


def end_card(im, t, T_CTA, tease=None):
    p = prog(t, T_CTA, T_CTA + 0.3)
    im = Image.blend(im, Image.new("RGB", (LW, LH), INK), 0.94 * p)
    d = ImageDraw.Draw(im); d.fontmode = "1"
    if p < 1: return im
    hl = Image.new("RGBA", (40, 40), (0, 0, 0, 0)); hd = ImageDraw.Draw(hl)
    head(hd, 20, 20, "happy", t)
    hl = hl.resize((120, 120), Image.NEAREST)
    bounce = int(abs(math.sin(t * 5)) * 6)
    im.paste(hl, (-6, 150 - bounce), hl)
    d = ImageDraw.Draw(im); d.fontmode = "1"
    blink = GOLD if int(t * 4) % 2 else (255, 240, 140)
    text(d, "FOLLOW", 90, 58, WHITE, font=FONT_BIG, center=True)
    if CTA_MODE == "follow":
        if t > T_CTA + 0.3: text(d, "FOR PART 2", 90, 84, blink, font=FONT_BIG, center=True)
        if t > T_CTA + 0.6 and tease:
            text(d, "NEXT LEVEL:", 90, 116, (150, 255, 180), center=True)
            text(d, tease, 90, 128, WHITE, center=True)
    else:
        if t > T_CTA + 0.3:
            text(d, "FOR MORE", 90, 84, blink, font=FONT_BIG, center=True)
            text(d, "TIPS", 90, 106, blink, font=FONT_BIG, center=True)
        if t > T_CTA + 0.6:
            text(d, "NEW LEVEL", 90, 136, (150, 255, 180), center=True)
            text(d, "EVERY DAY", 90, 148, (150, 255, 180), center=True)
    if CTA_MODE == "more" and t > T_CTA + 0.9:   # open loop: the next boss waits in the dark
        text(d, "NEXT BOSS", 140, 232, (150, 255, 180), center=True)
        for k in range(3):
            mx = 126 + k * 14; my = 254
            d.rectangle([mx - 5, my - 5, mx + 5, my + 5], fill=(70, 60, 100))
            d.point((mx - 2, my - 1), fill=RED); d.point((mx + 2, my - 1), fill=RED)
    bx0 = 142 + int(math.sin(t * 6) * 2)
    d.rectangle([bx0 - 30, 200, bx0 + 30, 220], fill=INK)
    d.rectangle([bx0 - 29, 201, bx0 + 29, 219], fill=(90, 110, 230))
    d.rectangle([bx0 - 29, 201, bx0 + 29, 202], fill=(160, 175, 255))
    text(d, "+FOLLOW", bx0 - 26, 207, WHITE, shadow=False)
    if t > T_CTA + 1.2 and int(t * 2) % 2:
        text(d, "@DIMESMONEYQUEST", 90, 292, (200, 200, 220), center=True)
    return im


def post_fx(im, t, DUR, shakes=(), red=(), white=()):
    """screen shake, red flash on hits, white flash on power moves, fade at the very end"""
    out = im
    sh = 0
    for h in list(shakes):
        dd = t - h
        if 0 <= dd < 0.18: sh = int(3 * math.sin(dd * 120))
    if sh:
        out = Image.new("RGB", (LW, LH), INK); out.paste(im, (sh, -sh // 2))
    for h in red:
        if 0 <= t - h < 0.07: out = Image.blend(out, Image.new("RGB", (LW, LH), (255, 40, 60)), 0.35)
    for h in white:
        if 0 <= t - h < 0.06: out = Image.blend(out, Image.new("RGB", (LW, LH), WHITE), 0.5)
    if t > DUR - 0.2: out = Image.blend(out, Image.new("RGB", (LW, LH), INK), prog(t, DUR - 0.2, DUR) * 0.6)
    return out.resize((W, H), Image.NEAREST)


def run_quick(name, frame_fn, DUR, T_CTA, EVENTS, DIALOG, cover_t=0.4, music="quiz", check=()):
    out_silent = f"{STUDIO}/{name}_silent.mp4"
    if len(sys.argv) > 2 and sys.argv[2] == "cover":
        frame_fn(cover_t).save(f"{STUDIO}/{name}_cover.png")
        return
    N = int(FPS * DUR)
    proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                             "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264",
                             "-preset", "veryfast", "-crf", "16", "-pix_fmt", "yuv420p", out_silent], stdin=subprocess.PIPE)
    for i in range(N):
        fr = frame_fn(i / FPS)
        proc.stdin.write(fr.tobytes())
        if i in check: fr.save(f"{STUDIO}/{name}_f{i:03d}.png")
    proc.stdin.close(); proc.wait()
    sys.path.insert(0, STUDIO)
    from sound import quick_audio
    wav = f"{STUDIO}/{name}_sfx.wav"
    quick_audio(wav, DUR, T_CTA, EVENTS, DIALOG, music=music)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", out_silent, "-i", wav,
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest", f"{STUDIO}/{name}.mp4"])
    print("done", name)
