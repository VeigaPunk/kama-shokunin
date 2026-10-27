Verdict: One actionable receipt-compatibility defect; other reviewed launch mechanics have no identified defect.

## Finding — high: fd-mode receipts are rejected by the committed receipt checker

At build `5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8`, `tools/kama-llamacpp-live.py:1957` adds `LD_LIBRARY_PATH` to `child_env`; line 1962 records all child environment names in `receipt['child_env_keys']`. The unchanged `tests/llamacpp-live/check-receipt.py:634-645` rejects every key not in `CHILD_ENV_ALLOWLIST` (`PATH`, `HOME`, `LANG`, `LC_ALL`, `TMPDIR` at line 65). Thus an otherwise successful `--server-fd` run emits a receipt that the lane's receipt checker rejects. `--selftest` at this commit passed but only validates its existing selftest receipt/mutation matrix; it does not include this new producer key.

Evidence: `python3 /fast/scratch/hyaku/kama-r52/V2Review/check-receipt.py --selftest` → exit 0, `selftest: 16 VALID and 1 NOT-EVALUATED receipts accepted; 107 mutations + unreadable case rejected`. Static evidence: producer lines 1952-1962; checker lines 633-648. LSP device/status was unavailable in this seat's tool inventory, so caller/definition checks used literal source inspection; this is not semantic-reference proof.

Proposed fix (not applied): update the checker allowlist to admit `LD_LIBRARY_PATH` (its recorded name only, never its value), and add a selftest case exercising a receipt with the fd-mode environment key. The change must land alongside the producer change so emitted receipts are consumable.

## Reviewed without further findings

- `--server-fd` is optional `int` parsing (`tools/kama-llamacpp-live.py:1479`); fd validation occurs before `Popen` at 1955-56. `sealed_fd` checks regular-file type, all four required seals, size, and SHA-256 (`786-808`).
- `server_argv` is constructed as `[server_real, '-m', args.model, ...]` at 1935-44; therefore index 2 is the model value in the only construction path. Receipt argv is recorded after the absolute-path replacement (`1945`, `1961`), satisfying the checker’s model/`-m` consistency rule (`check-receipt.py:663-666`).
- `cwd` and `LD_LIBRARY_PATH` are added only for fd mode (`1952-61`, `1993-97`), preserving legacy launch behavior.
- `Popen(executable=...)` points to the live parent's fd path while argv[0] remains the server path (`1993-99`). This makes `/proc/<child>/cmdline` argv[0] the server path; Linux comm is based on executable basename rather than that preserved argv[0]. The checked `kama-probe.sh` source contains no process-comm/cmdline inspection; its contract is endpoint probing. No comm/cmdline dependency was found in the review scope.
- `server_exe` reports `seals` and `nlink` (`768-771`); replay's own identity check consumes those values. `check-receipt.py` does not validate the new `server.fd` or `server_exe` fields; its selftest is not evidence of that contract. This is not a separate defect because the replay/counter provide the relevant consumer check.

No server was started by this review. No tool was installed.