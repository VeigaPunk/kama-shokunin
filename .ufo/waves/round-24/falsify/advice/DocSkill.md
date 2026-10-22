# DocSkill — attack on the SKILL.md round-24 appended rules and registries

Round 24, FRESH FALSIFICATION of integrated commit `2e254a1763a9c08aa07fc53081287f506c447d84`.
Read-only production. L1 holds the planner. Lane bounds: leaf member, no subagent dispatch.

## Verdict

**PARTIAL.** Three of the four assigned axes hold outright; one holds only in substance.

| Axis | Verdict | Basis |
|---|---|---|
| Actual CLI flags / maps / paths exist | **HOLDS** (one tool-contract exception, F3) | every flag, path, exit code and pinned digest named in the round-24 rows was checked against the pinned tree |
| No legacy 31-count current reading | **PARTIAL** | the 31 is explicitly superseded in prose, but a live `gate:` row for the same command survives beside the new `probe:` row (F1) |
| Original rule withdrawn, not passed | **HOLDS (strong)** | the 44 original cells are byte-identical to the frozen oracle; the withdrawn view is reported separately and never enters a violation count |
| Probe vs gate clear | **PARTIAL** | gate/probe labels are semantically right per row, but the same command carries both labels in the same file (F1) |

Four defects are reported: **F2** (the registry's named score field is structurally zero in the
candidate arm — the strongest finding), **F1** (contradictory gate/probe rows for one command),
**F3** (the isolation probe's `--only` accepts an unknown id and exits 0 vacuously), **F4**
(the withdrawn-view report also collects ordinary regressions — a naming/legibility defect, not
a falsification of the withdrawn-not-passed axis).

No source bug was fixed in production; this lane is read-only. Minimal corrections are given
per finding.

---

## Environment, pins and provenance (observed, not inferred)

Scratch clone, `--no-hardlinks`, detached at the pinned revision:

```
/fast/scratch/hyaku/kama-r24/falsify/DocSkill/repo
git clone --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin repo
git checkout --detach 2e254a1763a9c08aa07fc53081287f506c447d84
git rev-parse HEAD            -> 2e254a1763a9c08aa07fc53081287f506c447d84
git status --porcelain        -> (empty)
```

Digest chain, computed in the pinned clone. Every task-stated pin matches:

| Artifact | sha256 (observed) | Task pin | Match |
|---|---|---|---|
| `tools/report-landing-audit.py` (source) | `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220` | `ea51bc35…` | yes |
| `tests/report-audit/promisor-grid.py` (runner) | `b034e1596746d312989b7894c0757b67859df19a476a01ccd95076424135cefa` | `b034e159…` | yes |
| `tests/report-audit/promisor-grid-expectations.json` (manifest) | `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1` | `d86b7bea…` | yes |
| `tests/report-audit/promisor-mutants.py` (mutation probe) | `6e0b9d62db9fe27f6c14c6e16ce239023f699142193adff5291e4374a1bb60a2` | `6e0b9d62…` | yes |
| `tests/report-audit/isolation-mutants.py` | `bb32ec2146484b74ace787d4d223c4895c68fedf734464485358630bf3c10a2d` | — | — |

Frozen base `0df800e896f6bce285a81e794ad4ae1d1e6c3a71`, present in the clone
(`git cat-file -t` → `commit`). The frozen auditor blob digest was re-derived:

```
git show 0df800e896f6bce285a81e794ad4ae1d1e6c3a71:tools/report-landing-audit.py | sha256sum
  -> da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1
```

That equals `derived_from.frozen_auditor_sha256` in **both** the shipped manifest and
`.ufo/waves/round-24/oracle-snapshot-before-inspection.json`. Both files also agree on
`views`, `amendment`, `calibration` (byte-equal JSON) and on
`derived_from.frozen_auditor_sha256` (observed by comparison, not assumed).

Production tree was not modified by this seat: `git status --porcelain` in
`/home/vgpnk/Projects/shokunin/kama-shokunin` shows only other lanes' concurrent edits under
`.ufo/waves/round-24/build/advice/` plus untracked wave directories; the only files this seat
wrote are the two paths listed under **Files written**.

All heavy scratch lived under `/fast/scratch/hyaku/kama-r24/falsify/DocSkill` with `TMPDIR`
pointed there for every subprocess. No network, no transport, no execution payload. No
`--keep`ed fixture was inspected by hand (a peer reported that the blobless fixture's
`remote.origin.url` stays reachable, so a stray `git` probe without `--no-lazy-fetch` can
materialise missing blobs and silently evaporate the premise — every auditor invocation here
went through the grid harness, which probes premises with `--no-lazy-fetch`).

---

## A1 — Actual CLI flags, maps and paths exist: **HOLDS**

### A1.1 Every flag named in the round-24 rows exists with the documented shape

| SKILL.md location | Documented command | Observed |
|---|---|---|
| `:850` | `promisor-grid.py --arm frozen\|current\|both [--json]` | `tests/report-audit/promisor-grid.py:922` `choices=("frozen","current","both")` — exactly the three documented values; `--json` at `:927` |
| `:850` | grid self-test `--selftest` | `:929` — exists, exit 0 (below) |
| `:850` | grid write scope `/fast/scratch/hyaku/kama-r24`, `--keep`, `--out` | `SCRATCH` at `:54`; `make_root` `:1114-1125`; `--keep` `:930`, `--out` `:928` |
| `:870` | `promisor-mutants.py --json` | `:633` — exists |
| `:870` | `--selftest`, `--anchors PATH --json` | `:630`, `:627` (metavar `PATH`), `--json` `:633` |
| `:871` | `isolation-mutants.py [--only NAME] [--json]` | `--json` `:146`, `--only` `:147` — exist (see F3 for the `--only` contract) |

Both `--selftest` claims were executed, not merely grepped:

```
python3 tests/report-audit/promisor-grid.py --selftest          -> exit 0, "selftest cases=11 failed=0"
python3 tests/report-audit/promisor-mutants.py --selftest        -> exit 0, "selftest cases=11 failed=0"
```

The grid's `--anchors` mode was exercised against the pinned auditor (static only — the
anchors path applies each mutation as text and compiles it; it never runs the grid and never
runs git):

```
python3 tests/report-audit/promisor-mutants.py --anchors tools/report-landing-audit.py --json
  -> exit 0; all 11 mutants reported an applicable alternative and mutant_compiles=true
```

This matches `:870`'s pin "`--anchors PATH --json` checks unique applicable/compiling mutations
without executing the grid" — the anchors branch returns before any grid invocation.

### A1.2 The grid verdict map in the registry row matches the implementation

`:850` states: "0 selected arm observations meet their declared column; 1 mismatch/twin
mismatch/object acquisition; 2 harness/premise/unavailable input."

Checked in `tests/report-audit/promisor-grid.py`:

* exit 1 sources — `live_fail` (`:1020-1021`, current arm vs the amended column),
  `frozen_fail` (`:1022-1023`, frozen arm vs the frozen column), twin mismatch
  (`:1025-1028`), and object acquisition (`:808-810` inside `grade()`: any acquired object
  adds a problem, so the row is not met and the arm reports a violation). All four map to
  exit 1.
* exit 2 sources — `Premise` (`:944` unknown `--case`, and the fixture builders' premise
  raises), `OSError` (`:1060-1068`), and any other exception (`:1070-1075`). All map to exit 2.
* exit 0 — `:1111`, when no arm has a violation.

### A1.3 The pinned values in the grid row are all present and true

* "adjacent `promisor-grid-expectations.json`" — the file sits next to the runner in
  `tests/report-audit/`. True.
* "frozen auditor `0df800e:tools/report-landing-audit.py`" — present in the clone; digest
  re-derived and equal to the recorded pin (above). True.
* "original44 frozen before L1 source inspection plus3 disclosed opaque-dependency cells" —
  **verified by byte comparison** (see A3.1): the 44 shared case objects are byte-identical
  between the shipped manifest and the frozen oracle snapshot, and exactly three further cells
  exist (PG46/PG47/PG48). True.
* "exact finding/token, raw/uncorrected distinction and twin documents" — the runner carries
  `defects` (kind+token), `raw_defects` (`:842`), and `document`/`twins`/`twin_equal`
  (`:854`, `:1002-1015`). True.
* "S102 documents the encountered-missing format, S103 packaging provenance, and rejected S104
  explains why fsck green is not local availability proof" — `corpus/SOURCES.md:114-116` carry
  those three rows, S104's status is `rejected`, and all three list `SKILL.md` in `used-by`.
  True.
* Auditor behaviour described at `:843-848` matches `tools/report-landing-audit.py`: two
  isolated `rev-list --missing=print` walks, the second filtering blobs (`:672-677`),
  `core.commitGraph=false` on both (`:672`), lazy per-store diagnosis computed at most once
  (`:124-130`), invoked only from the unresolved-token path (`unknown_citation` `:689-703`,
  `opaque_hole` `:705-717`; `store.missing()` is called from no other site), and roots that
  include dangling objects via `cat-file --batch-all-objects` (`:635-650`). The 20-second
  deadline (`:153` `GIT_TIMEOUT = 20`) and the global Git isolation options (`:138-142`
  `--no-replace-objects --no-lazy-fetch …`, `:147-150` clears `GIT_*`, `GIT_CONFIG_GLOBAL=/dev/null`,
  `GIT_CONFIG_NOSYSTEM=1`) are intact.

### A1.4 The mutation-registry rows' pinned values are true

* "11 named mutations with declared target cells" — 11 entries (`PM01`…`PM11`); ten carry
  `expect_rows`, `PM08` carries `[]` and is `execution: "static-only"`.
* "PM08 no-lazy-fetch removal static-only and never executed" — `PM08`'s alternatives are
  `replace` on `"--no-lazy-fetch"`; the runner's static-only branch (`:730-747`) applies the
  text, checks the marker before/after, and `continue`s **without** invoking the grid. The
  three `replace` alternatives are static text edits; nothing executes.
* "27 retained literals,4 retired IDs without reuse" — `MUTANTS` holds 27 entries and `RETIRED`
  holds 4 (`M14-promisor-config`, `M22-promisor-pack`, `M27-promisor-boolean`,
  `M29-promisor-pack-pairing`); none of the four ids reappears in `MUTANTS`. True.
* "`RETIRED` explains their removed component" — each retired entry carries a `why` and a
  `replaced_by` attribution to `PM01`. True.
* "M17 follows the current local-store spelling" — `M17-ref-shadow` targets
  `raise EvalError(f"{store.path}: citation {token} names a ref")`, which is the auditor's
  current wording (`tools/report-landing-audit.py:235`) and matches exactly once. True.
* The retired literals are genuinely gone from the auditor: each of the four retired patterns
  occurs **0** times in `tools/report-landing-audit.py`, while all 27 retained literals occur
  **exactly once** (checked by literal-count scan — no retained pattern is ambiguous or
  missing, so the probe's fail-fast rule cannot trip spuriously).

### A1.5 The isolation row's exit map is true, with one exception (F3)

`:871` states "0 pristine passed and selected inventory evaluated, survivors reported; 2
fail-fast could-not-evaluate". The tool returns 0 after running the pristine control and the
selected mutants, and returns 2 on pristine failure, on a pattern that does not match exactly
once, and on a grid exit 2 (`tests/report-audit/isolation-mutants.py:149-190`). Observed:

```
python3 tests/report-audit/isolation-mutants.py --only M01-replace-objects --json
  -> exit 0; pristine=passed, mutants=1, killed=1, surviving=[]
```

The exception is an unknown `--only` id (F3).

---

## A2 — No legacy 31-count current reading: **PARTIAL** (F1)

### A2.1 What is right

The 31 is not presented as a current count anywhere I could find:

* `SKILL.md:863` — "This supersedes the round23 mutation row's31-element current reading:
  M14/M22/M27/M29 are explicitly retired because their metadata-classifier component was
  deleted; M17 follows the current local-store spelling." The round-24 row (`:871`) pins
  "27 retained literals,4 retired IDs without reuse", which equals the tool's actual
  `MUTANTS`/`RETIRED` sizes. The superseded literal "31 single-literal mutants of the auditor"
  survives only at `SKILL.md:803`, inside the dated round-23 section, and is explicitly
  disclaimed in the round-24 section that follows it — the lane's established
  supersede-without-editing convention (cf. `:509`, `:559`, `:645`, `:676`, `:818`).
* `LOG.md:1396` ("31 mutants, 30 killed") and `SCORECARD.md:1166` ("30/31 killed on a named
  row") are both inside their dated **Round 23** sections, not in a current-reading position.

So the *number* is handled. The defect is that the row carrying it is not marked as a
historical row, and it disagrees with the round-24 row on a different, load-bearing field.

### A2.2 F1 (MEDIUM) — one command, two live registry rows, contradictory `Kind`

`SKILL.md` contains, for the same command `tests/report-audit/isolation-mutants.py`:

| Line | Row name | Kind | Pinned values |
|---|---|---|---|
| `:803` (round-23 section) | "Isolation mutants" | **`gate:`** | "31 single-literal mutants of the auditor" |
| `:871` (round-24 section) | "Retained isolation mutation experiment" | **`probe:`** | "27 retained literals,4 retired IDs without reuse" |

The round-24 supersession sentence (`:863`) names **only** the "31-element current reading".
It does not name the `Kind` cell of the superseded row, and the round-23 row's exit map
("kills on grid exit 1 and survivors listed") also differs from the round-24 map ("selected
inventory evaluated"). A reader who greps `isolation-mutants.py` in `SKILL.md` gets two
answers to "gate or probe?" with no pointer from one to the other. This is the one place where
the assigned "probe vs gate clear" axis fails: the labels are individually correct (the grid
row is a gate; the two mutation experiments are bounded probes, per `:861-862`), but the file
carries both labels for one command.

**Minimal correction (documentation only, one sentence).** Extend `SKILL.md:863` to name the
whole superseded row rather than one field, e.g.:

> This supersedes the round-23 mutation registry row in full — its `gate:` kind, its exit map
> and its 31-element current reading: M14/M22/M27/M29 are explicitly retired …

Equivalently, mark `:803` as superseded in the same way other superseded rows are handled in
this file. No tool change is required.

---

## A3 — Original rule withdrawn, not passed: **HOLDS (strong)**

This is the axis I attacked hardest, because it is the one where a relabelling would be
cheapest and most damaging. It holds.

### A3.1 The 44 original cells are byte-identical to the frozen oracle

Comparing `tests/report-audit/promisor-grid-expectations.json` against
`.ufo/waves/round-24/oracle-snapshot-before-inspection.json` cell by cell:

```
byte-identical case objects: 44
differing: []
```

Every one of the 44 shared case objects — including its `frozen`, `original`, `amended`,
`notes`, `policy_ref`, `reason_forbidden` and `names_any_of` fields — serialises to the same
bytes in both files. No expectation was rewritten after the snapshot was taken. The seven
rows the amendment changes (PG22, PG23, PG24, PG28, PG30, PG34, PG41) carry the same
`amended` values in both files (drift list empty), and PG37's `amended_rows` entry is `null`
in the snapshot and correspondingly absent from the shipped manifest, so PG37 falls back to
its `original` view exactly as the oracle prescribes. The three added cells are PG46/PG47/PG48
and their `amended` expectations match `oracle-supplement-2.json` row for row (exit 2 /
exit 2 / exit 0; PG48 exit 0 with `kinds: []`).

### A3.2 The withdrawn view is reported separately and never counted as achieved

* The grid docstring (`:13-16`) states the original view is "Reported; withdrawn for the rows
  the L1 amendment changes; never counted as achieved", and `:28` — "The original view's
  failures are reported as withdrawn, not counted as violations."
* In the code, `met_original` is used **only** to build the withdrawn list
  (`promisor-grid.py:1029-1030` → `withdrawn_original_failures` at `:1043`). The violation
  lists are built from `met_amended` (current arm, `:1020-1021`) and `met_frozen` (frozen arm,
  `:1022-1023`). There is no path by which meeting or missing the withdrawn expectation
  changes an exit code.

Observed on the live current auditor, PG22 (the row whose original view demands exit 2 and
whose amended view demands the ordinary unresolved finding):

```
python3 tests/report-audit/promisor-grid.py --arm current \
  --case PG22-unknown-citation-incomplete-promisor \
  --case PG37-unused-missing-blob-with-fabricated-citation-plain \
  --case PG48-opaque-unused-tree-no-unresolved-token --json
  -> exit 0
     current: graded=3 violations=0 violating_cases=[]
               withdrawn_original_failures=['PG22-unknown-citation-incomplete-promisor']
     PG22 exit=1 met_amended=True met_original=False
     PG37 exit=1 met_amended=True met_original=True
     PG48 exit=0 met_amended=True met_original=True
```

PG22 diverges from the withdrawn expectation exactly as the amendment requires, is listed in
the withdrawn report, and contributes **zero** violations and **exit 0**. The withdrawn rule
is neither passed nor failed-as-a-defect.

### A3.3 The exit-2 / wrong-type / opaque-supplement behaviour matches the amended contract

Three further cells were executed to check the amended contract's edges:

```
python3 tests/report-audit/promisor-grid.py --arm current \
  --case PG38-wrong-type-citation-plain \
  --case PG46-opaque-tree-hides-cited-blob \
  --case PG47-opaque-tree-with-unresolved-fabricated-token --json
  -> exit 0; graded=3 violations=0
     PG38 exit=1 kinds=['landed-unresolved']  met_amended=True
     PG46 exit=2 stderr: "could-not-evaluate: round 1: unknown: unavailable required object:
                            2f62e7ff… could be hidden behind the missing tree or commit …"
     PG47 exit=2 stderr: "could-not-evaluate: round 1: unknown: unavailable required object:
                            0123456789abcdef0123456789abcdef01234567 could be hidden behind …"
```

* A locally present wrong-type blob stays a genuine failed finding, not an unknown object
  (PG38: exit 1, `landed-unresolved`, no refusal).
* A missing tree that conceals the cited blob's name produces a content-derived
  could-not-evaluate naming the missing tree/commit — not a guessed defect (PG46).
* The same opaque hole with an unresolved fabricated token refuses on the unresolved-token
  path only (PG47), with the fabricated token named in the reason.
* PG48 (unused missing subtree, every citation resolving) returns exit 0 — no blanket
  completeness precondition.

Nine distinct cells of the 47 were executed in total (PG07, PG10, PG22, PG25, PG37, PG38,
PG46, PG47, PG48); the remaining 38 were checked statically (expectation bytes, builder
presence, exit/kind/defect columns) but not executed.

### A3.4 The "unknown from metadata" reading is absent from the shipped auditor

`tools/report-landing-audit.py` contains no promisor-metadata classifier: the only occurrences
of `partialclone`/`promisor` in the file are the auditor's own docstrings (`:58-59`, `:619`)
and its selftest, which asserts the opposite of the withdrawn rule — that metadata keeps the
local verdict and that the promisor remote is never contacted (`:1176-1195`). There is no
`git fetch` call anywhere in the auditor. The four retired mutation literals are absent from
it (count 0 each), confirming the classifier component was deleted rather than reworded.

---

## A4 — Probe vs gate clear: **PARTIAL** (same defect as F1)

Per-row semantics are correct and were checked against the tools' actual exit behaviour:

* the promisor grid is a **gate**: graded rows, an exit map of 0/1/2, an unknown `--case`
  refusing with exit 2, and the exit code deciding pass/fail;
* the two mutation experiments are **probes**: `promisor-mutants.py` returns 2 for
  could-not-evaluate and 0 for "inventory evaluated", with kills and survivors both listed and
  no claim of universal green (`:870`), and `isolation-mutants.py` reports survivors without
  failing on them (`:871`). The round-24 prose says so explicitly (`:861-862`).

The failure is that `SKILL.md` carries the *same* command under both labels without saying
which is live — F1. The label semantics themselves hold.

---

## F2 — HIGH for the pinned score field: `amended_view_met` is structurally zero in the candidate arm

`SKILL.md:850` pins: "Frozen-history reproduction is not improvement: **`amended_view_met`
supplies the comparable target score**."

The implementation does not deliver a score under that name in the arm that carries the
candidate. `tests/report-audit/promisor-grid.py:1031-1032`:

```python
baseline = [r for r in graded
            if r["arm"] == "frozen" and r["met_amended_frozen"]]
```

`graded` is rebuilt per arm inside the arm loop (`:1019`), so it contains **only that arm's
rows**. In the `current` arm iteration no row has `r["arm"] == "frozen"`, so `baseline` is
empty and `amended_view_met` is 0 (`:1038`) while `amended_view_total` is `len(graded)` —
the full current-arm graded count. `amended_view_unmet` (`:1040-1042`) filters on the same
`r["arm"] == "frozen"` predicate and is therefore structurally **empty** in the current arm.
Only in the `frozen` arm does the field mean anything: how many of the 47 cells the r23 base
already meets under the amended view — the historical baseline (16/47 per
`.ufo/waves/round-24/build/advice/GridOracle.md:317-325`, which itself calls that number "the
historical baseline the repair is measured against, **not a target**").

Observed, on a **fully compliant** candidate:

```
--arm both --case PG07-complete-lane-plain --case PG10-omission-lane-plain \
           --case PG25-unknown-citation-plain
  frozen : amended_view_met=3 / amended_view_total=3  unmet=[]   violations=0
  current: amended_view_met=0 / amended_view_total=3  unmet=[]   violations=0
```

and on the three-cell current-arm run quoted in A3.2: `amended_view_met=0`, `amended_view_total=3`,
`violations=0`; and on PG38/PG46/PG47: `amended_view_met=0`, `amended_view_total=3`,
`violations=0`.

So a reader who follows the registry pin and reads the candidate's own summary sees
**"0 of 3 met the amended view"** for a candidate that met every one of them; and in a full
run, "0 of 47". The candidate's true amended score is recoverable only from
`violations`/`violating_cases` or from the per-row `met_amended` flags — not from the field
the registry names. The build lane's own committed evidence shows the same artifact:
`.ufo/waves/round-24/build/out/ConnClosure/pgrid-allroots.json` has current-arm
`"amended_view_met": 0` with `"violations": 0`.

Two readings exist, and the pin is wrong under both:

* if "the comparable target score" means *the candidate's* amended score — the natural reading
  — the field is structurally 0 in the candidate arm and the pin is false;
* if it means *the score to beat* (the frozen baseline), then the pin names a field that
  lives under the frozen arm's summary and is 0 in the current one, and it contradicts the
  lane's own terminology ("historical baseline … not a target", GridOracle advice), so a
  reader still cannot tell which number to quote.

No verdict is affected: the gate's exit code is correct, and the candidate's amended score is
correctly enforced through `live_fail`. The defect is in the *published observability
contract* — the field the registry tells a reader to use.

**Minimal correction.** Either side can be fixed alone; the safest is both.

1. Tool (`tests/report-audit/promisor-grid.py`): compute the current arm's amended score from
   the current rows and give the two quantities distinct names, e.g. keep
   `frozen_amended_baseline_met` for the frozen arm's baseline and set the current arm's
   `amended_view_met` to `len([r for r in graded if r["arm"] == "current" and r["met_amended"]])`
   with `amended_view_unmet` filled from the same predicate.
2. Registry (`SKILL.md:850`): restate the pin so it names the arm and the field, e.g. "the
   frozen arm's `amended_view_met` is the historical baseline the r23 base already meets under
   the amended view; the candidate's amended score is the current arm's
   `violations`/`violating_cases` (0 = every amended row met)".

---

## F3 — MEDIUM: the isolation probe's `--only` accepts an unknown id and exits 0 vacuously

`SKILL.md:871` advertises `python3 tests/report-audit/isolation-mutants.py [--only NAME]
[--json]` with the verdict map "0 pristine passed and **selected inventory evaluated**,
survivors reported; 2 fail-fast could-not-evaluate".

`tests/report-audit/isolation-mutants.py:158` skips any mutant whose name is not in
`--only`, with no check that the requested name existed at all. Observed:

```
python3 tests/report-audit/isolation-mutants.py --only M99-nonexistent --json
  -> exit 0; pristine=passed, mutants=0, killed=0, surviving=[]
python3 tests/report-audit/isolation-mutants.py --only M01 --json
  -> exit 0; pristine=passed, mutants=0, killed=0, surviving=[]
python3 tests/report-audit/isolation-mutants.py --only M01-replace-objects --json
  -> exit 0; pristine=passed, mutants=1, killed=1, surviving=[]
```

A typo (`M01` for `M01-replace-objects`) or a stale id yields a **vacuous green**: exit 0
asserting that "the selected inventory [was] evaluated" while nothing was evaluated, with
`mutants=0` and `surviving=[]` indistinguishable from "everything was killed". The sibling
probe in the same registry row guards this correctly —
`tests/report-audit/promisor-mutants.py:718-722` refuses an unknown `--only` id with
`could-not-evaluate: unknown mutant id in --only` and exit 2. The isolation probe has no
equivalent guard.

**Minimal correction (tool, one block).** In `isolation-mutants.py`'s `main()`, mirror the
sibling: after the selection, verify that every requested `--only` value corresponds to a
known mutant name, and otherwise print `could-not-evaluate: unknown mutant id in --only` and
return 2. Listing the accepted names in that message (e.g. `M01-replace-objects`) also removes
the `M01` ambiguity. A documentation-only alternative is weaker and does not remove the
false green: `SKILL.md:871` would have to say that `--only` takes the full mutant id and that
an unmatched id yields exit 0 with an empty inventory.

---

## F4 — LOW: the withdrawn-view report also collects ordinary regressions

`SKILL.md:850` says "The original withdrawn view is reported separately", and the grid
implements `withdrawn_original_failures` as "rows whose **original** expectation was not met"
(`promisor-grid.py:1029-1030`). For the 40 rows where `original == amended` that coincides
with "rows the candidate failed", so a genuine regression also appears in the withdrawn list.

Demonstrated with a mutated scratch copy of the auditor (scratch only; production untouched)
that returns exit 1 instead of 0 for a clean verdict:

```
python3 tests/report-audit/promisor-grid.py --arm current \
  --current /fast/scratch/hyaku/kama-r24/falsify/DocSkill/mut-audit.py \
  --case PG07-complete-lane-plain --json
  -> exit 1; graded=1 violations=1 violating_cases=['PG07-complete-lane-plain']
                withdrawn_original_failures=['PG07-complete-lane-plain']
```

PG07 is not an amendment-affected row (`original == amended == exit 0`), so it is a plain
regression — yet it is listed as a withdrawn-original failure alongside its correct listing
as a violation. Under a correct candidate this cannot happen (the withdrawn list then
contains only the rows the amendment changed), so it does not falsify A3; it does mean the
field name and the registry sentence invite a reader to read the withdrawn list as "the
amendment-affected rows".

**Minimal correction (tool, naming only).** Rename the key to `original_view_failures`, or
restrict it to rows whose `amended` differs from `original` and expose the remainder as
`original_view_regressions`. Alternatively `SKILL.md:850` can say "rows where the candidate
does not meet the **withdrawn original** expectation are reported separately from violations"
so the overlap is explicit.

---

## Residual risk and verification gaps

* **Not executed:** the full 47-cell grid. Per the assignment I ran no full suite. 9 of 47
  cells were executed (PG07, PG10, PG22, PG25, PG37, PG38, PG46, PG47, PG48); the other 38
  were verified statically only (byte-identical expectations, builder presence, exit/kind/
  defect columns). A claim about the remaining 38 cells' *runtime* behaviour is not made here.
* **Unintended suite execution, disclosed.** Exercising the isolation probe's documented CLI
  necessarily runs that probe's own pristine control (`repo-state-grid.py --arm current`).
  Three `--only` invocations therefore ran 4 repo-state-grid current-arm runs in total
  (2 + 1 + 1). These are the probe's own positive control over local synthetic fixtures —
  offline, no transport, no execution payload — but they are more than the minimal probe
  behaviour I intended, and I am recording them rather than leaving them implicit.
* **Not executed:** `promisor-mutants.py` against the real grid (only `--selftest` and the
  static `--anchors` mode were run). No mutant was executed against the grid in this lane,
  and PM08 was not executed at all, per the standing prohibition.
* **Not verified by execution:** that the frozen arm reproduces the r23 base on all 47 cells
  (I ran 3 frozen-arm cells; all met). The frozen-arm baseline figure (16/47) is taken from
  the build lane's receipt, not re-measured here.
* **Unverified:** the `S105` reconciliation and the 105-row source census — outside this
  lane's assignment and owned by L1 after this stage.
* **Unverified:** the r23 evidence corrections recorded in `LOG.md` (69 reports, 40 of 56
  identities) and every other r23 falsify-wave claim. My work does not touch them.
* **Fixture hazard not exercised:** a peer reported that the blobless fixture keeps a
  reachable `file://` origin, so a stray `git` probe without `--no-lazy-fetch` can
  materialise missing blobs and silently evaporate the premise. Every auditor invocation in
  this lane went through the grid harness (whose premise probes use `--no-lazy-fetch`), and
  no `--keep`ed fixture was inspected by hand, so the hazard was not triggered — but it also
  means I did not independently confirm the harness is immune in the presence of the blobless
  family.
* **SKILL.md is not a machine-read contract:** my checks read the shipped text against the
  shipped tools. A consumer who never executes the tools (a doc reader, a scorecard writer)
  remains exposed to F2 and F1 in particular; those two are the ones I would fix before the
  next round rather than after.
* **No source bug was fixed.** All four findings are reported with minimal corrections only;
  production was not edited, and the mutation experiments and the `--keep`ed fixtures were
  not disturbed.

---

## Files written

| Path | Content |
|---|---|
| `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/advice/DocSkill.md` | this report |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/DocSkill/` | measurement evidence: `anchors.json` (11-mutant static anchor report), `pg3.json` (current arm, PG22/PG37/PG48), `pg3b.json` (current arm, PG38/PG46/PG47), `pg48.json` (both arms, PG48), `pgplain.json` (both arms, PG07/PG10/PG25), `conf.json` (mutated-auditor regression probe), `r23ascur.json` (r23 auditor as candidate), `iso-bogus.json` / `iso-m01.json` / `iso-m01full.json` (isolation `--only` behaviour) |

Scratch-only, not part of the deliverable:
`/fast/scratch/hyaku/kama-r24/falsify/DocSkill/` (clone, `mut-audit.py` mutated auditor copy,
`frozen-audit.py`, raw JSON outputs).

No installs, no services, no configuration changes, no network access, no secrets, no model
parameter changes.

Report: .ufo/waves/round-24/falsify/advice/DocSkill.md
