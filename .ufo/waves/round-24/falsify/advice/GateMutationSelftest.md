# GateMutationSelftest — round-24 falsification of `promisor-mutants.py --selftest`

**Verdict: PARTIAL.** Every required CLI status rule of the runner **holds** (0 = inventory
evaluated, 2 = could-not-evaluate; twin mismatches counted; leak/timeout credited nothing;
no `--baseline` flag; compilation failure = CNE). **No required rule was falsified.** Two
defects were found: one **provenance defect in the committed mutation-sensitivity evidence**
(high) and one **false-negative static check on PM08** (medium); plus two selftest coverage
gaps (medium/low) that leave two claimed branches unproven.

Scope respected: only `promisor-mutants.py --selftest` and its own stub grid were executed.
**No all-mutants sweep was run** (the runner was never pointed at the real promisor grid),
no repository fixture, no network/transport payload, no production mutation.

---

## 1. Environment and provenance

| Item | Value |
|---|---|
| Scratch clone | `/fast/scratch/hyaku/kama-r24/falsify/GateMutationSelftest` (`git clone --no-hardlinks`) |
| Observed base | `2e254a1763a9c08aa07fc53081287f506c447d84` (detached; `git rev-parse HEAD` = `2e254a1763a9c08aa07fc53081287f506c447d84`) |
| Tool under test | `tests/report-audit/promisor-mutants.py` |
| Tool sha256 | `6e0b9d62db9fe27f6c14c6e16ce239023f699142193adff5291e4374a1bb60a2` (matches the mutation-probe digest quoted in the round-24 contract, and is byte-identical to `production/tests/report-audit/promisor-mutants.py`) |
| Python | 3.14.8 |
| TMPDIR | `/fast/scratch/hyaku/kama-r24/falsify/GateMutationSelftest/tmp` (all temp/scratch under `/fast/scratch/hyaku/kama-r24/falsify/GateMutationSelftest`) |
| Production tree | untouched — `git status --short` in `/home/vgpnk/Projects/shokunin/kama-shokunin` shows only the untracked `?? .ufo/waves/round-24/falsify/` (this lane's own output area) |

## 2. Required checks — command / exit / finding

| # | Requirement | Command | Exit | Finding |
|---|---|---|---|---|
| 1 | selftest runs and is green | `python3 tests/report-audit/promisor-mutants.py --selftest` | **0** | stdout `selftest cases=11 failed=0`; deterministic across 2 repeats; no repo/network touched (1.2 s wall) |
| 2 | no `--baseline` flag | `python3 tests/report-audit/promisor-mutants.py --baseline` | **2** | argparse: `error: unrecognized arguments: --baseline`. The flag is absent from the runner at every commit in repo history (`git log --all -S'baseline_mode' -- tests/report-audit/promisor-mutants.py` → empty) |
| 3 | 0 = inventory evaluated | runner on stub grid, mode `ok` | **0** | `mutants=11 evaluated=11 killed=0 cne=[]` — 10 grid mutants survived, PM08 `static-only-not-executed` |
| 4 | unmet graded row ⇒ kill, still exit 0 | mode `unmet` | **0** | `killed=10`, every grid mutant `failed_rows=['PG01']`; `evaluated=11`, `cne=[]` |
| 5 | **twin mismatch counted as kill** | mode `twin` (row `twin_equal=False`) | **0** | `killed=10`, `failed_rows=['PG01']` for every grid mutant — the twin mismatch **is** counted, not ignored |
| 6 | no credit on grid exit 2 | mode `exit2` | **2** | `killed=0`, `cne=[10 grid mutants]`, `evaluated=1` (PM08 only) |
| 7 | no credit on rc1 with no rows | mode `rc1_no_rows` | **2** | `killed=0`, reason `grid exit 2: grid JSON carries no rows` |
| 8 | **no leak credit** | mode `leak` (`harness_leaks` + row `leaked=True`) | **2** | `killed=0`, reason `grid: grid arm reported harness_leaks` |
| 9 | **no timeout credit** | mode `timeout_row` (row `timed_out=True`) | **2** | `killed=0`, reason `grid: row PG01 timed out` |
| 10 | failing pristine ⇒ nothing attributed | mode `pristine_fails` | **2** | stderr `could-not-evaluate: pristine grid rc=1 unmet=['PG01']`; **no JSON verdict emitted**, no kill |
| 11 | rc1 with an ungraded row ⇒ CNE | extra stub mode (mine, offline) | **2** | reason `grid exit 1 without an identifiable violated row` — the branch works, but see F3 |
| 12 | **compilation failure ⇒ CNE** | runner with `--current broken.py` | **2** | `evaluated=0`, all **11** mutants `could-not-evaluate`; 5 by `the mutant does not compile (alternative N)`, 6 by `no alternative applied cleanly` |
| 13 | `--anchors` status rules | `--anchors broken.py` → **2**; `--anchors candidate.py` → **0** | 2 / 0 | both as required |

Evidence file: `.ufo/waves/round-24/falsify/out/GateMutationSelftest/selftest-cli-status-observation.txt`
(reproducer: `.ufo/waves/round-24/falsify/out/GateMutationSelftest/observe.py`; it imports the
tool module and reuses its own `STUB_GRID`/`CANDIDATE`, so it exercises the shipped fixtures
without copying them by hand).

Observed vs inferred: rows 1–13 are **observed** (executed, exit codes captured). The
"no all-mutants sweep" constraint was honoured: the real grid
(`tests/report-audit/promisor-grid.py`) was never used as `--grid`; only the in-memory stub
and my one extra stub mode were.

## 3. Findings, by severity

### F1 — HIGH (provenance): the committed mutation-sensitivity evidence cannot have been produced by the committed runner

`.ufo/waves/round-24/build/out/MutationOracle/sensitivity-promisor-grid.json` (landed at
`2e254a1`) carries:

```json
"baseline_mode": true,
"pristine": "failed rc=1",
"pristine_unmet_cells": ["PG15-missing-lane-tree-promisor", "PG16-missing-lane-tree-plain",
                         "PG19-missing-fleet-tree-promisor", "PG20-missing-fleet-tree-plain",
                         "PG46-opaque-tree-hides-cited-blob"],
"killed": 9, "surviving": ["PM07-full-all-missing-gate"], "could_not_evaluate": []
```

None of these keys/semantics exist in the committed runner (`6e0b9d62`):

* the runner emits **no** `baseline_mode`, **no** `pristine_unmet_cells`, and **no** `evaluated`
  key is absent from the artifact while the runner always emits `evaluated`
  (`promisor-mutants.py:804-810`);
* the runner's `pristine` field is the constant `"passed"` — it is never `"failed rc=1"`;
* the runner **returns 2 and writes no JSON at all** when the pristine grid fails
  (`promisor-mutants.py`, `if rc != 0: ... return 2`), and its kill rule states: *"the pristine
  candidate does not meet the grid … the whole run is could-not-evaluate, no mutant is
  attributed, no kill is credited"* (docstring, "Kill rule");
* `git log --all -S'baseline_mode' -- tests/report-audit/promisor-mutants.py` is **empty**: the
  string never existed in the committed file at any revision (the file was introduced at
  `ed1cc3a` already without it).

The committed stderr `build/out/MutationOracle/sensitivity-promisor-grid.err`
(`pristine grid rc=1; baseline mode: unmet cells are reported, not attributed to a mutant`)
belongs to the same unreproducible runner revision.

**Consequence for the wave.** The artifact attests 9 kills obtained **while the pristine
candidate did not meet the grid** — precisely the attribution the round-24 kill rule forbids.
Re-run against the committed runner, that same grid state is a whole-run **CNE with zero kills
credited** (`pristine rc=1` ⇒ exit 2, no mutant attributed). The 9 kills are therefore
unattributable under the committed rules, and the artifact must not be cited as the
mutation-sensitivity measurement of the current runner.

**Minimal correction (not applied — production not edited).** Re-generate the mutation
sensitivity artifact with the committed runner (`6e0b9d62`) and land that JSON/`.err` pair
replacing the baseline-mode pair; or, if the artifact is to be retained for history, mark it
explicitly as produced by an out-of-tree runner revision whose rule differs (baseline mode),
so it is never read as evidence for the current kill rule. L1 owns this decision.

### F2 — MEDIUM: PM08's static check is a false negative (`static_after` reports the gate still present after it was removed)

PM08 is the `static-only` mutant ("remove the `--no-lazy-fetch` gate"). The runner reports
`static_before`/`static_after` by substring test (`promisor-mutants.py`, static-only branch:
`present_before = marker in source` / `present_after = marker in applied`).

`tools/report-landing-audit.py` contains **4** occurrences of the marker `--no-lazy-fetch`:
the real flag in `GIT_ISOLATION` (L138) plus three prose mentions (L60, L137, L660). The PM08
mutation (`replace` alternative 0, `'"--no-lazy-fetch",\n                 '`) removes the **flag
element**; the quoted literal count goes **1 → 0** and `GIT_ISOLATION` no longer carries
`--no-lazy-fetch`. The three prose mentions survive, so the substring test reports
`static_after=True`.

Observed values (my static measurement against the pinned auditor):

```
occurrences of '--no-lazy-fetch' in auditor: 4
quoted literal count before: 1  after: 0
marker substring count before: 4  after: 3
applied alternative: 0 | compiles: True
```

The committed artifact carries exactly this misleading pair:
`--no-lazy-fetch present before=True after=True` (`sensitivity-promisor-grid.json`, PM08 row).

**Impact.** Bounded: PM08's `status` is unconditionally `static-only-not-executed` and
`killed=False`; **no kill or exit-code credit is affected** (no false kill is credited, so the
"no leak/timeout credit" and "no false credit" properties hold). What is wrong is the reported
observation: a reader cannot tell that the mutation *did* remove the gate, and the field reads
as if PM08 were a no-op. If the field is ever used as evidence that the gate is (or is not)
load-bearing, it is unsound.

**Minimal correction (not applied).** Make the check observe the flag rather than the prose:
test the quoted literal `"--no-lazy-fetch"` (1 → 0), or compare occurrence counts
(4 → 3), or strip comments before the membership test. Cheapest faithful form: report both
`static_after_literal` and `static_after_marker`, or reuse the mutation's own effect
(`source.count(marker) - applied.count(marker)`) instead of a bare `in` test.

### F3 — MEDIUM: the selftest leaves two claimed branches unproven, and asserts no kill counts

The shipped selftest (`promisor-mutants.py:983-1053`) asserts **exit codes** and, for the
CNE modes, that `doc["killed"]` is falsy. Two gaps against the requirements it is supposed to
certify:

1. **Twin-mismatch counts are not asserted.** The `unmet` and `twin` cases only check
   `exit == 0`. They never assert `killed >= 1`, nor that `failed_rows` contains the
   twin-mismatched row. A regression that kept the exit code but stopped crediting the
   twin-mismatch row (e.g. `violated_rows` losing the `twin_equal is False` clause while some
   other row still keeps `bad` non-empty) would pass the selftest unchanged. The behaviour is
   **verified correct by my harness** (mode `twin`: `killed=10`, `failed_rows=['PG01']`), but
   the selftest does not pin it.
2. **The `rc1_no_rows` case does not exercise the branch its label names.** The label reads
   *"grid exit 1 without a violated row is CNE"*, but the stub emits `"rows": []`, which
   `run_grid` short-circuits earlier (`if not rows: return 2, …, "grid JSON carries no rows"`).
   The distinct branch `if mrc == 1 and not bad:` → *"grid exit 1 without an identifiable
   violated row"* is **never taken** by the shipped selftest. I exercised it with one extra
   offline stub mode (grid exits 1 with an ungraded `kind:"open"` row): the runner correctly
   returns **2** with reason `grid exit 1 without an identifiable violated row`. So the
   behaviour holds; the *test* does not cover it.
3. Related, low: a whole-grid **timeout** (as opposed to a row-level `timed_out` marker) is
   correct by inspection (`run_grid` returns rc=2 → CNE) but is likewise not covered — the
   stub never hangs.

**Minimal correction (not applied).** Add a stub mode that exits 1 with a non-graded row and
expect exit 2; assert `doc["killed"] >= 1` and the `failed_rows` membership for the `unmet`
and `twin` cases; optionally assert `doc["evaluated"] == doc["mutants"] - len(cne)`.

### F4 — LOW: the stub's pristine/mutant discrimination is an unchecked filename convention

`STUB_GRID` decides "pristine vs mutant" by `not os.path.basename(current).startswith("PM")`.
The runner writes mutants as `<mutant id>.py`, and every current id starts with `PM`, so it
works today. But the selftest never asserts that invariant. If a future mutant id did not
start with `PM`, every mutant-mode stub case would silently degrade to the *pristine* branch:
the `twin` and `unmet` cases would then produce no kill and still exit 0 — i.e. the selftest
would keep passing while certifying nothing. **Minimal correction (not applied).** Assert
`all(m["id"].startswith("PM") for m in MUTANTS)` in the selftest, or key the stub off an
explicit marker file instead of a name prefix.

### F5 — LOW / informational: the pristine-failure case's "no kill" assertion is vacuous

In the `pristine_fails` case the runner returns 2 *before* writing its JSON, so the selftest's
parsed `doc` is empty and `doc.get("killed")` is `None` regardless. The check cannot fail.
Harmless in practice (that code path returns before any kill logic), but the assertion carries
no signal. Also noted: `pristine_fails` returns exit 2 **with no JSON verdict at all**, which
matches the supplement-2 expectation that a CNE emits no JSON verdict.

## 4. Requirements status table

| Requirement (assigned) | Status | Evidence |
|---|---|---|
| actual CLI status rules: 0 = inventory evaluated, 2 = CNE | **HOLDS** | rows 1, 3–12 above |
| twin mismatch counts | **HOLDS behaviour** (killed=10, `failed_rows=['PG01']`); **not pinned by the selftest** (F3.1) | mode `twin` |
| no leak/timeout credit | **HOLDS** (killed=0, exit 2 in both) | rows 8, 9 |
| no `--baseline` flag | **HOLDS in code**; **VIOLATED by the committed evidence artifact** (F1) | row 2; `sensitivity-promisor-grid.json` |
| compilation failure ⇒ CNE | **HOLDS** (exit 2, all 11 mutants CNE, `evaluated=0`) | row 12 |
| no all-mutants sweep | **HONOURED** — only `--selftest` + stub grid executed | §2 |

## 5. Residual risk and verification gaps

* **The real grid was not exercised** (forbidden: no all-mutants sweep). Whether the runner
  kills PM01–PM11 against the real `promisor-grid.py` under the committed kill rule is
  **unverified here**; F1 shows the only committed evidence of that (9 kills) was obtained
  under a rule the committed runner does not implement, so the mutation-sensitivity claim is
  currently **unproven** for the pinned revision.
* F1 and F2 are static/provenance findings; no production file was edited, as instructed.
* The `--anchors` path was exercised only against the synthetic candidate and the broken
  candidate, not against the real auditor — the real-auditor anchor census for PM01–PM11 is
  **not** part of this lane's scope.
* Inherited prerequisite still open at L0 (Git ≥ 2.45 floor) — untouched by this lane; the
  selftest needs no git at all.
* No tool was installed or updated by this lane (no `pacman`, `uv`, `cargo`, `npm` action);
  only stock `python3` 3.14.8 and `git` from the host were used.

## 6. Files written

* `.ufo/waves/round-24/falsify/advice/GateMutationSelftest.md` (this report)
* `.ufo/waves/round-24/falsify/out/GateMutationSelftest/selftest-cli-status-observation.txt`
* `.ufo/waves/round-24/falsify/out/GateMutationSelftest/observe.py` (reproducer)

Scratch-only (not part of the deliverable, under `/fast/scratch/hyaku/kama-r24/falsify/GateMutationSelftest`):
clone at detached `2e254a1`, `tmp/harness/observe.py`, `tmp/harness/stub-grid*.py`,
`tmp/harness/candidate.py`, `tmp/harness/broken.py`.

---

## 7. Addendum (appended after a peer's fixture-hazard report) — F1 gains an independent mechanism

Peer `KamaR23-2.CaseFleetBlobless` reported (and I confirmed **statically**, no execution):
the grid's **blobless** fixture keeps `remote.origin.url` pointing at a **reachable local
`file://` origin**, so a git probe *without* `--no-lazy-fetch` lazy-fetches and materialises the
missing blobs; the premise evaporates and the auditor can return a false **exit 0 "clean"**
where the correct verdict is exit 2.

Static confirmation at the pinned base (`2e254a1`, scratch clone, read-only):

* `tests/report-audit/promisor-grid.py:214-224` `blobless_clone()` runs
  `git clone --filter=blob:none --no-checkout file://{origin}` — the resulting clone's
  `remote.origin.url` is a **reachable** `file://` remote, so the exposure is structural;
* contrast `promisor-grid.py:197-202` `mark_config()`, which points `remote.origin.url` at
  `absent-remote.git` — that fixture family is **not** exposed (a lazy fetch there fails rather
  than materialises);
* the grid's own helpers are safe, as the peer stated: `git()` prefixes `--no-lazy-fetch`
  (`promisor-grid.py:111`) and `missing_objects` uses
  `["git", "--no-lazy-fetch", "--no-replace-objects", …]` (`promisor-grid.py:304`).

**This lane is unaffected** (no exposure of my own findings): the mutation runner never invokes
git against a fixture — it only spawns the grid; the auditor carries `--no-lazy-fetch` on every
call (`tools/report-landing-audit.py:138`, applied at `:162`); the only git calls inside the
runner are PM01's inserted `git -C repo config --null --list` and
`git -C repo rev-parse --git-path objects/pack`, neither of which reads objects and therefore
neither can materialise a blob. My selftest executed **zero** git commands and **zero** fixtures.

**Why it matters for F1.** The committed artifact's `pristine_unmet_cells` are exactly the
evaporable classes — `PG15-missing-lane-tree-promisor`, `PG16-missing-lane-tree-plain`,
`PG19-missing-fleet-tree-promisor`, `PG20-missing-fleet-tree-plain`,
`PG46-opaque-tree-hides-cited-blob`. A single stray probe of a `--keep`ed blobless fixture
between the pristine run and the mutant runs can therefore flip a would-be exit-2 refusal into
exit-0 clean and silently change the kill set. This is a **second, independent** reason (besides
the unreproducible `baseline_mode` semantics already recorded in F1) why the committed
mutation-sensitivity artifact must not be cited as the measurement of the runner at this
revision. It is a fixture-provenance hazard in the harness, **not** a defect in
`promisor-mutants.py`, and nothing was edited.

**Unverified (unchanged):** whether the committed artifact's run was actually contaminated by
such a probe cannot be determined from the artifact — it carries no probe log. This stays with
L1: re-running the sensitivity measurement must use `--no-lazy-fetch` for every probe, and any
`--keep`ed blobless fixture must not be inspected with a plain git command between runs.

Report: .ufo/waves/round-24/falsify/advice/GateMutationSelftest.md
