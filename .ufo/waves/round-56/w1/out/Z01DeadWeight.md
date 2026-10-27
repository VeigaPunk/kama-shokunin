# Z01DeadWeight — round-56 unnecessary code and duplicated logic

Seat: `Z01DeadWeight` (round 56, kama, wave 1). Axes: operability, calibration.
Scope: the four round-56 tools — `tools/round56-replay-code-audit.py` (frozen C1 counter),
`tools/round56-env-leg-test.py` (frozen C1 driver), `tools/round56-env-leg-battery.py`
(C1 roster battery), `tools/round56-prereg-check.py` (frozen C2 counter) — plus the
`tools/round54-replay-code-audit.py` baseline they use.

Verdict: **0 deletions applied.** 4 deletions are verified dead (AST proof plus
execution-equivalence proof) but every one of them lands in bytes bound by a frozen digest
or by already-recorded blob evidence, and the lane is read-only for this seat, so they are
forward proposals for a re-freeze round. 1 further unreachable-path candidate is found and
deliberately **not** proposed. 4 duplication surfaces are load-bearing and must never be
deleted; the largest of them (99.3 % of the round-56 counter is a byte copy of the round-54
counter) looks exactly like the stale leftover a simplifier would delete, and deleting it
destroys C1's red baseline. No claim predicate, counter, target, kill rule or preregistration
byte was changed.

## 1. Method and its limit

- Lane tree read-only for this seat, so every candidate was exercised on copies under
  `/fast/scratch/hyaku/kama-r56/Z01DeadWeight/`; the lane's tracked tree was byte-identical
  before and after (`git status --porcelain` shows only the pre-existing seat artifacts and
  the untracked `round-56/measured/` dir; the source mtimes of all four tools are unchanged
  at 13:00–13:01, and `tools/__pycache__/round56-replay-code-audit.cpython-314.pyc` is
  unchanged at 13:03 from the L1 run).
- The `lsp` device named by the simplifier role is **not mounted in this session**
  (`read xd://lsp` → `No such tool: xd://lsp`). Caller/definition proof is therefore done
  with Python's own `ast` scope analysis — a semantic name-binding pass over the module,
  not text grep. `grep` was used only to locate line numbers, never as the absence proof.
- Frozen digests re-measured and equal to the preregistration:
  `round56-replay-code-audit.py` `fc3d4b63…444ff6f` = prereg `claims.C1.counter_sha256`;
  `round56-prereg-check.py` `c7b0d787…f1489853` = prereg `claims.C2.counter_sha256`
  (`receipts/hashes.out`).

## 2. Verified deletion candidates (forward only — every one is hash-bound)

| # | file:lines | what is deleted | proof it is dead | behaviour-equivalence proof |
|---|---|---|---|---|
| A1 | `tools/round56-prereg-check.py:10` | `import sys` | `ast` unused-import pass: `sys` never appears as a `Name` or attribute base | slim variant run below |
| A2 | `tools/round56-prereg-check.py:12` | `BASE = "e10b6d39…13f"` | `ast` zero-`Load` module constant; `--tip` is the only input the checker uses | slim variant run below |
| A3 | `tools/round56-env-leg-battery.py:5` | `import os` | `ast` unused-import pass: `os` never appears | slim battery run below |
| A4 | `tools/round56-env-leg-battery.py:27` | `expected_result = f"ld_audit={expected}"` | dead local in `run()`: bound, never loaded in the function | slim battery run below |

Why A2 matters rather than being cosmetic: the same base commit now has three authorities —
`preregistration.json.base`, `round56-replay-code-audit.py:131 BASE`, and this unused copy.
Only two of them are read; the third can rot silently after the next re-freeze and be cited
by a later seat as "the base". Deleting it removes a stale authority without touching the
C2 predicate (the predicate is roster-vs-preregistration, not base).

Equivalence evidence (`receipts/runs/`):

```
# runs/prereg-check-nobase.py = the frozen checker minus A1 and A2
$ python3 runs/prereg-check-nobase.py --repo <lane> --tip e10b6d39af450e8d652be9ac2986768b531fe13f
tip=e10b6d39af450e8d652be9ac2986768b531fe13f
present=0 roster_match=0 kills=0 controls=0 met=False
exit=1
$ python3 runs/prereg-check-nobase.py --repo <lane> --tip efc6b3ec6fb6ea308c15855e9b8b62856f4255b7
tip=efc6b3ec6fb6ea308c15855e9b8b62856f4255b7
present=1 roster_match=1 kills=1 controls=2 met=True
exit=0
```

Both match the committed receipts `controls/base-c2.out` (`present=0 … met=False`, exit 1)
and `measured/build-c2.out` (`present=1 roster_match=1 kills=1 controls=2 met=True`) exactly,
field for field. The C2 predicate is therefore preserved by A1+A2.

```
# runs/battery-slim.py = the battery minus A3 and A4 (OUT/scratch retargeted to this seat's
# scratch so the committed measured/ receipts are never rewritten; that retarget does not
# touch run()'s ok computation)
$ python3 runs/battery-slim.py
base-old-counter: ld_audit=missed exit=0 -> pass
round56-counter: ld_audit=detected exit=0 -> pass
m-drop-ldaudit: ld_audit=missed exit=0 -> pass
battery_exit=0
```

The three receipts it wrote are byte-identical to the committed
`.ufo/waves/round-56/measured/{base-c1,build-c1,m-drop-ldaudit}.out` after normalising only
the pid token (`receipts/runs/receipt-equivalence.out`: `identical-after-pid-normalization`
for all three). The C1 predicate — miss / detect / mutant-miss — is preserved by A3+A4.

Variant digests, should a later round adopt them: `prereg-check` (A1+A2 removed)
`8158f8bf557695e2fcdf31e734041092ac67d3c70ac922f5a200d9ac5d39e53c`; `battery` (A3+A4 removed,
OUT retargeted) `52f36427def5041aec8e4a965caecfd3c634d4e9fda246a825fb90e7e4df0268`.
**Adopting A1/A2 changes the frozen C2 counter digest `c7b0d787…`; adopting A3/A4 changes a
blob whose sha256 `79b19596…` is already recorded as evidence by X02/X03/X05/S01/S02.** They
cannot be applied after scoring starts, and any future adoption must re-freeze and re-record
those hashes; the diffs are kept in `receipts/prereg-check-deletion.diff` and
`receipts/battery-deletion.diff`.

## 3. Found dead but deliberately not proposed

| # | file:lines | why it is dead | why it stays |
|---|---|---|---|
| B1 | `round56-replay-code-audit.py:468` `code_observe(pid, tree, arc, probs, collect=False, own=None)` | both live call sites (lines 710, 712) pass `collect=True, own=got` as literals, so the `collect=False` and `own is None` paths never execute | inside the frozen C1 counter (`fc3d4b63…`); the parameters are the documented two-pass and memfd-admission contract. Deleting 2 default tokens would change the measured digest for zero predicate gain |
| B2 | `round56-env-leg-test.py:26` `keys is not None and any("LD_AUDIT" in x for x in probs)` | `env_leg` returns `None` only when `/proc/<pid>/environ` is unreadable (`round56-replay-code-audit.py:431-434`), and in that case `probs` cannot contain `LD_AUDIT`, so the guard is logically implied by `any(...)` | the test file is named in the prereg C1 `counter` field and in X05's worktree-vs-freeze receipt (`ec7a2519…`); a logically redundant guard on the falsification driver is cheaper than the re-freeze |
| B3 | `round56-env-leg-battery.py:30` `p.returncode == 0 and fields.get("ld_audit") == expected` | the driver returns 0 iff `result == expect` and prints the field before returning, so the exit test is implied by the field test | removing it narrows the falsification surface if the driver is ever edited; the battery bytes are already recorded evidence. Keep the belt and the braces |

## 4. Duplicated logic that is load-bearing — do not delete

| # | duplication | evidence | what deletion would destroy |
|---|---|---|---|
| C1 | `tools/round54-replay-code-audit.py` ↔ `tools/round56-replay-code-audit.py`: 966 of 973 lines identical (99.3 %), 3 changed blocks, 7 changed lines | `receipts/static-census.out` | the round-54 file **is** the C1 red baseline — `round56-env-leg-battery.py:13 OLD`, and its own docstring says it was re-frozen as the round-55 counter. It is the only thing that makes `base-old-counter: ld_audit=missed` a control. A round-54 file name on a live control is a naming trap, not dead weight |
| C2 | `round56-env-leg-battery.py:15-19 ROSTER` duplicates `preregistration.json.battery.roster` | `round56-prereg-check.py:55-61` `ast.literal_eval`s exactly that assignment and compares it to the prereg roster | C2 itself. This is the one zero-`Load` constant in the family that must stay: the checker reads it through the AST, not through the runtime namespace |
| C3 | `clean_env`/`git` exist in both the counter (`:164`, `:176`) and the checker (`:17`, `:24`), similarity 0.55 | `receipts/static-census.out` | both frozen digests plus the counters' independence (X05's separation receipt). Hoisting ~15 lines into a shared module makes the C2 checker's bytes depend on the C1 counter family — one edit would then move both measured counters at once. Duplication is the cheaper contract here |
| C4 | ~40 `def git(...)` helpers across `tools/` | `grep -n "def git(" tools/*.py` | out of round-56 scope; a fleet-wide convention, and a shared helper would couple every frozen counter to one file. Not a round-56 finding |

## 5. Stale names inside the frozen counter's own docstring (defects, not deletions)

The counter's preamble (lines 3-6) says round 56 classifies `LD_AUDIT`; three older blocks of
the same docstring still say the opposite or name the wrong base. Two authorities disagreeing
inside one frozen file is exactly the kind of weight this seat exists to surface, but the fix
is a text replacement in hash-bound bytes, so it is recorded, not applied.

| line | current text | contradicts |
|---|---|---|
| `round56-replay-code-audit.py:44` | `base       3a600d2f729828419aaea34cc402c8b0d20fb720 (round-54 lane tip; round-55 start)` | `BASE` at `:131` = `e10b6d39…`, which is what `newrow_leg` (`:864-874`) actually diffs rows against |
| `:14` | `environment (no LD_PRELOAD);` | `BAD_ENV` at `:147` now includes `LD_AUDIT` |
| `:64` | `LD_PRELOAD (or DYLD_INSERT_LIBRARIES) among them is a problem (K1Cheat);` | ditto — the `(v)` facet sentence omits `LD_AUDIT` |
| `:80` | `PREDICATE … the server carries no LD_PRELOAD;` | ditto; a reader auditing C1 from the counter's own PREDICATE line would conclude `LD_AUDIT` is out of scope |

Proposed (post-round) replacement text is one line each, no code path touched; adopting them
changes `fc3d4b63…` and therefore needs a re-freeze, exactly like A1/A2.

## 6. Adjacent defect (not dead weight, 1 line to fix later)

`round56-env-leg-test.py:19 exec_module` compiles the frozen counter as an import, which
writes `tools/__pycache__/round56-replay-code-audit.cpython-314.pyc` into the "read-only"
lane tree (present, 13:03 — created by the L1 battery run, gitignored, so tracked state stays
clean). Consequence: the bytecode a battery leg executes is a derived artifact validated only
by source size+mtime. Fix when the file is next unfrozen: `sys.dont_write_bytecode = True`
before `exec_module`, or run the harness with `PYTHONDONTWRITEBYTECODE=1` (this seat's runs
used the latter and wrote no bytecode).

## 7. Preserved contract

- C1 predicate, target, kill rule and counter digest `fc3d4b63…444ff6f`: unchanged.
- C2 predicate, target, kill rule and counter digest `c7b0d787…f1489853`: unchanged.
- Preregistration roster, battery ROSTER, driver expectation semantics: unchanged.
- Lane tree: byte-identical; no `git add/commit/reset`; nothing written outside
  `.ufo/waves/round-56/w1/out/Z01DeadWeight/` and `/fast/scratch/hyaku/kama-r56/Z01DeadWeight/`
  (scratch removed before yielding).
- Scratch `/fast/scratch/hyaku/kama-r56/l1-battery` was **not** used or written; the slim
  battery ran with its own `TMPDIR` and output dir.

## 8. Tradeoff and stop condition

Stop point: the next deletion that would help is C1 — collapsing the round-54 copy into an
import — and it directly harms the calibration axis by removing C1's red baseline, so the
frontier ends here. The four verified deletions (A1-A4) buy a stale-authority removal and
three dead tokens/lines; they cost a re-freeze of the C2 counter digest and a re-record of
the battery blob hash, which is why they are proposals and not edits.

Receipts: `receipts/{hashes.out, static-census.out, prereg-check-deletion.diff,
battery-deletion.diff, runs/{prereg-base.out, prereg-freeze.out, battery-slim.out,
receipt-equivalence.out}}`.
