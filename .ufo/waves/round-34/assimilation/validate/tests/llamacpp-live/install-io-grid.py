#!/usr/bin/env python3
"""Finite install_tree I/O completeness gate (no server/network/host-tree writes).

--arm frozen|current|both --json: 0 all selected properties hold, 1 a property
fails, 2 could-not-evaluate. Frozen is expected red. --selftest invokes this CLI
on isolated producer fixtures, including an always-refuse negative control.
Source: S075/S076; the fail-closed rule is lane policy, not Python's policy.
"""
import argparse
from contextlib import ExitStack
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import types
from unittest.mock import patch

LANE = Path(__file__).resolve().parents[2]
PRODUCER = 'tools/kama-llamacpp-live.py'
FROZEN = '10271460cc575fc2280aa831e442726385fc2319'
FROZEN_SHA = 'cec679495591cf2410334dfe08c648e310f23825181dcbae7d13b911c980e023'
ERRORS = {'permission': PermissionError, 'missing': FileNotFoundError,
          'io': OSError, 'isdir': IsADirectoryError}
# Fixed finite population and oracle, independent of producer comparisons.
FAULTS = ([('list-' + e, 'listdir', None, e) for e in ('permission', 'missing', 'io')]
          + [('stat-' + n + '-' + e, 'lstat', n, e)
             for n in ('llama-server', 'lib.so')
             for e in ('permission', 'missing', 'io')]
          + [('read-' + n + '-' + e, 'read', n, e)
             for n in ('llama-server', 'lib.so')
             for e in ('permission', 'missing', 'isdir', 'io')]
          + [('late-read-lib.so', 'late-read', 'lib.so', 'io')])
PROPAGATION = tuple((site + '-' + error, site, error)
                    for site in ('listdir', 'lstat', 'read')
                    for error in ('type-error', 'interrupt'))
CONTROLS = ('regular', 'empty', 'symlink', 'directory', 'hardlink', 'unicode',
            'reversed-order', 'fifo') + tuple(row[0] for row in PROPAGATION)
BODY = {'llama-server': b'server\x00', 'lib.so': b'library\xff'}


class InjectedInterrupt(KeyboardInterrupt):
    """Distinguish the fixture signal from an operator's real Ctrl-C."""


def load(source, label):
    module = types.ModuleType('producer_' + label)
    module.__file__ = str(LANE / PRODUCER)
    exec(compile(source, module.__file__, 'exec'), module.__dict__)
    return module


def expected_tree(body):
    tree = {n: hashlib.sha256(b).hexdigest() for n, b in body.items()}
    digest = hashlib.sha256(''.join(f'{n} {tree[n]}\n' for n in sorted(tree)).encode()).hexdigest()
    return tree, digest


def observe(module, folder, stage=None, member=None, error='io', reverse=False):
    original_list, original_stat = module.os.listdir, module.os.lstat
    original_hash = module.sha256_file
    calls = {'fault': 0, 'late_chunks': 0, 'late_bytes': 0}
    fault = (InjectedInterrupt if error == 'interrupt' else
             TypeError if error == 'type-error' else ERRORS[error])
    injected = fault('injected fixture failure')

    def listing(path):
        if stage == 'listdir' and os.fspath(path) == os.fspath(folder):
            calls['fault'] += 1
            raise injected
        result = original_list(path)
        return sorted(result, reverse=True) if reverse else result

    def stated(path, *args, **kwargs):
        if stage == 'lstat' and os.fspath(path) == os.fspath(folder / member):
            calls['fault'] += 1
            raise injected
        return original_stat(path, *args, **kwargs)

    def hashed(path):
        if stage == 'read' and os.fspath(path) == os.fspath(folder / member):
            calls['fault'] += 1
            raise injected
        return original_hash(path)

    builtin_open = open

    class LateReader:
        def __init__(self, stream):
            self.stream = stream
            self.reads = 0

        def __enter__(self):
            return self

        def __exit__(self, *args):
            self.stream.close()

        def read(self, size):
            self.reads += 1
            if self.reads == 1:
                calls['late_chunks'] += 1
                chunk = self.stream.read(size)
                calls['late_bytes'] = len(chunk)
                return chunk
            calls['fault'] += 1
            raise injected

    def opened(path, *args, **kwargs):
        stream = builtin_open(path, *args, **kwargs)
        if stage == 'late-read' and os.fspath(path) == os.fspath(folder / member):
            return LateReader(stream)
        return stream

    with ExitStack() as stack:
        stack.enter_context(patch.object(module.os, 'listdir', listing))
        stack.enter_context(patch.object(module.os, 'lstat', stated))
        stack.enter_context(patch.object(module, 'sha256_file', hashed))
        stack.enter_context(patch.object(module, 'open', opened, create=True))
        try:
            tree, digest = module.install_tree(str(folder / 'llama-server'))
            result = {'status': 'returned', 'tree': tree, 'digest': digest}
        except module.SetupError as exc:
            result = {'status': 'refused', 'reason': exc.code,
                      'cause_is_fault': exc.__cause__ is injected}
        except (InjectedInterrupt, Exception) as exc:
            result = {'status': 'raised', 'exception': type(exc).__name__,
                      'same_exception': exc is injected}
    result.update(calls)
    if result['status'] == 'returned' and hasattr(module, 'install_links'):
        result['paired_problems'] = module.install_links(
            str(folder / 'llama-server'), result['tree'])[2]
    return result


def evaluate(module):
    rows = []
    with tempfile.TemporaryDirectory(prefix='kama-install-io-') as temp:
        root = Path(temp)
        for name, stage, member, error in FAULTS:
            folder = root / name
            folder.mkdir()
            for n, body in BODY.items():
                data = body + b'x' * (1 << 20) if stage == 'late-read' and n == member else body
                (folder / n).write_bytes(data)
            result = observe(module, folder, stage, member, error)
            if result['fault'] != 1:
                raise RuntimeError('fault_not_reached:' + name)
            expected_stage = 'read' if stage == 'late-read' else stage
            expected_reason = ('install-tree-unpinnable:' + expected_stage
                               + (':' + repr(member) if member else ''))
            good = (result['status'] == 'refused'
                    and result.get('reason', '').startswith(expected_reason + ':')
                    and result.get('cause_is_fault') is True
                    and result['fault'] == 1
                    and (stage != 'late-read' or
                         (result['late_chunks'] == 1 and result['late_bytes'] == 1 << 20)))
            rows.append(dict(case=name, kind='fault', expected='refused',
                             observed=result, passed=good))
        for name in CONTROLS:
            folder = root / ('control-' + name)
            folder.mkdir()
            body = {} if name == 'empty' else dict(BODY)
            if name == 'unicode':
                body['libé.so'] = b'unicode'
            for n, data in body.items():
                (folder / n).write_bytes(data)
            if name == 'symlink':
                os.symlink('lib.so', folder / 'soname.so')
            if name == 'directory':
                (folder / 'licensing').mkdir()
            if name == 'hardlink':
                os.link(folder / 'lib.so', folder / 'hard.so')
                body['hard.so'] = BODY['lib.so']
            if name == 'fifo':
                os.mkfifo(folder / 'ignored.fifo')
            propagation = next((r for r in PROPAGATION if r[0] == name), None)
            stage, error = (propagation[1], propagation[2]) if propagation else (None, 'io')
            result = observe(module, folder, stage, 'lib.so', error,
                             reverse=name == 'reversed-order')
            if propagation:
                expected = 'TypeError' if error == 'type-error' else 'InjectedInterrupt'
                good = (result['status'] == 'raised'
                        and result.get('exception') == expected
                        and result.get('same_exception') is True
                        and result['fault'] == 1)
            else:
                expected = 'complete-map-and-digest'
                tree, digest = expected_tree(body)
                good = (result['status'] == 'returned' and result['tree'] == tree
                        and result['digest'] == digest and result['fault'] == 0)
            rows.append(dict(case=name, kind='control', expected=expected,
                             observed=result, passed=good))
    faults = [r for r in rows if r['kind'] == 'fault']
    return {'faults': len(FAULTS), 'refused': sum(r['passed'] for r in faults),
            'null_results': sum(r['observed'].get('status') == 'returned'
                                and r['observed'].get('digest') is None for r in faults),
            'partial_digests': sum(r['observed'].get('status') == 'returned'
                                  and r['observed'].get('digest') is not None for r in faults),
            'paired_refusals': sum(bool(r['observed'].get('paired_problems')) for r in faults),
            'controls': len(CONTROLS), 'controls_passed': sum(r['passed'] for r in rows if r['kind'] == 'control'),
            'violations': sum(not r['passed'] for r in rows), 'rows': rows}


def frozen_source():
    env = {'PATH': os.defpath, 'GIT_CONFIG_NOSYSTEM': '1',
           'GIT_CONFIG_GLOBAL': os.devnull, 'GIT_OPTIONAL_LOCKS': '0',
           'GIT_NO_REPLACE_OBJECTS': '1'}
    proc = subprocess.run(['git', '-C', str(LANE), 'show', FROZEN + ':' + PRODUCER],
                          capture_output=True, env=env, timeout=60)
    if proc.returncode or hashlib.sha256(proc.stdout).hexdigest() != FROZEN_SHA:
        raise RuntimeError('frozen_source_unavailable_or_tampered')
    return proc.stdout


def selftest():
    # Each fixture runs through this gate CLI, not only the internal evaluator.
    fixed = '''class SetupError(Exception):
    def __init__(self, code): self.code = code
import os, stat, hashlib

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''): h.update(chunk)
    return h.hexdigest()

def install_tree(server):
    tree = {}
    directory = os.path.dirname(server)
    try: entries = sorted(os.listdir(directory))
    except OSError as exc: raise SetupError('install-tree-unpinnable:listdir:' + str(exc)) from exc
    for name in entries:
        full = os.path.join(directory, name)
        try: mode = os.lstat(full).st_mode
        except OSError as exc: raise SetupError('install-tree-unpinnable:lstat:' + repr(name) + ':' + str(exc)) from exc
        if not stat.S_ISREG(mode): continue
        try: tree[name] = sha256_file(full)
        except OSError as exc: raise SetupError('install-tree-unpinnable:read:' + repr(name) + ':' + str(exc)) from exc
    digest = hashlib.sha256(''.join(f'{n} {tree[n]}\\n' for n in sorted(tree)).encode()).hexdigest()
    return tree, digest
'''
    fixtures = [ ('complete', fixed, 0, 'clean'),
                 ('always-refuse', fixed + "\ndef install_tree(server): raise SetupError('install-tree-unpinnable:listdir:fixture')\n", 2, 'could-not-evaluate'),
                 ('always-empty', fixed + "\ndef install_tree(server): return {}, None\n", 2, 'could-not-evaluate'),
                 ('list-refusal-deleted', fixed.replace("except OSError as exc: raise SetupError('install-tree-unpinnable:listdir:' + str(exc)) from exc", "except OSError: return {}, None"), 1, 'incomplete-install-identity'),
                 ('stat-refusal-deleted', fixed.replace("except OSError as exc: raise SetupError('install-tree-unpinnable:lstat:' + repr(name) + ':' + str(exc)) from exc", "except OSError: continue"), 1, 'incomplete-install-identity'),
                 ('read-refusal-deleted', fixed.replace("except OSError as exc: raise SetupError('install-tree-unpinnable:read:' + repr(name) + ':' + str(exc)) from exc", "except OSError: continue"), 1, 'incomplete-install-identity'),
                 ('broad-exception', fixed.replace('except OSError as exc:', 'except Exception as exc:'), 1, 'incomplete-install-identity'),
                 ('broad-baseexception', fixed.replace('except OSError as exc:', 'except BaseException as exc:'), 1, 'incomplete-install-identity') ]
    failed = []
    with tempfile.TemporaryDirectory(prefix='kama-install-io-selftest-') as temp:
        for name, source, code, finding in fixtures:
            path = Path(temp) / (name + '.py')
            path.write_text(source)
            proc = subprocess.run([sys.executable, __file__, '--arm', 'current', '--current-source', str(path), '--json'],
                                  capture_output=True, text=True, timeout=60)
            doc = json.loads(proc.stdout)
            good = proc.returncode == code and doc['finding_id'] == finding
            if not good:
                failed.append(name)
            print(f'{name}: exit={proc.returncode} finding={doc["finding_id"]} expected={code}/{finding} pass={good}')
    print(f'selftest cases={len(fixtures)} failures={len(failed)}')
    return int(bool(failed))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--arm', choices=('frozen', 'current', 'both'), default='both')
    parser.add_argument('--current-source', type=Path, default=LANE / PRODUCER)
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--selftest', action='store_true')
    args = parser.parse_args()
    try:
        if args.selftest:
            return selftest()
        selected = ('frozen', 'current') if args.arm == 'both' else (args.arm,)
        arms, digests = {}, {}
        for arm in selected:
            source = frozen_source() if arm == 'frozen' else args.current_source.read_bytes()
            digests[arm] = hashlib.sha256(source).hexdigest()
            arms[arm] = evaluate(load(source, arm))
        good = all(v['violations'] == 0 for v in arms.values())
        doc = {'finding_id': 'clean' if good else 'incomplete-install-identity',
               'frozen_revision': FROZEN, 'source_sha256': digests,
               'population_sha256': hashlib.sha256(json.dumps([FAULTS, CONTROLS], separators=(',', ':')).encode()).hexdigest(),
               'arms': arms}
        print(json.dumps(doc, indent=2) if args.json else json.dumps({k: v for k, v in doc.items() if k != 'arms'}) + '\n' + '\n'.join(f'{a}: faults={v["faults"]} refused={v["refused"]} controls={v["controls_passed"]}/{v["controls"]} violations={v["violations"]}' for a, v in arms.items()))
        return 0 if good else 1
    except (OSError, RuntimeError, ValueError, SyntaxError, AttributeError,
            TypeError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({'finding_id': 'could-not-evaluate', 'reason': str(exc)}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
