VERDICT: confirm - S051’s citation is stale; the full paragraph is now at `corpus/SOURCES.md:210-215`.

# Scope and result

At `37bd4c5bd456a2f8a54d3312c28495c321715856`, the requested `git grep -n 'SOURCES.md:[0-9]'` population is 347 matching lines. The complete line/token/range-element census is in `.ufo/waves/round-20/build/out/S051AnchorShift/pointer-census.tsv`; the mechanically changed-element ledger is `.../stale-ledger.tsv`. The S057-caused subset is `.../s057-stale-table.tsv`; proposed end-of-file corrections are in `.../qualification-drafts.md`.

## Stale pointers caused by S057

| Pointer site (pointer-writing revision) | Old source range | Current source range at pinned tip | Finding |
|---|---:|---:|---|
| `corpus/lessons/round-18.md:285` (`0c75c611`) | `209-213` | `210-215` | **S051.** At the writing revision, the paragraph already spans `209-214`; the citation omitted its last sentence. The S057 insertion shifts the complete paragraph to `210-215`. |
| `.ufo/waves/round-18/falsify/advice/CorpusCensus.md:63` (`101f3991`) | `186-187` | `187-188` | Same cited text, shifted by one. |
| `.ufo/waves/round-18/falsify/advice/CorpusCensus.md:65` (`101f3991`) | `198-199` | `199-200` | Same cited text, shifted by one. |
| `.ufo/waves/round-18/falsify/advice/MistakesFailCapable.md:13` (`101f3991`) | `191-193` | `192-194` | Same cited text, shifted by one. |
| `.ufo/waves/round-18/falsify/advice/ReportSources.md:17` (`101f3991`) | `59-67, 181-199` | `59-67, 182-200` | First range holds; second shifted by one. |
| `.ufo/waves/round-18/falsify/advice/ReportSources.md:43` (`101f3991`) | `191-194` | `192-195` | Same cited text, shifted by one. |
| `.ufo/waves/round-18/falsify/advice/ReportTrends.md:22` (`101f3991`) | `60-62, 185-189` | `60-62, 186-190` | First range holds; second shifted by one. |

The six non-S051 items are other round-18 citations moved by the same insertion. Their end-of-file draft qualifications are supplied alongside the S051 draft; no lane files were edited.

## Later qualifications / non-findings

| Pointer site | Pointer | Result |
|---|---|---|
| `.ufo/waves/round-19/build/advice/QualityCriteria.md:23` | `round-18.md:285` cites `SOURCES.md:209-213, now 210-215` | Historical description of the stale pointer; its stated replacement `210-215` is correct. No further correction needed. |
| `.ufo/waves/round-19/build/advice/CritC1Inflation.md:11`, `R18Defects.md:12`, `RevisionDriftScan.md:13,22` | `SOURCES.md:217-221` | Holds. These cite the S055 qualification appended in the S057 commit itself, so that later block was not shifted by the insertion. |

## Evidence and method

- `git -C /tmp/kama-r20-S051AnchorShift/lane grep -n 'SOURCES.md:[0-9]' 37bd4c5bd456a2f8a54d3312c28495c321715856 | wc -l` — exit 0; output `347`.
- `git -C /tmp/kama-r20-S051AnchorShift/lane blame -L 285,285 37bd4c5bd456a2f8a54d3312c28495c321715856 -- corpus/lessons/round-18.md` — exit 0; pointer line written by `0c75c611`.
- `git -C /tmp/kama-r20-S051AnchorShift/lane show 0c75c611474cfc9f3c549e056fb0b736b20b854f:corpus/SOURCES.md` — exit 0; S051 clarification occupies lines 209-214.
- `git -C /tmp/kama-r20-S051AnchorShift/lane diff --unified=0 0c75c611474cfc9f3c549e056fb0b736b20b854f 7229fa9 -- corpus/SOURCES.md` — exit 0; adds S057 at line 69 and the later S055 qualification at the end.
- `git -C /tmp/kama-r20-S051AnchorShift/lane show 7229fa9:corpus/SOURCES.md` and `git -C /tmp/kama-r20-S051AnchorShift/lane show 37bd4c5bd456a2f8a54d3312c28495c321715856:corpus/SOURCES.md` — both exit 0; S051 clarification is at 210-215 and S055 qualification at 217-221.
- `git -C /tmp/kama-r20-S051AnchorShift/lane blame -L 217,221 37bd4c5bd456a2f8a54d3312c28495c321715856 -- corpus/SOURCES.md` — exit 0; all five S055 qualification lines were added by `7229fa9`.
- `git -C /tmp/kama-r20-S051AnchorShift/lane grep -n -E 'SOURCES\.md:217-221' 37bd4c5bd456a2f8a54d3312c28495c321715856` — exit 0; found the four later qualification references listed above.
- `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-20/build/out/S051AnchorShift/pointer-census.py /tmp/kama-r20-S051AnchorShift/lane 37bd4c5bd456a2f8a54d3312c28495c321715856 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-20/build/out/S051AnchorShift` — exit 0; `grep_lines=347`, `elements=392`, `tokens=366` distinct file/line/token tuples, `s057_caused_elements=7`, `mechanically_changed_elements=79`.

`pointer-census.tsv` expands comma/range forms and records pointer-line blame revision, selected source frame, historical/current text and mechanical mapping. Its `content_at_frame` field is a contextual heuristic, not semantic proof; `stale-ledger.tsv` intentionally includes changed rows and writer-frame out-of-bounds cases, not just S057 shifts. The seven-row S057 subset was checked against exact source excerpts above. **Unresolved:** some old pointers refer to uncommitted intermediate trees that Git cannot reconstruct; the full census marks writer-frame bounds/content uncertainty rather than treating it as proof of absence. No tools were installed or updated.