# CtlNoOracle — round-30 C1 pre-freeze control (calibration)

Seat: `kama-r30-ctl-CtlNoOracle`. Advisory evidence, not a verdict.

## Policy

Run the frozen LANE counter with **only one** of the two declared oracle populations:

```
--oracle .ufo/waves/round-29/w1/out/RecallA/missed.json
```

i.e. substitute the default two-path `ORACLE_FILES` tuple (RecallA + RecallB, 32 + 40 = 72
items) with RecallA alone (32 items). No source bytes are changed; the policy lives entirely in
the invocation (counter line 512: `oracle_paths = tuple(o.oracle) if o.oracle else ORACLE_FILES`).

## Clone / candidate

- `git clone /home/vgpnk/Projects/shokunin/kama-shokunin /fast/scratch/hyaku/kama-r30/ctl/CtlNoOracle`
- checkout `52ac3af8614b5040ba5e17f17a2c7af029706e6c` (lane tip)
- candidate commit = `52ac3af8614b5040ba5e17f17a2c7af029706e6c`, tree `45c05ee28cb573d0996d069bfc742ac269f72f22`
- **diff vs lane tip: empty** (`git diff` 0 lines, `git diff-index --cached` 0 lines, status clean).
  No local commit was created because there is no tree mutation to commit; the policy is a CLI
  flag, and an empty marker commit would change the receipt `tip` without changing a byte the
  counter reads.

## Command

```
/usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-30/count-c1.py \
  --repo /fast/scratch/hyaku/kama-r30/ctl/CtlNoOracle \
  --tip 52ac3af8614b5040ba5e17f17a2c7af029706e6c \
  --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-30/controls/CtlNoOracle/counter.json \
  --oracle .ufo/waves/round-29/w1/out/RecallA/missed.json
```

## Result (arm)

Receipt: `counter.json` sha256 `9ed9f763be00f0f423324f4a8288405f96c1a2d344a30a82f90653363d584c54`
(`counter.out` sha256 `88c7801f093a35d75fc5d986eb4a5b05dbe981bd923392c6d32b5cb826af7a5d`).

Verbatim summary line:

```
statements 101 extracted 69 oracle 32 bound 32 unbound 0 mismatched_at_base 12 append_only True valid_corrections 11 false_corrections 0 unresolved 1 met False tip 52ac3af8614b
```

Exit `0`.

Receipt fields:

| field | value |
|---|---|
| statements | 101 |
| extracted | 69 |
| oracle_items | 32 |
| oracle_bound | 32 |
| oracle_unbound | 0 (`oracle_unbound_items: []`) |
| oracle_paths | `['.ufo/waves/round-29/w1/out/RecallA/missed.json']` |
| by_class | C 36, H 7, N 2, P 10, Q 40, T 6 |
| mismatched_at_base | 12 |
| append_only | True |
| correction_rows | 11 |
| valid_corrections | 11 |
| false_corrections | 0 |
| unresolved | 1 |
| unresolved_ids | `['SCORECARD.md:Q:4a6f7c911e:o0']` |
| met | **False** |
| counter_sha256 | c3f16ef195a6b5de24afa5a798647d917070d988954baf1fe5923fc5e19ce40d |

## Matched baseline (same clone, same tip, default both populations)

Auxiliary, not the arm receipt: `baseline-both-oracles.json` / `.out`.

```
statements 141 extracted 69 oracle 72 bound 72 unbound 0 mismatched_at_base 13 append_only True valid_corrections 11 false_corrections 0 unresolved 2 met False tip 52ac3af8614b
```
Exit `0`. Only difference from the arm is the oracle set.

## What the arm drops

The single mismatch present with both populations and absent with RecallA only is the RecallB
Q item at SCORECARD.md:901, sid `SCORECARD.md:Q:422b431349:o0`, token
`declared2048 = captured training2048`, observed `q:no-artifact`, W
`92b146253fd3a8c4bfade94c909dc63b13d6f4a8`. It is one of the two statements the
preregistration names as never carrying a correction row. Trimming the population therefore
removes both a required statement and its mismatch: `mismatched_at_base` 13 -> 12,
`unresolved` 2 -> 1.

## Shortcut assessment

**Not a genuine shortcut.** It cannot satisfy the frozen predicate: `oracle_items` 32 != 72,
`mismatched_at_base` 12 != 13, and `unresolved` 1 != 0 are three independent failures
(`met False`). Its only advantage is cost (one population, shorter run); it narrows the
measured universe away from the declared 141-statement population and silently discards a
named unresolved statement, which is exactly what the `oracle_items == 72` conjunct guards.

## State / restoration evidence

- Policy changed no clone bytes: HEAD and tree identical before and after
  (`52ac3af...` / `45c05ee2...`), status clean; no restore needed.
- Lane counter untouched: sha256 `c3f16ef195a6b5de24afa5a798647d917070d988954baf1fe5923fc5e19ce40d`
  before and after, matching the frozen value; lane HEAD `fdf8cda19c0719f57e0c2af27e838b42304b0f56` unchanged.
- Oracle blobs read at pinned `6de225c289b7682bf280cffb4a07de3fb7d1275c`:
  RecallA/missed.json `a0aeac67dcd07298b3ca92d15b14a31d6a4bfa36f538ba99d20ed5a7db3064df` (32 items),
  RecallB/missed.json `08d7c536031176fdcfae1c4ee33f5c8b4eae76a9a26b8002904dfe78a8473d06` (40 items).
- No lane git write; writes limited to this seat directory under `controls/`.
- No tools installed; used `/usr/bin/python3` 3.14.8 and `/usr/bin/git`.
