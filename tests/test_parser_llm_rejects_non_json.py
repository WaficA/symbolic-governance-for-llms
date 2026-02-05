from __future__ import annotations

import json
from typing import Any, Dict, Callable, Tuple, Union

from core.intent.parser_llm import parse_llm, IntentParseError


class IntentParseError(Exception):
    pass


def _parse_strict_json(text: str) -> Dict[str, Any]:
    """
    Strict JSON parser.

    Rules:
    - Input must be non-empty
    - Input must start with '{' and end with '}'
    - Parsed value must be a dict (not list, not scalar)
    - No markdown, no prose, no extraction
    """
    if not text or not text.strip():
        raise IntentParseError("Empty LLM output")

    s = text.strip()

    # Hard reject markdown or prose
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
  "constraints": {{"dry_run": true}},
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

    LLM is untrusted.
    Any contract violation raises IntentParseError.
    """
    prompt = _intent_prompt(user_text)

    out = ask_llm(prompt)
    reply = out[0] if isinstance(out, tuple) else out

    data = _parse_strict_json(reply)
    return validate_intent_dict(data)

