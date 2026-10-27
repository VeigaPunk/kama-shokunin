# X7Regen — round-52 item X7Regen: independent full-scope recomputation of the C2 append-only accounting

**Verdict: no defect.** My own engine (no import of the frozen counter or of `tools/append-only-audit.py`), run against commit `5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8` over every contract row, every commit's first-parent diff, gives **corr_lost=0, row_lost=10**, and reproduces the tip ledger's **10 rows key for key, count for count, with no extra and no missing row**. It also reproduces the frozen base state exactly (corr_lost=151, row_lost=10, and the per-file distribution in `controls/base.c2.out:56`), which calibrates the engine against evidence it did not produce. One calibration observation follows (§6): the build restored 155 lines while the frozen simplified rule grades 151 of them as lost; the other 4 are `## Planned` (an exempt heading) lines the tool's origin/not-gutted exempt rule disclosed at base.

Scope statement (round-51 closure D4 asks for it): **all ten** `registry/append-only-contract.tsv:2-11` rows at the tip, expanded to **99 files** (the `corpus/lessons/*.md` glob resolves to 90 files at this revision), all **350** commits reachable from the tip, **109** (commit, file) deletion events, regions `*`, `exempt=` and `only=` applied here independently, A-row permitted rows removed here. **Nothing was left undecided**; caveats and sensitivities are in §7.

---

## 1. Scope, exactly

Contract read from the tip blob `git show 5dacf2c7:registry/append-only-contract.tsv`:

| contract row | rule | region (as declared) | files at tip |
|---|---|---|---|
| `LOG.md` | A-corr | `*` | 1 |
| `SCORECARD.md` | A-corr | `exempt=## Axes\|## Planned\|## Retired\|## Saturation\|## Capabilities@SCORECARD.md:6` | 1 |
| `corpus/QUALITY.md` | A-corr | `*` | 1 |
| `corpus/README.md` | A-corr | `*` | 1 |
| `corpus/SOURCES.md` | A-row | `*` | 1 |
| `corpus/lessons/*.md` | A-corr | `*` | 90 |
| `registry/history/DELTA.md` | A | `*` | 1 |
| `registry/report-landing-errata.tsv` | A | `*` | 1 |
| `corpus/knowledge/consumer-registry.md` | A-corr | `only=## Errata@...:30` | 1 |
| `corpus/knowledge/error-is-not-a-verdict.md` | A-corr | `only=## Round24@...:173` | 1 |

- **99 files audited, 21 with deletions, 78 with none** (including `registry/history/DELTA.md` and `corpus/knowledge/error-is-not-a-verdict.md`).
- Contract rows are **identical at base and tip** (`contract_rows_same_base_tip=True`).
- History: `git rev-list --topo-order --parents 5dacf2c7` = **350 commits**; each diffed against its **first parent** (`git diff <p1> <c>`). Two merges exist (`2f7303c2…`, `5396a876…`); both have **zero** deletions against their first parent (`git diff --no-color -U0 <m>^1 <m> -- <contract paths> | grep -c '^-[^-]'` → `0`, `0`), so merges do not affect the accounting.
- 109 deletion events — the same count the counter reports (`c2-build.out:12`, `events 109`).

## 2. Method (my own code)

Deliverable engine: `.ufo/waves/round-52/w1/out/X7Regen/recompute_c2.py` (`python3`, stdlib only).

- **Deleted lines:** parse `git diff --no-color --no-ext-diff --no-renames -U0 <p1> <c>`; each hunk header gives the **1-based old-line range**; the parser asserts per hunk that the body's `-`/`+` line counts equal the header's `-old,new` counts (any mismatch aborts), so a misread hunk cannot be silently graded. The deleted line bytes are taken from the parent blob at those positions.
- **Key:** line bytes with one trailing CR removed, `sha256` hexdigest.
- **Fence:** own CommonMark §4.5 reading (0–3 spaces + 3+ backticks with no backtick in the info string, or 3+ tildes; closing run same char, at least as long, only spaces/tabs after; unclosed runs to EOF). Fence lines and fenced lines never establish a section.
- **Section of a deleted line:** last line at or before it in the **parent** blob that starts with `## ` and is not a fence line nor inside a fence (`\r` and trailing blanks stripped); `None` before the first.
- **Grading:** `*` → all; `exempt=H1\|…\|Hn` → graded unless the section equals one of the Hi; `only=P` → graded only if the section starts with P.
- **A-row permitted rows (only `corpus/SOURCES.md`):** a deleted line matching `^ {0,3}\| *S[0-9]{3,} *\|` is ungraded when the commit's blob still holds a row with the same id and every cell except **0-based 7, 9, 10** (the docstring's 1-based cells 8, 10, 11 = status, recheck, used-by) byte-equal. Cells are split on `|` outside backtick spans, `\|` treated as content, cells stripped.
- **Held at tip, per event:** for each key graded `G` times, `P` = parent copies, `D` = copies this event deleted, `K = max(0, P-D)` (kept), `M` = tip copies, `restored = max(0, M-K)`, `unheld = G - min(G, restored)` — the frozen docstring's semantics, implemented independently.

## 3. Losses at 5dacf2c7 — totals per rule and per file

Rules (`recompute.txt:3-6`):

| rule | deleted | graded | permitted (A-row) | held at tip | **unheld** |
|---|---|---|---|---|---|
| A-corr | 6101 | 5856 | 0 | 5856 | **0** |
| A | 3 | 3 | 0 | 0 | **3** |
| A-row | 67 | 9 | 58 | 2 | **7** |
| **all** | **6171** | **5868** | **58** | **5858** | **10** |

Per file (`recompute.txt:7-28`; 78 further audited files deleted 0 lines):

| file | rule | deleted | graded | ungraded by region | held | unheld |
|---|---|---|---|---|---|---|
| `LOG.md` | A-corr | 2320 | 2320 | 0 | 2320 | 0 |
| `SCORECARD.md` | A-corr | 2611 | 2385 | 226 (exempt) | 2385 | 0 |
| `corpus/QUALITY.md` | A-corr | 377 | 377 | 0 | 377 | 0 |
| `corpus/README.md` | A-corr | 685 | 685 | 0 | 685 | 0 |
| `corpus/SOURCES.md` | A-row | 67 | 9 | 58 permitted | 2 | 7 |
| `corpus/knowledge/consumer-registry.md` | A-corr | 19 | 0 | 19 (only=) | 0 | 0 |
| `corpus/lessons/round-1.md` | A-corr | 3 | 3 | 0 | 3 | 0 |
| `corpus/lessons/round-16.md` | A-corr | 11 | 11 | 0 | 11 | 0 |
| `corpus/lessons/round-18.md` | A-corr | 4 | 4 | 0 | 4 | 0 |
| `corpus/lessons/round-19.md` | A-corr | 6 | 6 | 0 | 6 | 0 |
| `corpus/lessons/round-25.md` | A-corr | 10 | 10 | 0 | 10 | 0 |
| `corpus/lessons/round-26.md` | A-corr | 17 | 17 | 0 | 17 | 0 |
| `corpus/lessons/round-27.md` | A-corr | 13 | 13 | 0 | 13 | 0 |
| `corpus/lessons/round-28.md` | A-corr | 6 | 6 | 0 | 6 | 0 |
| `corpus/lessons/round-32-verifier-spotcheck.md` | A-corr | 1 | 1 | 0 | 1 | 0 |
| `corpus/lessons/round-38.md` | A-corr | 11 | 11 | 0 | 11 | 0 |
| `corpus/lessons/round-4-recensus.md` | A-corr | 1 | 1 | 0 | 1 | 0 |
| `corpus/lessons/round-40.md` | A-corr | 1 | 1 | 0 | 1 | 0 |
| `corpus/lessons/round-42.md` | A-corr | 4 | 4 | 0 | 4 | 0 |
| `corpus/lessons/round-43.md` | A-corr | 1 | 1 | 0 | 1 | 0 |
| `registry/report-landing-errata.tsv` | A | 3 | 3 | 0 | 0 | 3 |

Region usage, measured rather than assumed (`probe.txt`, `restored-arith` independent):

- `exempt=` (SCORECARD): all 226 ungraded deletions fall in exactly the five declared headings — `## Axes` 100, `## Planned` 66, `## Capabilities` 30, `## Retired` 20, `## Saturation` 10; every other parent section is graded (e.g. `## Round 20` 131, `## Round 22` 117; full table in `probe.txt:1-273`).
- `only=` (consumer-registry): all 19 deletions sit outside `## Errata` (five other headings: 9/5/2/1/2) → 0 graded, 0 lost; `error-is-not-a-verdict.md` had no deletions.
- `*`: everything else graded; nothing ungraded outside the two regions above and the A-row permitted rows.

## 4. Comparison with the frozen counter

| quantity | counter receipt | my recomputation |
|---|---|---|
| tip corr_lost | **0** (`measured/c2-build.out:3`) | **0** |
| tip row_lost | **10** (`measured/c2-build.out:3`) | **10** |
| tip ledger rows / disclosed | 10 (`c2-build.out:12`) | 10, matched 10, missing 0, extra 0 |
| tip graded deletions | 5868 (`c2-build.out:12`) | **5868** (exact) |
| tip deletion events | 109 (`c2-build.out:12`) | **109** (exact) |
| base corr_lost | 151 (`controls/base.c2.out:2`) | **151** |
| base row_lost | 10 (`controls/base.c2.out:2`) | **10** |
| base ledger rows | 165 (`base.c2.out:2`, `:57`) | 165 parsed |
| base graded deletions | 5867 (`base.c2.out:57`) | **5867** (exact) |
| base deletion events | 107 (`base.c2.out:57`) | **107** (exact) |
| base unheld per A-corr file | `base.c2.out:56` (LOG 22, README 20, SCORECARD 19, R26 17, R27 13, R16 11, R38 11, R25 10, R19 6, R28 6, R18 4, R42 4, R1 2, QUALITY 2, R4 1, R32 1, R40 1, R43 1) | **identical, file for file** |

The base match is the strong calibration: my engine had no access to the counter's numbers, yet reproduces its per-file loss distribution, its graded count, and its event count exactly at a revision frozen before this wave.

## 5. The ledger's 10 rows, key by key

Tip ledger (`git show 5dacf2c7:registry/append-only-disclosures.tsv`, 11 lines = header + 10). Every row is a deletion event my engine found, in an A or A-row file, with `restored=0`:

| ledger row (commit, file, sha256[:12], count) | my P / D / K / M / restored |
|---|---|
| `ccc4bb31267f…`, `corpus/SOURCES.md`, `e0580c97f53a`, 1 | 1 / 1 / 0 / 0 / 0 |
| `1471344b4c8b…`, `registry/report-landing-errata.tsv`, `287af57410f5`, 1 | 1 / 1 / 0 / 0 / 0 |
| `1471344b4c8b…`, `registry/report-landing-errata.tsv`, `aa792b393d96`, 1 | 1 / 1 / 0 / 0 / 0 |
| `1471344b4c8b…`, `registry/report-landing-errata.tsv`, `aaa567f70573`, 1 | 1 / 1 / 0 / 0 / 0 |
| `54c6f4fe070c…`, `corpus/SOURCES.md`, `3b584ff21379`, 1 | 1 / 1 / 0 / 0 / 0 |
| `54c6f4fe070c…`, `corpus/SOURCES.md`, `d7abbe77f01e`, 1 | 1 / 1 / 0 / 0 / 0 |
| `54c6f4fe070c…`, `corpus/SOURCES.md`, `de9562c37189`, 1 | 1 / 1 / 0 / 0 / 0 |
| `54c6f4fe070c…`, `corpus/SOURCES.md`, `f5ca7c2bbee4`, 1 | 1 / 1 / 0 / 0 / 0 |
| `8bc8e3758248…`, `corpus/SOURCES.md`, `bcd910486aa5`, 1 | 1 / 1 / 0 / 0 / 0 |
| `3d42897b6529…`, `corpus/SOURCES.md`, `d0c8b17e8055`, 1 | 1 / 1 / 0 / 0 / 0 |

Set equality holds in both directions: `ledger_missing_from_mine=[]`, `my_unheld_absent_from_ledger=[]` (`recompute.json`). No ledger row names an A-corr file, and every row is a deletion event (`verify_restore_arith.py` prints `tip ledger rows naming an A-corr file: 0`; `tip rows == base A/A-row rows: True`).

**A-row permitted detail** (`probe.txt:278-288`, `== A-ROW PERMITTED DETAIL`): of 67 deleted `SOURCES` lines, 58 rows were permitted (id still present with all immutable cells byte-equal), 6 failed on immutable cells, 1 on a vanished id, and 2 were blank lines (non-rows; graded but held — blank lines exist at tip). Not-permitted rows:

| commit | id | reason | immutable 0-based cells changed |
|---|---|---|---|
| `ccc4bb31267f` | S041 | immutable-cell-changed | 5, 6 (anchor, teaches) |
| `54c6f4fe070c` | S189 | immutable-cell-changed | 4 (scope) |
| `54c6f4fe070c` | S190 | immutable-cell-changed | 1, 4, 5, 6 |
| `54c6f4fe070c` | S191 | immutable-cell-changed | 1, 4, 5, 6 |
| `54c6f4fe070c` | S192 | id-gone (at that commit) | — |
| `8bc8e3758248` | S478 | immutable-cell-changed | 5, 6 |
| `3d42897b6529` | S498 | cell-count changed | old row splits to 7 cells, new row 11 |

All 7 `SOURCES` ids exist at the tip, and all 3 errata `(round, kind, token)` keys exist at the tip (`probe.txt:289-319`, `id_in_tip=True` / `key_in_tip=True`), so verbatim re-append would duplicate a registry id or an errata key — the ledger's stated rationale holds independently.

## 6. Restoration arithmetic: 155 restored = 151 graded losses + 4 exempt-section lines

`verify_restore_arith.py` (exit 0):

- 18 files carry `## Restored lines (round 52)` (`###` in `SCORECARD.md:2929`; `LOG.md:2358`; all 18 in `restored-headings.txt`) totalling **155** fenced content lines.
- Base engine: **151** unheld A-corr lines, per-file counts **identical** to the restored blocks for all 17 non-SCORECARD files; `SCORECARD.md` restored 23 vs 19 unheld → **+4**.
- Those 4 are `ef76777e5fbd` (`b28cbdd7da31`, `bb9019946103`) and `42ea1204aef3` (`bf5869828bfa`, `ed5ff78ef347`), each deleted from the parent section **`## Planned`** (parent lines 53, 67, 66, 53) — i.e. inside an `exempt=` heading, hence ungraded under the preregistered simplified rule, but disclosed by the tool's origin/not-gutted exempt logic at base and therefore present in the base ledger. The build restored them verbatim; all four are held at tip, so the tip state satisfies both readings.
- Consequence for wording only: `corpus/lessons/round-52.md:12` says "The 155 lost lines of A-corr files"; under the frozen C2 grading the count of *lost* lines is 151 and 155 is the count of *disclosed* ledger rows. This does not affect the predicate (`corr_lost=0`, ledger exact) and I propose no in-place edit; if the lane ever appends a round-52 erratum, "155 disclosed (151 graded losses + 4 exempt-section lines)" is the exact phrasing.

## 7. Sensitivities and what could not be decided

- **Fence-awareness is not load-bearing at this tip.** 29 deleted parent lines lie inside a fence (all `LOG.md`); **0** deletions get a different parent section with fences ignored (`probe.txt:274-277`, `== FENCE SENSITIVITY`). A full `--fence-blind` rerun gives **byte-identical JSON** (`recompute-fenceblind.json` vs `recompute.json`, `cmp` clean): corr_lost=0, row_lost=10.
- **Second deletion detector.** `crosscheck_difflib.py` derives deletions from `difflib.SequenceMatcher` opcodes instead of git hunks: corr_lost=0, row_lost=10, **the same 10 (commit, file, sha) keys**, ledger 10/10. It finds 9 fewer deleted lines overall (6162 vs 6171) on 8 events — `83bee7faf5a7`, `33b167ecccab`, `ed135b3cb869`, `ea72c3eae4ec`, `84a81304d7b0` (LOG.md), `e246c40ec1b4` and `1e41928aba2b` (README.md), `1e41928aba2b` (consumer-registry.md), `5dacf2c70f94` (round-1.md) — cases where git shows `-old/+new` for identical text while difflib aligns it as a pure insertion. Every one of those lines is held at tip, so the loss set and the verdict are invariant. The primary engine uses git's first-parent hunk positions, as the seat spec words the diff.
- **Undecided: none.** No audited file is binary, none was ever renamed or deleted in history (`git log --diff-filter=DR --name-status -- <contract paths>` is empty), no hunk count mismatch occurred, and no deleted position fell outside its parent blob (assertions in `sections_of_patch`).
- **Not re-derived here:** the counter's eight fixtures (scenarios 1–8) exercise the frozen tool/counter pair, not the lane's line accounting; the C2 lane leg is what this seat recomputes. The counter's own run of them is `8/8` in both receipts (`c2-build.out:4-11`, `base.c2.out:3-10`), and the build receipt's `met=True` is not something I can re-verify without running the frozen counter — which my assignment excludes.

## 8. Commands, exits, artifacts

Scratch `S=/fast/scratch/hyaku/kama-r52/X7Regen`; one live clone `git clone -q --shared /home/vgpnk/Projects/shokunin/kama-shokunin "$S/lane"` (toplevel verified = `$S/lane`; HEAD is `34d82600`, every read was by explicit rev, so sibling edits in the lane worktree — which is dirty — cannot leak into these results).

```
python3 …/out/X7Regen/recompute_c2.py --repo $S/lane --tip 5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8 --out $S/recompute.json
   → exit 0, 11.1 s: corr_lost=0 row_lost=10 ledger_matched=10 (files=99 events=109 graded=5868)
python3 … --tip 9ff76b1f763512be2f554cbbfd0b2213b63b0847 --out $S/recompute-base.json
   → exit 0, 4.3 s: corr_lost=151 row_lost=10 ledger=165 graded=5867 events=107
python3 … --tip 5dacf2c7… --fence-blind --out $S/recompute-fenceblind.json
   → exit 0, 13.5 s: identical JSON
python3 …/out/X7Regen/crosscheck_difflib.py --repo $S/lane --tip 5dacf2c7… --json $S/crosscheck.json
   → exit 0, 13.1 s: corr_lost=0 row_lost=10 ledger_matched=10
python3 …/out/X7Regen/probe_details.py --repo $S/lane --tip 5dacf2c7… --engine-json $S/recompute.json
   → exit 0, 19.9 s: region table, fence sensitivity, A-row reasons, disclosed-line content
python3 …/out/X7Regen/verify_restore_arith.py --repo $S/lane --tip 5dacf2c7… --base-engine-json $S/recompute-base.json
   → exit 0, 108.6 s: 18 files / 155 restored lines; SCORECARD +4; ledger rows exact
```

No tool was installed or upgraded; `python3 3.14.8`, `git 2.56.0`. No llama-server started, no service touched, lane Git/jj state untouched (read-only `git show/log/diff/rev-list` only). Scratch removed after the receipts were copied.

**Written:**
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X7Regen.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X7Regen/recompute_c2.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X7Regen/crosscheck_difflib.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X7Regen/probe_details.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X7Regen/verify_restore_arith.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X7Regen/recompute.txt`, `recompute.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X7Regen/recompute-base.txt`, `recompute-base.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X7Regen/recompute-fenceblind.txt`, `recompute-fenceblind.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X7Regen/crosscheck.txt`, `crosscheck.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X7Regen/probe.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X7Regen/restore-arith.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X7Regen/restored-headings.txt`
