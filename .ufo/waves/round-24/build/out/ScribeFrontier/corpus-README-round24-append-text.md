# Append-ready text for corpus/README.md (round-24 frontier correction)

# Copy the body below (everything after this header) and append it to
# corpus/README.md. Byte-identical to the tail of
# corpus-README.with-round24-frontier.md and to the hunk in
# corpus-README-round24-frontier.patch. Two fill slots remain:
#   ⟦POLICY-ROWS⟧ and ⟦MEASUREMENT⟧ — L1's single post-integration run.

## Frontier disposition — round 24 correction (appended)

Appended; the round-23 section above stays as filed. Round 24 is a
repair-first round on one axis: the report auditor's promisor handling.
The round-23 reading — a partial clone, or a paired promisor pack, is
refused, so a complete local promisor-marked repository can only return
could-not-evaluate — is withdrawn as a policy reading. Promisor metadata
(`extensions.partialclone`, a true `remote.*.promisor`, a `.promisor`
marker paired with its `.pack`) states where objects may come from; it
never changes local-object resolution, and it never changes a clean or
failed verdict. Availability is judged per required read, not as a
whole-root precondition:

- a complete local promisor-marked lane or fleet clone returns the same
  substantive finding as the otherwise identical full clone — clean, or the
  same defect set, with the same finding kinds and with authorized errata
  still applying — and not exit 2;
- a genuine omission in such a clone is still `landed-omitted`, exit 1;
- a locally unresolved citation keeps the ordinary failed verdict, exit 1,
  with the same finding kinds as the identical unmarked twin, unless it
  names content that is referenced but unavailable locally — then exit 2
  could-not-evaluate, with a content-derived reason and never a guessed
  absence;
- content that an audit read actually requires and that cannot be supplied
  locally is exit 2 could-not-evaluate, never a clean or a failed verdict;
- a repository that is locally sufficient is not refused because an
  unrelated historical blob, an unselected branch or an unused file is
  missing.

The required reads are the pinned lane tip, the round's lane commits, the
cited objects, the committed fleet report, the committed `corpus/SOURCES.md`
and the errata rows. A bounded missing-object traversal may diagnose one
unresolved token, but it is never a blanket precondition over the whole
object store; a whole-root precondition is deliberately not introduced,
because it would refuse repositories that hold everything the audit reads.

The withdrawal of the metadata refusal is not by itself the repair: without
the per-read availability rule an incomplete repository answers with a
false clean or false defect verdict instead of could-not-evaluate, so the
two halves land together.

Isolation is unchanged: every git call still carries `--no-replace-objects`
and `--no-lazy-fetch` with `log.follow=false`, `log.showSignature=false`,
`log.mailmap=false`, `log.showRoot=true` and
`i18n.logOutputEncoding=UTF-8`, and keeps its per-call deadline. No
transport is opened and no repository-configured program is executed.

One preregistered expectation is withdrawn prospectively: that an unknown
citation in any metadata-marked repository necessarily yields exit 2. It
conflicts with the audit's original local-object contract (base
`tools/report-landing-audit.py:12-19`) — the audited object is in the lane
or fleet repository, with no remote-universe existence guarantee — so it
is reported as not met, not as passed
(`.ufo/waves/round-24/oracle-amendment-1.json`). No remote repository
completeness and no remote abbreviation uniqueness are claimed;
abbreviation uniqueness is judged over the audited local object set only.

The round-23 row counts above describe the round-23 arm and remain as
filed. Round 24 changes only the promisor policy rows' expectations in the
retained grid `tests/report-audit/repo-state-grid.py` ⟦POLICY-ROWS⟧; every
other row's expectation is unchanged, and the new promisor policy rows are
graded by `tests/report-audit/promisor-grid.py` with the frozen arm at
`0df800e896f6bce285a81e794ad4ae1d1e6c3a71` ⟦MEASUREMENT⟧.

D4 remains partial. This is not untrusted-repository safety and closes
none of the round-23 open items: objects borrowed through
`objects/info/alternates` or a `.git` gitfile redirect still resolve as
local (O01/O02), the `--shared`-of-partial bypass, prefix-ambiguity
overwrite, duplicate `## Landed changes` sections, errata CR splitting, an
`--errata` naming a FIFO, the memory ceilings, and the unisolated sibling
tools `citation-provenance.py` and `sources-append-only.py` stay open. D4
local-Git-config/history and UTF-8 hardening remains frontier.

No new serving capability: no endpoint sample, no service restoration, no
new knowledge or consumer surface. Other frontier unchanged:
external-system-library identity, receipt-header minimization, historical
crash-as-kill leaves, K05/other-engine serving and real registered-consumer
reconciliation.
