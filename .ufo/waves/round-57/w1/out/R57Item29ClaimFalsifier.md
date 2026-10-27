# R57Item29ClaimFalsifier — C1 no-op control falsification (sentinel)

Seat: `round57/ClaimFalsifier/29`, sentinel, axes calibration + operability. Independent scratch only
(`/fast/scratch/hyaku/kama-r57/R57Item29ClaimFalsifier/`, removed after receipts were copied).
No shared file, source tree, registry, SCORECARD, lesson or sibling repo was written. No commits,
pushes or jj/git mutations were issued in the lane; the only git mutations were `git init`/`commit`
inside the scratch fixture after asserting `git rev-parse --show-toplevel` equalled that fixture.
No tool install or update was needed or performed.

Claim numbering note (not resolved here, as instructed): the dispatch paragraph orders C1=calibration
count / C2=operability binding, while `controls/freeze-amendment.txt` and this seat's prompt order
C1=round56-prereg-check no-op (operability) / C2=round42-selfdesc-reconcile stale count (calibration).
This seat measured the **C1 no-op control and predicate** named in its own prompt and in the amendment.

## Verdict

**Severity: high (claim-level falsification, not a lane outage).** The frozen defect is real, but the
frozen C1 predicate is *not* met by the measured repair: a no-op battery that declares the matching
roster and executes none of its entries still returns `met=True`, exit 0.

| Claim element | Frozen predicate | Independent measurement | Result |
|---|---|---|---|
| Defect exists | the frozen checker declares `met=True` for a matching roster literal without executing battery entries | frozen checker `c7b0d787…` at `b89bdab2` on the round-56 no-op fixture (`v1`): `present=1 roster_match=1 kills=1 controls=2 met=True`, exit 0 | **CONFIRMED** |
| Repair closes it | "the measured checker rejects a no-op that declares the matching roster **but executes none**, while the genuine battery roster remains accepted" | repair checker `dee6f92…` rejects `v1` (`met=False`, exit 1) and accepts the genuine battery (`met=True`, exit 0), but **accepts** `v3`, `v6`, `v7` (`met=True`, exit 0) — three no-ops that execute zero entries | **FALSIFIED** (the repair is a partial fix; the predicate's "executes none" clause is not measured) |
| Secondary precision | (not stated) | a behaviour-preserving rewrite of the genuine battery to keyword labels is rejected (`v5`: `met=False`, exit 1) | false negative |

## Evidence

### Instruments (hashed, pinned, never taken from a moving worktree)

| id | source | sha256 | note |
|---|---|---|---|
| frozen | `b89bdab2cc114735ec5d331c6c610134258f7864:tools/round56-prereg-check.py` | `c7b0d787f348691bbc057114b455545f5abfb0c70ec497e1ad695591f1489853` | equals the `counter_sha256` frozen in `.ufo/waves/round-56/preregistration.json` §claims.C2. This is the round-57 freeze base (`controls/freeze.txt`). |
| repair | `7b74e2f2515a6f598918488fa5144658ff29925f` ("round-57: bind prereg roster to executed calls"), unchanged at tip `8640e34c` | `dee6f922d0d93b10512f9a799b94f36a1e0f080404a525e08121a223b2e90ced` | the measured round-57 counter. |

Both were copied to the wave path and run from there; the lane working tree was only read with
`git show`. The round-56 preregistration and battery are byte-identical between `b89bdab2` and the
tip (`report.json` → `battery_and_prereg_at_base_head` both `true`), so the fixture's inputs are not
contaminated by later commits.

### Fixture cells

Each variant is the exact file committed as `tools/round56-env-leg-battery.py` at the stated fixture
tip, with the genuine round-56 preregistration; both checkers were run against every tip. Full
machine-readable results: `.ufo/waves/round-57/measured/r57item29/report.json`.

| variant | what it does when executed | frozen | repair | receipt |
|---|---|---|---|---|
| `genuine` | the real round-56 battery (3 subprocess `run()` calls) | `met=True` exit 0 | `met=True` exit 0 | `receipts/genuine.*.out` |
| `v1_roster_only` | roster literal + `main(): return 0` (the round-56 no-op) | `met=True` exit 0 | `met=False` exit 1 | `receipts/v1_roster_only.*.out` |
| `v2_declare_print` | roster literal + a print, no entries | `met=True` exit 0 | `met=False` exit 1 | `receipts/v2_declare_print.*.out` |
| **`v3_dead_calls`** | roster literal; three `run("…")` calls inside `if False:` in `main`; `main` returns 0 — **executes zero entries** | `met=True` exit 0 | **`met=True` exit 0** | `receipts/v3_dead_calls.repair.out` |
| `v4_roster_plus_kill_call` | two of three labels declared dead | `met=True` exit 0 | `met=False` exit 1 | `receipts/v4_roster_plus_kill_call.*.out` |
| `v5_keyword_identical` | the genuine battery, labels moved to `run(label=…)` keywords | `met=True` exit 0 | `met=False` exit 1 | `receipts/v5_keyword_identical.*.out` |
| **`v6_crash_before_calls`** | `main()` raises `RuntimeError` before any `run()` — cannot execute at all | `met=True` exit 0 | **`met=True` exit 0** | `receipts/v6_crash_before_calls.repair.out` |
| **`v7_outside_main`** | roster literal; the three `run()` calls in a module-level `if False:`; `main` returns 0 | `met=True` exit 0 | **`met=True` exit 0** | `receipts/v7_outside_main.repair.out` |

Exact decisive output (repair checker, `v3`):

```
$ python3 checkers/repair-check.py --repo fixture --tip 187f97f78550bc37be17e36aaa06a34fbc7b1ab2 \
      --out receipts/v3_dead_calls.repair.out
tip=187f97f78550bc37be17e36aaa06a34fbc7b1ab2
present=1 roster_match=1 kills=1 controls=2 met=True
exit=0
```

The same cell rerun inside the harness produced identical bytes (`report.json` → `determinism`).
Variant sources are preserved at `.ufo/waves/round-57/measured/r57item29/variants/*.py`; the driver is
`measured/r57item29/harness.py`.

### What the repair actually measures

`7b74e2f2:tools/round56-prereg-check.py:61-76`:

```
invoked = set()
for node in ast.walk(tree):                       # whole module, not main()
    if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
        continue
    if node.func.id in ("run", "assert_mutant_breaks_detection") and node.args:
        label = node.args[0]
        if isinstance(label, ast.Constant) and isinstance(label.value, str):
            invoked.add(label.value)
expected = {name for name, spec in roster.items() …}
executed = expected <= invoked
…
met = match and executed and kills == 1 and controls == 2
```

The battery file is never imported or run: the counter only does `git show` on two blobs, `json.loads`
the preregistration and `ast.parse` the battery. `executed` is therefore a **lexical declaration**
test over every reachable-and-unreachable `Call` node in the module. It cannot distinguish "calls the
entry" from "mentions the entry in dead code", and it accepts calls outside `main`, although
`corpus/lessons/round-57.md` states the binding is "to calls in the battery's `main`".

## Exploit path

1. Keep the genuine preregistration (its roster is what the counter compares against — unchanged).
2. Commit a battery whose entire content is the matching `ROSTER` literal, a stub `run()`, and three
   `run("…")` calls under `if False:` (or after an unconditional `raise`). `main()` returns 0; the file
   executes none of the roster entries, and need not even be runnable (`v6`).
3. The counter's `ast.walk` harvests the three labels from the dead nodes, `executed=True`, `met=True`,
   exit 0. Four lines of dead code are enough; no execution, no receipts, no `LD_AUDIT` probe.
4. Result: a no-op harness satisfies the counter, which is exactly the condition the C1 predicate says
   must be rejected and the condition round-56's outside closure routed for repair
   (`corpus/lessons/round-56-verifier-spotcheck.md:44-45`: "a roster literal/no-op harness must fail").

## Impact

- **Calibration:** the round-57 lesson's language "so a no-op harness cannot satisfy the counter"
  (`corpus/lessons/round-57.md` §Claims C1) is false as implemented. The routed round-56 defect is
  only partially addressed: the specific `main(): return 0` fixture is now red, a slightly stronger
  no-op is green. Crediting C1 as closing the executed-entry binding would be fabricated readiness.
- **Operability:** in both directions the counter is wrong. It greens a battery that cannot execute
  (`v6`), and it reds a genuine battery that was refactored to keyword labels (`v5`). The `executed`
  name overstates what is checked.
- **Cross-round provenance (advisory):** the repair commit changes the blob whose sha256
  `c7b0d787…` is the frozen `counter_sha256` of round-56's C2. Any later re-evaluation of round-56's
  frozen C2 kill rule ("counter sha256 differs from the frozen digest") now trips on this file. Round
  56 is closed; this is recorded so the round-57 delta is not mistaken for tampering.
- One corroborating receipt already in the wave: `measured/noop-c1.out` (sibling run, tip `8caa23a2`)
  reports the *plain* no-op now `met=False`, exit 1 — consistent with `v1` here. It does not cover
  `v3`/`v6`/`v7`.

## Smallest remediation (advisory only — this seat has no remediation scope and edited nothing)

The predicate as frozen cannot be met by a lexical check. Either:

1. **Make the predicate lexical, stated honestly.** Keep `ast.walk`, rename `executed` to
   `declared`, and restate C1 as "declares the roster and names each entry in a call expression";
   then stop claiming a no-op harness cannot satisfy the counter. Cheap, but it concedes the
   round-56 routed defect and should not be presented as an executed-entry binding.
2. **Make the counter observe execution (recommended, still small).** Run the battery (or a driver)
   at the tip in the fixture repo and require, per roster label, an observed receipt/exit: the
   battery already writes `OUT/<label>.out` with `exit=` lines, so the check is "for every expected
   label, the receipt exists at the tip's run and its exit/field matches `expected`". This rejects
   `v3`, `v6`, `v7` and `v1`, and accepts `v5` (the keyword refactor executes identically).
3. If a runtime run is out of scope for this round, at minimum add constant-folding reachability
   (drop `If` with a constant-false test; drop statements after `raise`/`return`/`break`/`continue`),
   scope the walk to the `main` `FunctionDef`, read labels from `args` **or** `keywords`, and add
   `v3`/`v6`/`v7` as negative controls in `measured/`. That is hardening, not a proof of execution.

## Non-author source spot-check — S515

- Source: `https://git-scm.com/docs/git-config#Documentation/git-config.txt-GITCONFIGCOUNT`,
  section `GIT_CONFIG_COUNT` (anchor `Documentation/git-config.txt-GITCONFIGCOUNT` present).
- Fetched live this round: 2026-10-27, `curl` HTTP 200, 830,605 bytes
  (sha256 `706b1566467e9cd8c6cdda853a5fc82118a48fde3119777d18cefc014bcd3d5a`).
- Located quote, 18 words: "all environment pairs GIT_CONFIG_KEY_<n> and GIT_CONFIG_VALUE_<n> up to
  that number will be added to the process's runtime configuration".
- Matches `corpus/SOURCES.md:268` (S515) and `corpus/lessons/round-56.md:18`; the live page renders a
  typographic apostrophe in "process’s", the registry uses ASCII — a rendering difference, not a
  textual one. Page version markers on the fetched page include `2.56.0`, consistent with the recorded
  anchor. Verdict: the S515 quote is locatable, verbatim, and ≤25 words.

## Admit/reject decision spot-check (advise only — lane authors hold the decision)

- **S515 admit** (`corpus/SOURCES.md:268`, status `mined`): **supportable**, on the re-opened quote
  above. It is a correction row superseding S511's omitted revision marker, and its `used-by` stays
  `corpus/lessons/round-56.md`; the narrow runtime-injection claim is what the quote states.
- **Caution, not a verdict:** the same live page continues "These environment variables will override
  values in configuration files, but will be overridden by any explicit options passed via `git -c`."
  That precedence sentence is real but is *not* in S515's located quote; do not extend S515's
  `used-by` claim to precedence ordering without a separate anchor.
- **Unaddressed round-56 outside defect:** the round-56 non-author spot-check disagreed with the S513
  reject (`corpus/lessons/round-56-verifier-spotcheck.md:55`) and routed it for a lesson correction.
  `corpus/lessons/round-57.md` contains no S513 row. This is an outstanding lesson-addressing defect,
  reported here rather than fixed (no shared writes).

## Round-56 outside defects vs the round-57 lesson

| Routed defect (round-56 outside closure) | Addressed in `corpus/lessons/round-57.md`? |
|---|---|
| Bind executed battery entries; "a roster literal/no-op harness must fail" | **Partially — and overstated.** The lesson claims AST call-site binding; `v3`/`v6`/`v7` show a no-op still passes. |
| Resolve MISSION.md vs prompt/config/SCORECARD axis authority via operator/L0 | **Not addressed.** The lesson states operability+calibration without recording the conflict; the wave instructs seats not to resolve it. |
| Revisit S513 rejection rationale / record the outside disagreement | **Not addressed.** No S513 row in the lesson. |
| Inherited append-only audit exit 1 and invalid `declared_at`/SCORECARD bindings | **Not addressed in the lesson.** Not re-measured by this seat (out of its surface). |

## Assimilation

None. `considerthese/2026-10-26.md` proposal 3 (the counter-shortcut tally; its round-48 promotion is
`tools/shortcut-tally.py`, v2) was opened this round as instructed. This round fixes one concrete
counter no-op defect and falsifies its predicate; it does not implement or run the multi-round tally,
so proposal 3 remains unimplemented by round 57.

## Verification

All measurements are commands run from the scratch dir against a scratch fixture repo (`git init` +
one commit per variant; toplevel asserted for every git mutation). No lane gate, test suite, build or
formatter was run. `python3 harness.py` reproduces the whole matrix; per-cell commands are
`python3 checkers/{frozen,repair}-check.py --repo fixture --tip <variant tip> --out <receipt>`. The
harness is deterministic for the shared variants across three separate runs (matrix identical each
time; only fixture commit ids differ, since each run recreates the repo). Environment: Python 3.14.8,
git 2.56.0, curl 8.23.0.

Receipts: `.ufo/waves/round-57/measured/r57item29/` (`report.json`, `harness.py`, `variants/`,
`checkers/`, `receipts/`, `sha256sums.txt`). Scratch `/fast/scratch/hyaku/kama-r57/R57Item29ClaimFalsifier/`
was copied first and then removed.

Report: .ufo/waves/round-57/w1/out/R57Item29ClaimFalsifier.md
