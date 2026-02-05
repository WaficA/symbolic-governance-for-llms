from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Set

from .types import AuditEvent, Decision, Disposition, State, Zone


ALLOWED_TRANSITIONS: Dict[State, Set[State]] = {
    State.A:  {State.O, State.U, State.T},
    State.B:  {State.O, State.U, State.T},
    State.O:  {State.A, State.B, State.U, State.T},
    State.U:  {State.NA, State.NB, State.T},
    State.NA: {State.T, State.C},
    State.NB: {State.T, State.C},
    State.T:  {State.C, State.O},
    State.C:  {State.A, State.B},
}


def zone_for(state: State) -> Zone:
    if state in {State.A, State.B, State.O}:
        return Zone.AMBIGUITY
    if state in {State.U, State.NA, State.NB, State.T}:
        return Zone.BOUNDARY
    return Zone.NONE  # C is not a zone itself


@dataclass
class Governor:
    state: State = State.O  # start in Nil / Ø

    def can_transition(self, nxt: State) -> bool:
        # Self-transition is always allowed (NOOP / stabilization)
        if nxt == self.state:
            return True
        return nxt in ALLOWED_TRANSITIONS[self.state]

    def step(
        self,
        nxt: State,
        disposition: Disposition,
        *,
        audit: List[AuditEvent],
        action_plan: List[Dict[str, Any]] | None = None,
        required_checks: List[str] | None = None,
    ) -> Decision:

        if not self.can_transition(nxt):
            # Deterministic fail-closed behavior
            audit.append(
                AuditEvent(
                    "TRANSITION_DENIED",
                    f"{self.state} -> {nxt} not allowed; forcing Ø",
                )
            )
            self.state = State.O
            return Decision(
                state=self.state,
                zone=Zone.AMBIGUITY,
                disposition="NOOP",
                action_plan=[],
                required_checks=["transition_not_allowed"],
                audit=audit,
            )

        # Legal transition (including self-transition)
        self.state = nxt
        return Decision(
            state=self.state,
            zone=zone_for(self.state),
            disposition=disposition,
            action_plan=action_plan or [],
            required_checks=required_checks or [],
            audit=audit,
        )

