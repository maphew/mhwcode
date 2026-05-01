#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "scenedetect[opencv]>=0.6",
#   "opencv-python>=4.8",
#   "Pillow>=10.0",
#   "tqdm>=4.66",
# ]
# ///
"""
extract_poster_frames.py
------------------------
Scan home video file(s) and extract the sharpest, most poster-worthy still
from each detected scene.

Usage:
    uv run extract_poster_frames.py VIDEO [VIDEO ...] [options]

Examples:
    uv run extract_poster_frames.py holiday.mp4
    uv run extract_poster_frames.py *.mp4 --out posters --interval 3
    uv run extract_poster_frames.py holiday.mp4 --contact-sheet
"""

import argparse
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from scenedetect import open_video, SceneManager
from scenedetect.detectors import ContentDetector
from tqdm import tqdm


# ─────────────────────────────────────────────────────────────────────────────
# Sharpness scoring
# ─────────────────────────────────────────────────────────────────────────────

def sharpness_score(frame_bgr: np.ndarray) -> float:
    """Laplacian variance — higher = sharper."""
    gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var()


def brightness_ok(frame_bgr: np.ndarray, low: int = 30, high: int = 225) -> bool:
    """Reject nearly-black or blown-out frames."""
    mean = frame_bgr.mean()
    return low < mean < high


# ─────────────────────────────────────────────────────────────────────────────
# Best-frame picker within a scene
# ─────────────────────────────────────────────────────────────────────────────

def best_frame_in_scene(
    cap: cv2.VideoCapture,
    start_frame: int,
    end_frame: int,
    sample_count: int = 12,
) -> tuple[np.ndarray | None, int, float]:
    """
    Sample `sample_count` frames evenly across [start_frame, end_frame],
    filter for brightness, return the sharpest one.

    Returns (frame_bgr, frame_number, score)  or  (None, -1, 0) if all bad.
    """
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    length = end_frame - start_frame
    if length < 1:
        return None, -1, 0.0

    step = max(1, length // sample_count)
    candidates = range(start_frame, end_frame, step)

    best_frame, best_num, best_score = None, -1, -1.0

    for fnum in candidates:
        cap.set(cv2.CAP_PROP_POS_FRAMES, fnum)
        ok, frame = cap.read()
        if not ok or frame is None:
            continue
        if not brightness_ok(frame):
            continue
        score = sharpness_score(frame)
        if score > best_score:
            best_frame, best_num, best_score = frame, fnum, score

    return best_frame, best_num, best_score


# ─────────────────────────────────────────────────────────────────────────────
# Contact sheet builder
# ─────────────────────────────────────────────────────────────────────────────

def make_contact_sheet(
    image_paths: list[Path],
    out_path: Path,
    cols: int = 4,
    thumb_w: int = 480,
    thumb_h: int = 270,
    padding: int = 8,
    bg_color: tuple = (30, 30, 30),
) -> None:
    """Stitch thumbnails into a single overview image."""
    if not image_paths:
        return

    rows = (len(image_paths) + cols - 1) // cols
    cell_w = thumb_w + padding
    cell_h = thumb_h + padding
    sheet_w = cols * cell_w + padding
    sheet_h = rows * cell_h + padding

    sheet = Image.new("RGB", (sheet_w, sheet_h), bg_color)

    for idx, p in enumerate(image_paths):
        try:
            img = Image.open(p).convert("RGB")
            img.thumbnail((thumb_w, thumb_h), Image.LANCZOS)
            col = idx % cols
            row = idx // cols
            x = padding + col * cell_w + (thumb_w - img.width) // 2
            y = padding + row * cell_h + (thumb_h - img.height) // 2
            sheet.paste(img, (x, y))
        except Exception:
            pass

    sheet.save(out_path, quality=90)
    print(f"  Contact sheet → {out_path}")


# ─────────────────────────────────────────────────────────────────────────────
# Per-video processing
# ─────────────────────────────────────────────────────────────────────────────

def process_video(
    video_path: Path,
    out_dir: Path,
    threshold: float = 27.0,
    min_scene_seconds: float = 1.5,
    min_sharpness: float = 50.0,
    sample_count: int = 12,
) -> list[Path]:
    """
    Detect scenes, extract best frame per scene, save as JPEG.
    Returns list of saved image paths.
    """
    print(f"\n▶  {video_path.name}")
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = video_path.stem

    # ── Scene detection ──────────────────────────────────────────────────────
    video = open_video(str(video_path))
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector(threshold=threshold))
    scene_manager.detect_scenes(video, show_progress=True)
    scenes = scene_manager.get_scene_list()

    if not scenes:
        print("  No scenes detected — treating whole file as one scene.")
        cap_tmp = cv2.VideoCapture(str(video_path))
        total = int(cap_tmp.get(cv2.CAP_PROP_FRAME_COUNT))
        cap_tmp.release()
        fps_val = video.frame_rate or 25
        from scenedetect import FrameTimecode
        scenes = [(FrameTimecode(0, fps_val), FrameTimecode(total - 1, fps_val))]

    fps = video.frame_rate or 25
    min_frames = int(min_scene_seconds * fps)
    print(f"  {len(scenes)} scene(s) found, FPS={fps:.2f}")

    # ── Frame extraction ─────────────────────────────────────────────────────
    cap = cv2.VideoCapture(str(video_path))
    saved_paths: list[Path] = []

    for i, (start_tc, end_tc) in enumerate(
        tqdm(scenes, desc="  Extracting", unit="scene", leave=False)
    ):
        start_f = start_tc.get_frames()
        end_f = end_tc.get_frames()

        if (end_f - start_f) < min_frames:
            continue

        frame, fnum, score = best_frame_in_scene(
            cap, start_f, end_f, sample_count=sample_count
        )
        if frame is None or score < min_sharpness:
            continue

        ts_sec = fnum / fps
        minutes, seconds = divmod(int(ts_sec), 60)
        hours, minutes = divmod(minutes, 60)
        ts_str = f"{hours:02d}h{minutes:02d}m{seconds:02d}s"

        out_name = f"{stem}_scene{i+1:04d}_{ts_str}_sharpness{int(score)}.jpg"
        out_path = out_dir / out_name
        cv2.imwrite(str(out_path), frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
        saved_paths.append(out_path)

    cap.release()
    print(f"  ✓ Saved {len(saved_paths)} candidate frame(s) to {out_dir}/")
    return saved_paths


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract poster-candidate stills from home video.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "videos",
        nargs="+",
        type=Path,
        help="One or more video files (mp4, mov, avi, mkv, …)",
    )
    parser.add_argument(
        "--out", "-o",
        type=Path,
        default=Path("poster_frames"),
        help="Output folder (default: ./poster_frames)",
    )
    parser.add_argument(
        "--threshold", "-t",
        type=float,
        default=27.0,
        help="Scene-change sensitivity 10–40 (lower = more scenes). Default 27.",
    )
    parser.add_argument(
        "--min-scene",
        type=float,
        default=1.5,
        metavar="SECS",
        help="Skip scenes shorter than this many seconds. Default 1.5.",
    )
    parser.add_argument(
        "--min-sharpness",
        type=float,
        default=50.0,
        metavar="SCORE",
        help="Discard frames below this sharpness score. Default 50.",
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=12,
        metavar="N",
        help="Frames sampled per scene to find the sharpest. Default 12.",
    )
    parser.add_argument(
        "--contact-sheet",
        action="store_true",
        help="Also produce a single contact-sheet overview image.",
    )

    args = parser.parse_args()

    # Resolve glob patterns on Windows (shells don't expand * automatically)
    video_files: list[Path] = []
    for p in args.videos:
        if p.exists():
            video_files.append(p)
        else:
            # Try parent-dir glob
            matches = list(p.parent.glob(p.name))
            if matches:
                video_files.extend(matches)
            else:
                print(f"Warning: no files matched '{p}', skipping.", file=sys.stderr)

    if not video_files:
        print("No video files found. Exiting.", file=sys.stderr)
        sys.exit(1)

    all_saved: list[Path] = []
    for vf in video_files:
        saved = process_video(
            vf,
            out_dir=args.out / vf.stem,
            threshold=args.threshold,
            min_scene_seconds=args.min_scene,
            min_sharpness=args.min_sharpness,
            sample_count=args.samples,
        )
        all_saved.extend(saved)

    print(f"\n{'─'*60}")
    print(f"Total frames saved: {len(all_saved)}")
    print(f"Output folder:      {args.out.resolve()}")

    if args.contact_sheet and all_saved:
        sheet_path = args.out / "contact_sheet.jpg"
        make_contact_sheet(all_saved, sheet_path)

    print("\nDone! Open the output folder to browse candidates.")
    print("Tip: filenames include timestamp + sharpness score to help you sort.")


if __name__ == "__main__":
    main()
