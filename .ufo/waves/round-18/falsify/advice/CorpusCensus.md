VERDICT: confirm — the round's SOURCES delta is append-only clean on both consecutive source-changing pairs (exit 0/0), the tip registry is census-valid (55 rows, exit 0, the same two W04s as the round-start receipt), and the "+8 rows" statement reproduces exactly; a disclosed whitespace-only escape and an unrecorded KQ22 sweep are reported below, neither overturning the claim.

# CorpusCensus — scoped falsification advice

Advice to L1, not admission. Attacked: the round-18 SOURCES registry delta and the
append-only guard at pushed lane master, not the C1/C2 runtime numbers. Target
`1c325b2e58fcfdc6761f645b44cedfb1d65243e6`, round start
`e75cf680b53484a61709ee1b2787d8dbc6419f74`, measured C1/C2 revision
`c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d`. All counting ran in
`/tmp/kama-r18-falsify-CorpusCensus` (tip clone, base clone under `base/`, synthetic
repos under `synth2/` and `pending/`), never against the live lane.

Axes named: **calibration** (do the stated counts and the guard's own sensitivity
match observation), **operability** (validator, census and guard execute on the
committed tree), **evidence integrity** (pinned inputs, read-only inspection,
clone-only counting, scratch removed).

## Input identity

| Blob | SHA-256 |
|---|---|
| `corpus/SOURCES.md` @ `e75cf68` (also byte-equal to `5e9ae6e:corpus/SOURCES.md`; `git diff --stat 5e9ae6e e75cf68 -- corpus/SOURCES.md` empty) | `d821f66b89714522168c2c46efbb311f1e9f37f3aba61d4076a068f708276d6a` |
| `corpus/SOURCES.md` @ `c6dc46fa` | `af7be7e71c95489dcc930f7903bc4b95f59ddadd7b166a2d00e9b8652d05d37e` |
| `corpus/SOURCES.md` @ `1c325b2e` (tip; equals cloned working tree, `git status --porcelain` only untracked scratch) | `8b2907bd2667c49df199f546a494e4f985d14bc7e12527bf721ef4cc1a79cdb1` |
| `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh` | `3fb7261569f46423dd80ecc23e0a23789a7926f667c7a3fc559d2439d4a64e30` (unchanged from the round-17 receipt) |

Validator selftest `sources-census.sh selftest` → last line `selftest ok`, exit 0.
Round history in the clone is linear: `git rev-list --count e75cf68..1c325b2e` = 2,
`git log --merges` empty, `c6dc46fa^` = `e75cf68`, `1c325b2e^` = `c6dc46fa`. Exactly two
commits touch `corpus/SOURCES.md` in the round, so the complete consecutive pair set is
(`e75cf68`=`5e9ae6e`→`c6dc46fa`) and (`c6dc46fa`→`1c325b2e`).

## Reference census, committed clone trees

Commands (cwd = the respective checkout, `PYTHONDONTWRITEBYTECODE=1`):
`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh census --root <checkout> --today 2026-10-20 <checkout>`
and the same with `validate`; a second tip census run was byte-identical (`cmp` clean).

| metric | base `e75cf68` | mid `c6dc46fa` | tip `1c325b2e` |
|---|---:|---:|---:|
| rows / FLEET.rows | 47 | 54 | 55 |
| tier.A | 44 | 51 | 52 |
| tier.B | 0 | 0 | 0 |
| tier.C | 3 | 3 | 3 |
| status.mined | 37 | 43 | 44 |
| status.queued | 5 | 5 | 5 |
| status.rejected | 5 | 6 | 6 |
| missing / invalid | 0 / 0 | 0 / 0 | 0 / 0 |
| census exit | 0 | 0 | 0 |
| validate exit | 0 | 0 | 0 |
| E-codes | none | none | none |
| W-codes | W04 S031, W04 S043 | same | same |

Manual awk/grep over tip reproduces rows 55, malformed 0, `A=52 C=3`,
`mined=44 queued=5 rejected=6`; ids are `S001–S055` with 55 distinct values and no
duplicates. The base checkout's two W04 lines are byte-identical to
`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/sources-before-validate.txt`
(modulo the lane label and the capture's trailing `exit=0`), so the round introduced no
new warning.

Delta base→tip: **+8 rows, +8 tier A, +7 mined, +1 rejected**. This matches
`corpus/lessons/round-18.md:35` ("Newly written rows S048–S054 are all tier A … (S053
rejected as a basis)"), `corpus/SOURCES.md:186-187` at tip ("included 6 mined rows
S048–S052/S054, excluded 1 as a basis (S053 retained rejected …)"), and
`corpus/SOURCES.md:198-199` ("this round adds 8 rows total: 7 external candidates above
and 1 own-work set. No previously committed row was regenerated in place."). Lesson
`:178` dates S055 after the receipts. The six externals are mined, S053 is the one
rejected, S055 is mined own-work: 6 + 1 mined + 1 rejected = 8.

## Append-only over every consecutive source-changing pair

Entry point `tools/sources-append-only.py` @ tip sha256
`4d7868564226b6caa5957e9d7f4f8910a1c459ec26462a52d42e802be6079c2d` (same at
`c6dc46fa`; `git diff --stat c6dc46fa 1c325b2e -- tools/sources-append-only.py` empty).

```sh
env PYTHONDONTWRITEBYTECODE=1 python3 tools/sources-append-only.py --selftest
# → 42/42 selftest cases passed, exit 0
env PYTHONDONTWRITEBYTECODE=1 python3 tools/sources-append-only.py \
  --repo /tmp/kama-r18-falsify-CorpusCensus \
  --from 5e9ae6e --to c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d
# → added S048…S054 (allowed); no append-only violations; exit 0
env PYTHONDONTWRITEBYTECODE=1 python3 tools/sources-append-only.py \
  --repo /tmp/kama-r18-falsify-CorpusCensus \
  --from c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d --to 1c325b2e58fcfdc6761f645b44cedfb1d65243e6
# → added S055 (allowed); no append-only violations; exit 0
```

The round-start-base spelling `--from e75cf68 … --to c6dc46fa` prints the same added
list and exits 0 (the two base blobs are identical, row above).

Independent cell-level diff of the three committed blobs (parser comparing all 11 named
columns, `id` excluded), not relying on the guard:

- `e75cf68→c6dc46fa`: rows 47→54; added `S048 S049 S050 S051 S052 S053 S054`, removed
  none; changed rows: **`S047` only, `used-by` only** — old
  `corpus/lessons/round-17.md`, new `corpus/lessons/round-17.md,
  corpus/knowledge/llamacpp-loading-lifecycle.md, corpus/lessons/round-18.md`. All seven
  added rows are `tier=A`, `opened=2026-10-20`; S048–S052/S054 `status=mined`, S053
  `status=rejected`.
- `c6dc46fa→1c325b2e`: rows 54→55; added `S055` only; **zero changed cells and zero
  deletions** (`git diff --stat` = `6 insertions(+)`, and the raw diff contains no `-`
  line besides the file header). So no row added in the first commit was edited in the
  second, and "No previously committed row was regenerated in place" holds byte-exactly.

Fail-capability of the same tip guard in the same clone (the guard is not vacuous):
`--from b8e485c --to ccc4bb3` → `VIOLATION S041: cell \`anchor\` changed in place`,
`VIOLATION S041: cell \`teaches\` changed in place`, `1 append-only violation(s)`,
exit 1. The frozen round-start guard (`frozen/tools_sources-append-only.py`) also exits
0 on both round pairs, so these pairs do not exercise the newly repaired holes; that is
expected and not offered as repair evidence.

## "Added-then-edited must not hide" — witness and scoping

Synthetic repo in `/tmp/kama-r18-falsify-CorpusCensus/synth2` (three commits: `C0` has
S001; `C1` adds S002; `C2` edits S002 `teaches`):

```sh
# base-to-tip only
python3 tools/sources-append-only.py --repo …/synth2 --from C0 --to C2
# → added S002 (allowed); no append-only violations; exit 0   ← the add-then-edit is invisible
# consecutive pair
python3 tools/sources-append-only.py --repo …/synth2 --from C1 --to C2
# → VIOLATION S002: cell `teaches` changed in place; old teaches-b / new teaches-b-edited; exit 1
```

So the KQ22 per-pair method is necessary and does catch a row added in one commit and
edited in a later one; the base-to-tip comparison is exactly the blind method the
contract rejects. In the actual round there is no such row (pair 2 has no deletions or
cell changes), and S048–S054 were added only at `c6dc46fa`.

Residual (disclosed, low): a whitespace-only change to an immutable cell of an added
row still hides, because `split_cells` strips cell edges
(`tools/sources-append-only.py`, docstring: cells "compared verbatim after
leading/trailing whitespace strip"). Witness in the same synthetic repo: `C2→C4` changes
S001 `teaches-a` to `teaches-a ` (one trailing space, `cat -A` differs) and the guard
prints `no append-only violations`, exit 0. This conflicts with KQ22's literal
"byte-identical" wording, but it is documented in the tool and already disclosed at
`.ufo/waves/round-18/build/advice/C2AppendOnly.md:66`; the round's claim does not assert
byte-level padding identity. No non-whitespace hide was found: id changes surface as
removed/duplicate, cell renames/reorders are compared by name, escapes are compared
verbatim.

## Findings for L1 (neither is a claim kill)

1. **Medium — KQ22 round-end sweep has no retained round-18 artifact.** The official
   `runs/run.py` command list has exactly one append-only entry (`:29`,
   `('append-only-selftest', … , [])`); `runs/commands.json` (measured commit
   `c6dc46fa`, 32 commands) contains no `--from/--to` invocation and no census run. The
   lesson's "Official measurement pass" does not record one either. `SKILL.md:612`
   itself states the requirement ("KQ22 still requires every consecutive
   source-changing commit pair, not base-to-tip only") and
   `.ufo/waves/round-18/build/advice/C2AppendOnly.md:70` calls it "still the round-end
   obligation". The two clone runs above (exit 0/0) are the missing receipt; L1 should
   retain them at round end, otherwise the KQ22 obligation is unowned evidence-wise.
   This is an evidence/process gap, not a false claim: nothing in the lesson claims the
   sweep was run.
2. **Info — live working tree differs from the target.** Lane `git HEAD` is the target
   commit, but `corpus/SOURCES.md` on disk is sha256 `729c2a2e…` (58413 bytes, mtime
   2026-10-20 20:20:11 -03) versus the committed `8b2907bd…`. The live file is the
   falsify-wave integration: it adds `S056` (supersedes S054, same pinned arg.cpp) and
   appends its supplement, and changes only the mutable `used-by` cells of S049/S050;
   no row removed, no order change, no immutable-cell change. Preflight in a scratch
   repo (`pending/`, tip blob → live snapshot) passes: `added S056 (allowed); no
   append-only violations`, exit 0. Not part of the attacked commit; if committed, the
   next pair must still be run, and the lesson's "+8" becomes the live supplement's
   "+9".

## Limits

- I did not re-open any external source, URL or network page; only committed registry
  bytes, counts and the guard were exercised. Row-content/tier correctness and
  "written only after opening" are outside this item.
- Census `E11` resolves `used-by` relative to the checkout root, so I ran it on full
  checkouts (no `--file` relocation, which emits phantom E11 per the round-16 note).
- The guard compares trimmed cell values, not raw bytes (see residue above); it also
  ignores row order. KQ22's "byte-identical" should be read as trimmed-cell identity
  unless the owner changes the comparison.
- Two source-changing commits, linear history, no merges: the pair set is complete for
  the pushed master. No dangling/branch commits were considered.
- No final census receipt exists under round 18 (`find … -iname '*census*'` empty); the
  "end" numbers here are mine at `1c325b2e`.

## Installs, listeners, cleanup

No package install or upgrade; no pacman/uv/npm/cargo transaction. No server, port or
network connection was started; `ss -ltnp` shows no 8080/34113 listener. All writes were
under `/tmp/kama-r18-falsify-CorpusCensus` plus this report; the scratch tree (tip
clone, base clone, synth2, pending, scripts, capture files) was removed before filing.
