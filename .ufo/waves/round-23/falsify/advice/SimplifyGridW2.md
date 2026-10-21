# SimplifyGridW2 — repo-state-grid.py (CloseKama22.SimplifyGridW2-2)

## Verdict

**Holds (advisory).** Scratch simplification at `245a37f69628c2c6bb29bbf17897d8fb5946c857` preserves `population_sha256`, and `--arm both` per-row lines match the unmodified grid byte-for-byte. Net **−2 lines** (714→712) via shared fixture helpers; not integrated by L1.

## Godspeed axes

| Axis | Move |
|------|------|
| Population contract | Unchanged `83a84702251c62c6990c8222ea6c4276e09db05344b3c2c0d862a857e50ea2f1` |
| Duplication | `cited`/`base`, `git_out`, `errata_file`, `NOTES_FAKE`, `_hide_history` |
| Line count | 714→712 (`git diff --shortstat`: 54 insertions, 56 deletions) |
| Behavioral parity | Full grid stdout diff empty vs baseline |

## Simplifications (proposed diff)

Scratch clone: `/tmp/kama-r23w2/SimplifyGridW2-2` (`git rev-parse HEAD` = `245a37f69628c2c6bb29bbf17897d8fb5946c857`).

**Shared helpers** (after `require`):

- `git_out(repo, *args)` — git stdout with fixture `env()`
- `cited(tmp, lane_fmt=, fleet_extra=, nl=)` — pair + work commit + fleet report; `base = cited`
- `errata_file(lane, content)` — registry errata TSV commit
- `NOTES_FAKE` — shared `## Notes` + `FAKE` suffix for C03/F17
- `_hide_history(tmp, shallow)` — unifies F10/F11 shallow vs grafts

**Case builders shortened** (builder `__name__` unchanged): `c_clean`, `c_fake_full`, `c_crlf`, `c_cr_only`, `c_errata_ok`, `f_utf16_cutoff`, `f_log_encoding`, `f_report_bytes`, `f_sha256_lane`, `f_errata_bytes`, `f_errata_revision`, `f_huge_round`, `f_quote_path`, `f_shallow`, `f_grafts`.

Full diff: `/tmp/kama-r23w2/SimplifyGridW2-2` → `git diff tests/report-audit/repo-state-grid.py` (also copied to `.ufo/waves/round-23/falsify/out/SimplifyGridW2-2/repo-state-grid.diff`).

## Evidence

```text
git -C /tmp/kama-r23w2/SimplifyGridW2-2 rev-parse HEAD
245a37f69628c2c6bb29bbf17897d8fb5946c857

python -c '… population() …'
83a84702251c62c6990c8222ea6c4276e09db05344b3c2c0d862a857e50ea2f1

wc -l tests/report-audit/repo-state-grid.py   # after edit
712

python tests/report-audit/repo-state-grid.py --arm both 2>/dev/null | diff - /tmp/grid-baseline-both.txt
# (empty — identical to pre-edit baseline captured in same clone)

python tests/report-audit/repo-state-grid.py --arm both; echo $?
0
```

Baseline and simplified runs both report: frozen `faults=0/26 controls=8/8 violations=26`; current `faults=26/26 controls=8/8 violations=0`.

## Tradeoffs

- `cited()` centralizes the “one work commit + Landed report” pattern; cases that need a different first publish (F04, F06, F13, O01) stay on explicit `pair`/`commit`/`publish`.
- `f_replace_fabricated` / similar were **not** routed through `cited` when that would double-publish (same HEAD, extra noise only).

## Not verified

- `tests/report-audit/isolation-mutants.py` or `report-landing-audit.py` selftest
- `--json` output byte identity (only text grid lines compared)
- Integration commit to lane master

## Tooling installs

None.

## Files written

- `.ufo/waves/round-23/falsify/advice/SimplifyGridW2.md` (this file)
- `.ufo/waves/round-23/falsify/out/SimplifyGridW2-2/repo-state-grid.diff`
- Scratch-only: `/tmp/kama-r23w2/SimplifyGridW2-2/tests/report-audit/repo-state-grid.py`, `/tmp/grid-baseline-both.txt`
