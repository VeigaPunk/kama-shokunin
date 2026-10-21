# Row F10-shallow-lane — independent falsification

Verdict: **partially**.

- The row's premise is real and reproduces by hand: a regular-file shallow
  lane hides a genuine round-1 omission, frozen exits 0 clean, current exits
  2 with `shallow repository`. As written, F10 is met by current.
- The expected outcome (exit 2, not a verdict) is the **correct** one: a real
  `--depth 1` clone both hides omissions and makes legitimate older citations
  unresolvable, so no verdict is sound there (demonstrated below).
- However the shallow/hidden-history channel is **not closed**. Two near
  variants of the same repository-local channel still defeat current:
  1. **FIFO at `.git/shallow` hangs the auditor indefinitely** — exit 124
     under an external `timeout`; the auditor has no internal timeout. This
     is the exact "must not ... hang" clause and the check itself is the
     first opener of the file.
  2. **A tampered commit-graph** (HEAD's CDAT parent slots cleared, trailing
     SHA-1 recomputed) flips current to **exit 0 clean** on the same omitted
     commit — identical outcome to the frozen shallow failure, while every
     commit object stays intact and hash-correct. `git commit-graph verify`
     detects the corruption; the auditor never runs it and does not disable
     the graph.

Neither variant is in the declared open list (O01 alternates, O02 gitfile,
ambiguity overwrite, second Landed section, errata CR, sibling tools).

## Method and identities

- Clone: `git clone --no-hardlinks ... /tmp/kama-r23w2/RowF10ShallowLane`;
  `git -C ... rev-parse HEAD` = `245a37f69628c2c6bb29bbf17897d8fb5946c857`.
- Auditors: frozen blob `4fe9339f8fc3a4a4a479d9c938a850da12f1124d:
  tools/report-landing-audit.py` (sha256 `09ecd63bdc3a5be5264e6d2966602a32
  e52ca0678dc89de99959318245ab3b3f`); current blob `f10d811eafcc5bc853abdf75
  c4a05ec2374cd579` (sha256 `f228f17420134a4a4fb6d1f93b943f78647e7e60882f76
  e6cb7cba11d6928a7`).
- Environment: git 2.56.0, Python 3.14.8, every run under
  `env -i PATH=/usr/bin:/bin HOME=/tmp GIT_CONFIG_GLOBAL=/dev/null
  GIT_CONFIG_NOSYSTEM=1`; fresh repos only under `/tmp/kama-r23w2/`.
- Fixture built by hand from the semantic description (no import of
  `repo-state-grid.py`): lane commits `4c2a2a5` (author `kama-shokunin`,
  author time 900, subject `round-1: omitted`) then `1c42004` (time 1000,
  `round-1: work`); fleet adds `.ufo/reports/round-1/kama.md` at 2000 citing
  only `1c42004...`. (Fleet author is irrelevant: `report_cutoff` reads only
  `%at` at `tools/report-landing-audit.py:203-206`.)
- Builder: `/tmp/kama-r23w2/build-f10.sh`.

Grid referents at 245a37f6:
- `tests/report-audit/repo-state-grid.py:348-352` — `f_shallow` writes the
  cited tip into `.git/shallow` and requires `rev-list --count HEAD == 1`.
- `tests/report-audit/repo-state-grid.py:551` — row
  `("F10-shallow-lane", "fault", f_shallow, 2, None)`.
- `tests/report-audit/repo-state-grid.py:582` — reason pin
  `"F10-shallow-lane": "shallow repository"`.
- `tools/report-landing-audit.py:426-448` — `check_history_repo`; shallow
  probe at `:436-437`; called for both repos at `:475-476`.
- `tools/report-landing-audit.py:93-96` — `GIT_ISOLATION` (no
  `core.commitGraph`, no timeout); `:180-183` — `round_commits` uses
  `git log`; `:108-116` — `git()` runs `subprocess.run` with **no timeout**.

## Q1 — Is the premise real and observed in the frozen arm?

Yes, both directions reproduced.

Control (same fixture, **no** shallow file), proving the omission is genuine:

```
$ python3 frozen-audit.py  --lane-repo .../deep/lane --fleet-repo .../deep/fleet --json --rounds 1 --no-errata
exit 1   status failed   by_kind {landed-omitted: 1}
$ python3 current-audit.py <same>
exit 1   status failed   by_kind {landed-omitted: 1}
```

Fault (`.git/shallow` = cited tip `1c42004...`):

```
$ git -C .../shallow/lane rev-list --count HEAD      -> 1
$ git -C .../shallow/lane rev-parse --is-shallow-repository -> true
$ python3 frozen-audit.py ...   -> exit 0   status clean   defects 0
$ python3 current-audit.py ...  -> exit 2
  stderr: could-not-evaluate: /tmp/kama-r23w2/f10/shallow/lane: shallow repository
```

No traceback, no timeout, no executed side effect (the fixture configures no
program; there is nothing to run in F10). The frozen arm does exactly what
the grid reports: a silent clean pass on a report that omits a real round-1
commit. The fixture premise check (`rev-list --count HEAD == 1`) also holds.

## Q2 — Is the expected outcome the correct one?

Yes. Exit 2 is "could-not-evaluate" by contract
(`tools/report-landing-audit.py:43-46`), and the refusal happens before any
report is read (`:475-476` runs before `audit_round`). The alternative is not
merely risky, it is demonstrably wrong in a real shallow clone: a genuine
`git clone --depth 1 file://...` lane hides the pre-boundary commit **and
drops its object**, so a report that legitimately cites it cannot be audited:

```
$ git -C .../real-shallow/lane rev-list --count HEAD        -> 1
$ git -C .../real-shallow/lane cat-file -t <older commit>   -> fatal: could not get object info
$ frozen ... -> exit 1  kinds {landed-unresolved, unresolved-full-hash}
$ current ... -> exit 2  "shallow repository"
```

So a shallow repo can produce either a false clean (synthetic shallow, above)
or a false defect (real shallow); exit 2 is the only sound outcome. The
message matches the grid's `REASONS` pin.

Precision notes (both fail closed, neither flips a verdict):
- A **0-byte** `.git/shallow` yields `--is-shallow-repository` = `true`
  while `rev-list --count HEAD` = 2 (history fully visible); current refuses
  with exit 2. Over-broad refusal, but safe direction.
- A newline-only `.git/shallow` makes `git rev-parse --is-shallow-repository`
  fail `rc=128 fatal: bad shallow line`, which becomes an `EvalError`
  (exit 2, no traceback) — still fail-closed; the pinned phrase is not what
  the user sees.

## Q3 — Near variants of the same channel that current still gets wrong

### V-A (hang) FIFO at `.git/shallow`

```
$ ls -l .../fifo/lane/.git/shallow
prw-r--r-- 1 vgpnk vgpnk 0 ... .git/shallow
$ timeout 3 git -C .../fifo/lane rev-parse --show-object-format   -> exit 0
$ timeout 3 git -C .../fifo/lane rev-parse --show-prefix          -> exit 0
$ timeout 3 git -C .../fifo/lane rev-parse --is-shallow-repository -> exit 124
$ timeout 10 python3 current-audit.py --lane-repo .../fifo/lane --fleet-repo .../fifo/fleet ...
  -> exit 124, stdout 0 bytes, stderr 0 bytes
```

`git rev-parse --is-shallow-repository` opens `.git/shallow` and blocks on
the FIFO; `check_history_repo` (`:436-437`) therefore hangs before any
refusal can be raised, and `git log` would block later anyway. The auditor
has no internal timeout (`:108-116`), so without an external `timeout` this
blocks forever; under the grid's `TIMEOUT = 30` it would be `timed_out` and
the row NOT met. The frozen arm hangs identically (exit 124 under
`timeout 5`).

Contrast: a FIFO at `.git/info/grafts` is refused without opening it
(`os.path.lexists` at `:440-441`): exit 2, `... info/grafts rewrites
history`. The shallow probe could use the same lstat-first shape
(`git rev-parse --git-path shallow` returns `.git/shallow` without opening
the file in this repo; observed exit 0) and refuse non-regular shallow
paths.

### V-B (flip) Tampered commit-graph

Fixture: copy of the deep control plus `git commit-graph write --reachable`
(single v1 graph, `objects/info/commit-graph`, read-only). Tamper script
`/tmp/kama-r23w2/tamper-cg.py` locates HEAD's graph position via
OIDF/OIDL, rewrites its two CDAT parent slots to `0x70000000`
(`GRAPH_PARENT_NONE`), and recomputes the trailing SHA-1 so the file is
internally consistent.

```
$ git -C .../cg/lane cat-file commit HEAD | head -2
tree a33984f...
parent 4c2a2a5b90755f0639480d692d850b1d1fa81318      # object still says parent
$ git -C .../cg/lane log --format='%H %s'
1c42004b... round-1: work                            # older commit hidden
$ git -C .../cg/lane rev-list --count HEAD            -> 1
$ git -C .../cg/lane -c core.commitGraph=false log --format='%H %s'
1c42004b... round-1: work
4c2a2a5b... round-1: omitted                         # mechanism confirmed
$ git -C .../cg/lane commit-graph verify
commit-graph parent list for commit 1c42004b9f5dd3e1ac04438e59c9f437579eeb4d terminates early
$ git -C .../cg/lane fsck --no-progress ; echo $?     -> 16 (same message)
```

Auditor results, isolating the graph as the cause:

```
clean graph regenerated (git commit-graph write --reachable):
  frozen  exit 1  failed  {landed-omitted: 1}
  current exit 1  failed  {landed-omitted: 1}
tampered graph:
  frozen  exit 0  clean   defects 0   (expected: frozen is unprotected)
  current exit 0  clean   defects 0   round_commits = 1
```

This is precisely the F10 outcome (visible history != object history) via a
different repository-local file, and current's refusal set (shallow, grafts,
promisor, object format at `:426-448`) does not cover it. `GIT_ISOLATION`
(`:93-96`) does not pass `-c core.commitGraph=false`, and `round_commits`
(`:180-183`) trusts `git log`. Detection is cheap (`commit-graph verify`):
it reports "parent list ... terminates early" while the commit object still
carries the parent.

## Other probes (all safe / refused)

- Shallow in a linked worktree (shallow file in the common git dir):
  `is-shallow=true`, count=1, current exit 2 `shallow repository`.
- Shallow in a bare lane repo: current exit 2.
- Shallow in the **fleet** repo (`:475-476` covers both): exit 2 naming the
  fleet path.
- Shallow entry naming an unreachable dangling commit: `is-shallow=true`,
  current exit 2.
- Empty 0-byte shallow: exit 2 (over-refusal, see Q2).
- Newline-only shallow: git rc=128 -> `EvalError` exit 2, no traceback.

## What I did NOT verify

- Did not run `repo-state-grid.py` itself; the 26/26, 8/8, selftest 50/50
  and ledger claims were taken as given. F10 was rebuilt by hand only.
- Did not test split commit-graph chains
  (`objects/info/commit-graphs/commit-graph-chain`) or multi-level graphs;
  one single-file v1 graph only.
- Did not test whether adding `-c core.commitGraph=false` to `GIT_ISOLATION`
  closes every traversal (`log`, `rev-list`, `--contains`, etc.).
- Did not test FIFO at `.git/config` or other git-opened repository files;
  only `.git/shallow` and the `.git/info/grafts` contrast.
- Did not verify behavior under other git versions (2.56.0 only); the
  declared floor is 2.45.
- Did not test the frozen arm on the FIFO beyond confirming it also hangs
  (exit 124 under `timeout 5`).
- No installs or upgrades were made (no pacman/uv/npm); nothing to record.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/falsify/advice/RowF10ShallowLane.md` (this report)
- `/tmp/kama-r23w2/RowF10ShallowLane/` (scratch clone)
- `/tmp/kama-r23w2/frozen-audit.py`
- `/tmp/kama-r23w2/build-f10.sh`
- `/tmp/kama-r23w2/variants.sh`
- `/tmp/kama-r23w2/tamper-cg.py`
- fixtures and captured outputs under `/tmp/kama-r23w2/`
  (`f10/`, `cg/`, `cgclean/`, `fifo/`, `grafts-fifo/`, `v2b/`, `v5/`,
  `real-shallow/`, `variants/`, `out-*`).

## Lane working-tree observation (end of session, not mine)

`git -C /home/vgpnk/Projects/shokunin/kama-shokunin status --porcelain` at
session end shows uncommitted modifications to
`tools/report-landing-audit.py` (worktree sha256 `3fc567ab...`, committed blob
`f10d811e...` sha256 `f228f174...`) and
`tests/report-audit/repo-state-grid.py` (worktree sha256 `3ccd9752...`,
committed blob sha256 `72c1e530...`), plus `corpus/README.md` and
`corpus/knowledge/error-is-not-a-verdict.md`. I did not write these; HEAD
remains `245a37f6...` and my clone was taken before they appeared. All
evidence above is pinned to the committed blobs at `245a37f6...`; the frozen
arm and the current arm were executed from those blobs only.
