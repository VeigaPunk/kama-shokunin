# CaseAlternatesComplete — offline oracle case: `clone --shared` backed by a complete local marked store

Round 24, C1 calibration 7→7 (lowest assigned axis: operability harm repair).
Base `0df800e896f6bce285a81e794ad4ae1d1e6c3a71`. Lane role: leaf member, no
dispatch. No production file was written; no lane/fleet/sibling repo was
touched; no commits, no pushes; no tool installed.

## Verdict

**One offline oracle case, specified and constructed, with its expectation
derived before any candidate implementation exists.**

The case is: *a `git clone --shared` of a local repository that is
promisor-marked but whose content is complete.* The correct answer is the same
substantive verdict as an otherwise identical full clone — here **exit 1
(failed) with exactly one defect, `landed-omitted ce743590588f9a15c068e2c3a3e4a1b6648fdf8f`**
— never exit 2.

At the frozen base the case **fails exactly one arm**: the shared clone that
is itself promisor-marked is refused with
`could-not-evaluate: …/case2-lane: partial clone (remote.origin.promisor)`
(exit 2). That refusal is triggered by the *declaration alone*: a fresh pair
of shared clones from the same store, with the three declaration keys unset,
answers exit 1 with the identical finding set. This is the r23 harm the
round-24 repair must undo.

## The case (one store, four arms, identical content)

Fixture store `store/` (local, offline, one branch `master`):

| object | author | author time | subject | path |
|---|---|---|---|---|
| `db796f8b820bf3825c58832419138cdba23206a7` (A) | `kama-shokunin` | 1000 | `round-1: work` | `f` |
| `ce743590588f9a15c068e2c3a3e4a1b6648fdf8f` (B) | `kama-shokunin` | 1100 | `round-1: more` | `g` |
| `1940965bce034fac27efbdbeb7284f48d654324f` (R) | `fleet` | 2000 | `round-1: report` | `.ufo/reports/round-1/kama.md` |

The report blob is `315f23b8fdb782eabb6e4cf8201d4f79fc18b885`; its body cites
A only:

```
# kama round 1

## Work performed

Round-1 fixture: two local lane commits, one cited below.

## Landed changes

- db796f8b820bf3825c58832419138cdba23206a7 round-1: work
```

So the report's first-add cutoff is R's author time 2000; A and B are both
required lane commits; the report cites A only; **B is the one substantive
defect** (`landed-omitted`).

Arms (lane and fleet repo of each arm are built from the *same* store):

| arm | construction | marking |
|---|---|---|
| `control` | `git clone --no-hardlinks store` (own objects) | none |
| `case-1` | `git clone --shared store` (alternates only) | store marked; clone carries none |
| `case-2` | `git clone --shared store` (alternates only) | store marked **and** clone marked |
| `case-2-unmarked` (diagnostic) | `git clone --shared store` | clone's three declaration keys unset |

"Marked" = the promisor declaration, config only, no promisor pack:

```
core.repositoryformatversion = 1
extensions.partialclone      = origin
remote.origin.url            = <nonexistent LOCAL path>   # no transport can succeed
remote.origin.promisor       = true
remote.origin.partialclonefilter = blob:none
```

## Expected exits and findings (the oracle)

| arm | exit | defects | summary |
|---|---|---|---|
| `control` | 1 | `landed-omitted ce743590588f9a15c068e2c3a3e4a1b6648fdf8f` | reports=1 defects=1 uncorrected=1 required=2 post_report=0 status=failed |
| `case-1` | 1 | same single defect | same |
| `case-2` | 1 | same single defect | same |
| `case-2-unmarked` (diagnostic) | 1 | same single defect | same |

All three graded arms must agree on **exit code and the defect set**, not
merely on the exit code: a candidate that answers exit 0 on the marked arms
(pretending the omission is not there) fails this case, and so does one that
answers exit 2.

### Why the marked arms are *entitled* to that verdict (content, not metadata)

The expectation does not rest on any declaration. It rests on measured
content, and the builder asserts each of these premises before the audit runs
(all 38 premise checks in `observed-base-before.premise` are `True`):

* the store holds A, B, R and the report blob, and
  `git -C store rev-list --objects --all --missing=print` emits **no `?`
  line** — nothing is missing from the store;
* in every arm, `git cat-file -t` (with `--no-lazy-fetch`) resolves A, B and
  the report blob, and `git rev-list --objects --all --missing=print` emits no
  `?` line: every reachable object is present *locally* (own objects or
  alternates);
* `git rev-list --objects --all` is **byte-identical** across the control and
  both shared arms (lane and fleet): the arms differ in metadata and in where
  the bytes live, not in content;
* the shared arms really borrow — `git count-objects -v` reports `count: 0`,
  `in-pack: 0`, `alternate: …/store/.git/objects`; the control arm holds its
  own objects.

Two facts about git that the case also pins down (git 2.56.0, observed):

1. **`git clone --shared` does not inherit the promisor declaration.** The
   clone's config after cloning the marked store contains only
   `core.*`, `remote.origin.url`, `remote.origin.fetch`, `branch.master.*` —
   no `remote.origin.promisor`, no `extensions.partialclone`, and
   `core.repositoryformatversion` back to 0. Metadata inheritance is not a
   channel here; the marking must be *stated* on the clone to be seen at all.
   (That is why `case-2` marks the clone explicitly and `case-1` does not.)
2. **Objects borrowed through `objects/info/alternates` resolve as local**:
   `git --no-lazy-fetch cat-file --batch-check` on the shared clone answers
   `<oid> commit 174` for an object that exists only in the store, and
   `<oid> missing` for one that exists nowhere. With the declaration removed
   from the clone (`case-2-unmarked`) the audit answers exit 1 with the same
   defect set, which isolates the declaration as the sole cause of the base's
   exit 2.

### Base observation (the "before" side), frozen base blob

`audit-base.py` is `git show 0df800e:tools/report-landing-audit.py`; the
working-tree copy is byte-identical to that blob at the time of the run
(`git diff 0df800e -- tools/report-landing-audit.py` empty; blob sha256
`da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1`).

Command (per arm; `--rounds 1 --no-errata --json`):

```
python3 case_alternates_complete.py --build --auditor audit-base.py \
        --policy before --json
```

| arm | observed exit | observed defects | base expectation (`--policy before`) | match |
|---|---|---|---|---|
| `control` | 1 | `landed-omitted ce743590…` | exit 1, same defect | yes |
| `case-1` | 1 | `landed-omitted ce743590…` | exit 1, same defect | yes |
| `case-2` | **2** | none (stderr: `could-not-evaluate: …/case2-lane: partial clone (remote.origin.promisor)`) | exit 2 (r23 blanket refusal) | yes |
| `case-2-unmarked` | 1 | `landed-omitted ce743590…` | exit 1, same defect | yes |

Under the round-24 expectation (`--policy after`, exit 1 and the same defect
set in every arm) the base matches 3 arms and fails `case-2`
(`observed-base-after.json`). That single failing arm is the harm this case
exists to catch.

## Row spec for `tests/report-audit/promisor-grid.py` (candidate integration)

```python
# ids, arm, grade, expected exit, expected defect set
("alternates-complete-control",        "control",        "control", 1, [("landed-omitted", "ce743590588f9a15c068e2c3a3e4a1b6648fdf8f")]),
("alternates-complete-shared",         "case-1",         "control", 1, [("landed-omitted", "ce743590588f9a15c068e2c3a3e4a1b6648fdf8f")]),
("alternates-complete-shared-marked",  "case-2",         "fault",   1, [("landed-omitted", "ce743590588f9a15c068e2c3a3e4a1b6648fdf8f")]),
("alternates-complete-unmarked",       "case-2-unmarked","control", 1, [("landed-omitted", "ce743590588f9a15c068e2c3a3e4a1b6648fdf8f")]),
```

`control` rows are ordinary verdicts that must hold in every arm (they also
prove the marked arms are not silently excused); `fault` row is the r23 harm.
The frozen r23 base must fail the `fault` row and pass the three `control`
rows.

## Offline / isolation proof (all checked, not asserted)

* **No transport.** A `git` shim first on `PATH` recorded every git invocation
  the auditor made: 25 calls in the `control`/`case-1`/`case-2-unmarked` arms
  and 6 in `case-2` (it stops at the refusal). Every call is a local
  read — `rev-parse`, `config --null --list`, `for-each-ref`, `ls-tree`,
  `show`, `log`, `cat-file --batch-check` — and every call carries
  `--no-replace-objects --no-lazy-fetch` plus the `-c` isolation flags
  (`log.follow=false`, `log.showRoot=true`, `log.showSignature=false`,
  `log.mailmap=false`). No `fetch`, `ls-remote`, `upload-pack`, `send-pack`,
  `pull`, `push`, `clone`, `archive --remote`, `submodule` or `credential`
  call appears in any log (`git-calls-*.log`).
* **No reachable remote.** The promisor remote of the marked store and of the
  marked clone points at `<scratch>/run/no-such-promisor-remote`, which does
  not exist. Even if a git invocation had tried to use it, no transport could
  succeed and no network is involved. Independently observed: in a marked
  clone, `git cat-file -e <absent-oid>` **without** `--no-lazy-fetch` tries to
  fetch and fails (`fatal: '…/no-such-promisor-remote' does not appear to be
  a git repository`); with `--no-lazy-fetch` it answers `missing` silently.
  The isolation flag is therefore load-bearing for this case and must be
  preserved.
* **No execution payload.** No repository-configured program is involved: the
  fixture sets no `core.sshCommand`, no filter, no hook; the only program run
  is git itself, and no script is executed from a repository.
* **No fixture escaped the scratch.** Everything the builder creates lives
  under `/fast/scratch/hyaku/kama-r24/CaseAlternatesComplete/run` (1.3 MB);
  the builder asserts every path it creates is under that root
  (`premise all_paths_under_scratch: True`). Nothing was written to `/tmp`
  (`find /tmp -maxdepth 2 -name '*.git' -newermt '-2 hours'` → empty). In the
  lane repository, `git status --porcelain` shows only this wave's build
  directory as untracked; `LOG.md` shows as modified, which is another
  writer's change, not mine (`git diff --stat 0df800e -- tools/report-landing-audit.py`
  is empty, and I wrote no file under `tools/`).
* **No installs.** No package, tool or service was installed or updated; no
  pacman/uv/cargo/npm transaction was run.

## Reproducible artifact and the source of the expected result

* Builder/oracle: `.ufo/waves/round-24/build/out/CaseAlternatesComplete/case_alternates_complete.py`
  (sha256 `23d4718328726546d7591d38b880d6ae232c1a789f825c08c26cc26a71690929`).
  It builds the fixture, checks the premises, runs any auditor under test
  through the `git` shim, and grades the arms against the expectation table
  above (`--policy after|before` selects the round-24 invariant or the r23
  baseline).
* The fixture is byte-deterministic: fixed author/committer names, fixed
  `@<epoch> +0000` dates, fixed bytes ⇒ fixed object ids (A, B, R and the
  report blob are asserted at build time; a moved id aborts the run with a
  premise error, so the oracle can never drift silently).
* **Source of the expected result** (it is not copied from a candidate run):
  the expected verdict is the verdict of the *control* arm — the same content
  in an ordinary full clone — evaluated by the frozen base auditor, i.e. the
  substantive semantics that exist independently of any promisor marking.
  The marked arms must reproduce it; the `case-2-unmarked` arm (same shared
  clones, declaration removed) independently reproduces it at base, so the
  declaration is provably the only variable. The expectation is therefore
  fixed before the candidate exists and is not a transcript of one.

## Open policy question for L1 (does not change this case's expectation)

This case is **policy-agnostic**: its expectation (exit 1, same defect set)
holds under either reading of "promisor-backed", because nothing is missing
in it. The reading matters for the *missing-evidence* rows, and I flag it
rather than decide it:

* Does a shared clone whose **alternate store** is promisor-marked count as
  promisor-backed? The clone has no fetch path of its own (git consults the
  clone's own config for lazy fetch, not the alternate's), so its absence of
  an object is arguably evidence. But the alternate store, if marked, could
  itself fetch the object, so its absence is not evidence *there*.
* Conservative choice (recommended for the repair): treat an audited
  repository as promisor-backed if the repository itself is marked **or** any
  store named in its `objects/info/alternates` is marked, and then treat
  *missing* required objects as unknown (exit 2) instead of as defects.
  This choice cannot change my case's outcome (nothing is missing), so the
  grid stays consistent whichever way L1 decides.

## Verification gaps (not verified here)

* Only git 2.56.0 / Python 3.14.8 on this host; other git versions were not
  exercised (in particular whether older git copies `remote.origin.*` on
  clone — the "no metadata inheritance" observation is version-scoped).
* This case cannot distinguish a candidate that repairs the refusal from one
  that simply deletes the promisor check and ignores promisor semantics
  entirely; that requires the missing-evidence rows (exit 2 for an
  unavailable required object, exit 2 for an unresolvable citation in a
  promisor-backed repository) — other round-24 cases, not this one.
* No promisor **pack** sidecar (`objects/pack/*.promisor`) was used: the
  marking here is config-only, which is the base's second refusal trigger.
  A store carrying a real `.promisor` sidecar was probed separately (in
  scratch): git then treats objects in the alternate as promisor objects, and
  a missing-object lookup in the clone still answers `missing` under
  `--no-lazy-fetch`. Not turned into a graded row here.
* The fleet side is exercised only in the "the report is present and
  committed" shape; a missing report blob (exit 2 by the audit's own
  contract) is out of this case's scope.
* I did not run the candidate, the r23 grid, the auditor selftest or any
  suite: only the frozen base auditor against this fixture, as recorded above.

## Files written

* `.ufo/waves/round-24/build/advice/CaseAlternatesComplete.md` (this report)
* `.ufo/waves/round-24/build/out/CaseAlternatesComplete/case_alternates_complete.py`
  — fixture builder + oracle (the recipe; deterministic, offline)
* `.ufo/waves/round-24/build/out/CaseAlternatesComplete/audit-base.py` —
  frozen base auditor blob (`0df800e:tools/report-landing-audit.py`)
* `.ufo/waves/round-24/build/out/CaseAlternatesComplete/row-spec.json` —
  machine-readable row spec for `tests/report-audit/promisor-grid.py`
  (ids, arms, grades, expected exit and defect sets, constraints)
* `.ufo/waves/round-24/build/out/CaseAlternatesComplete/observed-base-before.json`,
  `observed-base-after.json` — base observations under both expectation policies
* `.ufo/waves/round-24/build/out/CaseAlternatesComplete/observed-base-before.premise`,
  `observed-base-after.premise` — the 38 premise checks
* `.ufo/waves/round-24/build/out/CaseAlternatesComplete/git-calls-*.log` —
  every git invocation the auditor made, per arm (transport proof)
* Fixture trees: `/fast/scratch/hyaku/kama-r24/CaseAlternatesComplete/run/`
  (rebuilt deterministically by `--build`)
