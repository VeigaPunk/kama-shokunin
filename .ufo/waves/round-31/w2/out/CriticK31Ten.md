# CriticK31Ten

FINDING: **refusal correct yes** under frozen rule (e). The adapter-authored message is nevertheless a false negative for the rule's provenance purpose.

| Pinned static literal (JSON notation) | Inherited emitted message (JSON notation) |
|---|---|
| `"response_format type must be one of \"text\" or \"json_object\", but got: "` | `"response_format type must be one of \"text\" or \"json_object\", but got: xml"` |

The decoded difference is exactly the appended offending value `xml`; the emitted string equals the pinned literal plus `response_type`, not the static literal alone. Raw-source membership also fails because the source escapes the inner quotes. Stripping the suffix would not fix that second mismatch and would break live message equality.

Evidence: registry K31-10, SKILL.md:1256, S181, pinned server-common.cpp:1366/1375, counter:42-43/465-466, and inherited DataA10 response/server-log excerpts. Frozen source and counter hashes matched. The inherited refusal receipt contains only `reject-message-not-adapter` and `live: {}`.

Impacted axes: **depth** (false-negative exclusion), **calibration** (do not mistake the reason label for absence of adapter provenance). Operability unchanged.

Smallest safe correction: leave the frozen round-31 refusal intact; document the false negative. Only a future pre-data rule should recognize the decoded pinned literal plus the source-bound request value, retaining exact live-envelope comparison.

LIMITS: No live server, frozen counter, canonical judge, build, or test suite was run. The response is inherited evidence; the string comparison uses transcribed inputs. No conclusion about overall C1 count/admission or endpoint health. No tool installs/updates; no tracked lane edits.

Full report, every shell command with exit code and verbatim output, and raw receipts: [CriticK31Ten/report.md](CriticK31Ten/report.md). This file is the required seat-report index, not a second evidence authority.
