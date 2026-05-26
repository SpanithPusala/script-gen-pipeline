import os
import json
import subprocess
from datetime import datetime
from pathlib import Path

INPUT_FILE = "input/reference_links.txt"
OUTPUT_DIR = "transcripts"

os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(INPUT_FILE, "r") as f:
    links = [line.strip() for line in f if line.strip()]


def extract_video_id(url):
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    return url.split("/")[-1]


def flatten_transcript(events):
    final_text = []

    for event in events:
        segs = event.get("segs", [])

        for seg in segs:
            text = seg.get("utf8", "").strip()

            if text:
                final_text.append(text)

    transcript = " ".join(final_text)

    transcript = transcript.replace("\n", " ")
    transcript = " ".join(transcript.split())

    return transcript


for url in links:
    try:
        video_id = extract_video_id(url)

        print(f"\nProcessing: {video_id}")

        temp_dir = Path("temp_subs")
        temp_dir.mkdir(exist_ok=True)

        subprocess.run([
            "yt-dlp",
            "--write-auto-sub",
            "--sub-lang", "en",
            "--skip-download",
            "-o", f"{temp_dir}/%(id)s.%(ext)s",
            url
        ], check=True)

        subtitle_files = list(temp_dir.glob(f"{video_id}*.json3"))

        if not subtitle_files:
            print(f"No subtitles found for {video_id}")
            continue

        subtitle_path = subtitle_files[0]

        with open(subtitle_path, "r", encoding="utf-8") as f:
            subtitle_data = json.load(f)

        events = subtitle_data.get("events", [])

        transcript_text = flatten_transcript(events)

        output_data = {
            "video_id": video_id,
            "url": url,
            "transcript": transcript_text,
            "transcript_length": len(transcript_text),
            "created_at": datetime.now().isoformat()
        }

        output_path = os.path.join(
            OUTPUT_DIR,
            f"{video_id}.json"
        )

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(f"Saved cleaned transcript: {output_path}")

    except Exception as e:
        print(f"Error processing {url}")
        print(e)