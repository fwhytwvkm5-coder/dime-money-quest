"""Chiptune score + sound effects for the boss-fight template.

episode_audio(...) writes a mono 44.1 kHz WAV that follows the episode beats:
battle music under the attack, a sad half-time loop during the damage, a riser into
the power-up, a victory theme after the counterattack and a level-complete jingle
on the end card. Effects: title slams, punches, coin scatters, combo, damage womp,
item-get, weapon hit (bonk, snip, ping, swat, ring or block), cash register, coin returns, typewriter blips.
"""
import math, wave
import numpy as np

SR = 44100
RNG = np.random.default_rng(7)

def _t(dur): return np.arange(int(SR * dur)) / SR

def M(*xs):
    """Mix signals of different lengths (pads the shorter ones with silence)."""
    n = max(len(x) for x in xs)
    out = np.zeros(n)
    for x in xs: out[:len(x)] += x
    return out

def note(name):
    names = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}
    p, o = name[:-1], int(name[-1])
    return 440.0 * 2 ** ((names[p] + 12 * (o + 1) - 69) / 12)

def env(n, a=0.004, r=0.05):
    e = np.ones(n)
    na, nr = max(1, int(a * SR)), max(1, int(r * SR))
    e[:na] = np.linspace(0, 1, na)
    if nr < n: e[-nr:] *= np.linspace(1, 0, nr)
    return e

def sq(f, dur, vol=0.1, duty=0.5, decay=0.0, slide=None):
    t = _t(dur)
    if slide is None: ph = (t * f) % 1.0
    else: ph = np.cumsum(np.linspace(f, slide, len(t))) / SR % 1.0
    return vol * np.where(ph < duty, 1.0, -1.0) * np.exp(-decay * t) * env(len(t))

def tri(f, dur, vol=0.1, decay=0.0):
    t = _t(dur)
    ph = (t * f) % 1.0
    return vol * (4 * np.abs(ph - 0.5) - 1) * np.exp(-decay * t) * env(len(t))

def sine(f, dur, vol=0.1, decay=0.0, slide=None):
    t = _t(dur)
    if slide is None: ph = 2 * np.pi * f * t
    else: ph = 2 * np.pi * np.cumsum(np.linspace(f, slide, len(t))) / SR
    return vol * np.sin(ph) * np.exp(-decay * t) * env(len(t), 0.001)

def noise(dur, vol=0.1, decay=0.0, hp=False):
    n = RNG.uniform(-1, 1, int(SR * dur))
    if hp: n = np.diff(n, prepend=0) * 0.6
    return vol * n * np.exp(-decay * _t(dur)) * env(len(n), 0.001)

def sweep(dur, vol, up=True):
    n = RNG.uniform(-1, 1, int(SR * dur))
    t = _t(dur)
    k = np.linspace(0.05, 0.9, len(t)) if up else np.linspace(0.9, 0.05, len(t))
    out = np.zeros_like(n); acc = 0.0
    for i in range(len(n)):           # one-pole filter with moving cutoff
        acc += k[i] * (n[i] - acc); out[i] = acc
    shape = np.sin(np.pi * t / dur) ** 2
    return vol * out * shape

# --- drums ---
def kick(vol=0.5): return sine(150, 0.16, vol, 18, slide=42)
def snare(vol=0.3): return M(noise(0.14, vol, 26), tri(190, 0.08, vol * 0.4, 30))
def hat(vol=0.08): return noise(0.035, vol, 90, hp=True)

# --- effects ---
def punch(vol=0.6):
    return M(sine(120, 0.18, vol, 16, slide=48), noise(0.12, vol * 0.7, 35), sq(330, 0.06, vol * 0.25, 0.5, 30, slide=110))
def coin(vol=0.09, pitch=1.0):
    return np.concatenate([sq(988 * pitch, 0.05, vol, 0.5), sq(1319 * pitch, 0.14, vol, 0.5, 12)])
def slam(vol=0.35): return M(sweep(0.18, vol, up=False), sine(90, 0.12, vol, 20, slide=55))
def womp(vol=0.14):
    return np.concatenate([sq(392, 0.25, vol, 0.5, 3, slide=370), sq(349, 0.25, vol, 0.5, 3, slide=330), sq(311, 0.7, vol, 0.5, 2.5, slide=262)])
def item_get(vol=0.1):
    seq = [note(n) for n in ("C5", "E5", "G5", "C6", "E6", "G6")]
    return np.concatenate([sq(f, 0.06, vol, 0.25, 4) for f in seq] + [sq(note("C7"), 0.35, vol, 0.25, 6)])
def shimmer(dur=0.8, vol=0.05):
    out = np.zeros(int(SR * dur))
    for k in range(10):
        s = sine(2000 + 300 * k, 0.12, vol, 25); i = int(k * dur / 10 * SR)
        out[i:i + len(s)] += s[:len(out) - i]
    return out
def bonk(vol=0.6): return M(punch(vol), sine(900, 0.3, vol * 0.4, 9, slide=500))
def snip(vol=0.5):
    return M(noise(0.06, vol * 0.8, 50, hp=True), sine(2600, 0.35, vol * 0.35, 10), sine(3900, 0.25, vol * 0.2, 14), np.pad(noise(0.05, vol * 0.6, 60, hp=True), (int(0.08 * SR), 0)))
def ping(vol=0.5):
    """magnifying-glass scan: a radar ping that sweeps up, plus a 'found it' double beep"""
    return M(sine(700, 0.4, vol * 0.45, 5, slide=1800), sq(1320, 0.06, vol * 0.12, 0.25, 20),
             np.pad(sq(1760, 0.08, vol * 0.14, 0.25, 15), (int(0.09 * SR), 0)), punch(vol * 0.6))
def swat(vol=0.6):
    """rolled-up map smack: paper whoosh into a heavy thud"""
    return M(np.pad(punch(vol), (int(0.07 * SR), 0)), sweep(0.12, vol * 0.5, up=True), sine(220, 0.25, vol * 0.3, 12, slide=90))
def ring(vol=0.5):
    """alarm-clock reminder: fast bell trill over a punchy hit"""
    out = np.zeros(int(0.6 * SR))
    for k in range(14):
        b = M(sine(2350 if k % 2 else 2650, 0.05, vol * 0.22, 30), sq(1175 if k % 2 else 1325, 0.04, vol * 0.05, 0.25, 40))
        i = int(k * 0.04 * SR); out[i:i + len(b)] += b[:len(out) - i]
    return M(out, punch(vol * 0.6))
def block(vol=0.6):
    """shield block: metallic clang with a ringing tail"""
    return M(punch(vol * 0.8), sine(1480, 0.5, vol * 0.25, 7), sine(2210, 0.4, vol * 0.18, 9), sq(740, 0.08, vol * 0.12, 0.5, 25), noise(0.05, vol * 0.5, 70, hp=True))
WEAPONS = {"bonk": None, "snip": None, "ping": ping, "swat": swat, "ring": ring, "block": block}
def register(vol=0.25):
    return M(np.pad(M(sine(1568, 0.6, vol, 5), sine(2093, 0.6, vol * 0.7, 6)), (int(0.05 * SR), 0)), noise(0.04, vol, 60))
def level_up(vol=0.1):
    seq = [note(n) for n in ("G4", "C5", "E5", "G5", "E5", "G5")]
    lens = [0.08, 0.08, 0.08, 0.16, 0.08, 0.4]
    return np.concatenate([sq(f, l, vol, 0.5, 3) for f, l in zip(seq, lens)])
def blip(vol=0.012): return sq(1700, 0.018, vol, 0.5, 60)

# --- music ---
def pattern(buf, t0, t1, bpm, bass, lead, drums="full", vol=1.0, lead_duty=0.25):
    """bass/lead: lists of note names (None = rest), one per 8th note, looped."""
    step = 60 / bpm / 2
    i = 0; t = t0
    while t < t1 - 1e-6:
        b = bass[i % len(bass)]
        if b: _add(buf, t, M(tri(note(b), step * 0.95, 0.22 * vol), sq(note(b), step * 0.5, 0.03 * vol, 0.5, 8)))
        l = lead[i % len(lead)]
        if l: _add(buf, t, sq(note(l), step * 0.6, 0.045 * vol, lead_duty, 6))
        beat8 = i % 8
        if drums == "full":
            if beat8 in (0, 4): _add(buf, t, kick(0.45 * vol))
            if beat8 in (3, 6): _add(buf, t, kick(0.25 * vol))
            if beat8 in (2, 6): _add(buf, t, snare(0.22 * vol))
            _add(buf, t, hat(0.06 * vol)); _add(buf, t + step / 2, hat(0.035 * vol))
        elif drums == "soft":
            if beat8 == 0: _add(buf, t, kick(0.3 * vol))
            if beat8 == 4: _add(buf, t, snare(0.1 * vol))
            if beat8 % 2 == 0: _add(buf, t, hat(0.03 * vol))
        elif drums == "hats":
            _add(buf, t, hat(0.04 * vol))
        i += 1; t += step

def _add(buf, t0, sig, gain=1.0):
    i = int(t0 * SR)
    if i >= len(buf) or i < 0: return
    n = min(len(sig), len(buf) - i)
    buf[i:i + n] += gain * sig[:n]

def episode_audio(path, DUR, HITS, T_BOX, T_GRAB, T_WHACK, T_PAY, T_CTA, DIALOG, weapon="bonk", title_lines=3):
    n = int(SR * DUR)
    music = np.zeros(n); sfx = np.zeros(n)
    # battle: A minor, driving
    pattern(music, 0.0, 3.6, 164,
            ["A2", "A2", "A2", "C3", "A2", "A2", "G2", "E2"],
            ["A4", "C5", "E5", "A5", "E5", "C5", "B4", "C5", "A4", "C5", "E5", "G5", "F5", "E5", "D5", "E5"])
    # damage: half-time, sad
    pattern(music, 3.6, T_GRAB - 0.8, 120,
            ["A2", None, None, None, "F2", None, None, None, "D2", None, None, None, "E2", None, "E2", None],
            ["E5", None, "D5", None, "C5", None, "B4", None, "A4", None, None, None, "G#4", None, None, None],
            drums="soft", vol=0.8, lead_duty=0.5)
    _add(sfx, 3.6, noise(T_GRAB - 4.4, 0.012, 0.0))          # light rain hiss under the sad part
    # riser into the power-up
    _add(sfx, T_GRAB - 0.8, sweep(0.8, 0.22, up=True))
    for k in range(8): _add(sfx, T_GRAB - 0.8 + k * 0.1, sq(note("C4") * 2 ** (k / 4), 0.08, 0.05, 0.25, 6))
    # victory: C major, bouncy
    pattern(music, T_WHACK + 0.1, T_CTA, 164,
            ["C3", "C3", "G2", "C3", "F2", "F2", "G2", "G2"],
            ["E5", "G5", "C6", "G5", "A5", "G5", "E5", "G5", "F5", "A5", "C6", "A5", "G5", "B5", "D6", "B5"])
    # end card: light loop
    pattern(music, T_CTA + 0.9, DUR, 164, ["C3", None, "G2", None], [None, "E5", None, "G5", None, "C6", None, "G5"], drums="hats", vol=0.7)

    # effects
    _add(sfx, 0.0, punch(0.55)); _add(sfx, 0.0, kick(0.6))
    for k in range(title_lines): _add(sfx, k * 0.1, slam(0.28))
    for i, h in enumerate(HITS):
        _add(sfx, h, punch(0.55))
        for k in range(4): _add(sfx, h + 0.04 + k * 0.05, coin(0.07, 0.8 + 0.15 * k))
    _add(sfx, HITS[-1] + 0.15, np.concatenate([sq(note(x), 0.07, 0.08, 0.25, 5) for x in ("E5", "G5", "B5")]))
    _add(sfx, 3.8, womp()); _add(sfx, 3.8, kick(0.5))
    _add(sfx, T_BOX + 0.5, punch(0.3)); _add(sfx, T_BOX + 0.5, shimmer(0.6, 0.035))
    _add(sfx, T_GRAB, item_get()); _add(sfx, T_GRAB, shimmer(0.9, 0.04))
    _add(sfx, T_WHACK, snip() if weapon == "snip" else (WEAPONS[weapon]() if WEAPONS.get(weapon) else bonk())); _add(sfx, T_WHACK, kick(0.6))
    for k in range(10): _add(sfx, T_WHACK + 0.2 + k * 0.07, coin(0.08, 1.0 + 0.04 * k))
    _add(sfx, T_PAY + 0.2, register())
    _add(sfx, T_CTA, sweep(0.35, 0.2, up=False)); _add(sfx, T_CTA + 0.3, level_up())
    for t0, msg in DIALOG:
        for k, ch in enumerate(msg):
            if ch != " " and k % 3 == 0: _add(sfx, t0 + k / 34, blip())

    # duck the music under big hits
    duck = np.ones(n)
    for t0 in list(HITS) + [0.0, 3.8, T_GRAB, T_WHACK, T_PAY + 0.2]:
        i = int(t0 * SR); m = int(0.35 * SR)
        if i < n: duck[i:i + m] = np.minimum(duck[i:i + m], np.linspace(0.45, 1.0, min(m, n - i)))
    mix = music * 0.55 * duck + sfx * 0.9
    mix = np.tanh(mix * 1.4) / np.tanh(1.4)
    mix /= max(1e-6, np.max(np.abs(mix))) / 0.89
    if DUR > 0.3:  # short fade at the very end so the loop restarts cleanly
        f = int(0.2 * SR); mix[-f:] *= np.linspace(1, 0, f)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR)
        wf.writeframes((mix * 32767).astype(np.int16).tobytes())


# ---------- quick formats (quiz, 10-second tip, want-or-need, Dime reacts) ----------
def tick(vol=0.12): return M(sq(1200, 0.03, vol, 0.5, 60), noise(0.02, vol * 0.5, 120, hp=True))
def ding(vol=0.12):
    return np.concatenate([sq(note("E6"), 0.08, vol, 0.25, 6), sq(note("A6"), 0.4, vol, 0.25, 5)])
def buzz(vol=0.1): return M(sq(110, 0.35, vol, 0.5, 4), sq(116, 0.35, vol, 0.5, 4))
def stamp(vol=0.5): return M(punch(vol), noise(0.08, vol * 0.5, 40), sine(70, 0.2, vol * 0.5, 14))
def poof(vol=0.25): return M(sweep(0.3, vol, up=False), noise(0.15, vol * 0.4, 20))
def jump(vol=0.07): return sq(300, 0.18, vol, 0.25, 6, slide=750)

QUICK_FX = {
    "punch": lambda: M(punch(0.55), kick(0.5)), "coin": lambda: coin(0.09),
    "coins": lambda: np.concatenate([np.pad(coin(0.07, 1.0 + 0.05 * k), (int(0.06 * k * SR), 0)) for k in range(1)]),
    "slam": lambda: slam(0.28), "womp": lambda: M(womp(), kick(0.5)), "item": lambda: M(item_get(), shimmer(0.9, 0.04)),
    "register": register, "tick": tick, "ding": lambda: M(ding(), shimmer(0.6, 0.04)), "buzz": buzz, "stamp": stamp,
    "poof": poof, "levelup": lambda: M(sweep(0.35, 0.2, up=False), np.pad(level_up(), (int(0.3 * SR), 0))),
    "jump": jump, "bonk": bonk, "snip": snip, "ping": ping, "swat": swat, "ring": ring, "block": block,
    "riser": lambda: M(sweep(0.8, 0.22, up=True), *[np.pad(sq(note("C4") * 2 ** (k / 4), 0.08, 0.05, 0.25, 6), (int(k * 0.1 * SR), 0)) for k in range(8)]),
}

def quick_audio(path, DUR, T_CTA, EVENTS, DIALOG, music="quiz"):
    """EVENTS: list of (time, effect name from QUICK_FX); 'coinrain' adds 8 rising coins."""
    n = int(SR * DUR)
    mus = np.zeros(n); sfx = np.zeros(n)
    if music == "quiz":      # tense-bouncy thinking loop, then bright after the reveal (first 'ding')
        reveal = next((t for t, e in EVENTS if e == "ding"), T_CTA)
        pattern(mus, 0.0, reveal, 150, ["D3", None, "D3", None, "F3", None, "D3", "C3"],
                ["A4", None, "D5", None, "A4", None, "F5", "E5"], drums="soft", vol=0.9)
        pattern(mus, reveal + 0.2, T_CTA, 164, ["C3", "C3", "G2", "C3", "F2", "F2", "G2", "G2"],
                ["E5", "G5", "C6", "G5", "A5", "G5", "E5", "G5"], vol=0.9)
    else:                    # 'battle': same A-minor drive as the boss fights, victory after the first 'item'
        win = next((t for t, e in EVENTS if e in ("item",)), T_CTA)
        pattern(mus, 0.0, win, 164, ["A2", "A2", "A2", "C3", "A2", "A2", "G2", "E2"],
                ["A4", "C5", "E5", "A5", "E5", "C5", "B4", "C5", "A4", "C5", "E5", "G5", "F5", "E5", "D5", "E5"])
        pattern(mus, win + 0.3, T_CTA, 164, ["C3", "C3", "G2", "C3", "F2", "F2", "G2", "G2"],
                ["E5", "G5", "C6", "G5", "A5", "G5", "E5", "G5", "F5", "A5", "C6", "A5", "G5", "B5", "D6", "B5"])
    pattern(mus, T_CTA + 0.9, DUR, 164, ["C3", None, "G2", None], [None, "E5", None, "G5", None, "C6", None, "G5"], drums="hats", vol=0.7)
    duck = np.ones(n)
    for t0, e in EVENTS:
        if e == "coinrain":
            for k in range(8): _add(sfx, t0 + k * 0.07, coin(0.08, 1.0 + 0.05 * k))
        else:
            _add(sfx, t0, QUICK_FX[e]())
        if e in ("punch", "stamp", "womp", "ding", "buzz", "bonk", "snip", "ping", "swat", "register"):
            i = int(t0 * SR); m = int(0.35 * SR)
            if i < n: duck[i:i + m] = np.minimum(duck[i:i + m], np.linspace(0.45, 1.0, min(m, n - i)))
    _add(sfx, T_CTA, QUICK_FX["levelup"]())
    for t0, msg in DIALOG:
        for k, ch in enumerate(msg):
            if ch != " " and k % 3 == 0: _add(sfx, t0 + k / 34, blip())
    mix = mus * 0.55 * duck + sfx * 0.9
    mix = np.tanh(mix * 1.4) / np.tanh(1.4)
    mix /= max(1e-6, np.max(np.abs(mix))) / 0.89
    f = int(0.2 * SR); mix[-f:] *= np.linspace(1, 0, f)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR)
        wf.writeframes((mix * 32767).astype(np.int16).tobytes())
