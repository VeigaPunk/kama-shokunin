# ReopenS112: falsify check of SOURCES row S112 and its Gate line

Verdict: defect found (minor). The anchor sha256, the release tag, every cited line, the Gate quote and the Gate line all hold. Three defects need correction: one teaches phrase is not in the line it cites; the row's negative claim about HTTP surfaces has no locator covering `/metrics`; and the used-by cell omits SKILL.md, which cites S112. Two wording nits and one note are listed under Check 5.

Checked: SOURCES.md row S112 at line 124 (committed fa3b62ae and working copy are identical; the S112 row hashes the same in both). Gate line: corpus/lessons/round-25.md line 28 (identical in committed and working copies at last check). Entry: corpus/knowledge/context-capacity.md, using committed fa3b62ae bytes as the reference, because the working copy changed several times during this check (see section 3).

## 1. Sources

- Pinned README, fetched fresh 2026-10-22 with `curl -fsSL` from the raw form of https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/README.md. 119,661 bytes, 2,402 newline-terminated lines.
- Pinned code, cross-check only: https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp (6,320 lines; sha256 dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329, equal to the S060 anchor).

## 2. Per-check verdicts

**Check 1. Anchor sha256: holds.** `echo "714c067bdbc49bde2735810fbff83eb2933b12c57d50f0012b61fcecb75a6a37  readme-704366d.md" | sha256sum -c -` printed `OK`, exit 0 (out/ReopenS112/readme-sha256-check.txt).

**Check 2. "release b11755": holds.** `git ls-remote --tags https://github.com/ggml-org/llama.cpp 'refs/tags/b11755' 'refs/tags/b11755^{}'` printed `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad	refs/tags/b11755`, exit 0 (out/ReopenS112/ls-remote-b11755.txt).

**Check 3. Every cited line (locator cell): holds, all 13 cited ranges.**

| Cited | What the README says at that line | Result |
|---|---|---|
| Common params, line 50 | `-c, --ctx-size N`, section header at line 30 | holds |
| Server-specific params, lines 165, 169, 177 | 165 `--kv-unified-per-slot N`; 169 `-kvu, --kv-unified`; 177 `-np, --parallel N`; header at 159 | holds |
| GET /props, lines 839-934 | header at 839; next header (POST /props) at 935 | exact |
| /props bullet 927 | `default_generation_settings` | holds |
| /props bullet 928 | `total_slots` | holds |
| GET /slots, lines 983-1126 | header at 983; line 1126 is the closing `]` of the example; section continues to 1130 | holds (range stops 4 lines early; harmless) |
| /slots n_ctx examples 999 and 1064 | `"n_ctx": 65536` in each; both inside the one "Example with 2 slots" block (992-1127) | holds |
| GET /v1/models, line 1304 | `"n_ctx_train": 131072` inside `"meta": {` at line 1301; header at 1254 | holds |
| POST /completion, bullet 671 | `generation_settings` ... "including `n_ctx`"; section header at 492 | holds |
| POST /completion, bullet 683 | `truncated` | holds |

Evidence: out/ReopenS112/readme-cited-lines.tsv and out/ReopenS112/quote-checks.txt.

**Check 4. Gate quote and Gate line: holds.** Quote: `when set without -c/--ctx-size, the shared KV pool is sized to n_parallel*N`. It is a byte-exact substring of README line 165 (Python check; that line is pure ASCII). It has 12 words (limit 25). The Gate URL equals the row URL. round-25.md line 28 is byte-identical in committed fa3b62ae and the working copy (`cmp` exit 0; out/ReopenS112/gate-S112-committed.txt and gate-S112-working.txt).

**Check 5. Teaches cell says only what the lines say: defect (minor).** Every quoted phrase is a byte-exact substring of the line it cites (lines 50, 165, 169, 177, 671, 683, 927, 928, 999, 1064, 1301, 1304 checked; the cell drops README backticks, which is fine). One defect (a), one note (b) and two wording nits (c, d):

- (a) "`/v1/models` meta.n_ctx_train is the training context." Line 1304 gives the value with no definition. The README uses the words "training context" once, at line 63, for `--yarn-orig-ctx` ("model training context size"), not for n_ctx_train. The meaning is correct per the pinned code: server-context.cpp 4848 `model_n_ctx_train = llama_model_n_ctx_train(...)` and 5187 `{"n_ctx_train", meta.model_n_ctx_train}`. But the row cites no code for it. The wave-1 seat report (a2-build/advice/SrcServerReadme.md) makes the same gloss at its line-1304 item without citing code. Fix: "the example at line 1304 shows meta.n_ctx_train 131072 with no definition; the training-context meaning comes from S060 (server-context.cpp 4848, 5187)."
- (b) The /v1/models example (lines 1301-1308) lacks `n_ctx` and `ftype`, which the same code emits (server-context.cpp 5186 `{"n_ctx", meta.slot_n_ctx}`; 5191 `{"ftype", meta.model_ftype}`). The row does not say the example is complete, so this is not a false statement. One clause in the fix for (a) would cover it.
- (c) "The only pool-sizing promise in the README." True for the KV pool. Case-insensitive "pool" hits are lines 165, 176, 763, 775, 945, 1539; only line 165 concerns a KV pool, and the rest are pooling types. But line 168 (`-cram, --cache-ram N`) says "set the maximum cache size in MiB", a size promise for the prompt cache. Fix: "the only KV-pool sizing promise."
- (d) "Otherwise n_ctx appears only as fields:" is followed by the option definitions for `-c`, `--kv-unified` and `--parallel` (lines 50, 169, 177), none of which contains n_ctx. Fix: "Other context statements:".

Holds: the n_ctx mentions are exactly lines 671, 683, 850, 999, 1064 and 1304 (Python scan). The README has no statement on how an unset context divides across slots, and none on the served n_ctx for any -c, -np or kv-unified combination.

**Check 6. "never mentions the KV pool size in any HTTP surface": holds on the bytes; evidence gap (low).** I read every KV, pool and cache hit in the HTTP sections (lines 477-2395). They are prompt cache (500, 532, 596, 604, 681), cache reuse "via KV shifting" (541), slot save and restore (1157-1197), reused-token counts (1439, 1454, 1466), model cache folders (1860-2305), and sleep mode "(including the KV cache)" (2337). None states a pool size. Pooling types are at 763, 775, 945 and 1539. §GET /metrics (lines 1131-1155) has no KV or pool metric; its only size-like entry is line 1149, `llamacpp:n_tokens_max` "High watermark of the context size observed." The row's locator cites no part of §GET /metrics, yet the claim covers every HTTP surface. The committed entry (line 136) and committed SKILL.md (line 689) both say "`/metrics` was not read." Fix: add "§GET /metrics lines 1131-1155 (no KV pool metric; line 1149 is a context-size high watermark)" to the locator, or narrow the claim to the cited sections. Optional: cite fit options at lines 89-91 (`-fit`: "whether to adjust unset arguments to fit in device memory"; `-fitc` default 4096). They bear on the unset-context sentence, which stays true without them.

**Check 7. used-by: defect (minor).** used-by lists only corpus/knowledge/context-capacity.md. S112 is also cited by ID in SKILL.md: committed line 689 ("(S112; K1 and X2 report identical values with pools 2048 and 8192)"; working copy line 690 at last look). The convention allows SKILL.md: the S102 used-by cell lists it (grep count 1 on the committed SOURCES.md). Fix: add SKILL.md to S112's used-by.

**Check 8. Gate paragraph's W04 statement (round-25.md lines 36-38): holds.** The lane census `validate` on the lane directory exited 0 (out/ReopenS112/census-validate-lane.tsv). Lines 26-29 are W04 warnings for S108, S109, S110 and S112. Line 29: `kama-shokunin W04 S112 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/README.md across scopes`. The later row of each other shared-URL pair (S043, S056, S060) is also flagged, and S035 (the first of its pair) is not, as the Gate says. The lane run has no E-level line. A run on a scratch copy printed E11 lines and exited 1, because used-by paths resolve from the registry's location. That run is not a lane result.

**Check 9. How the entry uses S112: holds, except for the gap in Check 6.** Committed fa3b62ae bytes of corpus/knowledge/context-capacity.md:

- Line 1 (header) cites S112 as tools/server/README.md. Holds.
- Line 62 "(S108, server.cpp 179-186; S112 is the only README sizing promise)." Holds: line 165 is the only README sentence tying a KV pool to sizing. "even when the cache is split" comes from S108; S112 says nothing about split caches.
- Line 135 "(S112 documents none; S060 lists the fields)." Holds for /props, /slots and /v1/models in the README.
- Line 136 "`/metrics` was not read." Conflicts with the row's whole-README claim (Check 6).
- Lines 43-45 ("`/props` `default_generation_settings.n_ctx`, every `/slots` `n_ctx` and `/v1/models` `meta.n_ctx` all read one function, `n_ctx_slot()`") do not rely on S112. They cite server-context.cpp 1437, 5186, 5236 and S060. Checked against the pinned file: 1437 `slot.n_ctx = n_ctx_slot();`; 4655-4663 `n_ctx_slot()`, which returns `std::min(res, llama_model_n_ctx_train(model_tgt))` at 4662 after the --kv-unified-per-slot branch at 4658; 4829 `impl->n_ctx_slot()` placed into meta; 5186 `{"n_ctx", meta.slot_n_ctx}`; 5236 `{ "n_ctx", meta.slot_n_ctx }`. All hold (out/ReopenS112/server-context-cited-lines.txt). The README example has no `meta.n_ctx`, so citing S060 for it is correct.

**Check 10. Other sources touched.** The pinned server-context.cpp matched the S060 sha256 anchor. The S108 line citations next to S112 (server.cpp 179-186) belong to another row; I did not check them.

## 3. Working-tree state during this check (for the landing owner)

- corpus/SOURCES.md: working equals committed (sha256 45810d49...). No drift. The S112 row line hashes the same in both (d960433e...).
- corpus/lessons/round-25.md: changed during the check (last sha256 c2379807...). Line 28 still equals committed. The diff at 07:07 showed Mistakes-table edits outside S112.
- corpus/knowledge/context-capacity.md: changed three times during the check (last sha256 cea0f422...; committed 0959b234...). The S112 sentences moved: committed lines 62 and 135-136; working lines 68 and 173-176 at last look. Re-check the landed copy before acting on any line number.
- SKILL.md: changed during the check (last sha256 e1de48c7...). The S112 row moved from committed line 689 to working line 690.

## 4. Smallest corrections

1. Teaches cell: replace "is the training context" with the README fact plus the code pointer (Check 5a). Optionally note that the example omits `n_ctx` (Check 5b).
2. Teaches cell: "The only KV-pool sizing promise" and "Other context statements:" (Check 5c, 5d).
3. Locator: add §GET /metrics lines 1131-1155, or narrow the negative claim (Check 6). The entry line and SKILL.md row that say "`/metrics` was not read" then need the landing owner's decision.
4. used-by: add SKILL.md (Check 7).

## 5. Residual risk and verification gaps

- No runtime evidence was sought. No llama-server was started, which this seat was not allowed to do. The row is docs-only, and its claims were checked byte for byte against the README.
- The entry's `/v1/models` `meta.n_ctx` sentence (Check 9) rests on S060 and the pinned code. I checked the cited lines, not all of S060's row.
- The wave-1 seat report (a2-build/advice/SrcServerReadme.md) was read only. Its quotes agree with my checks. Its byte-identity claim against the round-16 snapshot was not re-run.
- The working-tree entry changed under me, so working-copy line numbers may be stale by the time this report is read.

## 6. Files written

Advice (lane):
- .ufo/waves/round-25/a2-falsify/advice/ReopenS112.md (this report)

Artifacts (lane, .ufo/waves/round-25/a2-falsify/out/ReopenS112/):
- readme-sha256-check.txt (Check 1)
- ls-remote-b11755.txt (Check 2)
- readme-cited-lines.tsv (Check 3)
- quote-checks.txt (Checks 4, 5, 6: quote and scan results)
- gate-S112-committed.txt, gate-S112-working.txt (Check 4)
- census-validate-lane.tsv (Check 8; exit 0)
- server-context-sha256.txt, server-context-cited-lines.txt (Check 9)
- entry-committed-S112-uses.txt, skill-committed-S112-lines.txt (Checks 6, 7, 9)
- working-sha256-final.txt (working-copy hashes at last check)

Scratch (/fast/scratch/hyaku/kama-r25a2w2/ReopenS112/): readme-704366d.md (fresh README fetch), server-context-704366d.cpp (pinned code), SOURCES.committed.md, round-25.committed.md, context-capacity.committed.md, SKILL.committed.md (committed copies from `git show`), round-25.diff.txt (committed versus working lesson diff at 07:07), census-validate-committed.tsv (scratch-path census run; its E11 lines are path artifacts, not findings), census-validate-lane-file.tsv (lane census with --file; exit 0).

## 7. Tools, installs and restricted actions

- Installs or upgrades: none. None was needed.
- Tools used: curl (fresh fetch); git show and git ls-remote (read only); sha256sum, cmp, sed (print only), cut and wc; the read-only census script `scripts/sources-census.sh validate` (stdout redirected to scratch or out files); Python in the eval kernel (read-only checks).
- Not done: no llama-server started, no port probed, no jj command, no commit, push, add, checkout, reset or stash, no subagent spawned.
