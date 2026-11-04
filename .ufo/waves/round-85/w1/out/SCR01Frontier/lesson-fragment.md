## Gate — independent SCR01Frontier source opens

Axes: calibration and operability; this seat supplies calibration provenance only. Both URLs were independently opened by this seat on 2026-11-04; these are author-side proposed decisions, not outside admission.

| ID | URL | Access date | HTTP / bytes | Located verbatim quote (≤25 words) | Proposed decision / provenance |
|---|---|---|---|---|---|
| S576 | https://spec.commonmark.org/0.31.2/#atx-headings | 2026-11-04 | 200 / 514698 | §4.2, fetched HTML lines 1613–1614: “The opening # character may be preceded by up to three spaces of indentation.” (16 words) | mined/A/spec, used-by corpus/lessons/round-85.md; sha256 c85f56cc2101f761cc94215c677cd2c7c1ecca9c47be016479fdfe718af60f0d |
| S577 | https://raw.githubusercontent.com/ggml-org/llama.cpp/b7200/examples/server/README.md | 2026-11-04 | 404 / 14 | Complete actual response body, line 1: “404: Not Found” (3 words) | rejected/docs/A, exact path only; sha256 d5558cd419c8d46bdc958064cb97f963d1ea793866414c025906ec15033512ed; flip: a retrievable revision-specific document at that path |

Retained raw bodies and response headers live beside this fragment in `.ufo/waves/round-85/w1/out/SCR01Frontier/`. curl returned exit 0 for both requests: HTTP404 is an observed response status, not curl failure (no `--fail`). No alternate URL was fetched. CommonMark example 68 demonstrates 1/2/3-space headings; example 69 demonstrates four-space indented code. The quotation decodes the HTML `<code>#</code>` markup without changing its text.

Identifier caution: S576/S577 were absent in the frozen revision 7d3c987c0e3a6ee62673c18c26ecdd22f39e5cdd, but already occupied in the concurrently edited working registry when inspected. `append.tsv` is a candidate replacement for those same rows, not authorization to append duplicate IDs. KQ137 is also already occupied in the working QUALITY file; the proposal below refines that same criterion, not a second row.

## Mistakes — scoped draft

| Type | Concrete evidence | Superseded criterion / gap | Proposed remedy |
|---|---|---|---|
| backing-token / heading escape | Round84 outside closure R84V4 identifies stale current authority wording; round85 frozen plan C1 records token-only and 0–3-space correction-heading controls | KQ136 named current authority cells, but tokens elsewhere do not establish the actual cell value | KQ137 below scopes evaluation to the first live Current authority paragraph and calibration row in the first Axes section; S576 grounds 0–3-space correction-heading recognition. This seat did not execute controls or admit C1. |
| reference-drift | Round84 plan lines 94–95 cites absent `.ufo/waves/round-84/measured/before/red-selfrecord.out`; retained `.ufo/waves/round-84/measured/after/c2-red.out` lines 1–2 names revision 3e93febb0f40955b08dc80367e8ef658eaccdfd6 and `--no-corrections` | Frozen-plan citation did not bind the promised historical uncorrected tree to the retained red receipt | Append this erratum without rewriting the frozen plan: the actual receipt is an explicit no-corrections red control, not a historical uncorrected-tree run. Its retained summary is claims=8 mismatches=6 corrected=0 unbacked=6, EXIT=1; those are read receipt values, not a new execution. |

### R84V5 append-only citation/provenance erratum

The frozen round84 plan's `measured/before/red-selfrecord.out` pointer is absent from the current before-receipt directory listing. Actual `.ufo/waves/round-84/measured/after/c2-red.out` records `python3 tools/round84-selfrecord-round83.py --repo . --no-corrections` at `3e93febb0f40955b08dc80367e8ef658eaccdfd6`, not execution against the promised historical uncorrected tree. The retained receipt prints `SELFRECORD_R83 claims=8 mismatches=6 corrected=0 unbacked=6`, `EXIT=1`. This corrects citation and provenance only; it supplies no missing historical run and no retrospective claim admission. See `corpus/lessons/round-84-verifier-spotcheck.md` R84V5.

### Proposed KQ137 — same occupied ID, integration draft

| ID | Admit only when | Reject or limit when | Motivating lesson |
|---|---|---|---|
| KQ137 (operationalizes KQ136 for the two frozen cells) | Evidence is read from the declared first live Current authority paragraph and calibration row in the first Axes section. Unrelated text and dated correction restatements cannot repair stale live cells. Controls cover unrelated correct witnesses and 0/1/2/3-space correction blocks remaining red, genuine repaired cells passing, and four-space indentation not being treated as an ATX heading (S576). | Witness-token presence substitutes for cell repair; column-zero-only heading exclusion accepts indented correction witnesses; a finite two-cell result is generalized to a whole-record census or complete CommonMark parser. Require retained control receipts before claiming execution. | `corpus/lessons/round-85.md` §Mistakes and §Gate; S576; frozen `.ufo/waves/round-85/count.py` C1. |

No corpus mirror, endpoint sampling, source-origin guarantee, whole-record calibration claim, C2 execution claim, or new score is supplied by this fragment.
