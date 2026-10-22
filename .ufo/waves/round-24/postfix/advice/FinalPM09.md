# FinalPM09 — PM09-peel-bare-full-hash-lookup, bounded falsification (2 cells/tool)

VERDICT: **mutant killed on a declared attribution row (PG39) in the bounded 2-cell sample; PG44 (the assigned primary cell) does not discriminate PM09.**
Kill class: violated graded row, `met=false` (amended view). Exit taxonomy: **same-verdict-exit** (expected 1 → actual 1); no refusal-2, no actual-verdict, no verdict-change credit. No twin row was exercised (`twin_equal=null` in both runs). No timeout, leak, traceback or internal_error in either run.

Setup (all local, no network): scratch clone `/fast/scratch/hyaku/kama-r24/postfix/FinalPM09/clone`, `git clone --no-hardlinks` from the local lane, detached at **92063cfc60e217fa7e2098c568578119b16a1b95**, `git status --porcelain` empty after the run. Pinned bytes verified: auditor `b9be4f42…3b26f`, grid `30483830…f270`, mutator `971c3ecb…f200`, 47-cell manifest `d86b7bea…14cd1` (unchanged, `EXPECTED_CASES=47` untouched).

Operator application (mutator APIs `apply_mutation`/`compiles`/`run_grid`; its `main()` sensitivity path with the 47-cell pristine was **not** invoked): the registered alternative `[0] replace "full = lookup(stores, full_tokens)"` matches **exactly once** in the pinned auditor (line 538) → applicable, unique; mutant compiles. Mutant bytes sha256 `f002488d…3caa` (single-line change, `lookup(stores, full_tokens, "^{commit}")`); pristine copy sha256 `b9be4f42…3b26f`.

Executions (grid `--arm current --current <copy> --json --case PG44-missing-unused-tree-promisor --case PG39-wrong-type-citation-promisor`, TMPDIR = own `…/FinalPM09/tmp/{pristine,mutant}`):
- pristine: grid exit **0**, no violated graded row.
- mutant: grid exit **1**, one violated graded row: `PG39-wrong-type-citation-promisor` (kind policy) `met_amended=false`.

Decisive observation (PG39, graded amended view): pristine `kinds=['landed-unresolved']`, `problems=[]`; mutant `kinds=['landed-unresolved','unresolved-full-hash']` with `defects [('landed-unresolved','56d7b323…0919'), ('unresolved-full-hash','56d7b323…0919')] != [('landed-unresolved','56d7b323…0919')]`. The peel turns the locally present blob into an extra `unresolved-full-hash` defect — a changed defect set (not a names/reason-only difference); exit stays 1. `objects_acquired` empty for lane and fleet in every row of both runs (no fixture hydration, no lazy fetch).

PG44-missing-unused-tree-promisor: `met=true`, exit 0 = expected 0, in **both** runs → PM09 does not change the missing-unused-tree verdict; that cell does not discriminate this operator in this sample.

Restoration: the clone's auditor is byte-identical after the run (`b9be4f42…3b26f`), `git status` clean, manifest bytes `d86b7bea…14cd1`; the mutation was applied only to a private copy under my own scratch. No production, sibling or other-seat file was written.

Residuals (bounded sample, not global equivalence): PM09's other declared row **PG38** and PG39's twin **PG38**, and PG44's twin **PG45**, were not executed (2-cell budget), so no twin equality was measured; PG44 lies outside PM09's declared `expect_rows` envelope (PG38/PG39) and its survival is a coverage observation only. The original unknown clause stays WITHDRAWN/NOT-ACHIEVED; amended cells only; no score promotion or self-admission is claimed.

Evidence: `.ufo/waves/round-24/postfix/out/FinalPM09/{result.json,grid-pristine.json,grid-mutant.json,mutant-PM09-auditor.py,probe.py,hashes.txt}`.
