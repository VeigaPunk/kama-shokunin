#!/bin/bash
# Pre-wave-f mutants of the AMENDED C1 counter (AMENDMENT 1). Usage: run-c1-mutants-a1.sh FIXREPO TIP SCRATCH
# Each mutant must print met=False. Output is the receipt controls/c1-mutants-a1.txt.
set -u
L=/home/vgpnk/Projects/shokunin/kama-shokunin
FIX=$1; T=$2; S=$3
mut(){ name=$1; a=$2; b=$3
  cp $L/tools/round64-c1-counter.py $S/mut-$name.py
  python3 - "$S/mut-$name.py" "$a" "$b" <<'PY'
import sys
p,a,b=sys.argv[1:4]
t=open(p).read(); assert a in t, 'pattern missing: '+a; open(p,'w').write(t.replace(a,b,1))
PY
  echo "## mutant $name: [$a] -> [$b]"
  python3 $S/mut-$name.py --repo $FIX --tip $T --work $S/wm-$name 2>&1 | cut -c1-420; echo "exit=${PIPESTATUS[0]}"
}
mut skip_receipt_ref "fails.add('receipt_ref_text')" "pass"
mut ns_always "out['bind_ns'] = bool(hs and sn) and all(" "out['bind_ns'] = True or bool(hs and sn) and all("
mut argv_prefix_only "and a == expected_argv(sp, mp, raw.get('port'))" "and a[:1] == [sp]"
mut env_denylist_only "return isinstance(e, dict) and all(
            k in ex and e[k] == ex[k] for k in e)" "return isinstance(e, dict) and not any(k.startswith('LD_') for k in e)"
mut gone_always "    pp, tk = stat_fields(pid)
    if pp is None:
        return True
    if ticks is None:
        return False" "    return True
    pp, tk = stat_fields(pid)
    if pp is None:
        return True
    if ticks is None:
        return False"
mut veto_noop "    if hit and clean_receipt:" "    if False and hit and clean_receipt:"
