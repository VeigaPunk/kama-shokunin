# MutationEvidenceV5 — round 24 C1 mutation contract, inventory version 5

**Proposal only; no production file is edited by this seat.** Version 4
(and versions 2 and 3) stay filed, the lane's integrated runner
(`6e0b9d62db9fe27f6c14c6e16ce239023f699142193adff5291e4374a1bb60a2`) and
the integrated legacy harness
(`bb32ec2146484b74ace787d4d223c4895c68fedf734464485358630bf3c10a2d`) stay
unchanged, and every filed receipt is untouched.

| file | sha256 | bytes | note |
|---|---|---|---|
| `promisor-mutants.py` | `00b89b5061e77a297cb23f15d3ef34237623c5592f67261fbec4807d7cedca4b` | 54485 | inventory version 5 |
| `promisor-mutants-v5.patch` | `7d3d1643e86bcb0a897c6e57d76d16c1b8fb686a97b2dd7a7dea488881d67173` | 33659 | unified diff against the integrated `6e0b9d62…`; `git apply --check` clean at p1 |
| `isolation-mutants.py` | `eace4f56e225f33e96676c0fb6c58d657256c9e37cf06130d487155d343e2a00` | 9691 | the legacy harness with the empty-selection guard (unchanged from V4) |
| `isolation-mutants.patch` | `e29abf65637f987c6b0fb70a0513468382e144fa3d5c8755eab6a62c094bb0f4` | 899 | unified diff against the lane's `2e` file (unchanged from V4) |
| `inventory-v5.json` | — | — | 11 = 10 executable + 1 review-only; the PM07 decision; the v4→v5 delta |
| `selftest-receipt.txt` | — | — | `selftest cases=15 failed=0`, exit 0 |

Scratch: `/fast/scratch/hyaku/kama-r24/MutationEvidenceV5` at base
`2e254a1763a9c08aa07fc53081287f506c447d84`.

---

## 1. PM07 is restored to the canonical recipe; only the prose changes

The version-4 retarget of PM07 (broadening the name-hiding walk from the
pinned root to every present root) is **declined and reverted**: it was
not the operator's `--all` mutation, and retargeting a mutant to force a
detect is not a legitimate move. Version 5 therefore restores the **exact
version-3 alternatives and expect_rows**:

* alternatives: `--all` is appended to the **store-wide missing roots**
  (`roots = present_roots(repo)` → `roots.append("--all")`), with the two
  historical fall-backs;
* expect_rows: `PG31, PG32, PG35, PG36, PG44, PG45, PG48` — unchanged
  from version 3.

Only the **prose** is corrected, to say what the recipe actually does:

* the recipe adds `--all` to the **store-wide missing roots** and does
  **not** broaden the name-hiding (opaque) walk, which stays rooted at
  the pinned root only;
* survival on the finite 47 is an **observation of this candidate**, not
  a global-equivalence proof;
* the canonical mutant can also differ on a **broken unselected REF
  target that is not among the present roots**, so **no universal no-op
  is claimed**;
* **supplemental post-fix experiments**, specially named and **separate
  from the 47 and from this canonical operator**, may test unselected-ref
  opacity.

No kill is presumed for PM07; the final run decides.

## 2. What is carried over unchanged from version 4

* **PM08** keeps the manual review-only wording: the candidate's
  **repository-reading wrappers** carry `--no-lazy-fetch`, so a missing
  promisor object is not fetched through the promisor remote **on the
  paths those wrappers read**; it is a manual reading of the isolation
  flags, **not a proof about every git call**. Unchanged in shape:
  review-only, no alternatives, no source or wiring assertion, 0
  executions, `killed: false`, uncredited, skipped by `--anchors` (ten
  executable mutants checked). Counts: **11 = 10 executable + 1 manual
  note**.
* **The legacy empty-selection guard** and its file/patch (899 bytes):
  an empty selection is could-not-evaluate (exit 2), decided before the
  source read, the pristine and any grid call; the 27 operators and the
  retirement history are preserved; no unrelated argument is validated
  and no expectation changes.
* **Every other operator**, its alternatives and its attribution.

## 3. Documentation correction

The exit-map paragraph still said "surviving, or **static-only**" — the
vocabulary of the removed static gate. It now reads "**review-only**",
matching the only remaining entry kind. The PM07 docstring entry was
rewritten to the canonical recipe as described in §1.

## 4. Static anchor check (no sweep)

The anchors are checked statically against the latest core source
`fixes/StoreLocalPresence/report-landing-audit-v9.py`
(sha256 `b9be4f428cd70842320c698794faffaa95571a60fc530df6a84d7d8cade3b26f`):
**ten executable mutants, one applicable alternative each, every mutant
compiles, and the review-only entry is skipped** (`--anchors` exit 0).
The bounded `--selftest` passes 15/15.

**Not run**: no sensitivity sweep and no legacy fixture run (wave 2 is
active). The 47 grid rows, the operator's instructions and the filed
receipts are untouched.
