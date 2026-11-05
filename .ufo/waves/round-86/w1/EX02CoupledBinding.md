# EX02CoupledBinding — C1 gate-coupling attack (kama r86 w1)

Seat: attack C1's gate coupling (`tools/round86-rendered-cells.py`, frozen at the freeze commit).
No claim admission — author-side advisory only; the L1 owns integration and is the sole committer.

## Measured revision and byte identity

- Instrument under test: the **committed** bytes at the freeze commit
  `c07e1f909414aafb2d8de5605a81fd3bd4e3550e`, extracted with
  `git -C /home/vgpnk/Projects/shokunin/kama-shokunin show c07e1f90…:tools/round86-rendered-cells.py`.
  sha256 of the extracted bytes equals sha256 of the worktree file (`00-identity.receipt`,
  `identical=True`), so worktree and freeze-commit instrument are the same program.
- Real tree graded at base `3ff23da3f291ce8abf7bf5c54f9abacec67e3e8d` and at the freeze commit.
  HEAD is `67eddac89f44e768b670301ea0feff06e766f32d` (already past the freeze; worktree carries a
  pre-existing `M LOG.md`). Irrelevant to the measurement: the instrument reads committed bytes
  only (`git ls-tree` / `git show` / `git merge-base --is-ancestor`).
- `git merge-base --is-ancestor 3ff23da… c07e1f90…` → rc=0 (base is an ancestor of the freeze).

## Real tree at the freeze commit

`python3 frozen_c1.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --rev <rev>` (rc=1 at both
revs, `02-real-base.receipt` / `03-real-freeze.receipt`):

```
RENDERED_CELLS facts=3 mismatches=3 gate=0 closure=0 disposition=0 newest_gate=85 newest_closure=85
RENDERED_CELLS_FINDING gate declared round=84 newest terminal receipt round=85 (.ufo/waves/round-85/measured/after/gate.out)
RENDERED_CELLS_FINDING closure row names round-84 newest committed closure is round-85 (corpus/lessons/round-85-verifier-spotcheck.md)
RENDERED_CELLS_FINDING disposition row does not name `round85 rejected-honest-stop`
```

This reproduces the frozen before-receipt `.ufo/waves/round-86/measured/before/c1.out` exactly —
a do-nothing tree cannot reach `mismatches=0`. `--selftest` on the frozen bytes: 11/11 arms PASS,
rc=0 (`01-selftest.receipt`) — no control stopped discriminating, including the round-85
`fenced-shadow` false-green arm, which is red here.

## Attack verdicts — all six false-satisfaction attempts fail closed

Scratch git fixture `/fast/scratch/hyaku/kama-r86/EX02CoupledBinding/fixture` (toplevel asserted
`equal=True` before the first commit; graph in `10-fixture-build.receipt`): master
`A(c1c6bff)→B(7a3b696)→C(87554b3)`; side branches `stalecarry(ce82124)`, `vanish(0e47ef9)`,
`side(dd5d246)`, `ghost(c72d3df)`. Module-level arms run against the instrument's own
`DictTree` via `python3 /fast/scratch/hyaku/kama-r86/EX02CoupledBinding/attack.py <arm>`
(`30-attack-index.receipt`).

| # | Attack arm | Exact command (fixture rev / attack arm) | rc | Verdict |
|---|---|---|---|---|
| 1 | token from one receipt while naming another | `frozen_c1.py --repo <fixture> --rev master` + `attack.py wrong-receipt-named` | 1 (both) | RED — `gate no revision among 1 is an ancestor carrying a declared receipt with the exact token`; token is bound to the *named* receipt, not to any tree receipt |
| 2 | receipt only at a non-ancestor branch tip | `frozen_c1.py --repo <fixture> --rev ghost` + `attack.py tip-nonancestor` | 1 (both) | RED — `declared round=86 newest terminal receipt round=85` **and** uncoupled; real `merge-base --is-ancestor` rejects the side tip `dd5d246` |
| 3 | token digits differ from receipt bytes | `frozen_c1.py --repo <fixture> --rev stalecarry` + `attack.py digits-differ` | 1 (both) | RED — exact-token match required; `arms=14 failed=2` in the paragraph vs `arms=13 failed=1` in the receipt never couples |
| 4 | command naming another round | `attack.py cmd-other-round` | 1 | RED — `command round does not name the token round 85` |
| 5 | two revisions, only the stale one carries the receipt | `frozen_c1.py --repo <fixture> --rev vanish` | 1 | RED, fails closed — `declared round=85 newest terminal receipt round=84` + uncoupled; pointing backwards at a stale rev whose receipt was since deleted cannot satisfy the fact |
| 6 | token inside a fenced block / comment | `attack.py token-in-fence`, `attack.py token-in-comment` | 1 (both) | RED — `no coupled PRE_REPORT token in the rendered authority cell`; the rendered selector strips the shadow, the live cell without the token cannot satisfy |

Every arm MATCHed its pre-registered expectation; no fixture achieved a false green.

## Genuinely coupled or merely co-located?

**Within the graded tree: genuinely coupled.** The token must appear verbatim (backticks stripped)
inside the named receipt's committed bytes; the token's round must equal the newest terminal
receipt's round; the backticked command's `--round` must equal the token's round; and some named
40-hex revision must be a real ancestor (`merge-base --is-ancestor`). All four bindings are
exercised and hold under attack.

**Across history: merely co-located — one predicate clause is unenforced.** The frozen predicate
says "the receipt's bytes **at that revision** containing that exact token". The implementation
reads `tree.blob(path)` — receipt bytes at the **graded** revision — and requires only that some
named revision be an ancestor; it never reads bytes at R:

- `frozen_c1.py --repo <fixture> --rev master` → rc=0, `mismatches=0` (`11-fx-master.receipt`),
  although at the named revision `c1c6bff` the receipt carried
  `PRE_REPORT round=85 arms=9 failed=9 uncommitted=1`, not the token. The fact green-lights a
  paragraph whose "measured at R" claim is false at R.
- Cross-product tolerance: the coupling loop accepts ANY named ancestor revision × ANY named
  receipt carrying the token — `attack.py decoy-tip-named` and `attack.py decoy-receipt-named`
  both rc=0 (green) with a decoy non-ancestor revision / decoy receipt co-named in the same
  paragraph.

Severity: low. A false green still requires the exact token in the named receipt's graded-tree
bytes plus a genuinely ancestral named revision, so history cannot be invented — but the
"at that revision" byte-state clause is not what the code checks. If the L1 wants the predicate
sentence enforced literally, the fix is to read the receipt at R (`git show R:path`) instead of at
the graded rev, which would also turn the `fx-master` probe red. Advisory only; all six seat arms
already fail closed, so this does not block C1.

## Deliverables

Receipts in `.ufo/waves/round-86/w1/out/EX02CoupledBinding/`: `00-identity.receipt`,
`00-env-head.receipt`, `00-env-status.receipt`, `01-selftest.receipt`, `02-real-base.receipt`,
`03-real-freeze.receipt`, `10-fixture-build.receipt`, `11-fx-master.receipt`,
`12-fx-stalecarry.receipt`, `13-fx-vanish.receipt`, `14-fx-ghost.receipt`,
`20-attack-<arm>.receipt` ×9, `30-attack-index.receipt`, plus this note as
`findings-note.md`. Driver sources (`drive.py`, `attack.py`, `build_fixture.py`) were scratch-only
and are removed with the scratch dir; every command and rc is preserved in the receipts.

## Boundaries

Only the seat out dir and `/fast/scratch/hyaku/kama-r86/EX02CoupledBinding/` were written; the
fixture repo is `git init`'d (no clone), all git ops explicit `git -C` with env-provided identity,
toplevel asserted before the first commit. No production file touched, no commit, no mutating git
command, no `.ufo/state` / watchdog / MANIFEST access, no config or credential reads, no live
endpoints, no tool installs needed (tooling authorization unused). Scratch removed after receipts.
