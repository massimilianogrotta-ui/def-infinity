#!/usr/bin/env python3
"""Mechanical gate: are the files this archetype changed inside what it may touch?
Usage: gate.py --archetype <name> [--repo DIR] [--base REF] [--approved] [--json]
Reads changes from git (uncommitted + untracked, plus commits since --base if given).
Exit 0 = allowed, 2 = escalate (a rule was broken), 1 = usage or git error.
It looks only at files. Push, merge, deploy and messages stay with the host's own guards."""
import argparse, json, pathlib, re, subprocess, sys

ALWAYS_DENY = [".env", ".env.*", "**/.env", "**/.env.*", "**/secrets/**", "**/*.pem", "**/*.key",
               "**/id_rsa*", "**/credentials/**"]
TESTS = ["**/test/**", "**/tests/**", "**/__tests__/**", "**/*.test.*", "**/*.spec.*", "**/test_*.py", "**/*_test.*"]
# For each archetype: which paths it may create/modify/delete without the human's --approved.
RULES = {
    "prototyper": {"note": "only its spike folder and spike notes",
                   "allow": [".spike/**", "**/.spike/**", "spike_*.md", "**/spike_*.md"]},
    "grower": {"note": "only experiment notes; real files need a baseline and --approved",
               "allow": ["EXPERIMENT_*.md", "**/EXPERIMENT_*.md"]},
    "maintainer": {"note": "L1: only health notes and its state file; L2/L3: also small edits to existing files",
                   "allow": ["HEALTHCHECK_*.md", "**/HEALTHCHECK_*.md", "MAINTAINER_STATE.md", "**/MAINTAINER_STATE.md"],
                   "l2_max_files": 3},
    "sweeper": {"note": "may edit and delete, may not add files or delete tests without --approved",
                "allow_new": ["UNSHIP_LIST.md", "**/UNSHIP_LIST.md"], "max_files": 15},
    "builder": {"note": "anything except secrets"},
}

def glob_re(g):
    out, i = "", 0
    while i < len(g):
        if g.startswith("**/", i):
            out += "(?:.*/)?"; i += 3
        elif g.startswith("**", i):
            out += ".*"; i += 2
        elif g[i] == "*":
            out += "[^/]*"; i += 1
        elif g[i] == "?":
            out += "[^/]"; i += 1
        else:
            out += re.escape(g[i]); i += 1
    return re.compile(out + r"\Z")

def matches(path, globs):
    return any(glob_re(g).match(path) for g in globs)

def git(repo, *args):
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip() or f"git {' '.join(args)} failed")
    return r.stdout

def changes(repo, base=None):
    """{path: 'A'|'M'|'D'} for uncommitted, untracked and (with base) committed changes."""
    out = {}
    if base:
        for line in git(repo, "diff", "--name-status", "--no-renames", f"{base}...HEAD").splitlines():
            st, p = line.split("\t", 1)
            out[p] = st[0]
    for entry in git(repo, "status", "--porcelain=v1", "--untracked-files=all", "--no-renames", "-z").split("\0"):
        if not entry:
            continue
        xy, p = entry[:2], entry[3:]
        st = "A" if xy == "??" or "A" in xy else ("D" if "D" in xy else "M")
        out[p] = "A" if out.get(p) == "A" and st == "M" else st
    return out

def maintainer_level(repo):
    for f in [repo / "MAINTAINER_STATE.md", *repo.glob("**/MAINTAINER_STATE.md")]:
        if f.is_file():
            m = re.search(r"^\*{0,2}Level:?\*{0,2}:?\s*(L[123])", f.read_text(), re.M)
            return m.group(1) if m else "L1"
    return "L1"

def check(archetype, ch, approved=False, level="L1"):
    rule, bad = RULES[archetype], []
    for p, st in sorted(ch.items()):
        if matches(p, ALWAYS_DENY):
            bad.append((p, st, "secret or env file: never, for any archetype")); continue
        if approved or archetype == "builder":
            continue
        if archetype in ("prototyper", "grower") and not matches(p, rule["allow"]):
            bad.append((p, st, rule["note"]))
        elif archetype == "maintainer" and not matches(p, rule["allow"]):
            if level == "L1":
                bad.append((p, st, "maintainer at L1 reports only"))
            elif st != "M":
                bad.append((p, st, "maintainer may not add or delete files (a new script is a feature)"))
        elif archetype == "sweeper":
            if st == "A" and not matches(p, rule["allow_new"]):
                bad.append((p, st, "sweeper removes, it does not add files"))
            elif st == "D" and matches(p, TESTS):
                bad.append((p, st, "deleting a test needs the human's yes"))
    n = len(ch)
    if not approved and archetype == "sweeper" and n > RULES["sweeper"]["max_files"]:
        bad.append(("*", "", f"{n} files changed, more than {RULES['sweeper']['max_files']}: split the pass"))
    if not approved and archetype == "maintainer" and level != "L1":
        edits = [p for p, st in ch.items() if not matches(p, RULES["maintainer"]["allow"])]
        if len(edits) > RULES["maintainer"]["l2_max_files"]:
            bad.append(("*", "", f"{len(edits)} files edited, more than {RULES['maintainer']['l2_max_files']}"))
    return bad

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--archetype", required=True, choices=sorted(RULES))
    ap.add_argument("--repo", default=".")
    ap.add_argument("--base")
    ap.add_argument("--approved", action="store_true", help="the human said yes to this change")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    repo = pathlib.Path(a.repo).resolve()
    try:
        ch = changes(repo, a.base)
    except RuntimeError as e:
        print(f"gate: {e}", file=sys.stderr); return 1
    level = maintainer_level(repo) if a.archetype == "maintainer" else None
    bad = check(a.archetype, ch, a.approved, level or "L1")
    if a.json:
        print(json.dumps({"archetype": a.archetype, "level": level, "changed": ch,
                          "violations": [{"path": p, "status": s, "rule": r} for p, s, r in bad]}, indent=1))
    elif bad:
        print(f"GATE ESCALATE ({a.archetype}{' ' + level if level else ''}): {len(bad)} problem(s)")
        for p, s, r in bad:
            print(f"  {s or '-'} {p}: {r}")
        print("Undo these changes (or ask the human) and write a blocker; do not finish the piece.")
    else:
        print(f"GATE OK ({a.archetype}{' ' + level if level else ''}): {len(ch)} changed file(s) within the rules")
    return 2 if bad else 0

if __name__ == "__main__":
    sys.exit(main())
