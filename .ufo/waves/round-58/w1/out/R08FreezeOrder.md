# R08FreezeOrder — round-58 freeze-order and frozen-byte integrity (lane kama)

Observed at lane HEAD `e4f207f544315612a6ea55b5b7a1cc2d2d4b4a79` (2026-10-27 16:50:20 -0300).
Method: read-only git (`log`/`show`/`rev-parse`/`ls-tree`/`hash-object`/`merge-base --is-ancestor`)
against committed bytes; no counter or control was executed (seats find and report; outcome judging
is owned by the counter seats). Raw receipt (103 lines, all commands + ids + exit codes):
`.ufo/waves/round-58/w1/out/R08FreezeOrder/receipt-freeze-order.txt`.

## Finding 1 — commit order base -> freeze -> controls -> build -> fix: PASS
Linear single-parent chain, each commit's parent is the previous; all five consecutive-ancestry
checks exit 0 (`merge-base --is-ancestor`):

| role        | rev      | subject                                                            | time (UTC-3) |
|-------------|----------|--------------------------------------------------------------------|--------------|
| base        | 2f53614e | round-57 verifier spot-check (integrator, hyaku)                    | 16:35:45     |
| freeze      | dcd69473 | round-58: freeze C1/C2 counters, variant set and predicates         | 16:44:03     |
| controls    | cb1ef102 | base and do-nothing control receipts (frozen counters)              | 16:45:14     |
| build       | bfaea953 | execution-bound battery checker (C1), calibration row re-anchored   | 16:47:26     |
| fix         | e4891d8a | calibration row cites MANIFEST without unresolvable path token      | 16:48:15     |
| (post-fix)  | e4f207f5 | validated 72-seat v2 wave spec and dispatch = HEAD                  | 16:50:20     |

Naming note (observation, not defect): the frozen claim's "Build tip e4891d8a" is the measurement
tip that includes the fix; the build-implementation commit is bfaea953. The claimed order
base->freeze->controls->build->fix holds under either reading.

## Finding 2 — no counter, variant or predicate byte changed after freeze: PASS
Git blob ids are content-addressed, so equal id == equal bytes. Identical at dcd69473, cb1ef102,
bfaea953, e4891d8a, e4f207f5 (16-hex prefixes shown; full ids in receipt):

- freeze.txt `b54a2961e5f9202d`, make-variants.py `bfdf4ee0d5d9368f`, c1-counter `ed2dfa49b9cb016d`,
  c2-counter `99798397bd7de047` — present from the freeze commit, byte-identical through HEAD.
- controls/checkers always-accept `147994fa…`, always-reject `cf7f15d8…`, hash-only `eb5f611a…` —
  introduced at controls cb1ef102 (absent at freeze by construction), unchanged since.
- tools/round58-battery-exec-check.py `02616f0ff3d6566c` — introduced at build bfaea953, unchanged
  through HEAD (this is the only post-freeze addition to the predicate implementation; named here).
- tests/round58-battery-variants/ subtree tree-id `8c3c1fcd07fe5b38` identical at all five revs;
  all 15 worktree files (genuine.py, B1–B3, N01–N11) MATCH their freeze-rev blob ids.

## Finding 3 — post-freeze change inventory (all additions or SCORECARD row edits)
`git show --name-status` per commit; no M/D line on any frozen surface after dcd69473:
- cb1ef102: A-only — 16 control receipts (.exit/.out) + 3 do-nothing checkers.
- bfaea953: A tools/round58-battery-exec-check.py; M SCORECARD.md (C2 row re-anchor, expected).
- e4891d8a (the fix): M SCORECARD.md only — no frozen surface touched.
- e4f207f5: A build_spec.py, measured/c2-build.out, w1-dispatch.json, w1-spec.json.
Working tree matches HEAD on every tracked frozen file (blob-id equality via `hash-object`);
`git status --porcelain` on round-58 paths shows only untracked w1 outputs (w1/, w1.ready,
w1.ready.partial). Commit named by this report for each post-freeze change: cb1ef102, bfaea953,
e4891d8a, e4f207f5. No uncommitted or unattributed change to frozen bytes exists.

## Cross-repo note on the C2 manifest anchor
freeze.txt pins `fleet-manifest-rev=941acf70583a2b3a…`. That object does not exist in the lane repo
(`git cat-file -t` in lane: "bad object" — expected: MANIFEST.json lives at fleet root) and resolves
in /home/vgpnk/Projects/shokunin as commit "round-59: mori dispatch evidence (hyaku inline attempt 1)"
(2026-10-27 16:38:02) with MANIFEST.json present at that rev. Timestamp sits between base
(16:35:45) and freeze (16:44:03), consistent with "frozen before any seat result".

## Derived-source stability (feeds make-variants.py and the counters)
tools/round56-env-leg-battery.py `1f4ebff0a62c…`, tools/round56-prereg-check.py `642a575ed159…`,
tools/round42-selfdesc-reconcile.py `2cf92cac822a…` — blob-identical from base through HEAD
(no regeneration drift possible for the committed variant set).

## Defects
None. Every check the seat names passed with the committed bytes.

## Residual risk and verification gaps
- I verified byte/order integrity, not outcomes: C1/C2 counters and controls were not executed here
  (judging owned by counter seats); a byte-frozen predicate can still fail on behavior.
- `w1.ready`/`w1.ready.partial` are untracked harness state I did not interpret.
- Freeze-claim semantics (roster literal wording, S517 sourcing) were taken as given; I verified the
  15-file variant set and claim text bytes, not the pedagogy of the S517 citation.
