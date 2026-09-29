"""Capture ad.html frame by frame and encode it to MP4 and GIF.

    python promo/capture.py              # full render -> promo/out/
    python promo/capture.py --stills     # a few preview stills only

Needs Playwright (Chromium) and imageio-ffmpeg, both available in a
flow-render environment plus `pip install imageio-ffmpeg`.
"""
import argparse
import subprocess
from pathlib import Path

import imageio_ffmpeg
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
WIDTH, HEIGHT = 1920, 1080
STILLS = [1.4, 4.9, 6.6, 8.6, 12.4, 16.2, 21.5]


def open_page(playwright):
    browser = playwright.chromium.launch(channel="chromium")
    page = browser.new_page(viewport={"width": WIDTH, "height": HEIGHT})
    page.goto((HERE / "ad.html").as_uri() + "?capture")
    page.evaluate("window.ready")
    return browser, page


def frame(page, t):
    page.evaluate(f"window.seek({t:.4f})")
    return page.screenshot(type="png")


def stills():
    OUT.mkdir(exist_ok=True)
    with sync_playwright() as p:
        browser, page = open_page(p)
        for t in STILLS:
            path = OUT / f"still-{t:05.2f}.png"
            path.write_bytes(frame(page, t))
            print(f"wrote {path.relative_to(HERE)}")
        browser.close()


def video(fps):
    OUT.mkdir(exist_ok=True)
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    mp4 = OUT / "steam-search-ad.mp4"
    encoder = subprocess.Popen(
        [ffmpeg, "-y", "-loglevel", "error",
         "-f", "image2pipe", "-framerate", str(fps), "-i", "-",
         "-c:v", "libx264", "-preset", "slow", "-crf", "18",
         "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(mp4)],
        stdin=subprocess.PIPE,
    )
    with sync_playwright() as p:
        browser, page = open_page(p)
        duration = page.evaluate("window.DURATION")
        frames = int(round(duration * fps))
        for i in range(frames):
            encoder.stdin.write(frame(page, i / fps))
            if i % fps == 0:
                print(f"frame {i}/{frames}", flush=True)
        browser.close()
    encoder.stdin.close()
    encoder.wait()
    print(f"wrote {mp4.relative_to(HERE)}")

    gif = OUT / "steam-search-ad.gif"
    subprocess.run(
        [ffmpeg, "-y", "-loglevel", "error", "-i", str(mp4),
         "-vf", "fps=12,scale=800:-1:flags=lanczos,split[a][b];"
                "[a]palettegen=max_colors=96:stats_mode=diff[p];"
                "[b][p]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle",
         str(gif)],
        check=True,
    )
    print(f"wrote {gif.relative_to(HERE)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--stills", action="store_true")
    parser.add_argument("--fps", type=int, default=30)
    args = parser.parse_args()
    stills() if args.stills else video(args.fps)
