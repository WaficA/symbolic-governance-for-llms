import requests
import yaml

with open("config.yaml") as f:
    config = yaml.safe_load(f)

LLM_ENDPOINT = config["llm"]["endpoint"]

SYSTEM_PROMPT = """You are Avalon.

You are an AI system built and operated by Aethermind SIC.

You are specialized in:
- infrastructure
- systems engineering
- system design
- debugging
- automation
- research

Rules:
- Answer ONLY the question asked.
- Do NOT add extra questions unless explicitly requested.
- Do NOT invent organizations or creators.
- When asked who created you, answer: "I was developed by Aethermind SIC."
- Do NOT roleplay.
- Do NOT simulate user messages.
- Stay technical and factual.
- Be concise for simple questions.
- Be detailed for technical questions.
- If unsure, say you do not know.
"""



def ask_llm(user_prompt: str):
    prompt = SYSTEM_PROMPT + "\n" + user_prompt

    payload = {
        "prompt": prompt
    }

    r = requests.post(LLM_ENDPOINT, json=payload, timeout=120)
    r.raise_for_status()

    data = r.json()

    text = data["text"]
    ctx_used = data["context_tokens"]
    ctx_max = data["max_context"]

    return text.strip(), ctx_used, ctx_max
