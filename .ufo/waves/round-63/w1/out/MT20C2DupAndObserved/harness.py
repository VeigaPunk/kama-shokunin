"""In-process discriminator for the three C2 mutants. The live scorer is replaced
by the recorded verdict (no servers launched); everything else - score(),
controls(), canon_problems() - is the committed counter code, unmodified except
for the one mutation under test. Used only to show per-control tags; the live
counter runs are the primary evidence."""
import importlib.util
import os
import subprocess
import sys

S = '/fast/scratch/hyaku/kama-r63/w/MT20C2DupAndObserved'
CLONE = os.path.join(S, 'clone')
TIP = '03a6a1d850902a66a13dfad33f89cf3a8b759a09'
WT = {'base': os.path.join(S, 'wt-base/tools/round63-c2-counter.py'),
      'a': os.path.join(S, 'wt-a/tools/round63-c2-counter.py'),
      'b': os.path.join(S, 'wt-b/tools/round63-c2-counter.py'),
      'c': os.path.join(S, 'wt-c/tools/round63-c2-counter.py')}


def git_show(path):
    return subprocess.run(['git', '-C', CLONE, 'show', f'{TIP}:{path}'],
                          capture_output=True, text=True).stdout


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def load_variant_a1():
    """Variant a1: delete the whole dup-row block (duplicate is then scored)."""
    src = open(WT['base']).read()
    old = ("        if seen[cap] > 1:\n"
           "            errs.append(f'dup-row:{cap}')\n"
           "            continue\n")
    assert src.count(old) == 1
    path = os.path.join(S, 'variant_a1.py')
    open(path, 'w').write(src.replace(old, ''))
    return load(path, 'c2_a1')


def fake_run_bound(row, templates, tip_tree, scratch, repo, tip, env):
    tpl = next(t for t in templates if t['id'] == row['binding'])
    if row['verdict'].lower() == 'host-busy':
        return ('host-busy', tpl['alt'], True, False)
    return ('true', tpl['pattern'], True, False)


def run(label, m, reg):
    m._EXEC_CACHE.clear()
    m.run_bound = fake_run_bound
    sc = git_show('SCORECARD.md')
    can_n, can_rows, canon_mismatch = m.canon_problems(sc)
    population = [(slug, m.MANIFEST[slug][0]) for slug, _, _ in m._MANIFEST]
    facts = m.score_registry(reg, None, S, CLONE, TIP, {}, population=population)
    baseline = bool(can_rows) and not canon_mismatch and m.is_met(facts)
    m._EXEC_CACHE.clear()
    rejected, total, detail = m.controls(reg, None, S, CLONE, TIP, {},
                                         population, sc)
    print(f'[{label}] baseline_facts: covered={facts["covered"]}/'
          f'{facts["population"]} bound={facts["bound"]} '
          f'mismatches={facts["mismatches"]} errors={facts["errors"]} '
          f'baseline_met={baseline} err_list={facts["err_list"][:3]}')
    print(f'[{label}] controls_rejected={rejected if baseline else 0}/{total}'
          f' (raw={rejected}, baseline_gate={baseline})')
    for k, v in detail.items():
        flag = 'HIT ' if v['hit'] else 'ESCAPE'
        print(f'    {flag} {k:10s} met={v["met"]} tags={v["tags"]}')
    return facts, rejected


def main():
    reg = git_show('registry/capability-claims-r63.tsv')
    mods = {k: load(v, f'c2_{k}') for k, v in WT.items()}
    mods['a1'] = load_variant_a1()
    print('== REAL REGISTRY (tip 03a6) ==')
    for k in ('base', 'a', 'a1', 'b', 'c'):
        run(k, mods[k], reg)

    lines = reg.splitlines()
    head, data = lines[0], lines[1:]
    cells = [l.split('\t') for l in data]
    print('\n== PLANTED ROWS (scored only; controls not rerun) ==')
    plants = {
        'short-quote-6': [head] + ['\t'.join(
            [c[0], 'Curate'] + c[2:]) if i == 0 else l
            for i, (c, l) in enumerate(zip(cells, data))],
        'empty-quote': [head] + ['\t'.join(
            [c[0], ''] + c[2:]) if i == 0 else l
            for i, (c, l) in enumerate(zip(cells, data))],
        'nonident-dup': [head] + data + [
            '\t'.join(['sources-registry', 'Curate where', 'census',
                       'python3 %T/tools/evil.py --selftest',
                       '45/45 selftest cases passed', 'true',
                       '45/45 selftest cases passed', 'planted'])],
    }
    for pname, rows in plants.items():
        text = '\n'.join(rows) + '\n'
        for k in ('base', 'a', 'a1', 'b', 'c'):
            m = mods[k]
            m._EXEC_CACHE.clear()
            m.run_bound = fake_run_bound
            sc = git_show('SCORECARD.md')
            _, _, _ = m.canon_problems(sc)
            population = [(slug, m.MANIFEST[slug][0]) for slug, _, _ in m._MANIFEST]
            f = m.score_registry(text, None, S, CLONE, TIP, {},
                                 population=population)
            print(f'  {pname:14s} {k:5s} covered={f["covered"]}/{f["population"]}'
                  f' mismatches={f["mismatches"]} errors={f["errors"]}'
                  f' err={f["err_list"][:2]} is_met={m.is_met(f)}')


if __name__ == '__main__':
    sys.exit(main())
