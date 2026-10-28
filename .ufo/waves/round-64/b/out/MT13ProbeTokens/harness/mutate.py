#!/usr/bin/env python3
"""Write one mutant of the counter into the clone's working tree. Each mutant
is one or more exact-string replacements, each asserted to match exactly once
in the counter as committed at HEAD~ (the genuine counter). Usage: mutate.py <id>|restore"""
import subprocess, sys
S = '/fast/scratch/hyaku/kama-r64/b/MT13ProbeTokens'
D = S + '/clone'
P = D + '/tools/round64-c1-counter.py'
ALL_BIND = ("    return out\n\n\nBIND_CHECKS",
            "    for _k in list(out):\n        out[_k] = True\n    return out\n\n\nBIND_CHECKS")
NO_LHP = ("    out['listener_holders_pinned'] = bool(",
          "    out['listener_holders_pinned'] = True or bool(")
NO_REF = ("        f.add('live_ref_text')\n", "        pass  # no ref text\n")
M = {
 'm01_drop_live_ref_text': [NO_REF],
 'm02_drop_live_ref_usage': [("        f.add('live_ref_usage')\n", "        pass  # m02\n")],
 'm03_drop_finish_gate': [("and (p.get('finish_reason') != 'length' or uc == n)", "and True")],
 'm04_drop_pn_cn_sum': [("and pn + cn == up):", "):")],
 'm05_drop_live_ptok': [("        f.add('live_ptok')\n", "        pass  # m05\n")],
 'm06_drop_live_status': [("        f.add('live_status')\n", "        pass  # m06\n")],
 'm07_drop_live_fp_shape': [("        f.add('live_fp_shape')\n", "        pass  # m07\n")],
 'm08_fixed_n_predict': [("        n = rng.randint(3, 9)\n", "        n = 8\n")],
 'm09_hollow_reference': [("            witness['ref'] = ref\n", "            witness['ref'] = []\n")],
 'm13_disable_bind_holders': [("    out['bind_holders'] = bool(", "    out['bind_holders'] = True or bool(")],
 'm14_disable_bind_exe': [("    out['bind_exe'] = bool(hs) and all(", "    out['bind_exe'] = True or bool(hs) and all(")],
 'm15_no_holder_observation': [ALL_BIND, NO_LHP],
 'm16_no_ref_no_holder': [ALL_BIND, NO_LHP, NO_REF],
}
arg = sys.argv[1]
base = subprocess.run(['git', '-C', D, 'show', 'f6a4ea9a8b5a876d685b08e7e582ec0723412a4a:tools/round64-c1-counter.py'],
                      capture_output=True, check=True).stdout.decode()
if arg == 'restore':
    open(P, 'w').write(base); print('restored'); sys.exit(0)
txt = base
for old, new in M[arg]:
    n = txt.count(old)
    assert n == 1, (arg, n, old[:60])
    txt = txt.replace(old, new)
open(P, 'w').write(txt)
print('mutant', arg, 'applied (%d replacement(s))' % len(M[arg]))
