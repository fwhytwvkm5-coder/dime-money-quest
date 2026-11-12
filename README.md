# Dime's Money Quest — content studio

Private studio for the Instagram / TikTok / YouTube Shorts account **@dimesmoneyquest**.
Dime is a pixel-art guy with a coin for a head. Money habits are explained as a retro arcade game:
bad habits are enemies that hurt Dime, tips are power-ups, savings are the score.

## Folders

| Path | What it is |
| --- | --- |
| `studio/render_arcade.py` | Arcade world engine: sky, city, ground, HUD, pixel font, coins, monsters, chiptune helpers |
| `studio/render_guy.py` | Dime the character (coin head + body, moods: happy, sad, shock, neutral) |
| `studio/render_takeout.py` | Reference episode: boss-fight template (video 4, Takeout Bag). `python3 render_takeout.py comment` or `follow` picks the end card |
| `studio/sound.py` | Chiptune score and sound effects for every episode |
| `studio/episodes/` | One script per episode, copied from the template |
| `studio/pfp.py` | Profile picture |
| `studio/PressStart2P.ttf` | Pixel font (SIL Open Font License, see `PressStart2P-LICENSE.txt`) |
| `CONTENT_RULES.md` | Format, the four checks every video must pass, roles, posting plan |
| `ENEMIES.md` | Enemy roster and the first 50 topics |

## Render

```
cd studio
python3 render_takeout.py more      # end card: more | follow | comment -> ep4_takeout_attack.mp4 (1080x1920, 30 fps, with sound)
```

Needs Python 3 with Pillow and numpy, plus ffmpeg. Rendering is local and costs no credits.
Rendered files (`*.mp4`, `*.png`, `*.wav`) are not committed.
