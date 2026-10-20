VERDICT: partial — frozen/current numbers reproduce; (a) and (b) change frozen counts, while (c) and (d) survive the two-pair numeric detector; all four survive current-only counts.

# Attack and axes

Seat: KamaR17.MutControlsSelf. Advisory mutation evidence only; no round-admission or integration decision.

Attacked the C2 **detector**, `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/llamacpp-live/controls.py`, at assigned commit `54a29268e2083caa2b1e0d54ee1e7d90961302f3`; did not mutate either lifecycle tool, receipt gate, probe, or server contract.

Axes: detector calibration; attributed rejection coverage; gate re-derivation coverage; positive-control exit discrimination; exact restoration/isolation. Independent prerequisite reads ran concurrently. Behavioral runs were deliberately serial, with at most one generated fake active for this seat.

Claim anchors:
- `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-17.md:166-170`: “6 accepted-bad” and “gate-flip arm 0 accepted.”
- `/home/vgpnk/Projects/shokunin/kama-shokunin/SCORECARD.md:681`: “each failing its targeted check.”

# Detector and baseline

The bounded behavioral command was the full K0–K8 `controls.py --tool ABS --gate ABS --probe ABS --json`, once per frozen/current pair per phase. No `--only`, fixture changes, timeout edits, or input substitutions. Each invocation had an external 600-second bound; original per-tool/per-gate bounds remained 180/60 seconds. All 18 invocations completed, emitted parseable JSON, and had empty stderr.

The **numeric mutation oracle** compared `(accepted_bad, gate_flip_bad, inconclusive, good_ok, process_exit)` against the reproduced pristine values:
- frozen: `(6, 0, 1, true, 1)`;
- current: `(0, 0, 0, true, 0)`.

Frozen process exit 1 is the expected result of measuring a known-defective target, not a failed mutation baseline. Both pristine signatures matched the stated expectations. A mutant is called *killed by the numeric oracle* only when that signature changes and exact-byte restoration returns the baseline. An exit-only oracle kills none of these four mutants: frozen always exited 1 and current always exited 0.

## Actual output summary

Every table entry is observed JSON plus the observed process return code. `flip arms` counts non-null per-row `gate_flip` results, not accepted flips. T = true.

| Phase | Frozen: accepted_bad / gate_flip_bad / inconclusive / good_ok / exit | Current: accepted_bad / gate_flip_bad / inconclusive / good_ok / exit | Flip arms frozen/current |
|---|---|---|---|
| pristine | 6 / 0 / 1 / T / 1 | 0 / 0 / 0 / T / 0 | 0 / 8 |
| mutant (a) | **5 / 0 / 2 / T / 1** | 0 / 0 / 0 / T / 0 | 0 / 8 |
| restored (a) | 6 / 0 / 1 / T / 1 | 0 / 0 / 0 / T / 0 | 0 / 8 |
| mutant (b) | **6 / 0 / 0 / T / 1** | 0 / 0 / 0 / T / 0 | 0 / 8 |
| restored (b) | 6 / 0 / 1 / T / 1 | 0 / 0 / 0 / T / 0 | 0 / 8 |
| mutant (c) | 6 / 0 / 1 / T / 1 | 0 / 0 / 0 / T / 0 | **0 / 0** |
| restored (c) | 6 / 0 / 1 / T / 1 | 0 / 0 / 0 / T / 0 | 0 / 8 |
| mutant (d) | 6 / 0 / 1 / T / 1 | 0 / 0 / 0 / T / 0 | 0 / 8 |
| restored (d) | 6 / 0 / 1 / T / 1 | 0 / 0 / 0 / T / 0 | 0 / 8 |

# Findings and mutants

## (a) Tool-exit-only rejection: changes frozen counts, not current counts

Source: `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/llamacpp-live/controls.py:557-565`; quote: “rejected = receipt_written and tool_exit not in (0, None)”.

Mutation: replace the entire bad-control rejection block at lines 557–565, including K6's receipt requirement, with:

```python
        rejected = tool_exit not in (0, None)
```

Attribution and gate-flip remain intact; this isolates rejection-by-exit from mutation (b).

Actual distinguishing row, frozen K6:

```text
                       pristine/restored       mutant (a)
tool_exit              4                       4
gate_exit              null                    null
receipt_written        false                   false
escaped                true                    true
failed_checks          []                      []
attributed             false                   false
accepted               true                    false
rejected               false                   true
inconclusive           false                   true
```

Thus `accepted_bad` falls 6→5, but `inconclusive` rises 1→2. It does **not** create an additional attributed detection: frozen attributed/conclusive rejections remain 1. The crash-without-receipt is merely moved from accepted-bad to inconclusive. Current outputs do not change.

Verdict: **killed by the two-pair numeric oracle; survives current-only and exit-only oracles.**

## (b) Drop attribution: removes the frozen K3 warning

Source: `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/llamacpp-live/controls.py:567-570`; quote: “inconclusive = bool(rejected and attributed is False)”.

Mutation: replace line 570 with `inconclusive = False`. Keep the `attributed` telemetry and all rejection/gate-flip predicates, so only the attribution requirement is dropped.

Actual distinguishing row, frozen K3:

```text
                       pristine/restored       mutant (b)
tool_exit              2                       2
gate_exit              1                       1
receipt_written        true                    true
failed_checks          []                      []
attributed             false                   false
accepted               false                   false
rejected               true                    true
inconclusive           true                    false
```

`accepted_bad` remains 6; `inconclusive` changes 1→0. Derived conclusive bad rejections rise 1→2, despite K3 having no recorded failed checks. Current outputs do not change.

Verdict: **killed only if the two-pair oracle includes the inconclusive count; survives the accepted-bad headline, current-only, and exit-only oracles.**

## (c) Drop gate-flip: numeric survivor despite deleting all current flip coverage

Source: `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/llamacpp-live/controls.py:572-574`; quote: “gate_flip = _gate_flip(st, gate, receipt_doc, failed)”.

Mutation: delete only lines 573–574. Keep `gate_flip = None` and the normal aggregation unchanged.

Aggregation source: `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/llamacpp-live/controls.py:676-678`; quote: “result['gate_flip_bad'] += 1”. It increments only for a non-null accepted flip.

Actual current K1–K8 flip outputs:

| Control | Pristine and restored `gate_flip` | Mutant (c) |
|---|---|---|
| K1 | exit 1, rejected true, accepted false, flipped 1, setup_error null | null |
| K2 | exit 1, rejected true, accepted false, flipped 1, setup_error null | null |
| K3 | exit 1, rejected true, accepted false, flipped 2, setup_error post-probes:child-exited-rc0 | null |
| K4 | exit 1, rejected true, accepted false, flipped 1, setup_error null | null |
| K5 | exit 1, rejected true, accepted false, flipped 1, setup_error null | null |
| K6 | exit 1, rejected true, accepted false, flipped 1, setup_error internal:RuntimeError | null |
| K7 | exit 1, rejected true, accepted false, flipped 3, setup_error ready-timeout | null |
| K8 | exit 1, rejected true, accepted false, flipped 1, setup_error null | null |

Frozen already had zero applicable flip arms. Both reported signatures remain identical, including `gate_flip_bad=0`; current still exits 0 after doing **zero** flips rather than eight. All other compared grading-row fields are unchanged.

Verdict: **survives the two-pair numeric oracle and current-only oracle.** A full-row/non-null-arm coverage assertion would distinguish this mutant; the reported zero accepted flips alone does not distinguish rejection from non-execution. This is a measurement-coverage finding, not evidence that the current receipt gate accepts doctored receipts.

## (d) K0 accepts -15: numeric and grading-row survivor

Source: `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/llamacpp-live/controls.py:551-555`; quote: “accepted = (tool_exit == 0 and gate_exit == 0”.

Mutation: change the K0 predicate to:

```python
        accepted = (tool_exit in (0, -15) and gate_exit == 0
                    and not escaped and not tool_timed_out)
```

This is explicitly K0's **tool-process exit** predicate, not a change to the fake server's teardown returncode or to K8. Gate/receipt/timeout requirements remain intact.

Actual K0 output on both pairs, pristine, mutated, and restored: `tool_exit=0`, `gate_exit=0`, `receipt_written=true`, `failed_checks=[]`, `accepted=true`, `good_ok=true`. All compared grading-row fields and both numeric signatures are unchanged.

Verdict: **survives both pair oracles.** [INFERENCE] These runs do not exercise K0's added `tool_exit=-15` acceptance branch, so they cannot demonstrate that this acceptance weakening is detected. No claim is made that an observed real run took that branch.

# Current baseline row evidence

This also fixes what “unchanged current” means for the four mutations. Every current bad row had a receipt, gate exit 1, and `accepted=false`, `inconclusive=false`.

| Control | Tool exit | Failed checks | Attributed |
|---|---|---|---|
| K1 | 1 | health_ready | true |
| K2 | 1 | loading_envelope_graded | true |
| K3 | 2 | teardown_graceful, teardown_port_closed | true |
| K4 | 1 | teardown_graceful | true |
| K5 | 1 | teardown_graceful | true |
| K6 | 2 | teardown_graceful | true |
| K7 | 2 | teardown_graceful, teardown_port_closed, loading_envelope_graded | null (no attribution expected) |
| K8 | 1 | teardown_graceful | true |

# Exact execution commands and exit codes

Clone/check out, exit **0**:

```sh
git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/KamaR17.MutControlsSelf-clone && git -C /tmp/KamaR17.MutControlsSelf-clone checkout -q 54a29268e2083caa2b1e0d54ee1e7d90961302f3
```

The following are the exact detector argv, rendered in shell form with the two environment overrides. Executed using Python `asyncio.create_subprocess_exec`, cwd `/tmp/KamaR17.MutControlsSelf-clone`, inherited environment otherwise unchanged. Each phase in the output table ran **F then C**, with the indicated detector bytes; the exit codes for every invocation are in that table. No detector command ran in the lane.

**F (frozen tool + frozen gate):**

```sh
env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/KamaR17.MutControlsSelf-evidence/tmp /usr/bin/python /tmp/KamaR17.MutControlsSelf-clone/tests/llamacpp-live/controls.py --tool /tmp/KamaR17.MutControlsSelf-clone/.ufo/waves/round-17/frozen/tools_kama-llamacpp-live.py --gate /tmp/KamaR17.MutControlsSelf-clone/.ufo/waves/round-17/frozen/tests_llamacpp-live_check-receipt.py --probe /tmp/KamaR17.MutControlsSelf-clone/tools/kama-probe.sh --json
```

**C (current tool + current gate):**

```sh
env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/KamaR17.MutControlsSelf-evidence/tmp /usr/bin/python /tmp/KamaR17.MutControlsSelf-clone/tests/llamacpp-live/controls.py --tool /tmp/KamaR17.MutControlsSelf-clone/tools/kama-llamacpp-live.py --gate /tmp/KamaR17.MutControlsSelf-clone/tests/llamacpp-live/check-receipt.py --probe /tmp/KamaR17.MutControlsSelf-clone/tools/kama-probe.sh --json
```

Order: pristine F/C; mutant-a F/C; restored-a F/C; mutant-b F/C; restored-b F/C; mutant-c F/C; restored-c F/C; mutant-d F/C; restored-d F/C. This is 18 complete K0–K8 invocations. Observed durations in that order, seconds: `15.954, 15.786, 19.727, 22.250, 16.199, 29.255, 19.290, 15.958, 15.605, 15.938, 107.120, 15.628, 15.564, 15.954, 101.862, 36.058, 15.439, 16.271`. Timing was not a mutation oracle.

Initial hash command, exit **0**:

```sh
sha256sum /tmp/KamaR17.MutControlsSelf-clone/tests/llamacpp-live/controls.py /tmp/KamaR17.MutControlsSelf-clone/tools/kama-llamacpp-live.py /tmp/KamaR17.MutControlsSelf-clone/tests/llamacpp-live/check-receipt.py /tmp/KamaR17.MutControlsSelf-clone/tools/kama-probe.sh /tmp/KamaR17.MutControlsSelf-clone/.ufo/waves/round-17/frozen/tools_kama-llamacpp-live.py /tmp/KamaR17.MutControlsSelf-clone/.ufo/waves/round-17/frozen/tests_llamacpp-live_check-receipt.py
```

Final hash command, exit **0**:

```sh
sha256sum /tmp/KamaR17.MutControlsSelf-clone/tests/llamacpp-live/controls.py /tmp/KamaR17.MutControlsSelf-clone/tools/kama-llamacpp-live.py /tmp/KamaR17.MutControlsSelf-clone/tests/llamacpp-live/check-receipt.py /tmp/KamaR17.MutControlsSelf-clone/tools/kama-probe.sh /tmp/KamaR17.MutControlsSelf-clone/.ufo/waves/round-17/frozen/tools_kama-llamacpp-live.py /tmp/KamaR17.MutControlsSelf-clone/.ufo/waves/round-17/frozen/tests_llamacpp-live_check-receipt.py /home/vgpnk/Projects/shokunin/kama-shokunin/tests/llamacpp-live/controls.py
```

`ss -ltnp` ran before the probes and twice after all probes, exit **0** each time. Final listener PID attribution read command lines only to test for this seat's scratch prefix, without printing their contents; observed `seat_owned_listening_pids=[]`. Other seats' listeners were not touched. The socket listings contained no listener on 8080 or 34113; this seat's fake selection retained the original registered-port refusals.

Version commands, each exit **0**: `/usr/bin/python --version` → `Python 3.14.8`; `git --version` → `git version 2.56.0`; `curl --version` → `curl 8.23.0`.

# Before/after hashes and restoration

Original detector SHA-256, identical in the initial clone, final clone, final lane source, and **all four exact-byte restores**:

`aad8b1c758fe9616ecd7ad78538dbfd82227c7e99df3b051d2bf82d34d6e3a06`

| Mutant | Mutated detector SHA-256 | Restored bytes equal pristine | Restored F/C numeric signatures equal baseline |
|---|---|---|---|
| a | 0ad341daea8f1c096b29cc214aa0171f2c2a6b679c8cec4373f84685d4977b1d | true | true / true |
| b | fd46b00e59d1f6728427a46d93bd634237e61c9618eb35cd56770e151fbb8314 | true | true / true |
| c | c3b936ac91e828621e0229b26aa724a4d60de8cf6ca18939765790b9380b47e7 | true | true / true |
| d | dd720d01207a18d2f247af9b34a8b6e921a8ceb3a6a284f35df4029ed31c180c | true | true / true |

Unmutated target inputs, same SHA-256 before/after:

| Absolute input | SHA-256 |
|---|---|
| /tmp/KamaR17.MutControlsSelf-clone/tools/kama-llamacpp-live.py | 0efd1723b02ef748d720a6036d3ac481b1d5fe9755110999d7c9acaf486c46ac |
| /tmp/KamaR17.MutControlsSelf-clone/tests/llamacpp-live/check-receipt.py | ad6801791f2ada896a7ee188609391aac86185c47320dbf415331869ca9cd2a5 |
| /tmp/KamaR17.MutControlsSelf-clone/tools/kama-probe.sh | 36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3 |
| /tmp/KamaR17.MutControlsSelf-clone/.ufo/waves/round-17/frozen/tools_kama-llamacpp-live.py | b8c5e8d402595f3b919ea82f29c87f9a2b5d5c2d88bccffa48f1f8880c2f4fe4 |
| /tmp/KamaR17.MutControlsSelf-clone/.ufo/waves/round-17/frozen/tests_llamacpp-live_check-receipt.py | 6b9576a13dde1872977a6af4547599a75cf484f37fe6fe0f4f5557349b09ced6 |

Each mutation was restored before the next was applied; both full commands were rerun after every restore. Byte equality was checked against the in-memory pristine bytes, not merely inferred from gate output.

Cleanup command, exit **0**, output exactly `scratch_removed=true`:

```sh
rm -rf -- /tmp/KamaR17.MutControlsSelf-clone /tmp/KamaR17.MutControlsSelf-evidence && test ! -e /tmp/KamaR17.MutControlsSelf-clone && test ! -e /tmp/KamaR17.MutControlsSelf-evidence && printf 'scratch_removed=true\n'
```

# Limitations and installs

- Scope is these four detector weakenings and generated fake-server controls. No real llama.cpp runtime was invoked; real-run receipts and broader C2 admission were not re-evaluated.
- Survivors are explicitly relative to the numeric oracle. Mutant (c) changes eight per-row flip objects to null and is not invisible to a full-row coverage assertion. Mutant (d) adds an unexercised tool-process signal-exit branch; it is not a demonstration that the receipt gate accepts a server returncode of -15.
- Temporary raw JSON captures were removed with scratch as required; the observed numeric outputs, distinguishing rows, exact commands, source anchors, hashes, and restoration evidence are preserved here.
- Lane writes: only this assigned Report. No lane source, fleet root, sibling source, manifest, state, routing, or VCS writes. No subagents. No protected session/history/credential stores were accessed.
- Installs/updates: **none**. Used existing Python 3.14.8, Git 2.56.0, curl 8.23.0, and `ss`. No pacman transaction or host-service change.
