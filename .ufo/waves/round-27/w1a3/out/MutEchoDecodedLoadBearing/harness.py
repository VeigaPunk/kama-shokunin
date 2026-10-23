#!/usr/bin/env python3
"""Offline clause-(f) mutation detector; never calls counter.main or starts a server."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import resource
import sys

LANE = Path('/home/vgpnk/Projects/shokunin/kama-shokunin')
SOURCE = LANE / '.ufo/waves/round-27/count-c1.py'
REGISTRY = LANE / '.ufo/waves/round-26/w2-falsify/out/CriticShortcutRows/shortcut.registry.json'
OUT = LANE / '.ufo/waves/round-27/w1a3/out/MutEchoDecodedLoadBearing'
SCRATCH = Path('/fast/scratch/hyaku/kama-r27c/MutEchoDecodedLoadBearing')
SOURCE_SHA = '49491b80e4f4ed2a85ab822a52f0b1a0fdb1dee53423e3d43b60ee25d1bf2765'
REGISTRY_SHA = '1b78c8aa0423151b9d84f6ad3cef35de7e5260e5ec869fea764ba5dbcc691b91'
LABELS = ('M1', 'M2', 'M3', 'M4', 'M5')


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def save(name: str, result: dict) -> None:
    (OUT / name).write_text(json.dumps(result, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def forbid_live_runtime(event: str, args) -> None:
    if event.startswith(('subprocess.', 'os.exec', 'os.posix_spawn')) or event in {
        'os.system', 'os.fork', 'os.forkpty', 'socket.connect', 'socket.bind', 'socket.getaddrinfo'
    }:
        raise RuntimeError(f'offline detector forbids {event}')


def run() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', required=True, choices=('prepare', 'pristine', 'mutated', 'restored'))
    parser.add_argument('--mutant', choices=LABELS)
    args = parser.parse_args()
    source_bytes = SOURCE.read_bytes()
    registry_bytes = REGISTRY.read_bytes()
    assert sha(source_bytes) == SOURCE_SHA, 'frozen source pin mismatch'
    assert sha(registry_bytes) == REGISTRY_SHA, 'shortcut registry pin mismatch'
    assert sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode
    OUT.mkdir(parents=True, exist_ok=True)
    if args.phase == 'prepare':
        assert args.mutant is None
        SCRATCH.mkdir(parents=True, exist_ok=True)
        copies = {}
        for label in ('pristine', *LABELS):
            path = SCRATCH / f'{label}.py'
            assert not path.exists(), f'refusing to overwrite {path}'
            path.write_bytes(source_bytes)
            copies[str(path)] = sha(path.read_bytes())
        result = {
            'phase': args.phase, 'source_sha256': SOURCE_SHA, 'registry_sha256': REGISTRY_SHA,
            'copies': copies, 'exit_code': 0, 'harness_sha256': sha(Path(__file__).read_bytes()),
            'limits': {name: resource.getrlimit(kind) for name, kind in (
                ('file_size', resource.RLIMIT_FSIZE), ('address_space', resource.RLIMIT_AS),
                ('processes', resource.RLIMIT_NPROC))},
        }
        save('prepare.json', result)
        print(f'prepare copies={len(copies)} sha256={SOURCE_SHA} exit=0')
        return 0

    assert args.mutant is not None
    path = SCRATCH / f'{args.mutant}.py'
    before = path.read_bytes()
    if args.phase != 'mutated':
        assert before == source_bytes, 'non-pristine baseline/restoration bytes'
    else:
        assert before != source_bytes, 'mutation absent'
    sys.addaudithook(forbid_live_runtime)
    name = f'r27_echo_probe_{args.mutant}_{args.phase}'
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.__name__ != '__main__'
    entries = json.loads(registry_bytes)['signatures']
    assert len(entries) == 12
    rows = []
    for entry in entries:
        request = entry['request']
        raw_body = request['body']
        assert isinstance(raw_body, str)
        wire_bytes = raw_body.encode('utf-8')
        body = json.loads(wire_bytes)
        sig = entry['signature']
        assert body['response_format']['type'] == sig
        req = {'method': request['method'], 'path': request['path'],
               'body': body, '_wire_body': wire_bytes.decode('utf-8')}
        surfaces = module.request_surfaces(req)
        catalog = [('path', req['path']), ('raw-body-as-sent', req['_wire_body'])]
        catalog.extend((f'json_strings[{index}]', value)
                       for index, value in enumerate(module.json_strings(body)))
        catalog.extend((('json.dumps(default)', json.dumps(body)),
                        ('json.dumps(ensure_ascii=False)', json.dumps(body, ensure_ascii=False))))
        hits = []
        for index, surface in enumerate(surfaces):
            if module.occurs(sig, surface):
                hits.append({'index': index,
                             'guards': [kind for kind, value in catalog if value == surface],
                             'exact_case_verbatim': sig in surface})
        rows.append({'id': entry['id'], 'signature': sig,
                     'wire_body_sha256': sha(wire_bytes),
                     'raw_body_contains_signature': sig in raw_body,
                     'decoded_value_equals_signature': True,
                     'flagged_echo': bool(hits), 'hits': hits})
    flagged = sum(row['flagged_echo'] for row in rows)
    after = path.read_bytes()
    assert after == before, 'import/detector changed scratch source bytes'
    assert SOURCE.read_bytes() == source_bytes, 'lane source changed during detector'
    assert REGISTRY.read_bytes() == registry_bytes, 'registry changed during detector'
    exit_code = 0 if flagged == 12 else 1
    result = {
        'mutant': args.mutant, 'phase': args.phase, 'counter_path': str(path),
        'counter_sha256_before': sha(before), 'counter_sha256_after': sha(after),
        'lane_source_sha256': SOURCE_SHA, 'registry_sha256': REGISTRY_SHA,
        'harness_sha256': sha(Path(__file__).read_bytes()),
        'adapter': 'Decode the R26 wire-body string once into an R27 body object; retain exact UTF-8 wire body as _wire_body for M1. No static_checks/main/live validation.',
        'detector': 'any(module.occurs(signature, surface) for surface in module.request_surfaces(request)); require 12/12 echoes',
        'audit': 'Process launch/exec/fork and network connect/bind/lookup forbidden; no forbidden event occurred.',
        'rows': rows, 'flagged': flagged, 'total': len(rows), 'exit_code': exit_code,
    }
    save(f'{args.mutant}.{args.phase}.json', result)
    print(f'{args.mutant} {args.phase} flagged={flagged}/12 exit={exit_code} sha256={sha(before)}')
    print(' '.join(f"{row['id']}={'echo' if row['flagged_echo'] else 'MISSED'}" for row in rows))
    return exit_code


if __name__ == '__main__':
    raise SystemExit(run())
