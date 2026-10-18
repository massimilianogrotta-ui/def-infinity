---
name: def-infinity
description: Use when running a plan-first build protocol (align, research, plan, lock in, run) and you need to decide WHICH kind of work a step is. Adds the five archetypes (Prototyper, Builder, Sweeper, Grower, Maintainer) to the protocol with three hooks: an Archetype field on every plan piece, a fast spike lane for unverified research facts, and a cleanup piece plus a health cadence at the end.
---

# DEF ∞ · five archetypes on a proof-first protocol

The host protocol stays the rail: align with the human, research with sources, plan in pieces with "done when" lines, lock in, run with proofs re-run. This graft adds only the WHO and the WHEN. It never relaxes a host rule or a human gate.

## The five archetypes (subagents in this plugin)
| Archetype | Kind of work | Output |
|---|---|---|
| prototyper | answer one open question fast, throwaway | `spike_<slug>.md` with Kill / Proceed |
| builder | implement an approved piece, tested | code + verify output in the log |
| sweeper | remove, simplify, clean leftovers | removal list with evidence |
| grower | iterate on a live thing with data | experiment note, pre-registered |
| maintainer | recurring health check of a live system | health note PASS/WARN/FAIL |

## Cost rule: hooks fire only when they pay
Every hook below has a trigger. If the trigger is not met, skip the hook and write one line saying why (for example "no spike: no not-verified fact blocks the plan"). Do not run a hook for ritual.
Run the archetype INLINE (you follow its rules yourself) by default. Spawn the archetype subagent only when the piece is large, needs an isolated context, or can run in parallel with other work.

## Hook 1 · Research: the fast spike lane
After research, look at every item marked "not verified". Trigger: the plan depends on it AND a small experiment could settle it AND guessing wrong would cost a rework. Only then run the **prototyper** on it BEFORE planning (one spike per item, time-boxed). Proceed turns the item into a verified fact with the spike as its source; Kill records why and the plan routes around it. Items that cannot be settled by an experiment stay "not verified" as usual.

## Hook 2 · Plan: an Archetype field on every piece
Next to the piece's Autonomy field, add `Archetype: <prototyper | builder | sweeper | grower | maintainer>` with a one-line reason. It decides which subagent runs the piece. A piece that mixes two kinds of work usually wants splitting only if the host protocol's own split rules allow it; otherwise name the main archetype.

## Hook 3 · Lock in: cleanup and cadence
- Every locked-in plan ends with a **sweeper** pass: always the leak sweep (machine paths, secrets, scratch folders, debug leftovers) on the plan's diff; a full removal list only if the plan added more than about 300 lines or touched existing modules. A small plan does the pass inline as the last step, not as a separate piece. Visible deletions stay a human gate.
- Trigger for a **maintainer** check: the plan touches a live system where drift or decay is a real risk. Then add with a cadence (for example weekly) that compares the system with its declared source of truth and writes a health note.
- A **grower** piece enters a plan only with data and a metric written down before the change.

## Choosing quickly
- "Does this even work?" → prototyper
- "Build this approved thing" → builder
- "Too much stuff / slow / leftovers" → sweeper
- "It runs, make it better, we have numbers" → grower
- "Is it still healthy / do the copies agree?" → maintainer
