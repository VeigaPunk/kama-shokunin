# A01C1PortRace — C1 live request-plane port-race attack

Axis: operability. Review target: whether the counter's outside contact can be redirected to an attacker listener during `--hold-dir`.

## Evidence

Frozen base is `a959fd9022b1ac1f3cb4dc2475d9cded8b2b01c3`; the requested master tool was present at `65d7cad0fce90e34de37527cde22e97b63b118bf` (`round-62: live request-plane tool, capability-claims registry, canonical list + ledger classifications`). Live model and `llama-server` fixtures were available at their pinned default paths. No tool was installed or updated.

Observed baseline (the counter includes its real hold-window outside contact and the control families):

```text
$ python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round62-c1-counter.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip master --work /fast/scratch/hyaku/kama-r62/w/A01C1PortRace/baseline
tool_present=1 live_ok=1/1 fake_rejected=2/2 stale_rejected=1/1 tamper_rejected=8/8 log_rejected=1/1 predead_rejected=1/1 sigterm_rejected=1/1 hold_rejected=1/1 outside_rejected=1/1 errors=0 met=True
```

## Probes

- **Adjacent-port decoy: REJECTED as a spoof path (not an observed counter run with a planted decoy).** The counter reads the exact port from the live tool's `hold.json` and POSTs to `127.0.0.1:<that port>`; it does not scan adjacent ports or derive the port from an external discovery mechanism. A listener on another port cannot receive that request. Counter's witness additionally requires the response model/alias, current child PID and held port, fingerprint shape, nonce-bearing prompt, listener ownership, and pinned model/server digests. This conclusion is source-derived, not a claim that I ran an adjacent-listener race.
- **Port-pick race: REJECTED as a false-acceptance path by the visible ownership gate; can cause denial/setup failure.** Tool obtains a candidate with `_live.pick_port(...)`, starts its child, then requires `_live.port_owned_by(proc.pid, port)` before collecting request-plane captures. A rival listener that wins the bind race will not be the child PID; tool returns `SETUP_ERROR` (`listener on … is not owned by child …`) rather than a successful receipt. The counter requires a valid successful receipt and its own witness checks. I did not run an active port-pick race; therefore no runtime ACCEPTED/REJECTED result is asserted for that attack execution.
- **Bind after teardown: REJECTED as a route to spoofing the outside request.** Counter sends its POST after observing `hold.json` and before writing the `release` file. The tool removes `hold.json` and proceeds to graceful teardown only after `hold_for_witness` observes that release. A listener bound after teardown is temporally too late to receive the completed outside POST; moreover the receipt records `port_closed`, and the counter derives `teardown_port_closed` from that receipt. I did not inject a post-teardown bind; no runtime ACCEPTED/REJECTED result is claimed for that unexecuted probe.

## Smallest safe correction

No correction indicated by this review. The remaining TOCTOU window at port selection can at most deny the run under the visible child-ownership check; do not claim adversarial-race runtime coverage from this pass. The successful baseline counter result establishes ordinary live operation, not proof against a deliberately timed attacker.
Report: .ufo/waves/round-62/w1/A01C1PortRace.md
tool_present=1 live_ok=1/1 fake_rejected=2/2 stale_rejected=1/1 tamper_rejected=8/8 log_rejected=1/1 predead_rejected=1/1 sigterm_rejected=1/1 hold_rejected=1/1 outside_rejected=1/1 errors=0 met=True
