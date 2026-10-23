# SimplifyAdditions — round-31 additions audit (advisory, read-only)

Seat: `KamaR31.SimplifyAdditions` (wave 2, attempt 2). Read-only audit of everything the
round-31 range `07794a4d..382d11b2` added (219 files, +57919/−0). No lane file was edited;
all comparisons ran on read-only git/cmp/python.

```RESULTS
$ git -C /home/vgpnk/Projects/shokunin/kama-shokunin diff --stat 07794a4d..382d11b2107d335705875da1a4d889b074bd6fa6
exit 0 | tail: `226 files changed, 57919 insertions(+)` (219 A + 7 M; full stat in files.txt receipt)

$ git -C /home/vgpnk/Projects/shokunin/kama-shokunin diff --name-status 07794a4d..382d11b2 | awk '{print $1}' | sort | uniq -c
exit 0 | `    219 A` / `      7 M`

$ sha256sum .ufo/waves/round-31/sources/llama.cpp-704366d/*
exit 0 | utils.hpp = d5558cd4…512ed; file contents: `404: Not Found` (13 bytes committed as a C++ header)

$ cat .ufo/waves/round-31/sources/llama.cpp-704366d/utils.hpp
exit 0 | `404: Not Found` — a failed fetch committed verbatim; absent from SNAPSHOT.json; git grep tip-wide: no round-31 reference

$ grep -n 'server-http\|server-models\|utils.hpp' .ufo/waves/round-31/sources/SNAPSHOT.json
exit 1 (no matches) | SNAPSHOT.json pins exactly server-common/server-schema/server-task/server-chat only

$ grep -n 'SNAPSHOT' .ufo/waves/round-31/count-c1.py  (lines 298-341)
exit 0 | counter loads files["..."] from SNAPSHOT.json, sha256-verifies each; iterates the manifest — server-chat.cpp and server-task.cpp are REQUIRED inputs (keep); server-http.cpp/server-models.cpp/utils.hpp are never read

$ cmp .ufo/waves/round-{16,31}/sources/llama.cpp-704366d/server-http.cpp ; cmp .ufo/waves/round-{26,31}/.../server-models.cpp ; cmp .ufo/waves/round-{27,31}/.../server-task.cpp ; cmp .ufo/waves/round-{16,31}/.../server-common.cpp
exit 0 each | byte-identical duplicates of earlier committed snapshots at the same upstream commit 704366d

$ cmp .ufo/waves/round-31/c1/c1-remap.json .ufo/waves/round-31/c1/c1-54c6f4fe.json
exit 0 | byte-identical; `git grep -l c1-remap <tip>` over tracked files: 0 hits (uncited duplicate receipt)

$ cmp .ufo/waves/round-31/controls/CtlTamper/c2-frozen.json .ufo/waves/round-31/controls/CtlDoNothing/c2.json
exit 0 | byte-identical frozen-vs-baseline input copies (each arm self-contained — keep)

$ python3: json.load(registry/chat-param-outcomes-r31.json)
exit 0 | `n rows 18`; ids K31-01..K31-18 unique; param+sent dup pairs: ('logprobs','true') K31-03 slot vs K31-12 reject, ('top_logprobs','3') K31-04 slot vs K31-05 reject — distinct requests+outcomes, not duplicate assertions

$ grep -rn 'c2-tip.json' SCORECARD.md …
exit 0 | SCORECARD.md:1582 cites `.ufo/waves/round-31/c2/c2-tip.json`; `ls .ufo/waves/round-31/c2/` = c2-b4f3edc0.json only → dangling citation

$ grep -rn '19 live rows|19 rows|S180-S192' SKILL.md SCORECARD.md LOG.md PROVINCE.md corpus/
exit 0 | corpus/README.md:469 `19 live rows`; :470 `19 rows`; :475 `19 measured rows, 13 pinned source rows S180-S192`; PROVINCE.md:136 `S180-S192` — actual: 18 rows (K31-01..18), 12 sources S180-S191

$ for s in <seat names>: grep -rl "$s" SKILL.md SCORECARD.md LOG.md PROVINCE.md corpus/ prereg*.json count-*.py
exit 0 | uncited round-31 out dirs: CriticIgnoredClass, DataA02..A18 (17), ExecC2Corrections, ExecC2CrossCheck, ExecCensus, MutC2? (1 hit), RevChatSource, RevSourceQuotes, ScribeSkillIntro, ScribeSkillLimits, SentinelLive, SrcOpen2-4 — seat-name citations live mostly in corpus/lessons/round-31.md

$ diff .ufo/waves/round-31/w1/out/ExecCensus/census-start.txt .ufo/waves/round-31/census-start.out
exit 1 | different snapshots: seat copy = clean `ok` run pre-append; committed .out = E12 run (12 findings) cited by lesson Mistakes row 4 — keep .out

$ git log --oneline -8 382d11b2
exit 0 | tip commit `382d11b` message: "…two late seat artifacts" — DataA06/row.json and CriticIgnoredClass/raw.json were committed as artifacts, not cited by any tracked file

$ wc -c .ufo/waves/round-31/w1/out/CriticIgnoredClass/{raw.json,server.log}
exit 0 | 1,201,398 + 185,359 bytes — raw capture + server log, re-derivable from committed measure.py
```

FINDING: the round is heavy but mostly load-bearing; the deletion set with zero predicate/citation
breakage is small: (1) `sources/llama.cpp-704366d/utils.hpp` — a 13-byte `404: Not Found` fetch
artifact committed as a header, unpinned and unread; (2) `sources/llama.cpp-704366d/server-http.cpp`
and `server-models.cpp` — unpinned, uncited, byte-identical copies of round-16/round-26 snapshots
(~154 KB dead weight); (3) `c1/c1-remap.json` — byte-identical, uncited duplicate of
`c1/c1-54c6f4fe.json`; (4) 36 `DataA*/meaning.txt`+`render.txt` one-line files — verbatim copies of
the committed SKILL meaning/outcome cells, mandated only by the seat item spec, unread by any
counter. Separately (accuracy, not deletion): README/PROVINCE repeat wrong `19 rows`/`S180-S192`
counts (actual 18 rows, S180-S191) and SCORECARD cites a non-existent `c2/c2-tip.json`.

LIMITS: "not cited by a tracked file" ≠ "no value" — uncited `w1/out` directories are the wave's
audit trail (falsify-seat review evidence) and the L1 may treat wave trees as append-only provenance;
verdicts below mark such files `delete?` only where the loss is bounded (re-derivable or draft copies).
The 18-row/12-source counts were re-derived by parsing the committed registry/SOURCES at the tip, not
by re-running the frozen counters; C1/C2 counter runs were not performed (out of item scope — falsify
seats own those). I did not check whether future rounds plan to cite the unpinned snapshot files.

## Deletion table

| path:range | verdict | why |
|---|---|---|
| `.ufo/waves/round-31/sources/llama.cpp-704366d/utils.hpp:1` | **delete** | 13-byte `404: Not Found` fetch failure committed as a C++ header; absent from `SNAPSHOT.json`; counter never reads it; zero references tip-wide. Breaks nothing. |
| `.ufo/waves/round-31/sources/llama.cpp-704366d/server-http.cpp` (940 ln) | **delete** | Not in SNAPSHOT.json, uncited by any round-31 row/counter/SOURCES entry; byte-identical to `.ufo/waves/round-16/sources/llama.cpp-704366d/server-http.cpp` (same upstream commit). The round-16/17/21/26/27 copies already back the older S036 citations. |
| `.ufo/waves/round-31/sources/llama.cpp-704366d/server-models.cpp` (2983 ln) | **delete** | Same: unpinned, uncited, byte-identical to the round-26/27 copies. 117 KB dead weight. |
| `.ufo/waves/round-31/c1/c1-remap.json` (305 ln) | **delete** | Byte-identical to `c1/c1-54c6f4fe.json` (the cited claim receipt); `git grep` finds no tracked reference. Remap provenance is fully covered by LOG/lesson text. |
| `.ufo/waves/round-31/w1/out/DataA{01..18}/meaning.txt` + `render.txt` (36 files, 1 ln each) | **delete** | Verbatim copies of the committed SKILL table cells (spot-verified K31-01/02/03/13/18); required only by the seat item spec (w1/items/DataA*.md); no counter reads them; `row.json` remains as the raw measurement. |
| `.ufo/waves/round-31/w1/out/CriticIgnoredClass/raw.json` (1.14 MB) + `server.log` (185 KB) | **delete?** | Largest wave artifact; findings/summary keep the conclusion; `measure.py` (committed) regenerates them on the pinned fixture. Deleting removes the only stored raw bodies behind findings.md's `[raw.json]` links — advisory evidence, not a committed predicate. |
| `.ufo/waves/round-31/w1/out/ExecC2Corrections/corrections.md` (19 ln) | **delete?** | Superseded draft of the committed `## Round 31 — claim-row evidence corrections` table in SCORECARD.md; its clone-commit receipt (`receipt.txt`, unique) is worth keeping if the dir is trimmed. |
| `.ufo/waves/round-31/w1/out/ExecC2CrossCheck/` (census.py, census.tsv, diff.md) | **delete?** | Uncited cross-check seat; no claim row references it. Keep only if wave audit-trail provenance is valued. |
| `.ufo/waves/round-31/w1/out/ExecCensus/census-start.txt` (87 ln) | **delete?** | Pre-append clean-census snapshot; the committed `census-start.out` (E12 findings) is the cited evidence. counts.txt (4 ln) records a count not committed elsewhere — L1 call. |
| `.ufo/waves/round-31/w1/items/*.md` (44 files, ~51 ln each) | keep (weak delete) | Dispatch specs; not evidence for any claim and names are duplicated in `swarm-registry.json`, but they are the only committed record of per-seat tasking text (provenance for wave audit). |
| `.ufo/waves/round-31/w1/out/{RevChatSource,RevSourceQuotes,ScribeSkillIntro,ScribeSkillLimits,SentinelLive,SrcOpen2,SrcOpen3,SrcOpen4}/` | keep? (weak delete) | Uncited by tracked files; they are falsify/scribe seat outputs = audit trail. Deleting loses review evidence, breaks no predicate. |
| `registry/chat-param-outcomes-r31.json` (369 ln, 18 rows) | keep | No duplicate assertions: the two param+sent repeats (logprobs K31-03/12, top_logprobs K31-04/05) are distinct requests with distinct outcomes. K31-10 (uncounted) is deliberately retained per LOG. |
| `.ufo/waves/round-31/sources/llama.cpp-704366d/{server-common,server-schema,server-task,server-chat}.cpp` | keep | All four are in SNAPSHOT.json; the frozen counter iterates the manifest and sha256-verifies every entry — deleting server-chat/server-task breaks count-c1.py (exit 2). server-common is byte-identical to the round-16 copy but is the file SNAPSHOT pins — keep the pinned one. |
| `.ufo/waves/round-31/controls/CtlTamper/c2-frozen.json` ≡ `controls/CtlDoNothing/c2.json` | keep | Byte-identical (123 ln) but each is a self-contained arm input; per-arm self-containment is the control-call contract. |
| `.ufo/waves/round-31/w1/out/CriticClaimSize/c1-{noop,type-guess,distinct-baseline}.json`, `c2-*.json`, `scratch-fixtures.bundle` | keep | c1-noop.json is THE citation for the not-admitted verdict (SCORECARD, LOG, lesson, README); the rest are the attack's committed fixtures. |
| `.ufo/waves/round-31/census-{start,end}.out` | keep | Cited by lesson Mistakes row 4 (E12 evidence) and the SOURCES relocation note. |
| `corpus/lessons/round-31.md` ## Gate table (S180-S191 rows) | keep | Duplicates SOURCES.md rows verbatim, but this is the lane convention (round-30 lesson Gate table duplicates its two rows identically); also records reject decisions. |
| `corpus/knowledge/chat-adapter-outcomes.md` ## Limits bullets 1-2 | keep (dedupe option) | Restate SKILL "Client-facing rules" 2 and the prereg's known_limits; the knowledge entry is the canonical long-form store so overlap is by design, but the two bullets add nothing a pointer couldn't. |
| `corpus/README.md:469-475` (coverage rows + frontier) | keep — **fix numbers** | Convention coverage-map rows; but `19 live rows`, `19 rows`, `19 measured rows`, `13 pinned source rows S180-S192` are factually wrong (18, 12, S180-S191) — needs correction, not deletion. |
| `PROVINCE.md:136` | keep — **fix** | `S180-S192` should be `S180-S191` (same wrong count duplicated). |
| `SCORECARD.md:1582` | keep — **fix** | C2 row cites `.ufo/waves/round-31/c2/c2-tip.json` which does not exist; actual file is `c2-b4f3edc0.json`. Broken citation. |
| `LOG.md` round-31 entry; SCORECARD Round-31 claims/corrections/Planned | keep | Changelog vs ledger duplication is lane convention; corrections rows are C2's load-bearing evidence. |
| `corpus/QUALITY.md` KQ41; `corpus/SOURCES.md` S180-S191 rows + relocation note | keep | Cited predicates/evidence; relocation note explains the append-only move. |

Notes: untracked working-copy files `c1/c1-382d11b2.json`, `c2/c2-382d11b2.json` exist on disk but are
NOT in the diff range (no tracked counterpart) — outside this audit's delete set; if the L1 wants the
dispatch-tip receipts committed, that is an addition decision. No tooling installed this round
(all checks ran on stock git/cmp/python3/sha256sum).
