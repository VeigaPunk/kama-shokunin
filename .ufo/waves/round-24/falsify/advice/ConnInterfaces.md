# ConnInterfaces — round-24 FALSIFY lane: implementation / grid / mutation interface surfaces

Target (assignment): check implementation+grid+mutation interfaces, exact CLI args / row-kind
policy / control, original/amended columns, kill attribution and retired-old-pattern migration;
no defaults pointing at absent sources.

**Verdict: PARTIAL.** The three interfaces are internally coherent and reproduce the pinned
digests and the fixed47 manifest exactly; the amended column and the row-kind policy hold
against the shipped candidate. Nine interface defects are filed, of which three are new and
material to how a reader must interpret the round's own receipts:

- the mutation runner has a **false-green mode** (`--arm frozen`) in which *no mutant is ever
  executed* and the run still exits 0 "inventory evaluated" (N1);
- the grid **double-counts a twin mismatch** into both the live and the frozen failure lists, so
  `violations` and `violating_cases` overstate the damage (N2);
- the frozen inventory's `expect_rows` is a **whitelist only**: a mutant that does *not* break
  the cells declared for it is reported as a clean "survived" with no signal anywhere (N3).

Everything below was measured in a scratch clone at the pinned revision. No production file,
lane, index, fleet, sibling or service was touched. No network, transport or execution payload
was used; PM08 was never executed (static-only).

---

## 0. Snapshot, method, pins

- Scratch clone: `git clone --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin repo`
  → `git rev-parse HEAD` = `2e254a1763a9c08aa07fc53081287f506c447d84` (exact base observed).
- Production HEAD, read-only: `2e254a1763a9c08aa07fc53081287f506c447d84`.
- `sha256sum` (exit 0) — scratch and production agree byte-for-byte and match the assignment pins:

| file | sha256 | pin |
|---|---|---|
| `tools/report-landing-audit.py` | `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220` | source tool `ea51bc35…` ✔ |
| `tests/report-audit/promisor-grid.py` | `b034e1596746d312989b7894c0757b67859df19a476a01ccd95076424135cefa` | runner `b034e159…` ✔ |
| `tests/report-audit/promisor-grid-expectations.json` | `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1` | manifest `d86b7bea…` ✔ |
| `tests/report-audit/promisor-mutants.py` | `6e0b9d62db9fe27f6c14c6e16ce239023f699142193adff5291e4374a1bb60a2` | mutation probe `6e0b9d62…` ✔ |

- `TMPDIR` was set to `/fast/scratch/hyaku/kama-r24/falsify/ConnInterfaces/tmp` for every
  subprocess except where a different value is the subject of the measurement.
- Git isolation: the grid's `env()` (not re-verified here beyond the fixtures' behaviour) and
  `--no-lazy-fetch` on every auditor git call were exercised only through local fixtures.

---

## 1. HOLDS

### H1 — The three interfaces are the pinned bytes and the shipped tree is the pinned tree
Observed: digests above; `git rev-parse HEAD` = `2e254a1…` in scratch and production; the
scratch clone's four pinned files are byte-identical to production's.

### H2 — The frozen mutation inventory still applies to the *shipped* candidate (no retired pattern)
Command (exit 0):
`python3 tests/report-audit/promisor-mutants.py --anchors tools/report-landing-audit.py --json`

Observed: all 11 mutants report ≥1 applicable alternative and `mutant_compiles: true`
(`applicable_alternative` = 1 for PM01 and PM03, 0 for the other nine). No pattern was retired
by the L1's source change.

PM08 is correctly never executed (wave contract "never execute PM08"):
`python3 tests/report-audit/promisor-mutants.py --only PM08-remove-no-lazy-fetch-gate --case PG01-complete-lane-promisor-config --json` → **exit 0**, `status: "static-only-not-executed"`,
`reason: "--no-lazy-fetch present before=True after=True; not executed: a fixture that could reach a transport is forbidden in this wave"`.

### H3 — Row-kind policy and control vocabulary hold
Observed from the manifest and the grid: kinds = {`policy`: 30, `control`: 17} = 47 graded cells,
plus exactly one `open` row (`PG40-missing-cited-unselected-branch-object-promisor`), which the
grid excludes from `graded` (`promisor-grid.py:984`, `:1019`) and the runner excludes through
`GRADED_KINDS`. 26 manifest cells carry a `twin` link. The grid emits `kind ∈ {policy, control}`;
the runner accepts `("policy","control","fault","contract")`, so every graded cell of this grid
is graded by the runner (no silent under-grading). All 47 graded cells met the amended view
against the shipped auditor in my per-cell runs (PG01–PG39, PG41–PG48 covered in subsets;
PG40 is the open row and is never graded).

### H4 — Original/amended columns are faithful to the frozen oracle
Observed by direct comparison of `tests/report-audit/promisor-grid-expectations.json` with
`.ufo/waves/round-24/oracle-snapshot-before-inspection.json`:

- the 44 original cases are **byte-equal** to the snapshot's `cases` (44/44, zero differing
  entries);
- the shipped file adds exactly the three disclosed opaque cells `PG46`, `PG47`, `PG48`;
- the amendment map `snapshot["amendment"]["amended_rows"]` (8 entries: PG22, PG23, PG24, PG28,
  PG30, PG34, PG37=*null*, PG41) matches the shipped per-case `amended` values with **zero
  mismatches** (`PG37` correctly carries no `amended` key, i.e. "unchanged");
- the live view rule is `live = expect.get("amended", expect["original"])` and `met_original` is
  scored separately, so the withdrawn view is not graded;
- the manifest's per-case column set is `frozen / original / (amended) / reason_forbidden /
  names_any_of / twin / kind / builder / notes / policy_ref` — no case silently lacks a column
  other than `amended` where the amendment does not apply.

### H5 — The retired-old-pattern migration did not regress the mutation runner
Observed: `diff -u .ufo/waves/round-24/build/out/MutationOracle/promisor-mutants.py
tests/report-audit/promisor-mutants.py` → **exit 0, 0 diff lines** (byte-identical to the
pre-integration build copy). The runner's empty-selection guard exists in both runners
(`--only` with an unknown id → exit 2 CNE), and the r23 isolation runner keeps its 27 retained
literals with 4 retired ids and a `RETIRED` table.

### H6 — No default points at an absent source (except the one in N5)
Observed: grid `--current` has no default (required; a missing file → Premise → exit 2);
`promisor-mutants.py` defaults `--current` → `LANE/tools/report-landing-audit.py` and
`--grid` → `LANE/tests/report-audit/promisor-grid.py` (both exist);
`repo-state-grid.py` resolves `AUDIT = "tools/report-landing-audit.py"` relative to
`LANE_DIR` (`git -C LANE_DIR cat-file blob FROZEN:AUDIT`, `--current` default
`LANE_DIR/AUDIT`), so no relative-path default is resolved against the caller's cwd.
The single exception is the grid's hard-coded scratch root (N5).

---

## 2. FALSIFIED / PARTIAL interface findings

### N1 — MATERIAL — `promisor-mutants.py --arm frozen` is a false green: no mutant is ever executed
Observed (exit 0):
`python3 tests/report-audit/promisor-mutants.py --arm frozen --only PM01-blanket-metadata-refusal --case PG01-complete-lane-promisor-config --json`
→ `{"pristine": "passed", "killed": 0, "killed_ids": [], "surviving": ["PM01-blanket-metadata-refusal"], "could_not_evaluate": [], "evaluated": 1}`,
and the row: `status="survived", killed=false, grid_exit=0, failed_rows=[], attributed=true`.

Why (code): `promisor-mutants.py:467-468` always calls the grid as
`<grid> --arm <arm> --current <auditor> --json`; the grid's **frozen arm ignores `--current`**
and grades the r23 auditor read from git (`promisor-grid.py:964-966`, `:1131-1135`). In the
frozen arm the mutated file is never executed, so every mutant "survives" by construction. The
same mutant under `--arm current` is killed (`status="killed"`, exit 1 from the grid, killed=true).

Impact: the runner's own documented exit contract ("Exit: 0 the inventory was fully evaluated
(every mutant killed or surviving …)") is false for `--arm frozen`: the run reports a pristine
pass, zero kills, a survivor list and exit 0 while having exercised no mutant at all. A reader
of such a receipt cannot tell "the mutant survived the grid" from "the mutant was never run".

Minimal correction (not applied; report-only lane): reject `--arm frozen` in the mutation
runner (argparse error or a CNE exit 2 naming the mode), or map a frozen-arm run to
`could-not-evaluate` instead of "inventory evaluated". Do not change the grid's frozen arm: it
is the historical baseline the round measures against.

### N2 — MATERIAL — a twin mismatch is counted twice: `violations` and `violating_cases` overstate the damage
Observed (grid exit 1) with a local measurement fixture (a copy of the shipped auditor patched
so that a promisor-marked lane yields one extra defect — asymmetric twins; the probe is kept
in the out directory, it is not production):
`python3 tests/report-audit/promisor-grid.py --arm current --current <probe> --case PG01-complete-lane-promisor-config --case PG07-complete-lane-plain --json`
→ `violations = 5` for **two** graded rows; `violating_cases = ["PG01-…", "PG01-…", "PG07-…", "PG01-…", "PG07-…"]` (PG01 three times, PG07 twice); `twin_mismatch = ["PG01-…", "PG07-…"]`.

Why (code): `promisor-grid.py:1024-1028` appends the twin-mismatch rows to **both** failure
lists without an arm filter:

```python
live_fail   += [r for r in graded if r.get("twin_equal") is False]
frozen_fail += [r for r in graded if r.get("twin_equal") is False]
```

In a single-arm run the frozen list must be empty, so one mismatched pair contributes 2 to the
count and 4 entries to the case list (plus the genuinely unmet row). The shipped pair itself
produces no twin mismatch (`twin_mismatch` empty in all my runs), so this is latent for the
round's own candidate but live for any candidate whose marked/plain twins differ — which is
exactly the divergence the twin control exists to catch.

Minimal correction: make each list arm-local (`if r["arm"] == "current"` for `live_fail`,
`if r["arm"] == "frozen"` for `frozen_fail`), and count a twin mismatch once per mismatched
pair rather than once per row of the pair.

### N3 — MATERIAL — `expect_rows` is a whitelist only: a declared target that is *not* broken is silently lost
Observed (exit 0 each):
- `… --only PM04-accept-unavailable-referenced-object --case PG46-opaque-tree-hides-cited-blob --json`
  → `status="survived", killed=false, attributed=true, unexpected_rows=[]`, although
  `PM04`'s registered `expect_rows` **declare PG46 and PG47**
  (`--list` output: `expects unmet rows: ['PG33', 'PG34', 'PG46', 'PG47']`).
- The same mutant is killed on its other declared cells:
  `… --only PM04-… --case PG33-missing-cited-blob-promisor --case PG34-missing-cited-blob-plain --json`
  → `status="killed", attributed=true, failed_rows=["PG33-…", "PG34-…"]`.

Why: `promisor-mutants.py:788-797` computes
`attributed = (not expected) or all(expected_match(f, expected) for f in failed)` — a subset
test on the *observed* failures. Nothing tests the converse (every declared target must
actually be broken), and nothing in the emitted document records "declared but not broken".
A mutant whose registered coverage silently evaporates is therefore indistinguishable from a
mutant that is genuinely redundant (e.g. `PM07-full-all-missing-gate`, which by design
"survives, and is credited with no kill": `… --only PM07-… --case PG31-missing-object-unselected-branch-promisor --json` → exit 0, `status="survived"`).

Minimal correction: add a `declared_not_broken` (or `missing_targets`) list per mutant —
`[e for e in expected if not any(expected_match(f, [e]) for f in failed)]` — and emit it; the
inventory owner can then decide per entry whether redundancy is intended. (Whether PG46 *should*
kill PM04 is a question for the inventory/manifest owner, not for this lane: PG46's refusal in
the shipped candidate is produced by the opaque-hole rule, which is PM10's target, so PM04 does
not discriminate PG46 — measured: PM10 kills PG46 with `attributed=true`, PM04 does not kill it.)

### N4 — PARTIAL — the grader computes the diagnosis and then throws it away
Observed (code + output): `promisor-grid.py:762-811` builds a `problems` list with eight
distinct, actionable messages (`"exit 2 != 2"`, `"kinds [...] != [...]"`,
`"defects [...] != [...]"`, `"reason not in class unavailable"`,
`"reason is the r23 metadata refusal"`, `"reason does not name the unavailable object"`,
`"stdout carries a verdict document"`, `"stderr does not start with could-not-evaluate:"`,
`"the audit acquired objects: [...]"`, `"traceback"`, `"timeout"`, `"harness leak"`), and
`run_case` uses it only as a boolean (`obs["met_amended"] = not grade(...)`). The emitted row
carries no `problems` key (observed row keys: `arm, case, defects, document, exit, expectation,
expected_exit, expected_kinds, kind, kinds, leaked, met, met_amended, met_amended_frozen,
met_frozen, met_original, objects_acquired, raw_defects, raw_kinds, row_class, stderr_tail,
timed_out, traceback, twin`).

Consequence: the grid's own JSON cannot say *why* a row was unmet, and the mutation runner's
`failed_row_detail` (which copies only `case, kind, exit, expected_exit, kinds, expected_kinds,
twin_equal, objects_acquired, stderr_tail`) cannot either. Sibling lane ConnMetrics §3.2
already records the consequence ("the exit-2 form check is not re-derivable"); this lane adds
that the missing information exists **one line away** in the grader.

Minimal correction: keep the list — `obs["problems"] = problems` in `grade`'s caller (or return
it alongside the boolean) — and let `failed_row_detail` carry it. No change to the manifest,
the auditor or the pass/fail semantics.

### N5 — PARTIAL — the grid's scratch default is a hard-coded absolute wave path, and a missing scratch root is reported as a grading failure
Observed:
- `promisor-grid.py:54` `SCRATCH = Path("/fast/scratch/hyaku/kama-r24")`; `make_root()`
  (`:1114-1125`) silently **discards** a TMPDIR that is not under `SCRATCH`
  (`base = None`), so `TMPDIR=/tmp python3 tests/report-audit/promisor-grid.py --arm current --case PG01-complete-lane-promisor-config --json` → **exit 0** with the fixture tree created
  **under the wave root**, not under the caller's TMPDIR and not under the caller's lane.
- A scratch root that does not exist is an unhandled `FileNotFoundError`:
  `TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/ConnInterfaces/nope python3 tests/report-audit/promisor-grid.py --arm current --case PG01-complete-lane-promisor-config --json`
  → **exit 1** with a Python traceback (`_os.mkdir … FileNotFoundError`), i.e. the documented
  "2 harness/premise/unavailable input" becomes "1 mismatch/violation". The mutation runner
  absorbs this correctly (same command through `promisor-mutants.py` → **exit 2**,
  "could-not-evaluate: pristine grid rc=1 …"), so only direct grid invocation is affected.

Minimal correction: default the root to `tempfile.gettempdir()` (honouring an existing TMPDIR),
keep `/fast/scratch/...` as an optional override, and wrap `mkdtemp` in `try/except OSError →
raise Premise(...)` so an absent root is exit 2, not exit 1 + traceback.

### N6 — PARTIAL — exact CLI vocabulary: the cell selector needs the full case name, the mutant selector needs the full slug, and a caller typo is reported as a pristine-grid failure
Observed:
- `python3 tests/report-audit/promisor-grid.py --arm both --case PG01 --json` → **exit 2**,
  `could-not-evaluate: unknown case(s): PG01`. The full name works
  (`--case PG01-complete-lane-promisor-config` → **exit 0**).
- `python3 tests/report-audit/promisor-mutants.py --only PM01 --case PG01 --json` → **exit 2**,
  `could-not-evaluate: pristine grid rc=2 could-not-evaluate: unknown case(s): PG01 unmet=[]`
  — the pristine candidate is blamed for the caller's selector typo (the pristine grid never
  ran a case).
- `python3 tests/report-audit/promisor-mutants.py --only PM01-blanket-metadata-refusal --case PG15 …` → **exit 2**,
  `could-not-evaluate: unknown mutant id in --only` (the inventory's own prose labels are
  `PM01 … PM11`; only the long slugs are accepted, and the message does not list them — the
  r23 isolation runner's guard does).
- Documentation drift: `.ufo/waves/round-24/build/advice/MutationOracle.md:84` advertises
  `[--case PG01 ...]`, i.e. the short form the grid rejects.

Minimal correction: accept the short `PGnn` prefix in the grid's `--case` (it already resolves
prefixes elsewhere: `expected_match` in the runner), and make the runner's error messages name
the offending selector and the accepted vocabulary ("unknown case id(s) …; ids are …") instead of
attributing the failure to the pristine grid.

### N7 — OBSERVATION with chronology weight — the build-wave grid copy still contains the path-based reason relaxation that the assignment records as DECLINED
Observed: `diff -u .ufo/waves/round-24/build/out/GridOracle/promisor-grid.py
tests/report-audit/promisor-grid.py` → exit 1, **117 diff lines** (saved as
`out/ConnInterfaces/grid-prefix-vs-shipped.diff`). The removed code is exactly the
path-based relaxation:

```python
-PATH_EXPR = re.compile(r"(?:[0-9a-f]{40}|HEAD):([^\s'\"]+)")
-def names_unavailable(err, names, paths):   # accepts a path that names the object
-    … return any(m in known for m in PATH_EXPR.findall(err))
```

The shipped grid requires the reason to contain one of the resolved object ids
(`any(n and n in err for n in names)`), i.e. the strong `names_any_of` grader the assignment
pins. Consequence for the round's own receipts: the build-wave grid copy (and the
`GridOracle/candidate.json` / `population.json` produced with it) was measured under a **weaker**
grader than the shipped one, so those build-era numbers are not comparable to the shipped
grid's; and since the mutation runner is byte-identical to its build copy (H5), the
attribution drift reported by sibling mutation lanes (MutOpaque, MutUnavailable, MutOverRefusal:
`attributed=false` with unexpected `PG46` / `PG15` / `PG19`) is **grid-side**, i.e. a
consequence of the relaxation removal and the new PG46 cell, not a runner regression.

### N8 — MINOR — the mutation receipt never records the auditor digest it graded
Observed: the grid reports `auditor_sha256` per arm (e.g. `{"current": "ea51bc35…"}` — the
candidate's digest, and for a mutant run the mutant's digest), but
`grep -c auditor_sha256 tests/report-audit/promisor-mutants.py` → **0** occurrences: the runner
discards it, so a mutation receipt cannot prove which bytes were mutated and graded.

Minimal correction: record `doc["auditor_sha256"]["current"]` (and the pristine candidate's
digest) in each mutant entry.

### N9 — MINOR — the "contract" row-kind mapping is dead code, and the runner's `contract` entry is unreachable through this grid
Observed: `promisor-grid.py:849` sets `obs["kind"] = "contract" if expect.get("kind") == "policy" else "control"`, but `:981` overwrites it with `obs["kind"] = case["kind"]`. The emitted vocabulary is therefore `policy`/`control` only (observed rows: `kind: "policy"`, `row_class: "policy"`), the comment at `:847-848` ("policy rows are declared behaviour contracts") never reaches the output, and
`GRADED_KINDS = ("policy","control","fault","contract")` in the runner keeps an entry this grid
can never produce. Harmless for grading (both vocabularies are accepted downstream), but it is
exactly the "retired old pattern" shape this lane was asked to look for.

Minimal correction: delete the dead mapping at `:849` and the unreachable `"contract"` entry in
`GRADED_KINDS`, or emit the contract vocabulary deliberately.

### N10 — OBSERVATION — interrupted grid runs leave fixture trees under the wave scratch root
Observed: `ls -1d /fast/scratch/hyaku/kama-r24/promisor-grid-*` → two trees remain
(`promisor-grid-pvnuiemp`, mtime 18:26:57 today; `promisor-grid-rsuiudo7`, mtime 15:20:04,
from another lane). A normal run cleans up: before/after count unchanged (2 → 2) across a
full `--arm current --case PG01` run, and no `promisor-grid-*` remains under my lane TMPDIR.
`shutil.rmtree(root, ignore_errors=True)` sits in a `finally` (`promisor-grid.py:1082-1084`),
so only a killed/interrupted run leaks a tree. I did not delete the other lane's tree.

---

## 3. Confirmed by sibling lanes (not claimed as new here)

- The `withdrawn_original_failures` bucket is not bound to the amendment (CritOriginalWithdrawn
  F1). I reproduced the conflation independently and exactly: with the r23 auditor supplied as
  `--current` over four cells (`PG01, PG07, PG22, PG37`), the grid exits 1 with
  `violating_cases = ["PG01-…", "PG22-…"]` and
  `withdrawn_original_failures = ["PG01-…", "PG22-…"]` — identical lists, although PG01's
  original and amended views are the same (exit 0) and only PG22 is an amendment-changed cell.
- The current-arm `amended_view_met/total/unmet` counters are structurally constant (ConnMetrics
  §3.1). My independent measurement: `--arm current` over one cell →
  `amended_view_met = 0, amended_view_total = 1, amended_view_unmet = []`; over four cells →
  `0 / 4 / []`, because the counters are computed from the frozen rows only
  (`promisor-grid.py:1034-1043`).
- The twin comparator is inert for refusal twins (GateGridSelftest). My N2 is a different
  defect on the same comparator: the *counting* path, not the comparison path.
- Attribution drift for PM01/PM02/PM03/PM06/PM11 (`attributed=false` with unexpected rows)
  is reported by MutOverRefusal, MutUnavailable and MutOpaque. My measurements reproduce it
  independently (PM01 → unexpected `PG15`, `PG19`, `PG46`; PM02/PM03/PM11 → unexpected
  `PG46`; exit 0 in every case, `killed=true`, `attributed=false`).

---

## 4. Observed vs inferred

- OBSERVED (measured in this lane): every exit code, every JSON field value, the two diffs,
  the digest set, the manifest/snapshot comparison, the attribution tables, the `--arm frozen`
  behaviour, the twin-mismatch double count, the scratch-root behaviour, the CLI rejections.
- INFERRED (reasoned from code, not executed): that the pre-integration build receipt
  (`build/out/GridOracle/candidate.json`) was produced with the relaxed path-based grader — the
  relaxed code is present in that build copy, and the shipped copy has it removed; I did not
  re-run the build-wave grid.
- INFERRED: that a reader of the wave's summaries would quote `amended_view_met` as the
  candidate's score — I measured the field's value (0/N in the current arm) and the SKILL
  registry's wording, but did not observe a downstream consumer.

## 5. Unverified / out of scope

- The full 11-mutant inventory was **not** swept against the shipped pair (that is the wave's
  own measurement, and the instruction for this lane is one bounded check). I ran eight
  mutant/case-scoped invocations. Mutants I did not run over their declared cells: PM05, PM06,
  PM09 — their attribution status is therefore not claimed here.
- No claim about the production auditor's verdict semantics, the amendment's policy content, the
  Git>=2.45 prerequisite, serving capability, or any scalar score.
- No production edit was made; no report in this lane was applied to production.

## 6. Files written by this lane

- This report: `.ufo/waves/round-24/falsify/advice/ConnInterfaces.md` (append-only lane file).
- Evidence copies: `.ufo/waves/round-24/falsify/out/ConnInterfaces/` —
  `grid-prefix-vs-shipped.diff`, `mutants-prefix-vs-shipped.diff` (empty), `anchors-shipped.json`,
  `mut-PM01.json`, `mut-PM02.json`, `mut-PM03.json`, `mut-PM10.json`, `mut-PM11.json`,
  `mut-PM04.json`, `mut-PM04b.json`, `mut-PM07.json`, `mut-PM08.json`, `mut-frozen.json`,
  `grid-r23-current-subset.json`, `grid-twin-asym.json`,
  `probe-twin-asym-auditor.py` (local measurement fixture, not production), plus the captured
  stderr logs `g-a.err` (absent scratch root → exit 1 + traceback), `g-b.err` (out-of-scope
  TMPDIR silently ignored), `g-c.err` (relocated grid copy → adjacent expectations file
  missing), `m-nope.err` (the same failure absorbed by the mutation runner → exit 2) and
  `mut-shortid-PM01/02/03/11.err` (`--only PM01` → "unknown mutant id in --only").
- Heavy scratch (not in the repository): `/fast/scratch/hyaku/kama-r24/falsify/ConnInterfaces/`
  — clone `repo/`, measurement output `out/`, `tmp/` for subprocess TMPDIR.
- The frozen r23 auditor used for the withdrawn-bucket measurement was materialised read-only
  from `0df800e896f6bce285a81e794ad4ae1d1e6c3a71:tools/report-landing-audit.py`
  (sha256 `da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1`) into scratch
  only; it is not copied into the repository.

## 7. L1 dispositions (appended 2026-10-21; §§1–6 above stand unchanged)

Source: `.ufo/waves/round-24/postfix/interface-findings-contract.txt` plus L1's message in this
lane's IRC. No measurement was re-run for this section, no production file was touched, and no
claim above was edited, softened or withdrawn.

| finding | disposition | what the owner will do (contract) | this lane's position |
|---|---|---|---|
| N1 `--arm frozen` false green | **ACCEPTED** (real false green) | MutationOracle owner: reject `frozen`/`both`/other arms **before** source/pristine/grid; keep explicit `--arm current` valid; no compatibility mapping; add bounded invalid-arm canary controls, no full matrix | finding stands as filed; no objection |
| N2 twin mismatch counted twice | **ACCEPTED** (real count bug) | GridOracle owner: `violations`/`violating_cases` must count **unique** graded cases failing their graded view OR the twin constraint, **for the currently selected arm only**; an asymmetric two-cell twin must report 2 unique violating cases, never 5; do not change the twin equality criterion or the links | the 5-of-2 measurement in §2/N2 is the acceptance evidence; no objection |
| N3 `expect_rows` whitelist-only | **DECLINED** (intentional attribution envelope) | attribution-envelope semantics are kept; **no** `declared_not_broken` metric — it would conflate unexecuted / allowed / target rows; canonical recipe and primary47 unchanged | finding stays on file as an observation, dispositioned declined; the PM04-vs-PG46 observation in §2/N3 is left to the inventory/manifest owner as a question, not as a metric |
| N4 grading diagnosis discarded | **ACCEPTED** (real explanation loss) | GridOracle owner: preserve `grade()`'s actual problem messages in the row output; name the compared view (frozen for the frozen arm, amended for the current arm); add `amended_problems` for the strict comparable target in both arms; reuse the existing computed lists instead of re-comparing; no rule weakened, no frozen expectation changed | finding stands as filed; the site map (`:762-811` → `run_case`/`main` → row JSON) is available to the owner |
| N5 baked-in scratch root | **ACCEPTED** (real portability/scope bug) | GridOracle owner: remove the hard-coded `/fast/scratch/hyaku/kama-r24` root; honour the caller's TMPDIR; if an explicitly requested scratch is unavailable, fail **CNE2 before any fixture or auditor**, never fall back silently and never traceback with exit 1; with TMPDIR unset use standard temporary-directory selection; keep every per-fixture containment guard; cover requested-root honouring and unavailable-root CLI2 in normal **and** selftest modes; coordinate runtime paths so parallel seats no longer share the baked-in root | finding stands as filed; this lane's measurements (`TMPDIR=/tmp` → exit 0 in the wave root; absent root → exit 1 + traceback) are the acceptance evidence |
| N6 CLI id exactness | **QUALIFIED** (full exact ids are intentional) | no short-ID aliases; active examples use the full exact IDs; a caller typo remains CNE2; the historical invalid shorthand advice is retained and qualified, not re-badged as an API change | the measured behaviour (grid `--case PG01` → exit 2; runner `--only PM01` → exit 2; typo blamed on the "pristine grid") stands as filed; the history/provenance qualifier is L1's |
| N7 build-wave relaxed grader | **DECLINED / already uncredited** | the build-out relaxed grader and the failed-pristine baseline receipt remain declined/uncredited; receipt-errata already identifies them | this lane's `out/ConnInterfaces/grid-prefix-vs-shipped.diff` (117 lines, the removed `PATH_EXPR`/`names_unavailable` path relaxation) is the byte evidence behind that errata; the load-bearing part of N7 for the round is that the attribution drift is **grid-side**, not a runner regression (the shipped mutation runner is byte-identical to its build copy) |
| N8 auditor digest not recorded | **ACCEPTED** (real provenance gap) | MutationOracle owner: record the actual candidate auditor digest, the grid producer digest and the pristine population/expectation digests; preserve the observed per-mutant auditor digest alongside the failed/class rows; coordinate the exact `auditor_sha256` placement with GridOracle; byte identities, reuse reads, no invented values | finding stands as filed; the grid already emits `auditor_sha256` per arm, and the runner currently drops it (0 occurrences) |
| N9 dead `contract` kind mapping | **CLEANUP accepted** | remove `run_case`'s kind translation/comment **only if** it is dead because `main` assigns the canonical manifest kind before all CLI output; preserve the actually emitted policy/control/open values and real consumers; no gratuitous schema alias change | the deadness is established in §2/N9 (`promisor-grid.py:849` overwritten at `:981`); the owner keeps the decision on "real consumers" |
| N10 leftover fixture trees | **not ours to delete except proven own paths** | obtain exact paths/attribution, preserve anything unowned, clean only proven own paths after all readers settle | exact paths and ownership basis in §7.1 below |

### 7.1 N10 — exact leftover paths and ownership basis

Two `promisor-grid-*` trees exist under the baked-in root `/fast/scratch/hyaku/kama-r24`
(observed by `ls -1d`/`stat`/`find`; read-only inspection):

**A — proven own by this lane** (may be removed by the owner after readers settle; not removed
by this lane, because the contract conditions the cleanup on the readers having settled):

- path: `/fast/scratch/hyaku/kama-r24/promisor-grid-pvnuiemp`
- birth = mtime = ctime = `2026-10-21 18:26:57.759200238 -0300`
- content: `current/000/lane`, `current/000/fleet` — one case, current arm, **no**
  `frozen-audit.py`;
- fixture identity (read-only `git config --list` on the fixture): lane repo has
  `remote.origin.promisor=true` and `extensions.partialclone=origin` with
  `remote.origin.url=…/promisor-grid-pvnuiemp/current/000/absent-remote.git`, no filter remote
  and no marker files; the fleet repo carries no promisor config — i.e. exactly the
  `PG01-complete-lane-promisor-config` fixture;
- ownership basis: (i) the timestamp lies inside this lane's active window (this lane's scratch
  root was created `2026-10-21 16:46:28.300693552`, last written `19:12:22`) and after the
  build wave closed; (ii) the content shape (a single current-arm case, no frozen auditor
  material) matches the **one** grid invocation of this lane whose TMPDIR fell outside the
  baked-in root — `TMPDIR=/tmp python3 tests/report-audit/promisor-grid.py --arm current --case
  PG01-complete-lane-promisor-config --json` (exit 0), which is why the tree landed in the wave
  root; every other grid invocation of this lane set TMPDIR under
  `/fast/scratch/hyaku/kama-r24/falsify/ConnInterfaces/tmp` and left no tree there (verified:
  `ls -1d …/tmp/promisor-grid-*` → empty).

**B — NOT this lane's; another seat's, preserved, must not be deleted by this round:**

- path: `/fast/scratch/hyaku/kama-r24/promisor-grid-rsuiudo7`
- birth = mtime = ctime = `2026-10-21 15:20:04.202883204 -0300`
- content: `frozen/000/lane`, `frozen/000/fleet` **and** `frozen-audit.py` — a frozen-arm run
  that materialised the frozen auditor blob;
- ownership basis: the birth time precedes this lane's scratch root (`16:46:28`) by more than an
  hour and falls inside the build wave's window (`build/out/GridOracle/candidate.json` 15:17,
  `build/out/GridOracle/promisor-grid.py` 15:33), and the frozen-arm shape with a materialised
  `frozen-audit.py` matches a frozen-baseline measurement rather than any invocation of this
  lane (this lane never ran `--arm frozen` except the single N1 probe at 19:10, which left no
  tree — `mut-frozen.json` is in the out directory and no tree of that shape exists);
- disposition: **preserved**. It belongs to the build-wave seat that produced it; this lane does
  not delete it, and the owner is asked to route it to that seat rather than remove it as part
  of the N5 cleanup.

Honest limit of the basis: timestamps plus fixture shape are strong but are not per-process
identifiers. The inference is stated as such. The one alternative producer of a
`promisor-grid-*` tree in the wave root at that second would have had to run a single current-arm
PG01 fixture with an out-of-scope TMPDIR; no other such tree exists in the root.

---

## 8. N10 qualification and correction (appended 2026-10-21; §7.1 above stands as filed, its wording is corrected here)

Source: L1 (KamaR23-2) message in this lane's IRC plus the GridOracle W1 seat's own transcript.
No re-run, no new measurement, no deletion, no production edit. §7.1's text is preserved above;
this section qualifies it.

### 8.1 Correction — B is this project's own W1 (build-wave) seat, not another project's lane
L1 reports that the **GridOracle W1 seat has the exact own transcript** for
`/fast/scratch/hyaku/kama-r24/promisor-grid-rsuiudo7`: an `--arm frozen … PG29 --keep` run whose
JSON recorded the root path, with the frozen bytes and the fixture tree left in place. The
`--keep` flag is exactly the switch that suppresses the grid's cleanup and records
`doc["grid_root"]` (`promisor-grid.py:930`, `:1082-1085`), which is why that tree exists.

Accordingly, two statements in §7.1 are too strong and are corrected here:

1. §7.1 said B was "NOT this lane's; another seat's … must not be deleted by this round" and
   implied "another project lane". The accurate statement is: **B belongs to this project's own
   build wave (GridOracle W1), proven by that seat's own `--keep` transcript** — it is not a
   foreign project's artifact, and it must not be swept as "unowned" either. Both trees stay
   untouched until all readers settle.
2. §7.1's exclusion argument for B used "this lane's scratch root was created 16:46:28" as an
   activity-window boundary. That timestamp is **this seat's scratch-directory creation time,
   not the r24 wave's start** (the wave began earlier), so it could not exclude an earlier
   project seat's run. The exclusion argument is withdrawn; the W1 transcript replaces it.

### 8.2 Qualification — A is *probably* this seat's, but no `--keep` receipt exists from this seat
L1 asks for the exact command (with `--keep`) and a path receipt for
`/fast/scratch/hyaku/kama-r24/promisor-grid-pvnuiemp` from this seat's own transcript/artifacts.
The honest answer, after searching this seat's retained artifacts and transcript:

- **No `--keep` receipt exists from this seat.** `grep -rl "pvnuiemp"` over
  `/fast/scratch/hyaku/kama-r24/falsify/ConnInterfaces/` and over
  `.ufo/waves/round-24/falsify/out/ConnInterfaces/` → **no hits**; none of this seat's grid JSON
  artifacts contains a `grid_root` field (the field the grid emits only under `--keep`); the
  retained transcript for this seat contains no `--keep` invocation of mine (the only `--keep`
  occurrence is L1's message about the W1 seat). I therefore cannot produce the requested
  `--keep` command for A, and I do not assert one.
- **The exact command this seat can attest that could have produced a root in the wave root with
  A's shape** (one current-arm case, no `frozen-audit.py`): because the grid *discards* a TMPDIR
  that is not under the baked-in root (`promisor-grid.py:1114-1125`), only an out-of-scope
  TMPDIR puts the root under `/fast/scratch/hyaku/kama-r24`. This seat ran exactly that, twice,
  from `/fast/scratch/hyaku/kama-r24/falsify/ConnInterfaces/repo`:

  `TMPDIR=/tmp python3 tests/report-audit/promisor-grid.py --arm current --case PG01-complete-lane-promisor-config --json` → **exit 0**
  (first occurrence: the N5 measurement, §2/N5; second occurrence: the cleanup test, which left
  **no** new tree — before = 2, after = 2).

  Because the second, identical invocation left no tree, this command is **not proven** to be
  the producer of A; and a surviving tree without `--keep` means the producing process never
  reached the cleanup (`finally: shutil.rmtree(root, ignore_errors=True)`), i.e. it was killed or
  interrupted. (Read-only git object files are **not** an explanation here: A has 50 directories,
  all writable, and 15 read-only files — `unlink` of a read-only file inside a writable
  directory succeeds, so the best-effort rmtree would have removed the tree.)
- **The path receipt A itself carries** is self-referential: the fixture's
  `remote.origin.url` = `/fast/scratch/hyaku/kama-r24/promisor-grid-pvnuiemp/current/000/absent-remote.git`,
  plus the fixture identity (lane repo `remote.origin.promisor=true` + `extensions.partialclone=origin`,
  no filter remote, no marker files; fleet plain) = `PG01-complete-lane-promisor-config`.
- **Residual uncertainty, stated rather than closed:** A may be an interrupted run of this same
  seat from the earlier part of this session (that transcript portion is no longer retained
  verbatim — `history://KamaR23-2.ConnInterfaces` returns only the recent turns), or a run of
  another seat using the same case with `--keep`/an out-of-scope TMPDIR. Timestamp and shape
  alone are not per-process identifiers. §7.1's wording "**proven own by this lane**" is
  therefore **downgraded to "probable, receipt pending"** by this section; §7.1's text is left
  in place above as filed.
- **Action taken by this seat: none.** A and B are both untouched; no deletion was performed or
  scheduled by this lane; cleanup waits for all readers per the contract.

### 8.3 Side observation for the N5 owner (report-only, not a new finding)
The grid's fixture-root hygiene is asymmetric with its new portability requirement: `--keep`
records the root but suppresses cleanup, and without `--keep` the cleanup is best-effort
(`ignore_errors=True`) and is skipped entirely if the process dies. Under the N5 fix
(caller TMPDIR honoured, no baked-in root, CNE2 before any fixture when the requested scratch is
unavailable), the same kill-before-cleanup path can still strand a fixture tree; the owner may
want an explicit cleanup report in the CNE/timeout paths. Not exercised here — no re-run was
performed.

---

Report: .ufo/waves/round-24/falsify/advice/ConnInterfaces.md
