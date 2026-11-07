# Round 92 — serving defaults re-declared under KQ146; three probe paths made linear

L1 `KamaR92` (attempt 1). Base `ed018ca0fa956c5052b3dc6b714a2cb72973da21`; freeze `309eadafd4d0557a056c1bf61455c59778cf5e1d`;
C2 measured `fa8aedb73d18448383c7a4d75405aba448fe8e38`; C1 measured `18153ebb5f9e2ae83f53e7fef57ee579bc409331`.
Plan: `plans/round-92-claims.md`. Previous closure: `round-91-verifier-spotcheck.md` (rejected-honest-stop; R1–R5).

## Gate

Rows opened 2026-11-06 by the L1 (`curl -sS -m 60`, receipt `.ufo/waves/round-92/controls/sources-opened.out`, fetched
2026-11-07T00:34:52Z = 2026-11-06 21:34 -03); each digest equals its `corpus/SOURCES.md` row.

| Candidate | Decision | URL / access date | Located quote (≤25 words) and location | Reason |
|---|---|---|---|---|
| S596 llama.cpp `common/arg.cpp` @ `b12177` | **admit** (A, code, mined) | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/common/arg.cpp — 2026-11-06, sha256 `c69c0e0703dbd343aec148ff4a65a343da80f65064d9385bc60120ed765e6f67` | `params.n_parallel = -1;     // auto by default` (line 1373, inside `} else if (ex == LLAMA_EXAMPLE_SERVER) {`, line 1372) | The server's own parser sets the slot-count default (KQ146); row R07. Also grounds R02 "`--timeout` sets read and write" (lambda lines 3562-3564). |
| S597 llama.cpp `tools/server/server.cpp` @ `b12177` | **admit** (A, code, mined) | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/tools/server/server.cpp — 2026-11-06, sha256 `d4d343db7c1b648eb5358ae2b87966a5f78ce5c9b245c7fbfe9827ba6971f08b` | `n_parallel is set to auto, using n_parallel = 4 and kv_unified = true` (line 127) | The entry point resolves auto to 4 slots outside the router role (lines 116, 126-130); row R08 (derived, H2). |
| S593 `common/common.h` @ `b12177` | **re-opened**, admitted for R01–R06 only | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/common/common.h — 2026-11-06, sha256 `c3010a3c…6073` equal | `int32_t port                = 9931;          // server listens on this network port` (line 632) | Each of R01–R06 equals the pinned `--help` default (`measured/c1.out` H1). Its teaches cell "one parallel sequence" is corrected (appended `corpus/SOURCES.md` §Round-92 correction). |
| S594 Ollama `envconfig/config.go` @ `v0.40.11` | **re-opened**, admitted | https://raw.githubusercontent.com/ollama/ollama/v0.40.11/envconfig/config.go — 2026-11-06, sha256 `0b0ea669…1895` equal | `keepAlive = 5 * time.Minute` (line 130) | R09–R13; the decisions no longer claim what the line does not set (round-91 RV02: T09, T10, T11). |
| S595 vLLM `vllm/envs.py` @ `v0.32.0` | **re-opened**, admitted for lines 812 and 1144 | https://raw.githubusercontent.com/vllm-project/vllm/v0.32.0/vllm/envs.py — 2026-11-06, sha256 `e963af06…0694` equal | `os.environ.get("VLLM_ENGINE_READY_TIMEOUT_S", "600")` (line 812) | R14/R15 bind the `environment_variables` lambdas the module `__getattr__` (line 2291) serves at run time. |
| S595 lines 26 and 111 as the default's anchor | **reject** (declaration, not the reader) | same URL — 2026-11-06 | `VLLM_ENGINE_READY_TIMEOUT_S: int = 600` (line 26, under `if TYPE_CHECKING:` line 14) | A type-checker declaration is not what the server reads. Counter limit: control V7 binds it anyway (`controls/c1-forgeries.out`), so this stays a reviewer rule. Flip: never (a declaration is not a default) unless vLLM reads it at run time. |
| S593 line 464 as the llama-server slot-count anchor | **reject** (shared struct overridden) | S593 URL — 2026-11-06 | `int32_t n_parallel            =     1; // number of parallel sequences to decode` (line 464) | KQ146: `arg.cpp:1373` overrides it for the server; control V1 (`help-default=-1`) fails it mechanically. Flip: a future pin's parser stops overriding it and `--help` prints 1. |

`status` / `recheck` / `used-by` changes on existing rows: none (S593–S595 stay byte-identical; their limits are in the
appended correction). S596, S597 are new rows (`mined`, recheck `on-release`, used-by SKILL §Serving defaults (round 92
revision) and `corpus/knowledge/serving-thresholds.md`).

Assimilation: none (no `merge/kama/` theme taken; `considerthese/` not mined this round).

## Mistakes

**M1 — a differential cell compared a clock.** Class: harm detector reading run-variant bytes as output. Evidence:
the counter draft v0 compared `snapshot`'s `latest.tsv` byte for byte; the file's first line is `#@snapshot_id <UTC
second>`, so the base probe failed against itself on D7 whenever the two runs straddled a second
(`.ufo/waves/round-92/controls/c2-base-v0.out`: `D7-snapshot-50-paths ok=0 … equal_to_base=0`; reproduced 9/12 in a
loop). Captured-by: the pre-freeze base-against-base control (round 9 §9 "build the cheapest control … before
freezing"). Fix: `stable()` drops the `#@snapshot_id` line before comparing (counter docstring), re-run
`controls/c2-base.out` D7 `equal_to_base=1`; new QUALITY KQ147. Shown able to fail: v0 above.

**M2 — a line number carried from prose.** Class: citation copied from a summary instead of the fetched bytes. Evidence:
the drafted R08 cited `server.cpp` line 128 (a blank line) because the round-91 correction said "lines 126-129"; the
assignment is on line 129. Captured-by: the pre-freeze positive control P0 (`controls/c1-forgeries.py`), which failed on
B6 `literal-not-at-line` until the row cited 129. Fix: row corrected before freeze; the counter's B6 is the rule.
Shown able to fail: the first battery run, P0 exit 1 with `R08 … why=literal-not-at-line`
(`.ufo/waves/round-92/controls/c1-forgeries-v0.out`; the committed `controls/c1-forgeries.out` is the corrected run).

**M3 — a routed fix not carried into the next frozen harm list (repeat of round-91 M4).** Class: probe-bound receipt
outside the kill list. Evidence: round-91 M4 routed "a successor harm list names every probe-sha-bound instrument";
round 92's frozen `controls/harm.sh` copied the round-91 list plus `round91-answer-time.py` and still omitted
`tools/round90-reason-rows.py`; at `83f9e3d4` (after the C2 probe change) it read `bound=0 unbound=24 receipt=stale`,
exit 1 (`measured/r90-reason-rows-stale.out`). Captured-by: none in the frozen plan; found by the L1 before the wave
read it. Fix: receipt re-captured at the C2 probe — 24 (cell, reason, verdict) triples identical
(`measured/r90-reason-recapture.out`, `r90-reason-cells-prior.jsonl` vs `r90-reason-cells-recaptured.jsonl`), re-bound
24/24 at `d5a06431` (`measured/r90-reason-rows-tip.out`, exit 0); new QUALITY KQ148 names the instrument so the next
probe change's harm list must carry it. Shown able to fail: the stale receipt above.

## Dispositions of the round-91 closure (R1–R5)

- **R1** `round75-instruments` red (`bad_rows=19`, L0 open since r87): carried, not claimed; the arm stays red in the
  terminal gate.
- **R2** S593 teaches cell: dated correction appended (`corpus/SOURCES.md` §Round-92 correction), row byte-identical.
- **R3** scratch discipline: every wave item names its own root `/fast/scratch/hyaku/kama-r92/<seat>/` and the context
  forbids another seat's path (`.ufo/waves/round-92/w1-spec.json`).
- **R4** superseding rows: C1 (R01–R15 supersede T01–T14 row for row; counter `supersedes=14`).
- **R5** SC02 F1–F3: C2 (`measured/c2.out`, L1–L6 within 20 s, D1–D9 equal to base). The "counter does not own the
  rule" limit of round 91 is answered for these paths by the differential cells and the scaled `served_model` check.
