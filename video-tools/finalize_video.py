"""Concatenate the per-scene narration WAVs into one track, pad it with
silence to match the recorded video's length, and mux the two into a final
H.264/AAC MP4 suitable for uploading to a competition submission portal.
"""
from __future__ import annotations

import json
import os
import subprocess

import imageio_ffmpeg

HERE = os.path.dirname(os.path.abspath(__file__))
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
AUDIO_DIR = os.path.join(HERE, "audio")
MANIFEST_PATH = os.path.join(AUDIO_DIR, "manifest.json")
VIDEO_PATH = os.path.join(HERE, "raw_video", "recording.webm")
CONCAT_LIST_PATH = os.path.join(AUDIO_DIR, "concat_list.txt")
NARRATION_TRACK = os.path.join(AUDIO_DIR, "narration_full.wav")
OUT_DIR = os.path.join(os.path.dirname(HERE), "demo")
OUT_PATH = os.path.join(OUT_DIR, "flow_recording.mp4")


def run(cmd: list[str]):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("COMMAND FAILED:", " ".join(cmd))
        print(result.stderr[-3000:])
        raise SystemExit(1)
    return result


def get_duration_seconds(path: str) -> float:
    result = subprocess.run(
        [FFMPEG, "-i", path], capture_output=True, text=True
    )
    for line in result.stderr.splitlines():
        line = line.strip()
        if line.startswith("Duration:"):
            ts = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = ts.split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    raise RuntimeError(f"Could not determine duration of {path}")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    with open(MANIFEST_PATH, "r", encoding="utf-8-sig") as f:
        manifest = json.load(f)

    # 1) Concatenate all narration clips into one continuous track.
    with open(CONCAT_LIST_PATH, "w", encoding="utf-8") as f:
        for item in manifest:
            wav_path = os.path.join(AUDIO_DIR, item["file"]).replace("\\", "/")
            f.write(f"file '{wav_path}'\n")

    concat_raw = os.path.join(AUDIO_DIR, "narration_concat.wav")
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", CONCAT_LIST_PATH, "-c", "copy", concat_raw])

    # 2) Figure out how much silence to pad at the end so the audio track
    #    covers the full video (some scenes ran a bit long against live
    #    network calls, so the video is slightly longer than the sum of the
    #    narration clips).
    video_duration = get_duration_seconds(VIDEO_PATH)
    narration_duration = get_duration_seconds(concat_raw)
    pad_seconds = max(0.0, video_duration - narration_duration + 0.5)
    print(f"Video: {video_duration:.2f}s, narration: {narration_duration:.2f}s, padding: {pad_seconds:.2f}s")

    run(
        [
            FFMPEG, "-y", "-i", concat_raw,
            "-af", f"apad=pad_dur={pad_seconds}",
            NARRATION_TRACK,
        ]
    )

    # 3) Mux video + narration into a final H.264/AAC MP4.
    run(
        [
            FFMPEG, "-y",
            "-i", VIDEO_PATH,
            "-i", NARRATION_TRACK,
            "-map", "0:v:0", "-map", "1:a:0",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-c:a", "aac", "-b:a", "160k",
            "-pix_fmt", "yuv420p",
            "-shortest",
            OUT_PATH,
        ]
    )

    print(f"Final video written to {OUT_PATH}")


if __name__ == "__main__":
    main()
