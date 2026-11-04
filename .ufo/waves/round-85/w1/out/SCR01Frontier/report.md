# SCR01Frontier — round85 author-side source and calibration report

## Behavior and findings

Axes: **calibration + operability**. This seat independently fetched both assigned public documents, retained full response bodies and headers, and drafted the two registry rows and Gate/Mistakes/erratum/criterion fragment. No claim admission or score change.

- CommonMark0.31.2 §4.2: HTTP200, 514698 bytes, sha256 `c85f56cc2101f761cc94215c677cd2c7c1ecca9c47be016479fdfe718af60f0d`. Located 16-word quotation at fetched HTML lines1613–1614: “The opening # character may be preceded by up to three spaces of indentation.” Examples68–69 distinguish 1/2/3-space headings from four-space code. This supports the narrow heading rule, not a complete CommonMark parser claim.
- Exact b7200 examples/server README URL: HTTP404, 14 bytes, sha256 `d5558cd419c8d46bdc958064cb97f963d1ea793866414c025906ec15033512ed`. Actual complete body is “404: Not Found”. Reject exact ref/path only; flip is a retrievable revision-specific document at that path, not an unperformed alternate-path fetch.
- Both curl commands exited0 (no `--fail`); HTTP404 is not a transport error. Access date for both:2026-11-04. Exact commands and outcomes: `commands.md`.
- Frozen revision `7d3c987c0e3a6ee62673c18c26ecdd22f39e5cdd`: S576/S577 each have zero registry rows. Concurrent working tree already contains both and KQ137. L1 clarified independently opening/appending the same IDs and reported scratch census0; that is L1-reported, not this seat's validation evidence. Do not append duplicate rows or a second KQ137. `append.tsv` and criterion text are candidate refinements/critique only.
- R84V5 provenance checked by reading retained receipt: `.ufo/waves/round-84/measured/after/c2-red.out` records `--no-corrections` at `3e93febb0f40955b08dc80367e8ef658eaccdfd6`, summary claims8/mismatches6/corrected0/unbacked6, EXIT=1. The current before-directory listing lacks the promised `red-selfrecord.out`. This is a citation/provenance erratum, not evidence of the promised historical uncorrected-tree run. Frozen round84 plan left untouched.

## Gates and limits

Read complete round85 plan (re-read truncated line21 raw), frozen counter, authorization rules and required skills. Observed revision is the freeze commit; counter sha256 `e550a24786d7c3e073c549a8dcb03d456579696ba92a7f2a15ea2e7c04bedca9`. Read-only ID check completed exit0. Existing source census/validate receipts were read, not rerun. No counter, gate-control, build, lint, test, selftest, or schema-validation execution by this seat. Integration and execution judgments remain L1/outside-closure responsibilities. No tools installed/updated; no clones, commits, pushes, services, secrets, live endpoint samples, or corpus mirrors. Owned scratch was explicitly created; all fetch commands set TMPDIR there; `rmdir /fast/scratch/hyaku/kama-r85/SCR01Frontier` completed exit0 after receipts were retained directly in output.

## Touched surfaces and artifacts

Only `.ufo/waves/round-85/w1/out/SCR01Frontier/` was written (plus created/removed owned scratch):

- `append.tsv`: two candidate Markdown registry rows, despite filename extension.
- `lesson-fragment.md`: independent Gate, Mistakes, append-only R84V5 erratum and same-ID KQ137 criterion proposal citing round85 lesson.
- `commands.md`: exact executed commands, observed outcomes/revision, provenance limits.
- `commonmark.html`, `commonmark.headers`: independently fetched primary source.
- `rejected-readme.txt`, `rejected-readme.headers`: independently fetched actual404 evidence.
- `report.md`: this report.

## Conflicts, verbatim

- Contract: “Write ONLY /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-85/w1/out/<YOUR-NAME>/” and “write at /home/vgpnk/Projects/shokunin/kama-shokunin/<that path> only if inside your owned dir.”
- Trailer: “Report: write your scoped findings to .ufo/waves/round-85/w1/SCR01Frontier.md”.

Resolution: the trailer path is outside ownership; no write there. Report retained at owned path below. No product code or judge edits. ID collision is concurrent integration, not a frozen-ID conflict; L1 explicitly confirmed no duplicate rows.

## Self-evaluation (not admission)

Accuracy4: byte receipts and exact historical command distinguish observed fetches from read evidence; source-origin authentication beyond HTTPS is not established. Completeness4: assigned artifacts delivered, integration/schema validation not executed by this seat. Clarity4: collision warnings prevent treating candidate rows as duplicate append instructions. Actionability4: L1 can use receipts/critique directly; merge wording remains integration-owned. Conciseness4: separate command ledger preserves audit detail but repeats key provenance. Overall4.0. Highest-impact improvements already applied: actual404 body retained, historical-red provenance limited, duplicate-ID hazard explicit. Expected user agreement: yes, bounded to author-side evidence.

Report: .ufo/waves/round-85/w1/out/SCR01Frontier/report.md
