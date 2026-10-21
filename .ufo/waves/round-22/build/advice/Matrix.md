# Round 22 install-tree I/O matrix

Lane: `/home/vgpnk/Projects/shokunin/kama-shokunin`.

## Owned implementation

Created `tests/llamacpp-live/install-io-grid.py` in the independent sandbox clone at `.ufo/waves/round-22/build/sandboxes/Matrix/`. Only that assigned implementation path was changed in the clone; no lane production file or sibling-owned path was edited. The script accepts `--arm frozen|current|both`, `--json`, and `--selftest`; it does not launch a server or depend on host permission changes. The injected fault rows count the exact operation and require its injected exception to be raised before a refusal can count. A returned tuple, including `(tree, None)`, is an escaping identity; refusal requires `SetupError.code == 'install-tree-unpinnable'`. Unconditional refusal is exposed as an injection-not-reached error and also fails the named positive controls.

## Frozen evidence and committed oracle

Frozen producer revision: `10271460cc575fc2280aa831e442726385fc2319`.

Frozen `tools/kama-llamacpp-live.py` SHA-256: `cec679495591cf2410334dfe08c648e310f23825181dcbae7d13b911c980e023` (measured from the independent clone, matching the pinned blob).

The literal 16 fault IDs in the script cover listdir PermissionError/OSError; lstat PermissionError/FileNotFoundError/OSError independently on server and library; and `sha256_file` PermissionError/FileNotFoundError/IsADirectoryError/OSError independently on server and library. Every current-arm fault expects typed refusal. Frozen-arm rows provide the red-before control. The two positive controls pin the exact regular-file map and tree digest, both without ignored entries and after adding a symlink plus a populated subdirectory:

- `llama-server` → `ba28c4bd990ab8de10ba4e075aaaf1898cf6f8d1c8f9de965e86dd577d8ccf31`
- `libllama.so.0.7.0` → `15bc1cbc5801222026914454b05098f5ca16e34b7c383cb670a857be904c889b`
- combined digest → `a0d631033a76ada09e9fabdb2301c608dbe5f56af0e16d1ae6217065d98c105f`

## Checks and blockers

No matrix/selftest, build, lint, formatter, or smoke command was run, per wave instructions. No tools were installed. LSP was unavailable in the exposed tool inventory. No implementation blocker identified; L1 should run the matrix after integrating the producer and test file.

## Append-only resumed-turn correction

The initial two-member/two-control sandbox draft and this report were delivered before a terminal-capacity failure; the parent later resumed the same Matrix identity and directed completion of the sandbox draft only. This addendum supersedes earlier control-population and digest statements above. L1 has integrated a separate matrix in the lane checkout; I did not touch lane production or that integration.

The sandbox draft is now `tests/llamacpp-live/install-io-grid.py` under `.ufo/waves/round-22/build/sandboxes/Matrix/`. Its current arm requires explicit `--producer PATH` and never implicitly reads `LANE/tools/kama-llamacpp-live.py`; frozen remains pinned to `10271460cc575fc2280aa831e442726385fc2319`, source SHA-256 `cec679495591cf2410334dfe08c648e310f23825181dcbae7d13b911c980e023`. It records the injected cause/errno, returned map keys and digest, and independently classifies null-digest versus self-consistent partial escapes. `IsADirectoryError` uses `(EISDIR, os.strerror(EISDIR), path)`. Missing injection activation with passing controls is exit 2; an evaluated non-refusal or named control mismatch is exit 1. Exact refusal token is `SetupError.code == 'install-tree-unpinnable'`, per ApiFix's confirmed interface.

Fault IDs remain the literal 16 rows: `listdir:permission`, `listdir:oserror`; `lstat:server:{permission,missing,oserror}` and `lstat:library:{permission,missing,oserror}`; `read:server:{permission,missing,isdir,oserror}` and `read:library:{permission,missing,isdir,oserror}`. The IsADirectory library victim is `libmtmd.so.0.4.0`; fault calls are direct `install_tree` calls, not producer e2e.

Three isolated exact-tuple controls now run on both arms: `control:complete-map-digest`, directory-only `control:subdir-member-skipped` with populated `openvino-licensing/LICENSE.txt`, and symlink-only `control:symlink-member-skipped`. The four regular fixture members and independent per-file SHA-256 pins are `llama-server` → `ba28c4bd990ab8de10ba4e075aaaf1898cf6f8d1c8f9de965e86dd577d8ccf31`, `libllama.so.0.7.0` → `15bc1cbc5801222026914454b05098f5ca16e34b7c383cb670a857be904c889b`, `libllama.so.0.7.1` → `bc80a92210a4483f4ddb7691d71475caaeaf827776b3b7f80cd36a1a789a083b`, and `libmtmd.so.0.4.0` → `51ae5bca00ba86fc93551e10ff0322b2eb13098c03fc47ff28183e11b166a0d3`. The pinned combined digest is `6d17af2a31e5fcf7e42e2abbb0bead8e9b79a2361f8d8dd0f286c11909277469`.

No matrix/selftest or other verification was run during the build wave. No tool was installed. The parent owns post-integration verification.

## Static comparison with L1's lane-integrated matrix

Read-only inspection only; no test or producer execution occurred. The integrated `tests/llamacpp-live/install-io-grid.py` uses a broader oracle (18 fault rows including listdir-missing and late-read, plus propagation and additional controls). This sandbox draft stays to the assigned 16 listdir/lstat/member-read I/O rows and three isolated exact-tuple controls, with an explicit `--producer` path.

One integration risk requires reconciliation before L1's gate: the integrated matrix stores `SetupError.code` in `result['reason']` and requires a colon-suffixed stage/member prefix. ApiFix confirmed its stable `.code` is the bare `install-tree-unpinnable` token, with diagnostic detail separately preserved. Under that confirmed interface the integrated matrix's current refusal predicate is statically incompatible and would classify expected typed refusals as failed rows. This is a source-level finding, not a behavioral result; L1 owns any lane-side reconciliation.

The frozen revision/source and fixed fixture SHA-256 values above were obtained through read-only revision/hash calculations. No producer, matrix, or selftest command was executed.
