# ReopenS133 — falsify SOURCES row S133 and its round-26 Gate quote

ATTACK S133 (KQ31 supersession of S109) + its round-26 Gate quote: holds

No asserted fact in S133 is false at the pinned commit. The correction matches
the routed round-25 defect, the sha256 and every cited line number check out
against a fresh fetch, and the Gate quote is 3 words on line 1813. Five
low-severity notes (four precision, one attribution) are listed at the end;
none makes a claim wrong.

## Evidence base

- Fresh fetch: `/fast/scratch/hyaku/kama-r26w2/ReopenS133/fresh` (git init +
  `git fetch --depth 1 origin 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad`,
  access 2026-10-23, `git rev-parse FETCH_HEAD` ->
  `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad`, fetch exit 0).
- `git show FETCH_HEAD:tools/server/server-context.cpp > fresh-server-context.cpp`
  -> `sha256sum` = `dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329`,
  6320 lines. `cmp` against
  `.ufo/waves/round-26/sources/llama.cpp-704366d/server-context.cpp` prints
  nothing, so I echoed `IDENTICAL_TO_SNAPSHOT` (exit 0). Snapshot hash computed
  separately in place: same dd1de0f2…
- Row URL: `curl -s -o /dev/null -w "%{http_code}"` on
  `.../blob/704366d76…/tools/server/server-context.cpp#L1813` -> `200`;
  `raw.githubusercontent.com/.../server-context.cpp` -> `raw:200`.
- Lane tip: `git rev-parse HEAD` = `f4066979096e3452ae731c0e09e50155c6d8258a`.
  `git diff --stat 7e5ff9b f406697 -- corpus/SOURCES.md SKILL.md registry/
  corpus/lessons/round-26.md` -> empty (exit 0), so the counter tip 7e5ff9b
  and the landed tip f406697 hold identical bytes for every measured file.
  `git status --porcelain` for those paths -> empty (working tree == HEAD).
- No live server was used by this seat (no port block assigned): `pgrep -af
  llama-server` prints nothing.

## Per-cell verdicts (corpus/SOURCES.md:145, 11 data cells, awk NF=13)

| cell | value | verdict | proof |
|---|---|---|---|
| id | `S133` | holds | `awk -F'\|' 'NR==145{print "NF="NF}'` -> `NF=13`; `git show HEAD:corpus/SOURCES.md \| grep -n "S133"` -> `145:` |
| source | title + blob URL at 704366d76 | holds | file fetched at that commit, 6320 lines, HTTP 200; `b11755` label backed by `SOURCES.md:50` (S038 ties tag b11755 to commit 704366d76) |
| kind | `code` | holds | the target is C++ source (`server-context.cpp`) |
| tier | `A` | holds by convention | same as sibling code rows `SOURCES.md:54` (S042) and `SOURCES.md:121` (S109). NOTE: no tier-definition block exists in SOURCES.md though `corpus/QUALITY.md:24` says "Source tiers are defined in `SOURCES.md`"; pre-existing gap, not introduced by S133 |
| scope | "decode retry, idle-slot clearing and full-cache error path at this commit; not load/fit or HTTP status/body rendering" | holds, see D4 | the three anchored items are exactly the decode path; HTTP rendering is genuinely outside this file (`format_error_response` is defined at `tools/server/server-common.cpp:91`, the error body JSON at `tools/server/server-task.cpp:1504`, and `send_error` at `server-context.cpp:2170-2185` only queues a `server_task_result_error`) |
| anchor | `try_clear_idle_slots lines 1810-1834; decode terminal branch 4298-4330; retry call 4334-4339; raw sha256 dd1de0f2…` | holds, see D1 | `git grep -n try_clear_idle_slots FETCH_HEAD` -> `1810:` (definition) and `4335:` (only call site); `grep -n "" fresh-server-context.cpp \| sed -n '1810,1835p'` -> signature 1810, `return res;` 1834, closing brace 1835; `sed -n '4294,4341p'` -> 4298 `if (n_batch == 1 && ret == 1) {`, 4330 `throw std::runtime_error(err);`, 4334 comment, 4335 `if (!try_clear_idle_slots()) {`, 4336 `n_batch /= 2;`; fresh-fetch sha256 = dd1de0f2… |
| teaches | `supersedes S109 — …` | holds, see D2/D3 | byte prefix check: `cell.startswith('supersedes S109 \u2014')` -> True (em dash U+2014, not ASCII hyphen) |
| status | `mined` | holds | same value as the sibling live code rows, e.g. `SOURCES.md:121` (S109); 116 of 135 rows carry `mined` |
| opened | `2026-10-23` | holds | fetch and reading done today, 2026-10-23 |
| recheck | `on-release` | holds | the dominant value: `awk -F'\|' '/^\| S[0-9]/{print $11}' corpus/SOURCES.md \| sort \| uniq -c` -> 114 `on-release`, 9 `90d`, 6 `every round`, 4 `180d`, 2 `365d` |
| used-by | `corpus/knowledge/context-capacity.md, corpus/lessons/round-26.md` | holds as written, see D5 | `grep -n "S133" corpus/knowledge/context-capacity.md` -> `258:`; `grep -n "S133" corpus/lessons/round-26.md` -> `46:`. Both named files cite S133. The draft's third entry `SKILL.md` was dropped at landing, and accurate for S133 itself, but the file that consumes the superseded claim is `SKILL.md:689` (see D5) |

## Claim-by-claim check of the teaches cell

Source lines are from the fresh fetch (`fresh-server-context.cpp`).

1. "on a ret == 1 decode failure with n_batch > 1, the retry path calls
   try_clear_idle_slots (4334-4337)" — holds. 4294 `if (ret != 0) {`; 4298
   `if (n_batch == 1 && ret == 1) {` sets err; 4315 `if (!err.empty())` throws;
   with n_batch > 1 and ret == 1 err stays empty, so control reaches 4335
   `if (!try_clear_idle_slots()) {`. See D3 for the one unlisted entry case.
2. "The helper can clear at most one slot" — holds: 1825 `slot.prompt_clear();`,
   1827 `res = true;`, 1829 comment `// clear slots one by one`, 1830 `break;`.
   See D2 for the per-call reading.
3. "and only when KV is unified" — holds: 1813 `if (!params_base.kv_unified) {`
   1814 `return res;`. Independently corroborated by an uncited source comment
   at 1577-1578: "without a unified KV cache, clearing a slot frees no reusable
   room, so we only publish a RAM-cache copy of idle slots".
4. "and it finds a non-processing slot with a nonempty prompt (1813-1834)" —
   holds: 1818 `if (slot.is_processing()) { ... continue; }`, 1822
   `if (slot.prompt.n_tokens() > 0) {`.
5. "If it clears one, n_batch is not halved; otherwise n_batch is halved
   (4335-4337)" — holds: 4335-4337 `if (!try_clear_idle_slots()) { n_batch /= 2; }`.
6. "With n_batch == 1 and ret == 1, the terminal branch sets Context size has
   been exceeded and sends the error to processing slots before throwing
   (4298-4330)" — holds: 4301 `err = "Context size has been exceeded.";`,
   4318-4327 loop with 4319 `if (slot.is_processing())`, 4320 `send_error(slot, err)` ,
   4321 `slot.release()`, 4325 `slot.prompt_clear()`, 4330 `throw std::runtime_error(err);`.
7. "this source does not establish HTTP rendering" — holds (see scope cell proof).

## Routed-defect match (round-25 spot-check defect 3)

`corpus/lessons/round-25-verifier-spotcheck.md:213-217` asks: "Do the same for
S109 (the idle-slot purge precondition)". S133 supplies exactly that
precondition (kv_unified, non-processing, nonempty prompt, at most one per
call) as the corrected cell, under the `supersedes S109 —` form that
`corpus/QUALITY.md:164` (KQ31) requires. Old-row immutability also holds:
`git show 7f84cd0^:corpus/SOURCES.md | grep "^| S109 |" | sha256sum` and the
same over the current file both print
`e027c08c7d855253f71c1140cd86c61815275484ebaae4e79055d05663d0ebaf`
(`S109_BYTE_IDENTICAL`), so the landing commit 7f84cd0 did not edit S109.

## Gate quote (corpus/lessons/round-26.md:46)

- Exact committed line: `| S133 | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L1813 | 2026-10-23 | line 1813: `if (!params_base.kv_unified) {` |`
  (read from `git show HEAD:corpus/lessons/round-26.md | sed -n '46p'`).
- Quote text after `line 1813:` is `if (!params_base.kv_unified) {` = 3
  whitespace-separated words (limit 25). Even counting the `line 1813:` prefix
  it is 5 words.
- Located: `grep -nF 'if (!params_base.kv_unified) {' fresh-server-context.cpp`
  -> `1813:        if (!params_base.kv_unified) {`, `occurrences=1`, so the quote
  is unique in the file and sits exactly on the line the URL anchors.
- Access date 2026-10-23 matches this seat's fetch; URL returns HTTP 200.

## Advisory notes (precision only; no claim is false)

- D1 (anchor, trivial). Anchor says "try_clear_idle_slots lines 1810-1834" but
  the definition's closing brace is line 1835; S109 (`SOURCES.md:121`) and
  `corpus/knowledge/context-capacity.md:131` both say 1810-1835. Smallest
  correction: change the anchor range to `1810-1835` (or write "body
  1810-1834") so the two rows do not quote different extents for one function.
- D2 (teaches, ambiguity). "The helper can clear at most one slot" is true per
  invocation, but a failed retry can call it again: `decode` returns false at
  4341, the caller does `continue` at 3350-3351 with n_batch unchanged when a
  slot was cleared, so successive attempts can purge more than one slot in one
  request. Smallest correction: "can clear at most one slot per call".
- D3 (teaches, incompleteness). The retry block is not exclusive to ret == 1:
  with ret == 2 (abort) err stays empty (4313 `// TODO: handle ret == 2 (abort)`)
  and 4334-4337 runs unchanged. Smallest correction: append "the same block
  also runs when a decode returns 2 with no error message (4313-4316, 4334)".
- D4 (scope, breadth). "idle-slot clearing" can be read wider than the anchored
  helper: a second idle-slot purge exists at 2885-2896 (`--cache-idle-slots`,
  gated on `params_base.kv_unified` at 2893, see also the 1569-1580 comment).
  Smallest correction: "decode-retry idle-slot clearing (try_clear_idle_slots);
  not the `--cache-idle-slots` purge at 2885-2896".
- D5 (used-by attribution, not a false claim). `SKILL.md:689` is the file that
  consumes the superseded parent: it says "every processing request fails with
  HTTP 500 `Context size has been exceeded.` (S109; …)". `grep -n -o "S109\|S133"
  SKILL.md` -> `689:S109` and no S133. The landed used-by cell names only
  `context-capacity.md` and `round-26.md`, so the correction row is invisible
  from the one SKILL.md row that cites its parent. The S133 correction does not
  falsify that SKILL row (it already keys on `kv_unified`), so the smallest
  correction is attribution only: if used-by means "consumers of the corrected
  claim", list `SKILL.md` with the "via S109" qualifier; do not rewrite the
  SKILL row itself under KQ31.

## Ancillary checks

- `bash scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama`
  (cwd /home/vgpnk/Projects/shokunin, stdout/stderr redirected into my scratch):
  exit 0, last line `kama	ok	.../corpus/SOURCES.md`. It emits 49 W04 rows,
  including `kama	W04	S133 duplicate url .../tools/server/server-context.cpp
  across scopes` (census.out:47) — the same duplicate-URL warning class its
  parent row S109 already carries (census.out:27; 49 W04 lines in total).
  Warning only; the validator passes.
- Tools installed or updated: none.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/w2-falsify/advice/ReopenS133.md` (this report)
- `/fast/scratch/hyaku/kama-r26w2/ReopenS133/fresh/` (git init + depth-1 fetch of 704366d76; no lane repo touched)
- `/fast/scratch/hyaku/kama-r26w2/ReopenS133/fresh-server-context.cpp` (blob extracted from the fresh fetch)
- `/fast/scratch/hyaku/kama-r26w2/ReopenS133/census.out`, `/fast/scratch/hyaku/kama-r26w2/ReopenS133/census.err`

## Remaining unknowns

- Tier letters A/B/C have no definition block in SOURCES.md; I verified S133's
  letter is consistent with its siblings, not that it is the correct letter
  under a stated rule. Pre-existing for all 135 rows.
- The single Gate line quotes only the kv_unified half of the three-part
  precondition; the loop conditions (1818, 1822) are not in the Gate table.
  That is the one-quote-per-row design, not an S133 error.
- The frozen counter was not run by this seat (out of seat); clause (c)/(d)
  behaviour is left to the counter seats. S133 is not a counted row anyway.
