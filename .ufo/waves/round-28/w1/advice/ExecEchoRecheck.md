VERDICT: delivered — the proposed `tools/echo-recheck.py` is a runnable recheck that starts the pinned b11755 server, replays the six round-27 live-probe requests, compares status and response digests with the committed receipt, prints `echo-recheck same 6/6` / `drift <ids>` / `cannot-evaluate <reason>`, refuses an existing `--out`, and proves its port closed. Both required runs printed `same 6/6` (exit 0); the existing-path run was refused (exit 2) with the sentinel file unchanged; a mutated-baseline falsifier produced `drift req1-plain` (exit 1).

# ExecEchoRecheck — runnable replacement for the entry's `recheck:` cadence

Seat: `KamaR28.ExecEchoRecheck`. Claim served: round-27 outside spot-check routed
defect 6 (`corpus/lessons/round-27-verifier-spotcheck.md:280-283`): the
`recheck:` line of `corpus/knowledge/echo-discriminating-counters.md` names a
cadence but no procedure, and `ExecLiveEchoProbe/probe.py` writes over its
committed receipts. Ports 48231-48233 only. No tracked lane file was edited.
Tool installs: **none**. No subagents.

## Files

| role | path |
|---|---|
| proposed tool (L1 copies to `tools/echo-recheck.py`) | `.ufo/waves/round-28/w1/out/ExecEchoRecheck/echo-recheck.py` |
| proposed replacement `recheck:` line | `.ufo/waves/round-28/w1/out/ExecEchoRecheck/proposed-recheck-line.txt` |
| run 1 receipt + server log (auto port) | `.../out/ExecEchoRecheck/run1.json`, `run1.json.server.log` |
| run 2 receipt + server log (explicit `--port`) | `.../out/ExecEchoRecheck/run2.json`, `run2.json.server.log` |
| refusal sentinel (unchanged, sha below) | `.../out/ExecEchoRecheck/refuse-exists.json` |
| drift-falsifier receipt | `.../out/ExecEchoRecheck/falsifier-drift.json` |
| pre-fix diagnostic runs (exit 1, see below) | `.../out/ExecEchoRecheck/prefix-drift-run{1,2}.json(.server.log)` |
| scratch (mutated baseline) | `/fast/scratch/hyaku/kama-r28/w1/ExecEchoRecheck/` |

Tool sha256 `ced0ee8976ca0c03e31d17d72d99c7df5b7a6fa315b19f33d873144ca9df2d28`,
17,803 B. All out-dir files are under 8 KiB.

## What the tool does

- Requires `--out PATH`; refuses with exit 2 when the path (or its derived
  `<out>.server.log`) already exists. The existence check runs **before** pins,
  baseline read, or any server start, so a refusal cannot touch the filesystem.
- Reads the baseline `.ufo/waves/round-27/w1a3/out/ExecLiveEchoProbe/receipt.json`
  (`--receipt` overrides), records its sha256, and verifies that each of the six
  replayed request bodies has the committed `request_sha256` (fixture identity)
  before launching anything.
- Verifies the count-c1.py PINS: `llama-server`
  `b6a31a8e…cd804`, `libllama-server-impl.so` `e404b91a…9b59ed`, model
  `270cba1b…bd256d`; mismatch is exit 2.
- Picks the first free port of 48231-48233 (`--port N` to force one; a busy
  explicit port is exit 2) and launches exactly
  `~/.local/opt/llama-b11755/llama-server -m ~/.cache/kama-shokunin/models/stories260K.gguf --host 127.0.0.1 --port P`
  in a new session, logging to `<out>.server.log`, waiting for `/health` 200
  `{"status":"ok"}`.
- Replays `req4-control`, `req1-plain`, `req2-firstesc`, `req3-fullesc`,
  `req5-altsig-plain`, `req6-altsig-full` byte-for-byte from `probe.py` to
  `POST /v1/chat/completions`, recording status, byte count, response sha256 and
  the response body per request.
- Compares: committed 4xx bodies by exact body sha256 (these are the S137 echo
  responses); the committed 2xx control by status and a canonical projection
  that drops `id`, `created`, `timings`, `choices[].message.content` and
  `usage.prompt_tokens_details` (see the measured trap below). Raw sha256 is
  recorded for every request either way.
- Stops with `SIGTERM` to the process group, then proves closure with
  `ss -H -ltnp` (no line for the port) and a connect attempt (refused); the
  proof is stored in `shutdown.port_closed` and a failure is exit 2 even if the
  requests succeeded.
- Writes the receipt once with exclusive create (`open(..., "x")`); exit 0 when
  all six match, 1 with the differing ids, 2 for any cannot-evaluate.

## Exact commands, outputs, exit codes

All runs used cwd `/fast/scratch/hyaku/kama-r28/w1/ExecEchoRecheck` unless noted.

**Run 1 (auto port):**

```
timeout 300 /usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/w1/out/ExecEchoRecheck/echo-recheck.py \
  --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/w1/out/ExecEchoRecheck/run1.json
echo-recheck same 6/6
EXIT=0
```

Receipt: `port 48231`, `port_selection auto`, argv exactly the pinned four-flag
line above, health 200 `{"status":"ok"}`,
`shutdown {"exited": true, "returncode": 0, "port_closed": {"ss_ltnp_listeners": [], "connect_exit": 111, "closed": true}}`.

**Run 2 (explicit port):**

```
timeout 300 /usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/w1/out/ExecEchoRecheck/echo-recheck.py \
  --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/w1/out/ExecEchoRecheck/run2.json --port 48232
echo-recheck same 6/6
EXIT=0
```

Receipt: `port 48232`, `port_selection explicit`, same argv/health/shutdown
shape, `ss_ltnp_listeners []`, `connect_exit 111`.

**Run 3 (existing path must refuse):**

```
sha256sum refuse-exists.json        # 19c8af8b987b5c64789d9db77935418e51b76801a57f3aeea82764552f085ec0
timeout 60 /usr/bin/python3 echo-recheck.py \
  --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/w1/out/ExecEchoRecheck/refuse-exists.json --port 48233
echo-recheck cannot-evaluate --out exists: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/w1/out/ExecEchoRecheck/refuse-exists.json
EXIT=2
sha256sum refuse-exists.json        # 19c8af8b…5ec0 (unchanged)
ls refuse-exists.json*              # only refuse-exists.json: no server log was created
```

**Extra falsifier (drift path, scratch-mutated baseline):**

```
timeout 300 /usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/w1/out/ExecEchoRecheck/echo-recheck.py \
  --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/w1/out/ExecEchoRecheck/falsifier-drift.json \
  --receipt /fast/scratch/hyaku/kama-r28/w1/ExecEchoRecheck/mut-baseline.json
echo-recheck drift req1-plain
EXIT=1
```

`mut-baseline.json` is a scratch copy of the committed receipt with
`requests.req1-plain.response_sha256` set to 64 zeros; its request shas are
intact, so the fixture check passed and only the mutated request was flagged.

After every run, from the session shell:
`ss -ltnp | grep -E ':(48231|48232|48233) '` printed no line (fallback echo
`SS_LTNP_PORTS_CLOSED`), and `pgrep -af 'llama-server.*4823[123]'` printed
`NO_ECHO_SERVER_PROC`.

## Measured comparison evidence

Committed receipt sha256 `5b82294b2760525f0df46ad9b2683f891711050e73cd7219f4d4cc914ca71e0b`.

| request | status | basis | digest in run1 = run2 = committed |
|---|---|---|---|
| req1-plain | 400 | body sha256 | `9ea801fbea83aef6e0d7bd0f177458d58dd3d542bf4ef42d22a5ed18b9a45a06` |
| req2-firstesc | 400 | body sha256 | `9ea801fb…5a06` |
| req3-fullesc | 400 | body sha256 | `9ea801fb…5a06` |
| req5-altsig-plain | 400 | body sha256 | `9639846954d654fe7ea61d32c4f085c84c46c9d45e35a0342a7c212bbd297dc3` |
| req6-altsig-full | 400 | body sha256 | `96398469…7dc3` |
| req4-control | 200 | stable-json | projection `526227672dae7c610e6aa8bb0e07e0d684644d4707f5a8956499e7231bce2fe9` |

**The measured trap.** The first version of the tool compared the control on
status + projection that dropped only `id`, `created`, `timings` and the sampled
content. Both runs then printed `echo-recheck drift req4-control` (exit 1;
retained as `prefix-drift-run{1,2}.json`). Cause: the committed control reports
`usage.prompt_tokens_details.cached_tokens = 41` (it was probed with
`-c 256 -t 2`), while the round-28 mandated argv reports `0`; the rest of
`usage` (prompt 42, completion 1, total 43) and every other stable field agree.
The prefix-cache counter follows server context/cache state, not the build, so
`usage.prompt_tokens_details` is now an explicit excluded field. The five error
bodies were already byte-identical before that change; only the control moved.

This is a real limit of the committed receipt as a byte baseline: its control
response cannot be reproduced byte-for-byte by any later run (per-run `id`,
wall-clock `created`, timings, sampled token) and its cache counters depend on
the argv used. The tool therefore states its basis per request in the receipt
instead of pretending to compare raw control bytes.

## Proposed knowledge-doc replacement (L1 integrates)

Current line (`corpus/knowledge/echo-discriminating-counters.md:3`):
`recheck: on-release — reopen S137 and re-run the live probe when the installed llama.cpp build changes; S136/S139 180d`

Proposed line (also in `proposed-recheck-line.txt`):

```
recheck: on-release — reopen S137 and run tools/echo-recheck.py --out .ufo/waves/round-NN/echo-recheck-<build>.json (starts the pinned b11755 on a free port in 48231-48233 or --port, replays the six live-probe requests byte-for-byte, prints "echo-recheck same 6/6" exit 0, "echo-recheck drift <ids>" exit 1 or "echo-recheck cannot-evaluate <reason>" exit 2, proves the port closed, and refuses an existing --out so committed receipts are never overwritten); S136/S139 180d
```

It names the server start (the tool's pinned argv), the probe command
(`tools/echo-recheck.py`), a fresh output path (`.ufo/waves/round-NN/echo-recheck-<build>.json`),
and removes the overwrite defect. The `--out` path is deliberately outside the
round-27 probe directory: the committed fixtures stay untouched.

## Risks and limits

- **Pins freeze the build.** A different `llama-server` at the pinned path is
  exit 2, not drift. That is the correct reading of a *recheck of the frozen
  evidence*, but the on-release procedure must update the PINS block and commit
  a new baseline receipt (or add explicit `--binary/--model/--receipt`
  arguments) before it can evaluate a new build. The tool does not fetch or
  rewrite pins.
- **One build, one site, ASCII signatures.** Same limits as the round-27 probe:
  b11755 @ 704366d76, `/v1/chat/completions` `response_format.type`, ASCII
  values. The recheck proves build stability, not that S137 is the only echo
  site.
- **Control comparison is projected.** A change confined to the excluded
  fields (run id, timestamps, timings, sampled content, cache counters) is not
  detected; the receipt lists the exclusions per request. The five S137 error
  bodies are compared byte-for-byte.
- **Baseline integrity only.** The falsifier shows that a wrong committed digest
  becomes `drift`; it does not show that a corrupted baseline fails closed
  (a consistently corrupted baseline and receipt would agree). The committed
  receipt's sha256 is recorded in every run so a later reader can pin it.
- **Lane-absolute paths.** The tool hardcodes the lane receipt and HOME-based
  pins; the integrated copy must remain in this lane's `tools/`.
- Ports: only 48231 and 48232 were served; 48233 was named only in the refusal
  invocation and no server started. All three are closed per `ss -ltnp` after
  every run. Scratch use was confined to
  `/fast/scratch/hyaku/kama-r28/w1/ExecEchoRecheck/` (mutated baseline only).
