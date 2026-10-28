import importlib.util, sys, subprocess
sys.dont_write_bytecode = True
L = '/home/vgpnk/Projects/shokunin/kama-shokunin'
spec = importlib.util.spec_from_file_location('r62c2', L + '/tools/round62-c2-counter.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
TIP = '03a6a1d850902a66a13dfad33f89cf3a8b759a09'
reg = subprocess.run(['git', '-C', L, 'show', TIP + ':registry/capability-claims-r62.tsv'],
                     capture_output=True, text=True).stdout

def run(label, bad_rows):
    # mock live scorer: verdict from registry row; `bad_rows` rows report a wrong verdict
    # (stands in for the live mismatches of the measured baseline); sensitivity true.
    calls = {'n': 0}
    def mock_scorer(row):
        calls['n'] += 1
        live = True  # live truth: every bound check is green at the measured tip
        v = (not live) if row['cap'] in bad_rows else live
        return v, row['observed'] or '', True, False
    def fake_score_registry(text, tip_tree, scratch, repo, tip, env, population=None):
        return m.score(text, mock_scorer, population=population)
    m.score_registry = fake_score_registry
    base = m.score(reg, mock_scorer, population=None)
    rej, tot, det = m.controls(base, reg, '/x', '/x', L, TIP, {}, None)
    print(f"[{label}] baseline mismatches={base['mismatches']} errors={base['errors']} "
          f"covered={base['covered']}/{base['population']} bound={base['bound']} "
          f"controls_rejected={rej}/{tot}")
    for k, v in det.items():
        if v['met']:
            print(f"   ESCAPE {k}: met=True covered={v['covered']} mismatches={v['mismatches']} errors={v['errors']}")
    print('   err-list-base:', base['err_list'][:2])

run('clean baseline', set())
run('4-mismatch baseline (as measured)', {'sources-registry', 'pin-watch', 'digest-ledger', 'hexrun-census'})
