VERDICT: partial - S071's URL, 17-word quote, census, status and used-by agree; its anchor section (§OUTPUT, should be §BATCH OUTPUT), the Gate's location, and the teaches clause "a git failure [is] separable" do not.
Attacked: corpus/SOURCES.md row S071 (l.83) and corpus/lessons/round-21.md §Gate row (l.47) at a6617149 (identical at b76727f3), against CORPUS.md contract v1. Access date 2026-10-21.

## Sources re-opened (2026-10-21)
- Live https://git-scm.com/docs/git-cat-file (read, text and raw): "git-cat-file last updated in 2.56.0"; top version 2.56.0 (2026-09-28).
- Pinned https://git-scm.com/docs/git-cat-file/2.56.0 (curl exit 0): `_batch_output` l.2590, `_caveats` l.2791; quote l.2707; "SP missing LF" l.2694, l.2746; "SP ambiguous LF" l.2711.
- Upstream git.git v2.56.0 Documentation/git-cat-file.adoc (curl exit 0; sha256 6c32dbda8c2106be08bda471592db50b5afaf185de32f2e513e80d802b4a95b2; 470 lines): OUTPUT l.285; BATCH OUTPUT l.298; missing l.375-379; ambiguous l.389-392; -e l.49-52.
- Installed: `git --version` 2.56.0 (exit 0); `pacman -Q git` 2.56.0-1 (exit 0); man page owned by it (`pacman -Qo`, exit 0). Man l.246 OUTPUT, l.258 BATCH OUTPUT, l.330/340 tokens, l.337-338 quote (roff hyphen "am-/biguous"), l.389 CAVEATS.

## Field verdicts, row S071
| field | row says | verdict | evidence |
|---|---|---|---|
| id | S071 | agree | census: no duplicate id |
| source | git-scm.com/docs/git-cat-file | agree | resolves; latest = 2.56.0; pinned /2.56.0 URL is the stable form |
| kind, tier | docs, A | agree | official manual for that scope |
| scope | --batch-check, unresolvable and ambiguous, 2.56.0; complements S033 | agree | paragraphs sit under "If --batch or --batch-check is given" (adoc l.301); S033's clause is in OUTPUT |
| anchor section | §OUTPUT | DISAGREE | both paragraphs are in BATCH OUTPUT (adoc 298 < 375, 389 < 450); OUTPUT (285-297) covers -t/-s/-e/-p/<type> only |
| anchor tokens | SP missing LF, SP ambiguous LF | agree | adoc l.379, l.392 |
| anchor revision | installed git 2.56.0 manual | partial | matches package git 2.56.0-1; no public revision date or line numbers (S032/S033/S070 style) |
| teaches: missing | `missing` for unresolvable name | agree | adoc l.375-379; observed `zz-nope missing`, exit 0 |
| teaches: ambiguous | `ambiguous` for ambiguous short sha | agree | adoc l.389-392; observed `02b0 ambiguous`, exit 0 |
| teaches: git failure | "a git failure [is] separable" | partial (ungrounded) | page states no batch exit status or stderr; only -e has exit text (adoc l.49-52) |
| status | mined | agree | census mined 60; S071 cited at lesson l.37, 47, 75 |
| opened | 2026-10-21 | agree | URL reopened today; Gate used installed manual, same text |
| recheck | on-release | agree | contract cadence; `overdue` lists it as cadence |
| used-by | corpus/lessons/round-21.md | agree | repo-relative, exists; no knowledge/ entry cites S071 |

## Gate row (round-21.md l.47)
- Quote verbatim at adoc l.389, pinned l.2707, man l.337-338 (after roff hyphen join); 17 words (<=25): agree.
- Location "git 2.56.0 §OUTPUT": DISAGREE; lesson l.38 "Quotes are located" is false for S071. The build seat's own sweep (SrcGitCatFile.md l.15) placed these hits in BATCH OUTPUT.
- Grounding: quote covers only the ambiguous half. A 17-word missing-half quote, "If a name is specified on stdin that cannot be resolved to an object in the repository" (adoc l.375-376), is available.
- "-e documents no missing-object status": agree (adoc l.49-52; man l.41-44).

## Contract v1 and validator
- CORPUS.md l.70-148 vs kaika SOURCES-CONTRACT-v1.md l.3-81: diff exit 1; only three headings differ in depth (## vs ###). Text identical.
- Census (contract commands, lane root, a6617149): rows 74; malformed 0; A70/B1/C3; mined60/queued7/rejected7; no duplicate ids, enum violations, or mined-without-used-by. All exit 0.
- validate exit 0 (mine and measured runs/b76727f3 exit 0). S071 W04 is by design: sources-census.sh l.644-649 warns when a URL recurs under a new scope; E04 only for same URL and scope.
- Rule 2 (append-only): S071 is new this round. Only status, recheck, used-by change in place; an anchor or teaches fix needs a new row "supersedes S071 - ...".

## Observed git 2.56.0 (scratch repo, 3000 blobs, 66 colliding 4-hex prefixes; out/ReopenS071/probe-git-2.56.0-results.json)
- `--batch-check` on ambiguous `02b0`: stdout `02b0 ambiguous`, stderr `error: short object ID 02b0 is ambiguous`, exit 0.
- `--batch-check` on absent `0000...` or `zz-nope`: stdout `... missing`, exit 0. Bad format or bad GIT_DIR: exit 128 with `fatal:`.
- `cat-file -e` on absent 40-hex: exit 1, silent. `-e 02b0`: exit 128.
- So absence and ambiguity are stdout tokens at exit 0; git failure is exit 128; stderr alone cannot separate them. tools/report-landing-audit.py `lookup()` (l.93-117) and `git()` (l.80-90) match this; their exit-code reliance is not grounded in S071.
- Not an S071 field: measured validate prints 8 W04 lines (S031, S043, S056, S060, S064, S065, S067, S071); rounds 11-15 receipts show only S031; the lesson does not mention W04.

## Options for L1 (lane not edited)
1. Lesson l.47: "§OUTPUT" -> "§BATCH OUTPUT (adoc l.389)"; add the missing-half quote.
2. S071 anchor and teaches need a `supersedes S071 -` row (contract rule 2): anchor BATCH OUTPUT, adoc l.375-379 and 389-392, git.git v2.56.0 with sha256; teaches without "git failure", or citing an exit-status source. A new row makes 75 rows and invalidates the census receipt.
3. [INFERENCE] The contract has no pre-measurement exception; lesson M5 applied one to the ledger only.

## Commands (exit)
- curl pinned 0; curl adoc 0; sha256sum 0; wc -l 0; diff contract 1 (headings only).
- git clone 0; checkout a6617149 0; status --porcelain 0 (empty); diff --stat a6617149 b76727f3 0 (empty); merge-base --is-ancestor b76727f3 a6617149 0.
- census contract commands at lane root: 0 each; sources-census.sh validate, census, overdue: 0, 0, 0.
- pacman -Q git 0; pacman -Qo 0; git --version 0; man -P cat | col -bx 0; zcat | grep -c 0; python probe, quote and section cells: no error.
- Installs: none (existing git 2.56.0-1, curl, man-db, util-linux col, python). Cleanup: rm -rf /tmp/kama-r21-ReopenS071 exit 0, absence test 0. No processes started.
