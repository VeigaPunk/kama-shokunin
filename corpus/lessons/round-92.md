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
| S598 llama.cpp `tools/server/server-http.cpp` @ `b12177` | **admit** (A, code, mined) — opened after the wave, for the correction | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/tools/server/server-http.cpp — 2026-11-06, sha256 `aad15b757323f36b81235182c4a0a35d448399012ae3ef4fed9902b716fa17ea` | `port = std::stoi(getenv("AIP_HTTP_PORT", "8080"));` (line 96, under `AIP_MODE` == `PREDICTION`, line 93) | Grounds SKILL §Round 92 correction (R01): the AIP mode replaces the parsed port. Found by wave-1 SC01, re-read by the L1. |
| S599 llama.cpp `tools/server/server-models.cpp` @ `b12177` | **admit** (A, code, mined) — opened after the wave, for the correction | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/tools/server/server-models.cpp — 2026-11-06, sha256 `cab14969b9e5adf08a057c622d1abfc30fd8a17484de5b35942632d739a71108` | `inst.meta.port        = common_http_get_free_port();` (line 1218) | Grounds SKILL §Round 92 correction (R01): a router child listens on a free port. |

`status` / `recheck` / `used-by` changes on existing rows: none (S593–S595 stay byte-identical; their limits are in the
appended correction). S596, S597 are new rows (`mined`, recheck `on-release`). Their `used-by` changed in place this
round, old → new: `SKILL.md §Serving defaults (round 92 revision); corpus/knowledge/serving-thresholds.md` →
`SKILL.md,corpus/knowledge/serving-thresholds.md` (the census reads comma-separated paths and printed E11 on the prose
form; `sources-census.sh validate` exit 0 after the change).

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

**M4 — a decision cell universalised one line's default over the binary's other setters (round-91 overreach class,
again).** Class: the value is the binary's default (KQ146 holds) but the decision states what the binary *does* without
a sweep of the parameter's other setters. Evidence: R01 says a llama-server "started without `--port` … listens on
9931" and R08 says one "started without `-np` runs 4 slots"; wave-1 SC01 (`.ufo/waves/round-92/w1/SC01SourceReopen.md`)
found, and the L1 re-read at b12177, `--embd-gemma-default` setting `params.port = 8011` and `params.n_parallel = 32`
(S596 `arg.cpp:4613`, `:4616`; more presets at 4629-4764), `AIP_MODE=PREDICTION` replacing the port (S598 lines 93-125)
and router children on a free port (S599 line 1218). The designated K2 reviewer (RV02) passed every row; the scout's
sweep caught it. Captured-by: none — KQ146 covers the value only, and the counter cannot read a decision. Fix: dated
correction under the table (`SKILL.md` §Round 92 correction), C1 recorded **not verified** by the author; new QUALITY
KQ149 (a decision that says what the binary does names or excludes every setter a `params.<field> =` sweep of the
program's sources finds). Shown able to fail: `grep -n 'params.port = \|params.n_parallel = ' common/arg.cpp` at b12177
prints 18 lines — the parser's own four (1373, 2521, 2529, 3321), 4613 and 4616, and twelve more preset lines
(4629-4764) — against R01/R08's unconditional wording.

## Dispositions of the round-91 closure (R1–R5)

- **R1** `round75-instruments` red (`bad_rows=19`, L0 open since r87): carried, not claimed; the arm stays red in the
  terminal gate.
- **R2** S593 teaches cell: dated correction appended (`corpus/SOURCES.md` §Round-92 correction), row byte-identical.
- **R3** scratch discipline: every wave item names its own root `/fast/scratch/hyaku/kama-r92/<seat>/` and the context
  forbids another seat's path (`.ufo/waves/round-92/w1-spec.json`).
- **R4** superseding rows: C1 (R01–R15 supersede T01–T14; counter `supersedes=14`), but C1 is not verified: R01 and R08
  decisions overstate the binary (M4), corrected in a dated note; R4 stays open for those two rows.
- **R5** SC02 F1–F3: C2 (`measured/c2.out`, L1–L6 within 20 s, D1–D9 equal to base). The round-91 limit "the counter does
  not own the rule" still holds for C2's counter: wave-1 CR01 passes five forgeries at `probe=rev` (SCORECARD §Round-92
  disclosed limits); M2 itself is linear and correct on each of those held-out shapes.

## Wave-1 findings integrated (`.ufo/waves/round-92/w1/`)

- RV01 (C2 diff): no reachable behaviour change in 915 comparisons; three latent differences (non-default IFS words,
  >pipe-buffer multi-line `served_persist` exit 141, awk-missing failure) unreachable in the probe's runtime.
- RV02 (C1 K2 read): 15/15 rows hold, three non-firing notes (R03 policy clause, R04 "0 for decision models", R07
  default-scoped). SC01 (source sweep): every literal on its line; R01/R08 decisions overstate the binary → M4.
- CR01 (C2 counter): five forgeries pass at `probe=rev` (mixed-escape quadratic fallback, 85 000 router cap, `/m/`-only
  persist, 20 000 persist cap, trailing-space strip); M2 correct and linear on each held-out shape; routed to round 93.
  L1 doubling at M2 (`.ufo/waves/round-92/measured/c2-doubling.out`): mixed-escape id 0.48 → 0.87 → 1.72 s, snapshot
  4 000 → 32 000 ids 0.22 → 0.59 s, router 20 000 → 80 000 entries 0.49 → 1.64 s.
- CR02 / MT02 (C1 counter): 14 wrong tables exit 0; 16/23 counter mutants exit-identical on the battery; routed.
- MT01 (C2 probe mutants): 7/19 killed, 8 equivalent, 4 real gaps identical at base and M2; routed.
- EX01 (held-out cells): no harm; base and M2 byte-equal where base completes. EX02 (no-python, awk portability): M2
  equal to base with and without python; `AWK_JSTR`/`served_persist` byte-identical under gawk, busybox 1.35.0 and mawk
  1.3.4 (scratch-only binaries). CN01: no sibling contradicts R01–R15.
