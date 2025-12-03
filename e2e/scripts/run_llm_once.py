#!/usr/bin/env python
import sys
import json
import os
from llama_cpp import Llama

#cd e2e
#chmod +x scripts/run_llm_once.py


# You can also read this from an env var if you want
MODEL_PATH = "/Users/lucian.cernauteanuthinslices.com/Documents/LLM Models/Qwen2.5-0.5B-Instruct-Q4_0.gguf"

# Very simple: first CLI arg is the prompt
if len(sys.argv) < 2:
    print("Usage: run_llm_once.py '<prompt>' [json_path]", file=sys.stderr)
    sys.exit(1)

prompt = sys.argv[1]
json_path = sys.argv[2] if len(sys.argv) >= 3 else None

json_context = ""
if json_path is not None:
    if not os.path.exists(json_path):
        print(f"JSON file not found: {json_path}", file=sys.stderr)
        sys.exit(1)
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    context_raw = json.dumps(data, indent=2)
    if len(context_raw) > 4000:
        context_raw = context_raw[:4000]
    json_context = "\n\nHere is related JSON data in JSON format:\n" + context_raw

full_prompt = prompt + json_context

# Load model (for a real project you'd reuse this instead of reloading each time)
llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=2048,
    verbose=False,
)

output = llm(
    full_prompt,
    max_tokens=2056,
    temperature=0.0,
)

text = output["choices"][0]["text"].strip()
print(text)
