import importlib.util, os, sys, json
spec = importlib.util.spec_from_file_location('c2', sys.argv[1]); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
repo, tip, work, tree = sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
scratch = os.path.join(work, 'run'); os.makedirs(scratch, exist_ok=True)
env = {k: v for k, v in os.environ.items() if k in m.ENV_KEYS}; env['TMPDIR'] = scratch
reg = m.blob(repo, tip, m.REG)
rows, _ = m.parse_registry(reg)
for row in rows:
    outcome, observed, sens, dead = m.run_bound(row, m.MANIFEST[row['cap']][1], tree, scratch, repo, tip, env)
    print(row['cap'], row['binding'], outcome, 'sensitive=' + str(sens), 'dead=' + str(dead), '|', observed[:80].replace('\n', ' '))
