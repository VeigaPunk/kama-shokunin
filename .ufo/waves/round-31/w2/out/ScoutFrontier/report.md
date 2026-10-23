```RESULTS
# cmd 1 — path resolution, registry/source counts, git object presence
# cwd: /home/vgpnk/Projects/shokunin/kama-shokunin
# full stdout: .ufo/waves/round-31/w2/out/ScoutFrontier/receipts.txt
python3 - << 'PY'
# newest-lesson mtimes; path existence; SKILL heading; registry ids;
# SOURCES S180-S192; claim strings; git rev-parse/status/ls-files/
# check-ignore/cat-file/grep/log
exit 0
--- tail ---
===== git log -1 chat-adapter-outcomes exit=0 =====
54c6f4fe070c5d4edd994a8894277083be64118c 2026-10-23 18:03:29 -0300 round-31: remap S180-S191 to the twelve measured source lines and drop the duplicate K31-14 row

===== git log -1 registry exit=0 =====
54c6f4fe070c5d4edd994a8894277083be64118c 2026-10-23 18:03:29 -0300 round-31: remap S180-S191 to the twelve measured source lines and drop the duplicate K31-14 row

WROTE .../ScoutFrontier/receipts.txt bytes=11785

# same stdout, earlier tails, all exit 0 unless noted:
# newest lesson: round-31.md (mtime 1792795902), then round-30-verifier-spotcheck.md
# EXISTS corpus/knowledge/chat-adapter-outcomes.md
# MISSING corpus/registry/chat-param-outcomes-r31.json
# EXISTS registry/chat-param-outcomes-r31.json
# MISSING corpus/SKILL.md
# EXISTS SKILL.md ; heading line 1232
# registry: rows=18 unique_ids=18 ids=K31-01..K31-18 dups={}
# SOURCES present=S180..S191 (12) missing=S192
# HEAD: addeb57c5d717785a94105a2e36cc8a76940fb6c
# git status --short on the named tracked files: empty
# git ls-files lists every named artifact, including
#   .ufo/waves/round-25/final/context-capacity-receipt.json
# git check-ignore -v that receipt: exit 1 (not ignored)
# git cat-file -e HEAD:<each named path>: exit 0, in-HEAD
# git grep -F S180-S192 HEAD: PROVINCE.md:136 and corpus/README.md:475 only

# cmd 2 — ancestor of the dispatch tip, README history, SKILL row count
# note: .ufo/waves/round-31/w2/out/ScoutFrontier/receipts-2.txt
python3 - << 'PY'
# git rev-parse; merge-base --is-ancestor 382d11b2 HEAD;
# log -8 README; grep S180-S192 at 382d11b2; grep Round-23; count K31 rows
exit 0
--- tail ---
===== SKILL round-31 K31 rows exit=0 =====
section_lines=1232-1272 count=18
1247:K31-01
...
1264:K31-18

# same stdout, earlier:
# git merge-base --is-ancestor 382d11b2107d335705875da1a4d889b074bd6fa6 HEAD → exit 0
# README last commit: 3b1e84f8212e136351f078b4d5c1cc170aaf12fa
#   message says "13 pinned source rows"
# S180-S192 still at 382d11b2 in corpus/README.md:475 and PROVINCE.md:136
# error-is-not-a-verdict.md:55 "## Round-23 deepening — the auditor's own exit class"
# SKILL.md K31-01..K31-18 at lines 1247-1264 (18 rows)
```

FINDING: coverage map chat-adapter pointer | yes | `corpus/README.md:469` entry `knowledge/chat-adapter-outcomes.md` resolves to `corpus/knowledge/chat-adapter-outcomes.md` (blob in HEAD `addeb57c`, last touched `54c6f4fe`). The same row's `registry/chat-param-outcomes-r31.json` and the next row's `SKILL.md` (`:470`, heading `SKILL.md:1232`) resolve from the lane root, not from `corpus/` (`corpus/registry/...` and `corpus/SKILL.md` are absent). Both lane-root targets are in HEAD. The covers cell still says "19 live rows"; the committed registry and the SKILL table each have 18 ids, K31-01..K31-18.

planned round 32 vs the two lesson defects | yes | `SCORECARD.md:1642-1644` names the same two defects the lesson's Claims section records. C2: a uniqueness precondition on the correction key ↔ `corpus/lessons/round-31.md:18-22` (`(row, class)` collapses three Claim-cell `C1` rows, rounds 11/12/13; reference arm `valid 10 false 3 unresolved 3`). C1: a counted row must name a parameter and value the base request does not already carry, and `ignored` must exclude keys the session layer consumes ↔ `corpus/lessons/round-31.md:11-14` (twelve duplicate `n_predict=1` rows; an `ignored` claim on a field the session consumes; a `slot` value equal to the base). `SCORECARD.md:1637` also offers a round-qualified composite key; Planned keeps only the uniqueness precondition. The lesson's wave line `:91-92` ("five ... for round 32") is not a third defect set left out of Planned: the no-op, F1 and F2 sit inside the C1 clause, and the surviving duplicate-id row plus the dead evidence path are the "open calibration ground" sentence at `SCORECARD.md:1646-1647`.

frontier row advanced without a committed artifact | no | The round-31 sentence `corpus/README.md:474-475` ("Advanced: ... held in the committed corpus") has committed artifacts at HEAD and already at dispatch tip `382d11b2`: `corpus/knowledge/chat-adapter-outcomes.md` (itself says S180-S191), `registry/chat-param-outcomes-r31.json` (18 rows), `SKILL.md:1232` (18 table rows), `PROVINCE.md:129-136`, `corpus/SOURCES.md` S180-S191. The parenthetical "19 measured rows, 13 pinned source rows S180-S192" does not match those blobs: S192 is absent, and `54c6f4fe` (after README's last edit `3b1e84f8`) is the commit that remapped S180-S191 to the twelve measured source lines and dropped the duplicate K31-14 row without updating the frontier sentence. Other rows that use the word advanced also name files present in HEAD: round 23 → `corpus/lessons/round-23.md` and `corpus/knowledge/error-is-not-a-verdict.md:55`; round 25 → `corpus/knowledge/context-capacity.md`, `tools/kama-context-capacity.py`, and `.ufo/waves/round-25/final/context-capacity-receipt.json` (`git ls-files` lists it; `git check-ignore` exit 1).

```
check | yes/no | pointer
coverage map chat-adapter pointer | yes | corpus/README.md:469 → corpus/knowledge/chat-adapter-outcomes.md (HEAD); registry + SKILL.md:1232 resolve from the lane root only
planned round 32 vs lesson's two counter defects | yes | SCORECARD.md:1642-1644 ↔ corpus/lessons/round-31.md:11-22; wave's five at :91-92 are inside 1642-1647
frontier row advanced with no committed artifact | no | corpus/README.md:474-475 artifacts are in HEAD; the "19 rows / S180-S192" parenthetical is not (SOURCES stops at S191, registry has 18)
```

LIMITS: This run does not re-execute `count-c1.py` or `count-c2.py`, and it does not decide whether C1 or C2 is admissible. It does not show that the 18 registry rows or the S180-S191 quotes are true of llama-server b11755; it only shows the files and the ids are in the commit. It does not audit every historical frontier disposition for numeric drift — only the rows that say "Advanced" (rounds 23, 25, 31) were checked for a committed file, and only round 31's counts were compared to the blobs. The lesson's C2 line says `rows 30` at `b4f3edc0` while the SCORECARD C2 cell says `rows 28`; that difference was not re-counted and is not what the Planned paragraph claims. HEAD at measurement was `addeb57c` (descendant of dispatch tip `382d11b2`); the S180-S192 sentence is the same at both. No tracked lane file was edited. No tool was installed. LSP was not used: the question is markdown paths and git blobs, not a symbol definition.
