# ReviewS211

Seat: ReviewS211. Axis judged: calibration. Leaf; no subagent. Neither target was edited. No source row was appended.

Working-tree bytes of both targets match tip `e5a8ececf3d60fd53b36bb74299693a29e8f74b6` (`git hash-object` equals `git rev-parse <tip>:<path>`). Lane HEAD at read time was `9014843cb7de8fbe87a97954c13832b67d55f046`; these two paths were unchanged relative to that tip.

## Findings

### Seat report records a successful fetch; still-live is absent from the page

Yes, and yes. `.ufo/waves/round-35/w1/out/ScoutQuarantineS211.md` records a successful fetch of the cited chapter, and records that the register quote `still-live` is absent from that page.

- Line 38: "The page was fetched successfully."
- Line 84: "The page was fetched successfully. The exact token `still-live` is absent from both the raw markdown and the GitHub blob text extract."
- Terminal verdict, lines 236–238: verdict `absent`; "The cited page was fetched. The register quote `still-live` is not in it."
- Lines 260–268: cited blob and raw file at commit `35b83cee12ae26f10b58d4163298352384503907` returned the chapter; "The token `still-live` does not occur in the blob extract or the raw body."

Scope, so this is not over-read:

- Success is the cited blob and the raw sibling at that commit. Line 264 records a separate GitHub contents API fetch as failed. That failure is not the cited-page result.
- The seat report does not record an HTTP status code. It contains neither `HTTP 200` nor the token the lesson used for this row.
- `still-live` is absent from the fetched page. It is not absent from the report: the report names the register quote and says the page lacks it.
- `seat-exit-codes.json` has `ScoutQuarantineS211` `timed_out` false, `report_exists` true, `stdout_persisted` true. The file is a persisted transcript plus that terminal verdict. Both parts agree. The exit file is corroboration only.

### HEAD status the spot-check records

HTTP 200. That is the spot-check's recorded closure HEAD status, not a status this reviewer re-measured, and not a status code in the seat report.

- `corpus/lessons/round-35-verifier-spotcheck.md:95`: "Closure HEAD returned HTTP 200." The same cell says the seat report (not timed out) records a successful fetch and says `still-live` is absent, and that the lesson's HTTP 429 is not in that report.
- Line 118: "Closure HEAD was 200, and `ScoutQuarantineS211.md` records a fetch with `still-live` absent."

### What a round-36 correction row must not restate

It must not restate the round-35 lesson's S211 reason. The spot-check routes that reason as the error: the lesson says the fetch was unreachable because it returned HTTP 429 (`corpus/lessons/round-35.md:42`). The frozen C1 predicate requires the correction row not to contain the token 429. `tools/round36-statement-audit.py` sets `FORBIDDEN = "429"` and counts any correction row containing that token as a false correction, including a denial that still spells the token.

Do not copy that token into `corpus/lessons/round-36.md`. Do not rewrite `corpus/lessons/round-35.md`. Do not append S211. Those last two are the spot-check route (lines 95 and 118), not a second page verdict.

A row that satisfies the counter's R35-S211 arm cites `ScoutQuarantineS211.md`, states that `still-live` is absent, and states HEAD 200. That 200 is the spot-check HEAD status. Saying the seat report itself recorded HTTP 200 would mis-cite it.

## Residual risk

- Putting the forbidden token into the lesson correction row fails C1 even when the row also states HEAD 200 and page absence. This review names the token so the constraint is explicit. This file is not the lesson.
- Treating the contents-API failure as the cited fetch, or treating `still-live` as absent from the report text, would invert the recorded facts.

## Verification gaps

- This reviewer did not re-fetch the GitHub chapter. The task was to read the two files. A live status beyond what the spot-check records is not claimed here.
- Byte length of the fetched chapter was not re-measured. The seat report already leaves that unmeasured.

## Recommendation

Keep the seat-report reading as successful fetch and `still-live` absent on the cited page. Keep the spot-check HEAD status as HTTP 200. A round-36 correction row must not restate the lesson's HTTP 429 unreachable reason, and must not contain that token.
