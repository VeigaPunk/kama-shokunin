"""E: (1) loader shadowing by an ADDED regular file after the producer snapshot
(RUNPATH=$ORIGIN), (2) non-UTF-8 link keys under a non-Python JSON reader,
(3) 'canonical JSON' portability, (4) gate chain-walk cost on long chains.
Only stub binaries built in /tmp are executed."""
import json
import os
import shutil
import subprocess
import sys
import time

import common as C

P, G, W = C.P, C.G, C.WORK


def fresh(name):
    d = os.path.join(W, name)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    return d


def sh(cmd):
    cp = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    return cp.returncode, cp.stdout.strip(), cp.stderr.strip()


print('== E1a build shadow stubs (soname libz.so.1; RUNPATH $ORIGIN on host)')
src = os.path.join(W, 'src')
with open(os.path.join(src, 'hostz.c'), 'w', encoding='utf-8') as fh:
    fh.write('#include <stdio.h>\nconst char *zlibVersion(void);\n'
             'int main(void){printf("%s\\n", zlibVersion());return 0;}\n')
with open(os.path.join(src, 'evilz.c'), 'w', encoding='utf-8') as fh:
    fh.write('const char *zlibVersion(void){return "EVIL-libz-shadow";}\n')
print(' gcc host:', sh(['gcc', '-o', os.path.join(W, 'host-z'), os.path.join(src, 'hostz.c'),
                        '/usr/lib/libz.so.1', '-Wl,-rpath,$ORIGIN'])[0])
print(' gcc evil:', sh(['gcc', '-shared', '-fPIC', '-Wl,-soname,libz.so.1', '-o',
                        os.path.join(W, 'evil-libz.so.1'), os.path.join(src, 'evilz.c')])[0])
print(' host NEEDED:', [ln.split('[')[1].rstrip(']') for ln in
                        sh(['readelf', '-d', os.path.join(W, 'host-z')])[1].splitlines() if 'NEEDED' in ln])

print('== E1b snapshot a dir WITHOUT libz.so.1, then add a shadowing file')
D = fresh('shadow')
srv = os.path.join(D, 'stub-server')
shutil.copy(os.path.join(W, 'host-z'), srv)
os.chmod(srv, 0o755)
snap, _ = C.server_block(srv)
r = C.live_receipt()
r['server'] = snap
r['argv'][0] = snap['realpath']
rec = C.write_receipt(os.path.join(W, 'e1-snapshot.json'), r)
rc, before, err = sh([srv])
print(' loader before addition (zlibVersion):', before, '| exit', rc, err[:80])
shutil.copy(os.path.join(W, 'evil-libz.so.1'), os.path.join(D, 'libz.so.1'))   # post-snapshot write
rc, after, err = sh([srv])
print(' loader after addition  (zlibVersion):', after, '| exit', rc, err[:80])
print(' snapshot tree members:', sorted(snap['install_tree']), '| tree sha256', snap['install_tree_sha256'][:16])
rc_g, out_g, _ = C.gate(rec, '--expect-install-tree-sha256', snap['install_tree_sha256'])
print(' gate on pre-addition receipt with its own tree pin: exit', rc_g, '|', out_g.splitlines()[0][:100])
post_tree, post_sha = P.install_tree(srv)
print(' re-snapshot after addition: members', sorted(post_tree), '| digest differs:', post_sha != snap['install_tree_sha256'])

print('== E2 non-UTF-8 link keys: Python gate vs a non-Python JSON reader')
links = {'\udcfe': 'missing-target', '\udcff': 'libllama.so.0.7.0'}
r2 = C.live_receipt()
r2['server']['install_links'] = links
r2['server']['install_links_sha256'] = G.install_links_sha(links)
p2 = C.write_receipt(os.path.join(W, 'e2-surrogate-keys.json'), r2)
rc_g, out_g, _ = C.gate(p2, '--require-install-links')
print(' python gate exit', rc_g, '|', out_g.splitlines()[1][:120] if len(out_g.splitlines()) > 1 else out_g[:120])
print(' receipt text (escapes):', [ln.strip() for ln in open(p2, encoding='utf-8') if 'udc' in ln])
rc_j, out_j, err_j = sh(['jq', '-c', '.server.install_links', p2])
print(' jq (jaq 3.1.1) keys/values:', out_j, '| exit', rc_j, err_j[:80])
rc_j2, out_j2, _ = sh(['jq', '-c', '.server.install_links | to_entries | map(.value)', p2])
print(' jq chain values seen by a jq-based check:', out_j2)
node_src = ("const fs=require('fs');const t=fs.readFileSync(process.argv[1],'utf8');"
            "const d=JSON.parse(t).server.install_links;"
            "console.log(JSON.stringify(Object.keys(d).map(k=>[k.charCodeAt(0).toString(16),d[k]])));")
rc_n, out_n, err_n = sh(['node', '-e', node_src, p2])
print(' node JSON.parse keys (code units, value):', out_n, '| exit', rc_n, err_n[:80])

print('== E3 "canonical JSON" portability (RFC 8785 vs producer ensure_ascii)')
m = {'libé.so.0': 'libé-real.so'}
py = P.links_digest(m)
jcs = __import__('hashlib').sha256(
    ('{"libé.so.0":"libé-real.so"}').encode('utf-8')).hexdigest()
print(' producer digest  :', py[:32])
print(' RFC8785-style    :', jcs[:32], '| equal:', py == jcs)
print(' producer text    :', json.dumps(m, sort_keys=True, separators=(',', ':'), ensure_ascii=True))

print('== E4 gate chain-walk cost on long link chains (validate() loops every link)')
for n in (1000, 2000, 4000):
    links_n = {f'h{i}': f'h{i + 1}' for i in range(n)}
    links_n[f'h{n}'] = 'libllama.so.0.7.0'
    tree_n = {'libllama.so.0.7.0': 'a' * 64}
    t0 = time.perf_counter()
    bad = 0
    for name in sorted(links_n):
        if G.link_chain_problem(name, links_n, tree_n):
            bad += 1
    dt = time.perf_counter() - t0
    print(f' n={n:5d} links: chain problems={bad} time={dt:.2f}s', flush=True)
print('done E', flush=True)
