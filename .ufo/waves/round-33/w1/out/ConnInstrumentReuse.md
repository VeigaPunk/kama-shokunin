# ConnInstrumentReuse — r32 gate output vs reusable receipt bytes

Seat: connector. No shared lane files edited. No tools installed (pacman pause; nothing missing for a read-only compare).

## Axes

- Reuse fidelity: which existing command and format bytes already satisfy a round-33 receipt.
- Contract compatibility: whether a nearby capture shape parses as `KAMA_GATE_RECEIPT_V1` and matches `EXPECTED_STDOUT`.
- Lineage integrity: source rev `967d88528c1d83535563f971863f7855f76b4849` must not be replaced by the c2r tip `dc4258bdb08d658f1c5b15abc8378461659bd155` or by a 12-hex selftest prefix.
- Non-harm: C1 still needs the three authoritative r32 stdout files byte-intact. Do not wrap or rewrite them to satisfy C2.

## Evidence

### Reusable bytes (C2 only)

Registered commands, `SKILL.md` round-33 receipt section and `preregistration.json` C2:

```sh
python3 tools/round33-gate-receipts.py capture --repo . --source-rev 967d88528c1d83535563f971863f7855f76b4849 --out .ufo/waves/round-33/c2/final
python3 tools/round33-gate-receipts.py audit --repo . --tip <full commit> --source-rev 967d88528c1d83535563f971863f7855f76b4849 --receipt-dir .ufo/waves/round-33/c2/final
```

`capture` refuses an existing output directory (`round33-gate-receipts.py` `capture`) and will not refresh `.ufo/waves/round-33/c2/final`. Replay is `audit` of committed blobs.

Header order from `receipt_text` (final `gate-tip-r33.out` matches):

```
FORMAT=KAMA_GATE_RECEIPT_V1
FIXTURE=<gate-tip|thin-row|empty-exit-map|missing-path>
COMMAND=<stable replay line below>
COMMAND_ARGV_JSON=<not replayable; see below>
SOURCE_REV=967d88528c1d83535563f971863f7855f76b4849
EVALUATED_REV=<40 hex>
EVALUATED_TREE=<40 hex>
GATE_SHA256=e07cf8d753560cd34b5945c89f4dc3f19122ca87d19f8e85844e3b1ae4e0506b
RUNNER_SHA256=309543621a90f3c50bf130e06bc4e26a95e40202d84e81f769fca826a9e1dc04
EXIT_CODE=<0 for gate-tip, 1 for the three controls>
STDOUT_BEGIN
<exact EXPECTED_STDOUT lines, trailing newline>
STDOUT_END
STDERR_BEGIN
STDERR_END
```

Stable `COMMAND` lines (placeholders, not temp paths). These are what `output_ok` compares:

```
python3 tools/gate-registry-check.py --repo <lane> --rev 967d88528c1d83535563f971863f7855f76b4849
python3 tools/gate-registry-check.py --repo <fixture:thin-row> --rev 77ff9c056e32f5c5b41abd3c0d2e83a59c2e6a83
python3 tools/gate-registry-check.py --repo <fixture:empty-exit-map> --rev 58f49f42348c74af41a31dc06697f4edf4292c8d
python3 tools/gate-registry-check.py --repo <fixture:missing-path> --rev a1ff870829fb2980f9716359e115095441eb7297
```

`COMMAND_ARGV_JSON` is not a replay command. Final gate-tip argv is:

```
["/usr/bin/python3", "/tmp/kama-r33-gate-vjibi9wa/lane-gate/gate-registry-check.py", "--repo", "/home/vgpnk/Projects/shokunin/kama-shokunin", "--rev", "967d88528c1d83535563f971863f7855f76b4849"]
```

`audit` does not require argv equality. `output_ok` only checks length 6, `python`/`python3` basename, script suffix `gate-registry-check.py`, `--repo`, absolute repo, `--rev`, and argv[5] equal to `EVALUATED_REV`. The `/tmp/kama-r33-gate-*` directory is gone. Replaying argv[1] fails.

Fixture commit ids are content-addressed, not runner-addressed. thin-row `77ff9c05…` / tree `3782dc3d0053c0c06462834e47f6da300fb1c878` and missing-path `a1ff8708…` / tree `136ed301987ca8fd2dfd40054b49b6c2f4ddb5c3` are identical in `diagnostic-attempt1` and `final` while `RUNNER_SHA256` changed (`3913d26b…` → `30954362…`). `audit` accepts any runner digest in `git log` of `tools/round33-gate-receipts.py`. It does not accept a fixture commit the current runner no longer rebuilds.

### Incompatible contracts (do not reuse)

1. Authoritative r32 fixture stdout is the C1 oracle, not C2 stdout.

| fault | C1 path (`round33-claim-audit.py` `FAULTS`) | sha256 | first defect line |
|---|---|---|---|
| thin-row | `.ufo/waves/round-32/c2/controls/thin-v2.out` | `72274403cbf7f7052919778b57073fe95d089d13fe7f6230d8b45b55a4040a78` | `defective .ufo/waves/round-29/count-c1.py: thin-row` then `registered 9 unregistered 0 defective 3` |
| empty-exit-map | `.ufo/waves/round-32/c2/controls/noexit-v2.out` | `6093142f78a564a2766dc47408105ae7af93c30b36ccfc6380e4f6138cb30a79` | `defective .ufo/waves/round-29/count-c1.py: empty-exit-map` then `registered 9 … defective 1` |
| missing-path | `.ufo/waves/round-32/c2/controls/badpath-v2.out` | `067828249770a393ee0e33dd31a91a593e26b625b51c640132d7315004c9cdca` | `defective .ufo/waves/round-29/count-c1.py: missing-path:.ufo/waves/round-999/count-c999.py` then `registered 9 … defective 1` |

C2 `EXPECTED_STDOUT` names `.ufo/waves/round-33/count-fixture.py` and `registered 1`. `output_ok` requires `stdout.splitlines() == EXPECTED_STDOUT[case]`. Pasting the C1 lines into a V1 envelope makes the receipt `invalid`. Rewriting the r32 files to the synthetic lines makes C1 `expected_line in corrected_receipt` fail and breaks the byte-intact rule in `SKILL.md`.

2. The three stale `*-v2.out` files are one base-tree capture, not three controls.

sha256 `002a4b6072f54c8213b9914a1d8a15c5992907e8a26c7d685df5c6c519482a77` is shared by `before-base.out`, `thin-row-v2.out`, `empty-exit-v2.out`, and `nonexistent-path-v2.out`. Body:

```
unregistered .ufo/waves/round-17/count-verdicts.py
unregistered .ufo/waves/round-26/count-c1.py
registered 7 unregistered 2 defective 0
```

No `EXIT_CODE`, no revision. Clean gate stdout is a different file: `gate-tip.out` sha256 `9acdd7cfb4f9d3c888349c25bdf249bce92b222351243d69b9429409c718534a`, single line `registered 10 unregistered 0 defective 0`. `gate-data-tip.out` (`98f55a2a…`) is not that arm: it adds `defective .ufo/waves/round-32/count-c2r.py: missing-path:.ufo/waves/round-32/c2r/c2r-tip.json`.

3. v1 `EXIT_CODE=` is a copied stdout trailer, and `parse_receipt` rejects it.

All seven `*-v1.out` files share sha256 `72032b1e1bdca4a136e38b7f5fc08521048fd1a6c5308a57c891c8d5518816c8`, including `prose-only-v1.out`:

```
registered 9 unregistered 0
EXIT_CODE=0
```

`SUMMARY.md` says `prose-only-v1.out` is the base tree with two prose-only counters. The bytes are not. Defect 4's hint to record exit "like the v1 controls" does not produce `STDOUT_BEGIN` / `FORMAT=KAMA_GATE_RECEIPT_V1` / `SOURCE_REV` / full `EVALUATED_REV`. `parse_receipt` returns None, so `audit` counts the file `invalid`, not a partial.

Mutation exits are not one shape either. `MutNoExitMap-vs-CtlNoExitMap.out`, `MutNoPath-vs-CtlBadPath.out`, and `MutNoPath-vs-CtlBadpath.out` append `EXIT_CODE=0` after a banner or a summary line. `MutNoThin-vs-CtlThin.out` (`ea194aa0…`) has no `EXIT_CODE`. `MutNoExitMap-vs-CtlBadpath.out` is byte-identical to `badpath-v2.out` (`06782824…`) and also has no `EXIT_CODE`. Copying "the mutation receipt" can copy the control stdout.

4. `tools/instrument-agreement.py` is the wrong instrument, and it is not a registry row.

`SKILL.md` has no cell containing `tools/instrument-agreement.py`. The gate contract (`gate-registry-check.py` lines 15–18) says a prose mention does not register; the only pointer is `corpus/knowledge/instrument-run-agreement.md` `recheck:`. That file states `agree` is reproducibility, not correctness.

Receipt schema is JSON `instrument-agreement/v1`. Each run keeps `exit` plus `stdout_head` (first line, 200 chars) and drops later lines. The C2 summary line is the last stdout line, so a thin-row agreement receipt would keep the defect line and drop `registered 1 unregistered 0 defective 3`. There is no `SOURCE_REV` / `EVALUATED_REV` split and no `STDOUT_BEGIN`. Three runs of the stale body would `agree` (one sha256 `002a4b60…`), which is the r32 defect certified as success. Default `--runs` must be ≥ 2, so it cannot emit the single-shot four-receipt set.

5. Diagnostic empty-exit is already a V1-shaped receipt the oracle must reject.

`diagnostic-attempt1/controls/empty-exit-map.out` has `FORMAT=KAMA_GATE_RECEIPT_V1`, `SOURCE_REV=967d8852…`, `EXIT_CODE=1`, and `GATE_SHA256` equal to final, but stdout is:

```
defective .ufo/waves/round-33/count-fixture.py: empty-exit-map
defective .ufo/waves/round-33/count-fixture.py: missing-path:tools/measure.py
registered 1 unregistered 0 defective 2
```

`EVALUATED_REV=4a229db4c725f30ba4393293ad55f19c33432baa` and tree `8b159b005aa8b16f50df1b462818f348c01c4fc2`, not final `58f49f42348c74af41a31dc06697f4edf4292c8d` / `30f8b99a78ef97dec65c8fb664c41b60b48dc5da`. Amendment-1: the entry cell contained the path token `tools/measure.py`; the final row is the path-free text `python3`; the oracle now requires the exact line set. Reusing the diagnostic file, or rebuilding the fixture with any slash token in the entry cell, changes both stdout and `EVALUATED_REV`, so stable-field equality fails even though `RUNNER_SHA256` would still be historical.

6. Wrong revision pins.

| source | bytes | why it is not the gate evaluated rev |
|---|---|---|
| `c2r/c2r-tip.json` `tip` | `dc4258bdb08d658f1c5b15abc8378461659bd155` | statement-writing commit; the lineage contradiction if copied into `EVALUATED_REV` |
| `selftest-final.out` line 6 | `lane-tip 967d88528c1d` | 12 hex; `FULL_REV` and `output_ok` require 40 |
| clean arm | `967d88528c1d83535563f971863f7855f76b4849` | `SOURCE_REV` and `EVALUATED_REV` on `gate-tip-r33.out`; tree `cedccaa267dfbcaa60f4b860c94d3b6e23800f22` |

`selftest-final.out` also stores `exit=1` in prose and puts the summary in `line=` while `want-line=` holds the defect. Paths there are `.ufo/waves/round-98/count-selftest.py`, a third vocabulary besides round-29 (C1) and round-33 (C2).

## Proposed move

Keep the two contracts disjoint. C2 replay stays on the registered capture/audit commands and the final `KAMA_GATE_RECEIPT_V1` bytes above. Do not "complete" r32 gate outputs by grafting v1 `EXIT_CODE=` trailers, mutation banners, `instrument-agreement/v1` JSON, `selftest-final.out`, `gate-data-tip.out`, or `c2r-tip.json`'s `tip` into that envelope. Do not wrap `thin-v2.out` / `noexit-v2.out` / `badpath-v2.out` either: those lines are the C1 correction oracle. The empty-exit fixture entry must stay the path-free word `python3`; any slash token recreates the diagnostic second defect and a new fixture commit.

This improves C2 operability (a false reuse path cannot turn `complete=4/4` into `invalid`) and does not move C1: the three historical files stay the correction targets, stale files stay disclosed legacy, filed report bytes stay untouched.

## Risks

- A later edit to `write_fixture` changes `EVALUATED_REV`, `EVALUATED_TREE`, `COMMAND`, and exact stdout together. Historical `RUNNER_SHA256` membership will not save those receipts. thin-row and missing-path survived the runner-hash change only because their fixture bytes did not change; empty-exit did not.
- `COMMAND_ARGV_JSON` still looks like the "exact argv" `SKILL.md` describes. A consumer that shells it out will fail on a dead temp path even when `audit` would pass.
- `instrument-agreement` over the stale trio would print `agree` and exit 0. That is a green result for the defect.

## Verification

Observed this round, read-only: the sha256 identities above; header and stdout reads of final, diagnostic, v1, v2, `before-base`, `gate-tip`, `gate-data-tip`, `selftest-final`, and `c2r-tip.json`; `FAULTS` / `EXPECTED_STDOUT` / `parse_receipt` / `output_ok` / `audit` stable fields in the two counters; no `tools/instrument-agreement.py` cell in `SKILL.md`.

L1 check that falsifies this move: point `round33-gate-receipts.py audit` at a directory whose four bodies are v1 trailers, stale `*-v2.out`, diagnostic empty-exit, or V1 envelopes whose stdout is the round-29 `registered 9` lines. Expected: `complete` below `4/4` (`missing` or `invalid`), not a C1 regression. The passing set remains `.ufo/waves/round-33/c2/final` at source rev `967d88528c1d83535563f971863f7855f76b4849`. Do not re-capture onto that existing directory.
