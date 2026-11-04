# SC03Lesson — scoped findings (kama round 79, wave 1, scribe)

Full evidence: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-79/w1/SC03Lesson/`

1. **Deliverables drafted (not landed; the L1 lands).**
   - `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-79/w1/SC03Lesson/round-79.md`
     (15,141 bytes): opening naming the three frozen claims (C1 calibration, C2 operability,
     C3 coverage) and the wave (14 seats: 4 executor, 3 scribe, 2 scout, 1 connector,
     1 reviewer, 2 critic, 1 mutation-tester; attack 4/14), with base `ee53f1a2`, freeze
     `33103703`, sealed `7a3cd982`, scribe-cut tip `f7442dea53bd8f474293a2252437b5d869801f49`
     read with `git -C <lane> rev-parse master`; `## Gate` (llama.cpp router `GET /models`
     admit with URL, access date 2026-11-04 and a 16-word located quote; a same-surface
     duplicate reject with reason and flip; the own-work instrument class note for C3's census
     class); `## Mistakes` (`stale-premise`, round 78's "tip" wording, with the F5 capture and
     the correction as fix); `## Corrections` with exactly two frozen-shape blocks, F5 and F6.
   - `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-79/w1/SC03Lesson/llama.cpp-server-README-39febd2ad.md`
     (135,608 bytes, sha256 `8fd5abde2fb52de3b30f30a170631d4c0d92febecc8da44d0541e48b132b35c6`)
     — retained raw body of the admitted source.
   - `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-79/w1/SC03Lesson/fetch-receipt.txt`
     — command, exit, bytes, sha256, line count, access date.

2. **Correction blocks (frozen shape, verified with the counter's own parser).** Imported
   `CORRECTION_RE` and `norm` from
   `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round79-selfrecord-round78.py` and applied
   them to the draft: **2 matches, 0 others**. F5 `old=tip-accounting=rev:22cce544/is-tip:true`
   `new=tip-accounting=rev:22cce544/is-tip:false`; F6
   `old=c1-pre-correction-run=committed`
   `new=c1-pre-correction-run=committed:.ufo/waves/round-79/measured/v2/c1-pre-correction.out`;
   both `at=7a3cd98243b69fcbee0cc9e31878782bd8459320` (40 hex, equal to the sealed revision),
   `date=2026-11-04`; both `old` strings equal the plan's declared value strings verbatim. The
   tokens are unquoted because the reader matches `corrected (F\d) old=(\S+) new=(\S+)`.

3. **New-value re-derivation, checked in a scratch clone (shape check, not a scored run).**
   In `/fast/scratch/hyaku/kama-r79/SC03Lesson/clone.Qa8p/repo` (`git clone --shared` of the
   lane; `git rev-parse --show-toplevel` asserted equal to the clone before the fixture commit),
   the receipt was committed at the clone tip `47331e14`. The counter's own
   `Record.verify_f5` / `Record.verify_f6` then returned:
   `F5_new_rederives=True`, `F5_old_rederives=False`, `F6_new_rederives=True`,
   `F6_wrong_path=False` (wrong-path control, fail-closed). **Dependency:** F6's new value
   re-derives only once the L1 commits
   `.ufo/waves/round-79/measured/v2/c1-pre-correction.out`; at this cut it exists in the
   worktree untracked (`git status --porcelain .ufo/waves/round-79/measured/v2/` → `??`).

4. **Gate evidence.** `curl -fsSL` of
   `https://raw.githubusercontent.com/ggml-org/llama.cpp/39febd2adb947b70da35e95f9351b3bf58ad170a/tools/server/README.md`
   → exit 0, HTTP 200, 135,608 bytes, sha256 `8fd5abde…b35c6`, identical to the pre-freeze
   receipt `.ufo/waves/round-79/measured/before/source-router-models.out` and to
   `/home/vgpnk/src/llama.cpp` (HEAD `39febd2ad…`). Quote at line 2227, 16 words: "If a model is
   not running, it will be added or updated according to the source"; the same section documents
   `status.value` at 2265/2271/2278/2287/2294/2303/2319 (six values). Precision carried into the
   lesson: line 2227 literally scopes to the `?reload=1` refresh, so "unloaded models are listed"
   rests on line 2199 plus the non-loaded examples. Reject/flip: re-rowing the same file for
   S001's and S526's surfaces (with S035/S112/S134/S494 at other pins) is a duplicate; the
   router-mode `GET /models` + `status.value` anchor is the flip. Cross-checked against
   `w1/SC01Sources/sources-append.md` (drafts `S553`, next free id after `S552`) and
   `w1/SCT02Source/source-check.md` (PASS on all four checks); no contradiction found.

5. **Mistake evidence (`stale-premise`).** `git rev-parse 22cce544` →
   `22cce544b23670984fa9e42bea673d603881aae7`; `git merge-base --is-ancestor 22cce544
   7a3cd982…` exit 0; `git rev-list --count 22cce544..7a3cd982…` → 6; the round-78 gate receipt
   `rev=2842ad29` is 5 commits before the tip. Sources: `SCORECARD.md:4538` (§Round 78 §Gate and
   tip state) and `corpus/lessons/round-78-verifier-spotcheck.md:30-34` (§1 defect 1). F6's
   sealed absence re-derived: `git grep -l mismatches=1 7a3cd982… -- .ufo/waves/round-78/` → 0
   files; the receipt header names `fa65ce2c` = `381b53dc~1`.

6. **State at the scribe cut.** `tools/round79-selfrecord-round78.py` present;
   `tools/round79-unregistered-census.py` absent (no counter run claimed);
   `tools/pre-report-gate.py` still `BASE_ARM_ORDER 9` (`.ufo/waves/round-79/measured/before/c2-gate-arms.out`);
   `tools/kama-probe.sh listeners` still without a `registered` column
   (`probed=33 model_endpoints=7 foreign_service=24 unauthorized_service=0 dead=2 not_http=0
   model_loading=0`, exit 0, `.ufo/waves/round-79/measured/before/c3-listeners-base.out`).
   C2/C3 are recorded from the frozen plan and pre-freeze receipts, not as executed counters.

7. **Bounds.** Writes only the three files under
   `.ufo/waves/round-79/w1/SC03Lesson/` and this digest; no edit to `corpus/lessons/`, the plan,
   `corpus/SOURCES.md`, or any sibling seat dir; no git writes in the lane (read-only git only;
   the one fixture commit was inside the scratch clone); the scored gate and the C1 claim
   counter were not run; no installs; scratch `/fast/scratch/hyaku/kama-r79/SC03Lesson/`
   removed (`rm -rf`, verified absent).
