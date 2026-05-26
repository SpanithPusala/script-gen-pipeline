import os
import json
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

INPUT_DIR = "datasets"
OUTPUT_DIR = "analysis"

os.makedirs(OUTPUT_DIR, exist_ok=True)

MODEL_NAME = "Qwen/Qwen2.5-3B-Instruct"

print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

print("Loading model...")
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16,
    device_map="auto"
)

print("Model loaded.\n")


def analyze_chunk(text):

    prompt = f"""
You are an expert YouTube content strategist.

Analyze this transcript chunk and return ONLY valid JSON.

Transcript:
{text}

Return this exact JSON structure:

{{
  "summary": "...",
  "main_topic": "...",
  "hook_type": "...",
  "emotion": "...",
  "storytelling_pattern": "...",
  "viewer_retention_strategy": "...",
  "cta": "..."
}}
"""

    messages = [
        {
            "role": "user",
            "content": prompt
        }
    ]

    text_input = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    model_inputs = tokenizer(
        text_input,
        return_tensors="pt"
    ).to(model.device)

    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=300,
        temperature=0.7
    )

    output = tokenizer.decode(
        generated_ids[0],
        skip_special_tokens=True
    )

    return output


files = [
    f for f in os.listdir(INPUT_DIR)
    if f.endswith(".json")
]

for file_name in files:

    print(f"\nProcessing {file_name}")

    path = os.path.join(INPUT_DIR, file_name)

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    analyzed_chunks = []

    for chunk in data["chunks"][:3]:

        try:
            result = analyze_chunk(chunk["text"])

            analyzed_chunks.append({
                "chunk_id": chunk["chunk_id"],
                "analysis": result
            })

            print(f"Analyzed chunk {chunk['chunk_id']}")

        except Exception as e:
            print(f"Error analyzing chunk {chunk['chunk_id']}")
            print(str(e))

    output_data = {
        "video_id": data["video_id"],
        "title": data["title"],
        "channel": data["channel"],
        "analyzed_chunks": analyzed_chunks
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

    print(f"Saved analysis: {output_path}")