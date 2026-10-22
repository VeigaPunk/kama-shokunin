# Round-24 falsification — SCORECARD / preregistration / current-claim record

Seat: `DocScorecardAuthority` (leaf member; no subagent dispatch).
Base observed: `2e254a1763a9c08aa07fc53081287f506c447d84`
("round-24: land completed 64-seat build evidence and explicitly carry residual
closure debt").
Scratch clone (detached, `--no-hardlinks`):
`/fast/scratch/hyaku/kama-r24/falsify/DocScorecardAuthority`.
Lane production `/home/vgpnk/Projects/shokunin/kama-shokunin` was read only;
no production file was edited. No suite, no grid run, no mutation probe, no
network, PM08 not executed. No tool was installed (nothing in this slice needed
one; `git`, `python3`, `sha256sum` from the base image were used as-is).

## Axes named (godspeed)

1. **Record honesty** — does any round-24 record claim the withdrawn original
   oracle passed, or claim a final measurement that has not happened?
2. **Numeric non-promotion** — did any axis score, capability row, saturation
   line or census number move at r24?
3. **Prior-r23 history fidelity** — do the r23 numbers and pointers recorded in
   `SCORECARD.md` §Round 23 match the filed r23 evidence at the pinned revision?
4. **Oracle integrity** — is the shipped 47-cell manifest really *original44
   unchanged* + 3 independent opaque cells, with the strong `names_any_of`
   grader intact and the four pinned digests matching?
5. **Final-record spec** — are the exact required final fields derivable now,
   so the post-falsification measurement record cannot self-certify?

## Verdicts

| Axis | Verdict |
|---|---|
| 1 Record honesty | **HOLDS** |
| 2 Numeric non-promotion | **HOLDS** |
| 3 Prior-r23 history fidelity | **PARTIAL** (F1 over-broad parity claim, F3 ambiguous T01 wording) |
| 4 Oracle integrity | **HOLDS** |
| 5 Final-record spec | **PARTIAL** (F2 field-semantics trap in the grid summary) |

---

## F1 — LOW/MEDIUM — `SCORECARD.md:1167` over-states the frozen-vs-current parity scope

`SCORECARD.md:1167` (round-23 row "Existing selftest / historical ledger, no
harm") reads: *"rounds 10–22 ledger and `--no-errata` byte-identical to frozen
(exit 0 / exit 1, 9 raw defects all corrected)"*, pointing at recipe line
`nh-history-parity`.

Observed:

- `.ufo/waves/round-23/final/nh-history-parity.stdout` is **144 bytes / 4
  lines**: `10-21 current 0 frozen 0 same`, `10-21 --no-errata …`,
  `10-22 …`, `10-22 --no-errata …`.
- `.ufo/waves/round-23/recipe.json:168` entry `nh-history-parity` loops
  `for r in ('10-21','10-22')` against the frozen `4fe9339f` auditor blob —
  rounds **10-21 and 10-22 only**.
- Rounds 10–20 are covered only by the **current-arm** historical run:
  `.ufo/waves/round-23/final/audit-historical-ledger.stdout` (rounds list
  10–22, reports 13, required_commits 54, defects 9, corrected 9,
  uncorrected 0, status clean) and `audit-historical-raw.stdout`
  (`--no-errata`: uncorrected 9, status failed). Neither stdout contains a
  frozen arm.

So the literal breadth "rounds 10–22 … byte-identical to frozen" is not
supported for rounds 10–20; the byte-identity claim holds for 10-21/10-22
only. The same over-statement is repeated in build advice
`.ufo/waves/round-24/build/advice/ConnNoHarm.md:254` (*"covers rounds 10–22"*).

Minimal correction (append-only; filed r23 bytes must not be rewritten —
`corpus/lessons/round-24.md:51` records the append-only rule): append one
sentence to the `## Round24` section of `SCORECARD.md` (or a new
`### Erratum — round-23 parity scope` subsection), e.g.:

> "The round-23 parity artifact covers rounds 10-21/10-22 only
> (`nh-history-parity`); rounds 10-20 rest on the current-arm historical
> ledger run (`--rounds 10-22`), which is not a frozen-vs-current comparison."

## F2 — MEDIUM — the grid's current-arm `amended_view_met` is 0 by construction, and `SKILL.md:850` presents it as "the comparable target score"

`tests/report-audit/promisor-grid.py:1031-1039` computes

```
baseline = [r for r in graded if r["arm"] == "frozen" and r["met_amended_frozen"]]
"amended_view_met": len(baseline), "amended_view_total": len(graded)
```

inside the **per-arm** loop (`for arm in arms:` … `rows` is arm-scoped), so in
the **current** arm block `baseline` is empty: `amended_view_met` is **0** and
`amended_view_unmet` is `[]` by construction, whatever the current arm did.

Observed in a committed artifact:
`.ufo/waves/round-24/build/out/ConnClosure/pgrid-allroots.json` →
`arms.current = {"graded": 5, "violations": 0, "amended_view_met": 0,
"amended_view_total": 5, "amended_view_unmet": []}` (and
`expectations_sha256 d86b7bea…`, `population_size 47`).

`SKILL.md:850` states: *"Frozen-history reproduction is not improvement:
`amended_view_met` supplies the comparable target score."* Read against the
code, that field is the **frozen-arm baseline** (how many of the 47 the r23
base already satisfies), and in the current arm it is 0/47. A final record
that quotes `amended_view_met` from the current arm would publish a spurious
"0 of 47 met"; the honest current-arm score is `graded − violations`
(current arm: graded 47, violations 0 → 47/47; `promisor-grid.py:851`
`obs["met"] = obs["met_amended"]` for the current arm).

Minimal correction (report only — production not edited):

- **(a) record-level (mandatory for the final record):** express the current
  score as `graded − violations` with `violating_cases: []`; cite the
  frozen-arm `amended_view_met` / `amended_view_total` / `amended_view_unmet`
  only as the historical baseline, never as the current score.
- **(b) optional minimal source fix** in `promisor-grid.py:1031-1039`: compute
  the met count from the arm's own rows (`met_amended` for the current arm,
  `met_amended_frozen` for the frozen arm) so the field is non-degenerate in
  both blocks. This is a reporting field only; it changes no expectation,
  no exit class and no graded row.

## F3 — LOW — `SCORECARD.md:1173-1174` and `corpus/lessons/round-23.md:207` keep the T01 wording the r24 lesson flags as a stale premise

`SCORECARD.md` §Round 23: *"Operability is **traded, not unchanged**, on two
declared states: a complete blobless partial clone (T01) and a paired promisor
pack without promisor config (F23) now refuse (exit 2) where frozen gave a
verdict"*. `corpus/lessons/round-24.md:53` records the correction: *"T01
clones with checkout (hydrates its single blob); F23 uses `--no-checkout` and
asserts a real reachable blob is absent … never repin T01 to a refused ungraded
trade by assuming all blobless clones are incomplete"*.

SKILL.md:816-820 already disambiguates ("T01 is a checked-out single-blob clone
whose checkout hydrates that blob; F23 is a different, `--no-checkout` fixture
whose cited blob is genuinely unavailable"), but `SCORECARD.md` does not, and
the phrase "a complete blobless partial clone" is still readable as an
*incomplete* clone. The r24 `## Round24` section already supersedes the r23
admission and quality-improved readings, so this is precision, not a wrong
claim.

Minimal correction: in the `## Round24` section append one clause —
*"T01 is content-complete (checkout hydrates its single blob); only F23 is
genuinely incomplete"* — or cross-reference `SKILL.md:816`.

## F4 — LOW — the round-24 `SCORECARD.md` section omits the source-ledger state landed in the same round

Commit `f1e755e` ("…scorecard authority") landed `S105` (explicit superseding
rejection record for S095's cross-API inference), the `corpus/SOURCES.md`
reconciliation and `corpus/lessons/round-24.md`, and added the `## Round24`
section — but that section says nothing about the source ledger. The ledger
state is: **105 rows** (`grep -c '^| S[0-9]' corpus/SOURCES.md` → 105),
S095 retained as rejected with its immutable teaches cell, S105 filed as the
explicit rejection record, only mutable `used-by` cells changed
(`corpus/lessons/round-24.md` §"Gate consumer reconciliation"). The source
census is L1-owned **after** this stage, so the final record must carry it;
the round-24 declaration currently does not mention it at all.

Minimal correction: append one sentence to `## Round24` naming the ledger
state (105 rows, S105 superseding rejection record, used-by-only mutation) and
marking the census verification as pending L1 after the falsification stage.

---

## Verified holds (with the exact command and observed value)

**H1 — no numeric promotion, no new capability (axis 2).**
`git diff 0df800e 2e254a1 -- SCORECARD.md` → **+25 lines appended at EOF
only** (new `## Round24` section). The §Axes table (rows last changed round
3 / round-10 erratum), the §Capabilities table and the §Saturation line are
untouched. `SCORECARD.md:1212-1213`: *"No numeric promotion or new
capability."* `LOG.md` (r24) and `corpus/lessons/round-24.md:7-8` repeat it.
Commit `2e254a1` landed, besides the 64-seat build evidence, only
`.ufo/waves/round-24/sources-before.json` and `corpus/lessons/round-24.md`
(+39) — no score, no capability row.

**H2 — the original oracle is nowhere claimed passed (axis 1).**
Every record states the opposite:

- `tests/report-audit/promisor-grid-expectations.json` →
  `views.original`: *"Withdrawn prospectively for the rows the amendment
  changes; reported separately and never counted as achieved"*;
  `amendment.original_view_verdict`: *"withdrawn prospectively, not counted as
  achieved"*.
- `tests/report-audit/promisor-grid.py:14-18` (docstring): *"original … never
  counted as achieved"*; *"The original view's failures are reported as
  withdrawn, not counted as violations."* Grading code `:830`
  `live = expect.get("amended", expect["original"])` (amended is the graded
  view), `:851` `obs["met"]` uses `met_amended` for the current arm, `:1043`
  reports `withdrawn_original_failures` separately.
- `SKILL.md:850` *"The original withdrawn view is reported separately."*
- `SCORECARD.md:1200-1202` *"withdrawn/not-achieved, not retroactively
  passed."*
- `LOG.md` §round 24 *"explicitly withdrawn/not-achieved, not retroactively
  passed"*; `corpus/lessons/round-24.md:46` same.

**H3 — final measurements are explicitly deferred (axis 1).**
`SCORECARD.md:1207-1211`: *"Integration is pinned at `ed1cc3a…`; … Final
measurements are separate committed-tree evidence after fresh falsification;
this declaration does not claim that those runs have occurred."* No
`.ufo/waves/round-24/final/` exists in the pinned tree (verified:
`ls .ufo/waves/round-24/final` → *No such file or directory*). `LOG.md`
§round 24: *"Main measurement follows the fresh falsification stage.
Preliminary seat results remain attributed to their exact candidate/harness
hashes, not substituted for the final committed-tree run."*

**H4 — r23 history numbers in `SCORECARD.md` match the filed r23 evidence
(axis 3, the parts that do hold).**
`python3` read of `.ufo/waves/round-23/final/grid-both.json`:
`arms.current {faults 26, faults_met 26, contracts 4, contracts_met 4,
controls 13, controls_met 13, tracebacks 0, timeouts 0, violations 0,
commands_executed 0}`; `arms.frozen {faults_met 0/26, contracts_met 1/4,
tracebacks 9, timeouts 2, commands_executed 3, violations 29}` →
`SCORECARD.md:1163` *"0/26 → 26/26; tracebacks 9 → 0, executed programs 3 → 0,
timeouts 2 → 0"* ✓. `.ufo/waves/round-23/final/mutants.json` →
`killed 30, mutants 31, surviving ["M20-log-sha-shape"]` ✓
`SCORECARD.md:1166` *"30/31 killed … survivor M20 defensive-only"* (the
"defensive-only" qualifier is asserted in the row text and in
`corpus/lessons/round-23.md:120`; the JSON itself only names the survivor —
see unverified items). `.ufo/waves/round-23/final/selftest.out` →
`selftest cases=50 failed=0`, `rc=0` ✓ *"50/50 → 50/50"*. `grid-both.json`
`auditor_sha256.current = da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1`
and `population_sha256 = f29fab8d9af1d02de7f6fa4c7b39b2307113d3716fd4b11cffdd0cd65d55364a`
match `SCORECARD.md:1156-1157` (`da5041a8…5af1`, `f29fab8d…364a`) ✓. The
audit code is unchanged between the r23 measurement tree and the r24 frozen
base (`0df800e`), because the r24 expectations pin the same auditor digest
`da5041a8…5af1` — the two histories are comparable.

**H5 — oracle integrity (axis 4).**
`python3` diff of the frozen snapshot against the shipped manifest:

- `.ufo/waves/round-24/oracle-snapshot-before-inspection.json` → **44 cases**,
  sha256 `1f5a469989b24b6b321b6b9a39533dad00f7e4daba80dca5f1321e888b142b0e`.
- `tests/report-audit/promisor-grid-expectations.json` → **47 cases**, sha256
  `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1`
  (identical to the digest pinned in the build receipt
  `.ufo/waves/round-24/build/out/GridOracle/RECEIPT.md`).
- Field-by-field comparison over all 9 fields of the 44 shared cases:
  **0 changed fields**; the 3 additions are exactly `PG46-opaque-tree-hides-cited-blob`,
  `PG47-opaque-tree-with-unresolved-fabricated-token`,
  `PG48-opaque-unused-tree-no-unresolved-token` — i.e. *original44 unchanged +
  3 independent opaque cells* ✓.
- The strong grader is intact: `promisor-grid.py:828` grades tokens by
  `names_any_of`; no path-expression relaxation was introduced (L1 declined it,
  `corpus/lessons/round-24.md:44-46`).
- All four digests in the assignment brief match the pinned tree:
  `tools/report-landing-audit.py` `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220`;
  `tests/report-audit/promisor-grid.py` `b034e1596746d312989b7894c0757b67859df19a476a01ccd95076424135cefa`;
  manifest `d86b7bea…`; `tests/report-audit/promisor-mutants.py`
  `6e0b9d62db9fe27f6c14c6e16ce239023f699142193adff5291e4374a1bb60a2`.

---

## Exact falsifiable claims (each with the command that would falsify it)

| # | Claim | Falsified if | Status at base |
|---|---|---|---|
| C1 | The r24 `SCORECARD.md` change is append-only with no numeric promotion | `git diff 0df800e 2e254a1 -- SCORECARD.md` touches §Axes/§Capabilities/§Saturation | **holds** (EOF append only, +25) |
| C2 | No record claims the original (withdrawn) oracle passed | any of SCORECARD/LOG/lesson/SKILL/expectations/grid docstring ties "passed/achieved" to the original view | **holds** |
| C3 | No record claims the final measurement has occurred | any r24 record asserts a committed-tree measurement result | **holds** (no `.ufo/waves/round-24/final/`) |
| C4 | The r23 grid numbers quoted in SCORECARD are the filed ones | `grid-both.json` disagrees with §Round 23 | **holds** |
| C5 | The r23 isolation number 30/31 with survivor M20 is the filed one | `mutants.json` differs | **holds** |
| C6 | The r23 selftest 50/50 rc0 is the filed one | `selftest.out` differs | **holds** |
| C7 | The r23 historical parity covers rounds 10–22 vs frozen | `nh-history-parity.stdout` / `recipe.json` cover only 10-21/10-22 | **FALSIFIED as stated** (F1) |
| C8 | The 9 raw historical defects are all corrected | `audit-historical-raw.stdout` uncorrected ≠ 9 or ledger uncorrected ≠ 0 | **holds** (9 → 0, 9 errata rows) |
| C9 | The shipped manifest = frozen44 unchanged + 3 disclosed opaque cells | any of the 44 differs, or the additions are not exactly PG46/47/48 | **holds** (0 changed fields) |
| C10 | The grader is the strong `names_any_of`, no path relaxation | path-expression grading present in `promisor-grid.py` | **holds** (token-based, `:828`) |
| C11 | The current-arm `amended_view_met` is a usable current score | current-arm block reports 0 by construction | **FALSIFIED** (F2) |
| C12 | The r24 declaration records the source-ledger state landed at `f1e755e` | `## Round24` mentions rows/S105/used-by reconciliation | **FALSIFIED** (F4) |

## Exact required final fields (the post-falsification measurement record)

The final measurement is intentionally deferred to L1 after this stage; it must
not self-certify. Required fields, in the order they should appear:

- **R1 Pinned measurement point** — the full 40-hex commit measured, with a
  clean tree (`git status --porcelain` empty). A working-tree run is not
  evidence.
- **R2 Pinned digests** — auditor `ea51bc35…`, runner `b034e159…`, manifest
  `d86b7bea…`, mutation probe `6e0b9d62…`; plus the grid-reported
  `expectations_sha256` (must equal `d86b7bea…`), `population_sha256`
  (expected `612b0a74f3eebaa9074bdde8ecd8f194f55ebaf9a35ab2b975fddbff8dd2ed88`),
  `population_size` (47), and `auditor_sha256.current` (must equal the
  committed `tools/report-landing-audit.py` digest).
- **R3 Grid command and exit** — `python3 tests/report-audit/promisor-grid.py
  --arm both --json` with **exit 0** (every graded row of every selected arm
  met its live expectation); record the exit code literally.
- **R4 Per-arm block, current arm** — `graded` (47), `violations` (0),
  `violating_cases` (empty), `tracebacks`/`timeouts`/`harness_leaks` (0),
  `twin_mismatch` (empty), `twin_pairs_compared`, `twin_pairs_in_manifest`.
  **The current score must be `graded − violations` (47/47), not
  `amended_view_met`** (F2).
- **R5 Frozen-arm baseline, as history only** — `amended_view_met`,
  `amended_view_total`, `amended_view_unmet` (the r23 base against the live
  policy) and the frozen-arm `violations` against the *frozen* expectation
  (red by design). Never presented as the target or as improvement.
- **R6 The original view, reported separately and never as achieved** —
  `withdrawn_original_failures` per arm, an explicit sentence *"the original
  registration view is withdrawn/not-achieved; no original-view row is
  counted as passed"*, and the byte-identity statement that the 44 shipped
  cells equal the frozen snapshot (snapshot sha256 `1f5a4699…`; per-case diff
  = 0 changed fields) with PG46/PG47/PG48 named as the only additions.
- **R7 Non-promisor no-harm** — the retained r23 grid results re-stated with
  their digests (`da5041a8…`, population `f29fab8d…`, frozen `4fe9339f…`) and
  the numbers 26/26, 4/4, 13/13, tracebacks 9→0, executed 3→0, timeouts 2→0,
  plus the explicit parity scope (F1: 10-21/10-22 vs frozen; rounds 10–20
  current-arm only) and the historical ledger figures (13 reports, 54
  required commits, 9 raw defects all corrected → uncorrected 0).
- **R8 Selftest** — `python3 tools/report-landing-audit.py --selftest` →
  `cases=50 failed=0`, `rc=0` (plus the grid's own `--selftest`).
- **R9 Mutation sensitivity** — `python3 tests/report-audit/promisor-mutants.py
  --json`: inventory evaluated, kills and survivors listed (no universal-green
  claim), exit semantics 0/2, pristine failures and uncompiled/unapplied
  mutants credited nothing, **PM08 static-only and never executed**, and the
  isolation experiment's 27 retained literals + 4 retired IDs (no reuse).
- **R10 Git floor** — "Git ≥ 2.45 remains an inherited prerequisite (auditor
  `GIT_TIMEOUT = 20`, `tools/report-landing-audit.py:153`); R23-H2 stays an
  open operator decision; no older-Git restoration is claimed."
- **R11 Source ledger** — row count (105), S105 as the explicit superseding
  rejection record, S095's immutable teaches cell retained, only mutable
  `used-by` cells changed, and the **source-census verification result with
  its command and exit** (L1-owned after this stage; F4).
- **R12 No numeric promotion** — an explicit statement that calibration stays
  7→7, no capability row was added, the saturation line is unchanged, and no
  axes-table or capability-table row was created for round 24.
- **R13 Residual debt carried** — the named open rows (near-variant classes,
  alternates/gitfile, ambiguity overwrite, errata CR/FIFO, memory ceilings,
  sibling gates) and the declared 47-cell limitation (refs-only traversal vs
  all present-object roots for a dangling commit naming a missing cited blob)
  must appear as still-open, not closed by the final record.
- **R14 Provenance** — every number cited to a committed evidence path under
  `.ufo/waves/round-24/final/`, plus the falsification-wave report ids
  consumed.
- **R15 Non-claim guard** — the record must not contain "the original oracle
  passed", must not attach "passed" to any original-view row, and must not
  assert a final measurement before R1-R4 exist.
- **R16 Probe-hygiene note for the final run** (cross-seat hazard, reported by
  `KamaR23-2.CaseFleetBlobless`): a blobless fixture built by
  `tests/report-audit/promisor-grid.py` keeps `remote.origin.url` pointing at
  the reachable local `file://` origin, so any git probe **without**
  `--no-lazy-fetch` materialises the missing blobs and silently destroys the
  premise (reproduced A/B: blob absent → exit 2 content-derived refusal; blob
  materialised by one stray `git cat-file -e HEAD:<path>` → false exit 0
  "clean"). Every probe the final record cites — including any manual
  inspection of a `--keep`ed fixture — must use `--no-lazy-fetch`, and the
  final record must state which probe discipline was used.

## Cross-seat note

`KamaR23-2.CaseFleetBlobless` reported the fixture lazy-fetch hazard above;
it is recorded here because it directly affects R3-R4 (a final measurement run
that inspects a `--keep`ed blobless fixture without `--no-lazy-fetch` can
manufacture a false clean). No source defect is claimed by that seat and none
is claimed here.

## Observed vs inferred

- **Observed** (direct file reads / digests / counts): every digest, case
  count, field-diff count, grid summary number, recipe range, stdout byte
  count, section diff, and the 0-changed-field comparison.
- **Inferred** (not executed): that `amended_view_met` will read 0 in the
  final current-arm block — derived from the code path
  (`promisor-grid.py:1031-1039` inside a per-arm loop) and *confirmed
  observationally* in the committed preliminary artifact
  `build/out/ConnClosure/pgrid-allroots.json` (current arm
  `amended_view_met: 0`, `amended_view_total: 5`, `violations: 0`), so this is
  observed behaviour of the same code path, but not from a full 47-cell run.
- **Inferred**: that the r23 row's "defensive-only" characterisation of M20 is
  supported — the retained JSON names the survivor but does not itself assert
  the classification (the assertion lives in `corpus/lessons/round-23.md:120`).

## Files written

- `.ufo/waves/round-24/falsify/advice/DocScorecardAuthority.md` (this report)
- `.ufo/waves/round-24/falsify/out/DocScorecardAuthority/checks-transcript.md`
  (verbatim command/output transcript backing every number above)

Nothing else was written; no production file was modified; the scratch clone at
`/fast/scratch/hyaku/kama-r24/falsify/DocScorecardAuthority` is detached at
`2e254a1` with a clean `git status --porcelain`.

## Unverified items / verification gaps

1. No grid, mutant, selftest or historical-parity command was executed in this
   slice (read-only assignment, no full suite). All r24 behaviour claims are
   therefore **static**; the 47-cell pass/fail is unmeasured here and belongs
   to the post-falsification L1 measurement.
2. The current arm's `amended_view_met` degeneracy (F2) was observed on a
   5-row preliminary artifact from the build stage with a **candidate** auditor
   digest (`e9790358…`), not on the pinned `ea51bc35…` tool; the code path is
   identical, but no full-47 run at the pinned tree was performed.
3. Whether M20 is "defensive-only" is asserted in the r23 lesson, not derived
   from `mutants.json`; the retained JSON shows only that M20 survived.
4. The outside-closure MANIFEST (`rounds[428]`) is not in this repository; the
   Round24 section's summary of it ("rejected-harmed, calibration improved but
   operability/quality harmed") was checked only against `LOG.md:1413-1416`
   and `corpus/lessons/round-24.md:55-60`, which agree with it.
5. Sibling falsify seats' findings were not read; no cross-check of their
   claims was performed.
6. `git` version on this host was not recorded (the Git ≥ 2.45 floor is an
   inherited open question, R23-H2; this slice does not settle it).

## Residual risk

- If the final record is drafted from the SCORECARD/LOG wording alone, it can
  inherit F1 (parity over-claim), F2 (0/47 `amended_view_met`) and F4 (missing
  source-ledger state) and thereby over-credit or mis-state the round. The
  required-field list above is the mitigation.
- F2 is the only item that could turn a passing run into a *misreported* one;
  it is a reporting-semantics defect, not a behavioural defect.
- The r23 filed bytes stay immutable by rule, so F1/F3 must be corrected by
  appending in the round-24 section, never by editing the r23 section.

Report: .ufo/waves/round-24/falsify/advice/DocScorecardAuthority.md
