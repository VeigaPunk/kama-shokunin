VERDICT: confirm - behaviour-preserving for gated CLI outputs; patch drops 9 lines and one duplicate git wrapper

## Axes (godspeed)
- **Operability**: single `git()` helper (optional `env`) replaces selftest-only `_sh()` — one subprocess convention.
- **YAGNI / dead weight**: removed never-read `subject` on lane-commit rows, dead `cited_elsewhere` + `cited_anywhere` scan, tightened `apply_errata`.
- **Calibration**: unchanged defect detection on population rounds 10–20 (gated outputs byte-identical).

## Deletions (scratch @ `a29bb84`, not lane)
| Change | Evidence |
|--------|----------|
| Drop `_sh()`; extend `git(..., env=None)` | selftest still 15/15 |
| Remove `cited_elsewhere` from `landed-omitted` defects | grep: no fleet/lane consumers of `cited_elsewhere` (text grep; no LSP on this path) |
| Omit `subject` from internal commit dicts | never surfaced in `render()` or summary JSON |
| `apply_errata`: one pass for `corrected_by`; list comp for `invalid` | same exit/summary counts on default run |

## Preserved contract
- Four defect kinds, errata rules, exit 0/1/2, `--selftest` cases, text render shape unchanged.
- **Tradeoff**: `--json` defects no longer include `cited_elsewhere` (was write-only metadata). Text population and selftest unchanged.

## Verification (executed)
Pin: `a29bb84abbb8b4d328f5970a89e448330a3a42ac`. Lane repo for errata: scratch clone; fleet: `/home/vgpnk/Projects/shokunin`.

```text
python3 tools/report-landing-audit.py --lane-repo <scratch/lane> --fleet-repo <fleet> --no-errata  → exit 1
python3 tools/report-landing-audit.py --lane-repo <scratch/lane> --fleet-repo <fleet>            → exit 0
python3 tools/report-landing-audit.py --selftest                                                 → exit 0

cmp baseline/no-errata.txt after/no-errata.txt  → identical (exit 0)
cmp baseline/default.txt   after/default.txt    → identical (exit 0)
cmp baseline/selftest.txt  after/selftest.txt   → identical (exit 0)
```

Before: 404 lines; after: 395 lines (`git diff --stat`: 18 insertions, 27 deletions).

## Deliverable
Patch: `.ufo/waves/round-21/build/out/SimplifyAudit/report-landing-audit.simplify.patch`

## Tooling
No installs or upgrades this seat.

Report: `.ufo/waves/round-21/build/advice/SimplifyAudit.md`
