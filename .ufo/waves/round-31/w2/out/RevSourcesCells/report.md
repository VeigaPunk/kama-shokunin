# RevSourcesCells — SOURCES.md rows S180–S191 cell-by-cell vs SOURCES-CONTRACT-v1

```
RESULTS
$ grep -nE '^\|[[:space:]]*S(18[0-9]|19[01])[[:space:]]*\|' corpus/SOURCES.md        # exit 0
  → 12 rows at lines 192–203 (verbatim copies saved in rows-S180-S191.txt)
$ grep -n '^##' corpus/SOURCES.md                                                  # exit 0
  → ## Registry at line 9; rows 192–203 precede ## Paths at line 205 → inside the
    one Registry table; `## Round-31 rows relocated into the registry` note at 440
    records the append-only positional move of these exact rows.
$ awk -F'|' '/S1(8[0-9]|9[01])/{print NF}' corpus/SOURCES.md                        # exit 0
  → NF=13 on every row → 11 well-formed cells, no stray '|'.
$ awk enum check (kind/tier/status/opened/recheck per row)                         # exit 0
  → all rows: kind=code tier=A status=mined opened=2026-10-23 recheck=on-release
$ awk duplicate-id check over whole table                                          # exit 0
  → prints nothing; S178,S179 precede S180, S191 is last → sequence contiguous.
$ head -1 corpus/lessons/round-31.md                                               # exit 0
  → '# kama — round 31 lesson (2026-10-23)' → round date = 2026-10-23.
$ sed -n '24,45p' corpus/lessons/round-31.md                                        # exit 0
  → ## Gate table rows S180–S191: URL (+#L anchor) and same quote per row; intro
    says snapshot opened/accessed 2026-10-23 (gate-records.txt).
$ sha256sum .ufo/waves/round-31/sources/llama.cpp-704366d/{server-common,server-schema}.cpp  # exit 0
  → b4f4aae7… server-common.cpp, 1f9d7b73… server-schema.cpp — both equal
    SNAPSHOT.json pins (verbatim-receipt.txt).
$ sed -n '<line>p' on every anchored line + exact string compare                   # exit 0
  → S180–S191 each quote matches the snapshot line verbatim modulo leading
    whitespace: 12× VERBATIM (verbatim-receipt.txt).
$ wc -w on each quote                                                              # exit 0
  → 7,15,7,7,9,10,9,5,9,3,1,9 words — all ≤25.
$ ls corpus/knowledge/chat-adapter-outcomes.md registry/chat-param-outcomes-r31.json  # exit 0
  → both exist (4367 B, 7450 B); registry cites each of S180–S188,S190,S191 at
    least once and S189 six times; knowledge file line 3 cites range 'S180-S191'
    → every 'mined' row has ≥1 existing used-by path citing it.
$ sed -n context around L1360,1388–1401,1514–1536, schema L45–49,62–66              # exit 0
  → each scope/teaches claim matches the code the line sits in (S189 loop guard:
    copies keys not already in llama_params, n_predict overwrite exception).
```

FINDING: contract-clean yes — all 12 rows (S180–S191) are well-formed per cell and inside the `## Registry` table; every quote is verbatim (not a reconstruction), ≤25 words, access/opened date equals the round date 2026-10-23, kind/tier/status/recheck enums valid, and every `mined` row's used-by paths exist and cite it. One cosmetic note, not a violation: `teaches` cells carry a bare backticked code line rather than benefit prose (a form the contract permits — rule 1 only *requires* the quote in the lesson `## Gate`, where it is also present); and `raw.githubusercontent.com` URLs carry a `#L<n>` fragment that the raw host ignores — redundant with the `L<n> @ 704366d` anchor cell, still a canonical URL.

LIMITS: I verified quotes against the local snapshot at `.ufo/waves/round-31/sources/llama.cpp-704366d/` (sha256-pinned to commit 704366d76), not against live GitHub; the anchor's abbreviated `704366d` revision is the full pinned commit in SNAPSHOT.json but I did not query the remote for uniqueness of the short sha. Cell-form checks used the frozen census awk pattern (NF=13, enums); I did not run `scripts/sources-census.sh`. Whether `opened` was honestly authored on 2026-10-23 is asserted by the row/lesson, not independently provable from file mtimes. A bare code line in `teaches` is my reading of "one grounded learner benefit" — an L1 reading it as requiring prose would flag all 12 rows on that axis alone.

Receipts: `verbatim-receipt.txt`, `rows-S180-S191.txt`, `gate-records.txt` in this directory.
