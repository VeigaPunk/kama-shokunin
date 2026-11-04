# kama round 79 — lesson

author: kama L1 (integration; drafted by SC03Lesson seat, landed by the L1)

Lane: kama. Round 79, ONE v1 build-and-attack wave of **14 seats** (4 executor, 3 scribe,
2 scout, 1 connector, 1 reviewer, 2 critic, 1 mutation-tester; attack 4/14 = 29 %), under
`ufo-wave-policy.json` (band 8–16). Base `ee53f1a25eab93a8ab55bbb877e49e2e731df535`;
freeze `331037039c30909aa2163b2d1de22a7964f90420` (the plan and the C1 counter); the sealed
revision C1 grades is `7a3cd98243b69fcbee0cc9e31878782bd8459320` (round 78's tip).

## The round's three claims

- **C1 — calibration** (lowest assigned axis, 7). `python3 tools/round79-selfrecord-round78.py
  --repo .` must print `SELFRECORD_R78 claims=6 mismatches=0 corrected=2 unbacked=0`, exit 0:
  each of the six facts the round-78 self-record declares re-derives at the sealed revision,
  or is answered by exactly one committed correction block at that revision whose stated new
  value re-derives at the tip. Pre-freeze: `claims=6 stale=2 corrected=0`, exit 1 (F5, F6).
- **C2 — operability.** `python3 tools/pre-report-gate.py --selftest` must print
  `PRE_REPORT_SELFTEST pass=26 fail=0`, and a scored run at the tip must print
  `PRE_REPORT round=79 arms=10 failed=0 uncommitted=0`: the tenth arm
  `round78-instruments` runs the three round-78 instruments' selftests, each required to end
  with its own summary, failing closed on a red, malformed or absent module.
- **C3 — coverage.** `python3 tools/round79-unregistered-census.py --repo .` must print
  `UNREGISTERED_CENSUS port=<p> unregistered=1 governed=1 class_missing=0`, exit 0: the probe's
  `listeners` census classifies a serving listener by whether a registry row declares its port,
  so an ungoverned serving listener is a named class instead of a manual observation.

## Gate

- **Admitted — llama.cpp router `GET /models`.** URL
  https://raw.githubusercontent.com/ggml-org/llama.cpp/39febd2adb947b70da35e95f9351b3bf58ad170a/tools/server/README.md,
  opened **2026-11-04** (HTTP 200, 135608 bytes, sha256 `8fd5abde2fb52de3b30f30a170631d4c0d92febecc8da44d0541e48b132b35c6`;
  the same bytes as the live listener's build tree `~/src/llama.cpp/tools/server/README.md`).
  Located quote, **14 words**, at line 2227 (§Router mode, `GET /models`, note 1): "If a model
  is not running, it will be added or updated according to the source" — the router lists
  unloaded models and marks each with a `status.value` (loaded/loading/unloaded/sleeping), so a
  model list is an inventory, never a loaded-model or readiness claim. Scope: the census class's
  meaning only; not `/v1/models` identity normalisation (S001/S016/S526 ground) and not model
  quality. Receipt: `.ufo/waves/round-79/measured/before/source-router-models.out`.
  *Correction (appended 2026-11-04; the filed paragraph above is not rewritten):* the quote is
  **16 words**, not 14; it sits under note 1's `?reload=1` refresh sentence of
  `### GET /models: List available models` (heading line 2197), and the anchor's "Router mode" is
  the region label — no heading carries that name. S553's scope is docs of the list's *semantics*
  at `39febd2a`, not S479's router model-listing code (`get_router_models`' capacity key) at the
  older pin and not S037's router-mode `is_ready` ordering. Pin divergence recorded, not
  reconciled: `registry/engine-pins.tsv` pins b11755 (`704366d76`), kengaku's S178 pins b7200
  (`ab49f094…`), this row pins `39febd2a`; only `engine-pins.tsv` feeds `pin-watch.py`.
  Independent re-open: `.ufo/waves/round-79/w1/SCT02Source/source-check.md`.
- **Rejected — llama.cpp INI presets.** URL
  https://raw.githubusercontent.com/ggml-org/llama.cpp/39febd2adb947b70da35e95f9351b3bf58ad170a/docs/preset.md,
  opened 2026-11-04 (HTTP 200, 4090 bytes, sha256 `3e6643541e12ff3dfee2a23c23a57357403bf4500beced780f010eaebbbdfe13`).
  Why rejected: the round's class reads the model list only; the probe parses no preset file,
  so a row would scope a configuration format no claim reads (KQ/Tier is not the question —
  ground is). **Flip:** a round that grades preset-inherited parameters on a lane-owned fixture
  reopens it.
- **Own-work class.** The round's own-work instrument set is the class C2 wires
  (`round78-selfrecord-round77`, `round78-append-registers`, `round78-live-reconcile` as the
  gate's tenth arm) plus the C3 counter and the probe's census class; no own-work row is
  appended for them (CORPUS rule 4 — expansion is knowledge, not rows).

## Mistakes

1. **`tip-names-an-ancestor`** — a record calls an ancestor revision "the tip" while claiming a
   green gate there.
   *Evidence pointer:* `SCORECARD.md` §Round 78 §Gate and tip state reads "The tip accounting
   is the round-77 counter, which is green at `rev=22cce544`"; the sealed tip is
   `7a3cd98243b69fcbee0cc9e31878782bd8459320` and `22cce544` is an ancestor
   (`.ufo/waves/round-79/measured/before/c1-enum.out`: F5 `is-tip:false`). Round 78's own
   non-author closure routed the class as R78V1
   (`corpus/lessons/round-78-verifier-spotcheck.md` §1 defect 1).
   *Captured-by:* C1's **F5** fact (`tip-accounting=rev:<r>/is-tip:<bool>`), added this round;
   at the round-78 base no rule tested a record's "tip" word against the sealed tip — the
   round-78 spot-check found it by reading.
   *Fix:* the correction block below names the revision as an ancestor; F5 re-derives it at
   the tip, so a future record that calls an ancestor "the tip" turns the counter red.

2. **`prose-only-evidence`** — a record says a run happened and points at the lesson, while the
   run's output is nowhere in committed bytes.
   *Evidence pointer:* the same §Round 78 §Freeze divergences item 4 says "the pre-correction
   tip run and the corrected tip run are both in the lesson"; at the sealed revision no blob
   under `.ufo/waves/round-78/` carries `mismatches=1` (F6 observed `absent`), which is the
   round-78 closure's R78V2. This round reproduced the run from the pre-fix module at
   `fa65ce2c` and committed the output
   (`.ufo/waves/round-79/measured/v2/c1-pre-correction.out`:
   `SELFRECORD_R77 claims=6 mismatches=1 corrected=4 unbacked=0`, `FINDING mismatch F2`,
   `EXIT=1`).
   *Captured-by:* C1's **F6** fact (a receipt, not prose, must exist at the sealed revision);
   CORPUS's "a fix is shown able to fail before it counts" states the duty but had no runnable
   check in this lane.
   *Fix:* the correction below points F6 at the committed receipt, and the counter re-derives
   that the receipt's bytes carry `mismatches=1` at the tip.

3. **`self-accepted-post-introduction-deletion`** — a round tried to book its own in-place
   deletions into the two ledgers that exist for *historical* events.
   *Evidence pointer:* this round added 38 `in-place-edit` rows to
   `registry/append-only-accepted.tsv` and 76 rows to `registry/append-only-disclosures.tsv` for
   commits made this round; both ledgers refuse a commit at or after their own introduction
   (`APPEND_ACCEPTED_FINDING post-introduction`, `bad_rows=38`; `audit bad_disclosures=76`). The
   rows were reverted and the ledger restored; the register restore is itself one unaccountable
   event (`APPEND_ACCEPTED unaccepted=1` on it, receipt
   `.ufo/waves/round-79/measured/after/c2-gate.out`).
   *Captured-by:* the ledgers' own temporal cutoffs (`SN01Register` in
   `tools/round75-append-accepted.py:69-72`, and the audit's disclosure verdict in
   `tools/append-only-audit.py` "names a commit at or after the ledger's introduction").
   *Fix:* an in-place deletion made in round N is either restored (its bytes held in the file, as
   the head-sections appendix does) or left as a disclosed red event; it is never booked into a
   ledger that predates it. Routed to round 80 as a QUALITY criterion (KQ131) and as a hard
   pre-commit check.

## Corrections

Two value-bound blocks, one per stale fact, in the frozen shape (`at` names the sealed
revision; each `old` is the plan's declared value string).

- `corrected F5` old=`tip-accounting=rev:22cce544/is-tip:true` new=`tip-accounting=rev:22cce544/is-tip:false` at=`7a3cd98243b69fcbee0cc9e31878782bd8459320` date=`2026-11-04`
  At the sealed revision the record's §Gate and tip state sentence calls `rev=22cce544` "the tip
  accounting"; the sealed tip is `7a3cd98243b69fcbee0cc9e31878782bd8459320` and `22cce544` is an
  ancestor of it (`git merge-base --is-ancestor` exit 0, `rev-parse 22cce544^{commit}` != sealed).
  The new value states the relation the bytes show; the record's own bytes are not rewritten.
- `corrected F6` old=`c1-pre-correction-run=committed` new=`c1-pre-correction-run=committed:.ufo/waves/round-79/measured/v2/c1-pre-correction.out` at=`7a3cd98243b69fcbee0cc9e31878782bd8459320` date=`2026-11-04`
  At the sealed revision the record asserts the pre-correction tip run is "in the lesson" while
  no committed blob under `.ufo/waves/round-78/` carries `mismatches=1`; the new value names the
  reproduction committed this round (pre-fix module and worktree at `fa65ce2c` in a scratch
  shared clone, `SELFRECORD_R77 claims=6 mismatches=1 corrected=4 unbacked=0`, `EXIT=1`), and the
  counter re-derives the receipt's bytes at the tip.

## Attack dispositions

The wave settled with **11 of 14 seats returning output** (EX02GateArm, EX03ProbeClass and
EX04CensusCounter returned empty and are recorded dead; the L1 built those three items itself and
their bytes are the committed ones the mutation seat graded). Integrated findings:

- **MT01Mutation (5 mutants, 5 killed, 0 survived)** — the probe's `registered` class (three
  mutants: always-yes, column omitted, registry column 3 instead of 4) and the gate's arm 10 (two
  mutants: first instrument only, nonzero exit passes) are each caught by their owning detector.
  Its graded snapshot hashes equal the committed bytes (`tools/kama-probe.sh`
  `0943fb46…`, `tools/round79-unregistered-census.py` `25daa989…`, `tools/pre-report-gate.py`
  `9b2ff3b4…`, committed at `5ac1a8d`). Evidence:
  `.ufo/waves/round-79/w1/MT01Mutation/mutants.md`.
- **EX01C1Facts (independent harness)** — re-derived all six facts without importing the counter;
  agreement on every value string, including the two stale ones (F5, F6). Evidence:
  `.ufo/waves/round-79/w1/EX01C1Facts/rederive.out`.
- **SCT01Recon (read-only)** — hand-derived all six facts from committed bytes; agrees on F5/F6
  stale and on the four fresh facts; names no vacuous fact. Evidence:
  `.ufo/waves/round-79/w1/SCT01Recon/facts.md`.
- **SCT02Source + SC01Sources + SC02Knowledge + SC03Lesson (scribes/scout)** — opened the router
  README (HTTP 200, 135608 bytes, sha256 `8fd5abde…`), confirmed the quote is 16 words at line
  2227 under note 1's `?reload=1` sentence, and flagged that the anchor's "Router mode" is a
  region label, not a heading name; the lesson's Gate carries the correction and the S479/S037
  distinction. Evidence: `.ufo/waves/round-79/w1/SCT02Source/source-check.md`,
  `w1/SC01Sources/sources-append.md`.
- **CN01Connector (overlap scan)** — no lane composes another's instrument selftests; the
  `unregistered` token collides with mado's `CHECK96` vocabulary for a different population, and
  kengaku's S178 reads the same host listener for eval identity — both reported, neither absorbed.
  Evidence: `.ufo/waves/round-79/w1/CN01Connector/overlap.md`.
- **RV01Reviewer, CR01Critic, CR02Critic** — ran while the tree was mid-flight (the C1/C3 counters
  and the arm were not yet landed) and reported that in-flight state; none certifies a claim, and
  no attack seat's self-assessment is treated as a closure.
