# demo.md — EX02CensusVerdict, round 70, claim C2

Candidate: `round65-host-census.py` in this directory.
Candidate sha256: `a82cad11d777aa4b34d8ae96b66250d52853ed880d4c2eaa510ea8b4bf37dc68`
Base sha256: `463899182af0d154859e86da785051760e4bc314f5489659ea32424c18374513`
(equal to tracked `tools/round65-host-census.py` and to
`measured/before/round65-host-census-base.py` at wave start).

All commands were executed 2026-11-03 on plazir27 (Linux 7.2.11-arch1-1,
python3 3.14.8). Except where noted, cwd = `/home/vgpnk/Projects/shokunin/kama-shokunin`
(the lane root). The candidate bytes live in this out dir until the L1 lands
them, so the census-importing commands below load the candidate and patch
`LANE` to the lane root — the same substitution the frozen control makes when
it replaces `MEMBERS`. Once the bytes are landed at
`tools/round65-host-census.py`, the same commands reproduce verbatim with the
landed path and no `LANE` patch (the script derives `LANE` from its own
location).

---

## 1. Frozen control on the candidate bytes

Command:

```console
$ python3 .ufo/waves/round-70/controls/refused-member-control.py \
    .ufo/waves/round-70/w1/out/EX02CensusVerdict/round65-host-census.py
$ echo CONTROL_EXIT=$?
```

Output (verbatim):

```text
{"refused_fixture": ["pass [A] synthetic-pass", "refused [A] synthetic-refused: fail-closed refusal: synthetic NTFS stand-in (control) (marker 'invalid path')", "HOST_CENSUS pass=1 fail=0 not_evaluated=1 waived=0 total=2 tierA_fail=0 tierB_fail=0", "HOST_CENSUS exit 1: 1 not-evaluated member(s) without a waiver: synthetic-refused"], "allpass_fixture": ["pass [A] synthetic-pass", "pass [A] synthetic-pass-2", "HOST_CENSUS pass=2 fail=0 not_evaluated=0 waived=0 total=2 tierA_fail=0 tierB_fail=0"]}
REFUSED_MEMBER_CONTROL refused_fixture_exit=1 allpass_fixture_exit=0
CONTROL_EXIT=0
```

Required reading: `refused_fixture_exit=1`, `allpass_fixture_exit=0`, and the
refused fixture's verdict line carries `not_evaluated=1`. (Base bytes scored
`refused_fixture_exit=0 allpass_fixture_exit=0`, control exit 1 — receipt
`measured/before/refused-member-control-old.out`.)

---

## 2. Real census on this host, candidate bytes, C1 still red

Command (cwd = lane root; loads the candidate, patches `LANE` to the lane
root, runs `main()`; members execute exactly as registered):

```console
$ python3 - <<'PY'
import contextlib, importlib.util, io, sys
from pathlib import Path
CANDIDATE = ".ufo/waves/round-70/w1/out/EX02CensusVerdict/round65-host-census.py"
spec = importlib.util.spec_from_file_location("census_candidate", CANDIDATE)
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
mod.LANE = Path.cwd()  # bytes live in out/ until landed; members run from the lane root
sys.argv = ["round65-host-census.py"]
buf, err = io.StringIO(), io.StringIO()
with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
    code = mod.main()
print(buf.getvalue(), end="")
if err.getvalue():
    print("--- stderr ---"); print(err.getvalue(), end="")
print(f"EXIT={code}")
PY
```

Output (verbatim; ~40 s):

```text
pass [A] test-snapshot harness
pass [A] pin-watch selftest
pass [A] report-landing-audit selftest
pass [A] sources-append-only selftest
pass [A] citation-provenance selftest
pass [A] capability-repertoire-audit selftest
pass [A] instrument-agreement selftest
FAIL [A] round42-selfdesc-reconcile selftest: exit=1 tail='SELFDESC_SELFTEST newest=69 planted_stale=57 ok:closure_ptr=1,mismatches=9 stale_ptr:closure_ptr=0,mismatches=10 stale_both:closure_ptr=0,mismatches=10 stale_incl:closure_ptr=0,mismatches=10 no_ptr:closure_ptr=0,mismatches=10 pass=4 fail=1'
pass [A] gate-registry-check selftest (lane-tip arm)
pass [A] worktree-landing-check selftest
pass [A] receipt-pointer-audit selftest
pass [A] newest-closure-counter selftest
pass [B] digest-ledger selftest
pass [B] hexrun-census selftest
pass [B] kama-ollama-evidence selftest
pass [B] gguf-identity selftest
pass [B] manifest-crosscheck selftest
pass [B] error-verdict-census selftest
pass [B] seat-report-immutability selftest
pass [B] prereg-time-check selftest
pass [B] release-recheck selftest
pass [B] append-only-audit selftest
HOST_CENSUS pass=21 fail=1 not_evaluated=0 waived=0 total=22 tierA_fail=1 tierB_fail=0
EXIT=1
```

While C1 is still red: `tierA_fail=1` (the reconciler selftest arm), exit 1.
The member ran and failed, so it is a `fail`, not `not_evaluated` — its real
semantics are intact.

---

## 3. Same real census with `--waive "round42-selfdesc-reconcile selftest"`

Same command as §2 with one line changed:
`sys.argv = ["round65-host-census.py", "--waive", "round42-selfdesc-reconcile selftest"]`.

Output (verbatim; member lines identical to §2 and omitted here except the
verdict, plus stderr):

```text
HOST_CENSUS pass=21 fail=1 not_evaluated=0 waived=0 total=22 tierA_fail=1 tierB_fail=0
--- stderr ---
warning: --waive 'round42-selfdesc-reconcile selftest' unused: member was evaluated (fail); a waiver covers only not-evaluated members
EXIT=1
```

The waiver is refused with a named warning: a member that ran and failed
stays a `fail`; waivers cover only not-evaluated members. Exit stays 1.

---

## 4. Waiver path done right: refused member + exact-name `--waive` → exit 0

Command (cwd = lane root; synthetic refused fixture, same shape as the
frozen control's, plus an explicit waiver):

```console
$ python3 - <<'PY'
import contextlib, importlib.util, io, sys
CANDIDATE = ".ufo/waves/round-70/w1/out/EX02CensusVerdict/round65-host-census.py"
FIXTURE = [
    ("A", "synthetic-pass",
     ["bash", "-c", "echo 'RESULT pass=30 fail=0'"],
     "RESULT pass=30 fail=0", []),
    ("A", "synthetic-refused",
     ["bash", "-c", "echo 'invalid path': the lane holds a tracked path NTFS cannot check out"],
     "NEVER-PRINTED",
     [("invalid path", "fail-closed refusal: synthetic NTFS stand-in (control)")]),
]
spec = importlib.util.spec_from_file_location("census_candidate", CANDIDATE)
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
mod.MEMBERS = FIXTURE
sys.argv = ["round65-host-census.py", "--waive", "synthetic-refused"]
buf, err = io.StringIO(), io.StringIO()
with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
    code = mod.main()
print(buf.getvalue(), end="")
if err.getvalue():
    print("--- stderr ---"); print(err.getvalue(), end="")
print(f"EXIT={code}")
PY
```

Output (verbatim):

```text
pass [A] synthetic-pass
refused [A] synthetic-refused: fail-closed refusal: synthetic NTFS stand-in (control) (marker 'invalid path') [waived]
HOST_CENSUS pass=1 fail=0 not_evaluated=1 waived=1 total=2 tierA_fail=0 tierB_fail=0
EXIT=0
```

The waived member keeps its reason on its own line (`[waived]`), the verdict
keeps `not_evaluated=1 waived=1` visible, and — and only because every
not-evaluated member is explicitly waived and no member failed — exit is 0.

---

## 5. Kill rule: an always-exit-1 shim FAILS the all-pass fixture

Command:

```console
$ S=$(mktemp -d /fast/scratch/hyaku/kama-r70/EX02CensusVerdict/fx.XXXX) \
  && trap 'rm -rf -- "$S"' EXIT \
  && printf '%s\n' '#!/usr/bin/env python3' \
     '"""always-exit-1 shim - kill-rule probe: must FAIL the all-pass fixture."""' \
     '' 'def main():' '    return 1' > "$S/always1.py" \
  && python3 .ufo/waves/round-70/controls/refused-member-control.py "$S/always1.py"; \
  echo CONTROL_EXIT=$?
```

Output (verbatim):

```text
{"refused_fixture": [], "allpass_fixture": []}
REFUSED_MEMBER_CONTROL refused_fixture_exit=1 allpass_fixture_exit=1
CONTROL_EXIT=1
```

The shim "passes" the refused half (exit 1) but scores
`allpass_fixture_exit=1`, so the frozen counter pair (refused=1, allpass=0)
is not met and the control exits 1. An always-exit-1 census is rejected; the
target is the pair, never the exit alone.

---

## 6. Bonus control: the base bytes' own failure mode

Base bytes on the refused fixture score `refused_fixture_exit=0
allpass_fixture_exit=0` (fail-open) — already recorded at
`measured/before/refused-member-control-old.out`; not re-run for this demo.
