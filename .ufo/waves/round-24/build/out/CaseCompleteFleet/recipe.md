# Case recipe — complete fleet with promisor config

Round 24, lane `CaseCompleteFleet`, base `0df800e896f6bce285a81e794ad4ae1d1e6c3a71`.
Everything below is offline: no network, no transport, no repository program.

## 0. Run it

```
python3 .ufo/waves/round-24/build/out/CaseCompleteFleet/case_complete_fleet.py \
    --auditor <path>/tools/report-landing-audit.py --json
```

Script exit: `0` the oracle holds (promisor arm == full arm, both clean) ·
`1` the oracle is violated (base behaviour) · `2` could not evaluate
(premise, auditor, timeout, containment, transport).

The builder refuses any `--scratch` outside `/fast/scratch/`.

## 1. Repositories (all under the scratch root)

**lane** (one repo, copied byte for byte into a second directory so no arm can
influence the other).  Author `kama-shokunin` unless stated.

| commit | author time | subject | file |
|---|---|---|---|
| L1 `work` | 1000 | `round-1: work` | `f` |
| L2 `measure` | 1100 | `round-1: measure` | `f` |
| L3 `late` | 1300 | `round-1: late advice` | `f` |
| E1 | 1350 | `fixture: empty errata registry` (author `fixture`) | `registry/report-landing-errata.tsv` (empty) |

E1 exists so the default errata path (`<lane tip>:registry/report-landing-errata.tsv`)
resolves; its author is not `kama-shokunin`, so it is never a required
round candidate.  The empty errata file keeps the audit at "clean".

**fleet** (two repos with identical commits, plus one discriminator).

| fleet | report first add | report revision | promisor metadata |
|---|---|---|---|
| `fleet-full` | 1200 | 1400 | none |
| `fleet-promisor` | 1200 | 1400 | `extensions.partialClone=origin`, `remote.origin.promisor=true`, `remote.origin.partialclonefilter=blob:none`, `remote.origin.url=<scratch>/no-such-origin.git` (never created) |
| `fleet-late-add` (discriminator) | 1400 | — | none |

The report is `.ufo/reports/round-1/kama.md` and cites **L1 and L2 only**; it
does not cite L3.  The 1400 revision appends a `## Notes` section and leaves
the `## Landed changes` section intact.

Because the promisor metadata lives in `.git/config` and not in a commit,
`fleet-full` and `fleet-promisor` have the **same HEAD**
(`11aec768f817b059af48926125163f9bb92cdbbc` at the time of writing) and the
same tree; the manifest `fixture-manifest.json` records them.

## 2. Premises the builder verifies before any audit runs

1. both fleets have the same HEAD and tree;
2. both fleets are **complete**: `git rev-list --objects --all --missing=print`
   yields no `?<oid>` line (no object is missing — this is what makes the
   promisor marking metadata only);
3. the promisor arm really carries `extensions.partialclone=origin` and
   `remote.origin.promisor=true`; the full arm carries neither;
4. the promisor URL is a **local path that does not exist**, so no transport
   is even possible;
5. neither fleet has a `objects/pack/*.promisor` file (this case is about
   config metadata, not about a blobless clone);
6. the report is touched twice: `git log --diff-filter=A --format=%at` yields
   exactly `1200`, and the full path log yields `1200` and `1400`;
7. the lane holds exactly three `round-1:` commits by `kama-shokunin`
   (1000, 1100, 1300) and the two lane copies have the same HEAD;
8. the report cites L1 and L2 and does not cite L3.

Any failed premise is a `could-not-evaluate` (script exit 2), never a pass.

## 3. Audit invocations

```
python3 <auditor> --lane-repo <lane-full>    --fleet-repo <fleet-full>    --rounds 1 --json
python3 <auditor> --lane-repo <lane-promisor> --fleet-repo <fleet-promisor> --rounds 1 --json
python3 <auditor> --lane-repo <lane-full>    --fleet-repo <fleet-late-add> --rounds 1 --json
```

The auditor runs with no inherited `GIT_*`, `GIT_CONFIG_GLOBAL=/dev/null`,
`GIT_CONFIG_NOSYSTEM=1`, a 60 s limit, its own process group (a timeout
kills the group), and the working directory set to the scratch root.

## 4. Expected results (registered before any implementation)

| arm | exit | findings | cutoff | required | post_report | status |
|---|---|---|---|---|---|---|
| full | 0 | `[]` | 1200 | 2 | 1 | clean |
| promisor | **0** | **`[]`** | **1200** | **2** | **1** | **clean** |
| discriminator (`fleet-late-add`) | 1 | `landed-omitted` for L3 | 1400 | 3 | 0 | failed |

The promisor arm must equal the full arm on `exit`, `findings`, `cutoff`,
`required`, `post_report`, `summary_status`, `summary_defects`,
`summary_uncorrected`, `summary_required_commits`,
`summary_post_report_commits`.

The discriminator proves the case is not vacuous: with the same lane and the
same report bytes, a first add at 1400 makes the uncited lane commit of 1300
a *required* citation, and the verdict flips to `landed-omitted`.  The clean
verdict of the case is reachable only through the correct **first-add**
cutoff of 1200.

## 5. At base (0df800e) the case is violated, on purpose

```
arm full:     exit=0 findings=[] cutoff=1200 required=2 status=clean
arm promisor: exit=2 stderr="could-not-evaluate: <fleet>: partial clone (remote.origin.promisor)"
discriminator: exit=1 findings=[('landed-omitted', <L3>)]
script exit:  1
```

The refusal comes from `tools/report-landing-audit.py:465`
(`raise EvalError(f"{repo}: partial clone ({key})")`), reached from
`check_history_repo` (line 438), which runs on both the lane and the fleet
before any object is looked at.

## 6. Containment checks the builder performs after every run

* object store, refs, `count-objects -v` and HEAD of every fixture repo are
  byte-identical before and after the audit runs — no lazy acquisition, no
  fetch, no new refs;
* stderr of every run is scanned for transport markers (`does not appear to
  be a git repository`, `Could not read from remote repository`,
  `unable to access`, `Connection refused`, …); any hit is a containment
  failure (script exit 2);
* the kama repository (`/home/vgpnk/Projects/shokunin/kama-shokunin`) is
  snapshotted (HEAD, `status --porcelain`, `count-objects -v`) before and
  after and must be identical;
* the fixture root must be under `/fast/scratch/`.
