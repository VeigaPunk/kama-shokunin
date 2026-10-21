# CritFrozenFairness — round 23 FALSIFY, frozen-arm fairness

Seat: CloseKama22.CritFrozenFairness-2 (critic). Base 245a37f69628c2c6bb29bbf17897d8fb5946c857
(clone /tmp/kama-r23w2/CritFrozenFairness, `git rev-parse HEAD` = base, verified).

## Verdict: PARTIALLY FALSIFIED

The direction of the C1 claim holds: frozen fails at least 18 of 26 fault rows whose
expectation follows from the frozen docstring, or that crash, hang, or run programs.
The "frozen 0/26" evidence is overstated:

- **3 rows (F17, F21, F23) are unfair to frozen.** On each, frozen gives an answer that
  follows its documented contract word for word. It does not crash, hang or run anything.
  Current passes them only because it changed the contract or added a refusal.
- **5 more rows (F06, F13, F16, F24, F26) pin current's specific refusal.** A frozen fix that
  follows the contract, does not crash and runs nothing still fails them (see the patch
  results below). Frozen's own failure on these rows is fair (a traceback or a program run),
  but the expectation shows that current's answer differs, not that it is the only correct one.

Fair accounting: frozen scores 0 out of the 23 fault rows that are fair to it, and 3 rows
should move to `tradeoff`/contract-change. Current's 26/26 includes 3 contract changes and
5 rows tied to its own wording or design.

## Reproduction (my clone, both arms)

`env GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 python3 tests/report-audit/repo-state-grid.py --json`
gave exit 1, which is expected because `--arm frozen` must fail:
- current: faults 26/26, controls 8/8.
- frozen: faults 0/26, controls 8/8.

This matches the L1 claim. The JSON is saved as `out/CritFrozenFairness/grid.json`
(sha256 71b9e9c0…2cdc).

Provenance nit: the goal calls `4fe9339f…` a "blob". `git cat-file -t` reports `commit`.
The grid reads `4fe9339f…:tools/report-landing-audit.py`
(repo-state-grid.py:639-640), so this is harmless but mislabelled.

## Contract used as judge

The frozen docstring (`git show 4fe9339f:tools/report-landing-audit.py`, lines 1-45) has:
- Defect kinds at lines 12-26.
- The errata rule at lines 34-40: "A row is `errata-invalid` when its correction is not a
  lane/fleet commit".
- The exit codes at lines 42-44: exit 2 = "missing/irregular report, unusable git,
  malformed ledger, empty round selection, output failure".

It has no shallow, grafted, sha256, partial-clone, subdirectory, ref-name or timestamp-width
clauses. Those clauses are new in current (current lines 44, 49-55).

The grid defines its own taxonomy (repo-state-grid.py:11-14): `fault` = "repository-local
state must not crash, flip or hijack the verdict", and `tradeoff` = "declared new refusals".

## Unfair rows: frozen follows its contract

### F17-errata-revision-correction (expected exit 1; frozen exit 0)

- Probe (`out/CritFrozenFairness/probe.py`):
  - With correction `HEAD`: frozen exit 0 with `invalid=0`; current exit 1 with `invalid=1`.
  - With the full hash of the commit `HEAD` names: **both exit 0**.
- So the only difference is how the correction is spelled. `HEAD` names a lane commit, so
  frozen's wording ("not a lane/fleet commit") accepts it.
- Current's docstring keeps the **same** wording (current :38-40). The hex-only rule exists
  only as a code comment (current :387-388: "a revision expression such as HEAD or :/text
  is never a correction").
- The row also tests ledger content, not repository-local git state, so it falls outside the
  stated C1 scope.
- Current's rule is a real improvement, because `HEAD` keeps changing and so validates
  anything. But it changes the contract; frozen did not break it.
- Smallest correction: document "correction is a 7..40-hex commit name" in the docstring and
  reclassify F17 as a contract-change (`tradeoff`) row, or move it out of C1.

### F21-nested-subdirectory-lane (expected exit 2; frozen exit 1)

- Frozen exit 1 with `['landed-unresolved','unresolved-full-hash']`. It fails closed: no clean
  verdict, no hidden omission.
- The fixture docstring (grid :502-503) says git "silently discovers upward" and that the
  enclosing history "lacks the omission". Frozen did not turn that into a pass.
- Against the real lane, both arms exit 1 with `['landed-omitted']` (probe).
- Frozen's answer is literally correct: `lc` is no object in the repository git resolved, nor
  in the fleet.
- The cause is the operator's path argument, not repository-local state.
- Counterexample showing the refusal is not a correctness property: a stale top-level clone
  of the lane (taken before `round-1: more`):
  - current `--lane-repo stale` gave rc=0;
  - current `--lane-repo lane` gave rc=1.
  
  Current refuses one way of spelling the wrong repository and still accepts another.
- Smallest correction: reclassify as `tradeoff`.

### F23-promisor-pack-without-config (expected exit 2; frozen exit 1)

- Frozen exit 1 with `['unresolved-full-hash']`.
- The clone's config (probe) has no promisor, partialclone or filter key, and the cited blob
  is absent. The frozen docstring (:12-13) says a 40-hex token "that is no git object in the
  lane or fleet repo" is unresolved. In the repository passed as lane, it is not one.
- Against the origin lane, both arms exit 0.
- No crash, hang or command run.
- Current refuses this row with the same message as T01, `partial clone (promisor pack)`,
  and T01 is graded as a `tradeoff`. The same refusal is counted as a fault win here.
- "Absence is not evidence" (grid :195-196) is a new policy, not a frozen violation.
- Smallest correction: reclassify as `tradeoff` next to T01, or keep it as a fault only with
  an expectation that frozen's contract also implies.

## Over-specified rows: frozen fails fairly, but a contract-faithful fix also fails

Each patched frozen copy changes one thing (diffs in `out/CritFrozenFairness/P*.diff`).
Each was run with `repo-state-grid.py --arm current --current <patched> --case <row>`.

| Row | Patch | Observed | Contract-implied answer |
|---|---|---|---|
| F06 lazy-fetch | P1 adds `--no-lazy-fetch` | exit 1 `['landed-unresolved','unresolved-full-hash']`, exec=0, NOT-MET | exit 1 |
| F13 ref-named abbrev | P2: a found oid must start with the token | exit 1 `['landed-unresolved']`, NOT-MET (controls C01/C02 still met) | exit 1 |
| F24 huge round | P3 `sys.set_int_max_str_digits(0)` | exit 2 "…/kama.md not committed in fleet HEAD", NOT-MET | exit 2 (missing report) |
| F26 huge author time | P3 | exit 0 `[]`, NOT-MET | exit 0 |
| F16 errata bytes | P4: UnicodeDecodeError becomes EvalError "cannot decode" | exit 2, NOT-MET | exit 2 (malformed ledger) |

Notes on each row:

- **F06:** frozen did run `core.sshCommand`, so its failure is fair. But the expectation of
  exit 2 with `partial clone` rejects the minimal fix that runs nothing. This also explains
  why mutant M02 survives in `isolation-mutants.py`: it is "superseded" only because this row
  pins the refusal.
- **F13:** the frozen docstring (:17-19) says a token that is "no commit in either repo" is
  `landed-unresolved`. Exit 2 `names a ref` is current's choice. Reason pin: grid :584.
- **F24:**
  - `--rounds` is a command-line argument, not repository-local git state, so the row is
    outside the C1 claim.
  - The reason pin `could-not-evaluate: internal: ValueError` (grid :589) requires current's
    catch-all handler. A real refusal, such as frozen's "missing report" exit 2, fails it.
- **F26:**
  - Git emits all 5,000 digits of `%at`, and the report's cutoff is 2000.
  - The frozen docstring (:30) says "Lane commits authored after the report are
    `post_report` and not required", so exit 0 follows from the contract.
  - Current's 12-digit cap (current :195) is not in its docstring.
- **F16:** exit 2 follows from "malformed ledger". The row fails only on the wording pin
  `output is not UTF-8` (grid :586).

F02 with P4 also failed the pin. There the pin is defensible: P4's message, "not committed
in fleet HEAD", is false because the report is committed (frozen's `audit_round` wraps
every EvalError that way). It is not counted as over-specified.

## Fair rows (expectation follows the frozen contract, or frozen crashed, hung or ran a program)

- **Tracebacks:** F01, F02, F16, F18, F19, F20, F22, F24, F26 (grid.json).
- **Programs run:** F06 and F09 (exec=1).
- **Hang:** F14 (timeout).
- **Same fixture with the fault setting removed** (probe):
  - F07: frozen exit 0 with `log.follow`, exit 1 without it (expected 1).
  - F08: frozen exit 1 with `log.showRoot=false`, exit 0 without it (expected 0).
  - F12: frozen exit 0 with the shadowing tag, exit 1 without it (expected 1).
  
  On all three, a repository setting changes the verdict, and the expectation equals frozen's
  own baseline answer.
- **F03, F04, F05 (refs/replace):** frozen accepts objects whose hash does not match their
  content. F04's FAKE is "no git object" under frozen :12-13. Fair.
- **F10 shallow, F11 grafts:** frozen exit 0. With the shallow file removed, both arms exit 1
  `['landed-omitted']`, so frozen's 0 is a false clean.
  - `git --no-replace-objects rev-list --count HEAD` on the grafts fixture still prints 1,
    so git has no switch to neutralize grafts, and refusing is a reasonable answer.
  - Fair, although the refusal itself is a new clause.
- **F15 sha256:** frozen exit 1 `landed-omitted` for a commit cited by its full 64-hex name.
  The 40-hex tokenizer cannot read it. A literal reading ("7..40-hex token") arguably
  supports frozen, but the verdict is false in substance. Fair, with a weak caveat.
- **F25:** a forged record gives a false `landed-omitted`. Fair.

## Impacted axes

- Axis 7 (C1 calibration): the evidence is inflated by 3 contract-change rows and 5 rows
  pinned to current's design. The 7→7 "narrow" score is not overturned, because the
  improvement direction survives on the 18 or more fair rows.
- Provenance and identity: the "blob" label for the frozen revision is wrong. F17's rule and
  F26's timestamp cap are undocumented, so current's docstring understates its contract.

## Smallest safe correction

1. Reclassify F17, F21 and F23 as `tradeoff` (or contract-change) rows and report frozen
   against 23 faults.
2. For F06, F13, F24 and F26, accept any exit that follows the contract with no execution or
   traceback. For example, F06 could accept {1 with the expected kinds, 2 with
   `partial clone`}. Alternatively, keep them but label them "current-design pins".
3. Relax the reason pins for F16 and F24 to the exit class.
4. Document the hex-only correction rule and the 12-digit author-time cap in the current
   docstring.

## Not verified

- I did not re-run `isolation-mutants.py`, the selftest or the rounds 10-22 ledger
  (M02 is discussed from the stated claim only).
- I did not check O01, O02 or T01 beyond the grid output: current marked those NOT-MET, as
  expected for `open`/`tradeoff` rows, and frozen T01 was met.
- I did not test git versions other than 2.56.0, or a real shallow or real partial clone
  with objects actually missing.
- I did not check the control rows for fairness beyond observing that both arms met 8/8.

## Installs

None.

## Files written

- This report: `.ufo/waves/round-23/falsify/advice/CritFrozenFairness.md`.
- `.ufo/waves/round-23/falsify/out/CritFrozenFairness/`: `grid.json`, `probe.py`,
  `P1-nolazy.{py,diff}`, `P2-refcheck.{py,diff}`, `P3-intdigits.{py,diff}`,
  `P4-decode.{py,diff}`.
- Scratch outside the lane: `/tmp/kama-r23w2/CritFrozenFairness` (clone),
  `/tmp/kama-r23w2/CritFrozenFairness-frozen.py`, `/tmp/kama-r23w2/CritFrozenFairness-out/`,
  `/tmp/kama-r23w2/crit-ff-*` fixtures.
