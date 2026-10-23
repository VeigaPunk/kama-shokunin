# VerifyRow04 — hand-verification of correction row 4

Seat: `kama-r29-w2-VerifyRow04` · claim: C1 (calibration), the 11 committed correction rows ·
item: row 4, sid `SA29:SCORECARD.md:Q:4f8083e30a:0`. Lane repo:
`/home/vgpnk/Projects/shokunin/kama-shokunin`. The frozen counter was **not** run on the lane
tree; every check below was re-executed by hand from committed objects only.

## Verdict

```json
{
  "sid": "SA29:SCORECARD.md:Q:4f8083e30a:0",
  "verdict": "confirmed-false",
  "hand_derived_observed": "q:no-artifact",
  "row_last_cell": "q:no-artifact",
  "last_cell_matches_observed": true,
  "base_location": "SCORECARD.md:211 @ 2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d",
  "W": "40660352d4a9eb00a5d6195f0f064f5c64618143",
  "row_position": "4th SA29: row under '## Round 29 — self-assessment corrections' at tip 513eba3 (SCORECARD.md:1457)"
}
```

## Evidence

### (1) Base statement located

The correction table at tip `513eba3ba51a142c9936553e3a85918345eb5c4c` (SCORECARD.md:1457)
names base line SCORECARD.md:211. At base
`2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d` that line reads:

```
| **freshness** (LIVE) | **7 → 8** | C1: 50 stale anchors corrected by appended entries
(uncorrected 50 → 0); new-pointer validation `bash .ufo/round-10/audit/validate-new-pointers.sh`
→ `rows=50 resolved=48 terminal=2 unresolved=0` (A17 dead surface, A51 UNDECIDABLE — corrected,
not re-anchored) | round 10 |
```

The quoted span `rows=50 resolved=48 terminal=2 unresolved=0` is the Q token (33 chars,
contains digits and `=`, does not start with a Q_CMD prefix). It is the only qualifying
backticked Q span on the line — `bash .ufo/round-10/audit/validate-new-pointers.sh` starts
with `bash` and is skipped without consuming a kq index — so statement index `:0` matches.

### (2) Writing revision W and sid components

`git blame --line-porcelain -L 211,211 2aa46e2… -- SCORECARD.md` names W =
`40660352d4a9eb00a5d6195f0f064f5c64618143` ("round-10: post-review fixes", committer
2026-10-19T19:47:40-03:00). The sid component `4f8083e30a` is **not** the W prefix — it is
`sha256(line_without_newline)[:10]` (counter `extract()`, line 179). Hand-derived:
`4f8083e30ad92ef4abd4f50f10136bc93a6189393a25991198312a596614763f`, prefix
`4f8083e30a` — matches the sid. The row's own `W` cell (`40660352`) correctly holds the W
prefix. No defect; sid convention is line-hash, not commit.

### (3) Q rule applied by hand at W

Rule (count-c1.py docstring, lines 27–32; check() line 260): the span must occur verbatim in
at least one blob of the tree at W other than SCORECARD.md, SHONEN.md, LOG.md, corpus/** —
else `q:no-artifact`. Hand-run equivalent:

```
git grep -F -e 'rows=50 resolved=48 terminal=2 unresolved=0' \
  40660352d4a9eb00a5d6195f0f064f5c64618143 -- . \
  ':(exclude)SCORECARD.md' ':(exclude)SHONEN.md' ':(exclude)LOG.md' ':(exclude)corpus'
→ no output, rc=1
```

An unrestricted `git grep -F` over the whole tree at W shows the span occurs **only** in
`SCORECARD.md` itself and `corpus/lessons/round-10.md` — both excluded paths. Therefore the
statement is **false at W**, observed value `q:no-artifact`, identical to the counter's
recorded observation in `.ufo/waves/round-29/before/c1-base.json:125` and to the L1's row.

### (4) Correction row last cell

Row at tip SCORECARD.md:1457 (7 cells under header
`| id | line at base | class | statement token | W | cause | observed |`):

```
| SA29:SCORECARD.md:Q:4f8083e30a:0 | SCORECARD.md:211 | Q |
  `rows=50 resolved=48 terminal=2 unresolved=0` | 40660352 |
  quoted audit result; no committed file at W holds this text | q:no-artifact |
```

Last cell `q:no-artifact` equals the hand-derived observed value exactly. Counter sha256
verified: `fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383` (matches the
frozen hash in the assignment and in the table preamble).

## Residual observation (low, does not affect verdict)

The row's cause cell — "no committed file at W holds this text" — is imprecise:
`corpus/lessons/round-10.md` at W *does* hold the text verbatim; the statement fails only
because the Q rule excludes `corpus/**` (and the self-file) from counting as evidence.
`q:no-artifact` is still the correct observed value under the frozen rule; this is a
wording nit in the cause cell, not a wrong correction. Uniqueness/validity of this row is
out of my scope (other rows/duplicates are covered by sibling seats and the L1 receipt).

## Tooling

No installs; stock git + sha256sum only. No lane files mutated; all reads via
`git show|blame|grep|ls-tree` on committed objects. Counter not executed.
