# EX01C1Repeat — round-63 C1 counter repeatability (advisory; no verdict)

Tip under test: 03a6a1d850902a66a13dfad33f89cf3a8b759a09. Counter run from a `git clone --shared` of the lane checked out (detached, inside scratch) at that tip:
`python3 $D/tools/round63-c1-counter.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip 03a6a1d8… --work $S/runN`
(counter sha256 in out/EX01C1Repeat/tip-checkout.txt). No tools installed. Nothing in the lane was edited or committed.

## Result: the line is stable in all 7 runs; no run differs (byte-identical stdout, empty stderr, exit 0)

Every run printed this one line (pasted verbatim once; `sort -u` over out1..out7.txt gives 1 distinct line of 7):

```
tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]
```

| run | condition | exit | wall | host loadavg at start |
|---|---|---|---|---|
| 1 | plain, sequential | 0 | 1.4 s | 35.66 37.63 22.14 |
| 2 | plain | 0 | 1.5 s | 35.66 37.63 22.14 |
| 3 | plain | 0 | 1.5 s | 35.66 37.63 22.14 |
| 4 | `HTTP_PROXY=http://127.0.0.1:9 http_proxy=http://127.0.0.1:9` | 0 | 1.4 s | 35.05 37.47 22.17 |
| 5 | 4 busy loops started immediately before (item as specified) | 0 | 1.5 s | 35.05 37.47 22.17 |
| 6 | supplement: 4 busy loops, 6 s warm-up, each at 99.6% CPU confirmed by ps | 0 | 1.4 s | 38.45 38.44 24.48 |
| 7 | supplement: 32 busy loops (= nproc), 6 s warm-up, ~60-90% CPU each by ps | 0 | 2.1 s | 41.70 39.11 24.78 |

Busy loops were `( while :; do :; done ) &`; all were killed after their run and `pgrep -f 'while :'` returned 0 afterwards. Scratch drivers: drive.sh (runs 1-5), drive2.sh (6-7); logs log.txt, log2.txt.

## Notes for the reader
- The host was already at loadavg ~35-40 on 32 cores before any seat load (concurrent peers), so runs 1-4 were not on an idle host. Run 5's loops lasted only ~1.5 s and did not visibly move loadavg, which is why runs 6-7 were added with a verified warm-up; they are the real load evidence.
- Each run is a genuine live lifecycle, not a replay: a distinct ephemeral loopback port every run (36221, 41695, 36089, 44453, 36731 for runs 1-5; receipts in out/EX01C1Repeat/receipt1..7.json), schema `kama-completion-live/v2`, verdict `REQUEST_OK`, server `/home/vgpnk/.local/opt/llama-b11755/llama-server` on the stories260K.gguf model (-c 512 -t 1), so the ~1.4 s wall time is the tiny model plus hold-mode lifecycle plus 44+3 re-scores, not a skipped step. The server log shows the real request/eval trace.
- The proxy run shows the counter/tool path is unaffected by proxy env vars (consistent with the v2 "proxy-free opener"); I did not packet-capture to prove nothing touched 127.0.0.1:9, only that the output and exit are identical.
- Scope of the stability claim: 7 runs, one host state at a time; timing-family checks (timing=4/4) passed even under 32-way CPU contention, but only a tiny model was served — slower models were not exercised.
- Runs executed against the lane's tip content read by the counter from git blobs of --repo (per the counter's design); the clone only supplied the counter script itself.

Counter one-liner for this item: `runs=7 exit_codes=0x7 distinct_lines=1 met=True x7 wall=1.4-2.1s`
