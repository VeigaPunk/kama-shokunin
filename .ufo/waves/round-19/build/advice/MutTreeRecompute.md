VERDICT: confirm - receipt-tree-sha reuse mutant killed by the no-pin control; the pin-only rejection aggregate survives.

Axes: operability; calibration (lowest assigned: 7). One isolated mutation only; no official measurement.

Mutant: in `/tmp/kama-r19-MutTreeRecompute/tests/llamacpp-live/install-tree-grid.py:88-89`, replace recomputation with `mutant["server"]["install_tree_sha256"] = base["server"]["install_tree_sha256"]`.

Expected detector: existing no-pin/pin pair against the archived receipt-1, three named library swaps. Both receipt baselines must remain VALID; no-pin must reject 0/3 (grid exit 1), pin must reject 3/3 (grid exit 0). Cases run concurrently, bounded to 60 seconds each; phase changes only the evidence label.

Executed commands (outer detector exits):
- `python3 /tmp/kama-r19-MutTreeRecompute/out/detector.py --phase pristine` — exit 0.
- `python3 /tmp/kama-r19-MutTreeRecompute/out/detector.py --phase mutated` — exit 1.
- `python3 /tmp/kama-r19-MutTreeRecompute/out/detector.py --phase restored` — exit 0.

| Bytes | No-pin stdout / grid exit | Pin stdout / grid exit |
|---|---|---|
| Pristine | baseline=VALID, rejected=0/3 / 1 | baseline=VALID, rejected=3/3 / 0 |
| Mutated | baseline=VALID, rejected=3/3 / 0 | baseline=VALID, rejected=3/3 / 0 |
| Restored | baseline=VALID, rejected=0/3 / 1 | baseline=VALID, rejected=3/3 / 0 |

All three no-pin member cases kill it: `libggml-base.so.0.27.0`, `libllama-common.so.0.7.0`, `libllama.so.0.7.0`. Each mutated gate output reports `server.install_tree_sha256 != recomputation over install_tree members`. Thus retaining the no-pin control matters: pinned 3/3 alone does not distinguish internally inconsistent fixtures from consistent swaps.

Restoration: exact reverse edit; bytewise `cmp` plus SHA-256 command exit 0. Grid hashes: pristine/restored `467d44d89685afcf4dc47d46fe82c09dd734f9194214d731326767709dcf902e`; mutated `f531aedb8514ebc339f96c90ad1e097ce42b5efb61943c6c673dc769d3339d86`. Gate, receipt and detector hashes stayed identical across phases.

Full exact commands, child exits/stdout/stderr, hashes and restoration evidence: `/tmp/kama-r19-MutTreeRecompute/out/receipt.json`, `/tmp/kama-r19-MutTreeRecompute/out/pristine.json`, `/tmp/kama-r19-MutTreeRecompute/out/mutated.json`, `/tmp/kama-r19-MutTreeRecompute/out/restored.json`. Reproducer and pristine bytes are retained in that OUT directory.

No installs, server/listener starts, runtime invocation or lane source/state edits; the requested advice file is the sole lane write. Pins are fixed archived-receipt identities; producer pin acquisition was not measured.
