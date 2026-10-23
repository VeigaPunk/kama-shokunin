VERDICT: holds — S138 is a compliant append-only supersession of S133: only the permitted cells differ, the corrected anchor `1810-1835` matches the cited snapshot byte-for-byte, the row follows the CORPUS.md contract shape, and `tools/sources-append-only.py` reports no violations.

Seat: KamaR27A3.ReviewRepairD7S138 (repair review, round-26 spot-check routed defect 7). Lane repo /home/vgpnk/Projects/shokunin/kama-shokunin @ tip 324d5d62e61276af312c8eb42f678004aec245d1 (read-only review; no repo writes).

## Defect under review

`corpus/lessons/round-26-verifier-spotcheck.md:239` (routed defect 7): "SOURCES S133 anchor 1810-1834 should be 1810-1835." Spot-check line 192 already recorded: "The anchor cell reads 1810-1834, but the function closes at 1835". `corpus/lessons/round-27.md` §Repairs item 7 claims: "S138 supersedes S133 with `try_clear_idle_slots` lines 1810-1835."

## 1. Cell-by-cell diff, S133 (line 145) vs S138 (line 150) of corpus/SOURCES.md

Method: split each row on `|`, compared cell-by-cell (Python, run in lane root). 13 pipe-split fields each; results:

| cell | field | S133 | S138 | verdict |
|---|---|---|---|---|
| 1 | id | `S133` | `S138` | DIFF — allowed (id) |
| 2 | source | identical: `llama.cpp server KV-cache-full decode handling @ 704366d76 (release b11755) — https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp` | same | SAME |
| 3 | kind | `code` | `code` | SAME |
| 4 | tier | `A` | `A` | SAME |
| 5 | scope | `decode retry, idle-slot clearing and full-cache error path at this commit; not load/fit or HTTP status/body rendering` | same | SAME |
| 6 | anchor | `try_clear_idle_slots lines 1810-1834; decode terminal branch 4298-4330; retry call 4334-4339; raw sha256 dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329` | `try_clear_idle_slots lines 1810-1835; …` (only `1834`→`1835`) | DIFF — allowed (anchor), and it is exactly the defect-7 correction |
| 7 | teaches | `supersedes S109 — on a ret == 1 decode failure with n_batch > 1, the retry path calls try_clear_idle_slots (4334-4337). The helper can clear at most one slot, and only when KV is unified and it finds a non-processing slot with a nonempty prompt (1813-1834). …` | `supersedes S133 — anchor correction only: try_clear_idle_slots opens at line 1810 and its closing brace is line 1835 (S133 said 1810-1834; round-26 spot-check routed defect 7). The rest of S133 stands: …` then verbatim copy of S133's remainder | DIFF — allowed (teaches prefix); opens `supersedes S133 —` per CORPUS.md rule 2 and preserves the still-true teaching text |
| 8 | status | `mined` | `mined` | SAME (allowed to differ; unchanged) |
| 9 | opened | `2026-10-23` | `2026-10-23` | SAME (allowed; the row was opened this round per the Gate table) |
| 10 | recheck | `on-release` | `on-release` | SAME |
| 11 | used-by | `corpus/knowledge/context-capacity.md, corpus/lessons/round-26.md` | `corpus/lessons/round-27.md` | DIFF — allowed (used-by) |
| 0, 12 | row padding | empty | empty | SAME |

No `|` inside any cell; the diff touches only id, anchor, teaches prefix, and used-by — a subset of the permitted set (id, anchor, teaches prefix, status, opened, used-by).

## 2. Anchor check against the opened source

Snapshot (committed in-lane): `.ufo/waves/round-27/sources/llama.cpp-704366d/server-context.cpp`.

```
$ sha256sum .ufo/waves/round-27/sources/llama.cpp-704366d/server-context.cpp
dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329
```

Identical to the anchor cell's `raw sha256 dd1de0f2…2329` and to the round-26 copy of the same file (same digest) — the fetched bytes are the cited bytes.

`sed -n '1805,1840p'` with numbering (absolute lines):

- 1810: `    bool try_clear_idle_slots() {` — opens at 1810 as claimed.
- 1834: `        return res;`
- 1835: `    }` — the function's closing brace. S133's `1810-1834` truncated the body one line early; S138's `1810-1835` is correct.
- Inside the range: guard `if (!params_base.kv_unified)` at 1813; the non-processing-slot skip at 1818-1819 (inside `for` at 1817); nonempty-prompt purge and `break` at 1822-1830 — consistent with the teaches claim "clear at most one slot … non-processing slot with a nonempty prompt (1813-1834)" (body lines, brace excluded — consistent usage).

Carried-forward anchors re-verified in the same snapshot:

- 4298-4330 terminal branch: `if (n_batch == 1 && ret == 1)` at 4298, `err = "Context size has been exceeded."` at 4301, `throw std::runtime_error(err);` at 4330 — matches "decode terminal branch 4298-4330" and the teaches text.
- 4334-4339 retry call: comment at 4334, `if (!try_clear_idle_slots())` at 4335, `n_batch /= 2;` at 4336, `SRV_WRN(...)` at 4339 — matches "retry call 4334-4339" and "(4334-4337)" phrasing in teaches.

## 3. Contract shape — `CORPUS.md` (fleet root) lines 86-118

- Header contract (line 86): `id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by` — S138's 11 cells map exactly, in order.
- Rule 1 (a row is a claim): the round-27 lesson `## Gate` table records S138's URL, access date `2026-10-23T06:53Z`, and quote "`bool try_clear_idle_slots() {` — line 1810; its closing `}` is line 1835" (≤25 words), grounding teaches.
- Rule 2 (append-only): S133's row is untouched in place (still reads `1810-1834`, still `mined`); the correction is a new row whose `teaches` opens `supersedes S133 —`, matching the required `supersedes S0NN —` form. `status`/`recheck`/`used-by` of other rows unchanged per the lesson's Gate note ("No existing row's status, recheck or used-by changed") — [INFERENCE] I verified S133 unchanged; the cross-file claim over all rows is covered by the tool run below.
- `id` uniqueness: S138 is the next unused id (S136/S137 added earlier this round); no reuse.
- `used-by` = `corpus/lessons/round-27.md` is accurate: the lesson's Gate and Repairs sections cite S138.

## 4. Append-only tool output

```
$ python3 tools/sources-append-only.py --from 0ec32cac --to 324d5d62e61276af312c8eb42f678004aec245d1
added S136 (allowed)
added S137 (allowed)
added S138 (allowed)
no append-only violations
EXIT=0
```

The tool independently confirms S138 is an allowed addition and that no existing row was mutated between the pre-round base (`0ec32cac`) and lane tip.

## Residual risk / gaps

- None material for defect 7. The one cell worth a second look is `used-by`: it replaced `context-capacity.md, round-26.md` with `corpus/lessons/round-27.md` rather than appending. CORPUS.md:107-108 defines `used-by` as the paths citing *this row*; S138 is a distinct row, so listing only round-27.md is correct — the S133 citations remain on S133's row. Not a defect.
- The snapshot used is the lane-committed round-27 copy; its digest equals the anchor's recorded raw sha256, so no network re-fetch was needed for verification.

## Install/update log

None — no tools installed or updated for this seat.

Report: .ufo/waves/round-27/w1a3/advice/ReviewRepairD7S138.md
