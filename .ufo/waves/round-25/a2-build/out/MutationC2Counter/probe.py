#!/usr/bin/env python3
"""Synthetic-only C2 counter probe; never starts a server or edits lane source."""
import concurrent.futures as cf
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

BASE = Path(__file__).resolve().parent
SOURCE = BASE.parents[2] / 'count-c2.py'
ORIGINAL = SOURCE.read_bytes()
TEXT = ORIGINAL.decode()
SHA = lambda b: hashlib.sha256(b).hexdigest()
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location('counter_under_test', SOURCE)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
BASE.mkdir(exist_ok=True)
for name in ('receipts', 'mutants'):
    (BASE / name).mkdir(exist_ok=True)
valid = {'server_version': 'version: 0.7.0-dev (build 11755, commit 704366d76)',
         'model_sha256': m.MODEL_SHA, 'cells': []}
for cid, (args, kind) in m.CELLS.items():
    c = {'id': cid, 'args': args, 'observed': True, 'props_n_ctx': 2048,
         'total_slots': 4, 'slots_n_ctx': [2048] * 4,
         'models_n_ctx_train': 2048, 'kv_pool_n_ctx': 2048,
         'log_lines': ['llama_context: n_ctx = 2048']}
    if kind.startswith('load'):
        c.update(request_mode='sequential' if kind == 'load-sequential' else 'concurrent',
                 requests=[{'status': 200, 'prompt_tokens': 1000, 'n_predict': 600} for _ in range(2)])
    valid['cells'].append(c)
receipts = {'valid_all_14': valid}
def cell_case(name, field, value=None, cid='K1', delete=False):
    d = copy.deepcopy(valid)
    c = next(c for c in d['cells'] if c['id'] == cid)
    if delete:
        c.pop(field)
    else:
        c[field] = value
    receipts[name] = d

def root_case(name, field, value):
    d = copy.deepcopy(valid)
    d[field] = value
    receipts[name] = d

def request_case(name, field, value):
    d = copy.deepcopy(valid)
    c = next(c for c in d['cells'] if c['id'] == 'L1')
    c['requests'][0][field] = value
    receipts[name] = d

root_case('failed_start_truthy_observed_only', 'cells',
          [{'id': cid, 'args': args, 'observed': 'false', 'started': 'false'}
           for cid, (args, _) in m.CELLS.items()])
d = copy.deepcopy(valid)
for c in d['cells']:
    c.update(observed='false', started='false')
receipts['failed_start_truthy_complete_fields'] = d
for field in ('props_n_ctx', 'total_slots', 'models_n_ctx_train', 'kv_pool_n_ctx'):
    cell_case('truthy_string_' + field, field, '2048')
    cell_case('missing_' + field, field, delete=True)
    cell_case('boolean_' + field, field, True)
cell_case('boolean_slots_element', 'slots_n_ctx', [True])
cell_case('string_slots_element', 'slots_n_ctx', ['2048'])
cell_case('empty_slots', 'slots_n_ctx', [])
cell_case('wrong_args', 'args', '-c 999')
d = copy.deepcopy(valid)
d['cells'].append(copy.deepcopy(d['cells'][0]))
receipts['duplicate_K1'] = d
d = copy.deepcopy(valid)
d['cells'].append(dict(copy.deepcopy(d['cells'][0]), id='EXTRA'))
receipts['extra_cell'] = d
root_case('wrong_server_build', 'server_version', 'build 11754')
root_case('wrong_server_build_prefix_collision', 'server_version', 'build 117550')
root_case('missing_server_version', 'server_version', None)
root_case('wrong_model_sha', 'model_sha256', '0' * 64)
cell_case('kv_pool_no_matching_log', 'log_lines', ['llama_context: n_ctx = 4096'])
cell_case('kv_pool_suffix_collision', 'log_lines', ['llama_context: n_ctx = 12048'])
cell_case('kv_pool_non_numeric_log', 'log_lines', ['llama_context: n_ctx = nonsense2048'])
cell_case('kv_pool_unrelated_suffix', 'log_lines', ['unrelated = 2048'])
cell_case('empty_logs', 'log_lines', [])
cell_case('empty_log_element', 'log_lines', ['', 'llama_context: n_ctx = 2048'])
cell_case('nonstring_log_element', 'log_lines', [123, 'llama_context: n_ctx = 2048'])
cell_case('mapping_logs', 'log_lines', {'llama_context: n_ctx = 2048': True})
cell_case('one_load_request', 'requests', [{'status': 200, 'prompt_tokens': 1000, 'n_predict': 600}], cid='L1')
cell_case('mapping_requests', 'requests', {'one': {}, 'two': {}}, cid='L1')
cell_case('wrong_request_mode', 'request_mode', 'sequential', cid='L1')
cell_case('request_not_dict', 'requests', [None, {'status': 200, 'prompt_tokens': 1000, 'n_predict': 600}], cid='L1')
request_case('boolean_http_status', 'status', True)
request_case('string_http_status', 'status', '200')
request_case('wrong_prompt_tokens', 'prompt_tokens', 999)
request_case('wrong_n_predict', 'n_predict', 599)
request_case('boolean_prompt_tokens', 'prompt_tokens', True)
request_case('boolean_n_predict', 'n_predict', True)
request_case('float_prompt_tokens', 'prompt_tokens', 1000.0)
request_case('float_n_predict', 'n_predict', 600.0)
for name, d in receipts.items():
    (BASE / 'receipts' / (name + '.json')).write_text(json.dumps(d, indent=2) + '\n')

# Each tuple weakens one behavior-bearing guard in a distinct scratch copy.
mutations = [
 ('M01_boolean_ints', 'return isinstance(v, int) and not isinstance(v, bool)', 'return isinstance(v, int)', 'boolean_props_n_ctx'),
 ('M02_integer_type', 'return isinstance(v, int) and not isinstance(v, bool)', 'return not isinstance(v, bool)', 'truthy_string_props_n_ctx'),
 ('M03_props_type', 'is_int(c.get("props_n_ctx"))', 'True', 'truthy_string_props_n_ctx'),
 ('M04_slot_count_type', 'is_int(c.get("total_slots"))', 'True', 'truthy_string_total_slots'),
 ('M05_training_type', 'is_int(c.get("models_n_ctx_train"))', 'True', 'truthy_string_models_n_ctx_train'),
 ('M06_pool_type', 'is_int(c.get("kv_pool_n_ctx"))', 'True', 'truthy_string_kv_pool_n_ctx'),
 ('M07_slots_guard', 'if not (isinstance(s, list) and s and all(is_int(x) for x in s)):', 'if False:', 'empty_slots'),
 ('M08_slots_nonempty', 'isinstance(s, list) and s and all(is_int(x) for x in s)', 'isinstance(s, list) and all(is_int(x) for x in s)', 'empty_slots'),
 ('M09_slots_elements', 'all(is_int(x) for x in s)', 'True', 'boolean_slots_element'),
 ('M10_log_list', 'isinstance(lines, list) and lines', 'lines', 'mapping_logs'),
 ('M11_log_elements', 'all(isinstance(x, str) and x for x in lines)', 'True', 'empty_log_element'),
 ('M12_pool_log_match', 'if not any("llama_context: n_ctx " in x and x.rstrip().endswith(\n            str(c["kv_pool_n_ctx"])) for x in lines):', 'if False:', 'kv_pool_no_matching_log'),
 ('M13_pool_log_label', '"llama_context: n_ctx " in x and x.rstrip().endswith(', 'x.rstrip().endswith(', 'kv_pool_unrelated_suffix'),
 ('M14_pool_log_value', 'x.rstrip().endswith(\n            str(c["kv_pool_n_ctx"]))', 'True', 'kv_pool_no_matching_log'),
 ('M15_load_evidence', 'if kind.startswith("load"):', 'if False:', 'one_load_request'),
 ('M16_request_mode', 'if c.get("request_mode") != want:', 'if False:', 'wrong_request_mode'),
 ('M17_request_cardinality', 'isinstance(r, list) and len(r) >= 2', 'isinstance(r, list)', 'one_load_request'),
 ('M18_status_type', 'is_int(q.get("status"))', 'True', 'boolean_http_status'),
 ('M19_prompt_count', 'q.get("prompt_tokens") == LOAD_REQUEST["prompt_tokens"]', 'True', 'wrong_prompt_tokens'),
 ('M20_prediction_count', 'q.get("n_predict") == LOAD_REQUEST["n_predict"]', 'True', 'wrong_n_predict'),
 ('M21_duplicates', 'cid not in CELLS or ids.count(cid) != 1', 'cid not in CELLS', 'duplicate_K1'),
 ('M22_registered_id', 'cid not in CELLS or ids.count(cid) != 1', 'ids.count(cid) != 1', 'extra_cell'),
 ('M23_registered_args', 'c.get("args") == args and cell_ok(c, kind)', 'cell_ok(c, kind)', 'wrong_args'),
 ('M24_build_binding', '"build 11755" in ver', 'True', 'wrong_server_build'),
 ('M25_model_binding', 'sha == MODEL_SHA', 'True', 'wrong_model_sha'),
 ('M26_version_type', 'isinstance(ver, str) and "build 11755" in ver', '"build 11755" in ver', 'missing_server_version'),
 ('M27_log_nonempty', 'isinstance(lines, list) and lines', 'isinstance(lines, list)', 'empty_logs'),
 ('M28_slots_list', 'isinstance(s, list) and s and all(is_int(x) for x in s)', 's and all(is_int(x) for x in s)', 'string_slots_element'),
 ('M29_request_dict', 'isinstance(q, dict) and is_int(q.get("status"))', 'is_int(q.get("status"))', 'request_not_dict'),
]

def run(counter, receipt):
    p = subprocess.run([sys.executable, str(counter), str(BASE / 'receipts' / (receipt + '.json'))],
                       capture_output=True, text=True, timeout=5)
    return {'exit_code': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr}

def result_same(a, b):
    # stderr traceback file paths differ for an error; pristine selected probes all exit 0.
    return a == b

pristine = BASE / 'count-c2-pristine.py'
pristine.write_bytes(ORIGINAL)
with cf.ThreadPoolExecutor(max_workers=4) as pool:
    baseline = dict(zip(receipts, pool.map(lambda n: run(pristine, n), receipts)))

def probe(item):
    name, old, new, receipt = item
    if TEXT.count(old) != 1:
        raise RuntimeError(f'{name}: anchor count {TEXT.count(old)}')
    path = BASE / 'mutants' / (name + '.py')
    path.write_bytes(ORIGINAL)
    before = SHA(path.read_bytes())
    b = {r: run(path, r) for r in ('valid_all_14', receipt)}
    mutated = TEXT.replace(old, new, 1).encode()
    try:
        path.write_bytes(mutated)
        after_mutation = SHA(path.read_bytes())
        changed = {r: run(path, r) for r in ('valid_all_14', receipt)}
    finally:
        path.write_bytes(ORIGINAL)
    after_restoration = SHA(path.read_bytes())
    restored = {r: run(path, r) for r in ('valid_all_14', receipt)}
    baseline_ok = all(v['exit_code'] == 0 for v in b.values()) and b == restored
    verdict = ('inconclusive' if not baseline_ok else
               'killed' if any(not result_same(b[r], changed[r]) for r in b) else 'survived')
    return {'name': name, 'receipt': receipt, 'old': old, 'new': new,
            'before_sha256': before, 'mutated_sha256': after_mutation,
            'restored_sha256': after_restoration, 'baseline': b,
            'mutated': changed, 'restored': restored, 'verdict': verdict}
with cf.ThreadPoolExecutor(max_workers=4) as pool:
    results = list(pool.map(probe, mutations))
summary = {'source': str(SOURCE), 'source_before_sha256': SHA(ORIGINAL),
           'source_after_sha256': SHA(SOURCE.read_bytes()),
           'python_version': sys.version, 'receipts': baseline, 'mutants': results}
(BASE / 'results.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps({'receipts': len(receipts), 'mutants': len(results),
                  'verdicts': {k: sum(x['verdict'] == k for x in results)
                               for k in ('killed', 'survived', 'inconclusive')},
                  'source_sha256': summary['source_after_sha256'],
                  'restorations_exact': all(x['before_sha256'] == x['restored_sha256'] for x in results)}, indent=2))
