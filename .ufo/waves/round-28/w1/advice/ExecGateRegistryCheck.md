# ExecGateRegistryCheck — round-28 W1 repair (round-27 routed defect 3)

Status: implemented and measured. The check fails on the lane's real state at
the claim base (`exit 1`, two counters unnamed) and passes on a scratch clone
whose SKILL.md names both (`exit 0`). The pass condition is reachable and the
fail condition is the lane's own defect, not a synthetic one.

No lane file was edited by this seat: its writes are the untracked
`.ufo/waves/round-28/w1/` tree and the `/fast` scratch clone. A concurrent
round-28 seat modified `.ufo/waves/round-28/count-c1.py` at 05:37:36
(`git diff`: +39/−5, amendment A1 text); this seat did not touch it and the
change does not alter either query (population path and SKILL.md text), as the
post-change run in §7 shows. `SKILL.md` at the working tree and at tip
`5ebe7b1b` is sha256 `6127e49f1c7c38a05c5154c5e3f926c99ad7d6fe3ccb6c30d58b0aefa0fa7747`.
Shell git env carries only `GIT_EDITOR`/`GIT_PAGER`/`GIT_TERMINAL_PROMPT`;
`GIT_DIR`, `GIT_WORK_TREE` and `GIT_INDEX_FILE` were unset on every scratch
clone/checkout/commit command. No installs (tool, version, channel: none). No
server was started, so no port was bound.

## Deliverable

- Proposed tool: `.ufo/waves/round-28/w1/out/ExecGateRegistryCheck/gate-registry-check.py`
  (sha256 `28500af9024aaa328d65cf715b5dd031cd53f065976f85d0fb133296a9aead4e`,
  executable). The L1 moves it to `tools/gate-registry-check.py`.
- Contract: `--rev <git revision>` (default: working tree) evaluates the tree
  **and** `SKILL.md` at that revision. Population: every tracked path matching
  `^\.ufo/waves/round-[^/]+/count-[^/]+\.py$`. A path is `registered` iff its
  repo-relative text occurs verbatim in SKILL.md. Each missing path prints
  `unregistered <path>` (sorted); the last line is `registered R unregistered U`.
  Exit 0 iff `U == 0`, exit 1 otherwise, exit 2 when the tree, revision or
  SKILL.md cannot be read. Read-only: `git rev-parse --show-toplevel` (to
  resolve `--repo`/cwd), `git ls-tree` (with `--rev`), `git ls-files` (working
  tree), `git show` (`<rev>:SKILL.md`). Nothing is written, staged or checked out.
- Exact runnable commands: `commands.sh` beside the tool. Artifact checksums:
  `evidence.sha256`. Integration row: `proposed-skill-row.md`.

## Falsifier runs (exact commands, exact output)

1. Base run — expected fail, and it fails:

```
$ timeout 60 /usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/w1/out/ExecGateRegistryCheck/gate-registry-check.py \
      --repo /home/vgpnk/Projects/shokunin/kama-shokunin \
      --rev 4179301f7516ad667509d54b5ebfe0a70a002d5b
unregistered .ufo/waves/round-25/count-c2.py
unregistered .ufo/waves/round-27/count-c1.py
registered 2 unregistered 2
$ echo $?
1
```
   stderr empty (`base-4179301.{out,err,exit}`). The round-27 counter — the
   routed defect — is found, and so is the round-25 counter.

   Population at that revision (4 tracked counters): `round-17/count-verdicts.py`
   (registered, prose mention at SKILL.md:582), `round-25/count-c2.py`
   (unregistered), `round-26/count-c1.py` (registered, SKILL.md:1073),
   `round-27/count-c1.py` (unregistered).

2. Scratch clone — expected pass, and it passes. Clone of the lane at
   `/fast/scratch/hyaku/kama-r28/w1/ExecGateRegistryCheck/clone`, checked out at
   `4179301f`, `git env unset`, then this block appended to the clone's
   `SKILL.md` (nothing else changed):

```
## Round-28 scratch registration mentions (clone-only; not lane content)

- `.ufo/waves/round-25/count-c2.py` -- round-25 C2 counter; scratch registration
  mention for the round-28 `tools/gate-registry-check.py` self-demonstration.
- `.ufo/waves/round-27/count-c1.py` -- round-27 C1 counter; scratch registration
  mention for the round-28 `tools/gate-registry-check.py` self-demonstration.

This clone is scratch evidence only. The section adds no gate row, verdict map,
command or pinned value, and it is never pushed to the lane.
```

   committed as `18f62f891f0548f9430172d12231010d4d434143` (`git -c user.name=…
   -c user.email=… commit`, hardlinks off, `GIT_DIR`/`GIT_WORK_TREE`/`GIT_INDEX_FILE`
   unset), then:

```
$ cd /fast/scratch/hyaku/kama-r28/w1/ExecGateRegistryCheck/clone
$ timeout 60 /usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/w1/out/ExecGateRegistryCheck/gate-registry-check.py
registered 4 unregistered 0
$ echo $?
0
$ timeout 60 /usr/bin/python3 .../gate-registry-check.py --rev HEAD
registered 4 unregistered 0
$ echo $?
0
```
   (`scratch-worktree.{out,err,exit}`, `scratch-rev-HEAD.{out,err,exit}`,
   `scratch-commit.txt`.)

3. Revision-only delta inside the same clone — the verdict is caused by the
   SKILL.md text, not by the copy of the tool or the repo:

```
$ timeout 60 /usr/bin/python3 .../gate-registry-check.py --rev 4179301f7516ad667509d54b5ebfe0a70a002d5b
unregistered .ufo/waves/round-25/count-c2.py
unregistered .ufo/waves/round-27/count-c1.py
registered 2 unregistered 2
$ echo $?
1
```
   (`scratch-rev-base.{out,exit}`.)

4. `exit 2` paths, both measured:

```
$ ... --repo /home/vgpnk/Projects/shokunin/kama-shokunin --rev 0000000000000000000000000000000000000000
ERROR could not evaluate: git ls-tree 0000000000000000000000000000000000000000 failed: fatal: not a tree object
$ echo $?   # 2

$ ... --repo /fast/scratch/hyaku/kama-r28/w1/ExecGateRegistryCheck/notgit
ERROR could not evaluate: not a git working tree at '.../notgit': fatal: not a git repository
$ echo $?   # 2
```
   (`bad-rev.{out,err,exit}`, `notgit.{out,err,exit}`.)

5. Population semantics, measured: an untracked
   `.ufo/waves/round-99/count-x.py` placed in the clone is not listed
   (`registered 4 unregistered 0`, exit 0; `scratch-untracked.{out,exit}`), and
   the default `--repo .` from `clone/tools` still resolves the root
   (`registered 4 unregistered 0`, exit 0; `scratch-subdir.{out,exit}`).

6. Current lane tip, measured: `--rev 5ebe7b1b2defa4d8109de8fcc9b28f13dd6fb5f6`
   exits 1 with three paths — `.ufo/waves/round-25/count-c2.py`,
   `.ufo/waves/round-27/count-c1.py`, `.ufo/waves/round-28/count-c1.py`
   (`registered 2 unregistered 3`; `lane-HEAD-5ebe7b1.{out,exit}`). The
   working-tree run is identical (`worktree-head.{out,err,exit}`).

7. After the concurrent counter edit (05:37:36), the working-tree run was
   repeated and is unchanged: `unregistered .ufo/waves/round-25/count-c2.py`,
   `unregistered .ufo/waves/round-27/count-c1.py`,
   `unregistered .ufo/waves/round-28/count-c1.py`,
   `registered 2 unregistered 3`, exit 1
   (`worktree-head-after-sibling.{out,exit}`).

## Boundary of the verdict (read this before grading with it)

- The check is an **occurrence** test, as specified, not a row-shape test.
  `round-17/count-verdicts.py` passes only because its path appears in a prose
  paragraph (SKILL.md:582, "Wave artifacts … are process tools, not axis
  evidence"), not because it has a registry row. A row's entry command, verdict
  map, self-test and pinned values are not inspected. The round-27 routed defect
  asks for such a row; this tool can prove only absent/present.
- Working-tree mode uses the index, so a counter that is committed elsewhere but
  present in the index counts, and an untracked counter does not (measured).
  `--rev` uses the committed tree, so the two modes disagree exactly on
  index-only files.
- It does not report the inverse defect (SKILL.md names a counter path that no
  longer exists). That is outside the assigned contract and remains open.
- Git surface, stated against the "read-only git only (`git show`, `git ls-tree`)"
  constraint: those two carry the evaluation, and the tool adds exactly two other
  read-only plumbing calls — `git ls-files` for the working-tree population
  (`ls-tree` cannot see index-only entries) and `git rev-parse --show-toplevel`
  to resolve `--repo`/cwd to the root that owns SKILL.md. No git command writes;
  the scratch commits happened only in the `/fast` clone.
- At the round-28 landed tip the check will still exit 1 because
  `.ufo/waves/round-28/count-c1.py` is tracked at tip `5ebe7b1b` and the C1
  predicate adds a request-field outcomes section, not a row for that counter.
  Integration must decide: register the round-28 counter too (recommended; one
  row, same as the round-27 repair), or run the gate as `--rev` pinned to an
  older revision, which weakens it.

## Integration text

`proposed-skill-row.md` holds a 5-cell row matching the "## Local gate/probe
registry" header, plus notes. Source-read interface of the round-27 counter for
its own row (not executed by this seat; read at
`.ufo/waves/round-27/count-c1.py:601-603,720-745`): entry
`python3 .ufo/waves/round-27/count-c1.py --out <receipt.json>` (`--lane`,
`--repo` optional), exit 0 after a completed evaluation even when `met False`
(the count is on stdout and in the receipt), exit 2 on `could-not-evaluate`;
no exit 1.

## Retained evidence (all under `.ufo/waves/round-28/w1/out/ExecGateRegistryCheck/`)

`gate-registry-check.py`, `commands.sh`, `proposed-skill-row.md`,
`base-4179301.{out,err,exit}`, `worktree-head.{out,err,exit}`,
`lane-HEAD-5ebe7b1.{out,exit}`, `bad-rev.{out,err,exit}`,
`notgit.{out,err,exit}`, `scratch-worktree.{out,err,exit}`,
`scratch-rev-HEAD.{out,err,exit}`, `scratch-rev-base.{out,exit}`,
`scratch-untracked.{out,exit}`, `scratch-subdir.{out,exit}`,
`scratch-commit.txt`, `evidence.sha256`. Scratch: clone at
`/fast/scratch/hyaku/kama-r28/w1/ExecGateRegistryCheck/clone` (commit
`18f62f89`; 252 MB; kept as the passing fixture).
