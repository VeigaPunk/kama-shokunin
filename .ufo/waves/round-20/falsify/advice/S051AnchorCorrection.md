VERDICT: partial - the correction is appended, revision-qualified, and its stable label resolves, but the claimed current range 210-215 is stale at this tree (the paragraph is at 217-222).

# S051 anchor review

## Evidence
- `corpus/lessons/round-18.md:285` still contains the unqualified citation `corpus/SOURCES.md:209-213`.
- `corpus/lessons/round-18.md:425` opens the separate “Round-20 correction” section; lines 447-451 qualify the cited range at revision `8bf99cae`, explain S057's historical +1 shift, point to “S051 identity-label clarification,” and warn that future registry appends shift the text again. The old citation at line 285 was not replaced.
- This is consistent with append-only correction: `round-18.md:285` retains the old pointer and the correction is separately appended at 447-451. Frozen prior evidence, `build/advice/Lesson18Line42.md:23-25`, says the cumulative `8bf99cae`→`37bd4c5` diff had one pre-existing in-place edit at line 42 and a separate pure append; it does not show a change to line 285. Current-vs-pinned-revision diff was not run because Git/JJ operations are forbidden by the lane boundary.
- The label resolves uniquely in current `corpus/SOURCES.md`: line 217 begins `S051 identity-label clarification`. It is a paragraph lead-in, not a syntactic Markdown heading, but the exact label is findable and stable.
- Current `corpus/SOURCES.md:217-222` contains the full six-line S051 clarification, ending with “no strict online pin-verify pass is claimed.” It is not at 210-215. Current rows S058-S064 occupy lines 70-76 after S057 at line 69 (`SOURCES.md:68-76`); the prior R19 check records line 70 blank and `## Paths` at line 71 at its pinned tip (`build/advice/SourcesGuardR19.md:40`). This accounts for the additional seven-line shift from 210-215 to 217-222.

## Remaining stale claims
- `corpus/lessons/round-20.md:82` calls `corpus/SOURCES.md:210-215` the “current source text”; that range no longer locates S051 at the present tree. `build/advice/S051AnchorShift.md:1,25` likewise describes 210-215 as the current range; both claims need revision or an explicit pinned-tip qualifier.
- The earlier span record is internally inconsistent: `build/advice/S051AnchorShift.md:11` gives the complete paragraph as 210-215 at `37bd4c5`, while `build/advice/SourcesGuardR19.md:41` says 210-214 there. The six-line paragraph and full endpoint in the former are consistent with the current text after seven later rows; 210-214 omits its final sentence.

## Limits
Read-only review of the requested Markdown locations and related prior reports; no Git/JJ commands, installs, or scratch files. The current working-tree bytes were observed directly; exact blob equality with the named historical revisions was not independently checked in this seat.