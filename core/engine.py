"""
Avalon Decision Engine — Core Engine
State machine with indeterminate zone handling:
  - Requests more input when in an indeterminate zone
  - Self-resolves if no input is provided within max_attempts
"""

import time
from dataclasses import dataclass, field
from typing import Callable

from .states import State, STATE_DESCRIPTIONS, ZONE_DEFAULTS, which_zone
from .transitions import is_valid_transition, valid_next_states


@dataclass
class Decision:
    """A record of a single state transition."""
    from_state:  State
    to_state:    State
    reason:      str
    timestamp:   float = field(default_factory=time.time)
    self_resolved: bool = False

    def __str__(self):
        tag = " [SELF-RESOLVED]" if self.self_resolved else ""
        return (
            f"  {self.from_state.value:>4} → {self.to_state.value:<4} "
            f"| {self.reason}{tag}"
        )


class AvalonEngine:
    """
    The Avalon decision state machine.

    Usage:
        engine = AvalonEngine()
        result = engine.evaluate(intent, input_fn=my_input_function)
    """

    def __init__(
        self,
        initial_state: State = State.NULL,
        max_clarification_attempts: int = 2,
        verbose: bool = True,
    ):
        self.state = initial_state
        self.max_clarification_attempts = max_clarification_attempts
        self.verbose = verbose
        self.history: list[Decision] = []

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def evaluate(
        self,
        intent: dict,
        input_fn: Callable[[str], str | None] = None,
    ) -> State:
        self._log(f"\n{'='*60}")
        self._log(f"  INTENT  : {intent}")
        self._log(f"  ENTRY   : {self._describe(self.state)}")
        self._log(f"{'='*60}")

        # Step 1: classify intent into initial target state
        target = self._classify(intent)
        self._transition(target, reason=f"classified intent as '{intent.get('action', '?')}'")

        # Step 2: continue driving for multi-hop intents
        # reframe: T -> C -> A/B
        if intent.get("reframe") and self.state == State.T:
            self._transition(State.C, reason="reframe: entering context shift")
            # C resolves back to A or B based on original action
            action = (intent.get("action") or "").lower()
            final = State.A if action in ("allow", "permit", "open", "approve", "activate", "proceed") else State.B
            self._transition(final, reason="reframe complete: returning to operational state")

        # misclassified: U -> -A or -B
        elif intent.get("misclassified") and self.state == State.U:
            action = (intent.get("action") or "").lower()
            neg = State.NEG_A if action in ("allow", "permit", "open") else State.NEG_B
            self._transition(neg, reason="misclassified: domain negation")
            self._transition(State.T, reason="domain negation: escalating to transcendence")

        # Step 3: if still in indeterminate zone, try to resolve
        zone = which_zone(self.state)
        if zone:
            self._resolve_indeterminate(zone, intent, input_fn)

        self._log(f"\n  FINAL   : {self._describe(self.state)}")
        self._log(f"{'='*60}\n")
        return self.state

    def force_transition(self, to_state: State, reason: str = "manual") -> bool:
        """Manually force a transition — validates against transition table."""
        if is_valid_transition(self.state, to_state):
            self._transition(to_state, reason=reason)
            return True
        self._log(f"  INVALID : {self.state.value} → {to_state.value} not allowed")
        return False

    def reset(self, state: State = State.NULL):
        self.state = state
        self.history.clear()

    def print_history(self):
        print("\n  Decision History:")
        for d in self.history:
            print(d)

    # ------------------------------------------------------------------
    # Internal logic
    # ------------------------------------------------------------------

    def _classify(self, intent: dict) -> State:
        """
        Maps an intent dict to an initial target state.
        Respects the transition table — if a direct jump is invalid,
        routes through a valid intermediate state.
        """
        action = (intent.get("action") or "").lower()
        trust  = (intent.get("trust") or "unknown").lower()
        contradiction = intent.get("contradiction", False)
        misclassified = intent.get("misclassified", False)
        escalate      = intent.get("escalate", False)
        reframe       = intent.get("reframe", False)

        # Reframe requires C — must go through T first if at Ø
        if reframe:
            return State.T  # T -> C is valid; engine will continue from T

        # Escalate directly
        if escalate:
            return State.T

        # Misclassified — must reach -A or -B via U (Ø -> U -> -A/-B)
        if misclassified:
            return State.U  # caller will continue to -A/-B from U

        # Contradiction — Unity state
        if contradiction:
            return State.U

        # Insufficient context
        if trust == "unknown" or not action:
            return State.NULL

        # Clean actions
        if action in ("allow", "permit", "open", "approve", "activate", "proceed"):
            return State.A
        if action in ("deny", "block", "kill", "reject", "terminate", "deactivate"):
            return State.B

        return State.NULL

    def _resolve_indeterminate(
        self,
        zone: str,
        intent: dict,
        input_fn: Callable | None,
    ):
        """
        When in an indeterminate zone:
        1. Ask for more input (up to max_clarification_attempts)
        2. Try to reclassify with enriched intent
        3. Self-resolve if still unresolved
        """
        attempts = 0
        while attempts < self.max_clarification_attempts:
            attempts += 1
            self._log(f"\n  ZONE    : {zone.upper()} — requesting clarification "
                      f"(attempt {attempts}/{self.max_clarification_attempts})")

            if input_fn is None:
                clarification = None
            else:
                prompt = self._clarification_prompt(zone, intent, attempts)
                clarification = input_fn(prompt)

            if clarification:
                # Enrich intent and reclassify
                intent["_clarification"] = clarification
                intent = self._parse_clarification(clarification, intent)
                target = self._classify(intent)
                zone_check = which_zone(target)

                if zone_check is None:
                    # Resolved to a stable state
                    self._transition(target, reason=f"resolved via clarification: '{clarification}'")
                    return
                else:
                    self._log(f"  STILL INDETERMINATE after clarification.")
            else:
                self._log(f"  NO INPUT received.")

        # Self-resolve
        default = ZONE_DEFAULTS[zone]
        if default == self.state:
            # Already in the default state — log it, no transition needed
            self._log(f"  HOLD    : remaining in {self.state.value} — no resolution after {attempts} attempts")
            decision = Decision(
                from_state=self.state,
                to_state=self.state,
                reason=f"held in {self.state.value} after {attempts} failed clarification attempts",
                self_resolved=True,
            )
            self.history.append(decision)
        else:
            self._transition(
                default,
                reason=f"self-resolved after {attempts} failed clarification attempts",
                self_resolved=True,
            )

    def _parse_clarification(self, clarification: str, intent: dict) -> dict:
        """
        Minimal clarification parser.
        In production this would be an NLP/LLM step.
        Here we do simple keyword enrichment.
        """
        c = clarification.lower()
        enriched = dict(intent)

        if any(w in c for w in ("allow", "permit", "yes", "proceed", "open")):
            enriched["action"] = "allow"
            enriched["trust"]  = "verified"
        elif any(w in c for w in ("deny", "block", "no", "reject", "kill")):
            enriched["action"] = "deny"
            enriched["trust"]  = "verified"
        elif any(w in c for w in ("sandbox", "limit", "partial", "conditional")):
            enriched["contradiction"] = True
        elif any(w in c for w in ("escalate", "human", "safe mode")):
            enriched["escalate"] = True

        return enriched

    def _clarification_prompt(self, zone: str, intent: dict, attempt: int) -> str:
        if zone == "ambiguity":
            return (
                f"[Avalon] Ambiguous intent detected: '{intent.get('action', '?')}' "
                f"with trust='{intent.get('trust', '?')}'. "
                f"Please clarify: allow / deny / sandbox / escalate?"
            )
        else:
            return (
                f"[Avalon] Domain boundary reached. Current frame may be invalid. "
                f"Confirm domain or escalate to higher policy? (attempt {attempt})"
            )

    def _transition(self, to_state: State, reason: str, self_resolved: bool = False):
        if not is_valid_transition(self.state, to_state):
            if to_state != self.state:  # only log if it's actually an attempted move
                self._log(f"  BLOCKED : {self.state.value} → {to_state.value} "
                          f"not in transition table. Staying in {self.state.value}.")
            return

        decision = Decision(
            from_state=self.state,
            to_state=to_state,
            reason=reason,
            self_resolved=self_resolved,
        )
        self.history.append(decision)
        self._log(str(decision))
        self.state = to_state

    def _describe(self, state: State) -> str:
        return f"{state.value} — {STATE_DESCRIPTIONS[state]}"

    def _log(self, msg: str):
        if self.verbose:
            print(msg)
