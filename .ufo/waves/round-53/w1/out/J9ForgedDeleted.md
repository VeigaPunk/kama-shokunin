# J9ForgedDeleted — round 53 C2 ablation: forged deletion (calibration)

VERDICT: both forged-deletion arrangements are rejected by the frozen C2 counter — a `deleted` row whose
evidence commit is the base (which deleted no path at all) and a `never` row reclassed `deleted` at the build
(which also deleted no path) each give `fixture=1 lane=0 bad=1 undisclosed=1 met=False`, exit 1, while the
unmutated build at the same fleet revision still gives `met=True`, exit 0. Control passes; no defect in
`tools/round53-cited-path-check.py`.

## Mutations (fixture clone; each committed there with identity `fx <fx@invalid>`)

Clone: `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane` ($S =
`/fast/scratch/hyaku/kama-r53/J9ForgedDeleted`); `git -C $S/lane rev-parse --show-toplevel` printed `$S/lane`
before the first commit. Three branches, each one commit whose parent is the build `c22602bd` (diffs in
`ctlA.diff`, `ctlB.diff`, `ctlC.diff`):

| control | commit | change to `registry/cited-path-corrections.tsv` (build line) |
|---|---|---|
| A (assigned) | `4ea9683669dcf84659b3d5746228a4773028876b` | line 16 `deleted` evidence `9874e455…` → `4229ea1b9a789148dded1f159c20967d9a01373f` (the base) |
| B (assigned) | `2404119056b7f8bdd97e247a27a64286c7573f29` | line 17 `.ufo/waves/round-999/count-c999.py` `never  -` → `deleted  c22602bd8d83ab26349d1087e916ca537ee4f9d1` (the build) |
| C (supplementary, same mechanism) | `f0114116fdc3e9b4d13080e8a50a447e777c1472` | line 16 `deleted` evidence `9874e455…` → `19c07aa9b3c25e0def4c3b09f3dbb1765f3ae84d` (a commit that deleted two round-49 seat files) |

Why each forge is a forge, observed in the clone (transcript `facts.txt`):
`git show --diff-filter=D --name-only 4229ea1b` → empty (the base deletes nothing);
`git show --diff-filter=D --name-only c22602bd` → empty (the build deletes nothing);
`git ls-tree -r 4229ea1b^ / 4229ea1b -- …/round-31/sources/llama.cpp-704366d/utils.hpp` → absent in both,
while `9874e455^` has it (so only `9874e455` can carry a true `deleted` row);
`git log --all --name-only | grep -c round-999` → `0` (the token was never a path, so `never` was the only
class that could re-derive);
`git show --diff-filter=D --name-only 19c07aa9` → two round-49 paths, not `utils.hpp` (so C separates "the
commit deletes something" from "the commit deletes this token").

## Runs (frozen counter; sha256 `1afb8b9d32fd0706d0625a4ea70270890039f93fc32635c28b12fa71b13e3080` = the
preregistration `counter_sha256`, so the frozen instrument was the one run)

Command form: `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round53-cited-path-check.py --repo
$S/lane --tip <commit> --scratch $S --out <receipt>` (B and C additionally re-run with `--fleet-rev
d2a6c59aaabcbde2d4a946c31d0276bb2c3d7887` to pin the fleet revision; receipts `pinned-*.out`).

| run | tip | cited | unresolved | disclosed | undisclosed | bad | stale | dropped | fixture | lane | met | exit |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| reference (unmutated build) | `c22602bd` | 682 | 14 | 14 | 0 | 0 | 0 | 0 | 1 (8/8) | 1 | True | 0 |
| A: deleted row → base | `4ea96836` | 682 | 14 | 13 | 1 | 1 | 0 | 0 | 1 (8/8) | 0 | False | 1 |
| B: never → deleted at build | `24041190` | 682 | 14 | 13 | 1 | 1 | 0 | 0 | 1 (8/8) | 0 | False | 1 |
| C: deleted → commit deleting other paths | `f0114116` | 682 | 14 | 13 | 1 | 1 | 0 | 0 | 1 (8/8) | 0 | False | 1 |

Exact reason lines (from `ctlA-…out`, `ctlB-…out`, `ctlC-…out`):

```
detail: bad ledger line 16 (SCORECARD.md `.ufo/waves/round-31/sources/llama.cpp-704366d/utils.hpp` deleted): no repo has commit 4229ea1b9a78 deleting ['.ufo/waves/round-31/sources/llama.cpp-704366d/utils.hpp']
detail: undisclosed SCORECARD.md `.ufo/waves/round-31/sources/llama.cpp-704366d/utils.hpp`: [('.ufo/waves/round-31/sources/llama.cpp-704366d/utils.hpp', 'missing')]
```
```
detail: bad ledger line 17 (SCORECARD.md `.ufo/waves/round-999/count-c999.py` deleted): no repo has commit c22602bd8d83 deleting ['.ufo/waves/round-999/count-c999.py']
detail: undisclosed SCORECARD.md `.ufo/waves/round-999/count-c999.py`: [('.ufo/waves/round-999/count-c999.py', 'missing')]
```
```
detail: bad ledger line 16 (…utils.hpp deleted): no repo has commit 19c07aa9b3c2 deleting ['.ufo/waves/round-31/sources/llama.cpp-704366d/utils.hpp']
```

Calibration reads: the fixture leg stayed `8/8` in every run (the constructed scenarios, including its own
"forged deleted row is bad" and "forged never row is bad" cases, keep their verdicts), so the lane leg — not
the fixture — is what flips on the mutation; `undisclosed=1` accompanies `bad=1` by design (a row that fails
its class check does not disclose); the reference run reproduces the L1 build receipt's counts exactly
(`cited=682 unresolved=14 disclosed=14`) with a different fleet revision (`d2a6c59` vs the build's
`ee9f7341`), so the forgery, not fleet drift, drives `met=False`.

Counter lines exercised: `tools/round53-cited-path-check.py:59-66` (bad/stale definition and the two forged-row
fixture expectations), `:234` `check_row`, `:253-264` the `deleted` leg (requires the token present at `ev^`
and absent at `ev` in a repo that has the commit), `:265-268` the `never` leg (rejects a token that was ever a
path), `:439`/`:443` the fixture cases. All commits these rows cite are single-parent, so `ev^` is exact here;
the lane has 2 merge commits elsewhere but no ledger evidence names one.

## Observation (non-blocking; verdict correct, message imprecise)

`tools/round53-cited-path-check.py:264` returns the same sentence whether the evidence commit does not exist
or exists but did not delete the token. Control A is the second case (the base exists, it just deleted
nothing), yet the receipt says "no repo has commit 4229ea1b9a78 deleting […]", which a reader can take as
"commit not found" — visible with
`python3 tools/round53-cited-path-check.py --repo $S/lane --tip 4ea96836… --scratch $S`. Proposed wording
(no logic change):

```diff
-        return f"no repo has commit {ev[:12]} deleting {[e for e, _v in bad_exp]}"
+        return (f"commit {ev[:12]} does not delete {[e for e, _v in bad_exp]} "
+                f"(absent at {ev[:12]}^, or still present at {ev[:12]}, in every repo that has the commit)")
```

## Limits / notes

- The fleet repository was being written during the wave (HEAD observed `d2a6c59a`, then `71256a5d`, then
  `33540c6e`). Every receipt names the fleet revision it read (`d2a6c59a` in all four original runs), and
  A/B/C plus the reference were re-run with `--fleet-rev d2a6c59a…` (`pinned-*.out`); the counts are
  identical, so the receipts are reproducible.
- Only C2 ran here. No C1 path, no counter edited in place, no llama-server started by this seat (the two live
  `llama-server` processes belong to peer `K2Design`), scratch removed after the receipts were copied out.

## Files

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/J9ForgedDeleted.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/J9ForgedDeleted/{ctlA-forged-deleted-commit.out,ctlB-forged-never-as-deleted.out,ctlC-forged-deleted-other-deletions.out,ref-build-current-fleet.out,pinned-A.out,pinned-B.out,pinned-ref.out,ctlA.diff,ctlB.diff,ctlC.diff,facts.txt,commands.txt}`
