# Avalon Decision Engine

**A Multi-Layer Decision Logic for Safe Autonomous Systems**  
Framework by Wafic Abbass — © AetherMind S.I.C LLC | Project Avalon

---

## What This Is

A working Python implementation of the eight-state decision framework described in the paper *"A Multi-Layer Decision Logic for Safe Autonomous Systems: Eight Stable States and Two Indeterminate Zones"*.

This is not a toy. It is a governance kernel — a decision layer that can sit between an intent source (an LLM, a policy engine, a human operator) and an autonomous system's actuators.

---

## The Eight States

| State | Name           | Behavior                                                    |
|-------|----------------|-------------------------------------------------------------|
| A     | Affirm         | Allow / proceed / approve / activate                        |
| B     | Counter-Affirm | Deny / block / terminate / reject                           |
| Ø     | Nil/Void       | Suspend — insufficient context                              |
| U     | Unity          | Dual integration — sandbox / rate-limit / conditional       |
| -A    | Outside-A      | Request misclassified — not an allow-domain decision        |
| -B    | Outside-B      | Request misclassified — not a deny-domain decision          |
| T     | Transcendence  | Escalate — safe mode / human handoff / constitutional rule  |
| C     | Context Shift  | Full domain replacement — reframe the objective             |

## The Two Indeterminate Zones

- **Ambiguity Zone** (around Ø): data is incomplete or contradictory — engine requests clarification, self-resolves to Ø on timeout
- **Boundary Zone** (around U, -A, -B): domain or frame boundary — engine requests clarification, self-resolves to T on timeout

---

## Transition Table

```
A   → [Ø, U, T]
B   → [Ø, U, T]
Ø   → [A, B, U, T]
U   → [-A, -B, T]
-A  → [T, C]
-B  → [T, C]
T   → [C, Ø]
C   → [A, B]
```

All transitions are enforced. No state can jump outside this table.

---

## Project Structure

```
avalon-decision-engine/
├── core/
│   ├── __init__.py
│   ├── states.py        # State definitions, zone membership, descriptions
│   ├── transitions.py   # Transition table and validation
│   └── engine.py        # State machine, clarification loop, self-resolution
├── policy/
│   ├── __init__.py
│   └── default.yaml     # Micro-policy reference config
├── tests/
│   ├── __init__.py
│   └── test_engine.py   # 23 tests covering all states, zones, and paths
├── main.py              # Demo scenarios
└── README.md
```

---

## Running

```bash
# Demo scenarios
python main.py

# Tests
python -m unittest tests.test_engine -v
```

No dependencies beyond Python 3.10+.

---

## Using the Engine

```python
from core import AvalonEngine, State

engine = AvalonEngine(
    initial_state=State.NULL,
    max_clarification_attempts=2,
    verbose=True,
)

# Clean decision
result = engine.evaluate({
    "action": "allow",
    "domain": "network",
    "trust": "verified",
})
# → State.A

# Ambiguous — engine asks for clarification
def my_input_fn(prompt):
    return input(prompt)  # or route to LLM, operator, policy

result = engine.evaluate(
    {"action": "open", "trust": "unknown"},
    input_fn=my_input_fn,
)

# Contradiction — sandboxed, escalates if unresolved
result = engine.evaluate({
    "action": "allow",
    "trust": "partial",
    "contradiction": True,
})
# → State.U then State.T if no clarification
```

---

## Intent Dictionary Keys

| Key | Type | Description |
|-----|------|-------------|
| `action` | str | Verb: allow, deny, block, permit, open, terminate... |
| `trust` | str | verified / partial / unknown |
| `domain` | str | Context label: network, kernel, forensic, runtime... |
| `contradiction` | bool | Conflicting signals — routes to Unity (U) |
| `misclassified` | bool | Request is in wrong domain — routes to -A or -B |
| `escalate` | bool | Force escalation to Transcendence (T) |
| `reframe` | bool | Full frame replacement — T → C → A/B |

---

## What Comes Next

The intent parser in `engine.py` is currently keyword-based. The natural next step is replacing it with an LLM classifier that outputs structured intent dicts — keeping the engine itself clean and deterministic while the intelligence lives in the parser.

This engine is designed to be embedded. Target integrations:
- Kernel-level automation (eBPF policy hooks)
- LLM tool governance (action gating before execution)
- Multi-agent orchestration (inter-agent trust decisions)
- Cyber-defense agents (network policy enforcement)
- Avalon node governance layer

---

*Knowledge is free. Convenience is paid. Sovereignty is priceless.*  
© AetherMind S.I.C LLC | Project Avalon
