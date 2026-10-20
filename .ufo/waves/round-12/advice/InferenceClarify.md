# InferenceClarify — Kama round 12 D4

Status: scoped implementation complete. Documentation-only append; no
verification, build, lint, test or runner execution performed by this seat.
Author advisor, not independent closure.

## Assignment as executed

D4 in `corpus/lessons/round-11-verifier-spotcheck.md`: label the S031 locality
consequence and the corresponding crosswalk remote-entry conclusion explicitly
as inference, and clarify that `supersedes S011` is registry supersession rather
than a claimed upstream change — while preserving original content/provenance
and dates, adding no new fact or entry, and claiming no expansion.

## Files changed

- `corpus/knowledge/served-identity-crosswalk.md` — appended
  `## Correction — round 12 D4 (authored 2026-10-20 UTC)` at lines 87–134
  (two labeled bullets plus a `## Grounded failure cases` scope paragraph at
  124–134).
  Lines 1–85 are unchanged: the `source:`, `verified-at:` and `recheck:` header,
  the crosswalk table, failure cases, alias limits, "What cannot be concluded",
  province handoff, kama use, QUALITY clearance and cited sources all remain as
  written. The append is a new section after the last cited-source line; no
  table cell, heading, date or citation above it was rewritten.

## What the appended section says (documentation behavior)

1. Locality is `[INFERENCE]`. It names the two claim sites — line 29's
   “a tags entry does not prove local weights (S031)” in the Ollama table row and
   failure case 6 at line 38 (“Available inventory is not proof of local
   weights”) — and states they are kama's inference, not page text. The
   documented basis is the S031 row (`corpus/SOURCES.md:43`, `docs` / tier A,
   opened 2026-10-20): `ModelSummary` optional `remote_model` (“Name of the
   upstream model, if the model is remote”) and `remote_host` (the row's claim
   cell: the upstream Ollama URL). The same label is applied to S011's
   “locally available” implication (`corpus/SOURCES.md:23`, opened 2026-10-19).
2. Supersession is registry-scoped. The note states that the line 1 and line 84
   phrases “supersedes S011's local-residency implication” record a
   `SOURCES-CONTRACT-v1` registry scope relation between two rows over the same
   `https://docs.ollama.com/api/tags` page (S031 opened 2026-10-20; S011 opened
   2026-10-19), narrowing only the local-residency wording. It is explicitly not
   evidence of an upstream documentation change between the opens, not a claim
   that the page said something different on 2026-10-19, and not a retraction of
   S011's non-status cells (`name`, `digest`, `size`, `details`,
   available-vs-loaded). No upstream diff was observed, and none is claimed.
3. Preservation is stated in the appended section itself: no page reopened, no
   source row/fact/coverage added, `SOURCES.md` cells not rewritten (append-only
   registry contract), `verified-at`/`recheck` and QUALITY clearance intact.

## Retained evidence (static reads only)

- `corpus/knowledge/served-identity-crosswalk.md` — full file read at start
  (85 lines) plus raw anchor reads: line 1 S031 header parenthetical; line 29
  Ollama table row; line 38 failure case 6; line 59 registry-prose bullet;
  line 84 S031 cited-source bullet. Post-edit raw reads of lines 85–134 confirm
  the append begins after the original last line and renders as two labeled
  bullets plus the failure-case scope paragraph.
- `corpus/SOURCES.md` raw reads — line 1 (contract framing), S011 row (observed
  at line 23; `docs`, A, scope “Ollama locally available model inventory, not
  proof of a loaded model”, opened 2026-10-19), S031 row (observed at line 43;
  `docs`, A, scope “Ollama `/api/tags` remote inventory caveat: available-model
  membership is not proof of local residency”, claim cell naming
  `remote_model`/`remote_host`, opened 2026-10-20), and the round-11 search-log
  entry that limits the supersession to the local-residency implication and
  keeps S011's non-status fields as written. A sibling-added S032 row (Git
  git-show manual, opened 2026-10-20) now occupies line 44, appended after S031;
  direct reads at lines 42–45 confirm S031 was not shifted.
- `corpus/lessons/round-11-verifier-spotcheck.md` — D4 text and the sustain/
  non-sustain reasoning that frames this as clarification, not fact rejection.

## Static findings

- Both defect points existed at exact, singular anchors; no other occurrence of
  “supersedes S011” or of the locality conclusion was found in the file, so the
  appended labels reach every site without touching original text.
- The registry row itself already frames S031's scope as a caveat (“membership
  is not proof of local residency”) and its search log explicitly separates
  registry supersession from upstream change; the new note therefore restates
  recorded provenance rather than introducing a fact.
- Peer `KamaR12.SourceCorrections` independently appended D2/D4 correction prose
  after the Leads section of `corpus/SOURCES.md` (rows and cells untouched).
  That prose agrees with this section (inference from `remote_model`/
  `remote_host`; registry-only supersession; “locally available” wording not
  erased). My note now cites SOURCES rows by id (`§Registry row S011` /
  `§Registry row S031`), not by line offset, so row insertion cannot stale it;
  peer was notified of the final form.
- Peer `KamaR12.SourceCorrections` reported that the new S032 row at
  `corpus/SOURCES.md:44` had shifted S031 to line 45 and that the note's `:43`
  citation pointed at S032. Not sustained on static read: S032 was appended
  after S031, S030 remains line 42, S031 line 43 and S032 line 44 (raw read of
  lines 42–45), so no shift occurred. The citation was nevertheless converted to
  row-id form in both bullets to remove offset sensitivity; the report records
  the observed positions instead of treating them as stable.
- Peer `KamaR12.CorrectionsConnection` flagged that failure case 6 sits under
  `## Grounded failure cases` and that the correction must explicitly govern
  that section, not only the table. Addressed at lines 124–134: the paragraph
  states that the heading's “Grounded” describes each case's documented premise,
  not every sentence; cites case 1 at line 33 as the existing inline
  `[INFERENCE]` precedent; limits case 6's inference to its concluding sentence;
  and assigns the same status to the `MODEL_OK` bullet's locality restatement at
  line 52 without reclassifying any other sentence. No original line changed and
  no case added or removed.

## Risks and limits

- Crosswalk line anchors cited in the appended note (1, 29, 38, 59, 84) are
  absolute; any later edit above them would stale those labels, so integration
  must confirm them. SOURCES citations are row-id based (S011, S031) and no
  longer depend on the table’s line offsets.
- No upstream page was reopened by this seat. The quoted field description and
  the same-URL/supersession facts are taken from the recorded SOURCES rows and
  the round-11 spotcheck's quote check; the note says so explicitly and stays
  on the documentation/provenance boundary.
- This is wording calibration only. It is not admission, closure, a coverage
  gain, a capability claim, or evidence toward C1's frozen-snapshot count.
- D4's SOURCES-registry half is owned by `KamaR12.SourceCorrections`; this seat
  did not touch `SOURCES.md`. If L1 wants a single D4 authority, the two appended
  passages are additive and mutually consistent, not duplicative rows.

## Unrun checks (for L1)

Not run here per lane contract: markdown lint, link/anchor validation, repo
tests, fidelity CLI, `reproduce.py`, any git diff/status audit, and any source
page fetch.

Suggested integration checks:

1. `git diff -- corpus/knowledge/served-identity-crosswalk.md` — pure addition
   after line 85, zero deletions/modifications above it.
2. Confirm cited anchors still resolve: line 29 contains “a tags entry does not
   prove local weights (S031)”; line 38 begins “6. **Ollama remote entry**”;
   line 52 contains the `MODEL_OK` locality restatement; lines 1 and 84 contain
   “supersedes S011”; lines 87–134 hold the new section, with the failure-case
   scope paragraph at 124–134.
3. Confirm `corpus/SOURCES.md` rows S011 and S031 are byte-unchanged and still
   carry the quoted scopes/dates (observed at lines 23 and 43; S032 was added
   at line 44 after this append, so verify by row id, not offset), and that its
   appended D2/D4 prose remains consistent with this section.
4. Confirm no trailing whitespace and that the appended heading style matches the
   `## Correction — round 11` precedent in `runtime-health-surface-matrix.md`.

Tools installed or updated: none.
