# MutationEvidenceV3 — round 24 C1 mutation contract, inventory version 3

**Proposal only; no production file is edited by this seat.** The lane's
integrated runner (`6e0b9d62db9fe27f6c14c6e16ce239023f699142193adff5291e4374a1bb60a2`)
and every filed receipt stay **unchanged**. The version-2 AST proposal in
`fixes/MutationEvidence/` is **kept filed as a snapshot** and is superseded
here: its AST tuple-membership gate is **not shipped**.

| file | sha256 | note |
|---|---|---|
| `promisor-mutants.py` | `a34b834c1916b827dd9e0371b9ad33ce306341635bfc64a591559cc29703e99c` | inventory version 3 |
| `promisor-mutants-v3.patch` | `f1862d3496cc91b8c12542c91d2bd914e80b7f97b7d50844d195273233bfb32a` | 573-line unified diff against the integrated `6e0b9d62…`; `git apply --check` clean at p1 |
| `inventory-v3.json` | — | 11 entries = 10 executable + 1 review-only note, with the attribution deltas v1→v3 and v2→v3 |
| `selftest-receipt.txt` | — | `selftest cases=15 failed=0`, exit 0 |
| `rationale-v3.md` | — | this file |

Scratch clone: `/fast/scratch/hyaku/kama-r24/MutationEvidenceV3` at base
`2e254a1763a9c08aa07fc53081287f506c447d84`.

---

## 1. PM08 is a historical review-only note (operator instruction)

The operator's instruction supersedes the version-2 AST proposal. In
version 3:

* the inventory entry is **`PM08-no-lazy-fetch-review-only`**, with
  `execution: "review-only"` and **no alternatives at all**;
* the `static_check` field, the literal replacements, the AST helper
  (`isolation_flag`), the `ast` import and the tautological guard-wiring
  test are **removed** — the runner makes **no source assertion** for this
  entry, literal or AST, and asserts **no static transition**;
* the runner **never applies** the entry, **never builds** a mutant for it
  and **never invokes the grid** for it;
* the entry is reported with `killed: false`, `executions: 0`,
  `review_only: 1`, no failed rows, and the reason "review-only note: not
  applied, not executed, not credited";
* `--anchors` **skips** the review-only entry (`skipped: "review-only"`,
  no source assertion) and checks the **10 executable mutants only**;
* the inventory count is stated explicitly: **11 = 10 executable + 1
  manual review note**;
* the claim about `--no-lazy-fetch` stays a **manual reading** of the
  candidate's isolation flags, recorded in the review trail and credited
  to nobody.

This is the operator's requested test shape, honoured exactly: PM08 is not
a behavioural kill and no implementation/wiring assertion is shipped for it.

## 2. What stays from version 2

* **PM11 is an unconditional any-hole gate.** The earlier mutant patched
  `RepoStore.missing`, which the auditor consults only while a citation is
  unresolved, so the resolved-unused-hole controls (PG35, PG36, PG44,
  PG45, PG48) stayed clean: the old implementation did not do what its
  name claimed. The mutant now wraps `build_store`, so the store is built
  and **any** hole refuses the audit. Only the new, measured version may
  be claimed.
* **The attribution is version 2's independent semantic map** (delta in
  `inventory-v3.json`): PM01 +PG15/+PG19/+PG46 −PG07/−PG08 (only *marked*
  cells are affected by a metadata refusal); PM02 +PG46 (the opaque
  absence is misclassified as unknown; the errata cell is worse, because
  the refusal precedes the ledger and the ordinary finding never becomes a
  clean verdict after the correction); PM03 +PG46; PM06 +PG15/+PG19/+PG28;
  PM10 −PG33/−PG34 (those are the *named* missing blob, governed by the
  other rule); PM11 +PG13–PG21/+PG28/+PG31/+PG32/+PG43/+PG46 −PG25 (no
  hole). The 47 grid expectations are unchanged.
* **The selftest asserts behaviour, not just exit codes** (15 cases, 0
  failed): `unmet` and `twin` must credit at least one kill **and** name
  the violated cell; `rc1_no_violated_row` drives the intended branch
  (the grid exits 1 with a *met* row, so the reason is "grid exit 1
  without an identifiable violated row"); `exit2`, `leak` and
  `timeout_row` each assert their own could-not-evaluate reason; a
  **canary** log written by the stub grid proves that a pristine failure
  stops the run before any mutant phase (exactly one invocation, the
  pristine one); a mutant that does not compile is could-not-evaluate;
  `--anchors` returns 2 on a broken candidate and 0 on a sound one.
* **New in version 3 — the selftest proves the review-only shape** rather
  than a guard wiring: exactly one review-only entry, `killed: false`,
  `executions: 0`, `review_only: 1`, no failed rows; the document reports
  `review_only: 1` and `executable = mutants - 1`; **no grid invocation**
  carries the review-only id in the canary; and the review-only id never
  appears in `killed_ids`.
* **Provenance**: the filed preliminary receipt's producer (the runner
  that still had `--baseline`) is not recoverable — the `build/out/` copy
  was overwritten by the contract repair and the lane integrated the
  repaired version, so no commit holds the pre-repair file. The receipt
  stays filed unmodified and is annotated by the honest sidecar in
  `fixes/MutationEvidence/preliminary-receipt-provenance.md`; it is an
  unreproducible preliminary and carries **no credit**.

## 3. What is not claimed and not run

* No sensitivity sweep was run (wave 2 is active). The only executions
  here are the bounded `--selftest` (15 stub cases) and the static
  `--anchors` check (exit 0 against the integrated auditor `ea51bc35…`;
  1 review-only entry skipped, 10 executable mutants applicable and
  compiling).
* PM07's survival remains an honest observation of a redundant mutant on
  the current candidate, with **no** finite-equivalence claim.
* PM08 is never executed and never credited.
* The 47 grid expectations and the grid itself are untouched.

## 4. For the main agent's full re-run (after the barrier)

```
python3 tests/report-audit/promisor-mutants.py \
        --current tools/report-landing-audit.py \
        --grid tests/report-audit/promisor-grid.py --json
```

Expected shape: the document reports `mutants: 11`, `executable: 10`,
`review_only: 1`, the killed and the surviving executable mutants, and
exit 0 for a fully evaluated inventory (2 for any could-not-evaluate).

Apply with:

```
git apply .ufo/waves/round-24/fixes/MutationEvidenceV3/promisor-mutants-v3.patch
```
