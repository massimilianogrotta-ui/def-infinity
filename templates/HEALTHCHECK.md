# Health check: <system>

**Date:** YYYY-MM-DD
**Cadence:** <weekly / release / on-alert>

| Area | Status | Detail |
|---|---|---|
| Dependencies | PASS / WARN / FAIL | <versions behind, audit hits> |
| Security | PASS / WARN / FAIL | <secrets scan, audit findings> |
| Performance | PASS / WARN / FAIL | <against which budget> |
| Integrations | PASS / WARN / FAIL | <external API health> |
| Tests / CI | PASS / WARN / FAIL | <green? flakes?> |

## Recommended dispatch

<Per FAIL/WARN: which archetype picks it up (Maintainer fix, Sweeper simplification, Builder slice behind a spec) or what needs human judgment. Security FAIL is same-day.>
