# ReopenS109: row S109, its Gate line, and the entry's use of it (round 25, attempt 2, wave 2)

Verdict: defect found (minor). The S109 row's hash, line numbers, Gate quote and release tag all hold. The teaches cell claims nothing the lines do not show, but it leaves out one precondition. The entry (context-capacity.md:116-117) and SKILL.md:688 misstate the L1 cell count.

Lane tip checked: fa3b62ae6475d111eb466d79af616aeebb08bbb9. Evidence log with every command and exit code: `.ufo/waves/round-25/a2-falsify/out/ReopenS109/checks.md`.

## Findings, by severity

### F1. Medium. The L1 cell count is written as cells held, but it is not

- Where: `corpus/knowledge/context-capacity.md:116-117` ("2 × 1025 cells overflow the 2048 pool"). The same figure appears at `SKILL.md:688` ("both failed at 1025 tokens each of a 2048 pool"). The arithmetic comes from `.ufo/waves/round-25/a2-build/advice/CriticLearningBarA2.md:75` ("1000 + 25 + 25 = 2050").
- Evidence:
  - The server logs `prompt.n_tokens()` before the sampled token is pushed (`tools/server/server-context.cpp:559-560` log, `:582` push_back).
  - The first sampled token is logged with `n_tokens = 1000` at `final/raw/L1.server.log:1291`, which equals the prompt length (`:1266`, `task.n_tokens = 1000`). The count is taken before the append.
  - At `:1748-1749` the count is 1024. After the append the list holds 1025. Both slots are released at 1025 (`:1852`, `:1866`).
  - The failing decode at `:1753-1758` is a batch of two new tokens, one per slot.
  - `server-context.cpp:4323-4324` says the server does not track how much of a failed batch was processed.
  - `include/llama.h:1000` (pinned commit) says that after return 1 "the memory state is restored to the state before this call".
- [INFERENCE] Each slot had 1024 decoded tokens, which is the whole 2048-cell pool. Each slot's next token then had no cell. The 1025 counts that unplaced token. The claim that both requests failed stands.
- Smallest correction, in the entry at lines 116-117 and the same sentence in SKILL.md:688: "Both slots had 1024 decoded tokens each, which filled the 2048-cell pool [INFERENCE from server-context.cpp 559-582, L1 log 1748-1758, llama.h 1000]. Each slot's next token then had no cell. The log's `n_tokens = 1025` (lines 1852, 1866) counts that unplaced token."

### F2. Low. S109 is cited for HTTP 500, which its scope excludes

- Where: `SKILL.md:688` cites "(S109; ...)" next to "every processing request fails with HTTP 500 `Context size has been exceeded.`".
- Evidence: the S109 scope cell (`corpus/SOURCES.md:121`) says "not the HTTP status/body rendering".
- Smallest correction: take the HTTP 500 from the observed L1 row (`context-capacity.md:108`). Keep S109 only for "every processing slot gets the error" (`server-context.cpp:4318-4320`).

### F3. Low. The teaches cell omits the unified-cache precondition

- Where: `corpus/SOURCES.md:121`, teaches: "(unless try_clear_idle_slots purges an idle slot)".
- Evidence: `server-context.cpp:1813-1815` returns false before any purge when `!params_base.kv_unified`. On a split cache the halving always runs. The teaches says less than the lines, and nothing false.
- Smallest correction: the registry corrects a row by adding a new `supersedes S109 — ...` row, not by editing the old one (`corpus/SOURCES.md:254` and `:265` say immutable old cells stay as written; precedent S099 at `:111`). The superseding teaches should read: "(unless, on a unified cache, try_clear_idle_slots purges an idle slot that holds tokens, lines 1813-1827)". Until a superseding row lands, the entry carries the precondition (F4).

### F4. Low. Entry line 113 leaves out the purge step

- Where: `context-capacity.md:113`: "the server first halves the batch and retries".
- Evidence: on a unified cache the server first tries to purge an idle slot (`server-context.cpp:4335`, `:1813-1827`). No "purging slot" line appears in `final/raw/L1.server.log` (search: no match). So the L1 account holds, but the general sentence is incomplete.
- Smallest correction: insert before "halves": "on a unified cache it first purges an idle slot that holds tokens (server-context.cpp 4335, 1813-1827)".

### F5. Nit. The row's decode range is a branch, not the function

- Where: `corpus/SOURCES.md:121`, anchor: "`decode` lines 4294-4341".
- Evidence: `bool decode(int32_t & n_batch, int32_t off) {` is at `server-context.cpp:4253`. Lines 4294-4341 are the failure branch inside it.
- Smallest correction: "decode() failure branch, lines 4294-4341 (decode() begins 4253)". The range itself is correct.

### F6. Nit. The teaches cell does not say the failed slots are released first

- Evidence: `server-context.cpp:4321` releases each failed slot before `prompt_clear` (`:4325`). `abort_all_slots` (`:3217-3223`) then finds no processing slot and sends nothing. The L1 log has no send_error after line 1877 (lines 1878-1891 read).
- Not false. Optional addition if a superseding row is written anyway.

### F7. Info. The used-by convention is not stated

- S109 used-by lists only `context-capacity.md` (`SOURCES.md:121`). `SKILL.md:688` also cites S109, and `SKILL.md:689` cites S112. S112's used-by (`SOURCES.md:124`) also lists only the entry. The registry text read (`SOURCES.md:9-11`, `:126-153`) does not define used-by.
- No change proposed. The main agent should decide whether decision rows count as uses.

## Per-check verdicts

| # | check | verdict | line evidence |
|---|---|---|---|
| 1 | Fresh fetch; anchor sha256 | holds | `curl` exit 0; sha256 `dd1de0f2…2329`, equal to `SOURCES.md:121`; 264205 bytes, equal to the wave-1 seat's fetch |
| 2 | Release b11755 is commit 704366d76 | holds | GitHub API tag `b11755` → commit `704366d76…` (exit 0); `final/raw/L1.server.log:4` `build 11755 (704366d76)` |
| 3 | decode range 4294-4341 | holds, label nit (F5) | decode() at 4253; `if (ret != 0)` 4294; `return false` 4341 |
| 4 | error guard and string 4298, 4301 | holds | `if (n_batch == 1 && ret == 1) {` 4298; `err = "Context size has been exceeded.";` 4301 |
| 5 | send, release, clear 4318-4327 | holds | loop 4318; `send_error` 4320; `release` 4321; `prompt_clear` 4325; close 4327 |
| 6 | throw 4330 | holds | `throw std::runtime_error(err);` 4330 |
| 7 | halving 4334-4337 | holds | `if (!try_clear_idle_slots())` 4335; `n_batch /= 2;` 4336 |
| 8 | caller retry and abort 3331-3356 | holds | `for` 3331; `decode(n_batch, off)` 3338; `continue` 3351; `catch` 3353; `abort_all_slots` 3355; `break` 3356 |
| 9 | try_clear_idle_slots 1810-1835 | holds | def 1810; `kv_unified` check 1813-1815; `return res` 1834; close 1835 |
| 10 | Gate quote, right line, length | holds | `corpus/lessons/round-25.md:25`; quote at 4301 exact; guard at 4298 exact; 5 words (limit 25); committed and working copies identical at line 25 |
| 11 | teaches cell says only what the lines say | holds, with F3 and F6 | each clause checked in `checks.md` section 4; no over-claim found |
| 12 | scope: "KV cache is full" equals ret == 1 | holds | `llama.h:1002` "1 - could not find a KV slot"; L1 log 1758, 1763, 1846 "failed to find a memory slot" |
| 13 | entry line 1 and line 112 uses | holds | `context-capacity.md:1`, `:112` |
| 14 | entry line 113 | simplification (F4) | `:113` |
| 15 | entry 115-116 release at n_tokens = 1025 | holds, literal | L1 log 1852 (id 0), 1866 (id 1) |
| 16 | entry 116-117 "2 × 1025 cells overflow" | defect (F1) | section 7 of `checks.md`; `server-context.cpp:559-582`; L1 log 1291, 1748-1758 |
| 17 | entry 117-118 both requests failed | holds | admitted 1266, 1270; errors 1849, 1863 |
| 18 | SKILL.md:688 use | defect (F2), repeats F1 | `SKILL.md:688` |
| 19 | used-by | holds against siblings; F7 | `SOURCES.md:121`, `:124` |
| 20 | committed copy against working copy | holds | `cmp`: SOURCES.md exit 0, context-capacity.md exit 0; round-25.md exit 1, one `diff` hunk at lines 48-56 (Mistakes table only); Gate line 25 identical |

## What I checked that held, in brief

- The fetched file matches the anchor hash, the byte count recorded by the wave-1 seat, and every cited line number. Each cited line was read in the fetched file and matched by grep.
- The Gate quote matches line 4301 exactly and sits under the guard at 4298.
- The entry's account of the L1 path (halving 1024 to 1, the error at 1848, release and clear for both slots at 1025, the update_slots error at 1877) matches the L1 log line by line.
- The S109 row is the only source the entry cites for the decode path. No other file in corpus or tools cites S109's lines (`checks.md` section 8).

## Residual risk and verification gaps

- F1's decoded count of 1024 per slot is an inference from code order and log values. No log line prints cells in use. Settling it needs a verbose run with cell accounting. I did not run one, because the assignment forbids starting a llama-server child.
- The "KV full" reading of ret == 1 relies on `llama.h` (not in the S109 anchor). The row itself only says "free space in the KV cache" (`server-context.cpp:4334`, `:4339`). If the entry keeps that gloss, it should cite the header too.
- I did not check the other S106-S113 rows except as they bear on the used-by convention (F7).
- The tag check used the unauthenticated GitHub API. Its answer agrees with the build line in the L1 log.
- Wave-1 seat reports were read only for their S109 citations. I did not audit them.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-25/a2-falsify/out/ReopenS109/checks.md` (evidence log, commands and exit codes)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-25/a2-falsify/advice/ReopenS109.md` (this report)
- Scratch, outside the lane: `/fast/scratch/hyaku/kama-r25a2w2/ReopenS109/` holds `server-context.cpp`, `llama.h`, `SOURCES.tip.md`, `round-25.tip.md` and `context-capacity.tip.md`.

No lane file was edited. No commit, add, checkout, reset, stash or jj command was run. No llama-server child was started, and no port was opened.

## Tools and servers

- Tools installed or upgraded: none. `curl`, `sha256sum`, `stat`, `wc`, `cmp`, `diff` and `git` were already present.
- Servers: none started, no ports opened, no consumer port probed.
