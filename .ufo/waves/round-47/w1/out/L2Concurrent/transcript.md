# L2Concurrent — command transcript (exits and key output lines, verbatim)

Scratch: `/fast/scratch/hyaku/kama-r47/L2Concurrent` (removed after these artifacts were copied).
Lane: `/home/vgpnk/Projects/shokunin/kama-shokunin` (read-only). Host kernel `7.2.11-arch1-1`, Python `3.14.8`.

## Identity of the code under test

```
$ git -C <lane> log -1 --format='%H %ci %s'
46a924e027f05614558c45ff02bf7a94ca57d3e1 2026-10-26 18:23:37 -0300 round-47: wave spec kama-r47-w1 (65 seats, policy v2) and dispatch
$ git -C <lane> cat-file -t 3a09a1d93dcc16799cf6c4b48786e6440af134c4
commit
$ sha256sum <lane>/tools/kama-live-replay.py ; git -C <lane> cat-file blob 3a09a1d9…:tools/kama-live-replay.py | sha256sum
39cd387a3a95b47865d81484ffe30664e653d5016c4c75d47abf6e855e43fdd0   (both)
$ sha256sum <lane>/tools/kama-llamacpp-live.py ; git -C <lane> cat-file blob 3a09a1d9…:tools/kama-llamacpp-live.py | sha256sum
65301a3c76f925bf3316673d3774269f6d93ca22f4ccdb7c7139e6826b8ae65d   (both)
$ git -C <lane> status --porcelain -- tools/
(no output)
$ sha256sum <lane>/.ufo/waves/round-47/c2/live/receipt-1.json
a4caf311ac030ce3c50373d7f2c37aa62895bcec5deb93bfa8bbd24e0706e80d
```

## Pair 1 — two replays, one start instant, separate --work (lane tools)

```
$ bash drive.sh
driver_start 2026-10-26T21:25:41.596806082Z
A start=1793049941.693059352 end=1793049944.196681010 exit=0
B start=1793049941.693170432 end=1793049944.475595368 exit=0
a.json {'match': True, 'refused': None, 'mismatches': [], 'live_exit': 0}
b.json {'match': True, 'refused': None, 'mismatches': [], 'live_exit': 0}
A rerun-receipt.json: port 35567 outcome pass checks 11 failed []
B rerun-receipt.json: port 44199 outcome pass checks 11 failed []
$ ss -ltnp | grep -i llama        # post
(none)
$ pgrep -af llama-server          # post: a peer seat's run only, not mine
2640773 python3 tools/kama-llamacpp-live.py --server /home/vgpnk/.local/opt/llama-b11755/… --out /fast/scratch/hyaku/kama-r47/K2Fresh/naive-a.json
$ sha256sum wA/download/* wB/download/*      # digests verified before use
bf94332a…197e695b  (archive, both work dirs)
270cba1b…d3bd256d  (model, both work dirs)
$ for p in 2628543 2629822; do [ -e /proc/$p ] && echo ALIVE || echo gone; done
gone / gone
```
Serve windows from the rerun receipts: A `2026-10-26T21:25:44.015Z → .178Z`, B `21:25:44.288Z → .455Z`.
Sampler (`ss-during.txt`) saw `listeners=1` once at `21:25:44.073Z`, 0 in every other 0.5 s sample.

## Pair 2 — same trial, tools from a --shared clone at 3a09a1d9, receipt copy byte-identical

```
$ git clone --shared -q <lane> $S/lane && git -C $S/lane checkout -q 3a09a1d93dcc16799cf6c4b48786e6440af134c4
$ git -C $S/lane rev-parse --show-toplevel ; git -C $S/lane rev-parse HEAD
/fast/scratch/hyaku/kama-r47/L2Concurrent/lane
3a09a1d93dcc16799cf6c4b48786e6440af134c4
$ bash drive2.sh
pair2_start 2026-10-26T21:32:15.047974034Z
C start=1793050335.146198342 end=1793050337.587170799 exit=0
D start=1793050335.146191372 end=1793050337.895464954 exit=0
c.json {'match': True, 'refused': None, 'mismatches': [], 'live_exit': 0}
d.json {'match': True, 'refused': None, 'mismatches': [], 'live_exit': 0}
wC: port 34025 outcome pass checks 11 evaluated 11 ownership child child 869333 started 21:32:17.382Z ended 21:32:17.560Z log_path None port_refuses True
wD: port 37747 outcome pass checks 11 evaluated 11 ownership child child 870450 started 21:32:17.686Z ended 21:32:17.864Z log_path None port_refuses True
listeners_post=0
$ pgrep -af llama-server ; pgrep -af $S        # post
(no output) / (no output)
```

## Amplification (lane live tool, argv as kama-live-replay.py:161-166 builds it)

```
$ N=6 ROUNDS=8 bash amp.sh
48 runs; exits: 48 exit=0 ; ports: 48 occurrences, 48 distinct ; leftover listeners 0 ; leftover procs: none
start spread per round (ms): 6,3,2,5,3,4,8,8
receipts 48 / outcomes {'pass': 48} / all 11 evaluated: True / ownership set: {'child'} / setup_error set: {None}
first_transition_ms min/max: 6 10

$ N=2 MAXR=600 OUT=$S/stress2 bash stress.sh
runs=1200 rounds_done=600
rounds_with_dup_or_bad=0
listeners_after=0 ; procs_after: none

$ N=12 MAXR=200 bash stress.sh          # campaign A
STOP at round 6: round=6 n=12 ports=12 dup_within_round=[44879] bad=['1:setup-error'] setup_error=['1:port-listener-not-our-child']
runs=72 rounds_done=6 ; listeners_after=0 ; procs_after: none

$ N=12 MAXR=45 OUT=$S/stress12b bash stress.sh   # campaign B
runs=540 rounds_done=45 ; rounds_with_dup_or_bad=0 ; listeners_after=0 ; procs_after: none
```
(`total ports chosen` printed empty in both stress reports: `bc` is not installed on this host; totals were
recomputed from the retained `rounds*.txt`.)

## The collision — receipts

```
$ python3 -c '…'   # dump r6-1 / r6-2
r6-1.json port 44879 outcome setup-error setup port-listener-not-our-child own foreign checks 4 ev 3
          child 3760690 alive_at_teardown False rc 1 port_refuses False
          teardown_graceful False/True-evaluated observed {alive_at_teardown_start: false, returncode: 1, port_listener_ownership: "foreign", sigterm_sent: false, sigkill_sent: false}
          teardown_port_closed False/True-evaluated observed {port_refuses: false, port_listener_ownership: "foreign"}
          loading_envelope_graded None/not-evaluated ("no-loading-503-observed")
          model_unchanged True/True-evaluated
          transitions: models t_ms=16 status None error ConnectionRefusedError repeats 225; models t_ms=17 status 503 server llama.cpp
r6-2.json port 44879 outcome pass checks 11/11 own child log "server_on_li: listening on http://127.0.0.1:44879"
$ for p in 3760690 3760726; do … /proc/$p …; done
gone / gone
$ python3 -c 'import kama-live-replay as klr; klr.compare(receipt-1, r6-1)'
mismatches 11: outcome:pass->setup-error, 8× check:<id>:not-evaluated,
              check:teardown_graceful:True->False, check:teardown_port_closed:True->False
=> replay would report match=False exit=1                      (collision12/collision-compare.json)
```

## Forced port-in-use (foreign listener, explicit --port) — same reporting path

```
foreign listener port 38153
live exit 2  outcome setup-error setup_error port-in-use:38153 checks 0 evaluated 0 port None
replay compare() mismatches 13 ['outcome:pass->setup-error', 'server.sha256:…->None', 'check:health_ready:not-evaluated', 'check:loading_envelope_graded:not-evaluated', …]
=> replay would report match= False exit= 1                    (forced/forced-summary.json)
```

## Mechanism probes

```
$ python3 bindseq.py 200000
{"trials": 200000, "released_port_reassigned": 22, "rate": 0.00011, "distinct_first_ports": 6992}
$ python3 bindrace.py 1500
{"trials_pairs": 750, "binds": 1500, "duplicate_pairs": 0, "out_of_ephemeral_range": 0, …}
```

## Proposed patches — validation on scratch copies (never in the lane)

```
$ diff -u lane/tools/kama-live-replay.py        patches/kama-live-replay.py        > proposed-replay-retry.diff           (64 lines)
$ diff -u lane/tools/kama-llamacpp-live.py      patches/kama-llamacpp-live.py      > proposed-live-teardown-ownership.diff (49 lines)
$ python3 -m py_compile patches/kama-live-replay.py patches/kama-llamacpp-live.py
COMPILE_OK
$ python3 patches/kama-live-replay.py --selftest --scratch $S/st
pass match / pass check-differs / … / pass http-refused
KLR_SELFTEST pass=10 fail=0        exit=0
$ python3 patches/kama-live-replay.py --receipt <file:// fixture> --live <fake: 1 collision then clean>
patched replay exit 0 replay match=True refused=None mismatches=0 exit=0
attempts [{'attempt': 1, 'setup_error': 'port-listener-not-our-child'}, {'attempt': 2, 'setup_error': None}]
$ … --live <fake: always port-listener-ownership-unproven>
always-collision exit 2 match False refused rerun-setup-error:port-listener-ownership-unproven attempts 3
$ … --live <fake: model-digest-mismatch>
non-transient exit 2 match False refused rerun-setup-error:model-digest-mismatch attempts 1
$ cp patches/kama-llamacpp-live.py $S/lane/tools/ && python3 $S/lane/tools/kama-llamacpp-live.py --server … --model … --out patchval-live2.json
live_exit=0  outcome pass setup None checks 11 evaluated 11 failed [] own child
             teardown [('teardown_graceful', True, True), ('teardown_port_closed', True, True)]
$ git -C $S/lane checkout -q -- tools/kama-llamacpp-live.py ; git -C $S/lane status --porcelain -- tools/ | wc -l
0    (clone restored; blob sha256 back to 65301a3c…ae65d)
```
Rejected first attempt at that last check (recorded, not hidden): running the patched live tool from outside
the tree gives `setup_error probe-not-found:<scratch>/tools/kama-probe.sh` because the tool derives `LANE`
from its own path.

## Concurrent peer edit (not mine), observed after the runs

```
$ git -C <lane> status --porcelain -- tools/             # at 21:31Z, before the runs
(no output)
$ ls -l --time-style=full-iso <lane>/tools/kama-live-replay.py
-rwxr-xr-x 1 vgpnk vgpnk 13930 2026-10-26 18:34:09.889032714 -0300 …/tools/kama-live-replay.py   (= 21:34:09Z)
$ sha256sum <lane>/tools/kama-live-replay.py
80149f0105e5629a3dee800817858742d0adbb8f97e201fc2d272452e81372bf     (frozen blob was 39cd387a…3fdd0)
```
Diff vs the frozen blob: `notes` array, `live-exit:<n>` appended to mismatches, `original:no-evaluated-check`,
`fetch()` `.part` cleanup, 2 new selftest cases. A peer seat's edit; my runs (21:25Z, 21:32Z) used the frozen blob,
and all line anchors / the proposed diff in the report are at `3a09a1d9`.
