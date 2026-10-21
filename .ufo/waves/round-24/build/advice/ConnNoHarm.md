# ConnNoHarm — r23 grid rows/mutants affected by the r24 promisor-completeness repair

Seat: KamaR23-2.ConnNoHarm-2 (connector, leaf; no subagents, no production edits).
Date: 2026-10-21. Base: `0df800e896f6bce285a81e794ad4ae1d1e6c3a71`.
Artifacts: `.ufo/waves/round-24/build/out/ConnNoHarm/` —
`grid-policy-rows.patch` (variant A), `grid-policy-rows-closure-variant.patch`
(variant B), `mutants-policy.patch`, `probe-base-behavior.txt`.

## 0. Correction (append-only; supersedes my first issue)

**Withdrawn:** my first version claimed T01 is *not* content-complete and
proposed re-pinning it to exit 2 as an ungraded tradeoff. That inference was
wrong — I measured F23's shape, not T01's.

**Measured** (`out/ConnNoHarm/probe-base-behavior.txt` §12): the grid builds
T01 with `t_blobless` (`tests/report-audit/repo-state-grid.py:596-602`),
which clones **with** checkout; the checkout hydrates the fixture's only
blob. `git rev-list --objects --missing=print --no-object-names master` on
that clone reports **3 objects, no `?` line**, and the worktree file `f` is
present. The clone is content-complete; the r23 base auditor still refuses it
(`exit 2 partial clone (promisor pack)`) — that refusal is exactly the
rejected-harmed behavior. F23 (`f_promisor_pack`) is the *different* shape
(`--no-checkout`): its blob stays absent (`?6e98d181…`), so it is genuinely
incomplete and its exit 2 is justified — only its **reason** changes.

**Consequence:** T01 is restored to its round-23 expectation (exit 0, clean)
and **graded** — kind `tradeoff` → `control`. It is no longer an ungraded
red cell; it becomes the visible red cell that the r24 candidate must turn
green, and the r24 claim is graded by it together with C14/C15/C20. Both
candidate patches below carry this change; it is common to both policy
variants.

**Also open:** the *citation-absence* policy is pending CritUnknown, so the
rows whose expectation depends on it are given in two variants (A = the
preregistration's literal "missing citation in any promisor-backed repository
is unknown → exit 2"; B = closure-grounded "retain the original failed local
lookup once the selected roots' closure is complete, no blanket unknown
refusal"). Apply exactly one; §3 lists the deltas.

## Verdict

**4 of the 46 r23 grid rows and 5 of the 31 r23 mutants are touched by the
justified policy change; 42 rows and 26 mutants are unchanged invariants.**
The r23 grid is retained with the policy rows re-pinned (F06, F23, and F27
under variant A only), **T01 restored and graded**, and **8 new graded rows
added** (C14–C21) — without them the change silently deletes the kill
coverage of two mutants (M27, M29) and leaves the r24 claim ungraded inside
the retained grid. `O01` and `O02` stay open/red (reported, never graded);
`M20` stays a survivor and stays reported. No r23 row or artifact is deleted
to make the r24 candidate look clean; every expectation change below is
recorded with its round-23 value.

Measured cause of the harm (bounded probes): a **content-complete** lane that
carries promisor metadata is refused by the r23 base auditor (exit 2
`partial clone …`), while the identical unmarked lane returns its correct
verdict (exit 0 clean / exit 1 `landed-omitted`). T01 is the same thing in
the grid's own vocabulary, and the r23 base makes it red.

## 1. Axes named

| axis | meaning | r23 state |
|---|---|---|
| A1 calibration | correct exit/finding for a *supported* repository state | 7 (lowest assigned); r23 hurt it by refusing complete marked repos |
| A2 operability | a correct complete workflow must not be refused | r23 harm: T01 red cell, metadata-only refusal |
| A3 evidence integrity | never guess absence; unknown ⇒ exit 2 | r23 conflated "metadata present" with "evidence absent" |
| A4 isolation | `--no-lazy-fetch`, `--no-replace-objects`, log/signature suppression, timeout | must survive unchanged; F06/F27 are its only live probes |
| A5 measurement continuity | r23 grid/mutant coverage must not silently shrink | at risk: 2 mutants lose their killers, 2 more abort the harness |

## 2. Row map (r23 grid `tests/report-audit/repo-state-grid.py`, base 0df800e)

46 rows: 26 fault, 4 contract, 13 control, 2 open, 1 tradeoff.
Current arm: 43/43 graded rows met; 3 cells not met (O01, O02, T01 — all
ungraded). Source: `.ufo/waves/round-23/final/grid-both.json`.

### 2.1 Affected rows (4) — expectation change required, each with a reason

| row | kind | r23 expectation | variant A | variant B | change class |
|---|---|---|---|---|---|
| `F06-lazy-fetch-command` (grid.py:651) | fault | exit 2, reason `partial clone` | exit 2, reason **unknown** | exit **1**, kinds `[landed-unresolved, unresolved-full-hash]` | reason pin (A) / exit + kinds (B). The lane's selected-root closure is complete, so the missing citation is proved absence (B). The `core.sshCommand` marker assertion (no program executed) becomes **load-bearing for the first time** in both variants — it was vacuous while the metadata refusal ran first. |
| `F23-promisor-pack-without-config` (grid.py:670) | contract | exit 2, reason `promisor pack` | exit 2, reason **unknown** | exit 2, reason **unknown** | reason pin only. The fixture is genuinely incomplete (`--no-checkout`, `?6e98d181…`), so exit 2 stands; only its ground changes from a metadata refusal to an availability refusal. |
| `F27-filter-only-promisor-remote` (grid.py:674) | fault | exit 1, kinds `[landed-unresolved, unresolved-full-hash]` | exit **2** (unknown) | **unchanged** | exit change under A only. Under B the closure is complete and the original proved-absence finding stands, so this row leaves the affected set. The marker assertion must stay in both, or `M02` loses its killer. |
| `T01-blobless-partial-clone` (grid.py:689) | tradeoff → **control** | exit 0 (ungraded) | exit 0, **graded** | exit 0, **graded** | **kind change only** (value unchanged). The clone checks out, so its only blob is hydrated: the store is content-complete and the correct verdict is the clean exit 0 the full clone gives. Grading it is what turns the r23 harm into a visible red cell the r24 candidate must fix. |

**Contradiction, stated.** r23's lesson declares "partial clones are refused
even when every cited object is local (grid T01)" as an accepted tradeoff;
r24 reverses it for content-complete marked stores — and T01 *is* such a
store. The r23 sentence must be corrected append-only (ConnDocs lane), not
edited.

### 2.2 Unchanged invariants (42) — do not touch, they are the no-harm core

* 24 faults not promisor-related: F01, F02, F03, F04, F05, F07, F08, F09,
  F10, F11, F12, F13, F14, F15, F16, F18, F19, F20, F22, F25, F26, F28, F29, F30.
* 3 contracts not promisor-related: F17 (errata revision), F21 (nested
  subdirectory), F24 (huge round number).
* 13 controls: C01–C08, **C09** (`promisor=false`, exit 0), **C10** (orphan
  `.promisor` marker, exit 0), C11, C12, C13.
* 2 open rows: O01 (alternates), O02 (gitfile) — reported, not graded.
* C09 and C10 keep their exit-0 expectations; only their *mutant-kill role*
  moves to C17/C18 (§4). C05 (`--shared` clone) also stays exit 0: alternates
  are not promisor state.
* Ordering constraint implied by the change: the shallow / grafts / sha1 /
  top-level refusals (`tools/report-landing-audit.py:445-453`) must still fire
  **before** any new completeness probe, and keep their message text
  byte-identical, or F10, F11, F15, F21, F28 change their pinned reason.
* Under variant B, F27 is also an invariant (42 + 1 unchanged).

### 2.3 Row-class changes (not expectations)

`T01`: `tradeoff` → `control` (graded). `F06`, `F23`, `F27` keep their kind.
No row is reclassified from `open` to graded, and no `open`/`tradeoff` row is
deleted — that is the "hide the red cell" failure mode.

## 3. New rows required (8) — the coverage the policy change would delete

Without these, the r24 candidate could drop the unknown-absence rule or the
"not a promisor store" rules and the retained grid would still go green.
Candidates are in the two patches (both apply cleanly to base 0df800e;
`py_compile` ok; 12 selected rows re-run against the r23 base auditor with no
fixture-premise failure).

| new row | fixture | variant A | variant B | kills / pins |
|---|---|---|---|---|
| C14-marked-clean | complete lane + promisor metadata only | exit 0 | exit 0 | the r24 claim: metadata ≠ missing evidence |
| C15-marked-omission | same + genuine omitted pre-cutoff commit | exit 1 `[landed-omitted]` | same | "same substantive findings as the full clone" |
| C16-marked-missing-citation | same + fabricated 40-hex citation | exit 2 (unknown) | exit 1 `[unresolved-full-hash]` | policy-sensitive: unknown-vs-proved-absence in a marked, closure-complete store |
| C17-unmarked-missing-citation | `remote.origin.promisor=false` + fabricated citation | exit 1 `[unresolved-full-hash]` | same | **M27** (a false boolean reading would make this exit 2 under A) |
| C18-orphan-marker-missing-citation | orphan `.promisor` (no paired `.pack`) + fabricated citation | exit 1 `[unresolved-full-hash]` | same | **M29** (dropping the pairing would make this exit 2 under A) |
| C19-marked-wrongtype-citation | locally present blob cited as a Landed commit | exit 1 `[landed-unresolved]` | same | git answers a wrong-type peel as `missing`; an unknown-rule keyed on git's answer would swallow this |
| C20-marked-cross-repo-citation | token absent from the marked lane, present in the fleet | exit 0 | same | absence is decided **after** all audited repositories are consulted, not per repository |
| C21-incomplete-closure | blobless clone **without** checkout (F23's shape) + fully resolvable citation | exit 2 (unknown) | exit 2 (unknown) | an unavailable required object is a could-not-evaluate even when every citation resolves |

Measured on the r23 base (so each row is discriminating, not vacuous):
C14/C15/C16/C19/C20/C21/T01 → exit 2 (r23 metadata refusal) = NOT-MET;
C17/C18 → exit 1 `[unresolved-full-hash]` = met (true no-harm controls that
must keep passing). Variant A additionally flips F27 to NOT-MET on the r23
base; variant B leaves F27 met.

## 4. Mutant map (r23 `tests/report-audit/isolation-mutants.py`, 31 mutants, 30 killed)

| mutant | r23 killer | r24 status | action |
|---|---|---|---|
| M02-lazy-fetch | F27 | **still killed, stronger** (A: F27 + F06; B: F27) | F27 keeps its `core.sshCommand` marker assertion; under A, F06 also reaches the lookup (the metadata refusal is gone), so `--no-lazy-fetch` finally has two live probes. No literal change. |
| M14-promisor-config | F06 | **retired** | its literal `raise EvalError(f"{repo}: partial clone ({key})")` is deleted by policy → pattern matches 0 times → the harness aborts (`could-not-evaluate`, kills nothing). Retire **visibly** (`RETIRED` map, printed + in the JSON), never silently. |
| M22-promisor-pack | F23 | **retired** | same; the paired-marker *detection* survives, its refusal does not. |
| M27-promisor-boolean | C09 | **re-point** | C09 can no longer kill it (a promisor=false store with a clean report still exits 0 even when misread as promisor). New killer: **C17** (variant A; under B the mutant turns C17 into an exit-2 row that no longer matches → still killed). The literal `'\n                and git_bool(value)):'` is indentation-coupled to the rewritten code → re-choose it against the candidate text. |
| M29-promisor-pack-pairing | C10 | **re-point** | C10 can no longer kill it (orphan marker + clean report still exits 0). New killer: **C18**. |
| M01, M03–M13, M15–M21, M23–M26, M28, M30–M32 (26) | see r23 `mutants.json` | **unchanged invariants** | same literals, same killers. M12/M13/M15/M16 sit inside `check_history_repo` (`tools/report-landing-audit.py:445-453`), the function the r24 work must change: keep those four refusal lines byte-identical, or re-point all four. M20 stays a **survivor** (defensive-only) and stays reported, not credited. |

Harness coupling (a mechanism, not a hypothesis):
`isolation-mutants.py:118-121` returns exit 2 as soon as a pattern does not
match exactly once, and `grid()` treats a grid exit 2 as "kills nothing". A
policy-deleted literal does not merely lose one mutant — it aborts the whole
run. The candidate patch (`mutants-policy.patch`) removes M14/M22, records
them in `RETIRED`, and flags M27/M29 in `NEEDS_REPOINT`, printed and present
in the JSON, so the coverage delta is visible rather than silent.

New elements that must gain mutants (in the r24 promisor mutant harness,
`promisor-mutants.py`): unavailable-required-object → exit 2 (C21/F23),
proved absence in a closure-complete store (C16 under B, C17, C18),
wrong-type-not-unknown (C19), aggregate cross-repo resolution (C20), and
`--no-lazy-fetch` retention on the new rows. A detector error is not a kill;
a grid that cannot evaluate kills nothing.

## 5. Red-cell ledger (nothing hidden)

| cell | r23 state | r24 state | rule |
|---|---|---|---|
| O01-alternates-foreign-object | exit 0, expected 1 — **open, reported not graded** | unchanged (alternates are not promisor state) | stays open; do not reclassify |
| O02-gitfile-redirect | exit 0, expected 1 — **open, reported not graded** | unchanged | stays open; do not reclassify |
| T01-blobless-partial-clone | exit 2, expected 0 — red, **ungraded** | exit 0 expected, **graded** (`control`); still red against the r23 base, green only against the r24 candidate | restored and graded, never deleted; it is the r24 claim's visible red cell |
| M20-log-sha-shape | survivor | survivor | keep reported as defensive-only |
| M14 / M22 | killed by F06 / F23 | retired with reason | visible in `RETIRED`, in the JSON, and in the r24 lesson |
| C09 / C10 | killers of M27 / M29 | no longer killers | their exit-0 expectations stay; the kill moves to C17 / C18 |
| r23 population hash | `f29fab8d…364a` (pinned in `corpus/lessons/round-23.md:113`) | new population hash | record the new value append-only; do not edit the r23 lesson; do not rewrite `.ufo/waves/round-23/final/grid-both.json` / `mutants.json` |
| frozen-arm violations | 29 (r23 grid frozen = `4fe9339f`) | **31** (variant A) / 31 (variant B) — **measured** on the frozen arm: T01 exit 0 clean (met), C14/C15/C17/C18/C19/C20 met, C16 and C21 not met (the r22 base has no completeness check, so it answers C16 with a proved-absence finding and C21 with a clean exit 0). F27, F06 and F23 were already frozen-arm violations (the r22 base has no `--no-lazy-fetch`, so F27's `core.sshCommand` marker ran; F06/F23 exit 1 vs exit 2), so their re-pinning adds no delta | the frozen arm is expected to exit 1; the delta is recorded, not hidden |

## 6. Specified updates (candidate files; no production edit made here)

1. `out/ConnNoHarm/grid-policy-rows.patch` (**variant A**, preregistration
   literal) → `tests/report-audit/repo-state-grid.py`
   * docstring: append the round-24 policy note listing each changed row and
     its round-23 expectation (append-only, base 0df800e);
   * new builders `_marked`, `c_marked_clean`, `c_marked_omission`,
     `c_marked_missing_citation`, `c_unmarked_missing_citation`,
     `c_orphan_marker_missing_citation`, `c_marked_wrongtype_citation`,
     `c_marked_cross_repo_citation`, `c_incomplete_closure`;
   * rows: T01 → `control` exit 0; F27 → exit 2; new C14–C21 (all `control`);
   * `REASONS`: F06/F23 → `unknown`; C16, C21 → `unknown`.
2. `out/ConnNoHarm/grid-policy-rows-closure-variant.patch` (**variant B**,
   closure-grounded): same builders and same new rows, but F06 → exit 1 with
   kinds `[landed-unresolved, unresolved-full-hash]` and **no** reason pin,
   F27 untouched (its round-23 expectation stands), C16 → exit 1
   `[unresolved-full-hash]`, C21 → exit 2 with reason `unknown`.
   **Apply exactly one patch.**
   * The pin string `unknown` presumes the candidate's refusal line contains
     that token (e.g. `could-not-evaluate: <repo>: unknown: …`).
     **Coordination required with AuditRepair**: if the candidate's wording
     differs, the pin must be set to a substring of the candidate's actual
     message *and* the choice recorded in the r24 lesson — a stale pin is a
     silent red cell. A pin on an exit-0 or exit-1 row is always wrong: the
     grid checks the reason substring on every row.
3. `out/ConnNoHarm/mutants-policy.patch` → `tests/report-audit/isolation-mutants.py`
   * delete the M14 and M22 entries; add `RETIRED` (with reasons) and
     `NEEDS_REPOINT` (M27, M29), printed and included in the JSON output.
   * After the candidate lands: re-point M27/M29 to literals that exist in
     the candidate text, and add the new semantic mutants there or in
     `promisor-mutants.py`.
4. New rows are additions only; T01 changes kind, not value. No r23 row is
   deleted, and no `open` row is reclassified.

## 7. Verification (L1 runs once after integration)

```
python3 tests/report-audit/repo-state-grid.py --arm both --json
#   current arm: 52 graded rows (26 fault, 4 contract, 22 control), 0 violations,
#                 0 tracebacks, 0 executed programs, 0 timeouts
#   frozen arm: exit 1 (expected), violation count 31 (29 in r23 + C16 + C21)
python3 tests/report-audit/isolation-mutants.py --json
#   no "could-not-evaluate"; retired and needs-repoint lists present;
#   M20 remains the only survivor unless the r24 candidate adds a row for it
python3 tests/report-audit/promisor-grid.py --arm both --json      # r24 grid
python3 tests/report-audit/promisor-mutants.py --json              # r24 mutants
python3 tools/report-landing-audit.py --selftest                   # 50/50
```
Do not run the suites during the wave; the numbers above are *expected*, not
measured. The only numbers measured in this lane are in
`out/ConnNoHarm/probe-base-behavior.txt`.

## 8. Risks

* **R1 — pending policy (open, owner: CritUnknown).** Variant A vs B changes
  F06's exit, F27's membership in the affected set, and C16's expectation.
  Until that lands, the grid patches are two mutually exclusive candidates;
  applying both is an error.
* **R2 — reason-pin coupling (open, owner: AuditRepair).** The changed
  `REASONS` pins must match the candidate's actual refusal wording, and no
  pin may be attached to a non-exit-2 row.
* **R3 — completeness-probe scope.** The probe must decide completeness from
  the *selected roots'* closure. Measured: in a genuine blobless clone the
  branch-wide probe reports exactly one `?`-prefixed line (the filtered blob)
  and fetches nothing; in a complete marked repo it reports none. A
  branch-wide probe over *all* refs would refuse repositories whose unrelated
  objects are absent — the same class of harm r24 repairs (see
  `OracleMissingNonrequired`).
* **R4 — isolation regression.** The new probe must go through the existing
  `git()` wrapper, so it inherits `--no-lazy-fetch`, `--no-replace-objects`,
  the log/signature suppressions and `GIT_TIMEOUT`; a raw `subprocess` call
  would restore the lazy-fetch channel and the unbounded hang.
* **R5 — harness abort.** Any r23 mutant literal the candidate's rewrite
  moves (M12/M13/M15/M16/M27/M29) aborts `isolation-mutants.py` with exit 2
  and kills nothing. Re-point before the run; do not delete the entries.
* **R6 — historical parity.** The r23 historical-ledger parity
  (`.ufo/waves/round-23/final/nh-history-parity.stdout`) covers rounds 10–22
  and is unaffected by the promisor policy; the r24 candidate must not change
  those bytes (RevHistory owns that check).
