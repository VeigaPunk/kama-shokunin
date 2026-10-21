# Row F06-lazy-fetch-command — independent hand rebuild

**Verdict: HOLDS as graded; PARTIALLY FALSIFIED as a closed channel.**
The fault premise is real and I observed it on the frozen arm: a missing-object
lookup in the lane ran the repo-configured `core.sshCommand` (marker recreated),
and frozen returned exit 1 with defects. The graded expectation (exit 2,
`partial clone`) is the correct substantive call for this fixture, not merely
current's output. But the committed detector matches config **names** and
ignores values: a lane carrying `remote.<name>.promisor = false` — which git
treats as non-promisor and never lazy-fetches from — flips a clean audit
(0→2) and a true omission (1 `landed-omitted`→2) into `could-not-evaluate`.
The frozen arm evaluates those same repos correctly with no execution, so the
flip is introduced by the round's isolation work and is not covered by the
declared T01 tradeoff (`corpus/lessons/round-23.md:83-84`: "partial clones and
shallow clones are refused even when every cited object is local").

Base `245a37f69628c2c6bb29bbf17897d8fb5946c857`; clone
`/tmp/kama-r23w2/RowF06LazyFetch-2` HEAD verified equal and worktree clean.
Committed auditor blob `f10d811eafcc5bc853abdf75c4a05ec2374cd579`
(sha256 `f228f17420134a4a4fb6d1f93b943f78647e7e60882f767e6cb7cba11d6928a7`);
frozen blob `fcc255ce5115a749dfbd09cf992ba9851a2dc90a` from
`4fe9339f8fc3a4a4a479d9c938a850da12f1124d:tools/report-landing-audit.py`
(sha256 `09ecd63bdc3a5be5264e6d2966602a32e52ca0678dc89de99959318245ab3b3f`).
Runtime: git 2.56.0, CPython 3.14.8. No installs or upgrades were needed or made.

**Environment caveat (not mine):** while this seat ran, the lane working tree
was modified by another actor — `tools/report-landing-audit.py` (mtime
2026-10-21 12:55:56, sha256 `3fc567ab...`, 39 insertions/23 deletions vs
committed), plus `tests/report-audit/repo-state-grid.py` and
`isolation-mutants.py` (`git status --porcelain`). I did not write, revert or
integrate any lane file. Every "current" measurement below is pinned to the
committed blob `f228f174…` archived in `out/RowF06LazyFetch-2/`; the grid
cross-check runs from the clean clone. A grid/auditor run that defaults to the
lane worktree path now measures the dirty file, not 245a37f6.

**Contract breach (self-reported, at the L1's direction).** The V5/V6 probes in
`probe2.sh` captured `git rev-parse --git-path objects/pack`, which prints the
**relative** path `.git/objects/pack`; the later shell redirections resolved it
against the process cwd `/home/vgpnk/Projects/shokunin`, not against the
fixture. At 12:50:16 and again at 12:58:00 -0300 the script therefore created
zero-byte `.promisor` markers next to the **real fleet packs**:
`.git/objects/pack/pack-22727cb1bcc67a7ba804c7e9ed3fb5d0dec3812d.promisor`,
`pack-3cd47c8a034bb088d889f993bfd2eaa569f73acd.promisor`,
`pack-e193a79004e5d3868405113951a811b60b47b59a.promisor`, and
`pack-deadbeef.promisor` (zero bytes). That writes the fleet root, which this
seat's contract forbids; the L1 removed them (verified read-only at 13:00: no
`*.promisor` remains in that directory). I stopped probing when told and wrote
nothing further to that repository. Consequences for this report: (a) the
V5/V6 "promisor pack" probes are **void** — the fixture repos never received
the markers, only the fleet did — so no pack-marker claim is made here; (b)
`out/RowF06LazyFetch-2/probe2.sh` and `run-all.sh` must not be rerun as
archived; a corrected version must use `git rev-parse --absolute-git-dir` (or
`cd` into the fixture) and assert `git -C <dir> rev-parse --show-toplevel`
equals the fixture before any write. Every other probe wrote only under
`/tmp/f06-hand`; the F06, V0, V1-clean and V1-dirty arm evidence is unaffected.
I did not measure whether the markers affected any concurrent git operation in
the fleet root.

## 1. Premise and frozen arm — observed

Builder read at `tests/report-audit/repo-state-grid.py:271-286`: lane commit
`lc` (`round-1: work` @1000, author `kama-shokunin`); fleet report citing `lc`
and `abcdefabcdefabcdefabcdefabcdefabcdefabcd`; lane config
`extensions.partialClone=origin`, `remote.origin.url=ssh://example.invalid/x.git`,
`remote.origin.promisor=true`, `core.sshCommand="touch <marker>; false"`; premise
`git cat-file -e <fake2>` must create the marker (`:284`). Row and reason pin at
`:547` and `:581`.

I rebuilt it by hand in `/tmp/f06-hand/arch` (no import of the grid module; the
builder was read, not executed). Hand run, `bash out/RowF06LazyFetch-2/build.sh`:

```
lane lc=1a2718b68369eb0a2c43ddd6872728e987aa7019
premise cat-file rc=1 marker=present
premise stderr: fatal: Could not read from remote repository. …
ARM frozen exit=1 executed=yes traceback=no
  kinds: ['landed-unresolved', 'unresolved-full-hash']
ARM current exit=2 executed=no traceback=no
  stderr: could-not-evaluate: /tmp/f06-hand/arch/lane: partial clone (extensions.partialclone)
```

The premise is real: a missing-object read in this repo runs the configured
program. On the frozen arm the same marker is recreated **during the audit**
(`executed=yes`); no traceback, no timeout, and the verdict is a defect verdict.
Grid cross-check from the clean clone, current pinned:

```
$ python3 tests/report-audit/repo-state-grid.py --case F06-lazy-fetch-command \
    --current …/current-auditor-f228f174.py --json
GRID_EXIT=1
current exit=2 executed=False met=True violations=0
frozen  exit=1 executed=True  met=False violations=1
population_sha256 83a84702251c62c6990c8222ea6c4276e09db05344b3c2c0d862a857e50ea2f1
```

So the L1 claim "frozen runs the configured program / row NOT-MET; current
exit 2 without execution" holds for F06 exactly as stated.

## 2. Is exit 2 the correct expectation? — yes (observed counterfactuals)

The fixture's exact config makes git attempt a promisor fetch for **any**
missing object; it is not an artifact of the premise command only:

| repo config | `git cat-file -e <missing>` | program ran |
|---|---|---|
| `extensions.partialClone=origin` (F06, also promisor=true) | rc=1 | **yes** (`build.sh`) |
| `remote.origin.promisor=true` only, no extension (V2) | rc=1 | **yes** |
| `extensions.partialClone=origin` + `promisor=false` (V3) | rc=1 | **yes** (extension dominates) |

Git's partial-clone documentation states the lookup has no promisor-object
gate — the wave's gate row S092 (https://git-scm.com/docs/partial-clone, 2.56.0)
quotes: "For efficiency reasons, no check as to whether the missing object is
actually a promisor object is performed." (19 words). Therefore a lane-absent
cited hash is not evidence of absence: the object could exist on the configured
promisor remote, and the truthful verdict cannot be computed locally. Refusing
(exit 2, reason naming the partial clone) is the sound outcome and matches the
declared refusal design (`corpus/lessons/round-23.md:38-40, 76-78, 83-84`).
The frozen arm's exit 1 is only accidentally plausible (the remote is
unreachable in the fixture); it ran a repo-configured program to reach it.
An alternative sound design could evaluate with `--no-lazy-fetch` and mark
missing-token results unevaluable, but that is not this auditor's contract; for
the fixture as declared, exit 2 is correct and stronger than "don't execute".

## 3. Near variant current still gets wrong — yes: value-blind promisor config

Committed detection (`tools/report-landing-audit.py:445-448`) matches
`extensions.partialclone` or `remote\..+\.promisor` **by name only**; it never
reads the value. `remote.<name>.promisor` is a boolean; its own documentation
(git-config §remote.<name>.promisor, quoted in the wave's SrcGitConfig row:
"When set to true, this remote will be used to fetch promisor objects.")
means `false` disables promisor behavior.

Observed with git 2.56.0 (probe `out/RowF06LazyFetch-2/probe-variants.sh`):

```
V1: remote.origin.url=ssh://example.invalid/x.git, remote.origin.promisor=false,
    core.sshCommand=touch marker;false; git config --type=bool = false
    probe v1: rc=1 marker=absent          <-- git never lazy-fetches
V5: VOID — the `.promisor` markers this step wrote landed in the fleet repo's
    object store, not in the fixture (see contract breach above); the fixture
    itself had no markers, so this is not a pack-marker observation.
P1: extensions.partialClone="" (empty value), url set
    probe p1: rc=1 marker=absent          <-- no fetch; the name-only check at
                                              :446-448 still fires on this listing
```

V1 and V2 are the same repo shape, same missing hash and same URL; only the
`promisor` value differs (`false` vs `true`), and only the `true` case runs the
program — the fetch toggle is the value, not the object.

Auditor comparison on hand-built pairs (all runs pinned to committed blob):

* **v1-clean** — clean report citing the existing lane tip; lane carries
  `remote.origin.promisor=false`, the url, and the marker `sshCommand`:

  ```
  effective promisor bool: false
  premise missing-object probe: marker=absent
  ARM frozen exit=0 kinds=[] executed=no
  ARM current exit=2 executed=no
    stderr: could-not-evaluate: …/v1-clean/lane: partial clone (remote.origin.promisor)
  ```

  Frozen audits the repo and finds nothing; current refuses it. The key is
  inert for git, so this is an over-refusal, not a fault.

* **v1-dirty** — the grid's C02 shape (real omitted commit @900, report cites
  tip @1000) plus the same inert key:

  ```
  ARM frozen exit=1 kinds=['landed-omitted'] executed=no
  ARM current exit=2 executed=no
    stderr: could-not-evaluate: …/v1-dirty/lane: partial clone (remote.origin.promisor)
  ```

* **v0-control** — byte-identical fixture minus the promisor/url keys: both
  arms `exit=1 kinds=['landed-omitted']`. The single `promisor=false` key is
  what changes current's verdict.

This is a verdict flip caused solely by repository-local git state, on a repo
git does not consider partial: current converts a true `landed-omitted` defect
(and a clean 0) into `could-not-evaluate`. It is outside T01's declared
partial-clone tradeoff (no partial clone exists: no promisor pack, no
extension, no fetch) and is introduced by the round — frozen gets both cases
right without executing anything. `extensions.partialClone=""` (P1) is a
second, weaker instance of the same name-vs-value blindness (git does not
fetch; the empty value is malformed rather than meaningfully partial).

I did not find a false **negative** on this channel: `include.path` promisor
config appears in the same `git config --list --name-only` output the detector
reads (H1: `remote.origin.promisor` in the listing, `marker=PRESENT`); a remote
named with a literal `\n` escape is matched by the
regex and does fetch (E3: `detected-by-regex: YES`, `marker=PRESENT`); a
valueless `promisor` key means true and fetches (P2); a real quoted newline in
a subsection is rejected by git config itself (E2: `fatal: bad config line 7`).
No execution was observed in current under any fixture; `--no-lazy-fetch`
(`:93`) keeps that guarantee even when detection misses.

[INFERENCE] Repair direction for L1 (not implemented or tested): parse the
listing with values (`git config --null --list`, splitting key and value) and
apply git's boolean spelling to `remote.<name>.promisor`; keep the
`extensions.partialclone` and promisor-pack checks as they are (F23 declares
the pack refusal). The lane working-tree edit seen at 12:55 already contains
such a `git_bool()` helper plus a `.pack`-sibling condition on the pack check;
I did not review or integrate it.

## 4. What current gets right on this channel (observed)

- Exact F06: exit 2 `partial clone (extensions.partialclone)`, no execution,
  no traceback, reason pinned; grid row met.
- Repos where git really fetches match the name check: V2
  (`remote.origin.promisor`) and V3 (extension plus the key) both
  `marker=PRESENT`, and both names appear in the listing the check scans.
- Promisor config pulled in through `include.path` is visible in the same
  listing (H1: `remote.origin.promisor` listed, `marker=PRESENT`).
- Promisor-pack branch: the committed check refuses any `.promisor` entry in
  `objects/pack` (`:443-444`); F23 declares that refusal. I make no empirical
  pack-marker claim: the V5/V6 git-level probes were voided by the contract
  breach above, and I did not run the auditor on such a repo.
- I did not run the auditor on the V2/V3/H1 probe repos (no fleet pair), so
  their refusal is inferred from the scanned listing, not observed from an
  arm run; the exact F06 and V1 pairs above were run on both arms.

## 5. Not verified

- Whole-grid counts other than F06, the 22/24 mutant claim, selftest 50/50,
  rounds 10-22 ledger byte-identity, S089-S095/lesson text: outside this slice.
  Only F06 plus the hand variants above were run.
- git versions other than 2.56.0 (declared floor >=2.45); the boolean parsing
  of `remote.<name>.promisor` and the no-fetch observations are empirical for
  2.56.0 only.
- No network was contacted: `example.invalid` with `core.sshCommand` override
  only; no real promisor remote was reachable.
- Promisor-pack git behavior was not successfully tested: V5/V6 are void (the
  markers were written to the fleet root, then removed; see the contract
  breach), so no claim is made about `.promisor` markers without configuration.
- The proposed repair was not implemented or tested. The dirty lane files were
  read only to explain why an intermediate re-run changed results; they are not
  used as evidence.
- Adjacent, unclaimed and outside this channel: a repo-local `include.path`
  FIFO blocks every git command in both arms (`rev-parse --show-object-format`
  rc=124 under `timeout 5`), so it is not a round-23 regression.
- An intermediate archive attempt hit `No space left on device` on the shared
  `/tmp` (100% full at 12:55); every quoted output is from the rerun after
  space was freed, captured in `run.log`.

## 6. Files written

- `.ufo/waves/round-23/falsify/advice/RowF06LazyFetch.md` (this report)
- `.ufo/waves/round-23/falsify/out/RowF06LazyFetch-2/`: `build.sh`,
  `v0-control.sh`, `v1-clean.sh`, `v1-dirty.sh`, `probe-variants.sh`,
  `probe2.sh`, `probe3.sh`, `probe4.sh`, `detect.py`, `grid-run.sh`,
  `run-all.sh`, `run.log`, `current-auditor-f228f174.py`,
  `frozen-audit-4fe9339.py`, `grid-f06-F06-case.json`
- Scratch outside the lane: `/tmp/f06-hand` (regenerated by `run-all.sh`),
  `/tmp/frozen-r23-f06.py`, clone `/tmp/kama-r23w2/RowF06LazyFetch-2`
- **Contract-breach writes into the fleet root (removed by the L1):**
  `/home/vgpnk/Projects/shokunin/.git/objects/pack/` —
  `pack-22727cb1bcc67a7ba804c7e9ed3fb5d0dec3812d.promisor`,
  `pack-3cd47c8a034bb088d889f993bfd2eaa569f73acd.promisor`,
  `pack-e193a79004e5d3868405113951a811b60b47b59a.promisor`,
  `pack-deadbeef.promisor` (zero-byte markers, created 12:50:16 and 12:58:00
  -0300 by `probe2.sh`'s relative `.git/objects/pack`; verified absent at 13:00
  after the L1 removed them). I did not touch them after being told.

**Do not run `probe2.sh` or `run-all.sh` as archived** — the V5/V6 steps repeat
the relative-path write into whatever repo is the process cwd. Fix them to use
`git rev-parse --absolute-git-dir` and a `--show-toplevel` assertion first.

Except for the fleet-root markers disclosed above, no tracked lane file, lane
index, `.jj`, sibling lane, global config or `~/.omp` was written; no commits,
pushes or jj commands; no installs.
