# LAB01WaiverProbe — wave-1 labrat report (kama r71)

Seat: bounded probe, census waiver semantics on this host. Axis: operability (C2 grounding).
Lane rev at probe time: `b43e71a8` (freeze). `tools/census-waiver-boundary.py` absent
(`ls` → `No such file or directory`), so this seat probes the landed census bytes the C2
boundary will grade, not the boundary tool.

Inputs read first, in full: `plans/round-71-claims.md` §C2, §kill rules; `tools/round65-host-census.py`
(docstring, `MEMBERS`, `main()`).

## Method

```
cp tools/round65-host-census.py /fast/scratch/hyaku/kama-r71/LAB01WaiverProbe/census-probe.py
sha256sum <lane>/tools/round65-host-census.py $S/census-probe.py
44bebd671c0d12118c92ace1ef6bd7491a60c7acbce79f1668b81a822b245919  (both)
cmp -s ... && echo COPY_IDENTICAL                                            → COPY_IDENTICAL
```

Chosen mechanism: **import the copy** (`importlib`) and reassign only the module global
`MEMBERS` before calling `mod.main()`; `main()` is unmodified. (The alternative — editing a
copied `MEMBERS` literal — was not used, so the copy's bytes are provably the lane's bytes.)
`sys.argv` is set per arm; stdout/stderr captured via redirects; exit code recorded.

Documented deviations (benign, both stated in probe.md): the copy's `LANE` resolves to
`/fast/scratch/hyaku/kama-r71` (grandparent of the copy), not the lane; synthetic members are
`bash -c` one-liners that do not read the lane tree.

Environment: Python 3.14.8, Linux 7.2.11-arch1-1. No tool install/upgrade was needed.

## Verdicts (4/4 as frozen)

| H | Statement probed | Verdict | One-line evidence |
|---|---|---|---|
| H1 | waiver on an evaluated FAILING member exits 0 | **REFUTED** | `fail=1 … tierA_fail=1`, stderr `unused: member was evaluated (fail)`, exit 1 |
| H2 | waiver name that is a prefix/glob of a member covers it | **REFUTED** (exact only) | `syn-ref`, `syn-ref*`, `*` each → `not_evaluated=1` no `waived=`, `CENSUS_NOT_EVALUATED`, exit 1 |
| H3 | waived not-evaluated member still counts and prints `waived=1` | **CONFIRMED** | `not_evaluated=1 waived=1 total=2`, line carries `[waived]`, exit 0 |
| H4 | two in-process invocations are not silent / not cached | **CONFIRMED** | call1/call2 byte-identical; waiver→no-waiver transition in one process → call2 exit 1, no `waived=` |

Exact H1 output:

```
$ python3 census-probe.py --waive syn-fail
pass [A] syn-pass
FAIL [A] syn-fail: exit=1 tail='SYN-FAIL'
HOST_CENSUS pass=1 fail=1 not_evaluated=0 total=2 tierA_fail=1 tierB_fail=0
[stderr] warning: --waive 'syn-fail' unused: member was evaluated (fail); a waiver covers only not-evaluated members
[exit] 1
```

Exact H2 output (prefix arm; glob arms byte-identical in shape):

```
$ python3 census-probe.py --waive syn-ref
pass [A] syn-pass
refused [A] syn-refusal: fail-closed refusal: synthetic missing dependency (probe fixture) (marker 'missing dependency')
HOST_CENSUS pass=1 fail=0 not_evaluated=1 total=2 tierA_fail=0 tierB_fail=0
CENSUS_NOT_EVALUATED 1 member(s) without a waiver: syn-refusal — exit 1
[stderr] warning: --waive 'syn-ref' is not a census member name
[exit] 1
```

Exact H3 output:

```
$ python3 census-probe.py --waive syn-refusal
refused [A] syn-refusal: fail-closed refusal: … (marker 'missing dependency') [waived]
HOST_CENSUS pass=1 fail=0 not_evaluated=1 waived=1 total=2 tierA_fail=0 tierB_fail=0
[exit] 0
```

Exact H4 output (same argv twice, then leak check in one process):

```
call1 exit=0 call2 exit=0 stdout_identical=True stderr_identical=True
H4b call1 (--waive syn-refusal): not_evaluated=1 waived=1 total=2      exit=0
H4c call2 (no args, same proc):  not_evaluated=1 total=2               exit=1
```

## Additional arms (strengthen H2/H3 and give C2 its discriminators)

- **Prefix collision, decisive:** with members `syn-ref` *and* `syn-refusal` present,
  `--waive syn-ref` → `not_evaluated=2 waived=1`, `CENSUS_NOT_EVALUATED … syn-refusal`,
  exit 1. A `startswith`/fnmatch implementation would have given `waived=2`, exit 0. Exact-set
  membership is the observed rule.
- **Spaces:** real census names contain spaces (`test-snapshot harness`). `--waive test-snapshot`
  → warning + exit 1; `--waive "test-snapshot harness"` and `--waive="test-snapshot harness"`
  → `waived=1`, exit 0.
- **Parsing equivalence:** `--waive NAME` ≡ `--waive=NAME`; duplicate `--waive NAME NAME` →
  `waived=1` (set semantics, not a counter bump); unrelated positional args ignored.
- **Partial waiver:** two not-evaluated members, one waived → `not_evaluated=2 waived=1`, exit 1,
  the unwaived name printed. Waiving both → `waived=2`, exit 0.
- **Refusal branch is live on all three paths** (`s10d` grounding): refusal marker, budget
  timeout (budget patched to 1 s for the arm, restored), and spawn `OSError`
  (`/nonexistent/binary-xyz` → `refused … spawn error [Errno 2]`) each yield
  `refused […]`, `not_evaluated++`, `fail=0`, exit 1 unwaived; each is waivable by exact name
  → exit 0, `waived=1`.
- **`total` is derived**, not hard-coded (`s5t` grounding): observed `total=1/2/3` for
  1/2/3-member tables; real table length is 22 (12 tier A + 10 tier B, `probe-identity.out`).

## Divergences / hazards

- None between the frozen C2 predicate sentence and observed behaviour. The docstring's
  "exact member name", "a waiver never covers a fail", "waived token only when a waiver was
  used", and "not-evaluated member is never a pass" all held on every arm.
- One *reading* hazard for the C2 boundary author: `waived=` sits **between** `not_evaluated=`
  and `total=` (`not_evaluated=1 waived=1 total=2`). A fixture that greps
  `not_evaluated=(\d+) total=` finds nothing on waived runs and may mis-score a shim as
  compliant. Recommend the boundary cases assert the exact three-token grammar.
- Second hazard: the unused-waiver warning goes to **stderr** and does not itself change the
  exit; a shim could satisfy "fail-waiver fixture nonzero" only because `fail=1` drives the
  exit, not because of the warning. The boundary's fail-waiver fixture should therefore check
  `fail=1` on the verdict line, not the warning text alone.

## What a refutation of each would have meant for C2

- **H1 refuted (as frozen):** the C2 target "a waiver covers an evaluated failing member
  (that fixture must exit nonzero)" would be false on the landed bytes and the
  `s6w-waiver-swallows-failure` shim (exit 0 on the refused fixture) would be
  indistinguishable from the real tool — `killed=5 survivors=0` unreachable.
- **H2 refuted (as frozen):** the boundary would owe wildcard/prefix fixtures and the census's
  `--waive` contract sentence would be misstated; a single `--waive test-snapshot` would
  silence `test-snapshot harness`, collapsing the not-evaluated accounting.
- **H3 confirmed:** the `not_evaluated=<n> waived=<w>` double-token is a sound discriminator
  against `s3-cosmetic-not-evaluated`-class shims (a waived member dropping out of the count).
- **H4 confirmed:** a module-scope cached verdict is detectable by a double-call arm
  (`s8r-second-call-silent`), so the boundary can kill that shim reproducibly.

## Confidence

High for H1–H4 and the extra arms: the probe drives the lane's own `main()` on byte-identical
bytes; every verdict is read off the tool's printed contract line and its return code, not off
prose. Confidence in "the boundary tool will kill the five shims" is **not** claimed — that
tool did not exist at probe time.

## Could not verify

- Real 22-member census run (host verdict table): out of scope for this seat (22 subprocesses;
  scout's item), and it would only add host state, not waiver semantics.
- `tools/census-waiver-boundary.py` itself: absent at `b43e71a8` and at probe time; its
  `BOUNDARY cases=7 killed=5 survivors=0` line, its seven cases and the five shims
  (`/fast/scratch/hyaku/kama-r71/l1/shims`) were not executed.
- Real member names with parentheses (`gate-registry-check selftest (lane-tip arm)`) were not
  passed through `--waive`; only synthetic space-bearing names were exercised.

## Receipts

Written (no lane file edited, no service started, no git mutation):

- `.ufo/waves/round-71/w1/LAB01WaiverProbe/probe.md` — full write-up with verbatim outputs.
- `.ufo/waves/round-71/w1/LAB01WaiverProbe/probe-run.out` — H1–H4 run.
- `.ufo/waves/round-71/w1/LAB01WaiverProbe/probe-extra.out` — parsing equivalence + discriminators.
- `.ufo/waves/round-71/w1/LAB01WaiverProbe/probe-extra2.out` — prefix collision, space names.
- `.ufo/waves/round-71/w1/LAB01WaiverProbe/probe-extra3.out` — spawn-error and timeout refusal paths.
- `.ufo/waves/round-71/w1/LAB01WaiverProbe/probe-identity.out` — real `MEMBERS` census (22 = 12 A + 10 B).
- `.ufo/waves/round-71/w1/LAB01WaiverProbe/probe_harness.py`, `probe_extra.py` — harnesses.
- `.ufo/waves/round-71/w1/LAB01WaiverProbe/census-probe.copy.py` — the byte-identical copy
  (sha256 `44bebd67…b245919`).
