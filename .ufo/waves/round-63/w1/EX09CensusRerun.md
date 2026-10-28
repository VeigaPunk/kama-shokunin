# EX09CensusRerun — sources census re-run (round 63, kama)

Advisory findings only; no verdict. Tip under test: 03a6a1d850902a66a13dfad33f89cf3a8b759a09 (lane HEAD at start).
Full command+output transcripts: `out/EX09CensusRerun/census-tip.txt` (manual census, tip) and `out/EX09CensusRerun/census-cli.txt` (CLI, tip and live tree).

## Method
The lane working tree is NOT the tip: `git status` shows `corpus/SOURCES.md` modified (+2 uncommitted rows S527, S528; sha256 working 615d8b99… vs tip blob f9ff8176…). So the tip was measured from `git archive 03a6a1d8` extracted to scratch `…/EX09CensusRerun/root/kama-shokunin` (SOURCES.md sha256 f9ff8176e4d45ab8cab3026209fbacac21bd79a1cc5f86efc7d3a34798382e27) with a read-only copy of fleet `shokunin.conf` beside it (the CLI needs the conf to resolve lane `kama`). The literal item command was also run against the live tree and is reported separately as section B.

## A. Tip 03a6a1d8 (archive root)
```
$ scripts/sources-census.sh validate --root <tip-root> kama      -> exit=0   (last line: "kama  ok  …/corpus/SOURCES.md")
    findings: E-codes=0; W04 (same URL across scopes)=103; W01 (tier-C mined with non-— used-by)=1 (S481)
$ scripts/sources-census.sh census --root <tip-root> kama        -> exit=0
kama rows 266 | tier.A 252 tier.B 10 tier.C 4 (tier.invalid 0) | status.mined 240 queued 8 rejected 18 (status.invalid 0) | missing 0
```
Manual census (CORPUS.md "SOURCES.md — where a shokunin learns", run in the tip archive lane root):
```
rows (grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|')      266
malformed rows (NF!=13)                                        0
tier histogram                                                 A=252 B=10 C=4
status histogram                                               mined=240 queued=8 rejected=18
duplicate ids                                                  (nothing printed)
enum violations / tier inflation                               (nothing printed)
mined rows with missing used-by paths                          (nothing printed)
extra: id range S001..S526 sorted; NF==13 rows = 266 (== row count)
```
**Row count at tip: 266 (matches expectation).** CLI and manual census agree on rows 266, tiers 252/10/4, statuses 240/8/18. Duplicate ids 0, enum violations 0, missing used-by 0, malformed 0. Note ids reach S526 while rows are 266 (ids are not contiguous; not a violation of the contract).

## B. Live working tree (literal item command `--root /home/vgpnk/Projects/shokunin kama`) — NOT the tip
```
validate -> exit=1
    kama E11 S527 missing used-by corpus/lessons/round-63.md
    kama E11 S528 missing used-by corpus/lessons/round-63.md
    plus the same W01 (1) and W04 (104; +S528 duplicate url server-common.cpp)
census   -> exit=0   rows 268 | A=254 B=10 C=4 | mined=242 queued=8 rejected=18 | missing 0
manual census on the live tree: rows 268, malformed 0
```
Cause: uncommitted rows S527/S528 (tier A, mined, opened 2026-10-28, used-by `corpus/knowledge/completion-request-plane.md, corpus/lessons/round-63.md`); `corpus/lessons/round-63.md` does not exist yet (`ls` -> No such file). Both rows are round-63 additions by the L1 after the tip; E11 will clear when the lesson file is written. Anyone re-running the literal command against the working tree will get exit 1 and 268 rows, not 266 — the 266 expectation holds only at the committed tip.

## Observations
- W04 count (103 at tip) is a warning class that does not change exit status; W01 S481 (tier-C mined with used-by list) is a long-standing warning.
- Manual census (CORPUS frozen examples) and CLI agree, so the CLI's 0–3 space tolerance did not alter results for this file.
- No tool installs. Scratch `/fast/scratch/hyaku/kama-r63/w/EX09CensusRerun` removed after receipts were copied.

Counter line: rows=266 malformed=0 tiers A=252 B=10 C=4 status mined=240 queued=8 rejected=18 dup_ids=0 enum_viol=0 missing_used_by=0 validate_exit=0 (tip 03a6a1d8); live tree rows=268 validate_exit=1 (E11 S527,S528 -> absent corpus/lessons/round-63.md)
