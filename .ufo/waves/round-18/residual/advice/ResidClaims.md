VERDICT: partial — both counting commands reproduce their claimed counts, but C1's measured bytes are mislabeled as 101f3991 and have drifted since the run, the recovery run overwrote S055's cited evidence in place, and C1's internal-fault containment still has a finalizer escape that I triggered.

Seat `KamaR18Recovery.ResidClaims`: lane-advice criticism only, **not** the outside non-author admit/reject spot-check, which is still owed.
Bytes reviewed: copy A = HEAD 101f3991 + uncommitted gate `2f83a629…`, measure `8f4dc2dc…`, run.py `4f95c0e8…`; copy B (01:49 −03) = gate `1dfcf23e…`, measure `0efcc724…`, lesson `7323e621…`, C2 files unchanged.
All work ran in /tmp and the copies are deleted. No installs (pacman paused); no lane edits except this file.

## Evidence (executed)
- E1 `runs/commands.json`: 32/32 `as_expected`, `measured_commit` 101f3991; only keys {commands, measured_commit, python}, so no tree/dirty digest. `c1-measure`/`c2-survivors` stdout sha256 `831cc75a…`/`8cc59a65…` match the ledger; each `.json` equals its `.stdout` (cmp).
- E2 C1 recount from the 23 `c1-measure.json` `.controls` rows: before accepted_bad k18–k22 = 5, good_rejected k17 = 1, misclassified k16 = 1; after all `ok`. Equals `.counts` (5→0, 1→0, 1→0, uncontrolled 0→0, flip arms 16→17), exit 0, empty faults/reasons/warnings.
  Official argv re-run in /tmp: exit 0, identical counts and rows. Same counts on a 101f3991 clone (gate `e69f91b3…`, measure `a9577ed8…`) and on copy B (counter selftest 45/45, gate 72 mutations).
- E3 C2 recount from `c2-survivors.json` `results.*.items`: H1–H3/H5–H7, FC-target/f6cache/f0gate, AO-opened/blank survived→killed (11); refused-count miscount→correct; nested-json/bigint/escaped-sleep accepted→handled. 15 → killed 11 / correct 1 / handled 3, inconclusive 0/0, all witnesses match, exit 0.
  All 21 in-lane input digests equal both the working tree and the 101f3991 blobs; fleet policy file `70418a0f…` matches.
- E4 `runs/pre-repair/c2-survivors.json` (101f399 blob `bd217de0…`, counter `2af03fed…`) vs final (counter `87cad1ca…`): only FC-target/FC-f6cache change, inconclusive→killed. Raw arms identical: "selftest killed (targeted…); main inconclusive (fault-controls exit 2 (own fault))".
- E5 Recorded `live-gate-1` argv on 101f3991's gate: exit 2, `unrecognized arguments: --expect-server-impl-sha256`. Ledger records exit 0 VALID.
- E6 `live/receipt-1.json` replaced (-2/-3 likewise): 101f399 `e616f67e…`, port 33769, 2026-10-20T22:38:48.776Z, tool `dc036d7d…` → working tree `fc289e2f…`, port 46769, 2026-10-21T04:07:22.480Z, tool `ec7a7567…`. Both sets 11/11 pass; old receipt-1 also five-pin VALID on gate `2f83a629…`.
- E7 Measured tool `ec7a7567…`, no listener: BaseException raised at `tuple(old_handlers)` (`tools/kama-llamacpp-live.py:1420`) → `ESCAPED MemoryError`, no receipt written. Uninjected control: rc 2, setup-error receipt written.
- E8 Genuine-run consistent impl swap (receipt impl and tree member = X): run.py-style pin `sha(installed impl)` = X → VALID exit 0; constant pin `e404b91a…` → INVALID exit 1. Forged A/B → INVALID; swap C (`ggml-rpc-server` member) → VALID.

## Claim verdicts
- **C1 8→8 — partial.** Counts real and stable (E2); delta 0 and "hardened, not newly acquired" are not inflated. Three defects:
  (a) measured bytes ≠ labeled commit (E5) and gate/measure changed again after the run; the lesson's CounterC1 row now cites 45/45 vs retained `runs/c1-counter-selftest.stdout` 43/43 (gate mutations 69 retained vs 72 now).
  (b) E7 contradicts "contains internal BaseException faults" (lesson :17; lifecycle :255-256); ToolFaultPaths P2 is in neither the Fixed table nor the deferred list.
  (c) The ConnectTsukuroi "Fixed" row closes forged receipts only: run.py:48 computes the fifth pin from the installed file, so a pre-run swap still gates VALID (E8).
- **C2 7→7 — verified.** The named command on bytes identical to 101f3991 gives the claimed 15 → 11/1/3 (E3). Disclosure gaps: 2 of 11 kills are targeted-selftest-arm only after the `combine_arms` change (E4; LOG.md:1094-1096). Lesson :174-177 still prints attempt-1's "one FC self kill and two FC inconclusives"; SCORECARD:767 still only promises the append. SurvivorUniverse's exclusion of MutFaultControlsSelf (b) is defensible (round 17 recorded it killed by frozen comparison) but undispositioned.

## Findings → smallest safe correction
- **F1 False provenance / KQ22** (calibration, freshness): the recovery run overwrote S055's receipts, attempt-1 `commands.json` and `c1-measure.*` in place (E6), contradicting lesson :168 ("never overwritten") and :265-266 ("Reused … live receipts").
  SOURCES.md:67 (port 33769, tool `dc036d7d…`, measured c6dc46f) and lifecycle :263-269 now describe bytes no longer at those paths.
  Fix: restore 101f399 bytes at the cited paths; write recovery outputs to new paths (e.g. `runs/recovery-2/`, `live/recovery-2/`) recorded per KQ22 (QUALITY.md:123).
- **F2 Measured-commit label** (calibration, operability): run.py:7 stores `git rev-parse master` with no dirty flag and no run.py digest. The planned evidence commit does not fix this: `commands.json` would still name 101f3991, and as of 01:49 the committed gate/measure ≠ measured `2f83a629…`/`8f4dc2dc…`.
  Fix: freeze code, commit X, re-run run.py on clean X, then evidence commit X+1 with measured_commit X. Make run.py refuse a dirty tree, or record `git status --porcelain` + sha256 of every script it runs.
- **F3** (depth, operability): move `tuple(old_handlers)` inside the guard (E7), or list P2 as debt and qualify lifecycle :255-256.
- **F4** (calibration): pin a constant impl digest as the model already is, or state that the runner's pin is computed at runtime.
- **F5** (calibration): 17 of 38 non-confirm falsify reports (incl. ToolFaultPaths, SurvivorUniverse, RevToolDelta, SafetyDelivered, SimplifyC2, StaleDocs, TrendVerdicts) appear nowhere in the lesson, though lesson :288 (copy B) presents its list as the named debt.
- **No harm observed:** 5 legacy frozen/current gate pairs give byte-identical stdout; wrong-probe-pin exits 1. All retained legacy receipts carry impl `e404b91a…`, so five-pin strictness only affects null-impl receipts (none retained). No-harm clones (run.py:62) ran 101f3991 and touch no changed file. Cost: gate selftest 61→69 (now 72) mutations; C2 count 1576 s.

## Trend proposals (no round-18 author verdict in SCORECARD/lesson/LOG as of 01:49)
- **expansion — improved:** `corpus/README.md:261` coverage row for new `knowledge/loopback-listener-ownership.md`, citing mined S048–S050.
- **quality — harmed as-is, fixable:** F1 leaves S055 and lifecycle :263-269 stale and unmarked, and E7 contradicts lifecycle :255-256 (harm rule, LEARNING.md:34). Becomes improved after F1/F3 (S047 supersedes S043, S056 supersedes S054, v3 tri-state). ReportTrends' unconditional "quality improved" is unsupported on this tree.
- **discernment — improved** via LEARNING.md:35 route 2: outside round-17 R2/R4 → M1/M2 → KQ23/KQ24 (QUALITY.md:132-133), with retained `kq23-controls.py`. Still author-side; the round-18 non-author sample is owed.

## Limits
C2 was not re-run (1576 s); recomputed from rows and the pre-repair diff only. The P2 trigger was a synthetic module-global shadow; natural routes (MemoryError, a signal before SIG_IGN) are [INFERENCE]. E8 forges a receipt emulating a genuine run; no swapped server was launched. The lane is still changing, so findings bind to the digests above.
