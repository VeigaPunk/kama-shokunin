# FinalPM04 — PM04-accept-unavailable-referenced-object @ pin 92063cf60e217fa7e2098c568578119b16a1b95
**VERDICT: KILLED (bounded sample: 2 current-arm cells per tool).** The registered operator applies uniquely, compiles, and flips both selected graded cells from amended exit 2 (refusal) to exit 1 (ordinary failed finding).
- Falsification: pinned mutator's own API only — `apply_mutation(source, MUTANTS["PM04-accept-unavailable-referenced-object"])`, `compiles()`; its `main()`/default sensitivity path (47-cell pristine check) was NEVER invoked; no re-anchoring/retargeting.
- Pin: `git clone --no-hardlinks --no-local` → `/fast/scratch/hyaku/kama-r24/postfix/FinalPM04/clone`, detached `92063cf…b95` (`git rev-parse HEAD` verified).
- Applicability (observed): alt0 regex matches exactly 1× (alt1 also 1×; both unique); applied alternative **0**; `compiles()`=true. Diff = 1 line at `tools/report-landing-audit.py:784`: `for store in stores:` → `for store in ():` inside `unknown_citation`.
- Detector argv (pinned grid, current arm only, 2 cells/tool): `python3 <clone>/tests/report-audit/promisor-grid.py --arm current --current <auditor> --case PG33-missing-cited-blob-promisor --case PG34-missing-cited-blob-plain --json`, `TMPDIR=/fast/scratch/hyaku/kama-r24/postfix/FinalPM04/tmp/{pristine,mutated}`.

| tool | auditor sha256 | grid exit | PG33-missing-cited-blob-promisor | PG34-missing-cited-blob-plain | twin_equal |
|---|---|---:|---|---|---|
| pristine | `b9be4f42…3b26f` | 0 | exit 2, met=true, problems [] | exit 2, met=true, problems [] | true |
| mutated | `15c79792…6499a` | 1 | exit 1, met=false, `["exit 1 != 2"]` | exit 1, met=false, `["exit 1 != 2"]` | true |

- Mutated rows: expected_exit 2 → exit 1 (taxonomy `actual-verdict`; pristine rows are met 2→2 `diagnostic-only`), kinds `unresolved-full-hash` token `56d7b323865c731da81e0225cf109d66f0480919`; mutated stdout carries a verdict document, pristine stderr names the unavailable object (`could-not-evaluate: round 1: unknown: unavailable required object: 56d7b32…`).
- No harness fault in any of the 4 rows: `internal_error=false`, `timed_out=false`, `traceback=false`, `leaked=false`, `objects_acquired={lane:[],fleet:[]}`; 0 timeouts/tracebacks/leaks in both arms; violated rows pristine=[] vs mutated=[PG33,PG34].
- Bytes preserved: `promisor-grid-expectations.json`=`d86b7bea…14cd1` (pin) before/after; production auditor `b9be4f42…3b26f`, `git status` shows no tracked change; grid sha256 `30483830…3f270`.
- Restoration: pristine auditor never written — sha256 identical before/after (`pristine_bytes_restored=true`); mutation exists only in the private copy `out/FinalPM04/mutant-auditor.py`.
- Residuals: only PG33+PG34 executed; registered `expect_rows` also declare PG46/PG47 — **not exercised**, no global-equivalence claim; frozen arm and 47-cell grid not run; `expect_rows` read as an attribution envelope only. Inference (not observed): the amended exit-2 expectation, not twin inequality, is what kills PM04; PM03/PM04 kill sets are not proven identical.
- Evidence: `.ufo/waves/round-24/postfix/out/FinalPM04/{probe-report.json,grid-pristine.stdout.json,grid-mutated.stdout.json,grid-pristine.stderr.txt,grid-mutated.stderr.txt,mutant-auditor.py}`; scratch `/fast/scratch/hyaku/kama-r24/postfix/FinalPM04/`. No production edit; no tools installed.

Report: .ufo/waves/round-24/postfix/advice/FinalPM04.md
