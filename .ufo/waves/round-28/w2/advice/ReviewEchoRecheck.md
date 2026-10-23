# ReviewEchoRecheck — falsify Repair 6 (round-28 W2)

Item: `tools/echo-recheck.py` and the `recheck:` line
(`corpus/knowledge/echo-discriminating-counters.md:3`). Verdict: **holds** —
the line describes what the tool does; the tool runs, matches its documented
contract, and leaves no leftover process/port.

## Runs (all under timeout; scratch `/fast/scratch/hyaku/kama-r28/w2/ReviewEchoRecheck/`)

1. Fresh run, explicit port 48351:
   `timeout 300 /usr/bin/python3 tools/echo-recheck.py --out /fast/scratch/hyaku/kama-r28/w2/ReviewEchoRecheck/fresh/echo-recheck-r28.json --port 48351`
   - stdout: `echo-recheck same 6/6`; exit `0` (matches line: "echo-recheck same 6/6" exit 0).
   - Receipt (`echo-recheck-r28.json`): `exit 0`, `same 6`, `total 6`, `differing []`;
     `port 48351`, `port_selection explicit`; `pins` match the three pinned sha256
     (server b6a31a8e…, impl e404b91a…, model 270cba1b…); fixture sha256 per
     request equal baseline `request_sha256` values; server argv exactly
     `llama-server -m …/stories260K.gguf --host 127.0.0.1 --port 48351`.
   - Byte-for-byte replay evidence: req1-plain / req2-firstesc / req3-fullesc each
     recorded `status 400`, `response_sha256` == committed `9ea801fb…` (identical
     153-byte bodies containing the decoded value `echo_sig_9f3a`); req4-control
     200 stable-json projection.
   - Port-closed proof: `shutdown.port_closed` = `{closed: true, connect_exit: 111,
     ss_ltnp_listeners: []}`, `exited true`, `returncode 0`.
   - Writes: only the two documented files under `--out` (`echo-recheck-r28.json`,
     `echo-recheck-r28.json.server.log`); lane untouched.

2. Existing-path refusal:
   `timeout 60 /usr/bin/python3 tools/echo-recheck.py --out <same fresh path> --port 48351`
   - stdout: `echo-recheck cannot-evaluate --out exists: /fast/scratch/hyaku/kama-r28/w2/ReviewEchoRecheck/fresh/echo-recheck-r28.json`; exit `2` (matches line).
   - No overwrite: `stat` mtime unchanged at the first-run time (2026-10-23
     05:58:54 -0300).

3. Leftover check after both runs: `ss -ltnp` shows **no** listener on 48351 or
   48231-48233; our server pid 1738742 exited. (Unrelated peer servers exist on
   other ports 48301/48306/48307/48308/48314 — not from this tool.)

## Findings

- No actionable defect. The line's claims — starts pinned b11755 on 48231-48233
  or `--port`, replays the six live-probe requests byte-for-byte (verified against
  baseline sha before send), prints the three documented verdict/exit pairs,
  proves the port closed, refuses an existing `--out` — all match code and
  observed behavior. The `--port` explicit path and exit-0/exit-2 modes were
  exercised; exit-1 (drift) and auto-selection (48231-48233) were code-inspected
  but not re-executed (bounds allow only my assigned port 48351; drift is already
  evidenced by round-28 repair 6's ExecEchoRecheck run). No leftover process/port
  on our assigned port.

## Residual risk / gaps

- `on-release` cadence is documentation only; no mechanism enforces it (not a
  tool defect).
- Auto-port candidate loop (48231-48233, no `--port`) not run live this seat;
  logic is a simple free-port scan, same server/terminate path as exercised.
- Drift exit-1 path not re-run this seat; code path is `code = 1`, prints
  `echo-recheck drift <ids>` — consistent with the line and with the round-28
  repair evidence.
