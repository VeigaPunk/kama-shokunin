#!/usr/bin/env python3
"""Bounded offline replay of the frozen clause-(h) loop; never imports the counter."""
import argparse
import ast
import copy
import hashlib
import json
from pathlib import Path
import sys
import textwrap

LANE = Path('/home/vgpnk/Projects/shokunin/kama-shokunin')
OUT = LANE / '.ufo/waves/round-27/w1a3/out/MutFrameLoadBearing'
SCRATCH = Path('/fast/scratch/hyaku/kama-r27c/MutFrameLoadBearing')
COUNTER = LANE / '.ufo/waves/round-27/count-c1.py'
EVIDENCE = LANE / '.ufo/waves/round-26/w2-falsify/out/CriticShortcutRows'
INPUTS = {
    'counter': (COUNTER, '49491b80e4f4ed2a85ab822a52f0b1a0fdb1dee53423e3d43b60ee25d1bf2765'),
    'registry': (EVIDENCE / 'shortcut.registry.json', '1b78c8aa0423151b9d84f6ad3cef35de7e5260e5ec869fea764ba5dbcc691b91'),
    'receipt': (EVIDENCE / 'shortcut.receipt.json', '6020a2c39cf698860f64216754925ed623c7225c47871a1644e0c8e6d3d7ac19'),
}
MODULE = SCRATCH / 'clause_h.py'
FIXTURE = OUT / 'rows.json'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def input_hashes():
    result = {}
    for name, (path, expected) in INPUTS.items():
        actual = sha(path.read_bytes())
        if actual != expected:
            raise RuntimeError(f'{name}: frozen input hash changed: {actual}')
        result[name] = {'path': str(path), 'sha256': actual}
    return result


def prepare():
    hashes = input_hashes()
    registry = json.loads(INPUTS['registry'][0].read_text(encoding='utf-8'))
    receipt = json.loads(INPUTS['receipt'][0].read_text(encoding='utf-8'))
    observed = {r['id']: r for r in receipt['rows']}
    entries = registry['signatures']
    assert len(entries) == len(observed) == 12
    rows, attribution = [], []
    for n, entry in enumerate(entries, 1):
        obs = observed[entry['id']]
        sig = entry['signature']
        excerpt = obs['observed']['channel_excerpt']
        message = json.loads(excerpt)['error']['message']
        request = copy.deepcopy(entry['request'])
        assert obs['signature'] == sig and obs['observed']['status'] == 400
        assert sig in message
        assert sig not in request['body']
        assert json.loads(request['body'])['response_format']['type'] == sig
        rows.append({
            'id': entry['id'], 'why': [],
            'entry': {
                'signature': sig, 'request': request,
                'source': {'file': entry['source']['file'], 'line': 10000 + n,
                           'row': f'FRAME-SYNTH-{n:02d}'},
                '_next': f'synthetic distinct next action {n:02d}',
            },
            'live': {'message': message},
        })
        attribution.append({
            'id': entry['id'], 'original_source': entry['source'],
            'recorded_channel_sha256': obs['observed']['channel_sha256'],
            'excerpt_sha256': sha(excerpt.encode('utf-8')),
            'excerpt_matches_recorded_hash': sha(excerpt.encode('utf-8')) == obs['observed']['channel_sha256'],
        })
    assert len({r['entry']['_next'] for r in rows}) == 12
    assert len({(r['entry']['source']['file'], r['entry']['source']['line']) for r in rows}) == 12
    assert len({r['entry']['source']['row'] for r in rows}) == 12
    assert len({json.dumps(r['entry']['request'], sort_keys=True) for r in rows}) == 12
    pairs = [(a, b) for i, a in enumerate(rows) for b in rows[i + 1:]]
    substring_pairs = sum(a['entry']['signature'] in b['entry']['signature'] or
                          b['entry']['signature'] in a['entry']['signature'] for a, b in pairs)
    shared_pairs = sum(a['entry']['signature'] in b['live']['message'] or
                       b['entry']['signature'] in a['live']['message'] for a, b in pairs)
    frames = sorted({r['live']['message'].replace(r['entry']['signature'], '\0').lower() for r in rows})
    raw_loop = COUNTER.read_text(encoding='utf-8').splitlines(keepends=True)[690:722]
    extracted = ''.join(raw_loop)
    assert extracted.startswith('        counted, seen = [], []\n')
    assert extracted.endswith('                counted.append(r["id"])\n')
    module = ('import json\n\n\ndef count_rows(rows):\n' +
              textwrap.indent(textwrap.dedent(extracted), '    ') +
              '    return counted\n')
    MODULE.write_text(module, encoding='utf-8')
    (OUT / 'clause-h.extracted.txt').write_text(extracted, encoding='utf-8')
    (OUT / 'clause_h.pristine.py').write_text(module, encoding='utf-8')
    dump(FIXTURE, rows)
    preparation = {
        'inputs': hashes, 'extracted_counter_lines_inclusive': [691, 722],
        'module_path': str(MODULE), 'pristine_module_sha256': sha(module.encode('utf-8')),
        'fixture_path': str(FIXTURE), 'fixture_sha256': sha(FIXTURE.read_bytes()),
        'rows': 12, 'pair_count': len(pairs), 'substring_pairs': substring_pairs,
        'shared_message_pairs': shared_pairs, 'distinct_frames': len(frames), 'frames': frames,
        'attribution': attribution,
        'scope': 'clause h only; all rows start with why=[]; clauses a-g, including f, are not evaluated',
    }
    dump(OUT / 'preparation.json', preparation)
    print(json.dumps(preparation, sort_keys=True))
    return 0


class OnlyReason(ast.NodeTransformer):
    """Disable other h branches in memory for requested single-rule controls."""
    def __init__(self, reason):
        self.reason = reason
        self.disabled = []

    def visit_If(self, node):
        self.generic_visit(node)
        if len(node.body) == 1 and isinstance(node.body[0], ast.Assign):
            assignment = node.body[0]
            if (len(assignment.targets) == 1 and isinstance(assignment.targets[0], ast.Name)
                    and assignment.targets[0].id == 'clash' and isinstance(assignment.value, ast.Constant)
                    and isinstance(assignment.value.value, str) and assignment.value.value.startswith('h:')
                    and assignment.value.value != self.reason):
                self.disabled.append(assignment.value.value)
                node.test = ast.copy_location(ast.Constant(value=False), node.test)
        return node


def detect(args):
    hashes = input_hashes()
    raw = MODULE.read_bytes()
    fixture_raw = FIXTURE.read_bytes()
    preparation = json.loads((OUT / 'preparation.json').read_text(encoding='utf-8'))
    assert sha(fixture_raw) == preparation['fixture_sha256']
    rows = json.loads(fixture_raw)
    tree = ast.parse(raw, filename=str(MODULE))
    disabled = []
    if args.variant != 'full':
        reason = {'shared-only': 'h:shared-message', 'frame-only': 'h:same-message-frame'}[args.variant]
        transformer = OnlyReason(reason)
        tree = ast.fix_missing_locations(transformer.visit(tree))
        disabled = sorted(transformer.disabled)
        assert len(disabled) == 6
    namespace = {}
    exec(compile(tree, str(MODULE), 'exec'), namespace)
    counted = namespace['count_rows'](rows)
    exit_code = 0 if len(counted) == args.expect else 1
    reasons = {}
    for row in rows:
        for reason in row['why']:
            reasons[reason] = reasons.get(reason, 0) + 1
    result = {
        'label': args.label, 'variant': args.variant, 'survivors': len(counted),
        'registered': len(rows), 'counted_ids': counted, 'rejections': reasons,
        'rows': [{'id': row['id'], 'why': row['why']} for row in rows],
        'detector': 'survivor count equals expected', 'expected_survivors': args.expect,
        'detector_exit_code': exit_code, 'module_sha256': sha(raw),
        'fixture_sha256': sha(fixture_raw), 'harness_sha256': sha(Path(__file__).read_bytes()),
        'disabled_h_branches_in_memory': disabled, 'inputs_after': hashes,
    }
    dump(OUT / f'{args.label}.json', result)
    (OUT / f'{args.label}.module.py').write_bytes(raw)
    line = (f'{args.label}: variant={args.variant} survivors={len(counted)}/{len(rows)} '
            f'expected={args.expect} detector_exit={exit_code} '
            f'module_sha256={sha(raw)}\n' +
            'counted_ids=' + ','.join(counted) + '\n' +
            'rejections=' + json.dumps(reasons, sort_keys=True) + '\n')
    error = '' if exit_code == 0 else f'DETECTOR FAIL: expected {args.expect} survivors; observed {len(counted)}\n'
    (OUT / f'{args.label}.stdout').write_text(line, encoding='utf-8')
    (OUT / f'{args.label}.stderr').write_text(error, encoding='utf-8')
    (OUT / f'{args.label}.exit').write_text(str(exit_code) + '\n', encoding='utf-8')
    print(line, end='')
    if error:
        print(error, file=sys.stderr, end='')
    return exit_code


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('prepare')
    detector = sub.add_parser('detect')
    detector.add_argument('--label', required=True, choices=['pristine', 'mutated', 'restored', 'shared-only', 'frame-only'])
    detector.add_argument('--variant', choices=['full', 'shared-only', 'frame-only'], default='full')
    detector.add_argument('--expect', type=int, required=True)
    args = parser.parse_args()
    return prepare() if args.command == 'prepare' else detect(args)


if __name__ == '__main__':
    sys.exit(main())
