# ScribeGateLog — round-29 Gate verification draft

## Axes
- **Auditability:** each new row has its source URL, UTC access sample, and a short, verbatim quote.
- **Registry consistency:** status, recheck, and used-by transitions match the wave-1 proposals and current working-tree rows.

## Behavior / proposed lesson text

Proposed replacement for `corpus/lessons/round-29.md` §Gate's source table and status-change paragraph:

```markdown
## Gate

New SOURCES rows S174–S177 were proposed by the wave-1 scribes. Their saved source pages and quote captures are in the corresponding `w1/out/ScribeSrc*/` directories. Access timestamps below are the scribes' UTC samples from 2026-10-23.

| S### | URL | accessed (UTC, 2026-10-23) | located quote (≤25 words) | opened by |
|---|---|---|---|---|
| S174 | https://git-scm.com/docs/git-blame | 2026-10-23T12:02:48Z | “last modified the line” (§DESCRIPTION) … “commit information for each line, not just the first time a commit is referenced” (§--line-porcelain) (18 words) | ScribeSrcGitBlame |
| S175 | https://git-scm.com/docs/git-merge-base | 2026-10-23T12:03:03Z | “and exit with status 0 if true, or with status 1 if not.” (§OPTIONS, `--is-ancestor`; 13 words) | ScribeSrcMergeBase |
| S176 | https://git-scm.com/docs/git-grep; https://git-scm.com/docs/gitglossary | 2026-10-23T12:02:41Z; 2026-10-23T12:02:57Z | “Instead of searching tracked files in the working tree, search blobs in the given trees.” (§OPTIONS, `<tree>`; 15 words); “If it matches, the path is ignored.” (Pathspec magic, `exclude`; 7 words; 22 total) | ScribeSrcGitGrep |
| S177 | https://git-scm.com/docs/pretty-formats | 2026-10-23T12:02:47Z | “committer date, UNIX timestamp” (`%ct`) … “committer date, strict ISO 8601 format” (`%cI`) (10 words) | ScribeSrcPrettyFormats |

Registry transitions from each wave-1 proposal to the current `corpus/SOURCES.md` working-tree row (current status / recheck / used-by):

| Row | status old → new | recheck old → new | used-by old → new |
|---|---|---|---|
| S174 | `mined` → `mined` (unchanged) | `on-release` → `on-release` (unchanged) | `.ufo/waves/round-29/w1/out/ScribeKnowledgeEntry/self-assessment-at-writing.md` + `.ufo/waves/round-29/count-c1.py` → `corpus/knowledge/self-assessment-at-writing.md` + `.ufo/waves/round-29/count-c1.py` |
| S175 | `mined` → `mined` (unchanged) | `on-release` → `on-release` (unchanged) | `.ufo/waves/round-29/w1/out/ScribeKnowledgeEntry/self-assessment-at-writing.md` → `corpus/knowledge/self-assessment-at-writing.md` + `.ufo/waves/round-29/count-c1.py` |
| S176 | `mined` → `mined` (unchanged) | `on-release` → `on-release` (unchanged) | `.ufo/waves/round-29/w1/out/ScribeKnowledgeEntry/self-assessment-at-writing.md` → `corpus/knowledge/self-assessment-at-writing.md` + `.ufo/waves/round-29/count-c1.py` |
| S177 | `queued` → `mined` | `on-release` → `on-release` (unchanged) | `—` → `corpus/knowledge/self-assessment-at-writing.md` + `.ufo/waves/round-29/count-c1.py` |

The two current used-by targets both exist on disk. The former wave-1 knowledge-entry target also exists, but the integrated rows now point to `corpus/knowledge/self-assessment-at-writing.md`. S177's wave-1 proposal records that the intended entry was absent when checked, explaining its queued / `—` draft state. No claim is made here about the correctness of C1; these rows document source provenance.
```

## Findings and evidence

- The source registry is being read from the uncommitted working tree at lane `HEAD` `513eba3ba51a142c9936553e3a85918345eb5c4c`; `git status --short` showed `M corpus/SOURCES.md` and `?? corpus/lessons/round-29.md`. The round lesson and source rows are therefore not attributed to that commit.
- Current rows are `corpus/SOURCES.md:187–190` (S174–S177). Proposal rows are `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w1/out/ScribeSrcGitBlame/row.md:1–3`, `.../ScribeSrcMergeBase/row.md:1`, `.../ScribeSrcGitGrep/row.md:1–5`, and `.../ScribeSrcPrettyFormats/row.md:1–7`.
- Quote evidence: the corresponding saved source pages and `quote.txt` captures under `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w1/out/ScribeSrc{GitBlame,MergeBase,GitGrep,PrettyFormats}/`. Direct page reads/searches found S174's “last modified the line” and porcelain clause, S175's quoted exit-status clause, S176's tree-search clause and glossary exclusion clause, and both S177 placeholder phrases. The S176 tree-search phrase crosses an HTML line break; the full phrase is present in the saved page. The quote and access-time details are also in each scribe's `row.md` and `REPORT.md`.
- Current `## Gate` text is `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-29.md:93–108`. Its status paragraph reports S177's queued-to-mined and dash-to-use transition, but omits the S174–S176 used-by migration from the wave-1 draft knowledge-entry path to the canonical entry. It also omits the counter addition to S175 and S176. The draft above records those deltas and makes unchanged recheck values explicit.
- Current use-by target existence check, run from `/home/vgpnk/Projects/shokunin/kama-shokunin`:
  - Command: `for p in corpus/knowledge/self-assessment-at-writing.md .ufo/waves/round-29/count-c1.py .ufo/waves/round-29/w1/out/ScribeKnowledgeEntry/self-assessment-at-writing.md; do if test -f "$p"; then printf 'EXISTS %s\\n' "$p"; else printf 'MISSING %s\\n' "$p"; fi; done`
  - Output: `EXISTS corpus/knowledge/self-assessment-at-writing.md`; `EXISTS .ufo/waves/round-29/count-c1.py`; `EXISTS .ufo/waves/round-29/w1/out/ScribeKnowledgeEntry/self-assessment-at-writing.md`.
- The knowledge entry itself names S174–S177 in `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/knowledge/self-assessment-at-writing.md:1`.

## Commands and outcomes

1. `date -u '+%Y-%m-%dT%H:%M:%SZ' && git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse HEAD && git -C /home/vgpnk/Projects/shokunin/kama-shokunin status --short` — `2026-10-23T18:30:29Z`; `513eba3ba51a142c9936553e3a85918345eb5c4c`; working-tree status included the modified `corpus/SOURCES.md` and untracked `corpus/lessons/round-29.md`.
2. `git show 2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d:corpus/SOURCES.md | grep -nE '^\\| S17[4-7] \\|' || true; git log --format='%H %s' --all -- corpus/SOURCES.md | head -8` — the base-tree grep emitted no S174–S177 row; the history command printed its eight-entry log excerpt.
3. The three-file `test -f` loop above — all three paths returned `EXISTS`.
4. Read-only quote searches against the four saved wave-1 source pages found the text cited above. No page was fetched again.
5. `mkdir -p /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w2/out/ScribeGateLog` — completed without output.

## Touched surfaces, limits, and out of scope

- **Only file written:** `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w2/out/ScribeGateLog/report.md`.
- Read-only surfaces: `corpus/SOURCES.md`, `corpus/lessons/round-29.md`, `corpus/knowledge/self-assessment-at-writing.md`, `.ufo/waves/round-29/count-c1.py`, and the cited wave-1 source-scribe artifacts.
- No lane files, judge, Git index, or jj state were edited. No test, build, counter run, commit, install, or fresh web fetch was performed.
- The access times are the wave-1 scribes' UTC samples, not independently remeasured HTTP transaction times. In particular, the S175 report says its UTC sample was concurrent with fetch. S177's report says the live page is not version-pinned and its queried installed-manual locations were unavailable; its source proposal still records local Git 2.56.0.
- The task separately names `.ufo/waves/round-29/w2/ScribeGateLog.md` as a report path, outside the hard write boundary that permits writes only under this seat's `w2/out/ScribeGateLog/` directory. I left that out-of-scope path untouched; this file is the complete scoped report copy.

## Artifact

`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w2/out/ScribeGateLog/report.md`
