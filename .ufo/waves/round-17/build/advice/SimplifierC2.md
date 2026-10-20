VERDICT: partial — the v2 receipt, the two new check ids and K1/K2/K4/K5/K6 are justified; `alive_at_teardown_start`, control K7 and the v2 ownership selftest mutation are removable, and the gate should share its schema-independent ~410 lines instead of forking them.

Axes used: **operability** (fewest moving parts in the counted path), **calibration** (every control must separate before→after), **weight** (one authority per rule; no second copy of a derivation). Read-only seat: nothing executed beyond `grep`/`cmp`/`sha256sum`; no gate, tool, control suite or server run.

## Q1 — can v1/v2 share derivation without risking v1?

**Yes — share the prefix, fork only the check table.** The frozen and current files are byte-identical (`cmp` both IDENTICAL; gate sha256 `6b9576a1…`, tool `b8c5e8d4…`), so "preserve v1" and "refactor v1" are in direct tension; the boundary must be mechanical.

- Shared verbatim: `tests/llamacpp-live/check-receipt.py:173-586` — schema/run outcome (173), timestamps (181), alias/scalars (194), port/refusal (203), server (233), model (279), probe identity (299), tool block (318), child env (339), argv (355), loading lifecycle incl. `loading_envelope_exact` re-derivation (391), captures (448), probes (474), teardown shape (573). None of these reads a schema-specific key. ~410 lines.
- Divergent, per-schema: the expected schema literal and message (`check-receipt.py:175` "schema is {…!r}, want {RECEIPT_SCHEMA!r}"), `REQUIRED_CHECKS` (`check-receipt.py:53`), the extra-id rejection (`check-receipt.py:619` "unexpected check id {cid!r} (the schema names"; the message hardcodes "exactly 10"), and only 4 of 11 re-derivation blocks: `health_ready` (`:628`), `teardown_exited`/`teardown_graceful` (`:745`), `teardown_port_closed` (`:758`), plus the new loading block.
- Shareable re-derivation blocks (7/11, identical predicates today): models_alias_id `:639`, models_owned_by_llamacpp `:657`, metrics_not_enabled `:670`, props_alias `:682`, probe_model_ok `:698`, probe_mismatch `:721`, model_unchanged `:771`.
- **Never share across the producer↔gate boundary.** `check-receipt.py:78` "Mirror of producer loading_envelope_exact()" and `install_tree_sha` (`:70-75`) exist to re-derive independently; a v2 path that imports the tool's helpers destroys the capability. Sharing is legitimate only inside `check-receipt.py`, v1↔v2.
- Dispatch rule to keep v1 exact: anything that is not `v2` must fall through today's v1 body. Today an unknown schema only appends a problem at `:175` and then validates the whole v1 body; an early "unknown schema → stop" branch changes v1's observable problem list (exit code would stay 1, so the selftest would not notice).
- Risk pin (necessary, missing today): the 26-mutation selftest compares exit codes only (`check-receipt.py:990`, `cases` loop at `:996`), so a refactor can silently change 26 problem lists. Cheap mechanical proof: replay every mutation through the frozen gate and the new gate and diff stdout; then require both round-16 receipts VALID. `controls.py` covers only the current (v2) tool — it is not a v1 regression suite, so do not count it as one.

## Q2 — controls: what is redundant

| id | verdict | why |
|---|---|---|
| K0 good | keep | sole acceptance control (over-rejection guard) |
| K1 health-degraded | keep | only control for the new health body predicate |
| K2 loading-bad-envelope | keep | only control for the loading predicate |
| K3 self-exit rc 0 | **reshape** | discrimination is a race against the post-probes liveness gate (below) |
| K4 ignores-SIGTERM | keep | only control for `sigkill_sent`; costs 10 s (`tools/kama-llamacpp-live.py:64` `TERM_GRACE = 10.0`) — do not add a test-only grace flag |
| K5 exits nonzero | keep | only control for `returncode == 0` after a delivered SIGTERM (distinct from K4's conjunct) |
| K6 teardown-fault | keep | only route to an internal fault: every teardown OSError path is swallowed (`tools/kama-llamacpp-live.py:660-690`), so no external fake shape can induce it |
| K7 hang | **drop** | does not discriminate |

- **K7 is non-discriminating.** A listening-never-answering fake lands in `setup_error ready-timeout` → tool exit 2, and both gates reject any `setup_error` (`check-receipt.py:179` "a complete run has setup_error null"). Rejected before and after: delta 0, and it grades no v2 predicate. Round-16 already demonstrated the same shape.
- **K3 as specified is timing-racy.** If the fake self-exits before `verify_live(..., 'post-probes')` (`tools/kama-llamacpp-live.py:976`), the tool raises a setup error (`:540` "child-exited-rc"), the frozen gate already rejects, and K3 is not accepted-bad *before* — the control then measures the wrong defect. Only an exit in the window between `:976` and the teardown call (`:1021`) reproduces the round-16 `se` case; [INFERENCE] no wall-clock sleep hits that window deterministically. Deterministic replacement in the K6 in-process harness: wrap `teardown` so it first reaps a self-exiting child (`proc.kill(); proc.wait()`) and then calls the real teardown — result `sigterm_sent false`, `returncode 0`, `port_refuses true`, i.e. exactly the `se` receipt shape, while the frozen tool still passes `teardown_exited` ("returncode is not None", `:1025-1027`).
- **Add one acceptance control**: exact-envelope 503 then ready must be ACCEPTED (call it K8). K0 only exercises `loading_observed=false`. The branch the official run actually hits (round-16: 38 exact 503s) has no acceptance control, so an over-strict envelope predicate (e.g. comparing the wrapped body) fails L1's measured run with a green control suite. This is the one axis (over-rejection) the suite cannot currently see; it is cheaper than any new fake behaviour.
- **No control for `teardown_port_closed`'s ownership conjunct** (and no grandchild-holding-port fake): the conjunct cannot fail in any receipt the gate accepts, because `check-receipt.py:437-440` already requires "a valid receipt requires the ready listener proven to be our child". A grandchild holding the socket fails the original `port_refuses` predicate too. The strengthening is row-honesty only; spend no fake on it.
- K6 implementation note: in-process `main()` installs SIGINT/TERM/HUP handlers and ignores them for the shutdown/write window (`tools/kama-llamacpp-live.py:886-887`, `:1015`). Run it on the main thread and save/restore the control's own handlers around the call, or a stray signal during the run kills the control, not the tool.

## Q3 — are the new check ids needed

- `health_ready`: **keep the id.** The DOC already claims the body (`tools/kama-llamacpp-live.py:78-82` "GET /health returns 200 {"status":"ok"} once the model is loaded") while v1 graded the status half (`:938` `health_status == 200`). v2 restores the documented proposition; a new id would assert a new one.
- `teardown_exited` → `teardown_graceful`: **new id justified.** The proposition changes from "reaped" to "harness-initiated SIGTERM, no SIGKILL, rc 0"; -9 and rc 1 flip pass→fail. Keeping the id would let a v1 receipt's row appear to satisfy a v2 predicate — precisely the cross-schema confusion the id split prevents.
- `teardown_port_closed`: **keep the id.** Same proposition; the extra conjunct is already a global gate rule (`check-receipt.py:439`). Do not mint `teardown_port_owned` or a `_v2` id — churn with zero observable effect on any verdict.
- `loading_envelope_graded`: **new id is right, but make it a projection, not a second authority.** The tool computes the fact at `tools/kama-llamacpp-live.py:921-922`, the gate re-derives it from the stored body at `check-receipt.py:420-437` ("loading_envelope_exact is a receipt FIELD (bool|null), not a check"). The check must be derived from `loading_envelope_exact`/`loading_observed` on both sides and the gate must assert `row == (lef is not False)`; never grade the row's own `passed`. Keep the field as well (item says keep v1 field names). This also settles the round-16 H1 without adding a second body parser.
- `model_unchanged`: keep id, DOC relabel only.
- `_check` indexes `DOC[check_id]` (`tools/kama-llamacpp-live.py:715`), so both new ids need DOC entries or the check block aborts with KeyError before any row is appended.

## Q4 — other parts to delete or fix in the v2 design

- **Drop `alive_at_teardown_start`.** It is set exactly where `sigterm_sent` is set (`tools/kama-llamacpp-live.py:663-664`: `if proc.returncode is None: # F5: killpg only while child is alive` → `out['sigterm_sent'] = True`), so both fields carry the same bit and the gate cannot re-derive liveness from anything else — it would have to trust the new field. Stronger and smaller: set `sigterm_sent` only when `os.killpg` returns without `ProcessLookupError` (delivered, not attempted). Then `teardown_graceful = sigterm_sent and not sigkill_sent and returncode == 0` — one field, no new key.
- **Fix `verify_live`'s `None` ownership** (`tools/kama-llamacpp-live.py:540` returns `…, None`), which `main` writes into `port_listener_ownership`; the gate rejects anything outside child|foreign|unproven. Under v2 that is exactly K3's early-exit shape: the receipt becomes invalid for *shape*, so the control's "teardown check is false" assertion passes for the wrong reason. One-line map `None → 'unproven'` (round-16 L3, not carried into the C2 item).
- **Do not copy the selftest receipt literal.** `_selftest_receipt()` (`check-receipt.py:846`, "One valid receipt literal in the producer's exact shape.") is ~140 lines; parameterize it `(schema)` with the divergent keys (teardown id, loading id, optional new teardown field) instead of a second literal. The case loop needs no change.
- **Drop the v2 mutation "ownership unproven + port_refuses true":** it exits 1 through the same global rule already covered by the v1 `ownership-unproven` case (`check-receipt.py:1043`); it proves nothing about the `teardown_port_closed` block.
- Keep both `returncode -15` and `returncode 1` mutations: they test distinct conjuncts (signal death per Python docs vs ordinary nonzero), one line each.
- Doc/CLI strings that name only v1 and must name both: `check-receipt.py:1104` "Validate a kama-llamacpp-live/v1 receipt.", `:2` module docstring, `tools/kama-llamacpp-live.py:23`, `:50` `SCHEMA`, `:725` help text.

## Limitations

- Read-only; I executed no gate, tool, controls run or server, bound no port, and wrote nothing but this Report.
- K3 timing claims are [INFERENCE] from code order (`:976` before `:1021`), not from a run; the reshape removes the inference.
- Exact-equality of the `/health` body is taken as given from the C2 item and DOC; whether the upstream handler emits only that object is CriticSourcedClaim's check, not mine.
- I did not review C1's files or the SOURCES rows.

Installs: none.
