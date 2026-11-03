#!/usr/bin/env python3
"""Classify bounded owned chat-stream projections, never live serving evidence.
CLI: python -I kama-offline-chat-stream.py INPUT.json
Exits 0 complete; 2 incomplete/error; 3 invalid; 64 invocation; 70 runtime.
Requires the caller's independently verified isolation/resource envelope.
"""
import json
import math
import os
import re
import stat
import sys

MAX_BYTES = 65536
MAX_BODY_BYTES = 32768


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
    raise InvalidInput('nonfinite number')


def finite_float(value):
    number = float(value)
    if not math.isfinite(number):
        raise InvalidInput('nonfinite number')
    return number


def scalar_tree(value):
    if isinstance(value, str):
        value.encode('utf-8', errors='strict')
    elif isinstance(value, dict):
        for key, item in value.items():
            scalar_tree(key)
            scalar_tree(item)
    elif isinstance(value, list):
        for item in value:
            scalar_tree(item)


def strict_json(text):
    try:
        value = json.loads(text, object_pairs_hook=unique_object,
                           parse_constant=reject_constant, parse_float=finite_float)
        scalar_tree(value)
        return value
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise InvalidInput('invalid JSON') from exc


def events(body):
    """Return dispatched data/type pairs and undispatched-data presence."""
    if body.startswith('\ufeff'):
        body = body[1:]
    lines = re.split(r'\r\n|\r|\n', body)
    data = []
    event_type = ''
    dispatched = []
    for i, line in enumerate(lines):
        terminated = i < len(lines) - 1
        if line == '' and terminated:
            if data:
                dispatched.append((event_type, '\n'.join(data)))
            data = []
            event_type = ''
            continue
        if not line or line.startswith(':'):
            continue
        field, sep, value = line.partition(':')
        if value.startswith(' '):
            value = value[1:]
        if field == 'data':
            data.append(value)
        elif field == 'event':
            event_type = value
    return dispatched, bool(data)


def assess(raw):
    if len(raw) > MAX_BYTES:
        raise InvalidInput('outer byte limit')
    try:
        obj = strict_json(raw.decode('utf-8', errors='strict'))
    except UnicodeError as exc:
        raise InvalidInput('outer encoding') from exc
    if (not isinstance(obj, dict) or set(obj) != {'schema', 'synthetic', 'body'}
            or obj['schema'] != 'kama-chat-stream/v1' or obj['synthetic'] is not True
            or not isinstance(obj['body'], str)):
        raise InvalidInput('projection envelope')
    body = obj['body']
    if len(body.encode('utf-8')) > MAX_BODY_BYTES:
        raise InvalidInput('body byte limit')
    frames, pending_data = events(body)
    final = False
    usage = False
    error = False
    done = False
    for event_type, payload in frames:
        if event_type not in ('', 'message'):
            raise InvalidInput('event type')
        if done:
            raise InvalidInput('data after DONE')
        if payload == '[DONE]':
            done = True
            continue
        frame = strict_json(payload)
        if not isinstance(frame, dict):
            raise InvalidInput('frame must be object')
        if error:
            raise InvalidInput('data after error')
        if set(frame) == {'error'}:
            detail = frame['error']
            if (final or usage or not isinstance(detail, dict)
                    or set(detail) != {'message'} or not isinstance(detail['message'], str)
                    or not detail['message']):
                raise InvalidInput('invalid error projection')
            error = True
            continue
        if set(frame) != {'choices'} or not isinstance(frame['choices'], list):
            raise InvalidInput('invalid choices projection')
        choices = frame['choices']
        if not choices:
            if not final or usage:
                raise InvalidInput('usage order')
            usage = True
            continue
        if len(choices) != 1 or final:
            raise InvalidInput('chunk order')
        choice = choices[0]
        if (not isinstance(choice, dict) or set(choice) != {'index', 'finish_reason'}
                or type(choice['index']) is not int or choice['index'] != 0):
            raise InvalidInput('invalid choice')
        reason = choice['finish_reason']
        if reason is not None:
            if not isinstance(reason, str) or reason not in ('stop', 'length', 'tool_calls'):
                raise InvalidInput('invalid finish reason')
            final = True
    if pending_data:
        return 'INCOMPLETE', 'incomplete_sequence', 2
    if error:
        return 'STREAM_ERROR', 'error_event', 2
    if final and done:
        return 'COMPLETE', 'complete_sequence', 0
    return 'INCOMPLETE', 'incomplete_sequence', 2


def read_input(path):
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(fd, 'rb') as source:
            if not stat.S_ISREG(os.fstat(source.fileno()).st_mode):
                raise InvocationError('regular file required')
            return source.read(MAX_BYTES + 1)
    except (OSError, ValueError) as exc:
        raise InvocationError('input unavailable or nonregular') from exc


def main(argv):
    if len(argv) != 2:
        raise InvocationError('expected one input file')
    raw = read_input(argv[1])
    try:
        status, reason, code = assess(raw)
    except InvalidInput:
        status, reason, code = 'INVALID_OR_INSUFFICIENT', 'invalid_input', 3
    output = dict(schema='kama-offline-chat-stream/v1', status=status, reason=reason,
                  readiness='not_established', weight_identity='not_established',
                  runtime_ownership='not_established', live_observation=False)
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
