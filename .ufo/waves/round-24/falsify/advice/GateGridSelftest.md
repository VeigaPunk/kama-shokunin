# GateGridSelftest — promisor-grid `--selftest` + unknown-case negative control (round 24)

VERDICT: **HOLDS** for both required harness behaviours (selftest → 0, unknown case → 2, and
the 2 is a real could-not-evaluate, not a gate pass). **PARTIAL** on the twins +
acquisition-grade question: neither path is exercised by either assigned command; the twin
comparator is additionally **inert for refusal twins** (observed). **FALSIFIED** for the
implicit claim that “selftest exit 0” attests the fixed47 population, the strong
`names_any_of` grader, or twin-link integrity — three bounded mutations of the expectations
table all still pass the selftest with exit 0.

Scope: exactly the two assigned commands (`--selftest`, `--case negativecontrol`) plus three
mutation variants of the *same* `--selftest` command run against scratch copies of the
expectations table, static source reads of the grid, and read-only inspection of
sibling-lane retained grid artifacts. No full grid, no other lane suite, no mutation grid,
no network/transport/execution payload, no PM08 execution (static only). Production
`production/.jj/index`, fleet, sibling lanes, operator config, routing, services and real
object stores were not touched. No tools were installed or updated (none needed).

## 1. Snapshot identity (observed)

| Item | Value | Source |
|---|---|---|
| production HEAD | `2e254a1763a9c08aa07fc53081287f506c447d84` | `git rev-parse` |
| production worktree | clean except untracked `.ufo/waves/round-24/falsify/` | `git status --porcelain` |
| scratch clone | `git clone --no-hardlinks` → `/fast/scratch/hyaku/kama-r24/falsify/GateGridSelftest`, detached at `2e254a1` | observed |
| scratch ≡ production | `tests/report-audit` trees byte-identical (`diff -rq` → IDENTICAL); `tools/report-landing-audit.py` identical | observed |
| source tool | `tools/report-landing-audit.py` `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220` | `sha256sum` (matches L1 pin `ea51bc35…`) |
| runner | `tests/report-audit/promisor-grid.py` `b034e1596746d312989b7894c0757b67859df19a476a01ccd95076424135cefa` | `sha256sum` (matches L1 pin `b034e159…`) |
| manifest | `tests/report-audit/promisor-grid-expectations.json` `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1` | `sha256sum` (matches L1 pin `d86b7bea…`) |
| frozen (r23) auditor blob | `git cat-file blob 0df800e…:tools/report-landing-audit.py` → `da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1` | equals `oracle-snapshot-before-inspection.json → frozen_auditor_sha256` |
| population digest | `612b0a74f3eebaa9074bdde8ecd8f194f55ebaf9a35ab2b975fddbff8dd2ed88` (47 cases) | recomputed from the pinned table; equals L1’s `build/out/GridOracle/population.json` |
| git | 2.56.0 (≥ the inherited 2.45 floor; that L0 prerequisite stays open elsewhere) | `git --version` |
| TMPDIR | `/fast/scratch/hyaku/kama-r24/falsify/GateGridSelftest/tmp` for every subprocess | `make_root()` keeps the root under `SCRATCH=/fast/scratch/hyaku/kama-r24` |

## 2. Required command results (exact command → exit → tokens)

| # | Command (cwd = scratch clone) | Exit | Observed output | Finding/token |
|---|---|---|---|---|
| C1 | `python3 tests/report-audit/promisor-grid.py --selftest` | **0** | stdout 11 lines, all `ok`, final `selftest cases=11 failed=0`; stderr empty | required 0 met |
| C2 | `python3 tests/report-audit/promisor-grid.py --case negativecontrol` | **2** | stdout **0 bytes**; stderr exactly `could-not-evaluate: unknown case(s): negativecontrol` | required 2 met; `CNE_PREFIX` (`promisor-grid.py:80`) satisfied; **no verdict document, no `violations` counter, no JSON → not a gate pass** |

C1’s eleven checks (all `ok`): `unique-case-ids`, `builders-present`, `open-builders-present`,
`reason-classes-known`, `population-stable`, `premise-marks-lane`, `premise-fleet-plain`,
`premise-complete`, `premise-fake-absent`, `premise-hole-detected`, `premise-fake-still-absent`.

Auxiliary probes of the same script (usage-error paths only; no fixture, no auditor, no state):

| Command | Exit | stderr |
|---|---|---|
| `promisor-grid.py --case` (missing value) | 2 | `promisor-grid.py: error: argument --case: expected one argument` |
| `promisor-grid.py --case negativecontrol --arm bogus` | 2 | `promisor-grid.py: error: argument --arm: invalid choice: 'bogus' …` |
| `promisor-grid.py --arm both --json --case negativecontrol` | 2 | `could-not-evaluate: unknown case(s): negativecontrol`; stdout 0 bytes |
| `promisor-grid.py --selftest --case negativecontrol` | **0** | `selftest cases=11 failed=0` (see F4) |

## 3. Axes

| # | Axis | Result |
|---|---|---|
| A1 | selftest exits 0 | **HOLDS** (C1) |
| A2 | unknown case exits 2 as could-not-evaluate, not a gate pass | **HOLDS** (C2: empty stdout, typed stderr) |
| A3 | twins path exercised by the assigned commands | **NO** (F2) — reachable only from the graded arm run |
| A4 | acquisition-grade (no-acquisition pin) exercised by the assigned commands | **NO** (F2) — reachable only from the graded arm run |
| A5 | selftest attests the fixed47 population / grader strength / twin links | **FALSIFIED** (F1) |
| A6 | twin comparator meaningful for refusal twins | **PARTIAL/FALSIFIED for 5 of 25 pairs** (F3) |
| A7 | exit-2 signal unambiguous for a gate | **PARTIAL** — exit 2 is overloaded (F4) |
| A8 | no-acquisition pin proves “no transport invocation” | **PARTIAL** — it proves “no object added” (F5) |

## 4. Findings

### F1 — FALSIFIED: `--selftest` exit 0 attests nothing about the graded population, the grader strength, or twin links

Three bounded mutations of the expectations table (scratch copies only; the pinned file was
never modified and was re-verified byte-identical, `d86b7bea…`, afterwards):

| Variant | Mutation | population_sha256 | `--selftest` exit |
|---|---|---|---|
| m1 | drop graded case `PG48-opaque-unused-tree-no-unresolved-token` (47 → 46 cases) | `612b0a74…` → `d18941f8…` | **0** (`selftest cases=11 failed=0`) |
| m2 | weaken the strong grader: `PG13-missing-lane-blob-promisor.names_any_of` → `["$not_a_real_token"]` | **unchanged** `612b0a74…` | **0** |
| m3 | point `PG01-complete-lane-promisor-config.twin` at `PG99-does-not-exist` | `612b0a74…` → `a730a758…` | **0** |

Root cause (source, exact): `promisor-grid.py:898` — `cases.append(("population-stable",
population(table) == population(table)))` is a **tautology** (a pure function compared with
itself). It can only fail on nondeterminism; it never pins a case count and never compares
against a digest. Consequently the selftest cannot detect a dropped graded row, a weakened
`names_any_of`/`reason_forbidden` grader, or a broken twin link.

Second, sharper consequence: `population()` (used for `population_sha256`, `promisor-grid.py:874-881`
and recorded in every grid artifact) hashes only
`[case, kind, builder, frozen, original, amended, twin]`. `names_any_of` and
`reason_forbidden` live at **case level** and are *outside* the fingerprint (verified: m2
leaves the digest bit-identical). The retained population digest therefore does **not** attest
the “strong `names_any_of`” property that L1 treats as the load-bearing grader; a grader
weakening is invisible to both the selftest and the population digest.

Minimal correction (report only — no production edit):
1. replace the tautology with `("population-pinned", len(table["cases"]) == 47 and
   population(table) == "612b0a74f3eebaa9074bdde8ecd8f194f55ebaf9a35ab2b975fddbff8dd2ed88")`;
2. extend `population()` to include the case-level `names_any_of` and `reason_forbidden`
   (so the digest covers grader strength);
3. add a selftest case asserting every `case["twin"]` names an existing case and that twin
   links are symmetric (`twin` ↔ reverse map).

### F2 — PARTIAL: neither the twins path nor the acquisition-grade path is exercised by the assigned commands

Call-site evidence in `tests/report-audit/promisor-grid.py`:
`object_inventory` (310), `run_auditor` (694), `grade` (779), `normalise_document` (860) are
called **only** from `run_case` (978, 1062). `selftest` (884) calls only `build()` and reads
the premise dict; the unknown-case control returns at `promisor-grid.py:945-948`, *before*
`make_root()` (961) — so no fixture, no auditor, no inventory, no grading, no comparison
happens. Therefore:

* the twin comparator (`promisor-grid.py:986-1015`) is **unreachable** from `--selftest` and
  from `--case negativecontrol`;
* the no-acquisition pin (`before`/`after` object inventories at 818/821, graded at 808-810
  “the audit acquired objects”) is **unreachable** from both.

Corroboration that the paths *are* exercised by graded arm runs elsewhere (read-only, sibling
artifacts — **not** my measurement): `.ufo/waves/round-24/falsify/out/CaseConfigTwins/grid.json`
(current auditor `ea51bc35…`, expectations `d86b7bea…`) reports `twin_compared_rows=4`,
`twin_equal True×4`, `twin_mismatch=[]`, and `objects_acquired` empty for all 4 rows; the same
pattern appears in `CaseUnselectedBranch/grid/candidate.json` and
`CaseUnusedBlobless/candidate.json`. So the *evidence* exists — it just is not produced by the
two commands this assignment scoped, and a gate that cites “selftest passed” as proof of
twin parity / no-acquisition is citing the wrong artifact.

### F3 — OBSERVED + INFERENCE: the twin comparator is inert for refusal twins

25 distinct twin pairs are declared in the pinned table (26 case-level `twin` links; `PG07`
has three partners, `PG10` three, `PG25`/`PG36` two each). **5 pairs have both members
expecting exit 2**: `PG13/PG14`, `PG15/PG16`, `PG17/PG18`, `PG19/PG20`, `PG33/PG34`.

Mechanism (`promisor-grid.py:1005-1015`): a refusal prints no verdict document, so
`normalise_document` returns `None` → `results[partner] = None` (1009) → `twin_equal` becomes
`None` (1014) → the pair is neither compared nor counted as a violation; it simply drops out
of `twin_pairs_compared`.

Observed (sibling artifact, current arm): `.ufo/waves/round-24/falsify/out/CaseCitedHole/grid-PG33-PG34.json`
→ `twin_compared_rows=0`, `twin_pairs_compared=0`, `twin_equal None×2`, while the exit-0 pairs
in `CaseConfigTwins/grid.json` compare normally (`4` compared, `True×4`).
The other four refusal pairs are **[INFERENCE]** from the identical code path with the same
expected exit 2 (I did not run those rows).

Consequence for the amended contract: “complete marked versus unmarked twins … retain
identical substantive verdicts” is enforced by the twin comparator only for the **20
verdict-producing pairs**. For the 5 refusal pairs the twin path contributes nothing; the only
guarantee is per-row (exit code + reason class + `names_any_of`), so a marked twin that
refused for a materially different reason than its plain twin is **not** flagged by the twin
comparison. The honest receipt wording is: *identical verdicts verified for 20 verdict-producing
twin pairs; refusal twins are verified per row, not by comparison.* The counter gap
(`twin_pairs_in_manifest=25` vs `twin_pairs_compared`) is visible but is not a violation, so a
reader who checks only `violations=0` would not notice.

Minimal correction: when either twin document is absent, compare the comparable tuple
`(exit, reason_class)` instead of skipping, and report the inert pairs explicitly (e.g.
`twin_inert_pairs`) so the receipt cannot be read as “all twins compared”.

### F4 — GATE HAZARD: the selftest branch swallows the unknown-case guard, and exit 2 is overloaded

`promisor-grid.py:934-940` (selftest branch) precedes `945-948` (unknown-case guard).
Observed: `promisor-grid.py --selftest --case negativecontrol` → **exit 0** with
`selftest cases=11 failed=0`, i.e. a combined invocation reports *success* while the requested
case does not exist and was never evaluated. Any gate that composes the two flags must not
read that 0 as “the case was evaluated”.

Additionally, exit code 2 is not specific to could-not-evaluate: argparse usage errors exit 2
as well (observed: `--case` with a missing value, and `--arm bogus`). The negative control
must therefore be asserted by its **stderr token** (`could-not-evaluate: unknown case(s): …`)
**and** empty stdout — not by the exit code alone. The module docstring (lines 25-27) already
documents 2 as “could not evaluate (fixture premise, harness or environment failure)”, which
is the same overloading at the contract level.

### F5 — INFERENCE (source-level, not exercised by my commands): the acquisition pin proves “no object added”, not “no transport invocation”

The pin compares `object_inventory` before/after the auditor (818, 821) and fails a row when
the store grew (808-810). It therefore detects a **successful** acquisition; a transport
*attempt* that fails and leaves the store unchanged is invisible to it. The config-marked
fixtures point `remote.origin.url` at an absent path (`mark_config`, 197-202), so a lazy
fetch attempt would fail fast rather than hang — but the resulting refusal reason could still
satisfy the amended `"unavailable"` reason class: `REASON_CLASSES["unavailable"]`
(57-70) admits “unavailable”, “not found”, “missing”, and the only `reason_forbidden`
markers in the table are the r23 metadata ones (“partial clone (”, “promisor pack”,
`METADATA_REFUSAL`, 79). A transport-flavoured refusal could therefore be graded as a
local-unavailability refusal. Minimal correction: extend `reason_forbidden` on the 14 exit-2
rows with transport markers (e.g. `fatal: unable to access`, `Could not resolve host`,
`transport`) — the mechanism already exists and 30 cases already carry the field. Flagged
**[INFERENCE]**: I did not execute those rows (full grid out of bounds).

### F6 — Corroborated hazard carried into this report (from `KamaR23-2.CaseFleetBlobless`)

Manual probing of a `--keep`ed blobless fixture can materialise a missing blob and silently
evaporate the premise (false clean exit 0 instead of the correct exit 2). My probes never
touch a blobless fixture — the selftest builds only the config-marked lane via `build()`, and
every git probe the grid itself makes is `--no-lazy-fetch` — but the rule generalises to
anyone inspecting a kept fixture: **every** probe must carry `--no-lazy-fetch`.

## 5. Residual risk and verification gaps (explicitly unverified)

* **No full grid was run** (out of bounds). The graded 47-row verdict against the candidate
  auditor `ea51bc35…` is **not** verified by me; every statement about graded rows rests on
  static reading plus sibling-lane retained artifacts.
* The refusal-twin inertness is **observed** only for `PG33/PG34` (CaseCitedHole artifact);
  `PG13/14`, `PG15/16`, `PG17/18`, `PG19/20` are **[INFERENCE]** from the same code path.
* The frozen arm’s twin counters are 0 in every retained artifact I read — expected, because
  the r23 baseline refuses with metadata and prints no verdict document; its twin baseline is
  therefore not a comparable-twin measurement at all.
* F5 is source-level inference only; no transport-shaped refusal was produced or observed.
* The inherited **Git ≥ 2.45** floor is satisfied on this host (2.56.0) but that L0
  prerequisite remains open and was not measured here.
* The **original** unknown-from-metadata expectation (preregistration `expected_after[3]`) is
  withdrawn by `oracle-amendment-1.json` and is **not** re-labelled as passed anywhere in this
  report; every grid statement above is under the amended view.
* The source-census final verification of the S105/S095 ledger rows is L1-owned after this
  stage; nothing in this report touches it.

## 6. Files written (this lane)

* `.ufo/waves/round-24/falsify/advice/GateGridSelftest.md` (this report)
* `.ufo/waves/round-24/falsify/out/GateGridSelftest/selftest.stdout.txt`,
  `selftest.stderr.txt`, `negativecontrol.stdout.txt` (0 bytes), `negativecontrol.stderr.txt`,
  `selftest-plus-unknown.stdout.txt`, `selftest-plus-unknown.stderr.txt`, `exit-codes.txt`,
  `pinned-hashes.txt`
* `.ufo/waves/round-24/falsify/out/GateGridSelftest/variants/m1.stdout.txt`,
  `m2.stdout.txt`, `m3.stdout.txt` and the mutated `m1|m2|m3-expectations.json`

Scratch (outside the repo, disposable): `/fast/scratch/hyaku/kama-r24/falsify/GateGridSelftest`
(clone + `mut/` variants + `tmp`/`tmp2` TMPDIRs, both emptied by the grid’s own cleanup).
Note on production tree state: `git status` in production also shows
`M .ufo/waves/round-24/build/advice/GridOracle.md` and `?? .ufo/waves/round-24/fixes/` — both
are **other lanes’** writes observed during my run; I did not create, edit or revert them, and
the only production paths I wrote are the two listed above (`falsify/advice/GateGridSelftest.md`
and `falsify/out/GateGridSelftest/`).
`/fast/scratch/hyaku/kama-r24/promisor-grid-rsuiudo7` is a **pre-existing sibling** grid root
(mtime 15:20:04, before my 16:46 runs) and was not created, used or removed by me. No
installations or updates were performed.

Report: .ufo/waves/round-24/falsify/advice/GateGridSelftest.md
