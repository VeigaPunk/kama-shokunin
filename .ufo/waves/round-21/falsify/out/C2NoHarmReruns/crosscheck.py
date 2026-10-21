#!/usr/bin/env python3
# crosscheck.py - independent (Python json) check of fresh-clone reruns against the recorded
# official measurement runs/b76727f3, for every nh-*/fr-* item of recipe.json. Read-only.
import hashlib
import json
import pathlib

W = pathlib.Path('/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-21')
REC = W / 'runs' / 'b76727f3'
EV = pathlib.Path(__file__).resolve().parent / 'evidence'
recipe = json.loads((W / 'recipe.json').read_text())
recorded = json.loads((REC / 'commands.json').read_text())
rec = {c['name']: c for c in recorded['commands']}
names = [i['name'] for i in recipe if i['name'].startswith(('nh-', 'fr-'))]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


print('recipe items:', len(recipe), '| in-scope nh/fr:', len(names))
print('recipe sha256 on disk:', sha(W / 'recipe.json'), '| recorded:', recorded['recipe_sha256'])
print('recorded raw streams == recorded JSON hashes and exit files:', all(
    sha(REC / f'{n}.stdout') == rec[n]['stdout_sha256']
    and sha(REC / f'{n}.stderr') == rec[n]['stderr_sha256']
    and (REC / f'{n}.exit').read_text().strip() == f"exit={rec[n]['exit']}" for n in names))
print('recorded exit == expected_exit for all', len(rec), 'items:',
      all(c['exit'] == c['expected_exit'] for c in rec.values()))
for label in ('rerun-b76727f-run1', 'rerun-b76727f-run2', 'rerun-a661714-run1'):
    d = EV / label
    got = {c['name']: c for c in json.loads((d / 'commands.json').read_text())['commands']}
    exit_ok = sum(got[n]['exit'] == rec[n]['exit'] for n in names)
    out_bad = [n for n in names if got[n]['stdout_sha256'] != rec[n]['stdout_sha256']]
    err_bad = [n for n in names if got[n]['stderr_sha256'] != rec[n]['stderr_sha256']]
    raw_ok = all(sha(d / f'{n}.stdout') == got[n]['stdout_sha256']
                 and sha(d / f'{n}.stderr') == got[n]['stderr_sha256'] for n in names)
    print(f'{label}: exit {exit_ok}/{len(names)} | stdout-sha mismatches {out_bad} | '
          f'stderr-sha mismatches {err_bad} | raw files == own JSON: {raw_ok}')
