# FinalCase27 — PG27-cross-repo-found-plain (postfix wave3, pin 92063cfc…)
**VERDICT: PASS — no defect found in scope.** The pinned candidate still accepts a citation only the *second* audited store holds: PG27 exits 0, no findings, no refusal.
**Runs (bounded, own TMPDIR, current arm only).** Private clone `/fast/scratch/hyaku/kama-r24/postfix/FinalCase27/clone` (`--no-hardlinks`), detached at `92063cfc60e217fa7e2098c568578119b16a1b95`; auditor `b9be4f42…`, grid `30483830…`, expectations manifest `d86b7bea…` (unchanged bytes, all match the dispatch spec).
Graded run (2 cells: PG27 + PG26, the row that *declares* the twin): `python3 tests/report-audit/promisor-grid.py --arm current --case PG27-cross-repo-found-plain --case PG26-cross-repo-found-promisor --json --keep` → exit **0**, stderr empty.
Controls: two mutated *copies* of the auditor in my own scratch (pinned file untouched). Raw: `out/FinalCase27/{main,m1,m2}.stdout.json`, `pg27-premise-probe.json`, `mutants/`, `commands.md`.

## Decisive observations
1. PG27 row: exit **0**, defects `[]`, kinds `[]`, reason_class null → a verdict document exists (`summary.status clean`, defects 0, required 1, cutoff 2000); `met_amended=true`, `met_original=true`; `objects_acquired {lane: [], fleet: []}`; traceback/internal_error/timed_out/leaked all false; arm totals graded 2, violations 0, `withdrawn_original_failures []`.
2. Premise (kept fixture `current/001`): both stores plain — no `remote.origin.promisor`, no `extensions.partialclone`, no origin URL. Lane holds only `58866b56…`; fleet holds `42153ed9…`+`f723c76c…`. The cited fleet commit `f723c76c…` is `missing` in the lane (bare *and* `^{commit}`) and a `commit` in the fleet; the lane commit is `missing` in the fleet → each citation resolves in exactly one store, so PG27 exercises both directions of the merge.
3. Twin equality (declared on PG26's row; PG27's own `twin` is null): normalized PG26/PG27 verdict documents byte-identical (sha256 prefix `6c1b0b68e010f504`); harness `twin_equal=true`, `twin_mismatch=[]`.
4. Control m1 (lookup consults only the first store) → PG27 exit **1**, kinds `[landed-unresolved, unresolved-full-hash]` on `f723c76c…`: the cell is load-bearing, so exit 0 is not an artefact of the citation being ignored.
5. Control m2 (first store's absence poisons the citation — uncertainty wins) → PG27 exit **2**, no verdict document, reason names `f723c76c…`: the cell also detects resolution lost to first-store absence/uncertainty.
6. Both controls are attributed failures (no traceback/internal_error/timeout/leak, no objects acquired) — not harness could-not-evaluate.

## Residuals / verification gaps
- Frozen arm not run (out of scope; CNE2 before a pristine run). No full grid, no `--selftest`, no mutant driver, no historical suite, no score promotion or self-admission.
- Content-derived refusal-reason contract not exercised by PG27 (expects exit 0 → no reason produced); m2's refusal wording was rejected by the grader ("reason does not name the unavailable object") — that is the mutant's text, not the candidate's.
- Per-canonical-object reconciliation of *abbreviated* names is not exercised here (PG27 cites full 40-hex tokens); PG38/PG39 territory, outside this seat.
- Original unknown clause remains withdrawn/not-achieved; no expectation or data edited. No tool installs (git 2.56.0, Python 3.14.8 preinstalled).
