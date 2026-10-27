# M07BaseMutation — round-56 C2 mutation probe: preregistered base hash

Verdict: **SURVIVED** — the frozen C2 counter fails open when the preregistered
base hash in `preregistration.json` is re-pointed; it does not fail closed.
This is a coverage finding against C2's implied "the counter binds the
preregistration it validates"; it is not a change to the frozen contract.

## Mutant (one field, smallest plausible defect)

- File: `.ufo/waves/round-56/preregistration.json`, top-level `base` field only
  (`controls.base_do_nothing.tip` left at the true base).
- `- "base": "e10b6d39af450e8d652be9ac2986768b531fe13f"` (red do-nothing base)
- `+ "base": "efc6b3ec6fb6ea308c15855e9b8b62856f4255b7"` (the green freeze tip)
- Committed as `6b3ed6594f52dc5c5e82c7bd8c4dcb1ce924d185` in the seat scratch
  clone only; mutated blob sha256
  `b057ccbe69522db05ea15002eb20fdcfde66ff3fd2794f1871e19065628e7e35`.
  Full diff: `w1/out/M07BaseMutation/mutant-diff.patch`.

## Expected detector (frozen counter under test)

`tools/round56-prereg-check.py` sha256
`c7b0d787f348691bbc057114b455545f5abfb0c70ec497e1ad695591f1489853` (verified on
the lane file before and after). Claimed behavior under test: a changed
preregistered base hash must make the checker fail closed. The checker only
compares `battery.roster` from the committed preregistration against the
`ROSTER` AST literal in the committed battery; the `base` field is never read.

## Outputs (exact commands, stdout, exit)

All runs: `python3 <lane>/tools/round56-prereg-check.py --repo <scratch-clone> --tip <tip> --out <receipt>`.

1. Pristine base control `--tip e10b6d39…` →
   `present=0 roster_match=0 kills=0 controls=0 met=False`, **exit 1**
   (`pristine-base.out`) — red baseline reproduced.
2. Pristine freeze `--tip efc6b3ec…` →
   `present=1 roster_match=1 kills=1 controls=2 met=True`, **exit 0**
   (`pristine-freeze.out`) — detector validated on pristine bytes.
3. Mutant `--tip 6b3ed659…` →
   `present=1 roster_match=1 kills=1 controls=2 met=True`, **exit 0**
   (`mutant.out`) — checker stays fully green under the tampered base hash.
4. Restored `--tip efc6b3ec…` → identical bytes to run 2 (same sha256
   `01d95f52…`), **exit 0** (`restored-freeze.out`).

## Consequence

With `base` re-pointed at the freeze tip, an operator dereferencing
`prereg.base` as the do-nothing control would run the base control at
`efc6b3ec…` — which is green (run 2) instead of red (run 1). Per the frozen
kill rule "C2 is falsified if the base control is green", the tampered
preregistration flips the base control green, yet the counter reports
`met=True` exit 0. Fail-open.

## Restoration evidence

- Scratch clone hard-reset to `efc6b3ec…`; working file sha256 restored to
  `fa4b5a100a9fd6ceaec93c537f3d9264a0883fac873368243ff1ae041d82ee68`
  (== pre-mutation blob == lane working copy); `git status --porcelain` = 0
  entries.
- Lane files verified unchanged after all runs:
  checker `c7b0d787f348691bbc057114b455545f5abfb0c70ec497e1ad695591f1489853`,
  preregistration `fa4b5a100a9fd6ceaec93c537f3d9264a0883fac873368243ff1ae041d82ee68`.
  No git/jj command was run in the lane; the mutant commit exists only in the
  scratch clone (removed after receipts were copied).
- Note: a first restore attempt via `git checkout -- <file>` was a no-op
  (restored from the mutant HEAD, sha `b057ccbe…`); it was redone with
  `git reset --hard efc6b3ec…` before the restored run was accepted.

## Defects and proposed fixes (advisory; frozen artifacts untouched)

1. `round56-prereg-check.py` never reads the committed preregistration's
   `base` (or any identity field) — the counter validates the roster slice
   only, so preregistration tampering outside `battery.roster` is invisible.
   Proposed fix: assert the committed preregistration's `base` equals the
   checker's `BASE` constant (and/or that `controls.base_do_nothing.tip`
   equals `base`), returning `met=False`/exit 1 on mismatch.
2. Related dead code: module constant `BASE` is defined but never referenced
   in `main()` — the hook for fix 1 already exists.
3. Counter embeds a second copy of the base hash (`BASE`) that can drift from
   the preregistered value with no check binding them.

## Tooling

No tools installed or upgraded; `python3` and `git` from the host sufficed.
No pacman use. Scratch `/fast/scratch/hyaku/kama-r56/M07BaseMutation/` removed
after receipts were copied. Receipts: `w1/out/M07BaseMutation/` (SHA256SUMS.txt).
