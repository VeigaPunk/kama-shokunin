# Intent — r23 promisor blanket checks: original purpose and minimal retention

Verdict: the r23 refusal of promisor-marked repositories bundled two separable
purposes. Leg A (behavioral) — stop git from lazily fetching during the audit,
which would run repo-configured programs, invoke a transport, mutate the
audited object store, and let remote content manufacture verdicts — is carried
entirely by `GIT_ISOLATION`'s `--no-lazy-fetch` flag and survives r24
untouched. Leg B (epistemic) — in a promisor-backed repository a local
"missing" is not proof of absence, so absence-based verdicts are unjustified —
was implemented at the wrong granularity: repository-level, metadata-keyed,
upfront for both repos, so a complete local clone with promisor metadata is
refused exit 2 (declared tradeoff T01) where its full-clone twin gets a
justified verdict. The minimal retention of Leg B is to move it from metadata
to evidence: only a *missing required object* in a promisor-backed audited
repo becomes exit 2 could-not-evaluate (unknown, not proved absent); found
objects score normally; metadata alone refuses nothing. This is exactly the
preregistration expected_after set, and it is the same direction r23 already
moved twice under falsify pressure (C09/C10: metadata must not refuse when it
is false or orphaned; M4: contamination markers refused the real fleet).

Axes (godspeed): calibration (7, assigned lowest — this is the C1 7→7 narrow),
operability (8 — the harm being repaired), fidelity (evidence chain below),
no-harm (Leg A + non-promisor verdicts unchanged).

## 1. Evidence chain (commits and docstrings, base 0df800e896f6bce285a81e794ad4ae1d1e6c3a71)

### e0f0434 2026-10-21 12:30 "round-23: neutralize repository-local git state in report-landing-audit; fault grid and isolation mutants"

Introduced, in one commit:

- `GIT_ISOLATION` (now `tools/report-landing-audit.py:88-96`) with the stated
  rationale in the comment: "Repository-local state that changed, crashed or
  hijacked verdicts in the round-23 fault grid: refs/replace substitutions,
  promisor lazy fetches and signature verification (**both may run
  repo-configured programs**) ... Old git (< 2.45) rejects --no-lazy-fetch,
  which is an EvalError." Every `git()` call (`:117-136`) prepends it.
- `check_history_repo` (first form, `e0f0434:tools/report-landing-audit.py`,
  refined in place at `:437-465` today) with the epistemic docstring:
  "**Refuse a repository whose visible history is not its object history
  (shallow boundary, info/grafts), whose missing objects belong to a promisor
  remote (absence is not evidence there), or whose object names the 40-hex
  scanners cannot read (non-sha1 object format).**" Called upfront for both
  repos, before any round is evaluated (`:514-515`), so one config key refuses
  the whole audit. First form: any `objects/pack/*.promisor` file, and
  `config --list --name-only` matching `extensions.partialclone` or
  `remote.*.promisor` (value ignored — `remote.origin.promisor=false`
  refused).
- Module docstring trust paragraph (`:44-55`): "refs/replace, lazy fetch,
  signature display ... are neutralized; ... shallow, grafted, partial-clone,
  non-sha1 and non-top-level repositories and ref-named citations are
  refused."
- The fault grid `tests/report-audit/repo-state-grid.py` whose header pins the
  semantics: "`fault` (repository-local state must not crash, flip or hijack
  the verdict)", "`control` (ordinary verdicts both arms must keep)",
  "`tradeoff` rows (declared new refusals) ... reported, never graded."

### 34b2376 2026-10-21 12:41 "round-23: NUL-delimited log records, catch-all refusal, promisor/sha256/top-level refusals; grid F22-F26 and mutants"

Added the catch-all refusal (`main()` maps any unanticipated exception to
`could-not-evaluate ... return 2`, `:918-925` at that commit; today
`:947-951` for EvalError) and pinned the refusal reasons as grid rows with
`REASONS` stderr matchers (e.g. `"F23-promisor-pack-without-config":
"promisor pack"`). The refusal *code* is e0f0434's; this commit made the
refusal observable and graded: a grid credits exit 2 only when stderr carries
the pinned reason (`corpus/knowledge/error-is-not-a-verdict.md`, round-23
section: "A grid credits a refusal only when its stderr carries the pinned
reason, so the catch-all cannot launder an unrelated failure into a 'met'
row").

### e876b95 2026-10-21 13:56 "round-23: falsify-wave integration — git timeout, filter-only promisor, fleet history checks, ..."

Three refinements, all in the direction "metadata alone must not refuse":

- Promisor pack now requires the sibling `.pack`:
  `p.suffix == ".promisor" and p.with_suffix(".pack").exists()` (`:454-456`).
  Control C10-orphan-promisor-marker (`repo-state-grid.py:545-549,680`) pins
  that an orphan `.promisor` marker must NOT refuse. Born from mistake M4
  (`corpus/lessons/round-23.md:170-171`): a falsify probe wrote four zero-byte
  `.promisor` markers into the real fleet's pack dir via upward git discovery,
  "which made the current audit refuse the real fleet" — metadata lied, and
  the blanket refusal converted the lie into an operability failure.
- Config value must be true: `git_bool(value)` for `remote.*.promisor`
  (`:458-465`); control C09-promisor-false-config (`repo-state-grid.py:539,
  679`) pins `remote.origin.promisor=false` → normal verdicts.
- New fault F27-filter-only-promisor-remote (`:482-497, 674-677`), fixture
  docstring: "`remote.<name>.partialclonefilter` alone makes a promisor
  remote, so a missing-object lookup would fetch (and run core.sshCommand)."
  The fixture proves (with a `touch marker; false` trap and a bare
  `cat-file -e`) that git treats filter-only as a promisor channel — and that
  the refusal list does NOT cover it. Graded expectation at base: exit 1 with
  `landed-unresolved` + `unresolved-full-hash`, i.e. the flag alone suppresses
  the fetch and local absence is then scored as a defect.

### 0df800e (base) — the declared tradeoff

`corpus/lessons/round-23.md:83-84`: "**Declared tradeoffs: partial clones and
shallow clones are refused even when every cited object is local (grid T01;
RevCalibrationAxis, CritNoHarm).**" T01 (`repo-state-grid.py:596-602,689`) is
a genuine `git clone --filter=blob:none --no-local file://…` whose round is
clean — expected exit 0, refused exit 2, reported not graded. The lesson also
records (`:127-130`): "`--no-lazy-fetch` is not defensive-only: a
`remote.<n>.partialclonefilter` remote passes every refusal and lazy-fetches
through `core.sshCommand` without it (CritDefensiveOnly P01/P02). Grid F27 now
grades that channel and kills M02." Supporting doc (fetched plain HTTPS,
recorded as sources S092/S099 in the lesson, `:38-40,157-159`): git
partial-clone docs, "Handling Missing Objects" — "no check as to whether the
missing object is actually a promisor object is performed."

## 2. Reconstructed original safety purpose

The audit's verdicts rest on *proven local absence*: `unresolved-full-hash`
and `landed-unresolved` are emitted when `lookup()` returns `missing`
(`:325, :327-328, :336, :341-343`), `errata-invalid` likewise (`:404-407`),
and `landed-omitted` rests on the completeness of the lane `git log` traversal
(`:344-354`, read via `round_commits`, `:181-212`). Two things break that
foundation in a promisor-backed repository:

1. **Behavioral (Leg A):** a lookup of a missing object triggers lazy fetch
   (`git` docs, `--no-lazy-fetch`: "Do not fetch missing objects from the
   promisor remote on demand"). Without suppression that (i) runs
   repo-configured programs — `core.sshCommand`, and the remote's transport —
   an execution channel in an audit context; (ii) contacts the configured
   remote, a network transport the contract forbids; (iii) mutates the audited
   object store mid-audit; (iv) can *resolve* a citation from remote content,
   manufacturing a false clean (the report's claim "this hash exists in our
   repositories" would be satisfied by the network, not by local evidence).
2. **Epistemic (Leg B):** with fetch suppressed, "missing" in a promisor-backed
   repo means only "not in this object store", never "does not exist in the
   audited repository". An `unresolved-full-hash`/`landed-unresolved` verdict
   emitted from that absence would assert more than the evidence shows; the
   honest classification is could-not-evaluate. This is the docstring's own
   words: "absence is not evidence there" (`:440-441`).

r23 implemented Leg A per-invocation (the flag, plus the git >= 2.45
fail-closed floor when the flag is rejected — `:92`, OldGitFloor: only the
flag fail-closes; the env form fails open below 2.45) and Leg B as a blanket
repo-level refusal keyed on metadata (pack sibling / `extensions.partialclone`
/ `remote.*.promisor=true`), checked upfront for both repos (`:514-515`).

## 3. Divergence from that purpose

Leg B's metadata trigger exceeds its epistemic warrant. The warrant is about
*missing objects*; the trigger fires about *configuration*, even when every
required object is present and every verdict rests on found evidence. Harms,
each pinned in r23's own grid or lesson:

- T01 (complete blobless partial clone): clean round → exit 2 instead of
  exit 0 (`repo-state-grid.py:596-602,689`; lesson `:83-84`). This is the r24
  preregistration `expected_before`.
- M4 (contamination markers): metadata can be false in the other direction —
  r23 already conceded that by requiring the `.pack` sibling and by C09/C10.
- Asymmetry: a filter-only promisor lane (F27) — equally "absence is not
  evidence" per its own fixture docstring — is *scored*, not refused, at base.
  The boundary follows config spelling, not evidential situation.

r23's own trajectory (C09, C10, grafts_effective for M6) already walks the
principle: refusal evidence must be content, not declaration. r24 C1 applies
that principle to the promisor channel itself.

## 4. Minimal retention (intent-level contract for the repair)

Keep, unchanged — these never depended on the blanket refusal:

- `GIT_ISOLATION` incl. `--no-lazy-fetch`, `--no-replace-objects`, the `-c`
  pins, bytes+strict-decode, `GIT_TIMEOUT`, scrubbed env, git >= 2.45 floor
  with typed refusal on flag rejection (`:88-96, :117-136, :92`).
- shallow / info/grafts / non-sha1 / non-top-level / ref-named-citation
  refusals — distinct purposes ("visible history is not its object history",
  scanner readability), untouched by this claim.
- `EvalError` → exit 2 with reason; errors are never verdicts (`:84-85,
  :947-951`).

Narrow Leg B from repo-granular to object-granular, at the exact couplings
where absence becomes a verdict (the only sites needing the distinction):

- `lookup()` (`:139-174`): when a token is `missing` in an audited repo that
  is promisor-backed and not `found` in the other audited repo (lane/fleet
  merge already exists), raise EvalError — "citation unknown in
  promisor-backed <repo>: absence is not evidence", exit 2 — instead of
  returning `missing`. Non-promisor repos keep `missing` → defect.
  Covers `unresolved-full-hash` (`:325`), `landed-unresolved`/`-ambiguous`
  (`:336-343`), `errata-invalid` corrections (`:404-407`), selftest arms
  (`:832-836`).
- `round_commits` / any history traversal (`:344`, `:181-212`) and required
  blob reads (`:310-313`): already EvalError on git failure, which is what a
  missing commit/tree during `log` produces (grid F28/F29 precedent,
  ConnPlanningWalk table, `:288-297`) — no change needed; complete local logs
  under promisor metadata therefore still yield `landed-omitted` exit 1, the
  preregistration's case 2.
- "Promisor-backed" classification: `extensions.partialclone`,
  `remote.*.promisor=true` (git_bool), and promisor pack with `.pack`
  sibling — the base detectors repurposed from refuse to classify
  (`:443-465`). Include `remote.*.partialclonefilter` set: F27's own fixture
  docstring ("filter-only ... makes a promisor remote ... would fetch")
  asserts git treats it as one; leaving it scored would keep the asymmetry
  this claim removes. [INFERENCE from the F27 docstring and lazy-fetch
  premise; the grid/mutation lanes own the row-expectation change: F27 moves
  from exit 1 + defects to exit 2, and T01 from reported tradeoff to graded
  control at 0.]
- Metadata alone refuses nothing: `remote.origin.promisor=false` (C09),
  orphan marker (C10), and a fully-present promisor-marked clone (new control
  mirroring T01) all produce the same substantive findings as their full-clone
  twins.

What this does NOT claim (docstring `:44-55` must be reworded to match, but
its limits stay true): untrusted-repository authorization; alternates/gitfile
channels remain open (O01/O02); no network fetch occurs (the flag still
guarantees it); trusted repositories only.

## 5. Confidence and not verified

- Reconstruction of purpose: high — every element is quoted from committed
  docstrings, commit subjects/diffs (e0f0434, 34b2376, e876b95, 0df800e), the
  committed lesson, and the grid fixtures; no artifact-only evidence is load
  bearing.
- The object-granular retention rule is the minimal change that satisfies all
  seven preregistration `expected_after` rows simultaneously; I verified the
  coupling sites by reading the code, not by running it. No auditor was
  executed, no fixture built (this lane is intent-only; GridOracle and
  MutationOracle own measurement).
- Not verified: whether any other kama tool (sibling gates) shares the
  promisor refusal pattern (out of lane; ConnSiblingTools r23 covered the
  isolation gap, not this policy); exact `git_bool` semantics for unusual
  value spellings beyond C09's `false`.

Installs: none (no new tools needed; observation-only lane).

Artifacts: `out/Intent/promisor-intent-evidence.txt` — verbatim first (e0f0434)
and final (base) forms of `check_history_repo`, the F27/C09/C10/T01 fixtures,
and the GIT_ISOLATION docstring, extracted from the scratch clone.
