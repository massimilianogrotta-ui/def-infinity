# DEF ∞

Five work archetypes as Claude Code subagents, grafted onto a plan-first, proof-first build protocol.

Status: validated on 2 real tasks (A/B/blind-review each), both in favor. See `docs/RISULTATI.md`.

## Why
A good build protocol (align, research with sources, plan in pieces, lock in, run with proofs) mostly covers one kind of work: building an approved thing well. Products need four more kinds of work, as Boris Cherny pointed out: exploring many ideas and throwing most away, removing and simplifying, growing what runs using data, and keeping what runs healthy. DEF ∞ adds those four next to the builder without changing the protocol's rules.

## What is inside
- `agents/`: prototyper, builder, sweeper, grower, maintainer — five Claude Code subagents, each with its own rules, limits and output format.
- `skills/def-infinity/`: the three hooks that connect the five archetypes to a plan-first protocol, plus a cost rule so they only fire when they earn their keep.
- `templates/`: spike findings, unship list, experiment, health check — the artifact shape each archetype promises.
- `scripts/check.py`: package self-check (frontmatter valid, no machine-specific paths, no copied host-protocol text).
- `docs/RISULTATI.md`: what the two validation tests actually measured, in full.

## The three hooks
1. **Research → fast spike lane.** A "not verified" fact the plan depends on, where a small experiment could settle it and guessing wrong would cost real rework, gets a time-boxed prototyper spike with a Kill/Proceed call before planning continues.
2. **Plan → Archetype field.** Every plan piece names which archetype's rules run it (inline by default; a separate subagent only for large or isolable pieces).
3. **Lock in → cleanup + cadence.** Every locked-in plan ends with at least a leak sweep (machine paths, secrets, scratch files) on its own diff; a live system gets a maintainer health check on a cadence; a growth change needs a metric written down before it ships.

## How it was validated
Two real, independent tasks, each built twice (the host protocol alone vs. the host protocol with this graft), same model, same data, then an independent reviewer judged the two results without knowing which was which:
1. A journal-parity checker between two environments of a running product. First pass: the package was loaded but never used (no hook wired in — lesson learned, now documented as the first thing to check). Second pass, hooked in: same correct result, more complete process, but noticeably higher cost. The cost-rule fix below followed from this.
2. A schema change behind RLS in a larger codebase (adding a tamper-evident log for an admin action that previously left no trace). With the cost-rule fix applied: equal or lower cost than the host protocol alone, and the blind reviewer preferred the graft's result on design safety and coverage.

Full detail, numbers and the blind reviewer's own words: `docs/RISULTATI.md`.

## Install
```
claude --plugin-dir /path/to/def-infinity
```
Loading the plugin alone does nothing by itself (see the first validation run above) — a plan-first protocol needs to call `skills/def-infinity/SKILL.md` at its research and lock-in steps for the hooks to engage.

## Credits
See NOTICE. MIT License.

Thanks to Flowstate Technologies, whose build protocol this graft was designed to attach to and was validated against (see NOTICE) — none of its text is included here.
