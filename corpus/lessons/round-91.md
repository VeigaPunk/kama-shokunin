# Round 91 — large answers graded in linear time; serving thresholds (C2 not verified)

L1 `KamaR91` (attempt 1, died after landing the claims) and `KamaR91a2` (attempt 2: wave, record, report).
Base `c06838c5b94576971ea33ac465bf2c935e9037f9`; freeze `9a41912a598cad00f7ff08391586a0ef3732bbed`;
C1 measured `3decfa36b0eba7e5197c034dd1547146bca1568a`; C2 measured `3f317ecd211e80929c673e306e3230be287fdf20`.
Plan: `plans/round-91-claims.md`. Previous closure: `round-90-verifier-spotcheck.md` (admitted; R1–R6).

## Gate

All rows opened 2026-11-06; digests re-fetched by wave-1 SB01 and SC01 (`.ufo/waves/round-91/w1/out/SB01LessonDraft/round-91-lesson-draft.md`,
`w1/out/SC01SourceReopen/source-reopen-verdicts.txt`) and equal to the `corpus/SOURCES.md` rows.

| Candidate | Decision | URL / access date | Located quote (≤25 words) and location | Reason |
|---|---|---|---|---|
| S592 POSIX.1-2024 `awk` | **admit** (A, spec, mined) | https://pubs.opengroup.org/onlinepubs/9799919799/utilities/awk.html — 2026-11-06, sha256 `6df7d0776af4b28dbc3ec667a02a18e51ccd5066ea45a22166214e7e3832f898` | "as if they appeared in the awk program preceded and followed by a double-quote ('"') character, as a STRING token" (lines 107-108) | Grounds C1's `ENVIRON` hand-off: a `-v` operand is escape-processed, an ENVIRON element is not; elements may be numeric strings (lines 796-797), hence the `x ""` string compare. |
| S593 llama.cpp `common/common.h` @ `b12177` | **admit** (A, code, mined) — **limited** by KQ146 | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/common/common.h — 2026-11-06, sha256 `c3010a3c662a14556adb651b79bff00089564fde6b5e336959403e3db34e6073` | `int32_t timeout_read        = 3600;          // http read timeout in seconds` (line 634) | Seven T01-T07 literals on their lines. Limit found by RV02: line 464 (`n_parallel = 1`) is the `common_params` default the server's parser overrides (`common/arg.cpp:1373`); T07 misstates (M1). |
| S594 Ollama `envconfig/config.go` @ `v0.40.11` | **admit** (A, code, mined) | https://raw.githubusercontent.com/ollama/ollama/v0.40.11/envconfig/config.go — 2026-11-06, sha256 `0b0ea669b31cfe2b54313427257326a2b7a909bbc7bf8a671035efc446fb1895` | `keepAlive = 5 * time.Minute` (line 130; doc comment line 128 "Default is 5 minutes.") | T08-T12 literals on lines 23, 130, 150, 277, 281; RV02 marks T09/T10/T11 decisions as overreach (corrected in SKILL §Round 91 correction). |
| S595 vLLM `vllm/envs.py` @ `v0.32.0` | **admit** (A, code, mined) | https://raw.githubusercontent.com/vllm-project/vllm/v0.32.0/vllm/envs.py — 2026-11-06, sha256 `e963af06cf6c775fe285147e0d811ea5b4d679e5cbd6958980ec2a0d1da70694` | "Timeout in seconds for waiting for engine cores to become ready" (line 809) | T13/T14 on lines 26, 111 (TYPE_CHECKING mirrors; runtime getters 812, 1143). T13 decision overreaches (600 s per wait). |
| GNU gawk manual `Assignment-Options.html` | **reject** (unreachable) | https://www.gnu.org/software/gawk/manual/html_node/Assignment-Options.html — 2026-11-06 | — (curl rc=28, 0 bytes, on five gnu.org paths; SB01) | Host-wide connect timeout; existence not judgeable. S592 grounds the same rule. Flip: a fetch returns bytes. |
| SGLang v0.5.22 `python/sglang/srt/server_args.py` | **reject / not mined** | https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/python/sglang/srt/server_args.py — 2026-11-06, sha256 `d1b9ffc79edcbc857efd02a47d47eed9b414f8ac44bc4e3214d78a7922e90e03` | `from sglang.srt.arg_groups.fields.serving import (` (line 177) | Defaults moved to `arg_groups/fields/`; the watchdog default spans lines 66-69 of `device.py` and cannot bind one line (SC01 F4). Candidate rows T15-T22 stay in `w1/out/SC01SourceReopen/` (frontier). Flip: a round that applies KQ146 to them. |
| `corpus/knowledge/serving-thresholds.md` | **admit with dated correction** | cites S593-S595 | — | Own-corpus sweep (KQ143) recorded at freeze; rules 1, 3, 4 corrected in-file (round-91 correction section) after the non-author read. |
| `corpus/knowledge/probe-answer-bounds.md` round-91 append | **admit** | cites S592 + receipts | — | Adds the time bound and the r90 R2 verified-at correction. |

`status` / `recheck` / `used-by` changes on existing rows: none (S592-S595 were new rows, `mined`).

## Mistakes

**M1 — a struct default read as the binary's default.** Class: source line correct, program-level default
different (a library default overridden by the program's own argument parser). Evidence: SKILL C2 row T07 binds
`common.h:464` `n_parallel = 1`; `common/arg.cpp:1373` sets `-1` (auto) for `llama-server`, resolved to 4 slots
(`tools/server/server.cpp:126-129`); `.ufo/waves/round-91/w1/RV02ThresholdRows.md` BLOCKER-1, corroborated by
`w1/SC01SourceReopen.md`. C2 kill rule K2 fired: C2 not verified. Captured-by: K2 (non-author reviewer read) —
fired as designed; the frozen counter (B1-B7) binds the literal on the line and cannot see it (disclosed limit in
the plan). Fix: QUALITY KQ146 (the default must be the binary's: argument parser or `--help`) and the
`--help` check `.ufo/waves/round-91/measured/kq146-help-check.py`. Shown able to fail:
`measured/kq146-help-check.out` — `KQ146_ROW T07 … row_value=1 help_default=-1 DISAGREE`, `disagree=1`, exit 1;
T01-T06 agree.

**M2 — the fix's own comment names the wrong mechanism.** Class: a cost explanation in code no isolated test
reproduces. Evidence: `tools/kama-probe.sh` at `3decfa36` line 934 calls `${C_SERVED%,}` "quadratic"; SB01's bench
(`w1/out/SB01LessonDraft/bench-suffix-removal.out`) shows a matching suffix strip in 0.021 s and a non-matching one
in 63-69 s on 1.8 MB — the cost is the unmatched scan, and the base strip never matched (no trailing comma).
Captured-by: none (the counter grades wall time, correctly). Fix: routed (comment rewording, round 92 §Planned);
no verdict changes. Shown able to fail: the bench's three cases, 3 000× apart.

**M3 — a byte cap left time unbounded** (round 90 → 91). Class: the instrument bounds the resource the previous
fix touched. Evidence: `controls/c1-base.out` (T1/T2/T4/T5 killed at 120 s, T3 `MODEL_OK` at 75.7 s); r90 closure
R5. Captured-by: r90 closure R5. Fix: C1 (`BUDGET = 20 s` inside every pass condition). Shown able to fail:
`controls/c1-base.out`, `controls/c1-f1-count-cap.out`.

**M4 — a probe change staled another capability's receipt, and the harm list did not name it.** Class: harm
outside the frozen kill list (an instrument bound to the probe's sha256). Evidence: wave-1 SC02 F6
(`.ufo/waves/round-91/w1/SC02QuadraticSweep.md`): `tools/round90-reason-rows.py` at the C1 measured commit prints
`bound=0 unbound=24 receipt=stale`, because the round-90 receipt binds the base probe `b71c309a`; receipt
`.ufo/waves/round-91/measured/r90-reason-rows-stale.out` (rev `3c4f6a1e`, exit 1). Captured-by: none — C1's K2 harm
suite (`controls/harm.sh`) lists five suites and not the reason-row counter. Fix: receipt re-captured at the current
probe (`tools/round90-reason-capture.py`, `measured/r90-reason-recapture.out`); the 24 (cell, reason, verdict) triples
are identical to the prior receipt (`measured/r90-reason-cells-prior.jsonl` vs `-recaptured.jsonl`), so no reason or
verdict changed; the counter re-binds 24/24 at the landing commit (`measured/r90-reason-rows-tip.out`). Routed: a
successor harm list names every probe-sha-bound instrument. Shown able to fail: the stale receipt above.

**Driver-side note (not a lane mistake, orchestrator ruling).** Attempt 2 found `w1.ready` (l1 `KamaR91`) marked
`.partial.dead` and wrote a new wave `w1a2` with the same 12 items. The orchestrator had already re-spawned `w1` under
the attempt-2 label (`live()` matches `KamaR91` → `KamaR91a2`) at 20:23:18; `w1a2` spawned at 20:24:52; the
orchestrator cancelled 5 `w1a2` seats; twin seats shared scratch paths and one `rm -rf` wiped a twin's work
(each re-ran). Canonical wave: `w1`. Lane-side lesson: before writing a successor ready, `read proc://` for the
seat names (§6 run-6 rule) — the check that would have shown `w1` live.

## Dispositions of the round-90 closure (R1–R6)

- R1 `round75-instruments` red (`bad_rows=19`): carried, L0 still open.
- R2 verified-at: dated correction in `corpus/knowledge/probe-answer-bounds.md` (landed `3f317ecd`).
- R3 `router-?` reason: wave-1 SC02 F6 confirms it is still printed and absent from SKILL §Probe reason codes; carried to round 92.
- R4 latency budget pin: C1's counter puts a 20 s budget in every cell (`tools/round91-answer-time.py`); a
  persisted budget in `tests/` is still absent (EX02 proposed line, `w1/EX02NoPythonPath.md`): carried.
- R5 time bound: C1. Counter limits (CR01: expected id always last, probe identity not compared, `served_model`
  unread; MT01: router filter unowned) are routed to round 92.
- R6 held-out LIMIT cells and alias pins: carried.
