VERDICT: confirm — the gate-overclaim class recurs in seven documented claims across rounds 11-16; outside closures caught four, the rest only lane seats, and no closure has refused admission for it.

# Round 17 — PlannerWalk: the recurring gate-overclaim pattern (rounds 11-16)

Read-only bounded data-walk for the L1 planner seat. Sources limited to
`SCORECARD.md` §Round 12-16, `LOG.md` rounds 12-16 and
`corpus/lessons/round-1[2-6]*.md`, plus the lane bytes those files cite
(`SKILL.md:533`, `corpus/QUALITY.md`, `tests/probe-verdicts/check.py`,
`tools/kama-probe.sh`, the nine matrix JSONs, `.ufo/waves/round-16/falsify/advice/`).
No gate, harness, selftest, `measure.py`, mutant or live tool was executed; no
port was bound; nothing outside this report was written. Lane tip at read time
is `cff9e62f05aa7cfb9059444f62eb787100719713`; `check.py` there is byte-identical
to `.ufo/waves/round-17/frozen/tests_probe-verdicts_check.py`
(`b853576edd54e006c4d8742c1a7335a0d6cca475d107acce7792da75b6145762`).
The worktree also carried round-17 in-progress edits by sibling seats
(`tests/probe-verdicts/check.py`, `tests/llamacpp-live/check-receipt.py`,
`tests/probe-verdicts/fault-controls.py`, `AGENTS.md`, `.gitignore`,
`tools/sources-append-only.py`); every byte and line number below refers to the
committed tip or the frozen pre-round copies, which are the objects the counting
command grades.

## 1. What the class actually is

The recurring shape is not "the code forgot the check". In four of the seven
sustained instances the comparison existed and executed, and no input in the
fixed evidence could make it fail (rows 4, 7, 8, 9). The other three lacked the
comparison entirely while prose, criterion or receipt claimed it (rows 1, 2, 6).
The lane's own mutation seat named the distinction:
"distinguish an exercised but redundant comparison from an unexercised failure
path" (`.ufo/waves/round-16/falsify/advice/MutateHarness.md:6`).

Three layers are always present, and the overclaim lives in the gap between
layers 1 and 2, hidden by layer 3:

1. **Declared coverage** — prose in `SKILL.md`, `QUALITY.md`, a receipt `limits`
   string, or a run tally ("10/10", "VALID", "72/72").
2. **Executable predicate** — what the gate actually compares, and whether any
   input in the frozen corpus can discriminate that conjunct.
3. **Detector** — the thing allowed to notice the gap. Every failure below is a
   detector that structurally could not:
   - the same fixed corpus whose expectations were authored with the gate;
   - a selftest that re-spells the producer's schema instead of reading a real
     receipt;
   - a pass count over rows that never carry a discriminating value.

Five mechanisms account for all seven instances:

| # | Mechanism | One-line test that would have caught it |
|---|---|---|
| M-a | Non-load-bearing conjunct | Remove the conjunct; does any row fail? |
| M-b | Recorded-but-ungraded field | Is the field in `passed`, or only in the record? |
| M-c | Coverage asserted in prose, no executable obligation | Where is the check that fails when the promise is deleted? |
| M-d | Co-authored oracle (selftest re-spells the producer) | Does the selftest fixture come from a real producer receipt? |
| M-e | Wrong exit class (harness fault reported as subject failure) | Does malformed subject output produce a named finding, not a traceback? |

## 2. Dated timeline (all 2026-10-20, times as recorded at -03:00)

| When | Claim (round) | Declared | Actual predicate | Caught by | Outcome |
|---|---|---|---|---|---|
| Round-11 work; caught before the R12 closure (01:16:19-01:38:55) | Frozen-input integrity | "Eleven frozen input digests were verified" `LOG.md:594-595`; "frozen source bytes" `LOG.md:547` | Self-consistency against the shipped manifest, not the source blob | **Outside round-11 closure D1**, per `LOG.md:614-616` | `LOG.md:648`: "The eleven integrity checks did **not** independently establish source-commit correspondence." New `fidelity.py`; independent recount 1→0 |
| 01:38:55 R12 closure | KQ15 exit distinction | Mismatch/tamper/unavailable have "distinct nonzero exits" `corpus/lessons/round-12-verifier-spotcheck.md:147` | Exit map is 1/2/2; only finding IDs differ | **Outside round-12 closure D1** (same line) | KQ16 appended (`corpus/QUALITY.md:61`); literal 2→0 `SCORECARD.md:379` |
| 02:08:58 R13 closure | Textual criterion gate | "effective criterion precision" `SCORECARD.md:340` | Two literal assertion strings in one QUALITY cell | **Author pre-disclosed, outside bounded it**: "The red-before count only demonstrates absence of the two newly specified literal assertions" `corpus/lessons/round-13.md:68`; outside rejected the semantic reading `corpus/lessons/round-13-verifier-spotcheck.md:186` | No defect routed; paraphrase evasion kept as a declared limit `corpus/lessons/round-13-verifier-spotcheck.md:278` |
| 03:42:33 R14 closure | `measure.py` corpus guard | "say duplicated corpora fail before children" `corpus/lessons/round-14-verifier-spotcheck.md:142` | Minimum-unique-count only: "it never compares total names with unique names" (same line) | **Outside round-14 closure R1**, static code reading, no execution | Round-15 guard; red 23/27 → 50/0 `SCORECARD.md:522`; 483/483→0/0 `SCORECARD.md:533` |
| 05:44:34 R15 closure | Replay prose ordering | Rejection occurs "before the minimum-unique check" `corpus/lessons/round-15-verifier-spotcheck.md:169` | Duplicate problem appended first, minimum still checked | **Outside round-15 closure defect 5** (same line) | Appended precision only |
| 10:17 R16 build | Probe verdict for a loading server | Body lacking a model array is "non-2xx HTTP from a non-model service" `corpus/lessons/round-16.md:68` | No criterion compared documented engine states to verdicts `corpus/lessons/round-16.md:68` | **L1's own live smoke**: "L1 smoke at 10:17 -03 saw a real b11755 llama-server answer `GET /v1/models` with 503" `LOG.md:930-931` | `MODEL_LOADING`/KQ19; 55/17 → 72/0 `SCORECARD.md:610` |
| R16 falsify wave | Live lifecycle checks | Receipt "10/10 checks, `VALID`" `SCORECARD.md:611` | "`health_ready` ignores its documented body" `.ufo/.../ReviewLiveHarnessCode.md:95`; "`teardown_exited` proves reaping, not teardown" `:82`; "no check consumes it" `:55` | **Lane-dispatched falsify seats**; carried by outside closure as defect 6 `corpus/lessons/round-16-verifier-spotcheck.md:187` | Partial in-round repairs; remainder is this round's C2 |
| R16 falsify wave | Receipt gate selftest | Gate green on its own spelling | "self-authored selftest hides producer drift" `corpus/lessons/round-16.md:69`; "the first rebind still accepted a forged loading transition" `corpus/lessons/round-16.md:171` | **Lane-dispatched mutation seats** | Second rebind: "26 single-field mutations rejected" `corpus/lessons/round-16.md:131` |
| R16 falsify wave → this round | `check.py` coverage | "grades verdict, reason, exit and drift" `SKILL.md:533`; "verdict, reason, exit and drift are all graded" `corpus/QUALITY.md:109` | Four conjuncts at `tests/probe-verdicts/check.py:340-347`; 0 discriminating rows | **Lane-dispatched mutation seat**: "survived 5; killed 0; inconclusive 0" `.ufo/waves/round-16/falsify/advice/MutateHarness.md:20`; carried at `corpus/lessons/round-16-verifier-spotcheck.md:187` | Open — C1 of this round |

Count: seven sustained overclaims (rows 1, 2, 4, 6, 7, 8, 9), one prose residue
(row 5), one control instance (row 3).

## 3. Catching distribution — and the hole it exposes

- **Outside closures caught four**: rows 1, 2, 4, and the row-5 residue. All four
  were caught by *static* predicate-versus-prose reading, never by executing the
  gate (PROTOCOL's Gate standard forbids it; `corpus/lessons/round-15-verifier-spotcheck.md:5`
  records "No lane-owned gate, harness, selftest or serving probe was executed.").
- **Lane seats caught the three round-16 instances** (rows 7, 8, 9) and L1's own
  smoke caught row 6.
- **Every one of those admissions still passed.** The round-14 closure admitted
  while stating "A runner guard/prose defect is explicitly excluded and routed
  below" (`corpus/lessons/round-14-verifier-spotcheck.md:7`). The round-16
  closure header reads "**Closure: status `ok`, admitted `true`.**"
  (`corpus/lessons/round-16-verifier-spotcheck.md:7`) and its own defect 6 says
  "Five check.py harness mutants survive." (`:187`). Fail-capability is a
  *routed debt item*, not an *admissibility condition*. That is why the class
  survives admission five rounds running.

Corollary for framing: the axis score cannot register the class either.
`SCORECARD.md:320,379,445,522,610` are five consecutive rows reading
"calibration **7 → 7**, delta 0" (`:610`). A rule that a bounded repair never
moves the score means the only place the class can be made expensive is the
QUALITY criterion and the admission rule — not the number.

## 4. This round's C1 object, measured from bytes

The overclaim is on the record twice, in the registry and in the criterion:

- `SKILL.md:533` — "grades verdict, reason, exit and drift".
- `corpus/QUALITY.md:109` (KQ19) — "verdict, reason, exit and drift are all graded".

The predicate is `tests/probe-verdicts/check.py:340-347`:
`record["passed"]` conjoins verdict equality (`:341`), reason equality (`:342`),
probe exit versus expected exit (`:343`), and `drift == (verdict != "MODEL_OK")`
(`:346`). Line `:337` records five fields — `("verdict", "reason", "drift",
"served_model", "evidence")` — but `served_model` and `evidence` never enter
`passed`, which is mechanism M-b. The nine-file matrix is the only oracle, and
per the mutation seat its rows are non-discriminating by construction:

| Field | Frozen arm mismatches | Current arm mismatches | Consequence |
|---|---:|---:|---|
| verdict | 17 | 0 | load-bearing |
| reason | 17 | 0 | fails only through verdict; no reason-only row |
| exit | 0 | 0 | ignore-exit survives |
| drift | 0 | 0 | ignore-drift survives |
| non-uppercase verdict | 0 | 0 | casefold-verdict survives |
| timeouts / recorded errors | 0 | 0 | timeout-pass survives |

Source: `.ufo/waves/round-16/falsify/advice/MutateHarness.md` "Why the mutants
survived" table; "The timeout exception path was not exercised." (`:150`).

The residual exit-class defect (M-e) is visible in the static bytes: the
unparseable-output branch catches `(json.JSONDecodeError, KeyError, IndexError,
TypeError)` (`tests/probe-verdicts/check.py:332`) and returns a record, but
`row = doc["rows"][0]` (`:331`) followed by `row.get(key)` (`:338`) raises
`AttributeError` when `rows[0]` is not a mapping. Under `SKILL.md:533`'s own
contract ("1 a row failed, 2 harness/schema error") an uncaught traceback exits
1, so a harness fault is reported as a subject failure — the same class the
round-16 lesson states as "malformed probe output ends in a traceback (exit 1,
not 2)" `corpus/lessons/round-16.md:157`.

### 4.1 The two proposed invariants are implementable and load-bearing

Computed statically over the nine matrix files (no gate run): 72 rows,
71 `stub` + 1 `closed`.

- **route-match.** `classify()` fetches `/v1/models` unconditionally before any
  branch: `fetch "$port" "/v1/models" "m$port"` (`tools/kama-probe.sh:456`).
  So every stub-mode row must show a recorded `GET /v1/models`, including the
  one row with no declared route that answers from `default_route`
  (`tests/probe-verdicts/LoadingEnvelope.json`, row
  `LoadingEnvelope.every-non-frontend-path`, `"routes": {}` plus a 503
  `default_route`). The recorder is already plumbed —
  `make_handler(test["routes"], test["default_route"], record["requests"])`
  (`tests/probe-verdicts/check.py:307-308`) — and is currently consumed only by
  the zero-request guard (`:323`). Predicate must be
  "`GET /v1/models` ∈ `record["requests"]`", not "`/v1/models` ∈ declared
  `routes`", or that row is a false failure. The single `closed` row is exempt.
- **served_model.** Derivable from the stub's own body for 11 of 72 rows
  (8 `MODEL_OK`, 3 `MODEL_MISMATCH`): `routes["/v1/models"].body_json.data[].id`
  (e.g. `"id": "kama-ready"` in `tests/probe-verdicts/ReadyControls.json`,
  `ReadyControls.expect-exact-id`). The other 61 rows carry no model list and
  the probe's default is the literal `-` (`tools/kama-probe.sh:455`,
  `C_SERVED='-'`), so their derived expectation is `-`.

Trap to pre-register: the derived expectation is the **served** id, never the
row's `expect` field. Five rows with a model-list body deliberately have `expect`
outside the raw served ids — two `MODEL_MISMATCH` rows by definition, plus three
`MODEL_OK` rows where `expect` is a normalized or basename form (e.g.
`ReadyControls.ollama-name-not-served-id` expects `stories260K` while the stub
serves `kama-ready`). A naive `served_model == expect` check would fail five
legitimate rows and silently invert the invariant.

## 5. Structural fix — the class-level criterion (KQ20 candidate)

A per-round repair of `check.py` alone will not stop the class: rows 1, 2, 4, 7
and 8 were each "repaired next round" and the class returned. What stops it is
an invariant on *coverage claims*, enforced inside the gate.

**F1 — Coverage is enumerated, not asserted.** A gate publishes a machine-readable
coverage manifest mapping each declared conjunct to one control id and the
finding that control must produce. The gate exits 2 if a declared conjunct has
no control. This kills M-c at the source: `SKILL.md:533` and `QUALITY.md:109`
could not claim four graded fields unless four controls existed.

**F2 — Single-field fault controls on the subject's output.** Each control
corrupts exactly one field (or one behaviour, e.g. a probe that hangs) of the
produced row and requires a named failure. This is mechanism M-a's executable
form. Precedent already in-lane: the round-16 receipt gate was only trusted
after "26 single-field mutations rejected" (`corpus/lessons/round-16.md:131`);
the mutant runner states the weaker pre-fix state explicitly (M8,
`round-16.md:171`). Note this is forced here by the contract: the nine matrix
files are byte-frozen with set digest `bf9068d8…` and no new `*.json` may enter
`tests/probe-verdicts/`, so discrimination cannot be bought with new rows — only
with wrapper probes.

**F3 — Derived expectations.** Any expected value computable from another object
in the row must be computed, not restated: `served_model` from the stub body plus
verdict, route-match from the recorded requests. This is exactly C1(a), and it
also kills M-d: a selftest cannot drift from the producer if its expected values
are derived from a real producer receipt (cf. "self-authored selftest hides
producer drift", `round-16.md:69`).

**F4 — Exit-class discipline.** Malformed subject output becomes a recorded
per-row failure under the gate's harness-error class (exit 2), never a traceback
and never exit 1. Concretely: catch `AttributeError` (or validate
`isinstance(row, dict)`) at `tests/probe-verdicts/check.py:331-338`.

**F5 — Counting command.** The runner pins gate, subject and matrix digests,
then reports killed / survived / inconclusive for every grading-weakening
mutant; the claim is admissible only at 0 survived on the combined arm (frozen
corpus pair **plus** fault controls). Round-15 is the working template:
same matrix red 23/27 → 50/0 (`SCORECARD.md:522`), with negative controls
distinguished from an absent tool by exact reason, null findings and zero
process events (483/483 → 0/0, `SCORECARD.md:533`).

**F6 — Admission rule (the part no gate can enforce).** A fail-capability
defect is an admissibility condition, not a routed debt item. Evidence that this
is currently missing: round-14 admitted with the guard defect routed
(`corpus/lessons/round-14-verifier-spotcheck.md:7`), round-16 admitted with five
surviving harness mutants routed (`corpus/lessons/round-16-verifier-spotcheck.md:7,187`).
Without F6 the other five clauses are re-routed each round and the class
persists.

### Proposed row text for this round's QUALITY entry (KQ20)

> A gate's declared grading coverage is admissible only when every declared
> conjunct is load-bearing: a fault control corrupting exactly that one field or
> behaviour of the subject's output makes at least one row fail with a named
> finding; expectations derivable from the row's own fixture (stub body, recorded
> requests, verdict) are computed, not restated; and every grading-weakening
> mutant of the gate — defined against the *declared* coverage, including
> conjuncts not yet implemented — is killed by the same suite, counted
> before→after against a byte-pinned frozen gate. Malformed subject output is a
> recorded per-row failure under the harness-error exit class, never an escaped
> traceback. Reject: a conjunct with no discriminating input ("exercised but
> redundant"); a selftest that re-spells the producer's schema; a coverage count
> asserted in prose without a control count; and any claim whose only detector is
> a fixed corpus authored alongside the gate.

Historical coverage of that wording: rows 1 (derived source expectation), 2
(executable exit map), 4 (corpus fault control), 7 (`health` body and
termination-cause controls), 8 (producer-receipt comparison), 9 (mutant runner)
are each closed by one clause, which is the evidence that the rule is
class-level rather than a sixth ad-hoc repair.

## 6. Pre-registered numbers for the C1 counting command

- **Before** (frozen `check.py` + the 55/17-vs-72/0 pair detector): 5 survived —
  `ignore-reason`, `ignore-exit`, `ignore-drift`, `casefold-verdict`,
  `timeout-pass` (`MutateHarness.md:20` and table).
- **Do not stop at 5.** Three declarations have no implementation at all, so no
  code mutant can express them: `served_model` ungraded, route-match absent, and
  malformed output escaping as exit 1. If the mutant set is defined against the
  v2 declared coverage (the four current conjuncts plus the two new invariants
  plus the timeout behaviour plus the malformed-output exit class), the honest
  before is **8/8 survived**, after **0/8**. A 5→0 count alone would leave the
  new invariants unproven — the exact repeat of KQ19 asserting coverage it did
  not test.
- **The pair totals must not move.** 55/17 → 72/0 (`SCORECARD.md:610`) is the
  round-16 verdict change and is unchanged by this repair; the improvement lives
  entirely in the fault-control arm. Claiming otherwise would itself be M-a.
- **Digest pinning is required** (see R1) because the inherited survivor count
  was measured against an intermediate probe.

## 7. Divergences and risks the runner must handle

- **R1 — inherited survivor count is not digest-pinned to the shipped probe.**
  `MutateHarness.md` records `tools/kama-probe.sh` as
  `6edd3c4cfdf3…fa50`, but the shipped probe at `726f737` and at tip is
  `36b64978…a29d3` (`sha256sum`; also `corpus/lessons/round-16-verifier-spotcheck.md`
  C2 section). The mutation seat's values correspond to
  `b8e485c:tools/kama-probe.sh`; its harness hash
  `fd49ff7c…` equals `b8e485c:tests/probe-verdicts/check.py`, whose bytes are
  identical to tip. `git diff b8e485c 726f737 -- tools/kama-probe.sh` is 5
  insertions / 3 deletions confined to the header comment, so the pair's row
  fields are behaviourally unchanged [INFERENCE]; the *conclusion* transfers, but
  the runner must recompute on the pinned digests and print them.
- **R2 — do not derive `served_model` from `expect`** (five legitimate rows
  differ, §4.1).
- **R3 — route-match predicate is recorded requests, not declared routes**
  (the `default_route` row, §4.1).
- **R4 — `evidence` is also recorded and ungraded** (`check.py:337`). Either grade
  it through a normalized predicate or narrow the `SKILL.md:533` /
  `QUALITY.md:109` wording; leaving it out while claiming "grades …" is the same
  overclaim at a smaller scale.
- **R5 — key omission and wrong value are two mutants for `served_model`.** A
  wrapper that deletes the key yields `None` through `row.get` (`check.py:338`);
  a wrapper that serves a different id yields a wrong string. Two controls, two
  kills.
- **R6 — a wrapper must corrupt one field only.** If the rewriting wrapper also
  reorders keys or changes `evidence`, one control silently tests two things and
  the kill attribution is lost (the M8 class).

## 8. Limitations

- Read-only: no gate, harness, `measure.py`, `mutants.py`, `controls.py`,
  selftest, probe or live server was run; the 5/5 survivor and 23/27 figures are
  read from committed advice/receipts, not re-derived.
- Counts over the nine matrix files (72 rows, 71 stub, 11 derivable model ids,
  five `expect`-outside-body rows) are static JSON inspection of the committed
  files, not gate output.
- `corpus/lessons/round-11-verifier-spotcheck.md` was deliberately not read (out of
  the assigned source set); row 1 rests on the round-12 LOG erratum and closure.
- Wall-clock times are the closure digests' own -03:00 stamps, not independently
  verified.
- [INFERENCE] labelled items: the behavioural equivalence of the `b8e485c` and
  tip probe on matrix-relevant fields; the claim that F1-F5 would have caught each
  historical instance (argued from each defect's text, not counterfactually run).

## 9. Installs

None. No tool was installed or updated; `python3`, `git` read-only subcommands,
`sha256sum` and `cmp` sufficed.
