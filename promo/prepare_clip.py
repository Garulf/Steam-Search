"""Add a game-launch clip to the ad.

    python promo/prepare_clip.py recording.mp4 --start 2.5 --seconds 4
    python promo/prepare_clip.py --remove

Cuts `--seconds` of the video starting at `--start`, fills 1920x1080 (cropping
to fit), and writes JPEG frames to promo/build/clip/ plus clip.js, which
ad.html picks up. The ad then plays the clip full screen right after the
"Launching DOOM Eternal" card and pushes the later scenes back. Audio is
dropped. Re-run capture.py afterwards.
"""
import argparse
import shutil
from pathlib import Path
import subprocess

import imageio_ffmpeg

HERE = Path(__file__).resolve().parent
CLIP_DIR = HERE / "build" / "clip"
FPS = 30


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("video", nargs="?", help="Screen recording of the game launching")
    parser.add_argument("--start", type=float, default=0.0, help="Seconds into the video to start at")
    parser.add_argument("--seconds", type=float, default=4.0, help="How much of the video to use")
    parser.add_argument("--remove", action="store_true", help="Remove the clip from the ad")
    args = parser.parse_args()

    shutil.rmtree(CLIP_DIR, ignore_errors=True)
    if args.remove:
        print("removed launch clip")
        return
    if not args.video:
        parser.error("give a video path, or --remove")

    CLIP_DIR.mkdir(parents=True)
    subprocess.run(
        [imageio_ffmpeg.get_ffmpeg_exe(), "-loglevel", "error",
         "-ss", str(args.start), "-t", str(args.seconds), "-i", args.video,
         "-an", "-vf", f"fps={FPS},scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080",
         "-q:v", "3", str(CLIP_DIR / "%04d.jpg")],
        check=True,
    )
    frames = len(list(CLIP_DIR.glob("*.jpg")))
    if not frames:
        raise SystemExit("no frames extracted; check --start and --seconds")
    (CLIP_DIR / "clip.js").write_text(f"window.CLIP = {{ frames: {frames}, fps: {FPS} }};\n")
    print(f"wrote {frames} frames ({frames / FPS:.2f}s) to {CLIP_DIR.relative_to(HERE)}")


if __name__ == "__main__":
    main()
