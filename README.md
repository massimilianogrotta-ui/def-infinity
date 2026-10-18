# DEF ∞

Five work archetypes as Claude Code subagents, grafted onto a plan-first, proof-first build protocol.

Status: tested on 3 real tasks (A/B with a blind review each): two narrow wins (20-19, 27-26) and one loss (21-26), plus a trap test for each agent. These are signals, not statistical proof. See `docs/RISULTATI.md`.

## Why
A good build protocol (align, research with sources, plan in pieces, lock in, run with proofs) mostly covers one kind of work: building an approved thing well. Products need four more kinds of work, as Boris Cherny pointed out: exploring many ideas and throwing most away, removing and simplifying, growing what runs using data, and keeping what runs healthy. DEF ∞ adds those four next to the builder without changing the protocol's rules.

## What is inside
- `agents/`: prototyper, builder, sweeper, grower, maintainer — five Claude Code subagents, each with its own rules, limits and output format.
- `skills/def-infinity/`: the three hooks that connect the five archetypes to a plan-first protocol, plus a cost rule so they only fire when they earn their keep.
- `templates/`: spike findings, unship list, experiment, health check — the artifact shape each archetype promises.
- `scripts/check.py`: package self-check (frontmatter valid, no machine-specific paths, no copied host-protocol text).
- `docs/RISULTATI.md`: what the three A/B tests and the per-agent trap tests actually measured, in full (in Italian).

## The three hooks
1. **Research → fast spike lane.** A "not verified" fact the plan depends on, where a small experiment could settle it and guessing wrong would cost real rework, gets a time-boxed prototyper spike with a Kill/Proceed call before planning continues.
2. **Plan → Archetype field.** Every plan piece names which archetype's rules run it (inline by default; a separate subagent only for large or isolable pieces).
3. **Lock in → cleanup + cadence.** Every locked-in plan ends with at least a leak sweep (machine paths, secrets, scratch files) on its own diff; a live system gets a maintainer health check on a cadence; a growth change needs a metric written down before it ships.

## How it was tested
Three real, independent tasks, each built twice (the host protocol alone vs. the host protocol with this graft), same model, same data, then an independent reviewer judged the two results without knowing which was which. One run per arm, so read the numbers as signals:
1. A journal-parity checker between two environments of a running product. First pass: the package was loaded but never used (no hook wired in — lesson learned, now documented as the first thing to check). Second pass, hooked in: same correct result, more complete process, blind review 20-19 for the graft, but +67% cost. The cost-rule fix followed from this.
2. A schema change behind RLS in a larger codebase (adding a tamper-evident log for an admin action that previously left no trace). With the cost-rule fix applied: 5% lower cost than the host protocol alone, blind review 27-26 for the graft (design safety and coverage).
3. A behavior-preserving cleanup of a TypeScript repo. **Lost: 21-26, at +23% cost.** The graft ran the sweeper inline from memory, spent its effort on style-only edits (dropping `export` from 17 symbols) and reported "no dead code", while the host protocol alone found a broken npm script pointing at a file that never existed and a tsconfig including an empty folder. v0.3 fixes this: the sweeper looks for broken things before removing anything, lists style-only edits instead of making them, and the skill requires reading the agent file when running an archetype inline.

Per-agent trap tests (each agent alone on a small fake repo, with one normal request and one trap where it must stop): v0.2 failed or partly failed four of the five agents across the two environments it was run in (editing project files it should only read, rewriting a file without data, writing a sync script instead of reporting, not finding its templates). v0.3 passed all five in the cloud run, 2 runs each, after two rounds of fixes. These traps are not yet measured on a real A/B task.

Full detail, numbers, the before/after table and the blind reviewers' findings: `docs/RISULTATI.md`.

## Install
```
claude --plugin-dir /path/to/def-infinity
```
Loading the plugin alone does nothing by itself (see the first test run above) — a plan-first protocol needs to call `skills/def-infinity/SKILL.md` at its research and lock-in steps for the hooks to engage.

## Credits
See NOTICE. MIT License.

Thanks to Flowstate Technologies, whose build protocol this graft was designed to attach to and was tested against (see NOTICE) — none of its text is included here.
