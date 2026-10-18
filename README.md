# DEF ∞

Five work archetypes as Claude Code subagents, grafted onto a plan-first, proof-first build protocol.

Status: experimental, under A/B test. Results will be added here.

## Why
A good build protocol (align, research with sources, plan in pieces, lock in, run with proofs) mostly covers one kind of work: building an approved thing well. Products need four more kinds of work, as Boris Cherny pointed out: exploring many ideas and throwing most away, removing and simplifying, growing what runs using data, and keeping what runs healthy. DEF ∞ adds those four next to the builder without changing the protocol's rules.

## What is inside
- `agents/`: prototyper, builder, sweeper, grower, maintainer
- `skills/def-infinity/`: the three hooks into the protocol
- `templates/`: spike findings, unship list, experiment, health check
- `scripts/check.py`: package self-check

## The three hooks
1. **Research → fast spike lane**: a "not verified" fact the plan depends on gets a time-boxed prototyper spike with Kill/Proceed before planning.
2. **Plan → Archetype field**: every plan piece names which archetype runs it.
3. **Lock in → cleanup + cadence**: every plan ends with a sweeper piece; live systems get a maintainer health check on a cadence.

## Install
```
claude --plugin-dir /path/to/def-infinity
```

## Credits
See NOTICE. MIT License.
