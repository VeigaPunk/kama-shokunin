# CN01 — sibling-overlap scan (kama round 83, w1)

Scope: read-only scan of `.ufo/reports/round-*/<lane>.md` and each live lane's `corpus/lessons/` for chousa, tabi, souji, tsukuroi, kengaku, tameshi, mori, kaidoku, kasegi, mado — 645 report files, 1,286 lesson files, read 2026-11-04. Surfaces: **S1** register rows bound to their own introduction commit (`git blame`) as an acceptance rule; **S2** graded recheck row keyed to an upstream release relation, byte comparison deciding the verdict (kama holds `corpus/knowledge/pin-recheck-trigger.md`); **S3** self-record counter grading a previous round's declared facts with value-bound corrections.

| surf | lane | rnd | file:line | exact claim (verbatim substring) | verdict |
|---|---|---|---|---|---|
| S1 | souji | 1 | `.ufo/reports/round-1/souji.md:17` | "all 109 b2f2efa files have introducing commits that are ancestors of `origin/master` → 0 NOTPUSHED" | adjacent |
| S1 | mori | 16 | `mori-shokunin/corpus/lessons/round-16-verifier-spotcheck.md:50-51` | "Every receipt's `started_at` precedes the commit that first adds it." | adjacent |
| S1 | tameshi | 57 | `tameshi-shokunin/corpus/lessons/round-57.md:74` | "pipeline-introduction commit is not the deciding-receipts commit" | adjacent |
| S1 | tabi | 23 | `tabi-shokunin/corpus/lessons/round-23.md:153` | "a change and its LOG entry bound to different commits"; fix "`c6-landed-log-binding`: per-row commit → `LOG.md` membership" | adjacent |
| S1 | kaidoku | 67 | `kaidoku-shokunin/corpus/lessons/round-67.md:3-4` | "the operative freeze is the commit that first adds `.ufo/waves/round-67/claims.json`" | adjacent |
| S2 | tabi | 29 | `tabi-shokunin/corpus/lessons/round-29-verifier-spotcheck.md:77` | "both give `population=23 resolved=23 unresolved=0 holds=16 drifted=7`, exit 0" | adjacent |
| S2 | tabi | 29 | `tabi-shokunin/corpus/lessons/round-29-verifier-spotcheck.md:73` | "An exact-substring span recomputation over all 23 rows gives holds=16 and drifted=7" | adjacent |
| S2 | tsukuroi | 56 | `tsukuroi-shokunin/corpus/lessons/round-56-verifier-spotcheck.md:59` | "`RECHECK_SERVICES: PASS (12 rows, 12 match, 0 drift)`" | adjacent |
| S2 | mori | 53 | `.ufo/reports/round-53/mori.md:118-119` | "46 release-pinned rows re-read at v7.3 with pinned copies fetched by two independent channels" | adjacent |
| S2 | mado | 78 | `mado-shokunin/corpus/lessons/round-78.md:86-87` | "the five value-bound rows that a present-day host change would break" | none |
| S3 | tabi | 24 | `tabi-shokunin/corpus/lessons/round-24.md:65` | "`scripts/check-selfassessment.mjs` class `m1-selftest-tally`" | adjacent |
| S3 | tabi | 29 | `tabi-shokunin/corpus/lessons/round-29-verifier-spotcheck.md:57` | "`measure/c2-selfassessment-rev.json.txt` at `ab080992`: `mismatches=0`, `counted=[]`" | adjacent |
| S3 | tabi | 32 | `tabi-shokunin/corpus/lessons/round-32.md:133-134` | "A correction paragraph therefore clears a stale tally when *any* accepted number in it equals the oracle tally" | adjacent |
| S3 | chousa | 34 | `chousa-shokunin/corpus/lessons/round-34-verifier-spotcheck.md:37` | "`SELF_AUDIT_MISMATCHES=1` (the single mismatch `audit-tool-digest` carries an in-set disposition: superseded by `audit-tool-digest-v3`)" | adjacent |
| S3 | kaidoku | 79 | `.ufo/reports/round-79/kaidoku.md:97` | "**`mismatches 2`** naming `omp-pin` (record `:8`, pin at `:12`) and `kimi-pin` (record `:4126`, pin at `:4722`)" | adjacent |
| S3 | mori | 24 | `mori-shokunin/corpus/lessons/round-24-verifier-spotcheck.md:98` | "counts mismatches between a lane self-record (the dispatch ledger's `at`) and repo state (commit times)" | adjacent |

## Search commands

- `grep -rn 'git blame'` over the 10 lesson dirs and `.ufo/reports/round-*/{chousa,tabi,souji,tsukuroi,kengaku,tameshi,mori,kaidoku,kasegi,mado}.md` → **0** hits; `grep -rlE 'git blame|append-only-late' <lane>/{tools,scripts}` → **0 files in 10/10 lanes**.
- `grep -rniE 'introduc[a-z]* commit|per-row introduction|row.?s own introduction'` (same paths) → **6** hits (the S1 rows above).
- `grep -rniE 'release[- ]pin|pin[- ]recheck|pin row|recheck row'` over the 10 lesson dirs → **99** (tabi 74, mori 15, tameshi 3, tsukuroi 1, kaidoku 1; others 0); reports same pattern + `holds=16|drifted=7` → 26.
- `grep -rniE 'self-?assessment|self-?record|SELFRECORD'` over the 10 lesson dirs → **367** (tabi 117, tsukuroi 116, kaidoku 33, tameshi 30, souji 22, mori 21, kengaku 15, mado 7, chousa 3, kasegi 3); reports 212.

## Verdict — kama's round-83 claim is distinct on all three surfaces

**S1 (adjacent only, no owner).** No sibling resolves a row's own introduction commit as an acceptance rule: the five hits reuse the `git log --diff-filter=A`/introduction primitive for pushed-ness (souji r1), receipt dating (mori r16), LOG coupling (tabi r23), or single-container freeze identity (kaidoku r67), never per-row register acceptance against an event window. **No contested-scope handoff**; S1 is unowned in the live set.
**S2 (adjacent; nearest prior art tabi r29).** Tabi's release-pin recheck grades its own `SOURCES.md` rows at one Chromium tag (`holds=16 drifted=7`) by exact-substring span comparison over committed bytes. Kama differs: one row per `(engine, ref)` of `registry/engine-pin-relations.tsv`, a four-value verdict (`holds|reworded|moved|drifted`) re-derived from two committed extracts whose header `sha256` must match their bytes, plus a control where two identical extracts under a declared `drifted` are `bad`. Tabi's counter reads receipt-derived refetch records (its own disclosed weakness); tsukuroi judges service invariants and mori re-reads pinned sources without a relation register.
**S3 (adjacent; nearest prior art tabi's `check-selfassessment.mjs`).** It grades declared tallies against observed counters, but its supersession accepts *any* stated number in a correction paragraph (tabi r32 E27) and it grades current documents. Kama grades a prior round's six facts read with `git show` at the sealed revision, exact `old`/`new` tokens, a matching `at`, and a `fix` path whose tip bytes carry `new` outside correction-restatement regions. Chousa's self-audit uses disposition tags, kaidoku's `pointer-bind` grades line pointers, mori's is a closure observation — none is a sealed-revision fact regrade.

## Bounds

Read-only: no sibling repo, fleet-root file, or lane file was touched; only this seat dir was written. Coverage is the lanes and report ranges present (reports stop at r59–r87 per lane), so absence after a lane's last filed report is not claimed. Verdicts are textual adjacency; no sibling instrument was run.
