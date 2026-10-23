VERDICT: holds — With clause (f) bypassed, the frame rule alone limits these 12 round-26 shortcut rows to one survivor.

## Scope and axes

Probe evidence for exploratory X1, not X1's reviewer verdict and not a C1 score.
Axes: frame discrimination (survivor count), causal isolation (only one production predicate disabled), and byte preservation (exact restoration).

Offline only. No server, counter main(), other runtime, subagent, tool installation/update, or background process was started. All behavioral commands completed within their timeouts.

## Results

| Variant | Survivors / 12 | Surviving IDs | Rejections | Detector exit |
|---|---:|---|---|---:|
| Pristine, all clause-(h) checks on | 1 | X26-01 | 11 `h:same-message-frame` | 0 |
| Mutated, frame check off; other (h) checks on | 12 | X26-01 through X26-12 | none | 1 |
| Only `h:shared-message` on | 12 | X26-01 through X26-12 | none | 0 |
| Only `h:same-message-frame` on | 1 | X26-01 | 11 `h:same-message-frame` | 0 |
| Restored, all clause-(h) checks on | 1 | X26-01 | 11 `h:same-message-frame` | 0 |

**Mutant: killed.** The identical primary detector required one survivor on pristine, mutated, and restored bytes: exits **0 → 1 → 0**. Control expectations were separately 12 for shared-only and 1 for frame-only; they are not substitutions for the primary detector.

All evidence files named below are under `.ufo/waves/round-27/w1a3/out/MutFrameLoadBearing/` unless another location is given. Primary records: `pristine.json:2-30`, `mutated.json:2-39`, `restored.json:2-30`; single-rule controls: `shared-only.json:2-46`, `frame-only.json:2-36`. Complete per-row reasons and survivor IDs are in those JSON files. Matching `.stdout`, `.stderr`, `.exit`, and `.module.py` files preserve each run's output and executed scratch-source bytes.

## Harness and isolation

Harness: `probe.py` (sha256 `e38ef1595b2feb8df535ca368c078c24399c467eadee3f64f4f71de6f0942cb1`). Fixture: `rows.json` (sha256 `611c6ce2a9acbfa9b1b2d2bdf6c5429bd1458acb8fb147943fa4d037af8ef431`).

- `probe.py:44-76` reads the committed round-26 registry and receipt, preserving every signature, request, and JSON-decoded `error.message`. All 12 stored channel excerpts hash to their recorded channel SHA-256 values (`preparation.json:2-123`). No new live observations are claimed.
- `probe.py:66-68` synthesizes distinct source cells `(original file, line 10001..10012, row FRAME-SYNTH-01..12)` and distinct next-action cells. All 12 canonical requests are also distinct. All rows start with empty `why`; clauses (a)-(g), including (f), are outside the extracted harness. This is explicitly a clause-(h)-only replay, not a full counter run (`preparation.json:152`).
- `probe.py:88-96` extracts frozen counter lines **691-722**, changes indentation only, and wraps them in `count_rows`. Lines 721-722 are included because they append the accepted row; line 690 is an unrelated server-close exception and is not executed. Raw extraction: `clause-h.extracted.txt`; wrapped pristine bytes: `clause_h.pristine.py`.
- Production predicates: `.ufo/waves/round-27/count-c1.py:703-709`. There are **zero** sub/superstring pairs and **zero** cross-row shared-message pairs among all **66** unordered pairs, but exactly **one** normalized frame (`preparation.json:124-154`):

  ```text
  response_format type must be one of "text" or "json_object", but got: \u0000
  ```

- Single-rule controls disable the other six (h) predicates in memory using Python AST nodes (`probe.py:113-146`), without changing scratch bytes. The primary runs use the untransformed extracted function (`probe.py:132-150`).

### Exact mutant and restoration

Only `/fast/scratch/hyaku/kama-r27c/MutFrameLoadBearing/clause_h.py:21-22` was surgically changed with `functions.edit`. The sole behavioral change was adding `False and` to the frame predicate (production lines 707-709):

```diff
-            elif (fr := msg.replace(e["signature"], "\0").lower()).strip("\0 ") and \
+            elif False and (fr := msg.replace(e["signature"], "\0").lower()).strip("\0 ") and \
                     fr == om.replace(oe["signature"], "\0").lower():
```

The edit succeeded. After the expected detector exit 1, the inverse surgical edit succeeded before the restored detector ran. No lane source was edited.

[INFERENCE] For this fixed row shape and synthetic distinct cells, the 1→12 survivor change is attributable to the frame predicate: the input fixture and all other (h) logic were identical. Shared-message matching alone cannot detect distinct signatures in an otherwise identical echo frame. This does not establish robustness against other frame shapes, validate full-counter eligibility, or establish a universal error-echo rule.

## Exact behavioral commands and outputs

Working directory was `/home/vgpnk/Projects/shokunin/kama-shokunin`. Each command below was run as shown. File size, virtual memory, CPU time, process count, and wall time were bounded; no fixture/log output was directed to an imported file or to its own input.

```sh
timeout 20s bash -c 'ulimit -f 1048576; ulimit -v 524288; ulimit -t 15; ulimit -u 4096; exec python3 -I -S /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-27/w1a3/out/MutFrameLoadBearing/probe.py prepare'
timeout 20s bash -c 'ulimit -f 1048576; ulimit -v 524288; ulimit -t 15; ulimit -u 4096; exec python3 -I -S /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-27/w1a3/out/MutFrameLoadBearing/probe.py detect --label pristine --variant full --expect 1'
timeout 20s bash -c 'ulimit -f 1048576; ulimit -v 524288; ulimit -t 15; ulimit -u 4096; exec python3 -I -S /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-27/w1a3/out/MutFrameLoadBearing/probe.py detect --label shared-only --variant shared-only --expect 12'
timeout 20s bash -c 'ulimit -f 1048576; ulimit -v 524288; ulimit -t 15; ulimit -u 4096; exec python3 -I -S /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-27/w1a3/out/MutFrameLoadBearing/probe.py detect --label frame-only --variant frame-only --expect 1'
# After the single scratch mutation:
timeout 20s bash -c 'ulimit -f 1048576; ulimit -v 524288; ulimit -t 15; ulimit -u 4096; exec python3 -I -S /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-27/w1a3/out/MutFrameLoadBearing/probe.py detect --label mutated --variant full --expect 1'
# After exact restoration:
timeout 20s bash -c 'ulimit -f 1048576; ulimit -v 524288; ulimit -t 15; ulimit -u 4096; exec python3 -I -S /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-27/w1a3/out/MutFrameLoadBearing/probe.py detect --label restored --variant full --expect 1'
```

Preparation exited 0 and wrote `preparation.json`; trimmed values: `rows=12`, `pair_count=66`, `substring_pairs=0`, `shared_message_pairs=0`, `distinct_frames=1`.

The three independent pristine/control commands ran concurrently before mutation. Actual detector stdout (trimmed only to omit hashes, which are recorded below):

```text
pristine: variant=full survivors=1/12 expected=1 detector_exit=0
counted_ids=X26-01
rejections={"h:same-message-frame": 11}

shared-only: variant=shared-only survivors=12/12 expected=12 detector_exit=0
counted_ids=X26-01,X26-02,X26-03,X26-04,X26-05,X26-06,X26-07,X26-08,X26-09,X26-10,X26-11,X26-12
rejections={}

frame-only: variant=frame-only survivors=1/12 expected=1 detector_exit=0
counted_ids=X26-01
rejections={"h:same-message-frame": 11}

mutated: variant=full survivors=12/12 expected=1 detector_exit=1
counted_ids=X26-01,X26-02,X26-03,X26-04,X26-05,X26-06,X26-07,X26-08,X26-09,X26-10,X26-11,X26-12
rejections={}

restored: variant=full survivors=1/12 expected=1 detector_exit=0
counted_ids=X26-01
rejections={"h:same-message-frame": 11}
```

Only mutated stderr was nonempty:

```text
DETECTOR FAIL: expected 1 survivors; observed 12
```

Actual command exits were respectively **0, 0, 0, 0, 1, 0** (including preparation first). The detector predicate and logged exit calculation are `probe.py:149-174`.

## Restoration and before/after hashes

Exact byte comparison command:

```sh
timeout 20s cmp /fast/scratch/hyaku/kama-r27c/MutFrameLoadBearing/clause_h.py /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-27/w1a3/out/MutFrameLoadBearing/clause_h.pristine.py
```

Actual output: none; **exit 0**. Restored behavioral detector also exited 0.

| Scratch module state | SHA-256 |
|---|---|
| Before mutation (`pristine.json:26`) | `7732e2918a27a54ee173fc01f608b2ef85ef0c2ae375f2504f75856b0a7f20d0` |
| Mutated (`mutated.json:37`) | `54a24ce1eafe96f1546a4b59b5995f39f3ec9130950b9819307af77da43a8c55` |
| Restored (`restored.json:26`) | `7732e2918a27a54ee173fc01f608b2ef85ef0c2ae375f2504f75856b0a7f20d0` |

Initial input-hash command (exit 0):

```sh
timeout 20s sha256sum /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-27/count-c1.py /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/w2-falsify/out/CriticShortcutRows/shortcut.registry.json /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/w2-falsify/out/CriticShortcutRows/shortcut.receipt.json
```

Final hash command, after the restored detector (exit 0):

```sh
timeout 20s sha256sum /fast/scratch/hyaku/kama-r27c/MutFrameLoadBearing/clause_h.py /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-27/w1a3/out/MutFrameLoadBearing/clause_h.pristine.py /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-27/w1a3/out/MutFrameLoadBearing/mutated.module.py /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-27/w1a3/out/MutFrameLoadBearing/probe.py /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-27/w1a3/out/MutFrameLoadBearing/rows.json /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-27/count-c1.py /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/w2-falsify/out/CriticShortcutRows/shortcut.registry.json /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/w2-falsify/out/CriticShortcutRows/shortcut.receipt.json
```

Its scratch/evidence hashes match the values above. All three read-only input hashes were unchanged from the initial command:

```text
49491b80e4f4ed2a85ab822a52f0b1a0fdb1dee53423e3d43b60ee25d1bf2765  count-c1.py
1b78c8aa0423151b9d84f6ad3cef35de7e5260e5ec869fea764ba5dbcc691b91  shortcut.registry.json
6020a2c39cf698860f64216754925ed623c7225c47871a1644e0c8e6d3d7ac19  shortcut.receipt.json
```

No repository build, test suite, full counter, or live-server verification was run; those would be outside this assigned offline mutation probe.
