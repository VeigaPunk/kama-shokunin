#!/usr/bin/env python3
"""Scratch harness: mutate a copy of the counter (find must occur once) and
run it against a tip; or run the unmutated counter against a tip that carries
a tip-side mutation. Prints one result block per mutant."""
import os
import subprocess
import sys

S = '/fast/scratch/hyaku/kama-r64/b/X01C2Counter'
D = S + '/clone'
COUNTER = D + '/tools/round64-c2-counter.py'

CM = [
    ('C1-dup-row-record', "            errs.append(f'dup-row:{cap}')\n            continue",
     "            pass\n            continue"),
    ('C2-quote-floor', "or len(row['quote']) < 8", "or False"),
    ('C3-drop-recon-conjunct', "('closure_ptr', 1), ('recon_mismatches', 0),",
     "('closure_ptr', 1),"),
    ('C4-recon-ignores-rc', "ok = rc == 0 and n == 0 and kv.get('met') == 'True'",
     "ok = n == 0 and kv.get('met') == 'True'"),
    ('C5-busy-no-intersection', "if not (set(before) & set(after)) <= set(seen):",
     "if False:"),
    ('C6-work-reuse-allowed', "return any(os.path.lexists(os.path.join(work, d)) for d in ('tip', 'run'))",
     "return False"),
    ('C7-tally-counts-no-disclosure', "and by[n] != 'no-disclosure'", "and True"),
    ('C8-regress-count-check', "if s.count(find) != 1:", "if s.count(find) < 1:"),
    ('C9-pin-no-compare', "elif sha256(data) != want:", "elif False:"),
    ('C10-closure-no-compare', "if ptrs[0] != newest:", "if False:"),
    ('C11-idle-no-cells', "or not isinstance(s.get('cells'), int) or s['cells'] < 1",
     ""),
    ('C12-canon-round', "if can_n != ROUND:", "if False:"),
    ('C13-noop-regression', "if replace == find:", "if False:"),
    ('C14-flip-always', "return 'flipped' if mutated_outcome == 'false' else 'not-flipped'",
     "return 'flipped'"),
    ('C15-printer-always-rejected', "    if regressed_outcome == 'true':\n        return True, 'not-flipped'\n    return False, 'printer-sensitive'",
     "    return True, 'not-flipped'"),
    ('C16-eol-anchor', "return re.search(re.escape(pat) + r'[ \\t]*$', out, re.M) is not None",
     "return pat in out"),
    ('C17-recon-planted-skipped', "if not s['n'] > f['n']:", "if False:"),
    ('C18-printer-accepts-nonexec', "    if printer_outcome != 'true':\n        return False, 'printer-not-accepted'\n", ""),
    ('C19-dup-conflict-scored', "        if seen[cap] > 1:\n            errs.append(f'dup-row:{cap}')\n            continue\n",
     ""),
    ('C20-gate-population', "    if facts.get('population') != N_CAPS:\n        bad.append('population')\n", ""),
]

TIP = {}  # filled by a driver for tip-side mutants


def run_counter(counter, tip, name):
    work = f'{S}/mw/{name}'
    subprocess.run(['rm', '-rf', work])
    os.makedirs(work)
    env = dict(os.environ, TMPDIR=work)
    p = subprocess.run([sys.executable, counter, '--repo', D, '--tip', tip,
                        '--work', work + '/w'], capture_output=True,
                       text=True, env=env, cwd=D + '/tools')
    return p.returncode, p.stdout.strip(), p.stderr


def main():
    tip = open(S + '/tipB').read().strip()
    want = sys.argv[1:]
    os.makedirs(S + '/mc', exist_ok=True)
    for name, find, rep in CM:
        if want and name not in want:
            continue
        src = open(COUNTER).read()
        assert src.count(find) == 1, (name, src.count(find))
        path = f'{S}/mc/{name}.py'
        open(path, 'w').write(src.replace(find, rep, 1))
        rc, out, err = run_counter(path, tip, name)
        esc = [l for l in err.splitlines() if l.startswith('control-')]
        line = out.splitlines()[-1] if out else ''
        keys = ' '.join(t for t in line.split() if t.split('=')[0] in (
            'covered', 'pinned', 'regress_flipped', 'printers_rejected',
            'idle_ok', 'work_reuse_refused', 'closure_ptr',
            'recon_mismatches', 'tally_disclosed', 'controls_rejected',
            'errors', 'met'))
        print(f'## {name} rc={rc} {keys}')
        for l in esc[:6]:
            print('   ', l[:200])
        sys.stdout.flush()


main()
