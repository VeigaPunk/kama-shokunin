# Round-91 lesson — draft sections for `corpus/lessons/round-91.md`

<!-- Draft by seat SB01LessonDraft for the L1 to integrate. Everything below the line is written to be
     pasted as the round's `## Gate` and `## Mistakes`; the preamble above it is not lesson text.
     Every fetch below was run by this seat on 2026-11-06 (curl 8.23.0, bash 5.3.20, python 3.14.8);
     digests were compared to the committed `corpus/SOURCES.md` rows, not copied from them.
     Access date for every row: 2026-11-06. Load during the measurements: 19-46 (32 cores). -->

## Gate

| Candidate | Decision | URL / access date | Located quote (≤25 words) and location | Reason |
|---|---|---|---|---|
| S592 POSIX.1-2024 `awk` (The Open Group Base Specifications Issue 8) | **admit** (A, spec, mined) | https://pubs.opengroup.org/onlinepubs/9799919799/utilities/awk.html — 2026-11-06, sha256 `6df7d0776af4b28dbc3ec667a02a18e51ccd5066ea45a22166214e7e3832f898` (re-fetched by SB01: equal to the row) | "as if they appeared in the awk program preceded and followed by a double-quote ('"') character, as a STRING token" (lines 107-108); "all environment variables shall be visible via the awk variable ENVIRON" (line 185); the element "shall be considered a numeric string" (lines 796-797) | Grounds both halves of `AWK_NORM`: an assignment operand is escape-processed, so the expected id must reach awk through `ENVIRON` (line 107-108 vs 185), and an `ENVIRON` element may be a numeric string, so ids compare as strings with `x ""` (lines 796-797). Fixed edition ID in the URL, no moving ref. |
| S593 llama.cpp `common/common.h` @ tag `b12177` | **admit** (A, code, mined) | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/common/common.h — 2026-11-06, sha256 `c3010a3c662a14556adb651b79bff00089564fde6b5e336959403e3db34e6073` (equal to the row) | `int32_t timeout_read        = 3600;          // http read timeout in seconds` (line 634); `int32_t port                = 9931;` (line 632) | The tag of the binary the lane runs: `llama-server --version` → `build 12177, commit 6c01da627`, sha256 `ba272ee3…` = the harm receipts' `server_sha256`. This seat re-read all seven bound lines: 632, 634, 636, 644, 669, 703, 464 — each SKILL T01-T07 literal is present there verbatim. |
| S594 Ollama `envconfig/config.go` @ tag `v0.40.11` | **admit** (A, code, mined) | https://raw.githubusercontent.com/ollama/ollama/v0.40.11/envconfig/config.go — 2026-11-06, sha256 `0b0ea669b31cfe2b54313427257326a2b7a909bbc7bf8a671035efc446fb1895` (equal to the row) | `keepAlive = 5 * time.Minute` (line 130; doc comment line 128 "Default is 5 minutes.", 126-127 negative = infinite, zero = none) | Five defaults read inside their functions, so they are runtime defaults and not prose: lines 23, 130, 150, 277, 281 all carry the SKILL T08-T12 literals verbatim (re-read by this seat). |
| S595 vLLM `vllm/envs.py` @ tag `v0.32.0` | **admit** (A, code, mined) | https://raw.githubusercontent.com/vllm-project/vllm/v0.32.0/vllm/envs.py — 2026-11-06, sha256 `e963af06cf6c775fe285147e0d811ea5b4d679e5cbd6958980ec2a0d1da70694` (equal to the row) | "Timeout in seconds for waiting for engine cores to become ready" (line 809); `VLLM_ENGINE_READY_TIMEOUT_S: int = 600` (line 26) | Both values are corroborated twice in the same file: the annotation (26, 111) and the runtime getter — `os.environ.get("VLLM_ENGINE_READY_TIMEOUT_S", "600")` (812), `os.environ.get("VLLM_HTTP_TIMEOUT_KEEP_ALIVE", "5")` (1143), with the doc comments at 809-810 and 1142. `K2` caveat: lines 26 and 111 sit inside `if TYPE_CHECKING:` (16), so they are type-checker mirrors; the executable defaults are at 812/1143. The row's value and decision still fit its line. |
| GNU gawk manual, `Assignment-Options.html` and neighbours | **reject / not admitted** | https://www.gnu.org/software/gawk/manual/html_node/Assignment-Options.html, `Variable-Assignment-Options.html`, `Options.html`, `index.html`, and https://www.gnu.org/ — 2026-11-06 | — (no bytes arrived) | Not a bad page but an unreachable host: every one of the five paths returned curl `rc=28`, `http=000`, 0 bytes, "Connection timed out after 20001/45001 ms"; DNS resolves (`2001:470:142:5::116`, `209.51.188.116`) and `curl -v` shows the TCP connect timing out on both families. This reproduces the L1's `rc=28` and shows it is host-wide, not one bad URL, so page existence cannot be judged from here. No loss to C1: S592 (reachable POSIX spec) grounds the same rule. Flip: gnu.org reachable, or an archived copy staged with its sha256 — then a row with a located line. |
| SGLang v0.5.22 `python/sglang/srt/server_args.py` | **reject / not mined** | https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/python/sglang/srt/server_args.py — 2026-11-06, `http=200`, 35 396 B, sha256 `d1b9ffc79edcbc857efd02a47d47eed9b414f8ac44bc4e3214d78a7922e90e03`; dir listing `api.github.com/.../arg_groups?ref=v0.5.22` 39 entries | `from sglang.srt.arg_groups.fields.serving import (` (line 177); in `arg_groups/fields/serving.py`: `stream_interval: A[` … `] = 1` (lines 256-260) | At this pin the defaults are no longer on `server_args.py`: the class imports per-domain modules from `sglang/srt/arg_groups/fields/` (serving, parallel, schedule, memory, observability, …), and `grep -n "timeout\|keep_alive" server_args.py` returns nothing. A row binding a value to a line of `server_args.py` would be false. Flip: mine `arg_groups/fields/*.py` at a pin, one row per parameter carrying that file's own sha256. |
| `corpus/knowledge/serving-thresholds.md` | **admit** | cites S593-S595 + own receipts | — | Not new ground on the engine side — `endpoint-identity.md` (the probe's own waiting) and `router-mode-readiness.md` (router `status`) were held — but the *other* side's clocks were not: the lane bounded only its own timeout. The entry names its prior art, its recheck rule (a pin bump is a new row, never an edit) and `measured/c2.out` (14/14 bound, 3 engines). No row was measured on a live server, and the entry says so. |
| `corpus/knowledge/probe-answer-bounds.md` round-91 addition | **admit** (append, not a new entry) | cites S592 + receipts | — | The append adds the time bound the round-90 section lacked (per-id fork and the join/strip line, with base and M receipts) and carries the round-90 closure's R2 correction re-pointing `verified-at` to M′ `a09effae`. It states the limits it does not cover. See mistake M2 below for the one wording the append inherits from the probe comment. |

Proposed `status`/`recheck`/`used-by` changes: S592-S595 as committed (`mined`, `opened 2026-11-06`, `recheck on-release`,
`used-by` the two knowledge entries); `sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` → exit 0,
`kama ok`. No existing row changes.

## Mistakes

**M1 — a cap that bounded bytes left time unbounded, and the round-90 cells were shaped so they could not see it.**
Class: a frozen instrument bounds the resource the *previous* fix touched (bytes) while the next defect spends another
(time); its largest cell sat two orders of magnitude below the pathological input. Evidence: `controls/c1-base.out` —
T1/T2/T4/T5 `verdict=killed` at 120.10 s and T3 `verdict=MODEL_OK reason=matched seconds=75.71`, i.e. the **right
verdict at 3.8× the 20 s budget**: with round 90's grading (verdict only) that cell is green. The round-90 counter
grades no time at all — `tools/round90-hostile-answers.py:185` `timeout=90` per run, no seconds in its output — and its
largest list is `big_ids` 20 001 ids (`:311`); `plans/round-90-claims.md` §C1 names no time bound. Captured-by: round-90
closure R5 (SN01's 207 s for a 4 MiB answer of 200k ids) and SCORECARD §Planned (round 91) item 1/6 — carried as prose,
never as a cell. Fix: `tools/round91-answer-time.py` puts `BUDGET = 20 s` inside every pass condition and `KILL = 120 s`;
the probe applies the id rule in one awk pass (`AWK_NORM`, `model_matches`, `router_match`) and joins with `paste -sd,`
(`tools/kama-probe.sh` at `3decfa36`, lines 445-471 and 935). Shown able to fail: `controls/c1-base.out` (5 mismatches,
4 kills) and two forgeries cut from the base bytes — F1 count cap `probe_sha256=71ab0910…` `mismatches=5` T1/T2 wrong
verdict at 39-45 s, T4/T5 killed (`controls/c1-f1-count-cap.out`); F2 exact match `positive_mismatches=1` on P2
(`controls/c1-f2-exact-match.out`). Both forgeries also show the *shape* of the residual cost: with the per-id fork
already removed they still spend 39-45 s on the 200k-id cells, so the join/strip line — not only the fork — carried it,
and the single multi-MB-id cells stay killed at 120 s, so those are the pattern expansion.

**M2 — the fix's own explanation of that cost is wrong in kind.** Class: a mechanism asserted in a code comment that no
isolated test reproduces as stated. Evidence: `tools/kama-probe.sh` at `3decfa36` line 934 says "${C_SERVED%,} … took
38 s on a 1.6 MB list in a UTF-8 locale (bash suffix removal is quadratic there)". Measured by this seat (bash 5.3.20,
C.UTF-8, load 24-46) on one 1 800 000-byte comma list: `s=${s%","}` where the pattern **matches** the last character =
0.021 s; `s=${s%X}` and `s=${s%"X"}` where it **does not** = 68.57 s and 62.95 s (`out/SB01LessonDraft/bench-suffix-removal.out`).
So the cost is the unmatched suffix scan (every split point, multibyte-aware) — linear in bytes with a ~35 µs/character
constant, not quadratic. And in the base probe the pattern never matched: `ids=$(served_ids …)` strips the trailing
newline, so `tr '\n' ','` emits no trailing comma and the `%,` strip was a **no-op that still paid the scan** (F1 receipt:
39.38 s on T1 with the fork already gone). Captured-by: this seat's bench only; no counter can distinguish mechanism, and
the frozen counter correctly grades wall time instead. Fix: reword the comment to the measured mechanism (the advice it
carries — do not use that expansion here — is right); no code change. Shown able to fail: the same string has three
cases 3 000× apart (matching vs not), re-run below in the receipt.

**M3 — a cell the do-nothing control already passes** (round 90, M1). Class: non-discriminating cell. Evidence:
`corpus/lessons/round-90.md` M1 — the first H4 cell (`no stdout line starts with FORGED-ROW`) scored `ok=1` on the base
probe. Captured-by: §9 claim sizing (the cheapest control that skips the claimed work), which fired because the base
control ran before freeze. Fix: H4 also requires every header cell non-empty; base `ok=0 header_cols=9
empty_header_cols=2`, M `ok=1 header_cols=7` (`controls/c1-base.out`, `measured/c1.out`). Shown able to fail: the base row.

**M4 — a measured commit that was correct but 10× slower, with no cost in the kill rules** (round 89, M4 — M1's
ancestor). Class: cost/robustness harm not named by any frozen clause. Evidence: `corpus/lessons/round-89.md` M4 —
`w1/EX02HarmSweep.md` measured +1.3-1.4 s per live check at `4f9eacf7`; `w1/SN01ProbeSafety.md` F1 stalled 41.4 s on a
219-byte answer. Captured-by: none — K2 named verdict suites, not latency or bounded work; the round-90 closure then
routed the same class again (`round-90-verifier-spotcheck.md` R5, "no time bound"). Fix: repair `5b1e0fb3`, then round 91
puts the bound in the pass condition itself (M1). Shown able to fail: those receipts, and now `controls/c1-base.out`.

**M5 — a frozen counter that grades the verdict column only** (round 89, M3). Class: instrument narrower than the change
it certifies. Evidence: `corpus/lessons/round-89.md` M3 — `tools/round89-unloadable-cells.py` compares verdicts only, so
MT01 mutant M23 drops both `router-model-*` reasons and still prints `mismatches=0` (23 of 31 single-point mutants escape).
Captured-by: the round-88 MT01 finding, routed as "held-out cells" rather than "grade the reason"; no QUALITY criterion.
Fix: the claim stays on its frozen verdict predicate; the harm harness grades verdict, reason and exit
(`tests/probe-verdicts/`). Shown able to fail: `.ufo/waves/round-89/measured/harness-r5.out` — base `passes=74` of 77.

**M6 — five rounds on a self-referential calibration instrument** (round 88, M1). Class: claim whose oracle is the lane's
own parser of its own prose. Evidence: `corpus/lessons/round-88.md` M1 and `round-87-verifier-spotcheck.md` §2 C1
("successor passes its own battery but fails the frozen population rule"); MANIFEST closures r83-r87. Captured-by: none —
claim sizing asks for a do-nothing control, not for an oracle independent of the author. Fix: the oracle is the runtime's
own answer (a real completion) or a mined upstream line, never lane text. Shown able to fail: `controls/c2-pointer-only.out`
(partial fix still `mismatches=4`) and the forged probes `controls/c1-f1.out`/`c1-f2.out`.

**M7 — "new coverage ground" asserted without sweeping the lane's own corpus** (round 88, M4 → KQ143). Class: admission
reason not checked against held knowledge. Evidence: `corpus/lessons/round-88.md` M4 — `served-identity-crosswalk.md:28`
already held the router `status` vocabulary; caught by wave seat CN01 after landing, and the round-88 closure "disagrees
with the admission as landed". Captured-by: the connector seat; the census gate checks row shape, not admission reasons.
Fix: Gate reason corrected; KQ143 binds a "new ground" admission to an own-corpus sweep. Shown able to fail:
`grep -ril "router" corpus/knowledge` at base prints both prior entries.

**M8 — a counter that certifies the wrong bytes or the wrong subject** (round 86 R86V4, round 88 D1). Class: evidence
pointer bound to an instrument/revision that is not the one shipped. Evidence: `round-86-verifier-spotcheck.md` R86V4 (the
frozen counter executed worktree instrument bytes, not `--rev` bytes); `round-88-verifier-spotcheck.md` D1 (the capability
row's first green certified the superseded rule). Captured-by: a non-author closure, not the lane's own gate. Fix in
round 91: both counters read the probe with `git show <rev>:tools/kama-probe.sh` and print `probe=rev` with its sha256;
`--probe-file` prints `probe=override` and by construction cannot meet the predicate. Shown able to fail:
`controls/c1-f1-count-cap.out` and `c1-f2-exact-match.out` print `probe=override` (and both exit 1).
