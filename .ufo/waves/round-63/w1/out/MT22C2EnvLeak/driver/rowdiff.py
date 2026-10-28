# MT22C2EnvLeak per-row driver: loads a counter module from a path, builds the
# row environment the way that counter's main() does (allowlist vs full), runs
# every bound row live at the tip, and prints each row outcome. Uses no json
# (the caller env may carry a json shadow on PYTHONPATH).
import importlib.util
import os
import sys

counter_path, mode, repo, tip, work = sys.argv[1:6]
spec = importlib.util.spec_from_file_location('ctr', counter_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

repo = os.path.abspath(repo)
work = os.path.abspath(work)
scratch = os.path.join(work, 'run')
os.makedirs(scratch, exist_ok=True)
caller = dict(os.environ)
if mode == 'allow':
    env = {k: v for k, v in caller.items() if k in mod.ENV_KEYS}
else:
    env = dict(caller)
env['TMPDIR'] = scratch

tip_tree = mod.checkout_tip(repo, tip, work)
sc = mod.blob(repo, tip, 'SCORECARD.md')
can_n, can_rows, _ = mod.canon_problems(sc)
population = [(slug, mod.MANIFEST[slug][0]) for slug, _, _ in mod._MANIFEST]
reg = mod.blob(repo, tip, mod.REG)
if os.environ.get('MT22_PATCH') == '1':
    # forgery-consistent record: context-capacity recorded as the forged true
    reg = reg.replace('\thost-busy\thost-not-idle-before-K1\t',
                      '\ttrue\t"all_ports_closed": true\t')
mod._EXEC_CACHE.clear()
facts = mod.score_registry(reg, tip_tree, scratch, repo, tip, env,
                           population=population)
print(f'MODE={mode} env_keys={len(env)} covered={facts["covered"]}/'
      f'{facts["population"]} bound={facts["bound"]} dead={facts["dead"]} '
      f'mismatches={facts["mismatches"]} errors={facts["errors"]}')
for (t, cap), (outcome, observed, sensitive, dead) in sorted(
        mod._EXEC_CACHE.items(), key=lambda kv: kv[0][1]):
    obs = observed.replace('\n', ' | ')[:110]
    print(f'ROW {cap:32s} outcome={outcome:9s} sensitive={sensitive} '
          f'dead={dead} observed={obs!r}')
