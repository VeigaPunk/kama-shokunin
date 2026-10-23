# VerifyEchoReceipt — round-29 w2

## Findings

**No actionable defect found. Routed repair 6 is satisfied and committed.** The receipt proves the requested exit-2 refusal on a pre-existing `--out` sentinel, and both static control flow and an independent scratch run support that no server is started by this refusal path.

Evidence:

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/repairs/echo-exit2/receipt.txt` records `lane_tip 35b90184f638ab6a4149092b93143c7a2b873787`, command output `echo-recheck cannot-evaluate --out exists: .ufo/waves/round-29/repairs/echo-exit2/existing.json`, `exit=2`, and identical before/after sentinel hashes `ca3d163bab055381827226140568f3bef7eaac187cebd76878e0b63e9e442356`. It records `llama_server_before: 0` and `llama_server_after: 0`.
- Recomputed `sha256sum` in the lane tree: `existing.json` is `ca3d163bab055381827226140568f3bef7eaac187cebd76878e0b63e9e442356`; `tools/echo-recheck.py` is `ced0ee8976ca0c03e31d17d72d99c7df5b7a6fa315b19f33d873144ca9df2d28`, matching the receipt. The sentinel is `{}` (3 bytes). `git show HEAD:` produced the same committed sentinel hash; `git ls-files` lists both receipt and sentinel. The repair is in commit `513eba3ba51a142c9936553e3a85918345eb5c4c` (the lane's current tip in the observed log); its parent/pre-data control tip is `35b90184f638ab6a4149092b93143c7a2b873787`.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/echo-recheck.py:441-444` checks `os.path.lexists(out)` and returns 2 before entering `evaluate(args, out, doc)` at lines 451-452. That evaluation is where the server startup path is reached. Thus this refusal branch cannot start a server. The fallback race check at lines 466-468 also returns 2 if an output appears later.
- Independent scratch run using `/usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/echo-recheck.py --out /tmp/kama-r29-w2-VerifyEchoReceipt-3/sentinel.json` with a pre-created sentinel printed `echo-recheck cannot-evaluate --out exists: /tmp/kama-r29-w2-VerifyEchoReceipt-3/sentinel.json`, exited 2, preserved SHA256 `44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a`, and created no `.server.log`. Post-run `pgrep -fa llama-server` returned no output (`pgrep_exit=1`). Earlier lane check likewise returned no process (`pgrep_exit=1`).
- `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-28-verifier-spotcheck.md:239-240` specifically asks to commit a receipt for the exit-2 refusal on an existing path, noting only the sentinel had been committed. Both the sentinel and the receipt are now tracked at the repair commit.

## Residual risk and verification gaps

The recorded `llama_server_before/after` values are boundary process checks, not a process trace during the invocation. This is not an actionable gap for this case: `main()`'s early existing-path return precedes all server-starting code, and the independent reproduction also left no server log or process. No additional server run or tools were needed; no tools were installed.