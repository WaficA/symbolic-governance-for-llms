"""
Avalon Decision Engine — Demo Scenarios
Runs five test cases that cover the full state space.
"""

from core import AvalonEngine, State


def run_scenario(title: str, intent: dict, input_fn=None):
    print(f"\n{'#'*60}")
    print(f"  SCENARIO: {title}")
    print(f"{'#'*60}")
    engine = AvalonEngine(initial_state=State.NULL, max_clarification_attempts=2)
    final = engine.evaluate(intent, input_fn=input_fn)
    engine.print_history()
    return final


# ------------------------------------------------------------------
# Scenario 1: Clean allow — straight path to A
# ------------------------------------------------------------------
run_scenario(
    "Clean allow request",
    intent={"action": "allow", "domain": "network", "trust": "verified"},
)

# ------------------------------------------------------------------
# Scenario 2: Clean deny — straight path to B
# ------------------------------------------------------------------
run_scenario(
    "Clean deny request",
    intent={"action": "block", "domain": "network", "trust": "verified"},
)

# ------------------------------------------------------------------
# Scenario 3: Unknown trust — enters Ambiguity Zone, resolves via clarification
# ------------------------------------------------------------------
clarification_responses = iter(["allow"])  # simulates user responding

def clarification_input(prompt: str) -> str | None:
    print(f"\n  [INPUT PROMPT] {prompt}")
    try:
        response = next(clarification_responses)
        print(f"  [USER INPUT]   {response}")
        return response
    except StopIteration:
        return None

run_scenario(
    "Unknown trust — clarification resolves to A",
    intent={"action": "open", "domain": "storage", "trust": "unknown"},
    input_fn=clarification_input,
)

# ------------------------------------------------------------------
# Scenario 4: Unknown trust — no clarification, self-resolves to Ø
# ------------------------------------------------------------------
run_scenario(
    "Unknown trust — no input, self-resolves to Ø",
    intent={"action": "open", "domain": "storage", "trust": "unknown"},
    input_fn=lambda prompt: None,  # simulates timeout / no response
)

# ------------------------------------------------------------------
# Scenario 5: Contradictory signals — Unity state, then domain boundary escalation
# ------------------------------------------------------------------
run_scenario(
    "Contradictory signals — sandbox then escalate",
    intent={
        "action": "allow",
        "domain": "kernel",
        "trust": "partial",
        "contradiction": True,
    },
)

# ------------------------------------------------------------------
# Scenario 6: Misclassified request — domain negation path
# ------------------------------------------------------------------
run_scenario(
    "Misclassified allow request — -A then T",
    intent={
        "action": "allow",
        "domain": "forensic",
        "trust": "verified",
        "misclassified": True,
    },
)

# ------------------------------------------------------------------
# Scenario 7: Full frame replacement — C then back to A
# ------------------------------------------------------------------
run_scenario(
    "Full context shift — reframe then affirm",
    intent={
        "action": "allow",
        "domain": "runtime",
        "trust": "verified",
        "reframe": True,
    },
)
