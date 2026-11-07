# CN01SiblingOverlap — kama round 92 wave 1 (read-only cross-lane scan)

Referents: `SKILL.md:1925-1941` (`## Serving defaults (round 92 revision)`, R01–R15); `plans/round-92-claims.md`
§C2 (probe change: `jstr` / `router_refine` / `served_persist`); province from `PROVINCE.md` §Domain/§Refuses and
`corpus/knowledge/cross-lane-scope.md` §Adjacency rule. No lane file, service, endpoint or host config was touched;
no model was served; no tool installed or upgraded. Load at scan time `load average: 39.89`; no timing claims.
## Scope

20 sibling lanes under `/home/vgpnk/Projects/shokunin/*-shokunin` (all but `kama-shokunin`), surfaces `<lane>/SKILL.md`,
`<lane>/corpus/knowledge/*.md`, `<lane>/corpus/SOURCES.md`, `<lane>/PROVINCE.md` where a lane names kama, plus the
`corpus/lessons/` files carrying a handoff (kake round 50). Terms: llama.cpp / llama-server / Ollama / vLLM /
SGLang; ports 9931, 11434, 34113, 8080; timeouts; n_parallel / slots / `-np` / `--parallel`; keep-alive; queue and
model-count limits; JSON escaping and large/long-answer handling; consumers of `kama-probe.sh`. Default-value
referent: pinned `/home/vgpnk/.local/opt/llama-b12177/llama-server --help` (sha256 `ba272ee3446d…b362b0`; `--help`
only, no listener started).

## Commands and outputs (true exit codes; receipts in the out dir)

- `grep -rniE 'llama\.cpp|llama-server|ollama|vllm|sglang' */SKILL.md */corpus/{knowledge/*.md,SOURCES.md}` — rc 0,
  39 hits; in the set only kengaku (llama.cpp, vLLM docs), kagi (llama-server endpoints), kotoba (`~/llama.cpp`).
  kake's one Ollama row is in `corpus/lessons/` (N7), outside the set.
- `grep -rniE '\b(9931|11434|34113|8080)\b' …` — rc 0, 129 hits, all in kagi/kengaku/kumitate and all 34113 or
  8080. Word-boundary re-check: no real 9931/11434 statement in the set (only sha256 substrings); outside it the only
  real 11434 statement is kake's round-50 lesson (N7); tabi's lessons carry it only inside hashes.
- `grep -rniE 'n_parallel|total_slots|--parallel|-np [0-9]' …` — rc 0; the only `n_parallel` hits are
  `test_column_parallel_linear` identifiers (kengaku `tb2-torch-tensor-parallel-offline.md:17,20`); `total_slots`
  only kengaku `served-endpoint-identity-pin.md:20,37` and `PROVINCE.md:15`. No sibling states R07's parameter.
- `grep -rniE 'json escap|json unescap|\\u[0-9a-fA-F]{4}' …` — rc 0, 76 hits, none about the probe's output.
- `grep -rn 'kama-probe' …` — rc 0, 2 hits, both tameshi file-existence census rows; no lane consumes the probe.
- `sha256sum …/llama-server` — rc 0, `ba272ee3446d9b98c9150c79667e6a8b217f25ee58ce0c6156cc96d2b5b362b0`.
- `llama-server --help | grep -E '--temp|--top-k|--top-p|--seed|--parallel|--port|--timeout|--sse-ping-interval|--cache-ram|--models-max'`
  — rc 0: `port 9931`, `timeout 3600`, `sse-ping-interval 30`, `cache-ram 8192`, `models-max 4`, `parallel -1`,
  `temp 0.80`, `top-k 40`, `top-p 0.95`, `seed -1`.
## Findings

**D1 — DEFECT (sibling; not a kama row): kengaku publishes a "server defaults" row that does not match the pinned
binary's defaults, on the surface its own province gives to kama.** `kengaku-shokunin/corpus/knowledge/
served-endpoint-identity-pin.md:38` — `generation defaults | temperature=0.1, top_k=50, top_p=0.95,
seed=4294967295 (server defaults)`, build `b1-39ebd2` (`:39`; process `:40` shows 3 of 16 argv tokens). The same lane
says `absent → llama-server default 0.8` (`corpus/knowledge/bench-arena-round7-scaffold-ablation.md:21`, TSV row D1b,
which agrees with the binary). b12177 `--help` prints `--temp … (default: 0.80)` and `--top-k … (default: 40)`;
top_p 0.95 and seed -1 (4294967295 as u32) do agree. So under the binary-default reading two of four values misstate
the default; under the host-state reading the row is a *flagged* server's effective sampling (argv not fully quoted)
labelled "(server defaults)". Either way it needs the R07/R08 distinction kama makes for `n_parallel` (parser default
vs startup-resolved value). kengaku `PROVINCE.md:15` says "flag authority is kama's (serving plane)" and `:158` says
kengaku "never remediates flags (`--kv-unified`, q4_0 KV, `--parallel`)"; the endpoint is `ABSENT 2026-11-04`
(`PROVINCE.md:15,1028`), so a capture-time host fact is phrased as a defaults claim. Kama's 15 rows carry no sampling
parameter; nothing in the fleet corrects it.
**D2 — DEFECT (sibling, stale present-tense wording): kagi's executable header still puts the model on 8080.**
`kagi-shokunin/SKILL.md:9` — "fixed model `qwen-local/Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS` at `127.0.0.1:8080`";
the same file `:43` records "port 8080 was a Jitsi videobridge on 2026-09-28 while llama-server served the model on
34113", and `corpus/knowledge/handler-trust-boundary.md:131` says the overlay baseURL is 8080 "but today's model is
`llama-server` on 34113 and 8080 answers 404". This is consumer-pin drift already in kama's registry
(`cross-lane-scope.md` consumer table); under R01, 8080 is neither the default (9931) nor the live listener.
**N1 — NOTE, agrees: slots = 4 at another build.** `kengaku-shokunin/PROVINCE.md:15`, `served-endpoint-identity-pin.md:37`
— `slots 4` (`total_slots=4`) on `b1-39ebd2` with no `-np` in the quoted argv; `:35` gives the 1234 router as
`--models-max 2` over 5 ids. Agrees with R08 (startup 4 outside the router role) and R06's caveat (4 is only the
default; this router's 2 is argv-cited). Different build: corroboration, not verification.
**N2 — NOTE, agrees: explicit concurrency statements.** `kengaku-shokunin/SKILL.md:485-488`,
`corpus/knowledge/eval-prior-art-calibration.md:23`, `bench-arena-round12-ladder.md:237`: "8 slots at temp 0" and a
5–10-request burst horizon. The 8 is an explicit invocation; the horizon is the queueing R08 predicts at 4 slots.
**N3 — NOTE, duplicates an older pin: llama.cpp server README @ b7200.** `kengaku-shokunin/corpus/SOURCES.md:193`
(S178) pins `tools/server/README.md` @ b7200 (`ab49f094…`) for `/v1/models`, `/props`, `/health` and "default `id` =
path to model file … `--alias`" — same surface as kama's served-model reconciliation, older pin, no value conflict.
**N4 — NOTE, same 3600 s on a different object: kagi's client timeout.** `kagi-shokunin/corpus/knowledge/
janitor-env-contract.md:18`, `janitor-command-surface.md:63`, `handler-on-disk-state.md:110` —
`THE_JANITOR_REQUEST_TIMEOUT` default `3600` s (client.py L74). Equal to R02 numerically but a client bound; R02's
probe decision ("a probe timeout is the probe giving up") keeps them apart.
**N5 — NOTE, large-answer handling in a fleet consumer.** `kumitate-shokunin/corpus/knowledge/ops-watchers.md:400-412`
— one `fetch` to `config.backend.endpoint` (`http://127.0.0.1:34113/v1/chat/completions`, `:402`), prompt cap
`12_000` B (`:408`), reply through `readBoundedJson` capped by `MAX_CHAT_RESPONSE_BYTES = 1_048_576` (`:410`), model
echo checked. Duplicates kama's registry row `$UFO_SRC/config/the-tick.machine.json:16`; a different consumer from
the C2 cells (1.9M-byte ids).
**N6 — NOTE, duplicates kama's registry pin: local-helper 34113.** `kumitate-shokunin/corpus/knowledge/
remaining-scripts-census.md:567` — `scripts/local-helper.mjs:8` `DEFAULT_URL http://127.0.0.1:34113`, `MAX_INPUT_BYTES`,
model output re-validated (`model_output_invalid`). Same pin kama's `PROVINCE.md` lists.
**N7 — NOTE, handoff that agrees: Ollama's 11434.** `kake-shokunin/corpus/lessons/round-50-verifier-spotcheck.md:192`
staged Ollama's OpenAPI and rejected it because "`servers: url http://localhost:11434` — local model serving, which
kake `PROVINCE.md:41` assigns to kama"; `kake-shokunin/PROVINCE.md:47,355` repeat the assignment. Agrees with R09 at
a second, different statement (client `servers` URL, not the Go `defaultPort`). R09–R13 are the fleet's only Ollama
defaults.
**N8 — NOTE, out of province: HTTP `keep-alive` header lists.** `kake-shokunin/corpus/knowledge/freshening-304.md:194`
and `tabi-shokunin/corpus/knowledge/webdriver-bidi-firefox-runtime-round-35.md:235,238` concern header/caching
semantics, not R15's vLLM idle-connection timeout.
**N9 — NOTE, out of province, same defect class as `jstr`: JSON escaping lessons.** `kotoba-shokunin/corpus/knowledge/
harness-verifier-round10.md:150` (raw-byte match 16/17 vs `json.loads` 17/17); `chousa-shokunin/corpus/knowledge/
claim-record-fields-r33.md:55` (`"l\u0069ne"` is not the plain key); `kumitate-shokunin/corpus/knowledge/
distill-and-l3.md:12` ("injective without JSON escaping"); `revenger-shokunin/corpus/knowledge/
utf16-unpaired-surrogates-in-resource-names.md:81` (`\uDE00` legal JSON). None reads or asserts anything about the
probe's output.
**N10 — NOTE, probe visibility only.** `tameshi-shokunin/corpus/knowledge/fleet-suite-census.md:625` and
`fleet-kill-rate-ledger.md:127` name `tools/{kama-probe,test-snapshot}.sh` as file existence only ("gate-ness and
measurement state are U"). No lane consumes `kama-probe.sh` output, so the C2 change (D1–D9 differential cells) has
no duplicate or rival in the sibling corpora.
**P1 — NOTE, province routing (no lane claims the surface).** kumitate `PROVINCE.md:32,48,75`; tabi `:192` ("no shared
surface"); mori `:15,67`; tsukuroi `:46,122` (ADJ-01/OUT-002 cites kama's served-model reconciliation); tameshi
`:18`; mado `:15`; kotoba `:66`; kagi `:96`; kake `:47`. Only kengaku both routes the serving plane to kama and
states defaults on it (D1).

## Proposed move (one, bounded; adjacency)

Evidence: D1 + N1 + N7. Axes: **adjacency 7** (primary), **depth 7** (secondary — a defaults statement on kama's
surface gets the R07/R08 treatment); operability, coverage and calibration unharmed. Move: land a dated cross-lane
defaults note in `corpus/knowledge/serving-thresholds.md` §Round 92 revision (never in the frozen `SKILL.md` table)
recording (i) kengaku's `b1-39ebd2` row labelled "(server defaults)" whose temp 0.1 / top-k 50 are not the b12177
`--help` defaults (0.80 / 40) while top_p 0.95 and seed -1 agree; (ii) kagi's client 3600 s is not R02's server read
timeout; (iii) kake's refused Ollama OpenAPI `servers` URL agrees with R09 at 11434 and is kama's to open; then hand
the relabel request to kengaku. Risks: touching the 15-row table breaks `round92-server-defaults.py` (`rows=15`,
`supersedes=14`) — the note stays outside it; 0.1/50 may be deliberate argv on a dead endpoint, so judge the label,
not the values; the pin is `ABSENT 2026-11-04`, so date the note and do not use it as live evidence; kama must not
absorb kengaku's eval surface. Verification: re-run the C1 counter at M1 and require `rows=15 bound=15 supersedes=14
help_disagree=0`, exit 0; re-read the cited `--help` lines against sha256 `ba272ee3…b362b0`; confirm kengaku's files
are untouched by kama.
## Deliverables (`.ufo/waves/round-92/w1/out/CN01SiblingOverlap/`)

- `scan-receipts.txt` — scan commands, hit counts, first-stage exit codes, lanes, and the binary `--help` read.
- `overlaps.tsv` — 15 machine-readable rows (D1, D1b, D2, N1–N10, P1).

VERDICT: holds — no sibling statement contradicts any R01–R15 value or the C2 differential rule (kake's refused Ollama row and kengaku's slots-4 pin agree); the fleet's one mislabelled serving-defaults row is kengaku's, handoff material for kama, not a defect in kama's frozen rows.
