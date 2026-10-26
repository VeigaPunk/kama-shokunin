# S9Lesson — round-44 lesson skeleton (scribe, leaf)

**Verdict: delivered.** `round-44-skeleton.md` exists in the shape of `round-43.md` (header, `## Claims`, `## Gate`, `## Mistakes`, `## Spot-check`), both claim predicates appear verbatim from the preregistration, the Gate carries the two new rows with quote placeholders, `considerthese/2026-10-25.md` proposal 2, `Assimilation: none`, and D1–D6 with planned dispositions, and every measured round value is left as a placeholder. Two citation facts found on the way (G1 pin split, G2 `CORPUS.md` miscite) are recorded as findings, not repaired.

Axes named: **freshness** (C1's release-recheck population) and **calibration** (C2's self-vs-outside verdict ledger).

## Deliverables

- Skeleton: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/S9Lesson/round-44-skeleton.md` (82 lines, 17,766 bytes; 64 `<…>` placeholder spans).
- This report: `.ufo/waves/round-44/w1/out/S9Lesson.md`.
- Nothing was written to the lane tree, `corpus/`, `SCORECARD.md`, preregistration, counters or controls.

## What the skeleton contains

| Section | Content | Source of each fact |
|---|---|---|
| header | `author: kama L1`, `date: 2026-10-26`, `base: 9d9cc93e…`, `freeze:` placeholder | `round-43.md:1-6` shape; `.ufo/waves/round-44/preregistration.json:6` base |
| `## Claims` C1 | population 91, the prereg's "90 at 704366d76" vs the tree's 89/1/1 split, b11889 = `d854d98b…`, pin-watch `newer=117 status=behind`, counter sha256 `87503e18…`, base receipt `unverified=91 met=False`, target `unverified=0 flags_missing=0 section=1 met=True`, ledger header + verdicts, draft 81 `holds`/4 `unchanged-file`/6 `TODO`, C1 `limits` quoted | `preregistration.json:9-27,122`; `.ufo/waves/round-44/controls/base.c1.out:2`; `.ufo/waves/round-44/c1/{ls-remote,pin-watch}-freeze.out`; counter docstring `tools/round44-release-recheck-audit.py:24-26,57-60` |
| `## Claims` C2 | 34×3×2 = 204 rows, 30 outside files at base (rounds 20–23 absent ⇒ 12 outside keys `absent` by construction), counter sha256 `1933e75b…`, base `missing=204 met=False`, target `valid=204 table_missing=0 summary=1 axes=1`, scorecard legs, draft 204 rows (102/102, 15 `-` lines), C2 `limits` quoted, predicate verbatim | `preregistration.json:123-138`; `.ufo/waves/round-44/controls/base.c2.out:2`; counter docstring `tools/round44-verdict-ledger-audit.py:17-38,40-46` |
| `## Gate` | S482 (llama.cpp release b11889) and S483 (vLLM `preload.py` v0.31.0, D2) with URL/fetch/bytes/sha256/copy/quote placeholders; G1–G2 findings; considerthese proposal 2 (dated 2026-10-25); `Assimilation: none` with the one-line reason; id-collision check; D1–D6 table with planned dispositions | prereg `frontier`; `round-43-verifier-spotcheck.md` §7; `considerthese/2026-10-25.md` §Self-improvement suggestions |
| `## Mistakes` | placeholder + round-43 class vocabulary + the round-43 note-line convention | `round-43.md` §Mistakes |
| `## Spot-check` | placeholder naming `corpus/lessons/round-44-verifier-spotcheck.md` and the closure's seven sections | `round-43-verifier-spotcheck.md` §1–§7 |

Verbatim check (run, exit 0): both `predicate` strings from `preregistration.json` occur byte-for-byte in the skeleton — `C1 predicate verbatim: True`, `C2 predicate verbatim: True`; required tokens `# kama round 44 lesson`, `## Claims`, `## Gate`, `## Mistakes`, `## Spot-check`, `S482`, `S483`, `considerthese/2026-10-25.md`, `Assimilation: none` all present; `D1`…`D6` each have a table row.

## Evidence (commands run, output, exit code)

All read-only; every command ran in `/home/vgpnk/Projects/shokunin/kama-shokunin`.

1. `git log --oneline -3` → `098df344 round-44: wave-1 spec and dispatch (v2, 65 seats), C1/C2 drafts, seat fragment checker` / `77d1bbf5 round-44: freeze — preregistration, two counters, release-recheck draft tool, controls, census start` / `9d9cc93e round-43 verifier spot-check (integrator, hyaku)`. `git merge-base --is-ancestor 77d1bbf55c62a1d5fc08fcbd682f22277a5cdb40 HEAD` → exit 0. **Premise note:** the assignment names the working tree as commit `77d1bbf5`; the tree is one commit later (`098df344`), which carries the same preregistration and drafts plus the wave-1 spec/dispatch and the fragment checker.
2. `python3 -c` over `preregistration.json` → `population: 91`, `release: b11889 d854d98bae598388ecea1ed84396587e5edc326d`, `before: unverified=91 met=False (controls/base.c1.out)`, `target: unverified=0 flags_missing=0 section=1 met=True`, `C2 before: missing=204 met=False`, `C2 target: valid=204 table_missing=0 table_extra=0 summary=1 axes=1 met=True`, exit 0.
3. `sha256sum tools/round44-release-recheck-audit.py tools/round44-verdict-ledger-audit.py tools/release-recheck.py` → `87503e18e47dae6fa0414cf24d988f2a44ffa61d422db62c82cad3c24d8218d2`, `1933e75b2a5308d09d0cfafd166c95cfcb1b7c15eaf1bf9ad2b321a453224bd1`, `50e77fa1a3d9d1d4407c3fbdc9e0b67aeceaf0a92389638f0c471d44991ba157` — the first two equal `counter_sha256` in the preregistration; the third equals the `helper` line.
4. `cut -f10 .ufo/waves/round-44/c1/draft-ledger.tsv | tail -n +2 | sort | uniq -c` → `81 holds`, `6 TODO`, `4 unchanged-file`; `wc -l` → 92 (header + 91 data rows). `cut -f3 … | uniq -c` → `89 704366d76…`, `1 ad1b88ca…`, `1 c0fd7862…`.
5. `cut -f3 .ufo/waves/round-44/c2/draft-ledger.tsv | tail -n +2 | sort | uniq -c` → `102 outside`, `102 self`; `awk -F'\t' '$8=="-"'` → 15 rows with a `-` line; `cut -f1 … | sort -n | uniq` → rounds 10–43 all present. The draft's verdict column is deliberately not quoted in the skeleton (it is an unjudged last-hit).
6. `git ls-tree --name-only 9d9cc93e corpus/lessons/ | grep -c verifier-spotcheck` → `30`; the round numbers present are 10–19 and 24–43, so rounds 20–23 have no outside file (12 outside keys `absent` by construction).
7. Population pin check (Python over `git show 9d9cc93e:corpus/SOURCES.md`, exit 0): population 91, all 91 rows found; `rows whose source cell names 704366d76: 89`; only S001 and S015 name `master`; their anchors name `c0fd7862…` and `ad1b88ca…`. Ancillary: `ANCHOR-not-704` is expected for most rows — anchors carry line lists and raw sha256s, not the pin.
8. `git cat-file -e 9d9cc93e:corpus/CORPUS.md` → exit 128, `fatal: path 'corpus/CORPUS.md' does not exist in '9d9cc93e…'`; `git log --oneline --all -- corpus/CORPUS.md | wc -l` → 0; `git ls-files | grep -c '^corpus/CORPUS.md$'` → 0. `grep -n 'S482\|S483' corpus/SOURCES.md` → exit 1, no output (ids free; registry ends at `S481`, `corpus/SOURCES.md:234`).
9. `grep -n '^| id |' corpus/SOURCES.md` → `11:`; `sed -n '13p;27p' corpus/SOURCES.md` → S001, S015. The registry table header is line 11 and S001 line 13, so the skeleton's cites point where it says.
10. Counter docstring anchors (by grep, exact lines): C1 `tools/round44-release-recheck-audit.py:24` (`Ledger:`), `:57` (`Flags:`), `:60` (`met = …`); C2 `tools/round44-verdict-ledger-audit.py:17` (`Ledger:`), `:25` (`Evidence rule.`), `:40` (`Scorecard legs:`), `:46` (`met = …`). The skeleton cites these ranges after the first draft cited ranges two to six lines off.
11. `sed -n '1325p' SKILL.md` → the round-32 gate row containing "`--selftest` prints `GATE_SELFTEST pass=6 fail=0`" — the round-43 closure's `SKILL.md:1325` cite is accurate at base.
12. `sed -n '51,68p' SCORECARD.md` → line 53 still reads `Superseded in round 42. The live plan is \`### Round-43 measured results` and `### Planned (round 44)` lands at the end of the block (D1 open at base).

## Findings

**F1 (G1) — the preregistration's population sentence miscounts the pin split.**
- Where: `.ufo/waves/round-44/preregistration.json:15` (C1 `statement`), "(90 pinned at 704366d76 = b11755)".
- Show: `python3 -` over `git show 9d9cc93e:corpus/SOURCES.md` restricted to the 91 population ids → 89 source cells carry `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad`; S001 (`corpus/SOURCES.md:13`) names `master` and anchors `c0fd78626405c6d9b934efef0ec7291fcc20e3d6`; S015 (`corpus/SOURCES.md:27`) names `master` and anchors `ad1b88ca0d37a2171efba1c04f1a3531c78f1b52`. The draft ledger records exactly that: `89 / 1 / 1`.
- Impact: none on the predicate — the counter's population rule (pin = the URL ref when 40-hex, else the anchor's first 40-hex run) keeps S001 and S015 inside the 91 with their own pins, so `unverified` still counts 91.
- Proposed fix: counters and preregistration are frozen — do not edit. State `89 + 1 + 1 = 91` in the round-44 `SOURCES.md` section and in the measured results, and keep the flag in the lesson's Claims (done). Independently corroborated by peer seat `.ufo/waves/round-44/w1/out/K1Design.md:28` and `:174` (routed there as its D3), which derives the same split.

**F2 (G2) — the round-43 lesson cites a contract file that does not exist.**
- Where: `corpus/lessons/round-43.md:18` ("CORPUS.md rule 1") and `:44` ("CORPUS.md rule 2").
- Show: `git cat-file -e 9d9cc93e:corpus/CORPUS.md` → exit 128, path does not exist; `git log --oneline --all -- corpus/CORPUS.md | wc -l` → 0; `git ls-files | grep -c '^corpus/CORPUS.md$'` → 0.
- Proposed fix: do not rewrite the round-43 sentence (append-only). This round's lesson cites `SOURCES-CONTRACT-v1` (`corpus/SOURCES.md:3`) and the registry table (`corpus/SOURCES.md:11`) instead; if the L1 wants a record, add one line to the round-44 `SOURCES.md` search log naming the miscite.

**F3 — D1 is still open at base (routed, not mine to fix).**
- Where: `SCORECARD.md:53` — `Superseded in round 42. The live plan is \`### Round-43 measured results`; the round-43 block runs to line 67 and `### Planned (round 44)` sits at its end, so `### Round-43 measured results` has no heading of its own.
- Proposed fix (in the skeleton's D1 row, as planned disposition): restore line 53 to point at `### Planned (round 44)`, give `### Round-43 measured results` its own heading before it at the end of the file, and append a correction note in §Round 44 rather than rewriting cited text.

No defect found in the two counters, the controls, the draft ledgers or the preregistration's structure; the counters' `before`/`target` strings match `controls/base.c{1,2}.out` and their own docstrings.

## Placeholders left for integration (by design)

- Header `freeze:` commit; every measured round value in C1/C2 (`unverified`, `flags_missing`, `section`, `met`; `valid`, `missing`, `table_missing`, `summary`, `axes`, `absent`, the agreement line).
- Gate: S482/S483 URL, access date, fetch command, bytes, sha256, copy path, locator and located quote; S483's planned `source:` edit; the considerthese disposition line; the id re-check at integration.
- D1–D6: the receipt/diff/commit paths each disposition will produce; D6's entry-marking outcome and the N2 emitter fold.
- `## Mistakes`: all rows and the note lines.
- `## Spot-check`: every value, taken from `corpus/lessons/round-44-verifier-spotcheck.md` once it exists.

## Out of scope / not done

- No upstream fetch: I did not run `git ls-remote`, `gh`, or read `/fast/scratch/hyaku/kama-r44/shared/llama.cpp`; the b11889 tag→commit binding is quoted from the committed freeze receipt only.
- No counter was run against the round (there is no round-44 ledger to score); no `check-fragment.py` run (this seat produces no ledger fragment).
- No lane file written or committed; no git write; no service touched; no tool installed (nothing needed).
- Scratch `/fast/scratch/hyaku/kama-r44/S9Lesson/` held one copy of `SOURCES.md` at base for the id count and was removed before this report; nothing cited here depends on it.

## Artifact paths

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/S9Lesson/round-44-skeleton.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/S9Lesson.md`
