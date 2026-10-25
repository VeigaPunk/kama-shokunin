# R39-15 — scorecard/log consistency (round 39 attack findings)

Agent: L1Kama39.R39Attack15 (mutation-tester seat; axes calibration/coverage; milestone r39 claim falsification)
Repo: lane scratch working copy `/fast/scratch/hyaku/kama-r39` (base `6a4afdfe48b0b54239d127761d21a5cf21b5b0ea`, round-36 tip); read-only observation only.

## 1. Claim-state summary (working tree tip)

- Committed evidence trace: working-tree round-39 claims **C1 calibration 7 → 7** and **C2 coverage 9 → 9** in `SCORECARD.md` §§Round 39 and `LOG.md` round-39 entry are mutually consistent with the frozen preregistration (`.ufo/waves/round-39/assimilation/preregistration-frozen.json`, byte-identical to `preregistration.json`) and the predicate controls:
  - `c1-noop.out`: `admit=0 reject=0 source_rows=203 met=False exit=1` — matches base control.
  - `c2-noop.out`: `coverage_block=0 file_exists=0 cited_new=0 met=False exit=1` — matches base control.
  - `claim-after.out` / `claim-after-initial.out`: after-state record `admit=1 rejects=1 sourced_rows=1` (C1) and `round39_pointer=1 entry=1 S472=1` (C2); `initial` is the same verdict in prose form, superseded by the numeric form (not a contradiction).
- Evidence bytes execute: the lesson `corpus/lessons/round-39.md` Gate records one admit (`Admit the amendment`) and one package-theme reject (`Reject staged`) plus a second out-of-theme reject; source row S472 exists in `corpus/SOURCES.md` (11-col shape, `mined`, recheck 90d, used-by = admitted amendment) and cites quote “The Unix timestamp (in seconds) when the model was created.” located at Markdown line 17 of `.ufo/waves/round-39/assimilation/openai-list.md`; the amendment file `corpus/knowledge/served-identity-crosswalk-amendment-2026-10-24-r16.md` exists and is sourced by S472; README tip carries the coverage row (line 551) and `## Frontier disposition — round 39` section.
- Census (rerun by me via `sources-census.sh census --file corpus/SOURCES.md`): rows 204, tier A=195/B=6/C=3, status mined=185/queued=8/rejected=11, exit 0 — matches `claim-after.out` and LOG's round-end figures. `census-start.out` records `rows=203` and exit 2 (fleet root unavailable to scratch), consistent with LOG's narrative; `census-end.out` ends `ok …/corpus/SOURCES.md` with 93 W04 warnings, consistent with LOG's `exit 0 … 93 pre-existing W04` statement. During the working-tree append the base row count in `c1-noop.out` reads 203 while the tip census reads 204; the row delta (S472 only) is confirmed by `git diff HEAD -- corpus/SOURCES.md` (+3 lines: row + note + blank).

⇒ The scorecard/log pair is internally consistent and the C1/C2 claims are traceable to working evidence.

## 2. Observable inconsistencies

1. **Committed vs working scorecard/log truncation.** Head `SCORECARD.md` is 2032 lines; working is 77. Head `LOG.md` is 2194 lines; working is 13. The working copies excise the entire cumulative record (rounds 10–38: all prior claim rows, move log, capabilities, errata, and every prior round log). The retained round-39 content alone is coherent, but the files are no longer the append-only ledger their own headers/contract claim (`Single-writer file … per-contributor detail lives in corpus/`; `SCORECARD` contract: scores bound to evidence pointer and round that last changed them).
2. **Superseded-axes erratum dropped.** Head `SCORECARD.md` explicitly records that the top §Axes table (`coverage 1 → 8` last change round 1; `freshness 6 → 7` last change round 3) “predates round 10 and was not updated by the round-10 commit … superseded, not rewritten” by round-10 rows (`coverage 8 → 9`, `freshness 7 → 8`). The working `SCORECARD.md` retains the **stale top table** (coverage 1 → 8, freshness 6 → 7, calibration 1 → 7) while the same file's round-39 claims and held-readings text assert **coverage 9 → 9, freshness 8, calibration 7**. The erratum that explains the gap is among the excised lines, so on the face of the working file the table and claims disagree.
3. Minor surface nit: the SCORECARD C1 “Counting command” column shows `grep -c '^| S472 |'` which would not match the actual S472 registry row (the claim-after evidence files use the correct `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md` → 204). Cosmetic, no impact on the executed counter.

## 3. Bottom line

No falsification found for C1 (calibration 7→7) or C2 (coverage 9→9): claim state, lesson/amendment/SOURCES/README artifacts, and the census numbers all agree in the working tree, and the frozen controls were false at base. The scorecard/log inconsistency finding is structural: the working `SCORECARD.md`/`LOG.md` rewrite to ~13–77 lines drops the historical ledger and the round-10 erratum, leaving the live top axes table (coverage 8, freshness 7) contradicting the round-39 claim scores (coverage 9, freshness 8) on the face of the file.
