# VerifyShonenBox2 — SHONEN.md line 8

## Verdict
**No actionable numerical mismatch**, provided “8 adverse controls rejected” describes the current arm and the explicitly named “frozen” values describe the frozen arm. The evidence records exactly that current-versus-frozen split. If the opening phrase were read as describing the frozen arm, it would be false: that arm has only two `rejected: true` rows, K3 and K7, and K3 is inconclusive.

## Strings and evidence

- Working-tree `/home/vgpnk/Projects/shokunin/kama-shokunin/SHONEN.md:8` wording: **“8 adverse controls rejected: 7 bad server shapes + 1 injected teardown fault; frozen accepted-bad = 6 (5 accepted bad receipts + 1 receiptless escape), with K3 inconclusive”**.
- Frozen receipt `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/runs/controls-frozen.json` reports exactly `"accepted_bad": 6` and `"inconclusive": 1` (also `"good_ok": true`, `"gate_flip_bad": 0`). `jq` over all rows returned: `total_controls=9`; `accepted_bad=6 inconclusive=1 good_ok=true gate_flip_bad=0`; accepted-bad receipt IDs `k1,k2,k4,k5,k8`; receiptless escape `k6`; inconclusive ID `k3`. K6 has `accepted=true`, `escaped=true`, `receipt_written=false`, `tool_exit=4`, `gate_exit=null`; K3 has `inconclusive=true`. Thus the frozen parenthetical’s 5 + 1 = 6, and its K3 qualifier, match the receipt.
- The “8” denotes K1–K8 among the nine total controls (K0 is the good control). In `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/llamacpp-live/controls.py:525-578`, K1–K5 and K7–K8 are the seven bad-server-shape controls; K6 is `kind='inprocess'`, uses `shape='k0'`, and injects `RuntimeError` into teardown (`:558-564`).
- Current-arm cross-check: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/runs/controls-current.json` records `accepted_bad=0`, `inconclusive=0`, `good_ok=true`; K1–K8 each have `accepted=false` and `rejected=true`. This supports reading “8 adverse controls rejected” as the current outcome, not the frozen outcome. By contrast, the frozen rows with `rejected=true` are only K3 and K7; K3 is inconclusive.

## Provenance and limits

The frozen and current run artifacts are from round-17 commit `54a29268e2083caa2b1e0d54ee1e7d90961302f3`. `controls.py` is tracked and its latest change is commit `c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d` (round 18). Lane working-tree tip is `513eba3ba51a142c9936553e3a85918345eb5c4c`, with `SHONEN.md` modified in the working tree. SHA-256: frozen JSON `6eb9f772ac65877ecf0256e74ac6ac41e35939a53312f6e95830492a38565d11`; current JSON `75fd6ca93d423c68ecae57937a0577e308fe1e8d10d0f2f22b298b379ce7a315`; `controls.py` `106dd98b60e066a190ee8fea609e5be99c6b2065b9c5a404e14394ce59b6ffc8`.

This was a static review of recorded artifacts and control definitions; I did not rerun the controls suite. No LSP device was exposed in the available tool inventory, so no LSP status/references/definition/diagnostics were available. No tools were installed. No lane source or index was edited.