from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Literal, Tuple


class State(str, Enum):
    A  = "A"   # Affirm
    B  = "B"   # Counter-Affirm
    O  = "Ø"   # Nil/Void
    U  = "U"   # Unity/Transform
    NA = "-A"  # Outside-A domain
    NB = "-B"  # Outside-B domain
    T  = "T"   # Transcendence
    C  = "C"   # Context shift


class Zone(str, Enum):
    NONE = "NONE"
    AMBIGUITY = "AMBIGUITY"   # between A,B,Ø
    BOUNDARY  = "BOUNDARY"    # between U,-A,-B,T


Disposition = Literal["ALLOW", "DENY", "NOOP", "TRANSFORM", "ESCALATE", "REFRAME"]


@dataclass(frozen=True)
class AuditEvent:
    rule_id: str
    detail: str


@dataclass(frozen=True)
class Decision:
    state: State
    zone: Zone
    disposition: Disposition
    action_plan: List[Dict[str, Any]] = field(default_factory=list)
    required_checks: List[str] = field(default_factory=list)
    audit: List[AuditEvent] = field(default_factory=list)


@dataclass(frozen=True)
class Context:
    # keep minimal for now; expand later (user role, host mode, safety mode, etc.)
    mode: str = "normal"
    dry_run: bool = False

