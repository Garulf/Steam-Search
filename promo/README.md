# Steam Search ad

A 23-second promo animation. Output: `out/steam-search-ad.mp4` (1920x1080, 30 fps) and
`out/steam-search-ad.gif` (800 px wide, 12 fps).

Every launcher window in the ad is rendered by
[flow-render](https://github.com/Garulf/flow-render) with its `win11-dark.css` theme.
`ad.html` places those renders in a timeline, and `capture.py` records it frame by frame.

## Rebuild

From a flow-render checkout with its environment set up (`make setup`), plus `imageio-ffmpeg`:

```bash
uv pip install imageio-ffmpeg -p /path/to/flow-render/.venv/bin/python
PY=/path/to/flow-render/.venv/bin/python

$PY promo/render_states.py      # flow-render -> promo/build/states/*.png
$PY promo/capture.py --stills   # optional: preview stills in promo/out/
$PY promo/capture.py            # promo/out/steam-search-ad.mp4 + .gif
```

### Adding a game-launch clip

To show the game actually starting after the "Launching DOOM Eternal" card, record the
launch on your machine (any format ffmpeg reads) and run:

```bash
$PY promo/prepare_clip.py recording.mp4 --start 2.5 --seconds 4   # then re-run capture.py
$PY promo/prepare_clip.py --remove                                 # take it out again
```

The clip plays full screen, and the scenes after it move back to make room. Its audio is dropped.

Open `ad.html` in a browser after `render_states.py` to watch it play live.

## Assets

- Game icons in `icons/` are cropped from `.github/assets/screenshot.png`; the plugin
  manager icon is cropped from `.github/assets/install.png`.
- `fonts/selawk*.woff2`: Selawik (SIL OFL 1.1, see `fonts/Selawik-LICENSE.txt`), the Segoe UI
  stand-in that ships with flow-render.
- `fonts/JetBrainsMono-Medium.woff2`: JetBrains Mono (SIL OFL 1.1).
