# Draft — corpus/README.md round-24 frontier correction (candidate appendix)

Lane: kama round 24, seat ScribeFrontier (leaf scribe). Draft only.
Production files untouched. Append-only: the round-23 section
(`corpus/README.md:317-335`) stays exactly as filed; this text is a new
section appended after it.

Target file of the eventual edit: `corpus/README.md` (the lane README
carrying the `## Frontier disposition — round 23` section). The top-level
`README.md` is 14 lines and holds no frontier section, so it needs no
change.

**Policy revision (L1 decision, round 24).** The reading is **B**, not A:
availability is *per required read*, not a whole-root precondition.
`oracle-amendment-1.json` supersedes `preregistration.json`
`expected_after[3]` only — "unknown citation in any metadata-marked
repository necessarily exit 2" is withdrawn prospectively, because it
conflicts with the audit's original local-object contract (base
`tools/report-landing-audit.py:12-19`: the audited object is in the lane or
fleet repository; there is no remote-universe existence guarantee). The
initial registration stays immutable and is to be **reported separately as
not met**, never relabelled passed. Everything else in the preregistration
stands. This draft therefore states: metadata never changes local-object
resolution or a clean/failed verdict; only content an audit read actually
requires and cannot obtain is could-not-evaluate; a locally unresolved
citation keeps the ordinary failed verdict unless it names referenced but
unavailable local content.

Fill-in slots are marked `⟦…⟧` and are deliberately left unfilled: the
round-24 implementation is not landed at drafting time, and this lane runs
no build/test/formatter. Slot list:

- `⟦MEASUREMENT⟧` — the single post-integration run of
  `python3 tests/report-audit/promisor-grid.py --arm both --json`: frozen
  arm exit, current arm exit, per-row counts, population digest.
- `⟦POLICY-ROWS⟧` — the exact retained-grid rows whose expected exit or
  refusal-reason pin changed (promisor policy rows only), with the
  old→new expectation for each.
- `⟦R23-ROW-RESTATE⟧` — whether the round-23 sentence naming the 26 fault,
  4 contract and 13 control rows is restated as historical (recommended) or
  left untouched.

---

## A. Recommended appendix text (variant A — full correction, B reading)

```markdown
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
```

---

## B. Variant B — minimal correction (one paragraph, no list)

Use when L1 prefers a smaller diff; it keeps the three required claims
(partial reading withdrawn, D4 still partial, no new serving capability),
the per-read availability rule and the withdrawn-expectation note, and drops
the five-case enumeration, which the lesson file can carry instead.

```markdown
## Frontier disposition — round 24 correction (appended)

Appended; the round-23 section above stays as filed. The round-23 reading
that a partial clone or a paired promisor pack is refused — and that a
complete local promisor-marked repository can therefore only return
could-not-evaluate — is withdrawn as a policy reading: promisor metadata
states where objects may come from, and it never changes local-object
resolution or a clean/failed verdict. A complete local promisor-marked lane
or fleet clone now returns the same substantive finding as the otherwise
identical full clone (clean, or the same defect set, with authorized errata
still applying), and a genuine omission is still `landed-omitted` at exit
1. Availability is judged per required read: only content an audit read
actually requires and cannot supply locally is exit 2 could-not-evaluate,
with a content-derived reason and never a guessed absence; a locally
unresolved citation otherwise keeps the ordinary failed verdict, and a
locally sufficient repository is not refused because an unrelated historical
blob, an unselected branch or an unused file is missing. The metadata
refusal and that availability rule land together. One preregistered
expectation — unknown citation in a metadata-marked repository necessarily
exit 2 — is withdrawn prospectively and is reported as not met, not as
passed (`.ufo/waves/round-24/oracle-amendment-1.json`); no remote
repository completeness and no remote abbreviation uniqueness are claimed.
Git isolation is unchanged (`--no-lazy-fetch`, `--no-replace-objects`, log
and signature suppression, per-call deadline; no transport, no repository
program). D4 remains partial: alternates and gitfile redirects (O01/O02),
the `--shared`-of-partial bypass, prefix-ambiguity overwrite, duplicate
Landed sections, errata CR splitting, an `--errata` FIFO, the memory
ceilings and the unisolated sibling tools stay open. No new serving
capability, no endpoint sample and no service restoration is asserted;
other frontier is unchanged.
```

---

## C. Variant C — correction plus an explicit non-claim list

Use when the reviewer asks the README to state the non-claims next to the
frontier verdict rather than only in the lesson file.

Append after variant A's last paragraph:

```markdown
Non-claims for round 24: the auditor is not certified for untrusted
repositories; no lazy network fetch, transport invocation, signature
verification or replace-ref substitution is performed; a repository is
never executed; promisor metadata is not a completeness certificate; the
auditor claims no remote repository completeness and no remote abbreviation
uniqueness, and abbreviation uniqueness is judged over the audited local
object set only; a locally sufficient repository is not certified complete
for objects outside the audit's required reads. No scalar score, serving
surface or consumer claim moves.
```

---

## D. Wording hazards to check before landing

1. Do not write "partial clones are now supported". The withdrawn claim is
   the *automatic refusal*; the landed claim is that a complete local
   promisor-marked clone gets the same substantive verdict as the identical
   full clone, and that content an audit read actually requires and cannot
   obtain stays exit 2 — for availability, not for metadata.
2. Do not write "unknown citation ⇒ exit 2". That expectation is withdrawn
   prospectively (B reading). A locally unresolved citation keeps the
   ordinary failed verdict — the same finding kinds as the identical
   unmarked twin, authorized errata still applying — unless it names
   referenced but unavailable local content.
3. Do not introduce a whole-root precondition. Availability is per required
   read: an unrelated historical blob, an unselected branch or an unused
   file that is missing is not a reason to refuse a locally sufficient
   repository.
4. Do not call the round-24 change a D4 advance. D4 remains partial; the
   change removes a harmful over-refusal inside the D4 area.
5. Do not let the correction read as untrusted-repository safety, and do
   not silently close the alternates/gitfile/`--shared` items: they stay
   open exactly as round 23 filed them.
6. Do not describe the metadata-refusal removal on its own as the repair:
   removal without the availability rule was measured to answer exit 1
   `unresolved-full-hash` / `landed-unresolved` (the frozen arm's
   false-defect verdict) where exit 2 is owed. The two halves land
   together.
7. Do not claim the withdrawn expectation was met, and do not let the
   correction read as if it were achieved: it is reported as not met
   (see the amendment paragraph). The formal report belongs in the wave
   evidence and the lesson, not only here.
8. Keep "proved absent" out of the exit-2 wording: exit 2 is
   could-not-evaluate with a content-derived reason, never a guessed
   absence.
9. The r23 report-count and killed-process corrections (69 falsify-wave
   lane reports, not 68; 40 of 56 killed FIFO-process identities retained,
   not full identity evidence) appear in `corpus/lessons/round-23.md`, not
   in `corpus/README.md`. This scoped file carries no such counts, so
   those corrections need no text here; they belong to the lesson and log
   scribes.

## E. Evidence the draft rests on (measured elsewhere; quoted here as data)

Measured by the round-24 SKILL scribe on the base auditor blob
`cf706c52` (base `0df800e`), synthetic offline fixtures, one isolated
directory per case:

- identical complete lane+fleet content with no promisor metadata → exit 0
  clean; the same content with `remote.origin.promisor=true` → exit 2
  "partial clone (remote.origin.promisor)"; the same content with a paired
  `.promisor` marker → exit 2 "partial clone (promisor pack)". Zero
  missing objects in all three: the refusal is metadata-driven.
- a genuine uncited lane commit → exit 1 `landed-omitted` without metadata
  and exit 2 with metadata: the metadata refusal masks the omission.
- removing only the two metadata refusals (in a scratch copy) turns the
  genuinely-incomplete cases into exit 1 `unresolved-full-hash` /
  `landed-unresolved`, the frozen arm's false-defect verdict: refusal
  removal without the availability rule is a regression.
- under `--no-lazy-fetch` with the promisor remote pointed at
  `file:///nonexistent`: `cat-file --batch-check` reports "<sha> missing"
  (rc 0, no fetch) and `rev-list --objects --missing=print` reports
  "?<sha>"; `rev-list --all --missing=print` without `--objects` does not
  list the missing blob, so a missing-object probe must use the
  `--objects` form and must not become a whole-root precondition.

## F. Grounding of the policy choice (from the amendment, quoted as data)

`.ufo/waves/round-24/oracle-amendment-1.json` records, before L1 inspected
or integrated any candidate: the original finite mechanical audit contract
(base `tools/report-landing-audit.py:12-19` — the audited object is in the
lane or fleet repo, no remote-universe existence guarantee); an outside
closure control on a complete promisor-marked real lane, rounds 10-22,
including an errata-corrected locally missing hash, which the initial
expectation would abort before the errata could apply; an independent
preimplementation witness analysis; and the instruction that a whole pinned
root reachable-tree precondition is broader than the availability of objects
the audit actually requires. The initial registration remains immutable and
is reported separately as not met.
