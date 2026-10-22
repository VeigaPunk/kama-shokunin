# ReopenS109 evidence log

Seat: KamaR25a2.ReopenS109 (round 25, attempt 2, wave 2, falsify).
Lane master tip checked: fa3b62ae6475d111eb466d79af616aeebb08bbb9.
Scope: corpus/SOURCES.md:121 (row S109); corpus/lessons/round-25.md:25 (Gate line); the uses of S109 in corpus/knowledge/context-capacity.md and SKILL.md.
No llama-server child was started. No port was opened. No tool was installed or upgraded.
Scratch outside the lane: /fast/scratch/hyaku/kama-r25a2w2/ReopenS109/ (fetched server-context.cpp and llama.h, committed copies of the three lane files).

## 1. Commands and exit codes

1. `curl -fsSL -o .../ReopenS109/server-context.cpp https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp` gave exit 0. Fresh fetch on 2026-10-22.
2. `sha256sum .../ReopenS109/server-context.cpp` gave exit 0 and `dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329`.
3. `wc -l` gave 6320 lines. `stat -c %s` gave 264205 bytes, the same size the wave-1 seat recorded (`.ufo/waves/round-25/a2-build/advice/SrcCtxExceeded.md:7`).
4. `curl -fsSL -o .../ReopenS109/llama.h .../704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/include/llama.h` gave exit 0. `sha256sum` gave exit 0 and `961430f89e2553dbcd99e3e6c59826af9ec143f05911520c74f804d986ff3cd2`, 1746 lines.
5. `curl -fsSL https://api.github.com/repos/ggml-org/llama.cpp/git/refs/tags/b11755` gave exit 0. The object sha is `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad`, type `commit`.
6. `git -C /home/vgpnk/Projects/shokunin/kama-shokunin show fa3b62ae6475d111eb466d79af616aeebb08bbb9:<path>` for corpus/SOURCES.md, corpus/lessons/round-25.md and corpus/knowledge/context-capacity.md gave exit 0, 0, 0. Read-only git; output written to scratch.
7. `cmp -s` committed against working copy: SOURCES.md exit 0; context-capacity.md exit 0; round-25.md exit 1.
8. `diff -u` committed against working round-25.md gave exit 1. One hunk, `@@ -48,8 +48,9 @@`, in the Mistakes table (lines 48-56). The Gate line 25 is identical in both copies.
9. Search for `purging slot` in .ufo/waves/round-25/final/raw/L1.server.log: no match. Search for `immutable|frozen` in corpus/SOURCES.md: lines 3, 254, 265.

## 2. Row S109 (corpus/SOURCES.md:121) against the fresh fetch

Line numbers are from the fetched file (grep and numbered reads).

| cell | claim | fetched file | verdict |
|---|---|---|---|
| anchor sha256 | dd1de0f2...2329 | command 2 | holds |
| URL | tools/server/server-context.cpp at 704366d76 | command 1 fetched it | holds |
| release b11755 | tag resolves to the pinned commit | command 5; L1 log line 4 `build 11755 (704366d76)` | holds |
| decode | "`decode` lines 4294-4341" | `bool decode(int32_t & n_batch, int32_t off) {` is at 4253. 4294-4341 is the failure branch inside decode, not the whole function | holds as a range; label should say "failure branch" |
| failure branch | 4294-4341 | `if (ret != 0) {` 4294; `return false; // retry with the updated n_batch` 4341 | holds |
| error string | 4298-4301 | `if (n_batch == 1 && ret == 1) {` 4298; `err = "Context size has been exceeded.";` 4301 | holds |
| send, release, clear | 4318-4327 | `for (auto & slot : slots) {` 4318; `if (slot.is_processing()) {` 4319; `send_error(slot, err);` 4320; `slot.release();` 4321; `slot.prompt_clear();` 4325; loop closes 4327 | holds |
| throw | 4330 | `throw std::runtime_error(err);` 4330 | holds |
| halving | 4334-4337 | comment 4334; `if (!try_clear_idle_slots()) {` 4335; `n_batch /= 2;` 4336; close 4337 | holds |
| caller retry and abort | 3331-3356 | `for (int32_t off = 0; ...)` 3331; `bool ok = decode(n_batch, off);` 3338; `n_batch = llama_n_batch(ctx_tgt);` 3348; `continue;` 3351; `catch` 3353; `abort_all_slots(...)` 3355; `break;` 3356 | holds |
| try_clear_idle_slots | 1810-1835 | def 1810; `if (!params_base.kv_unified) {` 1813; `return res;` 1814; `return res;` 1834; close 1835 | holds |
| update_slots | named in teaches | `void update_slots() {` 3256 | holds |
| abort_all_slots | named in teaches | `void abort_all_slots(...)` 3217; body 3218-3223 acts only on `is_processing()` slots | holds |
| is_processing and release | used for the no-op claim | `is_processing()` 499-500; `release()` 586-594, state set IDLE at 594 | holds |

## 3. Gate line (corpus/lessons/round-25.md:25)

Quote: `err = "Context size has been exceeded."`, with the guard `if (n_batch == 1 && ret == 1)`.
Fetched line 4301 is `                    err = "Context size has been exceeded.";`. Exact substring.
Guard at 4298 matches exactly.
Words: 5 (limit 25). Verdict: holds. Committed and working copies identical at line 25.

## 4. Teaches cell, clause by clause

Teaches (SOURCES.md:121): "On decode failure ret == 1 with n_batch > 1, the server halves n_batch (unless try_clear_idle_slots purges an idle slot) and retries; once n_batch == 1 still fails, every processing slot is sent `Context size has been exceeded.`, its context is cleared (prompt_clear), and update_slots aborts via throw, abort_all_slots and break."

| clause | lines | verdict |
|---|---|---|
| ret == 1 with n_batch > 1 reaches halving | ret == -1, ret < -1 and n_batch == 1 guards are false here (4298, 4304, 4308), so err stays empty and control reaches 4335 | holds. Sufficient condition. Same branch also runs for ret == 2 (TODO at 4313); outside the KV claim |
| halves n_batch | 4336 | holds |
| unless try_clear_idle_slots purges an idle slot | purge needs `params_base.kv_unified` (1813-1815 return false otherwise); idle slot with tokens (1818-1822); returns true after one purge (1825, 1827, 1830) | holds, but the unified-cache precondition is omitted (F3) |
| and retries | 4341 `return false`; caller `continue` 3350-3351 | holds |
| once n_batch == 1 still fails | 4298 | holds |
| every processing slot is sent the error | 4318-4320 | holds |
| context cleared (prompt_clear) | release 4321, then prompt_clear 4325 | holds; release is not named (F6) |
| update_slots aborts via throw, abort_all_slots, break | throw 4330 inside decode() (4253); caught at 3353; abort_all_slots 3355; break 3356; enclosing function update_slots 3256 | holds |
| abort_all_slots effect | slots already released at 4321, so abort finds none processing (3218-3221) and sends nothing | [INFERENCE from code]; confirmed by L1 log: no send_error after line 1877 (lines 1878-1891 read) |

Scope cell check: "decoding fails because the KV cache is full" maps to ret == 1. llama.h at the pinned commit, line 1002: `1 - could not find a KV slot for the batch`. Line 1000: after ret 1, "the memory state is restored to the state before this call". L1 log lines 1758, 1763 and 1846: "failed to find a memory slot for batch of size 2 / 1". Holds.

## 5. The entry's uses of S109 (corpus/knowledge/context-capacity.md)

| line | text (abridged) | check | verdict |
|---|---|---|---|
| 1 | "S109 (tools/server/server-context.cpp full-cache decode path)" | scope wording matches the row | holds |
| 112 | "Order of events (S109, server-context.cpp 4294-4341)" | range matches the row's failure branch | holds |
| 113 | "when decoding finds no free KV space the server first halves the batch and retries" | no unified-cache purge step mentioned; server-context.cpp 4335 and 1813-1827 do purge first on a unified cache | simplification (F4). Did not happen in L1: no "purging slot" line in the L1 log |
| 114-115 | "when a batch of one still fails it sends ... to every processing slot, clears them and stops" | 4298, 4318-4320, 4325, 4330 | holds |
| 115-116 | "both slots were released at n_tokens = 1025 (lines 1849-1866)" | release lines 1852 (id 0, task 2) and 1866 (id 1, task 3), both `n_tokens = 1025` | holds, literal |
| 116-117 | "2 × 1025 cells overflow the 2048 pool" | pool is 2048 (log 284, 290, 816, 822, 1082). The 1025 counts the list after an unplaced token is appended; see section 7 | defect (F1) |
| 117-118 | "Both admitted requests failed, not only the newer one" | admitted at 1266 and 1270; errors at 1849 and 1863 | holds |
| 108 | L1 row: both HTTP 500 | not an S109 claim; S109 excludes HTTP rendering (SOURCES.md:121 scope) | holds as observed |

## 6. L1 raw log (.ufo/waves/round-25/final/raw/L1.server.log) against S109's path

| lines | event | matches |
|---|---|---|
| 4 | `build 11755 (704366d76)` | pinned commit |
| 9 | `n_parallel is set to auto, using n_parallel = 4 and kv_unified = true` | unified cache |
| 284, 290 | `llama_context: n_ctx = 2048`, `kv_unified = true` | 2048 pool |
| 1266, 1270 | tasks 2 and 3 admitted, `task.n_tokens = 1000` | both admitted |
| 1291-1292 | first `slot decode token ... n_tokens = 1000` | count before the append (see section 7) |
| 1748-1749 | `slot decode token ... n_tokens = 1024` for both | |
| 1753 | `decode: n_batch (effective) = 2048` | |
| 1758 | `failed to find a memory slot for batch of size 2` | ret 1 |
| 1760-1840 | `failed to find free space in the KV cache, retrying ... n_batch = 1024 ... 1` | halving path 4335-4339 |
| 1846 | `failed to find a memory slot for batch of size 1` | |
| 1848 | `decode: Context size has been exceeded. off = 0, n_batch = 1, ret = 1` | 4298-4301, 4316 |
| 1849 | `send_error: task id = 2` | 4320 |
| 1852 | `slot release: id 0 | task 2 | stop processing: n_tokens = 1025` | 4321 |
| 1854 | `slot prompt_clear: id 0 | clearing prompt with 1025 tokens` | 4325, 344 |
| 1863 | `send_error: task id = 3` | 4320 |
| 1866 | `slot release: id 1 | task 3 | n_tokens = 1025` | 4321 |
| 1868 | `slot prompt_clear: id 1 | clearing prompt with 1025 tokens` | 4325 |
| 1877 | `update_slots: decode() failed: Context size has been exceeded.` | 3353-3355 |
| 1878-1891 | no further send_error; shutdown | abort_all_slots sends nothing |
| search | no "purging slot" line in the file | no purge |

## 7. Cell accounting for L1 (F1)

- server-context.cpp 559-560 log `prompt.n_tokens()` inside the "slot decode token" line. Line 582, `prompt.tokens.push_back(sampled);`, appends afterwards. So the logged count is the count before the append.
- The first sampled token is logged at 1291 with `n_tokens = 1000`, which equals the prompt length (task.n_tokens = 1000 at 1266). Consistent with the count being taken before the append.
- At 1748-1749 the count is 1024 before the append, so the list holds 1025 after it. The failing decode at 1753-1758 is a batch of two new tokens, one per slot.
- server-context.cpp 4323-4324: "it's complicated to keep track of how much of the current batch has been processed before the error occurred".
- llama.h 1000: after ret 1 "the memory state is restored to the state before this call".
- [INFERENCE] Decoded cells per slot before the failing batch: 1024. Two slots: 2 × 1024 = 2048, which is the whole pool. The 1025 figure includes the one token per slot that could not be placed. The entry's "2 × 1025 cells overflow the 2048 pool" reads as if 2050 cells were resident. Conclusion (shared pool exhausted; both requests failed) stands. The figure is a stated inference presented as observation.
- Source of the arithmetic: `.ufo/waves/round-25/a2-build/advice/CriticLearningBarA2.md:75`, "1000 + 25 + 25 = 2050".

## 8. Other uses and used-by

- SKILL.md:688 cites S109 for "every processing request fails with HTTP 500 `Context size has been exceeded.`" and "L1 both failed at 1025 tokens each of a 2048 pool". The HTTP part is outside S109's scope (SOURCES.md:121: "not the HTTP status/body rendering"). The 1025 figure repeats F1.
- SKILL.md:689 cites S112 in the same way. Its used-by (SOURCES.md:124) is the entry only, so the used-by column does not list SKILL.md for siblings either. The registry text read (SOURCES.md:9-11, 126-153) does not define used-by. [INFERENCE: convention, not yet stated]
- corpus grep for S109 (corpus and tools): hits only in context-capacity.md (lines 1, 112) and round-25.md (lines 25, 36). Used-by is consistent with that.
- tools/kama-context-capacity.py, .ufo/waves/round-25/count-c2.py, preregistration.json and errata-attempt-2.json: no match for `S109|4294|4341|server-context|Context size`.
- Registry practice for corrections (SOURCES.md:254, 265; precedent S099 at line 111, "supersedes S092 — same teaching, corrected anchor"): old immutable cells stay as written; corrections go in a new supersedes row.
