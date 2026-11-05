# CR01DoNothingControl — do-nothing control sizing (kama round-86, wave w3)

Scope: frozen plan `plans/round-86-claims.md` (base `3ff23da3f291ce8abf7bf5c54f9abacec67e3e8d`,
freeze `c07e1f909414aafb2d8de5605a81fd3bd4e3550e`), frozen counter `.ufo/waves/round-86/count.py`
(sha256 `75b91e7048b4378877f228053b5bc4f72782ac4e2cb5a367ef02878e9eb2a2ad`, unchanged
`c07e1f90..bafae7af`), attacked tip `bafae7afb41843564ac2468d28beb8e0bb98e8e6`.
Host Linux 7.2.11-arch1-1 x86_64, Python 3.14.8. All runs on a `git clone file://…/kama-shokunin`
at the tip (`git rev-parse --show-toplevel` asserted = scratch clone); the lane was only read.
No tool was installed; nothing was needed.
Receipts: `.ufo/waves/round-86/w3/out/CR01DoNothingControl/` (`NN-*.out`, stubs, `00-drive.sh`,
`22-fixtures.txt`).

Verdict in one line: **all three before/no-work controls are real, reproducible executions; C1 and
C3 targets are not met by a do-nothing tree, C2's target is met by a do-nothing tree plus one
`print` line; the counter's `--rev` is unbound to instrument bytes for all three legs; the limit is
disclosed but the terminal record's own C2 evidence is not reproducible from committed bytes.**

## 1. (a) Are the frozen before/no-work controls real executions at the declared base?

| Claim | committed receipt | replay |
|---|---|---|
| C1 | `.ufo/waves/round-86/measured/before/c1.out` | `01-c1-before-replay.out` — **byte-identical** (summary + 3 findings) |
| C2 | `.../before/c2.out` | `02-c2-before-replay.out` — **byte-identical** (8 lines) |
| C3 | `.../before/c3.out` | `03-c3-before-replay.out` — identical except the abbreviated `--rev` string in the stderr line (`3ff23da3` vs full hex) |

Command replayed: `python3 .ufo/waves/round-86/count.py <leg> --repo <clone> --rev 3ff23da3 --work <scratch>`.
Commit order (base 15:21, freeze 21:44) also places the before receipts before the after receipts.
They are not promises or post-hoc replays of the *after* state.

Limit on (a): every before run was executed by the **freeze instrument**, which does not exist at the
base revision. The redness of C1/C2's before receipt is therefore a property of worktree instrument
bytes as much as of base bytes (§3). C3's before receipt is an honest presence refusal (`exit=2`,
absent file) but it measures no behaviour of the claimed capability — it is a presence gate.

## 2. (b) Cheapest do-nothing tree, scored with the frozen counter

**C1 — target not met by the do-nothing tree, but met by the record edit alone.**
Base tree: `RENDERED_CELLS facts=3 mismatches=3 gate=0 closure=0 disposition=0` exit1 (`01`).
Minimum satisfying tree: base tree + **only SCORECARD.md lines 6 and 18** replaced by the tip's lines
(`git commit-tree` fixture `f8f19f18a6d0c86d8110d5fca620db2ab30c66ae`) graded by the **freeze**
instrument → `RENDERED_CELLS facts=3 mismatches=0 gate=1 closure=1 disposition=1` exit0 (`08`).
The same freeze instrument grades the repaired tip green (`07`). Therefore the frozen target does not
test any round-86 instrument change; the instrument work (newest-path clause, `blob_at`, container
fences, backtick-info) is graded only by `--selftest`/the mutant driver, not by the claim's target
line. The claim is not void — the plan states the work *is* the record repair — but its
before→after pair cannot distinguish the freeze instrument from the delivered one, and the "append
dated corrections" half of the work is unmeasured by it.

**C2 — target met by a do-nothing tree plus one print line.**
Base tree: `DEBT_MUTANT_OWNERS mutants=5 killed=3 escaped=2 ... arms=unknown owners=3/5` exit1 (`02`).
Base tree + **one inserted line**
`print(f"APPEND_DEBT_SELFTEST_ARMS arms={len(cases)} expected=34 fail_lines={fail}")` — no
`EXPECTED_ARMS` constant, no `len(cases) == EXPECTED_ARMS` return assertion (fixture
`50d4c20d5ed151613d3b44afdf8de5ccac93482e`) → the **exact target line** `mutants=5 killed=5 escaped=0
invalid=0 arms=34 cardinality=ok owners=5/5` exit0 (`10`).
The record's claimed work ("add `EXPECTED_ARMS` and the ARMS line … and assert the declared arm
population") is thus half-unmeasured: the ARMS **print** is load-bearing; the in-tool **assertion**
is not. The instrument change *is* load-bearing — the freeze instrument on the repaired tip prints
`killed=4 escaped=1` (M6 escapes), exit1 (`09`).

**C3 — target unreachable without an instrument.**
Base tree: `could-not-evaluate: no tools/round86-pin-origin.py at 3ff23da3` exit2 (`03`). But base
tree + a five-line stub at `tools/round86-pin-origin.py` (fixture
`b3b2b9a2979746c363ba4360a5e3990aa53d81bb`) → target line exit0 (`16`). The target distinguishes
"a file that prints the line and exits 0" from "no file"; it cannot distinguish that stub from the
delivered instrument except through the delivered instrument's `--selftest`.

## 3. (c) `--rev` semantics — two green-at-base receipts

`count.py:47` is `command = [sys.executable, str(pathlib.Path(args.repo).resolve() / script)] + [...]`:
the instrument is executed from the **worktree**, never from `--rev`; only `REQUIRES_AT_REV`
(c3) consults the revision, and only as `git cat-file -e <rev>:<path>` (presence).

Tampered-worktree demonstrations (stub sha256: c1 `0614533…`, c2 `5c35bea…`, c3 `b044655…`;
`11-tamper-preamble.out`):

| id | command | output |
|---|---|---|
| T1 | `count.py c1 --repo . --rev 3ff23da3` | `RENDERED_CELLS facts=3 mismatches=0 …` exit0 (`12`) — **green at base** |
| T2 | `count.py c2 --repo . --rev 3ff23da3` | `DEBT_MUTANT_OWNERS mutants=5 killed=5 … arms=34 …` exit0 (`13`) — **green at base** |
| T3 | `count.py c3 --repo . --rev bafae7af` | `PIN_ORIGIN rows=5 verified=5 …` exit0, zero network (`14`) |
| T4 | `count.py c3 --repo . --rev 3ff23da3` | `could-not-evaluate: no tools/round86-pin-origin.py at 3ff23da3` exit2 (`15`) — presence gate only |
| T5 | `count.py c3 --rev <base+stub fixture>` | `PIN_ORIGIN rows=5 verified=5 …` exit0 (`16`) |

T1/T2 are the requested two green-at-base receipts. They also mean the **before** receipts are
forgeable in the same way: a red stub at base produces the same "red at base" claim.

## 4. Disclosure sufficiency — disclosed, but the claims are not bound

The record discloses the limit concretely: SCORECARD §Round 86 "**Disclosed limits**", with committed
w2 receipts `w2/out/CR01SizingControl/{c1,c2,c3}-tamper-green-at-*.out`, and `Planned (round 87)`
item 2 names the fix. That is honest and specific — sufficient **as disclosure**.

It is not sufficient to **bind** the claims:
- the gate's `worktree-landing` arm checks only `SCORECARD.md, LOG.md, PROVINCE.md, SKILL.md,
  corpus/SOURCES.md` (`tools/round67-worktree-landing-check.py:42-48`) — the executed round-86
  instrument bytes are not covered, and the round-86 instruments are not gate arms (disclosed);
- the terminal receipts (`d05f6d01:.ufo/.../terminal/commands.json`) record `leg`, `rev`, `exit` and
  no digest of the executed instrument;
- the record's own C2 evidence already contains a line no committed instrument can print (§5), which
  is exactly what an unbound `--rev` allows.

The mitigation sentence "the final measurement is run on a clean tree whose worktree bytes equal the
graded revision's" is an assertion at the measurement instant; nothing in the record measures it for
the bytes that matter.

## 5. Record's own numbers against committed bytes

| claim in the record | committed bytes | verdict |
|---|---|---|
| `corpus/lessons/round-86.md:59` "7/7 source mutants … `mutants=7 killed=7`" | driver declares 10 mutants; receipt `.ufo/.../after/c1-mutants.out` prints `mutants=10 killed=10 escaped=0`; SCORECARD says "10 source mutants"; my rerun 10/10 (`19`) | **stale — 7 must be 10** |
| `after/c2.out` tail `… APPEND_DEBT_SELFTEST pass=34 fail=0 arms=34` | no committed instrument (tip, `c5d71b7a`, or freeze) prints `arms=34` on the pristine line; all print `pass=34 fail=0` (`21`) | **not reproducible from committed bytes** |
| SCORECARD "selftest 17/0 at the terminal tree (11/0 at the freeze)" | 17/0 and 11/0 (`18`, before receipt) | ✓ |
| SCORECARD "selftest 13/0" / "7/0"; C1 "10 source mutants" | 13/0, 7/0, mutants 10/10 (`18`,`19`) | ✓ |
| SOURCES "317→319 rows"; append-only "15 rows" | 319 rows at tip; 15 added rows base..tip | ✓ |
| "counter is frozen before data and is not amended" | no diff `c07e1f90..bafae7af` on `count.py` | ✓ |

Note: the lane record has moved past the assigned tip (`d05f6d01`, `ec541687`, `0f8a0980`,
`239a8f39`, `84e6f457`); all findings above are against `bafae7af` bytes, as instructed.

## 6. Is any target reachable by editing the record rather than the instrument?

- C1 **yes**: two SCORECARD lines, freeze instrument (`08`). The claim's target is a record-consistency
  assertion; the instrument predates the work.
- C2 **no by record edit**, **yes by one tool `print` line** (`10`).
- C3 **no by record edit**; the register/anchors are inputs but an anchor rewritten to equal upstream
  still requires the fetch (or a guess), so no cheap record-only path — only the stub-at-path path.

## 7. Impacted axes

calibration (C1 record-cell binding; C2 evidence integrity), operability (C2 mutant instrument),
freshness (C3 origin line). No axis harm is claimed beyond the items above.

## 8. Smallest safe correction

1. Bind executed bytes in `count.py`: run `git show <rev>:tools/round86-*.py` to a temp file (or
   compare the worktree sha256 with the rev blob and refuse on mismatch) — one function, no claim text
   change; this closes T1/T2/T3 and makes the before receipts genuine rev measurements.
2. Record the instrument sha256 in `terminal/commands.json` (or add the three instruments to the
   landing arm's path set) so "clean tree" is measured, not asserted.
3. Regenerate `after/c2.out` at the tip (one-line difference) and correct `round-86.md` 7/7 → 10/10.
4. If the `EXPECTED_ARMS` in-tool assertion is claimed work, add a mutant that removes it (M7) so a
   do-nothing tree cannot pass (`10`); otherwise drop it from the C2 work list.
