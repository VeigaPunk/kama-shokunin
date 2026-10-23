# VerifyQualityDiff — corpus/QUALITY.md vs base 2aa46e24 — VERIFIED (pure append, zero deviations)

Seat: `kama-r29-w2-VerifyQualityDiff-11`. Full evidence: `.ufo/waves/round-29/w2/out/kama-r29-w2-VerifyQualityDiff-11/report.md`.

## Diff stat

```
corpus/QUALITY.md | 14 ++++++++++++++
 1 file changed, 14 insertions(+), 0 deletions(-)
```

One hunk `@@ -275,3 +275,17 @@` at EOF. Base blob `4fdca73` (277 lines) → worktree `d9459d5` (291 lines); 0 removal lines; prefix bytes 1–277 sha256-identical to the base blob (`827dcb9ff0b9388e59ce1d00eab22d59678210b4ca19b7137accf69dd99492bc`). Attribution: `2aa46e24`→`513eba3b` diff for this file is empty — all 14 lines are the uncommitted attempt-1 worktree edit (` M` status, index clean vs HEAD).

## Checks

- **Pure appends only**: YES — single EOF insertion hunk, zero `-` lines, sha256-verified unchanged prefix.
- **No existing criterion edited/deleted**: YES — ID census base KQ1–KQ37 = worktree KQ1–KQ37; only delta is +KQ38, +KQ39 (contiguous numbering, no renumbering).
- **Content scope**: exactly three pieces — `## Criterion added — round 29: measured depth requires measurement-dependent outcomes` (KQ38 table, new L279–283), `## Criterion added — round 29: calibration statements are judged at their writing revision` (KQ39 table, L285–289), and the one-paragraph integration note (L291, crediting `ScribeDepthCriterion` and describing the `CtlBaseTree` exercise).
- **4-column table shape**: all six new table lines have 5 pipes → 4 cells; headers byte-identical to the dominant `| ID | Admit only when | Reject or limit when | Motivating lesson |` convention; each table is blank-line-separated and renders.
- **Cited paths exist** (informational): all 9 spot-checked references resolve, including `.ufo/waves/round-28/w2/out/ExecShortcutPostData/shortcut-receipt.json` (the reject cell writes it as `w2/out/…` without the `.ufo/waves/round-28/` prefix — cosmetic inconsistency, not a defect of the append-shape claim).

## Deviation

None. Substantive accuracy of the KQ38/KQ39 wording and receipt values is outside this item's scope (sibling items).
