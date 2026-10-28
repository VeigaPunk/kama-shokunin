import importlib.util, sys
spec = importlib.util.spec_from_file_location('c2', '/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round63-c2-counter.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
reg = open('/dev/stdin').read() if False else None
import subprocess
txt = subprocess.run(['git','-C','/home/vgpnk/Projects/shokunin/kama-shokunin','show','03a6a1d850902a66a13dfad33f89cf3a8b759a09:registry/capability-claims-r63.tsv'],capture_output=True,text=True).stdout
pop = [(s, m.MANIFEST[s][0]) for s,_,_ in m._MANIFEST]
def mk(verdict_out):
    def scorer(row):
        cap = row['cap']
        tpl = m.MANIFEST[cap][1][0]
        return verdict_out(cap, tpl)
    return scorer
# scenario A: idle host -> outcome 'true' with the pattern observed
def idle(cap, tpl):
    if cap == 'context-capacity-receipt':
        return ('true', tpl['pattern'], True, False)
    return ('true', tpl['pattern'], True, False)
def busy(cap, tpl):
    return ('host-busy', tpl['alt'], True, False) if cap == 'context-capacity-receipt' else ('true', tpl['pattern'], True, False)
for name, fn in [('idle', idle), ('busy', busy)]:
    f = m.score(txt, mk(fn), population=pop)
    print(name, 'mismatches=', f['mismatches'], 'covered=', f['covered'], 'errors=', f['errors'], 'host_busy=', f['host_busy'], 'met_is=', m.is_met(f))
