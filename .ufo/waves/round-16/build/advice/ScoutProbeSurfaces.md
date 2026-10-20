# Scout — verdict-vocabulary surfaces for MODEL_LOADING integration

Audited revision: `tools/kama-probe.sh` sha256 `d0d48d8d6a5d96553adb773ae7f75d4d0f47e19be6b2d7d8a1c9b7a83f6db8fe`
(1134 lines), `tools/test-snapshot.sh` `236c23c12964cf0b2f0a2f970187e216d3398dcf2b92ffb7e8606e0fdd029646`
(194 lines), `SKILL.md` `074dba4d…`, `registry/endpoint-consumers.tsv` `674cc70c…`.
**Both probe and harness are uncommitted and were edited during this audit** (`git status`: `M
tools/kama-probe.sh`, `M tools/test-snapshot.sh`); the tables record the state at the shas above —
the frozen `before` probe of C1 is a different file and is not audited here.

Method: bounded greps and ranged reads inside the five named paths only; no probe, harness, gate or
endpoint was executed (measurement belongs to L1). Every effect below that is not literally printed
by the source is marked **[INFERENCE]**.

Legend: **DONE** = already carries MODEL_LOADING at the audited revision; **OPEN** = still needs the
edit; **REVIEW** = no mechanical edit needed but the wording/coverage becomes incomplete.

## 1. Hard enumerations of the vocabulary

| # | path:line | Evidence (verbatim) | Status |
|---|---|---|---|
| 1 | `tools/kama-probe.sh:28-30` | `# Verdict vocabulary (exact strings):` … `MODEL_LOADING` | **DONE**, but split across two lines; line 28 still heads a block that now continues on 30 |
| 2 | `tools/kama-probe.sh:32-35` | `MODEL_LOADING: llama.cpp still loading — every non-frontend path answers 503` | **DONE** (documents trigger and "Drift, never a foreign service") |
| 3 | `tools/kama-probe.sh:60` | `VOCAB="MODEL_OK … DEAD NOT_HTTP MODEL_LOADING"` | **DONE**. Single source for all four JSON emitters (`:742`, `:813`, `:888`, `:1064`), so `verdict_vocabulary` in `listeners`/`consumers`/`check`/`snapshot` expands automatically |
| 4 | `tools/kama-probe.sh:115` | `verdicts: MODEL_OK … DEAD NOT_HTTP MODEL_LOADING` | **DONE** (`usage()`; this literal is separate from `VOCAB`) |
| 5 | `SKILL.md:11-13` | `Verdict vocabulary is shared with` `tools/kama-probe.sh` … `UNAUTHORIZED_SERVICE` \| `DEAD` \| `NOT_HTTP` | **OPEN** — six-item list, no MODEL_LOADING |
| 6 | `corpus/knowledge/endpoint-identity.md:3` | `The verdict vocabulary is fixed:` … `DEAD`, and `NOT_HTTP` | **OPEN** — contract doc calls six "fixed" |
| 7 | `corpus/knowledge/consumer-registry.md:84-85` | `The **live verdict** column uses the binding vocabulary:` … `DEAD` \| `NOT_HTTP` | **OPEN** — six-item list |
| 8 | `registry/endpoint-consumers.tsv:31-32` | `# Verdicts come from tools/kama-probe.sh:` / `#   MODEL_OK … DEAD \| NOT_HTTP` | **OPEN** — registry header comment |

## 2. Code paths that consume or gate on the vocabulary

| # | path:line | Evidence (verbatim) | Finding |
|---|---|---|---|
| 9 | `tools/kama-probe.sh:721` | `local i n_model=0 … n_unauth=0 n_loading=0` | **DONE.** Loading bucket exists |
| 10 | `tools/kama-probe.sh:726-731` | `MODEL_OK\|MODEL_MISMATCH) n_model=…` … `MODEL_LOADING) n_loading=…` | **DONE.** Every verdict now increments a bucket |
| 11 | `tools/kama-probe.sh:742` | `"summary": {"probed": %s, … "not_http": %s, "model_loading": %s}` | **DONE.** Bucket sum again equals `probed`; `model_endpoints` remains OK+MISMATCH only, so a loading server appears solely under `model_loading` **[REVIEW]** — worth stating in the summary contract if anything consumes it |
| 12 | `tools/kama-probe.sh:747` | `probed=%s … not_http=%s model_loading=%s` | **DONE.** Same widening in the human summary line |
| 13 | `tools/kama-probe.sh:933-937` | `# a baseline row is only believable if its verdict is in the vocabulary` / `…*\ DEAD\ *\|*\ NOT_HTTP\ *\|*\ MODEL_LOADING\ *)` | **DONE.** MODEL_LOADING is whitelisted, so `snapshot` no longer drops a row it just wrote |
| 14 | `tools/kama-probe.sh:937` + `tools/test-snapshot.sh:182-183` | `unknown verdict still warns` / `unknown verdict still audited and dropped` | **DONE / verified by harness.** The whitelist widened without becoming accept-all: a near-miss (`MODEL_LOADED`, `:167`) is still dropped and audited |
| 15 | `tools/kama-probe.sh:846` | `if [ "$C_VERDICT" = "MODEL_OK" ]; then EV_OK=1; EV_DRIFTROW=(false)` | **DONE by construction** — MODEL_LOADING is not MODEL_OK, so `--port` mode records drift |
| 16 | `tools/kama-probe.sh:862` | `if [ "$verdict" != "MODEL_OK" ]; then drift=true; fi` | **DONE by construction** — registry/snapshot drift and exit 2 follow C1 without a literal edit |
| 17 | `tools/kama-probe.sh:493-498` | `401) C_VERDICT=UNAUTHORIZED_SERVICE` … `403) … http-403` | Precedence verified: 401/403 returns **before** the loading gate |
| 18 | `tools/kama-probe.sh:501-507` | `if [ "$F_CODE" = "503" ] && … body_is_llamacpp_loading` | **DONE.** Sits after 401/403 and before the `is2`/HTML branch (`:508-515`), so 2xx loading-shaped bodies and 503 HTML keep their old verdicts |
| 19 | `tools/kama-probe.sh:418-446` | `Requires python3:` … `without python3 the` `body keeps its old FOREIGN_SERVICE verdict (fail closed, never false-pass)` | **DONE**; exactness is enforced (`isinstance(code, int)`, bool rejected, `code == 503`) |
| 20 | `tools/kama-probe.sh:724,783,799,840,859` | `classify "$port"` / `classify "$pnum" "$expected"` | MODEL_LOADING is reachable in all four subcommands; only `listeners` exposes per-verdict counters (#9-#12), while `check`/`snapshot` fold it into `drift` (#15-#16) |
| 21 | `tools/test-snapshot.sh:9` | `for dep in curl flock python3 ss; do` | Harness already hard-requires python3, matching the helper's gate (no parity divergence) |
| 22 | `tools/test-snapshot.sh:92` | `check fixture is MODEL_OK/exit 0` | Unaffected (fixture returns 200 + `data[]`, `:44-52`) |
| 23 | `tools/test-snapshot.sh:117` | `EXPECTED_ROW=$(printf 'fixture-a\tMODEL_OK\tmatched\tfixture-model\t%s\tyes' "$PORT")` | Unaffected exact-row assertion; no loading fixture |
| 24 | `tools/test-snapshot.sh:140` | `fixture-a verdict MODEL_OK -> DEAD` | Unaffected |
| 25 | `tools/test-snapshot.sh:162-188` | `# Vocabulary growth: a baseline row whose verdict is MODEL_LOADING is trusted as` | **DONE (whitelist coverage).** Seeded `latest.tsv` proves accept-and-diff plus near-miss rejection with no live server; **OPEN (envelope coverage)** — no 503 `Loading model` stub, so only C1's matrix exercises the exact-match gate |

## 3. Documentation tables that assign verdicts to observed shapes

| # | path:line | Evidence (verbatim) | Finding |
|---|---|---|---|
| 26 | `corpus/knowledge/endpoint-identity.md:13-19` | `First-match precedence` … `Any non-`2xx` HTTP status other than `401`/`403` … `FOREIGN_SERVICE`` (row 5, `:17`) | **OPEN — largest doc defect.** The 503 loading envelope is exactly what row 5 now routes to FOREIGN_SERVICE; a new precedence row is required between the 401/403 row and the HTML row |
| 27 | `corpus/knowledge/endpoint-identity.md:9` | `Targeted `--port` examples exit `0` only for `MODEL_OK` and `2` for other verdicts` | **REVIEW** — still true; MODEL_LOADING is an "other verdict" |
| 28 | `corpus/knowledge/endpoint-identity.md:111` | `requires **3/3 `MODEL_OK`**` … `Three identical non-`MODEL_OK` verdicts are a stable failure/drift` | **REVIEW** — MODEL_LOADING is already correctly "not ready", no edit needed |
| 29 | `corpus/knowledge/endpoint-identity.md:163` | `implementation and verdict vocabulary are unchanged` | **OPEN — false after the cutover.** Round-11 historical sentence needs an appended correction, not a rewrite |
| 30 | `SKILL.md:125-140` | `## Decision table` … rows for HTML/refused/401/`MODEL_MISMATCH`/`DEAD`/`NOT_HTTP` | **OPEN.** No "503 Loading model" symptom row; operator action (wait/retry, do not repoint) is undocumented |
| 31 | `SKILL.md:167-182` | `## Historical error signatures` … `{"error":{"message":"File Not Found",…` | **OPEN.** No row for `{"error":{"message":"Loading model",…}}`; the table is where an operator matches observed bodies |
| 32 | `corpus/knowledge/alias-endpoint-normalization.md:55` | `treat `MODEL_OK`/`MODEL_MISMATCH` … as the only accepted local-model evidence` | **REVIEW** — MODEL_LOADING is neither evidence nor foreign; the "foreign/dead/unauthorized" phrase omits it |
| 33 | `corpus/knowledge/listener-census.md:7-8` | `are the frozen L1 binding contract` … `no vocabulary was added or renamed here` | **OPEN — historical claim.** Append a dated correction pointer; do not rewrite the census |
| 34 | `corpus/knowledge/listener-census.md:363` | `The contract's rule table only assigns a verdict for **2xx** responses (and for 401/403, refused,` | **OPEN.** §9's "no rule fires" gap analysis is stale once a 503 rule exists |
| 35 | `corpus/knowledge/runtime-health-surface-matrix.md:14` | `503 `unavailable_error` "Loading model" while loading; 200 `{"status": "ok"}` when loaded` | **REVIEW (corroboration)** — this is C1's documented trigger; optional note that the probe now encodes it |
| 36 | `corpus/knowledge/served-identity-crosswalk.md:52` | `on llama.cpp single-model it can even be observed mid-load` | **REVIEW** — that mid-load observation is now MODEL_LOADING, not MODEL_OK; confirm the sentence still describes the intended window |
| 37 | `corpus/knowledge/snapshot-history.md:28,35` | `Comparison baseline: `id`, `verdict`, `reason`` / `Later runs compare `verdict`, `reason`,` | **REVIEW** — prose names fields, not values; correct today, but `latest.tsv` acceptance is code-gated at #13 |
| 38 | `corpus/knowledge/snapshot-history.md:66-67` | ``RESULT pass=24 fail=0` in 1.15 s` | **OPEN — stale count.** `test-snapshot.sh` grew from 171 to 194 lines with six new `ok` assertions (`:162-188`) **[INFERENCE: pass=30 if all pass]**; the pinned 24 no longer describes the harness. L1 must re-measure, not copy 30 |
| 39 | `SKILL.md:303` | `exercises clean fixture, dead endpoint and their expected verdicts/exits` | **OPEN (coverage claim).** The harness now also exercises vocabulary growth (`test-snapshot.sh:162-188`), and the live 503 envelope is covered only by the new matrix; neither is named here |
| 40 | `SKILL.md:209` | `Schema `kama-probe/v1`, keys `subcommand`, `verdict_vocabulary`,` | **REVIEW** — key list only; the value widens automatically via `VOCAB` |
| 41 | `corpus/knowledge/ollama-evidence-replay.md:122` | `never read replay exit `0` as `MODEL_OK`` | **REVIEW** — semantic warning, unaffected |

Historical per-row labels also depend on the vocabulary but need no edit: `SKILL.md:37-38`
(`All three sampled `DEAD` / `connection-refused``), `corpus/knowledge/consumer-registry.md:72`
(`Every `MODEL_OK`/`FOREIGN_SERVICE` verdict in the table is` historical), `consumer-registry.md:88-107`
(live-verdict table), `corpus/knowledge/listener-census.md:49-68` (per-listener verdict column), and
`corpus/knowledge/drift-timeline.md:34` (`sample is DEAD/connection-refused`). These are dated
observations; rewriting them would fabricate a newer sample, so no edit belongs here.

## 4. Frozen artifacts — must not be edited

| # | path:line | Evidence (verbatim) | Why no edit |
|---|---|---|---|
| 42 | `registry/history/20261014T124232Z.json:5` | `"verdict_vocabulary": "MODEL_OK … DEAD NOT_HTTP",` | Point-in-time snapshot; a new run writes the widened string itself. Editing it would forge history |
| 43 | `registry/history/20261014T124525Z.json:5` | same | same |
| 44 | `registry/history/latest.tsv:1-4` | `#@snapshot_id … id	verdict	reason	served_model	port	file_match` | Historical baseline, all `DEAD`; leave as-is. Its **acceptance** is the code whitelist at #13 |
| 45 | `registry/history/DELTA.md:7-22` | `omp-llama-cpp-default verdict FOREIGN_SERVICE -> DEAD` | Append-only ledger; no edit |

## 5. Explicitly no vocabulary dependency

Zero occurrences of any verdict token in these in-scope files (verified per-file counts):
`corpus/knowledge/cross-lane-scope.md`, `free-tier-provider-limits.md`,
`gguf-runtime-compatibility-boundary.md`, `served-model-identity.md`, and
`serving-metrics-crosswalk.md` (the last explicitly says metrics `stay out of the identity-verdict
path`). No edit should be made to them for this change.

**False friend:** `SKILL.md:315` says `header defines the six-column contract` — that is the registry
TSV's six **columns**, not the six verdicts. Do **not** change it to seven.

## 6. Residual unknowns / limits

- Line numbers for `tools/kama-probe.sh` and `tools/test-snapshot.sh` are for the shas in the header;
  both were edited mid-audit by the integrating item(s) and may shift again. `SKILL.md`, the corpus
  files and `registry/endpoint-consumers.tsv` were byte-stable.
- No execution: every behavioral claim above is static reading. `pass=24` → 30 is arithmetic over
  six added `ok` call sites, not a run; L1 owns the actual measurement.
- A loading endpoint is reachable today only via an explicit `--port` probe (C1's matrix); the tracked
  registry rows all resolve `DEAD` (`registry/history/latest.tsv:2-4`), so no registry-mode
  MODEL_LOADING row exists yet **[INFERENCE]**.
- Out of named scope and therefore not audited: the C1 stub-matrix harness under `tests/`, `PROVINCE.md`
  (referenced by `listener-census.md:8`), and any `LOG.md`/lesson text.
