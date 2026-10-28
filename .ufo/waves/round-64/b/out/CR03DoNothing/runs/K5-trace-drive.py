import importlib.util, os, sys, threading, time, json
W = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('tool', os.path.join(W, 'tools', 'kama-completion-live.py'))
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
log = open(os.path.join(W, 'spawn.log'), 'w')
orig = m._spawn_second_holder
def traced(child_pid, port):
    p = orig(child_pid, port)
    log.write(f'spawn child={child_pid} port={port} holder={None if p is None else p.pid} t={time.time():.3f}\n'); log.flush()
    return p
m._spawn_second_holder = traced
def releaser():
    hp = os.path.join(W, 'hold', 'hold.json')
    while not os.path.exists(hp): time.sleep(0.05)
    time.sleep(0.2)
    open(os.path.join(W, 'hold', 'release'), 'w').write('go\n')
    log.write(f'release written t={time.time():.3f}\n'); log.flush()
threading.Thread(target=releaser, daemon=True).start()
rc = m.main(['--work', os.path.join(W, 'tool-work'), '--server', os.path.expanduser('~/.local/bin/llama-server'),
             '--model', os.path.expanduser('~/.cache/kama-shokunin/models/stories260K.gguf'),
             '--model-sha256', '270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d',
             '--server-sha256', 'b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804',
             '--alias', 'kama-completion-probe', '--hold-dir', os.path.join(W, 'hold'), '--hold-timeout', '60',
             '--out', os.path.join(W, 'receipt.json'), '--nonce', 'trace'])
log.write(f'rc={rc}\n'); log.close()
print('rc', rc)
