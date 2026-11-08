# SN01Bounds — round-99 w1: boundary and safety review of the three instruments and the candidate probe

Seat: SN01Bounds (leaf; no dispatch). Lane `/home/vgpnk/Projects/shokunin/kama-shokunin`.
Base `439fdb3d41b55e5b9e6d7c480d17f2c428bae978`; freeze commit `f6e7ccc285e0c1207378f73c394acbfda58bff23`.
No tracked lane file was written; no pacman; no sysctl; no pattern-kill; every stub is
`127.0.0.1:0` (OS-assigned ephemeral port) and no operator router or registered consumer was
contacted. Tooling: nothing installed (every dependency was already present: python3 3.14.8,
curl 8.23.0, bash 5.x, git, strace).

All candidate-probe line numbers below refer to the **freeze bytes**
(`sha256 829fbde5…`); the working tree inserts three lines at 952, so later candidate lines shift
by +3 there. Tool line numbers are the working-tree `tools/round99-*.py` bytes; only
`round99-record-audit.py` differs from the freeze commit (inside `read_bytes_at`, `:252-258`), and
the difference does not touch any line I cite.

Scope reviewed (the four files my seat names):

| file | verdict |
|---|---|
| `.ufo/waves/round-99/candidates/kama-probe.r99.sh` (`router_autoload`, `router_refine`) | **D1 defect** in the freeze bytes (regression, outside the graded predicate; fixed in the working tree at 12:46:40); **D4** the freeze receipt is pinned to the pre-fix sha; request surface clean |
| `tools/round99-autoload-states.py` | clean bounds; **D2** exit-class defect; **T3** transient `/tmp` write + SIGKILL leak; one latent hazard (**N1**) |
| `tools/round99-control-population.py` | clean write boundary; **D2** exit-class defect; one by-design execution limit (**L1**) |
| `tools/round99-record-audit.py` | clean (writes nothing, `--tree` unchanged); **D2** exit-class defect; one out-of-lane dependency (**L2**) |

---

## D1 — DEFECT in the freeze bytes, already remediated in the working tree: the C3 candidate makes `consumers` and `listeners` abort silently on an unloaded-autoload router entry

**Where.** Candidate `kama-probe.r99.sh:951-953`:

```bash
  if [ "$ncand" -gt 0 ]; then
    router_autoload "$port"; ra=$?      # line 952
  fi
```

> **State at report time.** The bytes I graded are the freeze commit's
> (`sha256 829fbde5859d9111c85a3d6fe1aa63d0e7c830a40a5fc83c3a0595001fda7f21`, the same sha the
> freeze receipt `controls/c3-candidate.out` records). At 12:46:40 the working-tree candidate was
> changed to `sha256 05ebee88…` with an equivalent condition-wrapped call
> (`if router_autoload "$port"; then ra=0; else ra=$?; fi`, citing "round 99 amendment 1, SC01's
> plain-call receipt"); I re-verified that shape through the real subcommands and the C3 counter
> (both clean, receipts `regress-now.out`, `c3-candidate-at-working-tree.out`). See **D4** for the
> freeze-basis consequence the wave still has to record.

`router_autoload` (`kama-probe.r99.sh:890-919`) now returns **0 on / 1 explicit off / 2 unread**
(it returned only 0/1 before). The script runs `set -euo pipefail` at line 93, and line 952 is a
bare simple command — not the condition of an `if`, not part of an `&&`/`||` list, not negated —
so when `router_autoload` returns 1 or 2 the shell exits *at the `return`*, before `ra=$?` runs.
The `EXIT` trap `cleanup` (`cleanup()` at :130, `trap cleanup EXIT INT TERM` at :131) then
removes `TMP_ROOT` and the process dies with status 1 or 2 and no output at all.

The base probe did not have this: base `tools/kama-probe.sh:931` reads
`if [ "$ncand" -gt 0 ] && router_autoload "$port"; then` — a *tested* context, where bash
suppresses errexit, and base's `router_autoload` never returned anything but 0/1 in that position.

**Why only some subcommands break.** `check` and `snapshot` are safe because they call
`eval_rows` as `eval_rows || exit_code=$?` (`kama-probe.r99.sh:1485`, `:1625`), which suppresses
errexit for the whole call tree. `consumers` (`:1383` port mode, `:1399` registry mode) and
`listeners` (`:1319`) call `classify` as a bare command, so errexit is active inside and the
`router_autoload` return kills the process.

**Reproduction** (scratch stubs only; command lines verbatim; scripts kept under
`out/SN01Bounds/receipts/`):

```
$ bash regress-probe.sh          # one unloaded entry whose status.args[0] is a local file
############ /props=nonjson stub=127.0.0.1:39561
  BASE check     rc=2 stdout=1090B stderr=0B  "verdict": "MODEL_UNLOADED"
  BASE consumers rc=0 stdout=1208B stderr=0B  "verdict": "MODEL_UNLOADED"
  BASE listeners rc=0 stdout=1002B stderr=0B  "verdict": "MODEL_UNLOADED"
  CAND check     rc=2 stdout=1104B stderr=0B  "verdict": "MODEL_UNLOADED"
  CAND consumers rc=2 stdout=0B    stderr=0B
  CAND listeners rc=2 stdout=0B    stderr=0B
############ /props=off stub=127.0.0.1:42739
  BASE consumers rc=0 stdout=1208B stderr=0B
  CAND consumers rc=1 stdout=0B    stderr=0B
  CAND listeners rc=1 stdout=0B    stderr=0B
```

Same result in registry mode with a one-row scratch registry whose consumer file pins
`http://127.0.0.1:<stub>/v1` (`regress-registry.sh`): `BASE consumers rc=0 1320B` /
`CAND consumers rc=2 0B` (unread), `CAND consumers rc=1 0B` (off).

`bash -x` tail of the abort (nonjson case):

```
+ router_autoload 46725
+ local port=46725 pbody=…/props46725.body state
+ curl -sS --noproxy '*' --connect-timeout 2 --max-time 5 --max-filesize 4194304 -o …/props46725.body http://127.0.0.1:46725/props
+ state=unread
+ case "$state" in
+ return 2
+ cleanup                     <-- EXIT trap; `ra=$?` never executes
+ rm -rf -- …/kama-probe.rsYMMi
```

**Impact.** Once M3 replaces `tools/kama-probe.sh` with this body, `bash tools/kama-probe.sh
consumers` — the audit the SKILL tells the operator to run to inspect pin provenance — prints
**nothing** and exits 1 (explicit off) or 2 (unread) — exit 1 is what the probe's own contract
documents as *"probe error (bad arg, missing dep, unreadable registry)"*, and exit 2 is *"at least
one drift"* printed with no row to explain it. The trigger is a normal state: any registered router row
whose matching entry is `unloaded`, which is exactly the state the round-99 vocabulary exists to
describe. `listeners` (the loopback census) dies the same way. Verdicts stay fail-closed, and
`check`/`snapshot` are unaffected, so **C3's five graded cells and the claim's "exit code is
unchanged" hold for the graded path** — the damage is to the two subcommands the claim does not
grade. The 77-test `tests/probe-verdicts` harness drives only `check`
(`PROBE_ARGV_TAIL = ("check", …)`, `tests/probe-verdicts/check.py:87`), which is why the candidate
passed 77/77 with this bug present.

**Independently found.** SC01Recon reached the same diagnosis through a patched `listeners)`
dispatch line (`.ufo/waves/round-99/w1/out/SC01Recon/10-c3-probe-plain-call-regression.out`,
`controls/c3-plaincall.out`); my reproduction drives the *unpatched* `consumers` and `listeners`
entry points, so the two agree on the cause and differ in method. The L1 applied the fix at
12:46:40 — it is **not** in the freeze commit.

**Smallest remediation** (verified, two added lines):

```bash
  if [ "$ncand" -gt 0 ]; then
    ra=0
    router_autoload "$port" || ra=$?
  fi
```

`ra=0` is required: `ra` is initialised to 1 at line 924, so `|| ra=$?` alone would make an
*explicit on* answer look like off. With the patched scratch copy
(`out/SN01Bounds/receipts/kama-probe.r99-fixed.sh`, diff in `receipts/fix.diff`):

- `consumers` and `listeners` return `rc=0` with the full JSON in both the unread and explicit-off
  scenarios (1208B/1208B and 1002B/1002B, matching base's byte sizes);
- the C3 counter still prints
  `AUTOLOAD_STATES99 cells=5 mismatches=0 base_mismatches=4 flips=4 stable=1 met=True`;
- `check` in registry mode emits byte-identical output to base on the explicit-off body (1096B)
  and the intended new reason on the unread body;
- the lane's own 77-test harness passes unchanged on the patched copy:
  `python3 tests/probe-verdicts/check.py --probe <patched>` → `tests=77 passes=77 failures=0`,
  exit 0.

I did not apply it to the candidate (seat bounds: no edits outside my out dir); the L1/EX03 owner
must apply it before M3. Note the C3 claim is still met without the fix — this is a
disclosed-shape defect the claim does not cover, and the report should say so rather than
re-scope C3.

---

## D4 — DEFECT (wave state, calibration): the post-freeze candidate edit leaves the C3 freeze receipt pinned to bytes that no longer exist

`controls/c3-candidate.out` — the freeze-time control the plan names — records
`probe_sha256=829fbde5859d9111c85a3d6fe1aa63d0e7c830a40a5fc83c3a0595001fda7f21`, which is
`git show f6e7ccc2:.ufo/waves/round-99/candidates/kama-probe.r99.sh`. The working-tree candidate is
now `05ebee88bed11e214bbb43cacfc965282b86359d9c2154f340eef36605def050`, and `grep -rl 05ebee88
.ufo/waves/round-99/` finds **nothing**: no receipt, no record, no lesson line names the bytes that
would be graded at M3. The plan's premise is "the graded bytes are the freeze commit's bytes ...
checkable rather than asserted", and kill rule **K1** says "the graded probe/counter bytes change
after the freeze commit". Read literally, K1 now fires on C3 even though the new bytes are strictly
better (the fix only restores `consumers`/`listeners`).

This is not hypothetical bookkeeping: the reviewer's first move is to hash the file and compare it
to the receipt.

**Smallest remediation (evidence already produced).** Record the amendment and re-pin the control at
the new bytes; I ran the replacement so the L1 only has to commit it:

```
AUTOLOAD_STATES99 cells=5 mismatches=0 base_mismatches=4 flips=4 stable=1 met=True
  rev=f6e7ccc285e0c1207378f73c394acbfda58bff23
  probe_sha256=05ebee88bed11e214bbb43cacfc965282b86359d9c2154f340eef36605def050
  base_sha256=40ab387ee9877a9505af61172db5fc1cd2006021fb026e761e558e307a5b4a6e candidate=yes
exit=0
```

(`receipts/c3-candidate-at-working-tree.out`.) Also regenerate `controls/c3-mutant-blanket.out`
from the new base bytes if its sha is quoted anywhere, and state in the lesson/report: *the candidate
gained a call-shape fix after the freeze at 12:46:40; the C3 predicate is unchanged and re-measured
at the new bytes; K1 is satisfied by the amendment, not by ignoring it.* The counter bytes
(`tools/round99-*.py`) are untouched, so C1/C2 are unaffected.

---

## C3 request surface — clean

- **No new request kind.** The candidate's only HTTP calls are
  `fetch()` `:360-363` and `probe_short()` `:395-397` (both base code) and
  `router_autoload()` `:893-894`, which is the *same* bare `GET /props` the base probe made
  (base `:886-887`). No `POST`, no `-X`, no `--data`, no `models/load`, no `/completion`, no
  `--user`, no `Authorization`, no `https://`, no host other than `127.0.0.1:$port`
  (`grep -n 'POST\|--user\|-u \|Authorization\|http://\|https://\|models/load\|completion'` over
  the whole file returns only comments and the six loopback URLs at `:363,:397,:894,:1222,:1385,:1442`).
- **No credential or state change.** `/props` is read bare, never `?model=` (header line 56-57),
  so the read cannot route to or wake an instance. The round-99 change only *interprets* the
  answer; it adds no write path.
- **Limits not weakened.** `TIMEOUT=5` (`:102`), `CONNECT_TIMEOUT=2` (`:103`),
  `MAX_BODY=4194304` (`:109`) are identical to base (`tools/kama-probe.sh:97,98,103`); the diff
  touches only the comment above `MAX_BODY`. `router_autoload` keeps
  `--connect-timeout "$CONNECT_TIMEOUT" --max-time "$TIMEOUT" --max-filesize "$MAX_BODY"` and
  re-checks the written size (`:895`).
- The unread path can only *do less*: when `ra != 0` the `router_file_states` pass (`:957-966`)
  is skipped, so an unread `/props` cannot lengthen the probe.
- One behavioural consequence worth stating in the claim's words: on an unread `/props` the probe
  now reports a *different reason* while keeping `MODEL_UNLOADED` and exit 2 — confirmed by every
  cell above (`router-autoload-unread` at tip, `router-unloaded` at base, exit 2 in both).

---

## Instruments run once each from an empty scratch dir

| instrument | command (verbatim, lane abbreviated `<L>`) | exit | key line |
|---|---|---|---|
| C1 grader | `python3 <L>/tools/round99-control-population.py --repo <L> --rev f6e7ccc2… --counter tools/round99-router-budget.py --work "<scratch>/work c1"` | **0** | `CONTROL_POP99 counter=tools/round99-router-budget.py drop=W14-900k-nd1 patch_removed=1 selected=6 ran=5 mutant_cells=5 mutant_cells_ok=5 mutant_control_exit=1 mutant_ok=0 refused=1 positive_cells=6 positive_exit=0 positive_ok=1 complete=1 population_shaped=1 met=True counter_sha256=e76c35b4… rev=f6e7ccc2…` |
| C2 audit, committed bytes | `python3 <L>/tools/round99-record-audit.py --repo <L> --rev f6e7ccc2… --work "<scratch>/work c2"` | **1** | `RECORD_AUDIT99 checks=12 mismatches=10 met=False` (checks 1,2,3,4,5,6,7,9,10,11 red — the corrections are still in the working tree, exactly the plan's do-nothing value) |
| C2 audit, in-flight tree | `python3 <L>/tools/round99-record-audit.py --repo <L> --tree "<scratch>/tree-m2" --work "<scratch>/work c2 tree"` | **0** | `RECORD_AUDIT99 checks=12 mismatches=0 met=True rev=tree:…` |
| C3 states | `python3 <L>/tools/round99-autoload-states.py --repo <L> --rev f6e7ccc2… --probe-file <L>/.ufo/waves/round-99/candidates/kama-probe.r99.sh --work "<scratch>/work c3"` | **0** | `AUTOLOAD_STATES99 cells=5 mismatches=0 base_mismatches=4 flips=4 stable=1 met=True rev=f6e7ccc2… probe_sha256=829fbde5…` |

Per-cell C3 result (real output, `receipts/c3.out`): U1/U2/U3/U4 tip
`MODEL_UNLOADED/router-autoload-unread`, base `MODEL_UNLOADED/router-unloaded`; P1 both
`MODEL_UNLOADED/router-unloaded`. Every cell exit 2.

**Where C2 stands:** the 12 checks only pass against the *working tree* (`--tree`). At the freeze
commit they print 10 mismatches — the two correction blocks, the lesson and the round-99
record are uncommitted, so the predicate is satisfiable only at M2. That is consistent with the
plan (M2 is the measured commit), and I record it so no one reads the 10 as a counter defect.

**Files created outside each instrument's own scratch** — `find` snapshots taken immediately
after each run over the lane tree, the fleet root, `/tmp` and `$HOME` (depth 3), plus
`strace -f -s 300 -e trace=openat,open,creat,mkdir,mkdirat,unlink,unlinkat,rename,renameat,renameat2,socket,bind`
over each instrument (successful operations only):

- **C2: none.** The only write-mode opens, mkdirs and unlinks are the two `sources-<tag>.md`
  files and their dirfd-relative unlinks inside `--work`; nothing else in the trace. The census
  helper is invoked as
  `bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh census --file <work>/sources-<tag>.md`
  (`round99-record-audit.py:90`) with `OUT=""`, so it writes stdout only; the materialized
  `--tree` is byte- and mtime-unchanged (`find … -printf '%T@ %p'` md5 identical before/after).
- **C1: none** from the grader — writes stay inside `--work`
  (`round99-control-population.py:100-101,105`, and the counter's own `mkdtemp(dir=…)`); the
  counter pins the probe's temp root into its work dir
  (`round99-router-budget.py:385`, `env = dict(os.environ, TMPDIR=str(self.cwd))`), so not even
  `/tmp` is touched. A live strace of the C1 run (still in flight when I stopped it) showed 23
  mkdirs / 346 write-opens, none outside `--work`, no `/tmp` path, and 11 `bind`s all
  `127.0.0.1:htons(0)`. Full census in `receipts/strace-census.txt`.
- **C3: the counter itself writes nothing outside `--work`, but the probe it drives does.** The
  trace shows 10 × `mkdir("/tmp/kama-probe.XXXXXX", 0700)` — one per probe invocation, because
  `round99-autoload-states.py:125-130` does **not** pin `TMPDIR` (unlike the budget counter's
  `Runner`) — each with `m<port>.{body,hdr,err}` and `props<port>.body`, and each removed by the
  probe's EXIT trap (`unlinkat(…, AT_REMOVEDIR) = 0`); `ls -d /tmp/kama-probe.*` afterwards:
  none. All ten `bind`s in the C3 trace are identical and read
  `bind(3, {sa_family=AF_INET, sin_port=htons(0), sin_addr=inet_addr("127.0.0.1")})` — loopback,
  ephemeral port, confirmed at the syscall level.
- No hit for `grep -n '8080\|34113\|11434\|1234'` over all four tools. The only hardcoded address
  anywhere in the reviewed set is `("127.0.0.1", self.port)` in `round99-router-budget.py:254`
  (a liveness check on its own stub).
- Two files did appear under `.ufo/waves/round-99/controls/` during my C1 window —
  `c1-grader-base.out` and `regression-timeout-reap.out` — but their contents quote *other* seats'
  scratch paths (`/fast/scratch/hyaku/kama-r99/c1-base-grader`, `/fast/scratch/hyaku/kama-r99/regression`)
  and the second is a peer's burner-reap receipt; they are L1-side freeze receipts, not this
  instrument's writes.

**T3 (minor defect, leak path).** Because `round99-autoload-states.py:157` calls
`subprocess.run(..., timeout=300)` and does not set `TMPDIR` (`:125-130`), a probe that overruns
the 300 s wall is SIGKILLed by Python, its EXIT trap never runs, and one
`/tmp/kama-probe.XXXXXX` tree survives the run. Smallest remediation: one kwarg —
`env=dict(os.environ, TMPDIR=str(work))` — which also removes `/tmp` from the instrument's write
set entirely (the budget counter already does exactly this at `round99-router-budget.py:385`).

---

## `tools/round99-autoload-states.py` — bounds

- **Stub binds loopback only, ephemeral port:** `super().__init__(("127.0.0.1", 0), Handler)`
  (`:115`); `daemon_threads = True` (`:111`), `allow_reuse_address = True` (`:112`). No code path
  can pick a registered consumer's port: the port is whatever the kernel assigns, and the probe is
  invoked with `--port <that port>` (`:126-127`).
- **4.5 MiB response is bounded:** `b"x" * (4_500_000)` (`:88`) — under the 50 MB rule; the probe
  caps at 4 MiB and aborts the transfer, and the stub swallows
  `BrokenPipeError`/`ConnectionResetError` around `wfile.write` (`:97-99`).
- **6.5 s slow cell is bounded:** `SLOW_DELAY = 6.5` (`:56`), one `time.sleep` (`:85`); the probe
  is given `--timeout 5`, so the cell costs ~5 s at the probe and ≤6.5 s in the stub thread.
  Measured: the whole 5-cell × 2-pass counter ran in **20.6 s**.
- **Sockets/threads closed on every path:** `try: got = verdict_reason(…)
  finally: stub.shutdown(); stub.server_close(); th.join(timeout=5)` (`:157-161`).
  `block_on_close` defaults True, so `server_close()` joins the handler thread and the 6.5 s
  sleeper is reaped before the next cell. Verified: no `r99-autoload-*` dirs and no listener owned
  by any process of my runs remained afterwards.
- **Scratch cleanup runs on failure:** `finally: shutil.rmtree(work, ignore_errors=True)`
  (`:201`) plus the explicit rmtree in the error branch (`:197`). Verified with a missing
  `--probe-file` (leftovers under `--work`: **0**).

**D2 (minor defect, exit-class).** `except (RuntimeError, subprocess.TimeoutExpired)` (`:196`)
does not cover `OSError`/`FileNotFoundError`/`PermissionError`, and `a.work.mkdir(…)` /
`mkdtemp` (`:183-184`) run outside the `try`. Consequences, measured:

```
$ python3 tools/round99-autoload-states.py --repo <L> --rev f6e7ccc2… --probe-file <missing> --work <w>
FileNotFoundError: [Errno 2] No such file or directory: '…/does-not-exist.sh'
rc=1                      # contract: 2 = could-not-evaluate
$ python3 tools/round99-autoload-states.py --repo <L> --rev f6e7ccc2… --work <read-only>/sub
PermissionError: [Errno 13] Permission denied: '…/ro3/sub'
rc=1                      # contract: 2 = could-not-evaluate
```

Same shape in `round99-control-population.py` (read-only `--work`: `PermissionError`, rc=1;
`git show` failure: `SystemExit("…could-not-evaluate…")` → message on stderr, **rc=1**) and in
`round99-record-audit.py` (mkdir/mkdtemp at `:115-116` outside the `try`). Impact: a wrapper that
maps 1 → "predicate not met" will call an infrastructure failure a falsification of the claim.
Remediation: wrap the work-dir creation and the whole body in
`except Exception as e: print(f"… could-not-evaluate: {e}"); return 2`.

**N1 (latent hazard, not a defect as written).** `Handler.scenario` is a *class* attribute mutated by
`Stub.handler_scenario()` (`:59`, `:118-121`), so two stubs alive at once would share the last
scenario set. `run_pass` runs cells strictly sequentially with shutdown between them (`:148-165`),
so the counter is correct today; any future parallelism would silently cross-talk.

**Not a defect.** `--probe-file` grades arbitrary bytes as the probe (documented "freeze control
only"); like every counter here it executes the artifact under test, so it must only be pointed at
lane-controlled files.

---

## `tools/round99-control-population.py` — write boundary

- **Writes only under `--work`:** `a.work.mkdir(parents=True, exist_ok=True)` (`:100`),
  `mkdtemp(prefix="r99-pop-", dir=a.work)` (`:101`), `path.write_bytes(payload)` for the two
  counter copies (`:105`), and the counter is given `--work work/run-<label>` (`:107`). Nothing
  else is opened for writing anywhere in the file.
- **No shell:** every invocation is a `subprocess.run([...])` list (`:79`, `:106`, `:117`), so
  spaces and metacharacters in paths are safe. Measured with `--work ".../space dir"`:
  the full predicate line printed and **exit 0**, leftovers **0**.
- **Read-only `--work`:** `PermissionError` traceback, exit **1** (contract says 2). See D2.
- **`--counter` outside the repo:** `git show <rev>:../../../../etc/passwd` → rc 128 →
  `CONTROL_POP99 could-not-evaluate: git show … rc=128` on stderr, **exit 1** (contract says 2).

**L1 (disclosed limit, by design).** The grader *does* execute caller-chosen **committed Python
bytes**: it runs `git show <rev>:<counter>` twice with `--repo <repo>`. Demonstrated in a fixture
repo (`mktemp -d` under scratch, `git init -q`, toplevel asserted) with a benign blob carrying the
frozen anchor line: both runs printed `MARKER: caller-chosen committed blob executed`. The
anchor gate in `patch_drop` (`:57-66`, exactly one line starting `("W14-900k-nd1",`) is what
stops an ordinary committed file from executing — `--counter README.md` exits 2 with
`could-not-evaluate: cell anchor 'W14-900k-nd1' matched 0 lines`. This is by design ("the graded
artifact is executable"), so the boundary rule is: `--repo` must be the lane, never an untrusted
clone. A committed counter runs unsandboxed with the caller's privileges and could write into
the lane tree; the grader cannot prevent that, and `--work` only governs the grader's own
scratch.
- `patch_drop` counts the anchor (`hits != 1` → could-not-evaluate) before executing, so a
  mutation that would silently not apply cannot pass as a surviving mutant. Clean.
- `--counter` is a *path inside `--repo`*, never a binary: the only process started is
  `sys.executable` on the extracted bytes (`:106`). `--drop` is a cell name matched literally, not
  a command.

---

## `tools/round99-record-audit.py` — write boundary

- Writes only `a.work.mkdir` + `mkdtemp` (`:115-116`) and `sources-<tag>.md` (`:88`), all inside
  `--work`; `shutil.rmtree` in `finally` (`:240`). The materialized `--tree` is opened read-only
  (`:120-121`) and verified unchanged (mtimes and content).
- **L2 (disclosed limit, out-of-lane dependency).** The census helper is an **absolute out-of-lane path**
  (`CENSUS = Path("/home/vgpnk/Projects/shokunin/scripts/sources-census.sh")`, `:57`) and the two
  census revisions are hardcoded (`R98_BASE` `:58`, `R98_TIP` `:59`, both matching the plan's
  `681c80a4`/`649bb2e9`). The audit cannot run in a lane-only checkout, and a
  change to the fleet census script changes the audit's verdict without any lane byte moving.
  The plan's disclosed limit (d) covers the *revisions*; it does not mention the fleet path.
- Bad rev → `RECORD_AUDIT99 could-not-evaluate: unresolvable rev deadbeef`, exit **2** (correct,
  unlike the other two graders). `--tree` without `--rev` works; neither → 64.

---

## Predicate wording vs printed line (calibration note, not a counter defect)

The frozen C1 and C3 predicate lines in `plans/round-99-claims.md` are *not literally* what the
counters print — both carry extra trailing tokens. C1:

```
plan:    … positive_ok=1 complete=1 met=True
actual:  … positive_ok=1 complete=1 population_shaped=1 met=True counter_sha256=… rev=…
```

C3 similarly appends `base_sha256=… candidate=yes` after `probe_sha256=…`. Every token the plan
lists appears, in order, with extras interleaved before `met=True`. A reviewer doing an exact
line match will read the predicate as unmet; a token-subsequence match passes. C2's line matches
exactly. Smallest fix is on the reporting side (quote the real line in `measured/*.out` and match
by token subsequence); the frozen plan cannot be edited.

---

## Summary for the wave

- **C1**: instrument behaviour witnessed at `f6e7ccc2` exactly as claimed (`refused=1`,
  `complete=1`, `met=True`, exit 0). I also re-ran the do-nothing control myself
  (`--rev 439fdb3d --counter tools/round98-router-budget.py`): it prints
  `selected=- ran=5 … mutant_control_exit=0 mutant_ok=1 refused=0 … met=False`
  (`receipts/c1-donothing.out`), and the freeze receipt
  `.ufo/waves/round-99/controls/c1-grader-base.out` records `exit=1` for that same line. Write
  boundary clean; `--drop` is matched literally, the only process started is `sys.executable`.
- **C2**: 12/12 against the in-flight tree, 10 mismatches against the freeze commit (expected:
  the corrections are uncommitted). Writes nothing; `--tree` untouched. Census re-derivation uses
  an out-of-lane script (limit).
- **C3**: 5 cells as claimed; the *candidate probe* also introduces **D1**, a silent abort of
  `consumers`/`listeners` on the very state the claim distinguishes. The claim's graded surface
  (`check`) is unaffected and the predicate is met; the working tree already carries the fix, but
  **D4** (freeze receipt pinned to the pre-fix sha, no record of the new sha) must be closed in the
  wave record before C3 can be read against K1.
  The counter's own bounds are clean (loopback ephemeral stub verified at the `bind` syscall,
  4.5 MiB and 6.5 s both bounded, sockets/threads closed on every path, `--work` always removed),
  with **T3**: it does not pin `TMPDIR`, so each probe run writes a transient `/tmp/kama-probe.*`
  that a SIGKILL-on-timeout would leave behind.
- Minor **D2** exit-class defect in all three graders: `could-not-evaluate` paths exit 1 instead of 2.
- **N1** latent class-attribute stub scenario (safe while sequential); **L1** the grader executes
  committed counter bytes by design (`--repo` must be the lane); **L2** the record audit depends on
  the fleet census script outside the lane.
- No host sysctl, no pacman, no pattern-kill, no operator/consumer contact; scratch
  `/fast/scratch/hyaku/kama-r99/SN01Bounds` deleted at exit.

Receipts: `.ufo/waves/round-99/w1/out/SN01Bounds/receipts/` — `c1.out`, `c1-donothing.out`, `c2-rev.out`,
`c2-tree.out`, `c3.out`, `outside-c{1,2,3}.txt`, `strace-census.txt`, `fix.diff`,
`kama-probe.r99-fixed.sh`, `c3-candidate-at-working-tree.out`, `regress-now.out`, and the drivers
(`run-instruments.sh`, `strace-instruments.sh`, `regress-probe.sh`, `regress-probe-now.sh`,
`regress-registry.sh`, `edge-tests.sh`, `fixture-blob-test.sh`).
