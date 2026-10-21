"""B: does the gate's chain rule agree with what the dynamic loader resolves?

Uses real ELF stubs built from /tmp/kama-r21-C2DigestSentinel/work and the
producer's own install_tree/install_links on /tmp trees. The only executable
run is a 16 KB C stub named stub-server that prints which(); llama-server is
never executed."""
import ctypes
import errno
import os
import shutil
import subprocess

import common as C

P, G, W = C.P, C.G, C.WORK
LIB_A = os.path.join(W, 'libllama-A.so.0.7.0')
LIB_B = os.path.join(W, 'libllama-B.so.0.7.1')
HOST = os.path.join(W, 'host-bin')


def fresh(name):
    d = os.path.join(W, name)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    return d


def kernel_open(path):
    try:
        fd = os.open(path, os.O_RDONLY)
        os.close(fd)
        return 'open ok'
    except OSError as exc:
        return f'open {errno.errorcode.get(exc.errno, exc.errno)}'


def dl_open(path):
    try:
        ctypes.CDLL(path)
        return 'dlopen ok'
    except OSError as exc:
        return f'dlopen FAILS: {exc}'


print('== B0 symlink target length accepted on /tmp filesystem (bisection)')
d0 = fresh('len-probe')
lo, hi = 255, 4095          # 255 known good
while lo < hi:
    mid = (lo + hi + 1) // 2
    try:
        os.symlink('t' * mid, os.path.join(d0, f'p{mid}'))
        lo = mid
    except OSError:
        hi = mid - 1
print(' largest creatable symlink target on /tmp:', lo, 'bytes')
print(' filesystem:', subprocess.run(['stat', '-f', '-c', '%T', d0], capture_output=True, text=True).stdout.strip())

print('== B1 hop limit: producer records, gate accepts, kernel/dlopen behaviour')
for k in (39, 40, 41, 42, 100):
    d = fresh(f'hops-{k}')
    shutil.copy(LIB_A, os.path.join(d, 'libllama.so.0.7.0'))
    shutil.copy(HOST, os.path.join(d, 'stub-server'))
    for i in range(k):
        target = f'hop{i + 1}.so' if i < k - 1 else 'libllama.so.0.7.0'
        os.symlink(target, os.path.join(d, f'hop{i}.so'))
    srv = os.path.join(d, 'stub-server')
    tree, _ = P.install_tree(srv)
    links, _, problems = P.install_links(srv)
    verdict = G.link_chain_problem('hop0.so', links, tree)
    print(f' k={k:3d} symlink hops: producer problems={problems} recorded={len(links)} '
          f'gate={"ACCEPT" if verdict is None else "REJECT: " + verdict} | '
          f'{kernel_open(os.path.join(d, "hop0.so"))} | '
          f'{dl_open(os.path.join(d, "hop0.so"))}', flush=True)

print('== B2 retarget between producer snapshot and load (no post-run recheck)')
D = fresh('tree-D')
shutil.copy(HOST, os.path.join(D, 'stub-server'))
shutil.copy(LIB_A, os.path.join(D, 'libllama.so.0.7.0'))
shutil.copy(LIB_B, os.path.join(D, 'libllama.so.0.7.1'))
os.symlink('libllama.so.0.7.0', os.path.join(D, 'libllama.so.0'))
os.symlink('libllama.so.0', os.path.join(D, 'libllama.so'))
srv = os.path.join(D, 'stub-server')

# producer-shaped receipt snapshot, taken BEFORE the window (cf. main() :1374-1396)
receipt, problems = C.receipt_for(srv)
print(' snapshot problems:', problems)
print(' snapshot links:', receipt['server']['install_links'])
path = C.write_receipt(os.path.join(W, 'snapshot-receipt.json'), receipt)
rc0 = subprocess.run([srv], capture_output=True, text=True, timeout=30)
print(' loader result before swap (which()):', rc0.stdout.strip(), 'exit', rc0.returncode)

# the window: same-user writer retargets the soname link
os.unlink(os.path.join(D, 'libllama.so.0'))
os.symlink('libllama.so.0.7.1', os.path.join(D, 'libllama.so.0'))
rc1 = subprocess.run([srv], capture_output=True, text=True, timeout=30)
print(' loader result after swap  (which()):', rc1.stdout.strip(), 'exit', rc1.returncode, '(2 = libB loaded)')

tree_after, tsha_after = P.install_tree(srv)
links_after, lsha_after, _ = P.install_links(srv)
print(' re-snapshot after swap links:', links_after)
print(' re-snapshot links_sha256 differs from receipt:',
      lsha_after != receipt['server']['install_links_sha256'])
print(' re-snapshot tree_sha256 differs from receipt:',
      tsha_after != receipt['server']['install_tree_sha256'])
print('done B', flush=True)
