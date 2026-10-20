VERDICT: confirm — v3 controls pass on the integrated tool/gate and expose the expected frozen defects.

Axes: operability; calibration (lowest assigned axis).

## Delivered

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/build/out/C1Controls-2/controls.py` — SHA-256 `106dd98b60e066a190ee8fea609e5be99c6b2065b9c5a404e14394ce59b6ffc8`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/build/out/C1Controls-2/controls.py.diff` — SHA-256 `5356eb71da682e950561e343d6d0a261c12d09e7d53bcfb97bb258e462d35963` (unified diff against the round-start frozen controls)
- Exclusive report: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/build/advice/C1Controls.md`

## Behavior and retained findings

- K0-K8 semantics remain; K6 now requires a receipt and tool exit exactly 2. K7 remains a setup-error rejection with no check attribution (`rejected-untargeted`); K7 does not count as an inconclusive targeted rejection. K9-K14 each target one formerly uncontrolled check (`models_alias_id`, `models_owned_by_llamacpp`, `metrics_not_enabled`, `props_alias`, `probe_model_ok`, `probe_mismatch`). K13/K14 switch the two curl responses by request count so only the named probe check fails. `build/out/C1Controls-2/controls.py:581-618` names the targeted checks and fakes; e.g. “only probe_model_ok fails” and “probe_mismatch”.
- K15 retains the listener after the fake server exits, targeting `teardown_port_closed`. K16 is a ready-at-once GOOD fake: expected tool exit 2, gate exit 3, and a coherent `not-evaluated` receipt. K17 is an accepted GOOD AF_INET6 `::ffff:127.0.0.1` listener with `IPV6_V6ONLY=0`. K18 injects KeyboardInterrupt into `teardown()` in an isolated wrapper and expects a receipt and tool exit exactly 2. Anchors: `build/out/C1Controls-2/controls.py:630-654`; quote: “GOOD zero-loading”; “the receipt must still be written”.
- K19-K22 forge only a real K0 receipt and send it to the gate: v1 schema floor under `--require-schema v3`, an inserted `--api-key X`, an altered `/v1/models` 503 transition with the loading-body list unchanged, and a duplicate `--host`. Forged argv is never executed. `build/out/C1Controls-2/controls.py:671-745` documents the mutations; `:1834-1846` dispatches forgeries to `grade_forgery_row` rather than `run_tool_control`.
- A gate usage error for the new `--require-schema` flag is explicitly not counted as rejecting that predicate: the same forged v1 receipt is checked flagless, and the result cannot be `rejected-targeted`. `build/out/C1Controls-2/controls.py:63-70` states the rule.
- Classification JSON reports `accepted`, `rejected-targeted`, `rejected-untargeted`, `not-evaluated`, or `misclassified`; includes `good_rejected`, `misclassified`, `uncontrolled_checks`, and separates `model_unchanged` under `input_integrity_checks`. If a required gate-flip arm did not run, aggregation raises a controls fault. `build/out/C1Controls-2/controls.py:1023-1031`, `1073-1098`, `1135-1136`, and `1240-1285`.
- Fail-closed staging copies the real registry or raises; no empty-registry substitute remains. Fakes bind only `127.0.0.1` or mapped loopback `::ffff:127.0.0.1`; the tool chooses their port from its refusal set. `build/out/C1Controls-2/controls.py:830-833`, `387-406`; quotes: “Fail closed instead”; “IPV6_V6ONLY=0”. Cleanup checks exact fake-script identity and kills the dedicated process group, avoiding the controls process group: `build/out/C1Controls-2/controls.py:777-808`, `863-886`.
- `--selftest` includes a null-to-true gate-flip, observed bad 503 evidence laundered as null (must be rejected), and a real failure combined with legitimate no-loading null (outcome fail, never not-evaluated): `build/out/C1Controls-2/controls.py:1663-1686`.

## Verification commands and exit codes

Ran from `/tmp/kama-r18-C1Controls` (the assigned clone; no commands ran against the lane source as an implementation target):

```text
python3 -m py_compile tests/llamacpp-live/controls.py
exit 0

python3 tests/llamacpp-live/controls.py --selftest
exit 0; selftest: 70 cases, 0 failure(s)

python3 tests/llamacpp-live/controls.py --tool /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/frozen/tools_kama-llamacpp-live.py --gate /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/frozen/tests_llamacpp-live_check-receipt.py --probe tools/kama-probe.sh --json
controls exit 1 (expected: frozen defects were detected)

python3 tests/llamacpp-live/controls.py --tool tools/kama-llamacpp-live.py --gate tests/llamacpp-live/check-receipt.py --probe tools/kama-probe.sh --json
controls exit 0

ss -ltnp (before and after control runs)
exit 0 each
```
Preparation and handoff:

```text
git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r18-C1Controls && git -C /tmp/kama-r18-C1Controls switch -q -c seat/C1Controls
exit 0

cp /home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py tools/kama-llamacpp-live.py && cp /home/vgpnk/Projects/shokunin/kama-shokunin/tests/llamacpp-live/check-receipt.py tests/llamacpp-live/check-receipt.py
exit 0

git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r18-C1Controls && git -C /tmp/kama-r18-C1Controls switch -q -c seat/C1Controls && cp /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/build/out/C1Controls-2/controls.py /tmp/kama-r18-C1Controls/tests/llamacpp-live/controls.py && cp /home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py /tmp/kama-r18-C1Controls/tools/kama-llamacpp-live.py && cp /home/vgpnk/Projects/shokunin/kama-shokunin/tests/llamacpp-live/check-receipt.py /tmp/kama-r18-C1Controls/tests/llamacpp-live/check-receipt.py
exit 0 (clone recreated before the final K7 parity edit; final verification ran in this clone)

mkdir -p /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/build/out/C1Controls-2 && cp /tmp/kama-r18-C1Controls/tests/llamacpp-live/controls.py /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/build/out/C1Controls-2/controls.py
exit 0

rm -rf -- /tmp/kama-r18-C1Controls && rm -f -- /tmp/kama-r18-C1Controls-frozen.json /tmp/kama-r18-C1Controls-current.json && test ! -e /tmp/kama-r18-C1Controls && printf 'clone_removed=true\n'
exit 0
```

The unified-diff command appears below; GNU `diff` returned 1 for differing files, which the enclosing delivery command handled as expected. All full digests are recorded in this report.

- Frozen/current tested input SHA-256s: frozen tool `0efd1723b02ef748d720a6036d3ac481b1d5fe9755110999d7c9acaf486c46ac`, frozen gate `ad6801791f2ada896a7ee188609391aac86185c47320dbf415331869ca9cd2a5`; current v3 tool `dc036d7dcfe2933827c07f8bc0dedba68a24f7b099309871f6cb25ccb811a04b`, gate `c5715641f34fb9b9ffaf33ca3e0391dd5485a0a914462bf6540e519b566c78335`, probe `36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3`. The frozen pair came from the round-18 frozen paths; current v3 pair was copied from the lane working tree into the clone before the runs.
- Current run JSON retained at `/tmp/kama-r18-C1Controls-current-final.json`; frozen run JSON retained at `/tmp/kama-r18-C1Controls-frozen-final.json`. Current: `accepted_bad=0`, `good_rejected=0`, `misclassified=0`, `uncontrolled_checks=[]`, `gate_flip_bad=0`, `gate_flip_arms=17`, `good_ok=true`; K7 remained `rejected-untargeted` (tool 2/gate 1, no check target); K16 classified `not-evaluated` with tool 2/gate 3; K17 accepted; K18 targeted with tool 2; each K9-K14 failed only its target. K19: current gate exit 1 under `--require-schema v3`, flagless exit 0; frozen gate's unknown-flag path fell back and accepted the flagless v1 receipt. Frozen: `accepted_bad=5`, `good_rejected=1`, `misclassified=1`, `uncontrolled_checks=[]`, `gate_flip_bad=0`, `gate_flip_arms=16`, `good_ok=true`; K7 remained `rejected-untargeted`; K16 was misclassified (legacy tool exit 1), K17 good-rejected (legacy listener ownership), K18 escaped without a receipt, and K19-K22 were accepted by the frozen gate. These are control results, not claims about a real llama-server run.
- `diff -u /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/frozen/tests_llamacpp-live_controls.py /tmp/kama-r18-C1Controls/tests/llamacpp-live/controls.py > /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/build/out/C1Controls-2/controls.py.diff` returned 1, the expected “files differ” status; the output diff was 2,147 lines. `sha256sum` over delivered file and diff exited 0.
- An initial frozen run using clone-relative `.ufo/waves/round-18/frozen/...` paths found no files (controls exit 2; following JSON extraction failed, compound shell exit 1). Re-running with the absolute round-18 frozen paths succeeded and produced the frozen results above.

## Limitations, risks, blockers, installs

- No real llama-server was launched. Fakes do not verify llama.cpp's actual argv parsing, startup timing, or signal behavior. K9/K10 rely on User-Agent separation; K13/K14 additionally rely on two curl requests in probe order. If the tool changes client/request order, their gate rejections are classified off-target rather than credited as coverage. Gate predicate attribution uses problem-line wording and fails closed as rejected-untargeted when wording changes.
- After the final pair of runs, `ss -ltnp` exited 0 and showed no test fake listener, 8080 listener, or 34113 listener. Earlier post-run samples briefly displayed localhost Python listeners on 41267 and 38035; both PIDs disappeared before `/proc/<pid>/cmdline` could be read, and I did not signal them. Their attribution to concurrent seats is [INFERENCE]; neither was present after the final runs.
- LSP was unavailable in the mounted tool inventory; no symbol/refactor request could be made. No tool installs or updates.
- Blockers: none.
