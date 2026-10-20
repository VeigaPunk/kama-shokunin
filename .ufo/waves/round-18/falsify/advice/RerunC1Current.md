VERDICT: confirm — the bounded current C1 controls arm meets its asserted outcomes and matches L1’s retained after-arm semantics; no assigned falsifier surfaced.

# Scope and setup

This is a current-arm falsification rerun only. It is not a rerun of `c1/measure.py`, a production-server run, or an external non-author judgment. The assigned clone was made and switched successfully with:

```text
git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r18-falsify-RerunC1Current
git -C /tmp/kama-r18-falsify-RerunC1Current switch -q -c seat/RerunC1Current 1c325b2e58fcfdc6761f645b44cedfb1d65243e6
exit 0; stdout/stderr empty
```

The assignment context and the retained lesson put C1 on operability and KQ24’s not-evaluated boundary (`corpus/lessons/round-18.md:13-19,86-101`; `corpus/QUALITY.md:132-133`). I read all three CLI helps before executing the bounded control run:

- `python3 /tmp/kama-r18-falsify-RerunC1Current/tools/kama-llamacpp-live.py --help` — exit 0; describes an ephemeral free loopback port and refusal of registered ports including 8080 and 34113.
- `python3 /tmp/kama-r18-falsify-RerunC1Current/tests/llamacpp-live/check-receipt.py --help` — exit 0; exposes `--require-schema {v1,v2,v3}`.
- `python3 /tmp/kama-r18-falsify-RerunC1Current/tests/llamacpp-live/controls.py --help` — exit 0; exposes all controls `k0`–`k22`, `--tool`, `--gate`, `--probe`, `--json`, and `--selftest`.

# Executed rerun

Exact command (clone CWD `/tmp/kama-r18-falsify-RerunC1Current`):

```sh
python3 /tmp/kama-r18-falsify-RerunC1Current/tests/llamacpp-live/controls.py --tool /tmp/kama-r18-falsify-RerunC1Current/tools/kama-llamacpp-live.py --gate /tmp/kama-r18-falsify-RerunC1Current/tests/llamacpp-live/check-receipt.py --probe /tmp/kama-r18-falsify-RerunC1Current/tools/kama-probe.sh --json > /tmp/kama-r18-falsify-RerunC1Current/controls-current.json; rc=$?; printf 'exit=%s\n' "$rc"; sha256sum /tmp/kama-r18-falsify-RerunC1Current/controls-current.json; exit "$rc"
```

Observed exit **0**; JSON stdout SHA-256 `2f5b958c268716a8cefe0d59a061bbaeecbb28d8a52a8650759293e9b546e9f4`. The invocation emitted no stderr text. Tested inputs:

- `tests/llamacpp-live/controls.py` `106dd98b60e066a190ee8fea609e5be99c6b2065b9c5a404e14394ce59b6ffc8`
- `tools/kama-llamacpp-live.py` `dc036d7dcfe2933827c07f8bc0dedba68a24f7b099309871f6cb25ccb811a04b`
- `tests/llamacpp-live/check-receipt.py` `c5715641f34fb9b9ffaf33ca3e0391dd5485a0a914462bf6540e519b566c78335`
- `tools/kama-probe.sh` `36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3`

Top-level result: `accepted_bad=0`, `good_rejected=0`, `misclassified=0`, `inconclusive=0`, `gate_flip_bad=0`, `gate_flip_arms=17`, `good_ok=true`, and `uncontrolled_checks=[]`; all 23 rows `k0`–`k22` have `bucket=ok`. The controlled-check map covers all ten emitted check IDs: `health_ready`, `loading_envelope_graded`, `metrics_not_enabled`, `models_alias_id`, `models_owned_by_llamacpp`, `probe_mismatch`, `probe_model_ok`, `props_alias`, `teardown_graceful`, and `teardown_port_closed` (`controls.py:1240-1276`).

All control identities and observed tool/gate verdicts:

| ID(s) | Observed verdict | Target / notable result |
|---|---|---|
| k0 | accepted, tool 0 / gate 0 | documented good control |
| k1 | rejected-targeted, 1 / 1 | `health_ready` |
| k2 | rejected-targeted, 1 / 1 | `loading_envelope_graded` |
| k3 | rejected-targeted, 2 / 1 | `teardown_graceful`, `teardown_port_closed` |
| k4, k5 | rejected-targeted, 1 / 1 each | `teardown_graceful` |
| k6 | rejected-targeted, 2 / 1 | RuntimeError internal fault, injection fired |
| k7 | rejected-untargeted, 2 / 1 | expected setup-timeout refusal; no targeted check; loading check null is not treated as a target failure |
| k8 | rejected-targeted, 1 / 1 | `teardown_graceful` |
| k9 | rejected-targeted, 1 / 1 | `models_alias_id` |
| k10 | rejected-targeted, 1 / 1 | `models_owned_by_llamacpp` |
| k11 | rejected-targeted, 1 / 1 | `metrics_not_enabled` |
| k12 | rejected-targeted, 1 / 1 | `props_alias` |
| k13 | rejected-targeted, 1 / 1 | `probe_model_ok` |
| k14 | rejected-targeted, 1 / 1 | `probe_mismatch` |
| k15 | rejected-targeted, 1 / 1 | `teardown_port_closed` |
| k16 | **not-evaluated, tool 2 / gate 3** | good zero-loading control; no false check, only `loading_envelope_graded` null, receipt outcome `not-evaluated` |
| k17 | **accepted, tool 0 / gate 0** | good IPv4-mapped-loopback (`::ffff:127.0.0.1`) listener; receipt outcome `pass` |
| k18 | rejected-targeted, 2 / 1 | KeyboardInterrupt internal fault, injection fired |
| k19 | targeted gate reject, gate 1 | v3 schema floor; same forged v1 receipt flagless gate 0 |
| k20 | targeted gate reject, gate 1 | argv forgery (`--api-key X`) |
| k21 | targeted gate reject, gate 1 | loading-transition forgery |
| k22 | targeted gate reject, gate 1 | duplicate-flag argv forgery |

The exact required edge outcomes are present: k16 is `(tool_exit=2, gate_exit=3, classification=not-evaluated)`; k17 is accepted; the only non-null `internal_fault` rows are k6=`internal:RuntimeError` and k18=`internal:KeyboardInterrupt`, both with `inject_fired=true` and exact tool exit 2. This matches `controls.py:630-658` and the tri-state classifier at `:994-1059`.

All **17** owed gate flips ran (k1–k16 and k18). Every flip returned gate exit 1, `accepted=false`, `rejected=true`, `targeted=true`; `gate_flip_bad=0`. This includes k16: flipping the nullable loading result to a clean-looking pass was rejected (exit 1), not reclassified as not-evaluated. There is no owed flip for k0, k17, or the forged-receipt controls k19–k22. The harness’s flip and owed-arm accounting are at `controls.py:1073-1102,1233-1260`; schema/argv/transition forgeries are defined at `:671-748` and run as gate-only forgeries.

# Comparison to L1-retained output

The raw L1 after-arm command is recorded in `.ufo/waves/round-18/runs/c1-measure.json` at `.runs.after.argv`; it invokes `controls.py --tool .../tools/kama-llamacpp-live.py --gate .../tests/llamacpp-live/check-receipt.py --probe .../tools/kama-probe.sh --json`. Its after arm reports exit 0, `timed_out=false`, `faults=[]`, `leaked_processes=[]`, and `duration_s=20.155`; raw L1 stdout hash is `7dd9e4da63336702eafdcf7fe2dd42ef3905a3951690cea4d019931ccb8657ba`, with canonical doc hash `975e12a74cbfd50ff56fe96e3c155b7f229cd591973d9a19bfe80b87c72f2899`.

I compared this rerun JSON with L1’s stored `.runs.after.doc`. The official wrapper’s `duration_s` is outside `.doc` and was therefore excluded. I additionally removed only per-run `receipt_sha256` and `forged_sha256` values, then canonicalized both JSON documents (`jq -S -c`); the resulting `cmp` exited **0**, and both normalized files hashed to `cbff6ff8ee39134cfbd7d5cb817430428bc4266e1f92cbc0d66e1bceef84bf91`. Thus all remaining output fields—including row order, each classification and target, per-row gate result/flip, and aggregate counts—match L1. Raw stdout hashes differ, as expected for run-specific content-addressed receipt material; this is not represented as byte-for-byte raw-output identity.

Important scope limit: the retained *whole* official C1 counter command was not green. `runs/commands.json` records `c1-measure` exit 2; `corpus/lessons/round-18.md:161-167` attributes that to its before-arm top-level/per-row `misclassified` mismatch and explicitly routes a corrected rerun. This standalone after-arm rerun confirms the current `controls.py` result only; it does not repair or pass that before-arm/counter result.

# Isolation, cleanup, limits

The fake harness binds IPv4 controls only to `127.0.0.1` and k17 only to IPv4-mapped loopback `::ffff:127.0.0.1` (`controls.py:387-406`); the production tool help states its default is a free ephemeral loopback port. No registered port was requested. Post-run and post-cleanup `ss -ltnp` snapshots showed no listener on 8080 or 34113. `pgrep -af '/tmp/kama-r18-falsify-RerunC1Current'` returned no process rows; the clone was then removed and the post-cleanup check repeated. Other concurrent loopback Python listeners were visible; a later `ps` mapped sampled live PIDs to `/tmp/kama-r18-falsify-CheckDecoder/.../check.py` and unrelated `check.py --probe wrap.py` commands, while other sampled owners exited before lookup. These were not touched. The harness runs one fake at a time and uses per-control cleanup (`controls.py:777-808,1847-1853`).

This is fake-server/control-gate evidence, not a real llama-server/model smoke test, an assertion about registered consumers, or proof of general immunity. The previously documented official before-arm counter mismatch remains a blocker to treating the complete C1 measure as passed. No tools were installed or updated. No production, frozen, fleet, lane, or sibling files were edited; this report is the only retained file from this seat.

Report: `.ufo/waves/round-18/falsify/advice/RerunC1Current.md`
