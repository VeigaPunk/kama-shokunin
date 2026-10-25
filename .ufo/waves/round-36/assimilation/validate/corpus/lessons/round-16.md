# Round 16 — loading-envelope verdict and a live llama.cpp lifecycle run

Steered round 16, 2026-10-20 (hyaku phase 2). Starting revision
`20e392ea683a36bc223eb7cb45897acfb45456a3`; initial `git status --porcelain`
was empty; no `lane-dead-no-report kama round=16` line, so nothing inherited.
Assignment: operability + calibration (`../shokunin.conf:52`); calibration 7
is the lowest assigned axis versus operability 8; no stagnation waiver.

## Declared claims

- **C1 calibration — catch the probe's loading-server overreach.** Since round 1
  (`c6199a2`) `tools/kama-probe.sh` graded every remaining non-2xx, non-HTML
  response without a model array (after the 401/403 rule)
  `FOREIGN_SERVICE` / `non-2xx-non-model-http`, evidence "non-2xx HTTP from a
  non-model service". A loading llama.cpp server answers `/v1/models` exactly
  that way. The lane's matrix (round 10, `runtime-health-surface-matrix.md:14`)
  documented the body for `/health` only, and the round-11 crosswalk read the
  README as a `/v1/models` 200 while loading; no criterion compared engine
  states with the probe's verdicts. The repair adds
  `MODEL_LOADING` / `llamacpp-loading` for the exact envelope only, keeps every
  other verdict, and appends corrections to each lane document that called the
  vocabulary fixed or routed the state elsewhere. Counting commands: `python3
  .ufo/waves/round-16/measure.py` (frozen versus current probe over the literal
  stub matrix `tests/probe-verdicts/*.json`) and `python3
  .ufo/waves/round-16/stale-statements.py --rev REV` (17-row ledger of stale
  lane statements and the round-16 correction that must cite each).
- **C2 operability — capability: live, lane-owned llama.cpp lifecycle run.**
  `tools/kama-llamacpp-live.py` starts the official b11755 llama-server with a
  pinned 1.2 MB GGUF on an unregistered loopback port, captures the documented
  surfaces, runs the probe against it, tears it down and proves teardown;
  `tests/llamacpp-live/check-receipt.py` re-derives every check from stored
  evidence. Before: no lane tool could start a runtime; the last real
  llama.cpp answer was the round-2 baseline (2026-09-29T04:30:44Z; round 3 saw
  only refused connections), and the registered consumers are `DEAD`.

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
| A green live receipt proves registered-consumer health or restoration | reject | S041 receipt port 37527 and refusal set {8080, 34113}; `registry/history/latest.tsv` still `DEAD`; nothing was restored |
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

## Falsify wave — dispositions (79 seats, 2026-10-20)

Confirmed by re-running: frozen 55/17 and current 72/72 (record-for-record
against the receipts, 9 runs, 4 concurrent); frozen-probe provenance chain;
live reproduction 10/10 by a second seat; refusals and digest gate; snapshot
persistence of `MODEL_LOADING` (`transitions=0` on rerun); `listeners` and
`check` registry-mode integration; the python3 fallback; all 8 matcher mutants
killed; the API-key precedence live (5 launches, 140 unkeyed 503s before any
401, `ExecApiKeyLiveOrder.md`); a live loading window (10/10 launches by
`ExecLoadingWindowCapture.md`, 453 byte-identical 503 bodies).

Repaired in the round (commit `726f737`):

- Live harness: ownership is proven at the first HTTP answer (a stranger's body
  had landed in `loading_503`, `CriticC2Admission.md` D1); `/v1/models` is
  polled alone on keep-alive, so the final receipt captured 38 exact-envelope
  503s on the real server (`loading_envelope_exact` true); unexpected errors
  still write a receipt (exit 2); redirects refused; `killpg` only on a live
  child; the prctl pipe no longer leaks into the child, so `pdeathsig.prctl_ok`
  is recorded as `unknown`; the receipt carries `tool` and `probe` digests.
- Receipt gate: rebound a second time (ownership must be `child`; argv,
  probe argv and declared port bound; loading fields consistent with
  transitions; install-tree digest recomputed; `None` entries fail closed);
  26 single-field mutations rejected; real receipts `VALID` with all four pins;
  the frozen-probe receipt fails with the current probe's pin (exit 1).
- `measure.py`: matrix set digest and counts (72, 17) pinned and gate exits
  checked, so a trimmed matrix can no longer PASS (`ReviewMeasurePy.md` F1).
- Matrix: two duplicate rows replaced by `ForeignControls.code-integer-500`
  (the `code == 503` conjunct was unpinned: an any-integer matcher scored 72/72)
  and `ForeignControls.html-body-sniff-text-plain` (the HTML body sniff was
  unpinned). Totals stay 72 rows, 17 `MODEL_LOADING`.
- Doc ledger `stale-statements.py`: 17 → 0 uncorrected (`CriticC1Admission.md`
  asked for a counted doc-side before→after). New corrections for SKILL.md:361,
  corpus/README.md:119 and endpoint-identity.md:126.
- Narrowed wording: router (only the router's own `/health` and `/v1/models`
  never answer with the body), exit (only `check`/`snapshot` gate), OPTIONS
  exemption, older builds can be false-ready (the entry had said "never a false
  `MODEL_OK`", contradicting its own leads), other engines are leads not
  knowledge (KQ6), PROVINCE narrowing marked pending L0, PATH shadowing stated.
- S041's anchor and teaches cells were amended before closure because the
  receipt file was regenerated; the row was first committed this round
  (`b8e485c`). No earlier-round row changed.

Kept as debt (not repaired; named so the next round can take them): matrix
`why` line citations use frozen numbering (+36/+43); one remaining duplicate
(`EnvelopeShapes.CodeAsString` = `Overbroad503.code-string`) and the
`LoadingRace` non-200 trio are one equivalence class; `check.py` grades reason,
exit and drift but no row makes them load-bearing (5 harness mutants survive,
`MutateHarness.md`), never grades `served_model`, has no route-match assertion,
its selftest does not reach the duplicate-name guard, and malformed probe output
ends in a traceback (exit 1, not 2); `ReadyControls` cannot tell exact from
substring or case-insensitive id matching (pre-existing `MODEL_OK` semantics);
live checks `health_ready` (status only), `teardown_exited` and
`teardown_port_closed` are weak and `loading_envelope_exact` is not graded
(`ReviewLiveHarnessCode.md`); an exception inside the harness `finally` block can
still escape; the frozen manifest lacks a prior-exposure field.

### Mistakes added by the falsify wave

| ID | Class | Evidence pointer | Captured-by | Fix / failure obligation |
|---|---|---|---|---|
| M6 | seat ran a prohibited command | `FamilyOverbroad503` ran `measure.py` by accident, rewrote both run receipts and restored them with `git checkout` (verdicts identical, its disclosure); build-wave `ReviewSkillPlacement` ran `check-receipt.py --selftest` | context clause "never measure.py" (worked as a detector only through disclosure) | final receipts regenerated by L1 at `726f737` and digested in `acceptance.json`; open: no mechanical guard stops a seat running it |
| M7 | session-store traversal recurs (round-15 routed defect 3) | `ReviewLesson` grep printed four `.ufo/interactive-sessions/` lines (unused); `ReviewReadmeProvinceShonen` `find ~/.config ~/.omp` listed session file names; `RerunSnapshotHarness` grep surfaced matches (none opened) | context clause — insufficient, the class repeated | open. Next wave context must give exact exclusions (`grep -r --exclude-dir=interactive-sessions`, never `find ~/.omp`); no fail-capable fix exists yet |
| M8 | M2 incomplete | the first rebind still accepted a forged loading transition, `--host 0.0.0.0`, another `-m` path and an `unknown` ownership token (`RerunReceiptGate.md`, `ReviewReceiptGateCode.md`, `MutateReceiptGate.md`) | falsify-wave mutation seats | second rebind; 26 mutations rejected; shown able to fail by the frozen-receipt/current-pin control (exit 1) |

Corrections to the table above: M3's fix column claimed a smoke that would
catch the hang; it would not (a stub without `serve_forever` still hangs on
`shutdown()`, `CriticMistakesFailCapable.md`). The actual backstops are the
30 s per-probe and 600 s per-run timeouts; M3 stays open as a harness design
gap. M4 undercounted: `ScoutMetricsSource` and `ReviewSourcesRowsA` also wrote
reports at the fleet root and moved them; `RevengerRunReceipts` left one there,
swept by L1 (report §Mistakes). M5 undercounted: `ConnectTameshi`,
`ConnectKake`, `ConnectMori` and `ConnectKengaku` also read sibling-lane files
beyond SKILL/PROVINCE/QUALITY by their own reports.

Discernment: no non-author admit/reject sample exists for this round; all 160
seats are lane-dispatched (LEARNING.md). Outside review remains pending.

Gate locations (falsify-wave `CriticSourceRows.md` D1/D2, `ReviewSourcesRowsB.md`
F1): all accessed 2026-10-20. S035
`https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/README.md`
lines 487 and 1258; S036 `…/704366d76…/tools/server/server-http.cpp` lines 312
and 318; S037 `…/704366d76…/tools/server/server.cpp` line 493; the no-slot and
router-stream quotes are `server-context.cpp:5396` and `server-models.cpp:2585`
at the same commit (pinned copies under `.ufo/waves/round-16/sources/`); S038
`https://github.com/ggml-org/llama.cpp/releases/tag/b11755`, expanded-assets
digest line; S039 `https://huggingface.co/ggml-org/models-moved`, model card
README line 1 (identity cells come from the tree API, not the quote); S040
`https://llm-d.ai/docs/0.10/operations/readiness-probes` §Problem Statement
(21 words); S017 `https://kubernetes.io/docs/concepts/workloads/pods/probes/`
§Types of probe, readiness sentence (11 words); S041 `receipt.json` check
`probe_model_ok`, re-serialized compactly from the pretty-printed file.
