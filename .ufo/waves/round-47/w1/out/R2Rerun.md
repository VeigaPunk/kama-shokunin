# R2Rerun — independent re-measurement of C2 (round 47, lane kama)

Verdict: **reproduced, no defect found in scope** — counter bytes equal the frozen sha256 at the build tip and at the lane worktree; two runs at build tip `3a09a1d93dcc16799cf6c4b48786e6440af134c4` both give `receipts=1 replay=1 tamper=1 newrow=0 rerun_checks=11 met=False` exit 1 (byte-identical to each other and to the L1 dry run, except the started timestamp), matching the expected `newrow=0` before integration; one run at base `172b8ad040d51ce8c011238c1408d4e0b6aa9595` gives `receipts=0 replay=0 tamper=0 newrow=0 rerun_checks=0 met=False` exit 1, exactly the frozen base control.

## Method

- Scratch `S=/fast/scratch/hyaku/kama-r47/R2Rerun` (TMPDIR set to it; removed at the end). One full clone: `git clone /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane` → clone toplevel verified `$S/lane`; clone HEAD `46a924e027f05614558c45ff02bf7a94ca57d3e1` (integration has not landed in the lane yet — `3a09a1d9` is the build commit, `bbcc6dc2` the freeze; `git -C $S/lane log --oneline -4` shows `46a924e0` → `3a09a1d9` → `bbcc6dc2` → `172b8ad0`).
- No tool installs or upgrades were performed (nothing beyond system python3/git was needed).

## Counter byte verification (preregistration.json claims[C2].counter_sha256 = `15408dce5b2f8f5dbe4dd7bacf17ddb0737fcbe480686907f40483273b128b0f`)

- Worktree at clone HEAD: `sha256sum $S/lane/tools/round47-live-replay-audit.py` → `15408dce…128b0f` — **equals frozen**.
- At build tip: `git -C $S/lane show 3a09a1d9…:tools/round47-live-replay-audit.py | sha256sum` → `15408dce…128b0f` — **equals frozen**.
- At base `172b8ad0`: the file does not exist (`fatal: path … exists on disk, but not in '172b8ad0…'`) — expected: the counter was created at freeze commit `bbcc6dc2`, after the base. The base run below uses the frozen worktree bytes with `--tip 172b8ad0…`.

## Runs (counter: `tools/round47-live-replay-audit.py`, read-only on the clone; every line of each run's stdout below)

Run 1 — build tip, exit **1**:
```
receipts=1 replay=1 tamper=1 newrow=0 rerun_checks=11 met=False
tip=3a09a1d93dcc16799cf6c4b48786e6440af134c4 started=2026-10-26T21:27:09.811783+00:00
detail: newrow: no registry row names b11909 and caa8191df159f764fb0160e3d2fc6be008948aee
```
Run 2 — build tip, exit **1**:
```
receipts=1 replay=1 tamper=1 newrow=0 rerun_checks=11 met=False
tip=3a09a1d93dcc16799cf6c4b48786e6440af134c4 started=2026-10-26T21:27:37.463786+00:00
detail: newrow: no registry row names b11909 and caa8191df159f764fb0160e3d2fc6be008948aee
```
`diff` of run 1 vs run 2 stdout: only the `started=` timestamp differs. Both match the L1 pre-wave dry run (`receipts=1 replay=1 tamper=1 newrow=0 rerun_checks=11 met=False`). `newrow=0` is the expected pre-integration state (the b11909 SOURCES row lands at integration), so `met=False` here is correct, not a failure of the claim.

Run 3 — base `172b8ad0…`, exit **1**:
```
receipts=0 replay=0 tamper=0 newrow=0 rerun_checks=0 met=False
tip=172b8ad040d51ce8c011238c1408d4e0b6aa9595 started=2026-10-26T21:27:52.566379+00:00
detail: receipts: .ufo/waves/round-47/c2/live/receipt-1.json absent or not a JSON object at tip
detail: receipts: .ufo/waves/round-47/c2/live/receipt-2.json absent or not a JSON object at tip
detail: receipts: .ufo/waves/round-47/c2/live/receipt-3.json absent or not a JSON object at tip
detail: tools/kama-live-replay.py absent at tip
detail: newrow: no registry row names b11909 and caa8191df159f764fb0160e3d2fc6be008948aee
```
Matches the frozen base control `C2 receipts=0 replay=0 tamper=0 newrow=0 met=False` (controls/base.c2.out) leg for leg. All runs: empty stderr.

## Receipt sanity (cited copies, from `git show 3a09a1d9…:.ufo/waves/round-47/c2/live/receipt-N.json`)

All three receipts: schema `kama-llamacpp-live/v4`, outcome `pass`, `build_info=b11909-caa8191df…`, `teardown.log_path=null`, 11 evaluated checks each, `provenance.server.asset_sha256=bf94332a3001…` (frozen asset digest), `provenance.model.sha256=270cba1bd510…` = `model.sha256` (frozen model digest). The three receipts are byte-identical at the build tip and at lane HEAD `46a924e0` (`cmp` clean ×3), so the copies cited here are the measured bytes. sha256 of the copies: receipt-1 `a4caf311…e80d`, receipt-2 `d36d2941…eb49`, receipt-3 `f3f96151…2b68`.

## Findings

- No defect in the C2 counter or its inputs observed in scope. The replay leg genuinely re-acquired both inputs (counter checks `started_utc ≥ counter start`, server/model sha256 equal to receipt-1's, paths under scratch, 11/11 check-by-check agreement), and both tamper legs refused (exit nonzero, no passing rerun receipt).
- Residual (not a defect): my evidence for the replay/tamper legs is the counter's own legs — the rerun receipt lives under the counter's scratch, which it removes on exit, so I did not inspect it directly. The counter's printed `rerun_checks=11` and the leg booleans are the record.
- Counter absent at base is by design (frozen at `bbcc6dc2`); the base run therefore exercises the frozen counter against a pre-freeze tree, which is exactly what the base control records.

## Files written (absolute)

- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/R2Rerun.md (this report)
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/R2Rerun/c2-build.out (run 2's --out receipt)
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/R2Rerun/c2-build.run1.out (run 1's --out receipt, preserved)
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/R2Rerun/c2-base-172b8ad0.out (base run's --out receipt)
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/R2Rerun/c2-run1.stdout, c2-run2.stdout, c2-base-172b8ad0.stdout
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/R2Rerun/receipt-1.at-build-tip.json, receipt-2.at-build-tip.json, receipt-3.at-build-tip.json

Scratch `/fast/scratch/hyaku/kama-r47/R2Rerun` removed after the report was written.
