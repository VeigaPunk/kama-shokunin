VERDICT: partial — expansion and KQ23/R7-respawn points hold; the round-18 deliverable at HEAD has no trend-verdicts section anywhere, SCORECARD ends on an unfulfilled "appended after execution" promise, and both counting-command exits remain own-fault exit=2 at HEAD (the repaired counters never ran on real inputs).

Seat: KamaR18.TrendVerdicts (leaf critic, round-18 FALSIFY). Lane root
`/home/vgpnk/Projects/shokunin/kama-shokunin` @ `1c325b2e58fcfdc6761f645b44cedfb1d65243e6`
(master). All paths below relative to the lane root. No clone was needed: every
check was a read over committed bytes or JSON inspection; no runtime experiment
was assigned or run, no port bound, no process spawned.

# Attack item decomposed

Four sub-claims: (a) one verdict each on expansion/quality/discernment, no
scalar; (b) the new procfs entry is uncovered ground; (c) KQ23 is grounded in
outside R2; (d) no lane seat substitutes an independent non-author sample;
plus the standing "correct round-17 outside discernment improved" record.

# Finding 1 — Medium: no round-18 trend verdicts exist in any deliverable; the conformance debt is real and unrecorded

The report contract requires "one verdict each for `expansion`, `quality`, and
`discernment` (`improved`, `harmed`, `unchanged`, `unprovable-but-better`), with
evidence; no scalar" (`/home/vgpnk/Projects/shokunin/templates/round-prompt.md:116-117`).
Skipping the section is a logged minimum-content conformance defect (`:122-125`),
not a silent omission.

- `SCORECARD.md:737-767` (§Round 18) ends at line 767. Rounds 3, 5, 10-17 all
  carry an explicit trend/verdict line (e.g. round-17 `SCORECARD.md:698-702`;
  LOG.md:398, 603, 692, 736, 841, 910, 986). Round 18 has none.
- `LOG.md:1051-1093` (both round-18 blocks) names the corrected outside
  round-17 discernment verdict at `:1079-1082` but declares no round-18
  expansion/quality/discernment verdicts.
- `corpus/lessons/round-18.md` contains no trend verdict; its only discernment
  statement is the scope guard at `:102` (wave-2 attacks are not an outside
  review) — true but not a verdict.
- Fleet report `.ufo/reports/round-18/` has no `kama.md` (only
  kaidoku/kasegi/kengaku/kotodama/mado/tabi/tameshi/tsukuroi). The verdicts may
  still be coming with the report, but at the pushed lane master the
  deliverable the trend section would stand beside is final — the SCORECARD
  round-18 block was committed at `c6dc46f` and never amended by `1c325b2`.

Impacted axes: calibration (SCORECARD promises not kept, see Finding 2) and
discernment (the round's own trend judgment is absent, so nothing exists for
an outside sampler to confirm or reject).

Smallest safe correction: record expansion/quality/discernment verdicts with
evidence at report finalization and append the promised measured-results
paragraph to §Round 18; do not let the absence be read as deliberate silence.

# Finding 2 — Medium: SCORECARD's "appended after execution" promise is stale and contradicted by LOG; official counting exits at HEAD are still 2 (own-fault), not passes

- `SCORECARD.md:767`: "Measured results, measured commit and exact commands are
  appended after execution." Nothing follows. LOG.md's second block (added by
  the same HEAD commit `1c325b2`) instead says "Final claim measurements await
  corrected counting invocations" (`LOG.md:1093`). The two committed
  statements disagree; the stale one sits in the authoritative scorecard.
- `runs/commands.json`: `c1-measure` exit 2 vs expected 0; `c2-survivors` exit
  2 vs expected 0 (30 of 32 commands met declared exits).
- `runs/c1-measure.json` proves the committed artifact is the **old** counter's
  output: `inputs.measure.sha256` = `55b26b3b…`, while `c1/measure.py` at HEAD
  is `a9577ed889…` (the bucket-source repair). The repaired counter's own
  selftest is 38/38 in the owner clone (`build/advice/C1Measure.md:51`), but
  no official rerun on real inputs exists.
- `runs/c1-measure.stderr`: "fault: before: misclassified=1 but 0 row(s)
  classified misclassified" — the pre-repair seam, matching
  `runs/c1-measure.json` `.runs.before.doc.controls[id=k16]`:
  `classification=rejected-targeted, bucket=misclassified, expected=not-evaluated`.
- `runs/c2-survivors.exit` = `exit=2`; `.stderr` shows family-b `FC-target` and
  `FC-f6cache` "main inconclusive" despite selftest kills — the independent-arm
  own-fault, matching `build/advice/C2Survivors.md`'s reported fix. The
  `2 (of 15 named)` after-count is thus still produced by the broken arm.

Honesty check (fails the strongest counterattack in the lane's favour): the
lesson does NOT launder these into passes — `lessons/round-18.md:161-167`
labels both "could-not-evaluate, not quietly called pass", routes them to the
counter owners, and records raw arms (`accepted-bad 5→0`, `good-rejected 1→0`,
`misclassified 1→0`, `uncontrolled 0→0`; C2: six H kills, three handled faults,
two append-only kills, refused 82, one FC kill, two FC inconclusives). That is
correct KQ24-shaped classification. The residual defect is narrower: the
scorecard still advertises unmeasured claims, and `runs/` mixes one
pre-repair artifact (`inputs.measure.sha256` mismatch proves it) with
post-repair code, so a reader cannot tell which arm results the final verdicts
will rest on until a rerun lands.

Impacted axis: calibration (self-assessment vs observed repo state);
operability is unaffected — the counters are measurement instruments, not the
capability.

Smallest safe correction: rerun the two counting commands against the repaired
counters, append the SCORECARD measured-results paragraph, and add the trend
verdicts; keep both failed artifacts per the lesson's own no-overwrite rule.

# Finding 3 — Confirmed: the procfs/ownership entry is genuinely uncovered ground, correctly scoped as expansion under C1

- `corpus/knowledge/loopback-listener-ownership.md` is a new file this round
  (64 added lines, `git diff e75cf680..HEAD`). Its content is mechanism the
  corpus previously lacked: the procfs LISTEN-row→inode→child-fd ownership
  join and tcp6 host-word encoding (`:9-14`, `:36-44`). Prior corpus coverage
  is adjacent, not overlapping: `listener-census.md` inode mentions are
  filesystem inodes (`stat -c '%i'`, `:36`, `:284`), not socket inodes;
  `endpoint-identity.md:174-175` only flags that F1 was *partial* for host-side
  socket ownership — i.e. the ground was documented as unheld.
- `corpus/README.md:261` adds the coverage-map row marked "newly held
  mechanism" and `:265` records "Frontier advanced" while keeping the open
  list (other engines, router/sleep, K05, consumers).
- `SCORECARD.md:763-765` correctly classifies it as "coverage expansion under
  C1, not a fourth claim" with coverage score unchanged at 9 — no score
  inflation. Limits are honest (`:54-59`: little-endian only, one namespace,
  non-atomic reads, deprecated-interface caveat).
- Sources S048-S050 are correctly layered: kernel code for the print format,
  RFC 4291 for address semantics, S049 explicitly limited away from
  byte-order authority (`SOURCES.md` new rows; `lessons/round-18.md` Gate).

Residual caveat (not a kill): the row's "owns the port" semantics depend on
the ProbeTcp6Format experiments being reproducible, and `endpoint-identity.md`
itself is not amended to note that its F1 partial-coverage statement is now
backed by a mechanism entry — an appended cross-reference would close the loop.
Impacted axes: none harmed.

# Finding 4 — Confirmed: KQ23 is grounded in outside R2 and demonstrated fail-capable, but its quality credit remains author-validated

- R2's exact requirement: "Add a KQ citing round-17 M8, or state why not"
  (`corpus/lessons/round-17-verifier-spotcheck.md:229-230`). KQ23 does cite M8
  (`corpus/QUALITY.md:132` motivating-lesson cell) and the lesson records it
  under M1 "mined round-17 M8 … outside R2" (`lessons/round-18.md:86`).
- Fail-capability is exercised, not asserted: the KQ23 row itself demands
  "a positive control and a targeted reset-omission rejection, not a
  reject-everything rule" and the application shows all three — S043 reject,
  S047 necessary-condition admit, reset-omission mutant reject
  (`QUALITY.md:132`; `lessons/round-18.md:74-78`;
  `build/advice/RevKQ23FailCapable.md:93-102` — S043 fails A3/A4/A5, S047
  admits on A1-A5 with the A6 limit, mutant C1 killed on exactly A4).
- The deeper evidence that the criterion is not hindsight-fitted:
  `RevKQ23FailCapable.md:104-108` shows the pins containing `running = true`
  at 279 existed at the same commit (`54a2926`) that wrote the S043 admit —
  possessing bytes did not catch M8, so the criterion targets accounting, not
  possession (matches `lessons/round-18.md:67-69`).
- The wording defect the reviewer caught in the first Gate draft (necessary →
  sufficiency drift, `RevKQ23FailCapable.md:149-166` B1) was corrected in the
  committed S047 row and the lesson's Gate line 41 now says "necessary
  ordering condition". B2's overstatement in
  `knowledge/llamacpp-loading-lifecycle.md:214-215` got an appended round-18
  correction (`:230-236`), preserving frozen bytes per KQ11/KQ14.
- Honest limit kept: `QUALITY.md`'s section header for round 18 still says
  "outside round-17 R2/R4" correctly — but the criterion was refined through
  author-dispatched review iterations; an outside applier has not yet run it.
  That supports quality-improved-at-best, never discernment-improved for
  round 18 — consistent with the lane's own guard (see Finding 5).

# Finding 5 — Confirmed: the lane does not substitute its own seats for the non-author sample; one boundary risk remains

- `LOG.md:1081-1082`: "Round-18 author/seat checks do not themselves satisfy
  the independent non-author spot-check duty." `lessons/round-18.md:101-102`:
  wave-2 attacks "must not be confused with an outside non-author review."
  `SCORECARD.md` claims no discernment move for round 18 — the only
  discernment sentence (`:739-741`) cites the round-17 outside verdict.
- The round-17 gap is also being closed structurally: R7e's seven dead seats
  (including `TrendVerdicts` itself, `round-17-verifier-spotcheck.md:255-258`)
  are respawned in this wave — `falsify/assignments.json` contains
  `C1Admission`, `C2Admission`/`SourcedSupport` equivalents,
  `Separability`/`NoHarm`, `MistakesFailCapable`, and this seat — exactly the
  reissue `RevSpotcheckMap.md:19` demanded ("not covered" → now covered).
  These remain lane-dispatched, satisfying R7e as undone-work, not as outside
  review — the lane says so itself.
- Round-17 outside discernment "improved" is correctly recorded:
  `SCORECARD.md:739-741` and `LOG.md:1079-1082` supersede the author's
  pending/unchanged reading and cite `round-17-verifier-spotcheck.md:217-221`,
  which judges improved on 2/2 standing admits + 3/3 rejects with the S043
  error caught and mined, not netted out.
- Boundary risk for the outside reviewer to watch: `QUALITY.md`'s criteria are
  demonstrated against the lane's own rows by lane-dispatched seats. If the
  eventual report reads KQ23's self-demonstration as discernment evidence for
  round 18, that is the exact substitution the lane disclaims. Nothing at HEAD
  does this; the risk is in the unwritten verdicts (Finding 1).

# Verdict synthesis (advice for L1/outside reviewer; canonical judge decides)

| Trend | Evidence-supported verdict | Basis |
|---|---|---|
| expansion | improved | New `loopback-listener-ownership.md` on genuinely uncovered mechanism ground; README frontier row; bounded to C1, no capability/score inflation (Finding 3). |
| quality | improved | KQ23/KQ24 landed with positive+negative controls against outside-routed defects; S047 Gate row repaired; overstatements corrected by appended text (Findings 4, B2 fix). Two stale/contradictory SCORECARD-LOG statements and a missing trend section are calibration nicks, not quality reversals (Findings 1-2). |
| discernment | unchanged for round 18; round-17's outside "improved" correctly carried forward | No non-author sample exists for round 18; all wave-2 seats are lane-dispatched and the lane says so (Finding 5). |
| scalar | none | All score deltas are `→` same-value (8→8, 7→7); no score moved. |

Net: nothing at HEAD refutes the two claims' bounded scopes, and the trend
posture is honest where stated. The two defects worth admission-gating are
procedural, not substantive: (1) the promised measured-results append +
trend verdicts must land with the report or the section is an explicit
conformance defect; (2) both counting commands still carry own-fault exit 2
artifacts measured by the pre-repair counter (`inputs.measure.sha256`
mismatch), so claim measurements formally await the corrected reruns the LOG
already admits are pending. Per the assignment's own rule these are
INCONCLUSIVE-as-measurement, not kills — the raw arms are preserved and
reported correctly.

# Commands run (all in the lane repo, read-only)

- `git log --oneline -5`; `git show --stat HEAD`; `git diff e75cf680..HEAD --stat`
  (production diff map; knowledge diff limited to the two named entries +
  SOURCES/QUALITY/SCORECARD/README).
- `cat runs/{c1-measure,c2-survivors,c1-self-mutants,c1-counter-selftest,c2-counter-selftest}.exit`
  → 2, 2, 0, 0, 0.
- `python3` over `runs/commands.json` → 32 commands; c1-measure exit 2 vs
  expected 0; c2-survivors exit 2 vs expected 0; all 30 others at expected.
- `python3` over `runs/c1-measure.json` → `inputs.measure.sha256=55b26b3b…`
  vs working `c1/measure.py` sha256 `a9577ed889…`; before-arm k16 row
  `{classification: rejected-targeted, bucket: misclassified, expected:
  not-evaluated}`; counts accepted_bad 5→0, good_rejected 1→0,
  misclassified 1→0, uncontrolled 0→0.
- `runs/c1-measure.stderr`: "fault: before: misclassified=1 but 0 row(s)
  classified misclassified". `runs/c2-survivors.stderr`: family-a 6/6 H
  killed, FC-target/FC-f6cache "main inconclusive", FC-f0gate killed,
  AO-opened/AO-blank killed, refused-count 82, three crash faults handled,
  "before 15 -> after 2".
- `sha256sum .ufo/waves/round-18/c1/measure.py` = `a9577ed8…`;
  `c2/survivors.py` = `87cad1ca…`.
- `wc -l SCORECARD.md` = 767; `git log -3 -- SCORECARD.md` → last touched
  `c6dc46f`.
- `ls /home/vgpnk/Projects/shokunin/.ufo/reports/round-18/` → no `kama.md`.
- `grep` for `expansion|discernment|Trend` across `corpus/lessons/round-18.md`,
  `LOG.md`, `SCORECARD.md`, `SKILL.md`, `corpus/README.md` → no round-18 trend
  verdicts anywhere.
- `git ls-tree -r HEAD .ufo/waves/round-18` → `RevKQ23FailCapable.md`,
  `RevSpotcheckMap.md`, `ProbeTcp6Format.md` and all build advice are tracked.
- Template contract: `templates/round-prompt.md:116-125` (trend verdicts
  required; absence = logged conformance defect, not a fail marker);
  `AXES.md:20-23` (trend↔axis mapping; discernment ↔ calibration).

# Limits, installs, teardown

- No runtime experiments: this item assigned document/ledger analysis only.
  No server started, no port bound; nothing to tear down. `ss` not needed.
- No official counting command was rerun in the live lane (contract-forbidden);
  the committed `runs/` artifacts are the executed evidence and were inspected
  in place.
- Reads excluded all forbidden paths (no .ufo/interactive-sessions, no
  ~/.omp beyond the standing RULES authorization, no credentials stores).
- Installs/updates: none. No pacman, uv, npm, cargo action taken; host pause
  on pacman respected.
- Scratch: none created; `/tmp/kama-r18-falsify-TrendVerdicts` was never
  needed — all checks were reads over the pushed tree.
- Only file written: this report.
