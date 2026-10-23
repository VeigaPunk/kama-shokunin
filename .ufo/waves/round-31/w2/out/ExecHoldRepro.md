```RESULTS
$ mkdir -p /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ExecHoldRepro /tmp/kama-r31w2/ExecHoldRepro
exit code: 0
verbatim tail: (empty)

$ git -C /home/vgpnk/Projects/shokunin/kama-shokunin log --format='%H %s' -20 -- .ufo/waves/round-30/count-c1.py > /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ExecHoldRepro/counter-history.log; rc=$?; cat /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ExecHoldRepro/counter-history.log; printf 'EXIT=%s\n' "$rc"
exit code: 0
verbatim tail:
fdf8cda19c0719f57e0c2af27e838b42304b0f56 round-30: C1 freeze (calibration): recall-population counter, preregistration, base receipt, census start; before any seat
EXIT=0

$ git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse HEAD > /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ExecHoldRepro/tip.log; r1=$?; sha256sum /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-30/count-c1.py > /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ExecHoldRepro/current-sha256.log; r2=$?; cat /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ExecHoldRepro/tip.log; cat /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ExecHoldRepro/current-sha256.log; printf 'EXIT=%s\n' "$((r1 || r2))"
exit code: 0 (both component commands exited 0)
verbatim tail:
bda324bbc5c1d7db93553adb13c5f380492c3c93
c3f16ef195a6b5de24afa5a798647d917070d988954baf1fe5923fc5e19ce40d  /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-30/count-c1.py
EXIT=0

$ set -o pipefail; git -C /home/vgpnk/Projects/shokunin/kama-shokunin show 382d11b2107d335705875da1a4d889b074bd6fa6:.ufo/waves/round-30/count-c1.py | sha256sum > /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ExecHoldRepro/tip-counter-sha256.log; rc=$?; cat /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ExecHoldRepro/tip-counter-sha256.log; printf 'EXIT=%s\n' "$rc"
exit code: 0
verbatim tail:
c3f16ef195a6b5de24afa5a798647d917070d988954baf1fe5923fc5e19ce40d  -
EXIT=0

$ git -C /home/vgpnk/Projects/shokunin/kama-shokunin diff --quiet 026eede9f46abd4eeea204eb4262bbbb31a4facb 382d11b2107d335705875da1a4d889b074bd6fa6 -- .ufo/waves/round-30/count-c1.py; rc=$?; printf 'EXIT=%s\n' "$rc"
exit code: 0 (git diff exited 0; its stdout was empty)
verbatim tail:
EXIT=0

$ set -o pipefail; git -C /home/vgpnk/Projects/shokunin/kama-shokunin show 026eede9f46abd4eeea204eb4262bbbb31a4facb:.ufo/waves/round-30/count-c1.py | sha256sum > /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ExecHoldRepro/landing-counter-sha256.log; rc=$?; cat /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ExecHoldRepro/landing-counter-sha256.log; printf 'EXIT=%s\n' "$rc"
exit code: 0
verbatim tail:
c3f16ef195a6b5de24afa5a798647d917070d988954baf1fe5923fc5e19ce40d  -
EXIT=0

$ /usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-30/count-c1.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip 382d11b2107d335705875da1a4d889b074bd6fa6 --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ExecHoldRepro/run-1.json > /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ExecHoldRepro/run-1.log 2>&1; rc=$?; cat /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ExecHoldRepro/run-1.log; printf 'EXIT=%s\n' "$rc"
exit code: 0 (counter exit 0)
verbatim tail:
statements 141 extracted 69 oracle 72 bound 72 unbound 0 mismatched_at_base 13 append_only True valid_corrections 13 false_corrections 0 unresolved 0 met True tip 382d11b2107d
EXIT=0

$ /usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-30/count-c1.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip 382d11b2107d335705875da1a4d889b074bd6fa6 --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ExecHoldRepro/run-2.json > /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ExecHoldRepro/run-2.log 2>&1; rc=$?; cat /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ExecHoldRepro/run-2.log; printf 'EXIT=%s\n' "$rc"
exit code: 0 (counter exit 0)
verbatim tail:
statements 141 extracted 69 oracle 72 bound 72 unbound 0 mismatched_at_base 13 append_only True valid_corrections 13 false_corrections 0 unresolved 0 met True tip 382d11b2107d
EXIT=0

$ /usr/bin/python3 -c 'import json,sys; r1=json.load(open(sys.argv[1])); r2=json.load(open(sys.argv[2])); old=json.load(open(sys.argv[3])); new=json.load(open(sys.argv[1])); print("run_receipt_keys_equal="+str(set(r1)==set(r2))); print("run_receipt_values_equal="+str(r1==r2)); print("run_receipts_identical="+str(r1==r2)); print("run_receipt_keys="+",".join(sorted(r1))); old.pop("tip",None); new.pop("tip",None); print("round30_vs_round31_non_tip_keys_equal="+str(set(old)==set(new))); print("round30_vs_round31_non_tip_values_equal="+str(old==new)); print("round30_vs_round31_mismatches_equal="+str(old.get("mismatches")==new.get("mismatches"))); print("round30_vs_round31_unresolved_ids_equal="+str(old.get("unresolved_ids")==new.get("unresolved_ids")))' /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ExecHoldRepro/run-1.json /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ExecHoldRepro/run-2.json /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-30/final/c1-tip.json > /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ExecHoldRepro/receipt-comparison.log 2>&1; rc=$?; cat /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ExecHoldRepro/receipt-comparison.log; printf 'EXIT=%s\n' "$rc"
exit code: 0
verbatim tail:
run_receipt_keys_equal=True
run_receipt_values_equal=True
run_receipts_identical=True
run_receipt_keys=append_only,base,by_class,correction_rows,counter,counter_sha256,extracted,false_corrections,met,mismatched_at_base,mismatches,oracle_bound,oracle_items,oracle_paths,oracle_unbound,oracle_unbound_items,statements,target,tip,unresolved,unresolved_ids,valid_corrections
round30_vs_round31_non_tip_keys_equal=True
round30_vs_round31_non_tip_values_equal=True
round30_vs_round31_mismatches_equal=True
round30_vs_round31_unresolved_ids_equal=True
EXIT=0

$ set -o pipefail; git -C /home/vgpnk/Projects/shokunin/kama-shokunin show fdf8cda19c0719f57e0c2af27e838b42304b0f56:.ufo/waves/round-30/count-c1.py | sha256sum > /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ExecHoldRepro/frozen-counter-sha256.log; rc=$?; cat /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ExecHoldRepro/frozen-counter-sha256.log; printf 'EXIT=%s\n' "$rc"
exit code: 0
verbatim tail:
c3f16ef195a6b5de24afa5a798647d917070d988954baf1fe5923fc5e19ce40d  -
EXIT=0

$ set -o pipefail; git -C /home/vgpnk/Projects/shokunin/kama-shokunin show 07794a4d30a54a60ebdff50ac76d12c6df40a0f1:.ufo/waves/round-30/count-c1.py | sha256sum > /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ExecHoldRepro/landing-base-counter-sha256.log; hash_rc=$?; git -C /home/vgpnk/Projects/shokunin/kama-shokunin diff --quiet 07794a4d30a54a60ebdff50ac76d12c6df40a0f1 382d11b2107d335705875da1a4d889b074bd6fa6 -- .ufo/waves/round-30/count-c1.py; diff_rc=$?; cat /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ExecHoldRepro/landing-base-counter-sha256.log; printf 'HASH_EXIT=%s\nDIFF_EXIT=%s\n' "$hash_rc" "$diff_rc"
exit code: 0 (hash and diff component commands both exited 0)
verbatim tail:
c3f16ef195a6b5de24afa5a798647d917070d988954baf1fe5923fc5e19ce40d  -
HASH_EXIT=0
DIFF_EXIT=0
```
FINDING: hold met True — yes.
LIMITS: Both receipts contain the same 22 keys and values; no volatile fields are present. Against the round-30 final receipt, only the measured `tip` was excluded; every other field, including `mismatches` and `unresolved_ids`, is identical, so no extracted self-assessment statement changed status. This measures only the counter's declared population and does not establish extractor completeness or the truth of the underlying assessments. The checkout HEAD was `bda324bbc5c1d7db93553adb13c5f380492c3c93`, not the requested tip; all measurements used explicit committed revision `382d11b2107d335705875da1a4d889b074bd6fa6`.
