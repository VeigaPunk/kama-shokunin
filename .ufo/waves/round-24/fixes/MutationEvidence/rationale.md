# MutationEvidence — round 24 C1 mutation contract repair (inventory version 2)

**Status: proposal only. No production file is edited by this seat.** The
files here are the corrected candidate for `tests/report-audit/promisor-mutants.py`
plus its patch against the version the lane already integrated. The lane's
integrated version (`6e0b9d62db9fe27f6c14c6e16ce239023f699142193adff5291e4374a1bb60a2`,
integrated in `ed1cc3a`, lane HEAD base `2e254a1763a9c08aa07fc53081287f506c447d84`)
and every filed receipt stay **unchanged**; nothing here is credited
retroactively.

| file | sha256 | note |
|---|---|---|
| `promisor-mutants.py` | `cbd43c855d991cd8505ba41a26f2c833183177738422e1f79f3d0d1baa54e5ab` | the corrected runner (inventory version 2) |
| `promisor-mutants-v2.patch` | `137d8d940c7928cc00db7115866300178c0a01ef372f3da2b70f85fa7ce79d8d` | 492-line unified diff, `a/`/`b/` paths, against the integrated `6e0b9d62…` |
| `inventory-v2.json` | — | the version-2 inventory with the per-cell attribution and the old→new delta |
| `selftest-receipt.txt` | — | `selftest cases=13 failed=0`, exit 0 |
| `preliminary-receipt-provenance.md` | — | honest provenance for the filed preliminary receipt |

Scratch clone: `/fast/scratch/hyaku/kama-r24/MutationEvidence` at base
`2e254a1`.

---

## 1. What the fresh falsifiers found, and what changes

### 1.1 PM08's static gate answered from a substring (MutStaticNoFetch)

The integrated runner asked `marker in source` for the static-only mutant.
The auditor's prose names `--no-lazy-fetch`, so the flag was "present" both
before and after the mutation: the gate reported `before=True, after=True`
and could not distinguish a removed flag from an intact one.

**Fix.** The gate now reads the candidate's `GIT_ISOLATION` tuple literal
through the AST (`isolation_flag()`), and requires

* the flag is a member of the tuple literal **before**,
* the flag is **absent** from the tuple literal **after** the mutation,
* the mutant **compiles**,

otherwise the mutant is `could-not-evaluate` (never credited, never
executed). Measured on the integrated auditor `ea51bc35…`:

```
isolation_flag before: True
isolation_flag after : False
substring before/after: True True      <- the old, useless check
mutant compiles: True
```

The mutant stays **static only**: it is never executed against the grid,
because a fixture that could reach a transport is forbidden in this wave.

### 1.2 PM11's gate was lazy (MutOverRefusal)

The integrated runner's PM11 patched `RepoStore.missing`, which the auditor
consults **only while a citation is unresolved**. A hole the audit never
needs therefore never reached the patched method: the resolved-unused-hole
controls (PG35, PG36, PG44, PG45, PG48) stayed clean, and the mutant did
not implement the property it advertised.

**Fix.** PM11 now wraps `build_store`: the store is built and any hole
(missing or opaque) refuses the audit **unconditionally**. The claim is
now the implemented behaviour, not a name. The old PM11 was a wrong
implementation; only the new, measured version may be claimed.

### 1.3 The built-in selftest asserted too little (GateMutationSelftest)

The integrated selftest asserted exit codes only. It now asserts the
**behaviour** behind them:

| stub mode | asserted now |
|---|---|
| `ok` | exit 0; the canary log shows the pristine invocation **and** at least one mutant invocation (the mutant phase really ran) |
| `unmet` | exit 0; **at least one kill** is credited **and** the killed mutant names the unmet cell (`PG01-unmet-cell`) |
| `twin` | exit 0; at least one kill and the failed twin cell (`PG02-twin-cell`) is named |
| `exit2` | exit 2, no kill, and the reason `grid exit 2` is present |
| `rc1_no_violated_row` | exit 2, no kill, and the reason `without an identifiable violated row` is present — the grid now reports a **met** row with exit 1, so the runner's intended branch is exercised instead of the "no rows" path |
| `leak` | exit 2, no kill, reason names `harness_leaks` |
| `timeout_row` | exit 2, no kill, reason names `timed out` |
| `pristine_fails` | exit 2, no kill, and the **canary holds exactly one invocation, the pristine one** — proof that no mutant phase ran after a pristine failure |
| broken candidate | exit 2 and a `could_not_evaluate` entry |
| `--anchors` on a broken / sound candidate | exit 2 / exit 0 |

The canary is a log file the stub grid appends to on every invocation
(`GRID_STUB_LOG`), with the line marked `pristine` or `mutant`.

Result: `selftest cases=13 failed=0`, exit 0 (`selftest-receipt.txt`).

### 1.4 Attribution was incomplete (MutOverRefusal, MutOpaque)

The version-1 attribution lists were written from the earlier kill map and
missed cells whose expectation the mutation also changes. Version 2 comes
from an **independent semantic map** of what each mutation must change, and
the old→new delta is recorded in `inventory-v2.json`:

| mutant | added cells | removed cells | why |
|---|---|---|---|
| PM01 blanket metadata refusal | PG15, PG19, PG46 | PG07, PG08 | the refusal affects **every** promisor-marked cell, including the marked missing-tree cells (PG15, PG19) and the marked opaque cell (PG46); the plain complete cells (PG07, PG08) are not marked, so the metadata refusal does not touch them |
| PM02 blanket unknown refusal | PG46 | — | in the opaque cell the absence of an unresolved token behind a missing tree is misclassified as unknown; the errata cell is worse than a wrong finding: the refusal happens **before** the ledger, so the ordinary finding never becomes a clean verdict after the correction |
| PM03 skip required-object availability | PG46 | — | the cited blob hidden behind a missing tree is unavailable required evidence |
| PM06 swallow actual read error | PG15, PG19, PG28 | — | the failed reads of the missing tree, of the fleet tree and of the unhydrated lane are required reads whose failure must stay could-not-evaluate |
| PM10 ignore opaque non-leaf missing | — | PG33, PG34 | PG33/PG34 are governed by the *named* missing blob (the `unknown_citation` rule), not by the opaque rule; only PG46/PG47 depend on the opaque rule |
| PM11 any-hole refusal | PG13–PG21, PG28, PG31, PG32, PG43, PG46 | PG25 | the unconditional gate refuses every cell whose repository holds a hole, whatever that cell's verdict is; PG25 (a fabricated citation in a complete repository) has no hole |

The 47 grid expectations are **unchanged**; nothing in this proposal edits
the manifest or the grid.

### 1.5 Provenance of the filed preliminary receipt

The filed receipt
`build/out/MutationOracle/sensitivity-promisor-grid.json`
(sha256 `a29cc01dc91e84da38d3aef6c05ae1db041d717f302d953c9dbf4e9034981f82`)
was produced by the **pre-repair** runner, the one that still had the
`--baseline` mode. That producer's exact bytes are **not retained**: the
`build/out/` copy was overwritten by the contract repair, and the lane
integrated the repaired version, so no commit holds the pre-repair file.
The receipt therefore cannot be reproduced byte-exactly and carries **no
credit** for the shipped contract. It is kept filed, unmodified, with an
honest sidecar (`preliminary-receipt-provenance.md`). Nothing was rewritten
or re-credited.

---

## 2. What this proposal does not do

* It does not edit any production file; the lane's `tests/report-audit/promisor-mutants.py`
  and every filed receipt stay as they are.
* It does not re-run the sensitivity pass (no full sweep while wave 2 is
  active). The only execution here is the bounded `--selftest` (13 stub
  cases) and the static `--anchors` check.
* It does not claim that PM07 is equivalent to anything: PM07's survival on
  the current candidate is reported honestly as an observationally
  redundant mutant (the candidate's traversal already starts from every
  present object, so rooting it at `--all` changes nothing), with **no**
  finite-equivalence claim.
* It does not execute PM08, and it does not claim a kill for it.

## 3. For the main agent's full re-run (after the barrier)

```
python3 tests/report-audit/promisor-mutants.py \
        --current tools/report-landing-audit.py \
        --grid tests/report-audit/promisor-grid.py --json
```

Expected shape with the version-2 runner: exit 0 when the inventory is
fully evaluated (killed and surviving mutants in the JSON), exit 2 for any
could-not-evaluate; PM08 reported as `static-only-not-executed` with
`static_before=True, static_after=False`; PM11 killed by the
resolved-unused-hole cells as well (PG35, PG36, PG44, PG45, PG48) if the
unconditional gate is implemented as proposed.

Apply with:

```
git apply .ufo/waves/round-24/fixes/MutationEvidence/promisor-mutants-v2.patch
```
