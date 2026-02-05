from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal

FORBIDDEN_KEYS = {
    "decision",
    "allow",
    "deny",
    "state",
    "verdict",
    "governor",
    "policy_result",
}


def _scan_forbidden_keys(obj: Any, path: str = "") -> None:
    """
    Recursively scan dicts/lists for forbidden authority keys.
    Raises ValueError on first violation.
    """
    if isinstance(obj, dict):
        for k, v in obj.items():
            key_lower = str(k).lower()
            if key_lower in FORBIDDEN_KEYS:
                raise ValueError(
                    f"Forbidden decision authority key '{k}' found at path '{path or 'root'}'"
                )
            _scan_forbidden_keys(v, f"{path}.{k}" if path else k)

    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            _scan_forbidden_keys(item, f"{path}[{idx}]")


@dataclass(frozen=True)
class RequestedAction:
    action_id: str
    args: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TargetRef:
    type: str
    ref: str


@dataclass(frozen=True)
class IntentV1:
    intent_version: Literal["1"]
    query: str
    domain: str
    goal: str
    requested_actions: List[RequestedAction] = field(default_factory=list)
    targets: List[TargetRef] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)
    observations: List[Dict[str, str]] = field(default_factory=list)


def validate_intent_dict(d: Dict[str, Any]) -> IntentV1:
    # 1. Recursive authority scan (MUST be first)
    _scan_forbidden_keys(d)

    # 2. Version check
    if d.get("intent_version") != "1":
        raise ValueError("intent_version must be '1'")

    # 3. Structural normalization
    ra = [RequestedAction(**x) for x in d.get("requested_actions", [])]
    tg = [TargetRef(**x) for x in d.get("targets", [])]

    return IntentV1(
        intent_version="1",
        query=str(d.get("query", "")),
        domain=str(d.get("domain", "unknown")),
        goal=str(d.get("goal", "")),
        requested_actions=ra,
        targets=tg,
        constraints=dict(d.get("constraints", {})),
        observations=list(d.get("observations", [])),
    )

