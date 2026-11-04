# LAB01Probes — four falsifiable git-state probes (kama r72 w1)

Read-only over the lane. Every fixture lives under scratch and was deleted after this receipt was
copied into the wave dir; no lane byte was touched.

- Host: Linux 7.2.11-arch1-1 x86_64, `git version 2.56.0`, `Python 3.14.8`, 2026-11-03.
- Scratch root: `S=/fast/scratch/hyaku/kama-r72/LAB01Probes`, fixtures under `F=$S/fixtures`.
- Every fixture repo was created with `git init -q -b main "$D"`; before its first commit
  `git -C "$D" rev-parse --show-toplevel` was asserted equal to `$D` (harness printed
  `toplevel=<D> expected=<D> OK`), and every commit used a throwaway identity:
  `git -C "$D" -c user.name=fixture -c user.email=fixture@invalid commit -q -m <msg>`.
- No mutating git command ran outside `$F`. No lane file was written. No tool was installed; the
  installed `git 2.56.0` and `python3 3.14.8` sufficed, so the tooling directive recorded nothing.
- Relation to the freeze: these are measurements, not rule changes. H2 is the empirical half of
  C1's stated motivating evidence (the round-71 vacuous green); H1/H3/H4 bound what a passing
  counter may rely on. No edit to `plans/round-72-claims.md` is proposed.
- Rendering: porcelain output is shown through `python3` `repr()` of each line and through
  `od -An -tx1`, so trailing spaces and record prefixes are visible rather than inferred.

## H1 — plain `git status --porcelain -uall` never lists a git-ignored file under `.ufo/waves/<round>`; `--ignored` does

**Verdict: CONFIRMED**, with one scope caveat (tracked paths, below).

### Fixture

```sh
D1=$F/h1
git init -q -b main "$D1"
printf '.ufo/state/\n.ufo/waves/round-72/*.secret\n.ufo/waves/round-72/cache/\n' > "$D1/.gitignore"
mkdir -p "$D1/.ufo/state" "$D1/.ufo/waves/round-72/cache"
printf 'state\n'  > "$D1/.ufo/state/session.bin"
printf 'secret\n' > "$D1/.ufo/waves/round-72/leak.secret"
printf 'cached\n' > "$D1/.ufo/waves/round-72/cache/artifact.bin"
printf 'visible\n' > "$D1/.ufo/waves/round-72/visible.txt"
git -C "$D1" add .gitignore
git -C "$D1" -c user.name=fixture -c user.email=fixture@invalid commit -q -m base
```

### Commands and observed output

```text
$ git -C "$D1" status --porcelain -uall -- .ufo/waves/round-72
records=1 exit=0
'?? .ufo/waves/round-72/visible.txt'
```

```text
$ git -C "$D1" status --porcelain -uall --ignored -- .ufo/waves/round-72
records=3 exit=0
'?? .ufo/waves/round-72/visible.txt'
'!! .ufo/waves/round-72/cache/artifact.bin'
'!! .ufo/waves/round-72/leak.secret'
```

```text
$ git -C "$D1" status --porcelain -uall --ignored=matching -- .ufo/waves/round-72
records=3 exit=0
'?? .ufo/waves/round-72/visible.txt'
'!! .ufo/waves/round-72/cache/'
'!! .ufo/waves/round-72/leak.secret'
```

```text
$ git -C "$D1" status --porcelain -uall            # whole repo, no --ignored
records=1 exit=0
'?? .ufo/waves/round-72/visible.txt'

$ git -C "$D1" status --porcelain -uall --ignored  # whole repo
records=4 exit=0
'?? .ufo/waves/round-72/visible.txt'
'!! .ufo/state/session.bin'
'!! .ufo/waves/round-72/cache/artifact.bin'
'!! .ufo/waves/round-72/leak.secret'
```

```text
$ git -C "$D1" check-ignore -v -- .ufo/waves/round-72/leak.secret .ufo/waves/round-72/cache/artifact.bin .ufo/waves/round-72/visible.txt
.gitignore:2:.ufo/waves/round-72/*.secret	.ufo/waves/round-72/leak.secret
.gitignore:3:.ufo/waves/round-72/cache/	.ufo/waves/round-72/cache/artifact.bin
exit=0
```

### Calibration

- The plain command returned one record and never names `leak.secret` or `cache/artifact.bin`;
  the same paths appear as `!!` records only when `--ignored` is added. The base arm's blindness
  is confirmed exactly as C1's motivating evidence claims.
- `--ignored=matching` reports the ignored *directory* (`!! .../cache/`) where `--ignored` with
  `-uall` expands to the file (`!! .../cache/artifact.bin`). Both are non-empty, so either
  satisfies an "ignored path exists" check, but the finding detail is flag-dependent.
- `check-ignore -v` names the matching `.gitignore` line per path, exits 0 when at least one path
  is ignored, and prints nothing for the non-ignored `visible.txt`.

**Scope caveat:** the blindness is about *untracked* ignored paths. A tracked path that matches an
ignore pattern is still listed when modified, and `check-ignore` does not treat it as ignored
(S1-a). "Is git-ignored" therefore cannot be decided by `check-ignore` alone for tracked paths,
and plain status is not blind to tracked dirt.

**What would have refuted it:** a `!!` record from the plain command, or an ignored path absent
from `--ignored`. Neither was observed.

## H2 — a `--round` label pointing at a nonexistent wave dir yields zero records even when the repo carries uncommitted round work elsewhere

**Verdict: CONFIRMED.**

### Fixture

```sh
D2=$F/h2
git init -q -b main "$D2"
mkdir -p "$D2/.ufo/waves/round-71" "$D2/plans"
printf 'base\n' > "$D2/README.md"
printf 'frozen plan\n' > "$D2/plans/round-72-claims.md"
printf 'old round\n' > "$D2/.ufo/waves/round-71/notes.md"
git -C "$D2" add -A
git -C "$D2" -c user.name=fixture -c user.email=fixture@invalid commit -q -m base
printf 'dirty root\n' >> "$D2/README.md"
printf 'dirty plan\n' >> "$D2/plans/round-72-claims.md"
mkdir -p "$D2/.ufo/waves/round-72"
printf 'new round work\n' > "$D2/.ufo/waves/round-72/notes.md"
```

### Commands and observed output

```text
$ git -C "$D2" status --porcelain -uall -- .ufo/waves/round-999    # nonexistent label
records=0 exit=0
''

$ git -C "$D2" status --porcelain -uall -- .ufo/waves/round-72     # correct label
records=1 exit=0
'?? .ufo/waves/round-72/notes.md'

$ git -C "$D2" status --porcelain -uall -- .ufo/waves/round-71     # existing but quiet label
records=0 exit=0
''

$ git -C "$D2" status --porcelain -uall                            # whole repo
records=3 exit=0
' M README.md'
' M plans/round-72-claims.md'
'?? .ufo/waves/round-72/notes.md'
```

Arm-5 logic replicated verbatim from `tools/pre-report-gate.py:209-221`
(`records = [ln for ln in text.splitlines() if ln.strip()]`,
`uncommitted = len(records) if code == 0 else 0`, `ok = code == 0 and uncommitted == 0`):

```text
round=999 exit=0 uncommitted=0 ok=True detail='files=0'
round=72 exit=0 uncommitted=1 ok=False detail='files=1 first=?? .ufo/waves/round-72/notes.md'
round=71 exit=0 uncommitted=0 ok=True detail='files=0'
```

### Calibration

- The wrong label produces the same green as a genuinely clean round: exit 0, zero records,
  `files=0`, `ok=True`. Nothing in the record distinguishes "wave dir does not exist" from
  "wave dir clean".
- The scoped pathspec also hides the other uncommitted work: the repo carried three records
  (root `README.md`, `plans/round-72-claims.md`, the round-72 wave file) and only the last is
  reachable from the round-72 pathspec. A clean round dir therefore suppresses evidence of
  stray work elsewhere.
- An existing-but-quiet dir (`round-71`) is equally vacuous, so the failure is not specific to
  nonexistent paths: any label that names a quiet directory passes.

**What would have refuted it:** a nonzero exit code, or any record emitted for the nonexistent
path. Neither was observed.

## H3 — `git merge-base --is-ancestor` exits 1 for a non-ancestor pair and 0 for an ancestor pair

**Verdict: CONFIRMED**, with a third class that a gate must not fold into either: exit 128.

### Fixture

```sh
D3=$F/h3
git init -q -b main "$D3"
printf 'a\n' > "$D3/a.txt"; git -C "$D3" add -A
git -C "$D3" -c user.name=fixture -c user.email=fixture@invalid commit -q -m A; A=$(git -C "$D3" rev-parse HEAD)
printf 'b\n' > "$D3/b.txt"; git -C "$D3" add -A
git -C "$D3" -c user.name=fixture -c user.email=fixture@invalid commit -q -m B; B=$(git -C "$D3" rev-parse HEAD)
printf 'c\n' > "$D3/c.txt"; git -C "$D3" add -A
git -C "$D3" -c user.name=fixture -c user.email=fixture@invalid commit -q -m C; C=$(git -C "$D3" rev-parse HEAD)
# sibling commit that shares A but is not on C's first-parent line:
T=$(git -C "$D3" rev-parse "$A^{tree}")
SIDE=$(printf 'side\n' | git -C "$D3" -c user.name=fixture -c user.email=fixture@invalid commit-tree "$T" -p "$A" -m side)
# unrelated root fetched from a second fixture repo:
D3B=$F/h3-unrelated; git init -q -b main "$D3B"
printf 'u\n' > "$D3B/u.txt"; git -C "$D3B" add -A
git -C "$D3B" -c user.name=fixture -c user.email=fixture@invalid commit -q -m U
git -C "$D3" fetch -q --no-tags "$D3B" main; U=$(git -C "$D3" rev-parse FETCH_HEAD)
```

Fixture revisions: `A=c31c8e74af943b6acc9277f5110883efff8d5d1c`,
`B=bc9427cd86d0e2f885ba264c30bf43dd3232f490`,
`C=601d46ee644b219aa9b055ca36d2d98a265b6b80`,
`SIDE=621022cb036cd5b4fdb1073d845e8a533a09dd03`,
`U=f2ba30efc5b274cfe5011c61eba90de25e343f94`.

### Commands and observed output

```text
$ git -C "$D3" merge-base --is-ancestor A C        # indirect ancestor
exit=0
$ git -C "$D3" merge-base --is-ancestor C A        # reversed
exit=1
$ git -C "$D3" merge-base --is-ancestor B B        # reflexive
exit=0
$ git -C "$D3" merge-base --is-ancestor SIDE C     # shares history, unreachable
exit=1
$ git -C "$D3" merge-base --is-ancestor A SIDE     # side branch descends from A
exit=0
$ git -C "$D3" merge-base --is-ancestor U C        # unrelated root
exit=1
$ git -C "$D3" merge-base --is-ancestor 0000000000000000000000000000000000000000 C
fatal: Not a valid commit name 0000000000000000000000000000000000000000
exit=128
$ git -C "$D3" merge-base --is-ancestor A:a.txt C  # blob, not a commit
error: object 78981922613b2afb6025042ff6bd878ac1994e85 is a blob, not a commit
fatal: Not a valid commit name c31c8e74af943b6acc9277f5110883efff8d5d1c:a.txt
exit=128
```

### Calibration

- The pair semantics are exactly as C2 needs: 0 = ancestor, 1 = not an ancestor, on the installed
  git 2.56.0. A C2-style gate can rest on the exit status.
- Ancestry is reachability, not "shares history": `SIDE` is a child of `A` and shares all of `A`'s
  history, yet `SIDE C` exits 1 because `SIDE` is not reachable from `C`. Symmetrically `A SIDE`
  exits 0. A gate must compare the receipt's named revision to the measured tip in that
  direction, not merely test for a common ancestor.
- Exit 128 is a third state (unresolvable or non-commit object). A gate that reads `!= 0` as
  "not an ancestor / shifted" will mislabel a typo, an abbreviated-but-ambiguous rev, or a tree
  as a planted shifted defect; a gate that reads `!= 1` as "ancestor" will pass an unresolvable
  rev. The frozen predicate's exit-2 vocabulary is the tool's own mapping; git itself says 128.
- Reflexive comparison returns 0, so a receipt header naming the measured tip itself is accepted
  by the ancestry step (its header/semantics are that receipt's business, not this probe's).

**What would have refuted it:** exit 0 for the reversed pair, or exit 1 for the indirect ancestor
pair. Neither was observed.

## H4 — porcelain marks ignored `!! `, untracked `?? `, and a staged-but-uncommitted file `A ` (so a stray rule must count staged paths)

**Verdict: CONFIRMED**, plus a granularity note for `-uall`.

### Fixture

```sh
D4=$F/h4
git init -q -b main "$D4"
printf 'ignored.txt\n' > "$D4/.gitignore"
git -C "$D4" add .gitignore
git -C "$D4" -c user.name=fixture -c user.email=fixture@invalid commit -q -m base
mkdir -p "$D4/newdir"
printf 'a\n' > "$D4/newdir/a.txt"
printf 'b\n' > "$D4/newdir/b.txt"
printf 'staged\n' > "$D4/staged.txt";    git -C "$D4" add staged.txt
printf 'untracked\n' > "$D4/untracked.txt"
printf 'ignored\n' > "$D4/ignored.txt"
mkdir -p "$D4/.ufo/waves/round-72"
printf 'staged wave\n'    > "$D4/.ufo/waves/round-72/staged-wave.txt"
git -C "$D4" add .ufo/waves/round-72/staged-wave.txt
printf 'untracked wave\n' > "$D4/.ufo/waves/round-72/untracked-wave.txt"
```

### Commands and observed output

```text
$ git -C "$D4" status --porcelain -uall
records=6 exit=0
'A  .ufo/waves/round-72/staged-wave.txt'
'A  staged.txt'
'?? .ufo/waves/round-72/untracked-wave.txt'
'?? newdir/a.txt'
'?? newdir/b.txt'
'?? untracked.txt'

$ git -C "$D4" status --porcelain -uall --ignored
records=7 exit=0
'A  .ufo/waves/round-72/staged-wave.txt'
'A  staged.txt'
'?? .ufo/waves/round-72/untracked-wave.txt'
'?? newdir/a.txt'
'?? newdir/b.txt'
'?? untracked.txt'
'!! ignored.txt'
```

```text
$ git -C "$D4" status --porcelain -uall | cut -c1-2 | sort | uniq -c
      4 ??
      2 A 
exit=0
```

(the `2 A ` bucket is `A` followed by one space in column 2; `cut` keeps both columns.)

Exact bytes of the three prefixes:

```text
$ git -C "$D4" status --porcelain -uall -- .ufo/waves/round-72/staged-wave.txt | od -An -tx1
 41 20 20 2e 75 66 6f 2f ... 74 0a          # 41='A', 20 20=two spaces, then the path
$ git -C "$D4" status --porcelain -uall -- .ufo/waves/round-72/untracked-wave.txt | od -An -tx1
 3f 3f 20 2e 75 66 6f 2f ... 74 0a          # 3f 3f='??', 20=one space
$ git -C "$D4" status --porcelain -uall --ignored -- ignored.txt | od -An -tx1
 21 21 20 69 67 6e 6f 72 65 64 2e 74 78 74 0a   # 21 21='!!', 20=one space
```

Granularity: the default untracked mode collapses a wholly-untracked directory, `-uall` lists
each file.

```text
$ git -C "$D4" status --porcelain            # no -uall
records=5 exit=0
'A  .ufo/waves/round-72/staged-wave.txt'
'A  staged.txt'
'?? .ufo/waves/round-72/untracked-wave.txt'
'?? newdir/'
'?? untracked.txt'
```

Scoped to the wave dir, the staged record is counted by the base arm's exact command:

```text
$ git -C "$D4" status --porcelain -uall -- .ufo/waves/round-72
records=2 exit=0
'A  .ufo/waves/round-72/staged-wave.txt'
'?? .ufo/waves/round-72/untracked-wave.txt'
```

Staged-then-modified after `git add`:

```text
$ printf 'changed\n' >> "$D4/staged.txt"
$ git -C "$D4" status --porcelain -uall -- staged.txt
records=1 exit=0
'AM staged.txt'

$ git -C "$D4" status --porcelain -uall | cut -c1-2 | sort | uniq -c
      4 ??
      1 A 
      1 AM
exit=0
```

### Calibration

- Prefixes are two status columns plus one separator space: `A` + space (column 2 empty) + space;
  `??` has no column-2 slot, hence `?? `; `!! ` likewise. A "stray" rule that matches only `??`
  misses staged new files: the staged wave file is a record of the base arm's own command
  (`A  .ufo/waves/round-72/staged-wave.txt`) and must count as uncommitted.
- A staged path that is subsequently modified becomes `AM`, not `A `: the record stays, and its
  first column still marks it as not-in-`HEAD`. Rules keyed on an exact `A ` string would drop a
  dirty staged file; keying on "column 1 is not space and not `?`/`!`" (or simply counting all
  non-empty records) covers `A `, `AM`, ` M`, and `??`.
- `-uall` changes record granularity for untracked directories (1 collapsed record vs 2 file
  records here) but not for staged paths. The frozen base-arm command uses `-uall`; a counter
  that drops it can undercount an untracked tree.
- Without `--ignored`, the ignored `ignored.txt` never appears, consistent with H1.

**What would have refuted it:** a staged-but-uncommitted file absent from plain status, or a
different prefix (e.g. `A` with no second column/separation). Neither was observed.

## Supplemental calibration (adjacent to H1/H2, not extra hypotheses)

### S1-a — an ignore pattern does not hide a tracked path

```text
$ git -C "$D1B" status --porcelain -uall -- .ufo/waves/round-72
records=1 exit=0
' M .ufo/waves/round-72/tracked.secret'

$ git -C "$D1B" status --porcelain -uall --ignored -- .ufo/waves/round-72
records=1 exit=0
' M .ufo/waves/round-72/tracked.secret'

$ git -C "$D1B" check-ignore -v -- .ufo/waves/round-72/tracked.secret
exit=1
```

Fixture: a file matching `.ufo/waves/round-72/*.secret` was force-added and committed, then
modified. Plain status still reports it; `--ignored` does not add an `!!` record; `check-ignore`
says it is not ignored. So C1's "ignored path" case is about untracked ignored paths only, and
a module that combines `status --ignored` with `check-ignore` gets consistent answers.

### S1-b — `git cat-file -e <rev>:<path>` distinguishes present from absent at a revision

```text
$ git -C "$D2" cat-file -e HEAD:plans/round-72-claims.md
exit=0
$ git -C "$D2" cat-file -e HEAD:plans/round-999-claims.md
fatal: path 'plans/round-999-claims.md' does not exist in 'HEAD'
exit=128
$ git -C "$D2" cat-file -e HEAD:.ufo/waves/round-999
fatal: path '.ufo/waves/round-999' does not exist in 'HEAD'
exit=128
```

This is the channel C1 case A needs ("claims plan exists at `<rev>`"): exit 0 vs 128, with no
dependence on the working tree and no vacuity when the wave dir is missing.

## Consequences for the frozen counters (implementation observations, no rule change)

- **C1 case C** must use `--ignored` (with `-uall`) or `check-ignore`; the base arm's plain
  `status --porcelain -uall -- <wave>` cannot see an ignored wave-dir file (H1).
- **C1 case B** must grade repo-wide status: a wave-dir-scoped status hides root and `plans/`
  dirt (H2.d). Counting non-empty records of `git status --porcelain -uall` (whole repo) sees
  all three dirt kinds observed here.
- **C1 case A** should test existence at the revision with `git cat-file -e <rev>:<path>`
  (exit 0/128, S1-b); a wave-dir status test inherits H2's vacuity.
- **C1 stray counting** must count staged records: `A ` and `AM` are records of the same plain
  command, and a staged wave-dir file is visible to the arm itself (H4.f). Counting all non-empty
  records is the robust rule.
- **C2 ancestry step** can rely on 0 = ancestor, 1 = non-ancestor on git 2.56.0 (H3), but must
  keep 128 as could-not-evaluate rather than folding it into `unbound`/`shifted`/`stale`, and
  must pass (header-rev, tip) in that direction (ancestry is reachability: H3.d/H3.e).

## Confidence

High for this host and git version: each verdict was observed directly, with fixtures small
enough that the mechanism is unambiguous, and the two riskiest results (H1's `--ignored` gap and
H2's wrong-label zero) were cross-checked with a second channel (`check-ignore`, whole-repo
status). Not probed (outside the assigned surface): submodules, sparse checkouts, linked
worktrees, case-insensitive filesystems, and global `core.excludesFile` sources.
