#!/usr/bin/env python3
"""M12C2AttackVerdict: verdict-family probes A2 + A3 against one live pass.

A2: registry pristine (victim verdict=true) while the victim tool is broken
    in the tip -> does the recorded-vs-computed verdict check catch the lie?
    Run through mod.main() — the counter's own code path, exit code returned.
A3: same tip (same cached executions), registry edited to honest-false:
    verdict=false + observed synced to the failing output. The freeze
    kill rule says a bound run that does not emit its frozen pattern kills
    the claim; does the counter's met agree?

Byte-pinned module: round62-c2-counter.py == git show master (sha256
15d11f1ce8f8cb85e002d83c50b40d2bd7e4dfa561d8dd2d453e2daa09c05929).
"""
import importlib.util
import json
import os
import sys

S = os.path.dirname(os.path.abspath(__file__))
FIX = os.path.join(S, 'fixture2')
TIP = sys.argv[1]

spec = importlib.util.spec_from_file_location(
    'c2counter', os.path.join(S, 'round62-c2-counter.py'))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

# ---- A2: the counter's own main() on the broken-tool fixture -------------
rc_a2 = mod.main(['--repo', FIX, '--tip', TIP,
                  '--work', os.path.join(S, 'work-a2')])
print(f'A2_exit={rc_a2}', file=sys.stderr)

# ---- A3: same tip, mutated registry text, executions come from cache ------
tip_tree = mod.checkout_tip(FIX, TIP, os.path.join(S, 'work-a2'))
scratch = os.path.join(S, 'work-a2', 'run')
env = dict(os.environ)
env['TMPDIR'] = scratch
env.pop('PYTHONPATH', None)

# canonical-section terms, byte-faithful to main()
sc = mod.blob(FIX, TIP, 'SCORECARD.md')
can_n, can_rows = mod.canonical_rows(sc)
canon_mismatch = []
population = None
if can_rows:
    slugs = [s for s, _ in can_rows]
    expected = [s for s, _, _ in mod._MANIFEST]
    if len(slugs) != len(set(slugs)) or not set(expected).issubset(slugs):
        canon_mismatch.append('canonical rows must contain each frozen '
                              f'capability once: {slugs}')
    population = [(slug, mod.MANIFEST[slug][0]) for slug in expected]
    for slug, prefix, _ in mod._MANIFEST:
        row_text = next((text for seen, text in can_rows if seen == slug), '')
        if not row_text.startswith(prefix):
            canon_mismatch.append(f'prefix:{slug}')
else:
    canon_mismatch.append('no canonical list section at tip')

reg_text = open(os.path.join(S, 'reg-a3.tsv')).read()
facts = mod.score_registry(reg_text, tip_tree, scratch, FIX, TIP, env,
                           population=population)
rejected, total, cdetail = mod.controls(facts, reg_text, tip_tree, scratch,
                                        FIX, TIP, env, population)
met = (bool(can_rows) and not canon_mismatch
       and facts['covered'] == facts['population']
       and facts['bound'] >= facts['population']
       and facts['dead'] == 0 and facts['mismatches'] == 0
       and facts['errors'] == 0 and rejected == total
       and population is not None and len(population) == mod.MIN_ROWS)
print(f"A3: population={facts['population']} rows={facts['rows']} "
      f"covered={facts['covered']}/{facts['population']} "
      f"bound={facts['bound']} eval_lines={facts['eval_lines']} "
      f"sensitive={facts['sensitive']}/{facts['bound']} "
      f"dead={facts['dead']} mismatches={facts['mismatches']} "
      f"canonical={can_n} controls_rejected={rejected}/{total} "
      f"errors={facts['errors'] + len(canon_mismatch)} met={met}")
print(f'A3_exit={0 if met else 1}', file=sys.stderr)
print('A3_err_list=' + json.dumps(facts['err_list'][:8]), file=sys.stderr)
print('A3_control_escapes=' + json.dumps(
    {k: v for k, v in cdetail.items() if v['met']}), file=sys.stderr)
