ATTACK round-26 self-assessment (SCORECARD "## Round 26", LOG "## Round 26", corpus/README.md "Frontier disposition — round 26"): BREAKS

Seat: KamaR26.ReviewerScorecardLogTruth (reviewer, read-only). Repo
/home/vgpnk/Projects/shokunin/kama-shokunin at `git rev-parse HEAD` =
f4066979096e3452ae731c0e09e50155c6d8258a. Sections read: SCORECARD.md:1312-1351,
LOG.md:1680-1709, corpus/README.md:402-410.

Summary. The C1 numbers hold: 17 registered rows, 17 counted, counter sha
unchanged since a23c0e04, 57 executor candidate entries, every row's quote
verbatim at its anchored line in bytes equal to a fresh fetch. Four statements
are false and four cannot be checked from the repo:

- FALSE: the before-state claim, made in both SCORECARD and LOG, that SKILL.md
  held no live b11755 error signature at base.
- FALSE: the claim that the September sample came from "ports that are now
  dead".
- FALSE (incomplete): "42 late paths committed (a4a159c3)".
- FALSE (misleading): the fault-survey count "8 more".
- UNVERIFIABLE: the round report that two statements point to does not exist,
  and the measured-commit cell names no commit.

No server started (this seat has no port block); the counter was not run.
`pgrep -af llama-server` was not needed for my processes, because I started
none.

## Defects (by severity)

### D1 (high, calibration): base SKILL.md already held live b11755 error signatures

Statements:
- SCORECARD.md:1325-1326: "before this round SKILL.md held only the September
  sample from dead ports ("Historical error signatures")".
- LOG.md:1682-1683: "Before: SKILL.md held no live error signature for the
  b11755 runtime".

Check: `git show 1560e4d8:SKILL.md > /fast/scratch/hyaku/kama-r26w2/ReviewerScorecardLogTruth/base-SKILL.md`,
then I read lines 509-530 and 677-690 of that file.

Result: false. At base:
- base SKILL.md:521-523 reads "Error signature (llama.cpp b11755 single-model,
  every non-frontend path while loading, before the API-key check): `503`
  `{"error":{"message":"Loading model","type":"unavailable_error","code":503}}`".
  This is a b11755 error signature graded live by the round-16/17 lifecycle
  tool (`loading_envelope_graded`, base SKILL.md:575).
- base SKILL.md:689 (Round-25 decision rows, receipt
  `.ufo/waves/round-25/final/context-capacity-receipt.json`): "every
  processing request fails with HTTP 500 `Context size has been exceeded.`",
  observed live on build 11755 (cells L1-L3).
- Wave 1 already knew this. `.ufo/waves/round-26/w1-build/out/ScoutBaseOverlap/overlap.md:86`
  lists "The `Loading model` 503 envelope ... at SKILL.md:518-523 — still
  emitted".

The C1 count is not affected: those strings are not E26 rows, and clause (b)
only needs each E26 signature to be new. The false part is the description of
the surface that moved.

Smallest correction (append; do not edit history):
- SCORECARD: "before this round SKILL.md held the September sample from
  historical ports plus two live b11755 signatures (round-16 `Loading model`
  503; round-25 `Context size has been exceeded.` 500); none of the 17 E26
  strings".
- LOG: "Before: SKILL.md held two live b11755 error signatures (SKILL.md
  round-16 and round-25 sections) and none of the 17 below".

### D2 (medium): not all of the "dead ports" are dead

Statements:
- LOG.md:1698-1699: "SKILL.md "Historical error signatures" is a September
  sample from ports that are now dead".
- SCORECARD.md:1325, "from dead ports".

Check: `ss -ltn | rg ':879[01]\b'`, a passive socket listing; I sent no
request to any port.

Output:
```
LISTEN 0      5          127.0.0.1:8790       0.0.0.0:*
LISTEN 0      512        127.0.0.1:8791       0.0.0.0:*
```
Exit 0. The sample's rows include ":8790, :8791 broker probes" (base
SKILL.md:176). 34113, 8080, 11434, 8888, 34955 and 41453 are not listening
(`ss -ltn | awk '{print $4}' | rg ':(34113|8080|8790|8791|11434|8888|34955|41453)$'`
matched only 8790 and 8791).

[INFERENCE] The current listeners may be different services. Even so, "now
dead" is false for two of the sampled ports.

Smallest correction: "a September sample, several of whose ports (34113, 8080)
no longer listen".

### D3 (medium): "42 late paths committed (a4a159c3)" is incomplete

Statement: LOG.md:1706, "42 late paths committed (a4a159c3)". Lesson §Mistakes
row 4 and §Routed defects row 1 say the same.

Checks and results:
- `git show --name-status --format='%h %s%n%b' 7e5ff9b`: the commit message is
  "commit the late round-25 L3 replication log skipped by the directory commit
  (routed defect 1)", and the commit adds
  `.ufo/waves/round-25/a2-falsify/out/ReplicateReceipt/replication-run3/raw/L3.server.log`.
  So a4a159c3 missed at least one of the 42, and it landed at 7e5ff9b5.
- `git show --name-status --format= a4a159c | rg 'round-25' | awk '{print $1}' | sort | uniq -c`
  gives 220 A, 2 M and 1 D under `.ufo/waves/round-25/a2-falsify`.
  [INFERENCE] The spot-check's "42" counts `git status --porcelain` entries,
  where an untracked directory shows as one entry. The number is not a file
  count, and the LOG gives no unit.

Smallest correction: "the 42 late `a2-falsify/` entries committed at a4a159c3
(220 files) and 7e5ff9b5 (one log the directory commit skipped)".

### D4 (low, misleading count): "the fault-survey scout listed 8 more, 3 of them not found by an executor"

Statement: LOG.md:1692-1693.

Check: survey table `.ufo/waves/round-26/w1-build/out/ScoutFaultSurvey/survey.md:24-39`.
I matched each of the 8 survey signatures by substring against every
`*/candidates.json` signature (with `\"` normalised to `"`).

Result:
- Candidates 1-3 ("missing completion id", "unknown control action", "This
  model is not a decision model") match no executor entry.
- Candidates 4-8 match entries from ExecLoraAudio, ExecEmbeddingsInput (three)
  and ExecRequestParams.

So "3 of them not found" holds. "8 more" does not: only 3 are more.

Smallest correction: "the fault-survey scout listed 8, 3 of them not found by
an executor (60 entries in total)".

### D5 (low, unverifiable): the round report the sections point to is missing

Statements:
- SCORECARD.md:1320, measured commit "the landed lane tip named in the round
  report".
- SCORECARD.md:1331-1332, "KQ36 re-run at the landed tip is in the round
  report".
- LOG.md:1702-1703, "(round report)".
- Lesson §Mistakes row 4, "the release lines are in the round report".

Check: `ls /home/vgpnk/Projects/shokunin/.ufo/reports/round-26/` shows chousa,
kagi, kaidoku, kake, kengaku*, kotodama, mori, tameshi and tsukuroi. There is
no `kama.md`. The lane `.ufo/reports/` has no round-26 entry either.

Result: unverifiable at f4066979.
- The KQ36 re-run receipt does exist:
  `.ufo/waves/round-26/final/c2-kq36-tip.out` = "registered 14 observed 14
  bound True missing [] / exit=0 tree=7e5ff9b5…".
- The measured-commit cell names no hash. Round 25 named hashes in this cell.
- The C1 receipt was produced at tree 7e5ff9b5
  (`final/c1-tip.out`; `c1-tip-receipt.json` lane
  `/fast/scratch/hyaku/kama-r26/tip-7e5ff9b5…`), two commits before the
  landed tip f4066979.
- Landed-tip equivalence under the new QUALITY.md KQ36 qualification does hold
  statically:
  `git diff --quiet 7e5ff9b f406697 -- SKILL.md corpus registry .ufo/waves/round-26/count-c1.py .ufo/waves/round-26/sources .ufo/waves/round-25/count-c2.py .ufo/waves/round-25/final`
  exited 0.
  `git diff --name-only 7e5ff9b f406697`, outside `final/` and `w1-build/`,
  lists only `LOG.md`. The counter reads LOG.md nowhere: `count-c1.py:325-330`
  reads SKILL.md, corpus/SOURCES.md and the registry, and `:115` runs `git grep`
  at BASE only.

Smallest correction: write "measured at 7e5ff9b5; counter inputs
byte-identical at landed tip f4066979 (`git diff --quiet` exit 0)" in the
measured-commit cell, and cite `final/c2-kq36-tip.out` directly instead of the
unwritten report. Alternatively, land the round report before these pointers
are read.

### D6 (low, inconsistency): "rejected streak (rounds 23-25) worked calibration and the report-landing auditor"

Statement: SCORECARD.md:1316-1317.

Checks:
- Round 23 closure, rejected-harmed: LOG.md:1413 and SCORECARD.md:1192-1193.
- Round 24, rejected-harmed: `corpus/lessons/round-24-verifier-spotcheck.md:13`.
- Round 25, rejected-honest-stop: `corpus/lessons/round-25-verifier-spotcheck.md:17`.
- The streak holds. However, round 25 also declared C2 (coverage), which was
  live context-capacity work on the same llama-server b11755 serving runtime
  (SCORECARD.md:1261). The preregistration says the streak was "r24-r25"
  (`.ufo/waves/round-26/preregistration.json:11`).
- [INFERENCE] The "anti-loop note" (LOG.md:1697) has no lane-local text. The
  only match is the preregistration itself
  (`rg -n -i 'anti-loop' --hidden -g '!.git' .` in the lane). The fleet
  contract's generic "## Anti-loop rules" are at
  `/home/vgpnk/Projects/shokunin/.scratch/goal-20261022-hyaku-12h.md:180`.

Result: true, but incomplete. The contrast "this round works depth on the
serving runtime" hides the fact that round 25 already worked that runtime.

Smallest correction: "the rejected streak (rounds 23-25) worked calibration
and the report-landing auditor, plus round-25 C2 coverage on the same runtime;
this round works depth".

### D7 (low, contestable): "Capabilities: none added"

Statement: SCORECARD.md:1344.

Check: `git diff --stat 1560e4d8 f406697 -- tools/` shows
`tools/prereg-time-check.py | 252 +++`, a new working tool. The lesson
demonstrates it: exit 1 at a4a159c3 and a12850c5, exit 0 at f071209a and
7e5ff9b5 (`final/prereg-time-check.out`).

[INFERENCE] By the round-25 convention ("capabilities: append", SCORECARD.md:1298-1302),
a new demonstrated tool is a capability row.

Smallest correction: add a capability row for `tools/prereg-time-check.py`
with its demonstration, or state why it is not a capability.

### Related (lesson §Gate, which LOG.md:1694 relies on): "nine further per-flag argument messages"

Check: I compared the unregistered candidates.json entries against
`corpus/lessons/round-26.md` before `## Mistakes`.

Result: ExecBadArgs filed 12 entries. One is registered (E26-17
`GGML_ASSERT(n_outputs >= 1)`) and one is named in §Gate (`error: invalid
argument: `). That leaves 10 per-flag messages: n_parallel, --flash-attn,
repeat-penalty, sleep-idle ("invalid value: cannot be 0 or less than -1"),
cache type, --log-colors, --reasoning, presence-penalty, frequency-penalty and
checkpoint-min-step. "nine" is off by one.

Every other unregistered entry has a reason in §Gate, so "the rest rejected or
held back with reasons" holds in substance.

Smallest correction: "ten further per-flag argument messages".

## Statement table

| # | Text (location) | Check command | Result |
|---|---|---|---|
| 1 | "One declared claim (preregistration …, pre-data amendments A0 and A1)" SC:1314-1315 | `python3 -c "…len(d['claims'])"` → `1 ['C1']`; keys `pre_data_amendment_A0`, `pre_data_amendment_A1` at prereg:29-30 | true |
| 2 | "Lowest axes at the start: depth, calibration and adjacency, all 7" SC:1315-1316 | SCORECARD.md:1260 (calibration 7), :1287 ("calibration 7; depth and adjacency also 7"), :1303 (op 8, fresh 8, depth 7, adj 7), coverage 9 (:1261) | true |
| 3 | "rejected streak (rounds 23-25) worked calibration and the report-landing auditor" SC:1316-1317 | closures LOG:1413, r24 spotcheck:13, r25 spotcheck:17; SC:1261 | true but incomplete (D6) |
| 4 | C1 "depth 7 → 8 (author reading)" SC:1322 | depth 7 at SC:1287/1303 | true as a reading; the closure decides |
| 5 | before `registered 0 counted 0 target 12 met False` at base 1560e4d8 SC:1322, LOG:1683-1684 | `cat .ufo/waves/round-26/before/c1-base.out` → `registered 0 counted 0 target 12 met False not-counted [] / exit=0` | true |
| 6 | after `registered 17 counted 17 target 12 met True` SC:1322 | `cat final/c1-tip.out` → `registered 17 counted 17 target 12 met True not-counted [] / exit=0 tree=7e5ff9b5…`; receipt 17 rows, all `counted` true, no check false | true (measured at 7e5ff9b5) |
| 7 | counter sha256 6501737c…6588, "unchanged since a23c0e04" SC:1322 | `sha256sum count-c1.py` → 6501737c749926be…6588; `git show <r>:…count-c1.py \| sha256sum` → a4a159c eea0cc75…, a12850c f800865d…, a23c0e0/7e5ff9b/f406697 6501737c… | true |
| 8 | measured commit "the landed lane tip named in the round report (receipt …c1-tip-receipt.json)" SC:1322 | receipt exists; `ls fleet .ufo/reports/round-26/` has no kama.md; receipt lane is tip-7e5ff9b5 | unverifiable (D5); inputs identical at f4066979 |
| 9 | evidence: SKILL "## Round-26 live error signatures" E26-01..E26-17 SC:1322, README:404-405 | `rg -n '^## Round-26 live error signatures' SKILL.md` → 1062; `rg -o 'E26-[0-9]{2}'` → 17 distinct | true |
| 10 | registry/error-signatures-r26.json SC:1322 | 17 ids E26-01..E26-17 | true |
| 11 | SOURCES S114-S130 new, one per row SC:1322, LOG:1686-1687 | `rg '^\| ?S1(1[3-9]\|2…' corpus/SOURCES.md`: S114-S130 rows, map E26-01→S114 … E26-17→S130; `git show 1560e4d8:corpus/SOURCES.md \| rg -c '^\| ?S1(1[4-9]\|2[0-9]\|3[0-5])\b'` → no match (exit 1) | true |
| 12 | "verbatim in a pinned 704366d source line" LOG:1686 | python: each signature found at exactly the `#L` line of its SOURCES row in `.ufo/waves/round-26/sources/llama.cpp-704366d/<file>` (17/17 anchor_ok True) | true |
| 13 | pinned bytes equal 704366d (fresh fetch) | `curl -fsSL raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f…/<path>` for server-context.cpp, server-common.cpp, gguf.cpp, llama-context.cpp, exit 0 each; sha256 equal to the lane snapshot (dd1de0f2…, b4f4aae7…, 7505d6a4…, 2a25e556…) | true |
| 14 | "absent from SKILL.md and corpus/ at base, absent from a healthy run and from --help/--version" LOG:1687-1688 | receipt checks `b_new_at_base`, `f_absent_from_baseline` true for all 17 | true per receipt (not re-run) |
| 15 | lesson `corpus/lessons/round-26.md` SC:1322 | file exists; sections Gate, Mistakes, Routed defects | true |
| 16 | "before this round SKILL.md held only the September sample from dead ports" SC:1325-1326 | base SKILL.md:521-523 and :689 | **false** (D1, D2) |
| 17 | "the same counter at base (counted 0)" SC:1327-1328 | row 5 | true |
| 18 | "Known counter limits … (warning lines, decoded echoes, file-content echoes, the 19-row port limit) are listed in the lesson and were not repaired" SC:1328-1330 | lesson §Mistakes row 3: F1-F4, "not fixed"; count-c1.py sha unchanged | true |
| 19 | "Repairs … defects 1-7, lesson §Routed defects" SC:1330-1331, LOG:1704-1708 | lesson:78-93 rows 1-7 (+8) | true; row 1 incomplete (D3) |
| 20 | "count-c2.py now binds raw hashes" SC:1331 | `git diff 1560e4d8 f406697 -- .ufo/waves/round-25/count-c2.py` (+51): RAW_DIR, RAW_FILES, sha checks | true |
| 21 | "KQ36 re-run at the landed tip is in the round report" SC:1331-1332, LOG:1702-1703 | report absent; `final/c2-kq36-tip.out` → `registered 14 observed 14 bound True missing []`, tree 7e5ff9b5 | unverifiable as cited (D5); receipt true |
| 22 | r25 trend conflict cites `.ufo/reports/round-25/kama.md:120-129` (quality unchanged, discernment unchanged) SC:1336-1338 | fleet `.ufo/reports/round-25/kama.md:120` "quality: unchanged", :127 "discernment: unchanged" | true |
| 23 | spot-check lines 187, 194 SC:1338 | `awk 'NR==187\|\|NR==194'` → "Quality: unchanged.", "Discernment: unchanged." | true |
| 24 | r25 trend line said "quality unchanged-to-improved", "discernment improved" SC:1335 | SCORECARD.md:1306-1308 | true |
| 25 | "Other scores held: operability 8, freshness 8, coverage 9, calibration 7, adjacency 7" SC:1343 | SC:1303, :1261, :1260 | true |
| 26 | "Capabilities: none added" SC:1344 | `git diff --stat 1560e4d8 f406697 -- tools/` → new prereg-time-check.py | contestable (D7) |
| 27 | Planned round 27 (stricter counter; held-back signatures in "lesson §Gate, rejected table") SC:1348-1351 | lesson:54-67 rejected table, held-back rows present | true (a plan) |
| 28 | "17 signatures, each reproduced by the counter against the pinned binary and fixture" LOG:1684-1685 | count-c1.py:53-56 SERVER ~/.local/bin/llama-server sha b6a31a8e…cd804, MODEL sha 270cba1b…256d; receipt 17 counted | true per receipt |
| 29 | "Freeze, controls and amendments: preregistration.json, controls/" LOG:1688-1689 | `ls controls` → A1-rescore, KamaR26CtlAllFalse, KamaR26CtlCounterMutants, KamaR26CtlShortcut, L1-dead-seat-controls | true |
| 30 | "KamaR26CtlAllFalse met the A0 counter with help text (12/14); A1 closed it before data (0/14)" LOG:1690-1691 | REPORT.md:53 "invalid-flag-usage: counted 12 of 14 … BREAKS"; invalid-flag-usage.json `registered 14 counted 12 met True`; `controls/A1-rescore/invalid-flag-usage-A1.out` → `registered 14 counted 0 … met False` | true |
| 31 | "Wave 1 (36 seats)" LOG:1691 | dispatch.json `/taskCall/tasks` 36; spec.json items 36; `ls w1-build/out \| wc -l` → 36 | true |
| 32 | "executors filed 57 candidate entries (`w1-build/out/*/candidates.json`)" LOG:1691-1692 | 18 files; sum of `len(signatures)` = 57 at 7f84cd0, 7e5ff9b, 3550523 and f406697 (56 distinct strings; `invalid_request_error` twice in ExecSlotActionNoPath) | true (the superseded "58" at 7f84cd0 was false; corrected at f406697) |
| 33 | "fault-survey scout listed 8 more, 3 of them not found by an executor" LOG:1692-1693 | survey.md:24-39 vs candidates | 3 holds; "8 more" misleading (D4) |
| 34 | "17 registered, the rest rejected or held back with reasons in §Gate" LOG:1693-1694 | unregistered entries mapped to lesson:54-67 | true in substance; "nine" should be ten (Related) |
| 35 | routed defect 8 "(work a lowest axis)" LOG:1696-1697 | r25 spotcheck:230 "8. Next round, work a lowest axis (calibration, depth or adjacency, all at 7)" | true |
| 36 | "the anti-loop note (leave calibration and the report-landing auditor)" LOG:1697-1698 | lane rg finds only prereg:11; fleet contract has generic anti-loop rules | unverifiable as a specific note (D6) |
| 37 | Historical sample "from ports that are now dead" LOG:1698-1699 | `ss -ltn` → 127.0.0.1:8790, :8791 LISTEN | **false** (D2) |
| 38 | "historical llama.cpp rows still match 704366d source (wave-1 ScoutBaseOverlap)" LOG:1701-1702 | overlap.md:77-88 "No staleness found" | true (seat report; not re-derived line by line) |
| 39 | "42 late paths committed (a4a159c3)" LOG:1706 | `git show --name-status 7e5ff9b` adds L3.server.log "skipped by the directory commit" | **false/incomplete** (D3) |
| 40 | "KQ36 qualification" LOG:1706 | `git diff 1560e4d8 f406697 -- corpus/QUALITY.md` → "## Round 26 qualification — KQ36 "landed tip"" | true |
| 41 | "round-25 erratum" LOG:1706 | `corpus/lessons/round-25.md` +13 lines | true (present; content not judged) |
| 42 | "S131-S135 supersession rows" LOG:1707 | `rg -o 'supersedes S1[0-9]{2}'` on S131-S135 → S106, S107, S109, S112, S113 | true |
| 43 | "context-capacity errata" LOG:1707 | `git diff -U0 … corpus/knowledge/context-capacity.md` → `@@ -243,0 +244,19 @@` | true (present) |
| 44 | "SCORECARD trend correction" LOG:1708 | SC:1333-1341 | true |
| 45 | "tools/prereg-time-check.py (exit 1 at a4a159c3)" LOG:1708-1709 | `final/prereg-time-check.out`: a4a159c3 "RESULT fail … exit=1" | true |
| 46 | README: section "holds 17 … signatures with triggers, code meaning, next action and sources S114-S130" README:404-406 | section header `\| id \| signature (channel) \| trigger \| meaning (code) \| next action \| source \|` | true |
| 47 | README: frontier "router-mode model errors (need a router launch)" README:407-408 | lesson:67 (ExecRouterModels: counter always passes `-m`) | true |
| 48 | README: "held-back signatures in `lessons/round-26.md` §Gate" README:408-409 | lesson:63-66 | true |
| 49 | README: "`--embeddings` server crash on `/completion` seen once by a wave-1 seat (not yet reproduced by the lane)" README:409-410 | `w1-build/out/ExecEmbeddingsInput/RUNS.txt:19-22` (SIGSEGV, coredumpctl pid 3310053, one occurrence) | true |

SC = SCORECARD.md, LOG = LOG.md, README = corpus/README.md, prereg =
`.ufo/waves/round-26/preregistration.json`.

## Residual risk and verification gaps

- I did not run the counter or llama-server (no port block). Rows 6, 14 and 28
  rest on the committed receipt, not a fresh run.
- Rows 41 and 43: I checked that the errata are present, not whether their
  content is correct. Other seats own those checks.
- Row 38: I relied on the ScoutBaseOverlap report and did not re-derive every
  historical row against source.
- D2: listener presence only. I sent no request, so the current service
  identity on 8790 and 8791 is unknown.

## Installs

None.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/w2-falsify/advice/ReviewerScorecardLogTruth.md` (this report)
- scratch `/fast/scratch/hyaku/kama-r26w2/ReviewerScorecardLogTruth/base-SKILL.md` (`git show 1560e4d8:SKILL.md`)
- scratch `/fast/scratch/hyaku/kama-r26w2/ReviewerScorecardLogTruth/r26-skill-section.md` (extract of the tip section)
- scratch `/fast/scratch/hyaku/kama-r26w2/ReviewerScorecardLogTruth/fresh/{server-context.cpp,server-common.cpp,gguf.cpp,llama-context.cpp}` (fresh fetch at 704366d, accessed 2026-10-23)
