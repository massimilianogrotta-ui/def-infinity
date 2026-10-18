#!/usr/bin/env python3
"""Does the plan's mix of archetypes fit the product's stage? A warning, never a block.
Usage: stage_check.py <plan.md> [--stage new|growing|mature]
The stage is declared by the human (a "Product stage:" line in the plan or the alignment note, or --stage).
Each plan piece names its archetype on an "Archetype:" line; the first archetype named is the main one.
Mix per stage, after Boris Cherny: new = 1+2+3, growing = 2+3+4 and some 5, mature = 3+4+5 and some 2.
Exit 0 always when the plan was read (warnings are printed); 1 if the stage or the pieces cannot be found."""
import argparse, collections, pathlib, re, sys

NAMES = ["prototyper", "builder", "sweeper", "grower", "maintainer"]
MIX = {"new": ({"prototyper", "builder", "sweeper"}, set()),
       "growing": ({"builder", "sweeper", "grower"}, {"maintainer"}),
       "mature": ({"sweeper", "grower", "maintainer"}, {"builder"})}
ALIASES = {"nuovo": "new", "in crescita": "growing", "crescita": "growing", "maturo": "mature"}

def read_stage(text):
    m = re.search(r"Product stage\**:?\**\s*:?\s*([A-Za-z ]+)", text, re.I)
    if not m:
        return None
    v = m.group(1).strip().lower()
    for k in list(MIX) + list(ALIASES):
        if v.startswith(k):
            return ALIASES.get(k, k)
    return None

def read_archetypes(text):
    out = []
    for m in re.finditer(r"^\s*[-*]?\s*\**Archetype\**:?\**\s*:?\s*(.+)$", text, re.I | re.M):
        line = m.group(1).lower()
        hits = sorted((line.find(n), n) for n in NAMES if n in line)
        out.append(hits[0][1] if hits else "n/a")
    return out

def report(stage, archs):
    core, some = MIX[stage]
    counted = collections.Counter(a for a in archs if a != "n/a")
    lines, warn = [f"Product stage: {stage} · expected mix: {' + '.join(sorted(core))}"
                   + (f", some {', '.join(sorted(some))}" if some else ""),
                   "Pieces per archetype: " + (", ".join(f"{a} {n}" for a, n in sorted(counted.items())) or "none")], []
    for a in sorted(set(counted) - core - some):
        warn.append(f"{a} is not in the mix for a {stage} product ({counted[a]} piece(s)): is that work for now?")
    if len(archs) >= 3:
        for a in sorted(core - set(counted)):
            warn.append(f"no {a} piece: a {stage} product usually needs one")
    lines += [f"WARN: {w}" for w in warn] or ["OK: the mix fits the stage"]
    return lines, warn

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("plan"); ap.add_argument("--stage", choices=sorted(MIX))
    a = ap.parse_args(argv)
    text = pathlib.Path(a.plan).read_text()
    stage = a.stage or read_stage(text)
    archs = read_archetypes(text)
    if not stage:
        print("stage_check: no 'Product stage:' line and no --stage: ask the human which stage the product is in"); return 1
    if not archs:
        print("stage_check: no 'Archetype:' lines found in the plan"); return 1
    print("\n".join(report(stage, archs)[0]))
    return 0

if __name__ == "__main__":
    sys.exit(main())
