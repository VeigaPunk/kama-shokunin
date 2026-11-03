#!/usr/bin/env python3
"""Bounded offline advertised-ID assessment, not endpoint/weight verification.
CLI: python -I kama-offline-identity.py INPUT.json
Exits: 0 exact membership; 2 normalization-only/no match; 3 invalid input;
64 invocation/file error; 70 unexpected runtime failure. Writes stdout/stderr only.
The caller must provide the independently verified isolation/resource envelope.
"""
import json
import os
import stat
import sys

MAX_BYTES = 65536
MAX_IDS = 256
MAX_SCALARS = 512


class InvalidInput(ValueError):
    pass


class InvocationError(ValueError):
    pass


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise InvalidInput('duplicate key')
        result[key] = value
    return result


def reject_constant(value):
    raise InvalidInput('nonstandard constant')


def valid_id(value):
    return (isinstance(value, str) and 1 <= len(value) <= MAX_SCALARS
            and all(not (ord(c) < 32 or 127 <= ord(c) <= 159
                         or 0xD800 <= ord(c) <= 0xDFFF) for c in value))


def legacy_norm(value):
    tail = value.rsplit('/', 1)[-1]
    return tail[:-5] if tail.endswith('.gguf') else tail


def assess(raw):
    if len(raw) > MAX_BYTES:
        raise InvalidInput('byte limit')
    try:
        obj = json.loads(raw.decode('utf-8'), object_pairs_hook=unique_object,
                         parse_constant=reject_constant)
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise InvalidInput('invalid JSON') from exc
    if not isinstance(obj, dict) or set(obj) != {'expected_id', 'data'}:
        raise InvalidInput('root schema')
    expected, data = obj['expected_id'], obj['data']
    if not valid_id(expected) or not isinstance(data, list) or not 1 <= len(data) <= MAX_IDS:
        raise InvalidInput('root values')
    ids = []
    for item in data:
        if (not isinstance(item, dict) or set(item) != {'id'}
                or not valid_id(item['id'])):
            raise InvalidInput('item schema')
        ids.append(item['id'])
    if len(set(ids)) != len(ids):
        raise InvalidInput('duplicate id')
    ids.sort()
    normalized = legacy_norm(expected)
    candidates = [value for value in ids if normalized and legacy_norm(value) == normalized]
    exact = [expected] if expected in ids else []
    if exact:
        status, reason, code = 'EXACT_ADVERTISED_ID', 'exact_member', 0
    elif candidates:
        status, reason, code = 'NORMALIZATION_ONLY', 'legacy_equivalence_only', 2
    else:
        status, reason, code = 'NO_ADVERTISED_MATCH', 'no_member', 2
    return dict(status=status, reason=reason, expected_id=expected,
                exact_candidates=exact, normalization_candidates=candidates,
                colliding_names=[v for v in candidates if v != expected],
                legacy_match=bool(candidates)), code


def read_input(path):
    # NONBLOCK prevents a FIFO swap from blocking before its fstat refusal.
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(fd, 'rb') as source:
            if not stat.S_ISREG(os.fstat(source.fileno()).st_mode):
                raise InvocationError('input must be a regular file')
            return source.read(MAX_BYTES + 1)
    except (OSError, ValueError) as exc:
        raise InvocationError('input unavailable or nonregular') from exc


def main(argv):
    if len(argv) != 2:
        raise InvocationError('expected one input file')
    raw = read_input(argv[1])
    try:
        output, code = assess(raw)
    except InvalidInput:
        output = dict(status='INVALID_OR_INSUFFICIENT', reason='invalid_input',
                      expected_id=None, exact_candidates=[], normalization_candidates=[],
                      colliding_names=[], legacy_match=None)
        code = 3
    output.update(schema='kama-offline-identity/v1', readiness='not_established',
                  weight_identity='not_established', runtime_ownership='not_established',
                  live_observation=False)
    print(json.dumps(output, sort_keys=True, ensure_ascii=True, separators=(',', ':')))
    return code


if __name__ == '__main__':
    try:
        exit_code = main(sys.argv)
    except InvocationError:
        print('invocation error: one readable regular nonsymlink input required', file=sys.stderr)
        exit_code = 64
    except Exception:
        print('runtime error: no verdict', file=sys.stderr)
        exit_code = 70
    sys.exit(exit_code)
