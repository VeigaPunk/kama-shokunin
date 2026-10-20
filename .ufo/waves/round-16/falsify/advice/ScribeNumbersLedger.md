# ScribeNumbersLedger — round-16 number ledger (falsify wave)

VERDICT: partial — round-16 numbers across lesson, SKILL §Round-16, SCORECARD, LOG, corpus README, `llamacpp-loading-lifecycle.md` and SHONEN. Every headline number (72/55/17, 72/0, 10/10, 30/0, 41 sources, 81 build seats, ports, digests) re-derives from receipts or re-runs. Refuted: the "measured results appended/follow" pointers (no such entries exist), a dangling `acceptance.json` pointer, and a correction-count mismatch between LOG/corpus README and the files.

Lane: `/home/vgpnk/Projects/shokunin/kama-shokunin`, HEAD `b8e485c`, start `20e392e`. Read-only except this report and removed scratch.

## 1. Commands run (exit codes)

| Command (cwd = lane root) | Exit | Result |
|---|---|---|
| `git log --oneline -6`; `git rev-parse 20e392e` | 0 | HEAD `b8e485c`; `20e392e` = `20e392ea683a36bc223eb7cb45897acfb45456a3` (full, matches lesson line 4) |
| `git show 20e392e:tools/kama-probe.sh \| sha256sum` | 0 | `93ee4302718f97862135472411ecf7aa6d5a0dc5cf778cce2c8deefe97a2cd64` (matches frozen manifest and SKILL row 531); blob `447e29b3…`, 47443 bytes = frozen file size |
| `git show b8e485c:tools/kama-probe.sh \| sha256sum`; `sha256sum tools/kama-probe.sh` | 0 | both `6edd3c4cfdf3f86c98202cef58859c29406d4a9cec17495454c514ac5972fa50` (= `run-after.json` probe_sha256); `git diff --stat b8e485c -- tools tests registry` empty |
| `git log -S'non-2xx-non-model-http' -- tools/kama-probe.sh` | 0 | only `c6199a2` (round-1) introduces the string — lesson "since round 1 (`c6199a2`)" confirmed |
| `python3 tests/probe-verdicts/check.py --probe tools/kama-probe.sh --json` (to /tmp) | 0 | tests 72, passes 72, failures 0 |
| `python3 tests/probe-verdicts/check.py --probe .ufo/waves/round-16/frozen/kama-probe-before.sh --json` (to /tmp) | 1 | tests 72, passes 55, failures 17 (expected 1 = frozen red) |
| `python3 tests/probe-verdicts/check.py --selftest` | 0 | exit 0 (content read earlier from `run-check-selftest.txt`: tests=72 passes=72; selftest 4/4 malformed rejected) |
| `python3 tests/llamacpp-live/check-receipt.py .ufo/waves/round-16/live/receipt.json` | 0 | `VALID` |
| same, `receipt-frozen-probe.json` | 0 | `VALID` |
| `python3 tests/llamacpp-live/check-receipt.py --selftest` | 0 | `16 mutations + unreadable case all rejected` |
| Python JSON readers over both live receipts, probe-verdict matrix, build/falsify dispatch JSON, `registry/`, `stat`, `sha256sum` on binary and GGUF | 0 | values in §2 |
| `pgrep -x llama-server` | 1 | none running (no server started by me) |
| `sha256sum` on `~/.local/opt/llama-b11755/llama-server` and `stories260K.gguf` | 0 | launcher `b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804`; model `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` |

Not run, by rule or design: `measure.py` (forbidden: rewrites L1 receipts); `tools/test-snapshot.sh` (not re-run; the `RESULT pass=30 fail=0` figure is cited from `run-test-snapshot.txt`, exit 0 there); `tools/kama-llamacpp-live.py` (no llama-server started; receipts only re-validated); no probe of 8080/34113.

## 2. Number ledger

Status: OK = matches its source of truth; MISMATCH = see §3.

| # | Number | Where stated | Source of truth | Status |
|---|---|---|---|---|
| 1 | 72 stub rows, 9 families | lesson §Measurements; SKILL row 530; LOG | `tests/probe-verdicts/*.json`: 9 files, 72 rows (re-counted) | OK |
| 2 | 17 MODEL_LOADING expectations | SKILL row 530; lesson M1 | re-counted: 17 rows with `expected.verdict == MODEL_LOADING`; per-family fails before: EnvelopeShapes 2 + LoadingEnvelope 8 + LoadingRace 5 + NearMissTriple 2 = 17 (`measure-stdout.txt`) | OK |
| 3 | frozen 55 pass / 17 fail | lesson M1, §Measurements; SKILL | `check.py` re-run exit 1, 55/17; `run-before.json` 55/17 | OK |
| 4 | repaired 72/72 | lesson; SKILL | `check.py` re-run exit 0, 72/0; `run-after.json` | OK |
| 5 | changed verdicts = 17 loading rows, directional equal | lesson; SKILL row 531; measure-stdout | `measure-stdout.txt`: `loading_expectations=17 before_failed=17 changed=17 equal=True`, exit 0 | OK |
| 6 | frozen probe sha `93ee4302…cd64` | lesson; SKILL row 531; knowledge | `git show 20e392e:tools/kama-probe.sh \| sha256sum` (re-run) | OK |
| 7 | frozen manifest source commit | `frozen/manifest.json` | `source_commit` 20e392ea…; blob 447e29b3… (`git rev-parse`) | OK |
| 8 | `bash tools/test-snapshot.sh` pass=30 fail=0 (was 24) | lesson §Measurements | `run-test-snapshot.txt` `RESULT pass=30 fail=0`, exit=0; not re-run (§1) | OK (receipt-cited) |
| 9 | live 10/10 checks | lesson; SKILL; SHONEN; knowledge | `live/receipt.json`: 10 check ids, 10 passed; re-derived `check-receipt.py` VALID exit 0 | OK |
| 10 | frozen-probe live control 10/10 | lesson; knowledge | `live/receipt-frozen-probe.json`: 10/10, VALID exit 0 | OK |
| 11 | live port 32845 | lesson; knowledge; S041 | `receipt.json` `port` 32845 | OK |
| 12 | frozen-control port (not stated in docs) | — | `receipt-frozen-probe.json` port 39375 | [not cited in docs] |
| 13 | refusal set {8080, 34113} | knowledge; S041 | `receipt.json` `port_refusal_set` | OK |
| 14 | window 13:49:38.040Z–13:49:38.170Z | lesson; knowledge; S041 | `receipt.json` `started_utc`/`ended_utc` | OK |
| 15 | install tree 51 files, `install_tree_sha256` 6c216313a88d71b1… | knowledge | `receipt.json` `server.install_tree` 51 entries; digest `6c216313a88d71b141bc62f6…` | OK |
| 16 | launcher sha `b6a31a8e97615a2a…`; impl `e404b91a81c9ab65…` | knowledge | `sha256sum` launcher = `b6a31a8e97615a2a1445…`; `server_impl_sha256` `e404b91a81c9ab65756b…` | OK |
| 17 | model sha `270cba1bd5109f42…` before and after | lesson; knowledge; SKILL | `receipt.json` `model.sha256`, `model_sha256_post`; `sha256sum` GGUF | OK |
| 18 | GGUF "1.2 MB" | lesson C2 | 1185376 bytes | OK (rounded) |
| 19 | build `/props` `b11755-704366d76` | knowledge | `receipt.json` captures `props.fields.build_info` | OK |
| 20 | endpoints /health 200, /v1/models 200 owned_by llamacpp, /metrics 501, /slots 200 | lesson; knowledge | `receipt.json` captures: health 200, models 200, metrics 501, slots 200, props 200 | OK |
| 21 | MODEL_OK exit 0 `matched`; MODEL_MISMATCH exit 2 `served-id-mismatch` with `kama-not-this-model` | lesson; knowledge; SHONEN | `receipt.json` probes[0] exit 0 `matched`; probes[1] exit 2 expect `kama-not-this-model` | OK |
| 22 | load window: /health and /v1/models refused once, then /health 200; no 503 captured | knowledge; lesson | `receipt.json` `transitions`; `loading_observed` false | OK |
| 23 | model loads "about 8 ms" | knowledge | teardown log: loaded at 8.725 ms, listening at 8.728 ms | OK [INFERENCE on wording: wall-clock from process start] |
| 24 | teardown: returncode 0, sigterm, port refuses | knowledge; SHONEN | `receipt.json` `teardown` | OK |
| 25 | controls: digest mismatch exit 3; --port 34113 exit 2; --port 8080 exit 2; --port 631 exit 2; post-run no llama-server | SKILL row 532 (exit 3); lesson §Meas. (34113 exit 2) | `live/controls.txt` (exit lines 3/2/2/2; pgrep=0, ss=0) | OK |
| 26 | `check-receipt --selftest` 16 mutations | SKILL row 533; lesson M2 | `controls.txt`; re-run exit 0 | OK |
| 27 | asset sha `753bfa7327a75b47…a226` | SKILL row 532; LOG; lesson gate; SOURCES S038 | `SOURCES.md` S038 `sha256:753bfa7327…a226`; full string identical in LOG, SKILL, lesson | OK (GitHub digest not re-fetched) |
| 28 | sources: S035–S041 added; 41 `| S` rows | lesson; LOG; SCORECARD "registry now 41 rows" | `corpus/SOURCES.md` `^\| S[0-9]` count = 41 | OK (see §3 M7 on wording) |
| 29 | S017 used-by two knowledge entries | LOG; lesson | `SOURCES.md` S017 used-by col = runtime-health-surface-matrix.md, llamacpp-loading-lifecycle.md | OK |
| 30 | build seats 81 (executor 16, scout 20, reviewer 14, critic 6, sentinel 2, connector 8, revenger 4, scribe 10, simplifier 1), policy 64–100 | LOG | `build/validation.json` spawn 81; `build/completion-summary.json` role_mix sums to 81; policy waveMinLanes 64 / waveMaxLanes 100; completed 81, failed 0 | OK |
| 31 | falsify wave seats 79 | (SCORECARD/LOG do not state; roster does) | `falsify/dispatch.json` spawn 79 | [not in round-16 docs] |
| 32 | consumer registry 3 rows | SCORECARD (historical) | `registry/endpoint-consumers.tsv` 3 data rows; `history/latest.tsv` 3 rows all DEAD, snapshot 20261014T124232Z | OK |
| 33 | VOCAB seven verdicts | SKILL line 11 (six, history); SKILL §Round-16 "seventh" | `tools/kama-probe.sh:62` VOCAB has 7 tokens incl. MODEL_LOADING | OK |
| 34 | KQ19 cites `server-http.cpp:307-328` | QUALITY KQ19; knowledge; S036 | `.ufo/…/sources/llama.cpp-704366d/server-http.cpp` gate at 308–328 (`is_ready` at 308, body literal 318) | OK |
| 35 | `server-http.cpp:312` quote "no endpoints are allowed…" | lesson gate | saved source line 312, verbatim | OK |
| 36 | `server.cpp:493` quote "start the HTTP server before loading…" | lesson gate; S037 | saved source line 493, verbatim | OK |
| 37 | server.cpp single-model `is_ready.store(true)` at 515, load at 507; router store at 460 | knowledge; S037 | saved `server.cpp` lines 460, 493, 507, 515 | OK |
| 38 | README `/health` 503 body at line 486, explanation 487; key order code/message/type | knowledge; S035 | saved `README.md` lines 479–490 | OK |
| 39 | README:1258 `meta` "can be null" | lesson gate; knowledge; S035 | saved `README.md` line 1258 verbatim | OK |
| 40 | README `/health` section 479–490 | S035 | saved README | OK |
| 41 | llama.cpp commit `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad` = b11755 | knowledge; S035–S037 | `sources/pins.json` commit field | OK |
| 42 | vLLM v0.32.0, TGI v3.3.7, KoboldCpp 1.123.1, SGLang v0.5.22 | knowledge scope limits | `build/advice/ScoutVllmStartup.md`, `ScoutTgiStartup.md`, `ScoutKoboldCppServer.md`, `ScoutSglangStartup.md` contain each version | OK (advice-level, not re-verified upstream) |
| 43 | probe sha after = `6edd3c4c…` (not in lesson) | run-after.json | working tree and `b8e485c` both equal | OK |
| 44 | frozen probe 93ee…: 8 digest prefixes/full forms across docs | SKILL, lesson, knowledge, LOG | all equal the full digests above | OK |
| 45 | SCORECARD round-16 axes: calibration 7→7, operability 8→8, freshness 8, coverage 9, depth 7, adjacency 7 | SCORECARD Current state; round-16 section | round-10 erratum (SCORECARD 205–213) and later "→ x → x" rows | OK for the 7→7 and 8→8 round-16 plans (planned, not measured — see M1) |

## 3. Mismatches and defects

M1 — Missing measured entries (refute). LOG §round 16 ends at line 952 with "Measured results follow in the next entry." LOG is 953 lines; no following round-16 measured entry exists (grep `round 16` → lines 925, 950, 952 only). SCORECARD §Round 16 ends with "Measured values are appended below after execution." and the file ends at line 598 with nothing below. Both pointers are dangling. The measured numbers exist only in `.ufo/waves/round-16/*.json|txt` receipts, not in the scorecard or LOG.

M2 — Dangling artifact pointer. `corpus/lessons/round-16.md` line 94: "Final numbers at the measured commit are in `.ufo/waves/round-16/acceptance.json`." The file does not exist (`ls` → no such file, `.ufo/waves/round-16/` lists none). Either create it (not my assignment) or remove the pointer.

M3 — Correction-count mismatch. LOG §round 16 says "appended corrections in five knowledge entries, the registry header comment and SKILL.md". `corpus/README.md` §Round-16 lists five: `endpoint-identity.md`, `consumer-registry.md`, `listener-census.md`, `served-identity-crosswalk.md`, `runtime-health-surface-matrix.md`. Actual "Correction — round 16" headings:
- endpoint-identity.md:182
- consumer-registry.md:406
- listener-census.md:389
- served-identity-crosswalk.md:136
- runtime-health-surface-matrix.md:60
- snapshot-history.md:106 (omitted from both LOG and corpus README)
That is six headings. The lesson's routed-defect list adds `ollama-evidence-replay.md` (replay prose precision, no "round 16" heading located; not verified in content). So the docs undercount by one (LOG, README) and the lesson/brief set of seven is not reflected in any README or LOG entry.

M4 — Frozen-control receipt registry path does not exist. `live/receipt-frozen-probe.json` `probes[0].result.registry` = `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-16/registry/endpoint-consumers.tsv`; `os.path.exists` → False. The live receipt's path (`…/kama-shokunin/registry/endpoint-consumers.tsv`) exists. [INFERENCE] the probe's `--port` mode builds its one row from the port and does not read this file, so the 10/10 control is unaffected; the receipt nonetheless names a file that is not in the tree. The receipt gate still returns VALID (exit 0).

M5 — Advice conflict on the exemption window, not reflected in the knowledge entry. `llamacpp-loading-lifecycle.md:80-83` gives "roughly b6000 and b7502" and cites `RevengerEnvelopeHistory.md`, which lists b7502 as exempted and b7731 as gated. `ReviewMatcherExactness.md:131` says "b6000–b7400" and proposes a "b7600+" scope note. The knowledge figure is consistent with the sampled-tag list; the reviewer's b7400 contradicts it. Recommend the knowledge entry note the disagreement or the reviewer advice be corrected (not edited by me).

M6 — "Already documented" cites a different commit. Lesson line 17 and knowledge line 17-18 say `runtime-health-surface-matrix.md:14` "already recorded the README's /health 503 body". That row cites `tools/server/README.md @ c0fd7862`, not b11755/704366d. The body is the same string in the b11755 README (verified, line 486). Whether it was byte-identical at c0fd7862 is not verified [INFERENCE].

M7 — Ambiguous "registry" wording. SCORECARD §Current state: "sources-registry … registry now 41 rows after round 16". The 41 is `corpus/SOURCES.md` (41 `| S` rows, correct). Elsewhere "registry" means `registry/endpoint-consumers.tsv` (3 rows). Numbers are correct; wording invites misreading.

M8 — Unverified secondhand quotes. Lesson gate row 44 quotes `server-context.cpp:5396` and `server-models.cpp:2585`. Those files are not in `.ufo/waves/round-16/sources/llama.cpp-704366d/` (only README.md, server-common.cpp/.h, server-http.cpp, server.cpp). The quotes appear only in advice (`CriticC1Overfit.md:22,74`, `RevengerEnvelopeHistory.md:55`). Also not re-fetched in this wave: S017 `probes.md:70`, S038 "Pre-release", S039 model card, S040 quote, the S021 404 claim, GitHub asset digest. Treat as [INFERENCE]/secondhand where the lesson does not say otherwise.

M9 — Observed, not caused by me. `git status --porcelain` before my runs listed `?? .ufo/waves/round-16/__pycache__/`; the after-run did not list it. I did not touch that path. The two `__pycache__` dirs my `check.py` / `check-receipt.py` runs created under `tests/probe-verdicts/` and `tests/llamacpp-live/` I removed.

## 4. Checked and clean (no defect)

- 72/17/55, 72/0, 17 family breakdown, 9 families — all re-derived.
- 10/10 live and frozen-control; VALID gates; 16 mutations; teardown; port and refusal set; launcher and model digests; install tree 51 files.
- 81 build seats, role mix sums to 81, policy 64–100; falsify 79 seats (dispatch.json).
- 30/0 test-snapshot (receipt-cited, §1).
- 41 sources, S035–S041 contiguous; S017 used-by correct.
- Frozen probe digest `93ee4302…cd64` and `git cat-file` blob equal.
- SHONEN statements match receipt facts.

## 5. Installs

None. No tool installed or updated by this wave.

## 6. Limitations

- No upstream refetch; upstream line numbers were checked against the saved copies in `.ufo/waves/round-16/sources/llama.cpp-704366d/` only.
- `measure.py` not re-run (forbidden for this seat); L1 receipts cited.
- `tools/test-snapshot.sh` not re-run.
- No llama-server started; live receipts validated, not re-executed.
