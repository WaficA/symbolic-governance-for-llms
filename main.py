"""
Avalon Decision Engine — Live Interface
Raw string → Mistral intent parser → state machine → decision

Requires: uvicorn server running at localhost:9000
Start with: uvicorn server.main:app --host 0.0.0.0 --port 9000
"""

from core import AvalonEngine, State
from core.intent_parser import parse_intent


def run(raw_input: str):
    print(f"\n{'#'*60}")
    print(f"  INPUT : {raw_input}")
    print(f"{'#'*60}")

    intent = parse_intent(raw_input)

    if "_error" in intent:
        print(f"  ERROR : {intent['_error']}")

    engine = AvalonEngine(initial_state=State.NULL, verbose=True)
    engine.evaluate(intent)


if __name__ == "__main__":
    print("\nAvalon Decision Engine — Live")
    print("Mistral-7B intent parser active.")
    print("Type your input. Ctrl+C to exit.\n")

    while True:
        try:
            raw = input(">> ")
            if raw.strip():
                run(raw)
        except KeyboardInterrupt:
            print("\nShutting down.")
            break
