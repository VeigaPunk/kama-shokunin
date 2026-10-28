# RV03C2CounterCode — review of tools/round63-c2-counter.py at 03a6a1d8

Seat: reviewer (leaf, advisory). Item: line-by-line review of the C2 counter.
Tip under test: 03a6a1d850902a66a13dfad33f89cf3a8b759a09. Counter read from the tip blob
(`git show`), never the working tree. Evidence: `.ufo/waves/round-63/w1/out/RV03C2CounterCode/`
(baseline run, reconciler run, repro outputs and scripts, five mutant CLI runs and patches).

## Baseline (unmutated counter, CLI, scratch `--work`)

```
population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=8 sens_selftest=4/4 controls_rejected=12/12 errors=0 met=False
```

`met=False` comes only from `selfdesc_mismatches=8`, the value the item and freeze say the base
tip must show (the SCORECARD head is re-derived by the L1 after measurement). Every other gate
is green. The reconciler at the tip prints `r41=1 banner=1 planned=2 retired=1 saturation=1
caps=1 receipts=0 readme=0 province=1 rel=0 mismatches=8` (`out/.../selfdesc.out`).

## Method and tools

- Read all 555 lines (`cat -n` from the tip blob); checked each item in the review scope.
- Nine reproduction probes against a copy of the counter (`out/.../repro/repro_a..f.py`).
  Controls were run with bound execution pre-seeded (`_EXEC_CACHE`), so no live tools fired.
- Five single-check mutants in scratch clones, committed in the clone with the seat identity,
  scored by the CLI from the clone path against the clone's own tip (`out/.../mutants/*.patch`).
- Installed nothing. Used python3, git, pgrep, bash. Lane not written; no lane commits.
- Lane `tools/__pycache__/` exists (gitignored, pre-dates this seat); not created or touched here.
- No `/tmp` or `tempfile` use in the counter (`grep`): all scratch is under `--work`.

## Findings (ordered by severity)

### F1 — High: `checkout_tip` reuses any existing `work/tip` (counter.py:480-482)
`checkout_tip` returns `work/tip` whenever the directory exists, without checking the tip.
A second run with the same `--work` and a different `--tip` reads the new tip's SCORECARD and
registry blobs but executes the previous tip's bound tools. A pre-existing empty or partially
extracted `tip/` is returned silently; every bound tool is then "dead" and the run fails with
no hint of why.
Reproduction (`repro_a.out` R1): archive A (`print('A')`), then B, same work dir:
`tree for B says: print('A') (expected B)`; an empty pre-existing `tip/` is returned as-is.
Fix: resolve the tip with `git rev-parse --verify <tip>^{commit}` and key the tree by that SHA,
or always re-extract to a fresh directory.

### F2 — Medium: host-busy acceptance does not bind the refusal to a process (counter.py:352, 363-367)
The branch accepts `host-busy` when rc==2, the alt text is printed, and `pgrep -x llama-server`
is non-empty both before and after the run. It never requires that the same pid appears on both
sides. `pgrep` is host-global, so a llama-server from another seat's live run satisfies either
side. Reproduction (`repro_a.out` R2, `pgrep_foreign` monkeypatched):
`before=[111] after=[222] -> ('host-busy',)` (accepted; disjoint pids). Empty before or after
is correctly `false`. On this host the operator servers (pids 1706355 on 1234 and 242776 on 45669)
were present in the process list during this review, so today the bracket is always non-empty
and adds no evidence about the refusing process. Fix: require `set(before) & set(after)`; this
is non-breaking here because the operator pids persist.
Race note: a foreign process that exits inside the window only makes `after` empty (fail-safe).
The false-positive window is the disjoint-pid case above.

### F3 — Medium: the live sensitivity column is an identity for the shipped verdict functions (counter.py:215-241, 322, 362, 369-370, 532, 536)
`verdict_fn` true implies `pat in out`, `rc==0`, `not dead`, `pat != ''`. `strip_all` removes every
occurrence of `pat`, so the stripped output fails the verdict; changing rc 0 to 1 fails it too.
The same holds for `refusal_fn` (rc 2 flips to 0). Therefore `is_sensitive(...) == verdict(...)`
for every input the live code can produce. Fuzz (`repro_b.out` R3): 400000 cases,
55751 verdict-true, 0 verdict-true-but-insensitive. Consequences:
- `sensitive=12/12` (line 536) and the gate `facts['sensitive'] == facts['bound']` (line 532) cannot
  fail for shipped verdict functions; they guard only future edits of `verdict_fn`.
- Mutant M5 (below) forces `sensitive=True` at line 362; it is behaviorally equivalent and no
  control can kill it. The only effective sensitivity test is `sensitivity_selftest`, which
  exercises `is_sensitive` on planted functions, not the live row.
Fix options: describe the live sensitivity column as structural in the freeze text, or make the
live check perturb an independent artifact (for example, confirm that the pattern is also present
in the tool's own receipt, such as `%S/cc.json` for context-capacity-receipt).

### F4 — Medium: three freeze clauses have no control family; SURVIVED mutants (counter.py:300-302, 171-172, 178-181)
The twelve families (lines 411-463) never delete or alter the run equality (300-302), the newest-round
test (171-172) or the canonical-row prefix test (178-181). Each deletion survives the full
CLI (`controls_rejected=12/12`, see the table). Repro: `repro_d.out` shows M1 accepts a registry
whose `run` column is tampered (`pin-watch` run replaced; unmutated: `run:pin-watch`, mutant: met);
M3 accepts a SCORECARD whose newest canonical list is round 62; `repro_e.out` shows M2 accepts an
altered frozen row prefix (`prefix:pin-watch` unmutated, empty for M2). The freeze clauses are
"binds exactly its manifest run template", "frozen row prefix" and "newest canonical list".
Also: every family rescores cached results (lines 376-382, 402), so `run_bound`,
`is_sensitive` and the host-busy branch are exercised only by the single baseline run.
A fix that adds families changes the frozen count (`EXPECT_FAMILIES`, lines 121 and 528-529),
which is an amendment decision for the L1; this reviewer does not decide it.

### F5 — Low-Medium: the `observed` column check is lenient (counter.py:324-327)
The check is skipped when the field is empty, and it accepts any substring of the pattern or alt.
Repro (`repro_b.out` R5): `observed=blank mismatches=0`, `observed=fragment "45" mismatches=0`;
only the wholly foreign string `FORGED` is caught (mismatches=1). The `observed` control (line 430)
tests only that last case. Fix: require exact equality with `want_obs` and drop the empty skip.

### F6 — Low: `score()` does not enforce sensitivity for the host-busy outcome (counter.py:322)
`(outcome == 'true' and not sensitive)` omits `host-busy`. `main` catches it only through the
aggregate at line 532. Repro (`repro_b.out` R4): a host-busy row with `sensitive=False` gives
`mismatches= 0` while `sensitive= 11 /bound 12`. Fix: add `or (outcome == 'host-busy' and not sensitive)`.

### F7 — Low: two selftest patterns are prefixes only (counter.py:84, 105)
`IA_SELFTEST pass=` and `AOA_SELFTEST pass=` do not bind `fail=`. `verdict_fn('IA_SELFTEST pass=0
fail=3', 0, False, 'IA_SELFTEST pass=')` returns True (`repro/prefix_pattern.out`). The two tools
exit 1 when fail>0 (`tools/instrument-agreement.py:117`, `tools/append-only-audit.py:1481`), so there is
no live false pass today; the row is only as strong as those exit codes. Other selftest rows bind the
full line. Fix: use the full `... pass=N fail=0` form.

### F8 — Low: sensitivity selftest term 4 is a witness that depends on a coincidence (counter.py:265-266)
Term 4 is `is_sensitive('a') and not r62_formula('a')`. It is not a planted verdict function passed to
`is_sensitive`. It passes because `r62_formula` returns False for `'a'`: the replacement token
`__kama_mut__` contains `a`. With pattern `'z'`, `r62_formula` returns True and the term is False
(`repro_f.out` R8). So "4 planted defective verdict functions" is 3 planted functions plus one witness.
Terms 1-3 are good: #1 is rejected by the strip and flip clauses, #2 by the strip clause, #3 by the
rc-flip clause (checked). Fix: replace term 4 with a fourth planted defect that is actually rejected by
`is_sensitive`, or drop the witness and document three.

### F9 — Low: a timed-out bound run leaves its grandchildren alive (counter.py:353-359)
`subprocess.run(..., timeout=900)` kills only the direct child. Repro (`repro_f.out` R7): after
`TimeoutExpired`, a grandchild `sleep 31.7231` was still alive. A timed-out tool that started a
llama-server therefore leaves a foreign llama-server, which the F2 bracket then sees in later runs.
Fix: `start_new_session=True` and `os.killpg` on timeout.

### F10 — Low: `canon-drop` is credited on any canonical-list problem (counter.py:458-462)
The control scores `hit = bool(probs)` and does not check the named failure. Repro (`repro_f.out` R9):
`hit=True` for an unmutated list and for a list with an unrelated prefix defect. `main` withholds all
credit when the baseline fails (lines 526-527), so this affects detail only, not `met`. Fix: name the
expected message.

### F11 — Low: failure paths print no `met=` line (counter.py:337, 354, 469-476, 600s timeout)
`pgrep` missing (337), `bash` launch errors (354), the reconciler timeout (473, 600 s) and `tar`
(487) are uncaught and produce a traceback. `selfdesc_mismatches` (475-476) has identical branches, so
the reconciler exit code is ignored; this is harmless today because the count is parsed from stdout.
Fix: catch these, emit `errors=N met=False`, and drop the dead ternary.

### F12 — Info: the tip is not resolved or printed (counter.py:496, 210, 378, 533-542)
`--tip` is used raw: in `git archive`, in the `TIPREV` substitution (`digest-ledger` and `hexrun-census`
receive a ref name if one is passed), and as the cache key. The one-line output never prints the commit.
Fix: `rev-parse` to a full SHA at entry and print `tip=<sha>`.

### F13 — Info: tautology and parser looseness (counter.py:531, 148-150)
`len(population) == MIN_ROWS` (531) compares two values built from `_MANIFEST`. `canonical_rows`
(148-149) accepts any line containing "canonical list as of round N", not only headings, and keeps the
first of two equal rounds (150). No current defect; worth a comment or a stricter match.

## Checked and correct
- `parse_registry` (185-205): exact header tuple; blank and `#` lines skipped; column-count errors counted.
- `score()` ordering (quote, binding, run, pattern, verdict, host-busy-declared): each rejects and
  `continue`s; the unmutated family hits (12/12) are consistent with those rejections.
- `run_bound` executes only the manifest template (`templates`, lines 345-346), never `row['run']`;
  a row cannot inject a command (the `free` family and M1 confirm the registry side).
- `strip_all` terminates (`pat` non-empty; each pass shortens the text). Empty `pat` is never true.
- Baseline gating (526-527) and the family-count check (528-529) are right: a removed family fails `met`.
- Env allowlist (42, 504-505): PATH, HOME, LANG, LC_ALL; `TMPDIR=scratch`; `git()` strips `GIT_*`.
- Race analysis for the bracket: see F2.

## Mutant verdicts (CLI, verbatim counter lines; `met=False` is the tip's `selfdesc=8`, so kill or survive is read from the controls field)

| mutant | change | verdict |
|---|---|---|
| m1 | delete run-equality, counter.py:300-302 | SURVIVED (`controls_rejected=12/12`; repro_d: tampered run accepted) |
| m2 | delete canonical prefix, counter.py:180-181 | SURVIVED (`controls_rejected=12/12`; repro_e: altered prefix accepted) |
| m3 | delete newest-round, counter.py:171-172 | SURVIVED (`controls_rejected=12/12`; repro_d: round-62 list accepted) |
| m4 | delete observed mismatch, counter.py:325-327 | KILLED (`controls_rejected=11/12`, `control-escape: observed`) |
| m5 | run_bound sensitivity forced True, counter.py:362 | SURVIVED, equivalent under the shipped verdict_fn (F3) |

Verbatim lines:
```
m1: population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=8 sens_selftest=4/4 controls_rejected=12/12 errors=0 met=False
m2: population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=8 sens_selftest=4/4 controls_rejected=12/12 errors=0 met=False
m3: population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=8 sens_selftest=4/4 controls_rejected=12/12 errors=0 met=False
m4: population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=8 sens_selftest=4/4 controls_rejected=11/12 errors=0 met=False
   control-escape: observed {'met': True, 'hit': False, 'tags': []}
m5: population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=8 sens_selftest=4/4 controls_rejected=12/12 errors=0 met=False
```

## Residual risk and verification gaps
- The host-busy race (F2) was reproduced by monkeypatching `pgrep_foreign`; not stress-tested with real
  processes. The real host has persistent operator servers, so the live row was accepted this run.
- The live baseline ran once; the `true` path for context-capacity-receipt was not observed (host-busy won).
- F1 was reproduced through `checkout_tip`, the function `main` calls at line 507; the full `main` was not re-run twice.
- The F3 identity is proved for `verdict_fn` and `refusal_fn` as written; it is not a property of any future edit.
- The reconciler's eight mismatches are other seats' scope; not analysed here.

Tally: 13 findings (1 High, 3 Medium, 9 Low/Info). 5 mutants: 1 KILLED, 4 SURVIVED (3 control gaps, 1 equivalent).
Scratch root removed after receipts were copied.

Counter (unmutated, tip 03a6a1d8):
population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=8 sens_selftest=4/4 controls_rejected=12/12 errors=0 met=False
