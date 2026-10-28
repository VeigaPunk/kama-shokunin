import sys, os, subprocess, time
sys.dont_write_bytecode = True
S = '/fast/scratch/hyaku/kama-r63/w/RV03C2CounterCode/h'
import c2
TIP = '03a6a1d850902a66a13dfad33f89cf3a8b759a09'
print('== R7 timeout leaves grandchildren running (run_bound uses subprocess.run timeout=900)')
tool = os.path.join(S, 'orphan.py')
open(tool, 'w').write("import subprocess,time\nsubprocess.Popen(['sleep','31.7231'])\ntime.sleep(60)\n")
try:
    subprocess.run(['bash', '-c', f'python3 {tool}'], capture_output=True, text=True, timeout=2)
except subprocess.TimeoutExpired:
    print('TimeoutExpired raised (as run_bound catches -> outcome TIMEOUT)')
time.sleep(0.5)
r = subprocess.run(['pgrep', '-f', 'sleep 31.7231'], capture_output=True, text=True)
print('grandchild still alive after timeout:', bool(r.stdout.strip()), r.stdout.split())
subprocess.run(['pkill', '-f', 'sleep 31.7231'])  # kills only the grandchild this probe spawned

print('== R8 sensitivity self-test term 4 depends on the token \'a\' occurring in "__kama_mut__"')
print("r62_formula('a') =", c2.r62_formula('a', 0, False, 'a'), " is_sensitive('a') =", c2.is_sensitive('a', 0, False, 'a'))
print("r62_formula('z') =", c2.r62_formula('z', 0, False, 'z'), " is_sensitive('z') =", c2.is_sensitive('z', 0, False, 'z'))
print('term4 with pattern z would be', c2.is_sensitive('z', 0, False, 'z') and not c2.r62_formula('z', 0, False, 'z'))

print('== R9 canon-drop credited on any canonical problem (no name check)')
reg = open(os.path.join(S, 'reg.tsv')).read(); sc = open(os.path.join(S, 'SCORECARD.md')).read()
bad = sc.replace('| pin-watch | List upstream release tags', '| pin-watch | List every upstream tag', 1)
head, tail = sc.split('**Capabilities — canonical list as of round 63', 1)
bad = head + '**Capabilities — canonical list as of round 63' + tail.replace('| pin-watch | List upstream release tags', '| pin-watch | List every upstream tag', 1)
pop = [(s, c2.MANIFEST[s][0]) for s, _, _ in c2.MANIFEST and [(x, None, None) for x in c2.MANIFEST]] if False else [(s, c2.MANIFEST[s][0]) for s in c2.MANIFEST]
for label, canon in [('canonical list unmutated', sc), ('canonical pin-watch prefix altered (not the sources row)', bad)]:
    c2._EXEC_CACHE.clear()
    for s in c2.MANIFEST:
        c2._EXEC_CACHE[(TIP, s)] = ('host-busy', c2.MANIFEST[s][1][0]['alt'], True, False) if s == 'context-capacity-receipt' else ('true', c2.MANIFEST[s][1][0]['pattern'], True, False)
    rej, tot, det = c2.controls(reg, '/nonexistent', S, S, TIP, {}, pop, canon)
    print(f'{label:55s} canon-drop detail: hit={det["canon-drop"]["hit"]} tags={det["canon-drop"]["tags"]}')
