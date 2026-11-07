# CN01SiblingOverlap — kama round 93 wave 1 (cross-lane scan & registry audit)

## Scope

Read-only scan of 20 sibling lane repos under `/home/vgpnk/Projects/shokunin/*-shokunin` (all except `kama-shokunin`) across `SKILL.md`, `PROVINCE.md`, `corpus/knowledge/*.md`, `corpus/SOURCES.md`, `corpus/lessons/*.md`, and `registry/` for any statements on llama-server listen ports (9931, 8080, 8011–8014, `LLAMA_ARG_PORT`, `AIP_MODE`), slot counts (`-np`, `n_parallel`, `kv_unified`, `--parallel`, `total_slots`), or router model-file checks (`router-model-*`, `gguf_state`, `SEEN`, `gguf_parse`) that contradict or duplicate kama's C1/C2 surface at M2 `ee19acbdabc8ac572e82ae56459c364457895b06`. Also audited kama's own `registry/endpoint-consumers.tsv` for consumer rows whose pinned port depends on a setter R16 lists without citing it. Revisions: Base B `5af794958b0f`, Freeze F `0f272a3773be`, M1 `fe5f031cb1b9`, M2 `ee19acbdabc8`, HEAD `4c4adc634ae8`. Pinned binary: `/home/vgpnk/.local/opt/llama-b12177/llama-server` (sha256 `ba272ee3446d9b98c9150c79667e6a8b217f25ee58ce0c6156cc96d2b5b362b0`). Host Linux 7.2.11-arch1-1, python 3.14, bash 5.x; `uptime` load average: 73.37, 61.14, 47.78.

## Commands and outputs (true exit codes)

- `python3 tools/round93-setter-rows.py --repo . --rev ee19acbd...` — rc 0 (verified M2 tip bindings: rows=48 bound=48 decisions=2 bound=2).
- `sha256sum /home/vgpnk/.local/opt/llama-b12177/llama-server` — rc 0 (`ba272ee3446d...`).
- `llama-server --help | grep -E '(--port|--parallel|-np\b)'` — rc 0: `--port PORT (default: 9931)`, `-np, --parallel N (default: -1, -1 = auto)`.
- Targeted surface sweep across 20 sibling lanes (239 raw hits) & deep scan across all sibling text files:
  - `\b9931\b`, `LLAMA_ARG_PORT`, `AIP_MODE`, `AIP_HTTP_PORT`, `LLAMA_ARG_N_PARALLEL`: 0 hits across all sibling lanes (rc 0).
  - `\b801[1-4]\b`: 0 hits (1 false match in tabi `round-17.md:57` was "8013 B" file size).
  - `router-model-{invalid,missing}`, `router-unloaded-autoload`, `gguf_state`, `gguf_parse`: 0 hits across all sibling lanes (rc 0).
  - `kama-probe`: 2 hits in tameshi (`fleet-suite-census.md:625`, `fleet-kill-rate-ledger.md:127`; file existence only, unconsumed).
  - `\b8080\b`: 132 hits (kagi, kengaku; legacy pins and Jitsi port collision).
  - `\b34113\b`: 73 hits (kumitate, kengaku, kagi; live server pin).
  - `\b11434\b`: 1 hit in kake (`round-50-verifier-spotcheck.md:192`; Ollama OpenAPI staged reject).
  - `--parallel`, `-np`, `total_slots`: 16 hits in kengaku (`PROVINCE.md:14,158`, `SKILL.md:526`, `served-endpoint-identity-pin.md:20,37`).

## Findings

DEFECT — kama's own consumer rows pin non-default ports without citing R16 setters (`registry/endpoint-consumers.tsv:35-37`). R16 requires: *"A registry row that pins another port cites which of these the unit's argv or environment sets; without that citation a DEAD on the pinned port is reported as port drift, never as a model fault"*. `omp-llama-cpp-default` (:35) pins `8080` without citing P36 (`AIP_MODE=PREDICTION`, `AIP_HTTP_PORT`) or P09 (`--port 8080`), so its DEAD verdict in `latest.tsv:2` is strictly port drift. Rows `ufo-fsd-thetick` (:36) and `ufo-fsd-local-helper` (:37) pin `34113` without citing P09 (`--port 34113` / `LLAMA_ARG_PORT=34113`).

DEFECT — kagi's executable header advertises a model on port 8080 (`kagi-shokunin/SKILL.md:9-10`). Quote: *"fixed model `qwen-local/Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS` at `127.0.0.1:8080`"*. Contradicts R16 (where 9931 is b12177's default and 8080 requires P36) and kagi's own `PROVINCE.md:63` (*"configured model endpoint 127.0.0.1:8080 (dead: Jitsi) vs live llama-server on 34113"*) and `handler-trust-boundary.md:131-132` (*"8080 answers 404"*).

NOTE — kengaku corroborates R17 startup slot count and duplicates parameter recognition (`kengaku-shokunin/corpus/knowledge/served-endpoint-identity-pin.md:37`, `PROVINCE.md:14`). On direct unflagged server `http://127.0.0.1:45669` (pid 242776), kengaku records `total_slots=4`, confirming R17's startup resolution. On unit pid 1299, kengaku records `--parallel 2 (no literal -np)`, confirming the `-np`/`--parallel` synonymity declared in P02.

NOTE — kengaku mislabels sampling defaults on kama's surface (`kengaku-shokunin/corpus/knowledge/served-endpoint-identity-pin.md:38`). Labels `temperature=0.1, top_k=50` as "(server defaults)" under b1-39ebd2; b12177 `--help` defaults are temp 0.80, top-k 40. Agrees with round-92 finding D1.

NOTE — kumitate and kake duplicate pins and assign province consistently (`kumitate-shokunin/corpus/knowledge/ops-watchers.md:402`, `kake-shokunin/corpus/lessons/round-50-verifier-spotcheck.md:192`). Kumitate pins `34113` (duplicating rows 36-37). Kake stages Ollama OpenAPI `servers: url http://localhost:11434` and rejects it to kama under `PROVINCE.md:41`.

NOTE — C1 surface has zero sibling duplicates or contradictions. Across all 20 sibling lanes, `router-model-invalid`, `router-unloaded-autoload`, `gguf_state`, `gguf_parse`, and probe `SEEN` memo have 0 hits. Tameshi only inventories `kama-probe.sh` file existence. Kama is the sole fleet creator/consumer of the C1 repeat-invariant check.

## Proposed move (bounded synthesis; adjacency & calibration)

Evidence: Internal DEFECT in `registry/endpoint-consumers.tsv:35-37` + kagi SKILL.md:9-10 DEFECT.
Affected axes: **adjacency 7 -> 8** (cross-lane alignment), **calibration 7 -> 8** (registry precision); operability, depth, coverage unharmed.
Move: Land an update to `registry/endpoint-consumers.tsv` adding the missing R16 setter citations to rows 35-37 (row 35: cite legacy fallback or P36/P09, certifying its DEAD is port drift under R16; rows 36-37: cite P09 `--port 34113`); stage a cross-lane handoff note in `corpus/knowledge/cross-lane-scope.md` requesting kagi update `SKILL.md:9-10` to reflect live 34113 / R16 default 9931.
Risks: Modifying TSV columns breaks `tools/kama-probe.sh check` if format changes — keep columns identical, modify `notes` column only; do not alter sibling files directly (read-only boundary).
Verification: Run `bash tools/kama-probe.sh check --json` and verify exit code 2 with 3 evaluated rows; run `python3 tools/round93-setter-rows.py` to ensure C2 remains clean.

## Deliverables

- `.ufo/waves/round-93/w1/out/CN01SiblingOverlap/scan-receipts.txt` — full scan receipt (commands, true exit codes, term counts, binary hash, uptime).
- `.ufo/waves/round-93/w1/out/CN01SiblingOverlap/overlaps.tsv` — 13 structured rows (F01–F13) categorizing every sibling/registry overlap.
- `.ufo/waves/round-93/w1/CN01SiblingOverlap.md` — this report.

VERDICT: partial — C1 and C2 surfaces hold across all 20 sibling lanes with zero conflicting router checks or setter rows (kengaku corroborates R17 slots=4, kake agrees on 11434); but 3 consumer rows in kama's own registry omit R16 setter citations and kagi's SKILL.md:9-10 retains a stale 8080 model pin.
