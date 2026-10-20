VERDICT: partial — v1 accepts degraded health and self-exit, plus evidence-consistent SIGKILL/non-exact-loading forgeries; it already rejects unproven ownership; both derivation mutants survive --selftest.

# C2 baseline receipt-gate mutation probe

Axes: **operability** (fail-capable lifecycle checks) and **calibration** (whether the validator and its selftest detect weakened predicates).

This is scoped scratch evidence, not claim admission, integration, or an official before→after measurement. Only this Report was written in the lane. All mutations were under `/tmp`; neither frozen bytes nor the round-16 receipt were modified.

## Inputs, detector, and bounds

- Receipt: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-16/live/receipt.json`.
- Frozen v1 gate: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/frozen/tests_llamacpp-live_check-receipt.py`.
- Scratch root used, subsequently removed: `/tmp/kama-r17-mut-baseline-receipt-gate-qLSpHM`.
- Existing interpreter observed: `Python 3.14.8` from `python3 --version`.
- Each invocation had a 45-second subprocess timeout, captured stdout/stderr, and scratch cwd. Independent invocations ran concurrently. No invocation timed out. Every captured stderr was empty.
- Receipt detector, used unchanged before mutation, on mutation, and after exact restoration:

```text
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/frozen/tests_llamacpp-live_check-receipt.py /tmp/kama-r17-mut-baseline-receipt-gate-qLSpHM/<case>.json
```

- Code-mutant detector, likewise run on pristine, mutated, and restored copies:

```text
python3 /tmp/kama-r17-mut-baseline-receipt-gate-qLSpHM/health-gate.py --selftest
python3 /tmp/kama-r17-mut-baseline-receipt-gate-qLSpHM/teardown-gate.py --selftest
```

The gate documents `0 receipt valid, 1 receipt invalid` at `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/frozen/tests_llamacpp-live_check-receipt.py:31-32`; quote: “0 receipt valid, 1 receipt invalid”.

## Receipt mutations and actual results

Each case started from its own exact-byte copy of the round-16 receipt. Mutated JSON serialization was `json.dumps(receipt, indent=2, sort_keys=True) + '\n'`. JSON pointers below identify **all semantic changes**. No check `passed` flag was altered.

The literal requested mutations were run first as distinct cases. Two additional constructions align duplicated evidence to distinguish a contract failure from an internal-consistency failure; they are not counted as independent lifecycle behaviors.

| Case | Changed JSON leaves | Pristine / mutated / restored exits | Mutated stdout and verdict |
|---|---|---|---|
| `health-degraded` | `/captures/health/body` → `{"status":"degraded"}`; HTTP status stays 200 | `0 / 0 / 0` | `VALID /tmp/kama-r17-mut-baseline-receipt-gate-qLSpHM/health-degraded.json` — **SURVIVED** |
| `self-exit-rc0` | `/teardown/sigterm_sent` → false; existing returncode remains 0 | `0 / 0 / 0` | `VALID /tmp/kama-r17-mut-baseline-receipt-gate-qLSpHM/self-exit-rc0.json` — **SURVIVED** |
| `sigkill-raw` | `/teardown/sigkill_sent` → true; `/teardown/returncode` → -9; check observation stays 0 | `0 / 1 / 0` | `INVALID …: 1 problem(s)`; exact problem below — **KILLED for inconsistent evidence**, not for SIGKILL |
| `loading-raw` | `/loading_envelope_exact` → false; `/transitions/1/body` → non-exact body below; `loading_503.body` stays exact | `0 / 1 / 0` | `INVALID …: 1 problem(s)`; exact problem below — **KILLED for inconsistent evidence**, not for the loading-envelope violation |
| `ownership-unproven` | `/port_listener_ownership` → `"unproven"` | `0 / 1 / 0` | `INVALID …: 1 problem(s)`; exact problem below — **KILLED** |
| `sigkill-coherent` | `sigkill-raw`, plus `/checks/7/observed/returncode` → -9 and `/checks/7/observed/sigkill_sent` → true | `0 / 0 / 0` | `VALID /tmp/kama-r17-mut-baseline-receipt-gate-qLSpHM/sigkill-coherent.json` — **SURVIVED** |
| `loading-coherent` | `loading-raw`, plus `/loading_503/body` → same non-exact body; update `/loading_503/body_sha256` and `/transitions/1/body_sha256` to its actual digest | `0 / 0 / 0` | `VALID /tmp/kama-r17-mut-baseline-receipt-gate-qLSpHM/loading-coherent.json` — **SURVIVED** |

Non-exact loading body, still valid JSON and HTTP 503:

```json
{"error":{"message":"Not the loading envelope","type":"unavailable_error","code":503}}
```

Its SHA-256 is `b2fd8219b1883b27a1fcfc4245256f03a145a9668773ad507a400eaf0c7e1518`.

Exact rejection outputs:

```text
INVALID /tmp/kama-r17-mut-baseline-receipt-gate-qLSpHM/sigkill-raw.json: 1 problem(s)
  - teardown_exited: observed.returncode 0 != teardown.returncode -9
INVALID /tmp/kama-r17-mut-baseline-receipt-gate-qLSpHM/loading-raw.json: 1 problem(s)
  - loading_envelope_exact is False but re-derivation from the stored loading_503 body gives True
INVALID /tmp/kama-r17-mut-baseline-receipt-gate-qLSpHM/ownership-unproven.json: 1 problem(s)
  - port_listener_ownership is 'unproven' — a valid receipt requires the ready listener proven to be our child
```

Every pristine and restored receipt invocation printed `VALID` followed by that case's same absolute path and exited 0. Thus no baseline failure makes these results inconclusive.

### Findings and source anchors

1. **Degraded ready-body forgery is accepted.** `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/frozen/tests_llamacpp-live_check-receipt.py:628-637`; quote: `elif health_status != 200:`. The observed mutation changed only the stored health body, not status; it still returned VALID. The baseline documentation explicitly names the body at `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-16/live/receipt.json:97`; quote: `GET /health returns 200 {"status":"ok"} once the model is loaded`.
2. **Harness-initiated SIGTERM is not required by the v1 validator.** `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/frozen/tests_llamacpp-live_check-receipt.py:745-756`; quote: `elif teardown.get("returncode") is None:`. Flipping only `sigterm_sent` to false while keeping rc 0 was accepted. The original receipt records rc 0 / SIGKILL false / SIGTERM true at `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-16/live/receipt.json:412-416`; quote: `"sigterm_sent": true`.
3. **SIGKILL/-9 is accepted once the copied observation agrees.** `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/frozen/tests_llamacpp-live_check-receipt.py:748-756`; quote: `"returncode" in o and o["returncode"] != teardown.get(`. The raw forgery was rejected solely for disagreement with observed rc 0; the coherent forgery was accepted with raw and observed rc -9 / SIGKILL true. Do not count the raw rejection as SIGKILL detection.
4. **A correctly reported non-exact loading envelope is accepted.** `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/frozen/tests_llamacpp-live_check-receipt.py:420-432`; quote: `loading_envelope_exact is a receipt FIELD (bool|null), not a check.` The gate rejects a false flag beside the original exact body, but accepts false when both stored 503 bodies actually have the non-exact message. This exercises the behavior rather than only the flag-consistency guard.
5. **Unproven listener ownership is already rejected.** `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/frozen/tests_llamacpp-live_check-receipt.py:434-440`; quote: `requires the ready listener proven to be our child`. The ownership-only forgery exits 1 despite unchanged passing check flags. This finding limits the C2 before-evidence: it does not establish an ownership blind spot in the frozen v1 receipt gate.

**Counting interpretation:** 2/5 literal constructions are accepted. Substituting the evidence-consistent SIGKILL and loading constructions for their inconsistent versions produces acceptance for 4/5 tested logical behaviors; only ownership is rejected. These are scratch receipt-gate observations, not the official fake-server controls measurement.

## Frozen-gate derivation mutants versus --selftest

Each mutant occupied a separate pristine copy. Only one behavior-bearing source line changed per copy; required checks, fixtures, expected exit codes, and selftest implementation remained unchanged.

| Mutant | Source anchor and exact change | Expected detector | Actual pristine / mutant / restored | Verdict |
|---|---|---|---|---|
| Health mistakenly treats loading HTTP 503 as ready | `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/frozen/tests_llamacpp-live_check-receipt.py:631`; quote: `elif health_status != 200:` → `elif health_status not in (200, 503):` | `--selftest` should exit nonzero if it covers this readiness weakening | `0 / 0 / 0`, identical stdout below | **SURVIVED** |
| Teardown confuses presence of a returncode key with a reaped process | `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/frozen/tests_llamacpp-live_check-receipt.py:748`; quote: `elif teardown.get("returncode") is None:` → `elif "returncode" not in teardown:` | `--selftest` should exit nonzero if it covers a present-but-null returncode | `0 / 0 / 0`, identical stdout below | **SURVIVED** |

Actual stdout for **all six** selftest invocations; stderr empty:

```text
selftest: 26 mutations + unreadable case all rejected; valid receipt accepted
```

The output wording is sourced at `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/frozen/tests_llamacpp-live_check-receipt.py:1094-1095`; quote: `all rejected; valid receipt accepted`. It remains green under both weakened predicates: 2/2 assigned derivation mutants survive this detector. This is a selftest coverage finding, not permission to weaken the lifecycle contract.

### Behavioral witnesses establish that the mutants changed acceptance

These supplementary witnesses were also derived from the round-16 receipt; they were not inserted into any lane test matrix.

- Health witness: `/captures/health/status` and `/checks/0/observed/status` → 503.
- Teardown witness: `/teardown/returncode` and `/checks/7/observed/returncode` → null.

Each witness was passed to the immutable frozen gate, its matching mutated scratch gate, and the restored scratch gate. The respective exits were **1 / 0 / 1** for both witnesses. Exact outputs:

```text
INVALID /tmp/kama-r17-mut-baseline-receipt-gate-qLSpHM/health-witness.json: 1 problem(s)
  - health_ready: captures.health.status 503 != 200
VALID /tmp/kama-r17-mut-baseline-receipt-gate-qLSpHM/health-witness.json
INVALID /tmp/kama-r17-mut-baseline-receipt-gate-qLSpHM/health-witness.json: 1 problem(s)
  - health_ready: captures.health.status 503 != 200
INVALID /tmp/kama-r17-mut-baseline-receipt-gate-qLSpHM/teardown-witness.json: 1 problem(s)
  - teardown_exited: teardown.returncode is null (process never reaped)
VALID /tmp/kama-r17-mut-baseline-receipt-gate-qLSpHM/teardown-witness.json
INVALID /tmp/kama-r17-mut-baseline-receipt-gate-qLSpHM/teardown-witness.json: 1 problem(s)
  - teardown_exited: teardown.returncode is null (process never reaped)
```

Witness findings use the same source anchors as the two mutants above. The expected original rejection is not a failing baseline for the mutation detector: the actual detector under challenge is `--selftest`, whose pristine run passed in both cases.

## Hashes and exact restoration

Input hashes were taken before mutation and again after restoration. The original receipt and frozen gate remained byte-identical throughout the probe.

| Input / restored copy class | Before SHA-256 | After SHA-256 |
|---|---|---|
| Original receipt and all seven restored receipt case copies | `076865e5b2de909604c5783d48ec5bf691310763949439d333c42ee5bdbd4669` | `076865e5b2de909604c5783d48ec5bf691310763949439d333c42ee5bdbd4669` |
| Original frozen gate and both restored scratch gate copies | `6b9576a13dde1872977a6af4547599a75cf484f37fe6fe0f4f5557349b09ced6` | `6b9576a13dde1872977a6af4547599a75cf484f37fe6fe0f4f5557349b09ced6` |

| Mutated scratch bytes | SHA-256 while mutated |
|---|---|
| `health-degraded.json` | `f44321d3908c3da962e1c33cbe24dee2ea715aad57a55e9cedbb42fb1b120f41` |
| `self-exit-rc0.json` | `e827d213dded992b703b8fed23aabc5dcebf12e43c2d319308d345ca999a0bb5` |
| `sigkill-raw.json` | `cc366d9a42c42b2e0208a7c989df812b3d5131d58439110227c1ff3abd71ea53` |
| `loading-raw.json` | `4ec9b462e98568a23c7f10fed0b76e402107c686c5e8bdd2171ba2c7d4ec8a88` |
| `ownership-unproven.json` | `b05f25e6d286476550c14eaa2623ba6c34878e5df9cf22b2591a33bf7f027ba7` |
| `sigkill-coherent.json` | `3222e4b5d75113d939f17e073a2317e7285219f7cefe1f21638e41b30be13a50` |
| `loading-coherent.json` | `7ca4ddba4612d5784a6de73d267f94d6f21e0d1a61a743b6ad26b6b9058e5ab2` |
| `health-gate.py` | `68684b324ca23397c1b9ddd96f281b596945611ec8049a5664d7d5c898b7e276` |
| `teardown-gate.py` | `283908bbc6b2bbbe28f16b69dcc98a38dd5219cd50fcd29509b4b17e23e144d7` |

All scratch filenames in this table were directly under `/tmp/kama-r17-mut-baseline-receipt-gate-qLSpHM`.

Restoration ran in `finally`, before rerunning detectors on restored bytes. Direct byte-equality checks, not only digest comparisons, produced:

```text
RESTORED_RECEIPTS_EXACT True
RESTORED_GATES_EXACT True
RESTORED_SOURCE_EXACT True True
```

The scratch tree was then removed using `rm -rf -- /tmp/kama-r17-mut-baseline-receipt-gate-qLSpHM`; `test ! -e` succeeded and the command printed:

```text
SCRATCH_REMOVED /tmp/kama-r17-mut-baseline-receipt-gate-qLSpHM
```

## Limitations and installs

- This tests the **frozen v1 validator**, not the current v2 implementation or producer behavior. No live server, fake server, model loading, or network listener was started. No ports were bound, so there was no spawned server requiring a socket teardown check.
- The degraded-health literal case intentionally changes one JSON leaf only: its old body digest/header length and recorded health transition are untouched. It demonstrates acceptance of the literal requested forgery; it is not a fully regenerated capture. Likewise, the two raw SIGKILL/loading cases deliberately expose duplicated-evidence consistency guards. Their coherent variants are explicitly separated rather than silently substituting a different mutation.
- The gate's ownership rejection is evidence about the **receipt validator**, not proof that the producer's `teardown_port_closed` predicate itself is non-vacuous. No claim is made about that producer behavior here.
- Supplemental witness receipts isolate changed derivations; they are validator inputs, not purported real server runs. No conclusion about an actual server's shutdown or readiness follows from forged JSON alone.
- No lane gates beyond the explicitly assigned frozen validator were run. No C1 mutant runner, round-16 measure, official C2 controls, VCS writes, other runtime/judge, or sibling-source edits were performed.
- Tool installs/updates: **none**. Used the existing Python 3.14.8 and existing shell/coreutils; no package transaction or host-service restart.
