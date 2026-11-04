# CR02 — falsification of the C3 second-engine target (round 80 w1)

Seat: CR02Critic-2. Axis judged: operability (C3). Instrument attacked, never edited:
`tools/round80-ollama-census.py`
(sha256 `5e3543a6445474a5fd9f383ed6903b676626e8ad37beb59a763cb19e0fa03e4c`) and
`tools/kama-probe.sh` (sha256 `0943fb461d0226e29d1b8a3b6af67740d4fe6863505ee6ed771719a30fdc3d19`,
byte-identical in lane worktree and my clone; `git status --porcelain` on both paths empty).
All runs executed in my scratch clone `/fast/scratch/hyaku/kama-r80/CR02Critic/clone`
(`git clone --shared`, toplevel verified), so the lane worktree and the executor's receipts were
never touched. Evidence copies: `.ufo/waves/round-80/w1/CR02Critic/` (this dir).

Baseline (T1, clone): `python3 tools/round80-ollama-census.py --repo $S/clone --work $S/w1
--out $S/out/t1.json` → `OLLAMA_CENSUS port=36175 engine=ollama unregistered=1 governed=1
class_missing=0`, exit 0; rows show `owner=ollama(pid=2198411)`, `verdict=MODEL_OK`, teardown
`port_closed: true`. Receipt `CR02Critic/t1-baseline.json`. The instrument reproduces its target
outside the lane. Selftest: `--selftest` → `OLLAMA_CENSUS_SELFTEST pass=6 fail=0`, exit 0.

## Q1 — Can the Ollama leg be satisfied by the llama.cpp fixture (same engine class, different binary)? → CATCHES (three independent gates)

Live llama.cpp b11755 (`~/.local/bin/llama-server --version` → `0.7.0-dev (build 11755,
commit 704366d76)`) on 127.0.0.1:46017, scratch registry declaring the port
(`CR02Critic/t3-probe.json`, probe exit 0):

```
row: {'port': 46017, 'registered': 'yes', 'owner': 'llama-server(pid=2291047)',
      'verdict': 'MODEL_OK', 'reason': 'expected-wildcard',
      'served_model': '/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf'}
```

The probe class is engine-blind: llama.cpp gets exactly the `registered=yes / MODEL_OK` class the
Ollama child gets. What catches it is the counter, not the class:

- gate 1 `curl http://127.0.0.1:46017/api/version` → `404 {"error":{"message":"File Not
  Found","type":"not_found_error","code":404}}` (`t3-apiversion.out`); the counter polls
  `/api/version` for exactly `{"version":"0.40.11"}` → `CouldNotEvaluate` → exit 2, never green.
- gate 2 `HOME=$S/w3/home OLLAMA_MODELS=$S/w3/models OLLAMA_HOST=127.0.0.1:46017
  ~/.local/opt/ollama-v0.40.11/bin/ollama create kama-r80-llama -f Modelfile` → `CREATE_EXIT=1`
  (`t3-create.out`).
- grade would also add `owner-not-ollama` (`owner=llama-server(pid=…)` lacks the substring).
- audit-level cross-wiring (llama.cpp receipt filed under the ollama register row) is caught:
  t5-crosswired (below) exit 1 `receipt-names-other-engine`.

The kill rule "the Ollama leg is satisfied by the llama.cpp fixture" holds.

## Q2 — Can a plain HTTP stub answering `{"data":[…],"object":"list"}` on a loopback port satisfy it? → MISSES at the class level, CATCHES at the counter level

Plain stub (python http.server, only `GET /v1/models` → `{"object":"list","data":[{…}]}`,
everything else 404; source `CR02Critic/stub_plain.py`) on 127.0.0.1:46011:

- Probe leg (`bash tools/kama-probe.sh listeners --json --registry reg --port 46011`, exit 0,
  `t2a-probe.json`): `registered=yes, owner=python3(pid=2291041), verdict=MODEL_OK,
  served_model=kama-r80-stub:latest, summary governed=1`. **The class proves only that a
  model-API listener exists — it does not prove an Ollama process.** The predicate's engine
  identity lives entirely in the counter's wrapper, not in `registered`.
- Counter gates on the same stub: `curl /api/version` → `404` (`t2a-version.out`) → the counter's
  version poll fails → exit 2; `ollama create` against it → `CREATE_EXIT=1` (`t2a-create.out`).
  Fail-closed.
- Stronger impostor (answers `/api/version` `{"version":"0.40.11"}`, `/api/tags` with the nonce,
  `/v1/models`, `/api/ps`, and POST `/api/create` → 200 ndjson; source
  `CR02Critic/stub_impersonator.py`) on 46013: gate 1 passes (`200 {"version": "0.40.11"}`),
  gate 3 would pass, but `ollama create` still exits 1 (`t2b-create.out`) — the pinned client's
  create handshake needs more than a 200 ndjson line. Probe leg on the impostor classifies it
  `registered=yes MODEL_OK owner=python3` (`t2b-probe.json`), so grade's `owner-not-ollama`
  is a further independent catch. A perfect protocol impostor is stopped by the `ss`-derived
  process-owner substring — which is the only remaining engine proof, and it is a substring
  test (`"ollama" in owner`), so any process whose comm contains "ollama" would pass it. Beyond
  plain-stub scope; boundary noted, not a kill-rule breach.

## Q3 — Can the two registry legs be made to agree without the probe's class? → CATCHES

End-to-end with the real pinned child and a lying `--probe` that returns the green yes-leg
document for BOTH registries (`CR02Critic/stub_probe_yesboth.sh`,
`python3 tools/round80-ollama-census.py --repo $S/clone --probe $S/stub_probe_yesboth.sh
--work $S/w4 --out $S/out/t4.json`):

```
OLLAMA_CENSUS port=45699 engine=ollama unregistered=0 governed=0 class_missing=0
OLLAMA_CENSUS_FINDING unregistered-leg=yes
OLLAMA_CENSUS_FINDING legs-agree
OLLAMA_CENSUS_FINDING governed-count leg=no governed=1
OLLAMA_CENSUS_FINDING unregistered-count leg=no unregistered=0
T4_EXIT=1
```

Agreeing legs cannot print the target line: `legs-agree`, the per-leg class checks and the
count-movement checks fire together, exit 1 (receipt `t4-lying-probe.json`, teardown
`port_closed: true`). The `class-missing` (row absent) and `counts-do-not-move` arms are also
covered by the selftest. Note: a probe that lies *consistently* (green yes under the declaring
registry, green no under the other) would print the target line — `--probe` output is trusted
wholesale. That override is the round's own sanctioned control hook (the base-probe control uses
it), so the guarantee is tied to the default `repo/tools/kama-probe.sh` path, exactly as the
predicate words it.

## Q4 — Can `--audit` print `CLASS_ENGINES engines=2 verified=2 stale=0` with a missing receipt or a `class_missing=1` receipt? → CATCHES both, plus every other audit defect except one provenance weakness

All in the clone with crafted registers (receipts present in the worktree; master lacks them, so
the baseline also documents the documented worktree fallback). Commands:
`python3 tools/round80-ollama-census.py --repo $S/clone --audit --register registry/<variant>`
(outputs `CR02Critic/t5-*.out`):

| variant | line | exit | verdict |
|---|---|---|---|
| t5-baseline | `CLASS_ENGINES engines=2 verified=2 stale=0` | 0 | reproduces target |
| t5-missing-receipt (ollama receipt path absent) | `engines=2 verified=1 stale=1` + `missing-receipt ollama …c3-t5-absent.out` | 1 | CATCHES |
| t5-receipt-red (`class_missing=1` in receipt) | `verified=1 stale=1` + `receipt-red ollama …c3-t5-red.out` | 1 | CATCHES |
| t5-crosswired (llama.cpp receipt under ollama row) | `verified=1 stale=1` + `receipt-names-other-engine ollama …c3-llamacpp-recheck.out` | 1 | CATCHES |
| t5-missing-counter | `verified=1 stale=1` + `missing-counter ollama tools/absent-counter.py` | 1 | CATCHES |
| t5-one-engine | `engines=1 verified=1 stale=1` + `one-engine engines=1` | 1 | CATCHES |
| t5-register-absent | `engines=0 verified=0 stale=0` + `register-absent` | 2 | CATCHES |
| t5-fused (llama.cpp receipt + one appended line mentioning "ollama") | `engines=2 verified=2 stale=0` | 0 | **PASSES — provenance is substring-only** |

The fused case: `if engine not in text` is the whole "names the same engine" check, so a receipt
that merely mentions the row's engine string anywhere verifies green even when its substance is
the other engine's. The register is trust-by-convention; only the re-run (T1) binds receipt to
engine. This is within the predicate's literal wording but is the one audit leg I could turn
green with a receipt that is not what it claims — worth a receipt-content convention (e.g. the
`engine=` token from the run line plus the port) if the lane wants the audit to bite.

## Missing selftest arm

The selftest carries six grade-side arms (`both-legs`, `class-missing`, `legs-agree`,
`owner-not-ollama`, `verdict-not-model-ok`, `counts-do-not-move`) and **zero audit-side arms**.
Named missing arms: `receipt-red` and `missing-receipt` (the two the predicate calls out), plus
`receipt-names-other-engine`, `missing-counter`, `one-engine` (audit), `register-absent`, and no
end-to-end foreign-listener arm (plain stub / impostor / llama.cpp binary) — the engine-proof
gates (`/api/version` pin, `ollama create` handshake, owner substring) are untested by the
selftest; my Q1/Q2 runs are the only evidence they fire.

## Observations (no action required for the claim)

1. The `registered` class itself is engine-agnostic (Q1/Q2 rows prove it); the predicate's
   second-engine strength rests entirely on the counter's wrapper. The SOURCED claim ("a tags
   listing is an inventory of models, and a second engine's model list is exactly what the class
   needs and no more") is accurate — and the "no more" is doing the load-bearing work.
2. `engine=ollama` in the output line is hardcoded in `grade()`'s summary, not derived from the
   listener; acceptable given the gates, but it is an assertion, not an observation.
3. `probe_json` never passes `--expect`, so both legs classify `MODEL_OK` with
   `reason=expected-wildcard` regardless of which model id is served; model identity is enforced
   only by the create+`/api/tags` nonce gate (matching the predicate, which claims a census
   class, not identity).
4. `--audit` accepts receipts that exist only in the worktree (not at `--tip`) — documented
   behavior, consistent with L1 committing receipts at closure.

## Receipts (absolute paths, all under the lane)

`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-80/w1/CR02Critic/`:
`t1-baseline.json`, `t2a-probe.json`, `t2a-version.out`, `t2a-create.out`, `t2b-probe.json`,
`t2b-create.out`, `t3-probe.json`, `t3-apiversion.out`, `t3-create.out`, `t3-version.out`,
`t3-serve.log`, `t4-lying-probe.json`, `t5-t5-*.out` (7 audit variants + register-absent),
stub sources `stub_plain.py`, `stub_impersonator.py`, `stub_probe_yesboth.sh`.
Every command and exit code is quoted above. No lane file was edited; the counter and probe were
executed read-only from a `--shared` clone (toplevel asserted before use); all my test servers are
torn down (stray-listener check: none); the pinned ollama children ran under scratch HOME/model
stores and were reaped by the counter's own teardown.
