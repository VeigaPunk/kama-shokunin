# SCR01LessonSources — round 84 w1 scoped report

## Behavior and axes

Axes: calibration and coverage. Produced prose drafts only; L1 must integrate and derive terminal claim verdicts. Personally fetched four admitted source bodies with curl this round. The missing b7200 document resolves at tools/server/README.md (200); examples/server/README.md returns 404. All three specified newest-side received digests match the round-83 recorded digests. No endpoint sampled, runtime invoked, product code edited, git mutation, commit, push, install or system change.

## Artifacts and touched surfaces

All new files are inside `.ufo/waves/round-84/w1/out/SCR01/`:

- `round-84-lesson.md`: full lesson draft, four Gate rows with complete digests, six correction lines, holds F6/F7, Mistakes, Frontier, explicitly provisional stale-lane and both assimilation wording variants.
- `sources-append.md`: four 11-column tier-A mined source rows S572-S575; 30d cadence and required used-by paths.
- `matrix-addition.md`: documentary S574 readiness/ping addition, provenance trio and paused-state distinction.
- `register-row-introduction-correction.md`: R83V4 appended correction preserving the cosmetic-edit limit.
- `coverage-rows.md`: R83V5 actual coverage rows plus dated frontier disposition table.
- `quality-row.md`: exact KQ136 append draft; explicitly names KQ27 in supersession.
- `received-documents/`: all five received bodies, including the 404 alternative-path body. These retained bytes, not a temporary path, support the Gate digests.
- `SCR01LessonSources.md`: this report.

Intended production surfaces are `corpus/lessons/round-84.md`, `corpus/SOURCES.md`, `corpus/knowledge/runtime-health-surface-matrix.md`, `corpus/knowledge/register-row-introduction.md`, `corpus/README.md`, `corpus/QUALITY.md`; none was changed by this seat.

## Commands, outcomes and provenance

Shell invocation 1 (exit 0):

```sh
wc -l /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/QUALITY.md /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/knowledge/runtime-health-surface-matrix.md /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/knowledge/register-row-introduction.md /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/README.md; git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse master
```

Counts were 673, 650, 145, 34, 1787 (3289 total); master was `eb03a64bcd8e2faab0f4f9bcdc55bfc5c1ed2c85`. This does not establish ahead/behind.

Shell invocation 2 (exit 0):

```sh
S=/fast/scratch/hyaku/kama-r84/SCR01LessonSources; mkdir -p "$S/dl"; cd "$S/dl"; echo "== b7200 tools/server/README.md"; curl -sS -w 'code=%{http_code} bytes=%{size_download}\n' -o b7200-tools-server-README.md https://raw.githubusercontent.com/ggml-org/llama.cpp/b7200/tools/server/README.md; echo "exit=$?"; echo "== b7200 examples/server/README.md"; curl -sS -w 'code=%{http_code} bytes=%{size_download}\n' -o b7200-examples-server-README.md https://raw.githubusercontent.com/ggml-org/llama.cpp/b7200/examples/server/README.md; echo "exit=$?"; echo "== b12111 tools/server/README.md"; curl -sS -w 'code=%{http_code} bytes=%{size_download}\n' -o b12111-tools-server-README.md https://raw.githubusercontent.com/ggml-org/llama.cpp/b12111/tools/server/README.md; echo "exit=$?"; echo "== sglang v0.5.23 native_api.mdx"; curl -sS -w 'code=%{http_code} bytes=%{size_download}\n' -o sglang-v0.5.23-native_api.mdx https://raw.githubusercontent.com/sgl-project/sglang/v0.5.23/docs/docs/basic_usage/native_api.mdx; echo "exit=$?"; echo "== vllm v0.33.0 prefix_caching.md"; curl -sS -w 'code=%{http_code} bytes=%{size_download}\n' -o vllm-v0.33.0-prefix_caching.md https://raw.githubusercontent.com/vllm-project/vllm/v0.33.0/docs/design/prefix_caching.md; echo "exit=$?"; sha256sum b7200-tools-server-README.md b7200-examples-server-README.md b12111-tools-server-README.md sglang-v0.5.23-native_api.mdx vllm-v0.33.0-prefix_caching.md
```

Every curl explicitly printed exit=0, including HTTP 404 (no --fail flag). HTTP/body outcomes respectively: 200/72181, 404/14, 200/136429, 200/18295, 200/13916. sha256sum exited 0; admitted body hashes are reproduced in each Gate row. The 404 body hash was `d5558cd419c8d46bdc958064cb97f963d1ea793866414c025906ec15033512ed`.

Shell invocation 3 (exit 0; diagnostic location/count reading, not a product gate):

```sh
cd /fast/scratch/hyaku/kama-r84/SCR01LessonSources/dl && echo "== b7200 health lines"; grep -n -i 'health' b7200-tools-server-README.md | head -30; echo "== b7200 line count"; wc -l b7200-tools-server-README.md; echo "== b12111 lines 478-484"; sed -n '478,484p' b12111-tools-server-README.md; echo "== b12111 line count"; wc -l b12111-tools-server-README.md; echo "== sglang lines 107-114"; sed -n '107,114p' sglang-v0.5.23-native_api.mdx; echo "== sglang line count"; wc -l sglang-v0.5.23-native_api.mdx; echo "== vllm lines 1-4"; sed -n '1,4p' vllm-v0.33.0-prefix_caching.md; echo "== vllm line count"; wc -l vllm-v0.33.0-prefix_caching.md
```

Located b7200 header/quote at 404/406, b12111 header/quote at 480/482, SGLang health header/ready/ping at 108/111/112, vLLM quote at 3. Line counts respectively 1530, 2620, 471, 236. Individual subcommand exit codes were not captured; only invocation exit 0 is asserted. Tool-policy deviation: shell grep/head/sed were used for these reads instead of specialized read/search. The two SGLang lines and b7200 quote were subsequently read with the read tool; no product check was rerun.

Shell invocation 4 (exit 0):

```sh
awk -F'|' '/^[[:space:]]*\|[[:space:]]*S[0-9]/ && NF!=13 {n++} END{print n+0}' /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-84/w1/out/SCR01/sources-append.md && cp -R /fast/scratch/hyaku/kama-r84/SCR01LessonSources/dl /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-84/w1/out/SCR01/received-documents && rm -rf -- /fast/scratch/hyaku/kama-r84/SCR01LessonSources
```

Required column check printed `0`. The && chain completed successfully: received bodies retained and own scratch removed. No scratch clone was needed.

Read/glob/grep tools inspected the complete frozen plan and round-83 lesson, SOURCES contract and final rows, QUALITY KQ27/KQ134/KQ135, README frontier/tail, both knowledge targets, relation register, SCORECARD head and four stored final receipts. These tool operations do not expose process exit codes. An initial strict regex search for S566-S571 returned no matches; a looser S571 search located rows 321-326. No source absence was inferred from the empty search.

Stored receipts personally read, not rerun: round-83 c1-legA/c1-pending/c1-delta carry measured revision `1d90dc816e200481c7a136934a35e8c418ec4501`, adverse exit 1 and late=22/window=7/falls=no/delta=113/103/10/10; c3-selftest carries pass=14 fail=0, EXIT=0. Other fact witnesses are attributed to the frozen table, not independent execution.

EX04Selfrecord confirmed by peer message that F2 uses comma packing and whole contiguous composite-token fix matching; six lines only, F6/F7 hold; F3 uses four values under L1's explicit instruction. Peer confirmation is provenance of integration syntax, not a counter pass.

## Gates and known limits

Exercised: curl document fetches, SHA-256 calculations, quote location, explicit requested awk shape check. Not run: source census, any C1/C2/C3 instrument, selftest, pre-report gate, lane-sync comparison, assimilation-package inspection. L1 should run census --file before appending SOURCES, then terminal integrated counters/gate after committing the production changes. No claim verdict or score promotion from this seat.

Report-path conflict (verbatim assignment text): `Write ONLY inside your own directory` versus `Report: write your scoped findings to .ufo/waves/round-84/w1/SCR01LessonSources.md`. The named delivery directory is `out/SCR01/`; this report stays inside that explicitly authorized directory instead of writing the conflicting external trailer path. L1 may relocate it.

Correction-count conflict (verbatim): `the eight correction lines` versus `F6 hold, no correction line; F7 hold, no correction line`. Delivered six corrected lines plus explicit two holds, consistent with frozen C2 target corrected=6 and EX04 confirmation.

F3 textual conflict (verbatim): frozen disposition `r83c1-delta=113/103/10` versus seat requirement `r83c1-delta=123/103/20/0->113/103/10/10`. Delivered the explicit four-cell seat token, retaining the adverse bad count; frozen plan unchanged. Canonical judge owns resolution.

## Out of scope

Production integration, fixes to SCORECARD live cells, criterion admission, registry extract creation/grading, instrument implementations, verdicts, closure and publishing remain L1/other seats' work. Stale-lane and assimilation lines are expressly requested draft placeholders, not unsupported completed observations.

## Self-evaluation

Accuracy 4: full received hashes and four personally located quotes, but integrated predicates remain unrun. Completeness 4: all named drafts plus standalone KQ row supplied; final stale-lane/assimilation wording intentionally depends on L1/scout evidence. Clarity 4: observed reads separated from frozen-table testimony; conflicts are explicit. Actionability 4: paste-ready append drafts and exact correction packing, but L1 must integrate. Conciseness 4: report preserves exact shell commands at the cost of length. Average 4.0. Highest-impact improvement is L1 replacing requested placeholders with terminal lane/scout receipts and running the integrated census/counters. Would the user agree: expected yes for a drafting seat; not a claim that round 84 passed.
