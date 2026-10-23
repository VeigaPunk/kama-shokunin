# ScribeKQ37Qualification — audit report

## Behavior
Drafted an append-only `## Round 28 qualification -- KQ37` block. It supersedes the S136 parenthetical with the exact S139 SOURCES row; corrects the clause-(d) explanation to include the joined-literals candidate; scopes the 3/17 result and marks E26-14 lexical coincidence as an open boundary-design question; and states the unbuilt F3 file/model-content leg requirement for future signature counters. The draft also distinguishes this round's request-field C1 claim and its control artifacts from signature-counter evidence.

## Gates and provenance
- Read the round-28 preregistration first. Checked every cited line range listed at the end of `out/ScribeKQ37Qualification/qualification.md` against its source file, including the exact S139 row and the round-27 counter implementation lines.
- The A3 tip artifact records this command and result (not run by this scribe): `# flock .../counter.lock timeout 900 /usr/bin/python3 .ufo/waves/round-27/count-c1.py --out c1-tip-receipt.json`; stdout: `registered 0 counted 0 target 15 met False not-counted []`; `exit=0` (`.ufo/waves/round-27/a3/c1-tip.out:1-4`). The round-27 lesson states C1 was withdrawn before data and no data seat was dispatched (`corpus/lessons/round-27.md:15-25`).
- The round-28 controls index reports five control classes without an evidentiary receipt; these are recorded as HOLDs, not receipts (`.ufo/waves/round-28/controls/HOLDS.md:18`). The report therefore describes the current artifacts as per-class control records (receipts plus holds), not a complete future signature-counter control set.
- Only shell command run for this task: `timeout 10 mkdir -p /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/w1/out/ScribeKQ37Qualification` — returned no output. Source inspection used the `read` and `grep` tools. No install/update was made.

## Touched surfaces
Created only:
- `.ufo/waves/round-28/w1/out/ScribeKQ37Qualification/qualification.md` — proposed append-only qualification text; not integrated into `corpus/QUALITY.md`.
- `.ufo/waves/round-28/w1/advice/ScribeKQ37Qualification.md` — this audit report.

Read-only source surfaces included `corpus/QUALITY.md`, `corpus/SOURCES.md`, `corpus/knowledge/echo-discriminating-counters.md`, `corpus/lessons/round-27.md`, the round-27 spot-check, counter and boundary-probe artifacts, and round-28 preregistration/control records.

## Findings and limits
- The KQ37 row still contains the superseded S136 wording in its existing source; this seat drafted replacement wording only.
- Clause (d) accepts a joined-literals candidate; this is weaker than a one-literal boundary condition. The draft cites the implementation and the knowledge entry.
- The 3/17 boundary cost is limited to exact, case-sensitive matching of decoded body keys/string values of length `>= 4`, with path/headers/argv excluded. E26-14 separately shows a lexical-coincidence refusal; the draft leaves its policy as an open next-counter design question.
- Round-27's signature-counter attempt had no data and no F3 file-content echo leg. The draft requires an F3 file/model-content leg and pre-data non-author controls for each named class of any future signature counter. Round-28 C1 is request-field outcomes, not a signature counter.
- No tracked lane files or product code were edited. No git/jj writes, counter run, server run, build, test, or linter was performed by this scribe; the drafted qualification remains to be integrated and judged by the lane owner.
