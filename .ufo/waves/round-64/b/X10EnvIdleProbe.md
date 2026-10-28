# X10EnvIdleProbe - C2 idle outcome (kama-context-capacity.py K1), round 64 wave b

Clone: /fast/scratch/hyaku/kama-r64/b/X10EnvIdleProbe/clone @ f6a4ea9a (no edits; lane files untouched).
Tool read: tools/kama-context-capacity.py (sha unmodified). Idle logic: `live_llama_server_pids()` (l.218) runs
`pgrep -x llama-server`, drops zombies via /proc/<pid>/stat; `wait_for_host_idle(timeout)` (l.241) polls every 2 s,
accumulates every pid ever seen in `seen`, returns ok=False if any pid is still present at the deadline.
`main()` (l.790) stores it as `receipt['host_idle'] = {ok, waited_s, other_pids_seen, cell}` (overwritten per cell).
No tools installed. Receipts: .ufo/waves/round-64/b/out/X10EnvIdleProbe/receipts/.

## Three real runs (`--only K1 --host-idle-timeout 20`, driver wraps pgrep before/after)
Host has three standing foreign llama-servers (242776 LFM3 port 45669, 1706355 port 1234 router, 3262613 stale ollama-bundled one), so the host is never idle.

| run | exit | stdout | host_idle | pgrep -x before / after |
|---|---|---|---|---|
| 1 | 2 | `{"all_ports_closed": true, "cells": 0, "observed": 0, "ports_used": []}` (stderr `host-not-idle-before-K1`) | ok=False, waited_s=21.711, seen=[242776,1706355,3262613,2022437] | {242776,1706355,1978394,3262613} / {242776,1706355,3262613} |
| 2 | 2 | same | ok=False, waited_s=21.765, seen=[242776,1706355,3262613] | {242776,1706355,3262613} / {242776,1706355,3262613} |
| 3 | 2 | same | ok=False, waited_s=21.94, seen=[242776,1706355,3262613,2279244,2340223,2356219,2380250,2415595,2415613,2416010,2450917] | {242776,1706355,3262613} / {242776,1706355,2456216,2456221,2456784,3262613} |

(`pgrep -f llama-server` is also recorded in run*.txt; it additionally matches non-server processes whose argv mentions llama-server - python3 peers 1978070, 2455387, 2455392, 2455893 - so it is not the tool's view. -f before/after sets give the same answers below.)

## Answers
1. Subset? NO. `other_pids_seen` is the union over the whole ~21 s polling window, so transient peer servers (run1: 2022437; run3: eight pids 2279244..2450917) appear in `seen` yet in neither the before nor the after pgrep. Counter-examples to "subset of before-union-after": runs 1 and 3. Run 2 happened to be a subset (quiet host). The reverse direction holds in all three runs: pids present in BOTH pgreps (the three standing servers; also true of the -f sets) are always in `seen` - but that is near-trivial (a pid alive across the window is polled ~10 times) and it cannot exclude a pid that was present in both snapshots yet absent in between. `seen` is a witness of persistence over the wait window, not a snapshot-bounded set; asserting `other_pids_seen == pgrep set` or `subset of pgrep` would be false.
2. Idle host (fixture): exit 0, stdout `{"all_ports_closed": true, "cells": 1, "observed": 1, "ports_used": [47400]}`, `host_idle` = `{"cell":"K1","ok":true,"other_pids_seen":[],"waited_s":0.005}`, stderr empty; yes `"all_ports_closed": true` appears. Reproduced twice (waited_s 0.005 / 0.004).

## Calibration findings
- `"all_ports_closed": true` is printed in BOTH outcomes: idle success (cells=1, exit 0) and non-idle failure (cells=0, exit 2). It is vacuously true on an empty cell list (`all([])`, l.833, also computed in `finally`). stdout alone cannot distinguish "ran and closed" from "never ran"; only `cells`/`observed`, exit code and stderr do. A registry claim must not accept the all_ports_closed key without cells>=1 and exit 0.
- `host_idle` is overwritten per cell, so in a multi-cell run only the last cell's block survives in the receipt; with `--only K1` it is the sole block. On failure the block exists only if the loop was entered.
- waited_s overshoots the timeout (21.7-21.9 s for 20 s) due to the 2 s sleep granularity.
- The idle test is host-global (`pgrep -x llama-server`, no port/ownership filter): any standing foreign server blocks every run, indefinitely, with exit 2 - this host currently can never produce the idle outcome without a fixture.

## Fixture
out/X10EnvIdleProbe/idle-fixture.sh `<repo-or-clone> <scratch>` - copies the tool byte-identically (cmp-checked) into a fixture tree (symlinks to read-only repo deps: kama-llamacpp-live.py, registry/endpoint-consumers.tsv, round-25 count-c2.py), puts a fake `pgrep` (prints nothing, exit 1; logs its calls) first on PATH inside the fixture bin dir only, then runs the unmodified tool code path with `--only K1 --host-idle-timeout 20`. Nothing foreign is touched; the one server is the tool's own K1 child on 47400, torn down by the tool (post-run `ss` shows no 474xx listeners). Produces the exit-0 idle outcome above (runs: receipts/fixture-run1.out, fixture-run2.out, fixture-idle-cc.json; fake pgrep called once: pgrep-calls.log).

Counter line: n/a (no counter output requested); fixture result = `exit=0 {"all_ports_closed": true, "cells": 1, "observed": 1, "ports_used": [47400]}`.
