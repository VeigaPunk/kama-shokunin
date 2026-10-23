# ConfirmM03 — first falsifier confirmation, sid `SCORECARD.md:P:980355388a:0`

## Verdict: `confirmed-false`

The counter's `p:absent` for this statement is correct. I established it without running
`count-c1.py`: I re-derived W by blame, read the line, and applied the class-P rule by hand.

## Hand-applied class-P rule (from count-c1.py `check()`, lines 234-238)

1. `data = blob(W, path)` — `git cat-file -e 1e41928…:MISSION.md` fails with
   `fatal: path 'MISSION.md' does not exist in '1e41928…'` → `data is None` →
   observed value `p:absent`. Rule satisfied; no line-count step needed.
2. Same at base 2aa46e24: also absent. `git log --all -- MISSION.md` is empty —
   the file never existed on any lane ref, so this is not later drift; it was already
   a dangling pointer at writing time.

Statement identity re-derived independently: sha256 of line 192 of base SCORECARD.md
(split on `\n`, index 191) = `980355388a`, matching the sid's line-hash component;
blame names W = `1e41928aba2b81dd65ea75084918a7fadf453720` (round-10 sources-registry
commit, committer time 1792449282 / 2026-10-19 19:34:42 -0300), matching the receipt.

## Intended referent

Fleet-root `/home/vgpnk/Projects/shokunin/MISSION.md` line 29:
`kama: { cwd: kama-shokunin/, axes: "operability + freshness (local model serving/endpoints)" }`.
The SCORECARD line asserts "Axis authority: MISSION.md:29 — operability + freshness";
that is exactly what fleet MISSION.md:29 says, and line 29 already said it at fleet
commit 84bade0 (2026-10-16), the last fleet commit at or before W's time. Evidence at W
inside the lane: LOG.md:518 and LOG.md:277 cite `MISSION.md:29` for operability +
freshness; `.ufo/round-10/audit/stale-anchors.tsv` A16 had already resolved an
identical bare `MISSION.md` pointer to `../MISSION.md` ("fleet-root MISSION.md,
resolved from the lane main checkout"); `corpus/knowledge/cross-lane-scope.md` and
`corpus/lessons/round-1-relaunch-freshness.md` use the same convention.
No artifact under `/home/vgpnk/Projects/shokunin/.ufo/reports/` was needed as referent.

## Not a counter false positive

The extractor's P binding (`RE_P` → path `MISSION.md`, end 29, `in_lane()` true since
the path has no `../`/`/`/`~`/`://` prefix) and the rule (lane blob at W must exist with
≥29 lines) were applied exactly as frozen; the observed value `p:absent` follows of
necessity. The false negative is in the statement text, not the instrument: the author
wrote a lane-relative pointer to a fleet-root file. The same defect class already had a
routed correction pattern — the lane's own convention for this file is `../MISSION.md`,
which the counter's `in_lane()` deliberately treats as out-of-lane.

## Correction row (informational, for the L1)

Observed value to record: `p:absent`.

## Residual risk / gaps

- Fleet MISSION.md working-tree mtime (2026-10-19 21:10 -0300) postdates W; I checked
  line 29 at pre-W fleet commit 84bade0 instead, so the referent's stability at W rests
  on committed fleet history, not the working tree.
- I verified class P only for this sid; sibling P statements are out of scope.

No tools were installed (none needed). All commands read-only; no lane file modified
except this seat's output files.
