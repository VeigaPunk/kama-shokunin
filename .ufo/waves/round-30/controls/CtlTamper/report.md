# CtlTamper — round-30 C1 pre-freeze control (calibration)

Seat: kama-r30-ctl-CtlTamper (item label `CtlTamper`). Mutation-tester role.
Lane read-only; all work in `/fast/scratch/hyaku/kama-r30/ctl/CtlTamper/`.

## Policy (assigned)

Rewrite history so the two false base lines look true: `git replace` the base commit
and SCORECARD blobs, with the replacement objects in an alternate object store, plus a
custom `GIT_REPLACE_REF_BASE` namespace. Then run the LANE counter (it passes
`--no-replace-objects` and sets `GIT_NO_REPLACE_OBJECTS=1`). Expected: identical 13
mismatches / met False.

## Mutation implemented

Clone: `git clone <lane> /fast/scratch/.../CtlTamper/repo`, checkout lane tip
`52ac3af8614b5040ba5e17f17a2c7af029706e6c`. Alternates file:
`.git/objects/info/alternates -> /fast/scratch/hyaku/kama-r30/ctl/CtlTamper/altobjects`.

Replacement objects (all blobs/trees/commits stored in the alternate store) and refs:

| replaced object | replacement | effect in ordinary git |
|---|---|---|
| `2aa46e24…` (base commit) | `ee4a23f7…` (commit, same parent/ident, tree 52916afc) | base tree carries edited SCORECARD.md |
| `24882de8…` (base SCORECARD blob) | `3cfe0fc7…` (blob) | line 41 `file=yes` → `file=missing` |
| `ea72c3ea…` (W of the line-41 oracle item) | `1e0d8c24…` (commit, tree b34a23f2) | adds `evidence/ctltamper-history-rewrite.txt` = "the pins verify file=yes at the relocated tree" |
| `92b14625…` (W of the line-901 oracle item) | `b444b31b…` (commit, tree b3155af0) | adds `evidence/ctltamper-history-rewrite.txt` = "declared2048 = captured training2048" |
| `21a41a7c…` (tip SCORECARD blob) | `ffd5a336…` (blob) | same line-41 edit, keeps the append-only prefix true in the tampered view |

Each pair is installed twice: `refs/replace/<oid>` (default vector) and
`refs/tamper/<oid>` (vector for `GIT_REPLACE_REF_BASE=refs/tamper/`).

Candidate commit: `4b5b85191aa069bc4fd66d1a9278806a2462cd3a` — empty commit on top of the
lane tip, local identity `CtlTamper seat <ctltamper@localhost>`.
Diff `52ac3af..4b5b8519`: **empty**; tree `45c05ee28cb573d0996d069bfc742ac269f72f22`
identical at both commits. The policy lives in `.git` replacement refs + alternate store,
not in a tree change.

### Tamper effectiveness (ordinary git, ordinary env)

- base SCORECARD blob: original `sha256 7af59cc0…`; tampered view `sha256 7ae236c6…`;
  `--no-replace-objects` view `7af59cc0…` (unchanged).
- tip SCORECARD blob: original `sha256 b155ca88…`; tampered view `sha256 9bc4cf54…`;
  shielded view `b155ca88…`.
- `git grep -F file=yes ea72c3ea -- . :(exclude)SCORECARD.md …` → hit in
  `evidence/ctltamper-history-rewrite.txt`; shielded → rc 1.
- `git grep -F 'declared2048 = captured training2048' 92b14625 …` → hit; shielded → rc 1.
- `git cat-file blob 52ac3af:SCORECARD.md` startswith `git cat-file blob 2aa46e24:SCORECARD.md`
  in the tampered view → append-only relation still true.
- env-only clone (`refs/replace` absent, refs/tamper only, alternate store registered):
  no env → base blob `7af59cc0…`, grep miss; `GIT_REPLACE_REF_BASE=refs/tamper/` →
  base blob `7ae236c6…`, both greps hit. The env vector is genuine.

## Counter runs

Lane counter bytes: `sha256 c3f16ef195a6b5de24afa5a798647d917070d988954baf1fe5923fc5e19ce40d`
(unchanged; the receipt's `counter_sha256` records the same).

1. Baseline (pristine clone, untampered tip `52ac3af`):
   `statements 141 extracted 69 oracle 72 bound 72 unbound 0 mismatched_at_base 13 append_only True valid_corrections 11 false_corrections 0 unresolved 2 met False tip 52ac3af8614b`
   exit 0. (`/fast/scratch/.../CtlTamper/baseline-tip.json`)

2. Lane counter, assignment command verbatim, tampered clone, tip `4b5b8519…`:
   `/usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-30/count-c1.py --repo /fast/scratch/hyaku/kama-r30/ctl/CtlTamper/repo --tip 4b5b85191aa069bc4fd66d1a9278806a2462cd3a --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-30/controls/CtlTamper/counter.json`
   `statements 141 extracted 69 oracle 72 bound 72 unbound 0 mismatched_at_base 13 append_only True valid_corrections 11 false_corrections 0 unresolved 2 met False tip 4b5b85191aa0`
   **exit 0**.

3. Lane counter, hostile env (`GIT_REPLACE_REF_BASE=refs/tamper/`,
   `GIT_ALTERNATE_OBJECT_DIRECTORIES=<alt>`, `GIT_OBJECT_DIRECTORY=<alt>`,
   `GIT_NO_REPLACE_OBJECTS=0`), tampered clone, tip `4b5b8519…`:
   same summary line, **exit 0**. `counter-env.json` is byte-identical to `counter.json`
   (`sha256 c6089e48…`).

4. Unshielded instrument copy (same counter with `--no-replace-objects` and the env
   filter removed; copy sha256 `e76c390c…`, diff limited to the `git()` wrapper) on the
   **same tampered repo**:
   `statements 141 extracted 69 oracle 72 bound 72 unbound 0 mismatched_at_base 11 append_only True valid_corrections 11 false_corrections 0 unresolved 0 met False tip 4b5b85191aa0`
   → the tamper is live; the shield is what hides it.

5. Unshielded copy on the pristine clone (copy control): exactly the baseline line
   (`13 … unresolved 2 met False`), so the copy differs only in the shield.

Field-by-field comparison, baseline tip vs tampered tip: only `tip` differs. Same
`unresolved_ids` (`SCORECARD.md:Q:422b431349:o0`, `SCORECARD.md:Q:4a6f7c911e:o0`).

`met` from the receipt: **False**.

## Verdict

**Survived** (no coverage change; the mutation had no effect under the lane counter).
No blocking finding: the tamper changed nothing in the lane counter's output, bare or
under hostile env; all three vectors (in-repo `refs/replace`, `GIT_REPLACE_REF_BASE`
custom namespace, alternate object store registration) are neutralised by
`git --no-replace-objects` plus `GIT_NO_REPLACE_OBJECTS=1` and the env filter.

Genuine shortcut? No. Even with the shield removed the arm reports
`mismatched_at_base 11, unresolved 0, met False`: making the two false base lines true
moves the population off the frozen `== 13` constant, so the arm cannot reach the claim
on either reading; the shield only changes how far the corruption would propagate.

Restoration: no source bytes were modified — the clone's tree equals the lane tip's
(`45c05ee2…`), the baseline clone holds pristine bytes, the lane counter hash is
unchanged, and the lane repo has no `refs/replace`/`refs/tamper` (count 0).

Tool installs: none.
