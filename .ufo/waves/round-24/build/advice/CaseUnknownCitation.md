# CaseUnknownCitation — round 24 leaf case (independent oracle specification)

**Verdict: the case is well-formed, discriminating and ready to be pinned by
the grid.** The required outcome is *exit 2 (could-not-evaluate) with zero
defect kinds* for a full-hash citation that is absent from both audited
repositories of a promisor-backed lane, and *exit 0* for the paired control on
the same lane. The base `0df800e` produces the harmful verdict (exit 1,
`unresolved-full-hash`) on the discriminating arm, so the expectation is not
a strawman and not a restatement of the candidate. Candidate behaviour is
**unverified** here (no candidate existed when this was written).

## 1. The case

A fleet report cites a full 40-hex commit that is absent from both audited
repositories, while the audited lane is promisor-backed and the cited commit
exists in the lane's promisor remote. Local absence is therefore uninformative:
the citation is *unknown*, not *proved absent*.

Policy source — `.ufo/waves/round-24/preregistration.json`, `expected_after`:

* `[3]` "An unavailable required commit/tree/blob/report object: exit2
  could-not-evaluate, never a clean or failed verdict."
* `[4]` "A missing citation in any promisor-backed repository is unknown, not
  proved absent: exit2 unless resolved locally by another audited repository."
* `[6]` "Metadata-only declarations do not establish incompleteness; content
  completeness and availability of required evidence determine the outcome."

### Arms and expected exits/findings

| arm | lane | fleet report | **required (candidate)** | base `0df800e` observed |
|---|---|---|---|---|
| **A-main** | `lane-filter`: `remote.origin.url=file://…/origin` + `remote.origin.partialclonefilter=blob:none` | cites the unknown commit in `## Notes` | **exit 2, defect kinds `[]`** (no `unresolved-full-hash`) | **exit 1**, `["unresolved-full-hash"]` token `29e8ea69cc44bbb72af22255c5231a7d13b577e0` |
| **B-control** | the *same* `lane-filter` | the *same* report without that citation | **exit 0, defect kinds `[]`** | exit 0, `[]` |
| **C-full** | `lane-full`: `+ extensions.partialclone=origin` + `remote.origin.promisor=true` | cites the unknown commit in `## Notes` | **exit 2, defect kinds `[]`** | exit 2, `could-not-evaluate: …/lane-full: partial clone (remote.origin.promisor)` |
| **D-store-lane** | `lane-filter` + a commit object that is **in the lane's store but unreachable from the pinned root** | cites that object in `## Notes` | **exit 0, defect kinds `[]`** | exit 0, `[]` |
| **E-store-full** | `lane-full` (canonical configuration) + the *same* store-positive object | cites that object in `## Notes` | **exit 0, defect kinds `[]`** | exit 2, `could-not-evaluate: …/lane-full: partial clone (remote.origin.promisor)` |

A-main + B-control are a pair on one lane: A-main exit 2 **together with**
B-control exit 0 is what attributes the refusal to the unknown citation and
not to the promisor metadata. C-full repeats the same policy row through the
canonical partial-clone configuration. No refusal wording is pinned, so the
expectation is not coupled to the candidate's message text.

The unknown citation is in `## Notes`, not `## Landed changes`, so the only
defect kind it could ever produce is `unresolved-full-hash` (the full-hash
scan); `landed-unresolved` / `landed-ambiguous` cannot fire. The `## Landed
changes` section cites O1, which is present locally, so no `landed-omitted`
and no `landed-section-missing` can fire either.

### 1a. The witness row (why D-store-lane and E-store-full exist)

A-main + B-control + C-full alone do **not** falsify an implementation that
decides "unknown citation" by *enumerating the lane's pinned-root closure*
instead of consulting the local object store: in A-main the unknown sha is
unreachable from the pinned root, so an enumeration-based rule also reaches
"unknown ⇒ exit 2" and passes every arm. This hole was found in review by the
`CaseMissingAncestor` lane and closed here with a **store-positive /
closure-negative** witness:

* object `064ab85244cfa7f72ca54449e69e19cffb03aa9b` — a commit written into
  the lane's object store with `git hash-object -t commit -w --stdin` (raw
  body, fixed timestamps), **not reachable** from `refs/heads/master`;
* measured: `git --no-lazy-fetch -C lane-filter rev-list --missing=print
  --objects --no-object-names master` lists 3 objects and the witness
  **0 times**; `cat-file --batch-check` answers `064ab852… commit` in
  `lane-filter` and in `lane-full`; the object is **absent from the fleet**,
  so resolution is lane-local and the "unless resolved locally by another
  audited repository" clause is *not* what decides D/E.

Expected: **found** ⇒ no defect ⇒ a **substantive** verdict (exit 0), the same
as the paired control. An enumeration-based unknown rule answers exit 2 here
and is falsified; a rule that consults only the lane's store but not the
fleet's would be caught by the neighbouring `CaseCrossRepoFound` row, not
here. D uses the filter-only lane and E the canonical configuration, so an
implementation cannot be enumeration-based on one configuration and
store-based on the other. E additionally pins `expected_after[1]` on the
canonical configuration: a complete promisor-marked lane whose cited commit
is locally present must give the full clone's substantive verdict, not exit 2
— the base gives exit 2 there (blanket refusal) although every cited object
is present.

Arms A/B/C were written before the base was run and before any candidate
existed; their entries are unchanged. D/E were added after that review, with
their expectations fixed from `expected_after[1]`/`[4]` **before** the base
was run on them (`expected.json` → `revision_note`).

## 2. Exact observations (path:line / command)

Base tool: `tools/report-landing-audit.py` at `0df800e896f6bce285a81e794ad4ae1d1e6c3a71`
(byte-identical to the working copy; the round-24 integration commit `d1b9d95`
touches no file under `tools/` or `tests/`).

All line numbers below are **base-blob** line numbers (`git show
0df800e:tools/report-landing-audit.py`), which coincide with the worktree
today. If a candidate diff shifts them, re-verify the spans against the
candidate file before reusing them.

* `tools/report-landing-audit.py:326-327` — `defects += [{"kind": "unresolved-full-hash", "token": t}`
  / `for t, s in full.items() if s != "found"]` is emitted for every full-hash
  token whose lookup status is not `found`. There is **no** branch that
  distinguishes "absent from a complete store" (proved absence) from "absent
  from a promisor-backed store" (unknown). This is the exact line the repair
  must reach.
* `tools/report-landing-audit.py:139-180` — `lookup()` asks `git cat-file
  --batch-check` per repository and returns only the three states
  `'found'|'ambiguous'|'missing'` (`:140`). There is no fourth state for
  "unknown", which is why a promisor-backed store and a complete store
  currently collapse onto the same `missing`. Under `GIT_ISOLATION`
  (`tools/report-landing-audit.py:93`, `--no-lazy-fetch`) git answers `missing`
  with rc 0 for an absent object in a promisor repository — the "missing"
  answer carries **no** information about whether the object exists at the
  promisor remote.
* `tools/report-landing-audit.py:438-465` — `check_history_repo()` refuses a
  repository wholesale on promisor metadata: paired marker (`:457`) or
  `extensions.partialclone` / `remote.*.promisor` (`:463-465`). That refusal
  is the r23 harm: it fires before the report is even read, so a complete
  promisor-marked clone can never produce a clean/failed verdict.
* `tools/report-landing-audit.py:949` — every `EvalError` becomes
  `could-not-evaluate: …` on stderr with exit 2 (`main()` at `:926`,
  `status = 0 if …` at `:538`).

Commands run against the built fixture (all local, offline):

```
$ git --no-lazy-fetch -C fixture/lane-filter rev-list --objects --missing=print --no-object-names master
db796f8b…  a33984f2…  6e98d181…            # 3 objects, no "?…" missing line
$ git -C fixture/origin cat-file -t 29e8ea69cc44bbb72af22255c5231a7d13b577e0
commit                                    # the cited commit IS in the promisor remote
$ git --no-lazy-fetch -C fixture/lane-filter cat-file -e 29e8ea69…   # absent
$ git --no-lazy-fetch -C fixture/fleet       cat-file -e 29e8ea69…   # absent
$ python3 base-audit.py --lane-repo fixture/lane-filter --fleet-repo fixture/fleet \
      --branch master --lane kama --rounds 1 --no-errata --json
  exit 1, by_kind.unresolved-full-hash = 1, token 29e8ea69…, required_commits 1
$ python3 base-audit.py … --lane-repo fixture/lane-full …
  exit 2, stderr: could-not-evaluate: …/lane-full: partial clone (remote.origin.promisor)
$ python3 base-audit.py … --lane-repo fixture/lane-filter --fleet-repo fixture/fleet-clean …
  exit 0, no defects
$ python3 base-audit.py … --lane-repo fixture/lane-filter --fleet-repo fixture/fleet-side …
  exit 0, no defects                       # D: the store-positive witness resolves
$ python3 base-audit.py … --lane-repo fixture/lane-full --fleet-repo fixture/fleet-side …
  exit 2, partial clone (remote.origin.promisor)   # E: blanket refusal although
                                                   #    every cited object is present
```

Witness measurements (the D/E object `064ab852…`):

```
$ git --no-lazy-fetch -C fixture/lane-filter rev-list --missing=print --objects --no-object-names master
db796f8b…  a33984f2…  6e98d181…          # 3 objects; the witness appears 0 times
$ printf '064ab852…\n' | git --no-lazy-fetch -C fixture/lane-filter cat-file --batch-check
064ab85244cfa7f72ca54449e69e19cffb03aa9b commit      # present in the store
$ git --no-lazy-fetch -C fixture/fleet-side cat-file -e 064ab852…   # absent from the fleet
```

Premise probe (`premise-probe.txt`, local `file://` to a **nonexistent**
path; no network, no script, no data transfer) — why local absence is
uninformative and why `--no-lazy-fetch` is what exposes it:

```
$ git cat-file -e 29e8ea69…                       # filter-only promisor remote
fatal: '…/absent-origin' does not appear to be a git repository
fatal: Could not read from remote repository.      # git ASKS the promisor remote
$ git --no-lazy-fetch cat-file --batch-check
29e8ea69… missing                                  # rc 0: the answer the auditor sees
```

No fetch happened during any arm run: the lane still lacks `29e8ea69…`
afterwards, gained no pack and no `FETCH_HEAD` (`run_case.py`
`fetch_observed=false` for all arms).

## 3. Containment — no fixture escaped the scratch

* Heavy fixture: `/fast/scratch/hyaku/kama-r24/CaseUnknownCitation/fixture`
  (1.2 MiB). Nothing in `/tmp`.
* `build_case.py` writes only through `Builder.guard()`, which raises for any
  path outside the root; negative test executed:
  `guard('/tmp/escape-attempt')` → `BuildError: write escapes fixture root`.
* `fixture-manifest.json` lists all 132 written paths; "not under root" → 0.
* `run_case.py` re-checks containment independently (`--show-toplevel` equals
  the fixture path, every `remote.origin.url` resolves under the root, no
  `objects/info/alternates`) → `containment_problems=[]`.
* No production file was written by this lane; the only lane files are the
  artifacts listed in §5.

## 4. Risks the grid should watch (bounded, no strawman)

1. **Attribution is the load-bearing property.** A candidate that refuses any
   promisor repository wholesale (the r23 behaviour) passes A-main and C-full
   by accident and fails B-control (it would exit 2 instead of 0) and E-store-full
   (it would exit 2 instead of 0 although every cited object is locally
   present). The pair is what makes the case falsifiable; a grid that keeps
   only A-main would let the r23 harm pass.
1b. **A/B/C alone do not falsify an enumeration-based rule.** The witness arms
   D/E close that hole (§1a): a citation that is in the store but unreachable
   from the pinned root must be *found*, not unknown. If the grid drops D/E,
   an implementation may pass the whole case while deciding "unknown" by
   enumerating the closure.
2. **The case is decided by the citation rule, not by the closure rule.** The
   lane's pinned-root closure is complete (no `?`-prefixed missing object), so
   the unresolved closure-scope policy (required-objects-only vs whole-closure)
   cannot change this case's outcome. If a candidate ties the unknown-citation
   refusal to "the store is incomplete", it will emit exit 1 here — a
   violation of `expected_after[4]`, which speaks of a *missing citation* in a
   *promisor-backed repository*, independent of closure completeness.
   Measured, on this fixture: `git --no-lazy-fetch rev-list --missing=print
   --objects --no-object-names master` lists exactly 3 objects, **no** `?`
   line, and the unknown citation `29e8ea69…` appears **0 times** — it is
   unreachable from the pinned root, so no closure enumeration can even mention
   it, while `cat-file --batch-check` answers `29e8ea69… missing`. A closure
   check therefore cannot express "unknown"; the repair needs a
   citation-level promisor decision (or a fourth lookup status). Related
   measured hazard from the `CaseMissingAncestor` lane: `rev-list
   --missing=print` returns rc 0 and lists only the commits *above* a gap in a
   promisor-backed lane, so closure enumeration is not a reliable history
   enumeration either — it is only usable for deciding whether *required*
   objects are present, never for concluding that a citation is absent.
3. **Detection surface.** A-main relies on `remote.origin.partialclonefilter`
   alone marking the remote as a promisor source (proved above: git asks the
   remote). A candidate that detects only `remote.*.promisor` /
   `extensions.partialclone` / paired markers will fail A-main while passing
   C-full — that is a real detection gap, not a fixture artefact. C-full is
   therefore kept as the configuration-independent witness.
4. **Not covered here** (adjacent lanes): the wrong-type citation (a locally
   present blob used as a Landed commit must stay a real failed finding), the
   cross-repository resolution (token absent in the promisor lane but present
   in the fleet ⇒ resolved, no refusal), and the unreachable-but-present
   citation. A candidate that answers every unknown citation with exit 2 will
   fail those neighbours; the grid must keep them.

## 4a. Reading-invariance of this case (for L1 / GridOracle)

The prereg says "promisor-**backed**" (`expected_after[4]`), while
`expected_after[1]` says "promisor-**marked**". Two readings are possible:

* *marked ≠ backed* — only a repository that names a promisor **source**
  (`remote.<name>.promisor`, `extensions.partialClone=<remote>`,
  `remote.<name>.partialclonefilter` **together with a remote URL**) can still
  supply a missing object; a paired `.promisor` marker alone marks the store
  but names no source, so its "missing" answer is final;
* *any promisor metadata* — every promisor-marked repository makes absence
  uncertain.

**This case is invariant under both readings**: A-main and C-full both carry
`remote.origin.url` *and* `remote.origin.partialclonefilter`, so they are
backed under either reading and must be exit 2 under either. The split itself
is pinned by the neighbouring row `OracleNoConfigPack/promisor-fabricated`
(marker-only + no remote + fabricated id): exit 1 under the *marked ≠ backed*
reading, exit 2 under the *any metadata* reading. The two rows together fix
the policy; if L1 takes the literal "any metadata" reading, that neighbour's
row flips and this lane's rows do not move.

## 5. Files

* `.ufo/waves/round-24/build/out/CaseUnknownCitation/build_case.py` —
  deterministic fixture builder (guarded writes, fixed ids/times).
* `.ufo/waves/round-24/build/out/CaseUnknownCitation/expected.json` — the
  expectation, written **before** the base was run and before any candidate.
* `.ufo/waves/round-24/build/out/CaseUnknownCitation/run_case.py` — arm runner
  with expectation check, containment re-check and fetch tripwire.
* `.ufo/waves/round-24/build/out/CaseUnknownCitation/base-observation.json` —
  base `0df800e` run (exit 1 / 0 / 2, `fetch_observed=false`, no containment
  problems).
* `.ufo/waves/round-24/build/out/CaseUnknownCitation/fixture-manifest.json` —
  resolved ids, arm map, all written paths.
* `.ufo/waves/round-24/build/out/CaseUnknownCitation/premise-probe.txt` —
  offline promisor-remote probe output.
* `.ufo/waves/round-24/build/out/CaseUnknownCitation/PROVENANCE.md` — full
  provenance, premise list, containment proof, reproduction commands.

## 6. Unrun / unverified

* **The candidate was not executed.** No candidate implementation existed
  when this was written (`git diff 0df800e HEAD -- tools/ tests/` is empty),
  and the assignment forbids running candidate suites. Every statement about
  candidate behaviour above is a requirement derived from the preregistration,
  not an observation.
* No network transport, no script execution, no repository program was used
  or asserted anywhere in this case; the only remote reference is a local
  `file://` URL used as a fetch tripwire, never contacted by the fixture.
* r23 grid rows F23 (`repo-state-grid.py:670`, fixture `:195-213`) and F27
  (`:482-498`) were read but **not re-executed** here; the filter-only
  premise was re-derived locally instead (see §2 probe).
