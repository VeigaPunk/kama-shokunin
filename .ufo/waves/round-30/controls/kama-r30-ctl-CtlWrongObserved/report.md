# CtlWrongObserved — round-30 C1 (calibration) control arm

Advisory evidence for the pre-freeze control call. Not a verdict on C1.

## Policy (as assigned)

Append the two round-30 comment rows with CORRECT sids but observed `observed`
(a placeholder) for both. Expected: 2 false corrections (wrong-observed),
unresolved 2+2; met False.

## Clone and candidate

- Clone: `/fast/scratch/hyaku/kama-r30/ctl/CtlWrongObserved`
- Start: `52ac3af8614b5040ba5e17f17a2c7af029706e6c` (lane tip), clean
- Candidate commit: `50a4db7e73af36fd8a241aac325d5c110e8f7144`
  ("control CtlWrongObserved: append two round-30 comment rows with correct sids
  and placeholder observed"), tagged `ctl-wrong-observed-candidate`
- Change: 1 file, +2 lines in `SCORECARD.md`, inside the existing
  "## Round 29 — self-assessment corrections" table (append-only vs base keeps
  the base prefix; the table lies far past the base file's 1441 lines).
- Diff: `mutant.diff` in this directory (sha256 2292bea2d75e0993e5f186373d27bdfbc6f96e7a2c3086a1f5a74f1795752567)

```
+| SA29:SCORECARD.md:Q:4a6f7c911e:o0 | SCORECARD.md:41 | Q | `file=yes` | ea72c3ea | round-30 comment row (control arm CtlWrongObserved): observed value is a placeholder, not a measurement | observed |
+| SA29:SCORECARD.md:Q:422b431349:o0 | SCORECARD.md:901 | Q | `declared2048 = captured training2048` | 92b14625 | round-30 comment row (control arm CtlWrongObserved): observed value is a placeholder, not a measurement | observed |
```

These are the two statements the baseline receipt leaves unresolved
(`SCORECARD.md:Q:4a6f7c911e:o0` line 41, `SCORECARD.md:Q:422b431349:o0` line 901);
both fail Q with observed `q:no-artifact`.

## Command (lane counter, lane bytes unchanged)

```
/usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-30/count-c1.py \
  --repo /fast/scratch/hyaku/kama-r30/ctl/CtlWrongObserved \
  --tip 50a4db7e73af36fd8a241aac325d5c110e8f7144 \
  --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-30/controls/kama-r30-ctl-CtlWrongObserved/counter.json
```

Counter sha256 `c3f16ef195a6b5de24afa5a798647d917070d988954baf1fe5923fc5e19ce40d`
(verified before and after; no tool installs, no pacman).

## Detector runs (same lane counter bytes)

Pristine (`52ac3af`, exit 0):

```
statements 141 extracted 69 oracle 72 bound 72 unbound 0 mismatched_at_base 13 append_only True valid_corrections 11 false_corrections 0 unresolved 2 met False tip 52ac3af8614b
```

Mutant (`50a4db7e`, exit 0):

```
statements 141 extracted 69 oracle 72 bound 72 unbound 0 mismatched_at_base 13 append_only True valid_corrections 11 false_corrections 2 unresolved 4 met False tip 50a4db7e73af
```

Restored (`52ac3af`, exit 0):

```
statements 141 extracted 69 oracle 72 bound 72 unbound 0 mismatched_at_base 13 append_only True valid_corrections 11 false_corrections 0 unresolved 2 met False tip 52ac3af8614b
```

Mutant receipt fields: `correction_rows 13`, `valid_corrections 11`,
`false_corrections 2` — both `why: wrong-observed`, `observed: "observed"`,
sids `SCORECARD.md:Q:4a6f7c911e:o0` and `SCORECARD.md:Q:422b431349:o0`;
`unresolved_ids` = those two sids; `unresolved 4` = 2 unresolved statements
+ 2 false rows; `met false`.

## Verdict

KILLED as designed: the arm fails the frozen predicate exactly as expected
(false corrections 2, unresolved 4, met False). A genuine shortcut? No — it
names the right statements but supplies no measured observed value, so the
counter refuses each row as wrong-observed and counts each false row as
unresolved on top of the statement it fails to correct. This shows the
correction check is value-keyed, not sid-keyed: correct sids alone cannot
turn C1 green. A green measurement here would not make the claim; this one is
red by construction.

## Restoration evidence

- `SCORECARD.md` before: sha256 `b155ca88c6d93e28b52e7d2089139fbc116c53e7d664922429750a247a6abcbd`,
  blob `21a41a7c170ac1f1d10f53a228f3b8abd8cec57c`
- after restore (`git checkout 52ac3af...`): same sha256 and blob; clone
  `git status --porcelain` empty; HEAD back at `52ac3af8614b5040ba5e17f17a2c7af029706e6c`
- candidate commit preserved at tag `ctl-wrong-observed-candidate`
- lane working tree untouched: lane `SCORECARD.md` sha256 `b155ca88…6abcbd`
  (blob `21a41a7c…`), lane counter sha256 `c3f16ef1…9ce40d` throughout

## Files

- `counter.json` (mutant receipt, 4342 B, sha256 d3400b1c…96da20)
- `counter.out` (summary line + exit)
- `pristine.json` (baseline run with `--list`, sha256 f30516de…)
- `restored.json` (restored run, sha256 9e074378…)
- `mutant.diff` (sha256 2292bea2…)
