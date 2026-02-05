# Threat Model

This system assumes Large Language Models are inherently untrusted.

---

## Threats Addressed

### 1. Hallucinated Authority
LLMs may invent decisions, states, or approvals.

**Mitigation:**
- Schema rejects all authority fields
- Governor ignores model suggestions

---

### 2. Hidden Reasoning
LLMs may embed logic in prose or structure.

**Mitigation:**
- Strict JSON-only parsing
- No extraction from text
- No markdown allowed

---

### 3. Non-Determinism
LLMs produce different outputs for identical inputs.

**Mitigation:**
- LLM output is normalized
- Governor decision is deterministic

---

### 4. Silent Failure
Systems that “sort of work” without guarantees.

**Mitigation:**
- Fail-closed transitions
- Explicit audit trails
- Mandatory validation

---

## Threats Explicitly NOT Addressed

- Model training data bias
- Model internal reasoning correctness
- Natural language truthfulness

This system governs *behavior*, not *knowledge*.

---

## Conclusion

This architecture treats LLMs as probabilistic sensors,
not as decision-makers.

The governor exists to restore control.

