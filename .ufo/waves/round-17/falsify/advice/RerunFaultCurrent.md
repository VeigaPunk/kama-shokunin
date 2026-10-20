# RerunFaultCurrent — C1 "after" number rerun (fault-controls current check.py)

VERDICT: confirm — fresh-clone rerun reproduces `.ufo/waves/round-17/runs/fault-controls-current.json` exactly modulo wall time; detected 8 / accepted 0, F0 identity passes, and every F row's `why` names the targeted conjunct, enforced in code, not just narrated.

## What I attacked

C1's after number (claim: current `check.py` grades 0 accepted-bad under F1–F8 while frozen check.py took 3 accepted), the F0 positive control, and the per-F conjunct-naming requirement.

## Findings

1. **Rerun reproduces the frozen after-number.** Command (2) below exited 0 with `detected: 8, accepted: 0` — identical to the frozen run file. A full structural diff excluding `seconds` reported `DIFFS(excl. seconds): NONE — byte-identical modulo seconds`, including every per-run `why`, `check_exit`, and the three digests. Frozen file at `.ufo/waves/round-17/runs/fault-controls-current.json` (`"detected": 8, "accepted": 0`).
2. **Identity pinning holds.** Independently computed `sha256sum` of clone files: `tests/probe-verdicts/check.py` = `ddc3f3cceaee9687de4d6aa29cd4adb72833e08ef0657371dff97cf582fe2099`, `tools/kama-probe.sh` = `36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3` — matching the run JSON's self-reported `check_sha256`/`probe_sha256` and matrix `sha256` `bf9068d8…` with 72 tests. `tests/probe-verdicts/fault-controls.py:714-728` refuses to grade on digest/breadth mismatch ("refusing to grade"), so the staged matrix was pinned.
3. **F0 identity passes and gates the suite.** Rerun `positive_control`: `check_exit: 0`, `detected: true`, why "all 5 rows passed (positive control healthy)" over `ROWS_FULL` (`fault-controls.py:88-94`). Gate confirmed in code: `fault-controls.py:733-741` prints "suite INVALID — positive control F0 failed" and `return 2` when F0 does not pass ("if a check.py cannot PASS the honest probe, the suite is invalid", `fault-controls.py:105-106`).
4. **Every F row names the targeted conjunct, and detection requires it.** Fault table `fault-controls.py:118-198` sets `target` per fault: F1 reason, F2 exit, F3 drift, F4 verdict, F5 served_model, F6 route, F7 error, F8 error; rows per fault match the claim's span (OK/MIS/LOAD trio; F5 adds the DEAD row; F6 stub rows only; F8 all 5 rows × 6 malformed variants incl. non-utf8). Enforcement is real: `classify_run` re-derives each row's failed conjuncts locally (`fault-controls.py:450-480`) and returns not-detected unless "target in fails" — "rows failed but NOT on the targeted … conjunct" (`fault-controls.py:524-537`); docstring: "a row that merely carries an 'error' … can never read as a clean detection of a field fault" (`fault-controls.py:486-489`). In the rerun JSON, each fault's `why` lists `row-shortname:conjuncts` and the target appears in every row: F1 `…:reason` ×3; F2 `…:exit` ×3; F3 `…:drift` ×3; F4 `expect-exact-id:drift,verdict` etc.; F5 `…:served_model` ×3; F6 `…:route` across all 4 per-row runs; F7 `expect-exact-id:drift,error,exit,reason,route,served_model,verdict`; F8 all 30 row-runs show `…,error,…` across 6 variants. `accepted` semantics consistent: `fault-controls.py:796-798` exits 1 iff any fault accepted.
5. **Minor, by-design (not a defect):** detection is target-inclusive, not target-exclusive — e.g. F7's row fails all 7 conjuncts, so an over-eager check that fails everything still counts F7 as detected. The header comment states this is intended ("a row's failure only counts as detection when its failed conjuncts include the target", `fault-controls.py:115-117`). Acceptance threshold remains 0 accepted across F1–F8, so this cannot mask an accepted-bad.

## Commands run (all exit codes recorded)

1. `rm -rf /tmp/KamaR17.RerunFaultCurrent-clone && git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/KamaR17.RerunFaultCurrent-clone && git -C /tmp/KamaR17.RerunFaultCurrent-clone checkout -q 54a29268e2083caa2b1e0d54ee1e7d90961302f3 && git -C /tmp/KamaR17.RerunFaultCurrent-clone rev-parse HEAD` → exit 0, printed `54a29268e2083caa2b1e0d54ee1e7d90961302f3`.
2. `cd /tmp/KamaR17.RerunFaultCurrent-clone && PYTHONDONTWRITEBYTECODE=1 python3 tests/probe-verdicts/fault-controls.py --check tests/probe-verdicts/check.py --json > /tmp/KamaR17.RerunFaultCurrent-rerun.json; echo "exit=$?"` → `exit=0`, `"detected": 8, "accepted": 0`, `seconds: 174.9`.
3. Python structural diff of frozen run JSON vs rerun JSON ignoring `seconds` → exit 0, `DIFFS(excl. seconds): NONE`.
4. `sha256sum /tmp/KamaR17.RerunFaultCurrent-clone/tests/probe-verdicts/check.py /tmp/KamaR17.RerunFaultCurrent-clone/tools/kama-probe.sh` → exit 0, digests as in finding 2.
5. Read-only `git` clone/checkout only in `/tmp`; no lane execution, no `jj`, no lane writes except this Report.

## Limitations

- The run JSON does not record `fault-controls.py`'s own digest; byte-identical-modulo-seconds output implies the frozen run used an equivalent detector at the pinned commit, but the frozen generator's exact identity is [INFERENCE] from output equality.
- One rerun on one machine; nondeterminism beyond `seconds` is excluded only insofar as every other field (incl. 46 per-run `why` strings) matched exactly.
- Wall time differed (rerun 174.9 s vs frozen 59.8 s) — timing only, no bearing on grading.

## Installs

None. No pacman, `uv tool`, or binary installs (host pacman pause respected). No servers started; no ports bound; scratch `/tmp/KamaR17.RerunFaultCurrent-clone` and `/tmp/KamaR17.RerunFaultCurrent-rerun.json` removed.
