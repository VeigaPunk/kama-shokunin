"""A: canonical-JSON links digest and name-handling experiments (producer+gate
functions, real filesystem, /tmp only). Never launches anything."""
import json
import os
import shutil
import unicodedata

import common as C

P, G, W = C.P, C.G, C.WORK


def newdir(name):
    d = os.path.join(W, 'd-' + name)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    return d


def wfile(path, data=b'stub\n'):
    with open(path, 'wb') as fh:
        fh.write(data)
    os.chmod(path, 0o755)


def show(label, value):
    print(f'{label}: {value}', flush=True)


print('== A1 links_digest injectivity over str->str maps')
a = {'\ud83d\ude00': 'x'}          # two lone surrogates (never produced by fs)
b = {'\U0001F600': 'x'}            # one astral code point (emoji filename)
show(' digest(lone-surrogate-pair key) == digest(astral key)', P.links_digest(a) == P.links_digest(b))
show(' JSON text of both', json.dumps(a, sort_keys=True, separators=(',', ':'), ensure_ascii=True)
     + ' | ' + json.dumps(b, sort_keys=True, separators=(',', ':'), ensure_ascii=True))
show(' gate install_links_sha256 equal', G.install_links_sha(a) == G.install_links_sha(b))
show(' docstring example {"a":"b\\nc -> d"} != {"a":"b","c":"d"}',
     P.links_digest({'a': 'b\nc -> d'}) != P.links_digest({'a': 'b', 'c': 'd'}))
show(' fs decode of CESU bytes ED A0 BD (would be U+D83D)',
     ascii(os.fsdecode(bytes([0xed, 0xa0, 0xbd]))))
show(' DEL / C1 variants give distinct digests',
     len({P.links_digest({'libllama.so.0': 'x'}), P.links_digest({'libllama.so.0\x7f': 'x'}),
          P.links_digest({'libllama.so.0\x9b': 'x'})}))

print('== A2 non-UTF-8 symlink NAME and TARGET in a real directory')
d = newdir('surr')
bd = os.fsencode(d)
srv = os.path.join(d, 'llama-server')
wfile(srv)
wfile(os.path.join(d, 'libllama.so.0.7.0'))
os.symlink(b'libllama.so.0.7.0', os.path.join(bd, b'\xffsoname'))
os.symlink(b'\xfe-dangling', os.path.join(bd, b'libdangle.so'))
tree, tsha = P.install_tree(srv)
links, lsha, probs = P.install_links(srv)
show(' install_tree members (ascii)', [ascii(n) for n in sorted(tree)])
show(' install_links (ascii)', {ascii(k): ascii(v) for k, v in links.items()})
show(' install_links problems', probs)
show(' links JSON (ensure_ascii)', json.dumps(links, sort_keys=True, ensure_ascii=True))
for k in sorted(links):
    show(f' gate chain verdict for {ascii(k)}', G.link_chain_problem(k, links, tree))

print('== A3 non-UTF-8 REGULAR member name')
d3 = newdir('surr-reg')
bd3 = os.fsencode(d3)
srv3 = os.path.join(d3, 'llama-server')
wfile(srv3)
wfile(os.path.join(bd3, b'\xfeimpl.so'))
try:
    P.install_tree(srv3)
    show(' install_tree', 'no exception')
except Exception as exc:  # noqa: BLE001 - we want the exact type
    show(' install_tree raises', f'{type(exc).__name__}: {str(exc)[:100]}')
show(' install_links problems (same dir)', P.install_links(srv3)[2])

print('== A4 Unicode normalization (NFC vs NFD names)')
d4 = newdir('nfc')
srv4 = os.path.join(d4, 'llama-server')
wfile(srv4)
nfc_link = unicodedata.normalize('NFC', 'libé.so.0')
nfd_link = unicodedata.normalize('NFD', 'libé.so.0')
nfc_tgt = unicodedata.normalize('NFC', 'libé-real.so')
nfd_tgt = unicodedata.normalize('NFD', 'libé-real.so')
nfd_only = unicodedata.normalize('NFD', 'libé-only.so')
nfc_miss = unicodedata.normalize('NFC', 'libé-only.so')
wfile(os.path.join(d4, nfc_tgt), b'nfc-target\n')
wfile(os.path.join(d4, nfd_tgt), b'nfd-target\n')
wfile(os.path.join(d4, nfd_only), b'nfd-only\n')
os.symlink(nfc_tgt, os.path.join(d4, nfc_link))
os.symlink(nfd_tgt, os.path.join(d4, nfd_link))
os.symlink(nfc_miss, os.path.join(d4, 'libcross.so'))       # NFC target; only NFD name exists
show(' NFC and NFD link names distinct', nfc_link != nfd_link and os.fsencode(nfc_link) != os.fsencode(nfd_link))
tree4, _ = P.install_tree(srv4)
links4, _, p4 = P.install_links(srv4)
show(' tree members (ascii)', [ascii(n) for n in sorted(tree4)])
show(' links (ascii)', {ascii(k): ascii(v) for k, v in links4.items()})
show(' problems', p4)
show(' gate verdict NFC link', G.link_chain_problem(nfc_link, links4, tree4))
show(' gate verdict NFD link', G.link_chain_problem(nfd_link, links4, tree4))
show(' gate verdict cross-form link (NFC target absent)', G.link_chain_problem('libcross.so', links4, tree4))
show(' kernel: stat(NFC target) exists', os.path.exists(os.path.join(d4, nfc_tgt)))
show(' kernel: stat(cross-form NFC target) exists', os.path.exists(os.path.join(d4, nfc_miss)))

print('== A5 very long link text')
d5 = newdir('long')
srv5 = os.path.join(d5, 'llama-server')
wfile(srv5)
wfile(os.path.join(d5, 'x' * 255), b'long-name-real\n')
for n in (255, 4000, 4095, 4096):
    try:
        os.symlink('t' * n, os.path.join(d5, f'L{n}.so'))
        show(f' symlink target length {n}', 'created')
    except OSError as exc:
        show(f' symlink target length {n}', f'{type(exc).__name__} errno={exc.errno}')
os.symlink('x' * 255, os.path.join(d5, 'y' * 255))
tree5, _ = P.install_tree(srv5)
links5, lsha5, p5 = P.install_links(srv5)
show(' problems', p5)
show(' recorded links', len(links5))
show(' gate verdict 255-byte chain', G.link_chain_problem('y' * 255, links5, tree5))
show(' gate verdict 4000-byte dangling link', G.link_chain_problem('L4000.so', links5, tree5))

print('== A6 control characters and names differing only by controls')
d6 = newdir('ctrl')
srv6 = os.path.join(d6, 'llama-server')
wfile(srv6)
wfile(os.path.join(d6, 'libllama.so.0.7.0'))
for n in ('libllama.so.0\x7f', 'libllama.so.0\x80', 'libllama.so.0\x9b',
          'libllama.so.0\u2028', 'libllama.so.0\x85'):
    os.symlink('libllama.so.0.7.0', os.path.join(d6, n))
links6, _, p6 = P.install_links(srv6)
show(' DEL/C1/U+2028/U+0085 names: problems', p6)
show(' DEL/C1/U+2028/U+0085 names: recorded keys (ascii)', sorted(ascii(k) for k in links6))
os.symlink('libllama.so.0.7.0', os.path.join(d6, 'lib\x1bx.so'))
show(' C0 ESC name problems', P.install_links(srv6)[2])
os.unlink(os.path.join(d6, 'lib\x1bx.so'))
os.mkfifo(os.path.join(d6, 'fifo\x9bname'))
show(' FIFO with U+009B in name: problem text (ascii)',
     [ascii(x) for x in P.install_links(srv6)[2]])
os.unlink(os.path.join(d6, 'fifo\x9bname'))

print('== A7 install_tree text digest: names containing newline/space')
honest = {'libA': 'a' * 64, 'libB': 'b' * 64, 'llama-server': 'c' * 64}
forged = {'libA ' + 'a' * 64 + '\nlibB': 'b' * 64, 'llama-server': 'c' * 64}
show(' honest text', repr(''.join(f'{n} {honest[n]}\n' for n in sorted(honest)))[:80] + '...')
show(' forged text', repr(''.join(f'{n} {forged[n]}\n' for n in sorted(forged)))[:80] + '...')
show(' install_tree_sha256 equal (gate recomputation)', G.install_tree_sha(honest) == G.install_tree_sha(forged))
show(' member counts honest/forged', (len(honest), len(forged)))
print('done A', flush=True)
