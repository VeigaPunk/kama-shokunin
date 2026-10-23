Confirmed one port-already-bound startup fault; its signature reproduced twice, and the final scratch counter counted it.

## Observations

- Fixture pins: `sha256sum ~/.local/bin/llama-server` = `b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804`; model = `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`. Both match the frozen counter pins.
- `ss -ltn | grep -E '4764[4-7]'` produced no output (grep exit 1), so the assigned ports were free before testing.
- The server was launched twice, each after binding/listening on 127.0.0.1 itself. Port 47644: llama-server exit 1; log line `run1.log:4`: `couldn't bind HTTP server socket, hostname: 127.0.0.1, port: 47644`. Port 47645: exit 1; `run2.log:4` contains the same message with port 47645. Both exited inside the 30-second wait. Each launch used `-t 2`.
- Selected 42-byte signature: `couldn't bind HTTP server socket, hostname`. It is verbatim in both logs and is not the request body (startup trigger has no request).
- Base absence: `git grep -F -q -e "couldn't bind HTTP server socket, hostname" 1560e4d8 -- SKILL.md corpus` returned exit 1 (absent).
- Healthy baseline: port 47646 reached `/health` status 200 and returned `{"status":"ok"}`; `healthy.log` has no candidate signature. `llama-server --help` and `--version` both exited 0 and contain no candidate signature. Raw outputs are included below.
- Pinned source fetched fresh on 2026-10-23: [llama.cpp server-http.cpp at 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad, line 517](https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-http.cpp#L517). Located quote (10 words): `couldn't bind HTTP server socket, hostname: %s, port: %d`. `sha256sum` of the fresh fetch and lane snapshot both equals `24ede172e526763567dbe929da5b16250693d7a2e44334ef0126649b6d3f5fdb`.
- Scratch-only check: extracted frozen tip `a23c0e042114016a909eb15173aa6df74b5b7eb0`; added placeholder SKILL/SOURCES rows KAMA-R26-PORTINUSE/S902 and tested the candidate with `args: ["-t", "2"]`. Under the host-wide lock, frozen counter output was `registered 1 counted 1 target 12 met False not-counted []` (exit 0). All checks for this row were true, including `e_error_shown`, `e_signature_seen`, `f_absent_from_baseline`, and `g_distinct`. The full receipt is `out/ExecPortInUse/scratch-counter-receipt.json`.
- Cleanup: ports 47644–47646 and counter ports 47560–47579 were closed after my runs. Earlier `pgrep` showed peer processes on ports 47604, 47624 and 47612; final check showed peer processes on 47655 only (PIDs 3608091/3608097). No process of mine remained.

## Files written

- `.ufo/waves/round-26/w1-build/out/ExecPortInUse/candidates.json` — one entry with requested `id: TBD` and `source.row: TBD`, source file `server-http.cpp`, and `args: ["-t", "2"]`.
- `.ufo/waves/round-26/w1-build/out/ExecPortInUse/RUNS.txt` — commands/results, exit codes, fixture and source evidence.
- `.ufo/waves/round-26/w1-build/out/ExecPortInUse/run1.log`, `run2.log` — complete raw startup logs for the two reproductions.
- `.ufo/waves/round-26/w1-build/out/ExecPortInUse/healthy.log`, `healthy-response.txt`, `help.txt`, `version.txt` — raw healthy and informational outputs/response evidence.
- `.ufo/waves/round-26/w1-build/out/ExecPortInUse/scratch-counter-receipt.json` — final one-row counter receipt.
- `.ufo/waves/round-26/w1-build/out/ExecPortInUse/scratch-counter-output.txt` — pasted counter stdout and exit code.
- `.ufo/waves/round-26/w1-build/out/ExecPortInUse/server-http-704366d-fetched.cpp` — fresh pinned source fetch, byte-identical to the lane snapshot.
- `.ufo/waves/round-26/w1-build/advice/ExecPortInUse.md` — this report.

## Risks and blockers

The candidate deliberately keeps the requested `TBD` id and source-row placeholders for the L1 integrator. Scratch counter evidence used temporary `KAMA-R26-PORTINUSE`/`S902` values only; no lane registry, SKILL.md, or SOURCES.md was edited. One counted row does not meet the overall C1 target of 12; this seat was assigned only this one fault family.
