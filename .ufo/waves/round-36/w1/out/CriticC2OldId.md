# CriticC2OldId

Axis: coverage. Attacked object: `tools/round36-coverage-audit.py` at `9014843cb7de8fbe87a97954c13832b67d55f046` (blob `43d756e791d71e934dfe481607ebc93817249b8a`, sha256 `b052a9fe251bedac50641bae7fd79f08c8727691e8c75257968419a50d738b60`). The tool was not edited. The predicate was not retargeted. No file was constructed under `corpus/`.

**No. Citing S006 inside the round-36 heading does not set `cited_new`.** S006 is not a witness. With `named=1` and `file_exists=1` already true, that citation still leaves `cited_new=0` and `met=False`.

## Selftest line

From `.ufo/waves/round-36/controls/c2-selftest.out`:

```
SELFTEST base_met=False outside_met=False old_id_met=False pass=1
```

Re-run:

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round36-coverage-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip e5a8ececf3d60fd53b36bb74299693a29e8f74b6 --selftest
```

stdout (exit 0), identical to the control file:

```
SELFTEST base_met=False outside_met=False old_id_met=False pass=1
base named 0 file_exists 0 cited_new 0 met False
```

`pass=1` implies the script's own `old_id` fixture has `cited_new==0`. That fixture cites S006 in the entry argument (`"source: S006\n"`), not in the heading. The heading case was scored separately, below. Probes imported the file in memory. No `__pycache__` under `tools/`. No git mutation.

## Counterexample

Attempted: put S006 where a heading-scanner would see it, with the other two conjuncts already true, and see if `cited_new` flips. It does not.

`score()` sets `cited_new` only inside this guard (`round36-coverage-audit.py` lines 70-75):

```python
if entry is not None and tip_sources is not None and base_sources is not None:
    tip_ids = registry_ids(tip_sources)
    base_ids = registry_ids(base_sources)
    if any(sid in tip_ids and sid not in base_ids for sid in cited_ids(entry)):
        cited_new = 1
```

`cited_ids` runs on the entry blob only. `block_names` never reads S-ids. The readme, including `## Coverage map — round 36 addition` and the block under it, is not an input to `cited_new`.

Same `score()`, real base `e5a8ececf3d60fd53b36bb74299693a29e8f74b6:corpus/SOURCES.md` as both registries unless noted:

| Fixture | named | file_exists | cited_new | met |
|---|---|---|---|---|
| S006 only in the round-36 block (`\| knowledge/sglang-native-route-deprecation.md \| cites S006 \| 36 \|`); entry has no S-id | 1 | 1 | 0 | False |
| S006 on the heading line itself (`HEADING + " S006"`), entry has no S-id | 1 | 1 | 0 | False |
| False heading-string opener containing S006 and the entry path; entry text `source: S006` | 1 | 1 | 0 | False |
| Selftest shape: heading names the entry, entry is `source: S006`, tip sources = base sources | 1 | 1 | 0 | False |
| Entry cites only S006; tip adds `\| S999 \|` and still has the S006 row | 1 | 1 | 0 | False |
| S006 row deleted from tip; entry still cites only S006 | 1 | 1 | 0 | False |
| Entry text is the heading block that cites S006 | 1 | 1 | 0 | False |
| `base_sources is None`, entry cites S006 | 1 | 1 | 0 | False |

The selftest conjunct is the base exclusion, not a missing tip row. On that fixture `cited_ids` is `['S006']`, `S006 in tip_ids` is True, `S006 in base_ids` is True, and the witness `sid in tip_ids and sid not in base_ids` is False. No tip edit can make the id string `S006` satisfy `sid not in base_ids` while `load()` still shows that base blob: the base set is frozen by `git show e5a8ececf3d60fd53b36bb74299693a29e8f74b6:corpus/SOURCES.md`.

## Evidence

- Base registry row, matched by `registry_ids` (`^ {0,3}\|\s*(S[0-9]+)\s*\|`): `| S006 | SGLang Native APIs — https://docs.sglang.io/docs/basic_usage/native_api | ... |`. `S006 in base_ids` is True. Base id count 201. Every `\bS[0-9]{3,}\b` token in that blob is a registry id (`prose_only` empty, `tableish_unparsed` 0). A second prose mention of S006 on the health-chain line is not a second identity.
- `knowledge/sglang-native-route-deprecation.md` is absent at that base (`git show` returns None). `## Coverage map — round 36 addition` is absent from that base README. Do-nothing `cited_new` is 0. The tool itself is not in that commit; it is the HEAD blob above.
- Positive control, so the counter is not stuck at 0: entry `source: S006 and S999` with tip row `| S999 |` scores `cited_new=1 met=True`. The witness is S999. Removing S006 from that entry text is not required for the flip. Heading text `cites S006` plus entry `source: S999` also scores `cited_new=1`; the heading token is unused.

## Impacted axes

None. Coverage is not met by an S006 citation in the round-36 heading, in the entry, or in both. The kill "an S-id already present at `e5a8ececf3d60fd53b36bb74299693a29e8f74b6` must not count" holds for S006.

Not a `cited_new` defect: a quoted or prefix copy of the heading string can still make `named=1` (the false-opener row above). That is the heading-window question, not this kill. It does not launder S006.

## Tradeoff the correction must not take

Do not treat a mixed citation as an S006 pass, and do not "fix" it by requiring every cited id to be new. The frozen predicate is existential: the entry cites an S-id present at the tip and absent at the base. `any(...)` is that predicate. S006 in the same entry does not count and must not poison a real new id. Changing that would retarget C2.

Do not scan the heading for S-ids. A heading token is not the file citation the predicate names. Wiring the readme into `cited_ids` would create a second authority and could only add false witnesses.

## Smallest safe correction

None. Do not edit `score()`, the selftest, or the predicate for this kill. `pass=1` does not print the old-id `cited_new` line and does not place S006 in the heading; that is a label limit, not a false admit. The entry fixture already forces `cited_new==0` on the real base blob, and the heading cannot reach `cited_new` at all.

This seat did not apply a patch.
