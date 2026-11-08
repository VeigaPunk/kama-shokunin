# SB01Entry — round 99 knowledge and record text (lane kama)

Seat `SB01Entry`, round 99, wave 1, lane `kama` at `f6e7ccc285e0c1207378f73c394acbfda58bff23`
(the round-99 freeze commit). Leaf member: no subagent dispatch.

## What this seat produced

Four drafts under
`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-99/w1/out/SB01Entry/drafts/`,
plus the receipts that back every number in them:

| Draft file | Content |
|---|---|
| `drafts/knowledge-router-props-autoload.md` | `corpus/knowledge/router-props-autoload.md` — the bare `/props` document (`role`, `max_instances`, `models_autoload`, S624), the default (S625), the three-state rule (on/off/unread), the five cell classes, the verdict/exit rule (`MODEL_UNLOADED` stays), the limits, and the provenance trio (`source:` / `verified-at:` / `recheck:`). |
| `drafts/SKILL-reason-table.md` | The `SKILL.md` change: the new `router-autoload-unread` reason row, the adjusted `router-unloaded` row, the current lines quoted verbatim (`SKILL.md:1862`, `:1867`, `:1868`), the two prose edits that the table change forces (`:1839-1841`, the round-88 decision row at `:1773`), and the operability cost of landing the row. |
| `drafts/lesson-round-99.md` | `corpus/lessons/round-99.md` — `## Gate` (three rows: S624 admit, S625 admit, S626 reject), `## Mistakes` (M1 the wave accounting written from a directory scan instead of `w1-results.json`, class `sampling`, carried-by M3, fix; M2 the r98 census mislabel; M3 the carried r98 M3 placement), plus the routed-defect answers. |
| `drafts/scorecard-log-correction-blocks.md` | The `SCORECARD.md` and `LOG.md` round-99 correction blocks: 12 reported / 0 dead, the 7 attack / 5 non-attack names, the pointers `SCORECARD.md:6431` and `LOG.md:4040`, `EX02BudgetControl` against the `SB01-equivalent` misattribution, `RV03Intent`, the census base/tip groups, and the gate's six failed arms — with the counter grading of these texts and the forgery control. |

Receipts (every command quoted in the drafts, with its real output) are in
`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-99/w1/out/SB01Entry/receipts/`:

| Receipt | What it shows |
|---|---|
| `s624-s626-reopen.txt` | This seat's own re-open of S624/S625/S626 (curl, HTTP 200, byte counts, sha256, UTC fetch time). |
| `w1-results-derivation.out` | seats=12, results=12, dead=[], the derived 7/5 split and each seat's role. |
| `census-base-tip.out` | The two frozen census groups re-derived from `git show <rev>:corpus/SOURCES.md`. |
| `c2-base-mismatch-detail.out` | The C2 counter at the base: `checks=12 mismatches=10 met=False`, exit 1, with each named mismatch. |
| `c2-tree-graded.out` | The drafts graded against the frozen counter (`checks=12 mismatches=0 met=True`), the freeze-commit bytes of the same counter over the same tree (`mismatches=1`, check 8), and the forgery control (`mismatches=2`, exit 1). |
| `c2-own-drafts-graded.out` | This seat's own draft texts graded against the counter (`checks=12 mismatches=0 met=True`) and against the freeze-commit bytes of the same counter (`mismatches=1`, check 8). |
| `c2-own-drafts-mutants.out` | Forgery control on this seat's drafts (`mismatches=2`, exit 1). |
| `c2-check-9-binding.out` | What check 9 binds: renaming a gate arm, and dropping `round-clean` from both blocks, each fire `MISMATCH 9`. |
| `c2-check-10-weakness.out` | What check 10 binds: moving the M3 record out of `## Mistakes` (or deleting it) still grades green. |
| `c1-grader-rerun.out` | The C1 grader at the freeze commit (`met=True`, exit 0) and against the round-98 predecessor at the base (`refused=0 met=False`, exit 1). |
| `c3-candidate-rerun.out` | The C3 counter against the candidate probe: 5 cells, `mismatches=0 base_mismatches=4 flips=4 stable=1 met=True`, exit 0. |
| `reason-rows-at-freeze.out` | The round-90 reason-table counter at the freeze commit (`bound=0 unbound=24 receipt=stale`, exit 1) and the three probe hashes. |
| `reason-rows-after-new-row.out` | What the new `SKILL.md` row does to that counter, in three measured configurations. |
| `s627-no-registry-row.out` | The S627 sources receipt with no `corpus/SOURCES.md` row. |
| `wave-file-census.out` | Which of the plan's measurement-time receipts exist and which do not. |
| `knowledge-draft-diff.out` | The knowledge draft body vs the committed file: exactly two lines differ. |
| `knowledge-body-claims.out` | The draft's two non-quoted body claims (`is_autoload`, `/props?model=` → `proxy_get`) checked against the fetched bytes. |
| `harness-reason-coverage.out` | The verdict-matrix harness rows by family: no cell expects `router-autoload-unread`. |
| `c3-regression-r98.out` | The round-98 19-cell regression on the candidate probe, with what finished and what was cut off. |

## Behaviour this seat verified (the three claims, attacked)

**C1 — operability.** The budget counter's control mode refuses a selected population it did not
run, and the unmodified counter still accepts a complete population. Verified by re-running the
frozen grader, not by reading the receipt:

```
$ python3 tools/round99-control-population.py --repo . --rev f6e7ccc285e0c1207378f73c394acbfda58bff23 \
      --work <scratch> --counter tools/round99-router-budget.py
CONTROL_POP99 counter=tools/round99-router-budget.py drop=W14-900k-nd1 patch_removed=1 selected=6 ran=5 \
  mutant_cells=5 mutant_cells_ok=5 mutant_control_exit=1 mutant_ok=0 refused=1 positive_cells=6 \
  positive_exit=0 positive_ok=1 complete=1 population_shaped=1 met=True \
  counter_sha256=e76c35b449be9a9680af50480a0871317c6ad88a9a87824ec30262c88ad6d246 rev=f6e7ccc2…
exit=0
```

The dropped-cell mutation is refused (`mutant_control_exit=1`, `refused=1`), and the unmutated
counter accepts the complete six-cell population (`positive_exit=0`, `complete=1`) — so the gain is
not a blanket refusal. The do-nothing control also holds: against the round-98 predecessor at the
base the same grader prints `refused=0 … met=False` and exits 1
(`receipts/c1-grader-rerun.out`, section B) — the round-98 counter accepted the mutation, so a
before-measurement exists and kill rule K3 is not met.

**C2 — calibration.** The lane's round-98 records agree with the committed wave evidence on the
twelve enumerated propositions. The counter at the base is red for the right reason — ten named
mismatches, including the six that the correction text has to carry
(`receipts/c2-base-mismatch-detail.out`) — and the drafted correction + lesson text is green
against the same counter (`checks=12 mismatches=0 met=True`, exit 0). The forgery control fails the
same checks (`mismatches=2`, exit 1), so the counter discriminates on the correction's content.

Every number in the drafts was re-derived here, not copied: seats 12 / results 12 / dead 0 from
`.ufo/waves/round-98/w1-results.json`; the 7/5 split from the counter's own role set
(`ATTACK_ROLES` at `tools/round99-record-audit.py:83`), which is where `RV03Intent` (revenger)
enters the attack seven and `CN01Overlap` (connector) leaves it — the round-98 prose had the
connector in the attack list and the revenger missing; the census base/tip groups from
`git show 681c80a4…:corpus/SOURCES.md` (361 rows: A 344, B 11, C 6; mined 324, queued 8,
rejected 29) and `git show 649bb2e9…:corpus/SOURCES.md` (363 rows: A 345, B 11, C 7; mined 325,
queued 8, rejected 30); the six failed arms from the committed gate receipt
(`selfdesc`, `newest-closure`, `round-scope`, `round-clean`, `round75-instruments`,
`round78-instruments` — the round-98 erratum named five, omitting `round-clean`).

**This seat's own draft texts were graded, not just the working-tree ones.** A tree was built from
the freeze commit's `SCORECARD.md` and `LOG.md` plus *this seat's* correction blocks, the freeze
commit's `corpus/lessons/round-98.md` plus *this seat's* lesson body, and the committed round-98
results file and gate receipt; the frozen counter over it prints
`RECORD_AUDIT99 checks=12 mismatches=0 met=True`, exit 0
(`receipts/c2-own-drafts-graded.out`, section A). Mutations on that tree show the checks bind:
forging the correction back to "10 reported, 2 dead" → `mismatches=2`, exit 1
(`receipts/c2-own-drafts-mutants.out`, section A); changing the lesson's census numbers →
`MISMATCH 7`, exit 1 (`receipts/c2-checks-7-10-binding.out`, section C); renaming a gate arm in the
receipt copy, and dropping `round-clean` from both correction blocks → `MISMATCH 9`, exit 1 each
(`receipts/c2-check-9-binding.out`). Only check 10 is weak: see finding 9.

**C3 — depth.** The probe's reason vocabulary separates an unread `/props` autoload flag from an
explicit `models_autoload:false` answer while the verdict stays `MODEL_UNLOADED`. Re-run of the
frozen counter against the candidate probe (`receipts/c3-candidate-rerun.out`): U1 slow, U2
oversize, U3 non-JSON, U4 non-router all read `MODEL_UNLOADED / router-autoload-unread` at the tip
and `router-unloaded` at the base; P1 (explicit off) reads `router-unloaded` at both. `cells=5
mismatches=0 base_mismatches=4 flips=4 stable=1 met=True`, exit 0. The exit code is 2 in every
cell, so the verdict and the exit code are unchanged — only the reason moved.

The regression control the plan names for this claim (K5) also holds on this seat's own run: the
frozen round-98 counter over the candidate probe prints `ROUTER_BUDGET98 cells=19 mismatches=0
positive_mismatches=0 load_cells=19 load_stable=1` and exits 0 at both loads
(`receipts/c3-regression-r98.out`), so the vocabulary change moved no cell expectation in the
19-cell population.

## Findings (file:line, and the command that shows each)

**Reconciliation with amendment 1 (`00394f3b`, landed 12:59 while this seat was drafting).** The L1
committed round-99 amendment 1 after the freeze commit; it supersedes parts of this seat's drafts and
settles one of its findings the other way:

| Draft / finding | Landed state at `00394f3b` |
|---|---|
| `drafts/SKILL-reason-table.md` (a new `router-autoload-unread` row in `## Probe reason codes`) | **Superseded**: the L1 documented the reason in a dedicated `## Round 99 unread-autoload reason` section plus a decision row (`SKILL.md:1773`) and explicitly declined a table row ("a row there cannot bind without editing the round-90 instrument", `SKILL.md:1832-1835`). This seat's §5 measurement is the arithmetic behind that sentence (see finding 1). |
| `drafts/knowledge-router-props-autoload.md` body | **Superseded** by the landed edit (8 cells, S627 admitted, S628 rejected, plain-call control). The draft's own body is still the freeze-commit body, and its `verified-at` fix (finding 2) is now moot in that form. |
| `drafts/lesson-round-99.md` + `drafts/scorecard-log-correction-blocks.md` | **Landed in substance**: `corpus/lessons/round-99.md` (+107 lines) and the SCORECARD/LOG blocks are in `00394f3b`. This seat's versions were graded green against the counter independently (see "Behaviour this seat verified"). |
| Finding 7 (S627 receipt without a registry row) | **Closed by the L1**: S627 is now a `corpus/SOURCES.md` row and the knowledge entry cites `arg.cpp:3682`. |
| Finding 10 (`controls/c3-regression.out` absent) | **Half closed, still open in substance**: the file now exists but is **untracked and carries no summary line** — see finding 2 below. |

Findings that stand, and the ones added after reading the landed commit:

1. **A `router-autoload-unread` row in the `## Probe reason codes` table cannot bind without editing
   the round-90 instrument — the landed decision to decline that row is now backed by numbers.**
   `tools/round90-reason-rows.py` binds every table row to a captured probe answer and exits 1 on
   any unbound row. Measured in a scratch clone (`receipts/reason-rows-after-new-row.out`), three
   configurations: (a) new row + the round-90 receipt as committed → `receipt=stale`, exit 1;
   (b) new row + a receipt re-captured against the candidate probe (24 cells) → `rows=25 bound=24
   unbound=1 additional=1`, **exit 1** — no captured cell produces that reason; (c) new row + one
   added capture cell in `tools/round90-reason-capture.py` + a 25-cell receipt → `rows=25 bound=25
   unbound=0 additional=2`, exit 0. So (a) and (b) are both red, and only (c) — which edits a
   round-90 instrument — is green. Amendment 1 landed the reason in a dedicated section plus a
   decision row instead (`SKILL.md:1773`, `1809-1835`); because `router-autoload-unread` is outside
   the counter's frozen 23-reason population, leaving it out of the table changes neither `missing`
   nor `unbound`. The table is red at the tip regardless, for an unrelated reason: the amendment
   changed `tools/kama-probe.sh`, so the round-90 receipt is stale (`bound=0 unbound=24
   receipt=stale probe_sha256=05ebee88…`, exit 1 at `00394f3b`,
   `receipts/landed-state-vs-drafts.out` section C). If the round-100 re-capture happens and the
   table row is then wanted, this seat's draft §§2/5 is the patch shape and (c) is its cost.

2. **The landed `verified-at` cites `controls/c3-regression.out` for a line that file does not
   contain.** At the freeze commit `corpus/knowledge/router-props-autoload.md:2` quoted
   `ROUTER_BUDGET99 cells=19 mismatches=0` for "the round-98 19-cell budget counter" and named
   `.ufo/waves/round-99/controls/c3-regression.out`, which did not exist. Amendment 1 fixed the
   prefix (`ROUTER_BUDGET98 cells=19 mismatches=0` at the tip) and the file now exists — but it is
   **untracked** and its three lines are a `# command:` line (`--rev 00394f3b … --burners 0`) and a
   two-line note that `--burners 0` makes the second pass a plain re-pass; there is **no**
   `ROUTER_BUDGET98 cells=…` summary line in it
   (`receipts/landed-state-vs-drafts.out` section D). So the citation still has no bytes behind it:
   a reader who opens the named receipt cannot see the quoted line. This seat's own run at default
   `--burners 64` produced it —
   `ROUTER_BUDGET98 cells=19 mismatches=0 positive_mismatches=0 load_cells=19 load_stable=1`, exit 0,
   both passes, `receipts/c3-regression-r98.out` — so the fix is to land that receipt under the
   path, or to run the landed `--burners 0` command to completion and append its output.
   `base_sha256` caveat: the round-98 counter's BASE is `27065a5c…`, not the `439fdb3d` probe
   (`40ab387e…`) the round-99 instruments use — two bases appear across the wave's receipts.

3. **The frozen C2 counter cannot grade the plan's own `--tree` forgery control.** The freeze
   commit's bytes of `tools/round99-record-audit.py` read the two census revisions from the
   materialised tree (`read_bytes_at`, freeze-commit lines 250-257), so over a `--tree` mirror it
   sees the tree's tip `corpus/SOURCES.md` for both revisions and reports
   `MISMATCH 8 census base={…366…} tip={…366…}` (`mismatches=1`, exit 1) — or, over a tree without
   `corpus/SOURCES.md`, `could-not-evaluate: census revision bytes unavailable`, exit 2. The
   working-tree copy carries the fix ("The two census revisions are historical and always come from
   git, also under `--tree`", working-tree `tools/round99-record-audit.py:250-257`) and grades the
   same tree `checks=12 mismatches=0 met=True`. Two consequences for the committer: the plan's C2
   kill rule K1 ("the counter's bytes change after the freeze commit") is met by that fix unless it
   is disclosed as an amendment, and the forgery control named in the plan
   (`controls/c2-forged.out`, "run with `--tree <scratch>`") cannot be produced by the freeze
   commit's bytes at all. Both readings are in `receipts/c2-tree-graded.out` (sections A, B, C, D).

4. **The C2 counter's own docstring says the base prints `mismatches=9`; it prints 10.**
   `git show f6e7ccc2:tools/round99-record-audit.py` line 10: "Before (do-nothing control): at base
   `439fdb3d` the same counter prints `mismatches=9`". The committed control receipt
   `.ufo/waves/round-99/controls/c2-base.out` says `mismatches=10`, the plan says 10, and this
   seat's re-run prints `checks=12 mismatches=10 met=False` (`receipts/c2-base-mismatch-detail.out`).
   The docstring is off by one against its own receipt.

5. **The C1 grader's docstring quotes a predicate line that is not what it prints.** The freeze
   commit's `tools/round99-control-population.py:5-9` says the grader prints
   `… complete=1 met=True`, but the code (`tools/round99-control-population.py:135-139`) prints
   `population_shaped=1` between `complete=1` and `met=True`, and appends `counter_sha256=` and
   `rev=`. The plan quotes the same short form. The receipt (`receipts/c1-grader-rerun.out`) carries
   the real line.

6. **The round-99 census-start receipt has no exit marker and no row count.** The plan cites
   `.ufo/waves/round-99/controls/census-start.out` as "exit 0, 363 rows"; the receipt ends at the
   `kama<TAB>ok<TAB>…/corpus/SOURCES.md` line and carries neither an exit line nor a row count
   (`grep -c rows` = 0), while the round-98 twin
   `.ufo/waves/round-98/controls/census-start.out` ends with an extra `census_exit=0` line. The
   363 figure is re-derivable from the bytes (`git show 439fdb3d:corpus/SOURCES.md` → 363 rows,
   `receipts/census-base-tip.out` shows the r98 base/tip groups) but not from the receipt.

7. **`S627` has a sources receipt but no registry row.** The freeze commit added
   `.ufo/waves/round-99/sources/s627-arg-models-autoload.txt` (llama.cpp `common/arg.cpp` @ b12177,
   sha256 `c69c0e07…`, lines 3676-3684, the `--models-autoload` / `--no-models-autoload` option
   pair), but `corpus/SOURCES.md` has no `S627` row (`grep -c S627` = 0) — the census at the freeze
   commit counts 366 rows and the tier split moves only for S624/S625/S626. The file's URL is the
   same file as the existing S596 row (`common/arg.cpp` @ b12177), so it is a re-open of a pinned
   file, not a new source. Left as a finding, not a decision: the wave plan says three rows were
   opened this round and does not mention S627 (`receipts/s627-no-registry-row.out`).

8. **The `S624`/`S625` registry rows name `SKILL.md` in `used-by`, but `SKILL.md` cites neither.**
   `corpus/SOURCES.md:379-380` carry `used-by=SKILL.md, corpus/knowledge/router-props-autoload.md`;
   `grep -n "S624\|S625" SKILL.md` finds no hit at the freeze commit. The SKILL.md rows the round-99
   draft adds are what would make that citation true — a dependency the committer should close in
   the same commit, or the `used-by` column stays a forward reference.

9. **C2 check 10 grades a token set, not the M3 record's placement — the defect it claims to repair
   is not what it binds.** `tools/round99-record-audit.py:238-241` computes
   `mistakes = section(lesson99, "## Mistakes")` and asserts `"M3" in mistakes and "round-98.md" in
   mistakes and "sampling" in mistakes`. Measured on this seat's own draft lesson
   (`receipts/c2-check-10-weakness.out`): with the M3 record's **text** moved out of `## Mistakes`
   into a later section — its bytes unchanged, only its section changed — the counter still prints
   `checks=12 mismatches=0 met=True`, exit 0. It stays green because the M1 record independently
   carries all three tokens ("`corpus/lessons/round-98.md` M3 records that …", Class:
   `sampling`). Only when the M3 record is deleted *and* M1's mention is de-tokenised does check 10
   fire (`MISMATCH 10 …`, exit 1). So a lesson that drops the carried M3 record entirely — the
   round-98 spot-check's routed defect 4, the very thing this round's M3 answers — still grades
   green. This is a calibration gap in the instrument, not in the text: the drafted lesson carries
   the record where it should be, but the counter cannot see the difference.

   By contrast, check 9 (the six failed gate arms) binds properly: renaming the `round-clean` arm
   in the receipt copy, and removing `round-clean` from both correction blocks, each fire
   `MISMATCH 9` and exit 1 (`receipts/c2-check-9-binding.out`). The gap is specific to check 10.

10. **Most of the plan's measurement-time receipts are untracked working-tree files.** At `00394f3b`,
    of the plan's list (`measured/c1.out`, `measured/c2.out`, `measured/c3.out`,
    `controls/c2-forged.out`, `controls/c3-regression.out`, `controls/census-end.out`): only
    `controls/c2-forged.out` is tracked; `measured/c1.out`, `measured/c2.out`, `measured/c3.out`,
    `controls/c3-regression.out` and `controls/census-end.out` are present on disk but **untracked**
    (`receipts/wave-file-census.out`). The plan says these are "committed with M1/M2/M3", so they are
    pending the measurement commit; but two committed records already cite them as evidence — the
    knowledge entry's `verified-at` cites `measured/c3.out` and `controls/c3-regression.out`
    (finding 2), and `SKILL.md:1826` cites `measured/c3.out`. Until they are committed, those
    citations point at bytes a fresh clone does not have. Their **content** is green, read at the tip
    (`receipts/wave-file-census.out` plus this seat's read of the files):
    `measured/c1.out` → `CONTROL_POP99 … selected=6 ran=5 … refused=1 complete=1 met=True`, exit 0
    (now also carrying `mutant_selected_ids`/`mutant_ran_ids`, i.e. the amendment hardened the
    identity check this seat's C1 limit (a) disclosed);
    `measured/c2.out` → `RECORD_AUDIT99 checks=12 mismatches=0 met=True`, exit 0;
    `measured/c3.out` → `AUTOLOAD_STATES99 cells=8 mismatches=0 base_mismatches=7 flips=7 stable=1
    met=True`, exit 0; `controls/census-end.out` → `census_exit=0`.

11. **The lane's verdict-matrix harness has no cell for the new reason.** `tests/probe-verdicts/`
    carries 77 rows over ten matrices, and `RouterUnloaded.json`'s five rows cover
    `router-unloaded-no-autoload` (`models_autoload:false`), `router-unloaded-failed`,
    `router-model-missing-autoload`, `router-model-invalid-non-gguf` and
    `router-model-invalid-gguf-v1` — none expects `router-autoload-unread`
    (`receipts/harness-reason-coverage.out`). The candidate probe passes all 77
    (`tests=77 passes=77 failures=0`, the committed `controls/c3-harness-candidate.out`), so the
    harness is green **without** ever exercising the new vocabulary: after the SKILL.md row lands,
    the reason a probe investigator is told to read has no harness row, only the five stub cells of
    `tools/round99-autoload-states.py`. A sixth `RouterUnloaded` row (a `/props` route answering
    non-JSON, expecting `MODEL_UNLOADED / router-autoload-unread / exit 2`) is the shape that would
    close it; that is a `tests/` edit, and this seat wrote no tracked file.

## Out of scope for this seat (not done, and why)

- No tracked lane file was edited. The lane working tree already carries uncommitted
  `SCORECARD.md`, `LOG.md`, `tools/round99-record-audit.py` and an untracked
  `corpus/lessons/round-99.md`; those are the committer's (L1 `KamaR99`) to land, and this seat did
  not touch them.
- No git/jj mutation in the lane repo, no commit, no push, no fleet-repo file, no sibling lane, no
  lane Git index, no jj state.
- No claim's predicate was re-derived for the *other* two seats' instruments beyond what the seat
  brief asked for; the C1/C2/C3 re-runs above were the seat's own verification of the claims it
  drafts text for.
- The `round-98 19-cell regression` control (`controls/c3-regression.out`) was re-run here and
  **passes**: `ROUTER_BUDGET98 cells=19 mismatches=0 positive_mismatches=0 load_cells=19
  load_stable=1`, exit 0, `probe_sha256=829fbde5859d9111c85a3d6fe1aa63d0e7c830a40a5fc83c3a0595001fda7f21`,
  `slow_files=72`, `w03_seconds=644.8`, over 72 slow files and both passes
  (`receipts/c3-regression-r98.out`) — so the vocabulary change moves no cell expectation at either
  load, and kill rule K5 is not met. Two caveats a reader must carry:

  - the lane's `controls/c3-regression.out` still does not exist; the committer should land this
    receipt under that name. The committed knowledge entry's `verified-at` already cites that path.
  - the line's `base_sha256=27065a5c487ec819a975cc96d3c990ab5161d0e55d82be02a87dde86974ed3b4` is the
    **round-98 counter's own BASE constant**, not the `439fdb3d` probe (`40ab387e…`) the round-99
    instruments use. Two bases appear across the wave's receipts; quoting them interchangeably would
    be wrong.

  A first attempt at the same run was SIGTERM'd by a 3000 s wall clock inside the load pass after
  grading 19 natural cells and 8 load cells green (exit 143); both attempts are in the receipt.

- The fleet report (`/home/vgpnk/Projects/shokunin/`) is outside the lane repo and was not read or
  written.

## Tooling

No tool was installed, upgraded or removed. Everything used was already present: `curl`, `git`
(read-only in the lane; a `git clone --shared` scratch clone under this seat's scratch for the
SKILL.md row experiment), `bash`, `python3` (3.14, the lane's own counter interpreter), and
`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh` (the fleet's own census generator, run
read-only). `pacman` was not invoked; no host service was restarted; no sysctl was touched.

## Scratch

All scratch lived under `/fast/scratch/hyaku/kama-r99/SB01Entry/` (the fetched source bytes, the
scratch `git clone --shared`, the materialised trees, the counter work dirs) and has been removed
after the receipts were copied into the out dir. Nothing was written under `/tmp`.
