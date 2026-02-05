import pytest

from core.governor.machine import Governor
from core.governor.types import State, Zone
from core.governor.types import AuditEvent


def make_audit():
    return []


def test_self_transition_allowed_for_O():
    """
    Ø → Ø must be allowed (NOOP / stabilization).
    This is the bug we just fixed and must never regress.
    """
    g = Governor(state=State.O)
    audit = make_audit()

    decision = g.step(
        State.O,
        "NOOP",
        audit=audit,
    )

    assert decision.state == State.O
    assert decision.zone == Zone.AMBIGUITY
    assert decision.disposition == "NOOP"
    assert not any(a.rule_id == "TRANSITION_DENIED" for a in decision.audit)


def test_self_transition_allowed_for_any_state():
    """
    Self-transition must be allowed for all states.
    """
    for state in State:
        g = Governor(state=state)
        audit = make_audit()

        decision = g.step(
            state,
            "NOOP",
            audit=audit,
        )

        assert decision.state == state
        assert not any(a.rule_id == "TRANSITION_DENIED" for a in decision.audit)


def test_illegal_transition_is_denied_and_forced_to_O():
    """
    Illegal transitions must fail-closed and force Ø.
    Example: Ø → -A is forbidden.
    """
    g = Governor(state=State.O)
    audit = make_audit()

    decision = g.step(
        State.NA,
        "ALLOW",
        audit=audit,
    )

    assert decision.state == State.O
    assert decision.disposition == "NOOP"
    assert any(a.rule_id == "TRANSITION_DENIED" for a in decision.audit)


def test_legal_transition_O_to_A():
    """
    Ø → A is explicitly allowed by the transition table.
    """
    g = Governor(state=State.O)
    audit = make_audit()

    decision = g.step(
        State.A,
        "ALLOW",
        audit=audit,
    )

    assert decision.state == State.A
    assert decision.zone == Zone.AMBIGUITY
    assert decision.disposition == "ALLOW"


def test_boundary_zone_classification():
    """
    Boundary zone must be correctly classified.
    """
    g = Governor(state=State.U)
    audit = make_audit()

    decision = g.step(
        State.U,
        "NOOP",
        audit=audit,
    )

    assert decision.zone == Zone.BOUNDARY


def test_C_is_not_a_zone():
    """
    C is a frame-shift state, not a zone.
    """
    g = Governor(state=State.C)
    audit = make_audit()

    decision = g.step(
        State.C,
        "NOOP",
        audit=audit,
    )

    assert decision.zone == Zone.NONE

