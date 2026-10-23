# Seat kama-r29-w2-MutateBaseTip — C1 counter at the pre-data freeze tip (fresh clone) + one mutation probe

Claim served: C1 (calibration) — counter and receipts.
Item: run the counter at `--tip 827d136546b85059a984b34970f5b493d9a71290` (freeze commit, pre-data) in a fresh clone; expect `met False`, `unresolved 11`, `valid_corrections 0`, `append_only True`. Then one minimal mutation probe against that fail-closed invariant. No lane file was edited; no lane-index command was run.

## 1. Required probe — EXACT LINE (pristine counter, fresh clone)

Environment: `/usr/bin/python3` = Python 3.14.8, `git` 2.56.0. Fresh clone from lane HEAD:

```
git clone --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r29-w2-MutateBaseTip
HEAD = 513eba3ba51a142c9936553e3a85918345eb5c4c
git status --porcelain | wc -l -> 0   (clean: uncommitted attempt-1 leftovers do not travel into the clone)
sha256(.ufo/waves/round-29/count-c1.py) = fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383  (matches frozen sha in the ticket)
```

Command:

```
python3 .ufo/waves/round-29/count-c1.py --repo /tmp/kama-r29-w2-MutateBaseTip \
  --tip 827d136546b85059a984b34970f5b493d9a71290 \
  --out .../w2/out/kama-r29-w2-MutateBaseTip/tip-827d136.json
```

Output (verbatim, exit 0):

```
statements 69 mismatched_at_base 11 append_only True valid_corrections 0 false_corrections 0 unresolved 11 met False tip 827d136546b8
```

Receipt fields (`tip-827d136.json`): `statements 69`, `mismatched_at_base 11`, `append_only true`, `correction_rows 0`, `valid_corrections 0`, `false_corrections []`, `unresolved 11`, `unresolved_ids` = 11 entries, `met false`, `tip 827d136546b85059a984b34970f5b493d9a71290`. All four required values hold exactly.

Why the tip is genuinely pre-data (verified independently of the counter):

```
git show 827d136...:SCORECARD.md | grep -c 'SA29:'              -> 0
git show 513eba3...:SCORECARD.md | grep -c 'SA29:'              -> 11
git rev-parse 827d136:SCORECARD.md == git rev-parse 2aa46e2:SCORECARD.md -> identical blob
git merge-base --is-ancestor 827d136... 513eba3...               -> yes
```

So at the freeze tip SCORECARD is byte-identical to BASE, `append_only` is true by construction, no correction rows exist, and every one of the 11 mismatches is unresolved — the counter reports `met False`.

## 2. Non-vacuity contrast (same clone, same counter)

| tip | meaning | line |
|---|---|---|
| `513eba3ba51a` (data) | corrections present | `statements 69 mismatched_at_base 11 append_only True valid_corrections 11 false_corrections 0 unresolved 0 met True tip 513eba3ba51a` |
| `35b90184f638` (controls, pre-data) | 14 control receipts, no correction rows | `statements 69 mismatched_at_base 11 append_only True valid_corrections 0 false_corrections 0 unresolved 11 met False tip 35b90184f638` |
| `bdb2a5b4e410` (round-28 tip, below BASE) | pre-base fail-closed | `statements 69 mismatched_at_base 11 append_only True valid_corrections 0 false_corrections 0 unresolved 11 met False tip bdb2a5b4e410` |

The data-tip run is `met True`, so the freeze-tip `met False` is a discriminating verdict, not a broken environment/baseline failure.

## 3. Mutation probe (one plausible defect)

Mutation M1 — smallest behavior-bearing point, line 324 of `count-c1.py`, the `append_only` branch of the unresolved computation. Plausible defect: "with no correction rows, nothing can be unresolved" (an empty-corrections shortcut), which is precisely the assumption the pre-data probe exists to deny.

```diff
         if append_only:
-            unresolved_ids = sorted(set(mism) - valid)
+            unresolved_ids = sorted(set(mism) - valid) if valid else []
         else:
             unresolved_ids = sorted(sids)
```

Hashes:
- pristine `count-c1.py`: `fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383`
- mutated `count-c1.py`: `a89a92f92f87f35d2d9cd52b1202c249e5afb951721afe198c4c718a1fbd947e` (diff: this directory's `mutation.diff`, applied copy `count-c1.mutated.py`)

Detector = the required pre-data probe: run at `--tip 827d136`, expected `met False` / `unresolved 11`.

Mutated, freeze tip (verbatim, exit 0):

```
statements 69 mismatched_at_base 11 append_only True valid_corrections 0 false_corrections 0 unresolved 0 met True tip 827d136546b8
```

Mutated, data tip `513eba3` (verbatim):

```
statements 69 mismatched_at_base 11 append_only True valid_corrections 11 false_corrections 0 unresolved 0 met True tip 513eba3ba51a
```

Verdict: **KILLED** by the pre-data detector. Coverage finding: the mutant's data-tip receipt is byte-for-byte equivalent in its summary line to the pristine data-tip receipt (`met True`, `unresolved 0`, `valid_corrections 11`); the final-tip receipt alone would NOT have caught it. The freeze-tip probe is therefore load-bearing, not redundant with the data-tip receipt.

## 4. Restoration evidence

```
cp .count-c1.py.pristine .ufo/waves/round-29/count-c1.py
sha256(...count-c1.py) = fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383   (byte-exact restore; see restored.sha256)
python3 count-c1.py --repo <clone> --tip 827d136...  ->
statements 69 mismatched_at_base 11 append_only True valid_corrections 0 false_corrections 0 unresolved 11 met False tip 827d136546b8
git status --porcelain  -> "?? .count-c1.py.pristine" only (tracked counter clean)
```

Post-restore output is identical to the pristine probe; `tip-827d136.RESTORED.json` == `tip-827d136.json` in all reported fields.

## 5. Verdict

C1 slice CONFIRMED for this item: in a fresh clone at `513eba3`, the frozen counter (`fe11d599…`) at the pre-data freeze commit `827d136` fails closed — `met False`, `unresolved 11`, `valid_corrections 0`, `append_only True` — and the invariant is falsifiable: a one-line empty-corrections shortcut flips that verdict to `met True` and is killed by this probe. The lane's counter and receipt for this slice match the claim; no defect found in this slice. Lane working tree unchanged by this seat (13 dirty/untracked entries before and after; only `w2/out/kama-r29-w2-MutateBaseTip/` added, itself inside the pre-existing untracked `w2/`).

Note (observation, not a defect against this item): tips older than BASE (e.g. round-28 tip `bdb2a5b`) also report `append_only True` with `unresolved 11`/`met False`; the counter remains fail-closed there, but `append_only` alone does not signal that the tip predates BASE.

## 5b. Appendix — identity of the 11 unresolved statements at the freeze tip

At `827d136` the receipt's `unresolved_ids` equals its `mismatches` sids exactly (11/11), and the mismatch set is identical to the one at the data tip `513eba3` (which the 11 correction rows resolve). All 11 live in `SCORECARD.md` (7 `Q`, 4 `P`); none in `SHONEN.md`. `W` = revision blamed at BASE.

```
SCORECARD.md:Q:f4c42debcc:0  Q  ea72c3eae4ec  q:no-artifact
SCORECARD.md:Q:f4c42debcc:2  Q  ea72c3eae4ec  q:no-artifact
SCORECARD.md:P:980355388a:0  P  1e41928aba2b  p:absent
SCORECARD.md:Q:4f8083e30a:0  Q  40660352d4a9  q:no-artifact
SCORECARD.md:P:312b3e69b1:0  P  c6dc46fabc51  p:absent
SCORECARD.md:Q:0ccd533544:0  Q  7229fa95eb12  q:no-artifact
SCORECARD.md:Q:4c5d902830:0  Q  7229fa95eb12  q:no-artifact
SCORECARD.md:Q:f1021c03db:0  Q  7229fa95eb12  q:no-artifact
SCORECARD.md:Q:a7e98b1030:0  Q  7229fa95eb12  q:no-artifact
SCORECARD.md:P:1c6c1f3e4c:0  P  7f84cd0e7662  p:absent
SCORECARD.md:P:17a7db7c81:0  P  d183ec572a5e  p:absent
```

## 6. Evidence inventory (all absolute paths)

- `/tmp/kama-r29-w2-MutateBaseTip/` — fresh clone (counter restored to frozen bytes)
- `…/w2/out/kama-r29-w2-MutateBaseTip/tip-827d136.json` — required pristine receipt
- `…/tip-513eba3.json`, `…/tip-35b9018.json`, `…/tip-below-base.json` — contrast receipts
- `…/tip-827d136.MUTATED.json`, `…/tip-513eba3.MUTATED.json` — mutant receipts
- `…/tip-827d136.RESTORED.json` — post-restore receipt
- `…/count-c1.pristine.py` (`fe11d599…`), `…/count-c1.mutated.py` (`a89a92f9…`), `…/mutation.diff`
- `…/mutated.sha256`, `…/restored.sha256`

Tooling: nothing installed; no pacman transaction run; no network access needed.
