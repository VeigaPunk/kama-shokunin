# CaseUnreachableCitation — round-24 oracle case (specified before implementation)

**Verdict: the case is specified, constructed and locally verified.** It is a
single, independent, offline oracle case for the preregistered C1 axis: a
commit citation whose object exists locally but is **not** in the branch
closure must stay resolvable, and promisor metadata alone must not turn a
locally complete lane into exit 2.

All expectations below were fixed **before** any candidate implementation and
are recorded in `case-manifest.json`. I did not modify any lane production
file; the repair prototype and the two mutants live only in scratch and in my
own out directory.

**Lane bounds respected.** No subagent dispatch (leaf member). No fleet,
sibling, operator-config, `.jj` or lane-Git-index writes. No commits, no
pushes, no pacman transactions, no host service or config mutation, no
secrets, no model overrides. Tools installed or updated: **none**.

---

## 1. What the case is

`tools/report-landing-audit.py` resolves a citation with `cat-file
--batch-check` (`tools/report-landing-audit.py:139-174`), i.e. it asks the
**object store** whether the object exists. It never asks whether the object
is *reachable*. The r23 base, however, refuses a repository outright as soon
as it sees promisor metadata (`tools/report-landing-audit.py:459-465`):

```
raise EvalError(f"{repo}: partial clone ({key})")
```

That refusal is the r23 harm the round-24 repair removes. The open question
this case pins down is the one the repair must not get wrong while removing
it: **how does the repaired auditor decide that a citation is available?**
If availability is decided by *reachability* instead of by *existence*, a
citation to a locally present but off-closure commit is falsely reported
unresolved — which is exactly the "proved absence" the preregistration
forbids.

The fixture is built so that the two available questions give **different**
answers for the same objects:

| object | location | `cat-file` (existence) | `rev-list --all` | `rev-list master` |
|---|---|---|---|---|
| C1 | on `master` | found | present | present |
| C2 | on `master` | found | present | present |
| **X1** | **dangling: no ref anywhere** | **found** | **absent** | **absent** |
| **X2** | reachable only via `refs/keep/x2` | **found** | present | **absent** |

X1 is the strict case (unreachable from *every* ref); X2 is the realistic
case (a kept ref outside the audited branch). Both are cited by the fleet
report. Both must resolve.

Measured by `probe_availability.py` → `probe-availability.json`:

```
C1: existence=True all_refs=True branch=True  expected=[True, True, True]
X1: existence=True all_refs=False branch=False expected=[True, False, False]
X2: existence=True all_refs=True branch=False expected=[True, True, False]
```

The auditor's own `git fsck` confirms the premise independently: `dangling
commit <X1>`.

## 2. The fixture (bounded, offline)

Built by `case_unreachable_citation.py` and mirrored, grid-ready, in
`grid-case-fragment.py` (same `builder(tmp) -> (lane, fleet, extra, marker)`
contract as `tests/report-audit/repo-state-grid.py:127`).

**Lane** (`git init -b master`, author `kama-shokunin`, round-1 subjects):

- C1 `round-1: work` (t=1000) — on `master`
- C2 `round-1: more` (t=1500) — on `master`, child of C1
- X1 `round-1: dangling` (t=1600) — commit object written with
  `hash-object -t commit -w`; **no ref points at it**
- X2 `round-1: kept` (t=1700) — same, then pinned by `refs/keep/x2`

**Fleet**: `.ufo/reports/round-1/kama.md` committed by `fleet` (t=2000), with a
`## Landed changes` section citing C1 by a 9-hex prefix and C2, X1, X2 by
their full 40-hex ids. The prefix is chosen by `citation_prefix()` to be the
shortest one that is *both* checkable (contains a digit **and** a letter, per
`checkable_abbrev`, `tools/report-landing-audit.py:182-186`) **and**
unambiguous — otherwise the token would silently stop being a citation and
the case would measure nothing.

**Promisor arm** = the same lane plus config only:
`extensions.partialClone=origin`, `remote.origin.promisor=true`,
`remote.origin.partialclonefilter=blob:none`. Every object stays present; no
`.promisor` pack is created; the object store is complete.

## 3. Expected exits and findings (fixed before implementation)

| case | arm | expected exit | expected kinds | expected findings |
|---|---|---|---|---|
| `P01-unreachable-citation-full` | no promisor metadata | **0** | **[]** | none |
| `P02-unreachable-citation-promisor` | promisor config only | **0** | **[]** | none |

Rationale for P02 = 0 rather than 2: the preregistration's `expected_after`
item 1 requires "exact same substantive clean/failed findings as otherwise
identical full clones, not exit2" for complete promisor-marked clones, and
item 6 requires that "metadata-only declarations do not establish
incompleteness; content completeness and availability of required evidence
determine the outcome". This lane *is* content-complete: every required
object is present. So the two arms must agree exactly.

P01 is a **control**: the repair must leave it byte-identical in outcome. It
already passes on the r23 base.

**Observed on the r23 base** (`observed-base.json`; auditor blob
`cf706c52233139920da60f8b55d06f031286c4f9` at base `0df800e8`):

```
full:     exit=0 kinds=[]
promisor: exit=2 kinds=None
          stderr='could-not-evaluate: <lane>: partial clone (extensions.partialclone)'
```

The promisor exit 2 is the **pre-repair observation**, not the expectation. It
is the harm the repair removes.

**Observed with a scratch repair prototype** (`candidate-repaired.py`,
`candidate-repair.patch` — a 9-line change in `check_history_repo` that
replaces the metadata refusal with an actual missing-object check):

```
P01 [candidate] exit=0 kinds=[]  match=True
P02 [candidate] exit=0 kinds=[]  match=True
```

This proves the expectation is **achievable** — it is not an unreachable
oracle. The prototype is scratch-only; the lane's
`tools/report-landing-audit.py` is unchanged (`git diff --stat HEAD --
tools/report-landing-audit.py` → empty).

## 4. Mutation sensitivity — the case has teeth

Two mutants, each a realistic wrong way to implement "is this citation
available?", both **killed**:

| mutant | mutation | P01 | P02 |
|---|---|---|---|
| `mutant-reachability.py` | `lookup()` filters tokens by the `rev-list --all` closure | exit 1, `unresolved-full-hash` + `landed-unresolved` on **X1** | same |
| `mutant-branch-closure.py` | `lookup()` filters tokens by the `rev-list master` closure | exit 1, both kinds on **X1 and X2** | same |

Exact defect tokens observed:

```
mutant-reachability   full: [('unresolved-full-hash', 'd6ac5ce1aa9a15089c8fe365dd2c9ee7d00546d8'),
                              ('landed-unresolved',     'd6ac5ce1aa9a15089c8fe365dd2c9ee7d00546d8')]
mutant-branch-closure full: [('unresolved-full-hash', '04eddf3735cb31171057f11924041dffd2c8d936'),
                              ('unresolved-full-hash', 'd6ac5ce1aa9a15089c8fe365dd2c9ee7d00546d8'),
                              ('landed-unresolved',     '04eddf3735cb31171057f11924041dffd2c8d936'),
                              ('landed-unresolved',     'd6ac5ce1aa9a15089c8fe365dd2c9ee7d00546d8')]
```

(`d6ac5ce1…` = X1, `04eddf37…` = X2. The hashes differ per fixture build;
the *shape* — X1 and X2 named as unresolved — is the invariant.)

Without X1 and X2 in the fixture, a reachability-based repair would pass
unnoticed. With them, it fails loudly and with the offending token named.

## 5. Offline and containment guarantees

- **No network.** The promisor remote URL points at
  `<scratch>/absent-origin.git`, a path that is **never created** (verified:
  `ls` → *No such file or directory*). Any transport attempt would fail
  instantly and locally.
- **No lazy fetch.** Every git call in the fixture builders and the probe
  passes `--no-lazy-fetch`; the auditor's own `GIT_ISOLATION` already
  includes it (`tools/report-landing-audit.py:93-97`).
- **No payload.** No `core.sshCommand`, no `gpg.program`, no filter transport
  hook, no signing program is configured anywhere in the fixture. The
  transport assertion is payload-free: the runner checks that no
  transport-error text (`does not appear to be a git repository`, `Could not
  read from remote repository`, `unable to access`, `Could not resolve host`)
  appears in the auditor's stderr. Observed: `transport_errors=[]` in both
  arms, both with the base auditor and with the candidate prototype.
- **No fixture escaped scratch.** All fixture repositories are created under
  `/fast/scratch/hyaku/kama-r24/CaseUnreachableCitation/`. `git status
  --porcelain` in the lane shows my writes only under
  `.ufo/waves/round-24/build/out/CaseUnreachableCitation/`; the other
  modifications visible in the lane working tree (`LOG.md`,
  `corpus/SOURCES.md`, `corpus/lessons/round-24.md`,
  `.ufo/waves/round-24/sources-before.json`) carry mtimes 14:56–15:02 from
  sibling seats and are **not** mine.
- **No /tmp fixtures.** The builder writes only under the scratch root; the
  pre-existing `/tmp/kama-*` entries are from earlier rounds, not this case.
- **No suite, no candidate run.** I ran the base auditor and my own scratch
  prototype on this fixture only. I did not run
  `tests/report-audit/repo-state-grid.py`, `isolation-mutants.py`, the
  auditor `--selftest`, or any full-suite command.

## 6. Boundary with the sibling cases (no duplication)

This case is the **complement** of `advice/CaseUnknownCitation.md`, not a
restatement of it. Read together they pin the whole availability rule:

| | citation state | expected |
|---|---|---|
| `CaseUnknownCitation` (sibling seat) | absent from both audited repos of a promisor-backed lane | exit 2, no defect kinds — *unknown*, not proved absent |
| **`CaseUnreachableCitation` (this case)** | **present locally**, but outside the branch closure | **exit 0, no defect kinds** — *found* |

The pair is the discriminating shape: an implementation that answers
availability by **reachability** fails *this* case (it reports a locally
present object as unresolved); an implementation that treats any promisor
metadata as incompleteness fails *the sibling* case and the P02 arm here.
An implementation that answers availability by **object existence** passes
both. Neither case alone can distinguish those two failure modes, so both
rows must land in the grid.

The other sibling cases (`CaseMissingLaneBlob`, `CaseMissingLaneTree`,
`CaseMissingFleetReport`, `CaseMissingFleetTree`, `CaseWrongTypeCitation`,
`CaseAlternatesComplete`, `CaseCompleteLane/Fleet`, `CaseHydratedLane`,
`CaseMarkerLane`) cover different object states and different repositories;
this fixture touches none of their premises — its lane has a **complete**
object store, and the only unusual property is that two cited objects sit
outside the branch closure.

## 7. Integration guidance (for L1)

1. Add the two rows from `grid-case-fragment.py::EXPECTED_CASES` to the
   round-24 `promisor-grid.py` CASES table, or to
   `tests/report-audit/repo-state-grid.py` as two new control rows.
2. Both rows expect **exit 0, no defect kinds**. `REASONS` needs no entry
   (an exit-2 expectation would pin a refusal reason; these rows forbid
   refusal).
3. If the harness keeps a `frozen` arm, the frozen=r23-base auditor will
   report **exit 2 on P02** with `partial clone (extensions.partialclone)`.
   That is the documented policy-row expectation change the preregistration
   already allows ("retained historical r23 grid with explicitly documented
   policy-row expectation changes"); P01 stays 0 on both arms.
4. The case needs no `--errata` and no `--report` override: the fleet report
   is committed at `.ufo/reports/round-1/kama.md` and the lane carries no
   errata table (use `--no-errata`).
5. **Do not** weaken the case by replacing X1 with a `refs/keep/`-held
   object. X1 (no ref at all) is what makes the `--all`-closure mutant
   fail; X2 (ref-held, off-branch) is what makes the branch-closure mutant
   fail. Both are load-bearing.
6. The mutant pair is the recommended negative control for the repair: if
   either mutant survives the integrated grid, the repair resolves
   citations by reachability and will report proved absence for locally
   present objects.

## 8. Residual risk and verification gaps

- **Unrun against the real integrated implementation.** The round-24
  candidate auditor does not exist yet, so the "after" rows are validated
  against my scratch prototype, not against the integrated code. The
  prototype is a *minimal* repair of `check_history_repo` only; a real
  implementation may also change `lookup()` or add a repo-local
  availability cache, and those paths are unexercised here. **Unverified.**
- **The `frozen` arm's P02 expectation is stated, not measured**, because
  the round-24 grid does not exist yet. What I did measure is the r23 base
  auditor's behaviour on this fixture directly (exit 2, `partial clone
  (extensions.partialclone)`), which is the same blob the frozen arm
  selects.
- **X1 depends on `gc.auto=0`** (set at fixture init) to survive as a loose
  object. A harness that runs `git gc` between fixture build and audit could
  prune X1 and turn the case into a vacuous pass. `git fsck` in the
  premise step catches a pruned X1 (it would no longer report
  `dangling commit`), so the failure mode is loud, but the harness must not
  gc the fixture.
- **Scope note.** This case covers citation *resolution*. It does not cover
  the sibling concerns owned by other seats (missing lane blob, missing lane
  tree, wrong-type citation, alternates, marker/metadata-only arms); those
  are separate cases with their own fixtures. This case touches none of
  them and duplicates none of them.
- **Not claimed:** nothing about arbitrary untrusted repositories, about
  closing the inherited parser/alternates/gitfile/size-limit findings, about
  live serving capability, or about a higher scalar score.

## 9. Named files

Written by me (all under the wave's out directory; the lane's production
files are untouched):

- `.ufo/waves/round-24/build/out/CaseUnreachableCitation/case-manifest.json`
  — the expected exits/findings, the pre-repair observation, the mutation
  results, the offline guarantees, the artifact index
- `.ufo/waves/round-24/build/out/CaseUnreachableCitation/case_unreachable_citation.py`
  — fixture builder, premise checks, arms, transport assertion
- `.ufo/waves/round-24/build/out/CaseUnreachableCitation/grid-case-fragment.py`
  — grid-ready builders + `EXPECTED_CASES`
- `.ufo/waves/round-24/build/out/CaseUnreachableCitation/probe_availability.py`
  and `probe-availability.json` — the existence/all-refs/branch measurement
- `.ufo/waves/round-24/build/out/CaseUnreachableCitation/observed-base.json`
  — base-auditor observations for both arms
- `.ufo/waves/round-24/build/out/CaseUnreachableCitation/candidate-repaired.py`
  and `candidate-repair.patch` — scratch-only prototype + its diff
- `.ufo/waves/round-24/build/out/CaseUnreachableCitation/mutant-reachability.py`
  and `mutant-branch-closure.py` — the two killed mutants

This report: `.ufo/waves/round-24/build/advice/CaseUnreachableCitation.md`.

**Report:** `.ufo/waves/round-24/build/advice/CaseUnreachableCitation.md`
