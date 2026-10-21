"""D: does the producer's fail-closed rule hold on real main() paths?

main() is executed in-process with subprocess.Popen replaced by a sentinel
that records argv and raises OSError (main() maps that to launch-failed).
Nothing is executed; the sentinel proves whether main() reached the launch
point. Trees live under /tmp/kama-r21-C2DigestSentinel/work."""
import errno
import hashlib
import json
import os
import shutil
import subprocess

import common as C

P, G, W = C.P, C.G, C.WORK
HOST = os.path.join(W, 'host-bin')
LIB_A = os.path.join(W, 'libllama-A.so.0.7.0')
LIB_B = os.path.join(W, 'libllama-B.so.0.7.1')
MODEL = os.path.join(W, 'model.gguf')
PROBE = os.path.join(W, 'probe.sh')
with open(MODEL, 'wb') as fh:
    fh.write(b'GGUF-stub-for-falsify\n')
with open(PROBE, 'w', encoding='utf-8') as fh:
    fh.write('#!/bin/sh\nexit 0\n')
MODEL_SHA = hashlib.sha256(open(MODEL, 'rb').read()).hexdigest()

SENT = []


def sentinel_popen(argv, **kwargs):
    SENT.append(list(argv))
    raise OSError(errno.ENOEXEC, 'sentinel: launch intentionally not performed')


subprocess.Popen = sentinel_popen          # main() maps OSError -> launch-failed:*
REAL_SHA = P.sha256_file


def fresh(name):
    d = os.path.join(W, 'm-' + name)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    shutil.copy(HOST, os.path.join(d, 'stub-server'))
    return d, os.path.join(d, 'stub-server')


def run_main(server, out):
    SENT.clear()
    if os.path.exists(out):
        os.unlink(out)
    rc = P.main(['--server', server, '--model', MODEL, '--model-sha256', MODEL_SHA,
                 '--probe', PROBE, '--out', out])
    rec = json.load(open(out, encoding='utf-8')) if os.path.exists(out) else None
    return rc, rec


def report(label, rc, rec):
    srv = rec['server'] if rec else {}
    print(f' {label}: rc={rc} setup_error={rec and rec["setup_error"]!r} '
          f'internal_fault={rec and rec["internal_fault"]!r} outcome={rec and rec["outcome"]!r}', flush=True)
    print(f'   launch attempted (sentinel calls)={len(SENT)}', flush=True)
    print(f'   receipt server.install_tree members={sorted(srv.get("install_tree", {}))}', flush=True)
    print(f'   receipt server.install_links={srv.get("install_links")}', flush=True)


print('== D0 control: clean stub tree reaches the launch point')
d, srv = fresh('clean')
shutil.copy(LIB_A, os.path.join(d, 'libllama.so.0.7.0'))
os.symlink('libllama.so.0.7.0', os.path.join(d, 'libllama.so.0'))
rc, rec = run_main(srv, os.path.join(W, 'm-clean.json'))
report('clean', rc, rec)

print('== D1 silent member drop: read error (EIO) on an UNLINKED member')
d1, srv1 = fresh('eio')
shutil.copy(LIB_A, os.path.join(d1, 'libllama.so.0.7.0'))
shutil.copy(LIB_B, os.path.join(d1, 'libmember-unlinked.so'))
os.symlink('libllama.so.0.7.0', os.path.join(d1, 'libllama.so.0'))
os.symlink('libllama.so.0', os.path.join(d1, 'libllama.so'))
true_tree, true_tree_sha = P.install_tree(srv1)            # honest identity, no fault
true_links, true_links_sha, _ = P.install_links(srv1)


def eio_sha(path):
    if os.path.basename(path) == 'libmember-unlinked.so':
        raise OSError(errno.EIO, os.strerror(errno.EIO), path)
    return REAL_SHA(path)


P.sha256_file = eio_sha
try:
    rc, rec = run_main(srv1, os.path.join(W, 'm-eio.json'))
    report('eio main()', rc, rec)
    print(f'   install_links problems under fault: {P.install_links(srv1)[2]}', flush=True)
    faulty_block, faulty_problems = C.server_block(srv1)
    print(f'   server_block under fault: tree members={len(faulty_block["install_tree"])} '
          f'problems={faulty_problems}', flush=True)
    print(f'   honest tree members={len(true_tree)} digest {true_tree_sha[:16]}', flush=True)
    rec_gate = C.receipt_for(srv1)[0]
    p_nopin = C.write_receipt(os.path.join(W, 'd1-eio-nopin.json'), rec_gate)
    rc_a, out_a, _ = C.gate(p_nopin, '--require-install-links')
    rc_b, out_b, _ = C.gate(p_nopin, '--require-install-links', '--expect-install-tree-sha256', true_tree_sha,
                            '--expect-install-links-sha256', true_links_sha)
    print(f'   gate on faulty-but-consistent receipt, no pin: exit={rc_a}', flush=True)
    print(f'   gate on same receipt, honest tree+links pin: exit={rc_b} | {out_b.splitlines()[:2]}', flush=True)
finally:
    P.sha256_file = REAL_SHA

print('== D2 TOCTOU variant: member unlinked between install_tree lstat and open')
d2, srv2 = fresh('race')
shutil.copy(LIB_B, os.path.join(d2, 'libmember-unlinked.so'))
shutil.copy(LIB_A, os.path.join(d2, 'libllama.so.0.7.0'))


def race_sha(path):
    if os.path.basename(path) == 'libmember-unlinked.so' and os.path.exists(path):
        os.unlink(path)                     # concurrent writer wins the race
    return REAL_SHA(path)                   # open() now raises FileNotFoundError


P.sha256_file = race_sha
try:
    rc, rec = run_main(srv2, os.path.join(W, 'm-race.json'))
    report('race main()', rc, rec)
finally:
    P.sha256_file = REAL_SHA

print('== D3 non-UTF-8 regular member name')
d3, srv3 = fresh('nonutf8')
with open(os.path.join(os.fsencode(d3), b'\xfeimpl.so'), 'wb') as fh:
    fh.write(b'x\n')
rc, rec = run_main(srv3, os.path.join(W, 'm-nonutf8.json'))
report('nonutf8 main()', rc, rec)

print('== D4 absolute-target soname link (producer PASS path)')
d4, srv4 = fresh('abs')
shutil.copy(LIB_A, os.path.join(d4, 'libllama.so.0.7.0'))
os.symlink('/usr/lib/libz.so.1', os.path.join(d4, 'libext.so.0'))
rc, rec = run_main(srv4, os.path.join(W, 'm-abs.json'))
report('abs-target main()', rc, rec)

print('== D5 C0 control-character name')
d5, srv5 = fresh('ctrl')
os.symlink('libllama.so.0.7.0', os.path.join(d5, 'lib\x1bx.so'))
rc, rec = run_main(srv5, os.path.join(W, 'm-ctrl.json'))
report('ctrl main()', rc, rec)

print('== D6 glibc-hwcaps subdirectory')
d6, srv6 = fresh('hwcaps')
os.makedirs(os.path.join(d6, 'glibc-hwcaps', 'x86-64-v3'))
rc, rec = run_main(srv6, os.path.join(W, 'm-hwcaps.json'))
report('hwcaps main()', rc, rec)

print('== D7 unreadable regular member (uid 1000, mode 000)')
d7, srv7 = fresh('unreadable')
sec = os.path.join(d7, 'libsec.so')
shutil.copy(LIB_B, sec)
os.chmod(sec, 0o000)
rc, rec = run_main(srv7, os.path.join(W, 'm-unreadable.json'))
report('unreadable main()', rc, rec)
os.chmod(sec, 0o644)
print('done D', flush=True)
