"""
Avalon Decision Engine — State Definitions
Author framework: Wafic Abbass
© AetherMind S.I.C LLC | Project Avalon
"""

from enum import Enum


class State(str, Enum):
    # Layer I — Internal Polarity
    A  = "A"   # Affirm: allow, proceed, approve, activate
    B  = "B"   # Counter-Affirm: deny, block, terminate, reject

    # Layer II — Internal Mediation
    NULL = "Ø"  # Nil/Void: suspend, insufficient context
    U    = "U"  # Unity: dual integration, transformed action

    # Layer III — Domain Negation
    NEG_A = "-A"  # Outside-Allow domain: misclassified request
    NEG_B = "-B"  # Outside-Deny domain: cross-domain error

    # Layer IV — Meta-Level
    T = "T"   # Transcendence: escalate, safe mode, human handoff
    C = "C"   # Context Shift: full domain replacement


# Zones of indeterminacy — not stable states, but transition regions
# A and B are stable resolved states — they do NOT trigger clarification
AMBIGUITY_ZONE  = {State.NULL}                                    # suspended / can't decide
BOUNDARY_ZONE   = {State.U, State.NEG_A, State.NEG_B}            # domain/frame boundary

# Self-resolution defaults when input timeout occurs
ZONE_DEFAULTS = {
    "ambiguity": State.NULL,   # suspend if we can't know
    "boundary":  State.T,      # escalate if we're at a boundary
}


def which_zone(state: State) -> str | None:
    if state in AMBIGUITY_ZONE:
        return "ambiguity"
    if state in BOUNDARY_ZONE:
        return "boundary"
    return None


STATE_DESCRIPTIONS = {
    State.A:     "AFFIRM       — allow / proceed / approve / activate",
    State.B:     "COUNTER      — deny / block / terminate / reject",
    State.NULL:  "NIL          — suspend / insufficient context / withhold",
    State.U:     "UNITY        — dual integration / sandbox / rate-limit / conditional",
    State.NEG_A: "OUTSIDE-A    — request misclassified; does not belong to allow domain",
    State.NEG_B: "OUTSIDE-B    — request misclassified; does not belong to deny domain",
    State.T:     "TRANSCEND    — escalate / safe mode / human handoff / constitutional rule",
    State.C:     "CONTEXT SHIFT— full domain replacement / reframe objective",
}
