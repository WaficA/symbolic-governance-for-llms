from __future__ import annotations
from typing import List

from .types import AuditEvent, Context, Decision, State
from .machine import Governor
from ..intent.schema import IntentV1


def evaluate_intent(governor: Governor, intent: IntentV1, ctx: Context) -> Decision:
    audit: List[AuditEvent] = []

    # Rule 1: missing goal or empty query => Ø
    if not intent.query.strip() or not intent.goal.strip():
        audit.append(
            AuditEvent("R_MISSING_INTENT", "Empty query/goal -> Ø")
        )
        return governor.step(
            State.O,
            "NOOP",
            audit=audit,
            required_checks=["need_goal"],
        )

    # Rule 2: unknown domain => Ø (ambiguity, not negation)
    if intent.domain in {"unknown", "", "?"}:
        audit.append(
            AuditEvent("R_DOMAIN_UNKNOWN", "Domain unknown -> Ø")
        )
        return governor.step(
            State.O,
            "NOOP",
            audit=audit,
            required_checks=["need_domain"],
        )

    # Rule 3: write intent + dry_run => U (transform)
    wants_write = any(
        a.action_id.startswith("write.")
        for a in intent.requested_actions
    )

    if wants_write and bool(intent.constraints.get("dry_run", False)):
        audit.append(
            AuditEvent(
                "R_DRY_RUN_TRANSFORM",
                "Write requested but dry_run -> U transform",
            )
        )
        plan = [{"action_id": "transform.to_dry_run", "args": {}}]
        return governor.step(
            State.U,
            "TRANSFORM",
            audit=audit,
            action_plan=plan,
        )

    # Rule 4: baseline allow for syntactically valid actions
    if intent.requested_actions:
        unknown = [
            a.action_id
            for a in intent.requested_actions
            if not a.action_id
        ]

        if unknown:
            audit.append(
                AuditEvent(
                    "R_BAD_ACTION",
                    f"Bad action ids: {unknown} -> Ø",
                )
            )
            return governor.step(
                State.O,
                "NOOP",
                audit=audit,
                required_checks=["fix_action_ids"],
            )

        audit.append(
            AuditEvent(
                "R_ALLOW_BASELINE",
                "Intent parsed, no blocking rules -> A",
            )
        )
        return governor.step(
            State.A,
            "ALLOW",
            audit=audit,
            action_plan=[
                {"action_id": a.action_id, "args": a.args}
                for a in intent.requested_actions
            ],
        )

    # Rule 5: no actions => Ø (informational / chat)
    audit.append(
        AuditEvent(
            "R_NO_ACTIONS",
            "No actions requested -> Ø",
        )
    )
    return governor.step(
        State.O,
        "NOOP",
        audit=audit,
    )

