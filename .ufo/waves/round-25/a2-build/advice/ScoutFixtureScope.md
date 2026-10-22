# ScoutFixtureScope — C2 fixture authorization and port scope

**Verdict: the round-16 lane-owned fixture is still unratified at L0 (no ruling on record), 47400-47469 is outside every registered consumer port and every lane-committed port reservation, so the port choice passes the written rule — but the block sits inside the kernel ephemeral range and was observed carrying live sockets minutes before this check, so `ss -ltn` alone is not a sufficient per-launch freedom test.**

All observations are from the lane tree at `1fc41e346853afd98cbd7010af5db4e54dc877f7` (working tree clean except the untracked `a2-build/`), read-only. No llama-server child was started by this seat.

## 1. The exact fixture scope rule

`kama-shokunin/PROVINCE.md:55-60` (round-16 note):

> "starts one llama-server child … with a pinned 1.2 MB GGUF kept in the lane-owned cache `~/.cache/kama-shokunin/`, on a free loopback port that is never a registered consumer port or a listening port, and tears it down in the same run."

`kama-shokunin/PROVINCE.md:61-64` bounds the exception:

> "narrowing round 1's \"L0 must approve any endpoint outside the declared local model registry\" only for the process this tool started, **pending L0 ratification** … any other unregistered endpoint still needs L0."

`kama-shokunin/SKILL.md:538-540` states the same in the gate section:

> "The live run is a lane-owned fixture on an unregistered loopback port. It is not service restoration, says nothing about the registered consumers (still `DEAD`) …"

The port-refusal mechanism the committed tool implements, `kama-shokunin/SKILL.md:535`:

> "refused ports 8080, 34113, every registry port and every listening port"

Cross-checked in source: `tools/kama-llamacpp-live.py:68` `HARD_REFUSED_PORTS = {8080, 34113}`; `:311-336` `refused_ports()` adds every port parsed from `registry/endpoint-consumers.tsv`; `:356-357` an explicit `--port` in that set raises `port-refused-registered`; `:371` otherwise only a port that refuses connections is offered.

## 2. The pending L0 line and later rulings

The pending entry is fleet `.ufo/l0-questions.md:58` (97-line append-only file, kama round-16):

> "Ratify or reject the lane-owned live llama.cpp fixture … marks this as narrowing round 1's \"L0 approves any endpoint outside the registry\" for that child only, pending your ruling. Decide: (a) ratify the fixture exception, or reject it; (b) keep, or remove, the persistent install, the PATH link and the model cache. Until answered, kama runs the fixture only inside steered rounds and contacts no other unregistered endpoint."

The interim sentence is the operative rule for this wave: steered-round use is the lane's declared behaviour until answered.

**No later ruling exists.** Evidence, each exit 0 unless noted:

- `grep -n '^kama |' .ufo/l0-questions.md` → lines 13, 15, 17, 21, 31, 41, 48, 52, **58**, 68, 87. Only 58 is the fixture ratification question; 68 is the separate retained-archive addendum (`~/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz`), not a decision.
- `awk 'NR==58' .ufo/l0-questions.md | grep -o 'L0 ANSWER[^|]*'` → no output (exit 1). Other kama/tsukuroi lines carry explicit `L0 ANSWER` text; this one does not.
- `grep -n -i -E 'lane-owned|fixture exception|round-16 fixture' .ufo/MANIFEST.json` → no output (exit 1).
- `.ufo/state/kama.round` = `1`, `.ufo/state/kama.mission` = `2684953`; no ruling text in either.
- Lane records agree it is open: `corpus/lessons/round-16-verifier-spotcheck.md:189` ("Open L0, operator-owned"), `PROVINCE.md:72` and `:82` ("still **pending L0 ratification**").

## 3. Port check for 47400-47469

Assignment in the attempt-2 dispatch (`a2-build/spec.json`, walk of `name` + prompt): `ExecCapacityTool` 47400-47419, `ExecLoadReplicate` 47420-47439, `ExecRawReplicate` 47440-47459, `ExecVerbosityControl` 47460-47469. Disjoint, union = the block named in the seat contract.

| Check | Result |
|---|---|
| Registered consumer ports (`registry/endpoint-consumers.tsv`, three data rows) | **8080, 34113** — no overlap |
| Lane tool refusal set (`kama-llamacpp-live.py:68,311-336`) | 8080, 34113 + every registry port + every listening port — no overlap |
| Ports named in committed lane docs/corpus | 8080, 34113, 8790, 8791, 8888, 9222, 40961, 40993, 631, 11434, 1234, 10086, 8766, 4000, 33525, 34955, 41453, 41819, 43775, 43999, 44035, 44689, 45507, 46631, 37527, 43229, 47311 (`pilot.md:6`) — **none in 47400-47469** |
| Fleet-wide committed-file scan `\b474[0-9]{2}\b` over all lanes | Only `kaidoku …/Crypto/Util/number.py:1012-1013` prime tables and `audio-shokunin/…/measurements.json` PulseAudio indices — **no TCP reservation anywhere** |
| Live listener check `ss -ltnH \| grep -E ':(474[0-9]{2}\|8080\|34113)$'` | no output, exit 1 — **nothing listening** in the block, on 8080 or on 34113 |
| Kernel ephemeral range `/proc/sys/net/ipv4/ip_local_port_range` | `32768 60999` — **the whole 47400-47469 block is inside it** |

**The caveat is observed, not theoretical.** During this check `ss -tan` showed ~140 sockets on the block: TIME-WAIT tuples on `127.0.0.1:47400-47413` (17 each on 47411-47413, 8 each on 47400-47410) and one ESTABLISHED `[2804:…]:47426 → [2607:6bc0::10]:443`. About one minute later the same count was 1: the TIME-WAITs had aged out. The tuples' direction is not determinable without process info (TIME-WAIT owners are gone), but they are confined to 47400-47413, `ExecCapacityTool`'s sub-range, consistent with a live seat's children cycling there [INFERENCE]. No listener existed at either sampling, so the written rule ("never … a listening port") was satisfied; the risk is a transient `EADDRINUSE` on rebind, and whether the child sets `SO_REUSEADDR` is **unverified**.

Conclusion: **passes the written scope rule; `ss -ltn` is an under-detecting freedom test for this block.** A seat should treat a failed bind as a port-collision retry within its own sub-range, not as a cell result, and should record the port actually used.

## 4. Scope findings the wave should carry

1. **The narrowing is tool-scoped.** `PROVINCE.md:61-63` covers "the process this tool started", i.e. `tools/kama-llamacpp-live.py`. A new `kama-context-capacity.py` is a different tool, so the literal narrowing does not name it; the broader interim practice is the L0 line's "only inside steered rounds". This is a genuine gap for L0/L1 to settle, not something a scout may rule.
2. **Verb envelope.** The round-16 admission covered a "GET-only" run (`corpus/lessons/round-16-verifier-spotcheck.md:7`, `:120`). C2's L1-L3 cells POST `/completion` with 1000-token prompts and `n_predict 600` (amendment 2). `PROVINCE.md:55-66` places no verb limit, so POST is not forbidden by the lane rule, but it exceeds what the round-16 admission recorded. Sentinel/critic should decide whether that needs an explicit sentence in the receipt.
3. **Fixed block vs round-16 precedent.** Round-16 receipts used ephemeral ports 43229 and 37527 and a documented bind(:0)-release-rebind race (`port_pick_note`). The fixed block removes the race but adds the ephemeral-range collision surface above.
4. **Pilot deviation, not a violation.** `pilot.md:6` used port 47311, outside 47400-47469; `pilot.md:3` declares it "not claim evidence" and it ran before the ranges were assigned.
5. **Concurrency wording.** `PROVINCE.md:56` says the tool "starts one llama-server child"; the wave runs four seats concurrently in disjoint sub-ranges with one child per seat. Per-seat serialization is the contract's grant; lane-wide simultaneity is not explicit in the PROVINCE note. Report-level disclosure would close it.

## 5. Confidence and unknowns

- Fixture rule text, L0 status, registered ports, listener state: **observed**, high confidence.
- TIME-WAIT attribution to the live capacity seat: **[INFERENCE]** from range ownership and ageing.
- Whether the child sets `SO_REUSEADDR` (affects rebind collision): **unverified**; needs the pinned source at 704366d76.
- Any operator ruling recorded outside `.ufo/l0-questions.md`, `MANIFEST.json` and `.ufo/state`: **not found**; not proven absent.

## Files written

- `kama-shokunin/.ufo/waves/round-25/a2-build/out/ScoutFixtureScope/port-scope-check.txt` (commands, outputs, exit codes)
- `kama-shokunin/.ufo/waves/round-25/a2-build/advice/ScoutFixtureScope.md` (this report)

No installs, no server child, no writes outside these two paths.
