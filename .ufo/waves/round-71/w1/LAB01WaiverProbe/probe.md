# LAB01WaiverProbe — census waiver semantics on this host

Seat: kama r71 w1 labrat, bounded probe. Lane rev at probe time: `b43e71a8`
(freeze commit). `tools/census-waiver-boundary.py` did **not** exist at probe time
(`ls` → `No such file or directory`); this probe characterises the *landed census
bytes* the C2 boundary will be graded against.

## Method (documented, reproducible)

- `cp tools/round65-host-census.py $S/census-probe.py`; sha256 both files:
  `44bebd671c0d12118c92ace1ef6bd7491a60c7acbce79f1668b81a822b245919` for both,
  `cmp -s` → `COPY_IDENTICAL`. The copy is byte-identical; `main()` is **not**
  patched.
- Each arm imports the copy with `importlib`, reassigns **only** the module global
  `MEMBERS` (the exact input the tool would read from a real census), sets
  `sys.argv`, and calls `mod.main()`, capturing stdout/stderr and the return code.
- Synthetic members are `bash -c` one-liners:
  - `syn-pass` → `echo SYN-PASS; exit 0`, marker `SYN-PASS`
  - `syn-fail` → `echo SYN-FAIL; exit 1` (evaluated FAIL)
  - `syn-refusal` → `echo 'missing dependency: libxyz'; exit 1` with refusal row
    `("missing dependency", reason)` (not-evaluated by refusal marker)
- Deviations from the real run, both benign: the copy's `LANE` resolves to
  `/fast/scratch/hyaku/kama-r71` (the copy's grandparent), not the lane; and the
  synthetic members do not read the lane tree. Neither touches waiver/verdict logic.
- Harnesses: `probe_harness.py` (H1–H4), `probe_extra.py` (parsing/equivalence),
  plus two inline cells for the prefix-collision / space-name / refusal-branch arms.
  Receipts: `probe-run.out`, `probe-extra.out`, `probe-extra2.out`,
  `probe-extra3.out`, `probe-identity.out` (this directory).
- Environment: `Python 3.14.8`, `Linux 7.2.11-arch1-1`.

## H1 — a waiver on an evaluated FAILING member exits 0 — **REFUTED**

```
$ python3 census-probe.py --waive syn-fail
pass [A] syn-pass
FAIL [A] syn-fail: exit=1 tail='SYN-FAIL'
HOST_CENSUS pass=1 fail=1 not_evaluated=0 total=2 tierA_fail=1 tierB_fail=0
[stderr] warning: --waive 'syn-fail' unused: member was evaluated (fail); a waiver covers only not-evaluated members
[exit] 1
```

Waiver is consulted only inside `record_ne()`; a member that ran never reaches it.
The same waiver on a *passing* member is likewise unused and `waived=` is absent
(exit 0 only because `fail=0`):

```
$ python3 census-probe.py --waive syn-pass
HOST_CENSUS pass=1 fail=0 not_evaluated=0 total=1 tierA_fail=0 tierB_fail=0
[stderr] warning: --waive 'syn-pass' unused: member was evaluated (pass); a waiver covers only not-evaluated members
[exit] 0
```

## H2 — a waiver name that is a prefix or glob of a member covers it — **REFUTED** (exact names only)

Prefix, `syn-ref*` and `*` against member `syn-refusal` (all three: not covered):

```
$ python3 census-probe.py --waive syn-ref
refused [A] syn-refusal: fail-closed refusal: synthetic missing dependency (probe fixture) (marker 'missing dependency')
HOST_CENSUS pass=1 fail=0 not_evaluated=1 total=2 tierA_fail=0 tierB_fail=0
CENSUS_NOT_EVALUATED 1 member(s) without a waiver: syn-refusal — exit 1
[stderr] warning: --waive 'syn-ref' is not a census member name
[exit] 1
```

`--waive syn-ref*` and `--waive *` produce byte-identical shape (warning names the
literal string as a non-member) — receipts `probe-extra.out` H2b/H2c. `--waive=syn-ref`
(equals form) behaves the same. The decisive leak test — an exact member name that is
*also* a prefix of another member — waives only itself:

```
$ python3 census-probe.py --waive syn-ref          # members: syn-pass, syn-ref, syn-refusal
refused [A] syn-ref: ... [waived]
refused [A] syn-refusal: ...                        # NOT waived
HOST_CENSUS pass=1 fail=0 not_evaluated=2 waived=1 total=3 tierA_fail=0 tierB_fail=0
CENSUS_NOT_EVALUATED 1 member(s) without a waiver: syn-refusal — exit 1
[exit] 1
```

Real census names contain spaces; exact matching survives quoting in both forms and a
bare prefix does not cover (`probe-extra2.out` H2e/H2f/H2g):

```
$ python3 census-probe.py --waive test-snapshot
[stderr] warning: --waive 'test-snapshot' is not a census member name        [exit] 1
$ python3 census-probe.py --waive "test-snapshot harness"
HOST_CENSUS pass=1 fail=0 not_evaluated=1 waived=1 total=2 ...                [exit] 0
$ python3 census-probe.py --waive="test-snapshot harness"
HOST_CENSUS pass=1 fail=0 not_evaluated=1 waived=1 total=2 ...                [exit] 0
```

Duplicate `--waive` of one name yields `waived=1`, not 2 (`waive_set` is a set;
`probe-extra.out` E2). `--waive=<name>` and `--waive <name>` are equivalent (E1/E1b).

## H3 — a waived not-evaluated member still counts in `not_evaluated` and prints `waived=1` — **CONFIRMED**

```
$ python3 census-probe.py --waive syn-refusal
pass [A] syn-pass
refused [A] syn-refusal: fail-closed refusal: synthetic missing dependency (probe fixture) (marker 'missing dependency') [waived]
HOST_CENSUS pass=1 fail=0 not_evaluated=1 waived=1 total=2 tierA_fail=0 tierB_fail=0
[exit] 0
```

`not_evaluated += 1` happens before the waiver branch returns `" [waived]"`; `waived`
is a separate counter. The `[waived]` marker sits on the member's own line and the
grammar is `not_evaluated=<n> waived=<w> total=<t>` (no-waiver runs keep
`not_evaluated=<n> total=<t>` contiguous, `probe-extra.out` D1). Partial waiver over
two not-evaluated members keeps `not_evaluated=2 waived=1`, names the unwaived one and
exits 1 (D2); waiving both gives `waived=2`, exit 0 (D2b).

## H4 — two invocations in one process are not silent (no cached early return) — **CONFIRMED**

```
=== H4a same argv twice in one process ===
call1 exit=0 call2 exit=0 stdout_identical=True stderr_identical=True
```

and the state-leak check — call 1 waives, call 2 runs with no argv in the same process:

```
=== H4b call 1 (waiver) ===   HOST_CENSUS ... not_evaluated=1 waived=1 total=2 ...   [exit] 0
=== H4c call 2 (no waiver) ===HOST_CENSUS ... not_evaluated=1 total=2 ...            [exit] 1
[stderr] (call 2 only) nothing from call 1
CENSUS_NOT_EVALUATED 1 member(s) without a waiver: syn-refusal — exit 1
```

All verdict state (`waive_set`, `passed/failed/not_evaluated/waived`, `evaluated`,
`unwaived_ne`, `lines`) is local to `main()`; nothing is memoised at module scope.
Second calls emit a complete verdict line and re-run every member.

## Extra discriminators the C2 boundary can key on (landed bytes)

| C2 shim | landed-census signature observed here |
|---|---|
| s4-refusal-as-fail | refusal marker → `refused […]`, `fail=0 not_evaluated=1`, exit 1 unwaived (`probe-extra.out` D1) |
| s5t-hardcoded-total | `total=len(MEMBERS)`: 1, 2, 3 observed across 1/2/3-member tables; real table is 22 (12 A + 10 B) |
| s6w-waiver-swallows-failure | waiver on evaluated fail → `fail=1`, unused-waiver warning, exit 1 (H1) |
| s8r-second-call-silent | two in-process calls both print full verdict, byte-identical (H4a) |
| s10d-refusal-branch-deleted | refusal branch is live on all three paths: refusal marker, budget timeout, spawn error — each → `refused […]`, `not_evaluated++`, never pass/fail (`probe-extra3.out`) |

Refusal-branch detail (budget patched to 1 s for the probe, restored after):

```
$ python3 census-probe.py                                  # spawn error member
refused [A] syn-spawn-err: spawn error [Errno 2] No such file or directory: '/nonexistent/binary-xyz'
HOST_CENSUS pass=1 fail=0 not_evaluated=1 total=2 ...      [exit] 1
$ python3 census-probe.py                                  # budget=1, member sleeps 5
refused [A] syn-slow: census budget 1s exceeded (recorded, not a verdict)
HOST_CENSUS pass=1 fail=0 not_evaluated=1 total=2 ...      [exit] 1
```

Both refuse; both are waivable by exact name (exit 0, `waived=1`).

## What a refutation would have meant for C2

- H1 refuted (observed): had a waiver covered a failing member, the frozen C2 target
  sentence "fail-waiver fixture must exit nonzero" would be unsatisfiable against the
  landed bytes and `s6w-waiver-swallows-failure` would be indistinguishable from the
  real census (killed=5 unreachable). The predicate's parenthetical is grounded.
- H2 refuted (observed): prefix/glob coverage would make one `--waive test-snapshot`
  silence `test-snapshot harness` and let `*` blanket-waive; the docstring sentence
  "repeatable, exact member name" would be false and the boundary tool would owe
  wildcard fixtures. Exact-set membership holds, including the prefix-collision case.
- H3 confirmed: the `not_evaluated=… waived=…` grammar is a reliable two-token
  discriminator between "waived refusal" and "member silently dropped" (the
  `s3-cosmetic-not-evaluated` failure mode).
- H4 confirmed: a shim caching a verdict at module scope is genuinely detected by a
  double-call arm; the real tool cannot be fooled that way.

## Not verified (scope)

- The real 22-member census was not run (22 subprocesses; scout's seat, not this probe),
  so no host verdict table is produced here.
- `tools/census-waiver-boundary.py` did not exist at probe time: its fixtures, its
  `BOUNDARY cases=7 killed=5 survivors=0` line and its five shims were not executed.
- `--waive` names are matched against `MEMBERS` only; membership of a *real* member
  name (spaces, parentheses, e.g. `gate-registry-check selftest (lane-tip arm)`) is
  covered only by the synthetic space-name arm.
- No tool install or upgrade was needed or performed.
