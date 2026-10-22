# CritOriginalWithdrawn — round 24 fresh falsification (critic)

Target: the original C1 unknown-from-metadata requirement (`preregistration.json`
expected_after[3]) versus the prospective amendment. A literal original reading
that was not met must never be read as passed or admitted. Find any summary that
hides original red cells, or that conflates a behavior repair with admission of
the original claim.

**Verdict: PARTIAL.**

- **Holds:** the headline. No committed summary relabels the original
  unknown-citation expectation as passed. LOG, SCORECARD, SKILL, README,
  knowledge and lesson all say "withdrawn/not-achieved". The 44 snapshot cells
  are cell-identical in the committed manifest. No numeric score is promoted.
- **Falsified:** completeness of that disclosure. Nine original-reading red cells
  exist at `2e254a1`, but the summaries name only one rule and give no count or
  identities:
  - two rows are withdrawn outside the amendment's declared supersession scope;
  - one open row hides an original red cell behind a rationale that does not
    match its fixture;
  - one retained-grid row is presented as a "migration";
  - the runner's `withdrawn_original_failures` bucket labels live failures as
    "withdrawn". GridOracle's filed "32 withdrawn original-view failures"
    inherits this false provenance.

## Snapshot and identity (observed)

- Scratch clone: `/fast/scratch/hyaku/kama-r24/falsify/CritOriginalWithdrawn/repo`
  (`--no-hardlinks`), detached at `2e254a1763a9c08aa07fc53081287f506c447d84`.
  `git rev-parse HEAD` printed that exact OID. Git version: 2.56.0.
- Pinned bytes match the assignment:
  - auditor `tools/report-landing-audit.py`: `ea51bc35b71ac09f…dd220`
  - runner `promisor-grid.py`: `b034e1596746d312…5cefa`
  - manifest: `d86b7bea9c49c3d2…14cd1`
  - mutants: `6e0b9d62db9fe27f…1bb60a2`
  - population: `612b0a74…2ed88`
  - frozen auditor `0df800e:tools/report-landing-audit.py`: `da5041a8…65af1`
- Oracle files (sha256):
  - `preregistration.json`: `6dde0d72…44c`
  - `oracle-amendment-1.json`: `930b087a…82f`
  - `oracle-snapshot-before-inspection.json`: `1f5a4699…b0e`
  - `oracle-supplement-2.json`: `4600a8c3…368`
- The tools and tests are unchanged between `ed1cc3a` (the SCORECARD integration
  pin) and `2e254a1`: `git diff --stat ed1cc3a HEAD -- tools tests` printed
  nothing.
- Snapshot versus manifest: all 44 case objects are equal. The only top-level
  difference is `derived_from.oracle_supplement`. PG46–48 are added.

## Bounded measurements (each a benign offline grid subset; TMPDIR under scratch)

All commands were run in the scratch repo with
`TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/CritOriginalWithdrawn/tmp`.
Outputs are in `.ufo/waves/round-24/falsify/out/CritOriginalWithdrawn/`.

### m1: integrated auditor against the amended rows and controls (exit 0)

Command: `promisor-grid.py --arm current --current tools/report-landing-audit.py --json`
with cases PG13, PG22, PG23, PG24, PG25, PG28, PG30, PG34, PG37, PG41.
Output: `m1-current-amended-subset.json`, sha256 `0575672e…1bd2`.

| case | exit | original exit | met_original | met_amended |
|---|---|---|---|---|
| PG22 | 1 | 2 | False | True |
| PG23 | 1 | 2 | False | True |
| PG24 | 1 | 2 | False | True |
| PG28 | 0 | 2 | False | True |
| PG30 | 0 | 2 | False | True |
| PG34 | 2 | 1 | False | True |
| PG41 | 1 | 2 | False | True |
| PG13, PG25, PG37 | 2, 1, 1 | same as observed | True | True |

Summary fields: `violations=0`, and `withdrawn_original_failures` lists exactly
PG22, PG23, PG24, PG28, PG30, PG34 and PG41. However, `amended_view_met=0` and
`amended_view_total=10`, while `amended_view_unmet=[]`. That is self-contradictory
(see F5).

### m2: frozen auditor run as `--current` (exit 1)

Cases: PG01, PG13, PG23. Output: `m2-frozen-as-current.json`, sha256 `92b3476b…d5cc`.

All three rows are live violations (`met_amended=False`), and all three are also
listed in `withdrawn_original_failures`. PG01 and PG13 have no amendment. Their
original view equals their live view, so nothing was withdrawn for them.

### m3: frozen auditor as `--current` on the seven amended rows (exit 1)

Output: `m3-frozen-as-current-amended7.json`, sha256 `2f347057…34e8`.

At the r23 base, only 6 of the 7 amended rows fail the original view: PG22,
PG23, PG24, PG28, PG30 and PG41. PG34 exits 1, which meets its original view.

### m4: open row PG40 against the integrated auditor (exit 0)

Output: `m4-open-PG40.json`, sha256 `2e101f85…c2c1`.

- PG40 observed exit 1; its original view expects exit 2.
- The row reports `met_original=False` and `met_amended=True`. The second value
  is vacuous: every field of PG40's amended view is null.
- The row appears in no graded count and no withdrawn list.
- `rg PG40` over LOG.md, SCORECARD.md, SKILL.md and corpus/ finds no matches.

No full suite was rerun. F06 is execution-bearing (a `core.sshCommand` marker
fixture), so it was checked statically only. PM08 was not touched.

## Findings (counterexample → evidence → impacted axes → smallest safe correction)

### F1 — The runner's "withdrawn" bucket is not bound to the amendment; it is false provenance

- **Counterexample:** in m2, live failures on PG01 and PG13 (no amendment) are
  reported as `withdrawn_original_failures`.
- **Evidence:** `tests/report-audit/promisor-grid.py:1029-1030` computes
  `withdrawn = [... if r["arm"] == "current" and r["met_original"] is False]`.
  The docstring at `:14-16, :27-28` says original failures are withdrawn
  "for the rows the L1 amendment changes".
- **Filed consequence:** `build/advice/GridOracle.md:8,151` reports that the r23
  base shows "32 withdrawn original-view failures". By m3, at most 6 of those 32
  are amended rows. At least 26 are live, never-withdrawn original-view red cells
  (for example PG01–PG06, whose original view is exit 0) that carry the
  "withdrawn" label.
- **Scope of impact:** in a fully green current run the bucket happens to equal
  the amended-and-differing rows, as m1 shows. The mislabel appears on any
  non-green run, including mutation and diagnostic runs.
- **Impacted axes:** calibration (false provenance of red cells) and evidence
  honesty.
- **Smallest safe correction:**
  1. Restrict the bucket to rows whose `expectation["amended"] != expectation["original"]`.
  2. Report original-view failures on unamended rows separately, for example as
     `original_view_live_failures`. They are already counted as violations.
  3. Append a correction to GridOracle's "32 withdrawn" line rather than
     rewriting it.

### F2 — PG28 and PG34 are withdrawn outside the amendment's declared supersession scope; the summaries hide them

- **The declared scope:** `oracle-amendment-1.json` sets
  `supersedes_expectation_only = "preregistration.json expected_after[3]"` and
  says "Other preregistered expected outcomes remain separately measured."
  GridOracle.md:74 repeats "supersedes expectation [3] only".
- **PG28** (unhydrated blobless lane):
  - Original view: exit 2, reason `unavailable`.
  - Its policy reference is an "L1 crosswalk", not expected_after[3]. The case
    involves no citation at all.
  - The original exit 2 is the literal reading of expected_after[5]: "content
    completeness ... determine the outcome".
  - The withdrawal is actually authorized by amendment `prospective_expected[4]`
    and authority bullet 4, not by the declared supersession field.
- **PG34** (plain store, missing cited blob):
  - Original view: exit 1, the r23 plain verdict. It is the preregistered
    "non-promisor no-harm" twin from the preregistration's `measurement` field.
  - The live view changes it to exit 2 by applying the token-scoped rule to
    every store.
  - This is a non-promisor verdict change. It is disclosed only in the manifest
    notes and GridOracle.md:97/322. No round summary reports it as a changed
    plain-store verdict or as a withdrawn no-harm cell.
  - `corpus/knowledge/error-is-not-a-verdict.md` says "The same rule applies
    with or without promisor metadata", which states the policy, not the
    regression from exit 1 to exit 2.
- **Misattribution:** the manifest's `calibration[0]` places PG28 and PG34
  under the expected_after[3] question.
- **Summaries that hide these cells:** SCORECARD.md §Round24, LOG.md
  §Prospective oracle correction, the knowledge §Round24 section and the lesson
  mistakes table each speak only of "the blanket unknown-citation expectation".
- **Tradeoff for the judge (not a defect I can resolve):** PG34 is arguably
  better calibrated, because a referenced-but-missing blob is not proved
  absent. But it converts a plain-repository finding into a refusal, against
  the preregistered non-promisor no-harm measurement. An alternative literal
  reading of expected_after[2] ("an unavailable required ... blob" gives exit 2)
  would make exit 2 the original expectation. Either way, the original-view
  cell is red and must be named.
- **Impacted axes:** calibration and operability (a non-promisor verdict changed).
- **Smallest safe correction:** an append-only scope erratum, for example a
  separate `oracle-amendment-1-scope-note.json` plus a LOG/lesson append, that:
  1. extends the declared supersession to the expected_after[5]
     content-completeness reading (PG28) and the non-promisor no-harm twin
     (PG34);
  2. lists PG34 explicitly as a non-promisor behavior change for the outside
     judge.

  Do not edit the frozen manifest.

### F3 — Open row PG40 hides an original red cell, and its rationale does not match its fixture

- **Rationale versus fixture:**
  - The manifest's `open_rows[0].not_graded_because` says that "closure over all
    refs would find the token as a hole (exit 2)".
  - But builder `c_missing_cited_unselected_branch_promisor`
    (`promisor-grid.py:675-677`) cites `FAKE` (`fake_landed=True`, `:378-379`)
    and drops an *uncited* side-branch blob.
  - The token is fabricated and can never be in any missing set. The fixture is
    PG31 plus a fabricated citation: the same shape as PG22 and PG41 (a
    promisor lane, an unrelated blob hole and a fabricated citation).
  - Under the live rule its verdict is unambiguously exit 1, which m4 observes.
- **What is hidden:**
  - The original view (exit 2, from the expected_after[3] literal) is red.
  - It is neither graded nor listed as withdrawn, and it is absent from every
    summary.
  - The JSON shows `met_amended: true` on the strength of an all-null view.
- **The coverage gap behind it:** the contested scenario its name describes (a
  cited object that is missing and referenced only from an unselected branch)
  has no fixture. The lesson's "dangling commit" limitation (lines 138-142) is
  related but not the same.
- **Impacted axes:** calibration and coverage honesty.
- **Smallest safe correction:**
  1. Through an appended supplement (not an edit to the frozen 44), record that
     PG40 as built is a fabricated-token row whose original view is withdrawn
     and whose live expectation is exit 1.
  2. If the unselected-branch question is wanted, register a new open row that
     actually cites the dropped side-branch blob.
  3. Emit open rows' `met_original=False` into a reported list, and never report
     `met_amended` for an all-null view.

### F4 — The retained r23 grid's F06 is an original red cell presented as a "migration"

- **Evidence (static):**
  - `repo-state-grid.py` `f_lazy_fetch` (`:274-289`) builds a promisor lane
    (`extensions.partialClone`, `remote.origin.promisor`) that cites a
    fabricated `abcdef…` token.
  - The literal reading of expected_after[3] gives exit 2. ConnPlan.md:259
    derived exactly that before the amendment.
  - At `2e254a1` the row is re-pinned from exit 2 to exit 1 with the findings
    `landed-unresolved` and `unresolved-full-hash` (diff `:653`). It now passes
    the retained grid as "met".
- **How the summaries present it:**
  - LOG.md:1495: "Migrated the legacy grid's F06 local-missing outcome".
  - The `repo-state-grid.py` docstring: "gives F06 the ordinary local
    missing-citation findings".
  - Neither says that the original-reading F06 cell is withdrawn and not
    achieved. The repaired behavior is presented as the retained grid's
    expectation, with no original view kept beside it.
- **Observed versus inferred:** the exit-1 observation is ConnClosure V4's
  (`build/advice/ConnClosure.md:179`). I did not execute F06.
- **Impacted axes:** calibration (an original cell is masked by re-pinning).
- **Smallest safe correction:** an appended note in LOG/lesson listing F06 as
  an expected_after[3] original cell that is withdrawn and not achieved. The
  retained-grid expectation can stay as the amended pin.

### F5 — The current arm's summary score is structurally zero

- **Evidence:** at `promisor-grid.py:1031-1042`, `baseline` filters
  `arm == "frozen"`. On the current arm, therefore:
  - `amended_view_met` is always 0;
  - `amended_view_unmet` is always `[]`.
- **Counterexample:** in m1 every row met the amended view, yet the summary
  reads `0/10` met and `unmet=[]`.
- **Why it matters:** SKILL.md:850 says "`amended_view_met` supplies the
  comparable target score". Quoting the current arm's field under-reports the
  repair; quoting the frozen arm's field (16/47 per GridOracle.md:316-322)
  reports the baseline. Neither is the candidate's score. This does not inflate
  the original view, but it is an ambiguous summary authority.
- **Smallest safe correction:** compute per arm. Use `met_amended` for current
  rows and `met_amended_frozen` for frozen rows.

## Enumerated original-reading red cells at `2e254a1` (what a summary must show)

| cell | original | observed / live | withdrawn under | disclosed in summaries? |
|---|---|---|---|---|
| PG22, PG23, PG24, PG30, PG41 | 2 | 1, 1, 1, 0, 1 (m1) | expected_after[3] | only as "the unknown-citation rule", no IDs or count |
| PG28 | 2 (`unavailable`) | 0 (m1) | not [3]; actually amendment prospective_expected[4] | no |
| PG34 (plain) | 1 | 2 (m1) | not [3]; non-promisor no-harm twin changed | no (manifest notes and GridOracle only) |
| PG40 (open) | 2 | 1 (m4) | expected_after[3], but filed as "open, contested" | no |
| F06 (r23 grid) | 2 (expected_after[3] literal) | 1 per ConnClosure V4 (inferred) | expected_after[3] | described as a "migration" |

## Not found (holds)

- Nothing in LOG, SCORECARD, SKILL, README, QUALITY, knowledge, the lesson, or
  any build advice I grepped claims the original view passed. I also found no
  "7/7", "44/44" or "47/47" stated as an original-view score.
- The 44 snapshot cells are unchanged in the manifest.
- The supplement is disclosed as an addition, not a rewrite.

## Observed versus inferred

- **Observed by me:** every hash above; the m1–m4 exits and fields; the
  runner's source lines; the PG40 builder; F06's builder (static source only);
  the doc greps.
- **Inferred:**
  - F06's current exit 1 (taken from ConnClosure V4; not executed, because it is
    execution-bearing);
  - that 26 or more of GridOracle's 32 are live rather than withdrawn (32 minus
    the measured 6 from m3, assuming GridOracle's count of 32 is accurate);
  - PG40's live expectation of exit 1 under the amendment (derived by me from
    the token-scoped rule and the identical PG22 shape).

## Files written

- `.ufo/waves/round-24/falsify/advice/CritOriginalWithdrawn.md` (this file)
- `.ufo/waves/round-24/falsify/out/CritOriginalWithdrawn/`:
  - JSON outputs `m1-current-amended-subset.json`, `m2-frozen-as-current.json`,
    `m3-frozen-as-current-amended7.json`, `m4-open-PG40.json`
  - their stderr files `m1.stderr` through `m4.stderr`, all empty

## Unverified

- The full 47-cell committed-tree run and the final source census are owned by
  L1.
- I did not re-execute F06.
- I did not recount GridOracle's 32.
- No tools were installed or updated.
- Production, `.jj`, fleet and config were not modified. The scratch is under
  `/fast/scratch/hyaku/kama-r24/falsify/CritOriginalWithdrawn`.

## Addendum — lazy-fetch fixture hazard (IRC from KamaR23-2.CaseFleetBlobless)

The reported hazard is real but does not affect these measurements. It applies
to manual probes of a fixture kept with `--keep` whose `remote.origin.url` still
points at a reachable `file://` origin: a probe without `--no-lazy-fetch`
silently hydrates the missing blobs, and the auditor can then return a false
clean exit 0.

- None of m1–m4 used `--keep`. The grid root was removed after each run, and
  every JSON output has `grid_root` unset.
- I made no manual git probe of any fixture. All premise and inventory checks
  were the grid's own helpers, which run with `--no-lazy-fetch`.
- Every m1 and m4 row reports `objects_acquired = {lane: [], fleet: []}`. That
  includes PG28, the unhydrated blobless lane whose exit 0 is cited in F2, so
  its exit 0 is not a hydrated false clean.
- Any future manual inspection of a kept blobless fixture must pass
  `--no-lazy-fetch` on every git call.
