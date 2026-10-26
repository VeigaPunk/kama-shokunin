# K1Heading — calibration attack on v3 sections

**Verdict: no lane-specific false exemption is present in the measured SCORECARD history; the parser has a real, declared fence-awareness limitation, but it does not explain the build's graded/ungraded split.**

## Parser behavior and strongest counterexample

`tools/append-only-audit.py:231-238` recognizes any byte line beginning exactly `b"## "`, regardless of Markdown fence state, strips a terminal CR and trailing whitespace, and makes that normalized text the current title until another recognized line. This is lexical, not Markdown section parsing. The frozen counter independently duplicates it at `tools/round48-append-audit-v3-check.py:268-274`.

- A heading inside a fenced code block **does become a section**; this is also explicitly disclosed by the preregistration's C1 limits and the lane's `append-only-audit.py` docstring (`tools/append-only-audit.py:20-21`). An attack fixture containing `## Axes` in a fence can therefore change classification of following lines. This is a parser limitation, not an undisclosed mismatch between tool and counter.
- `##` without a following space does not match. `## Axes ` and CRLF `## Axes\r\n` normalize to `## Axes`, so both match the exempt title.
- `###` does not match `## `; it therefore remains owned by the preceding `##` section, including within exempt sections. This matches the documented definition of section as the last `## ` line.
- A later dated/reused `## Capabilities` resets the owner to that same exempt title. If it has enough lines at some window commit to satisfy the title-level non-gutted test, those lines are exempt too. Exemption is by title, not occurrence or position. That is the strongest counterexample: a dated section reusing a carve-out title can be made non-graded despite being substantively historical content.

No code change is proposed: counters and preregistration are frozen, and this review's evidence found no lane occurrence that makes the repeated-title risk active. Smallest safe future correction: bind exemption to the unique head occurrence (or an explicitly bounded region), rather than every occurrence of a normalized title; if the contract keeps the documented lexical definition, fence-aware parsing would be a separate definition change requiring synchronized counter/fixture coverage.

## Lane history census

Command: `git -C "$S/lane" log --format=%H -- SCORECARD.md` (94 commits), followed for each commit by `git -C "$S/lane" show <commit>:SCORECARD.md`; a script enumerated every exact `^## ` line after the first and compared normalized titles with `{## Axes, ## Planned, ## Retired, ## Saturation, ## Capabilities}`.

Result: **no later/duplicate occurrence of any of the five exempt titles in any of the 94 SCORECARD versions.** In particular, at measured build `380bcdff9c8af06997c482f6eb03db926a794a2b`, line 8 `## Axes`, line 51 `## Planned`, line 55 `## Retired`, line 115 `## Capabilities`, and line 135 `## Saturation` are each the sole occurrence of their title. The later `## Historical head sections ...` and dated round sections have different titles. The scan found no CRLF in the history and no matching exempt-title heading inside a fenced block. The C1 counter's reading of the frozen declaration is also explicit: `tools/round48-append-audit-v3-check.py:139` defines those five titles, and `registry/append-only-contract.tsv:3` declares them as SCORECARD carve-outs.

## Does a graded/ungraded split depend on a repeated title?

No. Independent C1 run at the build commit:

`python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round48-append-audit-v3-check.py --repo "$S/lane" --tip 380bcdff9c8af06997c482f6eb03db926a794a2b --scratch "$S"`

Output: `selftest=1 contract=1 lane=1 fixture=1 stable=1 rows=9 files=89 lane_events=5 lane_failures=0 ungraded_lines=89 fixture_fail=0 met=True`, exit 0.

The direct tool run at the same tip reported `events=5`, `regressed=0`, `vanished=0`, `bad_declarations=0`; its only SCORECARD events were:

- `dd9f5dc6c0e6 SCORECARD.md deleted=31 graded=14 ungraded=17` — 7 deleted lines under `## Axes` and 9 under `## Planned` ungraded; 8 pre-heading lines and 6 under `## Retired` graded; the single deleted line under `## Saturation` ungraded, but `## Retired` was not an eligible title at that event window.
- `0718b6abbda6 SCORECARD.md deleted=2421 graded=2349 ungraded=72` — 42 lines under `## Axes`, 18 under `## Capabilities`, and 4 each under `## Planned`, `## Retired`, and `## Saturation` ungraded; all other deletions graded. These are the one-per-title head sections, not later dated duplicates.

Thus the measured 14/17 and 2349/72 splits depend on expected head-section carve-outs and the eligibility/non-gutted rule, not duplicate headings, fence headings, or reuse of exempt titles. The pre-heading authority-banner deletions remain graded, consistent with the parser's `None` before the first heading and with the reported restored banner evidence.

## Axes and evidence locations

- **Impacted axis:** calibration, because C1 is a declared-region measurement. Evidence does not warrant rejecting the measured claim on a lane-specific heading collision. Generic parser weakness remains disclosed and should be considered in future calibration work.
- Parser source: `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/append-only-audit.py:231-238`.
- Independent recomputation: `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round48-append-audit-v3-check.py:268-274,349-360`.
- Frozen limitation and title set: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/preregistration.json:24`; counter title set `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round48-append-audit-v3-check.py:139`; contract declaration `/home/vgpnk/Projects/shokunin/kama-shokunin/registry/append-only-contract.tsv:3`.
