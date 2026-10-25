# Round 37 / W1 — Append-only discipline review

Seat: L1Kama37.ExpectedMouse. Scope: the two frozen r36 blobs against
`LESSON_BLOB` / `REPORT_BLOB` in `tools/round37-statement-audit.py`. No edits made.

## Verdict

Both instructed comparisons **match**.

| Check | Command | Observed | Constant | Match |
|---|---|---|---|---|
| r36 lesson | `git -C <lane> rev-parse master:corpus/lessons/round-36.md` | `6fb1ec151407b1207e8d540e83ba87d6a909d8ea` | `6fb1ec151407b1207e8d540e83ba87d6a909d8ea` | yes |
| r36 fleet report | `git -C <fleet> rev-parse HEAD:.ufo/reports/round-36/kama.md` | `8b7408e663c1b1ea95826d240f498637f1961604` | `8b7408e663c1b1ea95826d240f498637f1961604` | yes |

Evidence beyond the literal command:

- Lane worktree `corpus/lessons/round-36.md` hashes to `6fb1ec15…` (`git hash-object`),
  identical to `master:`. `master` is `6a4afdfe` (= `BASE`), so the blob is unchanged
  since base by construction.
- Fleet `HEAD` is `df892d2b`; the report path is clean in the worktree and hashes to
  `8b7408e6…`. Its last-modifying commit `29698108` ("round-36: kama report erratum")
  carries `8b7408e6…`; the pre-erratum `428a0560` carried `47d13335…`. The constant pins
  the post-erratum blob, and `29698108` is an ancestor of fleet `HEAD`.
- Counter at the current jj working-copy commit `7e4b6071`:
  `uncorrected 4 false_corrections 0 lesson_unchanged 1 report_unchanged 1 met False`
  (`round-37.md` does not exist yet; met False is the correct pre-mutation control value).

## High severity — tip choice flips `lesson_unchanged`

The lane is checked out **detached at `873c5d77`** (`* (no branch)`), the last commit of
a four-step sandbox selftest series (`mut1`…`mut4`, all "sandbox only"). That commit's
r36 lesson blob is **`0418795f…`, not `6fb1ec15…`** — it corrupts one hex digit in the
`R35-WORDS` row. The clean bytes survive only in the worktree, which explains
`git status` showing ` M corpus/lessons/round-36.md`, and jj showing `@` = `7e4b6071`
whose parent `@-` = `873c5d77`.

Sensitivity, measured with the frozen counting command:

```
python3 tools/round37-statement-audit.py --repo . --tip 6a4afdfe…  -> lesson_unchanged 1
python3 tools/round37-statement-audit.py --repo . --tip 873c5d77…  -> lesson_unchanged 0
python3 tools/round37-statement-audit.py --repo . --tip 7e4b6071…  -> lesson_unchanged 1
```

Consequence: the round-37 tip MUST be a commit whose tree has the jj working-copy bytes
(`7e4b6071` or a descendant, i.e. `tip:corpus/lessons/round-36.md` = `6fb1ec15…`).
Using `873c5d77` or any commit built on it without the worktree modification makes
`met False` unfixable by any correction row. This is the same parked-working-copy hazard
that hit the lane last round; the append-only invariant is currently intact on disk and
would be broken by a tip taken from the detached HEAD.

## Residual risk

- `report_unchanged` resolves against fleet **`HEAD`** at run time (hardcoded `"HEAD"` in
  `load_facts`), not a pinned revision. A later fleet commit that rewrites
  `.ufo/reports/round-36/kama.md` flips the axis with no lane-side signal. Healthy today
  (clean worktree, blob matches at `HEAD` and at `29698108`).
- `master` is `6a4afdfe`, identical to `BASE`; the lesson check therefore proves
  "unchanged since base" only through `master`. It does not constrain the detached HEAD,
  which is why the tip-selection finding above is load-bearing.

## Verification gaps

- `lsp` was not used: these are Git object-graph facts, not symbol references; the
  authoritative instruments are `git rev-parse` / `git hash-object` / the frozen counter,
  all executed.
- The sandbox mut series was not inspected for whether it is intended to remain reachable
  from a ref; only its effect on the frozen blob was measured. No mutation performed, so
  the receipts above are reproducible.

## Installs

None.
