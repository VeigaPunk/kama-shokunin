<!-- Draft by seat SB01LessonDraft (round 91, wave w1a2, attempt 2) for the L1 to integrate as the round's
     `## Gate` and `## Mistakes`. Every fetch and every measurement below was run by this seat on
     2026-11-06; digests were compared with the committed `corpus/SOURCES.md` rows, not copied from them.
     Access date for every row: 2026-11-06. Host load during the fetches and timings: 30-44 (32 cores).
     Receipts: `sources-recheck.out`, `bench-suffix-removal.out` in this directory. -->

## Gate

| Candidate | Decision | URL / access date | Located quote (≤25 words) and location | Reason |
|---|---|---|---|---|
| S592 POSIX.1-2024 `awk` (The Open Group Base Specifications Issue 8) | **admit** (A, spec, mined) | https://pubs.opengroup.org/onlinepubs/9799919799/utilities/awk.html — 2026-11-06, sha256 `6df7d0776af4b28dbc3ec667a02a18e51ccd5066ea45a22166214e7e3832f898`, 144 111 B, 2 485 lines (equal to the row) | "value of each array element shall be a string consisting of the value of that variable" (lines 796-797); "all environment variables shall be visible via the awk variable ENVIRON" (line 185) | Grounds both halves of `AWK_NORM`: an assignment operand is read "as a STRING token" (lines 107-108), so `-v`/operand assigns escape-process backslashes, while `ENVIRON` carries the value itself; an element may be a numeric string (796-797), hence the `x ""` comparison. C1 cell T5 (1.9 M `a/` pairs ending `/good.gguf`) is green at M. |
| S593 llama.cpp `common/common.h` @ tag `b12177` | **admit** (A, code, mined) | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/common/common.h — 2026-11-06, sha256 `c3010a3c662a14556adb651b79bff00089564fde6b5e336959403e3db34e6073`, 58 830 B, 1 355 lines (equal to the row) | `int32_t timeout_read        = 3600;          // http read timeout in seconds` (line 634) | The exact tag of the binary the lane runs (b12177). This seat re-read every bound literal on its line: T01 632, T02 634, T03 636, T04 644, T05 669, T06 703, T07 464 — each present verbatim, so the seven C2 rows rest on the pin, not on prose. |
| S594 Ollama `envconfig/config.go` @ tag `v0.40.11` | **admit** (A, code, mined) | https://raw.githubusercontent.com/ollama/ollama/v0.40.11/envconfig/config.go — 2026-11-06, sha256 `0b0ea669b31cfe2b54313427257326a2b7a909bbc7bf8a671035efc446fb1895`, 16 343 B, 468 lines (equal to the row) | `Default is 5 minutes.` (line 128) … `keepAlive = 5 * time.Minute` (line 130) | Each default is set inside its function, not stated only in prose: T08 23, T09 130, T10 150, T11 277, T12 281 all carry the row's literal, and the doc comment above each value repeats the default (line 128 "Default is 5 minutes." for `keepAlive`, lines 146-149 for `loadTimeout`), so a moved default shows in two places. |
| S595 vLLM `vllm/envs.py` @ tag `v0.32.0` | **admit** (A, code, mined) | https://raw.githubusercontent.com/vllm-project/vllm/v0.32.0/vllm/envs.py — 2026-11-06, sha256 `e963af06cf6c775fe285147e0d811ea5b4d679e5cbd6958980ec2a0d1da70694`, 118 996 B, 2 488 lines (equal to the row) | "Timeout in seconds for waiting for engine cores to become ready during startup. Default is 600 seconds (10 minutes)." (lines 809-810) | T13/T14 literals are present at 26 and 111, and the executable defaults at 811-813 and 1143-1145. K2 note: the declaration block (lines 15-337) sits inside `if TYPE_CHECKING:` (line 14), so line 26 is a type-checker mirror of the getter at 811-813; the value is identical in both, but a row citing only line 26 cites a declaration, not the executed default. |
| GNU gawk manual `Assignment-Options.html` (plus `Command-Line-Options.html` and `https://www.gnu.org/`) | **reject** (not fetched) | https://www.gnu.org/software/gawk/manual/html_node/Assignment-Options.html — 2026-11-06 | — (0 bytes arrived; curl exit 28) | The host is unreachable, not one bad path: DNS resolves (`209.51.188.116`, `2001:470:142:5::116`) but TCP connect never completes (`conn=0.000000`, `ttfb=45.00/60.00 s`, `http=000`, 0 bytes); the host root page times out at connect on both `-4` and `-6` too. The lane recorded the same host timing out on 2026-10-20 (S053, `corpus/SOURCES.md:65`). No bytes → no quote and no row; the rule is already grounded at the spec by S592, and no admitted entry cites the manual (CORPUS rule 4). Flip: the page fetches (or an offline copy at a pinned tarball) and an admitted entry needs it. |
| SGLang v0.5.22 `python/sglang/srt/server_args.py` | **reject** (not mined) | https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/python/sglang/srt/server_args.py — 2026-11-06, sha256 `d1b9ffc79edcbc857efd02a47d47eed9b414f8ac44bc4e3214d78a7922e90e03`, 35 396 B, 893 lines | "Add fields to the matching namespace in ``arg_groups/fields/`` using" (lines 233-234) | At this pin the defaults are no longer in this file: `class ServerArgs:` (line 230) carries no field defaults, its docstring sends fields to `arg_groups/fields/` (233-234), and `add_cli_args` builds the CLI from the dataclass (line 352). The defaults live in `arg_groups/fields/serving.py` (opened this round: line 65 `host` = `"127.0.0.1"`, line 66 `port` = `30000`; sha256 `66a9ab458053c31290f21d9b7ce6686c7a9d83e6387f2a12a61a0e5599ff4923`, 13 638 B). A row on `server_args.py` has no threshold literal to bind; mining the field modules is the flip, not this round. |

Proposed `status` / `recheck` / `used-by` changes: none. The four admits are the rows C1/C2 already cite; the two
rejects add no row. `sources-census.sh` was not run by this seat (it reads the registry, which this seat did not change).

## Mistakes

**M1 — a cap that bounded bytes left time unbounded, and the round-90 cells were shaped so they could not see it.**
Class: a frozen instrument bounds the resource the *previous* fix touched (bytes) while the next defect spends another
(time); its largest legitimate cell was an order of magnitude below the pathological input (20 000 ids / 1 MiB vs
200 000 ids / 3.9 MB) and graded no seconds.

Evidence:
- `tools/round90-hostile-answers.py:311` — the largest legitimate answer is `big_ids = ["good"] + 20 000 ids`, padded
  to 1 MiB (line 313); its pass condition (line 314) grades the verdict only.
- `tools/round90-hostile-answers.py:185` — the only time bound is `timeout=90` on the whole run; no pass condition names
  seconds and the summary prints none, so a run of 89 s was a pass.
- The hostile cells cannot reach the per-id path: H1-H3 each expect the probe to refuse at the 4 MiB cap before parsing.
- `controls/c1-base.out` — on the very same 12 cells the base probe has T1/T2/T4/T5 `verdict=killed` at 120.10 s and T3
  `verdict=MODEL_OK reason=matched seconds=75.71`: the right verdict at 3.8× the 20 s budget, i.e. green under a
  verdict-only rule.
- The same cost was measured a round earlier (207 s for a 4 MiB answer of 200 000 ids, r89 SN01) and appears in
  `round-90-verifier-spotcheck.md:133` (R5) as a disclosed limit, not as a cell.

Captured-by: none in round 90. The 90 s kill is 4.5× the round-91 budget and only an answer an order of magnitude
larger could reach it; no cell sent one.

Fix: `tools/round91-answer-time.py` puts `BUDGET = 20 s` inside every pass condition, kills a run at 120 s, and adds
five large cells (T1 200 000 ids, T3 80 000 router entries, T4 one 3.9 MB id, T5 1.9 M `a/` pairs); the probe applies
the id rule in one awk pass and joins with `paste -sd,` (`tools/kama-probe.sh` at `3decfa36`, lines 445-471 and 933-935).

Shown able to fail: the same frozen counter on the base probe bytes prints `mismatches=5` (`controls/c1-base.out`); on
F1 (count cap at 1 000 ids) `mismatches=5` (`controls/c1-f1-count-cap.out`); on F2 (no `normalize_id`, no fork)
`mismatches=5 positive_mismatches=1` (`controls/c1-f2-exact-match.out`). F2's T1 is verdict-correct and still fails on
time (45.49 s), so the green at M cannot be earned by truncation, by dropping the rule, or by a right answer that is slow.

**M2 — a number in a frozen round with no committed receipt, and one measurement point where the claim needs two.**
Class: provenance (a figure in the probe comment and an admitted entry whose measurement was never committed) plus
calibration (a growth claim inferred from a single input size).

Evidence:
- `tools/kama-probe.sh` at `3decfa36`, lines 933-934: "the earlier `${C_SERVED%,}` took 38 s on a 1.6 MB list in a UTF-8
  locale (bash suffix removal is quadratic there)"; `corpus/knowledge/probe-answer-bounds.md:79` repeats it.
- No receipt under `.ufo/waves/round-91/controls/` or `measured/` isolates a suffix-removal timing; the figure exists
  only in prose (grep for `took 38` finds the probe comment, the entry, and a seat draft).
- This seat's bench (`bench-suffix-removal.out`; `/usr/bin/bash` 5.3.20, the probe's interpreter; load 27-44): on
  1 600 000-byte id lists, `${s%,}` where the pattern does **not** match at the end = 47 221 ms (a repeat read 43 849 ms),
  i.e. the same order as the 38 s quoted at lower load; the same string with a trailing comma (pattern **matches**) =
  19 ms; the same unmatched string timed in a bash whose own locale is C = 7 796 ms (5.6× faster on that one size,
  growth there not measured).
- The doubling series settles "quadratic": 400 000 B = 2 635 ms, 800 000 B = 11 220 ms, 1 600 000 B = 47 221 ms —
  4.26× and 4.21× per doubling (linear would be 2×). One size cannot show this: this seat's own first single-point
  reading (1.8 MB = 66 s under the tool shell's bash 5.2.37) is equally consistent with a linear story.
- The base probe always hit the unmatched case: `ids=$(served_ids "$FBODY")` (line 932) strips the trailing newline, so
  `tr '\n' ','` (base line 915) leaves no trailing comma and `${C_SERVED%,}` (base line 916) removed nothing while still
  paying the scan. F1 corroborates the magnitude: 39.38 s on T1 with the per-id fork already removed.

Captured-by: this seat's bench only; no frozen cell can distinguish the mechanism (the round-91 cells grade wall time,
correctly). The figure was not contradicted — it was unattributed, and no committed receipt backs it.

Fix: commit the bench next to the comment (or cite F1's residual), keep "quadratic" (the doubling series supports it),
and add the unlike-pattern condition — the 38 s is a non-matching removal, not suffix removal in general (19 ms when it
matches). No code change.

Shown able to fail: matched vs unmatched differs by ~2 500×, and the per-doubling ratio separates quadratic (4.2×) from
linear (2×); a future sentence that drops the condition or the growth claim would be contradicted by this receipt.

Note for the integrator: the attempt-1 seat's draft of this section (`.ufo/waves/round-91/w1/out/SB01LessonDraft/round-91-lesson-draft.md`,
untracked) concludes from one 1.8 MB point that the cost is "linear … not quadratic". Its 68.57 s agrees with this seat's
66 s at the same size; its inference does not survive the doubling series above.

**M3 — a shared scratch path let one attempt's mandatory cleanup delete another attempt's live work.**
Class: write-scope/scratch isolation; the round gave two attempts of the same seat the same scratch directory.
Evidence: at 20:26 `/fast/scratch/hyaku/kama-r91/SB01LessonDraft/` held both this seat's fetches and a peer's files
(`f/server_args.py`, `t/list16.txt`); at 20:36 it was gone (`ls` → "No such file or directory", `cd` → "i/o error"); the
peer `SB01LessonDraft` had been live in the same window (proc:// at 20:33) and the contract requires each seat to `rm -rf`
its scratch before yielding.
[INFERENCE] that cleanup removed the shared directory. This seat lost its fetched sources and id lists mid-bench and
re-fetched into `.../SB01LessonDraft-a2/`. Captured-by: nothing in the contract distinguishes the two attempts (same seat
name, same path); the loss was visible only as a failed `cd`.
Fix: namespace scratch per attempt (`<seat>/<attempt>/`, or a suffix), and remove only the directory the seat created.
Shown able to fail: the failed `cd`/`ls` and the re-fetch receipt (`sources-recheck.out` names the re-created path).

**M4 — a frozen cell that the do-nothing control already passed** (round 90, M1). Class: non-discriminating cell.
Evidence: `corpus/lessons/round-90.md:24-31` — the first H4 cell scored `ok=1` on the base probe, so the cell could not
distinguish the fix. Captured-by: §9 claim sizing (the base control ran before freeze). Fix: H4 also requires every
header cell non-empty. Shown able to fail: base `ok=0 header_cols=9 empty_header_cols=2` vs M `ok=1 header_cols=7`
(`controls/c1-base.out`, `measured/c1.out`).

**M5 — an instrument broken by its own stub, caught only by its positive cells** (round 90, M2). Class: stub fault
mistaken for a probe verdict. Evidence: `corpus/lessons/round-90.md:33-42` — all 13 cells printed `NOT_HTTP`; the hostile
cells "passed" and only the five positive cells went red (`positive_mismatches=5`). Captured-by: the positive cells
(KQ144). Fix: the stub writes its own status line. Shown able to fail: F1 blanket-refusal
`mismatches=6 positive_mismatches=5` (`controls/c1-f1-blanket-refusal.out`).

**M6 — a control expectation written from intent, not from the counter's rule** (round 90, M3). Class: label before
run. Evidence: `corpus/lessons/round-90.md:44-48` — the label said `bound=1 unbound=4`; the counter binds the duplicate
row and fails it through `duplicates=1` (`bound=2 unbound=3`). Captured-by: none (unreviewed label). Fix: the label was
corrected before freeze and both values recorded. Shown able to fail: the receipt disagrees with the first label by
construction; there is no separate failing run, and the lesson says so.

**M7 — a sanitizer that dropped what it could not print changed the verdict** (round 90, M4; M5 in the same round is the
same channel). Class: sanitize-by-dropping on a parsed input; a new branch ordered before the branch it shadows.
Evidence: `corpus/lessons/round-90.md:50-66` — a control character in a router id made M print `MODEL_OK
expected-wildcard` where base printed `MODEL_LOADING`, and a cap branch graded a 401 `FOREIGN_SERVICE body-too-large`
where base printed `UNAUTHORIZED_SERVICE http-401`. Captured-by: the plan's held-out rule, through a wave reviewer; no
QUALITY criterion. Fix: keep and escape the id (`a09effae`); `strip_ctl` drops 0x80-0xFF from header evidence; exit 63
with 401/403 keeps the auth verdict. Shown able to fail: the M column of
`repair/rv01-matrix-base-M-Mprime.out` (rows `router-ctlid-loading`, `badutf8server`, `big401`).

**M8 — cost harm outside the frozen kill rules** (round 89, M4; M1's ancestor). Class: a claim measured only on
verdicts, so a correct-but-slower commit passes. Evidence: `corpus/lessons/round-89.md:63-72` — +1.3-1.4 s per live check
at `4f9eacf7`; a 219-byte answer stalled the probe 41.4 s. Captured-by: none — K2 named verdict suites, not latency.
Fix: repair `5b1e0fb3`; round 91 then put the bound into the pass condition (M1). Shown able to fail: the EX02/SN01
receipts at `4f9eacf7`.

**M9 — a mutating git command in the lane** (round 89, M2). Class: write-scope breach. Evidence:
`corpus/lessons/round-89.md:44-50` — `git worktree add` from the lane registered a worktree in the lane's
`.git/worktrees`. Captured-by: the round-prompt write-scope rule, which the L1 had not applied to `worktree`. Fix:
`git clone --shared <lane> <scratch>` for clean checkouts. Shown able to fail: `git worktree list` printed two entries
before removal.

**M10 — vacuous control arms: the subject never entered the population the arm tested** (round 86, M3/M7). Class:
control attribution. Evidence: `corpus/lessons/round-86.md:52-60,143-150` — with the exclusion disabled the selftest still
printed `pass=11 fail=0` because the fixture emitted the stale cell first; the paragraph-coupling, row-first-wins and
first-`## Axes` rules had no arm at all (M7).
Captured-by: KQ139. Fix: the fixture emits the shadow first and gains arms for the unarmed rules. Shown able to fail:
each mutant run exits 1 naming its own arm.

**M11 — five rounds on a self-referential calibration instrument** (round 88, M1). Class: a claim whose oracle is the
lane's own parser of its own prose. Evidence: `corpus/lessons/round-88.md:33-41`; MANIFEST closures r83-r87. Captured-by:
none — claim sizing asks for a do-nothing control, not for an author-independent oracle. Fix: the oracle is the
runtime's own answer (a real completion) or a mined upstream line. Shown able to fail: `controls/c2-pointer-only.out`
(partial fix still `mismatches=4`) and the forged probes `controls/c1-f1.out`/`c1-f2.out`.
