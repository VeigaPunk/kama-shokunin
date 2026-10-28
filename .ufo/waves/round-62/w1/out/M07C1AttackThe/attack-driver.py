#!/usr/bin/env python3
"""M07C1AttackThe: hold-family falsification battery against the TIP counter bytes.

Reproduction method: score()/grade() are NOT re-typed; the exact tip blob
(git show master:tools/round62-c1-counter.py, sha256-verified) is imported as a
module and its own functions are called. witness_run is replicated verbatim
(same argv, same hold.json polling, same POST payload, same witness dict,
same release write) with one addition: the (receipt, witness, nonce) triple is
persisted to JSON so the battery is re-runnable and auditable.
"""
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import time

SCRATCH = os.path.dirname(os.path.abspath(__file__))
LANE = '/home/vgpnk/Projects/shokunin/kama-shokunin'
TIP = '65d7cad0fce90e34de37527cde22e97b63b118bf'
WORK = os.path.join(SCRATCH, 'battery')

spec = importlib.util.spec_from_file_location(
    'c1counter_tip', os.path.join(SCRATCH, 'counter.py'))
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)


def witness_run_persist(work, tool_path):
    """Byte-faithful replica of tip counter witness_run; persists the triple."""
    hold = os.path.join(work, 'hold')
    os.makedirs(hold, exist_ok=True)
    nonce = 'r62-' + hashlib.sha256(os.urandom(16)).hexdigest()[:10]
    out_path = os.path.join(work, 'receipt.json')
    proc = subprocess.Popen(
        [sys.executable, tool_path, '--nonce', nonce,
         '--work', os.path.join(work, 'tool-work'),
         '--model-sha256', C.MODEL_SHA, '--server-sha256', C.SERVER_SHA,
         '--alias', C.ALIAS, '--hold-dir', hold, '--hold-timeout', '90',
         '--out', out_path],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    witness = None
    t0 = time.monotonic()
    while time.monotonic() - t0 < 120:
        if os.path.exists(os.path.join(hold, 'hold.json')):
            try:
                h = json.load(open(os.path.join(hold, 'hold.json')))
            except (ValueError, OSError):
                time.sleep(0.2)
                continue
            port = h.get('port')
            pid = h.get('pid')
            nprompt = f'{nonce} under the'
            st, body = C.post(port, {'prompt': nprompt, 'n_predict': 4,
                                     'temperature': 0.0, 'seed': 3})
            wj = {}
            try:
                wj = json.loads(body)
            except ValueError:
                pass
            ch0 = (wj.get('choices') or [{}])[0]
            mod = importlib.util.spec_from_file_location(
                'kama_live_r62', os.path.join(
                    os.path.dirname(tool_path), 'kama-llamacpp-live.py'))
            live_mod = importlib.util.module_from_spec(mod)
            mod.loader.exec_module(live_mod)
            witness = {
                'status': st, 'port': port, 'pid': pid,
                'alias': h.get('alias'),
                'model': wj.get('model'),
                'fingerprint': wj.get('system_fingerprint'),
                'text': ch0.get('text'),
                'sent_prompt': nprompt,
                'nonce_prompt': nprompt,
                'listener_owned': live_mod.port_owned_by(pid, port),
                'server_sha256': h.get('server_sha256'),
                'model_sha256': h.get('model_sha256'),
            }
            break
        if proc.poll() is not None:
            break
        time.sleep(0.25)
    open(os.path.join(hold, 'release'), 'w').write('go\n')
    try:
        proc.wait(timeout=60)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=10)
    receipt = None
    try:
        receipt = json.load(open(out_path))
    except (ValueError, OSError):
        pass
    return receipt, witness, nonce


def mutate(rcpt, fn):
    m = json.loads(json.dumps(rcpt))
    fn(m)
    return m


def strip_hold_check(m):
    m['checks'].pop('hold_released', None)


def add_hold_check(m):
    m['checks']['hold'] = {'passed': True, 'evaluated': True,
                           'reason': 'forged hold entry'}


def hold_only_released(m, val):
    m['hold'] = {'released': val}   # no dir/port/pid/schema fields


def main():
    os.makedirs(WORK, exist_ok=True)
    # replicate main()'s tiproot extraction from the tip blobs
    tiproot = os.path.join(WORK, 'tip')
    os.makedirs(os.path.join(tiproot, 'tools'), exist_ok=True)
    os.makedirs(os.path.join(tiproot, 'registry'), exist_ok=True)
    tool_path = os.path.join(tiproot, 'tools', 'kama-completion-live.py')
    with open(tool_path, 'wb') as f:
        f.write(C.blob(LANE, TIP, 'tools/kama-completion-live.py'))
    with open(os.path.join(tiproot, 'tools', 'kama-llamacpp-live.py'),
              'wb') as f:
        f.write(C.blob(LANE, TIP, 'tools/kama-llamacpp-live.py'))
    reg = C.blob(LANE, TIP, 'registry/endpoint-consumers.tsv')
    if reg:
        with open(os.path.join(tiproot, 'registry',
                               'endpoint-consumers.tsv'), 'wb') as f:
            f.write(reg)

    receipt, witness, nonce = witness_run_persist(WORK, tool_path)
    C.NONCE = nonce  # same global step main() performs
    assert receipt is not None and witness is not None, 'live run failed'
    with open(os.path.join(SCRATCH, 'genuine-receipt.json'), 'w') as f:
        json.dump(receipt, f, indent=1, sort_keys=True)
    with open(os.path.join(SCRATCH, 'genuine-witness.json'), 'w') as f:
        json.dump(witness, f, indent=1, sort_keys=True)
    with open(os.path.join(SCRATCH, 'genuine-nonce.txt'), 'w') as f:
        f.write(nonce + '\n')
    print(f'live run: nonce={nonce} port={receipt["port"]} '
          f'child_pid={receipt["child_pid"]} verdict={receipt["verdict"]} '
          f'checks={sorted(receipt["checks"])}')
    print(f'receipt hold section: {json.dumps(receipt.get("hold"))}')
    hold_dir = os.path.join(WORK, 'hold')

    def show(name, rcpt, note=''):
        try:
            s = C.score(rcpt, witness)
        except Exception as exc:
            print(f'[{name}] CRASH (inconclusive): '
                  f'{type(exc).__name__}: {exc}')
            return None
        v = 'ACCEPTED' if s['met'] else 'REJECTED'
        print(f'[{name}] {v} score()={json.dumps(s, sort_keys=True)}'
              + (f' | {note}' if note else ''))
        return s

    print('--- battery (instrument: tip blob 275610b5..., functions imported unmodified) ---')

    # B0 baseline: pristine genuine pair
    show('B0-pristine', receipt,
         'tip counter vs its own genuine receipt')

    # H0 the counter's own hold control family: released=False, checks intact
    h0 = mutate(receipt, lambda m: m['hold'].update({'released': False}))
    s_h0 = show('H0-released-false-checks-intact', h0,
                "the 'hold' control family mutation")
    s_b0 = C.score(receipt, witness)
    print(f"[H0-vs-B0] rejection JSON identical to pristine: "
          f"{json.dumps(s_h0, sort_keys=True) == json.dumps(s_b0, sort_keys=True)}"
          " (non-discriminative if True)")

    # H1 gate-on probe: doctored checks['hold'], released=False
    h1 = mutate(receipt, lambda m: (add_hold_check(m),
                                    m['hold'].update({'released': False})))
    show('H1-gate-on-hold-key-released-false', h1)

    # H2 gate-on probe: checks['hold'] instead of hold_released, released=True, no dir
    h2 = mutate(receipt, lambda m: (add_hold_check(m),
                                    strip_hold_check(m),
                                    hold_only_released(m, True)))
    show('H2-gate-on-released-true-no-dir', h2)

    # F4 fs-independence demo first (dir still on disk): score pristine with
    # dir present, then with dir renamed away
    s_present = C.score(receipt, witness)
    shutil.move(hold_dir, hold_dir + '.gone')
    s_absent = C.score(receipt, witness)
    print(f'[F4-fs-probe] hold dir on disk: {json.dumps(s_present, sort_keys=True)}')
    print(f'[F4-fs-probe] hold dir absent : {json.dumps(s_absent, sort_keys=True)}')
    print(f'[F4-fs-probe] identical: '
          f'{json.dumps(s_present, sort_keys=True) == json.dumps(s_absent, sort_keys=True)}')

    # F1 ASSIGNED FORGERY: released=true, no release timestamp / no hold dir /
    # no schema fields, vacuous check entry stripped -> receipt silent on window
    f1 = mutate(receipt, lambda m: (strip_hold_check(m),
                                    hold_only_released(m, True)))
    show('F1-released-true-no-timestamp-no-dir', f1,
         'hold window semantics broken; receipt carries no hold evidence')

    # F2 mirror of the hold family: released=false, same broken semantics
    f2 = mutate(receipt, lambda m: (strip_hold_check(m),
                                    hold_only_released(m, False)))
    show('F2-released-false-no-timestamp-no-dir', f2,
         'never-released hold accepted once vacuous entry is stripped')

    # restore hold dir name for cleanliness of any later inspection
    if os.path.exists(hold_dir + '.gone') and not os.path.exists(hold_dir):
        shutil.move(hold_dir + '.gone', hold_dir)


if __name__ == '__main__':
    main()
