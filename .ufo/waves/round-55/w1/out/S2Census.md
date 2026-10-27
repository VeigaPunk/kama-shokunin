# S2Census — round-55 census reconstruction audit

**Verdict: PASS — the recorded start receipt reproduces exactly (exit 1, sole finding E11 S510) from an independently recreated base tree, and the live census is green (exit 0, zero E-codes). No defects found.**

Seat scope: reconstruct the round-55 start census against the round-54 base tree
(3a600d2f729828419aaea34cc402c8b0d20fb720) and confirm the live census; report both.

## 1. Reconstructed base-tree census (reproduces start.out)

Setup (all under my scratch `S=/fast/scratch/hyaku/kama-r55/w1/S2Census`, `TMPDIR=$S`):

```
mkdir -p "$S/base-root/kama-shokunin"
cp /home/vgpnk/Projects/shokunin/shokunin.conf "$S/base-root/shokunin.conf"
git -C /home/vgpnk/Projects/shokunin/kama-shokunin archive 3a600d2f729828419aaea34cc402c8b0d20fb720 \
    | tar -x -C "$S/base-root/kama-shokunin"        # full-tree archive; rc=0
/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root "$S/base-root" kama
```

Result: **exit 1**, with exactly one E-code line and 97 W-code lines:

```
kama  E11  S510 missing used-by corpus/lessons/round-54.md
```

Byte-level comparison against the recorded receipt
`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/census/start.out`:
`diff` shows the only differences are that receipt's own 3-line `#` header and its
`census_start_exit=1` trailer — all 98 data lines (97 W + 1 E11) are identical.
Evidence: `out/S2Census/base-validate.out` (raw script output, 98 lines).

Base-corpus facts that drive the E11 (observed in `$S/base-root`):
- `corpus/SOURCES.md` at 3a600d2f: S510 row used-by = `corpus/lessons/round-54.md`
  (confirmed via `gawk -F'|'` on the row; live tree has it re-pointed to
  `corpus/lessons/round-55.md`).
- `corpus/lessons/` at 3a600d2f contains `round-53.md`, `round-53-verifier-spotcheck.md`,
  `round-54-verifier-spotcheck.md` — **no** `round-54.md`, so the used-by dangles → E11.
- No S511 row exists at 3a600d2f (`grep -cE '^\| S511 '` = 0); it was opened this round.

Note on method: a corpus-only archive (`git archive $BASE corpus`) is NOT equivalent —
E11 checks used-by paths repo-wide, and that variant spuriously reports ~150 E11s for
tools/SKILL.md/registry paths. The recorded start.out header says the base tree is
"byte-identical to the round-start working tree", and the pre-existing
`/fast/scratch/hyaku/kama-r55/census-base/kama-shokunin` (left untouched; not mine)
likewise holds the full tree. A faithful reproduction requires the full-tree archive.

## 2. Live census (round-end state)

Command:

```
/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate \
    --root /home/vgpnk/Projects/shokunin kama
```

Run against the live lane at HEAD `8abadfedf89f35372645b1e5d6ce4a2109186f90`
(w1 dispatch commit on top of the round-55 freeze `9c60eae6`).

Result: **exit 0**, zero E-code lines, trailer `kama  ok  /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md`,
98 W-code lines — the 97 from the base run plus the new
`kama W04 S511 duplicate url git-scm.com/docs/git-config across scopes` expected from
this round's S511 addition. Evidence: `out/S2Census/live-validate.out` (100 lines incl. ok row).

Live-corpus spot checks:
- `corpus/SOURCES.md:263` S510 used-by = `corpus/lessons/round-55.md` (re-pointed old→new, as frozen).
- `corpus/SOURCES.md:264` S511 present, used-by = `corpus/lessons/round-55.md`, opened 2026-10-27.
- `corpus/lessons/round-55.md` exists on disk → the E11 resolves to clean.
- `git diff 9c60eae6..8abadfed -- corpus/` is empty and `git status --porcelain`
  shows no corpus modifications (only sibling seats' untracked out files), so the live
  census is also the freeze-commit census.

## 3. Findings

None. The recorded start receipt is accurate and reproducible; the round-55 corpus
changes (S510 re-point, S511 addition, round-55 lesson) flip the lane from red
(exit 1, E11 S510) to green (exit 0) exactly as claimed in the freeze narrative.

Tool installs: none (used host `git`, `tar`, `gawk`, fleet `scripts/sources-census.sh`).
