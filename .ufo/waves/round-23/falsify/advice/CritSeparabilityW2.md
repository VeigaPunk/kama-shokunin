# CritSeparabilityW2 — causal separability / one-claim framing of round-23 C1

Seat: `CloseKama22.CritSeparabilityW2-2` (critic, leaf). Base
`245a37f69628c2c6bb29bbf17897d8fb5946c857`; clone
`/tmp/kama-r23w2/CritSeparabilityW2`, `git rev-parse HEAD` =
`245a37f69628c2c6bb29bbf17897d8fb5946c857`. git 2.56.0, Python 3.14.8.
Current auditor sha256 `f228f17420134a4a4fb6d1f93b943f78647e7e60882f767e6cb7cba11d6928a7`.

## Verdict: PARTIALLY FALSIFIED (framing), mechanisms hold

The measured numbers reproduce: the current arm meets 26/26 faults and 8/8 controls
with 0 tracebacks, 0 executions and 0 timeouts, and the frozen arm meets 0/26.
NUL record parsing also holds against two forgery attempts (row 8).

The single claim does not. "Repository-local git state must not crash, flip,
hang or run programs" is scored only on calibration, but the 26 faults fall
into four separate causal families. Three of the four outcome types, and at
least four graded rows, are not repository-local state or are not calibration.

One isolation element is mislabelled "defensive-only": `--no-lazy-fetch` is
the element that stops F06's program execution. And the headline "0
tracebacks" is earned by the catch-all alone.

## Findings

### 1. F24 plus the catch-all is a separate claim and outside the declared population

- **Counterexample.** F24 passes `--rounds 999…(5000 digits)`. That is a
  command-line argument, not repository state. Its grid reason pins
  `"could-not-evaluate: internal: ValueError"`
  (`tests/report-audit/repo-state-grid.py:589`), and the CLI parser
  (`tools/report-landing-audit.py:403-414`, `:470`) is unchanged since the
  frozen blob.
- **Evidence (ablation).**
  - X2 is the frozen auditor plus only the catch-all (`main` `:918-924`).
    It meets exactly one fault, `['F24']`, and **tracebacks drop from 9 to 0**.
  - X4 is the current auditor minus the catch-all. It meets 25/26; only
    `F24` fails, with exit 1.
  - The shipped mutant suite agrees: `M24-catch-all` kills only
    `['F24-huge-round-number']`.
- **Consequences.**
  - The C1 headline "0 tracebacks" does not discriminate the isolation
    claim: any exception now leaves as exit 2 without a traceback.
  - Pinning `internal: ValueError` as the passing reason makes a real fix
    *fail* the grid. A real fix would be a bounded `--rounds`/`--report`
    parse raising `EvalError("--rounds: …")`.
  - The same input family is not closed. With `ulimit -v 3000000`:
    - `--rounds 1-99999999` gives rc=2 `internal: MemoryError`.
    - `--rounds 1-999999999999` gives rc=2 `internal: MemoryError`.
    - `--report 9…(5000)=/dev/null` gives rc=2 `internal: ValueError`.

    The memory and time behaviour without a ulimit was not run, to protect
    the host.
- **In-scope twin left ungraded.** A *committed* lane errata row whose round
  field has 5000 digits goes through `parse_errata`'s `int(parts[0])`
  (`:353-356`). Results:

  | Auditor | Exit | Output |
  |---|---|---|
  | Frozen | 1 | Traceback |
  | Current | 2 | `internal: ValueError` |
  | Current minus catch-all | 1 | Traceback |

  So the catch-all is load-bearing for real repository content, yet its
  only graded row is the CLI one.
- **Impacted axes.** Calibration: F24 is credited to C1 but is not
  repository state. Exit-contract totality is a distinct claim.
- **Smallest safe correction.**
  - Drop F24 from C1's 26, or move it and the catch-all to their own claim.
  - Add a committed-errata huge-round row, expecting exit 2 with the reason
    "malformed ledger" (needs a bounded round regex in `parse_errata`) or
    else `internal:`.
  - Stop reporting "0 tracebacks" as isolation evidence.

### 2. A committed-content parsing family is bundled as "repository-local state"

- **Counterexample.** F02, F16, F18, F19, F25 and F26 are caused by
  committed bytes, not by local config, refs or layout:
  - F02: fleet report bytes.
  - F16: errata blob bytes.
  - F18 and F19: commit-message bytes.
  - F25: a `\x1e`/`\x1f` subject.
  - F26: a 5000-digit author timestamp.

  These travel with an ordinary clone.
- **Evidence.**
  - I built the F25 forgery with fsck-clean `git hash-object -w` (rc=0)
    and cloned it with `git clone --no-local file://…`. The clone's local
    config holds only the default `core.*`, `remote.origin.*` and
    `branch.master.*` keys.
  - The frozen auditor then gives rc=1 with
    `UNCORRECTED landed-omitted ffffffffffffffffffffffffffffffffffffffff`,
    a forged round commit injected into the verdict.
  - The current auditor gives rc=0 with `[]`.
  - The fixes are different code elements from the isolation tuple:
    - Strict/surrogateescape decoding: M09/M23 kill F02 and F16; M10 kills
      F18 and F19.
    - NUL record parsing plus a timestamp shape check: X5 (NUL revert only)
      kills exactly F25; M25 kills F26.
  - Commit `e0f0434` ("neutralize repository-local git state") had 23
    faults. F24–F26, the catch-all and NUL parsing arrived together in
    `34b2376`, but the claim text was not re-scoped.
- **Impacted axes.** Same axis (calibration) but a different claim. It
  concerns authored-content integrity: a forged verdict pushed by any lane
  committer. That is not local state.
- **Smallest safe correction.** Split it out as C2 ("committed content
  cannot crash or forge verdicts"), with F02, F16, F18, F19, F25 and F26
  plus the errata huge-round row. C1 keeps the config/ref/layout rows.

### 3. Axis misattribution: "run programs" and "hang" are not calibration outcomes

- **Counterexample.** Calibration is verdict truthfulness. In F06 and F09
  the frozen verdict was already *correct*:
  - **F06.** The frozen auditor gives exit 1 with
    `['landed-unresolved','unresolved-full-hash']`. That is the ground
    truth: `abcdef…abcd` is fabricated and `lc` exists.
  - **F09.** The frozen auditor gives exit 0 with `[]`, which is correct
    for a clean report.

  Their only harm was `executed=True`. F14's harm is a timeout, which
  produces no verdict and so no false verdict.
- **Evidence.** `grid-both.json` frozen rows F06 (`exec`), F09 (`exec`)
  and F14 (`TO`). In current F06 the correct verdict becomes a refusal
  (exit 2), which is an operability cost.
- **Impacted axes.**
  - Safety: F06 and F09. This sits under KQ32 (untrusted-repository use
    is restricted), which the lesson says stays in force.
  - Operability 8: F14, plus F06's new refusal.

  Calibration is credited for all three.
- **Smallest safe correction.** Grade F06, F09 and F14 under
  safety/operability (or as no-harm side conditions), not as calibration
  movement. The calibration-attributable count is at most 26 − 1 (F24)
  − 3 = 22 across both claims, and 16 for C1 after the finding-2 split.

### 4. `--no-lazy-fetch` is not "defensive-only"; the promisor-config refusal is

- **Counterexample.** The lesson
  (`corpus/lessons/round-23.md:79-82`) says `--no-lazy-fetch` is
  "Defensive-only (no grid row needs them, mutant survives)" and the
  promisor refusal "runs first".
- **Evidence (F06/F23/T01 only).**

  | Variant | F06 result | Executed | Met | F23 | T01 |
  |---|---|---|---|---|---|
  | M14: remove `remote.*.promisor`/`extensions.partialclone` refusal | exit 1, correct `['landed-unresolved','unresolved-full-hash']` | False | False | still met (pack refusal) | still exit 2 |
  | M14+M02: also drop `--no-lazy-fetch` | exit 1 | **True** | — | — | — |

  - With M14 alone, F06 is "killed" only because the grid pins exit 2 with
    reason "partial clone". No fault materializes.
  - Adding M02 brings the program execution back.
  - So `--no-lazy-fetch` is the sufficient cause of F06's no-execution.
    The config refusal adds only operability cost, turning a correct
    verdict into exit 2. F23 and T01 are carried by the `.promisor` pack
    refusal (M22).
- **Impacted axes.** Operability: the git ≥ 2.45 floor is paid for a
  load-bearing element, so it is not a free defensive extra. Calibration
  provenance: the mutant kill reflects a pinned design choice, not observed
  harm.
- **Smallest safe correction.** Relabel M02 as load-bearing for F06's
  safety. Treat M14's kill as expectation-pinned, and either justify the
  config refusal with a fixture whose verdict actually flips without it, or
  mark it defensive.

### 5. Overdetermined and duplicate rows inflate the 26

- **F01 depends on no single element.** M03 kills only `F22`, and M10
  kills only `F18`/`F19`. F01 survives both single mutants. Only the double
  mutant M03+M10 fails it (exit 2, `can't decode byte 0xe9`). F01 adds no
  independent evidence over F18 plus F22.
- **M09 and M23** kill the same two rows (F02, F16), so they are one
  element counted twice in "22/24 killed".
- **M21** (newline normalization) kills only control C08. It restores
  frozen text-mode behaviour (no harm), not a fault fix.
- **Correction.** Report the kill table as distinct elements and rows.
  Mark F01 as joint coverage for M03 and M10.

### 6. The NUL-record element has no mutant

- The lesson's M1 fix promises "one mutant per isolation element", but
  `tests/report-audit/isolation-mutants.py:28-71` has none for
  `-z`/`%x00`.
- X5 reverts only the `\x1f`/`\x1e` record parsing and keeps the new
  `{1,12}` timestamp shape check. It meets 25/26 and fails exactly
  `F25-subject-record-injection` (exit 1, `['landed-omitted']`).
- The element is necessary and is graded by F25. Only the mutant suite
  under-reports it.
- **Correction.** Add a single-element mutant equal to X5.

### 7. Minor provenance discrepancy

The lesson's M1 row says the frozen grid had "8 tracebacks". At 245a37f6 I
observe 9: F01, F02, F16, F18, F19, F20, F22, F24 and F26. Presumably the
count dates from before F24–F26 were added [INFERENCE].

### 8. What holds (strongest counterexamples that failed)

- **NUL inside the subject.** A forgery
  `note\0<40f>\0kama-shokunin\0001500\0round-1: forged` needs `--literally`
  (fsck `nulInCommit`). `git log -z` truncates the subject at `note`.
  Both arms give rc=0, `[]`.
- **UTF-16LE through the encoding header.** The same forgery as a UTF-16LE
  body with an `encoding UTF-16LE` header, under the forced
  `i18n.logOutputEncoding=UTF-8`, outputs the subject `n`. It is truncated
  before re-encoding, and the current auditor gives rc=0,
  `round_commits: 1`.

The doc claim "git truncates names and subjects at NUL" held for subjects.

## Commands run (all in `/tmp`, `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1`, per command)

- `python3 tests/report-audit/repo-state-grid.py --json`: rc=1 as designed.
  - Current: 26/26 faults, 8/8 controls, tb=0, exec=0, timeouts=0.
  - Frozen: 0/26 faults, 8/8 controls, tb=9, exec=2, timeouts=1.
- `python3 tests/report-audit/isolation-mutants.py --json`: rc=0, 24
  mutants, 22 killed, survivors `M02-lazy-fetch`, `M20-log-sha-shape`.
  The per-mutant rows are quoted above.
- `repo-state-grid.py --arm current --current <variant>` for each variant:

  | Variant | Faults met | Failing rows |
  |---|---|---|
  | X1 | 24/26 | F25, F26 |
  | X2 | 1/26 (F24 only) | — (tracebacks 0) |
  | X3 | 2/26 (F25, F26) | — |
  | X4 | 25/26 | F24 |
  | X5 | 25/26 | F25 |

  The M14, M14+M02 and M03+M10 results are as quoted in findings 4 and 5.
- Ad-hoc fixtures under `/tmp/kama-r23w2/CritSeparabilityW2-nul.q9yU`
  (NUL and UTF-16 forgery, CLI ranges, errata huge round) and
  `/tmp/kama-r23w2/CritSeparabilityW2-xfer.4qzJ` (F25 forgery through
  `clone --no-local`).

## Not verified

- The git < 2.45 floor: I installed no old git, because pacman is paused.
- Unbounded memory and time for huge `--rounds` ranges without a ulimit.
- Whether F26's `--literally` object survives a clone when
  `transfer.fsckObjects` is set.
- Selftest 50/50 and the rounds 10–22 ledger no-harm check: not rerun.
- Alternates and gitfile (O01/O02) and the sibling tools.
- Which axis the canonical judge assigns: separability is argued from local
  evidence only.

## Tooling

No installs or updates.

## Files written

- `.ufo/waves/round-23/falsify/advice/CritSeparabilityW2.md` (this report)
- `.ufo/waves/round-23/falsify/out/CritSeparabilityW2/`:
  - Variant auditors: `X1-cur-minus-nul.py`, `X2-frozen-plus-catchall.py`,
    `X3-frozen-plus-nul.py`, `X4-cur-minus-catchall.py`,
    `X5-nul-only-revert.py`, `M14.py`, `M14+M02.py`, `M03+M10.py`
  - Per-variant grid JSON: `X1-cur-minus-nul.json`,
    `X2-frozen-plus-catchall.json`, `X3-frozen-plus-nul.json`,
    `X4-cur-minus-catchall.json`, `X5.json`, `M14.json`, `M14+M02.json`,
    `M03+M10.json`
  - `mutants.json` and `grid-both.json`
- Scratch, outside the lane: `/tmp/kama-r23w2/CritSeparabilityW2`
  (clone, untracked nothing), `/tmp/kama-r23w2/CritSeparabilityW2-out/`,
  `/tmp/kama-r23w2/CritSeparabilityW2-nul.q9yU/` and
  `/tmp/kama-r23w2/CritSeparabilityW2-xfer.4qzJ/`.
