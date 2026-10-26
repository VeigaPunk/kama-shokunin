# R1Rerun — independent re-measurement of C1 (round 47, kama)

Verdict: **C1 CONFIRMED at 3a09a1d93dcc16799cf6c4b48786e6440af134c4** — three independent runs of the frozen counter (fresh random fixture each) all report `selftest=1 contract=1 lane=1 fixture=1 stable=1 files=85 lane_events=5 lane_mismatch=0 fixture_mismatch=0 met=True`, exit 0, byte-identical receipts; base 172b8ad040d51ce8c011238c1408d4e0b6aa9595 reproduces the preregistration `before` (`met=False`, exit 1); counter bytes match the frozen sha256; all five lane event deleted-counts independently match `git diff --numstat`.

## Counter-byte identity vs freeze

- Frozen (`preregistration.json`, claims[0].counter_sha256): `a180ab84cc642731a6bd5fca92e5218dfaa6c074279e2f001110b348d73755ed`
- `sha256sum` lane original `tools/round47-append-audit-v2-check.py` = `a180ab84…55ed` ✓
- `sha256sum` my clone's copy `$S/lane/tools/round47-append-audit-v2-check.py` = same ✓

Clone: full `git clone /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane` (not `--shared`), `rev-parse --show-toplevel` = the clone; HEAD `46a924e0`, both target commits present, base is an ancestor of the build tip (`git merge-base --is-ancestor` ok). Runs used the clone's own counter copy and `--repo $S/lane`; read-only on the lane repo (no index/jj mutation).

## Runs and receipts

Commands (each with its own `--scratch` subdir; `TMPDIR` set per run):

```
python3 $S/lane/tools/round47-append-audit-v2-check.py --repo $S/lane --tip 3a09a1d9…4c --scratch $S/runK --out …/out/R1Rerun/c1-build[.run2|.run3].out
python3 $S/lane/tools/round47-append-audit-v2-check.py --repo $S/lane --tip 172b8ad0…95 --scratch $S/runbase --out …/out/R1Rerun/c1-base.out
```

Every receipt line (build runs 1–3, byte-identical, sha256 `4b3a1e1914a0c99742aaf8a69e046a493e75c7f1cab6e22ce0d78517bccdef2a` each; no stderr, no detail lines — all legs passed):

```
selftest=1 contract=1 lane=1 fixture=1 stable=1 files=85 lane_events=5 lane_mismatch=0 fixture_mismatch=0 met=True
tip=3a09a1d93dcc16799cf6c4b48786e6440af134c4 base=172b8ad040d51ce8c011238c1408d4e0b6aa9595
```

Exit codes: run1=0 (3 s), run2=0 (3 s), run3=0 (3 s); base=1 (<1 s).

Base receipt, every line (sha256 `78268ba82b98562688ddf4ec4e8bfbf055fccc2a66cd2ae368209cd3a8265eb5`):

```
selftest=1 contract=0 lane=0 fixture=0 stable=0 files=0 lane_events=0 lane_mismatch=-1 fixture_mismatch=-1 met=False
tip=172b8ad040d51ce8c011238c1408d4e0b6aa9595 base=172b8ad040d51ce8c011238c1408d4e0b6aa9595
detail: contract: absent at tip
detail: fixture: tool exit=2, stdout is not one JSON object
```

Matches preregistration `before` "selftest=1 contract=0 lane=0 fixture=0 stable=0 met=False".

**Run-to-run differences: none.** `diff` of the three build receipts and of their stdout: byte-equal (the random fixture changes content each run, but no leg verdict, count, or detail line changes; stderr empty in all runs).

## Independent ground-truth spot-check (numstat, outside both tool and counter)

`git diff --numstat --no-renames <p> <c> -- <file>` on my clone, deleted column:

| event | file | numstat deleted | claimed |
|---|---|---|---|
| dd9f5dc6 | SCORECARD.md | 31 | 31 (24 restored, partial) ✓ |
| 0718b6ab | LOG.md | 2292 | 2292 restored ✓ |
| 0718b6ab | SCORECARD.md | 2421 | 2421 (2420 restored, partial) ✓ |
| 0718b6ab | corpus/QUALITY.md | 375 | 375 restored ✓ |
| 0718b6ab | corpus/README.md | 663 | 663 restored ✓ |

All five counter events are exactly the (commit, file) pairs above (0718b6ab verified on the first-parent chain of the tip), all above threshold 20, and the deleted counts equal numstat — the D1 property holds on the measured commit.

## Observations (not defects in the counter)

1. The frozen control `.ufo/waves/round-47/controls/base.c1.out` is not byte-identical to the counter's own `--out`: it carries an extra trailing `exit=1` line. Origin: `build_controls.py:57` appends `f"exit={p.returncode}\n"` to the captured output. Leg content is otherwise byte-identical to my base receipt. Cosmetic; the control's embedded verdict is unaffected. If byte-compare of controls against counter receipts is ever used as a gate, strip that trailer first.
2. No other run-to-run or vs-freeze discrepancy found. No tool installs were needed (git + python3 only).

## Artifacts

- `…/w1/out/R1Rerun/c1-build.out` (run 1, item-named path), `c1-build.run2.out`, `c1-build.run3.out`, `c1-base.out` — counter receipts, absolute paths in the final answer.
- Scratch `/fast/scratch/hyaku/kama-r47/R1Rerun` removed (clone, run scratch, stdout/stderr captures) after this report; receipts live in the out dir.
