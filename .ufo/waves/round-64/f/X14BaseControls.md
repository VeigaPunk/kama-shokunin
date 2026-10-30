# X14BaseControls — red-before receipts

Axis: operability + calibration. No packages installed or updated.

Scratch clone: `/fast/scratch/hyaku/kama-r64/f/X14BaseControls/clone`, checked out measured tip `23b3fdb1a925129a9961cf551f6d40bf251602cb`; commands used the required isolated `--work` directories. Receipts/output are retained in this report; the clone/work directories remain in the assigned scratch root.

## Runs

(a) C1 counter, base tip `0c1eff3cb9ac4c11402ab0124c35842f06a436fc`:

`tool_present=1 live_ok=0/1 controls_targeted=0/0 of 91 families_exact=0 missing_families=['bind', 'canned', 'detach', 'digest', 'forge', 'hdr', 'hold', 'idcr', 'listener', 'log', 'outside', 'pathcopy', 'predead', 'preload', 'proxy', 'ptok', 'receiptbind', 'relabel', 'replay', 'reqbind', 'runfield', 'schema', 'shape', 'sigterm', 'stale', 'stalehold', 'tamper', 'timing', 'trunc', 'witness'] eval_selftest=0/8 errors=1 met=False families[]`

Exit: 1.

(b) C2 counter, base tip:

`tip=0c1eff3cb9ac population=0 covered=0/12 mismatches=0 pinned=12/13 deps_pinned=2/2 regress_flipped=0/12 printers_rejected=0/12 idle_ok=0 work_reuse_refused=1 closure_ptr=0 recon_mismatches=0 tally_disclosed=1/8 tally_selftest=4/4 controls_rejected=0/120 errors=2 recon[mismatches=0,maxN=63,met=True] tally[56:no-disclosure,57:no-disclosure,58:no-disclosure,59:no-disclosure,60:no-disclosure,61:no-disclosure,62:no-disclosure,63:ok] families[] met=False`

Exit: 1. The counter also emitted detail lines for missing canonical round-64 list, registry and regression table; baseline was not met and control credit withheld.

(c) Round-63 forged-tool replays: forge-A applied cleanly to the base-tip v2 tool and the round-63 counter output was:

`tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]`

Exit: 0; accepted, as expected from the frozen MT15 evidence.

Forge-B did **not** apply: `patch` reported both hunks failed at lines 204 and 390. I restored the base-tip v2 tool and verified the patch dry-run, which again failed both hunks. The v2 tool SHA-1 was `243f94727193a40645621f7f631405b9f322ee32`; the patch's recorded index starts `97f54794`. I did not score an unpatched tool as a forge-B replay. This discrepancy is an explicit blocker for that requested comparison.

(d) C1 counter, measured tip `23b3fdb1a925129a9961cf551f6d40bf251602cb`:

`tool_present=1 live_ok=1/1 controls_targeted=91/91 of 91 families_exact=1 missing_families=[] eval_selftest=8/8 errors=0 met=True families[bind=30/30 canned=1/1 detach=1/1 digest=1/1 forge=3/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 receiptbind=4/4 relabel=1/1 replay=1/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]`

Exit: 0.

## Evidence limits

Measured-tip C1 output reports the aggregate and declared families, not a per-control report for the two specific wave-b forgeries. Consequently this run establishes that the overall 91-control suite passed, but does not independently expose their individual rejection outcomes. The forge-B application failure prevents its C1/C63 comparison. No C2 measured-tip run was requested or performed.

C1 base was the expected `live_ok=0/1 met=False`; C2 base and C1 measured-tip results match their stated expected outcomes. The C63 forge-A control accepted the forgery (`met=True`, `44/44`).
