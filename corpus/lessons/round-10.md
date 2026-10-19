# Round 10 lesson — sources registry, cross-engine entries, anchor re-verification (2026-10-19)
source: LOG.md (rounds 1–9); corpus/lessons/round-1.md:45-49, round-1-critic.md:116,269-270, round-2.md:3-24, round-4-recensus.md:35,65, round-5.md:9-13,115-122; SCORECARD.md:21,134-188; corpus/knowledge/free-tier-provider-limits.md:1,55; /home/vgpnk/Projects/shokunin/.tower/worktrees/kaika/fleet-ledger/.ufo/waves/kaika-w1/kama-state.md §4
verified-at: 2026-10-19 — lane repo at 35e9175; every table pointer re-opened read-only by the scribe seat (no endpoint contacted by that seat; the L1's own gate runs are disclosed in §Contested L1 gate runs)
recheck: next correction round — re-run the per-row checks and the stale-anchor count; re-open kama-state.md §4
## Mistakes

| # | class | mistake | evidence pointer | captured-by criterion or none | fix |
|---:|---|---|---|---|---|
| 1 | C02/I | Port resolver read the `30` of `Qwen3-Coder-30B` as a port (synthesized port `30`) | `LOG.md:40`; `SKILL.md:286-291` | `SKILL.md:286-291` (anti-pattern 11) | Keep a fixture asserting no port is parsed from a model name; anti-pattern stays. |
| 2 | C04/I | `--json` path died on a trailing comma left by `$(…)` newline stripping | `LOG.md:41-42` | fixture `tools/test-snapshot.sh` (JSON contract; no trailing-comma case) | Add a trailing-comma fixture; hold the command exit separately from the parser exit. |
| 3 | C03/M | Lowercase `~/projects` sweep missed the whole `ufo-fsd-alpha` checkout | `LOG.md:66-67`; `corpus/knowledge/consumer-registry.md:30` | none | Canonicalize case before a sweep; record `pwd -P` and inode of each root. |
| 4 | C04/M | Bare `ss -tnp` cannot see listeners (`0` vs `23`) | `LOG.md:65`; `corpus/lessons/round-1.md:45` | `SKILL.md:214-219` (checklist step 4) | Keep `ss -ltn` in step 4; reject any listener claim from `-tnp`. |
| 5 | C01/M | `git remote -v` truncated by `head -2` invented a remote difference | `LOG.md:68`; `corpus/lessons/round-1.md:47` | none | Count the full set before reading a sample; no negative claim from a truncated read. |
| 6 | C01/C | Frozen route fact `m_flash` attributed to `alibaba-token-plan` instead of `charm-hyper` | `LOG.md:78`; `corpus/lessons/round-1-citations.md:17,28` | none | Re-derive a frozen host fact at its live line before citing it; date the frozen row. |
| 7 | C01/C | Wording `dead` for a service that was alive but foreign (HTTP 404) | `corpus/lessons/round-1-critic.md:269-270` | KQ1 + KQ2 | Say `does not serve the model`; reserve TCP-dead for refused connections. |
| 8 | C03/C | NAT question asserted where the correct verdict was UNDECIDABLE without root | `corpus/lessons/round-1-critic.md:116,270` | none | Record UNDECIDABLE plus the exact blocked command and verbatim error; no negative assertion. |
| 9 | C10/S | Whole-file config read returned a credential line | `LOG.md:83-85` | KQ5 | Shape-only reads (`test -e`, `wc -l`, `stat`); never open config bodies. |
| 10 | C04/S | Redaction regex matched `token` inside a route alias (false positive) | `LOG.md:85-88`; `corpus/lessons/round-1.md:49` | none | Scan key-side (left of `:`) for secret names; never substring-scan values. |
| 11 | C03/C | Draft claimed `periodic` monitoring when only invocation history existed | `corpus/lessons/round-2.md:3-7`; `LOG.md:109` | KQ4 | Invocation history is not a scheduler; name the absence of a timer. |
| 12 | C04/I | `set -e` turned legitimate drift exit 2 into a premature script exit | `corpus/lessons/round-2.md:21` | fixture `tools/test-snapshot.sh` | Capture the exit outside a `set -e` pipeline; fixture asserts exit 2. |
| 13 | C11/I | `index.jsonl` duplicated derivable dated-file metadata (dead weight) | `corpus/lessons/round-2.md:24`; `LOG.md:186` | none | No persisted state derivable from an authoritative artifact; simplify at review. |
| 14 | C01/C | 46 stale `current` lines survived round-1 review; 15 named lines still read as current at round 10 (dossier said 11) | `corpus/lessons/round-4-recensus.md:35`; count below | none | Run the count below each correction round; append dated corrections at end of file; target 15 to 0. |
| 15 | C11/P | Round-3 fleet report absent; counter/report gap recorded only in round 4 | `corpus/lessons/round-4-recensus.md:65`; `test -e .ufo/reports/round-3/kama.md` | none | Record a missing report in the same round's entry; reconcile report set to log headings by command. |
| 16 | C11/P | Relaunch reused `round-1` while the log history was at round 4 | `LOG.md:273`; `corpus/lessons/round-5.md:9-13` | none | Relaunch appends `round-(max+1)` with a start revision; never reuse a label. |
| 18 | C12/P | Generated prompt said `calibration`; `MISSION.md:29` said `freshness` | `LOG.md:273-280` | none | Mission file is the only axis authority; quote it in the round header. |
| 19 | C02/C | Index row claims the free-tier entry covers rounds 6–17; the entry measures 6–9 | `corpus/README.md:47`; `corpus/knowledge/free-tier-provider-limits.md:1,21-27` | KQ3 | Index rows name only measured ranges; re-measure before editing the index. |
| 20 | C02/C | SCORECARD depth row says 323 lines, 11 signatures, 14 steps; file has 342, 12, 8 | `SCORECARD.md:21`; `wc -l SKILL.md` | KQ3 | Re-measure every count in an index row; date the row. |
| 21 | C13/M | Round 7 re-sent 64 seats to a wire id that had just failed 64/64 plus a 1-seat probe at 18:32–18:33Z | `SCORECARD.md:149-160`; `LOG.md:466-477` | none | Probe one seat of the exact wire id before any multi-seat wave; re-dispatch only after the input changes. |
| 22 | C06/M | Round 9 re-attempted `glm-5.3-flash-free` two minutes after round 8's host-catalog rejection; catalog byte-identical | `SCORECARD.md:177-188`; `LOG.md:479-506` | none | List the dispatch catalog and pin its revision before dispatch; an identical failure is a stop, not a retry. |
| 23 | C04/M | Round-5 wave validator's route-family check was unprobed and did not enforce the alias bindings it was trusted for | `corpus/lessons/round-5.md:115-122` | none | Require a negative control for every gate; an unprobed validator cannot certify a wave. |
| 24 | C11/M | Free-tier entry uses craft round numbers 6–17 and reserves rounds 10–13 for loop 2; round 10 is this craft round | `corpus/knowledge/free-tier-provider-limits.md:1,55`; `corpus/README.md:47` | none | Give load-test loops a separate namespace (`L1.1`); renumber the pending loops. |
| 25 | C10/S | L1 ran `bash tools/kama-probe.sh listeners` during the pre-dispatch gate refresh outside explicit census scope; output discarded | `SKILL.md:232-236` (step 7); `LOG.md` §round 10 (L1 slip record) | `SKILL.md:232-236` (checklist step 7) | Do not run census commands outside declared scope; if run by mistake, record it and exclude the output from evidence. Now KQ10. |

Dropped vs `kama-state.md` §4: #17 (`documentation delta treated as progress`) — its own pointers (`corpus/lessons/round-5.md` §Gate; `SCORECARD.md` §Admission) say the lane admitted BLOCKED and added zero rounds, so the stated mistake is contradicted by its evidence. Corrected: #14's `11 lines` re-measures to 15 with the command below.

```sh
sum=$( { grep -rnE 'PROVINCE\.md:(22-26|22-30)' corpus/; grep -nE 'kama-probe\.sh:(47-48|386|338-350)' corpus/knowledge/endpoint-identity.md; grep -n 'opencode.json:158' corpus/knowledge/drift-timeline.md; grep -n 'currently has no `tools/kama-probe.sh`' corpus/lessons/probe-mutation-matrix.md; grep -n '323 lines' SCORECARD.md; grep -n '1544771' corpus/knowledge/consumer-registry.md; } | wc -l ); printf 'stale_named_lines=%s\n' "$sum"
```

### Unlearned classes → proposed criteria

- **(a) C01/C, C03/C — docs-sourced engine claims.** Admit only when each engine statement is scoped to engine plus documented version/revision plus S-row tier and quotes its anchor; reject when a vendor/spec claim is written as a present local-runtime fact or a frozen row is cited without re-derivation. Grounded in row 6 (frozen-fact misattribution) and KQ4's fixtures-vs-integration reject condition (row 11 is its lane instance).
- **(b) C01/C — mechanical stale-anchor sweep.** Admit a correction round only when the pasteable count returns 0 and corrections are appended at END of file; reject when any uncorrected row remains or dated history is rewritten. Grounded in row 14 (46 lines survived; 15 still live).
- **(c) C03/C — privilege/tool-bounded verdicts.** Admit a claim only when its blocking command ran; when privilege or tool is denied, record `UNDECIDABLE` with the exact command and verbatim error; reject the negative assertion. Grounded in row 8.
- **(d) C10/S — census scope.** Admit only commands named in the task's declared scope; reject out-of-scope census/probe runs and exclude their output from evidence. Grounded in row 25 (this round's listener slip).
- **(e) C13/M, C06/M — dispatch pre-flight.** Admit a multi-seat wave only after a one-seat probe of the exact wire id and a catalog listing pinned by revision; reject re-dispatch after an identical failure without a changed input. Grounded in rows 21–22.
- **(f) C04/M, C04/S — gate falsifiability.** Admit a gate only after a negative control makes it fail; reject a gate whose check cannot distinguish the failure it exists to catch. Grounded in rows 23 and 10.
- **(g) C11/P, C11/M, C12/P — numbering/report integrity.** Admit a round only when round number, report path and mission axis reconcile by command; blocked attempts use a distinct namespace. Grounded in rows 15, 16, 18, 24.
- **(h) C11/I — state derivability.** Admit no persisted artifact whose contents are derivable from an authoritative source. Grounded in row 13.
- **(i) C01/M, C03/M — evidence-read completeness.** Admit a negative or scope claim only from a full-set read at a canonical path; reject head-truncated reads and case-ambiguous roots. Grounded in rows 3 and 5.

Strongest: **(b)** — it is the only proposal with a mechanical, per-round, pasteable count; it turns KQ3 prose into a gate that can fail; and it targets C01, the fleet's named dominant failure (`attribution drift, not invention`). It starts falsifiable: the round-10 base measures 15 named live lines, not 0.

## Gate

Every new `SOURCES.md` row was opened on 2026-10-19 by the round-10 seat named in `.ufo/round-10/fragments/` (rows S011–S029 by the leads scout, whose blocks are carried here). Quotes are verbatim, ≤25 words.

| id | URL | accessed | quote | location |
|---|---|---|---|---|
| S001 | https://raw.githubusercontent.com/ggml-org/llama.cpp/master/tools/server/README.md (rendered path https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md) | 2026-10-19 | "Explanation: the model is successfully loaded and the server is ready." | §GET `/health` response format, 200 branch |
| S001 (metrics) | https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md | 2026-10-19 | "This endpoint is only accessible if `--metrics` is set." | §GET `/metrics`: Prometheus compatible metrics exporter (raw README line 1131 on master @ 4c3c581) |
| S002 | https://docs.vllm.ai/en/stable/serving/online_serving/ | 2026-10-19 | "`/health` - Health check" | §Instrumentator APIs → Basic APIs list |
| S003 | https://docs.vllm.ai/en/stable/usage/metrics/ | 2026-10-19 | "Every bucket boundary creates one extra time series per metric and per label combination" | §Custom Histogram Buckets, paragraph "Bucket cardinality" |
| S004 | https://docs.vllm.ai/en/stable/api/vllm/entrypoints/serve/instrumentator/health/ | 2026-10-19 | "Render-only servers have no engine; they are always healthy." | `health(raw_request)` source block comment |
| S005 | https://docs.vllm.ai/en/stable/features/quantization/ | 2026-10-19 | "This compatibility chart is subject to change as vLLM continues to evolve and expand its support" | note directly under the §Supported Hardware table whose GGUF row reads Volta/Hopper/Ada/Ampere/Turing and AMD GPU supported, Intel GPU, x86 CPU and Arm CPU not |
| S006 | https://docs.sglang.io/docs/basic_usage/native_api | 2026-10-19 | "`/health_generate`: Check the health of the server by generating one token." | §Health Check bullet list |
| S007 | https://docs.sglang.io/docs/references/production_metrics | 2026-10-19 | "For streaming requests it ends when the first output arrives after detokenization, which may contain no printable text." | §Language model metrics, `sglang:time_to_first_token_seconds` definition paragraph |
| S008 | https://docs.sglang.io/docs/advanced_features/quantization | 2026-10-19 | "If you use a pre-quantized model, do not add --quantization to enable online quantization at the same time." | warning paragraph after the §Quantization intro defining offline vs online quantization; §Platform Compatibility table lists gguf Yes for NVIDIA GPUs and Ascend NPUs, No for AMD GPUs |
| S009 | https://docs.ollama.com/api/introduction | 2026-10-19 | "Ollama's API isn't strictly versioned, but the API is expected to be stable and backwards compatible." | §Versioning paragraph (Base URLs table at §Base URLs) |
| S010 | https://docs.ollama.com/api/openai-compatibility | 2026-10-19 | "Ollama supports a subset of the OpenAI API" | opening paragraph; endpoint details under §Endpoints `/v1/models` |
| S011 | https://docs.ollama.com/api/tags | 2026-10-19 | "Fetch a list of models and their details" | `List models`; OpenAPI operation `GET /api/tags` |
| S012 | https://docs.ollama.com/api/ps | 2026-10-19 | "Models currently loaded into memory" | `List running models`; `GET /api/ps` 200 response description |
| S013 | https://docs.ollama.com/import | 2026-10-19 | "Ollama does not quantize GGUF models during import. Prepare and quantize them first with a GGUF tool" | §Importing a GGUF model, first paragraph |
| S014 | https://github.com/ggml-org/ggml/blob/master/docs/gguf.md | 2026-10-19 | "It is not intended to be perfectly parsable in the field due to the diversity of existing gguf filenames." | §GGUF Naming Convention, second paragraph |
| S015 | https://github.com/ggml-org/llama.cpp/blob/master/tools/quantize/README.md | 2026-10-19 | "Quantization is done in two phases: Convert the original model to GGUF format. Quantize the converted GGUF file." | §Overview, first bullet block; also opened §Quantize the GGUF and §Quantization tables |
| S016 | https://developers.openai.com/api/reference/resources/models/methods/list | 2026-10-19 | "Lists the currently available models, and provides basic information about each one such as the owner and availability." | `List models`; description |
| S017 | https://kubernetes.io/docs/concepts/configuration/liveness-readiness-startup-probes/ (301s to canonical https://kubernetes.io/docs/concepts/workloads/pods/probes/) | 2026-10-19 | "Liveness probes determine when to restart a container." | §Liveness probe under §Types of probe |
| S018 | https://prometheus.io/docs/practices/naming/ | 2026-10-19 | "Do not use labels to store dimensions with high cardinality (many different label values)" | §Labels, CAUTION block |
| S019 | https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-metrics.md | 2026-10-19 | "Time per output token generated after the first token for successful responses." | §Generative AI model server metrics, `gen_ai.server.time_per_output_token` table row |
| S020 | https://github.com/sgl-project/sglang/releases/tag/v0.5.22 | 2026-10-19 | "[Fix][DP] Prevent health checks from perturbing user request routing" | §Parallelism & Disaggregation first bullet (PR #35721) |
| S021 | https://llm-d.ai/docs/operations/readiness-probes | 2026-10-19 | "The `/v1/models` endpoint is model-aware and indicates true readiness" | v0.10 page, `/v1/models Endpoint (OpenAI-Compatible)` |
| S022 | https://docs.vllm.ai/en/v0.25.0/features/per_request_metrics/ | 2026-10-19 | "The `/metrics` Prometheus endpoint exposes server-level histograms" | `Relationship to Prometheus Metrics` |
| S023 | https://github.com/vllm-project/vllm/blob/8d2cff8140eb2c5f6a7b28948c0944d11898d9d2/examples/observability/prometheus_grafana/README.md | 2026-10-19 | "Navigating to `http://localhost:8000/metrics` will show the raw Prometheus metrics being exposed by vLLM." | `Launch` |
| S024 | https://github.com/sgl-project/sglang/blob/678913a0f029394ad1f4ee64d1439421e9ea56ef/docs/docs/advanced_features/sgl_model_gateway.mdx | 2026-10-19 | "SGLang Model Gateway is a high-performance model-routing gateway for large-scale LLM deployments." | opening paragraph; `Overview` |
| S025 | https://docs.ollama.com/api/usage | 2026-10-19 | "All timing values are measured in nanoseconds." | `Usage` |
| S026 | https://github.com/ggml-org/llama.cpp/pull/18001 | 2026-10-19 | "the `/v1` is reserved for openai-compatible API" | `Conversation`, maintainer comment by @ngxson on 2025-12-14 |
| S027 | https://github.com/ollama/ollama/issues/3144 | 2026-10-19 | "It would be nice of ollama had a `/metrics` endpoint for collecting metrics for prometheus or other monitoring tools." | issue description, opened 2024-03-14 |
| S028 | https://github.com/ggml-org/llama.cpp/issues/4746 | 2026-10-19 | "I'd like the server to have a /health endpoint." | issue description, opened 2024-01-03 |
| S029 | https://github.com/vllm-project/vllm/issues/36960 | 2026-10-19 | "When a GPU encounters a page fault or illegal memory access, the process remains alive but inference becomes impossible." | issue description, opened 2026-03-13 |
| S030 | own-work: `bash tools/kama-probe.sh check` (L1 run, 2026-10-19T21:35:49Z) | 2026-10-19 | "registry_rows_evaluated=3 model_ok=0 drift=3 exit=2" | `.ufo/round-10/gates/check.json` stdout, final line — row REJECTED, see §Contested L1 gate runs |

Revision pins for unversioned docs pages (S006, S007, S008, S009, S010, S018) were re-derived from each page's upstream source file and its last commit (per-file commit atom feeds); the S008 source moved from `quantization.md` (50ed4c01) to `quantization.mdx` (bdf8886a). The S009 quote uses straight ASCII apostrophes, as on the page.

## Admissions (QUALITY KQ1–KQ10)

| Entry | Decision | Basis |
|---|---|---|
| `knowledge/runtime-health-surface-matrix.md` | admit | uncovered in the lane map (README §Known gaps: llama.cpp-only runtime evidence); 8 opened tier-A rows (S001 S002 S004 S006 S009 S010 S017 S020); clearance block KQ1–KQ10; boundary: gateway health → kumitate, quality → kengaku |
| `knowledge/serving-metrics-crosswalk.md` | admit | uncovered fleet-wide (connector scan); every metric name verbatim from S001/S003/S007/S019; OTel marked Development; never identity evidence |
| `knowledge/gguf-runtime-compatibility-boundary.md` | admit | GGUF/quantization compatibility row absent from the map; S005/S008 hardware-conditional support stated; served-id normalization unchanged; quantization quality → kengaku |
| K02 served-identity crosswalk, K05 context capacity | deferred (not rejected) | rows S011 S012 S016 are opened and `queued`; K05 needs an authorized runtime for the declared-vs-served comparison (README §Frontier) |

## Rejected — evidence of taste

- Rows: S024 (gateway routing is kumitate's), S026 (open PR ≠ released contract; a search summary called it merged — the opened page decided), S027 and S028 (community requests do not establish released behavior or a universal convention), S030 (contested L1 gate sample, below).
- Candidate rules from the ART dossier, still rejected: one universal `/health` pass rule; "OpenAI-compatible" read as full behavioral equivalence; a completion request as an identity probe; a GGUF filename regex as identity/support; ranking quantizations from published tables.

## Corrections (claim C1)

Ledger `.ufo/round-10/audit/stale-anchors.tsv`: 50 rows (42 active, 8 historical — in-repo or host targets whose cited lines moved) across 12 files, each corrected by an end-of-file entry under `## Corrections — round 10 (2026-10-19)`; dated lines untouched. Review-driven changes before landing: A12 withdrawn as a false positive (the cited range's tail `tools/kama-probe.sh:1005-1007` still carries the claim's comment); 18 circular checks (A05, A06, A19–A29, A31, A33, A35, A36, A38) rewritten to observe the cited object shape-only (`test -e`, `wc -l`); A18 reduced to `wc -l` after the executor read 4 body lines of `~/Projects/ufo-fsd-alpha/config/l1-max-context.yml` (a read-only domain source tree, not a credential surface; recorded as a KQ5-class slip, its content-derived wording withdrawn); A16's anchor made fleet-root-relative; A51 added from the critic's sweep (`consumer-registry.md:101`, offset UNDECIDABLE without a body read). Out of scope and named as debt: historical pointers to deleted host files (already dated in `consumer-registry.md` §Errata), and stale anchors in `SKILL.md` (scout: 13 of 14 anchor-bearing lines), `PROVINCE.md:11`, `SCORECARD.md:21,42`.

Counting command (run from the lane root; prints ledger rows, then uncorrected rows — a header-only ledger prints `rows=0`, so the 0 is never vacuous):

```sh
tab=$(printf '\t'); cr=$(printf '\r'); echo "rows=$(tail -n +2 .ufo/round-10/audit/stale-anchors.tsv | grep -c .)"
tail -n +2 .ufo/round-10/audit/stale-anchors.tsv | while IFS="$tab" read -r id f line class old chk new || [ -n "$id$f$line$class$old$chk$new" ]; do id=${id%"$cr"}; [ -n "$id" ] || continue; if ! grep -F -e "(round 10, $id): \`$old\`" "$f" >/dev/null 2>&1; then printf 'uncorrected %s %s:%s\n' "$id" "$f" "$line"; fi; done | wc -l
```

Before the corrections landed the loop printed 50 (A12 then counted; the final ledger after A12's withdrawal and A51's addition is 50 rows); after, 0.

## Closed plan claim

`.ufo/round-10/plan.json` claim 2 ("refresh the gate evidence bundle" as operability) is closed, not claimed: re-running unchanged gates re-verifies state (a freshness signal) and moves no operability capability. The bundle exists at `.ufo/round-10/gates/` but is not evidence for any admitted claim (next section).

## Contested L1 gate runs

Before dispatch the L1 ran the lane checklist: `check` (twice, text and `--json`), `consumers`, `systemctl --user show qwen-coder.service`, `ss -ltn` on 8080/34113, `tools/test-snapshot.sh`, an isolated `snapshot --history /dev/shm/…`, and — outside checklist step 7's scope — `listeners` (Mistake 25). Results: 3 rows DEAD connection-refused, exit 2; consumers exit 0; fixtures `RESULT pass=24 fail=0`; unit not-found; no listener on either port; the fresh rows match tracked baseline `20261014T124232Z`. The sentinel and critic hold that the campaign's documentation-only rule covers the L1 too, so no admitted claim rests on these samples and S030 is rejected; the question goes to L0.

## Status changes

None in place: every registry row is new this round.

## Review record (lane L2s — not non-author verification)

- **Reviewer** (FAIL, 6 blocking): mid-file insertions → moved to appended blocks; circular `stale_check`s → rewritten shape-only; A18 body read → `wc -l` only; S030 vs the header claim → header disclosed, S030 rejected; five unversioned anchors → pinned to upstream commits; missing §Gate → added; KQ6 clearance → added to each entry. Non-blocking: the S009 apostrophe nit was checked and the page uses ASCII `'` (fragment correct); `;`-chained checks remain (one pipeline per row was not enforced).
- **Critic**: plan claim 2 falsified as operability (agreed: closed). C1 "falsified" on four points — missed `consumer-registry.md:101` (now A51), A16's unresolvable pointer (fixed), class enum (normalized to `active`/`historical`), and a vacuous-pass counter (the command now prints `rows=`). Disputed and left for the non-author check: A20 (the critic reads "No writer exists for #1/#6" as still literally true; the lane reads the open-gap bullet's premise as stale because consumers #1 and #6 no longer exist). C3 "weakened": the critic holds that `SOURCES.md` is a coverage move, not a capability; the campaign binding names it a capability whose row enters only on a clean census — the operator rules. The counter still does not validate `new_pointer`s; reviewers sampled them by hand.
- **Sentinel**: HIGH — the L1 gate runs (see §Contested L1 gate runs); MEDIUM — A18 body read (fixed) and mid-file insertions (fixed); LOW — newline-only rewrites of three files' last lines (recorded in `LOG.md`); credential scans of round-10 bytes: 0 hits.
- **Connector**: 0 sibling `SOURCES.md` rows share these URLs; boundary sentences adopted (kumitate: gateway/routing; kengaku: quantization quality; kagi: auth).
