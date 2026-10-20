# Round 16 — loading-envelope verdict and a live llama.cpp lifecycle run

Steered round 16, 2026-10-20 (hyaku phase 2). Starting revision
`20e392ea683a36bc223eb7cb45897acfb45456a3`; initial `git status --porcelain`
was empty; no `lane-dead-no-report kama round=16` line, so nothing inherited.
Assignment: operability + calibration (`../shokunin.conf:52`); calibration 7
is the lowest assigned axis versus operability 8; no stagnation waiver.

## Declared claims

- **C1 calibration — catch the probe's loading-server overreach.** Since round 1
  (`c6199a2`) `tools/kama-probe.sh` graded every non-2xx, non-HTML response
  without a model array `FOREIGN_SERVICE` / `non-2xx-non-model-http`, evidence
  "non-2xx HTTP from a non-model service". A loading llama.cpp server answers
  `/v1/models` exactly that way. The lane's own matrix (round 10,
  `runtime-health-surface-matrix.md:14`) already documented the body, and no
  criterion compared that knowledge with the probe's behaviour. The repair adds
  `MODEL_LOADING` / `llamacpp-loading` for the exact envelope only, keeps every
  other verdict, and appends corrections to each lane document that called the
  vocabulary fixed or routed the state elsewhere. Counting command: `python3
  .ufo/waves/round-16/measure.py` (frozen versus current probe over the literal
  stub matrix `tests/probe-verdicts/*.json`).
- **C2 operability — capability: live, lane-owned llama.cpp lifecycle run.**
  `tools/kama-llamacpp-live.py` starts the official b11755 llama-server with a
  pinned 1.2 MB GGUF on an unregistered loopback port, captures the documented
  surfaces, runs the probe against it, tears it down and proves teardown;
  `tests/llamacpp-live/check-receipt.py` re-derives every check from stored
  evidence. Before: no lane tool could start a runtime; the last real
  llama.cpp observation was round 3 (2026-10-14), and the registered consumers
  are `DEAD`.

The two claims are separable. C1 needs no runtime (stub servers only). The C2
live run with the frozen pre-round probe passes all 10 checks
(`.ufo/waves/round-16/live/receipt-frozen-probe.json`).

## Gate

All sources opened 2026-10-20. Quotes are verbatim and at most 25 words.

| Candidate | Decision | Source, location, quote |
|---|---|---|
| `MODEL_LOADING` for the exact triple on `/v1/models` 503 | admit (KQ19) | S036 `server-http.cpp:312` "no endpoints are allowed to be accessed when the server is not ready"; body literal at 318-320 `{"message", "Loading model"},` |
| The 503 window is reachable on a single-model server | admit | S037 `server.cpp:493` "start the HTTP server before loading the model to be able to serve /health requests" |
| Widen to any 503, any `unavailable_error`, or substring "loading" | reject | `server-context.cpp:5396` "no slot available" and `server-models.cpp:2585` "Stream owner model is loading, retry later" share type and code (advice `ScoutUnavailableUses.md`) |
| README alone supports the `/v1/models` 503 | reject | S035 README:1258 "The `meta` field can be `null` (for example, while the model is still loading)." — the README says the opposite for `/v1/models`; S035 is scoped to `/health`, README:487 "Explanation: the model is still being loaded." |
| A loading body proves the runtime is llama.cpp or which model loads | reject | body-shape match only; a stub that is not llama.cpp is graded `MODEL_LOADING` by the matrix itself |
| Not-ready is a readiness class, not dead and not foreign | admit, scoped | S017 probes.md:70 "Readiness probes determine when a container is ready to accept traffic."; S040 (vLLM-only) "The vLLM `/health` endpoint only indicates that the server process is running, not that models are loaded and ready to serve." |
| S040 supersedes S021 (URL 404) | admit | recorded S021 URL returned 404 on 2026-10-20; versioned v0.10 page returned 200 with the same text (advice `ScoutLlmdReadiness.md`) |
| Live capability on the pinned build | admit, scoped | S038 asset record `"digest": "sha256:753bfa7327a75b477d4d14cde71e0e46a40acc3a1408c5504530b78c33a6e226"`, page label "Pre-release"; S039 model card "Various models to be used in llama.cpp CI workflow." |
| A green live receipt proves registered-consumer health or restoration | reject | S041 receipt port 32845 and refusal set {8080, 34113}; `registry/history/latest.tsv` still `DEAD`; nothing was restored |
| Live receipt as own-work row | admit | S041 check `probe_model_ok` observed `{"exit": 0, "reason": "matched", "verdict": "MODEL_OK"}` |
| Generalize `MODEL_LOADING` to vLLM, SGLang, TGI, Ollama, LocalAI, LM Studio, KoboldCpp | reject | engine scans (wave advice) found no such body on `/v1/models`; kept as advice, not rows |

Row changes: new S035–S041; S017 used-by
`corpus/knowledge/runtime-health-surface-matrix.md` → same plus
`corpus/knowledge/llamacpp-loading-lifecycle.md`. No status or recheck cell of
an existing row changed. S021 stays `queued` and unedited; S040 supersedes it
by row.

## Mistakes

| ID | Class | Evidence pointer | Captured-by | Fix / failure obligation |
|---|---|---|---|---|
| M1 (mined) | overreach: a not-ready model server graded "non-model service" | frozen `.ufo/waves/round-16/frozen/kama-probe-before.sh:513-522` (`C_VERDICT=FOREIGN_SERVICE`, reason `non-2xx-non-model-http`); introduced round 1 `c6199a2`, never revised (advice `RevengerPlannerWalk.md`); the body was already documented at `runtime-health-surface-matrix.md:14` | none — no criterion compared documented engine states with the probe's verdicts | KQ19 plus the stub matrix. Shown able to fail: the frozen probe fails exactly the 17 expected-loading rows (`run-before.json`: 55 passed / 17 failed, directional equal), the repaired probe passes 72/72 |
| M2 | self-authored selftest hides producer drift | first `check-receipt.py` read `started`/`ended`, `json`, `port_closed` while the producer wrote `started_utc`/`ended_utc`, `result`, `port_refuses`; its selftest literal used the gate's own spelling and was green | outside the author: `SimplifierHarness.md`, `ReviewShonenEvidence.md` | gate rebound to the producer's exact keys; the real receipt validates (exit 0) and 16 single-field mutations are rejected (`--selftest`) |
| M3 | measurement started on an unreviewed harness | L1 started `measure.py` while `check.py` built its stub server without `serve_forever`; the run hung and was killed (bg job cancelled) | `ReviewSchemaAmbiguity.md` H1 | owner added the serving thread and a zero-request guard; L1 now runs a single-test timing smoke before any full measurement (`--only` run, 0.6 s) |
| M4 | seat write misroot | `RevengerPlannerWalk` first wrote its report relative to the fleet root, then moved it into the lane and removed the created directories (its own disclosure) | the round-prompt context clause on absolute paths; the seat's self-check | L1 misroot sweep before the report (`git -C /home/vgpnk/Projects/shokunin status --porcelain`) |
| M5 | seat read beyond its bound | `ConnectKumitate` read two kumitate note files beyond SKILL/PROVINCE/QUALITY; `ConnectTsukuroi` ran one `ls -la` on the C2 install paths (both disclosed) | context bounding clause (round-15 routed defect 3) | disclosed and kept as incidents, not evidence; no session or credential store was read by any seat that reported |

## Routed defects from `round-15-verifier-spotcheck.md`

1. R1 (count comparison) — resolved in round 15; no change.
2. R2 (partial output versus provider failure) — resolved in round 15; no change.
3. Process incidents — this round's wave context forbids session/transcript
   stores and unbounded searches, and tells seats that L1 owns measurements.
   M4 and M5 record the deviations that still happened. No QUALITY criterion:
   this is dispatch hygiene, not corpus admission.
4. Dispatch provenance — `.ufo/waves/round-16/build/validation.json` records
   argv, cwd, the three environment bindings and the `taskCall` digest; the
   falsify wave uses `.ufo/waves/round-16/dispatch-provenance.py`.
5. Replay prose precision — appended to `knowledge/ollama-evidence-replay.md`.
6. S012 wording — appended note in `SOURCES.md` marks the cross-source synthesis;
   no cell changed.

No disagreements were recorded in the round-15 outside sample (all five
agreed), so no criterion is owed for a disagreement.

## Measurements (L1)

- C1: `python3 .ufo/waves/round-16/measure.py` → exit 0. Frozen probe (sha256
  `93ee4302…cd64`, equal to `git cat-file blob 20e392e:tools/kama-probe.sh`):
  72 tests, 55 passed, 17 failed. Repaired probe: 72 passed, 0 failed. Changed
  verdicts: exactly the 17 `MODEL_LOADING` expectations. Final numbers at the
  measured commit are in `.ufo/waves/round-16/acceptance.json`.
- C1 no-harm: `bash tools/test-snapshot.sh` → `RESULT pass=30 fail=0` (was 24;
  the new cases assert a `MODEL_LOADING` baseline row is kept and an unknown
  verdict is still dropped). `python3 tests/probe-verdicts/check.py --selftest`
  → 72/72 plus 4/4 malformed tests rejected.
- C2: `python3 tools/kama-llamacpp-live.py …` → exit 0, 10/10 checks;
  `tests/llamacpp-live/check-receipt.py` → `VALID`; frozen-probe control 10/10;
  digest mismatch → exit 3 before launch; `--port 34113` → exit 2
  `port-refused-registered:34113`.
