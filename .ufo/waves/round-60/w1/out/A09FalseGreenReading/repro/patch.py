"""Generate patched copies of kama-ollama-live.py in the seat scratch (never the lane).

Each copy demonstrates one suspected false-green path. Every patch asserts its
anchor string occurs exactly once in the pristine source before replacing.
"""
import shutil
import sys

LANE = '/home/vgpnk/Projects/shokunin/kama-shokunin'
SRC = LANE + '/tools/kama-ollama-live.py'
S = '/fast/scratch/hyaku/kama-r60/A09FalseGreenReading'

REPO_ANCHOR = "REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))"
REPO_NEW = "REPO = '/home/vgpnk/Projects/shokunin/kama-shokunin'"

PATCHES = {
    # P1: widen the post-last-check window; record the child pid for the driver to kill.
    'p1.py': [
        ("""    proc = subprocess.Popen([binary, 'serve'], env=env, stdout=log, stderr=subprocess.STDOUT,
                            cwd=work, start_new_session=True)
""",
         """    proc = subprocess.Popen([binary, 'serve'], env=env, stdout=log, stderr=subprocess.STDOUT,
                            cwd=work, start_new_session=True)
    with open(os.path.join(work, 'childpid.txt'), 'w') as _f:
        _f.write(str(proc.pid))
"""),
        ("""            check('evidence-after-load', finding == 'loaded_same_digest' and ec == 0,
                  f'kama-ollama-evidence over tags+ps after generation: {finding} exit {ec}')
""",
         """            check('evidence-after-load', finding == 'loaded_same_digest' and ec == 0,
                  f'kama-ollama-evidence over tags+ps after generation: {finding} exit {ec}')
            with open(os.path.join(work, 'window.txt'), 'w') as _f:
                _f.write('open')
            time.sleep(float(os.environ.get('A09_WINDOW_S', '20')))
"""),
    ],
    # P2: import a different GGUF than the one model-digest verified (simulates a post-digest swap).
    'p2.py': [
        ("""    if not check('model-digest', model_sha == pin['model_sha256'], 'fixture GGUF sha256 equals the pinned digest'):
        return finish('MODEL_DIGEST_MISMATCH', 2)
""",
         """    if not check('model-digest', model_sha == pin['model_sha256'], 'fixture GGUF sha256 equals the pinned digest'):
        return finish('MODEL_DIGEST_MISMATCH', 2)
    gguf = os.path.realpath(os.path.expanduser(os.environ['A09_WRONG_GGUF']))
"""),
    ],
    # P3: dump the child's exec-time environment for the leakage check.
    'p3.py': [
        ("""        check('listener-owned', pid_owns_listener(proc.pid, port), 'the listening socket on the port is held by the child pid')
""",
         """        check('listener-owned', pid_owns_listener(proc.pid, port), 'the listening socket on the port is held by the child pid')
        try:
            with open(f'/proc/{proc.pid}/environ', 'rb') as _ef:
                _envdump = _ef.read()
        except OSError:
            _envdump = b''
        with open(os.path.join(work, 'child-environ.txt'), 'wb') as _f:
            _f.write(_envdump)
"""),
    ],
    # P4: squat the chosen port between free_port() and the port-unregistered check.
    'p4.py': [
        ("""    port = free_port()
""",
         """    port = free_port()
    import threading as _th
    def _squat():
        _s = socket.socket()
        _s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        _s.bind(('127.0.0.1', port))
        _s.listen(1)
        time.sleep(60)
    _th.Thread(target=_squat, daemon=True).start()
    time.sleep(0.5)
"""),
    ],
    # P5: raise inside the finally block after the child is dead but before the receipt is written.
    'p5.py': [
        ("""    proc = subprocess.Popen([binary, 'serve'], env=env, stdout=log, stderr=subprocess.STDOUT,
                            cwd=work, start_new_session=True)
""",
         """    proc = subprocess.Popen([binary, 'serve'], env=env, stdout=log, stderr=subprocess.STDOUT,
                            cwd=work, start_new_session=True)
    with open(os.path.join(work, 'childpid.txt'), 'w') as _f:
        _f.write(str(proc.pid))
"""),
        ("""        log.close()
""",
         """        log.close()
        raise OSError('A09-simulated-finally-failure')
"""),
    ],
    # P6: point the /api/show capture at a nonexistent endpoint (server returns 404).
    'p6.py': [
        ("""        st, raw = http_call(port, 'POST', '/api/show', {'model': qualified})
""",
         """        st, raw = http_call(port, 'POST', '/api/showX', {'model': qualified})
"""),
    ],
}


def apply(name, edits):
    text = open(SRC, encoding='utf-8').read()
    text = text.replace(REPO_ANCHOR, REPO_NEW, 1)
    assert REPO_NEW in text, name + ': repo patch failed'
    for old, new in edits:
        n = text.count(old)
        assert n == 1, f'{name}: anchor occurs {n} times: {old[:60]!r}'
        text = text.replace(old, new, 1)
    open(f'{S}/copy/{name}', 'w', encoding='utf-8').write(text)
    print(f'{name}: ok ({len(text)} bytes)')


for cname, edits in PATCHES.items():
    apply(cname, edits)

# Wrong-model fixture: the pinned GGUF with three appended bytes (parser ignores trailing bytes).
shutil.copyfile('/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf', f'{S}/gguf/mymod.gguf')
with open(f'{S}/gguf/mymod.gguf', 'ab') as f:
    f.write(b'A09')
print('mymod.gguf written')
