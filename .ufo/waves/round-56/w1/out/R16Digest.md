# R16Digest — frozen counter/checker sha256 recompute vs preregistration

Scope: recompute the sha256 of the frozen C1 counter and C2 checker from the
committed freeze tree and compare with `.ufo/waves/round-56/preregistration.json`.
Advisory only; no predicate, counter, target, kill-rule, or preregistration change.

## Method

All digests computed with `git show <commit>:<path> | sha256sum` inside the lane
repo `/home/vgpnk/Projects/shokunin/kama-shokunin` (git backend; `git cat-file -t`
returns `commit` for both pins). No fixture, no mutation, no scratch file content
was needed for hashing; TMPDIR scratch was created but unused for evidence.

- Freeze: `efc6b3ec6fb6ea308c15855e9b8b62856f4255b7` ("round-56: freeze LD_AUDIT
  env leg and prereg roster controls", 2026-10-27 13:03:18 -0300). This is the
  current HEAD.
- Base: `e10b6d39af450e8d652be9ac2986768b531fe13f` (round-55 verifier spotcheck).
  `git merge-base --is-ancestor` confirms base is the direct parent of freeze.

## Results

| File | Preregistered sha256 | Recomputed @ freeze | Match |
|---|---|---|---|
| `tools/round56-replay-code-audit.py` (C1 counter) | `fc3d4b63a3020cf37e6f4080e25c9d693a8b177c4f84cae6688b2e445444ff6f` | `fc3d4b63a3020cf37e6f4080e25c9d693a8b177c4f84cae6688b2e445444ff6f` | YES |
| `tools/round56-prereg-check.py` (C2 checker) | `c7b0d787f348691bbc057114b455545f5abfb0c70ec497e1ad695591f1489853` | `c7b0d787f348691bbc057114b455545f5abfb0c70ec497e1ad695591f1489853` | YES |
| `tools/round56-env-leg-test.py` (C1 driver; no frozen digest in prereg) | — | `ec7a2519f6d4b2e1bd08a7ead042a53c7b60e2f58af8e4db008dfd661acf82ac` | n/a |

## Corroborating observations

- Working-tree bytes equal freeze-tree bytes for all three tools files and for
  `preregistration.json` itself (`fa4b5a100a9fd6ceaec93c537f3d9264a0883fac873368243ff1ae041d82ee68`
  both ways) — no post-freeze drift on the measured surfaces.
- All three tools files and the preregistration are ABSENT at base `e10b6d39`
  (`git cat-file -e` fails for each), consistent with the C2 base-control
  expectation `present=0, met=False`.
- `git diff --stat base..freeze` touches only round-56 artifacts: the three
  tools files, `tools/round56-env-leg-battery.py`, preregistration, two control
  receipts, two source HTMLs, and `corpus/SOURCES.md` — a clean freeze footprint
  with no edits to pre-existing files.
- Informational: `git status` shows unrelated modified/untracked files under
  `.ufo/waves/round-55/` out directories only; nothing under `tools/` or
  `.ufo/waves/round-56/` is dirty.

## Verdict (advisory)

No defect. Both frozen digests recompute exactly from the committed freeze tree;
the kill-rule clause "measured counter sha256 differs from the frozen digest"
cannot fire for either C1 or C2 on this tree.
