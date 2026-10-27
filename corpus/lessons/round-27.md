# kama — round 27 lesson (2026-10-23, attempt 3)

Author: kama L1 round 27 attempt 3 (KamaR27A3). Attempts 1 (KamaR27, died
05:25:25Z) and 2 (KamaR27A2, died 06:19:06Z) ended with the orchestrator
process. Their landed commits `530eaa99`..`0ec32cac` are part of this round's
history; their uncommitted lane files (1846 files under
`.ufo/waves/round-27/w1-controls/advice/` and `out/`; the 1853 first written
here was the L1's `git status --porcelain --untracked-files=all | wc -l`,
taken while the 7 attempt-3 repair files were also untracked: 1846 + 7) were moved unread to
`/fast/scratch/hyaku/kama-r27/attempt2-untracked-w1-scratch/` and are not
cited.

## Claims

- **C1 (measured, depth) — withdrawn before data.** The preregistered claim
  (`.ufo/waves/round-27/preregistration.json`, target `counted >= 15`) needs a
  committed non-author shortcut-control receipt for each class it names
  before any data seat (round-26 spot-check defect 2). Under amendment A3 none
  exists: the 37-seat control wave dispatched 05:41:33Z died with the
  orchestrator, and a dead seat's task is never resent. No data seat was ever
  dispatched in this round. The A3 counter, predicate, target and kill rule
  are unchanged since `0ec32cac` (A0-A3 were pre-data amendments). Under the
  frozen kill rule, counted < 15 at the landed tip is a miss, and the landed
  tip holds no round-27 registry: C1 is reported as a **miss** (honest stop),
  not amended and not re-scaled. (The first landed text said "neither meets
  nor misses"; wave seat CriticC1Withdrawal showed that exemption is not in
  the frozen rule.)
- **X1 (exploratory, calibration — the lane's claim-measurement method).**
  Surface: `corpus/knowledge/echo-discriminating-counters.md` and
  `corpus/QUALITY.md` KQ37. What it improves: a counter that credits live
  error signatures must refuse decoded-request echoes and shared message
  frames. Why the prior state lacked it: the round-26 counter compared raw
  request bytes (line 384) and a base-tree shortcut met it 12/12; QUALITY.md
  held no echo rule (the round-26 preregistration named the echo and
  split-message classes as intents, and the spot-check prescribed decoded
  comparison; neither was lane knowledge or a criterion). Sources opened this
  round: S136, S137, S139 (supersedes S136); S138 is the round's anchor
  correction row. Verdict: only a
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

## X1 evidence (wave w1a3, 34 seats; reports under `.ufo/waves/round-27/w1a3/advice/`)

| question | seat | result |
|---|---|---|
| does b11755 echo the decoded `response_format.type`? | ExecLiveEchoProbe | yes: plain, first-char-escaped and fully escaped spellings give byte-identical 400 bodies holding the decoded value; two values share one frame; control 200 (`w1a3/out/ExecLiveEchoProbe/receipt.json`, observed 07:11:54Z) |
| round-26 test vs A3 on the 12 round-26 rows (offline) | ExecOfflineEchoReplay | round-26 flags 0/12; A3 (f) as written 0/12 (string bodies); A3 shape check refuses 12/12; A3 (f) on decoded bodies 12/12 |
| is the decoded part load-bearing? | MutEchoDecodedLoadBearing | raw-body-only mutant 0/12 (killed); other single-guard mutants survive because guards overlap |
| is the frame check load-bearing? | MutFrameLoadBearing | frame on 1/12 survivors, off 12/12 (killed) |
| does the frame rule collapse distinct genuine faults? | ExecOfflineFrameReplay | clause (h) verbatim: round-26 shortcut 1/12 survive (11 collisions); E26 17/17 survive, 0 collisions (9 rows have message = signature, so the frame test is vacuous there; 3 process rows are outside its reach) |
| other echo sites in the snapshot | ScoutEchoSitesSnapshot | 12 request-string frames (S137 one of them) + 14 request-JSON dumps |
| other raw echo tests in the lane | ScoutRawEchoInLaneTools | only round-26 `count-c1.py:384` |
| does the boundary leg cost genuine rows? | CriticBoundaryLegProbe (residual) | refuses 12/12 frame-tail variants, 12/12 round-26 rows, and 3/17 genuine E26 rows |
| does the revised entry overclaim? | CriticRevisedEntry (residual) | four overclaims (string-body reachability, literal binding, ASCII conformance, frame-replay provenance), fixed |
| does a sibling already hold KQ37? | ScoutSiblingEchoRules | no equivalent; two siblings name "server echo" as a control shape only |

## Gate

New SOURCES rows, each opened this round by the L1:

| row | URL | accessed | quote (≤25 words) and location |
|---|---|---|---|
| S136 | https://www.rfc-editor.org/rfc/rfc8259.txt | 2026-10-23T06:48Z (raw sha256 61a5378f…2d7) | "Any character may be escaped." — §7 Strings, rfc8259.txt line 433 |
| S137 | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp#L1375 (raw fetch sha256 b4f4aae7…d442) | 2026-10-23T06:48Z | `throw std::invalid_argument("response_format type must be one of \"text\" or \"json_object\", but got: " + response_type);` — line 1375 |
| S138 | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp (raw fetch sha256 dd1de0f2…2329) | 2026-10-23T06:53Z | `bool try_clear_idle_slots() {` — line 1810; its closing `}` is line 1835 |
| S139 (supersedes S136) | https://www.rfc-editor.org/rfc/rfc8259.txt (same fetch as S136, sha256 61a5378f…2d7) | 2026-10-23T06:48Z (same fetch, re-read by the L1 the same day) | "the character is represented as a 12-character sequence, encoding the UTF-16 surrogate pair." — §7, rfc8259.txt lines 456-457 |

No existing row's `status`, `recheck` or `used-by` changed. S136 stays as
landed; S139 supersedes its escape-length wording (S136 said six characters
for any character; CriticEntryFactsSources) and its STD 90 attribution (the
RFC text does not carry it; the RFC Editor and Datatracker indexes do,
ScoutReopenS136). The three new rows were re-opened by non-author seats:
ScoutReopenS136, ScoutReopenS137, ReviewLessonGate (S136-S138) and the
residual seat ReviewS139Row (S139), all `holds` (reports in
`.ufo/waves/round-27/w1a3/advice/` and `residual/advice/`).

Wave findings, admitted or rejected by the L1:

| finding (seat) | decision | reason |
|---|---|---|
| redact `credentialId`, message ids, transcript paths and quota-reset values from the d4 error lines and README (SentinelCommittedBytesSecrets) | **reject** | routed defect 4 asks for the raw provider error bytes; the sentinel found no credential material, token, key or URL; `credentialId` is a numeric slot index (`18`); redaction would break the byte identity ReviewRepairD4Bytes verified (sha256-equal to the transcript lines) |
| change the frozen counter to `casefold()` and literal deletion (CriticEntryRuleVsCode) | **reject** for this round | the A3 counter is frozen and C1 is not run; the gap is recorded in the entry and the KQ37 qualification instead |
| generalise KQ37 into "full shortcut-shape control coverage before data" (ConnectorShortcutClasses) | **reject** as KQ37 scope | KQ37 is the echo/frame rule; the general pre-data control rule already stands in prompt §9 and in seven sibling QUALITY files (ScoutSiblingEchoRules); copying it would duplicate, not add |
| clause (f) does not decode a string body; the 12 round-26 rows are refused by the shape check (ExecOfflineEchoReplay, ScoutRawEchoInLaneTools) | admit | entry §How the round-27 counter implements it; KQ37 qualification 2 |
| boundary-shifted signatures pass KQ37's echo and frame legs 12/12 (CriticKQ37Wording) | admit | KQ37 qualification 1 and the entry's boundary leg |
| `lower()` is not case folding; positional frame; tab-only remainder (CriticEntryRuleVsCode) | admit | entry §shortfalls; KQ37 qualification 3 |
| six-character escape wrong outside the BMP; "whatever string" too broad (CriticEntryFactsSources) | admit | S139; entry fact 1 and 2 rewritten |
| file/model echo provenance, baseline scope, conservative rejection (CriticEntryLimits) | admit | entry §limits and §rule |
| "neither meets nor misses" is not in the kill rule (CriticC1Withdrawal) | admit | C1 reported as a miss |
| X1 novelty: decoded comparison was prescribed at base (CriticNoveltyAtBase) | admit | entry "What is new here and what is not" |
| LOG correction miscounts sentences and omits f4066979 (ReviewRepairD1Log) | admit | second appended LOG correction |
| "1853 paths" is not the moved count (ReviewUntrackedDisposal) | admit | header now 1846 files |
| mistake row 1: mechanism not established; "every round-27 wave context" false; the cap does not stop the process (CriticMistakeRow) | admit | row 1 narrowed |
| clause (f) still sees stored string bodies; clause (d) literal binding weaker than one literal; ASCII conformance overstated; frame replay used synthetic metadata (CriticRevisedEntry, residual) | admit | entry §How the round-27 counter implements it rewritten |
| frame by "message minus signature" lets one literal give many frames; folding needs all compared text ASCII (CriticKQ37Qualification, residual) | admit | KQ37 qualification points 4-5 |
| boundary leg refuses 3/17 genuine E26 rows (CriticBoundaryLegProbe, residual) | admit as a disclosed cost | KQ37 qualification point 6; entry §boundary |
| replace the boundary leg with template-provenance spans (CriticKQ37Qualification, residual) | **reject** for this round | it needs per-site template knowledge the lane does not hold for the 26 echo sites; recorded as the round-28 counter design question, not as a criterion change after review |
| SCORECARD C1 "measured commit" pointed at a report not yet written (ReviewSelfAssessment: 1 mismatch in 57) | admit | cell now names `d183ec57` and its receipt |
| lesson F3-F5 (S139 re-open, 1853 composition, S138 omitted) (ReviewLessonFinal) | admit | fixed in this lesson |


## Mistakes

| class | evidence pointer | captured-by | fix |
|---|---|---|---|
| unbounded repeated fixture growth: a seat's preload fixture grew until it filled /fast (mechanism not established: the retained prefix repeats the two hook source lines, which the hook itself does not write; Main's note says MARKER "evidently" pointed back) | attempt-2 seat ReviewA3Diff: `sitecustomize.py` reported at 262699483136 bytes; copies of Main's removal note and the first 4096 bytes: `.ufo/waves/round-27/a3/mistake-runaway/` | none — the attempt-2 wave context capped processes, memory and wall time, never file size, and had no rule keeping a MARKER, log or redirect off a file that is imported or read as input (`w1-controls/spec.json` context; CriticMistakeRow) | the attempt-3 wave and residual contexts require `ulimit -f` on fixture-writing commands and a MARKER/log path disjoint from imported or input files; the cap bounds each file's size, it does not stop the process; shown able to fail by ExecFixtureBoundDemo (§Fix receipt) |
| correction written from memory instead of from the diff: the appended round-26 LOG correction said "three sentences" (four changed) and omitted the in-place edit at `f4066979` | LOG.md first round-27 correction entry; `w1a3/advice/ReviewRepairD1Log.md` | the round's own review seat (ReviewRepairD1Log) | second appended LOG correction; a correction's statement list is re-derived from `git diff`/`git log -- <file>` before landing |
| source paraphrase broader than the source: S136 said every character has a six-character escape | S136 `teaches`; `w1a3/advice/CriticEntryFactsSources.md` | the round's critic seat | S139 supersedes S136 |
| count over a mixed set: "1853 paths" counted 7 attempt-3 files with the 1846 moved files | lesson header (first landed text); `w1a3/advice/ReviewUntrackedDisposal.md` | the round's review seat | header corrected; counts are taken over the exact set named |


## Fix receipt (mistake row 1)

ExecFixtureBoundDemo (`.ufo/waves/round-27/w1a3/out/ExecFixtureBoundDemo/receipt.json`)
ran a fixture that appends its own bytes to itself. Under `ulimit -f 2048`
(2 MiB) it stopped at exactly 2,097,152 bytes (exit 153 with SIGXFSZ at its
default; exit 1, `OSError [Errno 27] File too large`, when launched from bash,
which starts children with SIGXFSZ ignored). The same loop under a 20 MiB
bound for 5 s reached 20,971,520 bytes, and a 2 MiB run with the same 5 s
timeout stopped at 2,097,152: the cap, not the timeout, stops it. A writer
that swallows the EFBIG error keeps spinning until its timeout, but the file
stays at the cap. So the rule bounds disk use; it does not end the process.

## Restored lines (round 52)

Lines this file lost in place, re-appended verbatim in round 52 (claim C2): the file is declared append-only with corrections appended (`registry/append-only-contract.tsv`), and `tools/append-only-audit.py` v6 graded each line below as deleted and no longer held (round-51 rows of `registry/append-only-disclosures.tsv`). They are historical bytes, kept so that no declared line is lost; where this file's later text replaced them, the later text stands. One fenced block per deleting commit, in history order.

Deleted by `d183ec572a5e` (round-27: w1a3 wave evidence (34 seats); X1 entry revised from wave findings (decoded-echo conditions, boundary leg, limits, novelty); KQ37 round-27 qualification; S139 supersedes S136; second LOG correction; C1 reported as miss; lesson Gate/X1 evidence/Mistakes/Fix receipt; SCORECARD, README, LOG round-27 entries):

`````text
history; their uncommitted lane files (1853 paths under
`.ufo/waves/round-27/w1-controls/advice/` and `out/`) were moved unread to
  dispatched in this round. The counter, predicate and target are unchanged;
  the claim is not pursued, so it neither meets nor misses. This is an honest
  stop, not a re-scaled target.
  held no echo rule. Sources opened this round: S136, S137. Verdict: only a
No existing row's `status`, `recheck` or `used-by` changed.
| unbounded self-referential fixture write: a seat's preload fixture was appended to itself until it filled /fast | attempt-2 seat ReviewA3Diff: `sitecustomize.py` reached 262699483136 bytes of a repeated two-line MARKER snippet; copies of Main's removal note and the first 4096 bytes: `.ufo/waves/round-27/a3/mistake-runaway/` | none — the wave contexts capped processes, memory and wall time, never file size, and never forbade a MARKER or log path that is also the fixture | every round-27 wave context requires `ulimit -f` on fixture-writing commands and a MARKER file separate from any file Python imports; shown able to fail only if this round's FixtureBoundDemo seat receipt shows the cap stopping a self-append (see §Fix receipt) |
`````

Deleted by `4d2e74f421bc` (round-27: residual review call (7 seats) evidence; late w1a3 seat outputs; X1 entry corrections (string-body reachability, literal binding, ASCII scope, frame replay provenance, boundary-leg cost); KQ37 residual qualification; SCORECARD measured-commit fix; lesson residual evidence and Gate decisions):

`````text
here also counted 7 attempt-3 repair files) were moved unread to
  round: S136, S137, S139 (supersedes S136). Verdict: only a
ScoutReopenS136, ScoutReopenS137, ReviewLessonGate (all `holds`; reports in
`.ufo/waves/round-27/w1a3/advice/`).
| unbounded self-referential fixture write: a seat's preload fixture was appended to itself until it filled /fast | attempt-2 seat ReviewA3Diff: `sitecustomize.py` reached 262699483136 bytes of a repeated two-line MARKER snippet; copies of Main's removal note and the first 4096 bytes: `.ufo/waves/round-27/a3/mistake-runaway/` | none — the wave contexts capped processes, memory and wall time, never file size, and never forbade a MARKER or log path that is also the fixture | every round-27 wave context requires `ulimit -f` on fixture-writing commands and a MARKER file separate from any file Python imports; shown able to fail by the wave seat ExecFixtureBoundDemo (§Fix receipt) |
`````
