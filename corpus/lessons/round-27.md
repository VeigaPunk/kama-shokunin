# kama — round 27 lesson (2026-10-23, attempt 3)

Author: kama L1 round 27 attempt 3 (KamaR27A3). Attempts 1 (KamaR27, died
05:25:25Z) and 2 (KamaR27A2, died 06:19:06Z) ended with the orchestrator
process. Their landed commits `530eaa99`..`0ec32cac` are part of this round's
history; their uncommitted lane files (1853 paths under
`.ufo/waves/round-27/w1-controls/advice/` and `out/`) were moved unread to
`/fast/scratch/hyaku/kama-r27/attempt2-untracked-w1-scratch/` and are not
cited.

## Claims

- **C1 (measured, depth) — withdrawn before data.** The preregistered claim
  (`.ufo/waves/round-27/preregistration.json`, target `counted >= 15`) needs a
  committed non-author shortcut-control receipt for each class it names
  before any data seat (round-26 spot-check defect 2). Under amendment A3 none
  exists: the 37-seat control wave dispatched 05:41:33Z died with the
  orchestrator, and a dead seat's task is never resent. No data seat was ever
  dispatched in this round. The counter, predicate and target are unchanged;
  the claim is not pursued, so it neither meets nor misses. This is an honest
  stop, not a re-scaled target.
- **X1 (exploratory, calibration — the lane's claim-measurement method).**
  Surface: `corpus/knowledge/echo-discriminating-counters.md` and
  `corpus/QUALITY.md` KQ37. What it improves: a counter that credits live
  error signatures must refuse decoded-request echoes and shared message
  frames. Why the prior state lacked it: the round-26 counter compared raw
  request bytes (line 384) and a base-tree shortcut met it 12/12; QUALITY.md
  held no echo rule. Sources opened this round: S136, S137. Verdict: only a
  named non-author reviewer can make it `unprovable-but-better`; wave seats
  supply evidence, not the verdict.

## Repairs (round-26 spot-check routed defects)

1. LOG.md in-place rewrite: appended correction entry at the end of LOG.md
   pointing at `7f84cd0e` → `fd48f9a3`.
2. Counter F2/F1/F3: the A3 counter (`count-c1.py`, landed `1471f67`)
   compares JSON-decoded request strings and excludes help/version text and a
   healthy-run log; KQ37 makes the rule a criterion. The "one receipt per
   class before data" part is met only vacuously (no data seat ran).
3. CriticShortcutRows pins: `info-help.txt` and `info-version.txt` committed
   under `.ufo/waves/round-27/repairs/d3-r26-shortcut-pins/`; their sha256
   equal what the pinned b11755 binary prints today; the COUNTER_SHA value
   equals the round-26 counter bytes (checked there, the script itself is not
   edited).
4. Dead-seat provider bytes: the `errorMessage` transcript lines of
   KamaR26CtlDoNothing, KamaR26CtlJunk and KamaR26CtlNoReader (429
   `RESOURCE_EXHAUSTED`, gemini-4-argon-high, reset 2026-10-25T14:27:28Z)
   committed under `.ufo/waves/round-27/repairs/d4-r26-dead-seat-errors/`.
5. Receipt key mislabel: `.ufo/waves/round-26/final/c1-tip.out:2` and
   `final/c2-kq36-tip.out:2` read `tree=7e5ff9b5…`; `7e5ff9b5` is a commit
   (`git cat-file -t` → `commit`) whose tree is `f2a981ee…`. The key should
   read `commit=`. The round-26 report (fleet `kama.md:152-153`) rejected
   AttackE2610 on the ground that `7e5ff9b5` is a commit; that is right, but
   AttackE2610's finding (`advice/AttackE2610.md:79`) was that the receipt
   names a revision other than the landed f4066979 (it also inverted the
   relation: `f2a981ee` is the tree of commit `7e5ff9b5`, not the reverse),
   and the mislabel stands (spot-check line 197).
   The round-26 files are not edited.
6. Round-26 Gate reject reasons (`lessons/round-26.md:63` and `:67`): the
   metrics message was held at base in **three** round-18 advice files
   (`ProbeArgvEffects.md`, `ScoutLlamaMetricsProps.md`,
   `ScoutLlamaNewerTags.md`) and three round-16 advice files
   (`CriticC2ToyModel.md`, `RevengerRound1Live.md`, `ScoutMetricsSource.md`),
   not one and two (`git grep -l 'does not support metrics' a720399e --
   .ufo/waves`). CriticAxisFit called its point "a measured caveat, not a
   kill" (`round-26/w1-build/advice/CriticAxisFit.md:105`), so the reject was
   L1 discretion. `authentication_error` has one fault (the invalid-key 401),
   so "shared by many faults" is true only of `invalid_request_error`
   (spot-check line 195).
7. S133 anchor: S138 supersedes S133 with `try_clear_idle_slots lines
   1810-1835`.
8. `count-c2.py` reads cell values from the receipt: **not fixed** this
   round. The attempt-2 seat that held it died and its task is not resent;
   the defect stays open (round 25 defect 5, round 26 defect 8).

## Gate

New SOURCES rows, each opened this round by the L1:

| row | URL | accessed | quote (≤25 words) and location |
|---|---|---|---|
| S136 | https://www.rfc-editor.org/rfc/rfc8259.txt | 2026-10-23T06:48Z (raw sha256 61a5378f…2d7) | "Any character may be escaped." — §7 Strings, rfc8259.txt line 433 |
| S137 | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp#L1375 (raw fetch sha256 b4f4aae7…d442) | 2026-10-23T06:48Z | `throw std::invalid_argument("response_format type must be one of \"text\" or \"json_object\", but got: " + response_type);` — line 1375 |
| S138 | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp (raw fetch sha256 dd1de0f2…2329) | 2026-10-23T06:53Z | `bool try_clear_idle_slots() {` — line 1810; its closing `}` is line 1835 |

No existing row's `status`, `recheck` or `used-by` changed.

## Mistakes

| class | evidence pointer | captured-by | fix |
|---|---|---|---|
| unbounded self-referential fixture write: a seat's preload fixture was appended to itself until it filled /fast | attempt-2 seat ReviewA3Diff: `sitecustomize.py` reached 262699483136 bytes of a repeated two-line MARKER snippet; copies of Main's removal note and the first 4096 bytes: `.ufo/waves/round-27/a3/mistake-runaway/` | none — the wave contexts capped processes, memory and wall time, never file size, and never forbade a MARKER or log path that is also the fixture | every round-27 wave context requires `ulimit -f` on fixture-writing commands and a MARKER file separate from any file Python imports; shown able to fail only if this round's FixtureBoundDemo seat receipt shows the cap stopping a self-append (see §Fix receipt) |
