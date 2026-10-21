#!/usr/bin/env python3
# Offline probe of the C2 producer diff (install_links). Scratch-only.
# Never launches llama-server or the live harness; only reads/writes temp dirs
# under SCRATCH and reads the real install tree (read-only).
import copy
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
LANE = Path(os.environ['LANE'])
SCRATCH = Path(os.environ['SCRATCH'])
EMPTY = hashlib.sha256(b'').hexdigest()
R20_TREE_PIN = ('6c216313a88d71b141bc62f684b8f95c040710ff050801b13521861826785a2c')
PRODUCER = LANE / 'tools' / 'kama-llamacpp-live.py'
GATE = LANE / 'tests' / 'llamacpp-live' / 'check-receipt.py'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


prod = load('kama_producer', PRODUCER)
gate = load('kama_gate', GATE)
print('python', sys.version.split()[0])


def mkserver(d):
    d.mkdir(parents=True, exist_ok=True)
    s = d / 'llama-server'
    s.write_bytes(b'\x7fELF-probe')
    os.chmod(s, 0o755)
    return s


def run(label, fn):
    try:
        print(label, '->', fn())
    except BaseException as exc:  # observe every outcome, never hide
        print(label, '-> RAISED', type(exc).__name__, str(exc)[:100])


def with_patched(attr, names, exc_factory, fn):
    real = getattr(os, attr)

    def flaky(p, *a, **k):
        if os.path.basename(str(p)) in names:
            raise exc_factory(str(p))
        return real(p, *a, **k)
    setattr(os, attr, flaky)
    try:
        return fn()
    finally:
        setattr(os, attr, real)


def lstat_enoent(names, fn):
    return with_patched('lstat', names,
                        lambda p: FileNotFoundError(2, 'emulated unlink race', p), fn)


def readlink_eio(names, fn):
    return with_patched('readlink', names,
                        lambda p: OSError(5, 'emulated readlink EIO', p), fn)


def gate_cli(path, extra=()):
    proc = subprocess.run(
        [sys.executable, '-B', str(GATE), str(path), *extra],
        capture_output=True, text=True)
    text = (proc.stdout + proc.stderr).strip().splitlines()
    return proc.returncode, (text[0] if text else '')


root = Path(tempfile.mkdtemp(prefix='probe-', dir=SCRATCH))
try:
    # E1: normal soname chain, gate recomputation and chain rule
    print('== E1 normal chain')
    d = root / 'e1'
    s = mkserver(d)
    (d / 'libllama.so.0.7.0').write_bytes(b'L')
    os.symlink('libllama.so.0.7.0', d / 'libllama.so.0')
    os.symlink('libllama.so.0', d / 'libllama.so')
    tree, tsha = prod.install_tree(str(s))
    links, lsha = prod.install_links(str(s))
    print('E1 tree_members', sorted(tree))
    print('E1 links', links)
    print('E1 links_sha', lsha)
    print('E1 gate_recompute_equal', lsha == gate.install_links_sha(links))
    print('E1 chain libllama.so', gate.link_chain_problem('libllama.so', links, tree))
    print('E1 chain libllama.so.0', gate.link_chain_problem('libllama.so.0', links, tree))

    # E2: no symlinks -> {} and sha256('')
    print('== E2 no symlinks')
    d2 = root / 'e2'
    s2 = mkserver(d2)
    run('E2 install_links', lambda: prod.install_links(str(s2)))
    print('E2 EMPTY', EMPTY)

    # E2b: listing denied (-wx directory)
    print('== E2b listing denied')
    d2b = root / 'e2b'
    s2b = mkserver(d2b)
    os.chmod(d2b, 0o311)
    try:
        run('E2b install_tree', lambda: prod.install_tree(str(s2b)))
        run('E2b install_links', lambda: prod.install_links(str(s2b)))
    finally:
        os.chmod(d2b, 0o755)

    # E3: per-entry OSError inside the link scan -> silent continue
    print('== E3 per-entry OSError (emulated race / EIO)')
    run('E3a lstat ENOENT on libllama.so.0',
        lambda: (lambda r: (r[0], r[1], r[1] == lsha))(
            lstat_enoent({'libllama.so.0'}, lambda: prod.install_links(str(s)))))
    run('E3a gate chain libllama.so after omission',
        lambda: gate.link_chain_problem(
            'libllama.so',
            lstat_enoent({'libllama.so.0'}, lambda: prod.install_links(str(s)))[0],
            tree))
    run('E3b lstat ENOENT on both chain links',
        lambda: (lambda r: (r[0], r[1], r[1] == EMPTY))(
            lstat_enoent({'libllama.so.0', 'libllama.so'},
                         lambda: prod.install_links(str(s)))))
    run('E3c readlink EIO on libllama.so',
        lambda: (lambda r: (r[0], r[1]))(
            readlink_eio({'libllama.so'}, lambda: prod.install_links(str(s)))))

    # E4: non-UTF-8 bytes in names/targets
    print('== E4 non-UTF-8 bytes')
    d4a = root / 'e4a'
    s4a = mkserver(d4a)
    os.symlink('llama-server', d4a / os.fsdecode(b'lib\xff.so.0'))
    run('E4a install_tree (non-UTF-8 symlink NAME)', lambda: prod.install_tree(str(s4a))[1])
    run('E4a install_links (non-UTF-8 symlink NAME)', lambda: prod.install_links(str(s4a)))

    d4b = root / 'e4b'
    s4b = mkserver(d4b)
    os.symlink(os.fsdecode(b'\xfe.so.0'), d4b / 'lnk.so')
    run('E4b install_tree (non-UTF-8 symlink TARGET)', lambda: prod.install_tree(str(s4b))[1])
    run('E4b install_links (non-UTF-8 symlink TARGET)', lambda: prod.install_links(str(s4b)))

    d4c = root / 'e4c'
    s4c = mkserver(d4c)
    (d4c / os.fsdecode(b'lib\xfe.bin')).write_bytes(b'R')
    run('E4c install_tree (non-UTF-8 REGULAR name; pre-existing)',
        lambda: prod.install_tree(str(s4c))[1])

    # E5: digest non-injectivity (' -> ' inside names/targets)
    print('== E5 digest collision')
    dA = root / 'e5A'
    sA = mkserver(dA)
    (dA / 'c').write_bytes(b'C')
    (dA / 'b -> c').write_bytes(b'BC')
    os.symlink('b -> c', dA / 'a')
    dB = root / 'e5B'
    sB = mkserver(dB)
    (dB / 'c').write_bytes(b'C')
    (dB / 'b -> c').write_bytes(b'BC')
    os.symlink('c', dB / 'a -> b')
    tA, tshaA = prod.install_tree(str(sA))
    lA, lshaA = prod.install_links(str(sA))
    tB, tshaB = prod.install_tree(str(sB))
    lB, lshaB = prod.install_links(str(sB))
    print('E5 links_A', lA)
    print('E5 links_B', lB)
    print('E5 maps_equal', lA == lB, '| tree_sha_equal', tshaA == tshaB,
          '| links_sha_equal', lshaA == lshaB, lshaA)
    print('E5 gate chain A(a)', gate.link_chain_problem('a', lA, tA),
          '| B(a -> b)', gate.link_chain_problem('a -> b', lB, tB))

    # E7: real install tree, read-only
    print('== E7 real tree (read-only)')
    real = Path.home() / '.local/opt/llama-b11755/llama-server'
    rt, rts = prod.install_tree(str(real))
    rl, rls = prod.install_links(str(real))
    print('E7 regular_members', len(rt), 'install_tree_sha256', rts,
          'equals_R20_pin', rts == R20_TREE_PIN)
    print('E7 links', len(rl), json.dumps(rl, sort_keys=True))
    print('E7 links_sha', rls, 'gate_recompute_equal', rls == gate.install_links_sha(rl))
    print('E7 chain_problems', {n: gate.link_chain_problem(n, rl, rt) for n in sorted(rl)})

    # E8: source_binding contract (producer vs gate pins)
    print('== E8 source_binding')
    sb = prod.source_bindings()
    pins = gate.SOURCE_BINDING_EXPECTED
    print('E8 counts producer', len(sb), 'gate', len(pins))
    for i, (b, spec) in enumerate(zip(sb, pins)):
        check, row, path, lines, fsha, ssha = spec
        same = (b['check'], b['row'], b['path'], b['lines'],
                b['file_sha256'], b['span_sha256']) == (check, row, path, lines, fsha, ssha)
        span_ok = (hashlib.sha256(b['span_text'].encode('utf-8')).hexdigest()
                   == b['span_sha256']
                   and len(b['span_text'].splitlines(keepends=True))
                   == b['lines'][1] - b['lines'][0] + 1)
        print('E8', i, b['check'], 'matches_gate_pin', same, 'span_recomputes', span_ok)

    # E9: receipt-level acceptance by the gate (v3 fixture from the gate's own builder)
    print('== E9 gate acceptance of link-field variants (CLI)')
    R = gate._selftest_receipt_v3()
    pin = R['server']['install_links_sha256']
    print('E9 fixture install_links', R['server']['install_links'])

    def dump(name, obj):
        p = root / name
        p.write_text(json.dumps(obj), encoding='utf-8')
        return p

    S = copy.deepcopy(R)
    del S['server']['install_links']
    del S['server']['install_links_sha256']
    F = copy.deepcopy(R)
    F['server']['install_links'] = {}
    F['server']['install_links_sha256'] = EMPTY
    N = copy.deepcopy(R)
    N['server']['install_links'] = {}
    N['server']['install_links_sha256'] = None
    variants = [
        ('valid-as-emitted', dump('valid.json', R), []),
        ('links-stripped', dump('stripped.json', S), []),
        ('links-stripped + pin', dump('stripped.json', S), ['--expect-install-links-sha256', pin]),
        ('links-emptied to sha(\'\')', dump('emptied.json', F), []),
        ('links-emptied to sha(\'\') + pin', dump('emptied.json', F), ['--expect-install-links-sha256', pin]),
        ('links {} + null digest', dump('nulldigest.json', N), []),
        ('links {} + null digest + pin', dump('nulldigest.json', N), ['--expect-install-links-sha256', pin]),
    ]
    for label, path, extra in variants:
        rc, first = gate_cli(path, ['--require-schema', 'v3', *extra])
        print('E9', label, '-> exit', rc, '|', first[:140])

    # E10: does the producer's own --selftest exercise install_links?
    print('== E10 producer --selftest coverage (mutant copy in scratch)')
    mut = SCRATCH / 'mut'
    (mut / 'tools').mkdir(parents=True, exist_ok=True)
    (mut / 'registry').mkdir(parents=True, exist_ok=True)
    shutil.copy(LANE / 'registry' / 'endpoint-consumers.tsv',
                mut / 'registry' / 'endpoint-consumers.tsv')
    src = PRODUCER.read_text(encoding='utf-8')
    needle = 'def install_links(server_real):\n'
    assert src.count(needle) == 1, 'needle not unique'
    mutant = mut / 'tools' / 'kama-llamacpp-live.py'
    mutant.write_text(src.replace(
        needle, needle + "    raise RuntimeError('mutant: install_links disabled')\n"),
        encoding='utf-8')
    proc = subprocess.run([sys.executable, '-B', str(mutant), '--selftest'],
                          capture_output=True, text=True)
    print('E10 mutant --selftest exit', proc.returncode, '|', proc.stdout.strip(),
          proc.stderr.strip()[:120])
    mod = load('kama_mutant', mutant)
    run('E10 mutant direct install_links() call', lambda: mod.install_links(str(s)))
    shutil.rmtree(mut, ignore_errors=True)

    # E11: unrelated absolute symlink in a shared directory
    print('== E11 absolute target')
    print('E11 chain x -> /usr/share/x',
          gate.link_chain_problem('x', {'x': '/usr/share/x'}, {'llama-server': 'h'}))
finally:
    shutil.rmtree(root, ignore_errors=True)
    print('cleanup root removed:', not root.exists())
