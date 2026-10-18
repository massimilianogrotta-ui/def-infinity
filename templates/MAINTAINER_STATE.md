# Maintainer state: <system>

**Level:** L1
**Paused:** no
**Cadence:** <weekly / daily / on release>
**Source of truth:** <declared by the human: which copy, file or system is right>
**Last run:** YYYY-MM-DD · <PASS / WARN / FAIL> · <link to HEALTHCHECK_YYYY-MM-DD.md>
**Useful reports at this level:** 0 of 5

## Levels
- **L1 — report only.** Reads, compares, writes the health note and this file. Changes nothing else (the gate enforces it).
- **L2 — small fixes.** May edit up to 3 existing files per run, one fix each, verify green; never adds files (a new script is a feature for the Builder). Production writes stay a hard stop.
- **L3 — unattended.** Same limits as L2, runs without a human watching. Only the human sets it.

Moving up: only the human changes **Level**, and only after 5 reports in a row at the current level that the human found useful. Any wrong or harmful report sends the count back to 0. Moving down is always allowed, also by the maintainer itself after a FAIL it caused.

## Open findings
| Since | Area | Status | Waiting on |
|---|---|---|---|

## Human overrides
<date · what the human decided · why>
