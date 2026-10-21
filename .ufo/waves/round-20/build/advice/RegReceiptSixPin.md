VERDICT: confirm - the v3 receipt-gate row can take `--expect-install-tree-sha256` with verdict map 0/1/2/3 as drafted; the executed selftest tally is 6 VALID + 1 NOT-EVALUATED, 77 mutations, exit 0 at 37bd4c5; the symlink boundary reproduces (digest unchanged, loader maps the external object).

Scope: draft row text for SKILL.md line 610 (receipt gate, v3). Lane not modified; clone at `/tmp/kama-r20-RegReceiptSixPin/lane` (HEAD `37bd4c5bd456a2f8a54d3312c28495c321715856`, verified by `git rev-parse`, exit 0). Scratch removed after evidence copy. Deliverables: `.ufo/waves/round-20/build/out/RegReceiptSixPin/`.

Tools: none installed. Used existing python3 3.14.8, `/usr/bin/strace`, `/usr/bin/readelf`, `/usr/bin/ldd`.

## Row text (replaces SKILL.md:610)

| Receipt gate | `python3 tests/llamacpp-live/check-receipt.py /tmp/kama-live.json --require-schema v3 --expect-model-sha256 HEX --expect-server-sha256 HEX --expect-server-impl-sha256 HEX --expect-install-tree-sha256 HEX --expect-probe-sha256 HEX --expect-tool-sha256 HEX`; 0 VALID, 1 INVALID (every problem listed; valid JSON that is not an object is INVALID), 2 unreadable or not JSON, 3 NOT-EVALUATED | Require v3 for a current run; explicit schema floor prevents self-declared v1 escaping v3 checks. Six pins identify bytes: model, launcher, implementation library, install tree, probe, tool. `--expect-install-tree-sha256` compares `server.install_tree_sha256`, the sha256 over sorted `name sha` lines of the server directory's depth-1 regular files (`install_tree()`, `tools/kama-llamacpp-live.py:178-202`, `lstat` + `S_ISREG`). Observed bytes, not authentication. Symlinks are neither members nor digested: a retargeted SONAME link (`libllama.so.0`) leaves the pin unchanged while the loader maps the external object. The gate reads only the receipt, never the install directory. The receipt is still self-reported. |

Row-text decisions: keep the 3-column shape; the v1/v2 row (SKILL.md:574) and its selftest counts stay as they are (historical).

## Verdict map (executed, lane 37bd4c5)

Source: docstring Exit block (lines 33-35) and `main()` returns: 2211 unreadable/not JSON, 2236 INVALID (exit 1), 2241 NOT-EVALUATED, 2243 VALID. Each row below was run on the round-18 `live-recovery/receipt-1.json` (schema v3, outcome pass) with the other pins supplied; copies in `out/`.

| case | command result | exit |
|---|---|---|
| six correct pins + `--require-schema v3` | `VALID ...receipt-1.json` | 0 |
| tree pin `0`×64 | `server.install_tree_sha256 6c216313… != expected 0000…` | 1 |
| tree pin `NOTHEX` | two problems: digest mismatch and `--expect-install-tree-sha256 'NOTHEX' is not 64 lowercase hex chars` | 1 |
| path does not exist | `cannot read ...: [Errno 2]` | 2 |
| file content `not json` | `cannot read ...: Expecting value` | 2 |
| file content `[]` | `INVALID ...: receipt is not a JSON object` | 1 |
| `server.install_tree_sha256` null + tree pin | `--expect-install-tree-sha256 given but receipt has no server.install_tree_sha256 digest` | 1 |
| `server.install_tree` = `{}` + copied digest + tree pin | `server.install_tree is empty` | 1 |
| `server` key absent, or `server: null`, or `install_tree: null` | INVALID with listed problems, no traceback | 1 |

Note for the row: the docstring's "2 unreadable / not JSON" does not cover valid JSON that is not an object. That case is exit 1, so the row says so. [EXEC]

## Selftest tally (executed)

Command: `python3 tests/llamacpp-live/check-receipt.py --selftest` in the clone at 37bd4c5, run twice, exit 0 both times. Stdout (verbatim):

    selftest: 6 VALID and 1 NOT-EVALUATED receipts accepted; 77 mutations + unreadable case rejected

Exit: `0`. Transcript: `out/RegReceiptSixPin/selftest-stdout.txt`, `selftest-exit.txt`. Round-19 notes cited 74 mutations (`GatePinFormat.md` T1) and the routed count "76 vs 77". At 37bd4c5 the count is 77. [EXEC]

## Identity boundary (executed; reproduces round-19 TreeCap)

Copy of `/home/vgpnk/.local/opt/llama-b11755` (read-only source) in scratch:
- Producer `install_tree()` (imported from the lane file): 51 members, digest `6c216313a88d71b141bc62f684b8f95c040710ff050801b13521861826785a2c`, equal to receipt-1 `install_tree_sha256`. Exit 0.
- Control: one byte flipped in regular member `libggml-base.so.0.27.0` → digest `10f9b2d2…7f06` (changed). The pin catches regular-file change.
- Retarget: `libllama.so.0` symlink re-pointed to `ext/libllama.so.0.7.0.alt` (original bytes + 64 zero bytes, outside the tree). Digest after = `6c216313…` (unchanged); tree dict equal. Exit 0.
- `strace -f -yy -e trace=openat,mmap ./llama-server --version` (`--version` only, no server): `openat(".../inst/libllama.so.0") = 3</…/ext/libllama.so.0.7.0.alt>`, then `mmap` of fd 3 from the `ext/` object. `--version` exit 0. Evidence: `out/RegReceiptSixPin/strace-fd-resolved.txt`.
- `LD_DEBUG=libs` names only the in-tree path (`calling init: …/inst/libllama.so.0`). Use strace `-yy`, not LD_DEBUG, to show the resolved object.
- Gate on receipt-1 with six pins: exit 0 before and after, since the receipt bytes do not change. [CODE] the gate opens only the receipt path.

Claim wording: "observed bytes of 51 depth-1 regular files; not authentication of execution; SONAME symlinks and system NEEDED libraries are outside the pin." Do not write "install-tree identity" without that qualifier.

## Pins: six, not five

The six pins are model, server launcher, server-impl, install-tree, probe, tool (argparse `check-receipt.py:2184-2191`). The round-19 wording "sixth pin" counts install-tree last. The row lists all six. Round-19 `lifecycle.md` (round-19 appended note) and `lessons/round-19.md:14,53-55` already state the scope.

## Out of scope / carried

- Not drafted here: the separate `install-tree-grid.py` and `citation-provenance.py` registration rows (round-19 routed defect 1).
- Not changed: the historical v1/v2 receipt-gate row at SKILL.md:574 (no tree pin).
- Carried debt: symlink-aware tree pin (hash link name→target or refuse links leaving the tree); producer silent `except OSError: continue` (`tools/kama-llamacpp-live.py:198-199`, GridDefaults R10).

## Commands and exits (ledger)

| command | exit |
|---|---|
| `git clone … && git checkout 37bd4c5…` | 0 |
| `python3 tests/llamacpp-live/check-receipt.py --selftest` (twice) | 0, 0 |
| gate: six pins + `--require-schema v3` on receipt-1 | 0 |
| gate: tree pin zeros / NOTHEX / nonexistent / non-JSON / `[]` / null digest / empty tree | 1, 1, 2, 2, 1, 1, 1 |
| gate: `server` absent / null / `install_tree: null` | 1, 1, 1 |
| producer `install_tree()` on real install dir (read-only) | 0 |
| symlink demo (copy, control flip, retarget) | 0 |
| `strace -f -yy … llama-server --version` | 0 |

Installed: none. Subagents: none spawned. Not run: live llama-server, model download, any lane file edit.
