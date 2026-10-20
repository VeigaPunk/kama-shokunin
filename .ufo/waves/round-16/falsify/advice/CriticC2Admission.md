VERDICT: partial — C2 `live-llamacpp-lifecycle` as a capability acquisition (AXES.md §Capabilities, PROVINCE round-16 note, KQ5) and its operability 8 → 8 score

Seat `KamaR16.CriticC2Admission`, read-only critic, lane commit `b8e485c`. I did not start llama-server. I ran the live tool once with a stand-in `--server` (a python stub, described below) and ran the receipt gate on L1's receipts and on /tmp copies.

## Summary

| Question | Finding |
|---|---|
| Does the demonstration run and verify? | **Confirm.** L1's two receipts pass the gate with every pin set. `RerunLiveHarness` also reproduced the run independently: 10/10 checks, identical to L1's. |
| Is 8 → 8 honest? | **Confirm.** The number is not inflated. The credit belongs in the capability row only. That row may enter only after the measured block exists (D5). |
| Does it stay inside the province? | **Partial.** The write boundary and KQ5 hold. Two defects remain. (1) The PROVINCE note's guarantee to probe "only the server this tool started" is not enforced at the HTTP layer: my run sent 188 GETs to a listener the child did not own (D1). (2) The note decides part of a question that round 1 sent to L0 (D6). |
| Is the provenance exact? | **Partial.** By default the gate does not check that the server is b11755 (D2). The run never captured the loading window, although "lifecycle" and the tool docstring suggest it (D4). The gate and the producer use different words for the ownership state (D3). |

## Evidence

### E1. The receipts validate with every pin, and the gate self-test passes (confirm)
- `python3 tests/llamacpp-live/check-receipt.py .ufo/waves/round-16/live/receipt.json --expect-model-sha256 270cba1b…256d --expect-server-sha256 b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804` → exit 0, `VALID`.
- The same command on `receipt-frozen-probe.json` → exit 0, `VALID`.
- `--expect-probe-sha256 6edd3c4c…fa50` (sha256 of `tools/kama-probe.sh`, equal to the `b8e485c` blob) → exit 0.
- `--selftest` → exit 0, "16 mutations + unreadable case all rejected; valid receipt accepted".
- `sha256sum ~/.local/opt/llama-b11755/llama-server` → `b6a31a8e…d804`, equal to the receipt.
- Sibling evidence (not my run): `falsify/advice/RerunLiveHarness.md:3` reports "ALL 10 CHECKS IDENTICAL". `RerunLiveNegatives.md` reports refusal exits 3/2/2/2/2. `SentinelHostFootprint.md:22` reports the install tree re-hashes to `6c216313…`.

### E2. KQ5 and the write boundary (confirm)
- The receipt records env names only: `child_env_keys ["HOME","LANG","PATH"]`.
- The log keeps 3 lines (`load_model`, `model loaded`, `listening on http://127.0.0.1:32845`). They contain no config, env, session or journal body.
- `argv` has no `systemctl`, `sudo` or `docker`. No unit or timer is involved, and no consumer is repointed.
- KQ5 rejects an admission that "requires enabling services, repointing consumers, installing timers, copying config/environment/session/journal bodies" (`corpus/QUALITY.md:13`). None of these happened.

### E3 → D1. The tool sends requests to a listener it does not own before it checks ownership (refute of the PROVINCE guarantee; fixable)
The PROVINCE note promises to probe only this tool's own server. `PROVINCE.md:61-62` says the narrowing applies "only for the process this tool started; any other unregistered endpoint still needs L0".

In `readiness_loop` (`tools/kama-llamacpp-live.py:405-443`), `http_get` runs on every poll. The ownership check (`port_owned_by`) runs only after `/health` answers 200. Any other answer keeps the loop polling whatever listener holds the port.

Counterexample, run deterministically:
- Stand-in server: `/tmp/kama-r16-CriticC2Admission/fake-server.py`, which is not llama-server. The launched process never listens. A double-forked `setsid` stranger binds the port the harness picked, logs each GET and answers 503 with the loading body. It exits by itself after 15 s. This simulates the race noted in the receipt's `port_pick_note`: another process takes the port after the harness releases it.
- Command: `python3 tools/kama-llamacpp-live.py --server ./fake-server.py --model dummy.gguf --model-sha256 <sha of dummy> --ready-timeout 2 --out race-receipt.json` → **exit 2**.
- Stranger log: **188 requests** (94 `/health`, 94 `/v1/models`) on kernel-chosen port 46303.
- Receipt: `setup_error ready-timeout`, `port_listener_ownership unproven`, **`loading_observed True`, `loading_envelope_exact True`**. The receipt records a loading observation taken from a process that is not its child. `teardown_port_closed` is False: the stranger outlived the process-group kill.
- `check-receipt.py race-receipt.json` → exit 1, `INVALID … 19 problem(s)`. The gate fails closed, so no false VALID receipt results.

Impact: adjacency and the province. The probe-own-server-only promise does not hold when the port is taken by another process; the run is then exactly the round-1 #3 case (an endpoint outside the registry, contacted without L0). The gap is narrow: only GET-only metadata requests go out, and the race needs another process to win the port within milliseconds. It is still real, and the PROVINCE note states the guarantee without qualification.

Smallest fix: in `readiness_loop`, check `port_owned_by(proc.pid, port) is True` before any `http_get`. Until it holds, wait on `/proc/net/tcp` without sending HTTP; time out or treat child exit as a setup error. This is about 5 lines of stdlib code. Then add a self-test case or control that uses this stub.

### E4 → D2. Without pins, the gate accepts a receipt from a different llama.cpp build (fixable)
Mutation of a /tmp copy of `receipt.json`:
- `server.sha256`, `install_tree['llama-server']` and `server_impl_sha256` set to other digests;
- `realpath`/`arg`/`argv[0]` set to `/usr/bin/llama-server`;
- `/props` `build_info` set to `b9999-deadbeef`.

Gate results:
- no pins → **exit 0 VALID**;
- `--expect-model-sha256` only → **exit 0 VALID**;
- `--expect-server-sha256 b6a31a8e…` → exit 1.

The gate never checks `build_info` (`grep build_info check-receipt.py` matches only the self-test fixture). Also, `/props` is captured with `keep_body=False` (`kama-llamacpp-live.py:497`). The `b11755-704366d76` evidence cited at `llamacpp-loading-lifecycle.md:95` is therefore a producer summary, and the gate cannot re-derive it from stored bytes.

The counting commands do not require the server pin:
- `SKILL.md:533` lists the pins as optional (`[--expect-server-sha256 H]`);
- `controls.txt` shows bare `VALID` lines;
- the falsify `RerunLiveHarness` ran with `--expect-model-sha256` only.

The actual receipts are b11755 (E1). Future re-runs are not bound to it, while `SHONEN.md:8` and the capability row say "pinned llama.cpp b11755".

Smallest fix: the capability row's evidence command must pass all three `--expect-*-sha256` values. Optionally add a `props_build_info` check, and keep the `/props` body.

### D3. The gate and the producer use different ownership words (the M2 mistake class again; low)
- Producer: `{True: 'child', False: 'foreign', None: 'unproven'}` (`kama-llamacpp-live.py:851`, `:461`).
- Gate: `if own not in ("child", "foreign", "unknown")` (`check-receipt.py:363`).

The gate rejects the producer's `unproven` and accepts `unknown`, a value the producer never emits. The mismatch shows up only on failure paths: the E3 receipt was flagged `'unproven' not in child|foreign|unknown`. This is the same class as lesson M2 (`round-16.md:65`, the self-authored self-test hides producer drift). Fix: the gate's set becomes `child|foreign|unproven`, plus one self-test mutation.

### D4. The loading phase was never captured live (calibration wording; low)
- `receipt.json` and `receipt-frozen-probe.json` both have `loading_observed false` and `loading_503 null`. The transitions are refused → refused → `/health` 200, and the model loads in about 8 ms.
- The independent re-run also had `loading_observed false` (`RerunLiveHarness.md`).
- The tool docstring (`kama-llamacpp-live.py:7`) says it "captures the documented HTTP lifecycle surfaces (loading -> ready)".
- `llamacpp-loading-lifecycle.md:105-106` supports the loading window with "An earlier L1 smoke run (10:17 -03, not receipted)". That is an unreceipted observation used as support. The entry does say it was not receipted, and line 122 lists the limit honestly.

Smallest fix: the capability row says "loading window not captured (loading_observed=false in all receipted runs)". Do not cite the 10:17 smoke as evidence. Optionally change the docstring to "(loading, if the window is long enough to sample)".

### D5. The capability row's evidence pointer is not closed yet (blocking until L1 appends)
- `SCORECARD.md:598` (end of file): "Measured values are appended below after execution." Nothing is appended and no capability row exists. `grep live-llamacpp-lifecycle` matches only the claim text at `:588`. This is not pre-claiming, because no row exists.
- `corpus/lessons/round-16.md:93-94` cites `.ufo/waves/round-16/acceptance.json`, but `test -e` reports that file missing at `b8e485c`.

AXES.md:63-64: "a capability without a passing demonstration in the round report is pre-claiming and does not enter the table." The row must enter only together with the appended measured block, and the acceptance pointer must resolve.

### D6. The PROVINCE note decides part of a question round 1 sent to L0 (judge's tradeoff, not a lane fix)
- `corpus/lessons/round-1-safety.md:78,88-89` lists under "Ambiguities requiring L0 operator decision": "L0 must approve any endpoint outside the declared local model registry."
- `PROVINCE.md:61` now says "This narrows round 1's … rule only for the process this tool started."
- `LOG.md:264`: "a province revision is an L0/fleet decision, not a lane self-edit."

Before `b8e485c`, contacting an unregistered port such as `127.0.0.1:32845` needed L0. After it, the lane does so on its own authority. For the L0 requirement this is an exemption: the lane gains authority. It is not a narrowing of what the lane may do, which is how `ReviewProvinceBoundary.md:26` frames it ("narrows lane probing authority; never widens it"). No L0 line was filed: LOG §round 16 lists none.

Arguments for the lane:
- Fleet precedent allows appended PROVINCE classification notes (for example `.ufo/reports/round-22/kasegi.md:29`: "a classification, not a re-scope").
- Round-1 ambiguity #3 is headed "non-model services", and the fixture is a model service the lane authored [INFERENCE: intent reading].

Smallest safe correction: append one L0 question asking L0 to ratify that a lane-authored, tool-owned, loopback fixture is exempt from round-1 ambiguity #3, and qualify the PROVINCE sentence as pending that ruling. D1 must land either way, because the exemption's own premise ("only the process this tool started") is currently not enforced.

## Score verdict (operability 8 → 8)
Honest. The numeric 8 should stay:
- the caps at `SCORECARD.md:26-28` still apply (one engine, host paths, invocation-driven);
- 8 is the saturation line (`SCORECARD.md:132`);
- rounds 11-15 credited capabilities and repairs at delta 0, and round 14's capability row is the precedent;
- D1-D4 are open, so a raise to 9 would be unsupported.

I found no operability harm: the existing tools are untouched, apart from the C1 probe change that C1 claims, and the frozen-probe control passes 10/10. The per-axis verdict should read "improved through the capability row only", with the row text bounded by D2, D4 and D5.

## Impacted axes
- **Adjacency/province:** D1, D6.
- **Calibration:** D2, D3, D4, D5.
- **Operability:** none harmed; the capability is real and was reproduced.

## Limitations
- I started no llama-server. The race was simulated with a stand-in server. I did not measure how often a real llama-server hits the race [INFERENCE: rare, since the release-to-rebind gap is sub-second].
- Port probing for refusal controls was not repeated; the sibling `RerunLiveNegatives` covers it.
- I did not trace llama-server's own filesystem writes (no strace).
- Teardown of my run:
  - `pgrep -x llama-server` → exit 1 before and after;
  - `pgrep -af fake-server.py` → exit 1;
  - `ss -Hltn 'sport = :46303'` → 0 lines;
  - no `/tmp/kama-llamacpp-live-*` left behind.
- Scratch `/tmp/kama-r16-CriticC2Admission/` (stub, dummy model, race receipt, mutated receipt, stranger log) was removed after this report was written.

## Installs
None.
