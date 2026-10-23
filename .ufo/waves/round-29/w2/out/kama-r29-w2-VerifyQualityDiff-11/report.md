# VerifyQualityDiff — corpus/QUALITY.md diff vs base 2aa46e24 (round 29, w2 seat)

Seat: `kama-r29-w2-VerifyQualityDiff-11` (reviewer, leaf — no subagents dispatched).
Repo: `/home/vgpnk/Projects/shokunin/kama-shokunin` (branch master, HEAD `513eba3ba51a142c9936553e3a85918345eb5c4c`).

## Item under verification

> `git diff 2aa46e24 -- corpus/QUALITY.md`: pure appends only (KQ38 and KQ39 sections + integration note); no existing criterion edited or deleted; each new criterion has the 4-column table shape. Report the diff stat and any deviation.

## Verdict: VERIFIED — the diff is a pure append; zero deviations from the described shape.

## Diff stat

```
corpus/QUALITY.md | 14 ++++++++++++++
 1 file changed, 14 insertions(+), 0 deletions(-)
```

`--numstat`: `14	0	corpus/QUALITY.md`. Exactly **one hunk**: `@@ -275,3 +275,17 @@` at end-of-file (base blob `4fdca73275351e89781b23a415d631d4d9ed07e1` has 277 lines; working tree has 291 = 277+14). Index line: `4fdca73..d9459d5`; `git hash-object corpus/QUALITY.md` = `d9459d52e611f9acebf332d593099bc3d9866816` (worktree blob matches diff `w/` side).

## Evidence per claim

### 1. Pure appends only — VERIFIED, stronger than "described": the appended bytes are byte-identical to base + insertion only

- `grep -c '^-[^-]'` over the hunk bodies: **0** removal lines. `grep -c '^+[^+]'`: 9 non-blank added lines; the remaining 5 of the 14 additions are blank `+` separators.
- Attribution: `git diff --stat 2aa46e24 513eba3b -- corpus/QUALITY.md` → **empty** (no committed change to this file since base). `git diff --stat 513eba3b -- corpus/QUALITY.md` → the same `14 +` hunk. `git status --porcelain -- corpus/QUALITY.md` → ` M` (worktree-only, uncommitted attempt-1 edit; index matches HEAD).
- Byte-exactness of the unchanged prefix: `sha256(git show 2aa46e24:corpus/QUALITY.md)` = `827dcb9ff0b9388e59ce1d00eab22d59678210b4ca19b7137accf69dd99492bc` **equals** `sha256(sed -n '1,277p' corpus/QUALITY.md)` — identical hash, so every existing byte through line 277 is untouched.

### 2. No existing criterion edited or deleted — VERIFIED

- ID census, base vs worktree (`grep -o '| KQ[0-9]*' | sort -u -V`): base lists KQ1–KQ37 (37 IDs); worktree lists KQ1–KQ39. The intersection contains every base ID — none removed, none renumbered; the only delta is +KQ38, +KQ39, contiguous numbering.
- Zero deletion lines + prefix-hash equality ⇒ no prior criterion row, header, section heading, or the KQ37 append-only-block note was edited.

### 3. Content = KQ38 + KQ39 sections + integration note — VERIFIED

Appended block (new-file lines 278–291), all within the single hunk:

| Lines | Content |
|---|---|
| 278 | blank |
| 279 | `## Criterion added — round 29: measured depth requires measurement-dependent outcomes` |
| 280–283 | blank; `\| ID \| Admit only when \| Reject or limit when \| Motivating lesson \|`; `\|---\|---\|---\|---\|`; `\| KQ38 \| …` |
| 284 | blank |
| 285 | `## Criterion added — round 29: calibration statements are judged at their writing revision` |
| 286–289 | blank; same 4-col header; separator; `\| KQ39 \| …` |
| 290 | blank |
| 291 | `Drafted by wave-1 scribe ScribeDepthCriterion (.ufo/waves/round-29/w1/out/ScribeDepthCriterion/), integrated by the kama L1, round 29. KQ39's drift-versus-writing distinction is exercised by control CtlBaseTree (.ufo/waves/round-29/controls/CtlBaseTree/): 4 statements that hold at W but not at base were refused as false corrections.` |

Nothing else was added.

### 4. Each new criterion has the 4-column table shape — VERIFIED

Per-line pipe counts on the six table lines (awk):

- L281 header `| ID | Admit only when | Reject or limit when | Motivating lesson |` — 5 pipes → **4 cells**
- L282 `|---|---|---|---|` — 5 pipes → **4 cells**
- L283 `| KQ38 | … |` — 5 pipes → **4 cells** (1550 chars)
- L287 header — 5 pipes → **4 cells**
- L288 separator — 5 pipes → **4 cells**
- L289 `| KQ39 | … |` — 5 pipes → **4 cells** (2019 chars)

The header is byte-identical to the dominant existing convention (used by KQ1–KQ27 and KQ30–KQ37 tables). Both tables are preceded by a blank line after their `##` heading, so they render.

### 5. Cited-path existence spot check (informational — verifies referenced receipts resolve)

All exist under the lane root: `.ufo/waves/round-28/controls-A1/CtlA1Conversion/{REPORT.md,receipt-A0.json}`, `.ufo/waves/round-28/w2/advice/ExecShortcutPostData.md`, `.ufo/waves/round-28/w2/out/ExecShortcutPostData/shortcut-receipt.json`, `.ufo/waves/round-29/w1/out/ScribeDepthCriterion/`, `.ufo/waves/round-29/controls/{SUMMARY.md,CtlBaseTree/}`, `.ufo/waves/round-29/preregistration.json`, `SCORECARD.md` (1504 lines ≥ cited range 1278–1291).

## Deviations found

None against the item's claims. One cosmetic observation, not a defect of this item's predicate: inside the KQ38 reject cell, `w2/out/ExecShortcutPostData/shortcut-receipt.json` is written without the `.ufo/waves/round-28/` prefix used by the sibling citation in the same cell (`.ufo/waves/round-28/w2/advice/ExecShortcutPostData.md`); the file does exist at the implied full path. Sibling-item claim checks (whether the KQ38/KQ39 *wording* is accurate) are outside this item's scope — diff shape only.

## Commands run (all read-only; no lane mutation, no index/commit ops)

- `git diff 2aa46e24 -- corpus/QUALITY.md` (full patch, incl. artifact `artifact://2411`)
- `git diff --stat` / `--numstat` for `2aa46e24`→worktree, `2aa46e24`→`513eba3b`, `513eba3b`→worktree
- `git status --porcelain=v1 -- corpus/QUALITY.md` → ` M`
- `git rev-parse 2aa46e24:corpus/QUALITY.md` → `4fdca73…`; `git hash-object corpus/QUALITY.md` → `d9459d5…`; `git rev-parse HEAD` → `513eba3b…`
- `sha256sum` comparisons over `git show` output and `sed -n '1,277p'` (read-only slice)
- `grep -c '^@@'` = 1 hunk; `grep -c '^-[^-]'` = 0; `grep -c '^+[^+]'` = 9
- `awk` pipe-count on lines 279–291; `grep -o '| KQ[0-9]*' | sort -u -V` ID census
- `test -e` existence loop for 9 cited paths — all OK

## Tooling

None installed; stock `git`/`coreutils`/`gawk` sufficed. No mutations performed; lane index, jj state and worktree untouched (all `git` invocations are read-only).

## Scope note

This seat verifies the *shape and purity* of the QUALITY.md diff only. Whether KQ38/KQ39 criterion text is substantively accurate, whether the cited control receipts actually contain the quoted `met` values, and whether the correction-row policy text matches the frozen counter are sibling items' concerns; nothing here rules on those.
