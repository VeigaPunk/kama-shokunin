# Round 12 — frozen evidence is not source correspondence

Steered round 12; 2026-10-20 UTC. Starting lane revision:
`79fa257719e8688692ed1dc443589331ba22b7fe`.
Outside authority: `round-11-verifier-spotcheck.md` by CloseKamaR11,
status ok / admitted true. This round never rewrites that review or its inputs.

## Declared claim

**C1 — calibration:** for one routed source path, the old auxiliary frozen
SOURCES snapshot still differs from its declared source commit; a new exact
corrective snapshot matches. The before/after source-mismatch count is one
versus zero across these two snapshots, not a mutation of old evidence.
Capture uses `git show` (S032); the same measurement command independently
reads the pinned historical blob with `git cat-file blob` for comparison.
Source revision/path: `2f7303c242319c1dc96c6bcf7702ac18b3ca1aad:corpus/SOURCES.md`.
Its manifest independently checks capture integrity.
A self-consistent snapshot and manifest alone cannot establish source
correspondence. Calibration is the lowest assigned axis (7 versus operability 8);
score remains 7 → 7, delta 0. No serving capability, endpoint freshness, coverage expansion or scalar
increase is claimed. Declaration: `.ufo/waves/round-12/claims.json`.

## Gate

| Candidate | Decision | Reason |
|---|---|---|
| New exact corrective snapshot and source-correspondence checker | admit only with committed red-before/green-after and isolated negative controls | D1; KQ14/KQ15; source correspondence and digest integrity are separate |
| The old frozen snapshot is faithful because its manifest digest matches | reject | CloseKamaR11 D1 found actual source SHA-256 `9dc40d25a595b3d42b39649e17094cfa4e7190cfbf340331252dd29dea22093a` versus frozen `52665cf2d648112be2683c61485d42da1bf1dc859ea1df41d857672c60142fa1` |
| Historical title/routing instructions remain current authority | reject | D5: the undelivered seat protocol is archival, never authorization to inspect environment or replay old host commands |
| Remote-origin inventory means locally resident weights | reject | S031 documents remote fields; the locality consequence is inference, not upstream wording or runtime evidence |
| New source row or corrected snapshot constitutes new serving knowledge | reject | Source curation and evidence repair do not expand covered domain ground |

### Source access and curation

New rows, actual opened evidence and located quotes are recorded below only
after the source is opened. Existing immutable cells remain unchanged; any
status/recheck/used-by changes are recorded old → new. Registry navigation/date
corrections are appended rather than changing historical row cells.

| New row | Opened URL / access date | Located quote (≤25 words) |
|---|---|---|
| S032 | https://git-scm.com/docs/git-show / 2026-10-20 | DESCRIPTION, plain blobs, Git 2.56.0 manual (2026-09-28): “For plain blobs, it shows the plain contents.” |
| S032 (additional grounding) | Same opened URL/date | DISCUSSION: “The contents of the blob objects are uninterpreted sequences of bytes. There is no encoding translation at the core level.” |

S032 is docs/A scoped to byte-preserving historical blob retrieval. C1 cites
it for capture method, not as proof of observed snapshot outcome. Added row:
absent → mined; recheck on-release; used-by `corpus/lessons/round-12.md`.
Existing S001–S031 status/recheck/used-by cells are unchanged; no old→new cell
changes besides the newly added row. Bounded search and prior-overlap credit
are detailed below and in SOURCES Search log.

### Independent review boundary

The 32 round-12 seats are author-dispatched advisors, not outside discernment
review. Outside round-11 review is learned here; it does not independently admit
round 12. Promotion boxes remain author assertions. A fresh non-author closure
must sample this round's admit and reject decisions.

## Mistakes

| Class | Evidence pointer | Captured-by | Fix / falsification obligation |
|---|---|---|---|
| evidence-fidelity | `round-11-verifier-spotcheck.md` D1; round-11 frozen SOURCES differs from actual git blob despite matching shipped digest | Gate standard Two evidences; KQ14, sharpened by KQ15 | New exact snapshot directly from git bytes; preserve old receipt; same gate must reject old snapshot and a coherently edited snapshot+manifest, then accept exact corrective bytes |
| stale-navigation | Same review D2; SOURCES introduction says all rows round 10, and K02 path still says next entry | KQ3/KQ12 | Appended scope/date/navigation correction credits S031 round 11 and landed crosswalk; no immutable row-cell edits |
| incomplete-criterion-pointer | Same review D3; SKILL line 357 narrows pointer to KQ11–KQ13 despite KQ14 | KQ14 and complete QUALITY admission authority | Appended complete-applicable-criteria pointer and local fidelity registry; not a new admission method |
| inference-boundary | Same review D4; S031 locality consequence and supersedes wording can read as upstream fact | KQ6/KQ13/KQ14 | Explicitly label locality inference and lane-registry supersession in appended registry/crosswalk clarification |
| archive-authority | Same review D5; undelivered round-10 seat protocol opens binding on all seats | KQ5/KQ10 | In-file archival disclaimer overrides prior binding wording; no old routing or host permission reactivated |

Only the D1 fix counts as demonstrated failure after its committed measurement
receipt; prose corrections D2–D5 are clarifications, not separate measured
fix-capability claims. Existing criteria capture their boundaries. The operator
cleanup item in the review belongs to Main, not this lane's write scope.

## Work and scope

One validated 32-seat wave; L1 holds canonical planner seat, bounded revenger
PlannerWalk provides a planning data-walk. Validation uses the campaign policy,
then the complete taskCall is dispatched unchanged in one task call, without
model arguments. Spec, dispatch, registry and advisory reports are committed
under `.ufo/waves/round-12/`. A rejected initial spec key was removed before
validation; no invalid wave was dispatched. No services, endpoints, config,
environment, credentials, provider routes or sibling repositories are changed.
No tool installation was necessary. Stale-lane: respawn-per-round; no other
mission of kama is open. Starting working tree was clean; existing non-author
verifier files are read-only and not swept into this round.

## Census — before

Command:
`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama`

```text
kama W04 S031 duplicate url docs.ollama.com/api/tags across scopes
kama ok /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md
```

Exit 0. Full streams plus `census` counting command/output in
`.ufo/waves/round-12/sources-before.json`: rows 31, A 28/C 3,
mined 21/queued 5/rejected 5. W04 is an existing scoped same-URL row, not
independent corroboration. Final census and measured results append below.

## Opened source and sourced-claim binding

C1 cites **S032**, the official Git git-show manual opened by L1 on
2026-10-20 at https://git-scm.com/docs/git-show. Located quote,
DESCRIPTION, plain blobs (manual last updated in 2.56.0, 2026-09-28):
**“For plain blobs, it shows the plain contents.”** This located quote
supports extracting historical blob contents directly rather than copying
tool-rendered text. It does not prove this snapshot's correctness; that is
separately measured against the immutable source and independent hash anchor.
The earlier proposed own-work S032 binding is superseded before admission by
this opened primary documentation row, avoiding circular self-endorsement.

Row changes: **S032 absent → mined, docs/A**, opened 2026-10-20,
recheck on-release, used-by `corpus/lessons/round-12.md`.
S001–S031 status/recheck/used-by cells are unchanged. Existing S031 was
reopened by OllamaSource on 2026-10-20: `ModelSummary.remote_model.description`
is “Name of the upstream model, if the model is remote”; `remote_host.description`
is “URL of the upstream Ollama host, if the model is remote”. No new row or
upstream-change claim follows. Receipt: `.ufo/waves/round-12/advice/OllamaSource.md`.
GitSource's separate gitrevisions syntax corroboration is advisory, not an
additional registry source or new serving knowledge.

Bounded source search: three pages identified/opened/screened across the L1
and scouts (git-show, gitrevisions, Ollama tags), one new row included, no
quality exclusions, two retained only as corroboration/existing-row recheck.
Command/page pointers and stop rationale are in SOURCES Search log. Admitted
knowledge entries and frontier ground added this round: zero; expansion is
unchanged, not inferred from row growth.

## Claim limit and prior-overlap credit

The fixed denominator is **one routed source path**, selected by D1 and
compared across its old and corrective snapshots, not a sweep of every frozen
input or erasure of the old mismatch. The outside round-11 closure established
the nine original knowledge blobs matched git while this auxiliary SOURCES
blob did not; `legacy-baseline.json` was round-11-generated metadata, not an
original blob at the source revision. The old mismatch is known evidence,
not this round's discovery. The corrective snapshot's match is a construction
check, not new domain knowledge. Calibration credit is the fail-capable,
independently source-anchored gate plus the explicit correction of the earlier
integrity-only claim in LOG, with score unchanged and outside review pending.

Archive clarification D5 uses a **prepended** current warning for the non-corpus
undelivered planning artifact, preserving its original bytes as a suffix.
L1 authorized that placement to warn before the obsolete binding title.
Historical corpus corrections remain appended; no historical corpus prefix
or round-11 frozen receipt is rewritten.

### Exact D1 erratum target

Old snapshot:
`.ufo/waves/round-11/frozen/before/corpus/SOURCES.md`.
Old pin/receipt:
`.ufo/waves/round-11/frozen/expected.json` and
`.ufo/waves/round-11/acceptance.json`.
The source commit's complete search-log line was truncated in the captured
file and an `artifact://1157` tool-display marker appended. The source and
old-frozen SHA-256 values in §Gate identify those unequal bytes. These old
artifacts stay byte-identical; a new corrective copy and expected manifest
live under `.ufo/waves/round-12/frozen/`, never regenerated over round 11.

## Advisor dispositions

- `AttackAdmission`: accept the narrow framing and explicit LOG erratum.
  One routed source path is compared across two snapshots; known D1 is not
  rediscovered, and exact-copy construction is not domain expansion.
- `AttackSourceAnchor`, `ReviewSourcePin`, `Safety`: pin source revision,
  path, blob OID, SHA-256 and length independently of the manifest. Separate
  integrity/source findings; an unavailable or invalid anchor is exit 2.
  Coherent snapshot+manifest edits must not redirect historical authority.
  No custom Git object parser or fleet-level protocol mechanism is introduced.
- `AttackHistory`, `Safety`: historical evidence stays intact; receipt output
  must not overwrite prior artifacts. D5's prepend placement is an explicit
  non-corpus archive ruling recorded in LOG. Original archive bytes remain.
- `ReviewInference`, `CorrectionsConnection`, `OllamaSource`: supplement the
  whole S031 conclusion, including the old grounded-failure-case heading,
  with explicit inference precedence and exact field-quote attribution.
- `AttackSourceCuration`: S032 supports raw historical capture method; the
  actual gate reads source bytes using `git cat-file blob` and independently
  verifies their identity. The same opened manual's DISCUSSION supplies the
  byte/encoding boundary in addition to DESCRIPTION's plain-contents quote.
  S032 is docs/A, not the superseded proposed own-work row.
- `ReviewGateInterface` final actual-code read found no blocking code defect;
  the pin-only corruption case has source-mismatch count zero, whereas a
  changed snapshot with unchanged pin has count one. Integrity failure still
  dominates either case with exit 2. Static review is not execution.
- Earlier advisor observations of missing S032/lesson/code/disclaimer are
  explicitly mid-integration observations, not final-tree verdicts. No absent
  artifact or unrun command is promoted to evidence by those reports.

No axis or source row is retired. No external protocol requirement is enacted:
the structural observation that digest integrity alone misses capture-time
corruption is handed to the protocol owner in the fleet report, not absorbed.
Earlier historical template copies are not executed or renumbered by this
round; its scoped D5 ruling labels the named round-10 artifact.
