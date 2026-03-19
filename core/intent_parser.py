"""
Avalon Decision Engine — LLM Intent Parser
Hits the local Mistral-7B service to classify free-form input
into a structured intent dict for the engine.

Service expected at: http://localhost:9000/generate
"""

import json
import re
import urllib.request
import urllib.error


LLM_ENDPOINT = "http://localhost:9000/generate"

SYSTEM_PROMPT = """You are a decision classifier for an autonomous governance engine.

Your job is to analyze a raw input and return a JSON object that classifies it.

The JSON must contain exactly these fields:
- "action": one of [allow, deny, block, permit, open, approve, activate, terminate, reject, deactivate] or null if unclear
- "trust": one of [verified, partial, unknown]
- "domain": a short string describing the domain (e.g. network, kernel, storage, forensic, runtime) or null
- "contradiction": true if the input contains conflicting signals, false otherwise
- "misclassified": true if the request does not semantically belong to the allow/deny domain, false otherwise
- "escalate": true if the situation requires human intervention or safe mode, false otherwise
- "reframe": true if the entire operational context needs to change, false otherwise

Rules:
- Return ONLY the JSON object. No explanation, no markdown, no extra text.
- If you are uncertain about a field, use the safest default (null or false).
- "contradiction" means the input simultaneously implies both allowing and denying.
- "misclassified" means the request is in the wrong domain entirely.
- "escalate" means the situation is beyond normal allow/deny resolution.
- "reframe" means the operational frame itself must be replaced.

Examples:

Input: "Open port 443 for verified HTTPS traffic"
Output: {"action": "allow", "trust": "verified", "domain": "network", "contradiction": false, "misclassified": false, "escalate": false, "reframe": false}

Input: "Block this process — it looks malicious but I'm not sure"
Output: {"action": "deny", "trust": "unknown", "domain": "kernel", "contradiction": false, "misclassified": false, "escalate": false, "reframe": false}

Input: "Allow and deny this request at the same time for audit purposes"
Output: {"action": "allow", "trust": "partial", "domain": null, "contradiction": true, "misclassified": false, "escalate": false, "reframe": false}

Input: "This is a forensic analysis request, not a runtime permission"
Output: {"action": null, "trust": "unknown", "domain": "forensic", "contradiction": false, "misclassified": true, "escalate": false, "reframe": false}

Input: "Emergency — switch to safe mode immediately"
Output: {"action": null, "trust": "unknown", "domain": null, "contradiction": false, "misclassified": false, "escalate": true, "reframe": false}

Input: "We need to stop treating this as a security problem and reclassify it as a stability issue"
Output: {"action": null, "trust": "unknown", "domain": "stability", "contradiction": false, "misclassified": false, "escalate": false, "reframe": true}

Now classify the following input:
"""


def _call_llm(raw_input: str, endpoint: str = LLM_ENDPOINT) -> str:
    """Send prompt to local Mistral service, return raw text response."""
    prompt = SYSTEM_PROMPT + f'\nInput: "{raw_input}"\nOutput:'

    payload = json.dumps({"prompt": prompt}).encode("utf-8")

    req = urllib.request.Request(
        endpoint,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.loads(response.read().decode("utf-8"))
        return result.get("text", "").strip()


def _extract_json(text: str) -> dict:
    """
    Extract the first valid JSON object from LLM output.
    Handles cases where the model adds extra text around the JSON.
    """
    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to find JSON block within the text
    match = re.search(r'\{[^{}]+\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return {}


def _validate_and_fill(intent: dict, raw_input: str) -> dict:
    """
    Ensure all required fields are present with safe defaults.
    Never lets a malformed LLM response crash the engine.
    """
    valid_actions = {
        "allow", "deny", "block", "permit", "open",
        "approve", "activate", "terminate", "reject", "deactivate"
    }

    action = intent.get("action")
    if action not in valid_actions:
        action = None

    return {
        "action":        action,
        "trust":         intent.get("trust", "unknown") if intent.get("trust") in ("verified", "partial", "unknown") else "unknown",
        "domain":        intent.get("domain") or "unknown",
        "contradiction": bool(intent.get("contradiction", False)),
        "misclassified": bool(intent.get("misclassified", False)),
        "escalate":      bool(intent.get("escalate", False)),
        "reframe":       bool(intent.get("reframe", False)),
        "_raw_input":    raw_input,
    }


def parse_intent(raw_input: str, endpoint: str = LLM_ENDPOINT) -> dict:
    """
    Main entry point.
    Takes a free-form string, returns a structured intent dict.
    Falls back to a safe Ø-bound intent if LLM call fails.
    """
    try:
        llm_output = _call_llm(raw_input, endpoint)
        raw_intent = _extract_json(llm_output)
        intent = _validate_and_fill(raw_intent, raw_input)
        intent["_llm_raw"] = llm_output
        return intent

    except urllib.error.URLError as e:
        # Service unreachable — fail safe
        return {
            "action":        None,
            "trust":         "unknown",
            "domain":        "unknown",
            "contradiction": False,
            "misclassified": False,
            "escalate":      False,
            "reframe":       False,
            "_raw_input":    raw_input,
            "_error":        f"LLM service unreachable: {e}",
        }

    except Exception as e:
        return {
            "action":        None,
            "trust":         "unknown",
            "domain":        "unknown",
            "contradiction": False,
            "misclassified": False,
            "escalate":      False,
            "reframe":       False,
            "_raw_input":    raw_input,
            "_error":        f"Parser error: {e}",
        }
