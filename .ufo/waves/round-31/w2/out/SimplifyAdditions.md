# SimplifyAdditions — scoped findings (wave 2, attempt 2)

Full report with RESULTS block, command receipts and the complete verdict table:
`.ufo/waves/round-31/w2/out/SimplifyAdditions/report.md` (+ receipts in the same dir).
Read-only audit of `07794a4d..382d11b2` (219 added, 7 modified files, +57919/−0). Nothing edited.

## Clean deletes (break no committed predicate or citation)

1. `.ufo/waves/round-31/sources/llama.cpp-704366d/utils.hpp` — contents are the 13 bytes
   `404: Not Found`; a failed fetch committed as a header. Not in `SNAPSHOT.json`, never read.
2. `.ufo/waves/round-31/sources/llama.cpp-704366d/server-http.cpp` and `server-models.cpp`
   (~154 KB) — unpinned, uncited by any round-31 row, byte-identical to the round-16/26/27
   committed copies at the same upstream commit.
3. `.ufo/waves/round-31/c1/c1-remap.json` — byte-identical uncited duplicate of
   `c1/c1-54c6f4fe.json` (the cited receipt).
4. `.ufo/waves/round-31/w1/out/DataA{01..18}/meaning.txt` + `render.txt` (36 files) — verbatim
   copies of the committed SKILL table cells; only the item specs mandate them; `row.json` is
   the real evidence.

## Delete candidates (bounded loss — L1 decision)

- `w1/out/CriticIgnoredClass/raw.json` (1.14 MB) + `server.log` (185 KB): heaviest artifacts of the
  round; re-derivable from the committed `measure.py`; findings.md/summary.json keep the conclusion.
- `w1/out/ExecC2Corrections/corrections.md`: draft superseded by the committed SCORECARD table.
- `w1/out/ExecC2CrossCheck/`, `w1/out/ExecCensus/census-start.txt`: uncited provenance only.
- `w1/items/*.md` (44 dispatch specs) and uncited review/scout output dirs
  (RevChatSource, RevSourceQuotes, ScribeSkillIntro, ScribeSkillLimits, SentinelLive, SrcOpen2-4):
  not evidence for any claim, but they are the wave's audit trail — keep unless wave trees are
  treated as disposable.

## Keep (load-bearing)

- SNAPSHOT-pinned `server-common/server-schema/server-task/server-chat.cpp` — the frozen C1 counter
  sha256-verifies every manifest entry; deleting any one exits 2.
- `controls/CtlTamper/c2-frozen.json` ≡ `CtlDoNothing/c2.json` byte-identical — self-contained arm
  inputs by contract.
- `registry/chat-param-outcomes-r31.json` — 18 unique ids; the two param+sent repeats are distinct
  requests/outcomes, not duplicate assertions.
- Lesson ## Gate table duplicating S180-S191 rows — lane convention (round-30 lesson does the same).

## Accuracy defects found while auditing (fix, not delete)

- `corpus/README.md:469,470,475` and `PROVINCE.md:136` say `19 rows`/`19 measured rows`/
  `13 pinned source rows S180-S192`; the committed table has 18 rows and 12 sources S180-S191.
- `SCORECARD.md:1582` cites `.ufo/waves/round-31/c2/c2-tip.json` — does not exist; the committed
  receipt is `c2-b4f3edc0.json`.
- Untracked `c1/c1-382d11b2.json` + `c2/c2-382d11b2.json` exist in the working copy but are not in
  the diff range — L1 to decide whether dispatch-tip receipts should be committed.
