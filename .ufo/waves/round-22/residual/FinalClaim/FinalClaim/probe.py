#!/usr/bin/env python3
"""FinalClaim probe: frozen vs current install_tree on real (non-mock) trees.

A. success-path differential: identical (tree, digest) or identical exception type.
B. real-errno refusals (non-root chmod): helper outcome per arm and the
   producer setup block emulation (install_tree -> install_links(tree) ->
   SetupError) without launching anything.
Writes only under a temp dir inside this residual folder; restores modes.
"""
import hashlib, json, os, stat, subprocess, sys, tempfile, types
from pathlib import Path

CLONE = Path(__file__).resolve().parent / 'clone'
PRODUCER = 'tools/kama-llamacpp-live.py'
FROZEN = '10271460cc575fc2280aa831e442726385fc2319'
FROZEN_SHA = 'cec679495591cf2410334dfe08c648e310f23825181dcbae7d13b911c980e023'


def load(src, label):
    m = types.ModuleType('p_' + label)
    m.__file__ = str(CLONE / PRODUCER)
    exec(compile(src, m.__file__, 'exec'), m.__dict__)
    return m


frozen_src = subprocess.run(['git', '-C', str(CLONE), 'show', FROZEN + ':' + PRODUCER],
                            capture_output=True, check=True).stdout
current_src = (CLONE / PRODUCER).read_bytes()
assert hashlib.sha256(frozen_src).hexdigest() == FROZEN_SHA
arms = {'frozen': load(frozen_src, 'frozen'), 'current': load(current_src, 'current')}


def helper(m, server):
    try:
        t, d = m.install_tree(server)
        return {'status': 'returned', 'tree': t, 'digest': d}
    except m.SetupError as e:
        c = e.__cause__
        return {'status': 'refused', 'code': e.code, 'cause': type(c).__name__,
                'cause_errno': getattr(c, 'errno', None)}
    except Exception as e:
        return {'status': 'raised', 'exception': type(e).__name__}


def producer_block(m, server):
    """Lines 1419-1424 of the producer (identity part of setup), no launch."""
    try:
        tree, _ = m.install_tree(server)
        problems = m.install_links(server, tree)[2]
        if problems:
            raise m.SetupError('install-tree-unpinnable:' + ';'.join(problems[:8]))
        return {'status': 'accepted'}
    except m.SetupError as e:
        return {'status': 'refused', 'setup_error': e.code}
    except Exception as e:
        return {'status': 'internal', 'exception': type(e).__name__}


def build(root, name, files, extra=None):
    d = root / name
    d.mkdir()
    for n, b in files.items():
        p = os.path.join(os.fsencode(d), n if isinstance(n, bytes) else n.encode())
        with open(p, 'wb') as fh:
            fh.write(b)
    if extra:
        extra(d)
    return d


base = {'llama-server': b'server\x00', 'lib.so': b'library\xff'}
out = {'python': sys.version.split()[0], 'euid': os.geteuid(),
       'source_sha256': {'frozen': hashlib.sha256(frozen_src).hexdigest(),
                         'current': hashlib.sha256(current_src).hexdigest()},
       'success_differential': [], 'real_errno': []}
work = Path(__file__).resolve().parent / 'tmp'
work.mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(dir=work, prefix='probe-') as tmp:
    root = Path(tmp)
    cases = {
        'regular': (base, None),
        'empty-but-server': ({'llama-server': b''}, None),
        'symlink': (base, lambda d: os.symlink('lib.so', d / 'soname.so')),
        'dangling-symlink': (base, lambda d: os.symlink('gone.so', d / 'x.so')),
        'directory': (base, lambda d: (d / 'licensing').mkdir()),
        'fifo': (base, lambda d: os.mkfifo(d / 'p.fifo')),
        'hardlink': (base, lambda d: os.link(d / 'lib.so', d / 'hard.so')),
        'unicode-space-colon': ({**base, 'libé x:1.so': b'u'}, None),
        'newline-name': ({**base, 'lib\nx.so': b'n'}, None),
        'multichunk-3MiB': ({**base, 'big.so': b'\xab' * (3 << 20) + b'z'}, None),
        'many-200': ({**base, **{f'l{i:03}.so': bytes([i]) for i in range(200)}}, None),
        'non-utf8-name': ({**base, b'\xff.so': b'b'}, None),
    }
    for name, (files, extra) in cases.items():
        d = build(root, name, files, extra)
        res = {a: helper(m, str(d / 'llama-server')) for a, m in arms.items()}
        out['success_differential'].append({
            'case': name, 'equal': res['frozen'] == res['current'],
            'frozen': {k: v for k, v in res['frozen'].items() if k != 'tree'},
            'current': {k: v for k, v in res['current'].items() if k != 'tree'},
            'members': len(res['current'].get('tree') or {})})
    # Real read-only lane directory as an additional positive control.
    real = helper(arms['frozen'], str(CLONE / 'tools' / 'x')), helper(arms['current'], str(CLONE / 'tools' / 'x'))
    out['success_differential'].append({'case': 'clone-tools-dir', 'equal': real[0] == real[1],
                                        'digest': real[1].get('digest'), 'members': len(real[1].get('tree') or {})})

    def errcase(name, setup, restore):
        d = build(root, name, base)
        setup(d)
        try:
            row = {'case': name}
            for a, m in arms.items():
                row[a] = {'helper': {k: v for k, v in helper(m, str(d / 'llama-server')).items() if k != 'tree'},
                          'producer_block': producer_block(m, str(d / 'llama-server'))}
            out['real_errno'].append(row)
        finally:
            restore(d)

    errcase('listdir-EACCES-mode0300', lambda d: os.chmod(d, 0o300), lambda d: os.chmod(d, 0o755))
    errcase('lstat-EACCES-mode0600', lambda d: os.chmod(d, 0o600), lambda d: os.chmod(d, 0o755))
    errcase('read-EACCES-lib-mode0', lambda d: os.chmod(d / 'lib.so', 0), lambda d: os.chmod(d / 'lib.so', 0o644))
    errcase('read-EACCES-colon-name', lambda d: (open(d / 'a:b c.so', 'wb').close(), os.chmod(d / 'a:b c.so', 0)),
            lambda d: os.chmod(d / 'a:b c.so', 0o644))
    errcase('read-EACCES-nonutf8-name',
            lambda d: (open(os.path.join(os.fsencode(d), b'\xfe.so'), 'wb').close(),
                       os.chmod(os.path.join(os.fsencode(d), b'\xfe.so'), 0)),
            lambda d: os.chmod(os.path.join(os.fsencode(d), b'\xfe.so'), 0o644))
json.dump(out, sys.stdout, indent=2, ensure_ascii=True)
print()
ok = all(r['equal'] for r in out['success_differential'])
sys.exit(0 if ok else 1)
