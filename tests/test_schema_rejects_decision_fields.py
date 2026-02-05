import pytest

from core.intent.schema import validate_intent_dict


def base_intent():
    """
    Minimal valid intent payload.
    Used as a base for mutation tests.
    """
    return {
        "intent_version": "1",
        "query": "hello",
        "domain": "test",
        "goal": "test goal",
        "requested_actions": [],
        "targets": [],
        "constraints": {},
        "observations": [],
    }


@pytest.mark.parametrize(
    "forbidden_key",
    [
        "decision",
        "state",
        "verdict",
        "allow",
        "deny",
        "policy_result",
        "governor",
    ],
)
def test_rejects_decision_authority_fields(forbidden_key):
    """
    Any attempt to inject decision authority into the intent
    must be rejected at schema validation time.
    """
    payload = base_intent()
    payload[forbidden_key] = "A"

    with pytest.raises(ValueError):
        validate_intent_dict(payload)


def test_rejects_nested_decision_authority_fields():
    """
    Even if decision-like fields are nested, they must be rejected.
    """
    payload = base_intent()
    payload["meta"] = {
        "decision": "ALLOW",
        "state": "A",
    }

    with pytest.raises(ValueError):
        validate_intent_dict(payload)


def test_accepts_clean_intent():
    """
    A clean intent without authority leakage must pass.
    """
    payload = base_intent()
    intent = validate_intent_dict(payload)

    assert intent.intent_version == "1"
    assert intent.query == "hello"
    assert intent.goal == "test goal"

