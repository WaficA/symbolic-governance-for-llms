from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class IntentMetrics:
    """
    Pure instrumentation.
    No logic, no decisions, no side effects.
    """
    llm_parse_success: int = 0
    llm_parse_failure: int = 0
    fallback_used: int = 0

    state_counts: Dict[str, int] = field(default_factory=dict)

    def record_llm_success(self):
        self.llm_parse_success += 1

    def record_llm_failure(self):
        self.llm_parse_failure += 1

    def record_fallback(self):
        self.fallback_used += 1

    def record_state(self, state: str):
        self.state_counts[state] = self.state_counts.get(state, 0) + 1

    def snapshot(self) -> Dict[str, object]:
        return {
            "llm_parse_success": self.llm_parse_success,
            "llm_parse_failure": self.llm_parse_failure,
            "fallback_used": self.fallback_used,
            "state_counts": dict(self.state_counts),
        }

