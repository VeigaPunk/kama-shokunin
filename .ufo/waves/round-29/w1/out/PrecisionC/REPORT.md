# PrecisionC — C1 calibration precision falsifier (round 29, wave 1)

Item: run the frozen counter `count-c1.py --list --tip 2aa46e24`; hand-verify every
class-C statement (27) and every holding P/H/N/T/Q statement (31); report wrong
verdicts or wrong classifications. Writes checks.json + REPORT.md (out dir) and
advice/PrecisionC.md.

## Execution

- Command run (item verbatim): `timeout 120 /usr/bin/python3
  /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/count-c1.py --list
  --tip 2aa46e24 --out /fast/scratch/hyaku/kama-r29/w1/PrecisionC/list.json`
  → `statements 69 mismatched_at_base 11 append_only True valid_corrections 0
  false_corrections 0 unresolved 11 met False tip 2aa46e2481d2`; exit 0. Counter
  sha256 fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383 (matches
  the freeze).
- Independent pass (verify.py, scratch): re-derived haul 69 W values via `git blame
  --line-porcelain <base>` 2/2 files; re-ran every class check with its own git calls
  (cat-file blob, merge-base --is-ancestor, rev-parse, show %ct, grep -F with the four
  excludes); re-scanned the 27 C tokens' citation context (cword prefix / Measured-commit
  cell), the upstream guard's 40-char prefix, and the Q artifact locations.

## Findings by severity

### Verdicts correct; one Q classification overreach
- 69/69 verdicts reproduced by an independent pass (code 0, no disagreements), all
  holds and all 11 falses re-confirmed at the counter's W, and the 11 false observed
  strings match (4 × `p:absent` for the path as written at W; 7 × `q:no-artifact`).
- **Wrong classification (low severity):** Q:1d350fb597:0, SCORECARD.md:880, `gguf==0.19.0` is a PyPI version pin/oracle identity, not quoted measurement output. The frozen Q syntax selects it and it occurs in related round-20 notes, so its `holds=true` verdict is mechanically right; assigning it to the semantic Q class is overbroad.
- All 27 C tokens resolve to lane commits, are cited as such (commit/revision/at/base/
  receipt/Measured-commit cell contexts, e.g. "Work commit `0c75c611…`",
  "Measured revision `726f737a…` (pushed)", "frozen source at 37bd4c5",
  "at base 1560e4d8", `Measured commit:` column cells on lines 1260/1261/1322/1369/
  1415), and are strict ancestors of W (c ≠ W and `merge-base --is-ancestor c W`
  true). None is a digest (the real digests on those lines — `bf9068d8…1f32`,
  `6501737c…6588`, `da5041a8…5af1` — are elided or sit in non-measured columns and
  are correctly not extracted); no extracted token carries llama.cpp/upstream/
  ufo-fsd/@ in its 40-char prefix.
- Round/citation spot-checks of commit subjects all corroborate the cited roles:
  1e41928=round-10, 20e392e=round-15, 92063cf=round-24, efe58e96/1560e4d8/
  52632caa/4179301f/d183ec57/7e5ff9b5=their cited rounds (subjects quoted in
  checks.json).
- 6 holding P: all paths exist at W with ≥ end lines and are the meant files
  (SKILL.md, round-18/19/25 lessons, tools/gguf-identity.py). 2 holding H and 2
  holding N: exact digest/newline matches (kama-probe.sh md5 1f81e859…, 1092
  newlines unterminated; test-snapshot.sh md5 860f26ac…; SKILL.md 323 newlines
  unterminated). 3 holding T: statement time ≤ W committer time (18:33Z vs +155s;
  2026-09-29T04:30:44Z ≪ W; 09:42:42Z vs +712s).

### Accidental Q hold (disclosure — medium)
- **Q:f4c42debcc:1 `transitions=0` (SCORECARD.md line 20, W=ea72c3ea) holds only
  by accident.** The statement's own "stable re-run" output is not committed at W
  (the companion full-span `snapshot=20261014T124232Z … transitions=16 exit=2` is
  itself `q:no-artifact`, one of the 11 mismatches). The span occurs only in
  SKILL.md:187 — the round-2 *baseline* snapshot `snapshot=20260929T043044Z prev=-
  rows=11 model_ok=3 drift=8 transitions=0 exit=2`, a different measurement — and in
  tools/test-snapshot.sh:123,128 — a comment and an `assert_contains` literal, not
  run output. Verdict "holds" is mechanically correct under the frozen Q semantics
  (verbatim occurrence in a non-excluded blob), so the counter is *not* wrong; the
  substantive check the statement describes is unbacked by committed output. This sid
  is not among the 11 mismatches, hence no correction row can or will name it.

### Observations (no action required)
- Q:bb5ad45ac4:0 `model_ok=0` and Q:cda32b698f:0 `registry_rows_evaluated=3
  model_ok=0 drift=3 exit=2` hold only via the SKILL.md transcription of the
  round-1 probe line (related committed record; genuine per class semantics, but the
  raw probe receipts are not in the tree at W).
- Q:1d350fb597:0 is the Q-classification overreach noted above; its matched round-20 notes establish occurrence, not output provenance.
- P:8fa37c9bb6 (round-25 lesson `:187,194`) binds end=187 only; the file at W has
  236 lines, so the second cited line (194) also exists — no beyond-eof, granularity
  note only.
- SHONEN.md contributes 0 statements at base; audited faithful (11 lines; no
  `path:L` pointer, no digest/`(N lines`, no backticked span with digit and =/Q-word;
  line 12 checked whole).
- The 4 false P's are bare or en-dashed paths (MISSION.md:29; round-17-
  verifier-spotcheck.md:217–221; .ufo/reports/round-25/kama.md:120-129;
  count-c1.py:384) — p:absent is correct for the path as written; the 7 false Q's
  are full output spans never committed verbatim at W.

## Residual risk / verification gaps
- The audit covers extraction *output* (the 69 statements); undercount direction
  (tokens the extractor might have missed on SCORECARD.md lines yielding no
  statement) was audited only for SHONEN.md (clean) and sampled C/Q lines, not
  exhaustively for all 1441 SCORECARD.md lines — the pilot history records the
  extraction rules as frozen and fixed pre-seat.
- Q holds are existence proofs (git grep in the W tree, excluding the four paths);
  they do not prove the artifact was *written by* the cited run, only that the span
  occurs verbatim in committed evidence at W.
- W itself is trusted as the counter derives it (git blame at base); my independent
  blame re-derivation matched 69/69.
- Checks are read-only git object operations; no working-tree state was touched.

## Deliverables
- out/PrecisionC/checks.json — per-statement verdict agreement + notes, findings,
  counters.
- out/PrecisionC/REPORT.md — this report.
- advice/PrecisionC.md — scoped advice copy.

## Summary (≤8 lines)
- Counter command reproduced: 69 statements, 11 mismatched, unresolved 11 at
  tip=base; sha256 matches the freeze.
- Independent pass re-verified 69/69 verdicts; blame W matched 69/69.
- 27 C: all lane-commit citations (no digest/upstream), all strict ancestors of W;
  spot-checked subjects corroborate.
- 31 holding P/H/N/T/Q all really hold at W with the meant path/span, one
  exception: Q:f4c42debcc:1 `transitions=0` holds only by accident.
  (SKILL.md baseline + test-snapshot.sh comment/assert literal).
- 11 falses re-confirmed (4 P p:absent, 7 Q q:no-artifact) with matching observed.
- SHONEN.md 0 statements at base (audited faithful).
- No wrong verdict; one Q semantic-class overreach; no C misclassification and no counter verdict defect.
- Residual: undercount direction not exhaustively audited on SCORECARD.md; Q holds
  are existence proofs only.
