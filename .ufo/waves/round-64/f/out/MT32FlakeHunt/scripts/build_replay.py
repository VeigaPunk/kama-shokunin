#!/usr/bin/env python3
"""Build the replay forgery for the round-64 tip tool.

A genuine pinned llama-server child holds the run port and answers (so
every procfs observation the counter makes is genuine), but the tool
writes a receipt copied from an EARLIER run instead of performing this
run's request plane. Only the counter's live hold dir takes the branch;
every other invocation keeps the real run().

This is the wave-b MT13 forgery (which SURVIVED the freeze counter
f6a4ea9a), rebuilt against the tip tool 23b3fdb1.

Usage: build_replay.py <tool.py> <genuine-receipt.json> <out.py>
"""
import json
import sys
import textwrap

tool, receipt_path, out = sys.argv[1:4]
base = open(tool).read()

BLOCK = r'''
# ---- replay forgery (clone-only; never in the lane) ------------------
_sk = socket.socket()
_sk.bind(('127.0.0.1', 0))
_port = _sk.getsockname()[1]
_sk.close()
_child = subprocess.Popen(
    [args.server, '--model', args.model, '--alias', args.alias,
     '--port', str(_port), '--host', '127.0.0.1', '-c', '512', '-t', '1'],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    stdin=subprocess.DEVNULL)
_t0 = time.time()
while time.time() - _t0 < 60:
    try:
        if urllib.request.urlopen(
                f'http://127.0.0.1:{_port}/health', timeout=2).status == 200:
            break
    except Exception:
        time.sleep(0.2)
_hj = os.path.join(args.hold_dir, 'hold.json')
with open(_hj, 'w') as f:
    json.dump({'schema': 'kama-completion-hold/v1', 'port': _port,
               'pid': _child.pid, 'alias': args.alias,
               'model_sha256': args.model_sha256,
               'server_sha256': args.server_sha256, 'prompt': 'x',
               'at': _utc_now()}, f)
_t0 = time.time()
while (time.time() - _t0 < args.hold_timeout
       and not os.path.exists(os.path.join(args.hold_dir, 'release'))):
    time.sleep(0.1)
os.unlink(_hj)
_child.terminate()
_child.wait()
_r = json.load(open('__RECEIPT_PATH__'))
_r['nonce'] = args.nonce
_r['child_pid'] = _child.pid
_r['port'] = _port
_r['listener_holders'] = [{'pid': _child.pid, 'exe': args.server,
                           'exe_sha256': args.server_sha256}]
_r['hold'] = {'dir': args.hold_dir, 'released': True}
with open(args.out, 'w') as f:
    json.dump(_r, f, indent=1, sort_keys=True)
return 0
'''

OLD = "    args = p.parse_args(argv)\n    receipt, rc = run(args)\n"
assert base.count(OLD) == 1, 'anchor not found exactly once'
block = textwrap.indent(BLOCK.replace('__RECEIPT_PATH__', receipt_path),
                         '        ')
NEW = ("    args = p.parse_args(argv)\n"
       "    if args.hold_dir and '/live/hold' in os.path.abspath(args.hold_dir):\n"
       + block + "    receipt, rc = run(args)\n")
open(out, 'w').write(base.replace(OLD, NEW))
print(f'replay forgery written: {out}')
print('receipt template:', receipt_path)
print('template request:',
      json.load(open(receipt_path))['request'])
