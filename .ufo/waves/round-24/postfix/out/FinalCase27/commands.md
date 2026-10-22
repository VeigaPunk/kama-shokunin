# FinalCase27 — command ledger (exact argv, exit codes, digests)

Pin: `92063cfc60e217fa7e2098c568578119b16a1b95` ("round-24: correct local object scope and measurement provenance")
Clone: `git clone --no-hardlinks --no-checkout /home/vgpnk/Projects/shokunin/kama-shokunin /fast/scratch/hyaku/kama-r24/postfix/FinalCase27/clone` then `git checkout --detach 92063cfc…` (clone HEAD == 92063cfc…, worktree clean).
Host: git 2.56.0, Python 3.14.8. No tool installs.

Producer digests at the pin (all match the dispatch spec):
- `tools/report-landing-audit.py` = `b9be4f428cd70842320c698794faffaa95571a60fc530df6a84d7d8cade3b26f`
- `tests/report-audit/promisor-grid.py` = `30483830e0461898bd9b710603e755b08cf58e2a2a215a747098ebbe0383f270`
- `tests/report-audit/promisor-grid-expectations.json` = `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1` (primary manifest pin)

## 1. Graded run (current arm only; 2 cells)

```
cd /fast/scratch/hyaku/kama-r24/postfix/FinalCase27/clone
TMPDIR=/fast/scratch/hyaku/kama-r24/postfix/FinalCase27/tmp \
python3 tests/report-audit/promisor-grid.py --arm current \
  --case PG27-cross-repo-found-plain --case PG26-cross-repo-found-promisor \
  --json --keep --out /fast/scratch/hyaku/kama-r24/postfix/FinalCase27/out/main \
  > out/main.stdout.json 2> out/main.stderr.txt
```
exit **0**; stderr empty. Grid-reported digests: `grid_sha256=30483830…`,
`expectations_sha256=d86b7bea…`, `population_sha256=612b0a74…`, `population_size=47`,
`auditor_sha256.current=b9be4f42…`, `grid_root=/fast/scratch/hyaku/kama-r24/postfix/FinalCase27/tmp/promisor-grid-2y_alxwx`.
Raw: `main.stdout.json` (sha256 `f41d29fe…`), `main.stderr.txt` (empty).

## 2. Premise probe on the KEPT PG27 fixture (observation only)

```
python3 probe-pg27-premise.py \
  /fast/scratch/hyaku/kama-r24/postfix/FinalCase27/tmp/promisor-grid-2y_alxwx/current/001 \
  > pg27-premise-probe.json
```
exit **0**. Every git call carries `--no-lazy-fetch --no-replace-objects`.
Raw: `pg27-premise-probe.json` (sha256 `30f28d08…`), `probe-pg27-premise.py`.

## 3. Discrimination controls (mutated auditor COPIES in this seat's own scratch; the pinned file is untouched)

```
TMPDIR=/fast/scratch/hyaku/kama-r24/postfix/FinalCase27/tmp-m1 \
python3 tests/report-audit/promisor-grid.py --arm current \
  --current /fast/scratch/hyaku/kama-r24/postfix/FinalCase27/out/mutants/m1-ignore-second-store.py \
  --case PG27-cross-repo-found-plain --json --out out/m1
```
exit **1**; `auditor_sha256.current=ccf4e5dacb1e98be9b8b92c46390475d67b93d68180b055c2ac9e2bbccbbdb6c`;
PG27 → exit **1**, kinds `["landed-unresolved","unresolved-full-hash"]`, token
`f723c76c41609df00704d93c29bd44408dcbdd2e`; `violations=1`, `violating_cases=["PG27-cross-repo-found-plain"]`.
Raw: `m1.stdout.json` (sha256 `e29d8a70…`), `m1.stderr.txt` (empty), `mutants/m1-ignore-second-store.py`.

```
TMPDIR=/fast/scratch/hyaku/kama-r24/postfix/FinalCase27/tmp-m2 \
python3 tests/report-audit/promisor-grid.py --arm current \
  --current /fast/scratch/hyaku/kama-r24/postfix/FinalCase27/out/mutants/m2-uncertainty-first.py \
  --case PG27-cross-repo-found-plain --json --out out/m2
```
exit **1**; `auditor_sha256.current=cc572a809b981f15ef0d09bff23b9af8d2d15dccd153c3bd97dabe2528cea379`;
PG27 → exit **2** (no verdict document), stderr tail
`could-not-evaluate: round 1: unknown: unavailable required object: f723c76c41609df00704d93c29bd44408dcbdd2e is present but its content cannot be served`;
`violations=1`. Raw: `m2.stdout.json` (sha256 `c005da3b…`), `m2.stderr.txt` (empty), `mutants/m2-uncertainty-first.py`.

Both controls: `objects_acquired {lane: [], fleet: []}`, `traceback=false`,
`internal_error=false`, `timed_out=false`, `leaked=false` — attributed failures, not
could-not-evaluate of the harness.

Not run (out of scope): frozen arm, `--arm both`, full 47-cell grid, `--selftest`,
the mutant driver, historical suites, any production write outside this seat's
advice/out paths.
