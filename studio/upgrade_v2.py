"""Upgrade a v1 boss-fight script (copied from ep001-ep008 / render_takeout) to the v2 look.
Usage: python3 upgrade_v2.py episodes/ep007_fee_ghost.py <scene> <day> <plan_before> <plan_after>
Prefer copying template_boss_v2.py for new episodes; this is for older scripts."""
import re, sys
path, scene, day, pb, pa = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
s = open(path).read()
if "paint_scene(SCENE" in s: raise SystemExit("already v2")
def rep(a, b):
    global s
    assert s.count(a) == 1, (a[:70], s.count(a))
    s = s.replace(a, b)
rep("\nimport sys\nCTA_MODE", '\nexec(open("/home/claude/dime-money-quest/studio/fx.py").read())   # v2 visuals\n\nimport sys\nCTA_MODE')
rep("DIALOG = [", f'''# ---- v2 look + Dime's story (content/story.md) ----
SCENE = "{scene}"
DAY, PLAN_BEFORE, PLAN_AFTER = {day}, {pb}, {pa}
DASH = (T_WHACK - 0.35, T_WHACK + 1.0, 17)
SPINS = [(T_GRAB - 0.45, T_GRAB + 0.05), (T_PAY + 0.15, T_PAY + 0.75)]
ZOOMS = [(0.0, 1.45, 1.22, 96, 205), (T_WHACK - 0.05, T_WHACK + 0.9, 1.35, 112, 205)]

DIALOG = [''')
m = re.search(r"def guy_state\(t\):\n    feet = GROUND_Y\n    x = GUY_X - int\(knock\(t\)\)\n    for \(j0, jd, hgt\) in \(\(T_GRAB - 0.45, 0.5, 22\), \(T_PAY \+ 0.2, 0.35, 14\), \(T_PAY \+ 0.7, 0.35, 14\)\):", s)
assert m, "guy_state shape"
s = s[:m.start()] + '''def guy_state(t):
    feet = GROUND_Y
    x = GUY_X - int(knock(t)) + dash_x(t, *DASH)
    if any(0 <= t - h < 0.12 for h in HITS[-1:]): return x, feet, None, 6, "up", 1.0
    for (j0, jd, hgt) in ((T_GRAB - 0.45, 0.5, 22), (T_PAY + 0.15, 0.6, 24), (T_PAY + 0.9, 0.35, 12)):''' + s[m.end():]
a = s.index("    top, bot = sky_colors(5)\n    im = Image.new"); b = s.index("    bx, by0 = draw_bag(d, t)")
s = s[:a] + "    im, d = paint_scene(SCENE, t)\n\n" + s[b:]
rep('''    fx, fy = GUY_X, GROUND_Y + 1
    spr = layer.crop((fx - 30, fy - 90, fx + 30, fy)).resize((120, 180), Image.NEAREST)
    im.paste(spr, (fx - 60, fy - 180), spr)
    d = ImageDraw.Draw(im); d.fontmode = "1"
    hx = fx + (gx - fx) * 2; hcy = fy - (fy - ghcy) * 2''', '''    layer = mirror_spin(layer, int(gx), t, SPINS)
    fx, fy = GUY_X, GROUND_Y + 1
    spr = layer.crop((fx - 30, fy - 90, fx + 50, fy)).resize((160, 180), Image.NEAREST)
    im.paste(spr, (fx - 60, fy - 180), spr)
    d = ImageDraw.Draw(im); d.fontmode = "1"
    hx = fx + (gx - fx) * 2; hcy = fy - (fy - ghcy) * 2
    speed_lines(d, t, DASH[0], DASH[0] + 0.3, hx - 14, hcy + 40)
    shockwave(d, t, T_WHACK, hx + 40, GROUND_Y - 20)
    dust(d, t, T_GRAB + 0.05, hx); dust(d, t, T_PAY + 0.75, hx)
    confetti(d, t, T_PAY + 0.15)
    im = world_zoom(im, t, ZOOMS)
    d = ImageDraw.Draw(im); d.fontmode = "1"''')
rep("    if T_PAY + 0.2 <= t < T_CTA:", "    if T_PAY + 0.7 <= t < T_CTA:\n        quest_bar(d, t, T_PAY + 0.7, DAY, PLAN_BEFORE, PLAN_AFTER)\n    if T_PAY + 0.2 <= t < T_CTA:")
rep("    if t < 1.5:\n        for k, ln in enumerate(", '    if t < 1.5:\n        im = plate(im, 58, 128); d = ImageDraw.Draw(im); d.fontmode = "1"\n        for k, ln in enumerate(')
open(path, "w").write(s)
print("upgraded", path)
