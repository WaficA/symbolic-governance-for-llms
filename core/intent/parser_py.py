# core/intent/parser_py.py
from __future__ import annotations
from .schema import IntentV1, RequestedAction, TargetRef

def parse_py(user_text: str) -> IntentV1:
    text = (user_text or "").strip()

    # Phase-1: deterministic "minimal intent"
    # - no actions
    # - domain unknown (forces nil/need_domain in policy unless you decide otherwise)
    return IntentV1(
        intent_version="1",
        query=text,
        domain="unknown",
        goal=text,  # keep it simple: goal == raw text
        requested_actions=[],
        targets=[],
        constraints={"dry_run": True, "read_only_preferred": True},
        observations=[],
    )

