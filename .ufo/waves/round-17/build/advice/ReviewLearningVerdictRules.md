VERDICT: partial — the C1/C2 claim structure is admissible as two axis moves without score or new row, but only `quality: improved` is author-earnable this round; `expansion` can only be `unchanged`, `discernment` cannot be author-earned at all, and the C1 counting design as written over-attributes kills to check.py.

## Scope and method

Read-only seat: I read the protocol, the lane scorecard, the round-17 build spec (item texts, not
the in-flight drafts), the frozen pre-round copies, the nine probe matrices, the live tool and both
receipt gates. I ran no lane gate, no `measure.py`, no `mutants.py`, no `controls.py`, and wrote
only this report. Paths are relative to `/home/vgpnk/Projects/shokunin/kama-shokunin` unless absolute.

## 1. What the author can earn — trend verdicts

LEARNING.md is per-round: "The three trends — one verdict each, every round"
(`/home/vgpnk/Projects/kimi-shokunin/skills/shokunin/protocol/LEARNING.md:26`). Claim axes and
trend axes are different vocabularies; C1/C2 land axis verdicts, not trend verdicts. For round 17:

| Trend | Author may write | Basis (quote + location) | Outside check needed? |
|---|---|---|---|
| **expansion** | **unchanged** | `improved` needs "net new admitted entries on uncovered ground, each citing its coverage-map row" (LEARNING.md:33). The round's knowledge work is an append: "Draft an append-ready section for" (`corpus/knowledge/llamacpp-loading-lifecycle.md`; `.ufo/waves/round-17/build/spec.json`, `ScribeKnowledgeTeardown`). C2 explicitly adds no capability row, and `Rows enter only through a round that demonstrates the capability running` (`/home/vgpnk/Projects/shokunin/AXES.md:62-63`). New SOURCES rows S042–S045 are curation, not admitted entries. | No for `unchanged`. |
| **quality** | **improved, conditional** | `improved` when "a weaker entry is superseded by a stronger one, or stale entries re-verify" (LEARNING.md:34). The appendix can deepen/re-verify `llamacpp-loading-lifecycle.md` against `server-context.cpp:5297`, `server.cpp:519-523`, `server.cpp:590`. Condition: name the entry-level before→after (anchors added / stale claims superseded), re-verify, and fail-closed if an admitted entry is found false. | No for the author's `improved`; the outside sample still governs discernment. |
| **discernment** | **unchanged only** | "Self-assessed taste is not discernment" (LEARNING.md:42); "at least one admit and one reject" (`:44`); "A subagent the lane dispatched is still the lane" (`:45-46`). Every build/falsify reviewer is lane-dispatched, so green suites are author evidence. | **Yes**; the outside sample is the only path to `improved`. |

Concrete consequences:

- **Do not write `expansion: improved`** on the strength of "hardened capability" or the four new
  SOURCE rows. That would be a fresh overclaim and would itself harm calibration
  (`AXES.md:15`: "overreach caught"). If L1 instead admits a genuinely new knowledge entry on
  uncovered ground, `expansion: improved` becomes earnable — but then it needs `source:` citing a
  `mined` row and a coverage-map row, and the appended section must not be relabelled as that entry.
- **Do not declare C1 or C2 `unprovable-but-better`.** Both have counting commands; the exploratory
  route requires a named non-author reviewer and "no counting command is required"
  (`AXES.md:44-46`), and "At most one exploratory claim per round" (`AXES.md:51`). Retro-fitting it
  after measurement is self-attestation, which LEARNING.md:48-49 forbids.
- `Growth without quality is not learning` (LEARNING.md:37): if quality lands `improved` but an
  admitted entry later fails its re-check, the round is a trade, not an admission
  (`AXES.md:34-35`: "a trade anywhere is not an improvement").

## 2. What the non-author check must see

### C1 (calibration)

1. **Both detector modes at the final commit.** `mutants.py --check
   .ufo/waves/round-17/frozen/tests_probe-verdicts_check.py --detector pair` and `--detector full`,
   then the same against the committed `tests/probe-verdicts/check.py`. The reviewer must see
   `applicable`, `killed`, `survived`, `site_found`, and per-mutant `evidence`
   (`.ufo/waves/round-17/build/spec.json`, `C1MutantRunner`), plus the exact command lines and exit codes.
2. **A per-field kill mapping, not "any observable difference".** The spec says "Killed = any
   observable difference versus baseline"; that is too weak for a calibration claim. Require
   M1↔F1 (reason), M2↔F2 (exit), M3↔F3 (drift), M4↔F4 (verdict case), M5↔F7 (timeout),
   M6↔F5 (served_model), M7↔F6 (route skip), M8↔F8 (malformed). Otherwise a kill caused by an
   unrelated formatting/error difference is credited to the field it was supposed to prove.
3. **Detector/subject separation.** The `before` bundle is frozen check.py + pair; the `after` bundle
   is current check.py + pair + fault controls. If all five legacy mutants are killed only by the
   fault controls, the honest finding is "the suite is load-bearing", not "check.py grades reason,
   exit and drift". The report must show pair-only survivors on current check.py (the round-16
   expectation is 5 survivors) separately from the full-mode count. Otherwise C1 repeats the
   overclaim it repairs.
4. **A positive control in `fault-controls.py`.** The spec's DETECTED rule is "exit 1 AND every
   faulted row has `passed: false`"; a check.py that fails every wrapper output would detect every
   fault vacuously. Require a P0 passthrough wrapper on the same `--only` row set that check.py
   accepts (exit 0, all rows passed). This is the lane's own precedent: "positive controls defeat a
   vacuous reject-all implementation" (`SCORECARD.md:496`).
5. **Fault failure mode is the field, not the parse path.** For F1–F5 the failing row must have a
   field mismatch and no `error`; only F8 may fail through the malformed-output path. The `why`
   field must say which comparison failed.
6. **`served_model` is body-derived, not verdict-derived.** The probe reports comma-joined
   `data[].id` and initialises to `-` (`tools/kama-probe.sh:527-529`, `:455`). An expected value
   computed from the verdict is circular; require it from the row's literal
   `routes['/v1/models']`/`default_route` body (ids → comma-join; no model array → `-`). The current
   grader reads the field but never compares it (`frozen tests_probe-verdicts_check.py:335-336`,
   `:340-347`).
7. **Route-match is probe-contract evidence, not a check.py kill.** All stub rows already record
   `GET /v1/models` (the stub appends before responding, `frozen tests_probe-verdicts_check.py:214`;
   raw-close is explicitly recorded, `:224`), so no matrix edit is required. But a check.py mutant
   cannot change the subject probe's requests; do not count M7 as evidence that check.py's grading is
   load-bearing.
8. **Malformed output red→green.** The frozen except tuple
   `(json.JSONDecodeError, KeyError, IndexError, TypeError)` (`:332`) does not catch `AttributeError`,
   so `{"rows":[["x"]]}` and a non-object `rows[0]` end in a traceback. The reviewer must see that
   variant accepted on the frozen check.py (no parseable JSON / exit 2) and rejected on current
   (exit 1, parseable JSON, row-level `error`, `passed:false`).
9. **Hard constraint intact.** Nine matrix files, byte-identical; set digest
   `bf9068d89e4cb8a080167cb32cc818943d717a65fcbd21edb2b8256e22771f32` and 72/17 breadth
   (`.ufo/waves/round-16/measure.py:281-283`); no new `*.json` in `tests/probe-verdicts/`. The
   reviewer must re-run the digest and list the directory.
10. **QUALITY row correction.** KQ19 currently asserts "verdict, reason, exit and drift are all
    graded" (`corpus/QUALITY.md:109`); unless a new row names and supersedes that clause with a
    round-17 lesson behind it, the gate still overclaims. `every criterion cites the lesson that
    produced it` (LEARNING.md:61); an ungrounded criterion is `discernment: harmed`
    (LEARNING.md:35).

### C2 (operability, capability hardening)

1. **Before/after accepted-bad counts from the actual frozen pair.** `controls.py --tool
   .ufo/waves/round-17/frozen/tools_kama-llamacpp-live.py --gate
   .ufo/waves/round-17/frozen/tests_llamacpp-live_check-receipt.py --json` must show a nonzero
   `accepted_bad` (K1 health-degraded, K2 bad envelope, K3 self-exit, K4 SIGKILL, K5 nonzero exit;
   K6 must show no receipt), then the current pair must show `accepted_bad 0` and `good_ok true`,
   with per-control `failed_checks` and `receipt_written`.
2. **K0 is the positive control.** A good fake server must be accepted by both tool and gate; a
   reject-all v2 check would otherwise pass K1–K7 vacuously.
3. **v1 receipts unchanged.** The frozen round-16 receipt `.ufo/waves/round-16/live/receipt.json`
   must still validate (exit 0) under the patched gate, while a v2 receipt validates on the v2 branch.
   The current gate names "exactly 10" checks
   (`frozen tests_llamacpp-live_check-receipt.py:614-621`) and treats `loading_envelope_exact` as
   "a receipt FIELD (bool|null), not a check" (`:420`); v2 adds an eleventh check, so the required
   set must dispatch on `receipt["schema"]`.
4. **The v2 predicates are source-cited, not prose.** The reviewer must open:
   - ready body: `server-context.cpp:5297` `res->ok({{"status", "ok"}});`;
   - single SIGTERM shutdown: `server.cpp:519-523` (`ctx_server.terminate()`) and `server.cpp:590`
     `return 0;`;
   - second-signal path: `server.cpp:29-34` `Received second interrupt, terminating immediately.`
     then `exit(1);` — so "graceful status 0" holds only for one SIGTERM, not a blanket rule;
   - `subprocess.Popen.returncode` negative-value sentence, which is what makes "no SIGKILL /
     self-exit" gradeable rather than a bare presence test.
5. **Teardown conjunction.** `teardown_exited` must require `sigterm_sent true`,
   `sigkill_sent false`, documented returncode 0; `teardown_port_closed` must require the
   pre-teardown `port_listener_ownership == "child"` plus `port_refuses true`. The current producer
   checks only `returncode is not None` (`tools/kama-llamacpp-live.py:1024-1027`), and the teardown
   error branch can KeyError out of the finally before the receipt is written (`:1021-1028`); K6
   must show the receipt on disk and exit 2.
6. **No new capability row; score stays 8.** The reviewer must confirm the `live-llamacpp-lifecycle`
   row still exists exactly once, its evidence pointer resolves to v2 evidence (or remains the
   round-16 first-working receipt), and operability is recorded 8→8 with the cap cited:
   "Why operability stops at 8 and freshness at 7: the gate is verified against a real"
   (`SCORECARD.md:26`).
7. **Safety.** No port 8080/34113/registry port, fake servers torn down, `ss -ltnp` clean; controls
   run only the lane tool and gate, not the registered consumers.

## 3. Does hardening count as an axis move, or must the score/row change?

**It counts as an axis move; neither the score nor a new row must change.** Grounds:

- AXES defines an axis move as "each claim is one axis-move: pick the axis, land one verifiable
  improvement, measure it" plus "record before→after in `SCORECARD.md`"
  (`/home/vgpnk/Projects/shokunin/AXES.md:27-29`). Nothing conditions the move on the 0–10 score
  changing. The before→after is the measured artifact delta (accepted-bad controls N→0, surviving
  mutants 5→0), not the integer.
- AXES says only that for an exploratory claim "The score on a subjectively-moved axis need not
  change" (`AXES.md:51-53`). That sentence permits the no-change case for exploratory claims; it
  does not make a score change mandatory elsewhere.
- Lane precedent: `SCORECARD.md:320` records "calibration 7 → 7, delta 0" with verdict "improved
  fail-capable source correspondence"; `SCORECARD.md:611` records "operability **8 → 8**, delta 0;
  capability row added". Both were admitted as moves.
- The discriminator against "no move" is behaviour, not bookkeeping: round 10 closed a gate-bundle
  refresh because "re-running unchanged gates is re-verification, not an operability move"
  (`SCORECARD.md:199`). C2 changes what the gate accepts and rejects, so it is a move; rerunning it
  would not be.
- Capability table: "Rows enter only through a round that demonstrates the capability running"
  (`AXES.md:62-63`). C2 demonstrates the *same* capability running with a stricter contract, so it is
  not a new row. The one-line "what it can now do" (`AXES.md:61-62`) may be restated by an appended
  supersession only if the old line became false (it says the gate "re-derives every check", which
  remains true); the evidence pointer must resolve to the v2 gate/controls. Renaming the row or
  assigning a new first-working round would be an unearned acquisition.
- Two claims on one axis count as one (`AXES.md:32-33`). C1's harness is operability-shaped but is
  claimed as calibration; its mutant/fault-control evidence must not be re-credited as an operability
  improvement. The knowledge appendix is C2's sourced evidence and a quality-trend observable, not a
  third axis claim unless declared as one.

## 4. Findings by severity

### High

**H1 — `discernment: improved` is not author-earnable, and no seat in this wave can supply it.**
`LEARNING.md:42-46` requires a non-author spot-check of "at least one admit and one reject",
recording `agree`/`disagree` with a reason, and states "A subagent the lane dispatched is still the
lane." All round-17 build/falsify seats are lane-dispatched. The author's maximum is `unchanged`
pending the outside sample; the sample belongs in `corpus/lessons/round-17.md` §Gate. If round 17
produces no reject decision to sample, `improved` is unavailable even after outside review.

**H2 — `expansion: improved` would overclaim the appended knowledge section and the hardened
capability.** `LEARNING.md:33` counts "net new admitted entries on uncovered ground"; the scribe item
is explicitly an append to an existing entry, and C2 adds no row. Writing `expansion: improved`
would cite the round-16 capability or new SOURCES rows, neither of which is an admitted entry on
uncovered ground.

**H3 — `mutants.py`'s "any observable difference" cannot support the calibration claim.** C1's
claim is that reason/exit/drift/served_model/route-match became load-bearing. If a mutant is called
killed by any difference — e.g. M1 killed by F5's served_model output, or by a wrapper formatting
byte — the count no longer proves the named comparison. Require the per-field mapping in §2.1/2.2.
Also report pair-only survivors on current check.py: if the fault controls are the only killer, the
claim must be restated as suite load-bearing.

**H4 — `fault-controls.py` as specified can be vacuously green.** Detection is "exit 1 AND every
faulted row has `passed: false`" (`.ufo/waves/round-17/build/spec.json`, `C1FaultControls`), with no passthrough control. A
check.py that rejects all wrapper outputs would score detected=8, accepted=0. Add P0 (no corruption,
same rows) that must exit 0 with every row passed; without it the `accepted` count is not evidence.

### Medium

**M1 — `served_model` derivation must be body-literal, and its representation pinned.** The probe
sets `C_SERVED='-'` and joins ids with commas (`tools/kama-probe.sh:455`, `:527-529`). The claim
says "given the stub's `/v1/models` body and the verdict"; if the verdict enters the expected value,
the invariant is circular. Pin: expected = comma-joined ids from the row's literal models body, else
`-`; closed rows `-`. The frozen grader stores the field but never compares it
(`frozen tests_probe-verdicts_check.py:335-336` vs `:340-347`).

**M2 — `check-receipt.py` must branch on schema; v2's eleventh check breaks v1's exact-10 rule.**
The frozen gate requires `REQUIRED_CHECKS` and rejects any "unexpected check id (the schema names
exactly 10)" (`:614-621`), and explicitly treats `loading_envelope_exact` as a field, not a check
(`:420`). C2 adds that check. Without a schema dispatch, the v2 receipt is invalid and the v1 path can
regress. The non-author control is the frozen round-16 v1 receipt: still exit 0.

**M3 — "documented graceful exit status" needs the double-signal caveat and an ownership-order
record.** `server.cpp:29-37` calls `exit(1)` on a second signal; the single-model single-SIGTERM path
ends at `server.cpp:590` `return 0;`. The check must assert one harness SIGTERM plus rc 0, and cite
both. `port_listener_ownership` is a single overwritten field (the post-probes verification writes it last,
`tools/kama-llamacpp-live.py:976-977`); v2 must state that it is the pre-teardown observation, otherwise
the "proven owned" conjunct can rest on a stale mid-run proof. [INFERENCE]

**M4 — `quality: improved` needs a named entry delta and safe supersession.** The appendix must
append, not rewrite, and name what it supersedes; every QUALITY criterion must cite the round-17
lesson (`LEARNING.md:61-62`). A criterion added with no lesson behind it is `discernment: harmed`
(`LEARNING.md:35`). A code-grounded but false appendix would be `quality: harmed`
(`LEARNING.md:34`: "an entry is found false or stale and left unmarked").

**M5 — the C2 before-count must be measured, not asserted from the round-16 receipt.** The frozen
tool and frozen gate are available; the reviewer must see both runs. K6 (teardown raises) is the
only control that exercises the escaped-exception path, and its required evidence is
`receipt_written true` plus exit 2 — a bare nonzero exit is insufficient.

**M6 — the round-16 pair cannot be inherited.** MutateHarness measured probes `93ee4302…` / `6edd3c4c…`;
the round-17 frozen/current probe is `36b64978…` and the frozen check.py is `b853576e…`. The `pair`
baseline (55/17 vs 72/0) must be re-established at the measured commit and reported as observed; a
changed baseline is not a mutant kill.

### Low

**L1 — "health body exactly" is ambiguous (byte vs parsed).** The code emits
`res->ok({{"status", "ok"}})` (`.ufo/waves/round-16/sources/llama.cpp-704366d/server-context.cpp:5297`), so parsed equality to
`{"status":"ok"}` with no extra keys is code-grounded. Byte equality is stronger but must be stated
explicitly, or the claim will be read as byte-exact while the gate parses JSON.

**L2 — F6's pre-pass cache must invoke the real probe directly.** If the pre-pass goes through the
wrapper, the wrapper recurses or the cached row includes the corruption. The spec already says
"cache by first running the real probe"; the implementation must record the real probe's row, not the
wrapper's. [INFERENCE]

**L3 — F7 costs ~35 s per run and runs under `--only`; include it in the wall-time budget.** The
mutant runner's `full` mode plus F7 at two detector modes and two check.py versions is the dominant
cost; `mutants.py` parallelises mutants but each timeout fault must still be counted once.

## 5. Residual risk and verification gaps

- **Self-authored oracle.** `check.py`, `fault-controls.py`, `mutants.py`, the live tool, the gate
  and `controls.py` are produced in the same wave by the same lane. Green counts are author evidence,
  never discernment (`LEARNING.md:42-46`). The outside reviewer must re-derive at least one C1 kill
  and one C2 rejection independently, not merely read the JSON.
- **Concurrent mid-wave edits.** At review time `git status` showed `M tests/probe-verdicts/check.py`
  and `M tests/llamacpp-live/check-receipt.py`; the frozen copies equal their `master` blobs
  (`b853576e…` and `6b9576a1…`), but L1 must measure only the final commit and re-verify
  frozen=blob then. My defect citations above use the frozen copies, not the moving worktree.
- **No reject to sample?** If round 17 admits S042–S045 with no rejected candidate, the outside
  sample cannot meet "at least one admit and one reject"; state `discernment: unchanged` and the
  reason, rather than sampling an old round's reject.
- **The 0–10 scale is coarse.** C1/C2 are both "improved with delta 0". The counted deltas in the
  SCORECARD rows are the falsifiable evidence; if L1 omits them, the verdicts become unfalsifiable
  self-assessment — the exact calibration defect C1 repairs.

## Installs

None. No tool was installed or updated; existing `python3`, `git` read-only commands, and the
lane's frozen artifacts sufficed.
