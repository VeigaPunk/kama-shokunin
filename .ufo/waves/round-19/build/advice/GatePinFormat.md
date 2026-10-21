VERDICT: partial - the sixth pin rejects consistent regular-file member swaps and refuses every malformed value, but an in-tree symlink retargeted outside the tree passes all applicable pins with a byte-identical receipt while the loader maps the external object.

Scope: `tests/llamacpp-live/check-receipt.py` pin checks, executed in `/tmp/kama-r19-GatePinFormat` (lane not modified). Evidence: `out/format_matrix.tsv` (68 rows), `out/undetectable.tsv` (16 rows), `out/loader-demo/RESULTS.json` and `TRANSCRIPT.json`, command ledger `out/RECEIPT.txt`. Tags: [EXEC] run here, [CODE] read only, [INFERENCE] reasoning.

## The six flags

| flag | receipt field, compare site | refusal sites | one receipt state it cannot detect |
|---|---|---|---|
| `--expect-model-sha256` | `model.sha256` (pre-run hash), 421-423 | 445-451 | [EXEC] `model.path`, `model.arg` and argv `-m` name another GGUF, digest unchanged: exit 0 alone and with all six. [INFERENCE] pre = post digest across an A→B→A swap (producer hashes at 1259, rehashes at 1563; gate compares only those two, 1377-1400). |
| `--expect-server-sha256` | `server.sha256` (launcher), 353-355; basename tie 366-374 | 445-451 | [EXEC] launcher unchanged; `libllama-server-impl.so` and `libllama.so` replaced, tree and impl digests recomputed: exit 0 alone, exit 1 with all six (impl and tree pins). |
| `--expect-server-impl-sha256` | `server.server_impl_sha256`, 400-409; tie to tree only if the row exists, 395-399 | 445-451 | [EXEC] impl unchanged; sibling `libllama.so` replaced, tree recomputed: exit 0 alone, exit 1 with all six (tree pin). Also [EXEC] impl row deleted from tree, digest kept: exit 0 alone. |
| `--expect-install-tree-sha256` | `server.install_tree_sha256`, 384-390; recomputed only if tree is non-empty, 380 | 385-387 (null digest), 445-451 | [EXEC] in-tree SONAME symlink retargeted outside the tree: members, digest and receipt bytes identical; gate VALID before and after with the five applicable pins (model, server, probe, tool, tree). `/proc/self/maps` shows the external object; `ldd` still prints the in-tree path. |
| `--expect-probe-sha256` | `probe.sha256`, 441-443 | 445-451 | [EXEC] both probe records' `argv[1]` names another script; `probe.path` and digest unchanged: exit 0 alone and with all six. No check ties `argv[1]` to `probe.path` (probe-record checks 724-739); producer always sets it (`tools/kama-llamacpp-live.py:742`). |
| `--expect-tool-sha256` | `tool.sha256`, 463-466 | 467-468 (no tool block), 469-471 | [EXEC] `tool.path` names another file; the gate never reads it: exit 0 alone and with all six. |

Format rule, identical for all six: the pin must be exactly 64 characters of `[0-9a-f]` (`is_hex64`). Anything else gives exit 1 with `--expect-X-sha256 'V' is not 64 lowercase hex chars`. The checks at 445-451 and 469-471 are unconditional, so no malformed pin reaches exit 0 [CODE + EXEC]. [EXEC] Uppercase, `sha256:` prefix, trailing `\n`, leading space, 63 chars, 65 chars, non-hex, and empty, across all six flags: 54 refusals, all exit 1; the six exact matches exit 0. A null receipt digest, or a missing tool block, with a pin: exit 1 ("given but receipt has no ...").

argparse layer (outside the gate's exit contract) [EXEC]:
- Missing value → exit 2; ambiguous `--expect-server` → exit 2. Exit 2 is also the documented "unreadable / not JSON" code (docstring lines 33-34).
- Abbreviation `--expect-install-tree` is accepted silently (exit 0).
- Repeated flag: the last value wins silently (bad-then-good exit 0; good-then-bad exit 1).

## Gate and producer findings beyond the six

- G1 [EXEC] `server.install_tree = {}` with `install_tree_sha256` copied from the pin passes all six pins (exit 0). The recompute (380) and basename tie (369-372) skip on an empty map. The producer emits `({}, e3b0...)` for an empty listing [EXEC], but a completed run hashes the server first (1267), so that shape needs a race or an edited receipt [INFERENCE].
- G2 [EXEC] No `argv[1] == probe.path` check (row 5).
- G3 [EXEC] The impl tie is conditional on the row's presence (395-397) (row 3).
- G4 [CODE] The gate reads only the receipt (2193). Every pin binds a string, not bytes; rows 1, 5 and 6 are undetectable for that reason.
- P1 [EXEC] `install_tree()` uses `lstat` and `S_ISREG` (191-195), so symlinks are neither members nor digested. This is the row-4 state: demo `libdemo.so.0` → `libdemo.so.0.1`, retargeted to `../../ext/libdemo-evil.so.0.1`; `demo_id` goes from IN-TREE to EXTERNAL.
- P2 [EXEC] Unreadable regular members are dropped silently (196-199). A chmod-000 member is absent from the tree, and the digest equals that of the readable subset. `run.py:57` takes its tree pin from the same function, so a pin taken in that state binds the reduced set [INFERENCE on timing].
- P3 [CODE] The impl digest uses `os.path.isfile` (1271-1272), which follows symlinks, while the tree excludes them. The impl pin can cover a file absent from the tree digest. Not executed.
- P4 [CODE] Time-of-check gaps: model hashed at 1259 and rehashed at 1563; probe hashed at 1273 and run later; tool hashed at 1304, after Python has loaded the code. Races not executed [INFERENCE].
- T1 [CODE + EXEC] `--selftest` exits 0 (74 mutations), but has no negative case for `--expect-server-sha256` or `--expect-probe-sha256` and no malformed-pin case. `install-tree-grid.py` mutates three regular `.so` members at receipt level only; no symlink case exists under `tests/llamacpp-live/`.
- Stale comment at line 453 says LiveHarness adds the tool block "after the fact". The producer always writes it (1233) and hashes it during the run (1304).

## Effect on the lane's C2 claim [INFERENCE from the rows above]

- Confirmed for regular members: consistent swaps are rejected once the tree pin is present (rows 2-3, all six → exit 1).
- Not covered: SONAME symlink retargets and the loader's resolution. The grid cannot see either. Sibling advice grepped during this run (CritC2Inflation, GateTreeBaseline R2, LdsoOrigin) records the same symlink gap; I did not open their artifacts.

## Recommendations

1. Tree: refuse symlink members or digest them (`readlink` plus `realpath`, required to stay inside the tree). Make `install_tree()` raise on an unreadable member. Or record realpaths of loaded objects (`/proc/<pid>/maps`) and bind them to the tree.
2. Gate: recompute the tree digest whenever it is hex (an empty map must fail). Require the impl row when the impl digest is hex. Require `argv[1] == probe.path`. Add negative selftests for the server and probe pins and for malformed pins. Reject repeated `--expect-*` flags and disable abbreviation.
3. Separate argparse usage errors from the documented exit 2.
4. Pins are opt-in: a subset invocation accepts what the omitted pins would catch (rows 2-3). Keep run.py's all-six call and state that in the docstring.

## Limits

- No real llama-server or GGUF was run. The loader demo is a synthetic install (llama-server plus one SONAME library), built with gcc.
- A→B→A and the other races were not executed.
- No installs or updates; only present tools were used (gcc, readelf, ldd).
- The lane was not modified except this report.
