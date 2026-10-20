VERDICT: partial — the "no 503 observation fails" rule provably fails a healthy server that is ready before the first poll (isolated control pair: sole failed check, tool exit 1, gate INVALID), but 20/20 real b11755 runs on the pinned tiny model saw 24–48 503s (zero runs at 0) inside a ~5.4 ms load window.

# Attack: `loading_envelope_graded`'s zero-observation rule (C2)

Claim under attack: `corpus/lessons/round-17.md:40-42` — "`loading_envelope_graded` over
every stored 503 body" — and the check's own rule, `tools/kama-llamacpp-live.py:140-141`:
"no 503 observed -> fail with {"loading_observed": false} (a real b11755 run shows
dozens)". Question: can a healthy server load before the first successful poll and fail
the run?

Everything below ran in `/tmp/LiveFastLoad-clone` at
`54a29268e2083caa2b1e0d54ee1e7d90961302f3` (`git rev-parse HEAD` exit 0), never in the
lane, with `PYTHONDONTWRITEBYTECODE=1`. No installs, no pacman.

## F1 — The rule is a hard, sole-cause failure, and it is reachable

Code path: the models phase breaks on the first non-503 answer
(`tools/kama-llamacpp-live.py:589`), `loading_503` stays `None`, and the check requires
`receipt.get('loading_observed') is True` (`tools/kama-llamacpp-live.py:1347`). Any failed
check forces producer exit 1 (`tools/kama-llamacpp-live.py:1376`), and the gate rejects a
false check (`tests/llamacpp-live/check-receipt.py:650`, "check {cid!r}: passed is false")
plus an empty evidence set (`tests/llamacpp-live/check-receipt.py:914-915`,
"loading_envelope_graded: no loading_503 body stored, nothing graded").

To prove this is not just dead code, I built an isolated control pair: one synthetic child
(`/tmp/LiveFastLoad-fake.py`, Python HTTP, not llama.cpp) cloned into
`/tmp/LiveFastLoad-fake-loading.py`, serving the same `/health`, `/v1/models`, `/props`,
`/slots`, `/metrics`, ids, probe responses, SIGTERM-0 teardown and ownership in both
arms. The only difference: the "loading" arm answers the exact 503 envelope to the first
40 `/v1/models` requests; the "ready" arm answers 200 on the very first request.

Commands (cwd `/tmp/LiveFastLoad-clone`, both exit codes recorded):

```
python3 tools/kama-llamacpp-live.py --server /tmp/LiveFastLoad-fake-loading.py \
  --model ~/.cache/kama-shokunin/models/stories260K.gguf --model-sha256 270cba1b…256d \
  --alias kama-live-probe --ctx 256 --threads 1 --out /tmp/LiveFastLoad-runs/LiveFastLoad-fake-loading.json
  → tool exit 0; python3 tests/llamacpp-live/check-receipt.py … → VALID, exit 0
  → 11/11 checks, total_503_responses 40, distinct_bodies 1
python3 tools/kama-llamacpp-live.py --server /tmp/LiveFastLoad-fake.py … (same args)
  → tool exit 1; check-receipt.py → INVALID, exit 1
  → failed_checks == ['loading_envelope_graded'] ONLY; observed
    {"loading_observed": false, "total_503_responses": 0, "distinct_bodies": 0}
  → gate: 3 problems, all "no loading_503 body stored, nothing graded"
```

Result: every other check (health body, alias id, owned_by, metrics 501, props alias, both
probes, graceful teardown, port closed, model unchanged) passed identically in both arms.
A server that is healthy on every graded surface but ready before the first poll is
failed **solely** by the zero-observation rule. So the answer to the question is
mechanically **yes** — the rule can fail a healthy server, and the failure is total
(tool exit 1 → gate INVALID), not a warning.

Caveat, stated plainly: the ready-at-birth arm is synthetic. It bounds the rule's
reachability, not a real b11755 observation.

## F2 — Real-server timing: the 503 window is ~5.4 ms wide, first contact already 503

Reading `readiness_loop` (`tools/kama-llamacpp-live.py:505-609`): phase "models" polls with
no sleep on one keep-alive connection; phase "health" starts only after the first non-503.
A missed 503 therefore requires the first *successful* `/v1/models` connect to land after
the model is ready.

To resolve what the receipt's integer-ms `transitions` cannot, I ran the unmodified clone
tool through a scratch wrapper (`/tmp/LiveFastLoad-instr.py`) that logs a monotonic
timestamp per readiness GET (3 runs, tool exit 0 each):

| run | first successful GET | status | first 503 | last 503 | first 200 | 503s | max intra-window gap |
|---|---|---|---|---|---|---|---|
| i1 | 5.88 ms | 503 | 5.88 ms | 11.34 ms | 11.46 ms | 34 | 1.69 ms |
| i2 | 6.02 ms | 503 | 6.02 ms | 11.69 ms | 11.77 ms | 31 | 1.77 ms |
| i3 | 5.77 ms | 503 | 5.77 ms | 11.15 ms | 11.22 ms | 30 | 1.57 ms |

The listener is up and answering the loading envelope at ~5.9 ms; readiness completes at
~11.2-11.8 ms. The observable window is **~5.3-5.7 ms**, not a sub-millisecond sliver.
Within it the client made 30-34 requests despite one ~1.7 ms scheduler gap. Heads-up for
receipt readers: `loading_503.t_ms` is the *first* 503 (6-7 ms) while the `transitions`
503 row's `t_ms` is the *last* (11-12 ms) because repeats overwrite it — the same receipt
shows two different "503 times".

## F3 — 20 fresh runs: min 24 / median 34.5 / max 48, no zero

20 sequential invocations of the clone tool with the lane's own configuration
(`~/.local/bin/llama-server`, b11755, `stories260K.gguf` sha256 `270cba1b…256d`,
`--alias kama-live-probe -c 256 -t 1`). Every invocation: tool exit 0; every receipt:
`loading_observed true`, `distinct_bodies 1`, `bodies_dropped 0`, all 11 checks passed;
`check-receipt.py` VALID exit 0 (20/20).

| total_503_responses per run (r01..r20) | 24, 32, 33, 35, 45, 45, 39, 48, 36, 48, 38, 31, 37, 26, 33, 25, 34, 36, 26, 25 |
|---|---|
| min / median / max / mean | **24 / 34.5 / 48 / 34.8** |
| runs with 0 observations | **0** |
| `loading_503.t_ms` / health-ready `t_ms` | 6-7 / 11-12 |

A separate pilot run (r00) also passed with 24; three more instrumented runs passed with
30-34. Total real observations: 24 consecutive real b11755+stories260K runs, 0 zeros.
The doc's "a real b11755 run shows dozens" is accurate (24-56 including the sibling
evidence `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/live/receipt-1.json`,
`total_503_responses: 42`).

## Margin and residual risk

- Measured margin: the run is red only if the client is blind for the whole **~5.4 ms**
  load window (first contact at ~5.9 ms → ready at ~11.5 ms). The client's observed cadence
  in that window is one request per ~20-200 µs with a worst gap of 1.77 ms; it never
  approached 5.4 ms. With 0/20 zeros, the per-run failure rate is bounded at ~14% by the
  rule of three [INFERENCE: assuming exchangeable runs; the structural requirement is a
  single client deschedule longer than the load window, which host load can produce even
  though it did not here].
- The window scales with model load time. This run uses the lane's smallest model
  (1.17 MB); the 5.4 ms is mostly server init + mmap of a tiny file, so this configuration
  is the *worst* case for the rule. A larger model widens the window (safer).
- The rule's real fragility is upstream, not statistical: any build that answers 200 on
  `/v1/models` before it is ready, or loads the model before `listen()`, fails a perfectly
  healthy server 100% of the time. b11755's listen-then-load ordering
  (`server-http.cpp` L314-325, bound in `source_bindings()`) is what keeps the window open;
  the check depends on that ordering, not on the server being healthy.
- Suggested hardening (advice only, no lane edits): fall back to a receipt field such as
  `loading_observed: false` + "server ready before first poll" as an explicit **exempt**
  outcome when `port_listener_ownership == 'child'` and every ready walk succeeded, or
  lengthen the modeled window by retrying the very first contact when it is 200 but the
  process started < N ms ago. Either keeps the check fail-capable for a server that never
  exposes the envelope while not red-flagging a fast healthy load.

## Limitations

- One host (the busy fleet host), one server build (b11755), one model, warm page cache.
  No cold-cache or forced CPU-contention runs: background jobs are barred to this seat, so
  I could not synthesize a ≥5.4 ms client stall against the real binary.
- The reachability proof uses a synthetic HTTP child, not llama.cpp; it demonstrates the
  rule's consequence, not a real missed window. Cross-check: the sibling
  `.ufo/waves/round-17/falsify/advice/LiveRerun.md` independently confirms 3 real runs with
  46/56/32 503s, consistent with my range.
- No lane file was edited; no `jj`/git write was run. Read-only git in the lane only.

## Cleanup and installs

Installs: none. Scratch removed before finishing: `/tmp/LiveFastLoad-clone`,
`/tmp/LiveFastLoad-runs`, `/tmp/LiveFastLoad-fake*.py`, `/tmp/LiveFastLoad-instr.py`.
Every fake and llama-server child was torn down by the tool; confirmed with
`pgrep -af 'LiveFastLoad-fake'` → none and `ss -ltnp` → no `llama-server` listener before
scratch removal. No registered port (8080, 34113, `registry/endpoint-consumers.tsv`) was
bound or contacted; the tool picked ephemeral loopback ports.
