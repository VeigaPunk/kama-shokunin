VERDICT: confirm - the draft `## Landed changes` names all 5 round-21 lane commits (full 40-hex); `report-landing-audit.py --rounds 10-20 --report 21=<draft>` exits 0 with round 21 required=5, defects=0, status clean.

# ScribeLanded — round-21 Landed changes draft and landing audit

Scope: draft the `## Landed changes` block from `git log --reverse --format='%H %s' 7a6bc911f9eb7dbea9e3b81f5f2449ecda10096d..master` and audit it with the landing tool. Lane not modified. No subagents. Installed/updated tools: none.

## Commands and exits (all executed)

1. `git -C /home/vgpnk/Projects/shokunin/kama-shokunin log --reverse --format='%H %s' 7a6bc911…..master` — exit 0; 5 commits, oldest first: a29bb84abbb8b4d328f5970a89e448330a3a42ac, 1471344b4c8ba4dcd20405f500741eab9b3c1183, 4e75d9e85ba4bb26e17fb6a5e48922c349e2a19b, b76727f31e522763ce24e43d6ec86d21b507a11f, a6617149722c73d90e142fbdc8154d6967055f7e.
2. `git rev-parse master` — exit 0; `a6617149722c73d90e142fbdc8154d6967055f7e` (matches the attacked tip).
3. `git show --stat` / `--name-only` per commit and `git show <commit>:registry/report-landing-errata.tsv` — exit 0 (file sets used for each bullet).
4. `ls runs/b76727f3/*.exit | wc -l` — exit 0; 28 exit files (matches the 28 declared exits).
5. `grep -n "four finite\|five" corpus/lessons/round-21.md tools/report-landing-audit.py` — exit 0.
6. `grep -rn KQ28 corpus/*.md` — exit 0; KQ28/KQ29 rows exist in `corpus/QUALITY.md:151-152`.
7. `python3 tools/report-landing-audit.py --rounds 10-20 --report 21=.ufo/waves/round-21/falsify/out/ScribeLanded/landed-draft.md` — exit 0. Output in `out/ScribeLanded/audit-draft.txt`.
8. Negative control: draft minus the a6617149 bullet, `--rounds 21 --report 21=…/control-omit-last.md` — exit 1; reports `UNCORRECTED landed-omitted a6617149722c73d90e142fbdc8154d6967055f7e` (output in `control-audit.txt`). The detector fires on an omitted commit.
9. `--rounds 21 --report 21=…/landed-draft.md --json` — exit 0; `required_commits=5`, `report_committed=False`, cutoff = wall-clock "now" (no fleet commit for the round-21 report yet) [observed].

## Audit summary (step 7, pasted verbatim)

```
round=21 required=5 post_report=0 defects=0
summary reports=12 defects=9 corrected=9 uncorrected=0 errata_unmatched=0 errata_invalid=0 status=clean
```
Rounds 10–20: 9 defects, all corrected by the 9 ledger rows (`registry/report-landing-errata.tsv`, 9 data rows on master). Round 21 draft: 0 defects.

## Draft deliverable

File: `.ufo/waves/round-21/falsify/out/ScribeLanded/landed-draft.md` (5 bullets, one per commit, full 40-hex, each with description and `LOG: <LOG pointer pending>` placeholder plus lesson pointer `corpus/lessons/round-21.md`). Bullets cover: C1 audit tool + errata ledger, C2 install-links producer/gate/grid, build-wave integration (SOURCES S066–S074, QUALITY KQ28–29, SKILL.md, knowledge doc, lesson, build evidence), measurement recipe and runner, late build advice, and the official measurement at b76727f3 (28 exits + live v3 receipt).

## Findings for the L1 (scoped to this section)

- F1 (stale lesson text): `corpus/lessons/round-21.md:13` says the audit "detects four finite defect kinds". The tool has five (`KINDS` tuple and docstring include `landed-section-missing`). Fix the lesson wording; the report's C1 description should say five.
- F2 (LOG pointer): `LOG.md` has no round-21 entry (grep of `round 21` / `R21` returned nothing). The five bullets carry the placeholder `<LOG pointer pending>`; the L1 must replace it when the LOG entry is written.
- F3 (append-only ledger edited in place): the errata header says "Append-only corrections", but commit 1471344 rewrote three existing rows' `evidence` text (diff: `first 16 hex` → `first 15 hex` for the 0957ce61 splice; two other rows reworded). Tokens and correction hashes are unchanged, and the audit verdict does not depend on evidence text. Flagged as a contract wording deviation [observed from `git show 1471344 -- registry/report-landing-errata.tsv`].
- F4 (cutoff for draft): because the round-21 fleet report is not yet committed, the tool uses wall-clock now as cutoff; the 5 round-21 commits are authored before it, so all are required. Once the report is committed, its first-add time becomes the cutoff; re-run the audit then.
- F5 (checkable tokens): the draft contains no 7–40-hex token with a digit and a letter other than the five commits; no `landed-unresolved` or `landed-ambiguous` was raised.

## Out-dir files

- `landed-draft.md` (draft section), `audit-draft.txt`, `draft-audit.json`, `control-omit-last.md`, `control-audit.txt`.

## Limits

- The draft is audited, not committed; the fleet report does not exist yet, so `report_committed=False` [observed].
- Commit descriptions were derived from commit subjects, `git show --stat`/`--name-only`, and the lesson; they were not re-measured. The 28-exit count is the file count only, not a re-run.
- No `/tmp` scratch was created.
