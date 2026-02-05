from shell.orchestrator import run_turn

while True:
    user = input("Avalon> ")
    if user.strip().lower() in {"exit", "quit"}:
        break

    intent, decision = run_turn(user)

    print("\n--- INTENT ---")
    print(intent)

    print("\n--- DECISION ---")
    print(f"state: {decision.state}")
    print(f"zone: {decision.zone}")
    print(f"disposition: {decision.disposition}")
    print(f"required_checks: {decision.required_checks}")
    print("audit:")
    for a in decision.audit:
        print(f"  - {a.rule_id}: {a.detail}")
    print()

