Verdict: defect found. The S108 row holds on every check; the entry's fit rule is contradicted by cell K7, and its S108-adjacent citations and the Gate quote need smaller corrections.

# ReopenS108: falsify check of SOURCES row S108, its Gate line, and its use in the entry

Scope: SOURCES.md:120 (row S108); corpus/lessons/round-25.md:24 (Gate line) and :35-42 (S108 mentions); corpus/knowledge/context-capacity.md:1, :58-64, :69-74. Pinned source: llama.cpp 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad. No llama-server child started. No subagent dispatched. No jj command. No git write (only `git show` and `git log`, both read-only).

## 1. Anchor sha256 and fresh fetch: holds

- `curl -sSL --fail -o server-704366d.cpp https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server.cpp` exit 0. Fetched 2026-10-22T10:07:29Z. 591 lines.
- `sha256sum` = 2143962217e9d6275f28c42d599139bb702e2f880dccbad01ab9d8b094f5aef4. Equal to the anchor cell in SOURCES.md:120 ("raw SHA-256 2143962217e9...").

## 2. Cited line numbers in the fetched server.cpp: holds

Excerpt with numbers: out/ReopenS108/server-704366d-lines-157-188.txt.
- 159 `if (!is_router_server) {` opens the non-router block, closed at 175. The row range "159-186" starts here.
- "non-router auto branch 169-174": 169 `if (params.n_parallel < 0) {`; 172 `params.n_parallel = 4;`; 173 `params.kv_unified = true;`; 174 `}`.
- "sizing predicate 179-181": 179 `const bool ctx_pool_auto_sized = params.kv_unified_per_slot > 0 &&`; 180 `params.n_ctx == 0 &&`; 181 `(uint32_t) params.fit_params_min_ctx != UINT32_MAX;`.
- "assignment 183-186": 183 `if (ctx_pool_auto_sized) {`; 184 `params.n_ctx = params.n_parallel * params.kv_unified_per_slot;`; 185-186 SRV_INF. The closing brace at 187 is outside the range. Cosmetic.

## 3. Gate line, round-25.md:24: defect (minor), the quote joins two lines

- Quote A, "lines 172-173": "params.n_parallel = 4; params.kv_unified = true;". The two statements are on lines 172 and 173, but the quote is one string joined by a space. `grep -c -F "params.n_parallel = 4; params.kv_unified = true;"` on the fetched file prints 0 (exit 1). No single line contains the quote. The same table's S111 row quotes each line separately (round-25.md:27). Correction: two quotes, one per line.
- Quote B, "line 184": "params.n_ctx = params.n_parallel * params.kv_unified_per_slot;". Verbatim (`grep -n -F` returns line 184, exit 0). Correct.
- Word counts: 6 and 5. Within 25.
- Committed bytes (fa3b62ae) and working copy agree on line 24. `diff` first differs at line 51.

## 4. Teaches cell: holds, one scope gap

- "In non-router mode, negative n_parallel becomes 4 and sets kv_unified true." Lines 159, 169, 172-173. Holds.
- "With kv_unified_per_slot > 0, n_ctx == 0 and the fit minimum-context sentinel not UINT32_MAX, startup assigns n_ctx = n_parallel * kv_unified_per_slot." Lines 179-181 and 184. Holds.
- Scope gap, not a false claim: lines 183-184 sit outside the `!is_router_server` block, so they also run in router mode, where n_parallel is not forced to 4. [INFERENCE, not run] In server-models.cpp (pinned; sha256 9c5a6f2cc7997a3a409482c53119a2462e8c409ddf001cc568a9a8740e708b4a) a grep for n_ctx, n_parallel, kv_unified, argv finds no params.n_ctx use. The n_ctx hits are n_ctx_train (lines 499, 529, 2378) and a JSON key (2250). Nothing visible consumes the router-mode value.

## 5. How the entry uses S108 (context-capacity.md)

(a) Line 1 lists S108 as "auto slots and pool sizing." Holds.

(b) Lines 58-59: "Leaving `-np` unset makes the server use 4 slots and a unified cache (S108, server.cpp 169-174)." The fact holds (K1.server.log:9 and :1082). But "unset means auto" depends on the default n_parallel = -1 at common/arg.cpp:1406 (server example only). That line falls inside S110's registered anchor range 1405-1406 (SOURCES.md:122) and is not cited for this sentence. Defect, minor. Correction: "(S110, arg.cpp 1406 default -1; S108, server.cpp 169-174)".

(c) Lines 59-60: "Giving `-np` keeps the default split cache (S110; common.h 580)."
- common/common.h:580 reads `bool kv_unified = false;` (sha256 8bcc5708c856653b0094ba312030df9c2f43ec2703e8ad78474fd4339d2540a9). The value is correct. But no registered row covers common/common.h: a `grep common\.h` over corpus/SOURCES.md returns no match. S110's anchor is common/arg.cpp only (SOURCES.md:122). Defect, minor to moderate: an unregistered file under a registered label.
- "K1 versus K2 shows the switch" is confounded. K1 args are "-c 0" (receipt line 4). K2 args are "-c 2048 -np 2 --no-kv-unified" (receipt line 99). They differ in -c, in -np, and K2 carries an explicit kv flag. The clean cell is K7, args "-np 2 --kv-unified-per-slot 512" (receipt line 575), no kv flag: K7.server.log:290 and :823 `kv_unified = false`; :1084 `kv_unified = 'false'`.

(d) Lines 61-64: "`--kv-unified-per-slot N` without `-c` sizes the pool to slots times N even when the cache is split." Holds. The predicate at 179-181 has no kv_unified term. The assignment at 184 gives n_ctx = 2 x 512 = 1024 for K7. K7.server.log:9 prints that sizing message (from 185-186); K7 is split (:290).

(e) Lines 71-74, the fit rule: "When `-c` is unset and `--fit` is on (the default), the fit step ... sets the context to the training context times the number of streams." Contradicted by K7.
- K7 has no -c. Fit is on: K7.server.log:17-18 "fitting params to device memory." The cache is split (kv_unified false).
- The rule as worded predicts 2048 x 2 streams = 4096.
- Observed pool 1024 (K7.server.log:284, :817). Fit reports "will leave ... no changes needed" (:549) and "successfully fit params" (:550).
- Cause: S108 sets n_ctx = 1024 at server.cpp:183-184 before the context resolves, so the rule's antecedent "-c is unset" is too broad.
- Defect, moderate: a registered cell contradicts a stated rule. Correction: add "and `--kv-unified-per-slot` is not given (with it, server.cpp 179-184 sets n_ctx first; K7 stays at 1024 and fit reports no changes, K7.server.log:549)."

(f) K-table rows K1, K2, K7 (args, per-slot, pool, slot counts): hold against receipt argv and logs.

## 6. Lesson claims that use S108: hold

- Lines 35-38, "share a URL with older rows ... W04 warnings." `bash scripts/sources-census.sh validate --today 2026-10-22 --root /home/vgpnk/Projects/shokunin kama` exit 0. Prints `kama W04 S108 duplicate url .../tools/server/server.cpp across scopes`. W04 also for S109, S110, S112, and for S043, S056, S060, which are the later rows of their pairs. No E-code. Stdout saved at out/ReopenS108/validate-2026-10-22.tsv. The census script keys E04 on URL plus scope (lines 643-649). S108's scope differs from S037 and S043, so the result is W04, not E04.
- Lines 41-42, "the auto slot decision is in server.cpp 169-174, not server-context.cpp." The fetched server-context.cpp (sha256 dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329, equal to the S109 anchor) has no `n_parallel < 0`, no `kv_unified = true`, no `ctx_pool_auto_sized`, and no "n_parallel is set to auto." Its kv_unified_per_slot uses are at 1357-1372 and 4658-4659, which are per-slot ceiling logic. Holds.
- Lines 35-36, "No status or recheck cell changed." Registry comparison 92063cf vs fa3b62ae: 105 old rows, only S060 used-by changed, no status, recheck, or immutable cell changed. Artifact: out/ReopenS108/registry-cells-92063cf-vs-fa3b62ae.txt. `tools/sources-append-only.py --from 92063cf --to fa3b62ae6475d111eb466d79af616aeebb08bbb9` exit 0, violations [].

## 7. used-by of S108 and S106-S113: convention defect, minor

- S108 used-by is `corpus/knowledge/context-capacity.md` only. The entry does cite S108, so the path is right.
- The lesson that introduced the row (Gate, round-25.md:24) is not in used-by. Earlier new rows list their introducing lesson: round-12.md:47, round-13.md:55, round-15.md:70 (S034), round-19.md:33-34 (S057).
- The census checks only that the used-by path exists (E11), so validate does not catch this.
- Correction: add `corpus/lessons/round-25.md` to the used-by cell of S106-S113 (used-by is a mutable cell under QUALITY.md KQ22), and log old to new in round-25.md. Or state why the lesson is left out.

## Residual notes (no defect in the entry; untested)

- A negative n_parallel overrides an explicit `--no-kv-unified`. arg.cpp:1727-1734 sets kv_unified from the flag. server.cpp:173 sets it true with no check of the flag, and the unset default is -1 (arg.cpp:1406). [INFERENCE from the lines; not run, since this seat starts no server.] The entry makes no claim about this combination. A future claim would need a test.
- Router mode: see section 4.

## Side checks (outside my item, free to record)

- Fetched arg.cpp sha256 bf4c58c189a774f2308acfe88e4ec5cebb0c43f60cf05cef4c5b2b9affd5822d equals the S110 anchor (SOURCES.md:122).
- Fetched server-context.cpp sha256 dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329 equals the S109 anchor (SOURCES.md:121).

## Smallest corrections, in order

1. context-capacity.md:71-74: add the `--kv-unified-per-slot` exception and cite server.cpp 179-184, with K7 as the example.
2. context-capacity.md:58-60: cite arg.cpp 1406 for the -1 default. Replace "K1 versus K2 shows the switch" with the K7 cell. Either drop "common.h 580" or register common/common.h as a new row (append-only, new id).
3. round-25.md:24: split the S108 quote into two single-line quotes, lines 172 and 173, each with its locator.
4. SOURCES.md used-by of S106-S113: add corpus/lessons/round-25.md, logging old to new in round-25.md, or record the reason.
5. Optional: S108 scope note on router mode and the `--no-kv-unified` override, only if a claim relies on them.

No change to the S108 anchor, sha256, line numbers, or teaches cell is needed.

## Gaps and risks

- No llama-server ran. K-cell values were read from the committed receipt and raw logs, not re-run.
- Did not check the S106, S107, or S112 quotes.
- The round-25.md working copy differs from fa3b62ae from line 51 on (a misroot row added, a false-timestamp row changed). Outside my target. The S108 Gate line is identical in both.
- The router-mode and `--no-kv-unified` notes are untested.

## Commands and exit codes

- curl for server.cpp, server-context.cpp, server-models.cpp, common.h, arg.cpp at 704366d: exit 0 each.
- git -C <lane> show fa3b62ae:corpus/SOURCES.md, :corpus/lessons/round-25.md, :corpus/knowledge/context-capacity.md: exit 0 each (read only).
- git -C <lane> show 92063cf:corpus/SOURCES.md: exit 0. git log --oneline -- corpus/SOURCES.md: exit 0.
- scripts/sources-census.sh validate --today 2026-10-22 --root /home/vgpnk/Projects/shokunin kama: exit 0 (W04 only, no E-codes). census: exit 0 (rows 113, A 108, B 2, C 3, mined 94, queued 8, rejected 11).
- python3 tools/sources-append-only.py --from 92063cf --to fa3b62ae6475d111eb466d79af616aeebb08bbb9: exit 0.
- `grep -c -F` on the joined Gate quote: 0 matches, exit 1.

## Tools installed or updated

None. Tools used: curl, sha256sum, sed, nl, git (read only), python3 (the lane's append-only tool and a read-only parse), bash (the census script, which writes only stdout here).

## Files written

- .ufo/waves/round-25/a2-falsify/advice/ReopenS108.md (this report)
- .ufo/waves/round-25/a2-falsify/out/ReopenS108/pinned-fetch-sha256.txt
- .ufo/waves/round-25/a2-falsify/out/ReopenS108/server-704366d-lines-157-188.txt
- .ufo/waves/round-25/a2-falsify/out/ReopenS108/validate-2026-10-22.tsv
- .ufo/waves/round-25/a2-falsify/out/ReopenS108/census-2026-10-22.tsv
- .ufo/waves/round-25/a2-falsify/out/ReopenS108/append-only-92063cf-fa3b62ae.json
- .ufo/waves/round-25/a2-falsify/out/ReopenS108/registry-cells-92063cf-vs-fa3b62ae.txt
- .ufo/waves/round-25/a2-falsify/out/ReopenS108/k-cells-args-and-logs.txt

Scratch outside the lane, /fast/scratch/hyaku/kama-r25a2w2/ReopenS108/: the fetched pinned sources (server.cpp, server-context.cpp, server-models.cpp, common.h, arg.cpp), committed copies of SOURCES.md, round-25.md, and context-capacity.md at fa3b62ae, and a round-24 copy of SOURCES.md.
