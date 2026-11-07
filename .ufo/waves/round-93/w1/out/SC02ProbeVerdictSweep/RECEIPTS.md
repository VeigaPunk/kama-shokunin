# SC02ProbeVerdictSweep — evidence receipts

All commands run from the lane root `/home/vgpnk/Projects/shokunin/kama-shokunin` with
scratch `/fast/scratch/hyaku/kama-r93/SC02ProbeVerdictSweep/` (removed at yield).
Probe bytes: M1 `fe5f031cb1b9d33e1160360d892149b8ac3c7771`
sha256 `159c80688c5d903ea776e3e548a980f64e6ddedf43b8d7a35ab4724acab48dbb`;
BASE `5af794958b0fc08f574aa2e67650282269549b02`
sha256 `36631d498901c40f76e1c36471166fecb71a2e84124c4795c301e9e8e5cbf962`.

## 1. counter at M1, natural load (4 reproductions)
`python3 tools/round93-router-repeat.py --repo . --rev fe5f031... --work <scratch>`
=> `ROUTER_REPEAT cells=10 mismatches=0 positive_mismatches=0 probe=rev ... load1=46.22` exit=0
(load1 34.43 / 46.22 / 64.75 / 68.50 across runs; all exit=0)

## 2. counter at M1, synthetic load 200 burners
`python3 counter_under_load.py <scratch> fe5f031... 200`
=> R02 ok=0 (run3 MODEL_OK/router-unloaded-autoload/5.48s)
   R03 ok=0 (run1 MODEL_OK/router-unloaded-autoload/5.11s)
   R05 ok=0 (run1 MODEL_OK/router-unloaded-autoload/5.51s)
   R06 ok=0 (run2 MODEL_OK/router-unloaded-autoload/5.55s)
   P04 ok=0 (run1 MODEL_OK/router-unloaded-autoload/5.87s)
   `ROUTER_REPEAT cells=10 mismatches=5 positive_mismatches=1 probe=rev ... load1=256.31`
   counter exit=1 wall=129.5s

## 3. counter at BASE, same synthetic load
`python3 counter_under_load.py <scratch> 5af794... 200`
=> `ROUTER_REPEAT could-not-evaluate: fixture slow.gguf: base loader state '-', designed 'invalid'`
   counter exit=2

## 4. fixed-load repeated trials (200 burners)
`python3 harness12.py <scratch> 200 10`
=> FLIP cell=P04 rev=BASE flips=3/10 want=MODEL_UNLOADED/router-model-missing load1=178.27
   FLIP cell=P04 rev=M1  flips=5/10 want=MODEL_UNLOADED/router-model-missing load1=244.18
   FLIP cell=R03 rev=BASE flips=10/10 want=MODEL_UNLOADED/router-model-invalid load1=288.12

## 5. memo effect (ONE file named by N candidates)
`python3 harness11.py <scratch> memo`
=> MEMO n=1    BASE wall=0.65s {'invalid': 1}     | M1 wall=0.71s {'invalid': 1}
   MEMO n=8    BASE wall=4.04s {'invalid': 6, '-': 2} | M1 wall=0.66s {'invalid': 8}
   MEMO n=64   BASE wall=4.19s {'invalid': 7, '-': 57} | M1 wall=0.60s {'invalid': 64}
   MEMO n=1024 BASE wall=6.53s {'invalid': 7, '-': 1017} | M1 wall=0.71s {'invalid': 1024}

## 6. DISTINCT slow files (fresh files per rev)
`python3 harness6.py <scratch> distinct`
=> distinct-k4 BASE rc=2 MODEL_UNLOADED/router-model-invalid 2.32s
   distinct-k4 M1  rc=2 MODEL_UNLOADED/router-model-invalid 2.39s
   distinct-k8 BASE rc=0 MODEL_OK/router-unloaded-autoload 4.32s
   distinct-k8 M1  rc=0 MODEL_OK/router-unloaded-autoload 4.35s

## 7. ONE file, ONE entry, cache warm, load varied
`python3 harness11.py <scratch> onefile 0,64,128`
=> burners=0   BASE rc=2 MODEL_UNLOADED/router-model-invalid 0.77s load1=69.78
   burners=0   M1  rc=2 MODEL_UNLOADED/router-model-invalid 0.80s load1=68.51
   burners=128 BASE rc=2 MODEL_UNLOADED/router-model-invalid 4.08s load1=78.16
   burners=128 M1  rc=2 MODEL_UNLOADED/router-model-invalid 4.74s load1=87.04
   burners=256 BASE rc=2 MODEL_UNLOADED/router-model-invalid 3.87s load1=105.45
   burners=256 M1  rc=0 MODEL_OK/router-unloaded-autoload    5.15s load1=123.11

## 8. /props latency vs --timeout 5
`python3 harness4.py <scratch> props-threshold`
=> props-ok-d4.9 BASE rc=0 MODEL_OK/router-unloaded-autoload 5.08s
   props-ok-d5.0 BASE rc=2 MODEL_UNLOADED/router-unloaded 5.12s
   props-ok-d5.0 M1  rc=2 MODEL_UNLOADED/router-unloaded 5.12s

## 9. timeout-8 kill / stdout buffering
`python3 timeout_buffer_demo.py`
=> SIGTERM case: rc=-15 lines_seen=5124 bytes=65502
   timeout wrapper: rc=124 lines_seen=200000 bytes=2888890
`python3 timeout_kill_demo.py <scratch>`
=> TK k=8   timeout=3 rc=124 wall=3.00s lines=6/8   nbad=6   ncand=8   -> MODEL_OK
   TK k=256 timeout=3 rc=124 wall=3.00s lines=7/256 nbad=7   ncand=256 -> MODEL_OK
   TK k=256 timeout=8 rc=0   wall=4.54s lines=256/256 states={'-':256} -> MODEL_OK

## 10. MAX_STEPS boundary (host-load independent)
`python3 steps_boundary.py <scratch>`
=> tensors=600000 wall=2.15s '0\tinvalid'
   tensors=650000 wall=2.29s '0\tinvalid'
   tensors=675000 wall=2.31s '0\t-'
   tensors=700000 wall=2.36s '0\t-'

## 11. argv candidate
`python3 argv_test.py`
=> getconf ARG_MAX = 2097152 ; n=131072 rc=0 lines=131071
