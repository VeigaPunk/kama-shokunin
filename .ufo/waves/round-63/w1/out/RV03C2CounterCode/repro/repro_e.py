import sys, os
sys.dont_write_bytecode = True
S = '/fast/scratch/hyaku/kama-r63/w/RV03C2CounterCode/h'
exec(open(os.path.join(S, 'repro_d.py')).read().split('# M1:')[0])
head, tail = sc.split('**Capabilities — canonical list as of round 63', 1)
tail2 = tail.replace('| pin-watch | List upstream release tags', '| pin-watch | List every upstream tag', 1)
assert tail2 != tail
alt_sc = head + '**Capabilities — canonical list as of round 63' + tail2
for name in ['M0-unmutated', 'M2-drop-canon-prefix']:
    m = load(name.replace('-', '_'), MUTANTS[name])
    b = baseline(m, reg, alt_sc)
    print(f'{name:24s} round-63 pin-watch prefix altered -> canon_probs={b["canon_probs"]}')
