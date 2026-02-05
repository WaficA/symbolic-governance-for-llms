from core.engine import ask_llm
import subprocess
import shutil

def enforce_output_discipline(user_input: str, reply: str) -> str:
    u = user_input.lower().strip()

    # identity questions → 1 sentence only
    if u in ["who are you", "who created you", "what is your name"]:
        reply = reply.split(".")[0] + "."

    # stop if model starts asking questions
    for marker in ["\nwhat ", "\nwho ", "\nwhy ", "\nhow "]:
        if marker in reply.lower():
            reply = reply.split(marker)[0].strip()

    # remove follow-up questions
    reply = reply.replace("?", "").strip()

    forbidden_phrases = [
        "how can i help",
        "can i help",
        "what can i do",
        "would you like",
        "do you want",
    ]

    for phrase in forbidden_phrases:
        if phrase in reply.lower():
            reply = reply.split(phrase)[0].strip()

    return reply



def get_vram_usage():
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=memory.used,memory.total", "--format=csv,noheader,nounits"]
        ).decode().strip()
        first = out.splitlines()[0]
        used, total = first.split(",")
        return int(used), int(total)
    except:
        return 0, 0

def draw_status_bar(vram_used, vram_total, ctx_used, ctx_max):
    width = shutil.get_terminal_size().columns
    vram_pct = int((vram_used / vram_total) * 100) if vram_total else 0
    ctx_pct = int((ctx_used / ctx_max) * 100) if ctx_max else 0

    lines = [
        "────────────────────────────────────────────",
        f"CTX  {ctx_used} / {ctx_max} ({ctx_pct}%)",
        f"VRAM {vram_used} / {vram_total} MB ({vram_pct}%)",
        "────────────────────────────────────────────",
    ]

    for line in lines:
        print(line.ljust(width))

# --- conversation buffer ---
history = []

while True:
    user = input("Avalon> ")
    if user.strip().lower() == "exit":
        break

    history.append(f"<user>{user}</user>")
    prompt = "\n".join(history)

    reply, ctx_used, ctx_max = ask_llm(prompt)

    # sanitize reply
    reply = reply.strip()
    for tag in ["<user>", "</user>", "<avalon>", "</avalon>"]:
        reply = reply.replace(tag, "")
        
    if reply.lower().startswith("user:"):
        reply = reply[5:].strip()
    if reply.lower().startswith("assistant:"):
        reply = reply[10:].strip()
       
    # enforce single-answer discipline    
    reply = enforce_output_discipline(user, reply)   
    print(reply)

    history.append(f"<avalon>{reply}</avalon>")

    usage = ctx_used / ctx_max if ctx_max else 0

    if usage >= 0.95:
        print("\n[CTX POLICY] Context critically full (>=95%). Please reset or summarize.\n")
    elif usage >= 0.85:
        print("\n[CTX POLICY] Context very high (>=85%). Summarization recommended.\n")
    elif usage >= 0.70:
        print("\n[CTX POLICY] Context getting high (>=70%).\n")

    vram_used, vram_total = get_vram_usage()
    draw_status_bar(vram_used, vram_total, ctx_used, ctx_max)
    print()

