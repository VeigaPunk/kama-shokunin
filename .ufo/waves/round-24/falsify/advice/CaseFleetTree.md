# CaseFleetTree — round-24 FRESH falsification, family FleetTree

Scope: fixture family `FleetTree` = `PG19-missing-fleet-tree-promisor` (policy) and
`PG20-missing-fleet-tree-plain` (control twin). Bounded selection only; read-only
production; leaf member (no subagents dispatched).

## Verdict

**HOLDS** on the **amended** (live) target columns for both rows, at the pinned revision.
**One real source defect found (M1, medium):** the *same* missing fleet tip tree is
refused with an object-naming reason under `--rounds <N>` but with a reason that names
**no object at all** under `--rounds <N>-` / the auditor's own default `--rounds 10-`.
The grid cannot see this because it always passes `--rounds 1`. A minimal source
correction is proposed below and **verified in scratch only**; production was not edited.

| row | arm | exit | met_frozen | met_amended_frozen | met_original | met_amended (live) | violations |
|---|---|---|---|---|---|---|---|
| PG19-missing-fleet-tree-promisor | frozen | 2 | true | **false** | n/a | n/a | 0 |
| PG19-missing-fleet-tree-promisor | current | 2 | n/a | n/a | true | **true** | 0 |
| PG20-missing-fleet-tree-plain | frozen | 2 | true | true | n/a | n/a | 0 |
| PG20-missing-fleet-tree-plain | current | 2 | n/a | n/a | true | **true** | 0 |

Whole-run result of the assigned command: **exit 0** (`violations: 0` in both arms,
`tracebacks: 0`, `timeouts: 0`, `harness_leaks: 0`).

Frozen history met is *not* counted as improvement. The only substantive delta versus
the frozen arm inside this selection is **PG19's reason class**: the r23 blanket metadata
refusal (`partial clone (remote.origin.promisor)`) became the content-derived
`unavailable required object: … (tip tree b1e11739…)`. PG20 is unchanged (no-harm twin),
and the exit code is 2 in all four rows. Note the frozen arm's `amended_view_met` is
**1/2** for this selection (`amended_view_unmet: ["PG19-missing-fleet-tree-promisor"]`)
— that is the historical baseline, not a target score.

## Environment and provenance (all digests observed in my own scratch clone)

Scratch clone: `git clone --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin`
→ `/fast/scratch/hyaku/kama-r24/falsify/CaseFleetTree/clone`, then
`git checkout --detach 2e254a1763a9c08aa07fc53081287f506c447d84` (detached; exact base
observed; `git rev-parse HEAD` = `2e254a1763a9c08aa07fc53081287f506c447d84`).

| artifact | observed sha256 | contract |
|---|---|---|
| `tools/report-landing-audit.py` (source tool) | `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220` | `ea51bc35…` ✔ |
| `tests/report-audit/promisor-grid.py` (runner) | `b034e1596746d312989b7894c0757b67859df19a476a01ccd95076424135cefa` | `b034e159…` ✔ |
| `tests/report-audit/promisor-grid-expectations.json` (manifest) | `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1` | `d86b7bea…` ✔ |
| `tests/report-audit/promisor-mutants.py` (mutation probe) | `6e0b9d62db9fe27f6c14c6e16ce239023f699142193adff5291e4374a1bb60a2` | `6e0b9d62…` ✔ |
| frozen auditor blob `0df800e8:tools/report-landing-audit.py` | `da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1` | manifest `derived_from.frozen_auditor_sha256` ✔ |

Host `git version 2.56.0`. `TMPDIR` was set per subprocess to
`/fast/scratch/hyaku/kama-r24/falsify/CaseFleetTree` (inside the grid's required
`SCRATCH = /fast/scratch/hyaku/kama-r24` root). Production was not modified by me:
`git status --porcelain` in `/home/vgpnk/Projects/shokunin/kama-shokunin` shows only
pre-existing entries (`.ufo/waves/round-24/build/advice/GridOracle.md` modified by
another lane, plus untracked `.ufo/waves/round-24/falsify/` and `.ufo/waves/round-24/fixes/`).

## Commands executed (exact)

```
cd /fast/scratch/hyaku/kama-r24/falsify/CaseFleetTree
git clone --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin clone   # exit 0
git checkout --detach 2e254a1763a9c08aa07fc53081287f506c447d84              # exit 0
git --version                                                               # git version 2.56.0
git cat-file -t 0df800e896f6bce285a81e794ad4ae1d1e6c3a71                     # commit
git cat-file blob 0df800e8…:tools/report-landing-audit.py | sha256sum        # da5041a8…
sha256sum tools/report-landing-audit.py tests/report-audit/promisor-grid.py \
          tests/report-audit/promisor-grid-expectations.json tests/report-audit/promisor-mutants.py
TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/CaseFleetTree \
  python3 tests/report-audit/promisor-grid.py --arm both \
    --case PG19-missing-fleet-tree-promisor \
    --case PG20-missing-fleet-tree-plain --json                # exit 0
TMPDIR=… python3 verify_fleet_tree.py                          # exit 0 (independent re-derivation)
TMPDIR=… python3 probe_nolazyfetch.py                          # exit 0 (bait remote)
TMPDIR=… python3 probe_ab.py                                   # exit 0 (A/B isolation control)
TMPDIR=… python3 (inline) cause-isolation control              # exit 0
TMPDIR=… python3 (inline) range / default-rounds probes        # exit 0
TMPDIR=… python3 (inline) minimal-correction candidate        # exit 0 (scratch copy only)
TMPDIR=… python3 (inline) git-call trace via a PATH git wrapper # exit 0
```

My scratch scripts import the **pinned grid's own builders**
(`c_missing_fleet_tree_promisor`, `c_missing_fleet_tree_plain`), so every fixture is
byte-identical to the graded one; the grid keeps only a 300-char stderr tail, so I
re-ran the auditors by hand to capture full stderr. No network, no transport payload,
no repository program, no execution payload, no `--keep`ed fixture reused across probes.

## Actual missing / present objects (asserted directly, both rows)

| fact | PG19 (promisor) | PG20 (plain) |
|---|---|---|
| fleet promisor-marked | **true** (`remote.origin.promisor=true`, `extensions.partialclone=origin`, `remote.origin.url=<tmp>/absent-remote.git`) | **false** (no `remote.*` key at all) |
| lane promisor-marked | false | false |
| lane missing objects (`rev-list --objects --missing=print --no-lazy-fetch`) | `[]` — lane complete | `[]` |
| fleet missing objects | **exactly one**: `['b1e11739fedfb736f2936bd9addf7e4a286d462e']` | identical single id |
| fleet tip tree `b1e11739…d462e` present (`cat-file -e`) | **no** | **no** |
| fleet report blob `0cf7ed5c…0302b` present | **yes** | **yes** |
| fleet HEAD commit `18f93ab8…3be6b` present | **yes** | **yes** |
| lane tip tree / lane cited commit `58866b56…4c33` present | **yes / yes** | **yes / yes** |
| `git show HEAD:.ufo/reports/round-1/kama.md` in fleet | rc=128 | rc=128 |
| `git ls-tree -r HEAD -- .ufo/reports` in fleet | rc=128 `fatal: not a tree object` | same |

**The fixture is minimal and exactly on point**: one object is removed — the fleet's
**root tree** — while the report *blob* it names (`0cf7ed5c…`) and the fleet commit
remain present. The lane is untouched and complete. So the refusal is forced by
content: the report blob cannot be *reached* without the tree that names it.
Proof from the intact twin (`verify-tree-message.json`): the same tree id
`b1e11739…d462e` in an intact promisor-marked fleet lists exactly
`100644 blob 0cf7ed5c…0302b  .ufo/reports/round-1/kama.md` and
`100644 blob bfa65511…446b  notes.md`, and `git show HEAD:.ufo/reports/round-1/kama.md`
there exits 0. The path **is** inside the missing tree — so the missing object is
required by the audit's own read, not an unrelated hole.

**Fixture data diff (PG19 vs PG20), measured field by field** (`verify-fixture-diff.json`):
the *only* differing keys are `fleet_cfg` and `fleet_promisor`. Shas, fleet object
inventory, lane object inventory, fleet missing list, lane missing list, both
worktrees, and the lane config are byte-identical. This is a clean twin pair.

## Exact finding / token pairs and content-derived reason

Both rows exit **2** and emit **no verdict document** (`stdout` = 0 bytes; not JSON),
so there are **no finding/token pairs at all** (`defects: null`, `kinds: null` — and the
live expectation for both rows is `kinds: null, defects: null` with
`reason_class: "unavailable"`). The refusal's content-derived identifiers are the only
output (identical for PG19 and PG20 up to the fixture path segment):

```
could-not-evaluate: unavailable required object: .ufo/reports/round-1/kama.md at fleet HEAD
(tip tree b1e11739fedfb736f2936bd9addf7e4a286d462e, <fleet repo>): git show
HEAD:.ufo/reports/round-1/kama.md in <fleet repo>: rc=128 fatal: path
'.ufo/reports/round-1/kama.md' exists on disk, but not in 'HEAD'
```

Source path: `audit_round()` → `git show HEAD:<rel>` fails → `required_read(<rel> at fleet
HEAD (tip tree …), exc)` → `EvalError` → `main` prints `could-not-evaluate: …`
(`tools/report-landing-audit.py:280-284` `required_read`, `:455-464` the report read,
`:266-273` `root_tree`, `:1314` the print).

Grader properties, all observed satisfied by the current arm:
`stderr` starts with `could-not-evaluate:` ✔; stdout carries no verdict document ✔;
reason class `unavailable` matched by the genuine terms `unavailable` and `not in 'head'`
✔; forbidden reasons `partial clone (` and `promisor pack` **absent** ✔ — the promisor
metadata does not appear in the reason at all; `names_any_of` satisfied by
`b1e11739fedfb736f2936bd9addf7e4a286d462e` ✔ — **the strong object-id name is what
carries it**, not a path fallback.

**Cause isolation** (`verify-cause-isolation.json`): a *complete* promisor-marked fleet
(`c_complete_fleet_config`) exits **0 clean** with `defects: []` and
`fleet_missing: []` — identical to its plain twin. So PG19's exit 2 is caused by the
missing tree, **not** by the promisor metadata. This is exactly the amended contract's
"metadata alone never changes a verdict".

**Frozen arm, for the record**: PG19's frozen stderr is the r23 blanket refusal
`could-not-evaluate: <fleet>: partial clone (remote.origin.promisor)` (reason class
`metadata`, which is why the frozen expectation for PG19 says `reason_class: "metadata"`),
and PG20's frozen stderr is `round 1: cannot read .ufo/reports/round-1/kama.md at fleet
HEAD: … fatal: path '…' exists on disk, but not in 'HEAD'` (already content-derived,
hence PG20's frozen expectation is `unavailable`).

## No objects acquired — and the assertion is not vacuous

`objects_acquired` = `{"lane": [], "fleet": []}` for **all four** rows (both arms, both
cases), computed by the harness as the set difference of `git cat-file
--batch-all-objects --batch-check=%(objectname)` before and after the audit.

The grid's own PG19 fixture points the promisor remote at a **non-existent** local
directory, so its no-acquisition assertion could not fail even if the auditor fetched.
I therefore ran a **bait-remote A/B** (`probe_ab.py`, `verify-ab-nolazyfetch.json`):
the promisor-marked fleet's `remote.origin.url` was repointed at a **valid local bare
repository that really holds the missing tree** `b1e11739…d462e`.

* **phase 1 (isolated auditor, as the grid runs it):** exit 2, reason names the missing
  tree id, `acquired = {lane: [], fleet: [], bait: []}`, `lost = {}`,
  `fleet_tree_present_after: false`, `bait_has_tree: true`.
* **phase 2 (un-isolated `git cat-file -e`, positive control on a separate copy):**
  rc=0 and `fleet_tree_present_after: true` — the object **is** materialised from the
  bait remote when isolation is removed (`warning: filtering not recognized by server,
  ignoring`).

So the auditor's `--no-lazy-fetch` isolation (`tools/report-landing-audit.py:138-141`,
applied to every git call at `:156-165`) is what prevents the acquisition; the
no-acquisition result is a real property, not an artifact of an unserviceable remote.

**Full git-call trace** (a PATH `git` wrapper logging argv, PG19 fixture): **15** git
invocations; `any fetch/clone/pull/remote/submodule` = **[]**;
`any rev-list --missing=print` = **[]**; `--no-lazy-fetch` present in **15/15**;
`--no-replace-objects` present in **15/15**. The trace ends at
`git show HEAD:.ufo/reports/round-1/kama.md` then `git log -1 --format=%T HEAD` (the
`root_tree` fallback that recovers the tip tree id from the commit header — the tree id
is in the commit object, which *is* present, so the refusal can name it).

## Twin document comparison — what actually happened

**No twin document comparison was executed for this family.** Both current rows carry
`twins: {"PG20-…-plain": None}` / `{"PG19-…-promisor": None}`, `twin_equal: null`; the
arm summaries show `twin_pairs_in_manifest: 1`, `twin_compared: 0`,
`twin_pairs_compared: []`, `twin_mismatch: []`. Cause: both rows exit 2 with empty
stdout, so `normalise_document()` returns `None` and the twin block records "not
comparable" (`promisor-grid.py` twin block; `results[partner] = None` →
`twin_equal = None`).

Consequence for the record: the manifest's declared twin link `PG19 ↔ PG20` is **not**
verified by any automated document comparison. My own manual comparison shows the two
refusals identical after path normalisation (`stderr identical after path
normalisation: True`; only the `…/PG19-…/fleet` vs `…/PG20-…/fleet` segment differs), so
the substance holds — but **the harness does not assert it**. A claim of "twin document
equality verified for PG19/PG20" would be unsupported; the correct claim is "twin
equivalence verified manually, by me". (Same structural gap already reported for the
adjacent family `PG17/PG18`; it is a property of the grid's twin block, not of this
family.)

## Original vs amended view (and the withdrawn expectation)

The manifest rows for **both PG19 and PG20 have no `amended` entry**, so per the
manifest's own rule ("a case without an 'amended' entry uses its 'original' view") the
live view is identical to the original view: `exit 2`, `reason_class "unavailable"`,
`kinds: null`, `defects: null`.

* Current arm: `met_original = true` **and** `met_amended = true` for **both** rows →
  `withdrawn_original_failures: []` for this selection. **Neither PG19 nor PG20 carries
  a withdrawn expectation**, so nothing here is relabelled as passed.
* The withdrawn set (`PG22`, `PG23`, `PG24`, `PG28`, `PG30`, `PG34`, `PG41`, plus
  `PG37` with `amended: null`) lies outside my selection and stays visible and unchanged
  in the manifest; I did not grade it and make no claim about it.
* Manifest integrity check (independent of the grid run): the 44 rows of
  `.ufo/waves/round-24/oracle-snapshot-before-inspection.json` are **byte-identical** in
  the shipped manifest across `kind, builder, policy_ref, notes, frozen, original,
  amended, twin, names_any_of, reason_forbidden` (**0 field diffs** on every row present
  in both), and the manifest adds exactly the 3 independent opaque cells
  `PG46-opaque-tree-hides-cited-blob`, `PG47-opaque-tree-with-unresolved-fabricated-token`,
  `PG48-opaque-unused-tree-no-unresolved-token` → `population_size = 47`, matching the
  fixed47 contract (original44 unchanged + 3 opaque cells). `PG19`/`PG20` rows are
  byte-identical to the snapshot rows. Live `population_sha256` =
  `612b0a74f3eebaa9074bdde8ecd8f194f55ebaf9a35ab2b975fddbff8dd2ed88` =
  the registered `build/out/GridOracle/population.json` value; manifest sha256
  `d86b7bea…` = registered value.

## Findings by severity

### M1 — [medium, SOURCE] The same missing fleet tree is refused without naming the object when the round selection is a range

`parse_rounds()` (`tools/report-landing-audit.py:589-611`) resolves an open round range
(`N-`, which includes the auditor's **own default `--rounds 10-`**, `argparse` at
`:1298`) by listing the committed fleet reports:

```python
listed = git(fleet_repo, "ls-tree", "-r", "--name-only", "HEAD",
             "--", ".ufo/reports", errors="surrogateescape")
```

That call is **not** wrapped in `required_read()` / `root_tree()`, unlike every other
required read in the file (`report_cutoff` `:318-324`, `load_source_urls` `:366-373`,
the report read in `audit_round` `:455-464`). Consequence, measured on the **same
PG19/PG20 fixtures**:

| invocation | stderr (current source) | names the missing object? |
|---|---|---|
| `--rounds 1` (what the grid uses) | `unavailable required object: .ufo/reports/round-1/kama.md at fleet HEAD (tip tree b1e11739…, …)` | **yes** |
| `--rounds 10-` (open range) | `could-not-evaluate: git ls-tree -r --name-only HEAD -- .ufo/reports in <fleet>: rc=128 fatal: not a tree object` | **no** |
| no `--rounds` (argparse default `10-`) | identical to the open-range line | **no** |

Applied to the grid's own `check_exit2_form()` with `names_any_of = ["$fleet_tip_tree"]`
and `reason_forbidden = ["partial clone (", "promisor pack"]`:

* `--rounds 1` → `[]` (all form properties satisfied)
* `--rounds 10-` → `['reason does not name the unavailable object']`

So the amended contract's "content-derived reason **naming the object**" holds on the
grid's selection but not on the default/real-world invocation. This is not cosmetic: the
manifest's grader for these rows is the **strong `names_any_of`** (it must contain
`b1e11739…`), and the refusal on the range path would fail it. It also contradicts the
auditor's own docstring (`:63-67`: "the audit refuses (exit 2, `unknown: unavailable
required object`, **naming the object**)") and the module contract that every refusal
names the unavailable object.

Scope limits, stated honestly:
* The **exit code is 2 in every case** and stdout stays empty — no false clean/failed
  verdict is produced, and the promisor metadata still does not appear in the reason.
  The defect is the *quality of the refusal reason*, not a wrong verdict.
* The frozen (r23) auditor has the **identical** asymmetry (`frozen:default` and
  `frozen:rounds_open` both give `fatal: not a tree object`; only `frozen:rounds_1`
  differs, because the metadata refusal fires first there). So this is an **inherited**
  shape, not a regression introduced by the r24 repair — but it is also not repaired by
  it, and the r24 contract explicitly requires the naming.

**Minimal correction (reported, NOT applied to production).** In `parse_rounds()`, wrap
the listing read the way the other three required reads already are:

```python
else:
    # committed fleet reports only, never working-tree drafts
    try:
        listed = git(fleet_repo, "ls-tree", "-r", "--name-only", "HEAD",
                     "--", ".ufo/reports", errors="surrogateescape")
    except EvalError as exc:
        tree = root_tree(fleet_repo, "HEAD")
        what = (f"the fleet report listing at fleet HEAD (tip tree {tree})"
                if tree else "the fleet report listing at fleet HEAD")
        raise required_read(what, exc) from exc
    ...
```

**Verified in scratch only** (`verify-minimal-correction.json`, applied to a copy under
`/fast/scratch/…/patch/patched-audit.py`, never to production): with the patch,
`--rounds 10-` on both PG19 and PG20 yields
`could-not-evaluate: unavailable required object: the fleet report listing at fleet HEAD
(tip tree b1e11739fedfb736f2936bd9addf7e4a286d462e): git ls-tree …` → `check_exit2_form`
returns `[]` and `names_tree: true`, and `--rounds 1` behaviour is **byte-identical** to
the unpatched source. The patch touches only the reason text; no exit code, verdict, or
premise changes.

Note the ordering caveat for the reviewer: `root_tree()` reads the tip tree id from the
**commit header**, which is present here; when the commit itself is missing, `root_tree`
returns `None` and the message degrades to the tree-less form — the same graceful
degradation the existing three call sites already have.

**Production reachability of M1 (measured, and it lowers the operational urgency, not the
contract defect):** the production fleet is intact —
`git ls-tree -r --name-only HEAD -- .ufo/reports` in
`/home/vgpnk/Projects/shokunin/kama-shokunin` exits 0 and lists
`.ufo/reports/round-5/kama.md`, and `git cat-file -e HEAD^{tree}` exits 0 — so the
`parse_rounds` listing read does not fail in production today. M1 is therefore a
**latent** contract gap on the path where the fleet tip tree is unavailable, not an
active production outage. It becomes live exactly in the situation the round-24
amendment is about (a fleet repository that cannot serve its tip tree), which is why the
round selection must not change the *form* of the refusal.

### M2 — [low, harness/manifest coverage] The declared twin link of this family is never compared
`promisor-grid.py` derives twin equality from the verdict **document** only; for exit-2
rows there is no document, so `twin_compared` is `0` while `twin_pairs_in_manifest` is
`1`. A reader of the arm summary could take `twin_mismatch: []` for "twins verified".
*Minimal correction (reported, not applied):* in the twin block, fall back to a
path-normalized stderr comparison when both documents are `None` (or expose
`twin_reason_compared`), so a refusal-pair twin is asserted rather than silently skipped.

### M3 — [low, fixture/expectation precision] `names_any_of` for PG19/PG20 depends on the grid's `--rounds 1`
The manifest's `names_any_of` for both rows is `["$fleet_tip_tree"]` — the strong
object-id requirement. It is met on the graded path *only because* the grid hardcodes
`--rounds 1` (`promisor-grid.py` `run_auditor`). Under the auditor's default round
selection the same cell would fail the `names_any_of` check (see M1). No expected cell
was changed by me, and no fixture was adjusted to fit the candidate — the mismatch is
reported as a source defect (M1) with a minimal correction, not papered over in the
manifest. A manifest row exercising an open range (e.g. `--rounds 1-`) would have caught
M1; the grid's single hardcoded `--rounds 1` cannot.

### M4 — [low, grading method] `reason_class` is a whole-stderr substring test
`REASON_CLASSES` matching is `t in err.lower()`. In my scratch runs the case directory
name `PG19-missing-fleet-tree-promisor` contributes the substring `missing` to stderr.
In the graded grid run the fixture path is `promisor-grid-<rand>/<arm>/<nnn>/<repo>`,
which contains no class term, so both rows' class was carried **only** by the genuine
content-derived terms `unavailable` (from `unavailable required object`) and
`not in 'head'` (from git's own message). No row outcome depends on the path artifact;
recorded because it weakens the class test in general.

### Fixture flaws vs source flaws
* **Fixture data (PG19/PG20): no flaw found.** The premise is minimal and exactly on
  point: exactly one missing object (the fleet's root tree), the report blob that the
  tree names still present, the fleet commit still present, the lane complete with its
  tip tree and cited commit present, PG19's fleet promisor-marked and PG20's plain,
  and the two fixtures differing **only** in the fleet's promisor config (measured
  field-by-field). The missing tree is genuinely *required* by the audit's read
  (proved from the intact twin's listing), so the exit-2 verdict is forced by content.
  It is deliberately distinct from the neighbouring families (PG15/16 missing *lane*
  tree, PG17/18 missing fleet report *blob*, PG43 fleet unhydrated blobless).
* **Source: one flaw found in scope (M1)** — the refusal reason on the open-range round
  selection names no unavailable object, so the auditor's own stated contract ("naming
  the object") and the manifest's strong `names_any_of` grader are not met on that
  path. Exit codes and verdicts are unaffected; the minimal correction is above and
  verified in scratch. No other source flaw found: the refusal path is content-derived
  end to end, never consults promisor metadata for the verdict, acquires nothing, and
  the marked and unmarked fleets are refused for the same substantive reason.

## Observed vs inferred

* **Observed**: exit codes (2/2/2/2), the full stderr of the current arm for both rows
  and for the range/default variants, the frozen arm's stderr tails, stdout emptiness
  (0 bytes) and non-JSON-ness, the premise missing lists, promisor facts, object
  presence/absence via `cat-file -e` / `ls-tree` / `rev-list --missing=print`, the
  before/after object-inventory deltas (empty), the 15-call git argv trace, the
  bait-remote A/B, the complete-fleet cause-isolation control, the field-by-field
  PG19↔PG20 fixture diff, twin results (`None`/`null`, `twin_compared: 0`), the
  met_frozen / met_amended_frozen / met_original / met_amended flags,
  `withdrawn_original_failures: []`, `violations: 0`, the manifest↔snapshot equality
  (0 diffs, 47 rows), the four contract digests, the live vs registered population
  digest, and the scratch-verified effect of the proposed minimal correction.
* **[INFERENCE]** that the refusal is "content-derived" in the intended sense: the reason
  embeds the actually-requested path, the fleet tip tree id read from the commit
  header, the exact git command, its rc and git's own message — all taken from the
  failing read, not from promisor metadata or from a fixed string.
* **[INFERENCE]** that no network transport occurred: the auditor's calls carry
  `--no-lazy-fetch` in 15/15 invocations, no fetch/clone/pull/remote command appears in
  the trace, no object was acquired even when the promisor remote provably could serve
  it, and the positive control shows that removing the isolation *does* materialise the
  object. I did **not** instrument sockets.

## Residual risk and verification gaps

1. **M1 is unfixed in production** — my correction is verified only in a scratch copy.
   Until it lands, the default `--rounds 10-` invocation on a fleet with a missing tip
   tree yields a refusal that names no object; the strong `names_any_of` grader would
   fail on that path.
2. The harness does not assert twin equivalence for this family (M2); the twin claim
   for PG19/PG20 rests on my manual comparison only.
3. The grid hardcodes `--rounds 1` (M3), so the open-range path is outside the whole
   47-cell population — the divergence is invisible to the suite.
4. The Git floor (`>= 2.45`) is untouched by this measurement: the host has git 2.56.0,
   so nothing here exercises the `--no-lazy-fetch` availability boundary or the rejected
   `--missing=print-info` / `--missing-only` prohibition. The inherited Git>=2.45
   prerequisite remains **open at L0**.
5. Only these two rows were exercised (by assignment). The other 45 graded rows, the
   open row PG40, the mutation probe `6e0b9d62…` and the selftest were **not** run by
   me.
6. The frozen arm was measured only for these two rows; "amended_view_met: 1/2" refers
   to this selection alone, not to the suite.
7. **Source-ledger supplement** (pinned revision): `corpus/SOURCES.md` has **105** rows,
   the last being `S103`…`S105`; **S105** records the explicit *rejected* cross-API
   inference against **S095** ("supersedes S095 — REJECTED: bytes.decode strict-default
   documentation does not establish subprocess text-mode or TextIOWrapper defaults;
   flip: cite the separately opened subprocess/io anchors (S097/S098)"), while the
   immutable **S095** row stays **filed** with status `rejected` and its original
   `teaches` cell unchanged (it still states the rejected inference). Only the mutable
   `used-by` cells were reconciled (`corpus/lessons/round-24.md:103-116` logs the
   transition table: S095 drops `tools/report-landing-audit.py`, S096 gains it). The
   final source-census verification of the 105 rows is **L1-owned after this stage** and
   is not asserted here.
8. No serving capability, no higher numeric score, no admission, integration or shipping
   judgment is asserted anywhere in this report. Read-only production throughout: the
   only production writes are this report and the out-directory artifacts listed below.

## Files written

* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/advice/CaseFleetTree.md` (this report; append-only, created fresh — the file did not exist).
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/CaseFleetTree/grid-pg19-pg20.json` (`f469a6ceb9aae29c477856e465055f1ea0117b514d2ed7a85a7f2bbad2ea8f71`) — the assigned command's `--json` output.
* `…/out/CaseFleetTree/grid-pg19-pg20.err` (`e3b0c442…`, empty) — the assigned command's stderr.
* `…/out/CaseFleetTree/verify-fleet-tree.json` (`962f1589…`) — independent re-derivation (missing/present objects, full stderr, acquisition delta, twin comparison, fixture diff).
* `…/out/CaseFleetTree/verify-nolazyfetch-fleet-tree.json` (`3cbc8a53…`) — bait-remote probe.
* `…/out/CaseFleetTree/verify-ab-nolazyfetch.json` (`0c58b8de…`) — isolated-vs-unisolated A/B control.
* `…/out/CaseFleetTree/verify-cause-isolation.json` (`64f39d75…`) — complete promisor fleet control (exit 0 clean).
* `…/out/CaseFleetTree/verify-tree-message.json` (`9fbf1f74…`) — proof the report path is inside the missing tree.
* `…/out/CaseFleetTree/verify-fixture-diff.json` (`9fc090f2…`) — field-by-field PG19↔PG20 fixture diff.
* `…/out/CaseFleetTree/verify-range-rounds.json` (`59129c99…`) — `--rounds 1` vs `--rounds 1-` vs `--rounds 10-`.
* `…/out/CaseFleetTree/verify-default-rounds.json` (`506d7f04…`) — argparse-default invocation.
* `…/out/CaseFleetTree/verify-round-selection-frozen-vs-current.json` (`7f8529c8…`) — frozen vs current across round selections (M1 baseline).
* `…/out/CaseFleetTree/verify-minimal-correction.json` (`19769a72…`) — scratch-verified minimal correction for M1.
* Scratch only (not production evidence): `/fast/scratch/hyaku/kama-r24/falsify/CaseFleetTree/` (clone, `verify_fleet_tree.py`, `probe_nolazyfetch.py`, `probe_ab.py`, `frozen-audit.py`, `out/*.json`, and the grid-owned fixture roots created by the runs).

No tool was installed or updated; no pacman/`uv`/`cargo`/`npm` transaction was performed.
No production source file was edited — the M1 correction is proposed in this report and
verified only against a scratch copy.

Report: .ufo/waves/round-24/falsify/advice/CaseFleetTree.md
