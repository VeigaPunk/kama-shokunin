# X8Rows — round 52 (lane kama): the 10 rows left in `registry/append-only-disclosures.tsv`

**Verdict:** all 10 rows must stay; restoring any of them verbatim is a new defect. The 7
`corpus/SOURCES.md` rows are refused by two frozen instruments — `sources-census.sh validate`
reports `E03 duplicate id` for every one of them (exit 1) and `sources-append-only.py` exits 2
with `duplicate id` (it refuses to grade the table); 4 of the 7 also trip `E04 duplicate
url … within scope`. The 3 `registry/report-landing-errata.tsv` rows duplicate a
`(round, kind, token)` key and re-introduce three **superseded evidence strings**, but
`report-landing-audit.py` does **not** detect the duplicate (exit 0; the defect's
`corrected_by` simply grows to two rows) — the only mechanical signal is the frozen C2
counter's ledger rule (`met=False`, `bad_disclosures=3`), so the errata half of the build's
justification rests on the registry's one-row-per-key contract plus C2, not on the audit.

Nothing in the lane was written. All mutations happened in one `git clone --shared` of the
lane under `/fast/scratch/hyaku/kama-r52/X8Rows/` (fixture identity `fx <fx@invalid>`), plus a
detached worktree of that clone; both were removed at the end. The frozen counters, tools,
preregistration and controls were read only.

## 1. Method

Scratch `S=/fast/scratch/hyaku/kama-r52/X8Rows`, `TMPDIR=$S`.

```
git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin "$S/lane"      # fixture clone
git -C "$S/lane" checkout -B fx 5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8      # the build
git -C "$S/lane" worktree add --detach "$S/base" 5dacf2c7…                    # clean 2nd tree
git -C "$S/lane" rev-parse --show-toplevel   -> /fast/scratch/hyaku/kama-r52/X8Rows/lane
git -C "$S/base" rev-parse --show-toplevel   -> /fast/scratch/hyaku/kama-r52/X8Rows/base
```
Every commit in those two trees was made with `-c user.name=fx -c user.email=fx@invalid` after
that toplevel check. The lane at `…/kama-shokunin` was only read (`git show`, `git diff`,
`git log`); `git -C <lane> status` was never touched.

Recovery (`recover_rows.py`, this directory): for each ledger row `(commit c, file f,
line_sha256 h, count n)` read `git diff -U0 c^ c -- f`, take the `-` lines, and match
`sha256(key(line))` with `key = bytes minus one trailing CR` — the key
`tools/append-only-audit.py:316-320` defines. Result: **10/10 rows matched exactly one deleted
line each, 0 unmatched** (`rows.json`, `recover_rows.py` exit 0). The recovered bytes are kept
as hex in `rows.json` and were inserted with `bytes.fromhex`, so the re-appends are byte-exact.

## 2. The 7 `corpus/SOURCES.md` rows (A-row file, region `*`)

Recovered line = the `-` line of the deleting commit; "tip row" = the registry row that holds
the same id at the build, with the immutable cells (`source kind tier scope anchor teaches
opened`, `tools/sources-append-only.py:75-77`) compared cell by cell (`cells.json`).

| ledger ln | deleting commit (round) | id | parent line | deleted sha256 | what the tip row at that id now says | census | guard |
|---|---|---|---|---|---|---|---|
| 2 | `ccc4bb31267f` (r16) | **S041** | 53 | `e0580c97f53a` | same own-work source; `anchor` re-pinned (receipt window `14:06:27.859Z–14:06:27.974Z`, port 37527, tool sha256) and `teaches` rewritten (the `/v1/models` 503 loading envelope) | E03 | exit 2 `duplicate id S041` |
| 6 | `54c6f4fe070c` (r31) | **S192** | 440 | `3b584ff21379` | **different source entirely**: id now holds the OpenAI Chat Completions `response_format` row; `source kind scope anchor teaches opened used-by` all differ | E03 + E04 | exit 2 `duplicate id S192` |
| 7 | `54c6f4fe070c` (r31) | **S189** | 437 | `d7abbe77f01e` | same source (`server-common.cpp#L1530`); `scope` reworded to "…before the schema keeps only what it declares, the path by which undeclared OpenAI-stan…" | E03 | exit 2 `duplicate id S189` |
| 8 | `54c6f4fe070c` (r31) | **S191** | 439 | `de9562c37189` | id now holds the `#L64` `n`-alias row (the old line's subject moved to S190) | E03 + E04 | exit 2 `duplicate id S191` |
| 9 | `54c6f4fe070c` (r31) | **S190** | 438 | `f5ca7c2bbee4` | id now holds the `#L47` `max_tokens`-alias row (the old line's subject moved to S189) | E03 | exit 2 `duplicate id S190` |
| 10 | `8bc8e3758248` (r42) | **S478** | 231 | `bcd910486aa5` | same source; `anchor` corrected (`get_kv_cache_capacity` line 2308 `return int(…)`) and `teaches` corrected (capacity derivation) | E03 + E04 | exit 2 `duplicate id S478` |
| 11 | `3d42897b6529` (r50) | **S498** | 251 | `d0c8b17e8055` | same source; the deleted line has **7 backticks (odd)** from the quoted `` (`) ``/`` (~) `` snippets and a `full page sha256` note; the tip line has 4 | E03 + E04 | exit 2 **`unterminated table row (no closing pipe)`** |

### 2.1 Combined re-append (all 7, history order, after the `S500` row at line 253)

Command (fixture commit `71699a59036b038c35254022e4251f4b82708151`):

```
bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --file "$S/lane/corpus/SOURCES.md"
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/sources-append-only.py \
        --from 9ff76b1f763512be2f554cbbfd0b2213b63b0847 --to HEAD --repo "$S/lane"
```

* baseline at the build (`census-base.out`): exit **0**, last line `file\tok\t…/corpus/SOURCES.md`
* after the re-append (`census-dup.out`): exit **1**, **13** new lines — 7 × `E03 duplicate id`,
  4 × `E04 duplicate url … within scope` (S192, S191, S478, S498), 1 new `W04` (S190) and a
  second `W04` for S189 (its first one pre-exists). `census-base.out` has zero `E0[34]`.
* guard baseline at the build (`append-only-base.out`): exit **0**, `added S500 (allowed)` /
  `no append-only violations`
* guard after the re-append (`append-only-dup.out`): exit **2**,
  `error: HEAD:corpus/SOURCES.md:254: duplicate id S041` — the table becomes ungradeable, so
  the append-only question itself can no longer be answered (`sources-append-only.py:48,290`).

### 2.2 Per-row isolation

Each row appended alone onto the build blob, committed, both instruments run
(`perrow.json`; every row: census exit 1, guard exit 2):

| row | census codes | guard message |
|---|---|---|
| S041 | E03 | `duplicate id S041` |
| S192 | E03, E04 | `duplicate id S192` |
| S189 | E03 | `duplicate id S189` |
| S191 | E03, E04 | `duplicate id S191` |
| S190 | E03 | `duplicate id S190` |
| S478 | E03, E04 | `duplicate id S478` |
| S498 | E03, E04 | `unterminated table row (no closing pipe)` |

**Verdict per row: keep the disclosure, do not restore.** For all 7 the id is still occupied
at the tip, so a verbatim re-append is a duplicate-id defect that both frozen instruments
refuse (`scripts/sources-census.sh:641`; `tools/sources-append-only.py:290`, exit 2 by
`:41-49`). The four r31 rows are worse than a duplicate id: the ids were **remapped** in place
(S190→S189, S191→S190, S192→S191, with S192 given to the OpenAI row), so the restored line
also asserts the old subject under the wrong id and, for S192/S191/S478/S498, reproduces the
same URL under the same `scope` → `E04` (`scripts/sources-census.sh:648-649`). S498 is a
special case: its old bytes are *unparseable* by the guard's own cell splitter
(`split_cells()` returns `None`; `tools/sources-append-only.py:257`), which is exactly the
round-50 defect the in-place edit fixed — restoring it would re-break the parser rather than
merely duplicate an id.

## 3. The 3 `registry/report-landing-errata.tsv` rows (rule `A`, region `*`)

Key = `(round, kind, token)` (`tools/report-landing-audit.py:34-40,578-590`). Each deleted line
was replaced in place by a row with the **same key** and a corrected `evidence` cell
(`cells.json`):

| ledger ln | key | deleted evidence (restoring it re-asserts) | tip evidence (the correction) |
|---|---|---|---|
| 3 | `20 landed-omitted 33a67778…b56c` | "…and build evidence; **absent from the whole report**" | "…**not cited by full hash or >=7-hex prefix anywhere in the report (only its 25-hex tail survives inside the line-7 splice)**" |
| 4 | `20 landed-omitted 0957ce61…d2c7` | "…**cited only in Work performed line 10 and the measurement table**, not in Landed changes" | "…**cited by full hash at Work performed line 10 only (line 7 carries the corrupted splice)**…; **the measurement table cites 9add96e4, not 0957ce61**" |
| 5 | `20 unresolved-full-hash 0957ce61…d13d` | "…splices the **first 16 hex** … with the **last 24 hex**…" | "…splices the **first 15 hex** … with the **last 25 hex** …" |

All three are factual corrections (the 15/25 split is arithmetic; the other two narrow an
over-broad "absent"/"only" claim). Re-appending them verbatim duplicates the key **with
contradictory evidence**, i.e. the registry would say two different things about one defect.

### 3.1 What the audit actually does with the duplicate — measured

```
python3 …/tools/report-landing-audit.py --lane-repo "$S/base" --fleet-repo …/shokunin \
        --branch HEAD --rounds 20 --json
```

* baseline (`audit-r20-base.json`): exit **0**, `defects 5, corrected 5, errata_rows 9,
  errata_unmatched 0, errata_invalid 0`; `corrected_by` = `[3] [4] [5] [6] [7]`.
* after the 3-line re-append (fixture commit `12d93869aa2d4f7612f8c8ab17ed6398b0f30a8c`,
  `audit-r20-dup.json`): exit **0**, `errata_rows 12`, `errata_unmatched 0`,
  `errata_invalid 0`, and `corrected_by` = `[3, 14] [4, 12] [5, 13]` — every duplicate row is
  accepted as a second correction of the same defect (`apply_errata` matches on
  round/kind/token and keys `unmatched` by **line number**, `:610-620`; `invalid` only checks
  that the correction resolves, `:654`). The audit has no duplicate-key check at all.

So the audit is **not** a guard for this half. What does fail is the frozen C2 counter and the
v6 tool's disclosure leg (`c2-errata-dup.out`, `round52-append-restore-check.py:476-480`):

```
tip=12d93869aa2d4f7612f8c8ab17ed6398b0f30a8c
fixture=1 lane=0 scenarios=8/8 corr_lost=0 row_lost=7 disclosed=10 met=False
detail: lane: 1471344b4c8b registry/report-landing-errata.tsv: own unheld 0 ledger 3 (3 keys differ)
detail: lane: tool definition v6 threshold 1 exit 1 {... 'bad_disclosures': 3 ...}
```

Restoring the three lines makes the three ledger rows name lines that are now **held**, so
`ledger == unheld key for key` fails and the tool reports 3 bad disclosures. Dropping the rows
instead leaves the duplicate key. That is the real dilemma, and it is mechanical.

The same dilemma holds for the SOURCES half (`c2-sources-dup.out`, tree `71699a5903…`):
`row_lost=3 disclosed=10 met=False`, four events with `own unheld 0 ledger 1/4/1/1`,
`bad_disclosures: 7`.

**Verdict per row: keep the disclosure, do not restore.** The duplicate key itself is a real
registry defect (two rows per corrected defect, contradictory evidence), but it is invisible
to `report-landing-audit.py`; only C2's ledger rule and the tool's disclosure leg catch the
restoration. A future round must not cite the audit as evidence that the errata half is safe.

## 4. Calibration findings

1. **`report-landing-audit.py` silently absorbs duplicate errata keys.** Proven above: exit 0,
   `errata_rows 9 → 12`, `corrected_by` grows, no `errata-unmatched`/`errata-invalid`. The
   build's phrase "would duplicate … an errata key" is true of the registry but is not backed
   by that tool. Proposed (not applied — tools are frozen): a `parse_errata` check that a
   `(round, kind, token)` triple occurs once, reported as `errata-duplicate`, would make the
   claim mechanical; the one-line change is at `tools/report-landing-audit.py:578-590`.
2. **`E04` vs `W04` is decided by the `scope` cell, not the URL.** S189/S190 got `W04`
   (warning, exit unchanged) while S192/S191/S478/S498 got `E04` (error) purely because their
   deleted `scope` text is byte-equal to the tip row's. A duplicate id is therefore an error in
   all 7 cases, but the URL-scope error is 4 of 7 — worth stating precisely.
3. **S498 is a parse defect, not a duplicate-id defect.** `split_cells()` returns `None` on its
   odd backtick parity (7 vs 4), so the guard's first complaint about that line is
   `unterminated table row (no closing pipe)`. Its duplicate-id defect is real but unreachable
   behind the parse error; census (different parser) still reports `E03`+`E04` for it.

## 5. Risks / limits

* `row_lost` in the C2 output is the counter's total unheld count over A/A-row files, not a
  count of stale ledger rows: on the errata tree it is 7 (the still-disclosed SOURCES lines)
  and on the SOURCES tree it is 3 (the still-disclosed errata lines). The failure signal is the
  `keys differ` detail plus `bad_disclosures`; do not read `row_lost` alone.
* The per-row fixture commits lived in scratch and are deleted with it; the commands above
  reproduce them (`insert_rows.py` + `bytes.fromhex` of `rows.json`). The recovered parent line
  numbers are `git diff -U0` old-file positions.
* Nothing here re-tests C1; no counter, tool, preregistration or control was modified; no
  llama-server was started (no process to tear down).
* `report-landing-audit.py` was run with `--lane-repo` pointed at a worktree of a `--shared`
  clone; the docstring states alternates still resolve as local, and the run reached the same
  verdict as the lane's own battery (`errata_rows 9`, clean at round 20).

## 6. Files in this directory

| file | what it is |
|---|---|
| `recover_rows.py`, `rows.json` | the 10 recovered deleted lines (hex + text), matched by the frozen key |
| `compare_cells.py`, `cells.json` | deleted row vs the tip row at the same key, cell by cell |
| `insert_rows.py`, `perrow.json` | byte-exact re-append into a fixture tree; per-row census/guard results |
| `census-base.out`, `census-dup.out` | census `validate` at the build and after the 7-row re-append |
| `append-only-base.out`, `append-only-dup.out` | `sources-append-only.py --from 9ff76b1f --to HEAD` both ways |
| `audit-r20-base.json`, `audit-r20-dup.json` | `report-landing-audit.py --rounds 20` both ways |
| `c2-sources-dup.out`, `c2-errata-dup.out` | the frozen C2 counter on each restoration tree |

## 7. Exact commands (all exit codes as reported)

```
python3 …/out/X8Rows/recover_rows.py <lane> 5dacf2c7… <out>/rows.json          # 0  rows=10 all_matched=True
bash scripts/sources-census.sh validate --file $S/base/corpus/SOURCES.md       # 0  (build baseline)
bash scripts/sources-census.sh validate --file $S/lane/corpus/SOURCES.md       # 1  7 E03, 4 E04, 2 W04
python3 …/tools/sources-append-only.py --from 9ff76b1f… --to 5dacf2c7… --repo $S/base   # 0  added S500 (allowed)
python3 …/tools/sources-append-only.py --from 9ff76b1f… --to HEAD --repo $S/lane        # 2  duplicate id S041
python3 …/tools/report-landing-audit.py --lane-repo $S/base --fleet-repo … --branch HEAD --rounds 20   # 0 (base), 0 (dup)
python3 …/tools/round52-append-restore-check.py --repo $S/lane --tip 71699a59… --scratch $S   # 1  met=False
python3 …/tools/round52-append-restore-check.py --repo $S/base --tip 12d93869… --scratch $S   # 1  met=False
```
