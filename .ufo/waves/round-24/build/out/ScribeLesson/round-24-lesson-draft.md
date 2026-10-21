# kama — round 24 lesson — DRAFT (Gate/Mistakes structure)

DRAFT — scribe output under `.ufo/waves/round-24/build/out/ScribeLesson/`. Not the corpus lesson.
Do not copy into `corpus/lessons/` without L1 integration.

Author: scribe seat `KamaR23-2.ScribeLesson-2` (leaf member; no subagent dispatch).
Round base: `0df800e896f6bce285a81e794ad4ae1d1e6c3a71` (git 2.56.0, Python 3.14.8).
Assigned axis: C1 calibration 7→7 (lowest assigned non-retired axis); operability harm repair.
L1 holds the canonical planner seat; this draft is advice only.

Everything below is derived from files already in the base tree plus four official
git documentation pages opened by this scribe on 2026-10-21 (quotes and digests in
§Gate). No lane, fleet, corpus, tool, config or Git-index file was written; no
build, test, formatter or grid run was executed; no network transport was used
(the only network access was plain HTTPS reads of git-scm.com manual pages).

---

## Declared claim (draft text for the L1)

**C1 — calibration 7→7, operability harm repair: promisor *metadata* is not
*unavailable evidence*.** At base `0df800e` the report-landing auditor refuses a
repository whose configuration or pack set merely *declares* a promisor remote,
so a complete, locally fully-populated promisor-marked lane or fleet clone —
identical in content to an otherwise ordinary full clone — is answered
`could-not-evaluate` (exit 2) instead of its correct substantive verdict
(clean / failed). The round-24 claim restores those verdicts and keeps every
r23 isolation guarantee:

- a repository is judged on the **availability of the evidence it needs**, not on
  the presence of promisor metadata;
- a **required** object (cited commit, report tree/blob, pre-cutoff history
  commit) that is genuinely absent is `could-not-evaluate` (exit 2) — never a
  clean or failed verdict, and never a guessed absence;
- an **unknown citation** in a promisor-backed repository is unknown (exit 2)
  unless it is resolved locally by another audited repository;
- `--no-lazy-fetch`, `--no-replace-objects`, the log/signature suppression set
  and the per-call git deadline stay in force on every git invocation.

Scope is unchanged from r23: this is narrow D4 movement on the trusted
lane/fleet repositories, not untrusted-repository hardening. KQ32 stays in
force; KQ34 (crosswalk that is not self-selecting) governs how the claim is
credited.

Measured form (L1's to fix): a finite grid
`tests/report-audit/promisor-grid.py --arm both --json` (frozen = r23 base
`0df800e`), full-clone and metadata-marked pairs, plus the retained r23 grid
with **explicitly documented policy-row expectation changes** and a
non-promisor no-harm check; selftest and historical parity; mutation
sensitivity. Not claimed: arbitrary untrusted repositories, closure of the
inherited parser/alternates/gitfile/size-limit findings, live serving
capability, a higher scalar score.

---

## Gate

### Gate rows carried from round 23 (status unchanged; not re-opened here)

These rows already anchor the r23 isolation mechanisms that round 24 must
preserve. This draft does not change their status, anchor, teaches or
recheck, and does not re-quote them (the text stays in
`corpus/lessons/round-23.md` §Gate).

| Row | Source | What it anchors in round 24 |
|---|---|---|
| S089 | git(1) global options | `--no-replace-objects`, `--no-lazy-fetch` must survive the repair (both are global options placed before the subcommand) |
| S090 | git-replace(1) | replacement refs apply by default; the repair must not re-enable them |
| S093 | git-log(1) | log text need not be valid UTF-8 (`--encoding` fallback); `log.follow` |
| S094 | gitrepository-layout(5) | `info/grafts`, `shallow`, `refs/replace`, `objects/info/alternates` (O01 remains open) |
| S096 / S097 / S098 | Python `bytes.decode` / `subprocess` / `io.TextIOWrapper` | bytes-mode strict decode of git output; an undecodable output stays exit 2 |
| S099 | partial-clone(1) §Handling Missing Objects | "no check as to whether the missing object is actually a promisor object is performed" — the reason a missing-object lookup in a promisor repository is not evidence of absence |
| S100 | git-config(1) log/transport/signature keys | `i18n.logOutputEncoding`, `log.follow`, `log.showRoot`, `log.showSignature`, `log.mailmap`, `core.sshCommand`, `gpg.program` |
| S101 | git v2.56.0 `commit.c` `read_graft_line` | only non-blank, non-`#` grafts lines can rewrite history (r23 M6 repair) |

Superseded rows stay superseded and are not revived by this draft: **S091**
(superseded by S100), **S092** (superseded by S099), **S095** (rejected,
superseded by S096).

### New candidate rows opened by this scribe on 2026-10-21

Proposed ids are provisional; the L1 assigns final ids and appends the rows to
`corpus/SOURCES.md` under KQ22/KQ31 (new rows only — no in-place edit of an
existing row's scope). Each quote is located by exact string match on the
fetched page; each page reports "last updated in 2.56.0", the host git version.

- **S102 (candidate) — git-rev-list(1) missing-object enumeration.**
  URL `https://git-scm.com/docs/git-rev-list` (page sha256 `6eca09d9ef21dd42…`,
  "git-rev-list last updated in 2.56.0").
  Anchor: `--missing=<missing-action>`.
  Quote (≤25 words): "will also print a list of the missing objects. Object IDs
  are prefixed with a "?" character."
  Second quote: "will only allow object traversal to continue for EXPECTED
  promisor missing objects."
  Teaches: a repository's missing objects can be *enumerated locally* without
  fetching, and git itself distinguishes "expected" promisor missing objects
  from unexpected ones. This is the mechanism that turns "is the required
  evidence present?" into a local question instead of a metadata question.

- **S103 (candidate) — git-cat-file(1) per-object availability.**
  URL `https://git-scm.com/docs/git-cat-file` (page sha256 `539830429faea901…`,
  "git-cat-file last updated in 2.56.0").
  Anchor: `--batch-check` / `--batch-all-objects`, and the missing-object output.
  Quote: "If a name is specified on stdin that cannot be resolved to an object
  in the repository" … "print: <object> SP missing LF".
  Teaches: the presence and type of a named object can be checked without
  reading its content, and absence is reported as `missing` rather than as a
  failure of the object.

- **S104 (candidate) — git-config(1) promisor/partial-clone keys.**
  URL `https://git-scm.com/docs/git-config` (page sha256 `5a63888b1c15a172…`,
  "git-config last updated in 2.56.0").
  Anchors: `extensions.partialClone`, `remote.<name>.promisor`,
  `remote.<name>.partialclonefilter`.
  Quotes: "Such a remote is called a "promisor remote" and it promises that all
  such omitted objects can be fetched from it in the future." (24 words) and
  "When set to true, this remote will be used to fetch promisor objects."
  Teaches: these keys declare *where missing objects may be fetched from
  later*. Their presence is a promise about the future, not a statement that
  anything is missing now. This is the row that anchors the round-24
  discrimination directly in the manual rather than only in a grid
  observation.

- **S105 (candidate) — partial-clone(1) promisor-remote configuration list.**
  URL `https://git-scm.com/docs/partial-clone` (page sha256 `8a6493225f76dba8…`,
  "partial-clone last updated in 2.56.0"; same page as S099, different scope).
  Anchor: §Partial Clone, the list of promisor-remoteness configuration keys.
  Quote: "Remotes that are considered "promisor" remotes are those specified by
  the following configuration variables".
  Teaches: promisor-ness is exactly a configuration declaration
  (`extensions.partialClone`, `remote.<name>.promisor`,
  `remote.<name>.partialCloneFilter`), i.e. metadata.

Rejected candidates (recorded so the L1 does not re-open them):

- **git-config(1) as the source for `extensions.partialClone` spelled exactly
  that way.** The page renders the key with its section and variable in
  separate markup, so a literal search for `extensions.partialClone` misses
  it; the entry exists (§`extensions.partialClone`, "When enabled, indicates
  that the repo was created with a partial clone …"). Use S104 with the
  rendered entry as the anchor, not a raw-string search.
- **A source row for "git config prints key names lower-cased".** This is a
  local observation of git 2.56.0 behaviour, not a documented contract; it
  belongs in the grid/mistake evidence, not in the Gate. Observed here:
  `git config --list` printed `extensions.partialclone=origin` (all lower case)
  for a repository configured with `extensions.partialClone=origin`, so the
  auditor's lower-case comparison of the key name matches what git prints.

Local (non-Gate) evidence gathered by this scribe, offline, in a scratch
repository under `/fast/scratch/hyaku/kama-r24/ScribeLesson/.scratch/` (no
remote contacted, `example.invalid` only as an inert URL):

- `git --no-lazy-fetch rev-list --objects --missing=print HEAD` printed
  `?ce013625030ba8dba906f756967f9e9ca394464a` for a blob whose loose object
  file had been removed from a promisor-marked repository, and returned
  immediately without any fetch attempt.
- `git --no-lazy-fetch cat-file --batch-check` printed
  `ce013625030ba8dba906f756967f9e9ca394464a missing` for the same object;
  `git --no-lazy-fetch cat-file -e <oid>` exited 1.
  These confirm the mechanism the new Gate rows describe; they are **not** a
  lane measurement and no exit/finding expectation is claimed from them.

### Gate obligations the round-24 lesson must state (for the L1 to bind)

1. Every exit-2 refusal keeps a **pinned reason string** (KQ34). The r23
   reason strings `partial clone (promisor pack)` and `partial clone (<key>)`
   are no longer available as *metadata* refusals; if they remain for the
   genuinely-unavailable case they need new, distinct reasons so that
   "metadata present" and "evidence absent" cannot be confused in the grid.
2. The r23 grid rows whose *expectation* changes (r23 F23 promisor-pack
   without config, and the r23 T01 blobless trade row) are **policy rows**:
   the change of expectation must be written down explicitly in the lesson,
   with the old expectation, the new expectation and the reason. KQ34 forbids
   crediting the repair through a self-selecting crosswalk.
3. The round-24 claim does not widen KQ32: the new rows are used to decide
   *availability*, never to promise safety for arbitrary repositories.

---

## Mistakes

### Carried from round 23 — status: fixed, evidence unchanged (no re-claim)

These are the r23 mistakes whose fixes must survive the round-24 repair. The
rows below restate only the pointer and the status; the authoritative text
stays in `corpus/lessons/round-23.md` (append-only).

| # | Class | Status at base `0df800e` | Where the fix lives |
|---|---|---|---|
| M1 | Instrument self-exemption: isolation/exit promises were never in the gate's own fault population | fixed (r23 grid + mutants) | `tools/report-landing-audit.py:93-96` (`GIT_ISOLATION`), `tests/report-audit/repo-state-grid.py`, `tests/report-audit/isolation-mutants.py`; QUALITY KQ34 |
| M2 | Unchecked fixture premise (a cell can "pass" with no fault present) | fixed (every builder `require()`s its premise; a failed premise exits 2) | r23 lesson M2; KQ30 |
| M3 | Operator-shell leak (`GIT_CONFIG_GLOBAL` exported into the persistent shell) | fixed (per-command environment) | r23 lesson M3 |
| M4 | Seat wrote fault fixtures into the real fleet repository (four `.promisor` markers) | fixed (markers removed; C10 orphan-marker control) | r23 lesson M4 |
| M5 | Seat misroot (scribe report written under the fleet root) | fixed (moved byte-exact into the lane; fleet copies removed) | r23 lesson M5 |
| M6 | Over-refusal shipped as isolation (comment-only `info/grafts` refused) | fixed (C13 control + `grafts_effective`, S101) | `tools/report-landing-audit.py:468-478`; r23 lesson M6 |
| M7 | Harness leak (grid timeout left blocked git children) | fixed (per-session auditor; 0 such processes remained) | `tests/report-audit/repo-state-grid.py` `run_case`; r23 lesson M7 — **count corrected below** |

Fixed known harms that round 24 must not regress (r23 lesson lines 112–121,
measured in a clean clone of `e876b953e9da28d2dffd29c923052bc626148c27`):
current arm `faults 26/26, contracts 4/4, controls 13/13, tracebacks 0,
executed 0, timeouts 0`; frozen arm `faults 0/26, contracts 1/4, controls
13/13, tracebacks 9, executed 3, timeouts 2`; mutants `31, 30 killed`;
selftest `50/50`. Honesty note carried forward: "faults 26/26" certified the
r23 *refusal* as a met fault — it did not certify that refusing a complete
promisor-marked repository was correct. The r24 lesson must not read the r23
count as evidence for the r23 trade.

### New in round 24

| # | class | evidence pointer | captured-by | fix / failure witness |
|---|---|---|---|---|
| M8 | Over-refusal shipped as isolation (second instance): a *metadata* declaration was treated as evidence of unavailability, so a complete promisor-marked clone with every cited object local was answered `could-not-evaluate` instead of its correct verdict. Same class as r23 M6, different channel | `tools/report-landing-audit.py:438-465` at base `0df800e`: `check_history_repo` raises `partial clone (promisor pack)` (`:455-457`) for any `*.promisor` pack beside its `.pack`, and `partial clone (<key>)` (`:458-465`) for `extensions.partialclone` or any `remote.*.promisor`; `.ufo/waves/round-23/build/advice/RevCalibrationAxis.md:57` ("TRADE: partial clone, every cited object local \| exit 0, clean, req 1 \| exit 2, 'partial clone (extensions.partialclone)' \| clean input flips to refusal (H2)") and `:72`; `RevSkillText.md:51` (committed e0f0434 exit 2 where frozen 4fe9339 gives exit 0 clean) and `:323` (T01: candidate exit 2, frozen exit 0 clean); `RevFrozenArm.md:82-84`; `RevLookup.md:73-75` ("a benign `file://` partial clone was `found` in base and is now refused"); `RevProbeScript.md:15` (F-4: the preflight refusal is a policy choice that needs explicit sign-off); `SentinelExecChannels.md:24-26`; r23 lesson lines 84 and 207-208 (the trade was *declared*, not graded) | none in r23 — the r23 grid encoded the refusal as the *expected* outcome (F23 and the T01 trade row), so the grid could not detect the harm; KQ34's "channel is reported open" branch was not used | decide availability per required object, not per configuration key; a metadata-marked repository with complete local evidence must produce the same substantive verdict as the otherwise identical full clone; the r23 F23/T01 expectation change is written down as a policy-row change with the old and new expectation |
| M9 | Refusal-scope inversion after the repair: once metadata stops refusing, an object that is *genuinely absent* can be read as "absent from history" — i.e. as a clean or failed verdict instead of a refusal. Absence of evidence must never become evidence of absence | base `0df800e` `tools/report-landing-audit.py:438-465` (the current check refuses on metadata, so no per-object availability check exists to invert); r23 lesson line 76 (the refusal list) and line 84 (T01 trade); round-24 preregistration `expected_after` items 3 and 4 | the r24 grid rows for a missing lane blob, missing fleet report, missing lane tree, missing fleet tree, missing ancestor, unknown citation, unreachable citation and cross-repo found citation (round-24 seats CaseMissing*/CaseUnknownCitation/CaseCrossRepoFound) | a required object that is missing is exit 2 `could-not-evaluate` with a pinned reason; an unknown citation in a promisor-backed repository is unknown (exit 2) unless resolved locally by another audited repository; a non-promisor no-harm check keeps the existing verdicts unchanged |
| M10 | Repair must not re-open the execution channel: dropping the metadata refusal could let a promisor-marked repository trigger the promisor remote's transport (a repository-configured `core.sshCommand`) when a required object is absent | base `0df800e` `tools/report-landing-audit.py:93-96` (`GIT_ISOLATION` carries `--no-lazy-fetch`), `:111-133` (`git()` runs every call with `GIT_ISOLATION` and a 20 s deadline), `:108` (`GIT_TIMEOUT = 20`); `SentinelExecChannels.md:24-26` ("Retain `--no-lazy-fetch` on every Git invocation"); `RevLookup.md:73` (promisor exec: base `sshCommand ran=True`, latest `False`, both `missing`); r23 grid F27 (`filter-only promisor remote`) | r23 F27 row (graded) and the r23 mutants; the round-24 grid must re-grade it against the repaired code | every git invocation keeps `--no-lazy-fetch`, `--no-replace-objects` and the log/signature suppression set; a promisor-marked repository whose required object is missing answers exit 2 with **no** transport marker created |

### Corrections (append-only to the filed round-23 lesson)

Declared by the round-24 preregistration (`expected_after` item 7). This draft
records them; it does not re-derive them, and it does not edit the round-23
lesson.

| # | Filed text | Correction | Basis |
|---|---|---|---|
| C-1 | r23 lesson line 178: "73 seats dispatched (68 reports; dead: RowC01Clean, RowF07LogFollow, RowF09SignatureProgram, CritOpenHonesty, killed with the host session, no output)" | the falsify wave filed **69** lane reports, not 68 (73 seats − 4 dead = 69) | arithmetic on the filed text; the 69 count itself was not re-enumerated by this scribe — the L1 must confirm before appending |
| C-2 | r23 lesson line 174 (M7): "56 blocked `git` processes under `/tmp/repo-state-grid-*` / `/tmp/kama-r23w2/` (12:18–13:29 -03)" | **40 of the 56** killed FIFO-process identities were retained; the 56 figure is a process count, not full identity evidence | round-24 preregistration; the 40 retained identities were not re-checked by this scribe — the L1 must confirm before appending |

---

## Integration and boundaries

- **What the round-24 lesson claims.** One C1 (calibration 7→7): the auditor
  answers on evidence availability, not on promisor metadata, while keeping
  every r23 isolation guarantee. The repair is a *policy* change to the
  exit-2 surface, and it is declared as such.
- **What it does not claim.** No untrusted-repository safety (KQ32 stays); no
  closure of the inherited findings that r23 left open — `objects/info/alternates`
  (O01), the `.git` gitfile redirect (O02), prefix-ambiguity overwrite, the
  second `## Landed changes` section, CR inside an errata line, the surviving
  detector-coverage mutants, the near-variant rows, the sibling tools
  `citation-provenance.py` / `sources-append-only.py`, and the memory-ceiling
  question. No live serving capability; no higher scalar score.
- **Declared trades to re-state honestly.** git ≥ 2.45 is still required
  (`--no-lazy-fetch` is rejected by 2.44.0 with exit 129 → audit exit 2).
  Any repository shape that round 24 still refuses (shallow, grafted, non-sha1,
  non-top-level, ref-named citation) keeps a pinned reason string.
- **What is measured where.** The round-24 measurement is
  `python3 tests/report-audit/promisor-grid.py --arm both --json` (frozen =
  r23 base `0df800e`), the retained r23 grid with documented policy-row
  expectation changes, a non-promisor no-harm check, the selftest and the
  historical parity check, plus mutation sensitivity. The L1 runs the
  measurement once, after integration; this draft ran nothing.
- **Files this draft touched.** Only
  `.ufo/waves/round-24/build/out/ScribeLesson/round-24-lesson-draft.md` and
  `.ufo/waves/round-24/build/advice/ScribeLesson.md`. The corpus lesson, the
  SOURCES registry, the auditor, the grids and the corpus knowledge files are
  untouched; the L1 integrates.
- **Sources opened by this scribe (2026-10-21, plain HTTPS docs, no other
  network use):** `https://git-scm.com/docs/git-rev-list` (sha256
  `6eca09d9ef21dd42…`), `https://git-scm.com/docs/git-cat-file` (`539830429faea901…`),
  `https://git-scm.com/docs/git-config` (`5a63888b1c15a172…`),
  `https://git-scm.com/docs/partial-clone` (`8a6493225f76dba8…`).
- **Not verified by this scribe.** The round-24 exit and finding expectations
  themselves (they belong to the L1's oracle); the 69-report and 40-of-56
  corrections (declared by the preregistration, not re-derived); the frozen
  arm's behaviour for the new grid rows; the r23 grid's F23/T01 policy rows
  under the repaired code; whether the repaired auditor keeps the r23 numbers
  `faults 26/26, tracebacks 0, executed 0, timeouts 0, mutants 30/31, selftest
  50/50`.
