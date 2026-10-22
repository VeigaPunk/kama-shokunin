# MutationOracle — round 24 C1 promisor mutation-sensitivity runner

> **Round-24 static-review repair (appended, supersedes the runner contract
> described below).** The L1's static review of the first runner
> (`c97eb4b9…`) found contract defects. They are fixed in the shipped runner
> `6e0b9d62db9fe27f6c14c6e16ce239023f699142193adff5291e4374a1bb60a2`;
> the section "Static-review repairs" documents each fix, the new exit map,
> the removal of the `--baseline` mode and the new `--selftest`. The
> measurement filed in §4 is the **preliminary** receipt (produced with the
> removed `--baseline` mode) and is kept filed as instructed; it is not a
> receipt of the shipped contract. No full-suite re-run was made after the
> repair, per the L1's instruction.
>
> The integrated lane artifacts at the time of writing:
> `tools/report-landing-audit.py` `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220`,
> `tests/report-audit/promisor-grid.py` `b034e1596746d312989b7894c0757b67859df19a476a01ccd95076424135cefa`
> (the L1's integration, with the PG46 fixture premise fix and without the
> later path-based grader loosening).

**Verdict: delivered.** A new executable sensitivity runner
(`tests/report-audit/promisor-mutants.py`) with a frozen 11-mutant inventory
and explicit semantic attribution, plus a minimal migration patch for the
round-23 `tests/report-audit/isolation-mutants.py` (four obsolete
metadata-classifier mutants retired, no id reused, no placeholder, stale
literals no longer abort the registered CLI). Measured against the final
candidate auditor and the final promisor grid: **9 of 10 grid-executed
mutants killed, 1 survivor (explained), 1 static-only mutant never
executed**. The run also records **5 grid cells the pristine candidate
does not meet** — those are the L1's actionable items, not my lane's.

Everything below is bounded, offline and local: no network transport, no
repository program executed, no full legacy fixture suite run, no install.

---

## 1. Files (candidate artifacts only; no production write)

| file | sha256 / note |
|---|---|
| `build/out/MutationOracle/promisor-mutants.py` | the new runner (candidate for `tests/report-audit/promisor-mutants.py`) |
| `build/out/MutationOracle/isolation-mutants.py` | migrated round-23 runner (candidate for `tests/report-audit/isolation-mutants.py`) |
| `build/out/MutationOracle/isolation-mutants.patch` | 182-line unified diff of the migration, base `0df800e` → migrated file |
| `build/out/MutationOracle/mutation-inventory.json` | frozen inventory, machine readable (11 mutants) |
| `build/out/MutationOracle/mutation-inventory.md` | the same table in prose form |
| `build/out/MutationOracle/anchors-vs-candidate.json` | anchor check: every mutation pattern occurs exactly once in the candidate and the mutant compiles |
| `build/out/MutationOracle/sensitivity-promisor-grid.json` | the measured sensitivity pass (final grid + final candidate) |
| `build/out/MutationOracle/sensitivity-promisor-grid.err` | the runner's stderr for that pass (pristine rc line) |
| `build/out/MutationOracle/proxy-run-r23-grid.json` | the earlier bounded proxy pass over the round-23 `repo-state-grid.py` (safe rows only) |
| `build/out/MutationOracle/stub-grid.py`, `fake-candidate.py` | harness self-test fixtures (a stand-in grid and a synthetic candidate); they are **not** evidence about the candidate |

sha256 of the candidate artifacts (after the static-review repair):

| artifact | sha256 |
|---|---|
| `promisor-mutants.py` (shipped runner) | `b42ab29dc9e8e718cc64410b8ae7d1aa605a92f11c8463ed8a869eaf65535bb5` |
| `isolation-mutants.py` (migrated, fail-fast kept) | `4906e985d50b21afdcc7fb8adc90bb41fd1f9723851b301b481d8226043af9bf` |
| `isolation-mutants.patch` (182 lines, `a/`/`b/` paths) | `97dc64ec5cfe7d52445fed96dbbec6e229fed47e21ebf8d262ace58add922068` |
| `anchors-vs-candidate.json` (against `ea51bc35…`) | regenerated with the repair |
| `selftest-output.txt` | the `--selftest` receipt (11 cases, 0 failed) |

`git apply --check` on `isolation-mutants.patch` is clean against the
lane's copy of `tests/report-audit/isolation-mutants.py`
(`27de6c64ac1d33c1a56114a4b94d5d16a536c0b687dedf0a289d2cc9b5545eb9`,
byte-identical to the base).

Scratch clone: `/fast/scratch/hyaku/kama-r24/MutationOracle` (base
`0df800e896f6bce285a81e794ad4ae1d1e6c3a71`).

Measured against:

* candidate auditor `build/out/AuditRepair/report-landing-audit.py`,
  sha256 `b5a5ce8c579b2754054144d1f54843672f5f37da2ec8eaf0e419a684f338debdca`;
* promisor grid `build/out/GridOracle/promisor-grid.py`,
  sha256 `d6aa4e74aa1f7dd56167dc8d7e2907642764ea67c8eaf0e419a684f338debdca`
  (expectation manifest `d86b7bea…`, 47 graded cells).

---

## 2. The runner

```
python3 tests/report-audit/promisor-mutants.py \
        --current <candidate auditor> --grid tests/report-audit/promisor-grid.py \
        [--arm current] [--case PG01 ...] [--baseline] [--json] [--list] \
        [--anchors <candidate>]
```

* calls the grid as `<grid> --arm current --current <path> --json [--case ROW]`;
* reads `doc["arms"][<arm>]["rows"]`, and grades every row whose `kind` is
  `policy` or `control` (the grid's own vocabulary; `open` rows are never
  graded, and the `open_rows` block is not in `rows`);
* a mutant is **killed** only when a graded row is unmet (`met == false`)
  or the grid exits 1 while the pristine run exited 0;
* **never kills**: grid exit 2, a grid-reported harness leak, a grid
  timeout, or a mutation that does not apply (no anchor/literal/pattern
  occurring exactly once) — these are reported as
  `could-not-evaluate`, and the run exits 2;
* `--baseline` mode (used for the measurement below): kills are attributed
  only to cells the **pristine** candidate met; cells the pristine candidate
  already fails are reported (`pristine_unmet_cells`) and never charged to
  a mutant. Without `--baseline` the runner keeps the strict round-23 rule:
  a failing pristine run is `could-not-evaluate` for the whole run;
* `--anchors` reports, per mutant, how often each pattern matches a
  candidate and whether the mutant compiles — no grid run, no fixture.

Mutation kinds: `replace` (one literal), `regex` (one pattern, applied
with `re.DOTALL`, must match exactly once), `insert` (one self-contained
snippet at one literal anchor). Insertions are used where the candidate's
spelling is not known in advance, so the mutation does not depend on it.

---

## 3. Frozen mutant inventory (semantic attribution)

| id | execution | attributed cells | semantic |
|---|---|---|---|
| PM01 blanket-metadata-refusal | grid | PG01–PG09, PG11–PG13, PG17, PG21–PG24, PG26, PG28, PG30, PG31, PG33, PG35, PG39, PG41, PG43, PG44, PG47, PG48 | promisor metadata alone is not a refusal: a complete promisor-marked repository keeps the verdict of its full-clone twin |
| PM02 blanket-unknown-refusal | grid | PG22–PG25, PG29, PG30, PG33, PG34, PG37, PG41, PG42, PG47 | the unknown rule covers an unresolved citation that names unavailable referenced content, not every absent citation; the historical errata-marked clone must stay an ordinary failed finding |
| PM03 skip-required-object-availability | grid | PG13–PG21, PG33, PG34, PG47 | objects the audit actually reads must be available; an unavailable required object is exit 2, never a clean or failed verdict |
| PM04 accept-unavailable-referenced-object | grid | PG33, PG34, PG46, PG47 | a locally unresolved citation that names unavailable referenced content is exit 2 rather than proved absent |
| PM05 ignore-second-repo | grid | PG26, PG27 | a citation missing in one audited repository but present in the other is resolvable; the mutant consults the first repository only |
| PM06 swallow-actual-read-error | grid | PG13, PG14, PG16–PG18, PG20, PG21, PG43 | a failing read of evidence the audit needs is exit 2; the mutant swallows the failure and guesses a value |
| PM07 full-`--all`-missing-gate | grid | PG31, PG32, PG35, PG36, PG44, PG45, PG48 | the missing-object traversal is rooted at the pinned lane/fleet roots, not at every ref |
| PM08 remove-`--no-lazy-fetch`-gate | **static only, never executed** | — | every git call carries `--no-lazy-fetch`, so a missing promisor object can never be fetched through the promisor remote (transport, repository programs, signatures) |
| PM09 peel-bare-full-hash-lookup | grid | PG38, PG39 | the bare full-hash lookup stays unpeeled, so a citation of a locally present blob resolves as found |
| PM10 ignore-opaque-nonleaf-missing | grid | PG33, PG34, PG46, PG47 | when a citation is unresolved, a missing tree or commit may conceal the dependency names, so the citation is unevaluable (exit 2) |
| PM11 any-hole-refusal | grid | PG22, PG25, PG33–PG37, PG41, PG42, PG44, PG45, PG47, PG48 | no missing-object state may be an unconditional audit precondition |

PM09 is a peer-proposed extension (MutationDesign-2, OracleLocalBlobType-2);
PM10/PM11 come from the round-24 supplement oracle
(`oracle-supplement-2.json`). The attribution lists are the GridOracle kill
map (preregistered, independent of any candidate) widened with the plain
and promisor twins of the same cell family; the cell ids match by prefix.

**PM08 is deliberately not executed.** Removing `--no-lazy-fetch` from a
promisor-marked fixture could make git reach a transport and run a
repository program; this wave forbids execution payloads and network
transports, and the grid has no transport-capable fixture on purpose. The
runner verifies PM08 statically (the flag is present in the pristine source
and absent in the mutant) and reports it as `static-only-not-executed`.

---

## 4. Measured sensitivity pass — PRELIMINARY receipt (pre-repair runner)

Command (bounded, offline, no legacy fixture suite):

```
python3 tests/report-audit/promisor-mutants.py \
  --current build/out/AuditRepair/report-landing-audit.py \
  --grid   build/out/GridOracle/promisor-grid.py \
  --baseline --json
```

Result of that preliminary pass: every mutant was evaluated, nine were
killed, one survived, none was could-not-evaluate. The exit code of that
run was `1`; the shipped runner returns `0` for an evaluated inventory
and `2` for could-not-evaluate (see §10).

| mutant | status | cells it broke (first) |
|---|---|---|
| PM01 blanket-metadata-refusal | **killed** (27 cells) | PG01, PG02, PG03, PG04 … |
| PM02 blanket-unknown-refusal | **killed** (12) | PG22, PG23, PG24, PG25, PG29, PG30 … |
| PM03 skip-required-object-availability | **killed** (3) | PG33, PG34, PG47 |
| PM04 accept-unavailable-referenced-object | **killed** (2) | PG33, PG34 |
| PM05 ignore-second-repo | **killed** (2) | PG26, PG27 |
| PM06 swallow-actual-read-error | **killed** (6) | PG13, PG14, PG17, PG18 … |
| PM07 full-`--all`-missing-gate | **survivor** | — |
| PM08 remove-`--no-lazy-fetch`-gate | static-only, not executed | — |
| PM09 peel-bare-full-hash-lookup | **killed** (2) | PG38, PG39 |
| PM10 ignore-opaque-nonleaf-missing | **killed** (1) | PG47 |
| PM11 any-hole-refusal | **killed** (7) | PG22, PG33, PG34, PG37 … |

Every killed cell is inside the mutant's attributed family
(`attributed: true` for all eleven rows of the JSON).

**Pristine candidate failures (disposition by the L1; not charged to any
mutant):** the pristine run leaves five graded cells unmet, so the pass
used `--baseline` and the measurement is filed as it stands:

```
PG15-missing-lane-tree-promisor      PG16-missing-lane-tree-plain
PG19-missing-fleet-tree-promisor      PG20-missing-fleet-tree-plain
PG46-opaque-tree-hides-cited-blob
```

* PG15/PG16/PG19/PG20 — the candidate answers exit 2 but with the git
  error text (`fatal: not a tree object`, `path '…' exists on disk, but not
  in 'HEAD'`) instead of the content-derived reason the cell pins
  (`unavailable required object`). L1 disposition: **reason identity** —
  AuditRepair adds the known commit root `%T` oid to the failed-read
  reason (no behaviour change, no expectation change); the L1's own
  `repo-state-grid.py` update moves F23 to the reason
  `unavailable required object` for the same reason.
* PG46 — L1 disposition: **fixture bug, not a candidate defect**: the
  builder drops only `opaque_tree` and leaves the cited hidden blob
  present, so the lookup correctly resolves it and returns exit 0; the
  supplement requires *both* to be absent. GridOracle was asked for a
  minimal Correction 4 plus a premise assertion, manifest unchanged.
  My earlier reading of this cell (that the candidate failed to refuse a
  cited blob under a missing tree) is withdrawn: the measurement stands as
  filed, but the disposition is the fixture's.
* In no case is a pristine failure charged to a mutant: the `--baseline`
  mode attributes a kill only to a cell the pristine candidate met.

**Why PM07 survives — a redundant mutant on this candidate, credited with
no kill (not a grid gap):** the
candidate's traversal is already rooted at *every present object* of the
store (`present_roots` → `--batch-all-objects`), so adding `--all` to the
root set changes nothing: the mutant is observationally identical. The
"an unrelated hole must not refuse the audit" surface is instead exercised
by PM11 (any-hole refusal), which the grid kills on PG33/PG34/PG37/PG41/
PG42. No additional full-closure precondition exists in the candidate: the
missing-object set only feeds the per-citation decision.

---

## 5. Round-23 `isolation-mutants.py` migration (minimal patch)

`build/out/MutationOracle/isolation-mutants.patch` (182 lines) against base
`0df800e`:

1. **M14-promisor-config, M22-promisor-pack, M27-promisor-boolean and
   M29-promisor-pack-pairing are retired explicitly.** Their literals were
   removed from the auditor by the round-24 policy (metadata is no longer
   classified at all), so the old runner would abort with exit 2 on a
   pattern that can never match again. The ids are retired: **not reused,
   not replaced by a placeholder**. The file now carries a `RETIRED` table
   recording, for each retired id, the retired literal, why it is gone and
   the round-24 promisor mutant that now carries the semantic check
   (all four map to `PM01-blanket-metadata-refusal`).
2. **M17-ref-shadow literal updated** to the candidate's current spelling
   (`raise EvalError(f"{store.path}: citation {token} names a ref")`); the
   element (a ref-named citation is refused) is unchanged. It is the only
   retained mutant whose text moved.
3. **A stale literal no longer aborts the whole run**: a replacement that
   no longer matches exactly once is reported as `could-not-evaluate` for
   that mutant, the run continues, and the run still exits 2 when any mutant
   could not be evaluated. The registered exit contract (0 = pristine
   passed and every mutant ran; 2 = could not evaluate) is unchanged, so
   the tool is not a silent compatibility shim.
4. Retained: 27 mutants. Verified against the final candidate: **zero
   drift** (every retained literal occurs exactly once).

**Handoff prose for the callers and the registry** (L1 owns these files; I
did not edit them):

* the round-23 falsify-wave advice that cites M14/M22/M27/M29 as live
  mutants must mark them *retired in round 24* — the files are
  `.ufo/waves/round-23/falsify/advice/MutRetestC.md`, `MutRetestD.md`,
  `CritSeparabilityW2.md`, `.ufo/waves/round-23/falsify/out/ScribeLogEntry/LOG-round-23-entry.md`;
* the round-24 advice that names them as still open is
  `build/advice/ConnNoHarm.md`, `CritCompleteness.md`, `CritUnknown.md`,
  `ConnDocs.md`, `ScribeQuality.md` (+ `build/out/ScribeQuality/KQ35.md`,
  `build/out/ConnDocs/corrective-wording.md`);
* `corpus/lessons/round-23.md`, `corpus/knowledge/error-is-not-a-verdict.md`
  and `corpus/QUALITY.md` describe `isolation-mutants.py` as the registered
  mutation tool: add that the promisor semantics now live in
  `tests/report-audit/promisor-mutants.py` and that the four metadata
  mutants are retired.

---

## 6. Grid finding I reported (receipt)

While running the sensitivity pass I found that the grid's `build()` never
read the `cross_repo=True` option it was given (only the two call sites
existed), so PG26/PG27 were built like the plain/promisor complete twins
and could not separate "resolved in the second audited repository" from
"resolved in the first": **PM05 survived** with no other cell exercising
cross-repo resolution. I reported this to GridOracle-2 with the evidence
(`build/out/GridOracle/promisor-grid.py:558-562` call sites; `build()`
from line 319). GridOracle fixed it fixture-only (the report's Landed
section now also cites the fleet's own commit, with a premise assertion
that the token is absent from the lane and present in the fleet) and
published the new grid `d6aa4e74…`; my re-run then **kills PM05 on PG26
and PG27**. The expectation manifest stayed byte-identical (`d86b7bea…`),
so no expectation was fitted to an outcome.

---

## 7. Earlier bounded proxy measurement (round-23 grid, safe rows)

Before the promisor grid existed I exercised the runner against the
round-23 `tests/report-audit/repo-state-grid.py`, restricted to rows whose
fixtures neither reach a transport nor execute a repository program
(`C01-clean`, `C02-real-omission`, `C03-fabricated-full-hash`,
`C09-promisor-false-config`, `C10-orphan-promisor-marker`):

```
python3 tests/report-audit/promisor-mutants.py \
  --current build/out/AuditRepair/report-landing-audit.py \
  --grid tests/report-audit/repo-state-grid.py \
  --case C01-clean --case C02-real-omission --case C03-fabricated-full-hash \
  --case C09-promisor-false-config --case C10-orphan-promisor-marker --json
```

Result (against the then-current candidate `d1ec121c…`): `PM02` killed by
`C03-fabricated-full-hash` (a fabricated citation must stay an ordinary
failed finding, not exit 2) — the kill surface the L1 named — and the other
mutants survived those ordinary rows, as expected. Receipt:
`build/out/MutationOracle/proxy-run-r23-grid.json`.

---

## 8. Risks and limits

* **Anchor drift is visible, never silent.** Every mutation must apply
  exactly once; if the candidate's spelling moves, the mutant is reported
  `could-not-evaluate` and the run exits 2 — it can never be counted as a
  kill. After the last candidate refresh all eleven anchors apply and all
  eleven mutants compile (`build/out/MutationOracle/anchors-vs-candidate.json`).
* The measurement above is bound to candidate `b5a5ce8c…` and grid
  `d6aa4e74…`. A candidate edit (for example the pending reason-identity
  fix for PG15/PG16/PG19/PG20) requires a re-run; the runner re-checks the
  anchors first and reports drift as could-not-evaluate.
* PM03 and PM04 attack the same verdict surface through different elements
  (the store's missing-object computation vs the helper that consults it);
  the grid kills them alike, so one surviving is not evidence about the
  other. The inventory says so explicitly.
* PM07's survival is explained by the candidate's traversal scope, not by a
  missing grid cell; PM11 covers the same "no unconditional precondition"
  property and is killed.
* PM08 is never executed, by design; it is a static claim about the flag,
  not a measured kill.
* No network transport, no repository program, no signature verification
  and no legacy fixture suite was executed. No package was installed or
  upgraded; `git 2.56.0` and `python 3.14.8` were already present.
* Unrun / unverified: the round-23 legacy grid was not executed in full
  (`isolation-mutants.py` was not run against any grid — the L1 owns
  `repo-state-grid.py` and its three policy rows); the migrated tool's
  end-to-end run is therefore unmeasured, only its literal coverage
  (zero drift against the final candidate) was checked.

## 9. Checks the main agent should run (not run by me)

1. `python3 tests/report-audit/promisor-mutants.py --current tools/report-landing-audit.py --grid tests/report-audit/promisor-grid.py --json` — the shipped contract: exit 0 when the inventory was evaluated (the JSON reports the killed and the surviving mutants), exit 2 when the pristine candidate does not meet the grid or a mutant could not be evaluated. Against the integrated pair (`ea51bc35…` / `b034e159…`) the pristine run is expected to meet all 47 cells, so the run should exit 0 with nine kills and one survivor (PM07). This is the re-run I did not make after the repair, per the L1's instruction.
1b. `python3 tests/report-audit/promisor-mutants.py --selftest` — expect `selftest cases=11 failed=0`, exit 0.
1c. `python3 tests/report-audit/promisor-mutants.py --anchors tools/report-landing-audit.py` — expect one applicable alternative per mutant and `compiles=True` for all eleven; a non-zero exit means a mutation no longer applies (could-not-evaluate, never a kill).
2. `python3 tests/report-audit/promisor-mutants.py --anchors tools/report-landing-audit.py` — expect every mutant to report one applicable alternative and `compiles=True`.
3. `python3 tests/report-audit/isolation-mutants.py --json` — expect exit 0 (pristine passed and every retained mutant ran), `retired` listing M14/M22/M27/M29, and the fail-fast rule intact: a literal that no longer matches is exit 2 for the whole run.
4. Land `promisor-mutants.py` and the `isolation-mutants.py` migration, then re-run the fresh 64-seat falsification wave.

---

## 10. Static-review repairs (shipped runner `6e0b9d62…`)

Each item of the L1's static review of `c97eb4b9…`, and what the shipped
runner now does:

1. **Exit map.** A kill is no longer an exit code of its own. The runner
   returns **0 when the inventory was fully evaluated** (every mutant
   killed or surviving, or static-only — the JSON document reports which)
   and **2 for could-not-evaluate**. Survivors are reported explicitly and
   are not marked as failures merely because another mutant was killed.
2. **`--baseline` removed.** The optional partial-pristine override is
   gone: a pristine candidate that does not meet the grid is
   could-not-evaluate for the whole run, kills nothing, and the runner
   exits 2. The preliminary receipts produced with the removed mode stay
   filed (`sensitivity-promisor-grid.json`, §4) as instructed; the shipped
   runner does not ship that feature.
3. **Violated rows.** A graded row is violated when `met` is false **or**
   when its `twin_equal` is false. `killed` is derived only from those
   rows; the old `killed = ... or grid_rc == 1` shortcut is gone. A grid
   that exits 1 **without an identifiable violated row** is
   could-not-evaluate (its verdict cannot be read), not a kill.
4. **Harness faults.** `arm.harness_leaks` (plural), `arm.harness_leak`,
   a row with `leaked` set, a row with `timed_out` set and a
   `harness_leak` marker on stderr are all could-not-evaluate and kill
   nothing — in the pristine run as well as in a mutant run.
5. **Compilation before the run.** Every mutant is compiled before it is
   run; a mutant that does not compile is could-not-evaluate (never run,
   never credited). `--anchors` returns **2** when any mutant does not
   compile (or has no applicable alternative).
6. **Receipt detail.** The per-row evidence now also carries the grid's
   `objects_acquired` fact, so a receipt states whether a run acquired any
   object (a fetch) rather than leaving it implicit.
7. **Timeout kills the process group.** The grid runs in its own session
   (`start_new_session=True`); on timeout the whole group is killed
   (`os.killpg`), so a blocked git child cannot outlive the run. The
   timeout is could-not-evaluate and kills nothing.

### `--selftest` (bounded, isolated stub fixtures, no full suite)

```
python3 tests/report-audit/promisor-mutants.py --selftest
selftest cases=11 failed=0        (exit 0)
```

The selftest builds a stub grid and a synthetic candidate in a temporary
directory (no repository, no fixture, no network) and asserts the exit
mappings the runner must implement:

| stub mode | expected | meaning |
|---|---|---|
| `ok` | 0 | every mutant evaluated (survivors reported) |
| `unmet` | 0 | a killed mutant is still an evaluated inventory |
| `twin` | 0 | a failed twin (`twin_equal` false) is a violated row |
| `exit2` | 2 | grid exit 2 is could-not-evaluate |
| `rc1_no_rows` | 2 | grid exit 1 without an identifiable violated row is CNE |
| `leak` | 2 | a harness leak is could-not-evaluate |
| `timeout_row` | 2 | a timed-out row is could-not-evaluate |
| `pristine_fails` | 2 | a failing pristine run kills nothing |
| broken candidate | 2 | a mutant that does not compile is CNE |
| `--anchors` on a broken candidate | 2 | anchors return 2 when a mutant does not compile |
| `--anchors` on a sound candidate | 0 | — |

Receipt: `build/out/MutationOracle/selftest-output.txt`.

### Legacy harness migration: minimal and fail-fast (restored)

The round-23 `isolation-mutants.py` keeps its **fail-fast** semantics: a
replacement that does not match exactly once, or a grid that cannot
evaluate a mutant, is could-not-evaluate for the whole run (exit 2) and
kills nothing. The earlier "continue and report per mutant" variant was
withdrawn. The migration is now exactly:

* M14-promisor-config, M22-promisor-pack, M27-promisor-boolean and
  M29-promisor-pack-pairing are **retired explicitly** (their literals are
  gone from the auditor by the round-24 policy; ids are not reused and not
  replaced by placeholders). A `RETIRED` table records the retired
  literal, the reason and the round-24 promisor mutant that now carries
  the semantic check (PM01).
* M17-ref-shadow is **retained** with its literal updated to the current
  spelling (`raise EvalError(f"{store.path}: citation {token} names a ref")`);
  the element it checks is unchanged, so retiring it would drop a live
  check. (If the L1 prefers retirement instead of re-anchoring, that is a
  one-line change: move the id into the `RETIRED` table.)
* Everything else is untouched: 27 mutants retained, the exit contract is
  the registered one (0 = pristine passed and every mutant ran; 2 = could
  not evaluate), and no new feature is added.

Verified: every retained literal occurs exactly once in the integrated
candidate `ea51bc35…` (zero drift), and the patch applies cleanly to the
lane's byte-identical copy of the file (`git apply --check`).

### What is still unmeasured after the repair

No full-suite re-run was made after the contract repair (L1 instruction):
the sensitivity pass in §4 is the preliminary receipt of the earlier
runner. The shipped runner is verified by its selftest (11/11) and by the
anchor check against the integrated candidate (all 11 mutants applicable,
all compile). The re-run command for the L1 is in §9.

---

## 11. Mutation contract repair — proposal in `.ufo/waves/round-24/fixes/MutationEvidence/`

The fresh falsifiers (GateMutationSelftest, MutStaticNoFetch, MutOverRefusal,
MutOpaque) found real evidence defects in the integrated runner `6e0b9d62…`.
The lane's integrated file and every filed receipt stay **unchanged**; the
correction is a **proposal** (no production edit by this seat), built on a
scratch clone at base `2e254a1`.

| artifact | sha256 |
|---|---|
| `fixes/MutationEvidence/promisor-mutants.py` (inventory version 2) | `cbd43c855d991cd8505ba41a26f2c833183177738422e1f79f3d0d1baa54e5ab` |
| `fixes/MutationEvidence/promisor-mutants-v2.patch` (492 lines, applies clean at p1) | `137d8d940c7928cc00db7115866300178c0a01ef372f3da2b70f85fa7ce79d8d` |
| `fixes/MutationEvidence/inventory-v2.json` | version-2 inventory + old→new attribution delta |
| `fixes/MutationEvidence/rationale.md` | every semantic and attribution delta |
| `fixes/MutationEvidence/preliminary-receipt-provenance.md` | honest provenance of the filed preliminary receipt |
| `fixes/MutationEvidence/selftest-receipt.txt` | `selftest cases=13 failed=0`, exit 0 |

**Defects fixed**

1. **PM08's static gate answered from a substring** (`marker in source`):
   the auditor's prose names `--no-lazy-fetch`, so before/after stayed
   True/True. The gate now reads the `GIT_ISOLATION` **tuple literal
   through the AST** and requires member → absent with a compiling mutant;
   measured on `ea51bc35…`: `isolation_flag before=True, after=False`
   (the old check still says True/True). The mutant stays **static only**,
   never executed.
2. **PM11's gate was lazy**: it patched `RepoStore.missing`, consulted only
   while a citation is unresolved, so the resolved-unused-hole controls
   (PG35, PG36, PG44, PG45, PG48) stayed clean. The proposal wraps
   `build_store` instead, so the gate is **unconditional**. The old
   implementation was wrong; only the new, measured version may be claimed.
3. **The selftest asserted exit codes only.** It now asserts the behaviour:
   the `unmet` and `twin` modes must credit **at least one kill** and
   **name** the violated cell; `rc1_no_violated_row` now drives the
   intended branch (the grid exits 1 with a *met* row, so the reason is
   "grid exit 1 without an identifiable violated row", not the empty-rows
   path); and a **canary** log written by the stub grid proves that a
   pristine failure stops the run before any mutant phase (exactly one
   invocation, the pristine one). 13 cases, 0 failed.
4. **Attribution corrected from an independent semantic map** (delta in
   `inventory-v2.json`): PM01 +PG15/+PG19/+PG46 and −PG07/−PG08 (only
   *marked* cells are affected); PM02 +PG46 (the opaque absence is
   misclassified as unknown; the errata case is worse — the refusal
   precedes the ledger, so the ordinary finding never becomes clean after
   the correction); PM03 +PG46; PM06 +PG15/+PG19/+PG28; PM10 −PG33/−PG34
   (those are the *named* missing blob, governed by the other rule);
   PM11 +PG13–PG21/+PG28/+PG31/+PG32/+PG43/+PG46, −PG25 (no hole). The 47
   grid expectations are unchanged.
5. **Provenance of the filed preliminary receipt**: its producer (the
   runner that still had `--baseline`) is **not recoverable** — the
   `build/out/` copy was overwritten by the contract repair and the lane
   integrated the repaired version, so no commit holds the pre-repair
   file. The receipt is therefore an **unreproducible preliminary with no
   credit**; it stays filed unmodified and is annotated by an honest
   sidecar. Nothing was rewritten or re-credited.

**Not run**: no sensitivity sweep (wave 2 active); only the bounded
`--selftest` and the static `--anchors` check (exit 0 against
`ea51bc35…`, all eleven mutants applicable and compiling). PM07's survival
is still reported as an observationally redundant mutant with **no**
finite-equivalence claim.

---

## 12. Inventory version 3 — PM08 as a historical review-only note (operator instruction)

The operator's instruction supersedes the version-2 AST proposal: **PM08
must stay static-only and must not be a behavioural kill, and no
implementation/source-text/wiring assertion may be shipped for it.** The
version-2 AST proposal in `fixes/MutationEvidence/` is kept filed as a
snapshot; the shipped proposal is version 3 in
`fixes/MutationEvidenceV3/`.

| artifact | sha256 |
|---|---|
| `fixes/MutationEvidenceV3/promisor-mutants.py` (inventory v3) | `a34b834c1916b827dd9e0371b9ad33ce306341635bfc64a591559cc29703e99c` |
| `fixes/MutationEvidenceV3/promisor-mutants-v3.patch` (573 lines, applies clean at p1) | `f1862d3496cc91b8c12542c91d2bd914e80b7f97b7d50844d195273233bfb32a` |
| `fixes/MutationEvidenceV3/inventory-v3.json` | 11 entries = 10 executable + 1 review-only, with the v1→v3 and v2→v3 deltas |
| `fixes/MutationEvidenceV3/rationale-v3.md` | the changes and what is not claimed |
| `fixes/MutationEvidenceV3/selftest-receipt.txt` | `selftest cases=15 failed=0`, exit 0 |

**PM08 in version 3** — the entry is `PM08-no-lazy-fetch-review-only`
(`execution: "review-only"`, **no alternatives**). The `static_check`
field, the literal replacements, the AST helper, the `ast` import and the
tautological guard-wiring test are **removed**: the runner makes **no
source assertion** for this entry (literal or AST) and asserts **no
static transition**. The entry is never applied, no mutant is built, the
grid is **never invoked** for it, and it is reported with `killed: false`,
`executions: 0`, `review_only: 1` and no failed rows. `--anchors` skips
it (`skipped: "review-only"`) and checks the **10 executable mutants
only**. Counts are stated: **11 inventory = 10 executable + 1 manual
review note**. The `--no-lazy-fetch` claim stays a manual reading of the
candidate's isolation flags, credited to nobody.

**Selftest now proves the shape, not a wiring** — 15 cases, 0 failed: one
review-only entry with `killed: false`, `executions: 0`, `review_only: 1`
and no failed rows; the document's `review_only: 1` and
`executable = mutants - 1`; **no grid invocation** carrying the
review-only id in the canary; and the review-only id never in
`killed_ids`.

**Unchanged from version 2** — PM11's unconditional any-hole gate (the old
mutant patched `RepoStore.missing`, consulted only while a citation is
unresolved, so it was a lazy gate that the resolved-unused-hole controls
could not see); the version-2 attribution from the independent semantic
map; the behavioural selftest assertions (≥1 kill and named cells for
`unmet`/`twin`, the intended CNE reason for
`rc1_no_violated_row`, the canary proof that a pristine failure stops
before any mutant phase); the honest provenance sidecar for the filed
preliminary receipt.

**Not run**: no sensitivity sweep (wave 2 active); only the bounded
`--selftest` (15 stub cases) and the static `--anchors` check (exit 0
against `ea51bc35…`: one review-only entry skipped, ten executable mutants
applicable and compiling).

---

## 13. Inventory version 4 — the v7 core freeze, PM07 re-anchored, and the legacy calibration hazard

The final core fix is `fixes/StoreLocalPresence/report-landing-audit-v7.py`
(sha256 `c19568547d50b6d752d1d3caf20fbcc935305ab2964c9569d03eda5b5b400d37`):
`missingAll` is walked from **all** present roots, `opaqueRelevant` (the
name-hiding holes) from the **pinned root only**. The version-3 proposal
and its receipts stay filed; the new proposal is version 4 in
`fixes/MutationEvidenceV4/`.

| artifact | sha256 | bytes |
|---|---|---|
| `fixes/MutationEvidenceV4/promisor-mutants.py` (inventory v4) | `57a186a4a40901bb64561ad44dd7528783c9181f6c0fb22bd2e93e5868862a96` | 54331 |
| `fixes/MutationEvidenceV4/promisor-mutants-v4.patch` (applies clean at p1) | `8ad6d905fb35fb1f05500cf9689e98c87f9c45634510df7cdf2805d7efac6cba` | 33775 |
| `fixes/MutationEvidenceV4/isolation-mutants.py` (proposed legacy harness) | `eace4f56e225f33e96676c0fb6c58d657256c9e37cf06130d487155d343e2a00` | 9691 |
| `fixes/MutationEvidenceV4/isolation-mutants.patch` (899 bytes, vs the lane's `2e` file) | `e29abf65637f987c6b0fb70a0513468382e144fa3d5c8755eab6a62c094bb0f4` | 899 |
| `fixes/MutationEvidenceV4/inventory-v4.json`, `rationale-v4.md`, `selftest-receipt.txt`, `legacy-empty-selection-proof.txt` | — | — |

**PM07 is re-anchored and re-worded.** With the v7 core the old prose
("globally redundant") is false: the name-hiding walk is rooted at the
pinned root only, so the mutant now roots **that** walk at every present
root, making a hole behind an unselected ref relevant. The store-wide
missing set already starts from every present root, so that part changes
nothing. **No kill is presumed**: the primary 47 may still survive; the
discriminator is an **unselected REF tree hole with a fabricated
citation**, which lies **outside the finite 47** (a wave-3 supplement).
The attribution names the closest in-grid surface (PG31, PG32) and says
plainly that the 47 may not distinguish it. The anchors are re-frozen
against `c1956854…`: ten executable mutants, one applicable alternative
each, all compiling (`--anchors` exit 0).

**PM08 stays a manual review-only note**: no alternatives, no source or
wiring assertion, 0 executions, `killed: false`, uncredited, skipped by
`--anchors` (10 executable mutants checked). Its wording is corrected to
the scope of the candidate's **repository-reading wrappers** — they carry
`--no-lazy-fetch`, so a missing promisor object is not fetched through
the promisor remote **on the paths those wrappers read** — and the note
says explicitly that this is a manual reading, **not a proof about every
git call**. Counts: **11 = 10 executable + 1 manual note**. The 47 rows
and the operator's instruction are unchanged.

**Legacy harness calibration hazard (DocSkillF3) — proposed fix.** After
the scoped r24 retirement the legacy ids are full names, so `--only M01`
selected nothing, the run still executed the pristine grid and **exited 0
with an empty inventory** — a silent pass that reads like a calibration
success. The proposed file makes an empty selection **could-not-evaluate
(exit 2)**, decided **before** the source read, the pristine and the grid:

```
BEFORE (integrated file): --only M01 -> exit 0, "mutants=0 killed=0", grid invocations: 1
AFTER  (proposed file):    --only M01 -> exit 2, "could-not-evaluate: --only selected no mutant: ['M01']; the ids are ...", grid invocations: 0
```

The 27 operators and the retirement history are preserved, the existing
CLI error format is reused, no unrelated argument is validated and no
expectation changes. The proof is bounded (a canary grid that records its
invocations; no legacy fixture run).

**Not run**: no sensitivity sweep (wave 2 active) — only the bounded
`--selftest` (15 stub cases, 0 failed) and the static `--anchors` check.

---

## 14. Inventory version 5 — PM07 restored to the canonical recipe

The version-4 retarget of PM07 is declined and reverted: broadening the
name-hiding walk from the pinned root to every present root was **not**
the operator's `--all` mutation, and retargeting a mutant to force a
detect is not legitimate. V5 restores the **exact V3 alternatives and
expect_rows** and changes the prose only.

| artifact | sha256 | bytes |
|---|---|---|
| `fixes/MutationEvidenceV5/promisor-mutants.py` (inventory v5) | `00b89b5061e77a297cb23f15d3ef34237623c5592f67261fbec4807d7cedca4b` | 54485 |
| `fixes/MutationEvidenceV5/promisor-mutants-v5.patch` (applies clean at p1) | `7d3d1643e86bcb0a897c6e57d76d16c1b8fb686a97b2dd7a7dea488881d67173` | 33659 |
| `fixes/MutationEvidenceV5/isolation-mutants.py` + `.patch` (legacy empty-selection guard, unchanged from V4) | `eace4f56e225f33e96676c0fb6c58d657256c9e37cf06130d487155d343e2a00` / `e29abf65637f987c6b0fb70a0513468382e144fa3d5c8755eab6a62c094bb0f4` | 9691 / 899 |
| `fixes/MutationEvidenceV5/inventory-v5.json`, `rationale-v5.md`, `selftest-receipt.txt` | — | — |

**PM07 (canonical, restored):** `--all` is appended to the **store-wide
missing roots**; the name-hiding (opaque) walk is **not** broadened;
`expect_rows` are the V3 set `PG31, PG32, PG35, PG36, PG44, PG45, PG48`.
The prose now says what the recipe does: it adds `--all` to the store-wide
missing roots and does not broaden the pinned-root opaque walk; survival
on the finite 47 is an **observation of this candidate, not a
global-equivalence proof**; the canonical mutant can also differ on a
**broken unselected REF target that is not among the present roots**, so
**no universal no-op is claimed**; and **supplemental post-fix
experiments, specially named and separate from the 47 and from this
canonical operator**, may test unselected-ref opacity. No kill is
presumed — the final run decides.

**Unchanged from V4:** PM08's manual review-only wording (repository-reading
wrappers; not a proof about every git call) and shape (no alternatives, no
source/wiring assertion, 0 executions, `killed: false`, uncredited, skipped
by `--anchors`); the legacy empty-selection CNE guard; every other
operator, its alternatives and its attribution. Counts remain **11 = 10
executable + 1 manual note**.

**Doc correction:** the exit-map paragraph still said "surviving, or
static-only" (the removed static gate's vocabulary); it now reads
"review-only".

**Static anchor check against the latest core**
`fixes/StoreLocalPresence/report-landing-audit-v9.py`
(`b9be4f428cd70842320c698794faffaa95571a60fc530df6a84d7d8cade3b26f`): ten
executable mutants, one applicable alternative each, every mutant compiles,
the review-only entry skipped, `--anchors` exit 0; bounded `--selftest`
15/15. **No sensitivity sweep and no legacy fixture run** (wave 2 active);
the 47 rows, the operator's instructions, the v2/v3/v4 proposals and every
filed receipt are untouched.

---

## 15. Inventory version 6 — the crashing-stand-in bug, attribution before credit, and the class rows

The fresh falsifier (W2DocQualityF1) found a real bug in the shipped
contract: a stand-in row whose auditor **crashed** was credited as a
kill. Version 6 fixes it and adds attribution and class reporting.
V2–V5 stay filed; the integrated files and every receipt are untouched.

| artifact | sha256 | bytes |
|---|---|---|
| `fixes/MutationEvidenceV6/promisor-mutants.py` (inventory v6) | `24549daa762a8f15b24a7938afc2660adc8399a6b4a53c9faa082c6bdc8f9ed6` | 63596 |
| `fixes/MutationEvidenceV6/promisor-mutants-v6.patch` (applies clean at p1) | `80a3794b46f890777065da90d743ad1db6f40ab2f2ce86dfe30ae9adfd3218ff` | 45741 |
| `fixes/MutationEvidenceV6/isolation-mutants.py` / `.patch` (unchanged) | `eace4f56e225f33e96676c0fb6c58d657256c9e37cf06130d487155d343e2a00` / `e29abf65637f987c6b0fb70a0513468382e144fa3d5c8755eab6a62c094bb0f4` | 9691 / 899 |
| `fixes/MutationEvidenceV6/inventory-v6.json`, `rationale-v6.md`, `selftest-receipt.txt` | — | `selftest cases=25 failed=0`, exit 0 |

**Harness faults are never kills.** `harness_fault` now rejects: a row
`traceback`; the per-row / arm / document `internal_error` flag
(GridOracle's confirmed canonical name); the stderr prefix
`could-not-evaluate: internal:` (the grid's stderr and each row's
`stderr_tail`, the fallback for a grid version without the boolean); an
invalid row exit (outside 0/1/2); and a malformed verdict (exit 0/1 with
a `document` field present but `None`). Each is could-not-evaluate: exit
2, **zero kills**.

**Attribution is enforced before a credit.** A violated row outside the
mutant's `expect_rows` is not a kill: the mutant is could-not-evaluate
(exit 2, `killed: false`), the out-of-attribution rows are **preserved**
in `unexpected_rows` and in the reason, and the allowlist is **not
widened**.

**Class rows, read from the row's own `expected_exit`/`exit`:** 
`refusal-2` (a normal 0/1 verdict became a refusal — an over-refusal
signal, **not** an availability credit), `actual-verdict` (an unavailable
2 became a real 0/1 verdict — the **availability** credit),
`verdict-change` (a normal verdict became another normal verdict, reported
separately), `diagnostic-only` (the exit is unchanged — **no** acceptance
or availability credit), and `unclassified` (the comparison fields are
missing or outside 0/1/2 — **no class credit is guessed**). The classes,
`availability_credit`, `verdict_change`, `diagnostic_only` and
`unclassified` are reported per mutant; the paired obligations (KQ35) are
read from these class rows, not from a raw kill count.

**No new admission gate:** a valid finite survival stays a completed run
(exit 0); exit 2 is reserved for could-not-evaluate, never for a
survivor.

**Negative controls** (bounded stub fixtures, 25 assertions): traceback
row, `internal_error` row, malformed verdict, out-of-attribution row
(preserved, not a kill), a violated row without the comparison fields
(reported `unclassified`, no availability credit), the pristine abort
(canary: no mutant phase ran), and the `unmet`/`twin` modes (≥1 kill
credited and the named cell reported). The stub rows carry the canonical
shape (`met`, `exit`, `expected_exit`, `document`).

**Legacy hazard attribution corrected:** the short-id behaviour
(`--only M01` never matching `M01-replace-objects`) **pre-existed** the
round-24 retirement; the retirement changed the id set and exposed the
staleness of a hard-coded short id. The guard itself is unchanged (an
empty selection is could-not-evaluate, decided before the source read,
the pristine and any grid call).

**Unchanged from V5:** the PM07 canonical recipe and its `expect_rows`,
PM08's manual review-only wording and shape, the legacy guard, and every
other operator with its alternatives and attribution. **Not run**: no
sensitivity sweep and no legacy fixture run; the anchors are checked
statically against the latest core `report-landing-audit-v9.py`
(`b9be4f42…`).

---

## 16. Inventory version 7 — the classification bug and the corrected taxonomy

The L1's static review of the version-6 runner found a real bug:
`classify_row` tested the normal/normal branch **before** the equality
branch, so a violated row with an unchanged exit (0 → 0 or 1 → 1) was
labelled `verdict-change` — an exit pair alone never shows that the whole
verdict changed. Version 7 compares the exits first.

| artifact | sha256 | bytes |
|---|---|---|
| `fixes/MutationEvidenceV7/promisor-mutants.py` (inventory v7) | `7ba30cccca3aa8f976dee7f20ccbfe7e4b533b65a4ceb1c5bf0e01530eaf4447` | 66708 |
| `fixes/MutationEvidenceV7/promisor-mutants-v7.patch` (applies clean at p1) | `69fe153ccc0d5e90fb68b0e96c63e88d30c1dec1b1578e8e9b04be217e7c7c6b` | 48907 |
| `fixes/MutationEvidenceV7/isolation-mutants.py` / `.patch` (unchanged) | `eace4f56e225f33e96676c0fb6c58d657256c9e37cf06130d487155d343e2a00` / `e29abf65637f987c6b0fb70a0513468382e144fa3d5c8755eab6a62c094bb0f4` | 9691 / 899 |
| `fixes/MutationEvidenceV7/inventory-v7.json`, `rationale-v7.md`, `selftest-receipt.txt` | — | `selftest cases=34 failed=0`, exit 0 |

**Taxonomy (from the row's own `expected_exit`/`exit`):** 0→0 and 1→1 are
`same-verdict-exit` (the same exit; the detail may differ — no
substantive exit change, no availability claim); **only** 0↔1 is
`verdict-change`; 0/1→2 is `refusal-2` (an over-refusal signal, not an
availability credit); 2→0/1 is `actual-verdict` (the availability credit);
2→2 is `diagnostic-only`; missing or out-of-envelope comparison fields are
`unclassified` (no credit guessed).

**Aggregates:** `diagnostic_only` is true **only** when every class is
`diagnostic-only`; a `same-verdict-exit` or `unclassified` row keeps it
false and its named rows are preserved separately (`same_verdict_exit`,
`unclassified`). `availability_credit` = an `actual-verdict` class;
`verdict_change` = a `refusal-2` or `verdict-change` class. The unused
`credit = availability` local is removed, and the main agent's final
statistics are derived from the observed classes.

**Behaviour control:** the selftest walks **all nine exit pairs**
(0/1/2 × 0/1/2) through a stand-in row and asserts each class; the
missing-metadata control stays. 34 assertions, 0 failed.

**Unchanged from V6:** the harness-fault set (row `traceback`, the
`internal_error` flag, the `could-not-evaluate: internal:` stderr
fallback, an invalid row exit, a malformed verdict); attribution enforced
before a credit with the out-of-attribution rows preserved and the
allowlist not widened; **no new admission gate** (a valid finite survival
stays a completed run, exit 0); PM07's canonical recipe and its
`expect_rows`; PM08's manual review-only wording and shape; the legacy
empty-selection guard; every other operator.

**Not run:** no sensitivity sweep and no legacy fixture run; the anchors
are checked statically against core v9 (`b9be4f42…`).

---

## 17. Inventory version 8 — final cleanup (one canonical internal-error flag)

| artifact | sha256 | bytes |
|---|---|---|
| `fixes/MutationEvidenceV8/promisor-mutants.py` | `b04c3812186e1a6c72f39f1a6a79adb632ee1efecaab687aa0d3c1fee7eed757` | 66844 |
| `fixes/MutationEvidenceV8/promisor-mutants-v8.patch` (applies clean at p1) | `b448b4ff584bdf3533354733cb0386a29bcf67b7b9b411c3f08a811318ef331e` | 49045 |
| `fixes/MutationEvidenceV8/isolation-mutants.py` / `.patch` (unchanged) | `eace4f56e225f33e96676c0fb6c58d657256c9e37cf06130d487155d343e2a00` / `e29abf65637f987c6b0fb70a0513468382e144fa3d5c8755eab6a62c094bb0f4` | 9691 / 899 |
| `fixes/MutationEvidenceV8/rationale-v8.md` | — | — |

**One cleanup only.** The agreed grid protocol carries a single canonical
internal-error signal — the per-row boolean `internal_error`, true when the
auditor's full stderr contains `could-not-evaluate: internal:`. Version 8
keeps only that name (`INTERNAL_FLAGS = ("internal_error",)`); the two
speculative aliases (`internal_errors`, `internal`) are **removed** and no
compatibility promise for another spelling is kept. The stderr checks stay
as **diagnostics on the same catch-all message** (the grid's stderr and
each row's `stderr_tail`), with the comment corrected: the per-row boolean
is authoritative, and a long message can push the prefix out of the kept
tail. Nothing else changed: the operators, their alternatives and
attribution, the class taxonomy and aggregates, the harness-fault set, the
attribution-before-credit rule, the review-only PM08 note, the legacy
empty-selection guard and all fixture data are identical to version 7, whose
inventory file stands.

**API:** there is **no exported `run_inventory`**; the runner exposes
`main(argv)` and the existing `STUB_GRID` / `CANDIDATE` helpers, which the
main agent's wave-3 negative control uses directly. No new API was added.

**Checks:** source compile only, per the instruction (`py_compile` passes).
The selftest and the sensitivity pass were **not** re-run in this version;
version 7's receipts stand (34 assertions, 0 failed). V2–V7 stay filed and
the integrated files and every filed receipt remain unchanged.

---

## 18. Inventory version 9 — N1 (the frozen-arm false green) and N8 (provenance)

The postfix interface contract
(`.ufo/waves/round-24/postfix/interface-findings-contract.txt`) assigns N1
and N8 to this lane. Version 9 closes both; V2–V8 stay filed, the
integrated files and every receipt stay unchanged, and there is no
primary-47, expectation, twin-link, PM08 or operator-recipe change.

| artifact | sha256 | bytes |
|---|---|---|
| `fixes/MutationEvidenceV9/promisor-mutants.py` (inventory v9) | `2ee2bea2b43024c97fb8b0bf657cbc052519a34eace9b23063b55dd03f432114` | 71798 |
| `fixes/MutationEvidenceV9/promisor-mutants-v9.patch` (applies clean at p1) | `c9b44c15d720b48d4078fd858475bf35739cd66804b4aaedcc5a0161b6cdd46e` | 55533 |
| `fixes/MutationEvidenceV9/isolation-mutants.py` / `.patch` (unchanged) | `eace4f56e225f33e96676c0fb6c58d657256c9e37cf06130d487155d343e2a00` / `e29abf65637f987c6b0fb70a0513468382e144fa3d5c8755eab6a62c094bb0f4` | 9691 / 899 |
| `fixes/MutationEvidenceV9/rationale-v9.md`, `selftest-receipt.txt` | — | `selftest cases=40 failed=0`, exit 0 |

**N1 — the frozen-arm false green is closed.** `--arm frozen` makes the
grid run its **fixed frozen auditor** and ignore the `--current` mutant,
yet the runner reported "pristine passed" and the mutants as survivors —
a green no mutant earned. The sensitivity runner now measures the
**current arm only**: any other arm (`frozen`, `both`, anything else) is
**could-not-evaluate (exit 2)**, decided **before** the source is read, the
pristine run and any grid call, with no compatibility mapping that fakes
an experiment. `--arm current` stays explicitly valid. The bounded
control: the selftest runs `--arm frozen`, `--arm both` and `--arm
currentish` and asserts exit 2, **zero grid invocations** (the canary log
stays empty) and a reason naming the current-arm restriction.

**N8 — the inputs identify what was actually measured.** The document
carries a `provenance` block of byte identities: the candidate file's
sha256, the grid producer's sha256 (each read once and reused), the grid
document's own `population_sha256`, `expectations_sha256` and
`population_size`, and the grid's `auditor_sha256` map (the digest of the
auditor each arm actually used). Every mutant entry carries the
**observed per-mutant auditor digest** from that run's grid document, and
the failed-row details carry it alongside the class rows. Nothing is
invented: a field the grid does not report stays absent, and the selftest
cross-checks that the grid's current-arm digest equals the digest of the
candidate file the runner passed. The stub grid was made honest for the
canonical output shape (it computes the same fields from the bytes it
uses). The exact placement of `auditor_sha256` was coordinated with
GridOracle, who confirmed the map shape and that no schema change is
needed.

**Unchanged from V8:** the operators, their alternatives and attribution;
the class taxonomy and aggregates; the harness-fault set (row `traceback`,
the canonical `internal_error` flag, the stderr diagnostics, an invalid row
exit, a malformed verdict); attribution enforced before a credit with the
out-of-attribution rows preserved and the allowlist not widened; no new
admission gate (a valid finite survival stays a completed run, exit 0);
PM08 as a manual review-only note; the legacy empty-selection guard; the
47 rows and the twin links. **N3 stays an intentional envelope**: the
expectation lists are the attribution, not a promise that every listed row
breaks, and no "declared not broken" metric is emitted.

**Not run**: no sensitivity sweep and no legacy fixture run (wave 2 is
active); the checks exercised are the bounded selftest (40 assertions, 0
failed) and the source compile.

---

## 19. Inventory version 10 — the grid's own producer digest and the grading explanation

GridOracle's V6 grid (proposal sha256
`d8ff2c473a28249433cc52dd42c67252a5af1c54b59c4d3aeee3c243e3cf654f`, proposal
only) adds one key, `doc["grid_sha256"]` — the producer's own source digest —
and carries the grade messages per row. Version 10 consumes both; it is a
**strict superset of version 9** (which stays valid if the L1 prefers fewer
changes), and V2–V9 stay filed.

| artifact | sha256 | bytes |
|---|---|---|
| `fixes/MutationEvidenceV10/promisor-mutants.py` | `c00af3513944a6c1ec29c9a987347d92220d55f741d484e229962d0f1e490c19` | 73767 |
| `fixes/MutationEvidenceV10/promisor-mutants-v10.patch` (applies clean at p1) | `84de3c880e5c283f82ed657f4ef6d58d8f10c5aa8cf2933ba1af892295079bf2` | 57792 |
| `fixes/MutationEvidenceV10/isolation-mutants.py` / `.patch` (unchanged) | `eace4f56e225f33e96676c0fb6c58d657256c9e37cf06130d487155d343e2a00` / `e29abf65637f987c6b0fb70a0513468382e144fa3d5c8755eab6a62c094bb0f4` | 9691 / 899 |
| `fixes/MutationEvidenceV10/rationale-v10.md`, `selftest-receipt.txt` | — | `selftest cases=41 failed=0`, exit 0 |

**The grid's own digest is compared, not trusted blindly.** The runner
records the grid's reported `grid_sha256` next to the digest it computed
from the grid file's bytes, and **refuses** the run (could-not-evaluate,
exit 2, zero kills) when they differ — a producer that does not match the
hashed file has not identified what was measured. The same check runs per
mutant, so a grid that changed between the pristine and a mutant run is
caught. A grid without the key leaves the field absent (V9 behaviour). The
bounded control: the stub reports a wrong producer digest in one mode and
the selftest asserts the refusal.

**The grading explanation travels with the failed rows:** the grid's
`problems`, `amended_problems` and `original_problems` are carried into the
failed-row details, so a receipt says *why* a row was violated. No grading
rule of the runner reads them and no field is required.

**Unchanged from V9:** the current-only arm rule (any other arm is exit 2
before the source, the pristine and any grid call); the provenance block
(candidate digest, grid digest, population/expectation digests and size,
the grid's `auditor_sha256` map, and the observed per-mutant auditor digest
alongside the failed and class rows); the operators, alternatives and
attribution; the class taxonomy and aggregates; the harness-fault set;
attribution enforced before a credit with the allowlist not widened; no new
admission gate (a valid finite survival stays exit 0); PM08 as a manual
review-only note; the legacy empty-selection guard; the 47 rows and twin
links; N3 as an intentional envelope with no "declared not broken" metric.

**Not run**: no sensitivity sweep and no legacy fixture run (wave 2
active); the exercised checks are the bounded selftest (41 assertions, 0
failed) and the source compile.

---

## 20. Inventory version 11 — the final coupled cut (help text and detail preservation)

| artifact | sha256 | bytes |
|---|---|---|
| `fixes/MutationEvidenceV11/promisor-mutants.py` | `5498202d9084d417cff30154f57811bd07a27fe39eed137dcff82c411faf3333` | 76461 |
| `fixes/MutationEvidenceV11/promisor-mutants-v11.patch` (applies clean at p1) | `b3e96d0e2ac47dd038c38f4342427341b90f14a0c795a5a12c3cf4718b981995` | 61079 |
| `fixes/MutationEvidenceV11/isolation-mutants.py` / `.patch` (unchanged) | `eace4f56e225f33e96676c0fb6c58d657256c9e37cf06130d487155d343e2a00` / `e29abf65637f987c6b0fb70a0513468382e144fa3d5c8755eab6a62c094bb0f4` | 9691 / 899 |
| `fixes/MutationEvidenceV11/rationale-v11.md`, `selftest-receipt.txt` | — | `selftest cases=42 failed=0`, exit 0 |

**The CLI help no longer advertises a frozen experiment.** The `--arm`
help read "grid arm to exercise", inviting a reader to try `--arm frozen`
— the arm that runs the grid's fixed frozen auditor, ignores the
`--current` mutant and reports a green no mutant earned. It now reads
"**CURRENT arm only**: the sensitivity runner measures the candidate the
`--current` path names. Any other arm is could-not-evaluate, because the
frozen arm runs the grid's fixed frozen auditor and ignores the
candidate". The behaviour is unchanged (any other arm → exit 2, before the
source, the pristine and any grid call); only the advertised contract was
wrong, and now it matches the rule.

**The grid's grading explanation is preserved, not discarded.** The newer
grid document carries the grading's own messages per row
(`problems`, `amended_problems`, `original_problems`); the failed-row
details carry them **alongside the codes and the observed auditor digest**,
so a receipt says why a row was violated and not only that it was. A field
the grid does not report stays **absent** — no alias, no invented value.
Bounded control: the stub emits one explained row and one plain row, and
the selftest asserts that the explained row's three fields reach the
detail and that the plain row's detail has none of them.

**Unchanged from V10:** the current-only arm rule; the provenance block
(candidate digest, grid digest, grid-reported producer digest with the
mismatch refusal, population/expectation digests and size, the grid's
`auditor_sha256` map, the observed per-mutant auditor digest alongside the
failed and class rows); the operators, alternatives and attribution; the
class taxonomy and aggregates; the harness-fault set; attribution enforced
before a credit with the allowlist not widened; no new admission gate;
PM08 as a manual review-only note; the legacy empty-selection guard; the
47 rows and twin links; N3 as an intentional envelope with no "declared not
broken" metric.

**Not run**: no sensitivity sweep and no legacy fixture run; the exercised
checks are the bounded selftest (42 assertions, 0 failed) and the source
compile. V2–V10 stay filed; the integrated files and every receipt remain
unchanged.

---

## 21. Inventory version 12 — the vacuous green with no graded cell

| artifact | sha256 | bytes |
|---|---|---|
| `fixes/MutationEvidenceV12/promisor-mutants.py` | `c7d1782310ce2e0e3c7ac10af0aeb3d2568d9f74d41dc240acec7c0548c2fb64` | 78717 |
| `fixes/MutationEvidenceV12/promisor-mutants-v12.patch` (applies clean at p1) | `ca51dea6e22c9cf2c83461fa14ce3acf271b8bcaccf166dc5879bba1c9186284` | 63969 |
| `fixes/MutationEvidenceV12/isolation-mutants.py` / `.patch` (unchanged) | `eace4f56e225f33e96676c0fb6c58d657256c9e37cf06130d487155d343e2a00` / `e29abf65637f987c6b0fb70a0513468382e144fa3d5c8755eab6a62c094bb0f4` | 9691 / 899 |
| `fixes/MutationEvidenceV12/rationale-v12.md`, `selftest-receipt.txt` | — | `selftest cases=43 failed=0`, exit 0 |

**The vacuous green is closed.** Selecting only an **open/ungraded** cell
(the grid's `PG40`) produced a valid pristine with **zero graded oracle
cells**: every mutant could then be reported as a survivor without any
comparison and the run exited 0 — the same class of defect as the
frozen-arm false green, a green no measurement earned.

Version 12 states the experiment's precondition:

* after a **valid pristine**, the run requires **at least one graded row**
  before it may report "pristine passed" and before the mutant loop
  starts; an empty graded set is **could-not-evaluate (exit 2)** with zero
  kills and **no mutant run at all**;
* a **mutant** run that yields no graded row cannot be a valid survivor:
  it is reported as could-not-evaluate, not as "survived".

Nothing is made graded — the open cell stays open and ungraded — and the
ordinary survival path (graded rows present, no violation) is unchanged.
Bounded control: the stub reports an **open-only** row and the selftest
asserts the runner aborts with exit 2 after **exactly one grid invocation**
(the pristine) and a reason that names the missing graded row.

This is a precondition, not a feature: no new manual mode, no telemetry
framework, no new admission gate; exit 2 remains could-not-evaluate, an
ordinary survival still completes with exit 0, and PM08 stays unexecuted
and uncredited.

**Unchanged from V11:** the current-only arm rule and its help text; the
provenance block (candidate digest, grid digest, grid-reported producer
digest with the mismatch refusal, population/expectation digests and size,
the grid's `auditor_sha256` map, and the observed per-mutant auditor
digest alongside the failed and class rows); the operators, alternatives
and attribution; the class taxonomy and aggregates; the harness-fault set;
attribution enforced before a credit with the allowlist not widened; the
grading explanation preserved where reported and absent where not; the
legacy empty-selection guard; the 47 rows and twin links; N3 as an
intentional envelope with no "declared not broken" metric.

**Not run**: no sensitivity sweep and no legacy fixture run (wave 2
active); the exercised checks are the bounded selftest (43 assertions, 0
failed) and the source compile.

---

## 22. Inventory version 13 — the digest refusal moves to the pristine, and every observed run stays identifiable

| artifact | sha256 | bytes |
|---|---|---|
| `fixes/MutationEvidenceV13/promisor-mutants.py` | `3dae9345743910e475a8d506a76f0bf1771f2c44becda72d7a2706c9e766d45f` | 80492 |
| `fixes/MutationEvidenceV13/promisor-mutants-v13.patch` (applies clean at p1) | `810f1862fe66e2f497ed617333b87fffa4483f4f3213fb0a640e880cb92b24b2` | 65777 |
| `fixes/MutationEvidenceV13/isolation-mutants.py` / `.patch` (unchanged) | `eace4f56e225f33e96676c0fb6c58d657256c9e37cf06130d487155d343e2a00` / `e29abf65637f987c6b0fb70a0513468382e144fa3d5c8755eab6a62c094bb0f4` | 9691 / 899 |
| `fixes/MutationEvidenceV13/rationale-v13.md`, `selftest-receipt.txt` | — | `selftest cases=45 failed=0`, exit 0 |

**The producer-digest refusal belongs to the pristine validation.** The
grid-reported `grid_sha256` check (against the digest the runner hashes
from the grid file) sat **after** the mutant loop, so a pristine whose
grid producer could not be identified still had every mutant run on it
before the refusal. V13 moves the **existing** check — same condition,
same result — into the pristine validation, **before** the loop: an
unidentified pristine is refused and no experiment runs on it. Bounded
control: the stub reports a wrong producer digest in the pristine, and the
selftest asserts exit 2 after **exactly one grid invocation** (the
pristine) and a reason naming the digest.

**Every observed run stays identifiable.** The observed per-mutant auditor
digest was recorded only on the killed/survived path, so a mutant that
ended in could-not-evaluate (harness fault, grid exit 2, producer-digest
mismatch, out-of-attribution violation) lost the digest of the run that
was actually observed. V13 records it **as soon as the grid reports it**,
so every observed run is identifiable even when nothing is credited; a
digest the grid does not report stays **absent** (nothing invented).
Bounded control: the stub reports a correct digest in the pristine and a
wrong one in the mutant runs, and the selftest asserts the
could-not-evaluate entry **keeps the observed digest**.

**Unchanged from V12:** the current-only arm rule and its help text; the
graded-row precondition (a valid pristine with no graded row is
could-not-evaluate; a mutant run with no graded row cannot be a valid
survivor); the provenance block; the operators, alternatives and
attribution; the class taxonomy and aggregates; the harness-fault set;
attribution enforced before a credit with the allowlist not widened; the
grading explanation preserved where reported and absent where not; the
legacy empty-selection guard; the 47 rows and twin links; N3 as an
intentional envelope with no "declared not broken" metric. No broader
binding validation and no telemetry.

**Not run**: no sensitivity sweep and no legacy fixture run (wave 2
active); the exercised checks are the bounded selftest (45 assertions, 0
failed) and the source compile.

---

## 23. Inventory version 14 — the exit-only pristine gap, and the mirror contradiction

| artifact | sha256 | bytes |
|---|---|---|
| `fixes/MutationEvidenceV14/promisor-mutants.py` | `971c3ecbc1af05d4e6806ed06e8d3c7499ff55caf09e7bbc2c5ae2992204f200` | 84320 |
| `fixes/MutationEvidenceV14/promisor-mutants-v14.patch` (applies clean at p1) | `cf21f1f27530ae450b1728c0e3a7d9d8545665d420d665bf4668dd04461786d3` | 69681 |
| `fixes/MutationEvidenceV14/isolation-mutants.py` / `.patch` (unchanged) | `eace4f56e225f33e96676c0fb6c58d657256c9e37cf06130d487155d343e2a00` / `e29abf65637f987c6b0fb70a0513468382e144fa3d5c8755eab6a62c094bb0f4` | 9691 / 899 |
| `fixes/MutationEvidenceV14/rationale-v14.md`, `selftest-receipt.txt` | — | `selftest cases=47 failed=0`, exit 0 |

**The exit-only pristine gap is closed.** The pristine check consulted
only the grid's exit code: a grid that returned rc 0 while a graded row
was unmet (or its twin constraint failed) was accepted as a pristine, and
the run continued on a "pass" the grid's own rows contradicted. V14
requires the pristine to satisfy the grid's contract in full — **rc 0 AND
no violated graded row** — otherwise the run is could-not-evaluate (exit
2) **before any mutant runs**.

**The mirror contradiction is not a kill.** A **mutant** run with rc 0 and
a violated graded row is a contradictory grid protocol (the grid says the
run passed and names a violated row): it is **could-not-evaluate with zero
kills**, the mirror of the existing "rc 1 without an identifiable violated
row" rule. The receiver may not launder a contradiction into a pristine or
into a kill. The resulting matrix (unchanged where it already held):
pristine 0/none → passes; pristine 0/some → CNE before the mutants;
pristine 1 → CNE; mutant 0/none → survivor (completed, exit 0); mutant
0/some → CNE, zero kills; mutant 1/some → kill, attributed; mutant 1/none
→ CNE.

**Two bounded controls**: the stub's pristine contradicts the grid (rc 0
with a violated row) and the selftest asserts exit 2 after **exactly one
grid invocation** and a reason naming the violated graded row; and a
mutant run contradicts the grid while the pristine is sound, and the
selftest asserts exit 2, **no kill credited**, and the could-not-evaluate
entry recording the contradictory row.

**Unchanged from V13:** the current-only arm rule and its help text; the
graded-row precondition; the pristine producer-digest refusal before the
loop; the early recording of the observed per-mutant auditor digest; the
provenance block; the operators, alternatives and attribution; the class
taxonomy and aggregates; the harness-fault set; attribution enforced before
a credit with the allowlist not widened; the grading explanation preserved
where reported and absent where not; the legacy empty-selection guard; the
47 rows and twin links; N3 as an intentional envelope with no "declared not
broken" metric; PM08 unexecuted and uncredited. No backend, no schema
framework.

**Not run**: no sensitivity sweep and no legacy fixture run (wave 2
active); the exercised checks are the bounded selftest (47 assertions, 0
failed) and the source compile.
