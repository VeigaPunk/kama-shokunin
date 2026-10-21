# OracleMissingNonrequired — r24 findings

Lane: `OracleMissingNonrequired` (reviewer/oracle). Wave 24, C1 calibration 7→7
(promisor metadata vs. unavailable evidence).
Base audited: `0df800e896f6bce285a81e794ad4ae1d1e6c3a71` (frozen r23).
Preregistration: `.ufo/waves/round-24/preregistration.json`.
Scratch: `/fast/scratch/hyaku/kama-r24/OracleMissingNonrequired/`.

## Verdict

**Refusing the entire `--all` object graph would add BOTH scope and harm, and
must not be the r24 repair.** The r24 completeness check must be rooted at the
audit's own evidence roots — the pinned selected lane branch tip and the pinned
fleet `HEAD` — not at every ref in the object store. A genuinely incomplete
object that lives only on an unrelated, unselected branch is **not** required
evidence: the expected outcome is the same clean verdict as an otherwise
identical complete repository (exit 0, no findings), **not** exit 2.

This is the same over-refusal harm class that got r23 rejected
(`preregistration.expected_before`), reached by a different route: r23 refused
on *metadata*, an `--all`-rooted check would refuse on *unrelated objects*.
Both make a complete-for-its-evidence repository unevaluable.

## Axes

1. **Verdict correctness** — clean/omission verdicts survive for complete local
   repositories; only genuinely unavailable *required* evidence yields exit 2.
2. **No-harm (operability)** — the repair must not reintroduce refusal of
   repositories that hold every object the audit reads.
3. **Scope discipline** — the required set must equal the evidence set, not
   "everything git can see".
4. **Isolation** — no lazy fetch, no transport, no replace-ref substitution, no
   signature program, deadlines preserved.
5. **Determinism** — the verdict must not depend on unrelated refs the
   operator happens to have locally.

## The question, answered

*Would refusing the whole `--all` graph add scope/harm?* Yes, on three
independent counts (all measured, see `measurements.md` §3):

1. **Scope creep.** `--all` covers every ref: other branches, remote-tracking
   refs, tags, stash. The auditor reads **none** of them. Requiring their
   closure means requiring objects that are not evidence — the required set
   becomes strictly larger than the evidence set.
2. **Over-refusal (harm).** With one missing object on an unselected branch,
   an `--all`-rooted check yields exit 2 on a repository that is complete for
   every object the audit reads (`marked` variant: lane-root and fleet-root
   walks are clean; only the `--all` walk reports the object). That is the
   exact harm r23 was rejected for, re-entering through the back door.
3. **Operational hazard.** In a promisor-marked repository the *default*
   missing action of `git rev-list --objects` is not "print": without
   `--no-lazy-fetch` it **attempts a fetch from the promisor remote**
   (measured: `fatal: '.../nonexistent.git' does not appear to be a git
   repository`, rc=128) and with `--no-lazy-fetch` it dies
   (`fatal: missing blob object '<sha>'`, rc=128). Only an explicit
   `--missing=print` yields rc=0 and a `?<sha>` line. An `--all` walk is
   therefore both the wrong scope and the most dangerous traversal to run.

Counter-argument considered and rejected: "the missing object on the
unselected branch shows the repository is a partial clone, so the selected
branch may be incomplete too." That risk is already covered — directly and
completely — by checking the closure **of the selected root itself**: a missing
object reachable from the selected lane tip *is* reported by the root-scoped
walk (measured in the `selected_missing` variant: lane-root walk reports
`?b8f99f5b…`, while `--all` reports the same line). `--all` adds no safety
here; it only adds scope.

## Targeted evidence roots (base `0df800e`, `tools/report-landing-audit.py`)

| Root | How the auditor reaches it | Base lines | What it covers |
|---|---|---|---|
| **Lane selected branch tip** | `resolve_branch()`: `refs/heads/<branch>` peeled to a commit, pinned once; a plain name never resolves to a tag or other ref | 489–499 | `git log <tip>` → all ancestors (round candidates, `round_commits()`, 189); `corpus/SOURCES.md` blob at tip (`load_source_urls()`, 258); `registry/report-landing-errata.tsv` blob at tip (`load_errata()`, 374) |
| **Fleet `HEAD`** | `git rev-parse --verify HEAD^{commit}` | 517 | report blob at HEAD (`git show HEAD:<rel>`, 310); report-path history and first-add cutoff (`report_cutoff()`, 215) |
| **Cited tokens (presence, not closure)** | `cat-file --batch-check` per repo over the local object store | 139–174 | cited hashes, `## Landed changes` tokens, errata corrections |

**Not evidence, and therefore not part of the required set:** every ref other
than `refs/heads/<branch>`; objects unreachable from the roots (dangling
objects, unrelated branch tips); blobs of paths the audit never reads.

Note on the fleet side: the *branch* dimension is settled here (fleet root =
`HEAD`); narrowing the fleet root further to the report path only (i.e. not
requiring unrelated historical fleet blobs) is a different question and
belongs to the `RevDraft` lane.

## Independent expected outcome (pinned before any candidate exists)

Machine-readable: `.ufo/waves/round-24/build/out/OracleMissingNonrequired/expected.json`
(`pinned_before_candidate: true`, `candidate_exists_at_pinning: false`).

| Row | Fixture variant | Expected exit | Expected findings |
|---|---|---|---|
| `N01-missing-object-unselected-branch` | `marked`: lane promisor-marked, missing blob of the unselected `side` branch; fleet ordinary | **0** | `[]` (clean) |
| `N02-missing-object-fleet-unselected-branch` | `fleet_marked`: incomplete object in the fleet's unselected branch | **0** | `[]` (clean) |
| `N03-missing-object-selected-branch` | `selected_missing`: the missing blob **is** reachable from the selected lane branch | **2** | could-not-evaluate, never clean/failed |
| `N04-unmarked-twin-control` | `unmarked_twin`: identical content, partial-clone metadata removed, same missing object still absent | **0** | `[]` (clean) |

Pinned expected substance for N01/N02/N04 (identical to the unmarked twin's
measured output):

```
summary: defects=0 uncorrected=0 required_commits=1 post_report_commits=0
         reports=1 status=clean
result : round=1 cutoff=2000 report_committed=true round_commits=1 required=1
```

The twin is what fixes the verdict **independently of the candidate**: it is
the same content with the metadata removed, so it exercises the auditor's
normal path and pins the substantive verdict. N01 must reproduce it byte for
byte (same summary, same `results` entries).

## Bounded offline fixture recipe

Builder: `.ufo/waves/round-24/build/out/OracleMissingNonrequired/build_fixture.py`
(drop-in grid version: `…/case_missing_nonrequired.py`; runner: `…/measure.sh`).

1. `git init -q -b master` a lane repo and a fleet repo.
2. Lane: commit `round-1: work` by author `kama-shokunin`, author time 1000,
   file `f` → the cited commit `C`.
3. Lane: `git checkout -b side`; commit `side work` by another author, author
   time 1500, file `side.txt`; back to `master`.
4. Fleet: commit `.ufo/reports/round-1/kama.md` (author `fleet`, time 2000)
   containing `## Landed changes` with the full hash of `C` → first-add cutoff
   2000, `C` required and cited → clean.
5. Mark the lane (and, for N02, the fleet) as a partial clone **by metadata
   only**: `remote.origin.promisor=true`,
   `remote.origin.partialclonefilter=blob:none`,
   `remote.origin.url=<nonexistent local path>` (never a network URL),
   `extensions.partialclone=origin`.
6. Make one object genuinely incomplete: delete the loose object file
   `.git/objects/<xx>/<38 hex>` of the `side` blob (N01/N02) or of the
   selected-branch blob `f` (N03). The commit and tree remain; only the blob
   bytes are gone — exactly what a blobless clone that was never hydrated
   looks like.
7. Premises asserted by the builder (no auditor involved): the object is
   absent (`cat-file -e` rc≠0), `C` is present and peels to a commit,
   `side` is not an ancestor of `master`, the all-refs walk reports the
   `?<sha>` line, and the rooted walks (`master`, fleet `HEAD`) are clean —
   except in N03, where the rooted lane walk reports the `?<sha>` line.

No clone, no transport, no network, no payload: everything is local `git`
plus one `unlink()` of a loose object.

## Measured baseline (frozen r23 auditor) and plain-git facts

Full log with exact commands: `.ufo/waves/round-24/build/out/OracleMissingNonrequired/measurements.md`
(frozen auditor sha256 `da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1`,
git 2.56.0, Python 3.14.8).

Frozen r23 on the same fixtures — the harm this lane targets:

```
marked            → exit 2  could-not-evaluate: …/lane: partial clone (remote.origin.promisor)
fleet_marked      → exit 2  could-not-evaluate: …/lane: partial clone (remote.origin.promisor)
selected_missing  → exit 2  could-not-evaluate: …/lane: partial clone (remote.origin.promisor)
unmarked_twin     → exit 0  defects=0 status=clean cutoff=2000 required_commits=1
```

Plain-git facts the candidate's closure check depends on (all measured):

```
git rev-list --objects --all                                   rc=128  fatal: '…/nonexistent.git' does not appear to be a git repository   (lazy fetch attempted)
git --no-lazy-fetch rev-list --objects --all                   rc=128  fatal: missing blob object '<sha>'
git --no-lazy-fetch rev-list --objects --missing=print --no-object-names --all
                                                            rc=0    …  ?<sha>            (the unselected branch's object)
git --no-lazy-fetch rev-list --objects --missing=print --no-object-names master
                                                            rc=0    3 objects, no '?' line  (lane root clean)
git --no-lazy-fetch cat-file --batch-check <<< <sha>          '<sha> missing'
GIT_TRACE=1 git --no-lazy-fetch cat-file -e <sha>             0 trace mentions of fetch/remote (no transport)
```

Consequences for the implementation:

- the closure check **must** pass `--missing=print` explicitly (the default
  action in a promisor-marked repository is a fatal error or a fetch attempt);
- it must keep `--no-lazy-fetch` (already in `GIT_ISOLATION`, base line 93);
- it must be **root-scoped**: `master`/selected tip for the lane, `HEAD` for
  the fleet — never `--all`.

## Mutants this case must kill

| Mutant | Effect on N01/N02 | Killed by |
|---|---|---|
| blanket metadata refusal (the r23 behaviour) | exit 2 | N01, N02 |
| all-refs (`--all`) closure refusal | exit 2 | N01, N02 |
| "any missing object anywhere → exit 2" | exit 2 | N01, N02 |
| skip the completeness check entirely | N03 returns 0/1 instead of 2 | N03 |
| refuse a repository whose *metadata* says partial clone, even when complete | exit 2 | N01, N02, N04 |

## No-harm boundaries the candidate must keep (verified in the same fixture)

- no lazy fetch / no transport: the promisor remote URL is a nonexistent
  **local** path and the trace shows no fetch attempt (`--no-lazy-fetch`);
- `--no-replace-objects` and the other `GIT_ISOLATION` entries stay in force
  (base line 93) — this lane adds no new git channel;
- the per-call deadline stays (`GIT_TIMEOUT`, base line 108) — a rooted
  closure walk is one extra bounded call per repository;
- `--no-lazy-fetch` on old git (< 2.45) remains an `EvalError`, i.e. exit 2,
  never a verdict.

## Verification gaps (unverified by this lane)

- **The r24 candidate was not run**: it does not exist at pinning time. The
  only auditor exercised is the frozen r23 base; the expected outcomes above
  are pinned against the **unmarked twin's measured output**, not against a
  candidate.
- A *genuine* partial clone (real `--filter=blob:none` clone with a
  `.promisor` pack marker, where git's promise table is populated) was not
  constructed here: the fixture marks the metadata by hand and removes one
  loose object. In a genuine clone, git's default missing action may skip
  promised objects silently instead of failing; the `--missing=print`
  requirement above is therefore *stronger* than the hand-marked fixture
  strictly proves. The `CaseHydratedLane`/`CaseHydratedFleet` lanes own the
  genuine-clone measurement.
- The `--all` walk's behaviour when the repository has a real `.promisor`
  pack (allow-promisor vs. error) was not measured (same reason).
- The fleet-side narrowing question (required set = report path only, not the
  whole `HEAD` closure) is **not** decided here; it is `RevDraft`'s scope.

## Named files

- Advice (this file): `.ufo/waves/round-24/build/advice/OracleMissingNonrequired.md`
- Pinned expected outcome: `.ufo/waves/round-24/build/out/OracleMissingNonrequired/expected.json`
- Fixture builder: `.ufo/waves/round-24/build/out/OracleMissingNonrequired/build_fixture.py`
- Drop-in grid case: `.ufo/waves/round-24/build/out/OracleMissingNonrequired/case_missing_nonrequired.py`
- Measurement runner + log: `.ufo/waves/round-24/build/out/OracleMissingNonrequired/measure.sh`,
  `.ufo/waves/round-24/build/out/OracleMissingNonrequired/measurements.md`
- Scratch fixture: `/fast/scratch/hyaku/kama-r24/OracleMissingNonrequired/fixture/{marked,unmarked_twin,fleet_marked,selected_missing}/`
- Audited base file: `tools/report-landing-audit.py` @ `0df800e896f6bce285a81e794ad4ae1d1e6c3a71`
