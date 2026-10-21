VERDICT: partial - rows S058-S065 pass every field/Gate check; search-log placement and two anchor-precision deviations found.
Scope: CORPUS.md §"SOURCES.md — where a shokunin learns" (frozen v1) + `scripts/sources-census.sh` vs lane `corpus/SOURCES.md` S058-S065 (lines 70-77). Read-only; no tool installs; no lane mutation.

## Checklist (what a NEW row + its lesson `## Gate` entry must meet)
1. `id` = S+3 digits, next unused, never reused; no `|` in any cell (11 cols => NF=13).
2. `source` = title — canonical URL or DOI (repo path/command for `own-work`).
3. `kind` ∈ spec|docs|paper|code|tool|dataset|talk|book|community|own-work (E05).
4. `tier` ∈ A|B|C, scoped to `scope`; `community` never A (E10); no NATO/GRADE labels.
5. `scope` = the claim/topic the tier applies to.
6. `anchor` = exact section/heading/page/line PLUS revision (version/commit/pub date); never a bare homepage.
7. `teaches` = one grounded learner benefit; rejected reads `REJECTED: <reason>; flip: <…>`; corrections open `supersedes S0NN —`.
8. `status` ∈ queued|mined|rejected; mined ⇒ ≥1 used-by path (W03 if `—`); W01 = tier-C mined with non-`—` used-by.
9. `opened` = ISO date the author opened it, not future (E08); `recheck` = ISO date or cadence (NNd/on-release) (E09).
10. `used-by` = repo-relative paths or `—`; mined paths must exist (E11); append-only: only status/recheck/used-by change in place, logged old→new in the round lesson (rule 2).
11. Warnings: W03 mined-with-`—`; W04 same URL across scopes (never fails validate); E04 = same URL+scope without `supersedes`.
12. Row written only in the round that opens the source; lesson `## Gate` records URL + access date + ≤25-word located quote grounding `teaches` (rule 1).
13. Search log (rule 5, Shape §`## Search log`): one prose note per bounded search — question/query, where, date, identified/screened/included/excluded, exclusion reasons, stop rationale; negative claim carries its sweep.
14. No credentials/session/private URLs/`op://` (rule 6); rows only inside `## Registry` (E12); Shape = exactly Registry/Paths/Search log/Leads.

## Executed verification (all commands run this session, cwd fleet root unless noted)
- `scripts/sources-census.sh census <lane>` → exit 0: rows 65, tier.A 62, tier.C 3; mined 52, queued 6, rejected 7 — exactly matches the declared census-before (`…/round-21/sources/census-before.txt` figures).
- `scripts/sources-census.sh validate --today 2026-10-21 <lane>` → exit 0; only W04: S031, S043, S056, S060, S064, S065. Zero E-codes.
- `scripts/sources-census.sh overdue --today 2026-10-21 <lane>` → exit 0; cadence lines only, nothing overdue.
- Frozen manual census block (CORPUS.md, lane root) → exit 0: rows 65, malformed 0, duplicate ids none, enum/tier-inflation none, missing used-by none.
- `git log -S"| S05N |"…` → S058-S064 first commit 33a6777 (2026-10-21, round-20); S065 c731103 (2026-10-21).
- `git diff 33a6777^ 33a6777 -- corpus/SOURCES.md` → +7 lines, 0 removed (append-only ✓). `git diff c731103^ c731103` → only S063 used-by rewrite (permitted cell, logged old→new in round-20.md "Wave-2 integration corrections"), +S065 row, +S065 note section.
- `ls` used-by/anchor paths → exit 0: `corpus/knowledge/gguf-declared-identity.md`, `corpus/knowledge/error-is-not-a-verdict.md`, `corpus/lessons/round-20.md`, `.ufo/waves/round-20/build/advice/SrcGgufPyReader.md`, `.ufo/waves/round-20/falsify/advice/SourceS061.md` all exist.
- round-20.md §Gate (line 43) + §Gate supplement (line 191): all 8 rows carry URL, revision, located quote; access date "All sources opened 2026-10-21" / "(opened 2026-10-21)". Quote word counts verified ≤25: S058=11, S060=17, S061=15, S062=14, S064=15, S065=5, S059/S063 located code quotes. Post-S065 census line in the lesson matches my observed validate/census output incl. W04 for S065.

## Findings (by severity)
- F1 [medium — contract placement] No `## Search log` entry in SOURCES.md for the bounded search that produced S058-S064. The note exists only in `corpus/lessons/round-20.md` §Gate ("Search question… Screened 7 … included 7 (one retained rejected)… Stop: …"). Rule 5 + Shape place notes in SOURCES.md `## Search log`; every batch through round 14 is there. Evidence: `grep -n 'S058\|S059\|S060\|S062\|S063\|S064' corpus/SOURCES.md` → zero hits after line 96; `## Search log` = lines 86-95, last bullet round-14.
- F2 [low] S065's search note is complete (question/where/Identified 1, screened 1, included 1, excluded 0/quote/stop) but sits in a fifth, non-contract H2 `## Round-20 source correction — S065` (SOURCES.md:231-237) after `## Leads (unopened)`; Shape enumerates exactly four H2 sections and reserves Leads for bullets. Extends pre-existing drift (rounds 15-19 supplements appended as prose under Leads).
- F3 [low] S059 `anchor` lacks line/§ precision: "GGUFReader version/endian branches and gguf/constants.py GGUFValueType at 704366d76" + advice-report path — weaker than contract "exact section/heading/page/line" and sibling code rows (S063 pins "RUN_ERROR(true) line 63"). Commit pin + opening-report path mitigate.
- F4 [low] S064 `anchor` revision says "Python 3.14 documentation" while sibling same-page rows S044/S061/S065 pin "Python 3.14.8"; minor revision imprecision.
- Info: S065 adds a 6th W04 (shares docs.python.org/3.14/library/sys.html with S061 across scopes); disclosed in the lesson's post-S065 census line; W-codes never change exit (validate exit 0). S061/S065 same-URL-different-scope correctly avoids E04, and S065 `teaches` opens `supersedes S061 —` per rule 2; S061 cells untouched (append-only ✓).
- Info: header "Every row was opened in round 10" (SOURCES.md:6-7) is stale for S058-S065 but already neutralized by the appended round-11 D2 correction prose (~line 101); no action.

## Residual risk / verification gaps
- Contract rule 1's "Non-author verification re-opens a sample" is unmet for these rows: round-20.md §Trend verdicts discloses "no independent non-author R20 admit/reject sample" — all 8 Gate entries are author-verified only.
- F1-F4 are prose/placement deviations; no mechanical validator covers them (E-codes/W-codes all clean). The round-21 L1 should require: any new row this round lands its search note inside `## Search log`, and an errata-style note could relocate/cross-reference the S058-S064 batch note and the S065 section without rewriting history.
[INFERENCE] none beyond labels above; every claim cites an executed command with observed output/exit.
