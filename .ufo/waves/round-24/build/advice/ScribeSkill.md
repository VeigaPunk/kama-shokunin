# ScribeSkill — round-24 SKILL correction for the promisor rules (draft only)

Seat: `KamaR23-2.ScribeSkill-2` (leaf, no dispatch). Base: `0df800e896f6bce285a81e794ad4ae1d1e6c3a71`.
Host: git 2.56.0, Python 3.14.8. Round-24 claim C1, calibration 7→7.

## Verdict

**Drafted to the L1's decision (B: actual required-read availability, not a
whole-root precondition); candidate append only, no production edit.**

The r23 harm is real and measured: at the base, promisor *metadata* alone
turned correct verdicts into exit 2 on repositories whose required objects
were all local, and hid a real `landed-omitted` finding. The drafted
SKILL.md section states the replacement rule (availability of the evidence
the audit reads decides; metadata never decides), keeps the trusted-use
restriction, the exit classification, the git isolation and the 20 s
deadline verbatim, and keeps the round-23 "Open, not claimed" list intact
except for the two promisor sentences it supersedes. No production file
was edited: the section exists as candidate text and as an append-only
unified patch that passes `git apply --check`.

Scope decision, taken by the L1 seat (`agent://KamaR23-2`, round-24):
**B** — availability is judged per required read, and a bounded
missing-object traversal is a diagnostic for one unresolved token, not a
precondition over the object store. The draft states B. The prospective
expectations come from `.ufo/waves/round-24/oracle-amendment-1.json`,
which withdraws the preregistration's `expected_after[3]` ("unknown
citation in any metadata-marked repository ⇒ exit 2") prospectively; that
original registration stays immutable and must be reported separately as
not met, not relabelled passed. No candidate implementation was
inspected, measured or integrated by this lane; the draft states policy,
not observed candidate behaviour.

## Behavior observed (bounded local fixtures, no network)

### 1. Metadata-only refusal flips correct verdicts (the r23 harm)

Fixtures: `tests/report-audit/repo-state-grid.py` fixture helpers
(`base()`, `commit()`, `publish()`, `report()`), one isolated directory
per case; a lane commit by `kama-shokunin` cited by the committed fleet
report; `--rounds 1 --no-errata --json`; the base auditor
`tools/report-landing-audit.py` (blob `cf706c52…`, identical to
`0df800e:tools/report-landing-audit.py`).

| case | fixture | missing objects | base exit | base findings |
|---|---|---|---|---|
| A1 | complete lane+fleet, no promisor metadata | 0 | **0** | clean |
| A2 | A1 plus one uncited lane commit before the cutoff | 0 | **1** | `landed-omitted` |
| B1 | **A1 content**, complete clone + `remote.origin.promisor=true` | 0 | **2** | — `could-not-evaluate: … partial clone (remote.origin.promisor)` |
| B2 | **A2 content**, complete clone + promisor config | 0 | **2** | — `partial clone (remote.origin.promisor)` (the real omission is masked) |
| C1 | **A1 content**, complete clone + paired `.promisor` marker, no promisor config | 0 | **2** | — `partial clone (promisor pack)` |
| D1 | blobless clone, cited blob absent | 1 | **2** | — `partial clone (promisor pack)` (correct outcome, metadata reason) |
| D2 | D1 with the promisor config stripped | 1 | **2** | — `partial clone (promisor pack)` |

Evidence: `evidence-promisor-metadata.json`; script
`probe-promisor-metadata.py`.

### 2. Removing the metadata refusal alone is *not* the repair

Same fixtures, base auditor with exactly two blocks removed in a scratch
copy (`make-no-promisor-refusal-candidate.py`; the production file was not
touched):

| fixture | base exit | without the metadata refusal |
|---|---|---|
| T01-like blobless clone, cited lane commit local | 2 `partial clone (promisor pack)` | **0 clean** — identical to the identical full clone |
| F23-like blobless clone, cited blob absent | 2 `partial clone (promisor pack)` | **1 `unresolved-full-hash`** — the false-defect verdict of the frozen arm |
| F06-like promisor-marked lane, fabricated citation | 2 `partial clone (extensions.partialclone)` | **1 `landed-unresolved` + `unresolved-full-hash`** — absence read as proof |

The transport program did not run in the F06-like case
(`core.sshCommand` marker absent): `--no-lazy-fetch` still holds.
Evidence: `evidence-no-promisor-refusal-candidate.json`.

### 3. Missing objects under the auditor's own isolation

Blobless clone whose promisor remote was pointed at
`file:///nonexistent/kama.git`, every git call run as
`git --no-replace-objects --no-lazy-fetch -c i18n.logOutputEncoding=UTF-8
-c log.follow=false -c log.showRoot=true -c log.showSignature=false
-c log.mailmap=false -C <repo> …`:

- `cat-file --batch-check` on the absent blob → `6e98d18… missing`, rc 0,
  no stderr, no fetch attempt;
- `cat-file -e <blob>` → rc 1, no stderr, blob still absent afterwards;
- `rev-list --objects --all --missing=print` → rc 0, the absent object
  listed as `?6e98d18…`;
- `rev-list --all --missing=print` **without** `--objects` → rc 0 and the
  missing blob is **not** listed (only the commit) — an availability
  enumeration needs `--objects`;
- a present commit in the same clone answers `… commit 140`.

Evidence: `evidence-missing-object-isolation.json`; script
`probe-lazy-fetch-and-availability.py`.

## Drafted SKILL.md append

- `SKILL-round24-promisor-correction.md` — the candidate section text.
- `SKILL-round24-promisor-correction.patch` — unified diff appending it to
  `SKILL.md` after line 814; `git apply --check` → OK (no worktree change).

Content map, against the assignment's three requirements:

1. **Trusted-use restriction preserved** — the section repeats "never
   point it at an untrusted repository", KQ32 narrowed by KQ34, the git
   isolation string (`--no-replace-objects`, `--no-lazy-fetch`,
   `i18n.logOutputEncoding`, `log.follow=false`, `log.showRoot=true`,
   `log.showSignature=false`, `log.mailmap=false`), strict UTF-8 decoding,
   the 20 s deadline and the git ≥ 2.45 floor; it states that no network
   transport, lazy fetch, signature verification or replace-ref
   substitution is reintroduced.
2. **Exit classification preserved** — 0 clean / 1 failed with named
   finding kinds / 2 could-not-evaluate, "an error is never converted into
   a verdict"; the unchanged refusal list (shallow, effective
   `info/grafts` lines, non-sha1, non-top-level, ref-named citation,
   unparseable log record, unanticipated exception) is restated so the
   section supersedes only the promisor sentences.
   The new rule is stated as a four-row table: promisor-marked or not,
   every object the audit reads local → the identical unmarked
   repository's verdict; a required object the audit reads cannot be read
   → exit 2 with a content-derived reason (never 0, never 1, never a
   guessed absence); a locally unresolved citation that names referenced
   but unavailable local content → exit 2 rather than a proved absence; a
   locally unresolved citation that names no local content → the ordinary
   failed verdict with the same finding kinds as the identical unmarked
   repository, and authorized errata still applies.
   Availability is judged per read over the objects the audit actually
   reads; a bounded missing-object traversal may diagnose one unresolved
   token but is never a blanket precondition; no remote completeness and
   no remote abbreviation uniqueness are claimed; abbreviation uniqueness
   is judged over the audited local object set only.
3. **Unclaimed leftovers explicit** — the round-23 "Open, not claimed"
   list is carried forward unchanged except for its two promisor
   sentences; added to it are the remote-completeness and remote-uniqueness
   non-claims, the exact scope of the bounded diagnostic traversal and the
   statement that a missing object reachable from a pinned root but never
   read does not block the verdict. The frozen arm's red-by-design status,
   the no-hardening / no-serving / no-higher-score boundary and the new
   grid gate row are stated.

## Alignment with sibling lanes (read, not merged)

Two sibling reports were read and their findings folded into the draft's
policy wording; no file of theirs was edited.

- `advice/CritCompleteness.md` — the promisor-backed predicate members
  (finding 5), the three absence→verdict sites including the errata
  lookup (finding 3), the F27 expectation change (finding 4), the
  precedence recommendation that unknown dominates (finding 6) and the
  local-only nature of abbreviation uniqueness (finding 8). Its finding 1
  (a closure walk is not a completeness certificate) is the reason the
  draft leaves the availability mechanism unclaimed.
- `advice/OracleMissingNonrequired.md` — the evidence roots (the pinned
  lane branch tip and the fleet `HEAD`), the rule that an `--all` walk
  would reintroduce the r23 harm class, and the pinned rows N01–N04. Its
  N03 expectation (a missing blob reachable from the selected lane branch
  ⇒ exit 2) is the reading the "root-scoped closure" alternative would
  implement; the L1 chose B instead, so that expectation does not govern.
- `advice/ScribeFrontier.md` — the corpus README half. It was rewritten to
  B after the decision: per-read availability instead of a whole-root
  precondition, the citation rule as decided, F27 keeping exit 1, F06 →
  exit 1 with the unmarked twin's findings and its `:697` reason pin
  dropped, F23 staying exit 2 with a content-derived `:704` reason, T01
  auditing clean, the withdrawn preregistration expectation reported as
  not met, the "the two halves land together" measurement carried in
  the README text. The SKILL append and the README correction therefore
  state the same policy, and the README half now names the required reads
  explicitly — the pinned lane tip, the round's lane commits, the cited
  objects, the committed fleet report, the committed `corpus/SOURCES.md`
  and the errata rows — with the bounded-traversal sentence mirroring the
  scope sentence in the SKILL table preamble, so the two documents cannot
  drift on what "required read" means.

## Findings for the L1

Written after the L1's scope decision (B) and after
`.ufo/waves/round-24/oracle-amendment-1.json`; items 2 and 3 supersede
what this report stated earlier in the wave.

1. **Retained-grid rows and reason pins move with the policy.**
   `tests/report-audit/repo-state-grid.py:697` pins F06 to the reason
   `"partial clone"` and `:704` pins F23 to `"promisor pack"`; both pins
   are now wrong, because neither refusal is metadata-based any more.
   Under decision B: F06 (`:651`, graded `fault`) — the fabricated
   citation names no local content, so the ordinary failed verdict
   applies (exit 1, `landed-unresolved` + `unresolved-full-hash`) and the
   reason pin must be dropped; the row's fault (the configured transport
   program must not run) stays graded. F23 (`:670`, graded `contract`) —
   the cited blob is referenced but unavailable, so it stays exit 2 with a
   content-derived reason instead of `"promisor pack"`. `CASES` entry
   `:689` marks T01 a `tradeoff` row (reported, never graded — `:13-14`,
   `:797`); under decision B a blobless clone whose cited lane commit is
   local audits clean, so that declared trade is withdrawn and the row's
   expectation of 0 already matches.
2. **F27 keeps exit 1 — this supersedes my earlier finding.** My earlier
   report said F27 (`:674-675`, filter-only promisor remote) should become
   exit 2. That followed CritCompleteness finding 4, which treated a
   filter-only remote as promisor-backed and therefore as a source of
   unknownness. The L1's decision and the amendment make the local-object
   contract govern: promisor metadata alone never changes a verdict, so a
   filter-only marked repository gets the same exit 1 as its unmarked
   twin. F27 needs no change.
3. **The preregistration's unknown-citation expectation is withdrawn
   prospectively, not achieved.** `.ufo/waves/round-24/oracle-amendment-1.json`
   supersedes `preregistration.json` `expected_after[3]` only: the
   requirement that an unknown citation in any metadata-marked repository
   is exit 2 is withdrawn prospectively, because it conflicts with the
   supported local-object workflow (base `tools/report-landing-audit.py`
   `:12-19`: the audited object is in the lane or fleet repository, with
   no remote-universe existence guarantee). The initial registration
   remains immutable and must be reported separately as not met, not
   relabelled passed. The draft states the prospective rule: a locally
   unresolved citation keeps the ordinary failed verdict unless it names
   content that is referenced but unavailable locally, which is exit 2.
4. **The two halves must land together.** Removing the metadata refusal
   without the availability rule converts exit 2 into false defect
   verdicts (F23-like, F06-like rows above). Any candidate that drops the
   refusal before the availability rule exists is a regression, not a
   repair.
5. **Availability is per required read, and the traversal is a
   diagnostic.** The audit reads the pinned lane tip, the round's lane
   commits, the cited objects, the committed fleet report, the committed
   `corpus/SOURCES.md` and the errata rows; a repository that is locally
   sufficient must not be refused because an unrelated historical blob, an
   unselected branch or an unused file is missing (OracleMissingNonrequired
   N01/N02/N04). A whole-root precondition is deliberately not introduced
   (Main's instruction; OracleMissingNonrequired's `--all` measurement).
6. **The exit-2 reason must be content-derived.** The grid's exit-2 rows
   pin refusal reasons, so the F23 row needs a reason that names the
   unreadable object, not the old marker text; the two exit-2 classes
   (required read failed; unresolved token naming unavailable referenced
   content) must be distinguishable in the evidence.
7. **r23 filed-evidence corrections** (69 falsify-wave lane reports, not
   68; 40 of 56 killed FIFO-process identities retained) are outside this
   lane; not touched here.

## Out of scope / not done

- No production edit by this seat: `SKILL.md`,
  `tools/report-landing-audit.py`, `tests/report-audit/*`, `LOG.md`,
  `SCORECARD.md`, `README.md` and `corpus/*` carry no change from me. Other
  seats' in-wave modifications (`corpus/SOURCES.md`, `corpus/QUALITY.md`,
  `corpus/lessons/round-24.md`) were left untouched.
- Per the L1's instruction, no production file, no grid and no frozen
  expectation was edited; the scope decision was taken by the L1 seat and
  the draft was rewritten to it.
- No candidate implementation of the availability check (AuditRepair's
  lane), no promisor grid (GridOracle's lane), no mutants.
- No commits, no pushes, no lane Git index writes; all fixtures were
  created under `/fast/scratch/hyaku/kama-r24/ScribeSkill` and in
  `tempfile` directories; the real lane and fleet repositories were only
  read.
- **Unrun / unverified:** `tests/report-audit/repo-state-grid.py --arm
  both --json`, `tests/report-audit/isolation-mutants.py`,
  `tools/report-landing-audit.py --selftest` and the preregistered
  `tests/report-audit/promisor-grid.py --arm both --json` (the grid does
  not exist yet at this base). No full-suite check was run in this wave,
  per the wave contract.
- No new source rows were registered; the draft cites the existing
  registered rows only (S101 for grafts). Source-row registration for the
  round-24 git pages belongs to the round-24 source seats.
- No installs: no tool was missing, so no package was installed and no
  channel was used.

## Artifact paths

- Advice report: `.ufo/waves/round-24/build/advice/ScribeSkill.md`
- Candidate SKILL text: `.ufo/waves/round-24/build/out/ScribeSkill/SKILL-round24-promisor-correction.md`
- Append patch: `.ufo/waves/round-24/build/out/ScribeSkill/SKILL-round24-promisor-correction.patch`
- Evidence: `…/ScribeSkill/evidence-promisor-metadata.json`,
  `…/ScribeSkill/evidence-missing-object-isolation.json`,
  `…/ScribeSkill/evidence-no-promisor-refusal-candidate.json`
- Scripts (re-runnable): `…/ScribeSkill/probe-promisor-metadata.py`,
  `…/ScribeSkill/probe-lazy-fetch-and-availability.py`,
  `…/ScribeSkill/make-no-promisor-refusal-candidate.py`
- Scratch (outside the lane): `/fast/scratch/hyaku/kama-r24/ScribeSkill/`
  (probe runs, candidate copy, patch build tree)

## Appended — round-24 instrument semantics continuation (W1 resumption)

Append-only; nothing above this section was changed. Production is pinned
at `2e254a17…` and `SKILL.md` now ends with the integrated
"## Round24 correction — local evidence, not promisor declarations"
section (lines 816–871), so this continuation is additive and states only
what that section does not: the core/grid/mutator semantics, the
supersession of the old 31-mutant gate reading, the PM08 manual no-assert
rule, the per-arm strict/loose method, and the withdrawal of the original
view.

**Draft**: `.ufo/waves/round-24/fixes/doc/ScribeSkill/append.txt` (draft
text only; no production edit, no patch applied).

**Sources read** (proposals, not assumptions): `fixes/docs-contract.txt`;
`fixes/StoreLocalPresence/README.md` and the selected v9 core
(sha256 `b9be4f42…`); `fixes/GridAttestation/README.md` and
`fixes/GridAttestationV3/README.md` (grid proposal sha256 `437128b8…`);
`fixes/MutationEvidenceV5/` and `fixes/MutationEvidenceV6/rationale-v6.md`;
production `SKILL.md:803,850,870,871`, `tests/report-audit/isolation-mutants.py`
(27 retained literals, retired M14/M22/M27/M29),
`tests/report-audit/promisor-grid.py` (sha256 `b034e159…`) and
`tests/report-audit/promisor-grid-expectations.json` (sha256
`d86b7bea…`, unchanged). The ConnSources source-curation packet was not
read or duplicated.

**Facts carried into the draft**
- Superseded registry reading: `SKILL.md:803` still reads kind `gate`
  with 31 single-literal mutants; the draft supersedes it in kind (now a
  bounded sensitivity `probe`) and in count (27 retained literals + 4
  retired ids, never reused; the historical 31 is not the current count),
  and records that the short-id selector hazard pre-existed the
  retirement.
- Per-arm method: the comparable frozen baseline is the strict 14/47
  (identical strong exit/defect/reason/name/no-verdict/acquisition rules
  in both arms); the older loose 16/47 stays filed under its own
  weaker-method label (`met_amended_frozen_loose`; PG16 and PG20 differ)
  and is not two extra product wins; the frozen historical reproduction
  47/47 is a separate measurement; the original unknown clause stays
  withdrawn and not achieved.
- PM08: one manual review note among ten executable operators — verified
  statically, never constructed, never executed, never killed; no
  permanent AST/text/wiring assertion.
- Fixture rules: blobless absence asserted immediately after the clone
  before any hydration; connected local file origins stay acquisition
  tripwires (no origin removal or repointing, no lazy forensic read);
  hydration changes input state and is not a detector repair;
  `internal_error` is captured from the full stderr, distinct from a
  content-derived refusal, and tracebacks/internal errors are unmet
  observations that cannot earn mutant kills.

**Not claimed**: no final candidate measurement, numerator, count or
landed hash; the V6 mutator's pending output-field names; the source
curation packet; any Git floor approval, score promotion or new frontier
capability.

**Unrun**: no test, grid, mutant sweep or full suite was executed in this
resumption — the draft states semantics from the proposals and the
production sources only.

## Appended again — continuation v2 (mutator delivery supplement)

Append-only; v1 (`fixes/doc/ScribeSkill/append.txt`, sha256
`804436de…`) is preserved unchanged and v2 is a minimal delta of it:
`fixes/doc/ScribeSkill/append-v2.txt` (sha256 `c494eff7…`).

What changed, and why
- **Mutator source is final.** The contract's EOF supplement names
  `fixes/MutationEvidenceV6/promisor-mutants.py` sha256 `24549daa…` as
  delivered (verified in the file). v2 drops the "V6 in preparation" and
  "pending output-field names" wording and states the delivered
  behaviour read from the source: `harness_fault()` turns a leak,
  timeout, traceback, internal error (row, arm or document boolean, with
  the `could-not-evaluate: internal:` stderr prefix as fallback), an
  invalid row exit or a malformed verdict document into
  could-not-evaluate with zero kill credit; a violation outside a
  mutant's attribution envelope is likewise could-not-evaluate, the
  out-of-envelope rows are preserved and reported, and the envelope is
  never widened; `classify_row()` classifies a credited violation from
  the row's own `expected_exit`/`exit` as `refusal-2` (over-refusal
  signal, not an availability credit), `actual-verdict` (the availability
  credit), `verdict-change` (substantive, reported separately),
  `diagnostic-only` and `unclassified` (no acceptance or availability
  credit, no class credit guessed).
- **PM08 wording.** v1 said PM08 is "verified statically"; v2 says it is
  settled by *uncredited manual source inspection* — never constructed,
  never executed, never credited with a kill, no permanent AST, text or
  wiring assertion — so no automated-looking guarantee is shipped.
- **Grid paragraph.** The V3 field names (`snapshot_unavailable2`,
  `snapshot_tampered2`, `amended_view_measured_on`) are now marked as the
  proposal's own names, not a pinned production interface.
  `fixes/GridAttestationV4/` (sha256 `8e0d5c54…`) is recorded as a
  test-fidelity proposal only and pending, keeping the V3 API and the
  47-cell manifest unchanged; it tightens the controls (a typed
  contract-violation clause instead of any setup failure, and behavioural
  stand-in controls that must and must not meet).

Unchanged in v2: the core (v9) semantics, the fixture and evidence rules,
the strict 14/loose 16 per-arm method with the original view withdrawn and
not achieved, the supersession of the old kind=`gate`/31-mutant reading by
the 27-literal probe with 4 retired ids, and the no-final-measurement
rule.

Not claimed: no final candidate number, count, verdict or landed hash; no
production write; no test or sweep was run.

## Appended again — live cutover draft (v3)

Append-only; v1 (`804436de…`) and v2 (`c494eff7…`) are preserved
unchanged and v3 is a new file: `fixes/doc/ScribeSkill/append-v3.txt`
(sha256 `08fa3752…`, 116 lines).

**Cutover form.** v3 names the canonical `tools/report-landing-audit.py`
and `tests/report-audit/…` files in the present tense, under one explicit
condition: it applies only if the L1 adopts these exact semantics in those
canonical files in the same commit that carries the text; otherwise the
round-24 sections above stand unchanged and it does not apply. Prototype
paths (`.ufo/waves/round-24/fixes/…`) appear only in a closing provenance
footnote.

**Delivered, not pending.** The grid's test-fidelity variant
(`8e0d5c54…`, same grid API) and the mutator source (`24549daa…`) are
described as delivered; no "proposed interface", "pending" or
after-metric wording survives in v3 (checked by grep: no `pending`,
`proposed`, `in preparation`, `will be`).

**`withdrawn_original_failures` clarified.** The grid's own computation
(`GridAttestationV3/promisor-grid.py`: `changed` = cells whose original
and amended expectations differ; `withdrawn = original_unmet ∩ changed`)
makes the name a legacy label for every unmet original expectation that
the amendment superseded — the amendment-changed cells, PG28 and PG34
among them — and not the literal unknown clause alone. An unmet row whose
original and amended views agree is an ordinary live failure and is not
withdrawn. v3 states exactly that, alongside `original_view_unmet`
carrying all original failures and the original unknown clause staying
withdrawn and not achieved.

**Kept from v2** (restated in the live form): the per-arm comparable
score with identical strong rules in both arms, the strict 14/47 frozen
baseline, the older loose 16/47 under its own weaker-method label
(`met_amended_frozen_loose`; PG16/PG20 differ, not two extra product
wins), the 47/47 frozen historical reproduction as a separate measurement,
the core's per-store bare presence and required-read identities, the
fixture and evidence rules, PM08 as an uncredited manual source
inspection, the mutator's fault and class semantics, and the supersession
of the old kind=`gate`/31-mutant row by the 27-literal probe with 4
retired ids.

Not claimed: no final candidate measurement, count, verdict or landed hash;
no code or policy change; no test, grid or sweep was run; production
`SKILL.md`, `tests/`, `tools/` and `corpus/` are untouched by this seat.

## Appended again — mutation taxonomy correction (v4)

Append-only; v1 (`804436de…`), v2 (`c494eff7…`) and v3 (`08fa3752…`) are
byte-preserved, and v4 is a new minimal file:
`fixes/doc/ScribeSkill/append-v4.txt` (52 lines, sha256 `3509cbf4…`).

**Selected source.** The canonical mutator source is now V7 —
`fixes/MutationEvidenceV7/promisor-mutants.py`, sha256 `7ba30ccc…`
(verified in the file), which replaces V6; the legacy isolation probe is
unchanged (`eace4f5…`), and the delivered test-fidelity grid is
`8e0d5c54…` with the same grid API and the immutable 47.

**The bug V7 fixes, as stated in the source and rationale.** V6's
`classify_row` tested the normal/normal branch before the equality branch,
so a violated row whose exit was unchanged (0 → 0, 1 → 1) was labelled
`verdict-change`. V7 compares the exits first: an exit pair alone never
shows that the whole verdict changed, because the same exit can hide a
different document.

**Taxonomy now shipped** (read from the row's own `expected_exit`/`exit`):
0→0 or 1→1 = `same-verdict-exit` (same exit; the detail may differ; no
substantive exit change and no availability claim); 0↔1 =
`verdict-change`; 0/1→2 = `refusal-2` (over-refusal signal, not an
availability credit); 2→0/1 = `actual-verdict` (the availability credit);
2→2 = `diagnostic-only` (the refusal stayed a refusal); missing or
outside 0/1/2 = `unclassified` (no class credit guessed). The
`diagnostic_only` aggregate means exclusively the same 2→2 — never same
normal exits, never unclassified — and `same-verdict-exit` rows are
reported under their own aggregate; no availability credit is guessed from
a `same-verdict-exit`, `diagnostic-only` or `unclassified` row. Runtime
faults and out-of-envelope violations stay could-not-evaluate with zero
kill credit, out-of-envelope rows are preserved and reported, the
attribution envelope is never widened, and a valid finite survival still
completes 0.

**Scope discipline.** v4 touches only the mutator provenance and the
taxonomy; it does not restate the core, grid, fixture or registry
readings, which stay as drafted in v3, and it carries the same live
condition (the L1 adopts these exact semantics in the canonical files in
the same commit that carries the text). No broader docs rewrite, no code
or policy change, no test or sweep, and no final candidate count.

## Appended again — unified final append (v5)

Append-only; v1 (`804436de…`), v2 (`c494eff7…`), v3 (`08fa3752…`) and v4
(`3509cbf4…`) are byte-preserved. v5 is one new unified file —
`fixes/doc/ScribeSkill/append-v5.txt` (133 lines, sha256 `20b2cae3…`) —
that merges v3's core/grid/fixture/registry readings with v4's corrected
taxonomy, so the two overlapping readings are never pasted together.

**Selected code now cited** (verified in the filed proposals): core v9
`b9be4f42…`; grid V5 `d2aca34a4031b332fc1d558083d27aa098768fa3a0623cfb9ae8e7cf83652469`
— V5 is V4 plus the deletion of the dead, never-referenced
`METADATA_REFUSAL` constant, with the active metadata-refusal handling
untouched (the frozen-history reason class, the manifest's per-cell
`reason_forbidden` pins and `check_exit2_form`); mutator V8
`b04c3812186e1a6c72f39f1a6a79adb632ee1efecaab687aa0d3c1fee7eed757` — V8
is V7 plus the removal of the two speculative internal-error flag aliases,
keeping only the canonical per-row `internal_error` boolean, with the V7
taxonomy, aggregates, attribution rule, harness-fault set and the
review-only PM08 note unchanged; legacy isolation probe `eace4f5…`
unchanged.

**Body form.** Present tense on the canonical files, same-commit cutover,
no conditional or unfinished "draft" prose in the body (grep for
`pending`, `proposed`, `in preparation`, `draft`, `applies only if`,
`would be` returns nothing); prototype paths appear only in the closing
provenance footnote. The single taxonomy table carries the V7 classes
(`same-verdict-exit`, `verdict-change`, `refusal-2`, `actual-verdict`,
`diagnostic-only`, `unclassified`) with the aggregates stated: the
`diagnostic_only` aggregate means exclusively the same 2 → 2, and
`same-verdict-exit` rows are reported under their own aggregate, with no
availability credit guessed from `same-verdict-exit`, `diagnostic-only` or
`unclassified` rows.

**Retained from v3 in the unified text**: the auditor's metadata
neutrality, per-store bare presence and same-canonical-object
reconciliation, selected-ledger and unselected-round handling,
required-read identities without a second diagnostic timeout on a fatal
timeout/OS cause, known-unavailable ids from all present local
commit/tree/tag roots, the opaque boundary only from the pinned audit
root, the absence of any whole-store completeness precondition, the
locally-sufficient marked repository keeping its unmarked twin's verdict,
the cited missing blob behind a dangling present tree staying
could-not-evaluate and unrelated opaque garbage plus an ordinary fake
staying an ordinary failed finding; the grid's 47 cells against the pinned
manifest bytes, the byte pin authenticating oracle identity only, the
per-arm comparable score under identical strong rules, the strict 14/47
frozen baseline, the older loose 16/47 under its own weaker-method label
(PG16/PG20 differ, not two extra product wins), the separate 47/47 frozen
historical reproduction, and `withdrawn_original_failures` as the legacy
name for the unmet original expectations the amendment superseded
(amendment-changed cells, PG28 and PG34 among them), excluding unchanged
live failures; the behavioural grid controls; the fixture and evidence
rules; and the supersession of the old kind=`gate`/31-mutant row by the
27-literal probe with 4 retired ids.

Not claimed: no final candidate measurement, count, verdict, score or
approval; no code or policy change; no new research, test, grid run or
sweep; production `SKILL.md`, `tests/`, `tools/` and `corpus/` are
untouched by this seat.
