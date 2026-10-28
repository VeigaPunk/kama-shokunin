# EX07Concurrency — concurrent C1 counters + live plain run (tip 03a6a1d850902a66a13dfad33f89cf3a8b759a09)

Method: `git clone --shared` of the lane into scratch, detached at the tip (HEAD verified = 03a6a1d8...); every tool run from the clone's tools/ with `--repo $D --tip 03a6a1d8...`.
No tool installs. No lane edits. No commits. Scratch /fast/scratch/hyaku/kama-r63/w/EX07Concurrency (removed before yield; receipts in out/EX07Concurrency/).

## Run 1 (the literal item): 3x round63-c1-counter.py (work dirs w1,w2,w3) + 1x kama-completion-live.py (plain: --work --out only, no --hold-dir), launched in the same shell instant
```
c1 #1: exit=0 tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]
c1 #2: exit=0 (identical line, met=True)
c1 #3: exit=0 (identical line, met=True)
live : exit=0, stdout EMPTY, stderr empty; receipt (--out) schema=kama-completion-live/v2 verdict=REQUEST_OK port=35155 hold.released=False (no hold dir, as plain) teardown{sigterm_sent=true, returncode=0, port_closed=true, child_pre_dead=false}
```
Counter live receipts (w1/w2/w3 work/receipt.json): REQUEST_OK, ports 38423 / 42079 / 37647 (+ live 35155) — four distinct ports, hold.released=true on all three.

## Run 2 (repeat for flakiness): 6 rounds of the same 4-way concurrent launch (python driver, per-process wall, 50 ms pgrep sampler on llama-server)
- 6/6 rounds: all 3 counters exit 0, met=True, 44/44, eval_selftest=3/3, errors=0, stderr empty; the live run exit 0 REQUEST_OK, stderr empty. 18/18 counter runs + 6/6 live runs green; 0 flakes.
- Wall per process 1.39-1.49 s; whole 4-way batch 1.71-1.89 s.
- Ports (from the receipts, 24 child servers incl. run 1 excluded): per round the 4 ports are distinct; all 24 distinct across rounds; none is a registered consumer port (8080, 34113 per registry/endpoint-consumers.tsv) or 1234/45669. No port collision, no EADDRINUSE/ready-timeout in any stderr.
- Verbatim per-round table in out/EX07Concurrency/rounds.json (rounds.log is the raw driver stream).

## Foreign processes (pgrep -af llama-server)
- Before run 1 / after run 2: operator servers pid 1706355 (`--port 1234 --models-dir /home/vgpnk/models/lfm3`) and pid 242776 (`--port 45669 --alias LFM3-1.7B`) present with unchanged cmdlines, never touched. In all 6 per-round before/after comparisons `foreign_unchanged=True` (same pids, same cmdlines).
- Other residents NOT mine and not touched: 3262613 (ollama llama-server, r61-closure leftover, port 37323) alive throughout; 2853755 (`stories260K ... --port 34451`, launched by the EX05CompletionEdges seat, an unregistered port) alive throughout and in the sampler each round — it is a sibling seat's server, not interference from this run (our ports never equalled 34451).
- All servers I spawned were gone after each round (final pgrep shows only the 4 above).

## Findings
1. No port collisions, no flakiness, no interference with operator servers under 4-way concurrency (24/24 + 6 live green).
2. Operability note (not a defect of the claims): `kama-completion-live.py` plain run prints nothing on stdout/stderr; verdict is only in the exit code and the `--out` JSON (without --out there is no one-liner). The "one-liner" for it must be derived from the receipt: `kama-completion-live/v2 REQUEST_OK port=35155 exit=0`. Whether a stdout summary is expected is the L1's call.
3. Sampler caveat: at 50 ms pgrep granularity not every short-lived child is sampled (3-4 of 4 seen per round); port-distinctness evidence rests on the receipts' `port` fields, which all four runs per round wrote.
4. Wall of run 1 per process was lost (no `bc` on host; driver in run 2 timed with Python). Does not affect any result.

One-liner (counter, each of 3 concurrent copies): `tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True`
