# VerifyRow10 — hand verification of correction row 10 (kama round-29 w2)

Seat: kama-r29-w2-VerifyRow10-3 · 2026-10-23 · Lane: /home/vgpnk/Projects/shokunin/kama-shokunin
No counter execution on the lane tree (forbidden by item); every value below hand-derived from git objects and the frozen counter source.

## Verdict

```json
{"sid": "SA29:SCORECARD.md:P:1c6c1f3e4c:0", "verdict": "confirmed-false", "observed_hand_derived": "p:absent", "row_last_cell": "p:absent", "last_cell_matches": true}
```

## Evidence

### (0) Counter integrity
- `sha256sum .ufo/waves/round-29/count-c1.py` → `fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383` — equals the frozen hash named in the assignment.

### (1) Row 10 and its base statement
- Tip/data commit `513eba3ba51a142c9936553e3a85918345eb5c4c`, `SCORECARD.md` line 1463, 10th data row under `## Round 29 — self-assessment corrections` (table has exactly 11 data rows, all sids distinct, no duplicate of this sid):
  `| SA29:SCORECARD.md:P:1c6c1f3e4c:0 | SCORECARD.md:1349 | P | \`.ufo/reports/round-25/kama.md:120-129\` | 7f84cd0e | a fleet-repo report path written as if lane-relative | p:absent |` (header: `id | line at base | class | statement token | W | cause | observed`).
- Base `2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d:SCORECARD.md` line 1349 (exact bytes):
  ``(`.ufo/reports/round-25/kama.md:120-129`: quality unchanged, discernment``
  — inside a `### Round 26 correction — round-25 trend verdicts` block. Regex scan of the line finds exactly one P-class token (k=0 → `:0` suffix): `.ufo/reports/round-25/kama.md:120-129`.

### (2) Writing revision W and sid identity
- `git --no-replace-objects blame --line-porcelain 2aa46e2481d2… -L 1349,1349 -- SCORECARD.md` → `7f84cd0e7662432b7b93e7586f86a40b06e5fdae 1338 1349 1`, summary `round-26: C1 live error signatures … SCORECARD correction …`, committer time 2026-10-23 00:50:35 -0300. `merge-base --is-ancestor 7f84cd0e… 2aa46e24…` → exit 0.
- The row's W cell `7f84cd0e` matches blame exactly.
- Sid-hex identity: per count-c1.py `extract()`, the sid hex is `sha256(line)[:10]`, **not** a commit prefix — the item's "confirm W's prefix matches the sid" does not describe the counter's actual construction. Hand-derived: sha256 of the exact line-1349 bytes = `1c6c1f3e4cf11364da0ee4e0686ff5db346010b785993ab8d4c5fa6b8fa9765b` → `1c6c1f3e4c` ✓. Uniqueness: exactly one line in base SCORECARD.md (line 1349) and none in SHONEN.md carries that lsha, so the bare (no `#n`) sid names this statement unambiguously.

### (3) P rule by hand at W — statement FALSE
Rule (docstring + `check()`): path `.ufo/reports/round-25/kama.md` is lane-relative (`in_lane` ✓: no `../`, `/`, `~`, `://` prefix); predicate = blob `W:path` exists and has ≥ max(L, M) = 129 lines.
- `git cat-file -e 7f84cd0e7662432b7b93e7586f86a40b06e5fdae:.ufo/reports/round-25/kama.md` → exit 128 (absent from W's tree). Same at base `2aa46e24…` and tip `513eba3b…` (exit 128 each); `git log --all -- .ufo/reports/round-25/kama.md` is empty — the path never existed anywhere in lane history.
- Blob absent at W ⇒ `check()` returns `(False, "p:absent")`. Statement false at W.
- Context for the cause cell: the fleet repo does have `/home/vgpnk/Projects/shokunin/.ufo/reports/round-25/kama.md` (177 lines; lines 118–129 carry the "quality: unchanged" / "discernment: unchanged" bullets the sentence paraphrases) — the pointer was written fleet-relative, so it cannot resolve in the lane tree. Consistent with, but not required by, the predicate.

### (4) Last cell equality
- `corrections()` takes the row's last column stripped of backticks: `p:absent`.
- Counter's printed observed for this sid at W is the exact string `p:absent` (`f"{cls.lower()}:absent"` when the blob is `None`).
- `row_last_cell == observed_hand_derived` → exact match; the row is a valid correction (unique sid, sid in mismatch set, observed equal).

## Residual risk / gaps
- I did not execute count-c1.py anywhere (item forbids lane-tree execution), so no end-to-end receipt reproduction from this seat; the appended-only precondition (`tip SCORECARD.md` startswith base bytes) is a whole-file property outside this row slice — not re-derived here.
- Item phrasing discrepancy noted in (2): sid hex is line-content sha256[:10], not W's prefix; both identities that do hold (W cell ↔ blame; sid hex ↔ line hash) were verified exactly.

## Tooling
- No tools installed or updated (git 2.x + system python used; no pacman touched).
