# A07ConcurrentRuns — round 60 w1, C1 falsification: isolation under concurrency

Seat: A07ConcurrentRuns (leaf, no subagents). Axes: operability (judged); calibration=7 noted as lowest assigned, not attacked here.
Tip: `e0b5b1ead9adb7a5a4744caca8837ec6496e1ca1` (verified: `git -C <lane> rev-parse --verify e0b5b1ea…^{commit}` → rc 0).
Date: 2026-10-27 18:40–18:47 -03:00. Tool installs/updates: none (no tooling-directive record to make).
Scratch used: `/fast/scratch/hyaku/kama-r60/A07ConcurrentRuns/` (removed before this report's hand-off; receipts first copied to `./` sibling dir `A07ConcurrentRuns/`).

## What ran (exact commands)

Wave 1 — five processes launched in the same instant (one bash driver, `run_one` wraps each with rc/elapsed capture; all `&`):

```
python3 tools/kama-ollama-live.py --work $S/w1 --nonce a07alpha12 --out $S/w1/receipt.json
python3 tools/kama-ollama-live.py --work $S/w2 --nonce a07bravo13 --out $S/w2/receipt.json
python3 tools/kama-ollama-live.py --work $S/w3 --nonce a07charli4 --out $S/w3/receipt.json
python3 tools/kama-ollama-live.py --work $S/w4 --nonce a07shared5 --out $S/w4/receipt.json
python3 tools/round60-c1-counter.py --repo <lane> --tip e0b5b1ead9adb7a5a4744caca8837ec6496e1ca1 --work $S/counter-root
```

Correction recorded: in wave 1 the intended same-nonce pair was NOT same-nonce (w1=`a07alpha12`, w4=`a07shared5` — my scripting error). The same-nonce/different-`--work` leg was re-run cleanly as the f-leg:

```
python3 tools/kama-ollama-live.py --work $S/f1 --nonce a07shared5 --out $S/f1/receipt.json
python3 tools/kama-ollama-live.py --work $S/f2 --nonce a07shared5 --out $S/f2/receipt.json   # same nonce, concurrent
```

Kill falsifiers (event-driven; server pid found via `/proc/<pid>/environ` containing the seat scratch path — only own PIDs killed):
- server-SIGKILL at listen (+0 s, +0.3 s, +0.8 s variants): victim d2/e2/g2 vs survivor d1/e1/g1;
- harness-SIGKILL: `kill -9` on the d3 python harness while its server was listening; survivor d4.
- `free_port()` TOCTOU probe (`toctou.py` in scratch, receipts copied): 8 processes × 10 rounds replicating the tool's exact `free_port()` (bind 0 → close → exclude {8080,34113}+listeners), then a 0.25 s pick→bind gap.

## Results

Wave 1 (all five concurrent; driver total wall 7.64 s; sampler saw up to 7 simultaneous ollama listeners — my 4 + counter's internal run1 (port 50049, pid 2161830) + 2 pre-existing other-seat servers on 33657/33475, all distinct ports):

| run | port | nonce | verdict | exit | harness elapsed |
|-----|------|-------|---------|------|-----------------|
| r1/w1 | 44587 | a07alpha12 | MODEL_OK | 0 | 7.42 s |
| r2/w2 | 50613 | a07bravo13 | MODEL_OK | 0 | 7.38 s |
| r3/w3 | 58407 | a07charli4 | MODEL_OK | 0 | 6.90 s |
| r4/w4 | 37665 | a07shared5 | MODEL_OK | 0 | 6.70 s |
| counter | (internal run1: 50049) | internal | met=True | 0 | <7.64 s |

Counter stdout (exit 0), raced against the four live runs:
`tool_present=1 live_ok=1/1 fake_rejected=2/2 stale_rejected=1/1 tamper_rejected=3/3 log_rejected=1/1 errors=0 met=True`

All four serve.log "Listening on 127.0.0.1:<port> (version 0.40.11)" lines carry the same timestamp 18:40:41.426 — four servers bound within one millisecond on distinct ports. Port collisions: **0** across 6 concurrent picks (4 + counter + 2 foreign listeners already held).

f-leg (same nonce `a07shared5`, different `--work`, concurrent): f1 port 47571 / f2 port 50095, both MODEL_OK exit 0; each `/api/tags` holds exactly ONE entry `kama-a07shared5:latest` and `/api/ps` the same digest `8cf91c7109e77999ac0ae6e6eab27dfea00d9f83ffbe4559a3f26266e455c792` — same name+digest in two disjoint stores, no cross-talk.

Kill falsifiers:

| phase | action | victim | survivor |
|-------|--------|--------|----------|
| a | SIGKILL d2's server at listen | FAIL, rc 1, `fault=RuntimeError: not-ready`, failed=[ready], teardown.returncode=-9 | d1 MODEL_OK rc 0 |
| c | +0.3 s after listen | e2 FAIL rc 1 (ready) | e1 MODEL_OK rc 0 |
| g | +0.8 s after listen | g2 FAIL rc 1 (ready) | g1 MODEL_OK rc 0 |
| b | SIGKILL d3's harness python | rc 137, **NO receipt** (`--out` never written); its ollama child pid 2330820 ORPHANED: still LISTENING on 127.0.0.1:55273, answered `GET /` → 200 "Ollama is running" and `GET /api/tags` → 200 `{"models":[]}` | d4 MODEL_OK rc 0 |

The b-phase orphan was killed by this seat only (SIGTERM sufficient; listener closed; attribution via environ scratch-path match). All three server-kills landed inside the harness's ready window — ollama 0.40.11 needed >0.8 s on this loaded host before `GET /` answered, so the post-ready failure mode (create/generate/ps flip) was not observed; the victim always failed loudly at `ready` with `teardown.returncode=-9`.

TOCTOU probe (`toctou-probe.txt`): `workers=8 rounds_each=10 total_picks=80 bind_failures=0 duplicate_picks=0` — the window exists in code but was not triggered at this scale, on top of 6 real concurrent picks with 0 collisions.

Cross-reference check: no w1–w4 receipt contains any sibling's nonce or port string (`sibling_references= none` for all four).

## Answers to the item's demanded records

- **Ports chosen**: 44587, 50613, 58407, 37665 (wave 1), 47571+50095 (f-leg), counter's internal run1 50049 (observed in sampler; counter deletes its work dir so the port is only externally observable), kill waves 50427/35503/52595/60815 (d1/d2/d3/d4), 51243/49149 (e1/e2), 41861/33365 (g1/g2).
- **Verdicts / exit codes**: every unharassed run MODEL_OK, exit 0 (9 receipts: w1–w4, f1–f2, d1, d4, e1, e2… plus victims FAIL rc 1; counter met=True rc 0). SIGKILLed harness: rc 137, no receipt.
- **Port collisions**: none observed (6 concurrent live picks + 80 probe picks).
- **Shared state**: writable state is fully per-run — `HOME`, `OLLAMA_MODELS`, serve.log, Modelfile, evidence-*.json all live under each run's own `--work` (child_env builds a fresh env; shell OLLAMA_* cannot leak). The model-store hint resolves as: the store path is per-work, so identical nonces in different works are isolated (f-leg proves it). What IS shared: read-only pins — the 40.8 MB pinned binary (exec'd/mmap'd by up to 7 servers at once), the fixture GGUF `~/.cache/kama-shokunin/models/stories260K.gguf` (hashed by every harness, read by every `ollama create`), pin TSV, `/proc/net/tcp`; and the contended ephemeral loopback port space. Residual shared-state hazard NOT exercised (outside the assigned matrix): pointing two instances at the SAME `--work` would share one store — concurrent `ollama create` of the same-named model would race blob/manifest writes.
- **Elapsed seconds**: wave 1 per-run 6.70–7.42 s under 5-way load; wall 7.64 s. f-leg 6.59/6.22 s. Kill-wave survivors 1.48–6.54 s. Victims failed at 0.83–1.64 s.
- **Verdict dependence**: none observed. Structurally, every check reads only its own port/pid/work (no receipt references a sibling; survivors stayed MODEL_OK across four sibling SIGKILLs). The only theoretical coupling is the `free_port()` TOCTOU: a loser of the port race would pass `ready` against a foreign server and then fail `listener-owned` — i.e. it fails loudly, it cannot pass while entangled. Not triggered here.

## Findings

**MEDIUM (operability, abnormal termination): SIGKILL/OOM of the harness leaks a live lane-owned Ollama server with zero trace.** Evidence: phase b — harness pid 2330778 SIGKILLed at 18:43:43; its child pid 2330820 kept serving `200 "Ollama is running"` on 127.0.0.1:55273; `d3` produced no receipt at all (`--out` is written only at finish). Mechanism: the child is spawned `start_new_session=True` (detached) and teardown lives only in the harness's `finally` (`tools/kama-ollama-live.py:407-418`); there is no parent-death guard (no `prctl(PR_SET_PDEATHSIG)`, no watchdog). Consequence under concurrency: an unowned, unauthenticated, receipt-less server holds an ephemeral port indefinitely and no counter/control can see it. Fix-shaped suggestion (not applied): `preexec_fn` setting PDEATHSIG, or a `--parent-pid` watchdog thread in the child, or writing the receipt incrementally. Within the freeze's stated limits (one lane-owned child torn down per run) the claim is untouched — this is the crash path outside it.

**LOW: `free_port()` TOCTOU window** (`tools/kama-ollama-live.py:71-81`): the candidate socket is closed before the listening-ports recheck and the server binds much later (two sha256 of the 40 MB binary + spawn in between). Empirically clean (0/80 probe, 0/6 real concurrent picks; Linux avoids immediate ephemeral reuse), and a collision fails safe (`listener-owned`/`ready`), so this is a documented race, not an observed defect.

**INFO: read amplification scales linearly with concurrency** — each run hashes the 40.8 MB binary twice (file + `/proc/<pid>/exe`) plus the GGUF; 5 concurrent runs ≈ 400 MB of hashing. Negligible on this host; relevant only if a wave ever scales to dozens of parallel seats.

**INFO: `SIGTERM`-of-server mid-run produces verdict FAIL (rc 1) with `teardown.returncode=-9`** — correct loud failure; receipts of victims (d2/e2/g2) show the harness notices the killed child rather than hanging; READY_TIMEOUT=90 s was never approached.

## Residual risk and verification gaps

- All server-kill timings landed pre-ready (ollama >0.8 s to first successful `GET /` under load); the post-ready kill failure mode (which of create/tags/ps/evidence flips) remains unobserved. The independence conclusion does not rest on it: survivor receipts are complete and green in all four kills.
- Same-`--work` double-run not exercised (out of the assigned matrix; analytic hazard only).
- The counter's internal run is verified only by its own summary line + my external sampler observation of its listener (its work dir is deleted in its `finally`).
- Single host, CPU-only, one Ollama version, one fixture model — per the freeze's stated limits; nothing here speaks to registered consumers or other versions.

Artifacts (receipts, counter log, listener sampler, toctou probe, d3 no-receipt log): `.ufo/waves/round-60/w1/out/A07ConcurrentRuns/`.
