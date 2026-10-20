VERDICT: partial — tameshi's method transfers into C1/C2 as conventions; the fault-control class, the live-producer arm, and one stale pin must be handed off, not absorbed.

Read-only overlap scan. Sources: `/home/vgpnk/Projects/shokunin/tameshi-shokunin/SKILL.md`, `/home/vgpnk/Projects/shokunin/tameshi-shokunin/PROVINCE.md`, `/home/vgpnk/Projects/shokunin/tameshi-shokunin/corpus/QUALITY.md`, plus kama's `PROVINCE.md`, `tests/probe-verdicts/check.py`, `.ufo/waves/round-16/measure.py`, `.ufo/waves/round-16/falsify/advice/MutateHarness.md`, `tools/kama-llamacpp-live.py`, `tests/llamacpp-live/check-receipt.py`. No gate, mutant runner, control suite, or `measure.py` was run; only checksums, one `sed` extraction, and read-only `git show/log` were executed.

File roots for the shorthand below: `SKILL.md`, `PROVINCE.md`, `corpus/QUALITY.md` = `/home/vgpnk/Projects/shokunin/tameshi-shokunin/…`; `check.py` = `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/check.py`; frozen `check.py` = `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/frozen/tests_probe-verdicts_check.py`; `measure.py` = `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-16/measure.py`; `kama-llamacpp-live.py` = `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py`; `check-receipt.py` = `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/llamacpp-live/check-receipt.py`; peer advice names (`MutBaselineCheckPy.md`, `RevengerPlannerWalk.md`, `ReviewMeasureDesignC1.md`, `ConnectSouji.md`) = `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/build/advice/…`.

## Axes

- **calibration (7, lowest):** whether a kill/survivor is attributable, denominated, and pre-registered.
- **operability:** one command, literal exits, a parseable receipt, no escape path.
- **non-harm check:** the nine `*.json` matrices stay byte-identical, no new `*.json` in that directory, no lane writes, L1 still runs every official measurement.

## Scope comparison

| Layer | Owner | Anchor |
|---|---|---|
| The method — "hermetic suites, mutation testing, fail-closed arms, verdict-line discipline, no-permissiveness audits, before/after proof" | tameshi | `tameshi-shokunin/PROVINCE.md:4-5` |
| A pattern claimed **general** | tameshi, only after "evidence in TWO independent lanes" | `PROVINCE.md:15-16` |
| Sibling gate code | owner lane; tameshi reads only — "Never edits a sibling's gate code (read-only probes; recommendations travel in round reports)." | `PROVINCE.md:16-17` |
| Endpoint health, served identity, llama.cpp lifecycle | kama — tameshi lists "Credential material (→ kagi), endpoint health (→ kama)." | `PROVINCE.md:18`; refused at `SKILL.md:1262` |
| A sweep of live substrates/sessions | tameshi refuses: "Live substrates / sessions | never read; a live-plane probe is a PATH-level stub, never the session" | `SKILL.md:1261` |
| A sweep without a one-command hermetic suite | tameshi refuses before any suite runs | `SKILL.md:1259` |
| Moving a pin | "a recommendation, never an edit — the service never edits, repairs or re-pins a gate" | `SKILL.md:1260` |

## Contested scope (name it; do not smooth it)

1. **"Fault control" is a method class, not a kama invention.** tameshi already measures three gate-attacking controls: "cite-check's mutation copy", "scope-gate `--falsify`, a mutation mode that attacks the gate itself", and "claims-check's external env-poison probe" (`SKILL.md:108-113`). kama's C1/C2 version attacks the **subject** (probe stdout, fake server) and requires the **checker** to fail — a distinct species, but the naming and generality belong to tameshi's layer. Two kama subjects (C1 check.py, C2 receipt gate) are still **one lane**; `PROVINCE.md:15-16` is not met. kama may call it "kama's subject-side fault control"; the general claim must wait for a second lane.
2. **C2 splits across the province line.** `tests/llamacpp-live/check-receipt.py` is a hermetic gate over retained receipts — it re-derives every check and "``"passed": true`` is never trusted" (`check-receipt.py:19`) — so tameshi's method applies directly and a case could be *offered*. It already accepts v1 **and** v2 (`RECEIPT_SCHEMA_V2`, `check-receipt.py:59`; `REQUIRED_CHECKS_V2`, `:81-91`) while the producer is still v1 (`SCHEMA = 'kama-llamacpp-live/v1'`, `kama-llamacpp-live.py:50`; `health_ready` grades status only, `:938`). The producer starts a real child, sends SIGTERM, and observes the port (`kama-llamacpp-live.py:659-687`); that is rows d/e territory (`SKILL.md:1261-1262`). Consequence: the **gate half** of `controls.py` is fully hermetic now (synthetic v2 receipts under `mkdtemp`, no llama-server), and only the **producer half** needs the live child. `tests/llamacpp-live/controls.py` as a whole must therefore stay kama-only and must not be filed as a tameshi ledger leg.
3. **The fixture rule and the hard constraint agree only one way.** tameshi's hermetic shape is "fixtures under `mkdtemp` only, cleaned in `finally`; no live path read" (`SKILL.md:62`); kama's digest is "every *.json file name and its sha256 under tests/probe-verdicts/, sorted by name" (`measure.py:279-281`) with `EXPECTED_TESTS = 72` (`:282`). Any JSON fixture added to that directory changes the digest and the breadth. Fault controls must be **wrapper scripts generated under `mkdtemp`**, never matrices. `fault-controls.py` itself is safe: `matrix_digest()` globs `*.json` only (`measure.py:286-290`; observed recomputation now returns `9 bf9068d8…`).
4. **Offers are not a schedule.** tameshi's intake row a: "no sweep — the queue is an offer, not a schedule" (`SKILL.md:1258`). No kama gate (including the frontier `tools/sources-append-only.py`, not a claim this round) should be routed to tameshi as a wave-2 sweep request; L1 owns measurement and criterion 20 forbids editing a seated instrument (`QUALITY.md:102-104`).

## What kama must hand off rather than absorb

- **The generalization and the corpus row.** If the C1/C2 before→after survives, kama hands tameshi a case-note *offer* (pins, suite string, control line, pre-registered spec, survivor probes) and the candidate control class. Writing into tameshi's `corpus/` is out of bounds; tameshi writes its own record.
- **The ledger-leg artifacts, only on opt-in.** A tameshi sweep needs a pinned revision, a one-command hermetic suite, and a clause-mapped defect spec (`SKILL.md:810-823`). kama supplies them; tameshi never re-pins kama's gate (`SKILL.md:1260`).
- **The C2 live half.** Hand off the *lesson* (a teardown/port predicate that passes after any exit is a zero-work green) as a method instance, not the llama.cpp predicates. Endpoint semantics stay in kama (`PROVINCE.md:18`).

## Reusable conventions — exact landing sites

| # | Convention (tameshi anchor) | Lands in | What it forces |
|---|---|---|---|
| 1 | Pre-registered defect table with `expect: killed|survived` and reason; "Pre-registration is what makes an expectation miss a calibration datum instead of a rationalization" (`SKILL.md:163-167`, `:819-821`) | `mutants.py` spec | Calibration gains a real datum: prediction hits/misses per arm, misses kept |
| 2 | Uniqueness gate before any run: `count(old) == 1`, literal `all unique`, `new != old` (`SKILL.md:170-178`, `:267-268`) | `mutants.py --check` | The round-16 `old` strings were derived from pre-repair bytes; re-derive from the frozen bytes, never from the advice |
| 3 | Control first; "a red control exits 2 (kills could not be attributed)" (`SKILL.md:843-844`) | `mutants.py`, `fault-controls.py` | An identity wrapper must pass before any corrupting wrapper is credited |
| 4 | Kill = red **with full enumeration**, failing labels verbatim; "a kill quoted without its failing labels is unverified" (`SKILL.md:193-199`, `:357-358`) | both counting commands | A mutant that dies before printing the summary is INCONCLUSIVE, not killed (this is the malformed-output class) |
| 5 | "Kill rate = killed / (killed + survived) — inconclusive runs are excluded from the denominator" (`SKILL.md:210-211`); `DEGRADED exit 1 on any inconclusive` (`:849-850`) | both | The before/after number cannot be inflated by crashes |
| 6 | "Probe every survivor for non-equivalence" off-suite (`SKILL.md:214-223`, `:1794-1796`) | `mutants.py` after-arm | A survivor that no off-suite wrapper distinguishes is `EQUIVALENT` with a reason (`QUALITY.md:119-120`) |
| 7 | Frozen pin + restore proof; `MUTATE_RESTORE: OK|DRIFT` (`SKILL.md:375-392`, `:849-851`) | `mutants.py` | Print check.py sha and matrix digest before and after; `DRIFT` fails the run |
| 8 | "Compare by byte-identity; scrub volatility only by an explicit list" (`SKILL.md:474-477`) | `mutants.py` row comparison | Name the excluded volatile fields (ephemeral port, probe metadata) in the receipt, as round-16 did with six fields |
| 9 | Repeated controls compare "raw exit/stdout/stderr tuples" over a finite sample and "never prove determinism" (`QUALITY.md:34-37`) | both | State n per arm; a single run is n=1, not determinism |
| 10 | A repair's selftest must "defeat each weaker rule it claims to exclude, one fixture per rule" (`QUALITY.md:116-121`); "the same reconciliation command must reject the unresolved original row and accept the disposition-only repair" (`QUALITY.md:61-65`) | `fault-controls.py`, `controls.py` | One wrapper per v1 weakness; one command shows old rejects / new accepts; a setup error (exit 2) is not a "rejected" control |
| 11 | Classify by behavior, "literal exits and stable finding IDs; helper-only controls are not a standalone selftest" (`QUALITY.md:77-80`) | `fault-controls.py` | check.py `--selftest` is validator-only — "feeds 4 embedded malformed tests through the schema validator" (frozen `check.py:28-30`); the public fault suite asserts exit 0/1/2 and exact row names |
| 12 | "Zero-work is a defect, not a green" (`SKILL.md:489`, `:506`); "A live gate may not pass on nothing" (`SKILL.md:75-77`) | both | `teardown_port_closed` grading `port_refuses is True` after any exit (`kama-llamacpp-live.py:1029-1032`) is exactly this defect; `loading_envelope_exact` is self-labelled "Not a check" (`:176`) |
| 13 | "An arm that cannot fire on this host is an unknown, not a pass" (`SKILL.md:519-521`); refusal paths need their own cases (`:118-121`) | `controls.py` | The `finally`/teardown fault path needs its own control, or the exit-2 guarantee is unproven |
| 14 | "Test a projected interval at its edge" (`SKILL.md:1790-1793`); "Grade by exit, not by stdout bytes" where `mkdtemp` names appear (`:1786-1787`); `env -i` with its own `HOME`/`TMPDIR` (`:1780-1782`) | both | served-model: matching id, near-miss (case/whitespace), and absent — not only the wholly-different midpoint; route-match: a row with zero `GET /v1/models` |
| 15 | "Never quote a case count from source … Name the executed summary line" (`SKILL.md:99-102`); shared survivor classes are "reported-but-unasserted data" and the "unreached/fixture-absent arm" (`:308-309`) | report | Quote `tests=72 passes=… failures=…` from the run; the round-16 five are the reported-but-unasserted class (five fields/arms never read) |

## Evidence finding — two pin deltas, one moving target

The round-16 advice pins the harness it swept as `P = fd49ff7c0621bf3799c835b8e2baffbac61c35ce8e2c6e91b92fc495ce376140` (`MutateHarness.md`, "Byte identities"). The round-17 frozen copy hashes `b853576edd54e006c4d8742c1a7335a0d6cca475d107acce7792da75b6145762`, 510 lines. **Naming collision to kill:** `MutBaselineCheckPy.md:10` calls the frozen `b853576e…` "P". A receipt that says "P" is ambiguous; use `R16` (`fd49ff7c…`) and `R17-frozen` (`b853576e…`) instead.

Cause of the delta: commit `726f737` ("round-16: falsify-wave repairs …") changed the file after the sweep; `git show 726f737^:tests/probe-verdicts/check.py | sha256sum` reproduces `fd49ff7c…`, and the delta is exactly four lines — the docstring and `--selftest` help text moving "3 embedded malformed tests" to 4 — line count unchanged, no behavior-bearing line touched. Corroborated independently: `MutBaselineCheckPy.md:10` already uses the frozen bytes and disclaims the round-16 hash; `RevengerPlannerWalk.md:265` maps `fd49ff7c…` to `b8e485c:tests/probe-verdicts/check.py`; `ReviewMeasureDesignC1.md:7` observed the same second delta (`dadc777e…` at 12:22:22); `ConnectSouji.md:69` warns the after-arm pin will not stay unambiguous while the file is repaired.

A second delta landed **during this scan**: the C1(a) repair hardened `grade()` (served-model and route graders, a `probe_output_row` guard). Observed sequence: `b853576e…` 510 L (also the frozen copy) → `12b835b6…` 626 L → `dadc777e…` 656 L, mtime `2026-10-20 12:22:22 -0300`. kama's nine `*.json` files and their digest stayed `bf9068d8…` / 9 files / 72 rows through all of it (recomputed, not quoted).

Consequences for `mutants.py`, in tameshi's terms: "A moved substrate needs a re-pin, never a re-interpretation of the old table" (`SKILL.md:1236-1237`). The before-arm sweeps the frozen `b853576e…` bytes and records `fd49ff7c…` as the round-16 bytes with the four-line delta; the after-arm sweeps whatever `check.py` sha the C1 owner hashes at dispatch and **prints that sha in the receipt**. Do not assert `sha == P` (that would SETUP-fail) and do not let the table imply one harness for both arms. All frozen line anchors below (`:28-30`, `:331-346`, `:493`) resolve on the 510-line frozen copy only; current-file anchors are labelled as such.

## Operational traps the counting command must close

1. **Zero-work green.** `load_matrix()` globs its directory for `*.json` and returns `tests=[]` with no error (`check.py:151-176`; `main` calls it bare at `:610`), and `code = 0 if doc["failures"] == 0 else 1` (`check.py:639`, current bytes). A one-file mutant copy in an otherwise empty scratch directory, invoked with an explicit `--probe`, runs **zero tests and exits 0** — every mutant would "survive". Each mutant must live in a full `cp -a` of the directory, and the run must assert `tests == 72` plus the matrix digest before adjudication; digest mismatch or `tests != 72` is SETUP, never green.
2. **Digest scope.** `matrix_digest()` uses `CHECK.parent.glob("*.json")` (`measure.py:286-290`), so the digest is a property of the copy's directory, not of the lane. Compute it on the same copy the mutant runs from.
3. **Unreachable duplicate grade path (current bytes).** The C1(a) repair left the old parse-and-grade block below `return record` at `check.py:474`; the dead copy spans `:475-494` (`try: doc = json.loads(...)` … `record["passed"] = (` … `return record`). An edit to those 20 dead lines is an *equivalent* mutant the uniqueness gate cannot see (the text still occurs once) and the suite cannot kill. Either the owner deletes the dead block, or `mutants.py` classifies any spec site at/after `:475` as `EQUIVALENT (unreachable)` with the reason; a survivor there is not a gap. The malformed-output class itself is now closed: `probe_output_row` returns "rows[0] is <type>, not an object" (`check.py:370-395`), which is the recorded-failure shape C1(a) asked for.

## Proposed move (one, bounded)

**One kill-attribution contract across both counting commands.** `mutants.py` and `controls.py` emit tameshi's vocabulary verbatim — `CHECK: all unique`, `CONTROL: GREEN|RED`, one `MUTANT <id> detector=<pair|fc:<name>> <KILLED|SURVIVED|INCONCLUSIVE|NOT-INJECTABLE|EQUIVALENT> rows=[…]` line, `MUTATE_RESTORE: OK|DRIFT`, closing `MUTATE: DONE (before=… after=…)` so the round-16 advice's five survivor classes become named kills or named equivalents, and the C2 "accepted-bad before → after" is directly comparable:

- **C1 before-arm:** frozen `b853576e…` + the pair detector only → expected `killed=0 survived=5 inconclusive=0` (the round-16 record, re-pinned).
- **C1 after-arm:** current `check.py` + pair + `fault-controls.py`, where **each mutant is run against each fault-control wrapper, not only against the pair**. This is the non-obvious part: running the fault controls against the pristine checker measures the checker, not the detector set; the after-metric only moves if the mutants meet the wrappers. Kill rows name the wrapper and the failing row names.
- **C2, split by substrate:** (i) gate half — `controls.py --gate --before <frozen check-receipt> --after <current check-receipt>` drives synthetic v2 receipts from `mkdtemp`; accepted-bad must fall to zero, every rejection must be exit 1 with a named check id, and no control may be satisfied by exit 2 (setup) — `QUALITY.md:61-63`; this runs today, without llama-server. (ii) producer half — `controls.py --producer --before <frozen tool+gate> --after <v2 tool+gate>` against fake servers; this is kama-only and never a tameshi leg.
- **Wrappers:** `mkdtemp`, removed in `finally`, identity wrapper first, one corrupted field per wrapper, and the wrapper preserves the probe's own exit code so a field failure cannot masquerade as an exit failure. Timeout control scoped with `--only` to one row (the probe-side bound is `PROBE_TIMEOUT = 30`, `check.py:51`), so the cost is one row, not 72.

Affected axes: **calibration up** (attribution, denominator, pre-registered misses, five survivor classes resolved by name), **operability up** (one grammar, literal exits, SETUP/DEGRADED split, no traceback), **contract unharmed** (wrappers are scripts under `/tmp`; matrices unchanged; L1 still runs it).

## Risks

- Re-expressed defects: a round-16 class whose `old` no longer exists must be `NOT-INJECTABLE`, never counted as killed; if all five remain injectable the before/after pair stays comparable, otherwise the pair's meaning must be stated.
- **Staggered landings.** The gate half of C2 already accepts v2 while the producer is still v1, and `check.py` moved twice during this scan. `controls.py` and `mutants.py` must print both subject shas (gate + producer; check.py + probe) and treat a schema/subject mismatch as SETUP, not as an accepted-bad or a survivor.
- **Dead code is mutation-invisible.** `check.py:474` returns before the repaired-over block at `:475-494`; a mutant there is equivalent, not a gap. Either delete the block in the C2/C1 cleanup or classify it `EQUIVALENT (unreachable)` by site.
- Over-broad wrappers corrupt several fields/rows and make a kill unattributable; scope each to one field and named rows.
- A wrapper that also alters the exit code confounds exit grading; assert exit preservation in the wrapper's own identity control.
- The timeout control is the only behavioral input that kills the round-16 `timeout-pass` class (frozen `check.py:319-321`); without it that class stays a named survivor.
- Do not present the kill rate as a gate: "Bands are a report convention, not a pass/fail gate." (`SKILL.md:335`).

## Verification (for L1; not run here)

1. `python3 tests/probe-verdicts/fault-controls.py --selftest` → exit 0; then `--before /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/frozen/tests_probe-verdicts_check.py --after tests/probe-verdicts/check.py` → before exits 1 with named rows, after exits 0 with the identity wrapper.
2. `python3 .ufo/waves/round-17/c1/mutants.py --before` → expect `MUTATE: DONE (… killed=0 survived=5 inconclusive=0 …)`, a re-pin line for `b853576e…`, and `fd49ff7c…` recorded with its four-line delta; `--after` → expect the dispatched `check.py` sha printed, then every round-16 class `KILLED` with `detector=fc:*` and row names, or `EQUIVALENT` with reason.
3. `python3 .ufo/waves/round-17/c1/mutants.py --restore-check` → `MUTATE_RESTORE: OK`, matrix line `9 files, set sha256 bf9068d8…` before and after, `git status --porcelain -- tests/probe-verdicts` empty.
4. `python3 tests/llamacpp-live/controls.py --gate --selftest` → exit 0, synthetic v2 receipts rejected by the frozen gate (exit 1 + check ids) and accepted by the current gate; `--producer` → before-arm accepted-bad > 0, after-arm accepted-bad = 0, a forced teardown exception yields a receipt and exit 2, not a traceback. Both halves print the gate/producer shas they ran.
5. `python3 tests/llamacpp-live/check-receipt.py --selftest` still exits 0 and the round-16 receipt (`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-16/live/receipt.json`) still validates unchanged.

## Limitations

- Read-only; nothing executed beyond checksums, a `sed` extraction, and read-only `git show/log`; no gate, mutant runner, control suite, or `measure.py` run.
- Tameshi's `corpus/knowledge/*` notes and `tools/mutate-and-run.sh` were outside the bounded read; anchors that resolve into those notes are quoted second-hand through `SKILL.md` [INFERENCE].
- No Python subject appears among tameshi's recorded legs [INFERENCE from the named targets]; transfer to a threaded stub harness (`ThreadingHTTPServer`, per-row subprocess) is unmeasured.
- The round-17 files moved while this scan ran: `check.py` was observed at three shas and `check-receipt.py` at 1189 lines with v2 support. Treat the cited current-bytes shas as snapshots, not as dispatch pins.
- The dead block at `check.py:475-494` is a reading of the `dadc777e…` snapshot; if a sibling deletes it, that risk closes and the `EQUIVALENT (unreachable)` clause becomes moot.

## Installs

None. Existing `python3`, `git`, `sha256sum`, `sed` sufficed; no tool was installed or updated.
