import yt_dlp
import os
import json
import re
import requests
from datetime import datetime, timezone

INPUT_FILE = "input/reference_links.txt"
OUTPUT_DIR = "transcripts"

os.makedirs(OUTPUT_DIR, exist_ok=True)


def extract_video_id(url):
    if "v=" in url:
        return url.split("v=")[-1].split("&")[0]

    if "youtu.be/" in url:
        return url.split("youtu.be/")[-1].split("?")[0]

    return None


with open(INPUT_FILE, "r") as f:
    links = [line.strip() for line in f.readlines() if line.strip()]


for url in links:
    try:
        video_id = extract_video_id(url)

        if not video_id:
            print(f"Skipping invalid URL: {url}")
            continue

        print(f"\nProcessing: {video_id}")

        ydl_opts = {
            "skip_download": True,
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": ["en"],
            "quiet": True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            subtitles = (
                info.get("automatic_captions", {})
                or info.get("subtitles", {})
            )

            transcript_text = ""

            if "en" in subtitles:
                subtitle_url = subtitles["en"][0]["url"]

                response = requests.get(subtitle_url)

                subtitle_data = response.json()

                transcript_parts = []

                events = subtitle_data.get("events", [])

                for event in events:
                    segs = event.get("segs", [])

                    for seg in segs:
                        text = (
                            seg.get("utf8", "")
                            .replace("\n", " ")
                            .strip()
                        )

                        if text:
                            transcript_parts.append(text)

                transcript_text = " ".join(transcript_parts)

                transcript_text = re.sub(
                    r"\s+",
                    " ",
                    transcript_text
                ).strip()

            else:
                print(f"No English subtitles found for {video_id}")
                continue

            data = {
                "video_id": video_id,
                "url": url,
                "title": info.get("title"),
                "channel": info.get("channel"),
                "transcript": transcript_text,
                "transcript_length": len(transcript_text),
                "created_at": datetime.now(
                    timezone.utc
                ).isoformat()
            }

            output_path = os.path.join(
                OUTPUT_DIR,
                f"{video_id}.json"
            )

            with open(output_path, "w", encoding="utf-8") as out:
                json.dump(
                    data,
                    out,
                    ensure_ascii=False,
                    indent=2
                )

            print(f"Saved: {output_path}")

    except Exception as e:
        print(f"Error processing {url}")
        print(str(e))