VERDICT: partial — every documented sentence is literally accurate except the check.py exit map and two live-tool guarantees; the rest are true-but-weak today and become stale/completeness-invalid after C1/C2 unless SKILL.md is edited.

## Scope and method

Read-only seat. Read `SKILL.md` §Local gate/probe registry (294-306) and §Round-16 (507-553), then verified each grading claim against the three implementations and the committed matrix/receipt bytes. No gate, measurement, mutant, control or server was executed; scratch was not used.

Baseline identity — **the worktree changed during this seat**, so two states were observed:

| File | First read (matched frozen + master) | Current in-flight read |
|---|---|---|
| `tests/probe-verdicts/check.py` | `b853576e…6145762` = frozen copy | `e3eb484e…b2d2895a` (moved through `12b835b6`, `0354b632`) — C1 invariants, malformed path, duplicate-name selftest, uncommitted |
| `tests/llamacpp-live/check-receipt.py` | `6b9576a1…4b09ced6` = frozen copy | `d4ed2c24…c4df72cf` (moved through `5ed600b2`, `65ac08b7`, `a3f939ac`) — v2 schema/ids + v2 health body, uncommitted |
| `tools/kama-llamacpp-live.py` | `b8c5e8d4…2f4fe4` = frozen copy | `b8c5e8d4…2f4fe4` — still frozen (no C2 producer change yet) |

The sentence-by-sentence table below is written against the **frozen baseline**, and each row says what the planned C1/C2 change does to it. A "Worktree drift observed during this seat" section at the end records what the in-flight bytes already do and the gaps that determine whether the edited sentences will be true or stale when the wave closes.

Status vocabulary: **TRUE** (literal code match), **TRUE-BUT-WEAK** (code does what is said, guarantee is vacuous for the failure a reader fears), **FALSE** (claim contradicted today), **STALE-AFTER-C1/C2** (claim remains literally true but omits what the change adds, so the row misdescribes the gate).

## §Local gate/probe registry (294-306)

This section contains **no sentence that claims anything about `check.py`, `kama-llamacpp-live.py` or `check-receipt.py`**. Its four rows are `bash tools/kama-probe.sh` gates only. The only adjacent guarantee sentence is:

| Line | Quote | Status today | Effect of C1/C2 |
|---|---|---|---|
| SKILL.md:298-299 | "These checks are lane-local evidence, never native judgment or mission-completion authority." | TRUE for the four `kama-probe.sh` rows; the three files are documented only at 533/535/536 | Unchanged. Needs no edit, but the later rows are not covered by this sentence. |

Registration gap (inference): the section is titled "Local gate/probe registry" yet the round-16/17 local gates are registered only in a second table at SKILL.md:531-536. If C1 lands `tests/probe-verdicts/fault-controls.py` and C2 lands `tests/llamacpp-live/controls.py` as counting commands, neither gains a row here. [INFERENCE] A reader looking up "local gates" finds three gates missing from the registry section.

## §Round-16 (507-553) — sentence inventory

### Vocabulary and decision-table prose (not claims about the three files)

| Line | Quote (<=25 words) | Status today | C1/C2 effect |
|---|---|---|---|
| SKILL.md:509-512 | "`tools/kama-probe.sh` `VOCAB` is the authority; its `--help` text and the `diff_baseline` whitelist repeat the same seven words by hand." | TRUE; about the probe, not the graders | None |
| SKILL.md:516 | "`GET /v1/models` → 503 whose JSON `error` has `message` exactly `Loading model`, `type` exactly `unavailable_error`, integer `code` 503" | TRUE; this is the contract the 17 `MODEL_LOADING` matrix rows grade (`check.py` rows pass today) | C1's route-match makes "the probe actually requested `/v1/models`" enforced; fault controls make the grading fail-capable. No wording change strictly required. |
| SKILL.md:517 | "Any other 503 (`no slot available`, ...) | unchanged (`FOREIGN_SERVICE`)" | TRUE; graded by `Overbroad503`/`NearMissTriple`/`NonLoadingStatuses` | None |
| SKILL.md:519-523 | "match parsed fields, never bytes" | TRUE; `EnvelopeShapes` rows cover key order, pretty print, padding | None |
| SKILL.md:523-524 | "The probe needs python3 for this verdict; without it the old `FOREIGN_SERVICE` reading returns." | TRUE as probe behaviour; **not graded by `check.py`** — no matrix row exercises `HAVE_PY=0` | [INFERENCE] C1 does not add such a row (matrix files are frozen), so this sentence stays an unverified probe claim. |
| SKILL.md:524 | "`check` and `snapshot` exit 2 on it" | TRUE for `kama-probe.sh check`; the bare word `check` now collides with `check.py` | [INFERENCE] After C1 the collision gets worse (`check.py` exits 2 only on harness fault, never on a `MODEL_LOADING` row). Wording should say `kama-probe.sh check`. |
| SKILL.md:534 | "the frozen arm fails exactly the `MODEL_LOADING` rows, the current probe passes all" | TRUE for the round-16 `measure.py` detector (pins: 72 tests, 17 loading, matrix digest `bf9068d8…`) | **STALE-AFTER-C1**: `mutants.py` becomes the counting command; this row still points at the round-16 pair, which does not detect grading weakening (next row). |

### Probe verdict stub matrix row (SKILL.md:533)

| Line | Quote | Status today | C1 effect |
|---|---|---|---|
| 533 exit map | "0 all rows pass, 1 a row failed, 2 harness/schema error" | **FALSE at the frozen baseline**: a probe whose `rows[0]` is not an object raised `AttributeError` from `row.get` at frozen `check.py:338`, outside the guarded block, and `main` caught only `HarnessError` — traceback, exit 1, no row record. **TRUE in the in-flight C1 bytes**: `probe_output_row` (`check.py:370-395`) rejects non-object `rows[0]`/missing string fields/non-bool drift, and `grade` records `malformed probe output` with `passed False` (`check.py:451-456`, exit 1). | C1 as landed makes this sentence TRUE; no wording change needed. |
| 533 grading | "grades verdict, reason, exit and drift" | TRUE at the frozen baseline (`check.py:340-347`). `served_model` is recorded and discarded (`check.py:297`, `337`); `requests` are recorded and only asserted non-empty (`323-327`); nothing asserts `GET /v1/models`. Drift is graded only as the derived invariant `verdict != MODEL_OK`; the matrix schema has no `drift` key. In the in-flight C1 bytes the row now also grades `served_model_ok` and `route_ok` (`check.py:461-471`), so the sentence is **already stale** in the worktree. | **STALE-AFTER-C1**: the row must add `served_model` and route-match. The 5/5 surviving grading mutants (`MutateHarness.md`) show the original four comparisons were not independently load-bearing: reason/verdict fail together (17/17), exit/drift never mismatch (0/0), case and timeout paths unexercised. |
| 533 selftest | "`--selftest`: full matrix plus 4 malformed tests rejected" | TRUE: `SELFTEST_MALFORMED` has exactly 4 entries (`check.py:359-380`); commit `726f737` corrected the docstring/help from 3 to 4 (56 grading bytes unchanged) | Remains TRUE (schema-only). **STALE-AFTER-C1** if the row still implies selftest is the fault detector: the fail-capable detector is `fault-controls.py`, a separate command the row does not name. |
| 533 pins | "literal expectations (72 rows, 9 families, 17 `MODEL_LOADING`)" | TRUE: 9 files, 72 rows, 9 distinct `family` values, 17 `MODEL_LOADING` (recounted from the nine JSON files) | Unchanged by C1 by the hard constraint (nine files byte-identical, no new `*.json`); stays TRUE. |
| 533 write scope | "stdout only; loopback stub servers on ephemeral ports, closed after each row" | TRUE: binds `("127.0.0.1", 0)` (`check.py:309`) and `shutdown()`/`server_close()` in `finally` (`352-356`); the single `closed` row (`AuthAndDead.closed-port-connection-refused`) binds and releases an ephemeral port without a server | Unchanged by C1 |

C1 feasibility facts (observed, not verdicts):

- `served_model` is derivable for all 72 rows from the stub body plus the verdict, with no matrix edit. Simulating `served_ids` precedence (`tools/kama-probe.sh:335-370`): 8 `MODEL_OK` rows and 3 `MODEL_MISMATCH` rows resolve to a comma-joined unique id; the other 61 rows (`17 MODEL_LOADING`, 37 `FOREIGN_SERVICE`, 5 `UNAUTHORIZED_SERVICE`, 1 `DEAD` closed, 1 `NOT_HTTP`) resolve to `-`; **zero** non-OK/non-MISMATCH rows carry string ids, so the rule "OK/MISMATCH → joined ids, else `-`" is exact on this matrix.
- Route-match is checkable for 71 stub rows: 70 declare `/v1/models` in `routes`; `LoadingEnvelope.every-non-frontend-path` declares none and relies on `default_route` 503. All stub rows record every request via `_seen.append` (`check.py:239`), including the raw-close route. The one `closed` row must stay exempt (no server).
- The grading code the round-16 mutants attacked is identical to the current/frozen bytes: `MutateHarness.md` ran `fd49ff7c…` = blob at `b8e485c`; `726f737` changed only the docstring "3"→"4" and the `--selftest` help string, so the 5/5 survival evidence transfers to `b853576e`.

### Live llama.cpp lifecycle row (SKILL.md:535)

| Line | Quote | Status today | C2 effect |
|---|---|---|---|
| 535 exit 0 | "0 all 10 checks pass" | TRUE count: exactly 10 ids are appended (`health_ready` 938, plus 946/950/955/962/984/991/1024/1029/1037). **Semantically weak**: `health_ready` passes on status 200 alone (`938-939`), so 200 `{"status":"degraded"}` passes; `teardown_exited` passes when a returncode exists (`1024-1028`), so self-exit rc 0 with `sigterm_sent false` or SIGKILL `-9` passes; `teardown_port_closed` passes on `port_refuses` alone (`1029-1032`); `loading_envelope_exact` is stored (`922`, `848`) and consumed by no check, so a non-exact loading body still yields 10/10 and exit 0 | v2 makes the guarantee TRUE; "all 10" becomes **STALE** if v2 adds an 11th check id, and truthful if v2 keeps 10 ids and strengthens predicates. |
| 535 exit 1 | "1 a check failed" | TRUE (`kama-llamacpp-live.py:1000`) | Unchanged |
| 535 exit 2 | "2 setup error (port refused or not owned, child exited, unreadable registry)" | TRUE: registry unreadable → `SetupError` (`200`); refused/registered/in-use port (`238`, `246`); not-owned/unproven owner (`479-490`, `540`); child exit (`496`, `509`, `540`) all map to exit 2 (`1001-1005`) | Unchanged |
| 535 exit 3 | "3 model digest mismatch before launch" | TRUE (`801`, before `Popen`) | Unchanged |
| 535 pins | "asset sha256 `753bfa…` (S038); model sha256 as in the command (S039); refused ports 8080, 34113, every registry port and every listening port" | S038/S039 accurate (`corpus/SOURCES.md:50-51`). "every listening port" is overstated: the explicit-port path returns the port on a timeout/reset `OSError` without a proven listener (`241-246`), and the default `bind(:0)` path cannot pre-check a listener (`221-233`) | Unchanged by C2; [INFERENCE] wording should say "every proven listener". |
| 535 write scope | "one child process on 127.0.0.1, torn down" | TRUE on the normal path. **FALSE on a teardown-internal raise**: the `finally` stores `{'error': …}` (`1019-1021`) then unconditionally indexes `['returncode']`/`['port_refuses']` (`1026`, `1031`) → `KeyError` escapes `main` before `_emit` (`1052`), so no receipt and no proven teardown [INFERENCE: requires `teardown()` to raise] | C2's "receipt always written on internal faults, exit 2" makes the sentence TRUE only if teardown is also guaranteed; wording should add "receipt written". |

### Live receipt gate row (SKILL.md:536)

| Line | Quote | Status today | C2 effect |
|---|---|---|---|
| 536 exits | "0 valid, 1 invalid (every problem listed), 2 unreadable" | TRUE: unreadable/non-JSON → 2 (`1124-1130`); invalid → prints every problem (`1138-1141`); valid → 0 | Must accept v2 as 0 while v1 still validates unchanged. |
| 536 pins | "pass the pins; without `--expect-server-sha256` a receipt from another build can validate" | TRUE: each `--expect-*` is optional and compared only when given (`289-291`, `312-314`); `install_tree_sha256` is recomputed for self-consistency, not authenticity | Unchanged |
| 536 selftest | "`--selftest`: single-field mutations rejected (count printed)" | TRUE: 26 mutation cases plus the unreadable case, all expected rejected; count printed (`1094`). Cases include `schema-id-changed`, `envelope-flag-inconsistent`, `ownership-unproven`, `tool-sha-mismatch-expect`. | Count changes when v2 mutations (health body, SIGKILL teardown, non-exact envelope) are added; sentence stays TRUE, understated. |
| 536 checks | "10 check ids; checks re-derived from stored captures and probe output" | TRUE for v1 at the frozen baseline: exactly 10 required (`53-64`), any other id rejected, each re-derived from captures/probe output. **But the re-derivation reuses the producer's weak predicates**: health = status 200 only (`628-637`), `teardown_exited` = returncode non-null (`745-757`), `teardown_port_closed` = `port_refuses` true (`758-770`), `loading_envelope_exact` = a bool field re-derived only for consistency (`420-432`). `teardown.sigterm_sent`/`sigkill_sent` are never read in validation. In the in-flight C2 bytes the gate now accepts schema v2 with **11** ids (`REQUIRED_CHECKS_V2`: `teardown_graceful`, `loading_envelope_graded` replace `teardown_exited`) — see drift section. | **STALE-AFTER-C2**: "10 check ids" describes only v1; the row must say v1=10 / v2=11 and name the strengthened predicates. |

### Prose after the table (538-553)

| Line | Quote | Status today | C2 effect |
|---|---|---|---|
| 538-540 | "The live run is a lane-owned fixture on an unregistered loopback port." | TRUE (`pick_port` binds `127.0.0.1:0`, `221-233`; receipt records the refusal set) | Unchanged |
| 540 | "grades no model quality" | TRUE: no check inspects weights, tokens or latency | Unchanged |
| 546 | "a passing receipt says nothing about weights, quality or timing of any real deployment" | TRUE by construction (fixture model, alias is the harness's own `--alias`) | Unchanged; C2 does not widen scope. |
| 549-552 | "while loading it answers `/v1/models` with the 503 envelope, and the round-16 live receipt captured exactly that body" | TRUE: `.ufo/waves/round-16/live/receipt.json` has `loading_503.path=/v1/models`, `status=503`, body `{"error":{"message":"Loading model","type":"unavailable_error","code":503}}`, `loading_envelope_exact=true` | C2's added grading turns "captured" into "enforced"; the sentence stays TRUE. |

## What the C1/C2 changes make true, false or stale — summary

At the frozen baseline: **false** were `533` "2 harness/schema error" (malformed `rows[0]` → traceback, exit 1), `535` "torn down" on a teardown raise (no receipt), and `535` "every listening port" (timeout/reset path returns the port). **True but not independently load-bearing** was `533` "grades verdict, reason, exit and drift" — the comparisons exist, but the pair detector could not see any of the five grading-weakening mutants (`MutateHarness.md`), and `served_model`/route-match were not graded. **True but vacuous guarantees** were `535` "0 all 10 checks pass" (degraded health, SIGKILL, non-exact loading all pass) and `536` "checks re-derived" (re-derives the weak predicates). **Stale after the planned edits** would be `533` grading/selftest columns, `534` (counting command becomes `mutants.py`), `536` "10 check ids" and the selftest count.

In the bytes observed during this seat, C1 has landed (`check.py`, latest `e3eb484e…`): the malformed-output exit map is now true, and the grading row now covers `served_model` and route-match, so `SKILL.md:533`'s "grades verdict, reason, exit and drift" is **already stale** and needs the two invariants added. C2's gate has only partially landed (`check-receipt.py`, latest `d4ed2c24…`): it accepts a v2 schema with 11 ids and a strengthened v2 health body, so `SKILL.md:536`'s "10 check ids" is **already stale for v2**, but `teardown_graceful` and `loading_envelope_graded` still have no evidence re-derivation (drift section). The C2 producer (`tools/kama-llamacpp-live.py`) is untouched, so every `SKILL.md:535` guarantee sentence still stands exactly as classified above until that file changes.

## Worktree drift observed during this seat (advice, not verdict)

These are concrete gaps between the in-flight bytes and the C1/C2 claims the SKILL rows are about. Both files moved repeatedly while this seat read them; this section is a **snapshot at `check.py` `e3eb484e…` and `check-receipt.py` `d4ed2c24…`**, and every line number below is as of that snapshot. A final re-check at `check.py` `32be75de…` / `check-receipt.py` `5ee34ca5…` found items 1-2 resolved, items 5-6 unchanged, and items 3-4 still holding (no `teardown_graceful` or `loading_envelope_graded` re-derivation block exists yet). Re-hash and re-open before acting.

1. **Resolved during this seat.** The dead duplicate grading block seen at `12b835b6` (old `json.loads`/`row.get` comparison after `return record`) is gone; only the live block remains, now including `served_model_ok` and `route_ok` (`check.py:461-471`).
2. **Resolved during this seat.** The `--selftest` duplicate-name claim in the docstring (`check.py:30`) is now implemented: `run_selftest` writes the same test name into two temporary files and requires `load_matrix` to reject it (`check.py:517-553`). `SKILL.md:533`'s "full matrix plus 4 malformed tests rejected" is still true but now understates the selftest (5 cases: 4 malformed + 1 duplicate-name); the printed label still says "malformed tests" for all five.
3. **C2 gate v2 is still only partly fail-capable.** `RECEIPT_SCHEMA_V2` (`check-receipt.py:59`) and `REQUIRED_CHECKS_V2` (`88-90`: `teardown_graceful` and `loading_envelope_graded` replace `teardown_exited`, 11 ids) are wired into acceptance (`205-208`, `653-660`). The v1-path checks now use `claim()` for health, `models_alias_id`, `models_owned_by_llamacpp`, `metrics_not_enabled` and `props_alias` (`662-771`), and v2 `health_ready` adds the exact ready body (`690-696`). But:
   - **`teardown_graceful` has no re-derivation block.** It is only checked for presence, `passed is True`, and `observed` being an object; v2 only validates that `sigterm_sent`/`sigkill_sent`/`alive_at_teardown_start` are booleans (`618-624`). A v2 receipt with `{"passed": true, "observed": {}}` plus `sigterm_sent false, sigkill_sent true, returncode -9` would validate — the exact case C2 must reject.
   - **`loading_envelope_graded` has no re-derivation block.** `loading_envelope_exact` remains a consistency field (`452-464`), never required `True`; a v2 receipt can declare the check passed with no evidence.
   - Consequence: do not update `SKILL.md:535/536` to claim v2 fail-capability until both blocks and matching mutations exist.
4. **C2 gate selftest is v1-only.** `_selftest_receipt()` builds `"schema": RECEIPT_SCHEMA` (`check-receipt.py:923`), and `RECEIPT_SCHEMA_V2` is referenced nowhere after line 59. The mutation list has no v2 case (SIGKILL teardown, 200 `{"status":"degraded"}`, non-exact loading body, missing `alive_at_teardown_start`). The 26-mutation count in `SKILL.md:536` therefore stays unchanged and says nothing about v2.
5. **C2 producer untouched.** `tools/kama-llamacpp-live.py` is still the frozen v1 bytes: `health_ready` grades status only (`938-939`), `loading_envelope_exact` is stored and consumed by no check (`922`), `teardown_exited` grades returncode presence (`1024-1028`), and the teardown-error `KeyError` path (`1019-1028`) still escapes before `_emit` (`1052`). Every `535` finding above therefore remains current.
6. **C1 fault controls have appeared.** `tests/probe-verdicts/fault-controls.py` exists (530 lines) with faults F1 reason suffix, F2 exit flip, F3 drift negation, F4 verdict casefold, F5 served_model forgery, F6 route skip, F7 hang, F8 malformed stdout, and the rule "DETECTED ⇔ every run exits 1 and every faulted row has `passed: false`" (file header). That matches the C1 counting-command claim and is the detector `SKILL.md:533` does not yet name. Also note the untracked `tests/probe-verdicts/__pycache__/` left by an execution — remove before commit.

Corrected v1/v2 facts for the gate (replacing the earlier v1-equality observation): v1 receipts still take the `REQUIRED_CHECKS_V1` 10-id path and the old status-only health/returncode teardown re-derivations, so "still validates v1 receipts unchanged" holds in these bytes. v2 receipts take the 11-id path; `health_ready` is strengthened (status + exact ready body + `claim()`), while `teardown_graceful` and `loading_envelope_graded` are not yet re-derived from evidence. The producer already stores what a v2 gate needs: `captures.health.body` (`ready_captures`, `567-578`) and `loading_503.body` (`919-922`). `teardown.sigterm_sent`, `sigkill_sent`, `term_wait_ms` are produced (`659-683`) and still never validated as predicates. The committed round-16 receipt has `returncode 0, sigterm_sent true, sigkill_sent false, term_wait_ms 3`; the gate's selftest fixture uses `returncode -15, sigterm_sent true, sigkill_sent false` — a v2 "documented graceful exit" predicate must accept both shapes if v1 receipts are to keep validating.

## Limitations

- All statuses are from byte reading and static enumeration; no gate, probe, server, measurement, mutant or control was executed, so this file offers no numeric verdict.
- Two gate files were rewritten by sibling seats while this seat was reading them. The in-flight findings identify `check.py` `12b835b6…` and `check-receipt.py` `65ac08b7…`; later edits may supersede them, so re-hash before acting on the drift section.
- The 5/5 survival figure is quoted from `MutateHarness.md`; its transfer to the frozen `b853576e…` bytes rests on the `726f737` diff (only the "3→4" docstring/help lines).
- The `served_model` derivation was simulated with a Python reading of `served_ids` precedence (`tools/kama-probe.sh:335-370`), not by running the probe.
- SKILL.md line numbers are working-tree numbers at tip `cff9e62`; SKILL.md is not in the frozen manifest, so numbers move with edits.
- Rows that are "true but not graded" (python3-less `MODEL_LOADING`, "every listening port") are flagged [INFERENCE] where the guarantee is interpretive.

Installs/updates: none (existing `git`, `python3`, coreutils sufficed).
