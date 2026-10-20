VERDICT: confirm — llama-server b11755 exits `returncode 0` on SIGTERM/SIGINT/single/double/group delivery in 25/25 runs (exit ≤10.1 ms); `returncode == 0` is the right `teardown_graceful` expectation but cannot alone prove harness-initiated SIGTERM.

# ProbeSigtermExit — signal-exit behaviour of `llama-server` b11755

Findings file (full data): `.ufo/waves/round-17/build/drafts/probe-sigterm-exit.md`
sha256: see end of this report.

## Method

Spawning the installed `~/.local/bin/llama-server` (→
`~/.local/opt/llama-b11755/llama-server`, `version: 0.7.0-dev (build 11755,
commit 704366d76)`) with the fixture
`~/.cache/kama-shokunin/models/stories260K.gguf` and argv `-m <model>
--alias kama-probe-x --host 127.0.0.1 --port <ephemeral> -c 256 -t 1`.
Fresh `bind(0)` port per run — nothing in `registry/endpoint-consumers.tsv`
touched (8080, 34113 untouched). 5 runs each of: (a) SIGTERM once ready,
(b) SIGINT once ready, (c) SIGTERM at first port-accept, (d) two SIGTERMs
10 ms apart, (e) SIGTERM to the process group (`start_new_session` +
`killpg`). Python `subprocess` + `os.killpg`; 15 s exit timeout with SIGKILL
fallback (never needed). One server at a time; post-run `ss -ltnp` /
`pgrep -af llama-server` clean.

## Results (all runs)

- (a) SIGTERM ready: **rc 0 ×5**, exit 3.1–3.2 ms
- (b) SIGINT ready: **rc 0 ×5**, exit 3.1–3.2 ms
- (c) SIGTERM at port-accept: **rc 0 ×5**, exit 1.1 ms
- (d) SIGTERM ×2 (10 ms): **rc 0 ×5**, exit 10.1 ms
- (e) SIGTERM→pgid: **rc 0 ×5**, exit 3.1 ms

stderr shutdown marker, identical in all 25 runs:
`I srv    operator(): operator(): cleaning up before exit...` — exactly one
shutdown line; no other signal/termination text.

## Advice for C2 `teardown_graceful`

1. `returncode == 0` matches observed graceful exit on every signal
   combination tested; pair it with `sigterm_sent && !sigkill_sent` and a
   `term_wait_ms` bound (≥100 ms; observed max 10.1 ms).
2. rc 0 does NOT distinguish SIGTERM vs SIGINT vs spontaneous exit — the
   harness's own signal record is the discriminator, per the round-16
   `ReviewLiveHarnessCode.md` defect.
3. stderr literal `operator(): operator(): cleaning up before exit...` is a
   stable optional marker of a graceful-exit path.

## Limitations

- Case (c) could not stage true "SIGTERM during loading": with the 1.2 MB
  fixture the socket only accepts after `model loaded`/`listening` (~20 ms),
  so the measurement is post-listen, pre-/health-200. True loading-state
  needs a slower load. [INFERENCE]
- Single small model/host; larger models may change latency. [INFERENCE]
- No nonzero returncode observed in any run.

## Installs

None — stock `python3` 3.14.8 only. Pacman pause respected.

## Files written (this seat)

- `.ufo/waves/round-17/build/drafts/probe-sigterm-exit.md`
- `.ufo/waves/round-17/build/advice/ProbeSigtermExit.md`

sha256 below.
