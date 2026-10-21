# Row F14-mailmap-fifo — falsifier advice

Commit audited: `245a37f69628c2c6bb29bbf17897d8fb5946c857`
Environment: git 2.56.0, Python 3.14.8, clone `/tmp/kama-r23w2/RowF14MailmapFifo`
(`git rev-parse HEAD` = 245a37f6…). No tools installed; no lane tracked files touched
(only this advice file was written under `.ufo/`).

## Verdict

**Partially.** The scored row itself **holds**: the FIFO premise is real, the frozen
arm is observed to hang (not merely reported), the current arm returns the accurate
clean verdict, the expected `exit 0 / kinds []` is the correct expectation, and no
verdict flip or traceback occurs. The broader C1 sentence — “repository-local git
state in audited repos must not crash … hang” — is **falsified for near variants**:
the current auditor still hangs unboundedly on a FIFO at `.git/shallow` (exactly the
path its F10 refusal guard probes), at `.git/config`, at the fleet’s `.git/HEAD`, at a
lane branch ref, and at `.git/packed-refs`. The mailmap channel proper is closed.

## 1. Premise real, and observed in the frozen arm

Rebuilt **by hand**, not via the grid, in `/tmp/f14-hand`: lane repo with one commit
`round-1: work` (author `kama-shokunin`, `@1000 +0000`), fleet repo with
`.ufo/reports/round-1/kama.md` citing that commit (`@2000 +0000`), then
`mkfifo lane/.mailmap`. All git invocations used
`GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1` and explicit identity.

Raw premise and mechanism (all with `timeout 5`):

```
git -C lane log -1                                   -> rc=124   (blocks)
git -C lane log -1 --format=%an                      -> rc=124   (blocks)
git -C lane -c log.mailmap=false log -1              -> rc=0     (does not read)
git -C lane rev-parse HEAD                           -> rc=0     (repo otherwise usable)
```

So `log.mailmap` defaulting to true makes `git log` *open* `.mailmap` even when the
format only asks for raw `%an`; `-c log.mailmap=false` prevents the open.

Auditor runs on the same hand-built fixture, cwd `/tmp/f14-hand`:

```
current  tools/report-landing-audit.py --lane-repo lane --fleet-repo fleet \
         --rounds 1 --no-errata --json      -> rc=0   stderr empty
         results[0]: required=1, defects=[], cutoff=2000, report_committed=true
         summary.status=clean
frozen   frozen-audit.py (extracted via
         `git cat-file blob 4fe9339…:tools/report-landing-audit.py`) \
         same argv                          -> rc=124 at 20 s, no output
```

Attribution of the frozen hang to the FIFO: the same frozen blob on the **identical
fixture with `.mailmap` removed** exits 0 with `required=1, defects=[], cutoff=2000`.
Causality inside current: removing only the two argv elements `"-c",
"log.mailmap=false"` from a /tmp copy of the current file and running it on the FIFO
fixture gives `rc=124` at 12 s (with the flag: `rc=0`). That flag is the whole
mitigation for this row.

Grid reproduction, `tests/report-audit/repo-state-grid.py --case F14-mailmap-fifo`:

```
population_sha256 83a84702251c62c6990c8222ea6c4276e09db05344b3c2c0d862a857e50ea2f1
auditor_sha256 frozen 09ecd63bdc3a5be5264e6d2966602a32e52ca0678dc89de99959318245ab3b3f
               current f228f17420134a4a4fb6d1f93b943f78647e7e60882f767e6cb7cba11d6928a7
current exit=0 kinds=[] traceback=false executed=false timed_out=false met=true
frozen  exit=null kinds=null traceback=false executed=false timed_out=true  met=false
```

(`--case` with both arms exits 1 because the frozen arm violates; that is the
documented `--arm frozen` behaviour, not a grid defect.) My frozen file’s SHA-256
equals the grid’s frozen auditor hash, so the bytes I ran are the bytes the L1 ran.

Row anchors at 245a37f6: builder `tests/report-audit/repo-state-grid.py:381-387`,
row `:555`, harness timeout `:36`, met predicate `:600-630`; mitigation
`tools/report-landing-audit.py:93-96`; log call `:183-184`.

## 2. The expected outcome is correct, not merely what current does

Expected by the grid: exit 0, no defect kinds, `--rounds 1 --no-errata`.

- The fixture’s only fact is “fleet report cites a lane commit that exists”; the LANE
  has no omitted round commit and the fleet has no post-report commit, so a clean
  verdict is the true one.
- Mailmap cannot move the author filter: the audit matches raw `%an`
  (`tools/report-landing-audit.py:183`), and with a regular `.mailmap`
  `Evil <evil@example.invalid> <a@x>` the observed output is
  `an=kama-shokunin aN=Evil` under default config, `log.mailmap=false`, and
  `log.mailmap=true`. Raw `%an` is never rewritten; `%aN` is, but is never used.
- The FIFO is untracked worktree state; the audit reads lane history and the fleet’s
  committed report (`git show HEAD:rel`, `:298`), not worktree files.
- No flip/hidden masking: with the FIFO present, a report citing a fabricated 40-hex
  exits 1 with `landed-omitted`, `landed-unresolved`, `unresolved-full-hash`; a report
  with the citation dropped exits 1 with `landed-omitted`. With vs without the FIFO
  the current arm’s JSON is equal (`cmp` on `json.dumps(doc, sort_keys=True)` of both
  runs: identical), both rc 0.

A refusal (exit 2) for an irregular `.mailmap` would be a *stricter* declared
tradeoff, not the correct verdict; nothing the audit reports depends on that file.
Exit 0 is right.

## 3. Near variants the current auditor still gets wrong

The `.mailmap` channel proper is closed. I could not make current read a mailmap:
lane `.mailmap` FIFO with repo `log.mailmap=true` → rc 0; `mailmap.file` pointed at a
FIFO and armed with `log.mailmap=true` (raw `git log -1` → rc 124) → auditor rc 0;
fleet `.mailmap` FIFO → rc 0. The surviving class is **adjacent repository-local
FIFOs at paths git opens eagerly**, which the auditor neither `stat`s nor time-bounds
(`subprocess.run` at `tools/report-landing-audit.py:114` has no `timeout=`; `grep -n
timeout tools/report-landing-audit.py` → none). Each fixture below is fresh, built like
§1, then one path replaced by `mkfifo`:

| FIFO path | premise command → rc | current auditor (10–20 s outer `timeout`) | hang site |
|---|---|---|---|
| lane `.git/shallow` | `git rev-parse --is-shallow-repository` → 124 | **rc=124**, empty stderr | `:436` shallow probe (`:431/:434` rc 0) |
| lane `.git/config` | `git rev-parse --show-object-format` → 124 | **rc=124** | `:431` first `git()` probe |
| fleet `.git/HEAD` | `git rev-parse --verify HEAD^{commit}` → 124 | **rc=124** | `:431` first `git()` probe |
| lane `.git/refs/heads/master` | `git rev-parse --verify refs/heads/master^{commit}` → 124 | **rc=124** | `:455-456` `resolve_branch` (`:431/:434/:436/:439/:445` rc 0) |
| lane `.git/packed-refs` (after `pack-refs --all`) | `git rev-parse --verify refs/heads/master^{commit}` → 124 | **rc=124** | `:455-456` `resolve_branch` (`:431/:434/:436/:439/:445` rc 0) |

`.git/shallow` is the nearest neighbour to F14: it is a plain repository-local file
that git opens eagerly, it is the exact state F10 grades with a regular file and
expects to be *refused* (`:436`, reason “shallow repository”), and in this fixture the
object store remains usable (`git cat-file -t HEAD` → rc 0), so the hang is the
auditor’s probe, not a dead repository. The frozen blob hangs on `.git/shallow` and
`.git/config` too (`rc=124`), so these are not regressions — but current does not meet
the unqualified C1 “never hang” claim either.

Controls that show this is per-path guarding, not an inherent limitation:
`.git/info/grafts` FIFO → current exits 2 in well under the outer timeout with
`could-not-evaluate: … .git/info/grafts rewrites history` (the `os.path.lexists`
check at `:440` never opens it); `--report N=PATH` FIFO → rc 2 in <1 s with
`could-not-evaluate: /tmp/f14-hand/rep.fifo: not a regular file` (the `stat.S_ISREG`
check at `:211`); fleet `.gitattributes` FIFO, fleet
`.git/info/attributes` FIFO and lane `.gitattributes` FIFO do not block the audit’s
git calls (rc 0 for both the raw premise and current).

One adjacent unguarded read outside the repository-state axis: `--errata PATH`
pointing at a FIFO (`load_errata` calls `Path(args.errata).read_text` at `:367`
without a regular-file check) hangs (rc 124 at 8 s). That path is operator-supplied,
not lane state, so I do not count it against C1.

Within the *worktree-root* metadata family, `.mailmap` is the only file these git
calls open — the `.gitattributes` FIFOs above are inert — so a closer worktree variant
does not exist; what survives is the `.git/` half of the same eager-open class.

Two satisfiable fixes exist
without redesign: `stat`-check the config/HEAD/shallow/ref paths before invoking git,
and/or pass `timeout=` in `git()` and map expiry to EvalError (exit 2).

## Not verified

- The other 25 grid rows; the L1’s “frozen 0/26, current 26/26, 8/8 controls” aggregate
  (only F14 was reproduced here).
- `tests/report-audit/isolation-mutants.py` and survivors M02/M20.
- No-harm claims (selftest 50/50, rounds 10-22 ledger identity, `--no-errata` exit 1).
- Tradeoffs T01 (shallow/partial clones) and the git ≥ 2.45 floor.
- Declared-open channels O01/O02, ambiguity overwrite, second Landed section, errata CR,
  sibling tools.
- Any git version other than 2.56.0; the `.git/config`/`.git/shallow` FIFO premise on
  other versions.
- REA/devices, browser, network (none used).

## Files written

- `kama-shokunin/.ufo/waves/round-23/falsify/advice/RowF14MailmapFifo.md` (this file).
- /tmp scratch only: `/tmp/kama-r23w2/RowF14MailmapFifo/` (clone + extracted
  `frozen-audit.py`), `/tmp/f14-hand/`, `/tmp/f14-var/` (fixtures, outputs,
  `grid-f14.json`, `cur-nomailmapflag.py`). No lane checkout, index, `.jj`, or
  configuration was modified.

## Provenance note (concurrent lane drift, not mine)

Every observation above is pinned to commit `245a37f6`. The clone used for all runs
was at that commit; the committed auditor there hashes
`f228f17420134a4a4fb6d1f93b943f78647e7e60882f767e6cb7cba11d6928a7`, which is also the
`auditor_sha256.current` the grid recorded during my F14 run (`grid-f14.json`).

After those runs, while this report was being written, the lane **working tree** was
observed dirty for files I never wrote: `tools/report-landing-audit.py` now hashes
`3fc567abfd3d21c78ea2f8553027a9e30906cd8d4c5d0b3ac2ce859dda763f8f` (`git diff` +62
lines, e.g. a new `git_bool`) and `tests/report-audit/repo-state-grid.py` has +106
lines incl. new rows F27–F29. That is concurrent work by others, not part of this
falsification. Line anchors and hashes in this report are the committed `245a37f6`
blast, verified in my clone; they do not describe the later working tree.
