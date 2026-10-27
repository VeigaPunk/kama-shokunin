# Round-50 gate decisions — lane kama, wave 1, seat S2Gate2

Verdict: **ADMIT** — at build commit `97c864bead3ee4a2f629574e77263d33834ec98a`, C1 reads
`bind=1 teardown=1 newrow=1 bound=3/3 met=True` (exit 0) and C2 reads
`fixture=1 lane=1 scenarios=12/12 met=True` (exit 0), both independently reproduced by me on
my own shared clone. Six gate decisions follow: the three named rejects
(environ-only, maps-inode-only, pdeathsig-only), each resolved as
**reject the shortcut / accept the build's measured surface**, and three C2 calibration
rejects (rev-list order, fence-blind sections, byte-exact keys) grounded by the same
counter at the base. One minor counter defect (`--out` write) is reported as a finding,
not patched (counters are frozen).

All commands below were run by me from my scratch
`$S=/fast/scratch/hyaku/kama-r50/S2Gate2` (removed at the end; copies of every output are in
this directory). Lane reads were read-only; no lane file, counter, preregistration or control
was edited.

## Instruments, commits, identity

| item | value |
|---|---|
| lane clone (read-only, `--shared`) | `$S/lane`, HEAD `3b79eaddf38246c637cc7ba1a94ab363422876b6` |
| measured build commit | `97c864bead3ee4a2f629574e77263d33834ec98a` (round-50 build) |
| base | `26ecba64ad6fb571d09074b07202d1618a46ecd1` (round-49 closure) |
| freeze / preregistration | `601c8889f33d1797c712feb753974c20cf891264`, `.ufo/waves/round-50/preregistration.json` |

Instrument identity against the frozen pre-registration (prereg `counter_sha256`):

```
$ cd <lane> && for f in tools/round50-replay-bind-audit.py tools/round50-append-audit-v5-check.py; do
    echo "$f $(git show 97c864be:$f | sha256sum | cut -d' ' -f1)"; done
tools/round50-replay-bind-audit.py ff6ac2ace541ea35a4d240ceebb019653c11a2a08c025e514770f3f94a9c5e89
tools/round50-append-audit-v5-check.py 925f07a48a02ad54a9c89230aac7e54c8dafee4ba2e8a823dcb851b9cf48ca46
```

Both equal the preregistration values (`ff6ac2ac…`, `925f07a4…`): the counters I ran are the
frozen counters. Tool drift from the measured commit to lane HEAD:

```
$ git -C <lane> diff --stat 97c864be..HEAD -- tools/ corpus/
 corpus/SOURCES.md | 2 +-
```

`tools/` is untouched after the build (the one corpus line is the `3d42897b` S498 row tick-parity
fix); C2 re-run at HEAD still reads `fixture=1 lane=1 scenarios=12/12 met=True`. C1's tree and
its three committed receipts are identical at HEAD for tool purposes.

## Gate reading (measured, independent runs)

```
$ python3 <lane>/tools/round50-replay-bind-audit.py --repo "$S/lane" --tip 97c864be… --scratch "$S" --out …/c1-build.out
tip=97c864bead3ee4a2f629574e77263d33834ec98a
bind=1 teardown=1 newrow=1 bound=3/3 met=True
detail: counter vocabulary: 512 tokens from its own download
detail: bind b1: pid 2795687 port 45091 exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode 1955775583 recorded, nonce 'kama witness 3e1f50968e8d1089' round-tripped
detail: bind b2: pid 2807768 port 36255 exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode 209584702 recorded, nonce 'kama witness 0ae467c6eafb62b8' round-tripped
detail: bind b3: pid 2827712 port 34447 exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode 682030054 recorded, nonce 'kama witness fe47b16be28797f3' round-tripped
detail: teardown: invoker SIGKILLed with 3 descendants; after 0.10 s alive [] port refuses ok
detail: newrow: 3 rows new since base; 1 name proc_pid_maps(5): ['| S496 |']
C1_EXIT=0
```

```
$ python3 <lane>/tools/round50-append-audit-v5-check.py --repo "$S/lane" --tip 97c864be… --scratch "$S" --out …/c2-build.out
tip=97c864bead3ee4a2f629574e77263d33834ec98a
fixture=1 lane=1 scenarios=12/12 met=True
detail: lane: tool exit 0 events 5 bad_declarations 0 regressed 0 ungraded_lines 89
detail: lane: event dd9f5dc6c0e6 SCORECARD.md ungraded 17 <= v5 natively exempt 23
detail: lane: event 0718b6abbda6 SCORECARD.md ungraded 72 <= v5 natively exempt 72
C2_EXIT=0
```

These two summaries reproduce the lane's measured receipts
(`.ufo/waves/round-50/measured/c1-build.out`, `c2-build.out`) line for line; the pids, ports,
nonces and inodes differ, as instance facts must.

```
$ python3 <lane>/tools/round50-append-audit-v5-check.py --repo "$S/lane" --tip 26ecba64… --scratch "$S" --out …/c2-base.out
tip=26ecba64ad6fb571d09074b07202d1618a46ecd1
fixture=0 lane=1 scenarios=9/12 met=False
detail: scenario order-b: FAIL exit 1 (want 0)
detail: scenario fence: FAIL exit 0 (want 1)
detail: scenario crlf-launder: FAIL exit 1 (want 1) event {'deleted': 25, 'graded': 0, 'ungraded': 25, 'status': 'ungraded'} want {'deleted': 25, 'graded': 25, 'ungraded': 0, 'status': 'unrestored'}
C2_BASE_EXIT=1
```

The base run reproduces the frozen do-nothing control
(`.ufo/waves/round-50/controls/base.c2.out`, same three FAIL scenarios, `ungraded_lines 82`).
I did not rerun C1 at the base: its preregistered control (`controls/base.c1.out`) is the
freeze artifact and is cited below, not re-executed.

---

## D1 — REJECT `/proc/<pid>/environ` alone as proof of interpreter cleanliness

**Claim.** The four allow-listed names and `-I` are the build's mechanism, but a gate may not
read "no canary in `/proc/<pid>/environ`" as "no interpreter was hijacked". Two independent
failures make environ-only unsound: (a) an interpreter can import a planted `sitecustomize`
while carrying no canary at all (environ clean, interpreter dirty); (b) `/proc/<pid>/environ`
is unreadable for a process of another uid, so an outside observer cannot sample it and must
fail closed rather than read silence as cleanliness. The accepted proof is therefore
**canary absent from the server's and its parent's environ AND the planted-sitecustomize marker
empty**, with unreadable environ graded as a problem.

**Evidence — command and output (mine).**

```
$ python3 "$S/exp/exp1.py" "$S" <lane>/tools
(i) hijacked interpreter (no -I, PYTHONPATH=plant):
KAMA_R50_CANARY in os.environ: False
PYTHONPATH in os.environ: True
sitecustomize imported: True
own environ keys containing CANARY: []
(i) exit: 0
(i) marker file lines: 1 -> ["3457794 ['-c']"]
(i) environ-only witness would call this interpreter CLEAN; the marker says DIRTY
(ii) own pid environ readable: True
(ii) /proc/1/environ: PermissionError: [Errno 13] Permission denied: '/proc/1/environ'
(ii) counter.environ_keys(1) -> None | None is graded as a problem, not as clean
(ii) /proc/1 owner uid: 0 | own uid: 1000
EXIT=0
```

The driver imports the counter's own `environ_keys()` and the marker plant uses the counter's own
`sitecustomize` shape. Build-side mechanism, by file:line:

- `tools/kama-live-replay.py:88` `LIVE_ENV_KEYS = ("PATH", "HOME", "LANG", "LC_ALL")`;
  `:112-115` `live_env()` copies only those and sets `TMPDIR`; `:319` the live child is started
  `sys.executable, "-I"`; `:314-318` and `:332` the child-side `PR_SET_PDEATHSIG` preexec.
- `tools/round50-replay-bind-audit.py:271-277` `environ_keys()` returns `None` on `OSError`;
  `:353-359` the env leg reads the server's and its parent's environ and appends
  `environ unreadable` for `None`; `:480-486` reads the marker after the replay exits and
  appends `planted sitecustomize imported by N interpreter(s)` for any line.
- Frozen base control (`controls/base.c1.out`) shows the other direction at the base:
  `detail: bind b1: server parent pid 418278 carries the planted KAMA_R50_CANARY`.

**Verdict.** Reject environ-only. Accept environ-canary-absence + empty marker + fail-closed on
unreadable environ. The build passes exactly this (three bind legs `env+mapped ok`, no marker
line in `c1-build.out`), so the seat's rejection is consistent with the measured build.

**Flip condition.** Flip to accepting environ-only only if a counter run demonstrates that
environ sampling is both *complete* and *unforgeable*: every process of the tree (server, live
tool, replay, invoker) is readable by the observer's uid and a planted `PYTHONPATH`
`sitecustomize` cannot be imported by any enumerated interpreter. Testably: the ablation control
"no env allow-list (live tool started without `-I` and with the replay's whole environment)"
would have to read `met=True` with the marker check removed while still catching the plant via
environ alone. Until that control reads met, the marker stays the required check.

---

## D2 — REJECT a maps dev+inode without the file hash

**Claim.** `/proc/<pid>/maps` dev+inode identifies *which file object* the server mapped; it
does not identify *the frozen model's bytes*. A host copy placed at the model path before the
server maps it is self-consistent: maps dev+inode equal `stat(path)`'s, and an inode-only check
passes, while the bytes are not `MODEL_SHA`. The accepted proof is
**dev + inode + sha256(mapped pathname) == MODEL_SHA**, and the rerun receipt's
`model_mapping` must record that same hash, dev and inode at the observed pid.

**Evidence — command and output (mine).** The driver uses the frozen model
(`270cba1b…`, 1185376 bytes), maps it in a scratch process, then repeats with a different-bytes
host copy at the same path, and calls the counter's own `mapped_model()` and the live tool's own
`model_mapping()`:

```
$ python3 "$S/exp/exp2.py" "$S" <lane>/tools
genuine path=…/stories260K.gguf size=1185376 sha256=270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d
genuine hashes to MODEL_SHA: True
A-genuine: pid 3506409 maps rows for path: 1; (dev,inode) distinct: [('103:05', '1489165957')]
A-genuine: stat(path) dev=103:05 inode=1489165957
A-genuine: inode-only identity check would pass: True
A-genuine: counter.mapped_model -> ('103:05', '1489165957') problems=[]
A-genuine: live.model_mapping -> mapped=True sha256=270cba1b… reason=None
B mediator path=…/host-copy.gguf size=5224 sha256=afb81fdcbe36200179e20c201dbb7528724bc4cc6ac9eb2b8519973075de5572
B sha256 == MODEL_SHA: False
B-host-copy: pid 3509752 maps rows for path: 1; (dev,inode) distinct: [('103:05', '1489165960')]
B-host-copy: stat(path) dev=103:05 inode=1489165960
B-host-copy: inode-only identity check would pass: True
B-host-copy: counter.mapped_model -> None problems=['no mapping of pid 3509752 is a file hashing to the frozen model (10 file mappings)']
B-host-copy: live.model_mapping -> mapped=True sha256=afb81fdc… reason=None
B-host-copy: live.model_mapping sha256 == MODEL_SHA: False
RESULT inode_only_passes=True counter_mapped=False counter_hash_gate_failed_closed=True live_records_wrong_sha=True
EXIT=0
```

Build-side code by file:line:

- `tools/round50-replay-bind-audit.py:309-341` `mapped_model()`: `:333` requires maps dev+inode to
  equal `stat(pathname)`; `:337` additionally requires `sha_file(pathname) == MODEL_SHA`; a
  candidate failing either is skipped, and if none survives a problem is appended (`:340`).
- `tools/kama-llamacpp-live.py:678-734` `model_mapping()`: maps line dev/inode must match
  `fstat()` of the pathname opened `O_NOFOLLOW` (`:704-717`), then the file is hashed (`:717-728`)
  and recorded with `mapped: True, dev, inode, size, sha256`; recorded into the receipt at
  `:2003` at the server's `child_pid` (`:1896`).
- `tools/kama-live-replay.py:343-348` refuses a rerun whose `model_mapping.sha256` differs from
  the receipt's model: `model-mapping:sha256:<want>-><got>`.
- `tools/round50-replay-bind-audit.py:472-476` requires the rerun receipt's
  `model_mapping.sha256 == MODEL_SHA` and `dev`/`inode` equal to the counter's own observation.

**Verdict.** Reject inode-only. Accept dev+inode+sha256 against the frozen model, with the
receipt-side hash and the counter-side hash both checked. The build passes (all three bind legs
`mapped ok`; the `B` case fails closed in the counter and is refused by the replay's hash leg).

**Flip condition.** Flip only if the mapped file's bytes are proven immutable for the life of the
mapping (e.g. a read-only/sealed backing store) *and* a control run shows the host-copy case is
excluded by identity alone. Testably: the ablation control "no model_mapping record" would have
to stay met=False while a hash-removed variant still rejects the host copy. Until then the hash
is load-bearing and the inode pair is not sufficient.

---

## D3 — REJECT `pdeathsig` alone as proof of teardown

**Claim.** `PR_SET_PDEATHSIG` is a per-process-on-itself request for a *catchable* signal; it is
not inherited across `fork()`, and it does not make a process tree die. A gate may therefore not
read "the replay and live tool set a parent-death signal" as teardown. The accepted proof is
**the counter SIGKILLs the invoker, then observes every snapshotted descendant gone and the port
refusing within 30 s**.

**Evidence — command and output (mine).** Three synthetic scenarios with `prctl(PR_SET_PDEATHSIG,
SIGTERM)`, guard (the middle process) SIGKILLed, 1 s later:

```
$ timeout 120 python3 "$S/exp/exp3.py"
PR_SET_PDEATHSIG(2const) = per-process-on-self, SIGTERM is catchable, not inherited by fork children
ignore: middle SIGKILLed; pdeathsig-carrying child pid 3458194 alive=True
fork: middle SIGKILLed; signal-holder pid 3473340 alive=False; forked grandchild pid 3473415 alive=True
default: middle SIGKILLed; pdeathsig-carrying child pid 3490817 alive=False
RESULT ignore_survives=True fork_grandchild_survives=True default_child_dies=True
VERDICT pdeathsig alone insufficient: signal ignored -> survivor; forked grandchild not covered -> survivor; default disposition -> dies
EXIT=0
```

The mechanisms actually shipped, by file:line:

- `tools/kama-live-replay.py:100-108` `set_own_pdeathsig()` (`PR_SET_PDEATHSIG=SIGTERM` on the
  replay, with an `os.getppid()` re-check and `os._exit(1)` if the parent was already gone);
  called from `main()` at `:587` before the replay runs.
- `tools/kama-live-replay.py:312-318` the live child's `preexec_fn` sets the same signal and
  exits if the replay is gone; `:332` passes it to `subprocess.run`.
- `tools/kama-llamacpp-live.py:661-675` `_preexec_pdeathsig()` sets `PR_SET_PDEATHSIG=SIGKILL`
  on the server child, with a ppid re-check.
- `tools/round50-replay-bind-audit.py:497-525` `teardown_leg()`: snapshot descendants
  (`:505`, pid+start time), `os.kill(p.pid, SIGKILL)` on the invoker (`:509`), poll up to
  `KILL_WAIT=30` (`:112`, `:512-514`) for every snapshotted pid to be absent and the port to
  refuse, and `ok` requires both (`:515-519`). Observed at the build: `3 descendants; after
  0.10 s alive [] port refuses ok`.

**Verdict.** Reject pdeathsig-alone. Accept the empirical kill-and-observe leg. The measured
build passes it (0.10 s, empty alive set, port refusing), and the base control's teardown line
(`alive [531059, 568483, 573554] port ACCEPTS FAIL`) shows the leg is not trivially satisfied.

**Flip condition.** Flip only if signal delivery to *every* descendant is guaranteed by
construction (uncatchable, tree-wide, race-free) and a run with the observation leg removed
still tears the tree down. Testably: the ablation control "no replay parent-death signal" would
have to read met=True under the observation leg's removal, or a survivor/delivery experiment
would have to end with no process alive and the port refusing without the counter's kill. Until
then the observation is the proof and the mechanism is not.

---

## D4–D6 — C2 calibration rejects (same counter, base run)

All three are the same rule: the instrument's grading must be a property of the commit graph and
its text, not of git's listing order, a fenced line's appearance, or a line's line ending. Each
is rejected by the v4 tool at the base and accepted by v5 at the build — one counter, same
fixtures.

| id | rejected shortcut | base evidence (`c2-base.out`, exit 1) | build evidence (`c2-build.out`, exit 0) | flip condition |
|---|---|---|---|---|
| D4 | origin = first blob in `git rev-list --topo-order --reverse` (sibling order decides) | `scenario order-b: FAIL exit 1 (want 0)` — same tree, merge parents swapped | `scenario order-b: ok exit 0 (want 0)` and `order-a: ok` | flip only if rev-list order is proven invariant for equal trees *and* a fixture pair with swapped merge parents is shown to be indistinguishable; otherwise the pair is a required fixture |
| D5 | sections blind to CommonMark fenced blocks (a `## ` line inside a fence re-titles dated lines) | `scenario fence: FAIL exit 0 (want 1)` — 25 deleted lines graded ungraded under a fake heading | `scenario fence: ok exit 1 (want 1)` with `graded 25 ungraded 0` | flip only if the lane's rule is restated to not depend on fence state and the fence fixture is removed from the contract; the CommonMark 0.31.2 §4.5 source row (S498) would then be unsupported |
| D6 | origin keys byte-exact (a line moved under a changed line ending has no origin) | `scenario crlf-launder: FAIL exit 1 (want 1)` — `deleted 25 graded 0 ungraded 25`, want `graded 25` | `scenario crlf-launder: ok exit 1 (want 1)` with `graded 25 ungraded 0` | flip only if the lane fixes a canonical line-ending representation for contracts *and* the CRLF fixture is shown to be graded by that rule; until then one trailing-CR strip is required |

**Verdict (D4–D6).** Reject rev-list-order origin, fence-blind sections and byte-exact origin
keys; accept v5's birth-DAG union, fence-aware sections and one-trailing-CR keys — measured by
the same counter, same fixtures: base `9/12 met=False` (exit 1), build `12/12 met=True` (exit 0).

The C2 accountancy leg (graded + ungraded == deleted, and deleted == `git diff --numstat`) is
checked inside every scenario by the counter and held at both commits (the base failures above
are grading, not arithmetic).

---

## Adopted gate rule (summary)

| surface | accepted proof | rejected shortcut | measured at build |
|---|---|---|---|
| interpreter environment | canary absent from server + server-parent environ **and** planted-sitecustomize marker empty; unreadable environ is a problem | environ only | pass (`env+mapped ok`, no marker lines) |
| model bytes | maps dev+inode **and** sha256(pathname) == `MODEL_SHA`; receipt `model_mapping` same sha/dev/inode at observed pid | inode only | pass (3/3 joined, dev `103:05`) |
| teardown | invoker SIGKILLed; every snapshotted descendant gone and port refusing within 30 s | pdeathsig only | pass (3 descendants, 0.10 s, port refuses) |
| append-only origin | birth-DAG union over commits reachable from tip; fence-aware sections; one trailing CR stripped; graded+ungraded==deleted | rev-list order / fence-blind / byte-exact keys | pass (12/12 fixtures, lane exit 0, 89 ungraded lines) |

## Limits of this gate

Carried from the preregistration (unchanged, they bound what the rejects prove):

- C1 limit 1: the mapped check compares the maps dev/inode with a *now* stat of the pathname and
  hashes that path; a file rewritten in place with identical bytes is indistinguishable, and a
  filesystem whose maps dev differs from `stat` st_dev fails closed (counter scratch is xfs).
- C1 limit 2: only `KAMA_R50_CANARY` and the `PYTHONPATH` sitecustomize are planted; LD_PRELOAD
  into the server and a modified `python` on PATH are not.
- C1 limit 3: teardown is killed once during the witness hold; kills during download or
  readiness are not exercised.
- C2 limits: births are computed over every commit reachable from `<to>`; text born in both an
  exempt and a dated section counts as exempt-born; the lane leg's binder is still the v4 rule
  and the sub-20 threshold is unchanged.

Mine, on top of those:

- The exp1 plant is a same-uid interpreter: the other-uid case is demonstrated only by
  `/proc/1/environ` (EACCES) and `environ_keys(1) -> None`, not by a live other-uid server.
- Exp2's "host copy" is a different-bytes file mapped at a path in scratch; it is not a
  substituted file inside a running replay's work tree.
- Exp3 uses synthetic `prctl` processes on this host/kernel, not the lane's replay; the
  lane-level teardown is the counter's own leg (observed once at the build).
- I did not rerun C1 at the base: the base control (`controls/base.c1.out`) is the freeze
  artifact; I reran only C2 at the base (reproduced its control) and both counters at the build.
- No kernel delivery tracing (no gdb/ftrace); exp3's survivors are observed with `kill(pid, 0)`.

## Findings

**F1 (defect, minor, in both frozen counters).** `--out` is written without creating its parent
directory, and the write happens *after* the summary is printed. A run whose receipt path has a
missing directory prints a full `met=True` summary and then exits 1 with a traceback — the same
exit code the contract uses for "not met", and the receipt is lost. Observed:

```
$ python3 <lane>/tools/round50-append-audit-v5-check.py --repo "$S/lane" --tip 97c864be… --scratch "$S" --out <nonexistent>/c2-build.out
tip=97c864bead3ee4a2f629574e77263d33834ec98a
fixture=1 lane=1 scenarios=12/12 met=True
… (details) …
Traceback (most recent call last):
  File "<lane>/tools/round50-append-audit-v5-check.py", line 545, in <module>
  File "<lane>/tools/round50-append-audit-v5-check.py", line 537, in main
FileNotFoundError: [Errno 2] No such file or directory: '…/c2-build.out'
C2_EXIT=1
```

- `tools/round50-append-audit-v5-check.py:537` `with open(a.out, "w") as fh:` (no parent mkdir,
  no `OSError` handling).
- `tools/round50-replay-bind-audit.py:597` the identical pattern.
- Proposed fix (not applied; counters frozen): before the open, in both counters,
  `os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)`, or wrap the write in
  `try/except OSError` and return 2 with `could-not-write-receipt: <path>: <err>` so "met but
  receipt lost" is distinguishable from "not met". The gate reading above is unaffected: my
  successful runs used an existing out directory and returned exit 0.

**F2 (provenance, passes).** Counter sha256 values equal the preregistration (`ff6ac2ac…`,
`925f07a4…`); the counters I ran are the frozen ones.

**F3 (cross-check, passes).** My independent C1/C2 runs at `97c864be` reproduce
`.ufo/waves/round-50/measured/c1-build.out` and `c2-build.out` line for line on every summary
and lane detail (`ungraded_lines 89`; `0718b6abbda6 ungraded 72 <= 72`); instance facts differ.

**F4 (drift, passes).** `tools/` is unchanged between `97c864be` and lane HEAD; only
`corpus/SOURCES.md` moved (2 lines, the `3d42897b` tick-parity fix). C2 at HEAD still reads
`fixture=1 lane=1 scenarios=12/12 met=True`.

**F5 (base negative control, passes).** C2 at `26ecba64` reads `fixture=0 lane=1 scenarios=9/12
met=False` (exit 1), matching `controls/base.c2.out`, including the same three FAIL scenarios and
`ungraded_lines 82`.

## Environment / tooling

No installs or upgrades; nothing new on PATH. Commands used were `python3` (stdlib drivers),
`git` (read-only), `sha256sum`, `curl` (one 1 KB range probe to huggingface.co), and the two
frozen counters (which download llama.cpp b11909 ~75 MB per replay from github.com and the
1.2 MB model from huggingface.co, and start three loopback llama-server processes). No
llama-server I started survives: C1's own teardown reported `alive []`, and `pgrep -af` matched
no process referencing my scratch or my out paths after the runs (the only `llama-server`
processes visible belonged to other seats' scratch trees, untouched).
