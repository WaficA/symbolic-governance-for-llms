from __future__ import annotations

import json
from typing import Any, Dict, Tuple, Union, Callable

from .schema import IntentV1, validate_intent_dict


class IntentParseError(Exception):
    """
    Raised when LLM output violates the intent parsing contract.
    All LLM parsing failures are normalized to this exception.
    """
    pass


def _parse_strict_json_object(text: str) -> Dict[str, Any]:
    """
    Strict JSON parser.

    Contract:
    - Output must be non-empty
    - Output must start with '{' and end with '}'
    - Parsed value must be a dict
    - No markdown, no prose, no extraction
    """
    if not text or not text.strip():
        raise IntentParseError("Empty LLM output")

    s = text.strip()

    # Enforce raw JSON object only
    if not (s.startswith("{") and s.endswith("}")):
        raise IntentParseError("LLM output is not a raw JSON object")

    try:
        obj = json.loads(s)
    except json.JSONDecodeError as e:
        raise IntentParseError(f"Invalid JSON: {e}") from None

    if not isinstance(obj, dict):
        raise IntentParseError("Top-level JSON must be an object")

    return obj


def _intent_prompt(user_text: str) -> str:
    """
    Contract prompt: LLM must emit exactly one JSON object.
    """
    return f"""
Output EXACTLY one JSON object and nothing else.

Rules:
- Output must be valid JSON
- Top-level value must be an object
- Do NOT use markdown
- Do NOT include keys: decision, allow, deny, state, verdict, governor, policy_result

Schema:
{{
  "intent_version": "1",
  "query": "<raw user text>",
  "domain": "<string>",
  "goal": "<short phrase>",
  "requested_actions": [],
  "targets": [],
  "constraints": {{"dry_run": true, "read_only_preferred": true}},
  "observations": []
}}

User text:
{user_text}
""".strip()


def parse_llm(
    user_text: str,
    ask_llm: Callable[[str], Union[str, Tuple[str, int, int]]],
) -> IntentV1:
    """
    Phase-2 LLM intent parser.

    LLM is treated as untrusted input.
    Any violation of the contract raises IntentParseError.
    """
    prompt = _intent_prompt(user_text)

    out = ask_llm(prompt)
    reply = out[0] if isinstance(out, tuple) else out

    # 1. Strict JSON parsing
    data = _parse_strict_json_object(reply)

    # 2. Schema validation + authority enforcement
    try:
        return validate_intent_dict(data)
    except ValueError as e:
        # Normalize all schema failures to IntentParseError
        raise IntentParseError(str(e)) from None

