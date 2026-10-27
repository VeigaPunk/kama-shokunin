# Proposed errata for round 55 (seat Sc2Scoring) — for the L1 to adopt or edit

Append-only per lane method: the proposed text below is for a new `## Errata` section at the
end of `corpus/lessons/round-55.md`. Nothing here edits `preregistration.json` (frozen), the
committed receipts, or any lane file.

## 1. Full text to append to `corpus/lessons/round-55.md`

```markdown
## Errata

- **§Mistakes, first row, last sentence (the kill-battery fix).** The sentence reads "each
  battery mutant receipt names the leg it kills" (lines 75–76 at `9c60eae6`). That is true of
  three receipts and false of a fourth: `m-ldaudit-writable.out:2` prints `met=True` and
  names no failing leg. The battery directory also holds `m-extra-in-tree.out` (a
  round-53-vector note that `met=True`, `:2`), which is not a mutant. Correct reading:
  the runner's kill-class receipts are `m-ldpreload` (`envnames=0/3`), `m-text-flip`
  (`bind=0/3 code=0/3`) and `m-member-flip` (`rehash=3`), each `met=False`, and its
  positive control is `met=True`; `m-ldaudit-foreign` is scored as a `"vector"` expected
  to pass (`run-battery.py:57-60,137`), and `m-ldaudit-writable` is not built by the
  runner at all (`run-battery.py:26,38,57,69`). The earlier bytes stay as written.
- **§Claims, C1 kill rule, as frozen.** `preregistration.json:44` names
  `m-ldaudit-writable (code leg)` and `m-ldaudit-foreign (hostlibs leg)` as mutants, and
  `:19` requires each named mutant receipt to print `met=False`; `:20` falsifies the claim
  if any battery mutant prints `met=True`. Both receipts print `met=True`
  (`c1/battery/m-ldaudit-writable.out:2`, `c1/battery/m-ldaudit-foreign.out:2`), so the
  frozen rule fires and C1 is not admitted on it. Disposition referred to the canonical
  judge (report `.ufo/waves/round-55/w1/out/Sc2Scoring.md`, defect D1).
- **§Gate, authority paragraph, the wrap-up pointer.** The preregistration cites the
  round-54 outside closure as "MANIFEST rounds[812]"
  (`preregistration.json:8`); in `MANIFEST.json` the kama round-54 entry is index 814
  (index 812 is kumitate round 67). The closure file and lane commit cited there are
  correct. Next freeze uses 814.
```

## 2. Candidate correction for the *next* freeze's kill battery (not a frozen-artifact edit)

Option A (preferred — declare the vector instead of calling it a mutant): list exactly the
set the runner builds, and give each entry its expected outcome, e.g.

```text
"mutants": ["m-ldpreload (envnames leg, expect met=False)",
            "m-text-flip (bind/code legs, expect met=False)",
            "m-member-flip (rehash leg, expect met=False)",
            "m-ldaudit-foreign (hostlibs vector, expect met=True: LD_AUDIT void on this glibc)",
            "m-extra-in-tree (vector note, expect met=True)"]
```

Option B (preferred if a `code`-leg kill is required): replace the root-gated
`m-ldaudit-writable` entry with a same-uid mutant that lands on the `code` leg — the landed
`m-text-flip` already does exactly that (`bind=0/3 code=0/3 met=False`), so the freeze
should either name it or state that the code leg is killed through it. A root-owned writable
library outside the frozen host set cannot be produced as a non-root mutant, which is why
`m-ldaudit-writable.out` reads `met=True`.

## 3. What must not change

`preregistration.json`, `controls/base.c*.out`, `measured/c*.out`, `c1/battery/*.out` and the
two counters are frozen for this round. The `m-ldaudit-writable.out` receipt stays in place
as superseded evidence (§1 above names it); deleting it would erase the conflict the errata
records.
