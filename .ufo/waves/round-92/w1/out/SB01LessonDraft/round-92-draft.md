# Round 92 — serving defaults re-declared under KQ146 (15 rows); three probe paths linear

L1 `KamaR92` (planner seat held by the L1). Base `ed018ca0fa956c5052b3dc6b714a2cb72973da21`; freeze
`309eadafd4d0557a056c1bf61455c59778cf5e1d`; C2 measured `fa8aedb73d18448383c7a4d75405aba448fe8e38` (M2);
C1 measured `18153ebb5f9e2ae83f53e7fef57ee579bc409331`, child of M2 (lane tip at drafting
`d5a064313522392bf7f8498d1a54c0cfd0ad314b`). Plan: `plans/round-92-claims.md`. Previous closure:
`round-91-verifier-spotcheck.md` (rejected-honest-stop; routed R1-R5).

## Gate

All rows opened 2026-11-06; digests re-fetched by this seat equal the `corpus/SOURCES.md` anchors
(`w1/out/SB01LessonDraft/source-digests.out`; the L1 receipt is `controls/sources-opened.out:1-6`).

| Candidate | Decision | URL / access date | Located quote (≤25 words) and location | Reason |
|---|---|---|---|---|
| S596 llama.cpp `common/arg.cpp` @ `b12177` | **admit** (A, code, mined) | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/common/arg.cpp — 2026-11-06, sha256 `c69c0e07…` | `params.n_parallel = -1;     // auto by default` (line 1373, under `else if (ex == LLAMA_EXAMPLE_SERVER)` line 1372) | Grounds R07 (`SKILL.md:1940`): the server parser replaces the shared-struct default before options are read, so `common.h:464`'s `1` is not the server's value. |
| S597 llama.cpp `tools/server/server.cpp` @ `b12177` | **admit** (A, code, mined) | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/tools/server/server.cpp — 2026-11-06, sha256 `d4d343db…` | "n_parallel is set to auto, using n_parallel = 4 and kv_unified = true" (line 127; the binding literal `params.n_parallel = 4;` is line 129) | Grounds R08 (`SKILL.md:1941`): outside the router role auto becomes 4 slots and unified KV (lines 126-130); the router role keeps auto (line 116). |
| S593 llama.cpp `common/common.h` @ `b12177` | **re-open** (digest equal) | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/common/common.h — 2026-11-06, sha256 `c3010a3c…` | `int32_t timeout_read        = 3600;          // http read timeout in seconds` (line 634) | R01-R06 bind 632/634/636/644/669/703; the row's "one parallel sequence" teaches cell is corrected by the dated note at `corpus/SOURCES.md:703-712`. |
| S594 Ollama `envconfig/config.go` @ `v0.40.11` | **re-open** (digest equal) | https://raw.githubusercontent.com/ollama/ollama/v0.40.11/envconfig/config.go — 2026-11-06, sha256 `0b0ea669…` | `keepAlive = 5 * time.Minute` (line 130) | R09-R13 bind 23/130/150/277/281. |
| S595 vLLM `vllm/envs.py` @ `v0.32.0` | **re-open** (digest equal) | https://raw.githubusercontent.com/vllm-project/vllm/v0.32.0/vllm/envs.py — 2026-11-06, sha256 `e963af06…` | "Timeout in seconds for waiting for engine cores to become ready" (line 809) | R14/R15 bind the run-time readers 812/1144, not the declarations 26/111. |
| S595 `envs.py:26` as a default anchor | **reject** | same URL — 2026-11-06 | `VLLM_ENGINE_READY_TIMEOUT_S: int = 600` (line 26, inside `if TYPE_CHECKING:` line 14) | The block is never executed at run time; the counter's disclosed V7 limit cannot tell it from the lambda (`controls/c1-forgeries.out:21-22`), so only a reviewer read discriminates. Flip: bind the run-time line 812 that R14 cites. |
| S593 `common.h:464` as llama-server's `n_parallel` | **reject** | same URL — 2026-11-06 | `int32_t n_parallel            =     1;` (line 464) | Shared-struct default; the server parser sets `-1` (`common/arg.cpp:1373`) and resolves `4` (`tools/server/server.cpp:129`); the pinned binary prints `-np … (default: -1, -1 = auto)` (`--help` line 468). Flip: bind the parser/entry point (R07/R08), or a non-server consumer. |

S596/S597 rows landed with the C1 commit (`corpus/SOURCES.md:351-352` at `18153ebb`); S593-S595 rows are unchanged
at `:348-350`. The two rejects are the two places a plausible anchor is not the value the binary uses.

## Mistakes

**M1 — a differential counter compared a timestamped file byte for byte.** Class: the equality is finer than the
artefact. V0 compared `latest.tsv` whole although it carries `#@snapshot_id <UTC second>`, so base against itself
failed D7: `controls/c2-base-v0.out:11` `D7-snapshot-50-paths ok=0 … equal_to_base=0`, `:20`
`mismatches=7 positive_mismatches=1`; the diagnosis is `:22-24`, and `:1-3` records the receipt as a verbatim copy
of the pre-freeze L1 job. Captured-by: the pre-freeze base-vs-base control (v0). Fix: `stable()` drops that one
line before compare (`tools/round92-linear-paths.py:207-209`, used at `:258`); the frozen base run now passes D7
(`controls/c2-base.out:8`). Shown able to fail: v0 (`positive_mismatches=1`).

**M2 — a binding table's line cell carried a prose line number (128) where the literal is on 129.** Class:
citation copied from a summary instead of the fetched bytes. The drafted R08 pinned `tools/server/server.cpp:128`
(a blank line); the pre-freeze P0 positive control failed on B6: `controls/c1-forgeries-v0.out:4-6`
`CASE P0-candidate expected_exit=0 exit=1 UNEXPECTED` with `R08 bound=0 … why=literal-not-at-line` at rev
`4f1794e4…`, and the header `:1-3` records that the v0 draft cited 128 and that `controls/c1-forgeries.out` is the
post-fix run. Captured-by: B6 (`tools/round92-server-defaults.py:28`, code `:214-215`), as designed. Fix: cite the
line the literal sits on (129) — `controls/c1-candidate-section.md:22`, `SKILL.md:1941`, and the committed P0 run
is green (`controls/c1-forgeries.out:2-3`). This seat re-demonstrated with a paired fixture built from the M1
section: 129 → `bound=1` (`w1/out/SB01LessonDraft/b6-positive-129.out:9,17-18`, exit 0); 128 →
`bound=0 why=literal-not-at-line` (`…/b6-mutant-128.out:10,18-19`, exit 1), and the fetched line 128 is empty.
Shown able to fail: v0 P0 (exit 1) and the mutant.

**M3 — the r91 M4 class recurred: the frozen harm list does not name every probe-sha-bound instrument.** Class:
harm outside the frozen kill list. The C2 probe change (M2) staled the round-90 reason-row receipt:
`measured/r90-reason-rows-stale.out:26-27` at `83f9e3d4` prints `bound=0 unbound=24 … receipt=stale`, exit 1, and
the frozen list (`controls/harm.sh:11-16`) names six sections (five suites plus the operator-router check) and not `tools/round90-reason-rows.py` — the same gap
as `round-91.md` M4. Captured-by: the L1 after M2 (no frozen control would catch it). Fix: recapture at the M2
probe (`measured/r90-reason-recapture.out:26-27`, 24 cells, exit 0; the 24 (cell, reason, verdict) triples are
identical before and after, only `probe_sha256` differs between `measured/r90-reason-cells-prior.jsonl` and
`-recaptured.jsonl`) and re-bind at the tip (`measured/r90-reason-rows-tip.out:26-27`, `bound=24
receipt=current`, exit 0). Routed: the successor harm list adds every probe-sha-bound counter.

## Dispositions of the round-91 closure (R1-R5)

- **R1** `round75-instruments` red (`bad_rows=19`, L0 open): carried, not claimed (`plans/round-92-claims.md`
  §Separability); no round-92 receipt in `.ufo/waves/round-92/`.
- **R2** S593 teaches cell / S595 lines: closed by the dated correction at `corpus/SOURCES.md:703-712` (appended
  2026-11-06, landed with M1 `18153ebb`, which adds 13 lines to `corpus/SOURCES.md`).
- **R3** scratch discipline: closed for this wave — `w1-spec.json` names 12 distinct per-seat roots
  `/fast/scratch/hyaku/kama-r92/<seat>`; no two seats share a root; this seat used `SB01LessonDraft`.
- **R4** = C1: measured `measured/c1.out:17-18` `rows=15 bound=15 … help_checked=7 help_disagree=0 supersedes=14`,
  exit 0 at M1; do-nothing base `controls/c1-base.out:2-3` `rows=0`, exit 1. The counter's bytes at F and M1 hash
  `a49e8984…` (K1/K3 hold).
- **R5** = C2: measured `measured/c2.out:17-18` `cells=15 mismatches=0 positive_mismatches=0`, exit 0 at M2
  (load average 78.95 in `:1`; slowest L cell 3.43 s, `:11`); base `controls/c2-base.out:17-18` `mismatches=6`,
  exit 1 (L1-L5 killed at 120 s, L6 53.98 s, `:11-16`). The three constructs are `jstr` in one awk pass
  (`tools/kama-probe.sh:211`, fast path `:225-234`), `cand+=($idx)` (`:834`) and `served_persist` in one awk pass
  (`:457`, `:1490`). Held-out cells remain outside the predicate (claims §C2), so the counter still grades time
  and byte-equality, not asymptotic class.
