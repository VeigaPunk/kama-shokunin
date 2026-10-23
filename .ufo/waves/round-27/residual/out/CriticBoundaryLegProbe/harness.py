#!/usr/bin/env python3
"""Offline KQ37 boundary-leg probe; never calls either counter's main()."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

LANE = Path('/home/vgpnk/Projects/shokunin/kama-shokunin')
OUT = LANE / '.ufo/waves/round-27/residual/out/CriticBoundaryLegProbe'
SCRATCH = Path('/fast/scratch/hyaku/kama-r27c/res-CriticBoundaryLegProbe')
COUNTER_SHA = '49491b80e4f4ed2a85ab822a52f0b1a0fdb1dee53423e3d43b60ee25d1bf2765'
COUNTER = LANE / '.ufo/waves/round-27/count-c1.py'
SOURCE_DIR = LANE / '.ufo/waves/round-27/sources/llama.cpp-704366d'
SHORTCUT_DIR = LANE / '.ufo/waves/round-26/w2-falsify/out/CriticShortcutRows'
BOUNDARY = LANE / '.ufo/waves/round-27/w1a3/out/CriticKQ37Wording/frame_boundary_probe.json'
REGISTRY = LANE / 'registry/error-signatures-r26.json'
FINAL = LANE / '.ufo/waves/round-26/final/c1-final-tip-receipt.json'
SOURCES = LANE / 'corpus/SOURCES.md'
INPUTS: dict[str, dict] = {}


def read_input(path: Path) -> bytes:
    data = path.read_bytes()
    INPUTS[str(path)] = {'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}
    return data


def load_json(path: Path):
    return json.loads(read_input(path))


def deny_live(event, args):
    if event in {'subprocess.Popen', 'socket.connect', 'socket.bind', 'os.exec', 'os.system'}:
        raise RuntimeError(f'offline-only audit refusal: {event}')


sys.addaudithook(deny_live)
sys.dont_write_bytecode = True
counter_bytes = read_input(COUNTER)
assert hashlib.sha256(counter_bytes).hexdigest() == COUNTER_SHA
SCRATCH.mkdir(parents=True, exist_ok=True)
copy_path = SCRATCH / 'frozen_count_c1.py'
assert copy_path != COUNTER and copy_path.suffix == '.py'
copy_path.write_bytes(counter_bytes)
assert hashlib.sha256(copy_path.read_bytes()).hexdigest() == COUNTER_SHA
spec = importlib.util.spec_from_file_location('_kama_r27_boundary_literal_copy', copy_path)
assert spec is not None and spec.loader is not None
frozen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(frozen)


def one_literal_texts(line: str) -> list[str]:
    # literal_texts appends a synthetic concatenation; qualification 1 says ONE literal.
    count = len(frozen.LITERAL_RE.findall(line))
    return frozen.literal_texts(line)[:count]


def spans(text: str, needle: str) -> list[tuple[int, int]]:
    found, start = [], 0
    while needle:
        start = text.find(needle, start)
        if start < 0:
            break
        found.append((start, start + len(needle)))
        start += 1
    return found


def request_strings(request: dict | None) -> list[dict]:
    body = (request or {}).get('body')
    if isinstance(body, str):
        body = json.loads(body) if body else None
    found = []

    def walk(value, pointer):
        if isinstance(value, str) and len(value) >= 4:
            found.append({'pointer': pointer, 'text': value})
        elif isinstance(value, dict):
            for key, child in value.items():
                if len(key) >= 4:
                    found.append({'pointer': pointer + '/<key>', 'text': key})
                walk(child, pointer + '/' + key)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, pointer + '/' + str(index))

    walk(body, '/body')
    return found


def boundary_leg(signature: str, message: str, source_line: str, strings: list[dict]) -> dict:
    literals = one_literal_texts(source_line)
    signature_spans = spans(message, signature)
    overlaps = []
    for item in strings:
        for a, b in spans(message, item['text']):
            for c, d in signature_spans:
                if a < d and c < b:
                    overlaps.append(item | {'request_span': [a, b], 'signature_span': [c, d]})
    literal_ok = any(signature in literal for literal in literals)
    reasons = ([] if literal_ok else ['not_substring_of_one_literal_on_source_line'])
    if overlaps:
        reasons.append('signature_overlaps_decoded_request_string_span')
    return {'accepted': literal_ok and not overlaps, 'reasons': reasons,
            'literal_ok': literal_ok, 'no_request_overlap': not overlaps,
            'source_literals': literals, 'signature_spans': signature_spans,
            'decoded_request_strings_ge4': strings, 'overlaps': overlaps}


source_pins = dict(frozen.SOURCE_SHA256)
# These two additional files are pinned by the round-26 counter (lines 62,65).
source_pins.update({
    'gguf.cpp': '7505d6a434dc740941a682fd3b476ef9bd9893ab76adf18c9969daa528bd5be5',
    'llama.cpp': '8058a140d444b67bf64a1ce393d241dfd60080f4b117130c6f82e637e2109233',
})
source_cache = {}


def source_lines(name: str) -> list[str]:
    if name not in source_cache:
        raw = read_input(SOURCE_DIR / name)
        assert hashlib.sha256(raw).hexdigest() == source_pins[name], name
        source_cache[name] = raw.decode().splitlines()
    return source_cache[name]


def source_record(name: str, line: int, authority: str) -> dict:
    text = source_lines(name)[line - 1]
    return {'path': str(SOURCE_DIR / name), 'line': line, 'text': text,
            'anchor_authority': authority}


def evaluate(row_id, signature, message, request, source, message_kind):
    return {'id': row_id, 'signature': signature, 'message': message,
            'message_kind': message_kind, 'source': source,
            **boundary_leg(signature, message, source['text'], request_strings(request))}


boundary_input = load_json(BOUNDARY)
shortcut_registry = load_json(SHORTCUT_DIR / 'shortcut.registry.json')['signatures']
shortcut_receipt = {r['id']: r for r in load_json(SHORTCUT_DIR / 'shortcut.receipt.json')['rows']}
genuine_registry = load_json(REGISTRY)['signatures']
genuine_receipt = {r['id']: r for r in load_json(FINAL)['rows']}
source_rows = {}
for line_number, line in enumerate(read_input(SOURCES).decode().splitlines(), 1):
    match = re.match(r'^\| (S\d+) \|', line)
    if match:
        source_rows[match[1]] = (line_number, line)

boundary_rows = []
for row in boundary_input['rows']:
    source = source_record('server-common.cpp', 1375, f'{BOUNDARY}:4 (S137)')
    boundary_rows.append(evaluate(row['id'], row['signature'], row['captured_message'],
                                  row['decoded_request'], source, 'captured decoded HTTP error.message'))

shortcut_rows = []
for row in shortcut_registry:
    captured = shortcut_receipt[row['id']]
    assert captured['signature'] == row['signature']
    message = json.loads(captured['observed']['channel_excerpt'])['error']['message']
    name, signature = row['source']['file'], row['signature']
    # Original controls cite FILE ONLY. Supply a best-case mined anchor, not false provenance.
    lines = source_lines(name)
    literal_matches = [n for n, text in enumerate(lines, 1)
                       if any(signature in lit for lit in one_literal_texts(text))]
    raw_matches = [n for n, text in enumerate(lines, 1) if signature in text]
    assert literal_matches or raw_matches, row['id']
    chosen = (literal_matches or raw_matches)[0]
    source = source_record(name, chosen, 'diagnostic mined anchor; original control has no line citation')
    source['all_literal_match_lines'] = literal_matches
    source['all_raw_match_lines'] = raw_matches
    shortcut_rows.append(evaluate(row['id'], signature, message, row['request'], source,
                                  'captured decoded HTTP error.message'))

genuine_rows, decoded_signature_diagnostics = [], []
for row in genuine_registry:
    captured = genuine_receipt[row['id']]
    assert captured['signature'] == row['signature']
    source_row_line, citation = source_rows[row['source']['row']]
    anchor = re.search(r'#L(\d+)\b', citation)
    assert anchor is not None, row['id']
    source = source_record(row['source']['file'], int(anchor[1]),
                           f'{SOURCES}:{source_row_line} ({row["source"]["row"]})')
    excerpt = captured['observed']['channel_excerpt']
    is_http = row['channel'] == 'http'
    message = json.loads(excerpt)['error']['message'] if is_http else excerpt
    kind = 'captured decoded HTTP error.message' if is_http else 'retained startup log prefix; NOT complete message'
    result = evaluate(row['id'], row['signature'], message, row.get('request'), source, kind)
    genuine_rows.append(result)
    unescaped = row['signature'].replace('\\"', '"')
    if unescaped != row['signature']:
        diagnostic = evaluate(row['id'], unescaped, message, row.get('request'), source, kind)
        diagnostic['diagnostic_only'] = 'Remove historical JSON-quote escaping; NOT the registered signature or primary result'
        decoded_signature_diagnostics.append(diagnostic)

assert (len(boundary_rows), len(shortcut_rows), len(genuine_rows)) == (12, 12, 17)


def summarize(rows):
    return {'total': len(rows), 'accepted': sum(r['accepted'] for r in rows),
            'refused': sum(not r['accepted'] for r in rows),
            'literal_only_refused': sum(not r['literal_ok'] for r in rows),
            'overlap_only_refused': sum(not r['no_request_overlap'] for r in rows),
            'refused_ids': [r['id'] for r in rows if not r['accepted']]}


sets = {'boundary_shifted': boundary_rows, 'round26_shortcuts': shortcut_rows, 'genuine_e26': genuine_rows}
receipt = {
    'schema': 'kama-r27-kq37-boundary-leg-offline/v1',
    'scope': 'Boundary qualification only; not full KQ37, frozen C1, live replay, or claim verdict',
    'axes': ['calibration (false credit/refusal)', 'depth/coverage (conditional genuine-row cost; C1 not scored)'],
    'counter_sha256': COUNTER_SHA, 'imported_scratch_copy': str(copy_path),
    'predicate': 'signature in ONE decoded C literal on selected source line AND no signature occurrence overlaps ANY exact decoded-body-string occurrence of length >= 4',
    'semantics': {'offsets': 'zero-based, half-open Unicode codepoint spans',
                  'strings': 'JSON-decoded body keys and string values at every depth; length >= 4; no path/headers/argv',
                  'comparisons': 'exact case-sensitive strings; no extra whitespace or case normalization',
                  'literal_texts': 'imported frozen function; omit its appended joined-literals synthetic candidate',
                  'occurrences': 'all, including repeated and overlapping matches; any overlap refuses',
                  'startup': 'No request/body strings exist for E26-15..17, so overlap leg is vacuous even though final receipts retain only log prefixes',
                  'shortcut_anchors': 'File-only original citations strengthened to mined best-case literal line for this diagnostic; never asserted to be original cited lines'},
    'inputs': INPUTS,
    'totals': {name: summarize(rows) for name, rows in sets.items()},
    'sets': sets,
    'representation_diagnostics_not_primary': decoded_signature_diagnostics,
    'execution': {'server_started': False, 'counter_main_called': False,
                  'subprocess_or_socket_calls': 'refused by Python audit hook', 'installs': []},
}
receipt_path = OUT / 'boundary-leg.receipt.json'
assert receipt_path != Path(__file__) and receipt_path != copy_path
receipt_path.write_text(json.dumps(receipt, indent=2) + '\n')
print('counter_sha256=' + COUNTER_SHA)
print('scratch_copy=' + str(copy_path))
for name, rows in sets.items():
    print(name + ': ' + json.dumps(summarize(rows), sort_keys=True))
for row in genuine_rows:
    if not row['accepted']:
        print('genuine_refused ' + row['id'] + ': ' + '; '.join(row['reasons']))
for row in decoded_signature_diagnostics:
    print('representation_diagnostic ' + row['id'] + ': ' + json.dumps({
        'accepted': row['accepted'], 'reasons': row['reasons'], 'overlaps': row['overlaps']}, sort_keys=True))
print('receipt=' + str(receipt_path))
