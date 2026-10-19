#!/usr/bin/env python3
"""Attempt ledger: after N failed tries on the same piece, stop and hand it to the human.
Usage: attempts.py log --piece ID --outcome fail|ok [--note TEXT] [--dir DIR]
       attempts.py check --piece ID [--max 3] [--dir DIR]
The ledger is DIR/.def-infinity/attempts.json (DIR defaults to the current folder), so the count
survives across sessions. check exits 2 when the failures since the last success reach --max."""
import argparse, datetime, json, pathlib, sys

def ledger_path(d):
    return pathlib.Path(d) / ".def-infinity" / "attempts.json"

def load(d):
    p = ledger_path(d)
    return json.loads(p.read_text()) if p.exists() else {}

def failures_since_ok(entries):
    n = 0
    for e in reversed(entries):
        if e["outcome"] == "ok":
            break
        n += 1
    return n

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    lg = sub.add_parser("log"); lg.add_argument("--piece", required=True)
    lg.add_argument("--outcome", required=True, choices=["fail", "ok"]); lg.add_argument("--note", default="")
    ck = sub.add_parser("check"); ck.add_argument("--piece", required=True); ck.add_argument("--max", type=int, default=3)
    for s in (lg, ck):
        s.add_argument("--dir", default=".")
    a = ap.parse_args(argv)
    data = load(a.dir)
    entries = data.setdefault(a.piece, [])
    if a.cmd == "log":
        entries.append({"at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
                        "outcome": a.outcome, "note": a.note})
        p = ledger_path(a.dir); p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(data, indent=1, ensure_ascii=False))
        print(f"logged {a.outcome} for piece {a.piece}: {failures_since_ok(entries)} failure(s) since last success")
        return 0
    n = failures_since_ok(entries)
    if n >= a.max:
        notes = "; ".join(e["note"] for e in entries[-n:] if e["note"])
        print(f"STOP piece {a.piece}: {n} failed attempts (limit {a.max}). Write a blocker for the human. Tried: {notes or 'no notes'}")
        return 2
    print(f"piece {a.piece}: {n} failure(s) since last success, {a.max - n} attempt(s) left")
    return 0

if __name__ == "__main__":
    sys.exit(main())
