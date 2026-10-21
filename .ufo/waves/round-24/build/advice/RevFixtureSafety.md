# RevFixtureSafety — bounded static review: new grid temporary-root guard, cleanup, and fixture isolation

Lane: reviewer (leaf, no dispatch). Base: `0df800e896f6bce285a81e794ad4ae1d1e6c3a71`.
Scratch clone (own, no hardlinks): `/fast/scratch/hyaku/kama-r24/RevFixtureSafety`.
Evidence: `.ufo/waves/round-24/build/out/RevFixtureSafety/git-path-resolution.probe.txt`.
No production file was edited. No grid, candidate, mutant or suite run; no network.

## Verdict

**The r23 base grid is not contaminated and does not leak on its own paths, but it carries neither of the two
guards the r23 lesson itself prescribed, and the r24 grid it is meant to be extended by inherits both gaps.**

Specifically:

1. The r23 fleet contamination (M4) has a **verified, reproducible mechanism** that the committed base grid
   does not guard against, and the r23 lesson's own prescribed fix ("fixture builders must assert
   `rev-parse --show-toplevel` equals the fresh temp dir before writing into `.git`",
   `corpus/lessons/round-23.md:171`) **is not present anywhere in the base grid file**. The new grid must
   implement it, and must additionally forbid the git command that caused the write.
2. The FIFO grandchild leak (M7) is only half-fixed: the base grid kills the auditor's process group on
   the **grid-timeout path only** (`tests/report-audit/repo-state-grid.py:736`). The auditor's own git
   timeout (20 s) is **shorter** than the grid's (30 s), so in every FIFO row the auditor times out
   *first* and the kill branch never runs. Any git grandchild that Python's `subprocess.run` timeout
   handling did not kill survives the case, unrecorded.
3. Neither the r23 nor the r24 design retains **process identity evidence** for killed processes; the r23
   filed row cites a count ("56") with `captured-by: none` and no pid list exists anywhere in the r23 wave
   tree. The r24 preregistration's "40 of 56 killed FIFO-process identities retained" is therefore an
   unbacked number that the new grid must not repeat: it must retain identities itself.

Findings F1–F3 are **High**, F4–F6 **Medium**, F7–F9 **Low**. Acceptance points are in §4 and are
written to be checkable without running the grid.

---

## 1. Findings

### F1 (High) — `git rev-parse --git-path` is the r23 contamination mechanism; the new grid must forbid it as a write target

**Evidence — the mechanism, measured locally** (`.ufo/waves/round-24/build/out/RevFixtureSafety/git-path-resolution.probe.txt`,
git 2.56.0):

| case | command (in repo `r1`) | output |
|---|---|---|
| A | `git -C r1 rev-parse --git-path objects/pack` | `.git/objects/pack` — **relative** |
| B | from `r1/sub` | `../.git/objects/pack` — relative, points **upward** |
| C | `git -C <non-repo path inside a repo> rev-parse --git-path objects/pack` | `../.git/objects/pack`; `--absolute-git-dir` = the **enclosing** repository's git dir |
| D | `git -C /tmp rev-parse --git-path objects/pack` | `fatal: not a git repository`, rc 128 |

Two independent, verified routes from a scratch fixture to the **real fleet's** pack directory:

* **Route 1 (upward discovery, case C).** A path that is *not* a repository but sits inside one resolves
  to the enclosing repository. A seat whose cwd is the fleet root, resolving a pack dir from a
  non-repository path, gets `/home/vgpnk/Projects/shokunin/.git/objects/pack`. This is the wording of the
  filed row (`corpus/lessons/round-23.md:171`).
* **Route 2 (relative capture, case A).** `--git-path` prints a path **relative to the git process's
  cwd** (which `-C` set to the fixture). The *capturing shell* then resolves that string against **its own**
  cwd. The same string `.git/objects/pack` means the fixture's pack dir when consumed inside the fixture
  and the **enclosing repository's** pack dir when consumed from the fleet root.

**The r23 writer matches route 2 exactly.**
`.ufo/waves/round-23/falsify/out/RowF06LazyFetch-2/probe2.sh`:

```
62  PACK=$($BASE_ENV git -C "$ROOT/v5" rev-parse --git-path objects/pack)
65  for p in "$PACK"/pack-*.pack; do : > "${p%.pack}.promisor"; done
72  PACK6=$($BASE_ENV git -C "$ROOT/v6" rev-parse --git-path objects/pack)
73  : > "$PACK6/pack-deadbeef.promisor"
```

`$PACK` is the relative string `.git/objects/pack`; line 65 globs it against the shell's cwd and creates
one marker per **real** pack; line 73 creates the fixture-named marker in the same directory. The observed
damage is exactly that file set — three markers named after real packs plus `pack-deadbeef.promisor` —
`.ufo/waves/round-23/falsify/fleet-contamination/promisor-markers.txt` (8 lines = two runs, mtimes
12:55:13 and 12:58:00 -0300, all four within 40 ms of each other per run). The marker name
`pack-deadbeef.promisor` is the base grid's own fixture name
(`tests/report-audit/repo-state-grid.py:548`), which is why the contamination looked like a grid bug.

**Why this still matters in r24.** The r24 grid must build promisor fixtures — paired `.promisor` marker
files, blobless clones — and the r24 case-builder seats will write shell/Python snippets of exactly the
r23 shape. The production auditor also uses the same command
(`tools/report-landing-audit.py:451`, `git rev-parse --git-path`), read-only today; a fixture that copies
that idiom into a *write* inherits the trap. Nothing in the base grid or the base auditor prevents it:
the base grid's own writes use literal absolute paths (`Path(lane, ".git/objects/pack/...")` at
`repo-state-grid.py:547-548`, `Path(clone, ".git/objects/pack")` at `:209`), which is why the *committed*
grid did not contaminate anything — the offender was a seat script outside the grid.

**Acceptance:** see A1–A4 in §4.

### F2 (High) — the FIFO grandchild leak is fixed only on the path that never fires

`tests/report-audit/repo-state-grid.py:717-738` (`run_case`):

```
730   stderr=subprocess.PIPE, env=env(), cwd=tmp,
731   start_new_session=True)
732   try:
733       out, err = proc.communicate(timeout=TIMEOUT)
735   except subprocess.TimeoutExpired:
736       os.killpg(proc.pid, signal.SIGKILL)
```

`os.killpg` runs **only** in the `TimeoutExpired` branch. But the auditor enforces its own, shorter
deadline: `GIT_TIMEOUT = 20` (`tools/report-landing-audit.py:108`) is used by
`subprocess.run(..., timeout=GIT_TIMEOUT)` (`:117-120`), and the grid's own `TIMEOUT` is `30`
(`repo-state-grid.py:37`). In every FIFO row (`F14` mailmap FIFO `:382-388`, `F30` include FIFO
`:527-536`) the auditor's git call times out at 20 s, the auditor exits 2, `communicate()` returns
normally at ~20 s, and **the kill branch is never reached**. The auditor's own timeout handling kills
only the *direct* child (`subprocess.run` sends SIGKILL to the child it spawned); a git grandchild — a
transport helper, an `sh -c` from `core.sshCommand`, a `git-remote-*` — survives the case, still blocked
on the fixture FIFO, with no record.

The r23 filed row is honest that the leak existed and that the *session* mechanism was the fix
(`corpus/lessons/round-23.md:174`), and it claims "after the final grid run 0 such processes remained".
That claim is about the *timeout* path. The path above is not covered by it.

**Acceptance:** see A5–A8 in §4.

### F3 (High) — no process identity evidence exists for any killed process; the "56" and "40 of 56" figures are unbacked in the lane

`corpus/lessons/round-23.md:174` (M7) gives the evidence pointer as a *count and a time window* — "56
blocked `git` processes under `/tmp/repo-state-grid-*` / `/tmp/kama-r23w2/` (12:18–13:29 -03)" — and
`captured-by: none`. `:109-110` repeats "56 such processes from this round were killed". I searched the
whole r23 wave tree for retained process identities: `grep -rln "pid\b|PGID|pgid"` over
`.ufo/waves/round-23/` returns only `execve-trace.txt` syscall traces and one selftest trace — **no
pid/pgid/cmdline list of the killed processes anywhere**. The r24 preregistration's correction
"40 of 56 killed FIFO-process identities retained, not full identity evidence" therefore cannot be checked
against any artifact in this lane: there is no file holding 40 identities either.

The honest statement available today is: *56 blocked git processes were reported killed; the lane retains
no process identity evidence for any of them, so neither 56 nor 40 is independently verifiable here.*
The r24 correction must say that, and the new grid must not repeat the pattern.

A precedent for doing it properly exists in the r23 wave: `RevengeGitfile.md:15-16` — "Harness kill at 10
to 20 s leaves zero orphan git processes (probe3 C3, `pgrep` pattern validated by a positive control)".

**Acceptance:** see A6–A7 in §4.

### F4 (Medium) — the retained r23 grid's population hash is pinned in committed files, and the r24 policy change alters it

`repo-state-grid.py:711-714` hashes the whole case table *including the expected exit and expected kinds*:

```python
def population():
    rows = [[n, k, b.__name__, e, s, REASONS.get(n)] for n, k, b, e, s in CASES]
    blob = json.dumps(rows, sort_keys=True).encode()
    return hashlib.sha256(blob).hexdigest()
```

The r23 value is pinned in three places, two of them committed documents:

* `corpus/lessons/round-23.md:113` — "population `f29fab8d…364a`"
* `SCORECARD.md:1157` — the same prefix
* `.ufo/waves/round-23/final/grid-both.json:1370` — the full
  `f29fab8d9af1d02de7f6fa4c7b39b2307113d3716fd4b11cffdd0cd65d55364a`

The r24 preregistration requires the r23 grid to be retained "with explicitly documented policy-row
expectation changes" — the promisor rows (`F23` promisor pack, `T01` blobless, and the `C09`/`C10`
promisor controls) are exactly the rows whose expectations move under the r24 policy. Any such change
alters `population()` and therefore invalidates the pinned hash. Editing `corpus/lessons/round-23.md:113`
or `SCORECARD.md:1157` in place would also break the lane's append-only rule.

**Acceptance:** see A9 in §4.

### F5 (Medium) — a single `want_exit` per case cannot express the r24 before/after, so the new grid needs per-arm expectations

`repo-state-grid.py:630-693` gives every case one `want_exit` and one `want_kinds`; the grid's exit
convention is "violations in **either** arm ⇒ exit 1" (`:837`) and its docstring states "`--arm frozen` is
expected to exit 1". That works in r23 because the frozen arm is red on essentially every graded row.

In r24 it does not. The r24 measurement is "frozen = r23 base" against the current candidate, and the
*r23 base is expected to return exit 2 on the promisor rows* — that refusal is the harm being repaired
(`preregistration.json` `expected_before`). If the frozen arm's exit 2 on a promisor row is graded
against the same `want_exit` as the current arm, the grid is red in **both** arms and its exit code
carries no information about the repair. The new grid therefore needs the expectation to be **per arm**,
or a paired structure in which each promisor row's current-arm expectation is inherited from its
non-promisor twin and the frozen-arm expectation is pinned to the r23 observed value.

**Acceptance:** see A10 in §4.

### F6 (Medium) — environmental exhaustion is currently indistinguishable from a case failure, and once counted as a mutant kill

`corpus/lessons/round-23.md:174` is one of several r23 records of the same class; the measured instance
is `.ufo/waves/round-23/falsify/advice/ExecLocaleArms.md:109-111`: "`/tmp` … was full: bytes 100% (3.3M
free) … Twelve of 37 fixtures failed with disk-full errors (`No space left on device`, `unable to write
new index file`…)". The r23 recipe draft then treated the resulting grid exit 2 as a kill
(`.ufo/waves/round-23/falsify/advice/CritNoHarmRecipe.md:87-88`, R5: "R5: the mutant line counts
environment errors as kills").

The committed `tests/report-audit/isolation-mutants.py` has the correct rule — `grid()` returns 2 for a
grid exit 2 (`:78-88`) and the mutant loop then returns 2, "a grid that cannot evaluate kills nothing"
(`:124-136`) — but it has **no timeout on the grid call** (`:79-81`: `subprocess.run([...],
capture_output=True)`), so a hung grid hangs the mutant runner forever.

**Acceptance:** see A11–A12 in §4.

### F7 (Low) — the grid's temporary root is `/tmp`, against the wave's scratch-path rule and against the measured `/tmp` pressure

`repo-state-grid.py:784`: `with tempfile.TemporaryDirectory(prefix="repo-state-grid-") as root:` — the
root follows `TMPDIR`, i.e. `/tmp` on this host. The r24 wave contract requires heavy files under
`/fast/scratch/hyaku/kama-r24/<Name>`; F6 shows `/tmp` on this host reached 100% during r23, and
`ExecLocaleArms.md:111` records that `/tmp/repo-state-grid-hyiacrq2` was still present, owned by another
lane, after that seat's run. A grid root on a controlled filesystem with a recorded path is both the
contract requirement and the mitigation for F6.

### F8 (Low) — two fixture premise checks depend on an external `timeout(1)` binary and on a magic return code

`repo-state-grid.py:385` and `:533` use `subprocess.run(["timeout", "5", "git", ...])` and require
`p.returncode == 124`. If `timeout` is absent the call raises `FileNotFoundError`, which the grid's
catch-all turns into "could-not-evaluate" (`:838-843`) — an indistinguishable reason from a genuine
premise failure. The blocked git is also started in the *grid's* process group, not a new session, so it
is cleaned up only by `timeout`'s own group signal.

### F9 (Low) — the frozen arm is read out of the live lane checkout

`repo-state-grid.py:761-767` (`frozen_auditor`) runs `git -C LANE_DIR cat-file blob FROZEN:AUDIT` with
`LANE_DIR = Path(__file__).resolve().parents[2]` (`:34`) — the live lane working tree. It is read-only
(`cat-file`), so it cannot contaminate anything, but it makes the measurement depend on the checkout the
operator happens to run from, and the r24 grid is required to freeze on the *r23 base*
(`0df800e…`) — a commit, not a working tree.

---

## 2. What the base grid already gets right (keep these)

* `env()` (`:44-51`) strips every ambient `GIT_*`, sets `GIT_CONFIG_GLOBAL=os.devnull`,
  `GIT_CONFIG_NOSYSTEM=1` and pins a fixture identity — no inherited global config, no ambient identity
  dependence (the r23 identity defect, `corpus/lessons/round-23.md:172` M6 / `CritNoHarm.md:45-47`).
* `start_new_session=True` (`:731`) — the auditor gets its own session; the right foundation for F2.
* `cwd=tmp` for the auditor (`:730`) — a relative-path bug inside the *auditor* lands in the case
  directory, not the fleet. Keep, and add the grid's own cwd (A4).
* Premise-before-assert discipline: `require(...)` (`:121-123`) makes a fixture whose fault never
  materialised a `Premise` → exit 2, never a pass.
* `REASONS` (`:695-711`) pins the refusal wording for every exit-2 row so an unrelated startup error
  cannot pass as the intended refusal.
* The auditor's isolation tuple `GIT_ISOLATION` (`tools/report-landing-audit.py:92-97`) keeps
  `--no-replace-objects`, `--no-lazy-fetch`, and the log/signature suppressions. The new grid must not
  relax it; the mutant runner already owns the per-element mutants (`isolation-mutants.py:29-30`).

---

## 3. Axes

| axis | meaning | r23 state | r24 target |
|---|---|---|---|
| A1 containment | no write outside the grid root; no upward git discovery | absent (M4 recurred twice) | structurally impossible |
| A2 cleanup | no surviving child process; identity evidence retained | partial (timeout path only) | every path + identities |
| A3 environment | exhaustion is could-not-evaluate, never a case failure | indistinguishable | typed + errno |
| A4 measurement | population pinned, arms distinguishable, r23 evidence still readable | hash pinned, will move | new hash + row diff appended |

---

## 4. Acceptance points (checkable without running the grid)

**A1 — one grid-owned root, recorded.** The grid creates exactly one root per run with
`tempfile.mkdtemp(prefix="promisor-grid-", dir=<explicit scratch dir>)`; the absolute root path is
written into the JSON receipt and into the run log. The root is on the wave's scratch filesystem
(`/fast/scratch/hyaku/kama-r24/<Name>`), never `/tmp` (F7). Cleanup failure is reported explicitly, not
swallowed.

**A2 — every path the grid writes passes one containment check.** All fixture writes (marker files,
`.promisor` markers, `include.path` FIFO targets, `core.sshCommand` marker targets, errata/registry
files) go through one helper that resolves the target and asserts it is under the resolved root; a
violation raises `Premise` → exit 2, before any write. No `git init`, `git clone`, `git config`,
`git update-ref` or `git replace` may target a path outside the root.

**A3 — every fixture is asserted to *be* the fixture before anything is written into it.** For each
fixture repository, before the first write:

```
top  = git -C <fixture> rev-parse --show-toplevel      # must equal the fixture root
gd   = git -C <fixture> rev-parse --absolute-git-dir   # must be under the grid root
```

and both are compared after `Path(...).resolve()`. This is the r23 lesson's own prescribed fix
(`corpus/lessons/round-23.md:171`), which the base grid does not contain. A fixture whose `--show-toplevel`
does not equal its own directory is a `Premise`, never a write.

**A4 — `git rev-parse --git-path` is never used to derive a write target.** Its output is relative to the
git process's cwd and, for a non-repository path, silently retargets the enclosing repository (F1, cases
A–C). Where a pack directory is needed, derive it from `--absolute-git-dir` and assert containment under
the root. Where a path relative to the repository is needed, resolve it against the *fixture top* from
`--show-toplevel`, never against the process cwd. As defence in depth, the grid sets its own cwd to the
grid root, so a relative-path defect lands in the root rather than in the operator's directory.

**A5 — the auditor's process group is killed on every exit path, not only on timeout.** `run_case`
must kill the group in a `finally` (ignore `ProcessLookupError`), because the auditor's own 20 s git
timeout fires before the grid's 30 s (F2). The grid must therefore not rely on the timeout branch for
cleanup.

**A6 — survivors are counted, and a survivor is a harness failure.** After each case, the grid enumerates
`/proc` for processes whose session id equals the case's session id and records, per survivor: pid, pgid,
sid, `cmdline` (`/proc/<pid>/cmdline`), `cwd` (`/proc/<pid>/cwd` symlink) and start time
(`/proc/<pid>/stat` field 22). A non-empty survivor set is recorded as `harness_leak` and makes the run
**exit 2 (could-not-evaluate)**, not exit 1: a leftover process means the measurement itself is
untrustworthy, which is a different class from "a graded row did not meet its expectation". The
`isolation-mutants.py` rule "exit 2 kills nothing" then protects the mutant run automatically.

**A7 — identity evidence is retained, not summarised.** The per-case survivor/kill records are written to
an append-only file under the wave's out directory (one line per process, with the case name and the
fixture path). A future claim of the form "N processes were killed" must be readable from that file. No
claim of the r23 form — a count and a time window with no identities — may be written again.

**A8 — premise checks that block on a FIFO are self-contained and cleaned up.** The `timeout 5 git …`
premise checks (`:385`, `:533`) are replaced by Python-level timeouts with their own session
(`start_new_session=True`) and the same group-kill discipline; the premise is asserted by observing the
timeout, not by a magic `rc == 124` from an external binary. A missing `timeout(1)` must not be able to
masquerade as "the fixture did not establish its fault".

**A9 — the new grid is a new file with its own pre-committed population hash, and the r23 grid's
population change is recorded as an append-only supersession.** The r24 grid must be
`tests/report-audit/promisor-grid.py` with its own `population()` hash, fixed *before* the candidate
exists (preregistration `oracle`). If `tests/report-audit/repo-state-grid.py` is edited for the promisor
policy rows, the r24 documents must append: the new population hash, the row-level diff (which rows'
expected exit/kinds changed), and the statement that `f29fab8d…364a` identified the `0df800e` file. The
existing pins (`corpus/lessons/round-23.md:113`, `SCORECARD.md:1157`) are append-only and must not be
edited in place.

**A10 — expectations are per arm.** Each case carries an expected exit/kinds for the frozen arm and for
the current arm. The frozen (r23 base) arm's expected exit 2 on the promisor rows is the recorded
"before", not a violation; the current arm's expectation on a promisor row is inherited from its
non-promisor twin. The grid's exit convention stays: violations in the *current* arm ⇒ exit 1; a
harness/premise/environment failure ⇒ exit 2; the frozen arm is expected to be non-zero on the repaired
rows and green on the non-promisor controls.

**A11 — environmental failures are typed.** Fixture builders and the case runner must distinguish
`OSError` with `errno` in {ENOSPC, EDQUOT, EMFILE, ENFILE} (and `PermissionError` on the root) from a
premise failure, report the errno and the path, and exit 2. The r23 measurement (12 of 37 fixtures lost
to a full `/tmp`) must not be re-runnable as a case failure.

**A12 — the mutant runner bounds the grid call.** The grid invocation in `isolation-mutants.py:79-81`
and in the new `promisor-mutants.py` must carry a timeout of its own (the grid's own case timeout plus a
margin) and must treat a timeout as "could-not-evaluate, kills nothing", never as a kill.

**A13 — no network, and the grid's own traps are local.** Promisor fixtures use `file://` local clones
with `protocol.file.allow=always` (as the base grid already does at `:201` and `:599`) and
`core.sshCommand` traps that `touch` a marker **under the grid root** (`:277-278`); the grid must assert
the marker path is under the root, and must never name a network remote.

**A14 — the frozen arm is read from a pinned object, not a working tree.** The r24 grid freezes on the
r23 base commit (`0df800e…`); it reads that blob from a repository it controls (a clone under its own
root) or asserts the blob's sha256 against a pinned value before use, and never writes to `LANE_DIR`.

---

## 5. Residual risk and verification gaps

* **Unrun / unverified by me:** no grid, candidate, mutant, selftest or historical-ledger run; no
  candidate evaluation; no network. Every statement about the *candidate* is from source reading only.
  The two bounded probes I ran are local `git rev-parse` calls in my own scratch clone; their transcript
  is in `.ufo/waves/round-24/build/out/RevFixtureSafety/git-path-resolution.probe.txt`.
* **The r23 contamination writer was never identified.** `CritNoHarmRecipe.md:48-51` records that the
  markers appeared at 12:50:16 and 12:58:00 -03 and disappeared again, that the finder "did not find the
  writer", and that the *fleet* was clean at 15:55:52Z. I have identified a **sufficient** mechanism
  (F1) that produces the exact file set and mtime clustering; I have **not** proven that
  `probe2.sh` was the process that ran at those two timestamps. The mechanism is stated as sufficient, not
  as the confirmed culprit.
* **The 56 / 40-of-56 process counts are unverifiable from this lane** (F3). I did not attempt to
  reconstruct them from host-level process accounting; that is out of scope for a static review.
* **Whether the r24 grid will use `git rev-parse --git-path` anywhere is not yet decidable** — the file
  does not exist at base. A1–A4 are written as acceptance points for it, not as findings against it.
* **Population-hash drift (F4) is a prediction**, contingent on the r24 policy rows actually changing
  `CASES`; if the r23 grid is left byte-identical and the r24 grid is a separate file, the pinned
  `f29fab8d…364a` stays valid and the correction is unnecessary. It becomes necessary the moment a
  promisor row's expectation moves.
* **Not assessed here** (other lanes): the auditor's own `--git-path` read at
  `tools/report-landing-audit.py:451` (read-only; correctness of that join for sub-directory and gitfile
  layouts is `RevBareWorktree`/`RevDraft` territory), the promisor refusal semantics themselves
  (`RevBoolean`, `RevFailureMap`), and the mutant set (`MutationDesign`).

## 6. Tooling

No tool was installed or updated. Host tools used unchanged: git 2.56.0, Python 3.14.8.
Scratch clone: `git clone --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin
/fast/scratch/hyaku/kama-r24/RevFixtureSafety`, checked out at `0df800e896f6bce285a81e794ad4ae1d1e6c3a71`.
No commits, no pushes, no lane file written outside the two paths named in this lane's assignment.
