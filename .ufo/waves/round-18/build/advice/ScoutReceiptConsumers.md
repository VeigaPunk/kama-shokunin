VERDICT: n/a — read-only recon; no lane claim was tested. Every file that names `kama-llamacpp-live/v1|v2`, the eleven check ids, or the receipt gate's exit codes was located and classified: 3 code files hold every v3 seam, 12 current-tense statements go stale or false, and the historical statements in §3 must stay byte-identical.

# Recon: receipt-schema and gate-exit consumers (round 18, C1 v3)

Method: `grep -rn --exclude-dir=interactive-sessions --exclude-dir=.git --exclude-dir=.jj` over the lane for
`kama-llamacpp-live/v[0-9]`, `loading_envelope_graded|health_ready|teardown_graceful|
teardown_port_closed|model_unchanged`, `check-receipt`, and receipt/exit vocabulary; then read every hit.
Nothing was executed, no server started, no port bound, no scratch tree created. The frozen copies
(`.ufo/waves/round-18/frozen/*`) are byte-identical to `e75cf68` for the three C1 files, so line numbers below
hold for both the frozen copy and the working file unless noted.

Terminology: **in-claim** = owned by C1 this round (the executor rewrites it anyway); **stale** = current-tense
sentence that v3 contradicts; **historical** = a statement about a past receipt/run, which v3 cannot falsify —
these are the compatibility oracle and must not be edited (KQ22, `corpus/QUALITY.md:123`).

## 1. Code seams

| File:line | Names | Under v3 | Required |
|---|---|---|---|
| `tests/llamacpp-live/check-receipt.py:206-208` | `if schema not in (RECEIPT_SCHEMA, RECEIPT_SCHEMA_V2): bad(f"schema is {schema!r}, want …")` | **Breaks**: any v3 receipt is INVALID on schema alone, exit 1, before one predicate runs. | Add the v3 constant and dispatch; a v3 receipt must reach the tri-state predicates. |
| `tests/llamacpp-live/check-receipt.py:58-59` | `RECEIPT_SCHEMA = "kama-llamacpp-live/v1"` / `…_V2` | Missing v3 constant; every selftest case is built from these. | Third constant + `--require-schema v1\|v2\|v3`; a *lower* declared schema than the requirement is INVALID, so this is a comparison, not a set membership test. |
| `tests/llamacpp-live/check-receipt.py:44-45` | "Exit: 0 receipt valid, 1 receipt invalid (every problem listed), 2 receipt unreadable / not JSON." | Exit map has no NOT-EVALUATED; a well-formed v3 receipt with one legitimately-null check has no exit value. | 3 = well-formed v3, every evaluated check re-derives true, only shortfall a null check. Also the docstring line 2 "Independent validator for kama-llamacpp-live/v1 and /v2 receipts." and the argparse description "Validate a kama-llamacpp-live/v1 or /v2 receipt." (`:1360`). |
| `tests/llamacpp-live/controls.py:557-559` | `base = (receipt_written and not tool_timed_out and (tool_exit != 0 or (gate_exit is not None and gate_exit != 0)))` | **Cannot express the contract.** Gate exit 3 is `!= 0` → a *good* zero-loading server is counted `rejected`. With `expected=[]`, `_attributed` returns `None` (`:457-458` `if not expected: return None`), so `inconclusive` stays False and the row is silently counted as a detection. | Not-evaluated needs its own arm and counter (`tool_exit == 2 and gate_exit == 3 and outcome == "not-evaluated"`), plus `clean` must require that counter; the bad arm should treat `gate_exit == 1` as rejection, matching `_gate_flip`'s already-strict `rejected: rc == 1` (`:487`). |
| `tests/llamacpp-live/controls.py:552-553` | `accepted = (tool_exit == 0 and gate_exit == 0 and not escaped and not tool_timed_out)` | Safe **only because K0's fakes always observe 503s** (`:166` `LOADING = {'/v1/models': 3, '/health': 1}`; `:48-50` "Every serving fake answers >=3 loading 503s … so the v2 loading-envelope checks have real evidence"). A zero-loading good server inserted into K0 would flip `good_ok` to false. | Keep K0 as-is; the zero-loading case is a new control, never K0. |
| `tests/llamacpp-live/controls.py:563` | `rejected = receipt_written and tool_exit not in (0, None)` (K6) | Any nonzero exit passes K6, including the tool's exit 3 (model digest mismatch) — a rejection for the wrong reason. | Tighten to exactly 2 (contract already says so). |
| `tests/llamacpp-live/controls.py:436` | `if isinstance(c, dict) and c.get('passed') is False:` | Correctly ignores `null`; attribution is v3-safe without change. | None. |
| `tests/llamacpp-live/controls.py:687-689` | `clean = (accepted_bad == 0 and gate_flip_bad == 0 and inconclusive == 0)` | A new not-evaluated control contributes to **none** of these counters — it is inert unless added. | Add its counter to `clean`. |
| `tools/kama-llamacpp-live.py:50` | `SCHEMA = 'kama-llamacpp-live/v2'` | **Breaks** the contract by emitting v2. | v3 + `outcome` + `evaluated` on every check. |
| `tools/kama-llamacpp-live.py:16-21` | "1 at least one check failed (server ran; receipt written) … 2 setup error …" | 1 no longer covers null; 2 widens from setup/internal fault to *any* not-evaluable run, including a healthy server with one unobservable check. | Rewrite the map so 2 reads could-not-evaluate and the receipt still distinguishes `setup-error` from `not-evaluated` via `outcome`. |
| `tools/kama-llamacpp-live.py:136-142` | check DOC: "no 503 observed -> fail with {\"loading_observed\": false}" | **False under v3** — and worse, it is the sentence the *gate* would be expected to enforce. | DOC must state the null/not-evaluated rule and cite the lane decision, not S036 (see §5). |
| `tools/kama-llamacpp-live.py:1346-1348` | `receipt.get('loading_observed') is True and loading_envelopes_all(bodies) is True` | Passed is a strict boolean; no null path exists in the producer. | Tri-state: `None` iff `loading_observed` false, with `observed.not_evaluated_reason = "no-loading-503-observed"`. |
| `tools/kama-llamacpp-live.py:1376-1378` | `exit_code = (0 if all(… passed is True …) else 1)` | Any null check lands in the `else` → exit 1, the exact R4 defect. | Separate null-with-none-false → 2. |
| `tools/kama-llamacpp-live.py:944-947` | argparse description "emit a `kama-llamacpp-live/v2` receipt." | Stale surface text; `--help` is quoted by operators. | v3. |

Nothing else in the lane **reads** a receipt. Verified non-consumers, with the search that proves it:
`tools/kama-probe.sh` (no `receipt` token), `registry/endpoint-consumers.tsv` and `registry/history/` (no
schema token), `.ufo/waves/round-16/measure.py` (its `receipt` keys are its own `run-*.json`, probe matrix
only), `.ufo/waves/round-17/c1/mutants.py` (probe sites only), `.ufo/waves/round-17/count-verdicts.py` and
`dispatch-provenance.py` (VERDICT lines / task calls), `.ufo/waves/round-16/live/replay-captured-503.py:12`
(reads the immutable v1 `loading_503` capture), `tools/test-snapshot.sh` (snapshot only). There is no `.ufo/waves/round-17/measure.py`; that round's counting commands are `count-verdicts.py`, `dispatch-provenance.py` and `c1/mutants.py`, none of which reads a receipt. No lane runner
invokes the receipt gate or `controls.py`; the only invocation sites are prose in `SKILL.md`.

## 2. Current-tense statements that v3 makes stale or false

| File:line | Quote (≤25 words) | Why it fails | Minimal remedy |
|---|---|---|---|
| `SKILL.md:574` | "0 valid, 1 invalid, 2 unreadable; v1 receipts validate exactly as in round 16" | Exit map omits 3; also omits that `--require-schema` makes a *lower* schema INVALID rather than merely unsupported. | Append: 3 = NOT-EVALUATED; `--require-schema v1\|v2\|v3` semantics. |
| `SKILL.md:574` | "`--selftest`: 26 v1 + 13 v2 mutations rejected, 2 valid receipts accepted" | Adding v3 mutations changes the printed count; the number is a current description, not history. | Append the new count after C1 lands (do not guess it now). |
| `SKILL.md:536` | "0 valid, 1 invalid (every problem listed), 2 unreadable" | The round-16 v1 gate row still carries a three-value map and is *not* covered by the round-17 supersession sentence, which only replaces its "10 check ids". | Append that this row's exit map also gains 3 (the same binary serves both sections). |
| `SKILL.md:573` | "2 setup error or internal fault (receipt still written, `internal:<ExcType>`), 3 model digest mismatch" | 2 widens to include a *healthy* run whose only shortfall is an unobservable check; a reader who treats 2 as "the harness broke" will misread a not-evaluated run. | Append the widened 2 and the `outcome` discriminator. |
| `SKILL.md:573` | "503s observed and every stored body exact; none observed fails" | Directly reversed: none observed is not-evaluated, never a failed check. | Append supersession. |
| `SKILL.md:565` | "the tool now emits `kama-llamacpp-live/v2` with 11 checks" | "now" becomes v3; 11 checks stay 11. | Append one sentence changing "now" to v3. |
| `SKILL.md:592-593` | "exit 1 can also come from a model rehash `OSError`, and a `BaseException` … can escape without a receipt" | Both behaviours are fixed by the contract (internal faults → receipt + exit 2; BaseException included). As written it describes the repaired defect as current. | Append that the round-18 latch closes both. |
| `PROVINCE.md:73` | "The tool now emits `kama-llamacpp-live/v2`" | Same "now" drift; the scope paragraph is otherwise unchanged by v3. | Append a round-18 note (scope unchanged, schema/outcome only). |
| `corpus/knowledge/llamacpp-loading-lifecycle.md:194` | "The v1 limits above are superseded for receipt v2" | Now a two-step supersession; "superseded for v2" reads as final. | Append "v2 is in turn superseded by v3 for the null case". |
| `corpus/knowledge/llamacpp-loading-lifecycle.md:198` | "`loading_envelope_graded` fails when no 503 was observed" | **False under v3.** This is the most dangerous stale line: it states the exact defect v3 repairs as the design rule. | Append the null→not-evaluated rule and the round-17 debt line that authorises it. |
| `corpus/README.md:241-243` | "receipt v2 grades every observed loading 503 body (42–45 per run) and fails a run that observed none" | Last clause is reversed. This is the frontier-disposition paragraph, i.e. the lane's own statement of what it holds. | Append a §Correction — round 18 paragraph; it can share the R3 append that adds the S047 pointer at `:238`. |
| `SCORECARD.md:695` | "whose evidence pointer is now receipt v2" | The canonical capability list names v2 as current evidence; the round-18 append must move it to a v3 receipt path. | Handled by L1's round-18 SCORECARD block (not a separate edit). |

## 3. Historical statements that must NOT change

These are the no-harm oracle: if any of their verdicts moves, the gate regressed.

- `corpus/SOURCES.md:53` (S041): "receipt `kama-llamacpp-live/v1` … port 37527, tool sha256 b8c5e8d4…, 10 checks".
- `corpus/SOURCES.md:58` (S046): "receipts `kama-llamacpp-live/v2` … 11 checks each, gate VALID with model, server, probe and tool pins". This sentence is the written v2 compatibility test; the contract already requires the round-17 receipts to keep VALID.
- `corpus/lessons/round-17-verifier-spotcheck.md:132`: "2 valid receipt(s) accepted; 39 mutations + unreadable case all rejected" — the round-17 gate's transcript; C1's selftest count will differ and that is not a contradiction.
- `corpus/lessons/round-17-verifier-spotcheck.md:234` (R4): "Zero observed 503s fails `loading_envelope_graded` with exit 1" — the defect statement v3 closes.
- `corpus/lessons/round-17.md:253-254`: "the honest next move is to classify zero observation as could-not-evaluate (exit 2) rather than a failed check" — this is the *authority* for v3's rule; v3 implements it, so it must be cited, not corrected.
- `SHONEN.md:8` ("Round 17 adds graded v2 receipts … 11/11 checks each"), `LOG.md:966` and `LOG.md:1014` ("receipt v2, … v1+v2"), `corpus/lessons/round-16.md:31,104`, `corpus/lessons/round-16-verifier-spotcheck.md:78,110`, `corpus/knowledge/endpoint-identity.md:185`, `corpus/README.md:238` — all report past runs; leave untouched.
- `corpus/knowledge/llamacpp-loading-lifecycle.md:101-102,160` (v1 receipt, tool `b8c5e8d4…`; S046 tool `0efd1723…`) — per-receipt hashes, correct forever.

## 4. Exit-code hazards

1. **The number 3 now means two different things on sibling commands.** Tool exit 3 = "model digest mismatch before launch" (`tools/kama-llamacpp-live.py:1023`, SKILL.md:573); gate exit 3 = NOT-EVALUATED. `SKILL.md:462-465` already rules "Do not transfer exit meanings across tools", so this is legal — but only if both rows carry the code explicitly. No wrapper in the lane captures both codes today; anything written later must name the command with the code.
2. **Widened 2 is the subtle one.** Before v3, exit 2 meant "the harness could not complete a run". After v3 it also means "the server ran, everything observable passed, one check was not observable". A receipt with `outcome: "not-evaluated"` and `setup_error: null` is the discriminator; the gate must not infer setup failure from exit 2 alone.
3. **Gate exit 2 keeps its meaning** (unreadable/unparseable) and must not be reused for internal faults in the gate, or "unreadable" and "crashed" become indistinguishable to a caller that only reads `$?`.
4. `--require-schema` is a new flag absent from every existing row and invocation example (`SKILL.md:536,574`). Not a break (defaults accept every known schema), but the flag's *rejection* direction (lower declared schema than required → INVALID, exit 1, not 3) must be stated, or a caller will expect exit 3.

## 5. Measurement hazards for the before/after count

- **Version pairing is not optional.** The frozen gate rejects v3 at `check-receipt.py:206-208`, one schema problem, exit 1. Pairing the current tool with the frozen gate makes every control "rejected" by schema; the bad-arm counters cannot see it (`accepted_bad` 0, `inconclusive` 0), and `_gate_flip` (`:487` `rejected: rc == 1`) reports rejected for a schema complaint. K0 does fail on a mixed pair (its `gate_exit == 0` requirement breaks), so the mistake surfaces as a good-control rejection, not as a clean count. The before arm must be frozen tool + frozen gate, the after arm current tool + current gate, and `measure.py` should assert the receipt's `schema` per arm and refuse a mixed pair.
- **The zero-observation control cannot be produced by the real server.** `LiveFastLoad.md:1`: "20/20 real b11755 runs … saw 24–48 503s (zero runs at 0)"; `corpus/knowledge/llamacpp-loading-lifecycle.md:227` adds "1 of 60 real runs at 32x `stress-ng` load observed no 503". A real-server zero-503 run is a rare, load-dependent event; the control must be a fake that is ready before the first `/v1/models` poll. [INFERENCE from those two observed rates.]
- **The null rule has no upstream source.** S036 grounds the loading envelope; it does not ground "unobserved ⇒ not-evaluated". The citation must be the lane decision (`corpus/lessons/round-17.md:253-254` / R4), or the falsify wave's `DocStringsSources` attack will land on a `documented_by` that claims llama.cpp for a lane policy.
- **KQ21 is satisfied, not bent.** `corpus/QUALITY.md:122` requires a retained control that makes the check fail and a gate that rejects the flipped receipt; a null check counted as not-evaluated is not counted as evidence, which is KQ21's own rule. The contract's "keep K0-K8 + add retained bad controls" is the correct shape.

## 6. Ordered minimal edits (for L1)

1. C1 executor: the three in-claim files per §1, including the new controls arm and counter from `controls.py:557` / `:687`.
2. C1 measure: pair versions, assert per-arm schema, print the receipt `outcome` distribution.
3. Append to `SKILL.md` §Round-17 block: gate 3 + `--require-schema`, widened 2, v3 as current schema, null rule, the two repaired escape paths (§2 rows 1-7). Append-only, same style as the existing "Round-17 falsify corrections (appended)" block.
4. Append to `PROVINCE.md` and `corpus/knowledge/llamacpp-loading-lifecycle.md` (§2 rows 8-11) — one short paragraph each, "v2 superseded by v3 for the null case".
5. `corpus/README.md`: one `§Correction — round 18` paragraph that both reverses "fails a run that observed none" and adds the S047 pointer R3 asks for (same insertion point, `:238-243`).
6. Do not touch §3. Do not edit `corpus/SOURCES.md`; if v3 needs a source row, it is S048+ (new row).

## 7. Limitations

- Read-only: I did not run the tool, the gate, or `controls.py`; every behavioural claim above is read from source at `e75cf68`, with the two observed rates quoted from the round-17 falsify advice. The verdicts "breaks" mean the code path provably cannot express the v3 contract, not that I observed a failing run.
- Line numbers are the frozen/round-start file; C1's edits will shift them.
- I did not inspect `.ufo/waves/round-18/build/out/**` (seat deliveries still in flight), so a seat may already have fixed an item in §1; the doc items in §2 are L1's integration surface either way.

Installs: none. No tools upgraded; no pacman transaction attempted.
