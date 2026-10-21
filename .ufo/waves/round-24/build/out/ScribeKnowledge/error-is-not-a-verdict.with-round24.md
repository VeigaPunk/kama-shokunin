source: S061 (Python 3.14 sys.exit), S062 (Stryker mutant taxonomy), S064 (subprocess signal returncodes); S063 (PIT counterexample, rejected as universal-rule support); corpus/lessons/round-20.md Gate
verified-at: 2026-10-21 — pinned round-20 source openings and named error-injection regression set
recheck: on-release — run tools/error-verdict-census.py on its pinned cell registry; reopen the Python and mutation-policy sources when their revisions change

# Error classification is not mutation-kill credit

A gate may correctly fail closed if its subject crashes. A mutation counter
claiming a targeted rejection needs more: a declared exit code and the
subject's emitted verdict, with evidence that the intended check ran.
This is a scoped lane measurement rule, not a universal testing convention.

## Exit status ambiguity

S061 states that `sys.exit` with a noninteger object prints it to stderr and
exits 1. Uncaught exceptions also produced 1 in round-20 host Python probes
(`build/advice/SrcPySysExit.md`). The same status can therefore mean an
intentional verdict or a crash. S064 describes negative POSIX returncodes as
signal termination; that alone is not a subject verdict either.

For the live-receipt grid, an actual rejection is exit 1 with the gate's
`INVALID ` line. A silent 1, traceback-only 1, signal, timeout or unknown
exit is visible error evidence and must not increase rejected counts or
produce a clean overall grid. A positive genuine-rejection control prevents
an always-error classifier from satisfying the regression suite.

A targeted `FAIL` literal before a selftest abort is insufficient kill
credit. The completed target assertion and complete enumeration must be
observed. Preserving a partial transcript is useful but not completion.

## Precedent is not universal authority

S062 Stryker distinguishes failed-test Killed from Runtime error and excludes
runtime errors from its score. S063 PIT instead marks `RUN_ERROR(true)` and
counts it in detected totals. Thus the inference "all mutation tools exclude
crashes" is rejected. The lane explicitly chooses its stricter evidence
policy rather than borrowing a universal numbering or scoring convention.

## Limits

The round-20 cells cover the named grid and selftest-arm repairs, not every
historical counter. Probe-checker subject crashes may still be row failures
(fail-closed policy); that is different from claiming a targeted kill.
Other historical mutation runners and post-verdict crashes are disclosed
residuals. Missing docs/git already returned citation-checker exit 2 at the
round-start commit; no improvement is credited for those correct paths.

## `sys.exit(None)` scope qualification — S065 (2026-10-21)

S061's status-1 statement applies to non-`None` noninteger exit objects. Python
3.14.8 says “None is equivalent to passing zero” in the `sys.exit` argument
paragraph; the other noninteger object case prints to stderr and produces exit
1. S065 supersedes only the overbroad exception wording in S061; this does not
change the evidence rule that an exit status alone is not an emitted verdict.

## Round-23 deepening — the auditor's own exit class

Appended 2026-10-21 (round 23); the frontmatter above describes the
round-20 sources. `tools/report-landing-audit.py` used `1` for `failed`, and
its `main()` mapped only `EvalError`/`OSError` to `2`. Its git calls used
`text=True`, so captured output was decoded by the io.TextIOWrapper default
(S097), which raises on invalid bytes (S098); git may emit non-UTF-8 log text
verbatim (S093). A repository-local `i18n.logOutputEncoding`, a non-UTF-8
committed report or errata blob, or a 5000-digit field therefore crashed it
into exit 1: an error read as a verdict. The round-23 grid observes 9 such
frozen-arm tracebacks (F01, F02, F16, F18, F19, F20, F22, F24, F26); the
lesson's first count of 8 predates F26.

The fix has two layers: decode git output as bytes with an explicit `strict`
UTF-8 decode mapped to a typed refusal (S096), and catch any remaining
exception as could-not-evaluate. A grid credits a refusal only when its
stderr carries the pinned reason, so the catch-all cannot launder an
unrelated failure into a "met" row. The catch-all alone meets exactly one
fault row (F24) yet removes all 9 tracebacks (falsify-wave ablation,
CritSeparabilityW2), so "0 tracebacks" is not evidence of isolation; only
per-row reasons and per-element mutants that the grid kills on a named row
are (KQ34). A mutant "kill" counts only on grid exit 1, never on a grid that
could not evaluate.

source: S093, S096, S097, S098, corpus/lessons/round-23.md; evidence
`tests/report-audit/repo-state-grid.py`, `tests/report-audit/isolation-mutants.py`.

## Round-24 deepening — a refusal is not a verdict either, and isolation is not availability

Appended 2026-10-21 (round 24); the frontmatter above describes the
round-20 sources and the section above describes the auditor's own exit
class. This section adds the mirror image of the failure already recorded
there: not an error read as a verdict, but a refusal that was never earned.

### Three states, not two

Round 23 named one error mode: an exception that surfaced as exit 1 was an
error read as a verdict. Round 24 names the other side of the same coin.
Exit 2 (`could-not-evaluate`) is honest only when it names evidence the
audit could not obtain. When every required object is present locally, the
input is a *supported complete state*: the audit can decide it, and the
decision is a verdict — clean, or failed with findings. Refusing such an
input does not make the refusal a verdict; it turns a decidable input into
an undecidable one and withholds a real finding. A refusal that is not
grounded in a missing object is therefore its own error class, and it is
not cured by being labelled `could-not-evaluate`.

Base behaviour, measured in this wave on paired offline fixtures: a complete
local promisor-marked lane exits 2 (`partial clone (remote.origin.promisor)`)
while the otherwise identical full clone exits 0; a promisor-marked lane
carrying a genuine omission exits 2 while its twin exits 1 with
`landed-omitted`; and removing only the `.promisor` marker file from the
marked clone — every other byte unchanged, every reachable object local —
returns exit 0. The declaration decided the outcome; the content did not.

The three states are:

1. **Supported complete state** — every required object (commit, tree, blob,
   committed report) is locally present and the citations resolve. The audit
   returns its ordinary substantive verdict, with the same findings an
   otherwise identical un-marked clone would produce. This includes the
   `landed-omitted` finding: a genuine omission stays a finding even when the
   repository carries promisor metadata.
2. **Unsupported input** — an object the audit actually requires cannot be
   read locally. Exit 2, reason naming that object and the repository that
   needs it. Never exit 0 (clean), never exit 1 (failed), and never a
   guessed empty result.
3. **[amended] Same state as the un-marked twin.** A locally unresolved
   citation is *not* a promisor problem: the marked repository must reach the
   same substantive verdict as its unmarked twin on the same bytes, including
   for a citation that resolves nowhere (that is the twin's
   `unresolved-full-hash` / `landed-unresolved` finding, not exit 2) and for
   an errata-corrected historical defect. The one exception is a citation
   that names *local content the audit must read* and that content is
   genuinely unavailable: then the outcome is exit 2 with a content-derived
   reason, because the evidence cannot be read. This replaces the
   preregistered expectation that every unknown citation in a metadata-marked
   repository is exit 2; that expectation was withdrawn prospectively by
   `.ufo/waves/round-24/oracle-amendment-1.json` (`supersedes_expectation_only:
   preregistration.json expected_after[3]`), because it aborted before the
   errata stage and so destroyed a correct local workflow. An unrelated
   missing historical object — an unused blob, a branch, a file no read
   touches — is not a precondition of the audit and must not become one.

### Safe isolation is not availability proof

The isolation measures the audit already carries are containment, not
evidence: `--no-replace-objects`, `--no-lazy-fetch`, the log/signature
suppression keys, the scrubbed environment and the per-call deadline. What
they establish is that the audit will not run repository-configured
programs, will not substitute replacement objects, and will not hang
(`tools/report-landing-audit.py:93-99`, `:108`). They are silent on what the
repository contains.

`--no-lazy-fetch` is the sharpest case. Its documented effect is that git
"does not fetch missing objects from the promisor remote on demand", and the
same page recommends pairing it with `git cat-file -e <object>` "to see if
the object is locally available" (S089 page, reopened 2026-10-21 in this
wave — `advice/SrcGlobalGit.md`, `build/out/SrcGlobalGit/pins.json`,
`quotes.no_lazy_fetch_use`; that sentence is not yet carried in the S089
`teaches` cell). Read in that pairing, the flag is the *precondition* of a
local availability measurement, not a substitute for one: it proves that no
fetch happened, never that an object is absent. The same page's scope limit
holds in the other direction — those two options "neither cover info/grafts
or shallow" — so isolation is a set of named channels, never a general
statement about the repository.

Absence read against a promisor declaration is a statement about the local
store, not about the repository's history. Git's own partial-clone
documentation says the missing-object path performs "no check as to whether
the missing object is actually a promisor object" (S099, superseding S092,
§Handling Missing Objects): git does not treat a promisor declaration as an
assertion about any particular object's presence, so neither may the audit.
The declaration is a transport arrangement; a `.promisor` marker beside its
pack "consist[s] of a `<name>.promisor` file with arbitrary contents"
(S103) and records packaging provenance, not the absence of anything an
audit needs. Content completeness and the availability of the specific
required evidence decide the outcome.

Two symmetrical errors meet here, and the repair must avoid both:

- **Refusing on metadata** treats a declaration as absence and refuses a
  complete local repository — the round-23 behaviour, which the round-24
  assignment classifies as operability harm rather than a disclosed trade.
- **Fetching to find out** lets a remote decide a local question and can run
  a repository-configured program, which the isolation exists to prevent.

The correct posture keeps the containment and then measures: with
`--no-lazy-fetch` and the rest of the isolation unchanged, ask locally per
required object whether it is present. The auditor's own lookup path already
asks that question — `git cat-file --batch-check` prints `missing` for a name
that cannot be resolved to an object and `ambiguous` for an ambiguous short
name (S083, superseding S071), and S083 records that a process failure is
distinguished by exit status, so a failed git call stays an error rather
than a missing verdict. A bounded missing-object traversal is the other
available probe: `--missing=print` "is like allow-any, but will also print
a list of the missing objects" (S102) — encountered-missing output, not a
completeness theorem and not an exit policy.

### A green integrity check is not an availability oracle

`git fsck` is the obvious way to ask "is anything missing?", and it is the
wrong instrument here. In git v2.56.0's `builtin/fsck.c`, `mark_object`
returns early for a promisor object — "if (is_promisor_object(options->repo,
&obj->oid))" … "return 0;" — before the HAS_OBJ check, so a green fsck is
not proof that every promised object is locally present (S104, **rejected**
as a proposed completeness oracle). The flip the registry records is the
right one: demonstrate the availability of the required evidence directly
rather than infer it from an fsck result. The manual, the installed 2.56.0
man page and the v2.56.0 adoc contain no statement about promisor objects at
all, so `git fsck` silence is evidence in neither direction.

### The refusal reason must name the evidence

If a refusal may be entered only when a required object is unavailable, its
reason has to say which object, in which repository. The round-23 grid pins
metadata reasons for two exit-2 rows — `"partial clone"` for
`F06-lazy-fetch-command` and `"promisor pack"` for
`F23-promisor-pack-without-config`
(`tests/report-audit/repo-state-grid.py:697`, `:704`). Both rows remain
exit 2 under the round-24 policy, because in both the cited object is
genuinely absent, but the reason text must change to the unavailable
object; otherwise a metadata reason and a content reason are
indistinguishable and the grid cannot tell a justified refusal from the
blanket one. The same reasoning applies to the repaired code path itself:
one reason string cannot express both "the declaration says so" and "the
object is gone".

### A refusal must be able to fail

KQ34 and KQ25 already forbid crediting a promise that the gate cannot
violate. The round-24 instance is concrete: the round-23 grid cannot kill a
blanket-refusal mutant, because `F23` refuses in both arms, `T01` is a
`tradeoff` row that is reported and never graded
(`tests/report-audit/repo-state-grid.py:13-15`, `:689`), and controls `C09`
and `C10` carry no promisor metadata at all (`:679-680`). Credit for the
repair therefore comes from a *paired* population — a full clone and a
metadata-marked clone of the same history with the same citations — where
the marked clone must produce the marked clone's twin's findings, and from
a mutant that restores the metadata-only refusal and is killed on that row.
Kill credit requires the grid to exit 1; a grid that could not evaluate
kills nothing.

### Limits of this section

- Scope unchanged: this concerns the trusted lane and fleet repositories the
  audit is for (KQ32). It is not a claim of untrusted-repository safety.
- It closes no other open item: objects borrowed through
  `objects/info/alternates`, a `.git` gitfile redirect, the
  `--shared`-of-partial bypass, prefix-ambiguity overwrite, the second
  `## Landed changes` section, a CR inside an errata line, an `--errata`
  naming a FIFO, the missing memory ceilings, and the unisolated sibling
  tools `citation-provenance.py` and `sources-append-only.py` all stay open.
- It claims no new exit code, finding kind, or verdict vocabulary, and no
  change to the global Git isolation or the deadline.
- It is a statement of the rule, not a report of a repair: this lane ran no
  grid, mutant, selftest, or probe, and the round-24 measurement
  (`python3 tests/report-audit/promisor-grid.py --arm both --json`) did not
  exist at drafting time.
- It asserts no remote completeness and no remote abbreviation uniqueness:
  the audit resolves objects in the lane and fleet repositories it was given
  (`tools/report-landing-audit.py:12-19`), and nothing here widens that.
- One source this section would like to lean on is **awaiting its
  opening**: that `remote.<name>.partialclonefilter` alone registers a
  promisor remote (git v2.56.0 `promisor-remote.c`, `promisor_remote_config`
  — candidate row drafted by seat `SrcPromisorCode`, not admitted in
  `corpus/SOURCES.md`). The section therefore does not rest on it.

source: S083, S089, S099, S102, S103, S104 (rejected), corpus/lessons/round-24.md,
`.ufo/waves/round-24/oracle-amendment-1.json`; evidence
`tests/report-audit/repo-state-grid.py`; wave-24 peer observations under
`.ufo/waves/round-24/build/out/` and `.ufo/waves/round-24/build/advice/`.
