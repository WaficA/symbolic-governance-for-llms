"""
Avalon Decision Engine — Transition Table
Derived directly from the micro-policy language in the paper.
"""

from .states import State

# Exact transition map from the paper (Section 4)
TRANSITIONS: dict[State, list[State]] = {
    State.A:     [State.NULL, State.U, State.T],
    State.B:     [State.NULL, State.U, State.T],
    State.NULL:  [State.A, State.B, State.U, State.T],
    State.U:     [State.NEG_A, State.NEG_B, State.T],
    State.NEG_A: [State.T, State.C],
    State.NEG_B: [State.T, State.C],
    State.T:     [State.C, State.NULL],
    State.C:     [State.A, State.B],
}


def is_valid_transition(from_state: State, to_state: State) -> bool:
    return to_state in TRANSITIONS.get(from_state, [])


def valid_next_states(from_state: State) -> list[State]:
    return TRANSITIONS.get(from_state, [])
