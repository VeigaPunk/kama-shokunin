VERDICT: confirm — the 72-row verdict matrix is fully deterministic under 5 sequential reruns and 4 concurrent copies; no row flapped, and the single closed-port row survived concurrent port pressure.

## What I attacked
Claim under test (round-16 build wave, C1): `tests/probe-verdicts/check.py` grades 72 stub/closed-port rows deterministically against `tools/kama-probe.sh`. Failure modes probed: (a) row-level non-determinism across reruns, (b) port-collision fragility when several harness instances run at once — specifically `bind_closed_port()` (check.py:262-270) binds, then *releases* an ephemeral port before the probe connects, a classic TOCTOU where a concurrent process could claim the port and turn refusal into a live connection.

## Commands run (all from `tests/probe-verdicts/`, outputs into /tmp/kama-r16-ExecMatrixDeterminism/, since removed)

Sequential determinism:
```
for i in 1 2 3 4 5; do
  python3 check.py --probe .../tools/kama-probe.sh --json > seq-$i.json 2> seq-$i.err
done
```
Exit codes: seq-1..5 all **0**. Wall time 189.88 s total (~38 s/run).

Concurrent port-collision check:
```
for i in 1 2 3 4; do
  python3 check.py --probe .../tools/kama-probe.sh --json > conc-$i.json 2> conc-$i.err &
done; wait
```
Exit codes: conc-1..4 all **0**. Wall time 37.81 s total — same as a single sequential run, confirming the four harnesses genuinely ran in parallel, each driving 72 probe invocations (~288 probe processes overlapping).

## Evidence

- Every run: `tests: 72, passes: 72, failures: 0`; `probe_sha256` identical across all 9 runs (`6edd3c4cfdf3f86c…`), so no probe drift between runs.
- Row-level comparison: extracted `(verdict, reason, probe_exit, passed, error)` for all 72 rows × 9 runs = 648 graded rows; compared each against the seq-1 baseline → **0 non-deterministic rows** (Python diff over the JSON documents).
- `error` field: empty on every record in all 9 runs — no stub serve faults, no probe timeouts, no unparseable output.
- Closed-port surface: exactly **one** closed-mode row exists in the whole matrix — `AuthAndDead.closed-port-connection-refused`. Across the 9 runs its freshly released port was never reused twice, and it passed every time (probe saw connection refused → expected verdict) including under 4-way concurrency.
- Matrix shape (from seq-1 JSON): 9 families (AuthAndDead 7, EnvelopeShapes 9, ForeignControls 8, LoadingEnvelope 8, LoadingRace 9, NearMissTriple 8, NonLoadingStatuses 7, Overbroad503 8, ReadyControls 8), 17 MODEL_LOADING rows — matches the build-wave manifest.
- `pgrep -x llama-server` after all runs: exit 1 (empty) — nothing left running; I never started a server (not in my item).

## Analysis

- The bind-then-release race in `bind_closed_port()` is real in principle, but the attack surface is one row × ~1 ms window per run; 4 concurrent harnesses did not hit it. Robust in practice, but the race is not eliminated by construction — a busier host could still collide. [INFERENCE] A bind-then-release port can also be claimed by unrelated host traffic; probability is low on an idle loopback.
- Concurrent wall time == single-run wall time confirms the harnesses' ephemeral-port stub servers (`ThreadingHTTPServer` on port 0) never collide — stub-mode rows are collision-free by construction.
- Determinism of verdicts under concurrency also confirms the probe makes no port-independent shared-state mistakes (e.g., no fixed temp files): 288 overlapping probe invocations produced byte-identical grading.

## Limitations

- 9 total runs is a modest sample; the closed-port race has a ~ms window and could still flake under heavier host churn (e.g., a 32-seat wave all running check.py). Not observed here.
- I did not rerun the frozen-probe comparison or `measure.py` (contract forbids measure.py; frozen-probe attack belongs to the LoadingWindowCapture seat).
- No installs were needed; python3 + bash already present. No lane files modified; /tmp scratch removed after extracting the facts above.
