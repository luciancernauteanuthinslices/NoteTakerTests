#!/usr/bin/env python
import sys
from llama_cpp import Llama

#cd e2e
#chmod +x scripts/run_llm_once.py


# You can also read this from an env var if you want
MODEL_PATH = "/Users/lucian.cernauteanuthinslices.com/Documents/LLM Models/Qwen2.5-0.5B-Instruct-Q4_0.gguf"

# Very simple: first CLI arg is the prompt
if len(sys.argv) < 2:
    print("Usage: run_llm_once.py '<prompt>'", file=sys.stderr)
    sys.exit(1)

prompt = sys.argv[1]

# Load model (for a real project you'd reuse this instead of reloading each time)
llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=256,
    verbose=False,
)

output = llm(
    prompt,
    max_tokens=2056,
    temperature=2.0,
)

text = output["choices"][0]["text"].strip()
print(text)
