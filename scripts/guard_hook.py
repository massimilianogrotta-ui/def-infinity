#!/usr/bin/env python3
"""PreToolUse hook: stops an archetype BEFORE it writes outside its rules (same rules as gate.py).
Acts only when the call comes from one of the five archetypes (hook input field agent_type);
any other agent or the plain main session passes through untouched."""
import json, os, pathlib, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gate import ALWAYS_DENY, RULES, matches, maintainer_level  # noqa: E402

PUSHY = re.compile(r"\bgit\b[^;&|\n]*\spush\b|\bgh\s+(?:pr\s+(?:create|merge)|release|repo\s+(?:create|delete))\b")

REDIRECT = re.compile(r"(?<![<>&0-9])>{1,2}\s*([^\s;&|<>()]+)")
TEE = re.compile(r"\btee\s+(?:-a\s+)?([^\s;&|<>()]+)")
CPMV = re.compile(r"\b(?:cp|mv|install)\s+(?:-[a-zA-Z]+\s+)*\S+\s+([^\s;&|<>()]+)")
TOUCH = re.compile(r"\btouch\s+([^;&|<>()]+)")
RM = re.compile(r"\b(?:rm|git\s+rm)\s+(?:-[a-zA-Z]+\s+)*([^;&|<>()]+)")
SEDI = re.compile(r"\bsed\s+(?:-[a-zA-Z]*i[a-zA-Z]*\S*)\s+(?:'[^']*'|\"[^\"]*\"|\S+)\s+([^;&|<>()]+)")
PKG = re.compile(r"\b(?:npm|pnpm|yarn)\s+(?:install|i|add|remove|uninstall|rm|pkg\s+set)\b")

def strip_heredocs(cmd):
    out, lines, i = [], cmd.split("\n"), 0
    while i < len(lines):
        out.append(lines[i])
        m = re.search(r"<<-?\s*['\"]?(\w+)['\"]?", lines[i])
        i += 1
        if m:
            while i < len(lines) and lines[i].strip() != m.group(1):
                i += 1
            i += 1
    return "\n".join(out)

def bash_targets(cmd):
    """Best-effort list of (path, 'write'|'delete') a shell command touches. gate.py stays the net."""
    c, out = strip_heredocs(cmd), []
    for rx in (REDIRECT, TEE, CPMV):
        out += [(m.group(1), "write") for m in rx.finditer(c)]
    for rx, kind in ((TOUCH, "write"), (SEDI, "write"), (RM, "delete")):
        for m in rx.finditer(c):
            out += [(t, kind) for t in m.group(1).split() if not t.startswith("-")]
    if PKG.search(c):
        out.append(("package.json", "write"))
    return [(t.strip("'\""), k) for t, k in out if t not in ("/dev/null", "/dev/stderr", "/dev/stdout")]

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
        cmd = inp.get("command", "")
        if PUSHY.search(cmd):
            return f"{agent} may not push, merge or publish: write a blocker with your recommended answer"
        for raw, kind in bash_targets(cmd):
            why = decide_path(agent, cwd, raw, kind)
            if why:
                return why + " (via a shell command)"
        return None
    raw = inp.get("file_path") or inp.get("notebook_path")
    return decide_path(agent, cwd, raw, "write") if raw else None

def decide_path(agent, cwd, raw, kind):
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
    if kind == "delete":
        if agent == "sweeper":
            from gate import TESTS
            return f"deleting a test ({rel}) needs the human's yes" if matches(rel, TESTS) else None
        if matches(rel, RULES.get(agent, {}).get("allow", [])):
            return None
        return f"{agent} may not delete project files ({rel})"
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
