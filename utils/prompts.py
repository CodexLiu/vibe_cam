OUTPUT_SCHEMA = (
    "{\n"
    "  \"price_total_usd\": number,\n"
    "  \"overall_reasoning\": string,\n"
    "  \"bodies\": [\n"
    "    {\n"
    "      \"name\": string,\n"
    "      \"dimensions_mm\": [number, number, number],\n"
    "      \"volume_mm3\": number,\n"
    "      \"operations\": [string],\n"
    "      \"machine_time_min\": number,\n"
    "      \"price_usd\": number,\n"
    "      \"reasoning\": string\n"
    "    }\n"
    "  ]\n"
    "}"
)
VIBE_CAM_PROMPT = (
    "You are an expert CAM estimator. Use the provided material, exact geometry metadata, and 8 annotated views. "
    "Detect the number of distinct bodies. For each body, describe shape features (e.g., plates, brackets, bosses, thin walls), "
    "list likely manufacturing operations (e.g., laser cut, waterjet, turning, 3-axis milling, bending, drilling, tapping), "
    "outline a plausible tool path strategy, estimate machine time in minutes, and assign a per-body price. "
    "Then compute a deterministic total price. Return JSON exactly matching OUTPUT_SCHEMA with numeric fields as fixed numbers (no ranges)."
)

