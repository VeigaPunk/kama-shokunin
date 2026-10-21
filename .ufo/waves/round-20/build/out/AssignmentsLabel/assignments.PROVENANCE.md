# Provenance — `.ufo/waves/round-18/residual/assignments.json`

**Status: retrospective record, written in round 19. It is not the original dispatch.**
It is not spawn, dispatch, or taskCall evidence, and it does not show how the seats were launched.

## Subject

- File: `.ufo/waves/round-18/residual/assignments.json` (48 lines, schema `kama-residual-assignments/v1`).
- sha256: `8d3a9aee251e700319f93210de7bdd945730fdb3d83fc17e5f109451ef389226`. Identical at `7229fa9`, at lane tip `37bd4c5`, and in the working tree.
- First committed at `7229fa9` ("round-19: citation provenance, install-tree pin, r18 defect corrections"; parent `8bf99ca`; author date 2026-10-21 02:55:06 -0300; committer date 03:34:47 -0300). The same commit adds `corpus/lessons/round-19.md`.
- Absent at `888cd38` (01:58:02, round-18 residual advice committed) and at `1b85a24` (02:05:22). `residual/` there contains only `advice/`.
- `ab95aef` and `e7ba3ce` share the change-id of `7229fa9`, have the same tree `2fd9fbe`, and are not reachable from any branch. They are not on the lane's master history.
- The working-tree mtime (03:12:31) is later than the commit. Content is unchanged, so the mtime is not evidence of provenance.

## What the file records

Seats (name, role, verdict), 7 in total:

| seat | role (file) | verdict (file) | advice line 1 `VERDICT:` |
|---|---|---|---|
| ResidPrivacy | reviewer | confirm | confirm |
| ResidHealth | reviewer | confirm | confirm |
| ResidImplPin | reviewer | confirm | confirm |
| ResidCounterC1 | reviewer | partial | partial |
| ResidCounterC2 | reviewer | confirm | confirm |
| ResidClaims | critic | partial | partial |
| ResidCorpus | reviewer | partial | partial |

Totals in the file: 6 reviewer, 1 critic, 4 confirm, 3 partial. These agree with the seat list and with the seven committed advice files at `.ufo/waves/round-18/residual/advice/`.

## What it does not establish

- **Single task call.** The `call` field ("one ordinary task call, 7 seats, no GRANT") paraphrases `corpus/lessons/round-18.md:311-319`. That text was committed at `0c75c61`, before this file existed. The field is copied from the lesson, not taken from a dispatch record.
- **Roles.** No advice file, spawn record, or dispatch record names a role. `ResidClaims.md` line 3 describes itself as "lane-advice criticism only" and gives no role label. The "critic" entry is therefore unsourced.
- **Completeness.** The file does not show that no other seat ran in the residual call.

## Correction to earlier labels

`corpus/lessons/round-18.md:389-394` (appended erratum, `7229fa9`) calls this file the "Dispatch record (defect 4)". That label is superseded. Cite the file as a retrospective roster of verdicts, not as dispatch evidence. Fleet report `.ufo/reports/round-18/kama.md:54-55` restates the call narrative and is not dispatch evidence either.

## Lesson

A record written after the fact is a retrospective roster, not dispatch evidence: it must carry a provenance label naming its committing revision and what it cannot prove, and any dispatch claim requires committed spawn evidence.
