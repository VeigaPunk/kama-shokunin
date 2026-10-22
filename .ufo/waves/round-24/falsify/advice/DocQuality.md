# DocQuality — KQ35 criterion quality review (round 24, integrated commit `2e254a17`)

**Verdict: HOLDS on the amended contract's substance; two defects are real and one is a
measurement defect. Minimal corrections are given in §7.**

The KQ35 row itself is a good criterion. It is the only corpus row that says, in one
place, all four of: the clean/failed verdict under metadata changes is decided by
content; the required-object diagnosis is content-derived; the two mutant obligations are
class-scoped (complete-state vs unavailable-state); and the original/prospective oracles
stay separately recorded. It correctly refuses the r23 harm shape without re-introducing a
blanket refusal, and it does not claim the withdrawn original expectation was achieved.

The findings below are ordered by severity. F1 and F2 are genuine defects in the shipped
mutation probe and grid; F3 is a defect in what the committed evidence actually
demonstrates.

---

## 1. Scope and pinned base

| Item | Value |
|---|---|
| Pinned commit | `2e254a1763a9c08aa07fc53081287f506c447d84` (detached in scratch clone) |
| Scratch clone | `/fast/scratch/hyaku/kama-r24/falsify/DocQuality` (`git clone --no-hardlinks` from `/home/vgpnk/Projects/shokunin/kama-shokunin`) |
| Scratch base observed | `git rev-parse HEAD` → `2e254a1763a9c08aa07fc53081287f506c447d84`; `git status --porcelain` empty at checkout (only `probe/` added later, untracked, outside the clone's tracked tree) |
| `tools/report-landing-audit.py` | sha256 `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220` |
| `tests/report-audit/promisor-grid.py` | sha256 `b034e1596746d312989b7894c0757b67859df19a476a01ccd95076424135cefa` |
| `tests/report-audit/promisor-grid-expectations.json` | sha256 `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1` |
| `tests/report-audit/promisor-mutants.py` | sha256 `6e0b9d62db9fe27f6c14c6e16ce239023f699142193adff5291e4374a1bb60a2` |
| Host | git 2.56.0, Python 3.14.8, linux x86_64 |
| Lane bounds | read-only; no production edit; no full suite; no network; no execution payload |
| Tools installed/updated | none (no install required) |

All measurements below are bounded: single-case or small-multi-case grid runs, the shipped
mutation probe's own `--selftest`, the shipped auditor's own `--selftest`, and static
inspection of committed files. No full 47-cell suite was run.

---

## 2. What KQ35 says, and whether each clause is satisfiable by the shipped instruments

KQ35 (`corpus/QUALITY.md:183`):

> **KQ35 (qualifies KQ34; no-trade rule unchanged)** | Admit only when: *Paired
> complete-state controls preserve the independent correct clean/failed verdict under
> metadata changes; missing objects actually required by the audit produce content-derived
> could-not-evaluate, never a guessed empty object or failure finding. A blanket-refusal
> mutant must fail the complete-state controls, and a missing-required-evidence acceptance
> mutant must fail the unavailable-state controls. Original versus prospectively corrected
> oracles remain separately recorded.* | Reject or limit when: *Promisor metadata or an
> unrelated missing historical object becomes a refusal precondition; a correct runnable
> workflow is lost and excused as a disclosed trade; a blanket unknown rule blocks
> authorized historical errata; expected outcomes are changed after measuring a candidate
> and reported as though originally preregistered.* | Motivating lesson:
> `lessons/round-24.md` Mistakes; MANIFEST rounds[428];
> `.ufo/waves/round-24/preregistration.json` and `oracle-amendment-1.json`

Clause-by-clause against the pinned tree:

| KQ35 clause | Satisfiable? | Evidence |
|---|---|---|
| Paired complete-state controls preserve the independent clean/failed verdict under metadata changes | **YES** | `PG01`/`PG07` pair: `twin_equal=True` on the pinned pair (see §3, probe P3). 26 of 47 cells carry a `twin` link; all 20 exit-0 cells are graded `kind=control` or `kind=policy` with an independent plain twin where one exists. |
| Missing required objects produce content-derived CNE, never a guessed empty object or failure finding | **YES** | Pinned grid + pinned auditor: `PG13` → exit 2 with the required blob id in stderr; `PG47` → exit 2 naming the fabricated token *and* the hiding tree; `PG48` → exit 0 clean. See §3 P4–P6. |
| A blanket-refusal mutant must fail the complete-state controls | **YES** | P3/P7: `PM01` fails exactly the 8 marked complete-state cells probed, `unexpected_rows=[]`. |
| A missing-required-evidence acceptance mutant must fail the unavailable-state controls | **PARTIAL — F1** | The obligation is stated in the corpus but **not enforced by the shipped probe**. See F1. |
| Original vs prospectively corrected oracles remain separately recorded | **YES** | Pinned grid reports `met_original`/`met_amended` per row and a `withdrawn_original_failures` list; `PG22` shows `met_original=False, met_amended=True` and is the sole withdrawn row on the probed set. The manifest is committed once (`ed1cc3a`) and never rewritten. |
| No-trade rule unchanged | **YES, with a sourcing gap — F4** | The AXES.md no-trade clause (`/home/vgpnk/Projects/shokunin/AXES.md:34-36`) has not changed since `84bade0` (2026-10-16), i.e. unchanged across round 24. But `corpus/QUALITY.md` never cites AXES.md, so the corpus-internal reader cannot resolve where the rule lives. |

---

## 3. Bounded measurements

### P1 — shipped probe `--selftest` (offline, isolated stub grid)

```
$ python3 tests/report-audit/promisor-mutants.py --selftest
selftest cases=11 failed=0          exit=0
```

### P2 — shipped auditor `--selftest` (offline, local git only)

```
$ python3 tools/report-landing-audit.py --selftest
... 62 ok lines ...
selftest cases=62 failed=0           exit=0
```

Among the 62: `promisor-metadata-keeps-the-local-verdict`, `promisor-remote-is-never-contacted`,
`unrelated-missing-object-does-not-block`, `missing-tree-is-an-opaque-hole`,
`opaque-hole-makes-an-unresolved-token-unknown`. So the *auditor* side of KQ35 is sound.

### P3 — complete-state pair, pinned pair

```
$ python3 tests/report-audit/promisor-grid.py --arm current \
    --case PG01-complete-lane-promisor-config --case PG07-complete-lane-plain \
    --case PG13-missing-lane-blob-promisor --case PG14-missing-lane-blob-plain --json
exit=0
PG01 exit=0 twin=PG07 twin_equal=True  met=True
PG07 exit=0 twin=None  twin_equal=True  met=True
PG13 exit=2 twin=PG14 twin_equal=None   met=True
PG14 exit=2 twin=None  twin_equal=None  met=True
```

The complete-state pair compares equal documents under metadata change; the
unavailable-state pair yields `twin_equal=None` (no document to compare — both refused),
which the grid handles by comparing exit/kinds/reason-class per cell instead. Correct.

### P4/P5 — required-object diagnosis, pinned pair

```
PG13 → exit 2, stderr:
  "…: git cat-file blob 051975b0ced83169116c235e7691c0a1a8313300 … rc=128 fatal: … bad file"
PG47 → exit 2, stderr:
  "could-not-evaluate: round 1: unknown: unavailable required object:
   0123456789abcdef0123456789abcdef01234567 could be hidden behind the missing tree or
   commit 2a675c1af91c97c51f5101d6cff10bb797458ab6 in …/lane"
```

Content-derived: the reason names the unavailable object (or the hiding tree), never an
empty object and never a failure finding.

### P6 — opaque-hole family, pinned pair

```
PG46 (opaque tree hides cited blob) → exit 2, met=True
PG47 (opaque tree + unresolved fabricated token) → exit 2, met=True
PG48 (opaque unused tree, no unresolved token) → exit 0, kinds=[], met=True
```

### P7 — blanket-refusal mutant on complete-state cells, pinned pair

```
$ python3 tests/report-audit/promisor-mutants.py --current tools/report-landing-audit.py \
    --grid tests/report-audit/promisor-grid.py --only PM01-blanket-metadata-refusal \
    --case PG01… --case PG03… --case PG05… --case PG26… --case PG28… --case PG35… \
    --case PG44… --case PG48… --json
exit=0
pristine=passed killed=1 attributed=True
failed_rows = PG01, PG03, PG05, PG26, PG28, PG35, PG44, PG48   (all 8 marked complete-state cells)
unexpected_rows = []
```

### P8 — acceptance mutants across **all 14** unavailable-state cells, pinned pair

```
$ for M in PM03 PM04 PM06; do
    python3 tests/report-audit/promisor-mutants.py --current tools/report-landing-audit.py \
      --grid tests/report-audit/promisor-grid.py --only $M <all 14 exit-2 cells> --json
  done
exit=0 for all three

PM03-skip-required-object-availability     killed=1 attributed=False
   failed = PG33, PG34, PG46, PG47
PM04-accept-unavailable-referenced-object  killed=1 attributed=True
   failed = PG33, PG34
PM06-swallow-actual-read-error             killed=1 attributed=False
   failed = PG13, PG14, PG15, PG16, PG17, PG18, PG19, PG20, PG21, PG43

exit-2 cells discriminated by NO acceptance mutant: []   (union = 14/14)
```

So the *substance* of KQ35's second mutant obligation holds on the pinned pair: every
unavailable-state cell is discriminated by at least one acceptance mutant, and every
acceptance mutant is killed. What does not hold is that the probe *enforces* the obligation
— see F1.

---

## 4. F1 (High) — the shipped probe credits a kill without enforcing KQ35's class-scoped obligation, and a diagnostic error can earn that kill

### 4.1 The obligation in KQ35 is class-scoped; the probe is not

KQ35: *"A blanket-refusal mutant must fail the **complete-state controls**, and a
missing-required-evidence acceptance mutant must fail the **unavailable-state controls**."*

`tests/report-audit/promisor-mutants.py:786` decides a kill as:

```python
killed = bool(bad)          # bad = violated_rows(rows)
```

and `violated_rows` (`:530-539`) returns *any* graded row with `met == False` or
`twin_equal == False`. The class scope lives only in the informational field
`attributed` (`:793-797`), which is computed *after* `killed` and never gates it.

Bounded proof, using the shipped runner with three stub grids that report only what the
real grid reports:

```
# stub grid 4: the PM03 ACCEPTANCE mutant fails ONLY PG01 (a complete-state cell)
$ python3 tests/report-audit/promisor-mutants.py --grid probe/stub-grid4.py \
    --current probe/candidate.py --only PM03-skip-required-object-availability --json
exit=0
killed=1 killed_ids=['PM03-skip-required-object-availability']
status=killed attributed=False failed_rows=['PG01'] unexpected_rows=['PG01']
```

An acceptance mutant that failed **zero** unavailable-state controls is still credited a
kill, and the run still exits 0. Under KQ35's own wording this mutant has **not**
discharged its obligation.

### 4.2 A diagnostic error can be the credited kill

The shipped grid marks a row unmet on a traceback (`promisor-grid.py:802-803`) or on an
internal error, and the probe then treats that unmet row as a violated row:

```
# real pinned grid + a deliberately crashing stand-in auditor (no repo, no network)
$ python3 tests/report-audit/promisor-grid.py --arm current --current probe/crash-auditor.py \
    --case PG01-complete-lane-promisor-config --json
exit=1
PG01: exit=1 traceback=True met=False met_amended=False
   stderr_tail="Traceback (most recent call last): … RuntimeError: deliberate crash …"

# the same row, fed to the shipped probe's own accounting functions:
harness_fault  -> None                      (only harness_leaks / leaked / timed_out are faults)
violated_rows  -> ['PG01-complete-lane-promisor-config']
=> killed=True, status='killed'
```

Same for an internal-error auditor (`exit 2`, `could-not-evaluate: internal: TypeError: …`):
`harness_fault -> None`, `violated_rows -> ['PG01-…']`, i.e. **an internal auditor defect
is credited as a targeted rejection.**

This is exactly the shape `corpus/knowledge/error-is-not-a-verdict.md` forbids
("A gate may correctly fail closed if its subject crashes. A mutation counter claiming a
targeted rejection needs more: a declared exit code and the subject's emitted verdict") and
that KQ25 rejects ("Exit1/negative returncode alone earns kill credit"). The round-23
sibling `tests/report-audit/isolation-mutants.py` avoids it by keying kills on the r23
grid's fault-row semantics; the round-24 probe has no equivalent guard.

Note this is **not** a hypothetical: the shipped probe's `harness_fault` (`:509-527`)
checks `harness_leaks`/`leaked`/`timed_out` and nothing else, and the shipped grid's
`grade` (`:779-816`) has no branch that separates "verdict differs" from "auditor
errored".

**Minimal correction (source, not applied — production edit is L1's):** in
`promisor-mutants.py`, gate the kill on the row's *verdict* class rather than on
`met == False` alone — e.g. exclude rows whose `stderr_tail` shows an internal/traceback
error or whose exit is 2-with-internal-reason, and exclude a mutant whose failed rows
fall outside its declared `expect_rows` class. One-line shape:

```python
killed = bool(bad) and all(expected_match(f, expected) for f in failed)
```

plus a fault filter for `traceback` / `could-not-evaluate: internal:` in `harness_fault`
(so a crashing mutant is reported could-not-evaluate, not killed).

### 4.3 The committed evidence does not show the obligation either

The only committed mutation-sensitivity artifact for round 24 is
`.ufo/waves/round-24/build/out/MutationOracle/sensitivity-promisor-grid.json`. It records
`pristine: "failed rc=1"`, `baseline_mode: true`, and it was produced against the
**build-out** grid `5e96fa6084049550…` and the build-out auditor — **not** the pinned
`b034e159…` grid. Its `killed_ids` (9 of 11) therefore do not describe the pinned
instrument set. Confirmed:

```
$ grep -rl "killed_ids" .   →  5 files, none of them a pinned-grid result
$ python3 -c "…sensitivity-promisor-grid.json"
   grid:      …/build/out/GridOracle/promisor-grid.py   (sha256 5e96fa60…)
   candidate: …/build/out/AuditRepair/report-landing-audit.py (sha256 ea51bc35…)
   pristine:  failed rc=1   baseline_mode: true
```

`mutation-inventory.json` pins `grid_sha256 b034e159…`, `runner_sha256 6e0b9d62…`,
`candidate_auditor_sha256 ea51bc35…` — the right hashes, attached to a result document
produced against a *different* grid. The three shipped hashes are the ones the round
context names, so the intended pairing is unambiguous; the *evidence file* is stale.

---

## 5. F2 (Medium) — KQ35's "paired complete-state controls" is checkable, but the manifest's `twin` links leave 21 of 47 cells unpaired and the pairing is asymmetric

The 47-case manifest declares a `twin` on 26 cells. The unpaired cells are the plain
twin targets (PG07/PG08/PG27/PG29/PG32/PG36/PG45) plus four `policy` exit-0 cells with no
twin at all:

```
exit-0 policy cells without a twin:  PG48-opaque-unused-tree-no-unresolved-token
```
plus (all exit-2) PG21, PG43, PG46, PG47.

Two consequences, both bounded and both visible in P3:

1. **PG48 is graded by its own expectation only.** It is a `policy` row, expects exit 0 /
   `kinds=[]` / `defects=[]`, and its `amended` expectation is *identical* to its
   `original` expectation. Its "same verdict under metadata change" property is therefore
   not witnessed by any pair; it rests on the manifest's exit/kinds/defects expectation
   alone. That is a real weakening of the *paired* clause for exactly the cell the
   supplement (`oracle-supplement-2.json` row `opaque-unused-tree-no-unresolved-token`,
   `expected: "same correct clean twin verdict"`) was filed to witness — the supplement
   promises a *twin verdict* that the committed manifest does not encode.
2. **The 4 opaque exit-2 cells (PG46/PG47) have no plain twin** even though the supplement
   rule explicitly says "Complete twin resolves the blob" for PG46. The manifest's
   `names_any_of` for PG46 is `['$hidden_blob','$missing_subtree']` — no plain counterpart
   row exists to resolve the blob.

This does not falsify the amended contract (the exit/kinds/reason-class expectations still
grade those cells, and my P6 shows PG46/PG47/PG48 all grade correctly). It falsifies the
*pairing* half of KQ35 for 21 cells, and specifically the twin-witness the supplement
promised.

**Minimal correction (source, L1's):** in the manifest, add the missing `twin` links
(a plain, complete counterpart for PG48, PG46, PG47) — *only* as a new manifest revision
with the original bytes preserved per KQ22/KQ31, since `d86b7bea…` is the frozen
authority. Failing that, KQ35's clause should read "paired complete-state controls
**where a twin exists**" so the corpus stops promising a pairing the instrument does not
carry.

---

## 6. F3 (Medium) — "Original versus prospectively corrected oracles remain separately recorded" is true in the corpus, but the *withdrawn* original expectation is nowhere labelled as not-achieved

The corpus part holds and is verifiable:

* `preregistration.json` (commit `d1b9d95`), `oracle-amendment-1.json` (`123640b`),
  `oracle-snapshot-before-inspection.json` + manifest `d86b7bea…` (`f66b226`), and
  `oracle-supplement-2.json` (`aacbd52`) all **precede** the candidate commit `ed1cc3a` in
  git history — the "before inspection" chronology is real, not asserted.
* The manifest is committed once and never rewritten; `original` and `amended` are both
  present on every cell; 7 cells differ (`PG22, PG23, PG24, PG28, PG30, PG34, PG41`).

The corpus-gap: **no corpus file states that the original expectation was withdrawn and
NOT achieved.** `corpus/SCORECARD.md:1199-1201` comes closest ("The initial registration's
blanket unknown-citation expectation is withdrawn/not-achieved, not retroactively passed"),
and `corpus/lessons/round-24.md:67` says the original expectation is "retained as
withdrawn/not-achieved". Both are true. But `corpus/QUALITY.md` — the criterion file — never
says it, and the round-24 QUALITY section has **no preamble line** naming which earlier
criteria remain in force, unlike every other added section (lines 45, 65, 76, 102, 113, 127,
137 all begin "No earlier criterion is superseded…"). KQ35's own ID cell says only
"(qualifies KQ34; no-trade rule unchanged)".

Consequence: a reader of `corpus/QUALITY.md` alone cannot tell that (a) KQ20/KQ25's
kill-credit discipline still binds the round-24 probe, or (b) the original preregistered
expectation was withdrawn rather than met. KQ35's Reject column forbids "expected outcomes
are changed after measuring a candidate and reported as though originally preregistered" —
the corpus satisfies this, but the *criterion file* lacks the standing-preamble device
used elsewhere to say so.

**Minimal correction (corpus, L1's):** add the standard preamble to the round-24 section,
e.g. *"No earlier criterion is superseded. KQ20 (detector must be able to fail), KQ25 (an
error is not kill credit) and KQ34 remain in force; the initial registration's
blanket unknown-citation expectation is withdrawn/not-achieved, not relabelled passed."*

---

## 7. F4 (Low) — "no-trade rule unchanged" has no in-corpus anchor

`corpus/QUALITY.md` cites `AXES.md` **zero** times (verified: `grep -c "AXES" → 0`), while
`corpus/knowledge/cross-lane-scope.md` does cite `../AXES.md:15-17`. The rule KQ35 declares
unchanged lives at `/home/vgpnk/Projects/shokunin/AXES.md:34-36` — outside the lane repo,
in the fleet root. Its last change is `84bade0` (2026-10-16), i.e. it is genuinely unchanged
across round 24, so the claim is true — but it is unresolvable from the corpus and
unverifiable from the lane tree.

**Minimal correction:** cite the anchor in KQ35's Motivating lesson cell, e.g.
"`AXES.md` §Working the axes (fleet root); `lessons/round-24.md` Mistakes; MANIFEST
rounds[428]; …".

---

## 8. Minor / informational

* **`METADATA_REFUSAL` is dead code.** `promisor-grid.py:79` defines
  `METADATA_REFUSAL = ("partial clone (", "promisor pack")` and the constant is never
  referenced again; the live check is the per-case `reason_forbidden` list in the manifest
  (30 of 47 cases carry it; all 30 marked ones do, none of the unmarked ones do — correct
  coverage, since only marked cases could refuse for a metadata reason). Cosmetic, but a
  reader grepping for the metadata guard finds a constant that is not the guard.
* **`withdrawn_original_failures` is computed from `met_original`, not from an explicit
  withdrawn-row set** (`promisor-grid.py:1029-1030`). On a pristine-passes run this yields
  the right set (P3: `PG22` alone), but it is derived, not declared. A case whose *original*
  and *amended* views agree (e.g. PG01) will be listed as "withdrawn" if the candidate
  merely fails it — visible in my crash probe, where `PG01` (whose original == amended)
  appeared in `withdrawn_original_failures`. Low severity (it is a reporting key, not the
  graded verdict), but the same event that triggers it (a failing candidate) is also the
  event that must not be read as an oracle withdrawal.
* **`twin_equal` is `None` (not `True`) for unavailable-state pairs** — expected and correct
  (no document to compare on a refusal); recorded here so a later reader does not read
  `None` as a skipped check.

---

## 9. What was verified vs inferred

**Verified by execution at the pinned revision** (commands and exits above): the shipped
probe's and auditor's selftests; the complete-state pair equality; the required-object
diagnosis wording; the opaque-hole family outcomes; PM01's class-scoped kill on 8
complete-state cells; the 14/14 union discrimination by the three acceptance mutants; the
attribution and diagnostic-error kill paths through the shipped runner's own functions; the
absence of any committed killed_ids artifact referencing the pinned grid.

**Verified by static reading of committed files**: the sha256 pins; the git chronology
(prereg → amendment → frozen manifest → supplement → candidate); the manifest's 47 cells,
`kind`/`twin`/`names_any_of`/`reason_forbidden` structure; the `killed = bool(bad)` and
`harness_fault` bodies; `METADATA_REFUSAL` being unreferenced; the corpus/QUALITY.md
preamble pattern; the AXES.md no-trade clause and its history; `corpus/SOURCES.md` row
count 105 with S105 recording the S095 rejection and S095's immutable `teaches` cell
intact.

**Inferred** (flagged as such): that the four absent `twin` links were an oversight rather
than a deliberate scope limit — no committed file states either way; that the stale
mutation-sensitivity artifact is a superseded build artifact rather than an intentional
filed record — the file's own `grid` field names the build-out grid, so the observation
stands either way.

**Not verified** (out of lane bounds): the full 47-cell suite at the pinned revision; any
behaviour of the r23 `repo-state-grid`/`isolation-mutants` pair beyond reading their
bodies; the truth of the round-24 SCORECARD/LOG claims beyond the mutation artifact.

---

## 10. Minimal corrections, consolidated

| # | Target | Correction |
|---|---|---|
| F1a | `tests/report-audit/promisor-mutants.py:786` | Gate the kill on the mutant's declared class: `killed = bool(bad) and all(expected_match(f, expected) for f in failed)`; keep `attributed` as the reported field. |
| F1b | `tests/report-audit/promisor-mutants.py:509` | Extend `harness_fault` to treat `traceback` rows and `could-not-evaluate: internal:` exits as harness faults, so a crashing/erroring mutant is could-not-evaluate, not killed. |
| F1c | committed evidence | Re-run `promisor-mutants.py` against the **pinned** pair (`b034e159…` grid, `6e0b9d62…` runner, `ea51bc35…` auditor) and commit that result document; the current `sensitivity-promisor-grid.json` names the build-out grid `5e96fa60…` and `pristine: "failed rc=1"`. |
| F2 | `tests/report-audit/promisor-grid-expectations.json` | Add the missing `twin` links (plain counterpart for PG46/PG47/PG48) as a **new** manifest revision preserving `d86b7bea…` bytes; or narrow KQ35's pairing clause to "where a twin exists". |
| F3 | `corpus/QUALITY.md` round-24 section | Add the standard standing-preamble naming KQ20/KQ25/KQ34 and stating the initial expectation is withdrawn/not-achieved. |
| F4 | `corpus/QUALITY.md:183` | Anchor the no-trade rule: cite `AXES.md` §Working the axes (fleet root) in the Motivating lesson cell. |

---

## 11. Tools installed/updates

None. No package was installed or upgraded during this review.

---

## 12. Files written

- `.ufo/waves/round-24/falsify/advice/DocQuality.md` (this report)
- Scratch only, outside the lane tree:
  `/fast/scratch/hyaku/kama-r24/falsify/DocQuality` (clone),
  `/fast/scratch/hyaku/kama-r24/falsify/DocQuality/probe/` (stand-in auditors, three
  stub grids, captured JSON outputs). The lane repo was **not** modified: the only
  lane-tree write is this report.

Report: .ufo/waves/round-24/falsify/advice/DocQuality.md

---

## 13. Addendum — L1 disposition (append-only; §1–§12 above stand unchanged)

Recorded 2026-10-21 from `KamaR23-2` (L1) after this seat's report was delivered.

**F1 (High) — ACCEPTED.** "runtime fault / unattributed false kills". MutationOracle is
preparing V6; GridOracle is preparing a V3 `internal_error` full-stderr flag. The
required shape is preserved: actual class rows are kept, and diagnostic failure is
separated from verdict failure. My §4.2 measurements stand as the falsifiable basis:
`promisor-mutants.py:786` `killed = bool(bad)` does not consult `attributed` (`:793`),
and `harness_fault` (`:509-527`) inspects only `harness_leaks`/`leaked`/`timed_out`, so a
traceback row and an internal `could-not-evaluate` row are both credited kills.

**F1 cold receipt — DISPOSITIONED, not re-opened by this seat.** The pre-contract
failed-pristine sensitivity receipt carries no admission credit and is already recorded in
`.ufo/waves/round-24/receipt-errata.json` (entry for
`build/out/MutationOracle/sensitivity-promisor-grid.json`: "obsolete unreproducible
preliminary, no current producer or admission credit"). §4.3 therefore needs no further
correction beyond the errata that already exists; the final pinned-pair receipt remains
the L1-owned measurement.

**F2 (Medium) — NO CHANGE TO THE FROZEN 47 / DATA / TWIN LINKS.** My §5 proposal to add
`twin` links to `promisor-grid-expectations.json` is **withdrawn**: the manifest is
frozen, never rewritten, and no expectation byte changes. The coverage gap stays
explicit instead: 42 of 47 cells participate in a plain-twin pair; the five `policy`
cells with no twin inside the frozen 47 are PG21, PG43, PG46, PG47 (exit 2) and PG48
(exit 0), and they are graded by their own per-cell exit/kinds/defects/reason-class
expectation, never by a twin verdict equality. Private plain metadata-only companions
for PG46/PG47/PG48 are exercised **outside** the frozen 47 as a supplement — the two
opaque unavailable-state companions report exit 2 with no verdict document to compare,
and the clean companion reports clean 0/0 — and they add no primary score, change no
manifest cell, and do not turn the frozen 47 into a paired population.

**F3 / F4 — CONTINUATION PROPOSED, NOT APPLIED BY THIS SEAT.** The paste-ready
append-only continuation is at
`.ufo/waves/round-24/falsify/out/DocQuality/append.txt`. It adds no criterion, rewrites
no row, and states: (1) KQ20/KQ25 remain in force and kill credit is verdict-shaped
rather than diagnostic-shaped; (2) the no-trade rule is anchored to `AXES.md` §Working
the axes (fleet root, lines 34-36; unchanged since `84bade0`); (3) the initial
registration's blanket unknown-citation expectation is withdrawn and **not** achieved; and
(4) the twin-pairing coverage bound is stated, not implied.

**No production edit was made by this seat.** `corpus/QUALITY.md`, `corpus/lessons/`,
`corpus/SOURCES.md`, the manifest, the grid, the probe and the auditor are untouched; the
only lane-tree writes are this report and the out/DocQuality artifact above.

Report: .ufo/waves/round-24/falsify/advice/DocQuality.md

---

## 14. Addendum 2 — v2 continuation wording (append-only; §1–§13 stand unchanged)

Recorded 2026-10-21 from `KamaR23-2` (L1) after this seat filed §13. Version 1 of the
append proposal (`.ufo/waves/round-24/falsify/out/DocQuality/append.txt`) is **filed and
unchanged**; the wording L1 should apply is **version 2**, at
`.ufo/waves/round-24/falsify/out/DocQuality/append-v2.txt`.

**Correction L1 required, and this seat accepts.** Version 1's phrase "kill credit is
verdict-shaped, never diagnostic-shaped" was too broad: KQ34 requires the refusal
reason to be pinned, and a mutant that drops or rewrites that reason must stay
detectable. v2 therefore separates three observables that v1 merged:

1. **Substantive class witness** — the only thing that discharges a KQ35 paired
   obligation. Complete-state obligation: a cell that must carry a normal verdict
   (exit 0/1) answering with a refusal (exit 2). Unavailable-state obligation: a cell
   whose required object is genuinely unavailable (correct answer exit 2) answering with
   a valid verdict (exit 0/1). A witness is per obligation and per class; a
   complete-state witness discharges no unavailable-state obligation.
2. **Reason-loss sensitivity** — a lost or altered pinned reason is detected and
   reported, but it is not evidence that an unavailable object was accepted, so it earns
   no availability-acceptance credit and cannot serve as the unavailable-state witness.
3. **Diagnostic-only outcome** — traceback, internal `could-not-evaluate`, timeout,
   harness leak, or a failure outside the mutant's declared envelope: 0 credit for any
   obligation, reported separately from the class witnesses.

**Bounded wording, no new policy fitted to code.** v2 states the substantive obligation
and leaves the mechanism to L1's V6 (MutationOracle) and V3 (GridOracle `internal_error`
full-stderr flag) instrument work; it prescribes no implementation, adds no criterion row,
rewrites no row, and changes no expectation byte.

**Probe exit 0 is a completed measurement, not an admission.** v2 says so explicitly: it
records that a finite, named inventory was measured over a pinned population. An
obligation is discharged only by a substantive class witness on a named control of that
class. Survivors are reported with their named reason and credit nothing; the count of
survivors not so accounted for is 0. (Committed inventory: exactly one documented
survivor, PM07, whose redundancy reason is named in the mutation inventory; the
committed sensitivity document lists PM07 alone.)

**Pairing coverage: encoded fact kept distinct from a planned observation.** The encoded
fact, measured on the frozen manifest `d86b7bea…` only: 26 cells carry a `twin` pointer
forming 25 unordered pairs; 42 of 47 cells participate in at least one pair; the five
unpaired `policy` cells are PG21, PG43, PG46, PG47 (exit 2) and PG48 (exit 0), and
PG48's `original` and `amended` expectations are identical. The private plain
metadata-only companions for those cells are **planned (W3), not yet live or measured**;
W3 will cover PG21 and PG43 as well as PG46, PG47 and PG48, outside the frozen 47, and
if observed are expected to report four paired refusals at 2/2 rows each with no
verdict-document equality available (a refusal emits no verdict document) and PG48 clean
at 0/0. That is stated as an expectation, **not** a measurement, and no companion run is
claimed. The companions add no primary score, change no manifest cell, and do not convert
the frozen 47 into a paired population.

**Class witnesses as observed on the pinned pair** (grid `b034e159…`, probe `6e0b9d62…`,
auditor `ea51bc35…`), which is what makes the v2 wording answerable rather than
aspirational:
- PM01 blanket refusal, complete-state class: `PG01` exit 2 (expected 0), `PG09` exit 2
  (expected 1, kinds `landed-omitted`), `PG26` exit 2 (expected 0), each stderr carrying
  the named reason `partial clone (remote.origin.promisor)`, `objects_acquired` empty.
- PM04 acceptance, unavailable-state class: `PG33` exit 1 (expected 2) and `PG34` exit 1
  (expected 2), each with kinds `unresolved-full-hash` — a valid verdict, not an error and
  not a guessed empty object.
- Unavailable-class coverage: PM03, PM04 and PM06 over all 14 exit-2 cells kill all
  three; the union of failed rows is 14 of 14; no exit-2 cell is left undiscriminated.

**No production edit by this seat.** `git status` on `corpus/`, `tools/` and `tests/` is
empty; the KQ35 row at line 183 is byte-identical. This seat's writes are
`falsify/out/DocQuality/append.txt` (v1, filed), `falsify/out/DocQuality/append-v2.txt`
(v2) and this appended §14. The F1 disposition in §13 (L1-accepted; V6/V3 in preparation)
and the cold-receipt disposition in §13 (already in `receipt-errata.json`) are unchanged.

Report: .ufo/waves/round-24/falsify/advice/DocQuality.md

---

## 15. Addendum 3 — v3 payload is final (append-only; §1–§14 stand unchanged)

Recorded 2026-10-21 from `KamaR23-2` (L1). **v3** is the final paste-ready payload:
`.ufo/waves/round-24/falsify/out/DocQuality/append-v3.txt`. v1 (`append.txt`) and v2
(`append-v2.txt`) remain **filed and unchanged**.

**Three corrections L1 required, applied in v3:**

1. **Count language replaced by exit-pair notation.** v2's "four paired refusals … at 2 of 2
   rows each … and PG48 clean at 0 of 0" was count language dressed as an observation.
   v3 uses **EXITPAIR(2,2)** for each of PG21, PG43, PG46 and PG47 (both sides refusing;
   no verdict-document equality available, because a refusal emits no verdict document) and
   **EXITPAIR(0,0)** for PG48 (both sides clean). No `2 of 2` / `0 of 0` counts remain.
2. **Survivor rule is normative, not a premature measurement.** v2 asserted "the count of
   survivors not so accounted for is 0", which is a measurement this seat had not made.
   v3 states the rule instead: **report each survivor with its reason; a survivor without a
   documented reason discharges no obligation.**
3. **"diagnostic-only" replaced by INVALID-EXPERIMENT / RUNTIME-FAULT.** v2's phrase
   "diagnostic-only outcome" was a category of this seat's own invention. v3 names the
   enum outcomes: a traceback, an internal error, a timeout, a harness leak, or a failure
   outside the mutant's declared envelope is an **INVALID-EXPERIMENT** or
   **RUNTIME-FAULT** outcome — 0 credit for any obligation, reported separately from the
   class witnesses. v3 also records the interaction L1 specified: in the V6/V7 enumeration
   such an outcome is a reason difference on the same could-not-evaluate exit as a
   content-derived refusal, so a lost named reason can still earn **KQ34 reason-loss
   sensitivity** while never earning **KQ35 acceptance credit**.

**Also applied:** the continuation heading is now a single Markdown line, and the payload
is bounded by the principles span `AXES.md:23-75` (§Working the axes through the
SCORECARD contract); the no-trade anchor cites `AXES.md` lines 25–38, whose substantive
sentence is at 34–36.

**Unchanged:** no criterion row added, no row rewritten, no expectation cell or manifest
byte changed, no SOURCES row added, no test run beyond the two shipped selftests, no
production file edited. The F1 disposition (§13, L1-accepted; MutationOracle V6, GridOracle
V3 `internal_error` full-stderr flag) and the cold-receipt disposition (§13, already in
`receipt-errata.json`) stand. The pairing bound stays explicit: 42 of 47 frozen cells
participate in a plain-twin pair; the five unpaired `policy` cells are PG21, PG43, PG46,
PG47 (exit 2) and PG48 (exit 0); their private plain companions are **planned (W3), not
yet live or measured**, and no companion run is claimed by this seat.

**No production edit by this seat.** `git status` on `corpus/`, `tools/` and `tests/` is
empty; the KQ35 row at line 183 is byte-identical. This seat's writes are
`falsify/out/DocQuality/append-v3.txt` (final), `append-v2.txt` and `append.txt` (both
filed, unchanged), and this appended §15.

Report: .ufo/waves/round-24/falsify/advice/DocQuality.md

---

## 16. Addendum 4 — integrator cutover selected; this seat's v3 line 21 was wrong (append-only; §1–§15 stand unchanged)

Recorded 2026-10-21 from `KamaR23-2` (L1). The integrator selected
`.ufo/waves/round-24/fixes/doc/QualityCutover/append.txt` (13 lines, untracked staging
under `fixes/`), derived from this seat's filed v2/v3 principles. All of this seat's
originals remain retained as evidence: `out/DocQuality/append.txt` (v1),
`append-v2.txt` (v2), `append-v3.txt` (v3), and this report.

**This seat's v3 line 21 was wrong, and L1 is right.** v3 said: "In the V6/V7 enumeration
such an outcome is a reason difference on the same could-not-evaluate exit as a
content-derived refusal, so a lost named reason can still earn KQ34 reason-loss
sensitivity — but never KQ35 acceptance credit." That merged two different things. A
runtime fault — traceback, internal error, timeout, harness leak, malformed verdict, invalid
exit, out-of-envelope failure — is **could-not-evaluate**, and it must never be re-labelled
as ordinary same-exit reason-loss sensitivity. Only a **valid, attributed same-exit
content-derived refusal whose named reason changed** can expose reason-loss sensitivity at
all. The integrator's cutover states this correctly and separately, and also adds a
distinction this seat had not drawn: an unchanged normal exit does not by itself establish
that the verdict document is unchanged or that a substantive exit changed, so its detail
must be preserved separately. The cutover also preserves the actual class rows and
unexpected rows without widening the attribution envelope.

**Cutover text verified against this seat's measured facts (no new measurement, no
test):**
- "26 twin pointers forming 25 unordered links, with 42 of 47 cells participating" —
  recomputed on the frozen manifest `d86b7bea…`: 26 pointers, 25 unordered links, 42
  participating; the 5 unpaired are exactly `PG21, PG43, PG46, PG47, PG48`. Match.
- Manifest sha256 `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1` —
  recomputed on the committed file. Match.
- Exit-pair expectations `(2,2)` for the four unavailable cells and `(0,0)` for PG48 —
  consistent with the frozen amended expectations: PG21/PG43/PG46/PG47 all
  `exit=2, reason_class=unavailable`, PG48 `exit=0`. Match, and correctly framed as
  expectations rather than observations.
- Standing KQ20/KQ25 binding, class-specific witnesses, no-trade anchor at `AXES.md`
  lines 34–36, and withdrawn-not-achieved original expectation — all carried over from the
  filed v2/v3 principles. Match.

**Cosmetic note for whoever lands the file (no rewrite requested).** The staged cutover
has five missing-space joins that read as run-together words: `lines34`, `has26`,
`outside47`, `pairs(2,2)`, `and(0,0)`. Content is unaffected; this seat does not ask for
a rewrite.

**No production edit by this seat.** `git status` on `corpus/`, `tools/` and `tests/` is
empty; the KQ35 row at line 183 is byte-identical; `fixes/` is the integrator's untracked
staging area and was not touched by this seat. This seat's writes remain the three filed
append versions and this appended §16. No further rewrite or test is requested or run.

Report: .ufo/waves/round-24/falsify/advice/DocQuality.md
