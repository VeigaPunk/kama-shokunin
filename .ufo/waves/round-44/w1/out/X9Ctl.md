# X9Ctl — round-44 freeze controls, independent re-run

**Verdict:** the controls reproduce exactly. All ten receipts carry the preregistration's
pinned summary line verbatim (10/10 MATCH), all ten end `exit=1` (i.e. `met=False`, as pinned),
and 2/10 are byte-identical to the committed copies while the other 8 differ **only** in their
first line `tip=<fixture commit>`; that line is derived from the throwaway fixture commit and is
therefore timestamp-dependent, which I proved by re-running with fixed commit dates (10/10
byte-identical across independent runs). Both frozen counters hash to the values pinned in
`preregistration.json` at `77d1bbf5`. No control is accidentally `met=True`, and no frozen
artifact changed between the freeze and the lane tip `098df344`.

## 1. Frozen inputs (sha256 at `77d1bbf55c62a1d5fc08fcbd682f22277a5cdb40` vs prereg)

Computed with `git -C <lane> show 77d1bbf5:<path> | sha256sum` in a `git clone --shared` of the
lane checked out at the freeze commit, then again as `sha256sum` of the checksummed working-tree
files in the real lane (identical — `diff` rc=0):

| file | sha256 | prereg pin |
|---|---|---|
| `tools/round44-release-recheck-audit.py` (C1 counter) | `87503e18e47dae6fa0414cf24d988f2a44ffa61d422db62c82cad3c24d8218d2` | C1 `counter_sha256` = same → **MATCH** |
| `tools/round44-verdict-ledger-audit.py` (C2 counter) | `1933e75b2a5308d09d0cfafd166c95cfcb1b7c15eaf1bf9ad2b321a453224bd1` | C2 `counter_sha256` = same → **MATCH** |
| `tools/release-recheck.py` (helper, not in predicate) | `50e77fa1a3d9d1d4407c3fbdc9e0b67aeceaf0a92389638f0c471d44991ba157` | C1 `helper` = same → **MATCH** |
| `.ufo/waves/round-44/controls/build_controls.py` | `1d3553b75f2a50e8a718e0220671a326f4f9183bb70c4627b2234cb9664cf03d` | (not pinned; recorded) |

Freeze integrity through the wave-1 spec commit: all four files above plus
`.ufo/waves/round-44/preregistration.json` (`c21f916186ccafd9ba278f9bcd6356bc456fd9eefcc5c493f9ff18f2ceb4cbc1`)
hash **identically** at `77d1bbf5` and at the lane tip `098df344d977a9047ea346a01a93c307887570b0`
(the wave-1 spec/draft/checker commit).

Evidence files: `out/X9Ctl/sha256-freeze.txt`.

## 2. Control run

```
S=/fast/scratch/hyaku/kama-r44/X9Ctl; export TMPDIR="$S"
git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin "$S/lane"        # rc=0
git -C "$S/lane" checkout -q 77d1bbf55c62a1d5fc08fcbd682f22277a5cdb40           # rc=0, HEAD=77d1bbf5…
git -C "$S/lane" rev-parse --show-toplevel                                     # /fast/scratch/…/X9Ctl/lane
python3 .ufo/waves/round-44/controls/build_controls.py \
  --lane "$S/lane" --upstream /fast/scratch/hyaku/kama-r44/shared/llama.cpp \
  --fleet /home/vgpnk/Projects/shokunin --scratch "$S/ctl"                     # rc=0, 6.9 s
```

Builder `rc=0` means its internal isolation guard (`git rev-parse --show-toplevel == clone dir`
before each fixture commit) passed for all four fixture clones; `$S/ctl` was empty afterwards
(each fixture is `shutil.rmtree`d, verified `ls -la` → 0 entries), and receipts landed only
beside the script **inside the clone** (`$S/lane/.ufo/waves/round-44/controls/*.out`), never in
the lane.

Ten receipts were produced (5 trees × 2 counters), exactly the keys of `preregistration.json`
`controls`.

Evidence: `out/X9Ctl/receipts-run1/` (fresh run), `out/X9Ctl/diffs/` (unified diff vs committed).

## 3. Per-receipt byte-equality

| receipt | full byte-equal | body-equal (from line 2) | summary line | exit |
|---|---|---|---|---|
| `base.c1.out` | **YES** (`8b6b3def…`) | YES | MATCH | 1 |
| `base.c2.out` | **YES** (`bd562491…`) | YES | MATCH | 1 |
| `junk-c1-allunchanged.c1.out` | no — `tip=` only | YES | MATCH | 1 |
| `junk-c1-allunchanged.c2.out` | no — `tip=` only | YES | MATCH | 1 |
| `junk-c1-draftonly.c1.out` | no — `tip=` only | YES | MATCH | 1 |
| `junk-c1-draftonly.c2.out` | no — `tip=` only | YES | MATCH | 1 |
| `junk-c2-allimproved.c1.out` | no — `tip=` only | YES | MATCH | 1 |
| `junk-c2-allimproved.c2.out` | no — `tip=` only | YES | MATCH | 1 |
| `junk-c2-noscorecard.c1.out` | no — `tip=` only | YES | MATCH | 1 |
| `junk-c2-noscorecard.c2.out` | no — `tip=` only | YES | MATCH | 1 |

The eight non-identical `diff`s are 8 lines each and consist solely of
`1c1 < tip=c8f11b7e…  --- > tip=a6393173…` (fixture commit shas of my run vs the committed run).
`base.*` are fully identical because their `tip=` is the fixed `BASE` commit, not a fixture commit.

Fresh `tip` values (real-timestamp run): `junk-c1-allunchanged=a6393173…`,
`junk-c1-draftonly=65690d8b…`, `junk-c2-allimproved=62b93dac…`,
`junk-c2-noscorecard=48be00f2…`, `base=9d9cc93e…`.

Evidence: `out/X9Ctl/byte-equality-summary.txt`, `out/X9Ctl/diffs/*.diff`.

## 4. Summary lines vs preregistration (10/10)

Every receipt's counter summary line (`pop=…` for c1, `rows=…` for c2) is **string-identical** to
the corresponding `controls.<name>.<tag>` value in `preregistration.json`:

```
base.c1                             MATCH pop=91 rows=0 valid=0 unverified=91 … section=0 met=False
base.c2                             MATCH rows=0 valid=0 missing=204 … summary=0 axes=0 met=False
junk-c1-allunchanged.c1             MATCH pop=91 rows=91 valid=6 unverified=85 … section=1 met=False
junk-c1-allunchanged.c2             MATCH rows=0 valid=0 missing=204 … met=False
junk-c1-draftonly.c1                MATCH pop=91 rows=91 valid=85 unverified=6 unchanged=4 holds=81 … met=False
junk-c1-draftonly.c2                MATCH rows=0 … met=False
junk-c2-allimproved.c1              MATCH pop=91 rows=0 … met=False
junk-c2-allimproved.c2              MATCH rows=204 valid=0 missing=0 bad=204 … met=False
junk-c2-noscorecard.c1              MATCH pop=91 rows=0 … met=False
junk-c2-noscorecard.c2              MATCH rows=204 valid=204 … agree=61 overclaim=3 underclaim=8 other=15 absent=15 table_missing=26 … met=False
```

`ALL_SUMMARY_MATCH=True`. Evidence: `out/X9Ctl/summary-vs-prereg.txt`.

Note the discriminating content is real, not vacuous: `junk-c1-draftonly.c1.out` shows the 6
draft TODO rows rejected with reasons (`S015 invalid: ranges do not parse or counts differ`,
`S037 invalid: unknown verdict`, …) and `section=0`; `junk-c2-noscorecard.c2.out` shows the
automatic last-hit ledger scored at `agree=61 / overclaim=3 / underclaim=8 / other=15 /
absent=15 / table_missing=26`, i.e. the counter is not fooled by mechanically plausible input.

## 5. Determinism finding (D1) and validated fix

`build_controls.py:commit()` commits in the fixture with `git -c user.name/email commit`, which
hashes the *current* timestamps into the fixture commit sha, and `score()` writes that sha as
line 1 of the receipt. Consequence: `diff` of an independent receipt re-run against the committed
receipt can never be empty for the 4 fixture trees (8 receipts).

Proof of the mechanism, two experiments:

1. Real-clock runs, repeated: run2 vs run1 → `IDENTICAL base.c1/.c2`, `TIP-ONLY-DIFF` for the
   other 8 (`c8f11b7e…/a6393173…` vs `a6393173…/af6b194f…`).
2. `GIT_AUTHOR_DATE=GIT_COMMITTER_DATE=2026-01-01T00:00:00 +0000` for two independent runs → the
   complete set of tips is identical between runs
   (`cmp` of the sorted tip sets → YES_ONE_TIP_SET), and 10/10 receipts are **byte-identical**
   between the two runs (`out/X9Ctl/receipts-fixeddate/`).

Proposed fix (full diff, not applied — controls are frozen):
`out/X9Ctl/proposed-fix-D1.diff` — give `sh()` an `env=` passthrough and pin
`GIT_AUTHOR_DATE`/`GIT_COMMITTER_DATE` inside `commit()`. Validated: the patched builder run
twice independently at `--lane $S/lane` produced 10/10 byte-identical receipts
(`out/X9Ctl/receipts-patched-fix/`, `out/X9Ctl/fix-validation.txt`) with the prereg summary
multiset unchanged (3× c1 base-line, 1× allunchanged, 1× draftonly, 3× c2 base-line, 1× bad=204,
1× noscorecard). So the fix buys reproducibility at zero behavioural cost.

Severity: low. The prereg pins only the summary line, so no claim is `met=True` or `met=False`
on this, and this round's evidence stands. It matters only for anyone — this seat included — who
is asked for "receipt byte-equality"; the correct reading here is "byte-equal from line 2".

## 6. Isolation / cleanliness checks

- Real lane untouched by me: `git -C kama-shokunin status --porcelain` shows no modification
  under `.ufo/waves/round-44/controls/` (only other seats' untracked `w1/out/`, `w1.ready`,
  `tools/merge.py`). Lane HEAD moved `77d1bbf5 → 098df344` by the L1's own wave-1 commit during
  my run — that is the L1, not this seat; frozen artifacts verified unchanged at `098df344` (§1).
- Fleet repo: `git -C /home/vgpnk/Projects/shokunin log -1` → `b0fd7b7f…`, unchanged; I ran no
  write and no commit there. No stray file created at the fleet root by me.
- Upstream `llama.cpp` clone: `rev-parse HEAD` → `d854d98bae598388ecea1ed84396587e5edc326d`
  unchanged, no checkout/fetch by me.
- No `pacman`, no installs, no tool upgrades this seat. No services touched, no `agent://all`.

### N1 (note, not a defect — but a live trap for other seats)

The shared upstream clone has **an empty worktree**: `git -C <upstream> status --porcelain` →
3914 entries (all staged `D`), `git ls-tree -r HEAD` → 3914 files, worktree files (depth ≤2) → 0,
`core.sparseCheckout` unset. Evidence that only the object store is intact:
`git -C <upstream> show d854d98…:src/llama-context.cpp | wc -l` → 4737.

The frozen counters are safe from this because they read upstream **only** through
`git rev-parse`/`git show`/`cat-file` (`round44-release-recheck-audit.py:96` `def git(repo,*args)`
→ `subprocess.run(["git","-C",repo,…])`; `:104` `git(repo,"show",f"{rev}:{path}")`; `:109`
`rev-parse --verify`; `:266,:272` `cat-file -e`) — consistent with my clean reproduction. Any
seat that reads an upstream *file path* directly (open(), grep on the worktree, `python -c
open(...)`) will silently see nothing. Read upstream with `git show <commit>:<path>` only.

### N2 (note)

`build_controls.py` resolves the receipt directory as `HERE = dirname(abspath(__file__))`, so
running the **lane's** copy would write ten receipts into the lane's tracked
`.ufo/waves/round-44/controls/`. That is exactly why the assignment says to run the clone's copy;
done that way, nothing outside my scratch was written. Anyone re-running controls must either use
a clone or add a `--receipts` option.

## 7. Evidence index (all under `.ufo/waves/round-44/w1/out/X9Ctl/`)

- `sha256-freeze.txt` — counter/helper/builder hashes vs prereg pins (§1)
- `receipts-run1/*.out` — the 10 fresh receipts from the clone (§2, §3)
- `diffs/*.diff` — `diff -u` committed vs fresh, one per receipt (§3)
- `byte-equality-summary.txt` — machine-generated table: full-byte / body flags, both sha256s, both tips
- `summary-vs-prereg.txt` — summary line vs `preregistration.json controls` (§4)
- `receipts-fixeddate/*.out`, `fix-validation.txt` — determinism experiment and validated fix (§5)
- `proposed-fix-D1.diff` — proposed `build_controls.py` change (§5)
- `receipts-patched-fix/*.out` — patched builder output, two independent identical runs (§5)

Method limits: byte-equality is asserted against the committed receipts at lane commit
`77d1bbf5`; I did not re-derive the counters' internals beyond the git-access points cited in
N1, and I did not run the counters against the live lane working tree (drafts there are other
seats' movable state).
