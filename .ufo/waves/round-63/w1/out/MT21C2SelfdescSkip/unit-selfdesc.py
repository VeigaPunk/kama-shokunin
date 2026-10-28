import importlib.util, os, sys
def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
S = os.environ['SCR']
env = {k: v for k, v in os.environ.items() if k in ('PATH', 'HOME', 'LANG', 'LC_ALL')}
base = load(os.path.join(S, 'clone-base-tools', 'round63-c2-counter.py'), 'base')
mB = load(os.path.join(S, 'clone-mB', 'tools', 'round63-c2-counter.py'), 'mB')
for label, m in (('unmutated', base), ('mutant-B', mB)):
    print(label, 'selfdesc_mismatches(crashing reconciler) =', m.selfdesc_mismatches(os.path.join(S, 'fake-tree'), S, 'HEAD', env))
