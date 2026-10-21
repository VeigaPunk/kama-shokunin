"""F: a symlink named glibc-hwcaps (not a subdirectory) escapes the producer's
subdirectory guard. glibc 2.44 on this host searches
$ORIGIN/glibc-hwcaps/x86-64-v4 before $ORIGIN, following symlinks.
Stub binaries only; main() runs with Popen replaced by a launch sentinel."""
import errno
import hashlib
import json
import os
import shutil
import subprocess

import common as C

P, G, W = C.P, C.G, C.WORK
MODEL = os.path.join(W, 'model.gguf')
PROBE = os.path.join(W, 'probe.sh')
MODEL_SHA = hashlib.sha256(open(MODEL, 'rb').read()).hexdigest()
SENT = []
_REAL_POPEN = C._REAL_POPEN


def sentinel_popen(argv, **kwargs):
    SENT.append(list(argv))
    raise OSError(errno.ENOEXEC, 'sentinel: launch intentionally not performed')


def run(path):
    cp = _REAL_POPEN([path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = cp.communicate(timeout=30)
    return out.strip(), cp.returncode, err.strip()


def fresh(name):
    d = os.path.join(W, name)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    return d


# evil hwcaps root: x86-64-v4 and v3 both carry a libllama.so.0 (= libB)
EV = os.path.join(W, 'evil-hwcaps')
shutil.rmtree(EV, ignore_errors=True)
for sub in ('x86-64-v4', 'x86-64-v3'):
    os.makedirs(os.path.join(EV, sub))
    shutil.copy(os.path.join(W, 'libllama-B.so.0.7.1'), os.path.join(EV, sub, 'libllama.so.0'))

print('== F1 baseline: pinned soname chain, no hwcaps symlink')
D = fresh('hwcaps-abs')
shutil.copy(os.path.join(W, 'host-bin'), os.path.join(D, 'stub-server'))
shutil.copy(os.path.join(W, 'libllama-A.so.0.7.0'), os.path.join(D, 'libllama.so.0.7.0'))
os.symlink('libllama.so.0.7.0', os.path.join(D, 'libllama.so.0'))
srv = os.path.join(D, 'stub-server')
print(' loader:', run(srv)[0], '(1 = libA from the pinned tree)')

print('== F2 add symlink glibc-hwcaps -> absolute external dir')
os.symlink(EV, os.path.join(D, 'glibc-hwcaps'))
out, rc, err = run(srv)
print(' loader:', out, 'exit', rc, '(2 = external libB via hwcaps search)', err[:80])
print(' producer install_tree members:', sorted(P.install_tree(srv)[0]))
links, lsha, problems = P.install_links(srv)
print(' producer install_links:', links, '| problems:', problems)

SENT.clear()
import sys  # noqa: E402
subprocess.Popen = sentinel_popen          # only for the main() call below
try:
    out_path = os.path.join(W, 'f2-main.json')
    if os.path.exists(out_path):
        os.unlink(out_path)
    rc_main = P.main(['--server', srv, '--model', MODEL, '--model-sha256', MODEL_SHA,
                      '--probe', PROBE, '--out', out_path])
    rec = json.load(open(out_path, encoding='utf-8'))
finally:
    subprocess.Popen = _REAL_POPEN
print(' producer main(): rc', rc_main, '| setup_error', rec['setup_error'],
      '| launch attempted (sentinel calls):', len(SENT))
print(' receipt install_links:', rec['server']['install_links'])

rec_gate, _ = C.receipt_for(srv)
p = C.write_receipt(os.path.join(W, 'f2-gate.json'), rec_gate)
rc_g, out_g, _ = C.gate(p, '--require-install-links')
print(' gate on the producer-shaped receipt: exit', rc_g, '|', out_g.splitlines()[1].strip()[:150] if rc_g else out_g[:80])

print('== F3 relative variant: glibc-hwcaps -> ../evil-hwcaps')
D3 = fresh('hwcaps-rel')
shutil.copy(os.path.join(W, 'host-bin'), os.path.join(D3, 'stub-server'))
shutil.copy(os.path.join(W, 'libllama-A.so.0.7.0'), os.path.join(D3, 'libllama.so.0.7.0'))
os.symlink('libllama.so.0.7.0', os.path.join(D3, 'libllama.so.0'))
os.symlink('../evil-hwcaps', os.path.join(D3, 'glibc-hwcaps'))
out, rc, err = run(os.path.join(D3, 'stub-server'))
print(' loader:', out, 'exit', rc, '(2 = external libB)')
links3, _, problems3 = P.install_links(os.path.join(D3, 'stub-server'))
print(' producer install_links:', links3, '| problems:', problems3)
r3, _ = C.receipt_for(os.path.join(D3, 'stub-server'))
p3 = C.write_receipt(os.path.join(W, 'f3-gate.json'), r3)
rc_g3, out_g3, _ = C.gate(p3, '--require-install-links')
print(' gate on relative-variant receipt: exit', rc_g3, '|', out_g3.splitlines()[1].strip()[:150] if rc_g3 else out_g3[:80])
print('done F', flush=True)
