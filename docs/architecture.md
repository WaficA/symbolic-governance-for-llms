# System Architecture

This repository implements a symbolic decision governor that constrains
and governs Large Language Models (LLMs) without modifying or trusting them.

The architecture enforces a strict separation between:
- language generation
- intent representation
- decision authority

---

## High-Level Pipeline

User Input (text)
↓
Intent Parser

Phase 1: parser_py (deterministic)

Phase 2: parser_llm (untrusted)
↓
Intent Schema Validation

authority key rejection

structural normalization
↓
Policy Evaluation (advisory)
↓
Governor State Machine (authoritative)
↓
Decision + Audit


---

## Authority Boundaries

| Component | Trust Level | Authority |
|---------|------------|-----------|
| LLM | Untrusted | None |
| Intent Schema | Trusted | Validation only |
| Policy | Semi-trusted | Suggestive |
| Governor | Trusted | Final decision |
| Executor | Disabled | None |

Only the governor may decide.

---

## Determinism Guarantees

- Same input → same intent
- Same intent → same decision
- Same decision → same audit

Non-determinism is explicitly excluded from the control path.

---

## Failure Model

- Invalid intent → rejected
- Illegal transition → fail-closed to Ø
- LLM failure → deterministic fallback
- No silent acceptance

---

## Status

- Architecture: **LOCKED**
- Trust boundaries: **PROVEN**

