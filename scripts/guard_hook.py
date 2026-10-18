#!/usr/bin/env python3
"""PreToolUse hook: stops an archetype BEFORE it writes outside its rules (same rules as gate.py).
Acts only when the call comes from one of the five archetypes (hook input field agent_type);
any other agent or the plain main session passes through untouched."""
import json, os, pathlib, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gate import ALWAYS_DENY, RULES, matches, maintainer_level  # noqa: E402

PUSHY = re.compile(r"\bgit\b[^;&|\n]*\spush\b|\bgh\s+(?:pr\s+(?:create|merge)|release|repo\s+(?:create|delete))\b")

def deny(reason):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                             "permissionDecisionReason": f"def-infinity gate: {reason}"}}))
    return 0

def decide(event):
    agent = (event.get("agent_type") or "").split(":")[-1]
    if agent not in RULES:
        return None
    tool, inp = event.get("tool_name", ""), event.get("tool_input") or {}
    cwd = pathlib.Path(event.get("cwd") or os.getcwd()).resolve()
    if tool == "Bash":
        if PUSHY.search(inp.get("command", "")):
            return f"{agent} may not push, merge or publish: write a blocker with your recommended answer"
        return None
    raw = inp.get("file_path") or inp.get("notebook_path")
    if not raw:
        return None
    target = (cwd / raw).resolve()
    try:
        rel = target.relative_to(cwd).as_posix()
    except ValueError:
        return None if agent == "builder" else f"{agent} may write only inside the work folder ({raw} is outside)"
    if matches(rel, ALWAYS_DENY):
        return f"{rel} is a secret or env file: never"
    exists = target.exists()
    if agent == "builder":
        return None
    if agent in ("prototyper", "grower"):
        return None if matches(rel, RULES[agent]["allow"]) else f"{agent}: {RULES[agent]['note']} ({rel} is not)"
    if agent == "maintainer":
        if matches(rel, RULES["maintainer"]["allow"]):
            return None
        level = maintainer_level(cwd)
        if level == "L1":
            return f"maintainer at L1 reports only: put the proposed change for {rel} in the health note"
        if not exists:
            return f"maintainer may not add files ({rel}): a new script or mechanism is a feature for the Builder"
        return None
    if agent == "sweeper" and not exists and not matches(rel, RULES["sweeper"]["allow_new"]):
        return f"sweeper removes, it does not add files ({rel})"
    return None

def main():
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0  # never break the session on a malformed event
    reason = decide(event)
    return deny(reason) if reason else 0

if __name__ == "__main__":
    sys.exit(main())
