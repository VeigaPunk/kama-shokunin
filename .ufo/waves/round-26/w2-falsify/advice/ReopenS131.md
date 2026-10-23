ATTACK SOURCES S131 (KQ31 supersession of S106) + its round-26 Gate quote: partial

Row content holds on every cell; the round-26 Gate sentence that underwrites its
provenance (corpus/lessons/round-26.md:13-16) is false for this row: common/fit.cpp
has no lane snapshot copy, so the row's sha256 cannot be checked against
`.ufo/waves/round-26/sources/llama.cpp-704366d/` as the Gate claims. The hash itself
is correct (verified by fresh fetch).

Lane HEAD measured: f4066979096e3452ae731c0e09e50155c6d8258a (`git rev-parse HEAD`,
exit 0). Base for old-row checks: 1560e4d8.

## 1. Fresh fetch and sha256

```
$ curl -sS -L -w 'http=%{http_code} bytes=%{size_download}\n' --max-time 60 \
    -o fit.cpp.fresh \
    https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/fit.cpp
http=200 bytes=52124
exit=0
$ sha256sum fit.cpp.fresh
1f83da2a5dc460b893373365e07341695be80d6c662e53679032a138cce4dd58  fit.cpp.fresh
```
A second fetch to `fit.cpp.recheck` returned `http=200 bytes=52124`, same sha256,
`cmp -s fit.cpp.fresh fit.cpp.recheck` → exit 0.

Verdict on the anchor's `raw sha256 1f83da2a…dd58`: **holds**. The value is the
sha256 of the 52124-byte file served at commit 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad.

## 2. Per-cell verdicts (corpus/SOURCES.md:143)

| cell | content claimed | verdict | proof |
|---|---|---|---|
| source | llama.cpp common/fit.cpp @ 704366d76 + blob URL | holds | URL served HTTP 200 (above); `grep -n 'supersedes S106' corpus/SOURCES.md` → `143:…` |
| kind / tier | code / A | holds | same field values as S106 (line 118); no machine check |
| scope | automatic-context sizing + fit control flow at this commit; not a server run, not another build | holds (consistent with the cited lines; the negative "not an observed run" is not testable here) | n/a |
| anchor | initial measurement 264; resolution + conditional second measurement 270-276; deficit guard 384; floor/interpolation 414-444; user-set 455; sha256 | **holds** | grep -n proof in §3 |
| teaches | starts `supersedes S106 —`; order/reduction/floor correction | **holds** | §3, §4 |
| status / opened / recheck | mined / 2026-10-23 / on-release | holds | line 143 fields 9-11; identical shape to S130 (line 142) |
| used-by | corpus/knowledge/context-capacity.md, corpus/lessons/round-26.md | holds | `context-capacity.md:258` "Rows S131, …"; `round-26.md:19,44,51` |
| old row intact | S106 keeps every cell (KQ31) | holds | append-only guard, §5 |

## 3. Line-number proof (grep -n on the fresh fetched bytes)

```
$ for p in …; do grep -n -F "$p" fit.cpp.fresh; done
dmds_t dmds_full = common_get_device_memory_data_impl                 264
const uint32_t n_streams                                              197
cparams->n_ctx = n_ctx_max;                                           272
if (n_streams > 1) {                                                  273
if (global_surplus < 0) {                                             384
if (n_ctx_auto) {                                                     271,393
if (n_ctx_max > n_ctx_min_total) {                                    394
cparams->n_ctx = n_ctx_min_total;                                     414
if (sum_used_target > sum_projected_used_min_ctx) {                   424
std::max(cparams->n_ctx - cparams->n_ctx % align, n_ctx_min_total);   430
context size set by user to                                           455
```

Read from the file: 264 measurement; 270 comment, 271 `if (n_ctx_auto)`, 272 assignment,
273 `if (n_streams > 1)`, 276 second `common_get_device_memory_data_impl`; 384 guard;
393-394 reduction preconditions; 414 floor; 424/425-430 interpolation + align
(425 is the `// linear interpolation …` comment, 426-427 the expression, 428-430 the
256×n_streams align floored at n_ctx_min_total); 441 `else`, 443-444 floor log;
454 `else`, 455 user-set no-change log.

Every number in the anchor and teaches cells resolves to the line it names.
The three extra references beyond routed defect 3 (393-394, 425-430, 455) are correct.

## 4. KQ31 form and correction match

- `awk -F'|' 'NR==143 {print NF}' corpus/SOURCES.md` → 13 (11 contract columns; the
  append-only parser accepts it, §5).
- Teaches prefix: `awk 'NR==143' corpus/SOURCES.md | grep -o 'supersedes S106 .' | xxd`
  → `73 75 70 65 72 73 65 64 65 73 20 53 31 30 36 20 e2 80 94` = `supersedes S106 —`
  with U+2014 em dash. Holds.
- Correction matches routed defect 3 (`corpus/lessons/round-25-verifier-spotcheck.md:213-217`):
  measurement 264 before resolution 270-276 (213-214), `global_surplus < 0` at 384 (215),
  floor path 414/441-444 (215-216). All three present; S131 adds 393-394, 425-430, 455.
- Gate quote (`corpus/lessons/round-26.md:44`): `line 264: \`dmds_t dmds_full = …log_level);\``
  — 13 whitespace-separated tokens (≤25), and byte-equal to fit.cpp:264 after
  removing the source line's 4-space indent. **Located and within limit.**

## 5. Old-row integrity and table validity

```
$ python3 tools/sources-append-only.py --from 1560e4d8 --to HEAD --repo <lane> --json
{ "violations": [], "added": [ S114 … S135 ], "ok": true }
exit=0
$ git diff --stat 1560e4d8 HEAD -- corpus/SOURCES.md
 corpus/SOURCES.md | 22 ++++++++++++++++++++++
 1 file changed, 22 insertions(+)
```
S131 is a pure addition; S106's seven immutable cells are unchanged, and the guard
parses S131 as a well-formed row. `git show 1560e4d8:corpus/SOURCES.md | grep -c S131`
→ 0 (new this round).

## 6. DEFECT D1 — the Gate's snapshot-equality sentence is false for S131

`corpus/lessons/round-26.md:13-16`:
```
Every row below was opened on 2026-10-23 from a fresh fetch at llama.cpp
commit 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad; the fetched bytes equal the
lane snapshot `.ufo/waves/round-26/sources/llama.cpp-704366d/` (sha256 in each
row's anchor cell; …)
```
Evidence the sentence cannot hold for S131:

```
$ git ls-tree -r --name-only HEAD -- .ufo/waves/round-26/sources | wc -l
13
$ git ls-tree -r --name-only HEAD -- .ufo/waves/round-26/sources | grep -c 'fit.cpp'
0            # grep exit 1, no match
$ find .ufo -name 'fit.cpp'
(no output)
$ ls -l .ufo/waves/round-26/sources/llama.cpp-704366d/
arg.cpp 224650, common.cpp 83694, gguf.cpp 58995, llama-context.cpp 169201,
llama-model-loader.cpp 80776, llama.cpp 22103, server-common.cpp 75061,
server-context.cpp 264205, server-http.cpp 37318, server-models.cpp 117111,
server-queue.cpp 22141, server-task.cpp 67241, server.cpp 24572
```
No snapshot file is 52124 bytes and none has the anchor's sha256, so this is not a
rename (`sha256sum .ufo/waves/round-26/sources/llama.cpp-704366d/*` printed none
equal to `1f83da2a…`).

The L1 had the counter-evidence in hand: the seat named in that same sentence,
`ScribeSupersedes`, wrote in `.ufo/waves/round-26/w1-build/advice/ScribeSupersedes.md`:
"The final checks printed `fit.cpp snapshot missing`, `llama-kv-cache.cpp snapshot
missing`, `README.md snapshot missing` … This report does not claim those comparisons
passed." The landed Gate converts that recorded limit into an affirmative claim.

Impact: bounded. Claim C1 is unaffected — SKILL.md cites no S131 (`grep -c S131 SKILL.md`
→ 0 / exit 1), and every file cited by S114-S130 is present in the 13-file snapshot.
The damaged claim is auditability: a reader cannot re-derive S131's pinned sha256 from
the lane tree; the hash rests on network fetches and the round-25 receipt
`.ufo/waves/round-25/a2-build/out/CriticLearningBar/sources.sha256:1` (`common_fit.cpp
1f83da2a…`), not on lane bytes.

Smallest correction (advice; I did not edit production files): in
`corpus/lessons/round-26.md:13-16`, scope the equality to the files the snapshot
holds and name the exceptions, e.g. "…; the fetched bytes equal the lane snapshot for
every source file the snapshot contains. `common/fit.cpp` (S131), `tools/server/README.md`
(S134) and `src/llama-kv-cache.cpp` (S135) have no snapshot copy, so their sha256 values
are bound to the fresh 2026-10-23 fetch receipts in
`.ufo/waves/round-26/w1-build/advice/ScribeSupersedes.md` only." Alternative: land the
three files under `.ufo/waves/round-26/sources/llama.cpp-704366d/` and keep the sentence.

Adjacent, outside my row (for the sibling seats): the same sentence is false for the
snapshot contents of S134 (README.md) and S135 (llama-kv-cache.cpp); both names appear
in the ScribeSupersedes "snapshot missing" line quoted above.

**Addendum, 2026-10-23 01:0x (worktree repair, not yet committed).** While this wave
was running, `.ufo/waves/round-26/sources/llama.cpp-704366d/` gained the three missing
files (13 → 16, mtimes `--time-style=full-iso`: `fit.cpp` 01:01:39.062,
`llama-kv-cache.cpp` 01:01:39.086, `README.md` 01:01:39.108). Their bytes match every
anchor and my fresh fetch:

```
$ sha256sum fit.cpp README.md llama-kv-cache.cpp
1f83da2a5dc460b893373365e07341695be80d6c662e53679032a138cce4dd58  fit.cpp
714c067bdbc49bde2735810fbff83eb2933b12c57d50f0012b61fcecb75a6a37  README.md
d0739eaf00d8457f4109a616e0beb1cf07ea074c9b460d92a7b6d48c4519d294  llama-kv-cache.cpp
$ cmp -s fit.cpp /fast/scratch/hyaku/kama-r26w2/ReopenS131/fit.cpp.fresh
fit_cmp=0
$ git status --porcelain -- .ufo/waves/round-26/sources/
?? .ufo/waves/round-26/sources/llama.cpp-704366d/README.md
?? .ufo/waves/round-26/sources/llama.cpp-704366d/fit.cpp
?? .ufo/waves/round-26/sources/llama.cpp-704366d/llama-kv-cache.cpp
$ git ls-tree -r --name-only HEAD -- .ufo/waves/round-26/sources | wc -l
13
$ git ls-tree -r --name-only HEAD -- .ufo/waves/round-26/sources | grep -c 'fit.cpp'
0            # exit 1
$ git rev-parse HEAD
f4066979096e3452ae731c0e09e50155c6d8258a
```

Status of D1 therefore: **true at the landed tip f4066979** (the tree the Gate sentence
and the receipt describe; the three files are untracked there) and **repaired in the
working tree**, one commit away. The L1 must commit the three files for the landed
Gate to hold; until then D1 stands as a landed-tip defect, and re-reading the report
after a commit that includes them retires it.

## 7. Commands not run / limits

- No llama-server started; no port used; `pgrep -af llama-server` shows no process of
  mine. No frozen counter run. No tools installed.
- The required "compare sha256 with the lane snapshot" step is impossible for this row
  because the file is absent; recorded above rather than scored as a pass.
- The row's "not an observed server run" scope statement was not exercised (no server
  authorized for this seat).

## 8. Boundary note (disclosed)

The first write of this report resolved a relative path against the session cwd
(`/home/vgpnk/Projects/shokunin`) and created `.ufo/waves/round-26/w2-falsify/advice/
ReopenS131.md` in the fleet root at 01:01:40. It was immediately copied to the lane,
then removed: `rm` of the file plus `rmdir` of the three directories it had created
(`.ufo/waves/round-26/w2-falsify/advice`, `…/w2-falsify`, `…/round-26`), all exit 0;
`ls /home/vgpnk/Projects/shokunin/.ufo/waves/ | grep -c round-26` now returns 0
(exit 1, no match). No fleet file other than that single self-created report was
touched.

## Files written

- `.ufo/waves/round-26/w2-falsify/advice/ReopenS131.md` (this report)
- `/fast/scratch/hyaku/kama-r26w2/ReopenS131/fit.cpp.fresh`
- `/fast/scratch/hyaku/kama-r26w2/ReopenS131/fit.cpp.recheck`
