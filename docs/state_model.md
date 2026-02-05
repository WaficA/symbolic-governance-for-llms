# Symbolic State Model

This document defines the **formal state machine** used by the Avalon
Symbolic Governor. The state model is deterministic, auditable, and
authoritative over all downstream behavior.

The model is intentionally **non-learning** and **non-probabilistic**.

---

## Design Goals

- Deterministic behavior
- Explicit, enumerable states
- Fail-closed transitions
- Clear separation between:
  - ambiguity
  - boundary conditions
  - resolution
- Full auditability

The state machine exists to **govern decision flow**, not to execute actions.

---

## States Overview

The governor operates over **8 discrete states**:

| State | Name | Meaning |
|-----|------|--------|
| Ø | Nil / Ambiguity | Insufficient or unclear intent |
| A | Affirm | Intent is acceptable |
| B | Block | Intent is disallowed |
| U | Transform | Intent must be transformed before resolution |
| -A | Negated Affirm | Explicit outside-domain affirmative |
| -B | Negated Block | Explicit outside-domain block |
| T | Terminal | Decision finalized |
| C | Context Reset | Frame-shift or restart |

States are **not scores**, **not probabilities**, and **not beliefs**.
They are symbolic markers in a deterministic process.

---

## Zones

States are grouped into **zones** that describe epistemic conditions.

### Ambiguity Zone

Includes:
- Ø (Nil)
- A
- B

Meaning:
- Decision is not finalized
- Clarification, evaluation, or stabilization is ongoing

---

### Boundary Zone

Includes:
- U
- -A
- -B
- T

Meaning:
- The system is crossing a semantic boundary
- Transformations or finalization occur here

---

### No-Zone State

- C (Context Reset)

`C` is not a decision state.
It represents a **frame reset** or restart of reasoning.

---

## Transition Rules

Transitions are governed by a fixed transition table enforced by the
state machine.

Key properties:

- Illegal transitions are **rejected**
- Rejection is **fail-closed**
- Self-transitions (e.g. Ø → Ø) are **explicitly allowed**
- Policy suggestions cannot override machine rules

Example:

- Ø → A : allowed
- Ø → -A : forbidden
- Ø → Ø : allowed (stabilization)
- Any illegal transition → forced Ø

---

## Authority Model

- The **state machine** is authoritative
- Policy logic is advisory
- Intent parsers (including LLMs) are untrusted
- Execution (when enabled) must obey state outcomes

No component can bypass or overwrite the governor.

---

## Auditability

Every transition produces:
- a decision record
- an explicit audit trail
- a list of fired rules

This ensures:
- reproducibility
- post-hoc analysis
- formal verification

---

## What This Model Is Not

- Not a neural network
- Not reinforcement learning
- Not prompt engineering
- Not autonomous execution

This is a **symbolic control substrate** for reasoning systems.

---

## Status

- State model: **LOCKED**
- Transitions: **TESTED**
- Semantics: **FROZEN**

Any change to this model requires updating formal tests.

