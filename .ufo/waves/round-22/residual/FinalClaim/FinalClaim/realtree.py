#!/usr/bin/env python3
"""Read-only: frozen vs current install_tree on the real b11755 tree vs committed receipt pin."""
import hashlib, json, subprocess, sys, types
from pathlib import Path
CLONE = Path(__file__).resolve().parent / 'clone'
P = 'tools/kama-llamacpp-live.py'
def load(src, label):
    m = types.ModuleType(label); m.__file__ = str(CLONE / P)
    exec(compile(src, m.__file__, 'exec'), m.__dict__); return m
fz = subprocess.run(['git', '-C', str(CLONE), 'show', '10271460cc575fc2280aa831e442726385fc2319:' + P], capture_output=True, check=True).stdout
cur = (CLONE / P).read_bytes()
server = str(Path.home() / '.local/opt/llama-b11755/llama-server')
pin = json.load(open(CLONE / '.ufo/waves/round-18/live-recovery/receipt-1.json'))['server']['install_tree_sha256']
out = {'pin_receipt_r18_1': pin}
for label, src in (('frozen', fz), ('current', cur)):
    m = load(src, label)
    t, d = m.install_tree(server)
    out[label] = {'source_sha256': hashlib.sha256(src).hexdigest(), 'members': len(t), 'digest': d,
                  'tree_sha256': hashlib.sha256(json.dumps(t, sort_keys=True).encode()).hexdigest(),
                  'links_problems': m.install_links(server, t)[2]}
out['frozen_eq_current'] = out['frozen']['digest'] == out['current']['digest'] and out['frozen']['tree_sha256'] == out['current']['tree_sha256']
out['current_eq_pin'] = out['current']['digest'] == pin
print(json.dumps(out, indent=2))
sys.exit(0 if out['frozen_eq_current'] and out['current_eq_pin'] else 1)
