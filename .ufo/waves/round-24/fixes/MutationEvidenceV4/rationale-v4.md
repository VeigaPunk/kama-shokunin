# MutationEvidenceV4 — round 24 C1 mutation contract, inventory version 4

**Proposal only; no production file is edited by this seat.** The lane's
integrated runner (`6e0b9d62db9fe27f6c14c6e16ce239023f699142193adff5291e4374a1bb60a2`),
the integrated legacy harness (`bb32ec2146484b74ace787d4d223c4895c68fedf734464485358630bf3c10a2d`),
every filed receipt and the version-2/3 proposals stay **unchanged**.

| file | sha256 | bytes | note |
|---|---|---|---|
| `promisor-mutants.py` | `57a186a4a40901bb64561ad44dd7528783c9181f6c0fb22bd2e93e5868862a96` | 54331 | inventory version 4 |
| `promisor-mutants-v4.patch` | `8ad6d905fb35fb1f05500cf9689e98c87f9c45634510df7cdf2805d7efac6cba` | 33775 | unified diff against the integrated `6e0b9d62…`; `git apply --check` clean at p1 |
| `isolation-mutants.py` | `eace4f56e225f33e96676c0fb6c58d657256c9e37cf06130d487155d343e2a00` | 9691 | the proposed legacy harness (empty-selection CNE) |
| `isolation-mutants.patch` | `e29abf65637f987c6b0fb70a0513468382e144fa3d5c8755eab6a62c094bb0f4` | 899 | unified diff against the lane's `2e` file |
| `inventory-v4.json` | — | — | 11 = 10 executable + 1 review-only; deltas v3→v4; the core-source freeze |
| `selftest-receipt.txt` | — | — | `selftest cases=15 failed=0`, exit 0 |
| `legacy-empty-selection-proof.txt` | — | — | the bounded before/after proof (0 grid calls after) |

Scratch: `/fast/scratch/hyaku/kama-r24/MutationEvidenceV4` at base
`2e254a1763a9c08aa07fc53081287f506c447d84`.

---

## 1. The core source changed: PM07 is no longer "globally redundant"

The final core fix is
`.ufo/waves/round-24/fixes/StoreLocalPresence/report-landing-audit-v7.py`
(sha256 `c19568547d50b6d752d1d3caf20fbcc935305ab2964c9569d03eda5b5b400d37`):

* `missingAll` — every missing object of the store, walked from **all**
  present roots;
* `opaqueRelevant` — the missing trees and commits that *hide names*,
  walked from the **pinned root only**.

The version-3 prose called PM07 "full `--all` missing gate … globally
redundant", because the candidate's traversal already started from every
present object. With the v7 core that is **no longer true**: the
name-hiding walk is rooted at the pinned root only, so rooting it at every
present root is a real change.

**PM07 is therefore re-anchored and re-worded** (`PM07-full-all-opaque-gate`):

* the mutation roots the **opaque (name-hiding) walk** at every present
  root of the store instead of the pinned root — a hole behind an
  unselected ref then becomes relevant to the audit;
* the store-wide missing set already starts from every present root, so
  that part of the mutation changes nothing;
* **no kill is presumed**: on the primary 47 the mutant may still
  survive. The discriminator is an **unselected REF tree hole together
  with a fabricated citation**, which lies **outside the finite 47** (a
  wave-3 supplement). The attribution names the closest in-grid surface
  (PG31, PG32 — the unselected-branch cells) and says plainly that the 47
  may not distinguish the mutant;
* the anchors are re-frozen against the v7 source: all ten executable
  mutants have exactly one applicable alternative and every mutant
  compiles (`--anchors` exit 0 against `c1956854…`).

The 47 grid rows and the operator's instructions are unchanged.

## 2. PM08 stays a manual review-only note

Unchanged in shape: review-only, **no alternatives**, no source or wiring
assertion of any kind, `0` executions, `killed: false`, uncredited, and
skipped by `--anchors` (which checks the **10 executable mutants only**).
The inventory count is stated: **11 = 10 executable + 1 manual note**.

The wording is corrected: the scope is the candidate's **repository-reading
wrappers** — they carry `--no-lazy-fetch`, so a missing promisor object is
not fetched through the promisor remote **on the paths those wrappers
read** — and the note says explicitly that it is a manual reading of the
candidate's isolation flags, **not a proof about every git call**.

## 3. The legacy harness calibration hazard (DocSkillF3)

With the round-24 scoped retirement of M14/M22/M27/M29, the legacy
mutant ids are full names (`M01-replace-objects`, …). A selector that
names only the numeric part selects nothing:

```
$ python3 tests/report-audit/isolation-mutants.py --only M01      # integrated file
mutants=0 killed=0 surviving=[] retired=['M14-promisor-config', 'M22-promisor-pack', 'M27-promisor-boolean', 'M29-promisor-pack-pairing']
exit=0        grid invocations: 1
```

The run executed the pristine grid and **exited 0 with an empty
inventory** — a silent pass that reads like a calibration success. The
proposed fix makes an empty selection **could-not-evaluate (exit 2)**,
decided **before** the source is read, before the pristine run and before
any grid call:

```
$ python3 tests/report-audit/isolation-mutants.py --only M01      # proposed file
could-not-evaluate: --only selected no mutant: ['M01']; the ids are M01-replace-objects, M02-lazy-fetch, ...
exit=2        grid invocations: 0
```

The 27 operators and the retirement history are preserved; no other
argument is validated and no expectation changes; the existing CLI error
format (`could-not-evaluate: …` on stderr, exit 2) is reused. The proof is
bounded: a canary grid that records its invocations, **no legacy fixture
run**.

## 4. What is not claimed and not run

* No sensitivity sweep was run (wave 2 is active). The only executions
  here are the bounded `--selftest` (15 stub cases) and the static
  `--anchors` check against the v7 core source.
* PM07's fate on the primary 47 is **not** predicted: no kill is
  presumed, and the discriminating fixture is outside the 47.
* PM08 is never executed and never credited; its note is a manual reading
  with the scope stated in §2.
* The grid, its 47 expectations and the operator's instruction are
  untouched; the filed receipts and the v2/v3 proposals are kept as they
  are.

## 5. For the main agent (after the barrier)

```
git apply .ufo/waves/round-24/fixes/MutationEvidenceV4/promisor-mutants-v4.patch
git apply .ufo/waves/round-24/fixes/MutationEvidenceV4/isolation-mutants.patch
python3 tests/report-audit/promisor-mutants.py --selftest
python3 tests/report-audit/promisor-mutants.py \
        --current tools/report-landing-audit.py \
        --grid tests/report-audit/promisor-grid.py --json
```

The last command is the full sweep and belongs to the main agent. The
document it produces reports `mutants: 11`, `executable: 10`,
`review_only: 1`, the killed and the surviving executable mutants, and
exits 0 for a fully evaluated inventory (2 for any could-not-evaluate).
