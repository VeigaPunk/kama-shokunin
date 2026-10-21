#!/usr/bin/env python3
"""C2 install-links policy probes (critic seat; scratch only).

Loads the producer and gate from the scratch clone at a29bb84 and the frozen
producer from 7a6bc91 (extracted to scratch). Builds synthetic install dirs
under /tmp/kama-r21-LinksPolicyCritic and copies the real install tree there
for loader-list checks. Never writes into the lane or into the real tree.
"""
import copy
import hashlib
import importlib.util
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

SCR = Path('/tmp/kama-r21-LinksPolicyCritic')
LANE = SCR / 'lane'
REAL = Path.home() / '.local/opt/llama-b11755'
LD = '/lib64/ld-linux-x86-64.so.2'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


prod = load('prod', LANE / 'tools/kama-llamacpp-live.py')
gate = load('gate', LANE / 'tests/llamacpp-live/check-receipt.py')
frozen = load('frozen', SCR / 'frozen-producer.py')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def mkdir_with(files, links):
    d = Path(tempfile.mkdtemp(prefix='probe-', dir=SCR))
    for name, data in files.items():
        (d / name).write_bytes(data)
    for name, target in links.items():
        os.symlink(target, d / name)
    return d


def identity(d):
    srv = str(d / 'llama-server')
    tree, tree_sha = prod.install_tree(srv)
    links, links_sha = prod.install_links(srv)
    return tree, tree_sha, links, links_sha


def receipt(d, tree, tree_sha, links, links_sha):
    r = copy.deepcopy(gate._selftest_receipt_v3())
    srv = str(d / 'llama-server')
    r['server'].update(arg=srv, realpath=srv, sha256=tree.get('llama-server'),
                       install_tree=tree, install_tree_sha256=tree_sha,
                       install_links=links, install_links_sha256=links_sha,
                       server_impl_sha256=None)
    r['argv'][0] = srv
    return r


def verdict(problems):
    return 'VALID' if not problems else 'INVALID: ' + ' | '.join(problems)


files = {'llama-server': b'SRV', 'libllama.so.0.7.0': b'LIB'}

print('## P1 install_links_sha256 is not injective (one crafted link name)')
G = mkdir_with(files, {'libllama.so.0': 'libllama.so.0.7.0',
                       'libllama.so': 'libllama.so.0'})
B = mkdir_with(files, {'libllama.so -> libllama.so.0\nlibllama.so.0':
                       'libllama.so.0.7.0'})
gt, gts, gl, gls = identity(G)
bt, bts, bl, bls = identity(B)
print('G links      :', gl)
print('B links      :', bl)
print('G links_sha  :', gls)
print('B links_sha  :', bls)
print('links_sha equal:', gls == bls, '| link maps equal:', gl == bl,
      '| install_tree_sha equal:', gts == bts)
name = next(iter(bl))
print('B chain check:', repr(name), '->', gate.link_chain_problem(name, bl, bt))
print('gate no pin, G:', verdict(gate.validate(receipt(G, gt, gts, gl, gls))))
print('gate no pin, B:', verdict(gate.validate(receipt(B, bt, bts, bl, bls))))
print('gate pin=G digest, B:', verdict(gate.validate(
    receipt(B, bt, bts, bl, bls), expect_links=gls)))

print('\n## P1b install_tree (frozen 7a6bc91 and current) has the same ambiguity')
A = mkdir_with({'a': b'AAA', 'b': b'BBB'}, {})
N = mkdir_with({'a ' + sha(b'AAA') + '\nb': b'BBB'}, {})
ft = frozen.install_tree(str(A / 'llama-server'))
fn = frozen.install_tree(str(N / 'llama-server'))
print('frozen tree A:', ft[0])
print('frozen tree N:', fn[0])
print('frozen install_tree_sha256 equal:', ft[1] == fn[1])

print('\n## P2 target rule: same-directory ./x and absolute same-dir targets')
print('chain ./x   :', gate.link_chain_problem(
    'libllama.so.0', {'libllama.so.0': './libllama.so.0.7.0'},
    {'libllama.so.0.7.0': 'x'}))
print('chain plain :', gate.link_chain_problem(
    'libllama.so.0', {'libllama.so.0': 'libllama.so.0.7.0'},
    {'libllama.so.0.7.0': 'x'}))
print('chain sub/x :', gate.link_chain_problem(
    'libllama.so.0', {'libllama.so.0': 'sub/libllama.so.0.7.0'},
    {'libllama.so.0.7.0': 'x'}))
D = mkdir_with(files, {'libllama.so.0': './libllama.so.0.7.0'})
dt, dts, dl, dls = identity(D)
print('producer records:', dl)
print('gate no pin, ./x:', verdict(gate.validate(receipt(D, dt, dts, dl, dls))))
AB = mkdir_with(files, {})
os.symlink(str(AB / 'libllama.so.0.7.0'), AB / 'libllama.so.0')
at, ats, al, als = identity(AB)
print('producer records abs same-dir:', al)
print('gate no pin, abs same-dir:', verdict(gate.validate(
    receipt(AB, at, ats, al, als))))

print('\n## P3 same-resolution rewrite: libllama.so -> libllama.so.0.7.0')
S = mkdir_with(files, {'libllama.so.0': 'libllama.so.0.7.0',
                       'libllama.so': 'libllama.so.0'})
st, sts, sl, sls = identity(S)
os.unlink(S / 'libllama.so')
os.symlink('libllama.so.0.7.0', S / 'libllama.so')
rt, rts, rl, rls = identity(S)
print('before:', sl)
print('after :', rl)
print('tree digest unchanged:', sts == rts, '| links digest changed:',
      sls != rls)
print('resolved bytes identical:',
      (S / 'libllama.so').resolve().read_bytes()
      == (S / 'libllama.so.0').resolve().read_bytes())
print('gate no pin:', verdict(gate.validate(receipt(S, rt, rts, rl, rls))))
print('gate pin=pre-rewrite:', verdict(gate.validate(
    receipt(S, rt, rts, rl, rls), expect_links=sls)))

print('\n## P4 retarget onto another pinned member (synthetic, LICENSE)')
pin_src = mkdir_with({'llama-server': b'SRV', 'libllama.so.0.7.0': b'LIB',
                      'LICENSE': b'text'},
                     {'libllama.so.0': 'libllama.so.0.7.0',
                      'libllama.so': 'libllama.so.0'})
_, _, _, pin = identity(pin_src)
R = mkdir_with({'llama-server': b'SRV', 'libllama.so.0.7.0': b'LIB',
                'LICENSE': b'text'},
               {'libllama.so.0': 'LICENSE', 'libllama.so': 'libllama.so.0'})
rtt, rtts, rtl, rtls = identity(R)
print('gate no pin:', verdict(gate.validate(receipt(R, rtt, rtts, rtl, rtls))))
print('gate pin=original:', verdict(gate.validate(
    receipt(R, rtt, rtts, rtl, rtls), expect_links=pin)))

print('\n## P4b real-tree mirror: retarget libmtmd.so.0 -> LICENSE')
M = SCR / 'mirror'
if M.exists():
    shutil.rmtree(M)
shutil.copytree(REAL, M, symlinks=True)
mt, mts, ml, mls = identity(M)
print('baseline chain libmtmd.so.0:', gate.link_chain_problem(
    'libmtmd.so.0', ml, mt))
base_ld = subprocess.run([LD, '--list', str(M / 'llama-server')],
                         capture_output=True, text=True)
print('baseline ld.so --list exit:', base_ld.returncode,
      '| libmtmd line:',
      [x.strip() for x in base_ld.stdout.splitlines()
       if 'libmtmd' in x][:1])
os.unlink(M / 'libmtmd.so.0')
os.symlink('LICENSE', M / 'libmtmd.so.0')
mt2, mts2, ml2, mls2 = identity(M)
print('links digest changed:', mls != mls2, '| tree digest changed:',
      mts != mts2)
print('retargeted chain libmtmd.so.0:', gate.link_chain_problem(
    'libmtmd.so.0', ml2, mt2))
print('gate no pin:', verdict(gate.validate(
    receipt(M, mt2, mts2, ml2, mls2))))
print('gate pin=baseline:', verdict(gate.validate(
    receipt(M, mt2, mts2, ml2, mls2), expect_links=mls)))
ld_after = subprocess.run([LD, '--list', str(M / 'llama-server')],
                          capture_output=True, text=True)
print('retargeted ld.so --list exit:', ld_after.returncode,
      '| stderr:', ld_after.stderr.strip().splitlines()[:2])

print('\n## P5 optional install_links: strip the fields from a new receipt')
r5 = receipt(G, gt, gts, gl, gls)
del r5['server']['install_links']
del r5['server']['install_links_sha256']
print('schema:', r5['schema'])
print('gate no pin:', verdict(gate.validate(r5)))
print('gate pin=G digest:', verdict(gate.validate(r5, expect_links=gls)))

print('\n## P6 DT_NEEDED census over the real tree (readelf -d, read-only)')
needed = set()
for f in sorted(REAL.iterdir()):
    if f.is_file() and not f.is_symlink():
        out = subprocess.run(['readelf', '-d', str(f)], capture_output=True,
                             text=True).stdout
        for line in out.splitlines():
            if '(NEEDED)' in line:
                needed.add(line.split('[')[1].split(']')[0])
links = sorted(p.name for p in REAL.iterdir() if p.is_symlink())
print('links (10):', links)
print('named in some DT_NEEDED:', [x for x in links if x in needed])
print('never in DT_NEEDED:', [x for x in links if x not in needed])
print('grid first link (sorted[0]):', links[0],
      '| grid second link (sorted[-1]):', links[-1])

print('\n## P7 frozen install_tree digest across link-only edits')
T0 = mkdir_with(files, {'libllama.so.0': 'libllama.so.0.7.0',
                        'libllama.so': 'libllama.so.0'})
base7 = frozen.install_tree(str(T0 / 'llama-server'))[1]
edits = {
    'delete libllama.so': lambda d: os.unlink(d / 'libllama.so'),
    'add extra link': lambda d: os.symlink('libllama.so.0.7.0',
                                            d / 'x.so'),
    'dangling soname': lambda d: (os.unlink(d / 'libllama.so.0'),
                                  os.symlink('nowhere', d / 'libllama.so.0')),
    'absolute outside': lambda d: (os.unlink(d / 'libllama.so.0'),
                                   os.symlink('/usr/lib/libc.so.6',
                                              d / 'libllama.so.0')),
}
for label, edit in edits.items():
    edit(T0)
    print(f'{label:<18} frozen digest unchanged:',
          frozen.install_tree(str(T0 / 'llama-server'))[1] == base7)

print('\n## P8 listing failure: producer returns {} / None')
print('install_links missing dir:', prod.install_links(
    '/nonexistent-r21/llama-server'))
print('install_tree missing dir:', prod.install_tree(
    '/nonexistent-r21/llama-server'))
miss = receipt(G, gt, gts, {}, None)
print('gate no pin, empty links:', verdict(gate.validate(miss)))
print('gate pin=G digest, empty links:', verdict(gate.validate(
    miss, expect_links=gls)))

shutil.rmtree(M)
print('\nprobe done')
