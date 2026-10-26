# K2Binding — round 49 seat report: v4 binding audit of registry/append-only-contract.tsv at 74558c71

**Verdict: 9 of 10 contract rows are bound by lines that genuinely declare their rule; the `corpus/lessons/*.md` row (contract line 7) binds by coincidence — `corpus/QUALITY.md:143` is a KQ26 criterion row, not a declaration of the lessons rule, and its sentence treats "filed lessons" and "append-only records" as separate categories. Proposed re-anchor to a new declarative line in `corpus/README.md` (demonstrated bound with the v4 tool, exit 0).**

Measured at lane commit `74558c71c38ceaeace15fd4cf8aa9d84977584b1` (build), on my shared scratch clone `/fast/scratch/hyaku/kama-r49/K2Binding/lane` (read-only use of the lane). The frozen C2 counter passes on this clone: `fixture=1 lane=1 scenarios=8/8 met=True` (receipt: `c2-counter-receipt.txt`). The contract is unchanged between base `438127bc` and tip (verified: `git diff 438127bc..74558c71 -- registry/append-only-contract.tsv` prints nothing), so the v4 row set is the round-48 set.

---

## 1. Per-row audit (contract line, declared_at line, region pointer line, v4 mechanical bind, verdict)

Method: the counter's own v4 binder is replicated verbatim (`token`/`says`/`binds` from `tools/round49-append-audit-v4-check.py:107-130`) against the tip blobs; the region pointer line is read from the contract's `region` cell. Full table: `row-audit.tsv` (same directory). Quotes below are exact tip lines.

| # | path | rule | declared_at | region | v4 bind | declared_at line (tip) | region pointer line (tip) | verdict |
|---|---|---|---|---|---|---|---|---|
| 2 | LOG.md | A-corr | README.md:16 | * | BOUND | ``- `LOG.md` — append-only round log: the evidence that motivated each change`` | — | TRUE declaration |
| 3 | SCORECARD.md | A-corr | corpus/README.md:761 | exempt=## Axes\|## Planned\|## Retired\|## Saturation\|## Capabilities@SCORECARD.md:6 | BOUND | ``append-only (SCORECARD.md, LOG.md, corpus/QUALITY.md, corpus/README.md, corpus/SOURCES.md)`` | SCORECARD.md:6: "The `## Axes` table, §Planned, §Retired, §Saturation and §Capabilities below are re-derived from the tree by `tools/round42-selfdesc-reconcile.py` … and kept current …" | TRUE declaration (shared line) |
| 4 | corpus/QUALITY.md | A-corr | corpus/README.md:761 | * | BOUND | same line as #3 | — | TRUE declaration (shared line) |
| 5 | corpus/README.md | A-corr | corpus/README.md:761 | * | BOUND | same line as #3 (self-match: declaring file == row path, non-wildcard, allowed by v4) | — | TRUE declaration (self + shared line) |
| 6 | corpus/SOURCES.md | A-row | SKILL.md:578 | * | BOUND | ``| SOURCES append-only guard | gate: `python3 tools/sources-append-only.py --from A --to B [--json]` | 0 no violation, 1 removed row or a changed cell outside `status`/`recheck`/`used-by`, … |`` | — | TRUE declaration of the guard (instrument-mediated) |
| 7 | corpus/lessons/*.md | A-corr | corpus/QUALITY.md:143 | * | BOUND | ``| KQ26 | Corrections to filed lessons, reports and append-only records are appended with the superseded text/revision named; … |`` | — | **COINCIDENCE — KQ26 criterion, not a declaration** |
| 8 | registry/history/DELTA.md | A | registry/history/DELTA.md:3 | * | BOUND | ``# Append-only; one line per row-field change between snapshots, in`` | — | TRUE self-declaration |
| 9 | registry/report-landing-errata.tsv | A | registry/report-landing-errata.tsv:1 | * | BOUND | ``# Append-only corrections for defects found by tools/report-landing-audit.py … (round 21).`` | — | TRUE self-declaration |
| 10 | corpus/knowledge/consumer-registry.md | A-corr | corpus/knowledge/consumer-registry.md:30 | only=## Errata@…:30 | BOUND | ``## Errata — 2026-10-14 re-census (append-only; rows below keep their round-1 text)`` | same line (names the `## Errata` prefix) | TRUE self-declaration |
| 11 | corpus/knowledge/error-is-not-a-verdict.md | A-corr | corpus/knowledge/error-is-not-a-verdict.md:173 | only=## Round24@…:173 | BOUND | ``Append-only; the round24 sections above stand and nothing here repeats them.`` | same line (names the `## Round24` prefix; the file's `## Round24 — isolation is not evidence availability` heading sits at line 82) | TRUE self-declaration |

All 10 rows also pass the tool's own declaration checks at tip: `tools/append-only-audit.py` at 74558c71 exits 0 with `bad_declarations=0` and every declaration `ok=True` (run A, below). The exempt pointer SCORECARD.md:6 names all five head titles and carries `re-derived`; both `only=` pointers are the self-declaring lines and satisfy the v4 `only` pointer check.

## 2. The flagged row: `corpus/lessons/*.md` @ `corpus/QUALITY.md:143`

`corpus/QUALITY.md:143` is the **KQ26 criterion row**. Its "Admit only when" cell reads:

> Corrections to filed lessons, reports and append-only records are appended with the superseded text/revision named; retrospective reconstructions are labelled with their actual creation round and what they cannot prove.

This is not a declaration that lesson files are append-only; it is a quality criterion about *how corrections are made*, and it applies jointly to three listed categories — **filed lessons, reports and append-only records**. The predicate ("are appended with the superseded text/revision named") governs corrections in all three categories; "append-only records" is listed as a category *distinct from* "filed lessons". The line therefore does not assert that lessons are append-only — if anything it presupposes the distinction. The v4 binder accepts it only because (a) the wildcard row token is the parent directory `lessons`, which occurs as a whole word in "filed lessons", and (b) "append-only" occurs in the separate category phrase "append-only records", with no negation within three words. Both words are present; neither predicates the rule. That is exactly the coincidence class v4's whole-word rule was meant to narrow but cannot catch, because the binder checks presence, not predication.

Confirmed: no other line in the repo (outside `.ufo/`, `tools/`, `tests/`) states the lessons rule either. The exhaustive intersection of `append-only`/`append only` with `lessons` at tip yields only content-level or meta statements: `LOG.md:1231` (one S051 correction inside round-18.md), `SCORECARD.md:2482` and `corpus/README.md:1073` (meta references to the re-anchor), `corpus/README.md:521` ("append-only records in `corpus/lessons/round-33.md`" — a content claim about one lesson, rejected as an anchor), `corpus/README.md:239` (table row about round-17.md's contents), `corpus/lessons/round-27-verifier-spotcheck.md:184` (lists the five append-only files — lessons not among them), `corpus/lessons/round-47-verifier-spotcheck.md:91` (records that lessons entered the audited set — a report, not a norm), and `corpus/QUALITY.md:41/82/123/143`. The previous anchor `corpus/lessons/round-23.md:100` ("are append-only.") is demonstrated unbound under v4 (run C): the wildcard row cannot self-bind and the line lacks the token `lessons`.

## 3. Proposed fix (better anchor for the lessons row)

Since no existing line declares the rule, add one declarative line and re-anchor. Append to the end of the append-only self-description paragraph in `corpus/README.md` (current line 771, "… the default five-file set is the tool's, not yet the lane's full declared contract." — an additions-only change, consistent with `corpus/README.md`'s own A-corr rule):

```
Lesson files under `corpus/lessons/` are append-only as the `A-corr` contract row declares: filed lessons stay, and corrections are appended with the superseded text named (KQ26).
```

and change contract row 7's `declared_at` from `corpus/QUALITY.md:143` to `corpus/README.md:772` (the new line). This line predicates the rule (token `lessons` whole word + `append-only`, no negation, no wildcard self-declaration), sits next to the existing declaration cluster, and survives the v4 binder for the right reason.

**Demonstration** (scratch clone, demo commit `d9b9013183626569e3ba6fd06761a6bf637f6de5` = tip + the one README line; the clone is scratch-only, no lane change):

- Run A — current contract at tip: `python3 tools/append-only-audit.py --repo <clone> --to 74558c71 --json` → exit 0; summary `commits=319 files=92 events=5 restored=5 partial=0 unrestored=0 ungraded_lines=82 regressed=0 bad_declarations=0`; all 10 declarations `ok=True`.
- Run B — proposed contract (`contract.proposed.tsv`, only cell changed: lessons row `declared_at` → `corpus/README.md:772`) at the demo commit: exit 0; summary `commits=320 files=92 events=5 restored=5 partial=0 unrestored=0 ungraded_lines=82 regressed=0 bad_declarations=0`; all declarations `ok=True`. The proposed anchor binds; events and graded mass are unchanged.
- Run C — old anchor (`contract.oldanchor.tsv`: lessons row `declared_at` → `corpus/lessons/round-23.md:100`) at tip: exit 1; `bad_declarations=1`; the tool reports `declaration corpus/lessons/*.md corpus/lessons/round-23.md:100 unbound: declared_at corpus/lessons/round-23.md:100 does not say append-only for corpus/lessons/*.md`. This is the round-48 K1Binding mechanism the build already had to re-anchor around, re-verified.

## 4. Other rows — judgement

- **#2 LOG.md (README.md:16)**: genuine, dedicated, prose declaration. No change.
- **#3–5 (corpus/README.md:761)**: the line is the continuation of "sets the five files the lane treats as append-only (SCORECARD.md, LOG.md, corpus/QUALITY.md, corpus/README.md, corpus/SOURCES.md)" — a genuine statement of the five-file set, satisfying all three rows (README via non-wildcard self-match; SCORECARD/QUALITY via whole-word tokens). Weakness (not a defect): three rows hang on one continuation line of a historical paragraph; if the paragraph is ever reworded, all three anchors move together.
- **#6 SOURCES (SKILL.md:578)**: this row declares the guard instrument and its exact verdict semantics ("0 no violation, 1 removed row or a changed cell outside `status`/`recheck`/`used-by`"), which mirror the row's own rule and carve-outs; I rate it a genuine (instrument-mediated) declaration, not coincidence. Do **not** switch it to KQ22 (`corpus/QUALITY.md:123`): KQ22's only `append-only` token sits inside its reject cell describing a misuse ("a census exit 0 … is offered as append-only evidence"), so that anchor would be *more* coincidental, not less.
- **#8–11**: true self-declarations; region pointers verified.

## 5. Evidence (commands, outputs, exit codes)

```
$ python3 tools/round49-append-audit-v4-check.py --repo <clone> --tip 74558c71c38ceaeace15fd4cf8aa9d84977584b1 --scratch $S --out …/c2-counter-receipt.txt
tip=74558c71c38ceaeace15fd4cf8aa9d84977584b1
fixture=1 lane=1 scenarios=8/8 met=True        (exit 0)
$ python3 tools/append-only-audit.py --repo <clone> --to 74558c71 --json   # tool archived from tip
exit=0  summary: commits=319 files=92 events=5 restored=5 partial=0 unrestored=0 ungraded_lines=82 regressed=0 bad_declarations=0
$ python3 tools/append-only-audit.py --repo <clone> --to d9b90131… --contract contract.proposed.tsv --json
exit=0  summary: commits=320 files=92 events=5 restored=5 partial=0 unrestored=0 ungraded_lines=82 regressed=0 bad_declarations=0
$ python3 tools/append-only-audit.py --repo <clone> --to 74558c71 --contract contract.oldanchor.tsv --json
exit=1  bad_declarations=1  declaration corpus/lessons/*.md corpus/lessons/round-23.md:100 unbound
```

Raw outputs: `runA.tip.current.json`, `runB.proposed.json`, `runC.oldanchor.json`, `contract.tip.tsv`, `contract.proposed.tsv`, `contract.oldanchor.tsv`.

## 6. Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/K2Binding.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/K2Binding/row-audit.tsv`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/K2Binding/c2-counter-receipt.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/K2Binding/runA.tip.current.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/K2Binding/runB.proposed.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/K2Binding/runC.oldanchor.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/K2Binding/contract.tip.tsv`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/K2Binding/contract.proposed.tsv`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/K2Binding/contract.oldanchor.tsv`
