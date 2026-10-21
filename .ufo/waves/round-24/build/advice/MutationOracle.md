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
