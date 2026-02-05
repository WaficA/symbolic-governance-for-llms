# shell/orchestrator.py
from __future__ import annotations

from core.intent.parser_py import parse_py
from core.intent.parser_llm import parse_llm, IntentParseError
from core.governor import Governor, Context, evaluate_intent
from core.llm_client import ask_llm
from core.metrics.intent_metrics import IntentMetrics

_metrics = IntentMetrics()


# -----------------------------
# Configuration
# -----------------------------

# Phase-1: "py"
# Phase-2: "llm"
PARSER_MODE = "llm"


# -----------------------------
# Persistent governor instance
# -----------------------------

_governor = Governor()


# -----------------------------
# Orchestration
# -----------------------------

def run_turn(user_text: str):
    """
    Single orchestration step:
    text -> intent -> governor -> decision
    """
    used_fallback = False

    if PARSER_MODE == "llm":
        try:
            intent = parse_llm(user_text, ask_llm=ask_llm)
            _metrics.record_llm_success()
        except IntentParseError:
            _metrics.record_llm_failure()
            intent = parse_py(user_text)
            _metrics.record_fallback()
            used_fallback = True
    else:
        intent = parse_py(user_text)

    ctx = Context(dry_run=True)
    decision = evaluate_intent(_governor, intent, ctx)

    _metrics.record_state(decision.state.value)

    return intent, decision, used_fallback


