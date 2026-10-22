# FinalCase43 — PG44-missing-unused-tree-promisor (reviewer seat)

VERDICT: PASS — no defect found in scope. Current-arm PG44 and its graded twin PG45 both meet the
amended (graded) expectation at the pinned commit; the lane's missing UNUSED subtree did **not**
become an audit-completeness precondition, and resolved / conclusively wrong-type citations keep
their registered result. Recommendation only: no admission, no score change, Gitfloor H2 untouched.

PIN (own clone `/fast/scratch/hyaku/kama-r24/postfix/FinalCase43/clone`, detached `92063cfc60e217fa7e2098c568578119b16a1b95`):
- `tools/report-landing-audit.py` sha256 `b9be4f428cd70842320c698794faffaa95571a60fc530df6a84d7d8cade3b26f` = registered producer id
- `tests/report-audit/promisor-grid.py` sha256 `30483830e0461898bd9b710603e755b08cf58e2a2a215a747098ebbe0383f270` = registered id; expectations manifest `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1` = primary manifest id
- Grid ran the pinned clone's auditor (grid-reported `auditor_sha256.current` = `b9be4f42…`); no proposal/mutable producer used.

ARGV / EXITS (TMPDIR under this seat's own scratch; grid honoured it, no baked-in root):
- A `python3 tests/report-audit/promisor-grid.py --arm current --case PG44-missing-unused-tree-promisor --case PG45-missing-unused-tree-plain --json --out <scratch>/out/grid` → exit 0
- B same argv without `--out`, second TMPDIR (determinism control) → exit 0; both JSONs byte-identical (sha256 `71cafde5…`)
- C `python3 <scratch>/probe.py` (pinned builder + pinned auditor on an own fixture) → exit 0
- Grid current arm: `amended_view_met 2/2`, `violations 0`, `twin_mismatch []`, tracebacks 0, timeouts 0, harness_leaks 0.

DECISIVE OBSERVATIONS (raw: `out/FinalCase43/grid-run.json`, `grid-run2.json`, `probe.json`):
1. PG44 row: exit 0, `met_amended` true, `problems []`, `defects []`, `kinds []`, reason_class null, stderr empty, traceback/internal_error/timed_out/leaked false, `objects_acquired {lane:[],fleet:[]}` → equals the registered live expectation `{"defects":[],"exit":0,"kinds":[],"reason_class":null}`.
2. Twin: PG45 row exit 0 with the same clean document; `twin_equal` true both directions. Both verdict documents exist (no refusal), so twin equality is a real document comparison, not two missing documents.
3. Premise is real, not vacuous: lane tip tree `893b5318…` lists `040000 tree 33fd12ec… extra`; `git --no-lazy-fetch cat-file -e 33fd12ec…^{tree}` → rc≠0 ("Not a valid object name"); `lane_promisor true`, `fleet_missing []`, `fake_present false`.
4. Two-root diagnosis is bounded, not a precondition: the auditor's own sets are `lane_missing {33fd12ec…}`, `lane_opaque {33fd12ec…}`, `fleet_missing {}`, `fleet_opaque {}` — it names exactly the one unrelated hole, nothing else.
5. Same fixture through the pinned auditor: exit 0, `summary.status clean`, defects [], no stderr, `objects_acquired` empty → the unrelated unused hole did not refuse the audit (no lazy fetch, no hydration).
6. Refusal gate (function-level, pinned module): resolved citation → no refusal; peeled wrong-type blob → no refusal (keeps the registered wrong-type finding even with the opaque hole present, per supplement-2 "not_unresolved"); absent fabricated token → refusal naming the missing tree `33fd12ec…` (sanctioned unresolved-citation path).
7. Determinism: two runs, different TMPDIRs → identical `population_sha256 612b0a74…`, identical exits/documents, identical empty acquisitions.

RESIDUAL RISK / VERIFICATION GAPS (flagged, not exercised here):
- `opaque_hole()` is not token-specific: with a missing tree under the audited root, ANY unresolved citation refuses, even one that cannot be related to that tree. Content-derived (names the hole) but coarse; sanctioned by `oracle-supplement-2.json`. PG44 does not exercise it.
- Blob-only holes never enter the opaque set (root walk uses `--filter=blob:none`); only tree/commit holes can conceal names. PG44 drops a tree, so the blob path is untested by me.
- The store-wide missing walk roots at every present object: cost scales with the store; a huge store could hit `GIT_TIMEOUT=20s` (a timeout is an EvalError → could-not-evaluate, not a verdict).
- I did not measure the frozen (r23) arm and no other cell (lane bounded me to these two); the frozen column (PG44 exit 2, metadata) is inherited from the snapshot, not reproduced.
- `original_problems []` for both rows, but the original unknown-citation⇒exit2 clause stays WITHDRAWN/NOT-ACHIEVED; amended rows do not pass it retroactively.
