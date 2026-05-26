import os
import json
import re

INPUT_DIR = "transcripts"
OUTPUT_DIR = "datasets"

os.makedirs(OUTPUT_DIR, exist_ok=True)

CHUNK_SIZE = 1200


def clean_text(text):
    text = re.sub(r"\[.*?\]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def chunk_text(text, chunk_size=1200):
    words = text.split()

    chunks = []

    current_chunk = []

    current_length = 0

    for word in words:
        current_chunk.append(word)

        current_length += len(word) + 1

        if current_length >= chunk_size:
            chunks.append(" ".join(current_chunk))

            current_chunk = []

            current_length = 0

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


files = [
    f for f in os.listdir(INPUT_DIR)
    if f.endswith(".json")
]

for file_name in files:
    path = os.path.join(INPUT_DIR, file_name)

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    transcript = clean_text(data["transcript"])

    chunks = chunk_text(transcript)

    structured_chunks = []

    for idx, chunk in enumerate(chunks):
        structured_chunks.append({
            "chunk_id": idx + 1,
            "text": chunk
        })

    output_data = {
        "video_id": data["video_id"],
        "title": data["title"],
        "channel": data["channel"],
        "url": data["url"],
        "total_chunks": len(structured_chunks),
        "chunks": structured_chunks
    }

    output_path = os.path.join(
        OUTPUT_DIR,
        file_name
    )

    with open(output_path, "w", encoding="utf-8") as out:
        json.dump(
            output_data,
            out,
            ensure_ascii=False,
            indent=2
        )

    print(f"Processed: {file_name}")