# kama — round 25 lesson (2026-10-22, attempt 2)

Attempt 1 (dispatched 08:23:56Z) was stood down at 08:30Z by the hyaku
orchestrator for capacity, not for a fault. Attempt 2 is a fresh author. Its
evidence is under `.ufo/waves/round-25/`; the attempt-1 build wave is
committed as a record only (`build/ATTEMPT-1-DISPOSITION.md`).

Claims: C1 calibration repair-first (registered isolation mutant anchors,
stale 2 → 0) and C2 coverage learning claim (declared versus served context
capacity, 14 registered cells on the lane fixture). Registration:
`preregistration.json`, amendments 1-4.

## Gate

All eight rows were opened on 2026-10-22 by wave-1 source seats, each from a
fresh fetch at llama.cpp commit 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad, with
the sha256 in the row's anchor cell. Seat reports:
`.ufo/waves/round-25/a2-build/advice/Src*.md`.

| id | URL | located quote (≤25 words) |
|---|---|---|
| S106 | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/fit.cpp | line 270: "llama_context would use only hp_nct in total for n_ctx == 0, resolve the context before measuring anything else:" |
| S107 | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-context.cpp | line 391: "n_ctx is not divisible by n_seq_max - rounding down to %u" |
| S108 | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server.cpp | line 172: "params.n_parallel = 4;"; line 173: "params.kv_unified = true;"; line 184: "params.n_ctx = params.n_parallel * params.kv_unified_per_slot;" |
| S109 | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp | line 4301: `err = "Context size has been exceeded."` (guarded by line 4298 `if (n_batch == 1 && ret == 1)`) |
| S110 | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/arg.cpp | line 1647: "disable context reduction in llama_params_fit if the user explicitly requests the full context size:" |
| S111 | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/common.cpp | line 1245: `if (params.fit_params) {` and line 1270: `common_fit_params(params.model.path.c_str(), &mparams, &cparams,` |
| S112 | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/README.md | line 165: "when set without -c/--ctx-size, the shared KV pool is sized to n_parallel*N" |
| S113 | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-kv-cache.cpp | lines 301-304: "size = %7.2f MiB (%6u cells, %3d layers, %2u/%u seqs), K (%s): %7.2f MiB, V (%s): %7.2f MiB" |

Status of all eight: new rows, `mined`, used by
`corpus/knowledge/context-capacity.md`. Old-row change: S060 `used-by`
`corpus/knowledge/gguf-declared-identity.md, corpus/lessons/round-20.md` →
`corpus/knowledge/gguf-declared-identity.md, corpus/lessons/round-20.md,
corpus/knowledge/context-capacity.md` (the entry cites it). No status or
recheck cell changed. S109, S108, S110 and S112 share a URL with older rows
(S042/S060, S037/S043, S054/S056, S035) on a different scope; the census
reports these as W04 warnings, as it does for earlier split-scope rows.

Rejected source reading: the attempt-1 seat SrcServerSlotsAuto looked for the
auto slot decision in `server-context.cpp`; it is in `server.cpp` 169-174
(S108). No row was written for the wrong file.

## Mistakes

| Class | Evidence | Captured-by | Fix / demonstrated boundary |
|---|---|---|---|
| stale-anchor: a registered counting instrument drifted from the source it measures, and nobody re-ran it at landing | `round-24-verifier-spotcheck.md:80-82`, routed at `:151-152`; at efe58e96 the C1 command printed `registered 27 stale 2 ['M11-listing-surrogates', 'M17-ref-shadow']`; the M11 literal stopped matching at round-24 commit 92063cf (`a2-build/advice/RevengerM11Element.md`) | none — KQ28-KQ35 do not ask for a registered count to be re-run when the measured source changes (`a2-build/advice/ScribeMistake.md`) | KQ36 below. Shown able to fail: the same command prints `stale 2` at efe58e96 and `stale 0` at 1fc41e34 (both exit 0; `a2-build/advice/ExecC1BaseRun.md`, `ScribeMistake.md`) |
| survival hidden by a same-line re-anchor | M17's re-anchored literal is the round-23 line, but since 92063cf no caller reaches it; F13's kill moved to the new M33 (`a2-build/advice/RevengerM17Sites.md`, causal run on ed1cc3a; `CriticC1NoHarm.md`) | CriticC1NoHarm and MutationM17M33Kill (wave-1 attack seats) | the instrument docstring and SKILL registry row now say M17 survives and why; the full run lists it (`final/c1/c1-tip-mutants.json`: 28 mutants, 26 killed, survivors M17 and M20) |
| counter accepted a wrong value | the amendment-2 counter accepted a pool line ending in 12048 for a pool of 2048, the fit-probe pool for X1, a build string `117550`, and unrecorded overlap for L1 (`MutationC2Counter.md`, `CriticC2SizingA2.md`) | the two wave-1 attack seats | amendments 3 and 4: stricter counter. Shown able to fail on synthetic receipts (amendment 3 `check_after_change`; `a2-build/out/CriticC2SizingA2/counter-attacks-proposed.out`) and on the first committed receipt, which scores 11 of 14 under amendment 4 because it lacks request times |
| misroot: a seat wrote by a relative path into the fleet root | wave-1 seat ReviewerC1Patch (`a2-build/advice/ReviewerC1Patch.md:94`, detail at `a2-build/out/ReviewerC1Patch/evidence.md:73`) first wrote two files under the fleet root, copied them byte-identical (`cmp`) into the lane and removed the fleet copies and the three directories it had created; the falsify scout confirmed no copy remains at the fleet root (`a2-falsify/advice/ScoutMisroot.md`). Seats also left files under `/tmp` outside their scratch (`CriticC1Calibration.md`, `ScribeQualityCriterion.md`, and three unattributed copies listed by ScoutMisroot) | the wave context rule "every `Report:` trailer path is relative to the lane" (it caught the report path, not the artifact path) | the falsify-wave context repeats the absolute-path rule for artifacts; the L1 misroot sweep before the report checks the fleet root |
| chronology: an amendment written after the receipt it governs | amendment 3 was committed (c808ba07) after the first receipt (5ea4fc44) | amendment 3 disclosed its own order (`order_disclosure`); CriticC2SizingA2's report followed a minute later | amendment 4 (46fb04bd) was committed before the receipt was re-run (5c95c8f1); the earlier receipt stays in history |
| false timestamp repeated | amendment 2 `written_utc` 09:30Z is later than its commit (09:28:44Z), and amendment 3 `written_utc` 09:40Z is later than its commit (09:38:45Z); the same class amendment 1 corrected | CriticC2SizingA2 and ReviewerAmendment2 | errata in amendment 4 and `errata-attempt-2.json`; amendment 4 names only the observed `date -u` output and defers to the commit time |
| axis misfiled: drift declared as a calibration claim | C1 counts instrument-to-auditor anchor drift; the SCORECARD and SKILL statements were true when written (counter `stale 0` at e876b95 and ed1cc3a, stale from 92063cf) (`a2-falsify/advice/CriticC1AxisFit.md` §1-4; `a2-build/advice/CriticC1Calibration.md`) | the prompt's claim-sizing rule for calibration claims (`.ufo/prompts/kama-round-25.md:347-348`), applied by two non-author critics; the preregistration did not apply it | before declaring a calibration claim, name the SCORECARD or SHONEN statement that is false at the before revision (lesson §C1 result). Not yet shown able to fail: no later round has applied it |

## Routed defects from the round-24 spot-check

1. Original clauses and the seven original-unmet cells: untouched. No r24
   file was edited.
2. Stale registered mutation semantics: the M-series anchors are repaired by
   C1. PM08 wording: `SKILL.md` registry row and the cutover paragraph no
   longer say "static-only" or "settled"; PM08 stays manual, review-only,
   unexecuted, uncredited. The historical `LOG.md:1501-1502` line keeps its
   bytes; the round-25 LOG entry carries the correction. An M02 kill is not
   PM08 credit.
3. Locator correction. The round-24 report `.ufo/reports/round-24/kama.md:16`
   names the ScribeLesson and ConnSources evidence without an on-disk
   locator. The exact locations, under `.ufo/waves/round-24/`, are
   `fixes/docs/ScribeLesson/` (six files, including
   `supersession-index.json`) and `falsify/out/ConnSources/verify.txt`
   (7052 bytes). `sources/fixes/docs/ScribeLesson/` and
   `build/out/ConnSources/verify.txt` do not exist. The round-24 report bytes
   stay unchanged (`a2-build/advice/ScribeLocatorErrata.md`). The
   prepared-versus-landed append lineage stays unresolved, as routed.
4. Native-role, chronology, scope and changed-input qualifications: kept;
   this round makes no no-effects, backend-identity or full-isolation claim.
5. H2 (Git >=2.45) stays operator-owned; the L0 line is open and is routed
   around, not re-asked.

## C1 result

Registered command (preregistration.json C1.command) over committed bytes:
`registered 27 stale 2` at efe58e96 → `registered 28 stale 0 []` at
1fc41e34. Repair: M11 literal spans the wrapped call (same element, killed
by F20); M17 keeps its round-23 line in `lookup()`; the second call site in
`bare_objects()` is new id M33 (killed by F13). Supporting full run at
1fc41e34: exit 0, pristine passed, 28 mutants, 26 killed, survivors M17 and
M20 (`final/c1/`), replicated by a seat (`a2-build/advice/ExecC1TipReplicate.md`).

Axis fit is not established. The wave-1 critic CriticC1Calibration and the
wave-2 critic CriticC1AxisFit both hold that the command counts
instrument-to-auditor anchor mismatches, not SCORECARD or SHONEN
self-assessment mismatches. The wave-2 critic showed that the self-assessment
was true when written (counter `stale 0` at e876b95 and ed1cc3a; stale from
92063cf on), so the defect is drift (freshness), not overreach. The author
accepts this and does not relabel the axis after landing: C1 is repair
evidence, and the round does not show the lowest-axis obligation. The full
instrument run (not the counting command) stops on reaching M11, after
M01-M10 have run, and emits no JSON.

Lesson for later rounds: under the 2026-10-22 claim-sizing rule, a
calibration claim needs a statement in SCORECARD or SHONEN that is false
against the repo at the before revision. Check that before declaring the
axis.

## C2 result

`python3 .ufo/waves/round-25/count-c2.py` over the committed receipt
(5c95c8f1): `registered 14 observed 14 bound True missing []`. Knowledge:
`corpus/knowledge/context-capacity.md`. What is new against the admitted
corpus: the KV pool as a second number with its log evidence; fit raising
an unset split context (X1 pool 8192, 2048 per slot; X3 with fit off: 2048,
512), which corrects the round-20 wave rule for that one case; both
concurrent requests failing on a shared pool (L1) while the same requests
pass on separate streams (L2) or one after the other (L3); and identical
endpoint values for different pools (K1 and X2). Per-slot values on K1-K8,
X2 and X3 replicate round 20.

## What the critics changed

- CriticLearningBarA2: replication labels per cell; supersession scoped to
  round-20 wave evidence (`SrcServerNctx.md:6`, `nctx-crosscheck.py:41`);
  E09 from the attempt-1 record named; endpoint claim limited to the three
  endpoints.
- CriticLoadCells: the limit is the pool total (each L1 request failed at
  1025 tokens), not a full per-slot context; L2 changes size and layout
  together; L3 covers only `cache_prompt` false; per-request times,
  truncation and error type are now recorded.
- SentinelFixtureScope: a cell counts only after its child is reaped and its
  port is closed; the exit code requires every port closed.
- ConnectorSiblingOverlap: `SKILL.md:188-190` now states the `--kv-unified`
  premise of the 16384 example; kengaku's production capture is cited as
  other-build evidence in the entry.

## Erratum — round 26 (2026-10-23): §Mistakes row 2

Routed by `round-25-verifier-spotcheck.md` defect 2 (F2). The Fix cell's
clause "the instrument docstring and SKILL registry row now say M17 survives
and why" is false for the SKILL registry row. At lane commit
`a23c0e042114016a909eb15173aa6df74b5b7eb0`, `SKILL.md` mentions M17 only at
line 883 ("M17 follows the current local-store spelling") and line 889 (the
M17 re-anchor and M33 as its second call site); neither says M17 survives.
Correct attribution: the full-run receipt `final/c1/c1-tip-mutants.json` lists
M17 and M20 as survivors; the SKILL registry row records the re-anchor and the
second call site only. Draft and check: round-26 wave-1 scribe
`.ufo/waves/round-26/w1-build/out/ScribeRoutedRepairs/Defect2-KQ36-and-lesson.md`.
