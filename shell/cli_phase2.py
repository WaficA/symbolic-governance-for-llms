from shell.orchestrator import run_turn
from shell.orchestrator import _metrics

print("Avalon Phase 2 — LLM Instrumented Mode")
print("Type 'exit' to quit.\n")

while True:
    try:
        user = input("Avalon> ").strip()
        if user.lower() in {"exit", "quit"}:
            break

        intent, decision, used_fallback = run_turn(user)

        print("\n--- PARSE ---")
        print("source:", "fallback(parser_py)" if used_fallback else "llm")

        print("\n--- INTENT ---")
        print(intent)

        print("\n--- DECISION ---")
        print(f"state: {decision.state}")
        print(f"zone: {decision.zone}")
        print(f"disposition: {decision.disposition}")
        print(f"required_checks: {decision.required_checks}")

        print("\n--- AUDIT ---")
        for a in decision.audit:
            print(f"- {a.rule_id}: {a.detail}")

        print()

    except KeyboardInterrupt:
        print("\nExiting.")
        break

print("\n--- METRICS SNAPSHOT ---")
print(_metrics.snapshot())
