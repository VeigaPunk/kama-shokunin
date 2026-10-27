# X05ControlSeparation — round-56 control separation (C1 vs C2)

Axes named: **operability** (C1) and **calibration** (C2). Seat is advisory; no claim,
predicate, counter, target, kill rule or preregistration was changed. No tool installs.

Question for this seat: run C1 and C2 controls independently, and show that each outcome
is invariant to the other gate's surfaces (and to that gate's own green/red state).

## Frozen identities checked first

```
$ sha256sum tools/round56-replay-code-audit.py tools/round56-prereg-check.py
fc3d4b63a3020cf37e6f4080e25c9d693a8b177c4f84cae6688b2e445444ff6f  tools/round56-replay-code-audit.py
c7b0d787f348691bbc057114b455545f5abfb0c70ec497e1ad695591f1489853  tools/round56-prereg-check.py
```

Both match `preregistration.json` (`claims.C1.counter_sha256`, `claims.C2.counter_sha256`).
Worktree vs freeze blobs (`git show efc6b3ec:<path>`), all four surfaces:

```
tools/round56-replay-code-audit.py   worktree=fc3d4b63… SAME
tools/round56-prereg-check.py        worktree=c7b0d787… SAME
tools/round56-env-leg-test.py        worktree=ec7a2519… SAME   (digest NOT pinned in prereg; see D2)
tools/round56-env-leg-battery.py     worktree=79b19596… SAME
```
Receipt: `receipts/counters-worktree-vs-freeze.out`, `receipts/c1-digests.out`.

All runs used `TMPDIR=/fast/scratch/hyaku/kama-r56/X05ControlSeparation`,
`PYTHONDONTWRITEBYTECODE=1` (lane `tools/__pycache__` untouched), and a single clone at
`/fast/scratch/hyaku/kama-r56/X05ControlSeparation/clone/lane` whose
`rev-parse --show-toplevel` prints that same clone path.

## A. C1 run standalone (env leg, live child)

Leg form: `python3 tools/round56-env-leg-test.py --counter <C> --expect <E>`.
The harness starts `sleep 5` with `LD_AUDIT=/usr/lib/libexpat.so.1` in its environment and
calls the counter's `env_leg(pid, probs)`; exit is 0 iff the observed `ld_audit=` equals `--expect`.

| counter | `--expect` | observed | exit |
|---|---|---|---|
| `tools/round56-replay-code-audit.py` (frozen) | detected | `ld_audit=detected problems=['env: server environment carries LD_AUDIT']` | 0 |
| `tools/round54-replay-code-audit.py` (red baseline) | missed | `ld_audit=missed problems=[]` | 0 |
| one-line mutant (delete `LD_AUDIT` from `BAD_ENV`) | detected | `ld_audit=missed problems=[]` | **1** |
| same mutant | missed | `ld_audit=missed problems=[]` | 0 |

Receipts: `receipts/c1-round56-detected.out`, `receipts/c1-base54-missed.out`,
`receipts/c1-mutant.diff`, `receipts/c1-mutant.sha256` (a3faaf6e…), `receipts/c1-mutant-expect-detected.out`,
`receipts/c1-mutant-expect-missed.out`. The mutant diff is exactly one line:

```diff
-BAD_ENV = ("LD_PRELOAD", "DYLD_INSERT_LIBRARIES", "LD_AUDIT")
+BAD_ENV = ("LD_PRELOAD", "DYLD_INSERT_LIBRARIES")
```

C1's frozen target reproduces: base misses (exit 0, it cannot see the variable), round-56
detects (exit 0), and substituting the mutant into the *expected-detected* slot makes that
assertion fail (exit 1) — the kill fires. The stderr line
`ld.so: object '/usr/lib/libexpat.so.1' cannot be loaded as audit interface: undefined symbol: la_version; ignored.`
appears in every leg and is irrelevant to the leg: detection is of the *variable name* in
`/proc/<pid>/environ`, which `strace` confirms (`openat("/proc/<pid>/environ", O_RDONLY)`),
matching the prereg's stated limit.

## B. C2 run standalone (roster fidelity at a committed tip)

Gate form: `python3 tools/round56-prereg-check.py --repo <clone> --tip <sha>`.

```
--tip e10b6d39af450e8d652be9ac2986768b531fe13f
tip=e10b6d39af450e8d652be9ac2986768b531fe13f
present=0 roster_match=0 kills=0 controls=0 met=False      exit=1
--tip efc6b3ec6fb6ea308c15855e9b8b62856f4255b7
tip=efc6b3ec6fb6ea308c15855e9b8b62856f4255b7
present=1 roster_match=1 kills=1 controls=2 met=True       exit=0
```

Receipts: `receipts/c2-base-tip.out`, `receipts/c2-freeze-tip.out`. C2's frozen control pair
reproduces exactly (red at the round-55 tip, green at the freeze tip).

## C. Separation, direction 1 — C1 invariant to every C2 state

Three C2 states, C1 legs re-run unchanged:

| C2 surface state | round-56 counter | base-54 counter | mutant @expect=detected |
|---|---|---|---|
| intact lane (C2 green) | detected exit=0 | missed exit=0 | missed exit=1 |
| island: no `preregistration.json`, no `round56-prereg-check.py`, no battery | detected exit=0 | missed exit=0 | missed exit=1 |
| island: bogus `{"battery":{"roster":{}}}` prereg + non-Python stub gate | detected exit=0 | missed exit=0 | missed exit=1 |

Receipts: `receipts/c1-isolated-no-c2-surface.out`, `receipts/c1-island2-empty-proof.out`
(empty find output proving zero C2 files in the island), `receipts/c1-with-corrupt-c2-surface.out`.

Runtime confirmation with `strace -f -qq -e trace=openat,open,execve`:

```
C1 run opens of any C2 surface (preregistration.json / round56-prereg-check.py / battery): 0
```

Receipt: `receipts/c1-strace-summary.out` (`NONE — 0 opens of any C2 surface`). Statically
consistent: `round56-env-leg-test.py` imports only `argparse, importlib.util, os, subprocess, time`,
and the counter mentions `preregistration.json` only in its module docstring.

## D. Separation, direction 2 — C2 invariant to every C1 state, still discriminating

At the freeze tip in the clone, all three C1 files (`round56-env-leg-test.py`,
`round56-replay-code-audit.py`, `round54-replay-code-audit.py`) were deleted and committed
(`a0db6371`), then a one-field roster mutation `kill -> control` was committed on top
(`c815b82b`):

| clone tip | C1 files | present | roster_match | kills | controls | met | exit |
|---|---|---|---|---|---|---|---|
| `e10b6d39` (base) | present | 0 | 0 | 0 | 0 | False | 1 |
| `efc6b3ec` (freeze) | present | 1 | 1 | 1 | 2 | True | 0 |
| `a0db6371` (C1 deleted) | **absent** | 1 | 1 | 1 | 2 | **True** | 0 |
| `c815b82b` (C1 deleted + one-field roster mutation) | absent | 1 | 0 | 1 | 2 | **False** | 1 |

Receipts: `receipts/c2-no-c1-surfaces.out`, `receipts/c2-roster-mutation.out`,
`receipts/c2-roster-mutation.diff` / `.diffstat` (1 insertion, 1 deletion), and
`receipts/c2-strace-summary.out`:

```
C2 run opens of any C1 surface (round56-env-leg-test.py / *replay-code-audit.py): 0
```

Because the mutation was committed *after* the C1 files were already deleted, the red
result is produced in a tree where no C1 surface exists at all: C2 both ignores C1 and
still discriminates on its own one-field mutation. The frozen kill rule's "one-field
designation mutation remains green" clause does not fire.

Aggregate matrix: `receipts/independence-matrix.out`.

## Findings, risks and defects (advisory)

- **D1 (observation, C2 scope):** `round56-prereg-check.py` computes `kills`/`controls` from
  the *prereg* roster while `roster_match` compares the *battery* AST to that roster; `met`
  ANDs them. A coordinated two-surface edit that changes both consistently would stay green.
  This does not fire any frozen clause (the prereg is frozen pre-data and the kill rule names a
  one-field mutation), but C2 grades roster fidelity, not mutant design quality — consistent
  with the prereg `limits`.
- **D2 (defect, unpinned digest):** `claims.C1.counter_sha256` names the pair
  "`round56-env-leg-test.py` + `round56-replay-code-audit.py`" but stores one digest, which is
  the counter's. `round56-env-leg-test.py` (ec7a2519…) is reproducibly the freeze blob but is
  not pinned anywhere. Proposed fix for the next round: add `env_leg_test_sha256` to the
  prereg and assert it beside the counter digest.
- **D3 (defect, unenforced kill clause):** C2's kill rule includes "if the counter sha256
  differs from the frozen digest", but the checker imports no hashing module and evaluates no
  digest; the clause is verified only out-of-band (this seat's `sha256sum`, §Frozen identities).
  Proposed fix: have the checker read `claims.C1.counter_sha256` and compare it with
  `sha256(git show tip:tools/round56-replay-code-audit.py)`. Note the coupling trade-off: that
  turns C2's verdict on a C1 artifact, so if separation is to be preserved the digest check
  should stay a separate one-line assertion outside the roster gate.
- **D4 (operability, lane-read-only conflict):** `tools/round56-env-leg-battery.py` hardcodes
  `LANE=/home/vgpnk/Projects/shokunin/kama-shokunin` and writes its receipts into the lane's
  `.ufo/waves/round-56/measured/`, so a seat inside the read-only lane cannot execute it as
  committed. This seat reproduced its three legs individually with the same expectation
  semantics and receipts under `receipts/`; the legs agree with the retained
  `.ufo/waves/round-56/measured/*.out`. Proposed fix: `--lane`/`--out` arguments.
- **Reading note on the C1 kill wording:** the committed battery runs the mutant with
  `expected="missed"` (so it goes red if the mutation is *ineffective* and the mutant still
  detects). The C1 target sentence — "so the battery's expected-detected assertion fails" — is
  the substitution reading, shown here as mutant `--expect detected` → exit 1. Both readings
  are exercised; both are red for the mutant.

## Scope / cleanliness

- Wrote only `.ufo/waves/round-56/w1/out/X05ControlSeparation.md` and
  `.ufo/waves/round-56/w1/out/X05ControlSeparation/receipts/*`; all transient state lived in
  `/fast/scratch/hyaku/kama-r56/X05ControlSeparation` (removed before yielding).
- Lane tracked files untouched by this seat. `SCORECARD.md` was already modified in the lane by
  a concurrent round-56 writer (mtime 13:07, round-56 authority banner) — not this seat, and
  left alone. No `git add/commit/reset` was run in the lane; the two commits `a0db6371` /
  `c815b82b` exist only in the scratch clone.
- Checks *not* run here: full `round56-replay-code-audit.py` replay legs (need the ~75 MB model
  and the release archive), and the committed battery wrapper itself (D4). Only the env leg of
  C1 was exercised, as the C1 target specifies.
