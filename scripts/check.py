#!/usr/bin/env python3
"""Self-check for the def-infinity package. Exit 1 on any failure.
Usage: check.py [host_protocol_file]  (optional file whose text must not be copied in)"""
import json, pathlib, re, sys
root = pathlib.Path(__file__).resolve().parent.parent
errors = []
json.loads((root / ".claude-plugin/plugin.json").read_text())
want = {"prototyper", "builder", "sweeper", "grower", "maintainer"}
found = set()
for f in (root / "agents").glob("*.md"):
    m = re.match(r"---\n(.*?)\n---\n", f.read_text(), re.S)
    if not m:
        errors.append(f"{f.name}: no frontmatter"); continue
    meta = dict(l.split(": ", 1) for l in m.group(1).splitlines() if ": " in l)
    if meta.get("name") != f.stem or not meta.get("description"):
        errors.append(f"{f.name}: bad name/description")
    found.add(meta.get("name"))
if found != want:
    errors.append(f"agents: {sorted(found)} != {sorted(want)}")
if not (root / "skills/def-infinity/SKILL.md").exists():
    errors.append("skill missing")
files = [p for p in root.rglob("*") if p.is_file() and ".git" not in p.parts and p.name != "check.py"]
host = []
if len(sys.argv) > 1:
    host = [l.strip() for l in pathlib.Path(sys.argv[1]).read_text().splitlines() if len(l.strip()) > 40]
for p in files:
    t = p.read_text(errors="ignore")
    for bad in ("Flowstate", "/Users/", "BEGIN PRIVATE KEY", "sk-ant-"):
        if bad in t:
            errors.append(f"{p.relative_to(root)}: contains {bad!r}")
    for l in host:
        if l in t:
            errors.append(f"{p.relative_to(root)}: copies host line {l[:50]!r}")
print("\n".join(errors) or f"OK: {len(found)} agents, {len(files)} files checked")
sys.exit(1 if errors else 0)
