VERDICT: holds — Decoded-body visibility carries refusal of these 12 shortcut rows; json_strings and decoded-body serialisations cover each other, while case and whitespace normalisation are not required by this fixture.

# MutEchoDecodedLoadBearing — X1 evidence

Axes: **calibration** (echo refusal and guard attribution), **operability** (bounded reproducibility and exact-byte restoration). This is scoped mutation evidence, not the X1 claim verdict; withdrawn C1 was not scored.

All artifact names below are relative to `.ufo/waves/round-27/w1a3/out/MutEchoDecodedLoadBearing/` (`OUT`). Scratch was exclusively `/fast/scratch/hyaku/kama-r27c/MutEchoDecodedLoadBearing/`.

## Detector and input boundary

The detector imports each scratch counter under a non-`__main__` name and evaluates the frozen request-echo expression:

```python
any(counter.occurs(signature, s) for s in counter.request_surfaces(request))
```

Expected: all 12 shortcut rows flagged as echoed. Exit 0 means 12/12; exit 1 means at least one missed echo. A mutant survives only at 12/12. Every mutant used the same `harness.py`, registry bytes and detector on pristine, singly mutated, then restored bytes. No detector baseline failed.

The round-26 registry stores each wire JSON body as a **string** (`.ufo/waves/round-26/w2-falsify/out/CriticShortcutRows/shortcut.registry.json:19,41,63`, remaining rows through line 261). The harness decodes this once into the object accepted by the round-27 helper and also retains the exact original UTF-8 wire-body spelling in a harness-only `_wire_body` field. Only M1 uses that raw field. The fixture generator deliberately escapes the first character (`gen_shortcut.py:94-98` in the same shortcut directory). This distinction matters: dumping the already-decoded body is not the original as-sent body.

Frozen behavior: `.ufo/waves/round-27/count-c1.py:343-372`; its actual clause-(f) request check is at `:585-587`, and the clause is documented at `:44-48`.

## Mutation table

Each row is an independent scratch file; mutants were never stacked. Actual diffs were captured before restoration in `OUT/M1.diff` through `OUT/M5.diff`.

| Mutant | Diff against original frozen line(s) | Pristine | Mutated flagged/12 | Restored | Exit P/M/R | Verdict and covering guard |
|---|---|---:|---:|---:|---|---|
| M1 | Replace lines 369–371 with `surf.append(req["_wire_body"])`; retain request path and original `occurs` | 12 | **0** | 12 | 0/1/0 | **Killed.** The original raw path/body spelling misses every Unicode-escaped first character. No remaining guard covers these bodies. |
| M2 | Delete line 369: `surf += json_strings(body)` | 12 | **12** | 12 | 0/0/0 | **Survived.** Both `json.dumps` serialisations of the decoded object contain every signature verbatim. |
| M3 | Delete lines 370–371: both `json.dumps` surfaces | 12 | **12** | 12 | 0/0/0 | **Survived.** `json_strings[7]`, the decoded `response_format.type` value, contains every signature verbatim. |
| M4 | Replace line 348 with case-sensitive verbatim OR case-sensitive whitespace-squashed matching | 12 | **12** | 12 | 0/0/0 | **Survived.** Exact-case verbatim matches in decoded values and both serialisations cover all 12. |
| M5 | Replace line 348 with `return sig.lower() in text.lower()` | 12 | **12** | 12 | 0/0/0 | **Survived.** Verbatim matching in decoded values and both serialisations covers all 12; whitespace squash is unnecessary here. |

M4's precise replacement was:

```python
return sig in text or re.sub(r"\s+", "", sig) in re.sub(r"\s+", "", text)
```

Thus neither matching alternative retains a hidden case fold through `squash()`. The original helper remains untouched for all other callers.

Result anchors: `OUT/M1.mutated.json:5-9` (0 echoes, exit 1); `OUT/M2.mutated.json:19-35` (both serialisation guards); `OUT/M3.mutated.json:19-26` (decoded-value guard). Aggregate counts, verdicts and phase hashes: `OUT/summary.json:6-28` (M1), `:30-55` (M2), `:57-81` (M3), `:83-109` (M4), `:111-137` (M5). Every surviving hit was exact-case verbatim, not dependent on normalisation.

## Commands and actual outputs

`OUT/commands-and-output.txt` records the exact executed commands and trimmed stdout for all 15 detector runs, preparation, diff capture and aggregation. Representative killed-mutant command, executed exactly:

```sh
timeout 30s bash -c 'ulimit -f 1048576 && ulimit -v 262144 && ulimit -u 512 && ulimit -t 20 && exec /usr/bin/python3 -I -S -B /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-27/w1a3/out/MutEchoDecodedLoadBearing/harness.py --phase mutated --mutant M1'
```

Actual trimmed output, exit **1**:

```text
M1 mutated flagged=0/12 exit=1 sha256=29b227d8695f4c24f794768c8a4994c471dbb7a965af808baf2acd772d3f72d9
X26-01=MISSED X26-02=MISSED X26-03=MISSED X26-04=MISSED X26-05=MISSED X26-06=MISSED X26-07=MISSED X26-08=MISSED X26-09=MISSED X26-10=MISSED X26-11=MISSED X26-12=MISSED
```

`evidence.py finish` emitted, exit **0**:

```text
M1 pristine=12/12 mutated=0/12 restored=12/12 killed exact_restoration=True
M2 pristine=12/12 mutated=12/12 restored=12/12 survived exact_restoration=True
M3 pristine=12/12 mutated=12/12 restored=12/12 survived exact_restoration=True
M4 pristine=12/12 mutated=12/12 restored=12/12 survived exact_restoration=True
M5 pristine=12/12 mutated=12/12 restored=12/12 survived exact_restoration=True
lane source and six scratch files match frozen bytes; exit=0
```

Setup-only failures are retained in the command record: an initial bounded shell copy could not fork under the process limit (exit 254), and `ps -L` was unsupported, so its `wc` output was not treated as a census. Preparation then succeeded using `exec` into Python without child processes. Neither failure was a detector result or a baseline failure.

## Hashes and restoration

Before all mutations and after exact inverse edits, the lane source and all six scratch files were byte-identical to the frozen counter:

```text
49491b80e4f4ed2a85ab822a52f0b1a0fdb1dee53423e3d43b60ee25d1bf2765
```

| Mutant | Mutated SHA-256 |
|---|---|
| M1 | `29b227d8695f4c24f794768c8a4994c471dbb7a965af808baf2acd772d3f72d9` |
| M2 | `e07f29935fab378a4952a326f52064bf93392e3d02a3ee2b0eb04ec5426d07f0` |
| M3 | `41b09ff0b5bb297295c698472ad1c6a4d37813650fc87bd7caf0954883e8c6be` |
| M4 | `27b895668065bed6062592be903f5361e7044db0a279d3ea391452f27e34b934` |
| M5 | `3c29e44cfad5358ad315670bd9c4a6fc327ffc0ffbfcc85a9c47b6b9691a482e` |

The registry SHA-256 was `1b78c8aa0423151b9d84f6ad3cef35de7e5260e5ec869fea764ba5dbcc691b91`. Every detector receipt records import-before/import-after hashes at lines 5–6; every restored receipt has the frozen hash and 12/12 at lines 5–9. `OUT/prepare.json:3-8` records original copy hashes; `OUT/summary.json:2-4` records exact restoration and unchanged lane source. The collector also compared complete restored bytes, not hashes alone.

## Limits of this evidence

Decoded-body visibility, rather than the raw escape spelling, is necessary on these original shortcut bytes. The decoded-string walk and decoded-object serialisations are independently sufficient on this fixture, so their individual deletion mutants survive. This does **not** show either guard dispensable generally, nor test case variations, whitespace changes, quote/backslash escaping, non-ASCII serialisation differences, or shared-frame clause (h). Survivors are coverage findings, not contract changes.

This is strictly a helper-level replay: the old registry was not passed through round-27 `static_checks`, no `main()` or counting command ran, no claim is made that round-27 would transmit the old escape spelling unchanged, and no live-server behavior or overall row acceptance was measured. A Python audit hook forbade process launches, exec/fork and network connect/bind/lookup; no such event occurred. All command processes returned; no server or persistent process was started. File size was capped at 1 GiB, address space at 256 MiB, process limit at 512, CPU at 20 seconds, and wall time at 30 seconds for the successful Python invocations (`OUT/prepare.json:12-24`). No tools were installed or updated. No lane source, sibling source, Git index or repository state was modified.
