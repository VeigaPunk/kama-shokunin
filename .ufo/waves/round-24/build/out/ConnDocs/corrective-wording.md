# ConnDocs — candidate append-only corrective wording (draft; not applied)

Seat `KamaR23-2.ConnDocs-2` (connector, leaf; no subagent dispatch). Draft only.
No production file, no `.jj`, no Git index, no commit, no push was touched.

Lane base observed: `0df800e896f6bce285a81e794ad4ae1d1e6c3a71` (preregistered
base). Working-tree state at inspection also carried uncommitted round-24
edits by L1 (`corpus/QUALITY.md` KQ35 at `:183`, `corpus/SOURCES.md` S102–S104,
`corpus/lessons/round-24.md`); those are the L1's and are not restated here.

All blocks below are **appended**. Existing text is quoted, never rewritten.
Per KQ26 (`corpus/QUALITY.md:143`) a correction names the superseded text or
revision. Precedent for the format: `corpus/lessons/round-2.md:74`
(`## Corrections — round 10 (2026-10-19)` + `*[correction …]*` lines) and
`corpus/lessons/round-21.md:114` ("Corrections to the text above (append-only;
earlier lines stay)").

Slots `⟦…⟧` are deliberately unfilled: the round-24 implementation is not
landed, and this lane runs no build/test/formatter.

---

## 0. The one distinction every block must keep

Two different things are called "a partial clone" in the round-23 text, and
the r24 repair separates them. Measured on the base fixtures
(`evidence/probe-output.txt` §4) and re-measured against the landed
AuditRepair candidate (`evidence/candidate-rowcheck.txt`):

| row | fixture | required objects local? | base outcome | candidate outcome |
|---|---|---|---|---|
| T01 | `t_blobless` (`repo-state-grid.py:596-602`), clone **with** checkout | **yes** — 0 missing objects, 2 promisor pack markers, `remote.origin.promisor=true` | exit 2 `partial clone (promisor pack)` | **exit 0 clean** — the same substantive verdict as the full clone |
| F23 | `f_promisor_pack` (`:195-213`), clone `--no-checkout` | **no** — 1 genuinely missing blob `?6e98d181…` | exit 2 `partial clone (promisor pack)` | exit 2, reason **names the missing object**: `unknown: unavailable required object: 6e98d181… is referenced by the history of … but the repository cannot serve it` |
| F27 | `f_filter_promisor` (`:482-498`), `remote.*.partialclonefilter` only | no missing object; the fabricated token is referenced by nothing | exit 1, kinds `landed-unresolved`, `unresolved-full-hash` | exit 1, **same kinds** — the fabricated token is a proved absence, metadata notwithstanding |

**Therefore no block may say "partial clones are now supported", and no block
may say "the promisor refusal is removed".** The withdrawal is of the
*metadata-alone* refusal only. T01 loses a refusal it should never have had;
F23 keeps a refusal it earns on content; F27 keeps its ordinary verdict.

### 0a. The rule is **token-scoped**, not repository-scoped — read this before drafting

The L1 has **prospectively withdrawn** preregistration `expected_after[3]`
("A missing citation in any promisor-backed repository is unknown, not proved
absent: exit2 unless resolved locally by another audited repository"), by
`.ufo/waves/round-24/oracle-amendment-1.json` (landed before the L1
inspected the candidate). The amendment's own `original_expectation_verdict`
records that the original reading "conflicts with the original supported
local-object workflow and is withdrawn prospectively, not counted as
achieved." The amended rule, in the candidate's own words
(`tools/report-landing-audit.py:57-67`):

> a citation that neither audited repository holds is still a proved absence,
> whatever the repository declares: promisor metadata alone never changes a
> verdict … The one case that is not a verdict is a citation whose content
> cannot be read … a token that names one of them, or that a missing tree or
> commit could hide, is unknown, not absent, so the audit refuses (exit 2,
> `unknown: unavailable required object`, naming the object). Missing objects
> the citation does not name are unrelated and block nothing; the diagnosis is
> never a precondition on the audit.

The amended expectation set (`tests/report-audit/promisor-grid-expectations.json`)
confirms it row by row: PG22/PG23/PG30 are amended from exit 2 to the
**ordinary failed/clean verdict**; PG34 is amended from exit 1 to exit 2 —
that is the **plain** (no metadata) twin, because the token-scoped rule
applies to every store, not only promisor-marked ones; PG25/PG37/PG42 are
controls that keep the ordinary verdict. `oracle-supplement-2.json` adds
PG46/PG47/PG48: only a missing **non-leaf** object (tree/commit) can conceal
dependency names, and only on the unresolved-citation path.

**Consequence for the drafting.** The rule a document must state is:

- promisor metadata alone never changes a verdict — the marked and unmarked
  twins keep identical substantive verdicts, including for fabricated
  citations and for the historical errata-corrected defect;
- a required object the audit actually reads, and which the local store
  cannot serve, is exit 2 with a content-derived reason that names the
  object;
- a citation the store *references but cannot serve* — or one whose absence a
  missing tree or commit could conceal — is unknown rather than proved
  absent, and is exit 2;
- an unavailable object the citation does not name is unrelated and blocks
  nothing; the availability diagnosis is never a precondition on the audit.

**A document that keeps the withdrawn "any unresolvable citation in a
promisor-backed repository is exit 2" wording would misdescribe the landed
auditor and would fail PG22/PG23/PG30.** That is the single most important
cross-document hazard this lane found, and it is invisible from the
preregistration alone.

---

## 1. `SKILL.md` — append after the round-23 section (file end, line 814)

### 1a. Callsites

| anchor | current text (abbreviated) | what it now says that r24 falsifies |
|---|---|---|
| `SKILL.md:791-793` | "a partial clone (`extensions.partialclone`, a `remote.*.promisor` that is true, or a `.promisor` marker paired with its `.pack`)" is refused with exit 2 | metadata alone ⇒ refuse. Untrue of T01, which has every cited object local. |
| `SKILL.md:796-798` | "A `remote.*.partialclonefilter`-only remote is not refused: `--no-lazy-fetch` keeps its missing objects missing (F27)" | the conclusion survives (F27 keeps its ordinary failed verdict, identical to the plain twin), but the stated *reason* is the wrong mechanism under the amended rule: the fabricated token is a proved absence because nothing references it. Re-word. |
| `SKILL.md:807` | "a `--shared` clone of a partial clone bypasses the promisor refusal" | there is no promisor refusal left to bypass; the residual is that borrowed objects resolve as local (an alternates-class open item). |
| `SKILL.md:811-813` | "Declared trades (frozen 0 → current 2 on complete repositories): a blobless partial clone (T01) and a paired promisor pack without promisor config (F23)" | T01 is not a "complete repository" in the F23 sense and must not be refused; F23 is not a complete repository at all and stays refused on content. The pair is conflated. |
| `SKILL.md:683` | the round-21 "Report landing audit" registry row | its exit-2 list ("unusable git") stays true; it needs no edit, but the round-24 registry rows must be added. |
| `SKILL.md:802-803` | the round-23 "Repository-state fault grid" and "Isolation mutants" rows | their pinned reason strings and mutant literals change with the repair (see §5 and §6) — the rows stay; their *reason/mutant* content is superseded by the new rows. |

### 1b. Candidate appended block

```markdown
## Round24 promisor completeness repair (owner: kama)

Appended; the round-23 repository-state section above stays as filed. Round 23
refused a repository on a **promisor declaration alone**: `extensions.
partialclone`, a true `remote.*.promisor`, or a `.promisor` marker beside its
`.pack`. A declaration states where objects may be fetched from later; it is
not a statement that any object is missing. Round 24 withdraws that
metadata-alone refusal and grades the **availability of the required
evidence** instead. Promisor metadata is neither a completeness certificate
nor a defect.

- A complete local promisor-marked lane or fleet clone — every required
  commit, tree, blob and committed report present locally — returns the same
  substantive finding as the otherwise identical full clone: clean, or the
  same defect kinds. It is not exit 2.
- A genuine omission before the report cutoff is still `landed-omitted`,
  exit 1, in such a clone, with the promisor metadata still present.
- A required commit, tree, blob or committed report that the audit reads and
  the local store cannot serve is exit 2 could-not-evaluate, and the reason
  names the unavailable object.
- A citation the store references but cannot serve — or one whose absence a
  missing tree or commit could conceal — is unknown rather than proved
  absent, and is exit 2.
- A citation that no audited repository holds, and that the store does not
  reference, stays a proved absence: the ordinary `unresolved-full-hash` /
  `landed-unresolved` verdict, in a promisor-marked repository exactly as in
  an unmarked one. A locally present object of the wrong type keeps its own
  verdict.
- An unavailable object the citation does not name is unrelated and blocks
  nothing: the availability diagnosis is never a precondition on the audit.

Isolation is unchanged and is not the thing that was repaired: every git
call still carries `--no-replace-objects` and `--no-lazy-fetch` with
`log.follow=false`, `log.showSignature=false`, `log.mailmap=false`,
`log.showRoot=true` and `i18n.logOutputEncoding=UTF-8`, and keeps its
per-call deadline. No transport is opened, no repository-configured program
is executed, and no lazy fetch is performed. Git ≥ 2.45 is still required.
KQ32's trusted-repository-only use is unchanged: never point the auditor at
an untrusted repository. D4 stays partial — alternates and gitfile redirects
(O01/O02), the `--shared`-of-partial borrowing channel, prefix-ambiguity
overwrite, duplicate `## Landed changes` sections, errata CR splitting, an
`--errata` naming a FIFO, the memory ceilings and the unisolated sibling
tools stay open exactly as round 23 filed them.

The round-23 numbers above describe the round-23 arm and remain as filed.
Round 24 changes the *expectation* of the promisor policy rows in the
retained grid `tests/report-audit/repo-state-grid.py` ⟦POLICY-ROWS⟧ and
grades the new paired population with `tests/report-audit/promisor-grid.py`
⟦MEASUREMENT⟧. No scalar score moves.

| Name | Kind / entry command | Verdict map | Self-test | Pinned values | Write scope | Owner |
|---|---|---|---|---|---|---|
| Promisor completeness grid | gate: `python3 tests/report-audit/promisor-grid.py --arm frozen\|current\|both [--json]` | 0 every graded row met; 1 a row not met (`--arm frozen` and `both` are 1 by design); 2 fixture premise failed or harness error | premise per builder; exit-2 rows pin the unavailable object, not a metadata marker | frozen auditor `0df800e896f6bce285a81e794ad4ae1d1e6c3a71:tools/report-landing-audit.py`; population SHA over case table and reasons ⟦SHA⟧; per-case timeout that kills the auditor's whole session | temporary fixture repos only | kama |
| Promisor policy mutants | gate: `python3 tests/report-audit/promisor-mutants.py [--json]` | 0 pristine passed and every mutant ran (kills on grid exit 1, survivors listed); 2 pristine failed, a pattern did not match once, or the grid could not evaluate a mutant | pristine run is the positive control | ⟨mutant inventory⟩ | temporary copies only | kama |

Two pins are superseded by this section. The retained grid's population
digest is now `46d66867ad5c68a1aceece646228e9c24e2e75c03526ca33bf6db901ba03da81`
— the round-23 "population SHA over case table and reasons" row above names
the digest by description and stays true, but the value published with the
round-23 measurement is superseded. And the round-23 isolation-mutant gate
(`tests/report-audit/isolation-mutants.py`, the row above) is **not
evaluable** against the repaired auditor: five of its 31 replacement patterns
are literal fragments of the code the repair changed (M14, M17, M22, M27,
M29 — M17 because the ref-shadow message moved from `{repo}` to
`{store.path}`), so it exits 2 and kills nothing. The round-24 mutant
population is `tests/report-audit/promisor-mutants.py`; the round-23 "30/31
killed" figure describes the round-23 arm and is not a round-24 result.
```

**Hazard to state in the block, not omit:** the r23
`tests/report-audit/isolation-mutants.py` cannot be run unchanged against a
repaired auditor. Its M14/M22 replacement patterns are the literal refusal
strings, and the runner aborts with exit 2 when a pattern no longer matches
exactly once (`isolation-mutants.py:119-122`; measured in
`evidence/probe-output.txt` §3). The r23 mutant row at `SKILL.md:803`
therefore describes the round-23 arm only.

---

## 2. `SCORECARD.md` — append after the round-23 section (file end, line 1188)

### 2a. Callsites

| anchor | current text (abbreviated) | what it now says that r24 falsifies |
|---|---|---|
| `SCORECARD.md:1171-1174` | "Operability is **traded, not unchanged**, on two declared states: a complete blobless partial clone (T01) and a paired promisor pack without promisor config (F23) now refuse (exit 2) where frozen gave a verdict" | the trade is withdrawn for T01 and narrowed for F23. Disclosure of a trade did not waive the no-trade rule; the r23 closure ruled the round `rejected-harmed` (`MANIFEST.json` `rounds[428]`). |
| `SCORECARD.md:1179-1183` | "Trend verdicts: … quality **improved** (KQ34, superseding rows for three defective source rows)" | the outside closure recorded `trends.quality: harmed` because a correct runnable workflow regressed. The author-side trend line is superseded, not deleted. |
| `SCORECARD.md:1185-1188` | "**Planned — supersedes earlier planned statements:** … decide with the operator whether the T01/F23 trades stand." | decided: the round-24 preregistration fixes the repair, not a choice. The planned line is overtaken. |
| `SCORECARD.md:1156-1157` | auditor sha256 `da5041a8…5af1`, grid population `f29fab8d…364a` | dated r23 pins; they stay as filed and are superseded by the r24 pins, which move (measured, §5). |

### 2b. Candidate appended block

```markdown
## Round 24 — promisor metadata is not unavailable evidence (2026-10-21)

Appended; the round-23 section above stays as filed. The round-23 author
verdict and its quality-improved trend are superseded by the outside closure
of round 23 (`MANIFEST.json` `rounds[428]`), which ruled the round
**rejected-harmed**: calibration improved, operability was harmed, and
disclosure of a trade does not waive the no-trade rule. Two filed r23
corrections carry over: the falsify wave has 69 durable lane reports, not
68, and 40 of the 56 killed FIFO-process identities were retained, not full
identity evidence.

Round 24 is one preregistered C1, calibration 7 → 7 (the lowest assigned
axis; operability 8 is the harm being repaired). The claim is narrow: a
promisor **declaration** is not evidence that an object is missing, so a
complete local promisor-marked clone keeps the substantive verdict the
identical full clone returns, while a required object the audit reads and
the store cannot serve stays exit 2 could-not-evaluate naming that object,
and a citation the store references but cannot serve — or one whose absence
a missing tree or commit could conceal — is unknown rather than proved
absent. A citation nothing holds and the store never references stays a
proved absence with the ordinary failed verdict, in a marked repository
exactly as in an unmarked one. `--no-lazy-fetch`, `--no-replace-objects`,
log and signature suppression and the per-call deadline are unchanged; no
transport is opened and no repository-configured program is executed. KQ32
stays in force. D4 stays partial.

| C1 component | Before (frozen `0df800e8`) → after (current) | Counting command | Evidence |
|---|---|---|---|
| Complete local promisor-marked lane and fleet clones, same substantive finding as the identical full clone | ⟦MEASUREMENT⟧ | `python3 tests/report-audit/promisor-grid.py --arm both --json` | `.ufo/waves/round-24/final/` |
| Genuine pre-cutoff omission in a promisor-marked clone | ⟦MEASUREMENT⟧ | same | same |
| Required commit / tree / blob / committed report the audit reads and the store cannot serve | exit 2 could-not-evaluate naming the object, never a clean or failed verdict | same | same |
| Citation the store references but cannot serve, or one a missing tree or commit could conceal | exit 2 (unknown) | same | same |
| Citation nothing holds and the store never references | the ordinary `unresolved-full-hash` / `landed-unresolved` verdict — identical to the unmarked twin | same | same |
| Isolation, log/signature suppression, timeout, no transport, no repository program | unchanged | `python3 tests/report-audit/promisor-mutants.py --json`; `python3 tools/report-landing-audit.py --selftest` | same |
| Historical ledger rounds 10–⟦N⟧ and `--no-errata` parity, frozen vs current | ⟦MEASUREMENT⟧ | recipe `nh-history-parity` | same |

Not a score increase and not a D4 advance. D4 remains partial: alternates
and gitfile redirects, the `--shared`-of-partial borrowing channel, second
Landed section, ambiguity overwrite, errata CR, `--errata` FIFO, memory
ceilings and the unisolated sibling gates stay open. The round-23 numbers
in the section above stay as filed; the round-24 pins are the ones measured
here, and they move because the grid's pinned refusal reasons and policy-row
kinds move with the repair. Two pins are therefore superseded by this
section: the retained grid's population digest is now
`46d66867ad5c68a1aceece646228e9c24e2e75c03526ca33bf6db901ba03da81`, not the
`f29fab8d…364a` quoted above, and the round-23 isolation-mutant gate is
**not evaluable** against the repaired auditor — five of its 31 replacement
patterns are literal fragments of the code the repair changed (M14, M17,
M22, M27, M29), so it exits 2 and kills nothing. The round-24 mutant
population is `tests/report-audit/promisor-mutants.py`; the round-23 "30/31
killed" figure above describes the round-23 arm and is not a round-24 result.
```

---

## 3. `corpus/README.md` — append after `## Frontier disposition — round 23` (file end, line 335)

### 3a. Callsites

| anchor | current text (abbreviated) | what it now says that r24 falsifies |
|---|---|---|
| `corpus/README.md:330-332` | "Declared trade: a complete blobless partial clone or paired promisor pack is refused where frozen gave a verdict." | the trade is withdrawn for the complete clone and narrowed to the genuinely-absent case. |
| `corpus/README.md:326-329` | the open list (alternates, gitfile, `--shared`-of-partial, ambiguity, duplicate sections, errata CR, `--errata` FIFO, memory ceilings, unisolated siblings) | stays open; the `--shared`-of-partial entry must be re-worded as a borrowing channel, since there is no promisor refusal left to bypass. |
| `corpus/README.md:320-322` | "26 fault, 4 contract and 13 control rows; frozen meets 0/26 faults, current 26/26" | a dated r23 count; it stays as filed. The r24 grid is a separate population with its own counts. |

`README.md` at the lane root (14 lines) contains **no** partial-clone
statement and needs no change.

### 3b. Candidate appended block

```markdown
## Frontier disposition — round 24 correction (appended)

Appended; the round-23 section above stays as filed. The round-23 reading —
a partial clone, or a paired promisor pack, is refused, so a complete local
promisor-marked repository can only return could-not-evaluate — is withdrawn
as a policy reading. Promisor metadata (`extensions.partialclone`, a true
`remote.*.promisor`, a `remote.*.partialclonefilter`, a `.promisor` marker
beside its `.pack`) states where objects may come from; it is not evidence
that an object is missing. The verdict follows the availability of the
required evidence:

- a complete local promisor-marked lane or fleet clone with valid cited
  commits returns the same substantive finding as the otherwise identical
  full clone — clean, or the same defect set — and not exit 2;
- a genuine omission in such a clone is still `landed-omitted`, exit 1, with
  promisor metadata present;
- a required commit, tree, blob or fleet report that the audit reads and the
  local store cannot serve is exit 2 could-not-evaluate naming the object,
  never a clean or a failed verdict;
- a citation the store references but cannot serve, or one whose absence a
  missing tree or commit could conceal, is unknown rather than proved absent
  and is exit 2;
- a citation no audited repository holds and that the store does not
  reference stays a proved absence with the ordinary `unresolved-full-hash` /
  `landed-unresolved` verdict, in a promisor-marked repository exactly as in
  an unmarked one;
- an unavailable object the citation does not name is unrelated and blocks
  nothing.

Isolation is unchanged: every git call still carries `--no-replace-objects`
and `--no-lazy-fetch` with `log.follow=false`, `log.showSignature=false`,
`log.mailmap=false`, `log.showRoot=true` and
`i18n.logOutputEncoding=UTF-8`, and keeps its per-call deadline. No
transport is opened and no repository-configured program is executed.

The round-23 row counts above describe the round-23 arm and remain as
filed. Round 24 changes only the promisor policy rows' expectations in the
retained grid `tests/report-audit/repo-state-grid.py` ⟦POLICY-ROWS⟧; every
other row's expectation is unchanged, and the new promisor policy rows are
graded by `tests/report-audit/promisor-grid.py` ⟦MEASUREMENT⟧.

D4 remains partial. This is not untrusted-repository safety and closes none
of the round-23 open items: objects borrowed through `objects/info/
alternates` or a `.git` gitfile redirect still resolve as local (O01/O02), a
`--shared` clone still borrows the source's objects, prefix-ambiguity
overwrite, duplicate `## Landed changes` sections, errata CR splitting, an
`--errata` naming a FIFO, the memory ceilings, and the unisolated sibling
tools `citation-provenance.py` and `sources-append-only.py` stay open. D4
local-Git-config/history and UTF-8 hardening remains frontier.

No new serving capability: no endpoint sample, no service restoration, no
new knowledge or consumer surface. Other frontier unchanged: external-
system-library identity, receipt-header minimization, historical crash-as-
kill leaves, K05/other-engine serving and real registered-consumer
reconciliation.
```

---

## 4. `corpus/lessons/` — two appends, no edits

### 4a. `corpus/lessons/round-23.md` — append at file end (line 209), corrections only

The round-23 lesson is filed evidence. Its trade sentences are **not**
rewritten; a correction block names them, following
`corpus/lessons/round-2.md:74` and KQ26.

```markdown
## Corrections — round 24 (2026-10-21)

*[correction 2026-10-21 (round 24): the line above reading "Declared
tradeoffs: partial clones and shallow clones are refused even when every
cited object is local (grid T01; RevCalibrationAxis, CritNoHarm)" and the
paragraph above reading "a complete blobless partial clone (T01) and a
paired promisor pack without promisor config (F23) are refused (exit 2)
where frozen gave a verdict" are superseded. The refusal they describe was
conditioned on a metadata declaration alone, and the outside closure of
round 23 ruled the round rejected-harmed (MANIFEST rounds[428]); disclosure
of a trade did not waive the no-trade rule. The two rows are also not the
same kind of case: on the base fixture T01 clones **with** checkout and
holds every required object locally (0 missing objects), while F23 clones
`--no-checkout` and one reachable blob is genuinely absent. Round 24
therefore withdraws the T01 refusal and keeps an F23-shaped refusal on the
absent object rather than on the marker. The shallow-clone refusal, the
info/grafts refusal, the non-sha1 and non-top-level refusals, the
`--no-lazy-fetch` floor (git ≥ 2.45) and the unclaimed open items are
unchanged. The measurement block above also carries two superseded pins: the
retained grid's population digest is now
`46d66867ad5c68a1aceece646228e9c24e2e75c03526ca33bf6db901ba03da81`, not
`f29fab8d…364a`, because the promisor policy rows' expectations and pinned
reasons changed; and the "31 mutants, 30 killed" figure describes the
round-23 arm only — the round-23 isolation-mutant file is not evaluable
against the repaired auditor (five of its replacement patterns are literal
fragments of the code the repair changed), so it exits 2 and kills nothing.
Superseding text: `corpus/lessons/round-24.md`.]*
```

### 4b. `corpus/lessons/round-24.md` — append at file end (line 61)

```markdown
### Cross-document correction targets (appended)

The round-24 reading of "a partial clone" splits the round-23 case pair, and
the split is a property of the fixtures, not of the wording. Measured on the
base grid: `t_blobless` (T01) clones with checkout, so every required object
is local and the clone carries only metadata; `f_promisor_pack` (F23) clones
`--no-checkout` and one reachable blob is genuinely absent. The correction
therefore withdraws the metadata-alone refusal (T01's harm) while keeping an
availability refusal (F23's case), and the r24 grid must keep the two rows
distinct — never repin T01 to a refused ungraded trade by assuming every
blobless clone is incomplete.

Three document surfaces must move together with the code, and each move is
observable outside the code:

1. the retained grid's pinned refusal reasons and policy-row kinds change,
   so its population digest changes and every document that pins it
   (`SKILL.md:802`, `SCORECARD.md:1156-1157`, this file's own round-23
   measurement block) is superseded by a new pin, not re-read;
2. `tests/report-audit/isolation-mutants.py` cannot be run unchanged
   against a repaired auditor, because M14/M22 match the literal refusal
   strings and the runner exits 2 when a pattern no longer matches exactly
   once;
3. the grid's `REASONS` pins for the promisor rows must name the
   unavailable object, not the metadata, or the row's own pinned-reason
   check credits the wrong cause.
```

---

## 5. `corpus/knowledge/error-is-not-a-verdict.md` — append at file end (line 80)

**Search result to record: the knowledge corpus contains no blanket
partial-clone refusal statement at all** — 0 hits for
`promisor|partial.?clone|blob:none|lazy.?fetch` across all 18 files in
`corpus/knowledge/`. There is therefore nothing there to retract; the
round-24 work is an addition, and the existing round-23 deepening block
(`:55-80`) stays as filed. `README.md` at the lane root likewise has 0 hits.

```markdown
## Round-24 deepening — unsupported input versus a supported complete state

Appended 2026-10-21 (round 24); the frontmatter above describes the round-20
sources and the block above describes round 23. A gate that refuses its
input is not thereby right about the world. Two refusals are
indistinguishable in their exit code and opposite in their meaning: the
refusal of an input the gate cannot support, and the refusal of a complete,
supported input because the gate read a declaration as a fact.

Round 23 shipped the second kind. The report-landing auditor refused any
repository that declared a promisor remote, so a complete local clone whose
cited objects were all present returned could-not-evaluate instead of the
verdict the identical full clone returned. The outside closure of round 23
ruled the round rejected-harmed: a disclosed trade is still a lost
workflow. The lesson for a gate is therefore not "refuse more" or "refuse
less" but "refuse on the state of the thing the verdict is about": the
availability of the required evidence, measured locally, never the
configuration that says where evidence might be fetched from.

The symmetry is the rule. A required commit, tree, blob or report that the
audit reads and the local store cannot serve is could-not-evaluate, and the
reason names the absent object; a citation the store references but cannot
serve, or one whose absence a missing tree or commit could conceal, is
unknown rather than proved absent; and the same repository, with the same
metadata, that holds every required object locally is audited normally and
may be clean or may fail on its own merits. A citation that nothing holds
and that the store never references stays a proved absence, in a
promisor-marked repository exactly as in an unmarked one; and an unavailable
object the citation does not name blocks nothing. Safe isolation is not an
availability proof: `--no-lazy-fetch` keeps a missing object missing, and
keeping it missing is what makes the absence observable — it is not a reason
to refuse the whole repository. Errors are still never verdicts, and a
refusal still names its cause.
```

---

## 5a. The policy-row expectation changes the documents must record (measured)

Measured with the **landed candidate** as `--current` against the retained r23
grid (`evidence/candidate-rowcheck.txt`). These are the "policy rows" whose
expectation the round-24 text has to name; the preregistration's measurement
line already requires "retained historical r23 grid with explicitly
documented policy-row expectation changes".

**The L1 has already applied these re-pins** in the working tree
`tests/report-audit/repo-state-grid.py` (F06 → exit 1 with the ordinary
findings, F23 → the content-derived reason, T01 → `control`, both metadata
`REASONS` entries dropped). The table below is therefore the *measured* basis
of the landed re-pin, and the document-visible consequence is the moved
population digest, not the re-pin itself.

| r23 row | kind | r23 expectation | candidate outcome | change |
|---|---|---|---|---|
| `F06-lazy-fetch-command` | fault | exit 2, reason `"partial clone"` | **exit 1**, kinds `landed-unresolved`, `unresolved-full-hash` | **exit code and reason change.** The metadata refusal is withdrawn, so the fabricated cited token is a proved absence; the row's execution-channel check (no `core.sshCommand` marker) still holds, and the candidate creates no marker. |
| `F23-promisor-pack-without-config` | contract | exit 2, reason `"promisor pack"` | exit 2, reason `unknown: unavailable required object: 6e98d181… is referenced by the history of … but the repository cannot serve it` | **reason changes** from a metadata marker to the named unavailable object. Exit code unchanged. |
| `F27-filter-only-promisor-remote` | fault | exit 1, kinds `[landed-unresolved, unresolved-full-hash]` | exit 1, **same kinds** | unchanged. |
| `C09-promisor-false-config` | control | exit 0 | exit 0 | unchanged. |
| `C10-orphan-promisor-marker` | control | exit 0 | exit 0 | unchanged. |
| `T01-blobless-partial-clone` | tradeoff → **control** | exit 0 (**ungraded** in r23) | **exit 0** | the r23 harm is repaired: the row now meets its own expectation, and the L1 re-grades it as a control. |

Two pins follow, and both are document-visible:

1. `REASONS` in `tests/report-audit/repo-state-grid.py` no longer pins the
   two metadata reasons; the new grid's own check
   (`tests/report-audit/promisor-grid.py:756`) fails any current-arm refusal
   whose reason is the r23 metadata refusal, so the re-pin is mandatory.
2. **The grid's population digest moved.** `population()`
   (`repo-state-grid.py:711-714`) hashes the pinned reason and each row's
   `kind` and expected exit. Recomputed from the landed file:
   **`46d66867ad5c68a1aceece646228e9c24e2e75c03526ca33bf6db901ba03da81`**.
   The previously published value was
   `f29fab8d9af1d02de7f6fa4c7b39b2307113d3716fd4b11cffdd0cd65d55364a`
   (reproduced exactly by this lane from the base file, and quoted at
   `SKILL.md:802`, `SCORECARD.md:1156-1157` and
   `corpus/lessons/round-23.md:113`). `SCORECARD.md:1156-1157` still quotes
   the old value and has not been touched; `corpus/lessons/round-23.md:113` is
   filed evidence and needs an appended note, not an edit; `SKILL.md:802`
   names the digest by description and stays true. **The round-24 documents
   must publish the new pin.**

**The F23 exit 2 is now earned on content, not on metadata** — the reason
string names the object. That is the whole point of the repair, and it is the
string the documents should quote.

### 5a-i. The r23 isolation-mutant gate is live-broken and no document says so

Against the **landed** auditor, five of `isolation-mutants.py`'s 31 patterns
no longer match exactly once — M14, M17, M22, M27, M29 — and the runner
aborts:

```
$ python3 tests/report-audit/isolation-mutants.py --json --only M14-promisor-config
could-not-evaluate: M14-promisor-config: pattern matches 0 times
EXIT=2
```

M14/M22/M27/M29 target the promisor refusal code the repair removed. **M17 is
the second-order one**: its pattern is the ref-shadow message
`raise EvalError(f"{repo}: citation {token} names a ref")`, and the repair
moved that message to `{store.path}`
(`tools/report-landing-audit.py:235`). A reviewer reasoning only about "the
promisor mutants" would not expect M17 to break.

`SKILL.md:803` still registers that gate as a live instrument ("31
single-literal mutants of the auditor"), and `SCORECARD.md:1166` still
presents "30/31 killed" as the standing figure. Until the round-24 mutant
population (`tests/report-audit/promisor-mutants.py`, `MutationOracle`'s
seat, not yet landed) replaces it, the round-24 text must say that the r23
mutant gate is **not evaluable against the repaired auditor** — otherwise a
reader who runs it sees exit 2 and may read it as a broken candidate, or
worse, credit the r23 figure to the repaired auditor.

---

## 6. Code-side callsites the wording must match (not changed here)

| file:line | what it is | why the documents are bound to it |
|---|---|---|
| `tools/report-landing-audit.py:438-466` | `check_history_repo` — the two blanket refusals (`:455-457` promisor pack, `:462-465` `extensions.partialclone` / true `remote.*.promisor`) and the shallow/grafts/non-sha1/non-top-level refusals that stay | the source of every `SKILL.md:788-798` and `corpus/lessons/round-23.md:75-78` refusal sentence. Owned by the `AuditRepair` seat; its module docstring (`:42-55`) repeats the same list and must move with it. |
| `tools/report-landing-audit.py:139-174`, `:335-342` | `lookup` — the only path that turns absence into a verdict (`unresolved-full-hash`, `landed-unresolved`, and the errata-correction lookup at `:405-412`) | the three sites where "unknown" must be distinguished from "absent". |
| `tests/report-audit/repo-state-grid.py:695-708` | the `REASONS` map — `F06` pins `"partial clone"`, `F23` pins `"promisor pack"` | the pinned reason is the row's kill condition (`:749-753`). Re-pinning the reason to the missing object changes the population digest. |
| `tests/report-audit/repo-state-grid.py:651,670,674,689` | `F06` fault exit 2, `F23` contract exit 2, `F27` fault exit 1, `T01` tradeoff exit 0 (ungraded, `:13-14`) | these four rows are the policy rows whose expectations move. `T01`'s `kind` participates in the population digest (`:711-714`). |
| `tests/report-audit/isolation-mutants.py:46-47,64-65,75,78-79` | `M14`, `M22`, `M27`, `M29` — the mutants that remove the promisor refusals | their replacement patterns are the literal refusal strings; the runner aborts with exit 2 when a pattern stops matching exactly once (`:119-122`). Measured: variant A breaks M14+M22; variant B breaks M13+M14+M22+M27+M29. |
| `tests/report-audit/repo-state-grid.py:711-714` | `population()` — SHA-256 over name, kind, builder, expected exit, expected kinds and the pinned reason | the digest `f29fab8d…364a` pinned at `SKILL.md:802`, `SCORECARD.md:1156-1157` and `corpus/lessons/round-23.md:113`. Reproduced exactly by this lane's recomputation; it moves with any reason or kind re-pin (measured: F23 reason re-pin → `0e280a7c…`; T01 kind → `3164a39e…`). |
