# U0Consumers — readers of the live receipt that treat a v4 receipt / null `log_path` differently

Verdict: ONE hard breaker class — every v3-bound reader refuses a v4 receipt (`check-receipt.py` exit 1 INVALID, `gguf-identity.py` exit 2 could-not-evaluate); NOTHING in tools/ SKILL.md corpus/ registry/ reads `teardown.log_path` for its value (null is safe); SKILL.md/corpus run instructions are stale (no provenance flags, no replay tool, v1–v3 only).
Lane read at HEAD 46a924e0 (build 3a09a1d9). Static grep over tools/ tests/ registry/ corpus/ SKILL.md PROVINCE.md README.md AGENTS.md MINT.md SHONEN.md plus three runs below.

## Runs (observed)
```
python3 tests/llamacpp-live/check-receipt.py .ufo/waves/round-47/c2/live/receipt-{1,2,3}.json     -> INVALID, 4 problems each, exit 1
  - schema is 'kama-llamacpp-live/v4', want v1, v2 or v3
  - required check 'teardown_exited' is absent
  - unexpected check id 'teardown_graceful' (the schema names exactly 10)
  - unexpected check id 'loading_envelope_graded' (the schema names exactly 10)
python3 tests/llamacpp-live/check-receipt.py receipt-1.json --require-schema v3                   -> same 4 problems, exit 1
python3 tools/gguf-identity.py ~/.cache/kama-shokunin/models/stories260K.gguf --receipt receipt-1.json --json
   -> receipt: {status: could-not-evaluate, exit_code: 2, reason: receipt_schema_unsupported}, exit 2
```
Receipt-1 facts: `teardown.log_path` is JSON null; `teardown.log_lines` inlined; `provenance` = {server:{asset_url,asset_sha256,member}, model:{url,sha256}}; `tool` {path (absolute host path /home/vgpnk/...), sha256}. Producer: tools/kama-llamacpp-live.py:54 SCHEMA, :876 `'log_path': None`, :1381-1387 provenance (nulls when the four flags are omitted — flags are optional, not enforced).

## A. Readers that treat a v4 receipt differently (MUST change or be consciously left)
| # | file:line | what it does | v4 effect | proposed change |
|---|---|---|---|---|
| A1 | tests/llamacpp-live/check-receipt.py:47-49 (constants), :300-306 (`is_v3`/`is_v2` flags + schema whitelist) | v4 not in the whitelist; `is_v2`/`is_v3` false, so the v1 check-id set (`teardown_exited`) is demanded and v3 ids rejected | INVALID exit 1 on all three round-47 receipts (observed). Every SKILL.md gate row (538, 576, 612, 656, 702) therefore cannot validate a current receipt | add `RECEIPT_SCHEMA_V4`; `is_v3 = schema in (V3,V4)`, `is_v2` likewise; widen message :305-306 |
| A2 | check-receipt.py:2363 (`--require-schema choices v1|v2|v3`), :2392-2403 (version map `{V1:1,V2:2,V3:3}`) | no `v4` choice; version map lacks V4 so a v4 passes the floor check silently (`version is None`) | `--require-schema v4` impossible; `--require-schema v3` on a v4 receipt gives no floor error but still INVALID via A1 | add `v4` choice and map entry 4 |
| A3 | check-receipt.py:2409-2412 | NOT-EVALUATED (exit 3) only when `schema == V3` | a v4 `not-evaluated` receipt would print VALID/INVALID instead of exit 3 | compare against {V3,V4} |
| A4 | check-receipt.py (no `provenance` handling anywhere; grep `provenance` = 0) | no key-closure check, so the new block is ignored, not rejected | provenance is unvalidated by the gate (shape, 64-hex asset_sha256, URL scheme, `provenance.model.sha256 == model.sha256`) | add optional-block validation for v4 |
| A5 | check-receipt.py:1753 (selftest fixture `"log_path": "/tmp/kama-llamacpp-live-x.log"`) and selftest mutation list (~:1797-1830 builds v2/v3 bases only) | only writer of `log_path` in the gate; never read as a value | no v4 base or null-`log_path` base in `--selftest`/mutants; selftest mutation count changes if v4 is added | add v4 base + `log_path`-not-null-allowed case |
| A6 | tools/gguf-identity.py:44 `RECEIPT_SCHEMA_V3`, :477-478 `if document.get("schema") != RECEIPT_SCHEMA_V3: raise ReceiptError("receipt_schema_unsupported")`, :820 selftest fixture; help text "llama.cpp live v3 receipt" | exact-equals v3 | `--receipt` on any v4 receipt → exit 2 could-not-evaluate (observed). SKILL.md:660 row (“Captured GGUF declaration agreement”) and SCORECARD.md:965 say v3 receipt | accept {V3,V4}; fields it reads (`model_sha256_post`, `captures.props/models`) are unchanged in v4 |
| A7 | tests/llamacpp-live/controls.py:182 `RECEIPT_V1`, :1350 `SYN_V3`, :1447-1448 (`_FakeGate` floor `schema != SYN_V3`), :171-198 CHECK_IDS universe | C1 counting command runs the REAL tool, which now emits v4, through the REAL gate (A1) | [INFERENCE, not run: needs a llama-server] K0 good control would be rejected by `check-receipt.py` → good_rejected; k19 forges v1 under `--require-schema v3` (fine). Fix after A1/A2 | bump SYN to v4 or accept both; rerun controls once |
| A8 | tests/llamacpp-live/install-tree-grid.py (`--receipt PATH` baseline), install-links-grid.py:47 `PRODUCER`, install-io-grid.py:22, unpinnable-e2e.py:10/:29 | take a receipt or run the producer and then the gate | [INFERENCE, not run] a v4 baseline receipt is gate-rejected, so the grid cannot establish a valid baseline; producers run by e2e now emit v4 and the gate rejects them for the schema, which can mask the targeted rejection reason the case expects | rerun after A1 |
| A9 | tools/round45-recheck-audit.py:231 `r.get("schema") != "kama-llamacpp-live/v3"` (grade_live), :107 `LIVE_DIR = ".ufo/waves/round-45/c1/live"` | frozen round-45 counter, pinned to the round-45 dir and build_info b11889 | unaffected for committed round-45 receipts; would return `schema …v4` if ever pointed at b11909 receipts. Frozen: do not edit | none; note only |
| A10 | tools/kama-context-capacity.py:183-188 `load_live_module` (imports tools/kama-llamacpp-live.py, uses `pick_port`/refused-ports; no `SCHEMA`), :727 | imports the producer, ignores receipts | unaffected by v4/null log_path (its own `log_path` at :299-393 is its own raw server log under `cfg['scratch']`) | none |

## B. `log_path` consumers (null handling)
- Value consumers: none outside the producer. grep `log_path` over tools/ tests/ registry/ corpus/ SKILL.md: tools/kama-llamacpp-live.py (:868-921 teardown, :1414 `log_path = None`, :1503-1504 mkstemp, :1643-1645, :1759-1762 cleanup); check-receipt.py:1753 (fixture only); kama-context-capacity.py and echo-recheck.py (own local variables, unrelated); tools/round47-live-replay-audit.py:31, :172-178 (C2 counter: key must be present; null or committed repo-relative path accepted, so v4 null passes).
- Prose consumers: corpus/lessons/round-46.md:37 and round-46-verifier-spotcheck.md:141 (D5) describe the dead-pointer; v4 null resolves D5 for new receipts; the three b11906 receipts at .ufo/waves/round-46/c1/live/ still carry /fast/scratch paths (historical, unchanged). corpus/QUALITY.md:386 KQ66 (re-fetch URL/bytes/sha for host-path inputs) is now satisfiable from `provenance` — the lane's tool block `tool.path` and `server.arg`/`model.arg` remain host paths; KQ66 also asks for a **byte count**, which `provenance` does not record (observed: only url/sha256). [INFERENCE on KQ66 reading].
- check-receipt.py v3 path never asserts `log_path` type; `log_lines`/`log_lines_truncated`/`log_tail_truncated` (read in teardown validation ~:888-906 region) are unchanged.

## C. Readers keyed on v3 that are NOT consumers of v4 (informational)
registry/required-citations.json:33 (`r18-live-receipt-1`, hash-pinned r18 v3 receipt); registry/recheck-r45.tsv:8-10 (S041/S046/S055 pointers at round-45 receipts); corpus/SOURCES.md:53,58,67,238,240 (S041/S046/S055/S485/S487 rows, each names its receipt dir and schema). Historical; no change. A new SOURCES row for the b11909 receipts is the one the C2 counter's `newrow` wants.

## D. Every place that tells a reader how to run the live tool (L1 update list)
SKILL.md
- :537 Live llama.cpp lifecycle (round-16 row): b11755 server path, "all 10 checks", `--out PATH` — stale (11 checks, v4, no provenance flags).
- :538 Live receipt gate: pins; "10 check ids".
- :567, :575-577 round-17 rows (v2/11 checks; `check-receipt.py` v1+v2; controls row).
- :606 prose and :611-613 current tool rows: :611 command uses `--server …llama-b11755/llama-server … --out /tmp/kama-live.json` (b11755 binary, `/tmp` out path, no `--server-asset-url/--server-asset-sha256/--server-member/--model-url`, says "Live v3 tool"); :612 gate row says "Require v3 for a current run" (rejects v4); :613 `--selftest` row.
- :655-656 six-pin gate row, :702 links-pin gate row, :703 install-links grid, :725 unpinnable-e2e, :741 install-io-grid — all name check-receipt.py and need the v4 floor once A1 lands.
- :659-660 gguf-identity rows: "captured v3 receipt" (A6).
- No row for tools/kama-live-replay.py (`--receipt R --work DIR --out J [--live TOOL] [--timeout S]`, `--selftest [--scratch DIR]`; exits per its docstring tools/kama-live-replay.py:14-30) — grep `kama-live-replay` over SKILL.md/corpus/registry = 0 hits.
Other
- tools/kama-llamacpp-live.py:2-30 docstring and :1096-1133 argparse help (already v4).
- PROVINCE.md:57-75 (round-16/17 live-fixture notes: v1/v2 text) ; README.md and AGENTS.md: no hits.
- SCORECARD.md:663, :733, :747, :833, :884, :965 (capability/gate rows; :965 "captured v3 receipt").
- SHONEN.md:8 (round-16 `kama-llamacpp-live/v1` assertion; historical).
- corpus/knowledge/llamacpp-loading-lifecycle.md: :2-3 (recheck: on-release — re-run the harness on build change), :101 (v1), :159 (round-17 run), :194 (v2), :239-262 (v3 section incl. `--require-schema v3` advice), :330, :375-377 (install-io-grid recheck), :399-402. No v4/provenance/replay section yet.
- corpus/knowledge/loopback-listener-ownership.md:3 (`--selftest` recheck), :107.
- corpus/README.md:698 (round-45 three v3 receipts, harness sha 8c0dbb2b…).
- corpus/QUALITY.md:133 (KQ24, v3-specific wording), :386 (KQ66, see B).
- corpus/lessons/round-16.md:103, round-17.md:37/:171 (historical run records).
- registry/digest-ledger.tsv:6 (model pin cites tools/kama-llamacpp-live.py).

## E. Suggested L1 order
1. check-receipt.py: v4 constants/flags/choices (A1-A3), then provenance validation (A4) and selftest v4 base (A5).
2. gguf-identity.py accept v4 (A6).
3. controls.py + the three grids (A7, A8): rerun once.
4. SKILL.md :537-538, :575-577, :606-613, :655-660, :702 rewrite to the b11909 command with the four provenance flags, an out path inside the lane (not /tmp), `--require-schema v4`; add a kama-live-replay row.
5. corpus knowledge lifecycle entry: v4 + replay section; QUALITY KQ66 byte-count gap; SOURCES row for the b11909 receipts.
No lane files edited; scratch /fast/scratch/hyaku/kama-r47/U0Consumers removed.
