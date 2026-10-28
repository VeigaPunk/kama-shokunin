import importlib.util, json, os, sys, copy, hashlib
S = '/fast/scratch/hyaku/kama-r63/w/KR01C1Fidelity'
REPO = S + '/clone-probe'
TIP = '03a6a1d850902a66a13dfad33f89cf3a8b759a09'
spec = importlib.util.spec_from_file_location('c1', REPO + '/tools/round63-c1-counter.py')
c1 = importlib.util.module_from_spec(spec); spec.loader.exec_module(c1)
work = S + '/work/probe'; os.makedirs(work, exist_ok=True)
tiproot = work + '/tip'
for d in ('tools', 'registry'): os.makedirs(f'{tiproot}/{d}', exist_ok=True)
tool_path = tiproot + '/tools/kama-completion-live.py'
open(tool_path, 'wb').write(c1.blob(REPO, TIP, 'tools/kama-completion-live.py'))
open(tiproot + '/tools/kama-llamacpp-live.py', 'wb').write(c1.blob(REPO, TIP, 'tools/kama-llamacpp-live.py'))
open(tiproot + '/registry/endpoint-consumers.tsv', 'wb').write(c1.blob(REPO, TIP, 'registry/endpoint-consumers.tsv'))
live_mod = c1.load_live_mod(tool_path)
receipt, witness, nonce = c1.witness_run(work, tool_path)
c1.NONCE = nonce
def rep(name, m, w=None):
    s = c1.score(m, w if w is not None else witness)
    print(f'PROBE {name}: met={s["met"]} fails={sorted(s["fails"])}')
rep('base', receipt)
rep('timing_predicted_ms_0', c1.edit_body(receipt, 'completion', lambda o: o['timings'].update(predicted_ms=0.0)))
rep('timing_prompt_n_100000', c1.edit_body(receipt, 'completion', lambda o: o['timings'].update(prompt_n=100000)))
def tok(m):
    m['captures']['tokenize']['request_body'] = '{"content": "The dog sat on the", "add_special": true}'
    m['captures']['tokenize']['request_sha256'] = c1.sha256_b(m['captures']['tokenize']['request_body'].encode())
rep('tokenize_request_content_dog', c1.edit(receipt, tok))
def temp(m):
    for k in ('completion', 'completion2'):
        c = m['captures'][k]
        j = json.loads(c['request_body']); j['temperature'] = 0.9; j['seed'] = 99
        c['request_body'] = json.dumps(j)
        c['request_sha256'] = c1.sha256_b(c['request_body'].encode())
rep('completion_request_temp_0.9_seed_99', c1.edit(receipt, temp))
rep('stored_passed_None', c1.edit(receipt, lambda m: m['checks']['completion_fingerprint'].update(passed=None)))
decoy = work + '/probe-decoy.bin'; open(decoy, 'wb').write(b'not-the-server')
rep('server_path_decoy_claimed_pinned_sha', c1.edit(receipt, lambda m: m['server'].update(path=decoy)))
rep('health_stored_false_recomputed_true', c1.edit(receipt, lambda m: m['checks']['health_ready'].update(passed=False)))
rep('stored_evaluated_false_passed_True', c1.edit(receipt, lambda m: m['checks']['completion_fingerprint'].update(evaluated=False)))
def forge_text(m):
    for k in ('completion', 'completion2'):
        j = json.loads(m['captures'][k]['body']); j['choices'][0]['text'] = ' zzz q'
        m['captures'][k]['body'] = json.dumps(j, separators=(',', ':'))
        c1.reseal(m['captures'][k])
        m['captures'][k]['headers']['content-length'] = str(m['captures'][k]['body_bytes'])
rep('forged_text_both_captures_reseal', c1.edit(receipt, forge_text))
