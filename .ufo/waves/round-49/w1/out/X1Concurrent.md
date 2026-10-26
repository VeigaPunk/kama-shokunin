# X1Concurrent — three witnessed replays at once (round 49, kama C1 operability)

**Verdict: hypothesis held (not falsified). Three witnessed replays of receipts 1, 2 and 3 started within 4 ms wrote three distinct `ready.json` port/pid pairs, every pid's `/proc/<pid>/exe` hashed to the frozen server digest `35ac50fb…7d8d7ff0` while owning its own LISTEN socket, and after releasing all three every pid was gone, every port refused and no listener on those ports remained. Reproduced in three independent 3-way trials; a 9-way stress of the same design also held.**

Lane tip measured: `74558c71c38ceaeace15fd4cf8aa9d84977584b1` (round-49 build). All runs used a `git archive` extraction of that commit, so both tools were the measured ones.

## Method

Own observer (not the frozen C1 counter, which witnesses sequentially): `x1concurrent-observe3.py`.

```
S=/fast/scratch/hyaku/kama-r49/X1Concurrent
git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane
python3 x1concurrent-observe3.py --repo $S/lane \
  --tip 74558c71c38ceaeace15fd4cf8aa9d84977584b1 \
  --scratch $S/trial1 --out $S/trial1-evidence.json
```

Per trial the observer extracts the tree at `--tip`, then spawns three
`tools/kama-live-replay.py --receipt <tree>/.ufo/waves/round-48/c2/live/receipt-N.json --work runs/wN/work --out runs/wN/replay.json --witness-dir runs/wN/wd --witness-timeout 180`
back to back (launch deltas 0.000/0.001/0.001 s), each with its own `work`, witness dir, `HOME`, `XDG_CACHE_HOME` and `TMPDIR`. Once all three `ready.json` files exist it reads them (never trusting them) and checks, per replay: schema `kama-live-witness/v1`; ports pairwise distinct; pids pairwise distinct; `sha256(/proc/<pid>/exe)`; a loopback LISTEN inode on the announced port present in `/proc/<pid>/fd`; the `-m` cmdline argument hashing to the frozen model and `--port` equal to the announced port; `GET /health` 200. It then writes all three `release` files and checks: replay exit 0 / `match: true`, rerun `witness.released: true` and `witness.port`/`witness.pid` equal to what the observer saw, pid gone, port refuses, no LISTEN inode on the port, and no llama-server left under its own scratch (exe-path attribution; the host is shared with sibling seats).

## Evidence (3-way trial 1, `receipts/trial1-evidence.json`)

| run | receipt | ready at | port | pid | `/proc/<pid>/exe` | owned LISTEN inode | replay | witness |
|---|---|---|---|---|---|---|---|---|
| w1 | receipt-1.json | +2.70 s | 45361 | 329140 | 35ac50fb2cfd… | 620490640 | exit 0, match true | released, 150 ms |
| w2 | receipt-2.json | +2.70 s | 43847 | 329003 | 35ac50fb2cfd… | 620491421 | exit 0, match true | released, 200 ms |
| w3 | receipt-3.json | +2.70 s | 34931 | 329002 | 35ac50fb2cfd… | 620474117 | exit 0, match true | released, 200 ms |

All three were held simultaneously (released at +2.821 s), each `-m` hashed to `270cba1b…d3bd256d`, each `/health` returned `200 {"status": "ok"}`. After release: all pids gone, all ports refuse, no LISTEN inode on any of the three; `pgrep`-equivalent scan (exe digest plus argv[0]) showed baseline `[]` → after `[]`.

Reproductions:

| trial | launched | ports | pids distinct | exe frozen | exit/match | post-release | leftovers |
|---|---|---|---|---|---|---|---|
| trial1 | 3 @ +0.000–0.001 s | 45361 / 43847 / 34931 | 3/3 | 3/3 | 3× 0/true | 3× pid gone, port refuses | none |
| trial2 | 3 @ +0.000–0.002 s | 45865 / 36675 / 38301 | 3/3 | 3/3 | 3× 0/true | 3× pid gone, port refuses | none (sibling pid 346295 present before and after, excluded) |
| trial3 | 3 @ +0.000–0.001 s | 43247 / 40457 / 36499 | 3/3 | 3/3 | 3× 0/true | 3× pid gone, port refuses | none (siblings 346295, 430663 unchanged) |
| stress9b (not the hypothesis; same design, 9 at once) | 9 @ +0.000–0.004 s | 44209/42895/37887/45049/46011/33397/44009/36723/42565 | 9/9 | 9/9 | 9× 0/true | 9× pid gone, port refuses | none |

The witness block is not merely self-reported: in every run its `port`/`pid` equalled the outside observation of the same live process, so each replay really announced its own server.

Mechanics that make the result meaningful (frozen source, unchanged):
- `tools/kama-llamacpp-live.py:1860-1867` calls `hold_for_witness()` only after the readiness loop and all checks, then re-verifies listener ownership post-witness; `tools/kama-llamacpp-live.py:280-300` writes `ready.json` atomically (`os.replace`, 289-292) and waits on `release` bounded by the timeout (295-296), returning `released` (298-300).
- `tools/kama-live-replay.py:275-281` forwards `--witness-dir`/`--witness-timeout` to the extracted live tool; the replay still compares only the stable projection, so the witness cannot mask a mismatch.
- Ports are picked by `pick_port()` (`tools/kama-llamacpp-live.py:481-501`), whose own docstring records the release/rebind race. 18 simultaneous picks (3+3+3 hypothesis runs and 9-way stress) produced no collision — measured absence at this scale, not a proof of mutual exclusion.

## Incidental findings and risks

1. **Harness false positive (mine, fixed):** the first 9-way stress (`receipts/stress9-evidence.json`) reported `FAIL … unexpected llama-server {420609: 'exe-digest'}`. That process was not started by the trial: all nine trial pids were accounted for, each had its own port that refused afterwards, and the pid was gone within seconds; other seats on this host run their own witnessed replays (baseline pids 346295/402516/402519 at different moments). Cause: my first leftover scan attributed any new llama-server pid to the trial. Fix: attribute by resolved `/proc/<pid>/exe` path under the trial scratch plus the recorded trial pids, and report foreign pids as informational (implemented before `stress9b`). No per-run clause failed in `stress9`. The lane contract is not at fault here.
2. **Residual risk, already documented in the tool:** concurrent replays can in principle pick the same free port (`pick_port` releases the probe socket before the server binds, `tools/kama-llamacpp-live.py:481-484`); a collision would fail one replay's bind, not silently mis-witness. Not observed in 18 simultaneous picks. The frozen C1 counter itself witnesses sequentially, so it cannot regress on this; the risk only matters for parallel fleet trials.
3. **Measurement note:** each replay downloads `llama-b11909-bin-ubuntu-x64.tar.gz` = 22,475,032 B (not the ~75 MB in my task text) plus `stories260K.gguf` = 1,185,376 B; three concurrent full replays completed readiness in ~2.7–3.6 s and teardown in ~0.2–0.95 s of witness hold.
4. No lane file was edited; the frozen counter/preregistration/controls were used read-only only for context — the exercise is my own observer, per the seat spec.

## Files written (absolute)

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/X1Concurrent.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/X1Concurrent/x1concurrent-observe3.py` (sha256 `0790129be053b1860138832dc9644d66fd5775de465d8ff8421947c12d9f99d1`)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/X1Concurrent/receipts/{trial1,trial2,trial3,stress9b,stress9}-evidence.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/X1Concurrent/receipts/trial1-ready-and-witness.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/X1Concurrent/receipts/trial1-w{1,2,3}-ready.json`, `trial1-w{1,2,3}-replay.log`
