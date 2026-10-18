---
name: def-infinity
description: Use when running a plan-first build protocol (align, research, plan, lock in, run) and you need to decide WHICH kind of work a step is. Adds the five archetypes (Prototyper, Builder, Sweeper, Grower, Maintainer) with four hooks: the product's stage at alignment, a fast spike lane for unverified research facts, an Archetype field on every plan piece checked against the stage, and a cleanup piece plus a stepped health cadence at the end. Mechanical gates keep each archetype inside its limits.
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
Inline does not mean from memory: before running an archetype inline, read its file (`${CLAUDE_PLUGIN_ROOT}/agents/<archetype>.md`, in this plugin's folder, not the project) and follow every numbered rule in order (for the sweeper, the search for broken things comes before any removal).

## Hook 0 · Align: the product's stage
Ask the human which stage the product is in and write it in the alignment note as `Product stage: new | growing | mature`. Never guess it: the human declares it. The stage sets the mix of work the plan should contain (after Boris Cherny):
| Stage | Main archetypes | Some |
|---|---|---|
| new (no product-market fit yet) | prototyper + builder + sweeper | — |
| growing (has found fit) | builder + sweeper + grower | maintainer |
| mature (strong fit) | sweeper + grower + maintainer | builder |

## Hook 1 · Research: the fast spike lane
After research, look at every item marked "not verified". Trigger: the plan depends on it AND a small experiment could settle it AND guessing wrong would cost a rework. Only then run the **prototyper** on it BEFORE planning (one spike per item, time-boxed). Proceed turns the item into a verified fact with the spike as its source; Kill records why and the plan routes around it. Items that cannot be settled by an experiment stay "not verified" as usual.

## Hook 2 · Plan: an Archetype field on every piece
Next to the piece's Autonomy field, add `Archetype: <prototyper | builder | sweeper | grower | maintainer>` with a one-line reason. It decides whose rules run the piece (inline, or that subagent when the cost rule allows). A piece that mixes two kinds of work usually wants splitting only if the host protocol's own split rules allow it; otherwise name the main archetype first.
Then run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/stage_check.py <plan file>` and copy its WARN lines (if any) into the plan's open risks with one line on why the mix is right anyway, or change the pieces. It is a warning, not a block: the human decides.

## Hook 3 · Lock in: cleanup and cadence
- Every locked-in plan ends with a **sweeper** pass: always the leak sweep (machine paths, secrets, scratch folders, debug leftovers) on the plan's diff; a full removal list only if the plan added more than about 300 lines or touched existing modules. A small plan does the pass inline as the last step, not as a separate piece. Visible deletions stay a human gate. When the whole task is a cleanup, the sweeper's broken-things search (scripts and configs pointing at missing files or folders) runs first, and style-only edits are listed, not made.
- Trigger for a **maintainer** check: the plan touches a live system where drift or decay is a real risk (usually a growing or mature product). Then add a maintainer check with a cadence (for example weekly) that compares the system with its declared source of truth and writes a health note. It starts at **L1, report only**, with a state file (`MAINTAINER_STATE.md`: level, paused switch, last run); only the human raises it to L2 (small fixes) after 5 useful reports in a row, and L3 (unattended) is never automatic.
- A **grower** piece enters a plan only with data and a metric written down before the change.

## Mechanical gates (what the prose cannot guarantee)
Rules written in an agent file are followed most of the time, not always. Three scripts make the important ones mechanical:
- `hooks/hooks.json` + `scripts/guard_hook.py`: before a write, stops an archetype that writes outside its limits (prototyper only `.spike/` and spike notes; grower only experiment notes; maintainer at L1 only its note and state, never new files; sweeper never adds files; nobody writes env or secret files), and stops push/merge/publish commands from any archetype. It acts only on the five archetypes (hook field `agent_type`); other agents pass through.
- `scripts/gate.py --archetype <a> [--base <ref>]`: the same rules on the finished diff, also catching files changed through shell commands. Exit 2 = undo and write a blocker. Run it before marking a piece done.
- `scripts/attempts.py`: a per-piece ledger of failed tries; at the third failure since the last success, the piece stops and goes to the human.
When an archetype runs INLINE in the main session there is no `agent_type`, so the hook cannot tell who is working: run `gate.py` yourself at the end of the piece.

## Choosing quickly
- "Does this even work?" → prototyper
- "Build this approved thing" → builder
- "Too much stuff / slow / leftovers" → sweeper
- "It runs, make it better, we have numbers" → grower
- "Is it still healthy / do the copies agree?" → maintainer
