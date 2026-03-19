"""
Avalon Decision Engine — Test Suite
Tests every stable state, both indeterminate zones, and all transition paths.
Run with: python -m pytest tests/ -v
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from core import AvalonEngine, State
from core.transitions import is_valid_transition, valid_next_states


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def make_engine():
    return AvalonEngine(initial_state=State.NULL, max_clarification_attempts=2, verbose=False)


def no_input(prompt):
    return None


def input_returning(value):
    return lambda prompt: value


# ------------------------------------------------------------------
# Transition table integrity
# ------------------------------------------------------------------

class TestTransitionTable(unittest.TestCase):

    def test_all_states_have_transitions(self):
        for state in State:
            assert len(valid_next_states(state)) > 0, f"{state} has no valid transitions"

    def test_known_valid_transitions(self):
        assert is_valid_transition(State.NULL, State.A)
        assert is_valid_transition(State.NULL, State.B)
        assert is_valid_transition(State.NULL, State.U)
        assert is_valid_transition(State.NULL, State.T)
        assert is_valid_transition(State.A, State.NULL)
        assert is_valid_transition(State.A, State.U)
        assert is_valid_transition(State.A, State.T)
        assert is_valid_transition(State.U, State.NEG_A)
        assert is_valid_transition(State.U, State.NEG_B)
        assert is_valid_transition(State.U, State.T)
        assert is_valid_transition(State.NEG_A, State.T)
        assert is_valid_transition(State.NEG_A, State.C)
        assert is_valid_transition(State.T, State.C)
        assert is_valid_transition(State.T, State.NULL)
        assert is_valid_transition(State.C, State.A)
        assert is_valid_transition(State.C, State.B)

    def test_known_invalid_transitions(self):
        assert not is_valid_transition(State.A, State.B)    # no direct polarity flip
        assert not is_valid_transition(State.B, State.A)
        assert not is_valid_transition(State.NULL, State.C) # can't jump to C from Ø
        assert not is_valid_transition(State.NULL, State.NEG_A)
        assert not is_valid_transition(State.A, State.C)
        assert not is_valid_transition(State.C, State.T)    # C only returns to A or B


# ------------------------------------------------------------------
# Layer I — Clean polarity decisions
# ------------------------------------------------------------------

class TestLayerI(unittest.TestCase):

    def test_clean_allow(self):
        e = make_engine()
        result = e.evaluate({"action": "allow", "domain": "network", "trust": "verified"})
        assert result == State.A

    def test_clean_deny(self):
        e = make_engine()
        result = e.evaluate({"action": "block", "domain": "network", "trust": "verified"})
        assert result == State.B

    def test_permit_maps_to_affirm(self):
        e = make_engine()
        result = e.evaluate({"action": "permit", "trust": "verified"})
        assert result == State.A

    def test_terminate_maps_to_counter(self):
        e = make_engine()
        result = e.evaluate({"action": "terminate", "trust": "verified"})
        assert result == State.B


# ------------------------------------------------------------------
# Layer II — Mediation states
# ------------------------------------------------------------------

class TestLayerII(unittest.TestCase):

    def test_unknown_trust_enters_null(self):
        e = make_engine()
        result = e.evaluate({"action": "allow", "trust": "unknown"}, input_fn=no_input)
        assert result == State.NULL

    def test_unknown_trust_resolves_via_clarification(self):
        e = make_engine()
        result = e.evaluate(
            {"action": "open", "trust": "unknown"},
            input_fn=input_returning("allow"),
        )
        assert result == State.A

    def test_contradiction_enters_unity(self):
        e = make_engine()
        result = e.evaluate({
            "action": "allow", "trust": "partial", "contradiction": True
        }, input_fn=no_input)
        assert result == State.T  # U self-resolves to T when no clarification


# ------------------------------------------------------------------
# Layer III — Domain negation
# ------------------------------------------------------------------

class TestLayerIII(unittest.TestCase):

    def test_misclassified_allow_reaches_neg_a_then_t(self):
        e = make_engine()
        result = e.evaluate({
            "action": "allow", "domain": "forensic",
            "trust": "verified", "misclassified": True
        })
        assert result == State.T
        states_visited = [d.to_state for d in e.history]
        assert State.U in states_visited
        assert State.NEG_A in states_visited
        assert State.T in states_visited

    def test_misclassified_deny_reaches_neg_b_then_t(self):
        e = make_engine()
        result = e.evaluate({
            "action": "deny", "domain": "forensic",
            "trust": "verified", "misclassified": True
        })
        assert result == State.T
        states_visited = [d.to_state for d in e.history]
        assert State.NEG_B in states_visited


# ------------------------------------------------------------------
# Layer IV — Meta-level states
# ------------------------------------------------------------------

class TestLayerIV(unittest.TestCase):

    def test_escalate_reaches_transcendence(self):
        e = make_engine()
        result = e.evaluate({"action": "allow", "trust": "verified", "escalate": True})
        assert result == State.T

    def test_reframe_full_path(self):
        e = make_engine()
        result = e.evaluate({
            "action": "allow", "domain": "runtime",
            "trust": "verified", "reframe": True
        })
        assert result == State.A
        states_visited = [d.to_state for d in e.history]
        assert State.T in states_visited
        assert State.C in states_visited
        assert State.A in states_visited

    def test_reframe_deny_returns_to_b(self):
        e = make_engine()
        result = e.evaluate({
            "action": "block", "domain": "runtime",
            "trust": "verified", "reframe": True
        })
        assert result == State.B


# ------------------------------------------------------------------
# Self-resolution behavior
# ------------------------------------------------------------------

class TestSelfResolution(unittest.TestCase):

    def test_ambiguity_self_resolves_to_null(self):
        e = make_engine()
        result = e.evaluate({"action": "open", "trust": "unknown"}, input_fn=no_input)
        assert result == State.NULL

    def test_boundary_self_resolves_to_t(self):
        e = make_engine()
        result = e.evaluate(
            {"action": "allow", "trust": "partial", "contradiction": True},
            input_fn=no_input,
        )
        assert result == State.T

    def test_clarification_on_second_attempt(self):
        """First attempt returns nothing, second returns a valid answer."""
        attempts = [0]
        def delayed_input(prompt):
            attempts[0] += 1
            if attempts[0] == 1:
                return None
            return "deny"

        e = make_engine()
        result = e.evaluate({"action": "open", "trust": "unknown"}, input_fn=delayed_input)
        assert result == State.B


# ------------------------------------------------------------------
# Force transition
# ------------------------------------------------------------------

class TestForceTransition(unittest.TestCase):

    def test_valid_force(self):
        e = make_engine()
        e.state = State.NULL
        success = e.force_transition(State.A, reason="test")
        assert success
        assert e.state == State.A

    def test_invalid_force_blocked(self):
        e = make_engine()
        e.state = State.A
        success = e.force_transition(State.B, reason="test")  # A->B not in table
        assert not success
        assert e.state == State.A  # unchanged


# ------------------------------------------------------------------
# History audit
# ------------------------------------------------------------------

class TestHistory(unittest.TestCase):

    def test_history_recorded(self):
        e = make_engine()
        e.evaluate({"action": "allow", "trust": "verified"})
        assert len(e.history) >= 1

    def test_self_resolved_flagged(self):
        e = make_engine()
        e.evaluate({"action": "open", "trust": "unknown"}, input_fn=no_input)
        self_resolved = [d for d in e.history if d.self_resolved]
        assert len(self_resolved) >= 1

    def test_reset_clears_history(self):
        e = make_engine()
        e.evaluate({"action": "allow", "trust": "verified"})
        e.reset()
        assert len(e.history) == 0
        assert e.state == State.NULL

if __name__ == '__main__':
    unittest.main()
