# ConnPriorLessons — the round-23 mistake row, mined from prior kama lessons

Seat: `CloseKama22.ConnPriorLessons` (connector, leaf; no dispatch, no REA devices, no installs).
Lane base `master=4fe9339f8fc3a4a4a479d9c938a850da12f1124d`; access date 2026-10-21.
All lane/corpus reads were read-only. The lane checkout is **dirty**
(`git status --porcelain` → ` M tools/report-landing-audit.py`), so every "frozen" claim below
is the committed blob `4fe9339f:tools/report-landing-audit.py`, never the worktree file.
No fault fixture, selftest, grid, ledger or probe was executed by this seat.

## 1. Axes (godspeed)

| axis | round meaning | effect of this advice |
|---|---|---|
| **calibration 7** (declared C1) | the audit's own promises become measurable | row wording + KQ34 make the claim falsifiable without raising the scalar (7→7) |
| **operability 8** | no serving/runtime surface harmed | no production tool, endpoint or consumer touched; old-git floor named as a cost, not a harm |
| **quality** | criteria, not prose | proposed KQ34 is the durable form of the row |
| **expansion / discernment** | no new ground; outside review pending | unchanged; the row takes no discovery credit from round 22 |

## 2. The requested scan: round-1*/round-2* have **no Mistakes tables**

Executed heading scan `grep -E '^#+.*(Mistake|Trap|mistake)'` over `corpus/lessons/`; it matched
`## Mistakes` only from `round-10.md` onward (first: `round-10.md:5`, tables run rounds 10–22) and
did not match the lowercase `## Method traps` heading, which a direct read of the file supplies.
The files named in the ticket contain:

| file | nearest section | anchor |
|---|---|---|
| `round-1.md` | `## Method traps (each produced a wrong conclusion this round)` | `:41-43` (trap table; no error/verdict trap — its traps are `ss`, case-sensitive paths, remotes) |
| `round-1-safety.md` | output contract | `:21-28`, esp. "On errors, print a fixed class (`DEAD`, `NOT_HTTP`, or probe error)" — the ancestor of "Errors are never verdicts" |
| `round-1-critic.md` | `## Scope and verdict convention` | `:3`; `:116-119` requires `UNDECIDABLE` where root blocked NAT inspection, forbids the negative assertion |
| `round-2.md` | `## Implementation traps caught during review` | `:19-29`, esp. `set -e` turns drift status 2 into a premature exit; a corrupt TSV line must never become a phantom `row-absent` |
| `round-1-citations.md`, `round-1-relaunch-freshness.md` | fact/verdict tables | `round-1-citations.md:5`; `round-1-relaunch-freshness.md:31-40` (historical samples vs current truth) |

Round 10 is where those early mistakes were actually mined: `round-10.md:16` (row 8, UNDECIDABLE
must be recorded with the exact blocked command and verbatim error; no negative assertion) and
`round-10.md:19` (row 11, cited separately). So the honest lineage of the two patterns is:

### 2.1 "Scrubbed env means isolated"

- `round-17.md:144-147` — round-16 `measure.py:116` already carried
  `--no-replace-objects` + `GIT_*` scrub; the lesson deliberately kept those bytes.
- `round-21.md:71-74` — the new audit adopted **only** "scrubbed git environment and config for
  every git call". No replace, lazy-fetch, encoding or follow channel.
- `round-22.md:117-122` (D4) — "Environment scrubbing does not suppress repository-local
  configuration"; `QUALITY.md:165` KQ32 restricts the audit to trusted fleet/lane repos.
- Round 23 measures the exact channels R21 assumed away. The keystroke was known two rounds
  earlier; it was not carried into the new instrument.

The structural analogue to round-1 rule 1 (`round-1.md:9-14`, "Identity, not liveness … never
gate on a status code") is exact: a scrub shows *which knob was turned*, not *which channels are
closed*. `git_env` proves the environment is not the redirect; it cannot prove the repository is
not. The round-23 row is the same correction applied to a different subject.

### 2.2 "Errors become verdicts"

- `round-16.md:158` — malformed probe output "ends in a traceback (exit 1, not 2)".
- `round-17.md:86` M2 — "gate-overclaim class: a gate documents gradings no input can make fail";
  seven instances rounds 11–16, "fail-capability was never an admission condition".
- `round-18.md:88` M2 — unobserved property classified failed instead of could-not-evaluate;
  `QUALITY.md:133` KQ24 ("a real failure dominates a missing observation").
- `round-19.md:90-92` — exit 2/3 and tracebacks are `error`, never a rejection.
- `round-20.md:75` M1 — "error credited as targeted rejection"; fix = explicit verdict +
  non-passing error class + genuine-verdict control.
- `QUALITY.md:142` KQ25 — "an error remains visible and non-passing. A genuine-verdict positive
  control prevents an always-error classifier from passing."
- `QUALITY.md:158` KQ30 — "an untriggered injection or arbitrary crash earns refusal credit" is
  rejected.
- `round-21.md:63-64` — M1/M2 captured-by is literally "none before R21": the report-side
  defects were captured by the closure, but the instrument's own error/exec behaviour had no row.

## 3. Proposed round-23 mined mistake row

One row (the round declares one C1); the class is the intersection, not a new "git security"
class. Do not split it into "docstring" + "decode" rows: one `git()` wrapper and one docstring
are the fix, and a second row would imply a second fix (round-22 M2 scope-inflation pattern).

Paste-ready, in the round-22 column shape:

```markdown
| M1 | Instrument self-exemption: a gate's own isolation and error-class promises were never in its fault population | `tools/report-landing-audit.py` at `4fe9339f`: `:42-45` exit contract, "Errors are never verdicts"; `:75-76` `EvalError` "never converted into a verdict"; `:79-84` `git_env` — strips `GIT_*`, sets only `GIT_CONFIG_GLOBAL=/dev/null`/`GIT_CONFIG_NOSYSTEM=1`, docstring claims audited repos "cannot be redirected"; `:87-97` `git()` uses `subprocess.run(..., text=True)` and converts only `OSError`; `:114` `cat-file --batch-check` and `:147-149` `git log` carry no `--no-replace-objects`/`--no-lazy-fetch` (0 occurrences in the frozen blob); `:175-176` guards decode for draft reports but `:266` reads committed reports through `git show`, and `:828-843` catches only `EvalError`/`OSError`; `:425-427` maps exit 1 to `failed`. L1 probe artifacts (peer-verified in `ScribeLessonDraft.md`): `f1-logenc.err`/`f2-report-bytes.err` end in `UnicodeDecodeError` traceback with empty `.out`; `f4` clean under `refs/replace/<fabricated 40-hex>`; `f5/marker` created by a promisor `core.sshCommand`; `f3` clean only in `run.xpxV` (replace ref absent in `run.uCZq`). Precedent: `lessons/round-17.md:144-147` vs `lessons/round-21.md:71-74`. | None in practice. R22 D4 named the debt without a test (`lessons/round-22.md:117-122`, `QUALITY.md:165` KQ32); R21 M1/M2 already record "none before R21" (`lessons/round-21.md:63-64`). Criteria existed but were not applied to this instrument: R17 M2 gate-overclaim (`round-17.md:86`), KQ25 (`QUALITY.md:142`), KQ24 (`:133`), KQ30 (`:158`). | One centralized invocation shape: bytes-mode git with strict UTF-8 → `EvalError`, global `--no-replace-objects`/`--no-lazy-fetch`, `-c i18n.logOutputEncoding=UTF-8 -c log.follow=false`; docstring enumerates covered channels and names uncovered ones. Frozen arm is the pinned blob (sha256 per `ConnPlanningWalk` E1) with explicit `--lane-repo/--fleet-repo`; every fault must assert activation (replace ref exists; marker absent before the run). Same-bytes controls: clean exit 0 with `defects []`; a genuine fabricated-hash defect still exit 1 (blocks always-exit-2); a genuine evaluation error exit 2 and distinguishable from defect exit 1 (blocks always-exit-1); selftest count stated (50 or 50+N, cases enumerated); ledger `--rounds 10-22` errata-mode exit 0 defects 9/corrected 9/uncorrected 0 and no-errata exit 1 with the same 9. Shown able to fail by the frozen arm reproducing crash/false-clean/exec and by mutants deleting each prefix element and short-circuiting the decode. |
```

### 3.1 Wording corrections that must survive integration

1. **Not "the error became a verdict."** No JSON verdict is emitted. Write: "an uncaught
   `UnicodeDecodeError` traceback exits 1, colliding with the tool's documented exit-1 `failed`
   class (`:42-45`, `:425-427`)". The defect is exit-class collision and lost `could-not-evaluate`,
   not a fabricated defect document. (Scribe artifact check; do not overstate.)
2. **Not a two-arm "fault → refusal" table.** A repair that turns everything into exit 2 launders
   real defects; that is R20 M1's always-error laundering in the opposite direction. The grid must
   grade **three** distinct classes on the same fault set: clean 0 / defect 1 / evaluation error 2.
3. **F3 is not a countable fault yet.** `run.uCZq/f3` had no replace ref; `run.xpxV/f3` was clean.
   Per KQ30 ("an untriggered injection … earns refusal credit"), the `git replace` row counts only
   after the fixture asserts `git for-each-ref refs/replace` is non-empty and `git log` shows the
   replacement subject. Same for the marker: assert absent-before.
4. **No discovery credit to round 23.** The debt is R22 D4 (`rounds[406].notes`, KQ32). The row
   credits the debt to R22 and the measurement to R23; that is what keeps it out of the
   round-22 M2 scope-inflation pattern.
5. **"Errors are never verdicts" can stay true only if typed.** The `EvalError` class exists
   (`:75-76`); the row's fix is to route every decode/exec refusal through it, not to add a second
   exception taxonomy.

### 3.2 Proposed durable criterion (KQ34, next free number)

> **KQ34.** A tool that asserts its own isolation or its own error taxonomy is admitted only with
> a finite per-channel fault population: each asserted channel has a frozen arm that actually
> crashes, flips a verdict, or executes a configured command, and a current arm that returns the
> correct verdict or a typed could-not-evaluate. On the same bytes, clean (0), genuine defect (1)
> and genuine evaluation error (2) must remain three distinguishable outcomes, and every channel
> the fix does not cover is named in Limits. Environment scrubbing alone never satisfies an
> isolation claim.
> **Rejects:** a traceback exit 1 counted as a failed verdict; a scrub treated as suppressing
> repository-local config; an untriggered injection counted; a docstring channel left unmeasured.
> **Motivating:** `lessons/round-23.md` M1; `round-22.md:117-122`; `round-17.md:86`;
> `round-20.md:75`; KQ25/KQ30.

This is calibration, not source validity, and it does not relax KQ32: the audit stays limited to
trusted fleet/lane repos until the remaining channels are measured separately.

## 4. Second-order effects (do not smooth)

1. **KQ28's counting command is the audited instrument.** `QUALITY.md:151` makes
   `python3 tools/report-landing-audit.py --rounds 10-<N-1> --report N=<draft>` the admission
   command. If `--no-lazy-fetch` refuses every repo on git < 2.45 (peer-measured PATH shim:
   exit 2, `unknown option`), KQ28 becomes unmeetable on that host. The floor must be declared in
   the tool docstring, the lesson, and the recipe (`git --version` recorded), or the option must be
   probed once instead of unconditionally prefixed.
2. **The frozen arm can fake "typed refusal."** Frozen `--lane-repo` defaults to
   `Path(__file__).resolve().parent.parent`; a frozen copy under `/tmp` audits `/tmp` and exits 2
   (peer-measured `ConnPlanningWalk` E4). A naive grid would score every frozen case as "refused".
   The frozen **clean control must exit 0 with `defects []`** before any row is credited.
3. **Severity is not symmetric.** False clean via `refs/replace` (f3/f4) defeats KQ28's purpose
   silently — R21 M1's spliced hash would pass. The traceback direction is loud. Report the
   silent direction first; never average the two into one "faults fixed" count.
4. **Channel leakage beyond the tuple.** Peer scouts report `log.showSignature`+`gpg.program`
   exec, `.git/info/grafts` surviving `--no-replace-objects`, and `extensions.objectFormat=sha256`
   mis-verdicting in both arms (`ConnPlanningWalk` E7/E8/E10). The row and Limits must name these
   as uncovered until their own seats land; otherwise the corrected docstring is a new overclaim,
   exactly the class being mined.
5. **Ledger has two legitimate modes.** Errata exit 0 and `--no-errata` exit 1 with the same nine
   defects are both correct (`rounds[406]` vs `rounds[418]`). "Clean ledger" must not be
   redefined, and no report may be edited to make history pass.
6. **Selftest count semantics.** R21-SELFTEST-DEBT (vacuous uncommitted-now fallback; crash-only
   `GIT_DIR` assertion) is still open and rides the same `selftest()`/`git_env()` surface. If the
   fix adds no case, say "frozen baseline 50/50; current 50/50; no isolation channel is
   selftest-covered" — do not let "50/50 unchanged" imply coverage it does not have.

## 5. Verification status

**Ran (read-only):**
- heading scan for `## Mistakes` over `corpus/lessons/` (first at `round-10.md:5`);
- `git cat-file blob 4fe9339f:tools/report-landing-audit.py` → 0 occurrences of
  `--no-replace-objects|--no-lazy-fetch|i18n.logOutputEncoding|log.follow`; 50
  `cases.append`/`check(` lines; line reads of `:42-45`, `:75-97`, `:114`, `:147-149`,
  `:171-177`, `:266`, `:828-843`, `:425-427`;
- `git rev-parse HEAD` = `4fe9339f…`; `git status --porcelain` shows the dirty
  `tools/report-landing-audit.py`;
- line reads of the lesson anchors cited above.

**Did NOT run:** the probe, any fault fixture, the selftest, the historical ledger, the
frozen/current grid, or the real fleet/lane audit. I did not read `/tmp/kama-r23-probe/` artifacts
first-hand (they enter only through the L1 context and `ScribeLessonDraft.md`); F3/F4/F5
reproduction, the old-git floor, grafts/showSignature/objectFormat and the `git_env` docstring's
authorship are other seats' measurements. No source rows opened, no network, no installs.

**Files written:** this file only
(`.ufo/waves/round-23/build/advice/ConnPriorLessons.md`). Tools installed/updated: none.
