# SC01SupersessionScan — SOURCES supersession scan at base ec3b0d583ed4eb05c7ae935dc59f560e86b0a80b

Source: `git show ec3b0d58…:corpus/SOURCES.md` (621 lines, 259 rows, all 11-cell). Table: pairs.tsv (33 rows).

## Commands and output
- `git show $B:corpus/SOURCES.md | awk -F' [|] ' '/^\| S[0-9][0-9][0-9] \|/ && $7 ~ /supersedes S/ {n++} END{print n}'` -> `33` (all 33 start `supersedes S0NN`; a python cell parse found 0 further rows with the phrase in another cell).
- `... $8=="rejected"{n++}` -> `17` rejected rows in the registry.
- `awk -F'\t' 'NR>1{print $3}' pairs.tsv | sort | uniq -c` -> 27 mined, 2 queued, 4 rejected (pairs); 32 distinct targets (S095 is hit by S096 and S105).
- `awk -F'\t' 'NR>1 && $7=="yes"{n++} END{print n+0}' pairs.tsv` -> `0`: no target row names its superseder in any cell.
- `awk -F'\t' 'NR>1 && $3=="rejected"{print $1"->"$2, "contra="$8}' pairs.tsv` -> S096->S095 no, S105->S095 no, S509->S505 no, S518->S513 YES.

## Rejected targets (4 pairs)
| pair | target flip text | flip satisfied by superseder? | target used-by |
|---|---|---|---|
| S518 -> S513 | "a future claim about secure-execution, dynamic string tokens, or loader namespace semantics" | YES: S518's scope is the secure-execution rule and $ORIGIN/$LIB/$PLATFORM tokens; S518 itself says S513's reason "is false for the secure-execution rule" | `—` |
| S509 -> S505 | row scoped to "with no backend dir compiled in, the executable directory (via /proc/self/exe) and the current directory are searched" | NO: S509 is itself REJECTED, corrects anchor/word count only, flip "as S505" | corpus/lessons/round-52.md |
| S096/S105 -> S095 | none in the row (S095 teaches a positive-looking sentence, status cell alone says rejected) | n/a; S096 narrows to the decoder fact, S105 records the rejection of the cross-API inference — consistent, not contradictory | round-23, round-24, error-is-not-a-verdict.md |

The other 29 pairs target mined/queued rows (anchor/version/scope corrections); none carries a pointer to the superseder; S021 and S074 are `queued`, used-by `—`. These are stale-pointer risks (a reader of the target sees no correction) but not rejection contradictions.

## Answer
At base, **1** target is left contradicting its superseder: **S513** (rejected, used-by `—`, flip condition written in its own row, satisfied by S518, no pointer in any S513 cell; S518 is `mined` and says it supersedes S513). Zero of the 33 targets carry a pointer. Calibration note: of the 4 rejected-target pairs, 1 has a fired flip; 32/32 distinct targets have no back-pointer, so detection must be done by scanning superseders (as here), not by reading the target.

## S513 / S518 reopen (https://man7.org/linux/man-pages/man8/ld.so.8.html, fetched live 2026-10-27)
- Live ld.so.8.html sha256 d9b7737e…0f83 equals the round-56 snapshot `.ufo/waves/round-56/sources/ld.so.8.html`; rtld-audit.7.html live sha256 a95aa3fb…3153 equals its snapshot. Footer ld.so(8): man-pages 6.19 2026-08-03 (S513's anchor says 2025-05-17, which is rtld-audit(7)'s date — S513 anchor date is wrong; S518 has the right one).
- ld.so(8) §LD_AUDIT: "LD_AUDIT is ignored in secure-execution mode." (6 words) plus "the dynamic linker understands the tokens $ORIGIN, $LIB, and $PLATFORM" in the LD_AUDIT list.
- rtld-audit(7): contains LD_AUDIT only as "must be defined to contain a colon-separated list of shared libraries"; the only "secure" hits are `LA_SER_SECURE` flag lines; no "secure-execution", no $ORIGIN, no AT_SECURE.
- Reading: S513's reason ("overlaps rtld-audit(7), S512") holds only for "the LD_AUDIT variable loads auditor objects", the claim's stated need; it does NOT hold for the secure-execution rule or token handling, which only ld.so(8) has. S513's own flip clause names exactly those topics, so the flip fired when S518 was written; S513 was never re-marked. The round-59 outside disagreement is supported by the page text. [INFERENCE] whether S513 should be admitted (as the broader row) or stay rejected as a duplicate of S518 is a planner decision; either way the row needs a pointer to S518.
- Fix shape (not applied): S513 status cell → `superseded` or rejected with "flip fired: see S518" in teaches; correct the anchor date to 2026-08-03; add a lane check that every `supersedes SNNN` target of status rejected carries the superseder id.

Scratch (HTML pages, base copy) in /fast/scratch/hyaku/kama-r60/SC01SupersessionScan, removed at end.
