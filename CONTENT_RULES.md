# Content rules

## Audience and promise
English-speaking 18–28-year-olds with their first real income. Money explained like a video game.
No specific investment recommendations; concepts only. Every on-screen amount carries "EXAMPLE NUMBERS".

## Volume
5 posts per day on Instagram (user's decision, 2026-11-14): 4 videos + 1 carousel. Never produce more than gets posted.
- Videos: 2 boss fights (17–20 s) + 2 quick formats (8–12 s).
- Carousel: 1 per day, 6–8 slides, 1080x1350 (see "Carousels").
- Saved items (log.csv date "tbd") are used up first, oldest first, before making new ones of that type.
- Slots (German time), all on the same calendar day except the last:
  | Slot | Time | Post |
  | --- | --- | --- |
  | D | 12:30 | Carousel |
  | E | 15:30 | Quick format |
  | A | 18:00 | Boss fight |
  | B | 21:00 | Boss fight |
  | C | 00:30 (the following night = next calendar day) | Quick format (US evening) |
- Re-check slots and the video/carousel split against insights after 14 days (around 2026-11-28): compare saves + shares per 1,000 reach and follows per 1,000 reach by format.

## Quick formats (rotate; the two quick posts of a day are always different formats, and never the same format as the previous quick post)
quiz · 10-second tip · want-or-need · Dime reacts · rate-the-purchase (items ranked by rarity, common waste to legendary buy) · speedrun (sort out payday in 60 s with a timer; keep it 8–12 s by showing the 3 key moves) · patch notes (Dime's budget "update log": nerfed X, buffed Y)
New quick formats use `studio/quick.py`, saved as `studio/episodes/qNNN_<slug>.py`.

## Carousels
Engine: `studio/carousel.py`; scripts `studio/episodes/cNNN_<slug>.py`; `python3 <script>.py more` writes `studio/<name>_01.png …` and `<name>_cover.png` (= slide 1). Reference: `c001_boss_guide_trial_trap.py`.
Types (rotate; never the same type two days in a row):
- **Boss guide:** wiki card for one enemy already posted as a video (stats, how it attacks, damage math, weak spot, loot, today's quest, end card). Cheapest: reuse the boss sprite with `enemy_from()`.
- **Spot the leak:** a made-up bank statement (no real brand names), viewer finds 3 leaks, answer + math on the last content slide.
- **7-day quest map:** one small action per day for 7 days, one slide per day.
- **Want or need, swipe edition:** one item per slide, verdict + rarity.
Rules: slide 1 = hook + "SWIPE"; "EXAMPLE NUMBERS" on every slide that shows an amount; one concrete action doable within 24 h; last slide = "Save this" + the end card from content/status.md + next-boss open loop; all text inside x 8–172 of the 180-px canvas; the four checks apply to the carousel as a whole.

## Boss-fight template
| Time | Beat |
| --- | --- |
| 0–1.5 s | Attack: enemy already hitting Dime on frame one. Red flash, shake, −€ damage, combo, headline slams in |
| 1.5–6 s | Damage: cost per month and per year. Dime sad, rain cloud |
| 6–10 s | Power-up: "!" block with the tip, Dime gets a fitting weapon |
| 10–14 s | Counterattack: enemy beaten, coins return, wallet bar refills, yearly payoff |
| 14–19 s | End card (see phases) |

## The four checks (Reviewer sends back any video that fails one)
1. **Stands alone:** someone who never saw the page understands it. One full loop: problem, damage, tip, payoff. No "as you know from part 1".
2. **Useful today:** one concrete action the viewer can take within 24 hours.
3. **Reason to follow:** an open loop at the end (next enemy silhouette, "Boss 3 of 5", Dime's progress).
4. **Natural product link:** Dime uses the product's tool on screen; only every 4th video asks directly.

Plus: every math line adds up; no real brands or logos; no text cut off at the frame edge; attack visible on frame 0.

## Phases and end cards
End-card modes in the template: `more` = "Follow for more tips", `follow` = "Follow for part 2" (teases the next enemy), `comment` = "Comment SCAN".
- Default until the user says otherwise: `more`. Check content/status.md every run.
- Weeks 1–2 (Launch): World 1; "Comment SCAN" only once the free Leak Scanner is live.
- Weeks 3–4 (Build): World 2, €19 Money Quest sheet live, "Comment SCAN" + link in bio.
- Week 5+ (Storyline): Season 1 "Dime vs. the debt bosses", end card "Follow for part 2"; every 4th episode still "Comment SCAN".

## Cover image
Every video gets a cover: `python3 <episode>.py <mode> cover` saves `*_cover.png` (1080x1920) from the attack moment: headline, Dime shocked (not red-tinted), enemy visible. Headline and characters must sit inside the middle 3:4 area (the profile-grid crop). Quick formats get a cover with their question or hook as the headline.

## Sound
Every episode uses `studio/sound.py` (`episode_audio`): battle music under the attack, sad half-time during the damage, riser into the power-up, victory theme, level-complete jingle on the end card, plus punches, coin scatters, combo, womp, item-get, weapon hit (`bonk` or `snip`, add new ones there), cash register, typing blips. Keep it busy and punchy.

## Roles (one daily run)
1. **Director:** picks the day's 5 posts (2 boss topics, 2 quick formats, 1 carousel) from the plan, analytics and enemy roster; writes scripts with exact numbers; tags each video.
2. **Animator:** renders every script with the studio engine (videos with `quick.py` / boss template, carousels with `carousel.py`).
3. **Reviewer:** independent check against the four checks and the rules above; looks at frame 0, the payoff frame and the end card.
4. **Guide:** captions, hashtags, posting times, weekly package; every two weeks reads the platform exports and reports what to do more or less of.

## Tags per video (for analysis)
id, date, platform, slot, format (boss/quiz/tip/want-need/reacts/rate/speedrun/patch-notes/carousel), world, enemy, hook type, length_s, end card, product mention (yes/no).

## Metrics that decide
Swipe-away/skip rate (hook) · average % watched (story) · shares + saves per 1,000 views (value) · SCAN comments (funnel) · follows per 1,000 views (growth).

## Products (in order, each only if the previous one works)
1. Free Leak Scanner (email) → 2. €19 Money Quest sheet → 3. Boss Fight Pack €12 / €29 bundle → 4. web app (at ~300 waitlist sign-ups) → 5. native app.
