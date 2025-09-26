import os
import base64
import json
from typing import List

import dotenv
from openai import OpenAI

from utils.prompts import VIBE_CAM_PROMPT, OUTPUT_SCHEMA


dotenv.load_dotenv(".env.local")


async def build_request_content(prompt: str, image_paths: List[str], views: List[str], material: str, metadata: dict | None = None) -> list:
    items: list = []
    meta_text = ""
    if metadata:
        meta_text = "\nMetadata: " + json.dumps(metadata)
    header = (
        f"Material: {material}\n"
        f"Instructions: Return JSON exactly matching this schema: {OUTPUT_SCHEMA}. "
        f"Use fixed numeric values (no ranges). Provide per-body breakdown (name, operations, machine path strategy, machine_time_min, price). "
        f"Discuss shapes/feature types you observe in the images.\n" +
        meta_text + "\n" +
        f"Prompt: {prompt}"
    )
    items.append({"type": "input_text", "text": header})
    for path, view in zip(image_paths, views):
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("ascii")
        items.append({"type": "input_text", "text": f"View: {view}"})
        items.append({"type": "input_image", "image_url": f"data:image/png;base64,{b64}"})
    return items


async def generate_quote_from_images(
    image_paths: List[str],
    views: List[str],
    material: str,
    prompt: str | None = None,
    model: str = "gpt-4.1",
    metadata: dict | None = None,
) -> dict:
    prompt = prompt or VIBE_CAM_PROMPT
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    content = await build_request_content(prompt, image_paths, views, material, metadata=metadata)
    resp = client.responses.create(
        model=model,
        input=[{"role": "user", "content": content}],
    )
    text = resp.output_text
    data = json.loads(text)
    return data

