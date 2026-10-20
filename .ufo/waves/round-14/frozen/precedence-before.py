#!/usr/bin/env python3
"""Classify caller-supplied offline Ollama /api/tags and /api/ps captures.

Usage:
  python3 tools/kama-ollama-evidence.py --tags PATH --ps PATH --expect EXACT_NAME
  python3 tools/kama-ollama-evidence.py --selftest [--cases PATH]

This is an OFFLINE METADATA CORRESPONDENCE classifier.  It never contacts an
endpoint, never reads environment/config/default locations, never acquires
captures, and writes nothing except one JSON object on stdout.  Both input
paths must point at regular files holding exported JSON metadata that the
caller already authorized.  `--expect` is an exact, case-sensitive model name
or model alias; there is no GGUF basename, `:latest`, case or digest-prefix
normalization.

Finding ids / exits:
  loaded_same_digest  0  one selected tags entry and one selected ps entry,
                          equal nonempty digests, no nonempty remote marker
  available_not_loaded 1  local tags entry; no matching ps entry (empty array ok)
  remote_inventory    1  selected tags or ps entry carries a nonempty
                          remote_model/remote_host
  identity_conflict   1  selected entry name/model differ, or selected
                          tags vs ps digests differ
  unknown             2  no tags entry matches the expected name, or a
                          selected entry carries a missing/empty digest
  invalid_input       2  unavailable/non-regular/oversized/non-UTF-8 input,
                          invalid JSON (including duplicate keys and NaN/
                          Infinity), non-object captures, non-array `models`,
                          non-object entries, non-string identity/digest/
                          remote-marker types, duplicate selected entries, or
                          missing/invalid/empty CLI arguments

Fixed precedence (first match wins): structural validation -> no tags match
(unknown) -> duplicate selection in tags or ps (invalid_input) -> selected
tags name/model conflict -> selected ps name/model conflict -> selected tags
remote marker -> selected ps remote marker -> selected tags missing/empty
digest (unknown) -> no selected ps entry (available) -> selected ps
missing/empty digest (unknown) -> unequal digests -> loaded_same_digest.
Remote markers are checked before digest comparison and before a missing
digest.  A present remote_model/remote_host must be a string; absent or "" is
not a marker, any present non-string (including null) is invalid_input, and
any nonempty string is a marker.  A selected entry may supply its identity
through either name or model; the other field may be absent.  Selected entries
with nonempty, unequal name and model are identity_conflict before remote
handling.

`loaded_same_digest` asserts only that the two supplied metadata snapshots
carry the same nonempty digest string for the requested identity.  It is NOT
readiness, NOT liveness, NOT local residency, and NOT vendor-guaranteed
artifact equivalence; the tags/ps digest join is an inference, not a
documented mapping.  `readiness` is always `unknown` and `scope` is always
`offline-captures-not-runtime`.  Both exported snapshots may describe different
instants; no timestamp, expiry or current-state claim is made.

--selftest runs THIS CLI as isolated child processes over the committed
fixtures in tests/ollama-evidence/cases.json and asserts each literal
expected_exit and expected_finding, the child's declared verdict_exit, and its
constant readiness/scope.  It emits its own schema
`kama-ollama-evidence-selftest/v1` with finding_id clean|selftest_failed and
exit 0|1, so a clean self-check cannot be mistaken for a loaded_same_digest
verdict.  It requires at least 16 committed cases with unique names, writes
only inside a TemporaryDirectory, and never imports this file as a module.  A
green selftest is fixture self-consistency only, never runtime evidence.
"""
from __future__ import annotations

import argparse
import json
import os
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

SCHEMA = 'kama-ollama-evidence/v1'
SELFTEST_SCHEMA = 'kama-ollama-evidence-selftest/v1'
SCRIPT = Path(__file__).resolve()
LANE = SCRIPT.parent.parent
DEFAULT_CASES = LANE / 'tests' / 'ollama-evidence' / 'cases.json'
MAX_INPUT_BYTES = 4 * 1024 * 1024
CHILD_TIMEOUT_SECONDS = 30
MIN_CASES = 16
SCOPE = 'offline-captures-not-runtime'
READINESS = 'unknown'
CONSTANT_REASONS = [
    'capture_timing_unknown_exports_not_asserted_simultaneous',
    'ps_expiry_not_evaluated',
]
FINDING_EXIT = {
    'loaded_same_digest': 0,
    'available_not_loaded': 1,
    'remote_inventory': 1,
    'identity_conflict': 1,
    'unknown': 2,
    'invalid_input': 2,
}
IDENTITY_FIELDS = ('name', 'model')
MARKER_FIELDS = ('remote_model', 'remote_host')


class InputError(Exception):
    """Bounded, value-free input failure; ``code`` is a stable reason token."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


class CliError(Exception):
    """argv failure mapped to the JSON invalid_input result, never a traceback."""


class Parser(argparse.ArgumentParser):
    def error(self, message):  # argv problems still emit the JSON contract
        raise CliError(message)


def _fail(code):
    raise InputError(code)


def _pairs(pairs):
    seen = {}
    for key, value in pairs:
        if key in seen:
            _fail('duplicate_json_key')
        seen[key] = value
    return seen


def _constant(value):
    _fail('non_finite_number')


def read_json_file(path, label):
    """Read one regular UTF-8 JSON file under a byte bound, fail closed."""
    try:
        fd = os.open(os.fspath(path), os.O_RDONLY | getattr(os, 'O_NONBLOCK', 0))
    except (OSError, TypeError, ValueError):
        _fail(f'{label}_input_unavailable')
    try:
        try:
            info = os.fstat(fd)
            if not stat.S_ISREG(info.st_mode):
                _fail(f'{label}_input_not_regular_file')
            buffer = bytearray()
            while len(buffer) <= MAX_INPUT_BYTES:
                chunk = os.read(fd, 65536)
                if not chunk:
                    break
                buffer.extend(chunk)
        except OSError:
            _fail(f'{label}_input_unreadable')
    finally:
        os.close(fd)
    if len(buffer) > MAX_INPUT_BYTES:
        _fail(f'{label}_input_too_large')
    try:
        text = bytes(buffer).decode('utf-8')
    except UnicodeDecodeError:
        _fail(f'{label}_input_not_utf8')
    try:
        return json.loads(text, object_pairs_hook=_pairs, parse_constant=_constant)
    except InputError as exc:
        _fail(f'{label}_input_{exc.code}')
    except (ValueError, RecursionError):
        _fail(f'{label}_input_invalid_json')


def validate_capture(document, label):
    """Validate the exported envelope and every entry; return the models list."""
    if not isinstance(document, dict):
        _fail(f'{label}_capture_not_object')
    if 'models' not in document:
        _fail(f'{label}_models_missing')
    models = document['models']
    if not isinstance(models, list):
        _fail(f'{label}_models_not_array')
    for index, entry in enumerate(models):
        if not isinstance(entry, dict):
            _fail(f'{label}_entry_{index}_not_object')
        for field in IDENTITY_FIELDS + ('digest',) + MARKER_FIELDS:
            if field in entry and not isinstance(entry[field], str):
                _fail(f'{label}_entry_{index}_{field}_invalid_type')
    return models


def _matching(entries, expected):
    return [entry for entry in entries
            if entry.get('name') == expected or entry.get('model') == expected]


def _identity_conflict(entry):
    name = entry.get('name')
    model = entry.get('model')
    return (
        isinstance(name, str) and name != ''
        and isinstance(model, str) and model != ''
        and name != model
    )


def _remote_marker(entry):
    for field in MARKER_FIELDS:
        value = entry.get(field)
        if isinstance(value, str) and value != '':
            return field
    return None


def _digest_present(entry):
    value = entry.get('digest')
    return isinstance(value, str) and value != ''


def classify(expected, tags_document, ps_document):
    """Return (finding_id, reasons) for one offline capture pair."""
    tags = validate_capture(tags_document, 'tags')
    ps_entries = validate_capture(ps_document, 'ps')

    tags_matches = _matching(tags, expected)
    if not tags_matches:
        return 'unknown', ['no_tags_entry_matches_expected_name']
    if len(tags_matches) > 1:
        return 'invalid_input', ['duplicate_tags_entries_match_expected_name']
    ps_matches = _matching(ps_entries, expected)
    if len(ps_matches) > 1:
        return 'invalid_input', ['duplicate_ps_entries_match_expected_name']

    tag = tags_matches[0]
    if _identity_conflict(tag):
        return 'identity_conflict', ['selected_tags_entry_name_model_conflict']
    if ps_matches and _identity_conflict(ps_matches[0]):
        return 'identity_conflict', ['selected_ps_entry_name_model_conflict']
    marker = _remote_marker(tag)
    if marker is not None:
        return 'remote_inventory', [f'selected_tags_entry_{marker}_present']
    if ps_matches:
        marker = _remote_marker(ps_matches[0])
        if marker is not None:
            return 'remote_inventory', [
                f'selected_ps_entry_{marker}_present',
                'ps_remote_marker_conservative_inference_not_vendor_schema',
            ]

    if not _digest_present(tag):
        return 'unknown', ['selected_tags_entry_digest_missing_or_empty']
    if not ps_matches:
        return 'available_not_loaded', [
            'tags_digest_local_no_matching_ps_entry',
        ]
    ps_entry = ps_matches[0]
    if not _digest_present(ps_entry):
        return 'unknown', ['selected_ps_entry_digest_missing_or_empty']
    if tag['digest'] != ps_entry['digest']:
        return 'identity_conflict', ['tags_ps_digest_mismatch']
    return 'loaded_same_digest', [
        'tags_ps_digest_equal',
        'metadata_correspondence_not_readiness',
    ]


def classify_payload(expected, finding, reasons):
    return {
        'schema': SCHEMA,
        'finding_id': finding,
        'verdict_exit': FINDING_EXIT[finding],
        'expected_model': expected,
        'readiness': READINESS,
        'scope': SCOPE,
        'reasons': list(reasons) + CONSTANT_REASONS,
    }


def selftest_payload(records, reasons):
    passed = sum(1 for record in records if record['passed'])
    failed = len(records) - passed
    clean = failed == 0 and len(records) >= MIN_CASES
    finding = 'clean' if clean else 'selftest_failed'
    reason_list = list(reasons)
    if failed:
        reason_list.append(
            f'{failed}_case(s)_did_not_match_literal_expected_exit_and_finding'
        )
    if not reason_list:
        reason_list = ['all_cases_matched_expected_exit_and_finding']
    return {
        'schema': SELFTEST_SCHEMA,
        'finding_id': finding,
        'verdict_exit': 0 if clean else 1,
        'expected_model': None,
        'readiness': READINESS,
        'scope': SCOPE,
        'reasons': reason_list,
        'passed': passed,
        'failed': failed,
        'total': len(records),
        'records': records,
    }


def emit(payload):
    sys.stdout.write(json.dumps(payload, ensure_ascii=True, allow_nan=False) + '\n')


def _fixture_text(value):
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=True, allow_nan=False) + '\n'


def _record(name, expected_exit, expected_finding, observed_exit, observed_finding, passed):
    return {
        'name': name,
        'expected_exit': expected_exit,
        'observed_exit': observed_exit,
        'expected_finding': expected_finding,
        'observed_finding': observed_finding,
        'passed': bool(passed),
    }


def _valid_case(case):
    name = case.get('name')
    expected = case.get('expect')
    expected_exit = case.get('expected_exit')
    expected_finding = case.get('expected_finding')
    valid = (
        isinstance(name, str) and name != ''
        and isinstance(expected, str) and expected != ''
        and 'tags' in case and 'ps' in case
        and isinstance(expected_exit, int) and not isinstance(expected_exit, bool)
        and expected_exit in FINDING_EXIT.values()
        and isinstance(expected_finding, str)
        and expected_finding in FINDING_EXIT
        and FINDING_EXIT[expected_finding] == expected_exit
    )
    return valid, name, expected, expected_exit, expected_finding


def run_selftest(cases_path):
    try:
        document = read_json_file(cases_path, 'cases')
    except InputError as exc:
        return selftest_payload([], [exc.code, 'no_cases_executed'])
    if not isinstance(document, list):
        return selftest_payload([], ['cases_not_array', 'no_cases_executed'])
    if not document:
        return selftest_payload([], ['cases_empty', 'no_cases_executed'])
    if len(document) < MIN_CASES:
        return selftest_payload(
            [], [f'cases_fewer_than_{MIN_CASES}', 'no_cases_executed'])
    names = [
        case.get('name') for case in document
        if isinstance(case, dict) and isinstance(case.get('name'), str)
        and case.get('name') != ''
    ]
    if len(names) != len(set(names)):
        return selftest_payload([], ['duplicate_case_names', 'no_cases_executed'])

    records = []
    with tempfile.TemporaryDirectory(prefix='kama-ollama-evidence-') as workspace:
        for index, case in enumerate(document):
            fallback = f'case-{index:03d}'
            if not isinstance(case, dict):
                records.append(_record(fallback, None, None, None, None, False))
                continue
            valid, name, expected, expected_exit, expected_finding = _valid_case(case)
            label = name if isinstance(name, str) and name != '' else fallback
            if not valid:
                records.append(_record(label, expected_exit, expected_finding,
                                       None, None, False))
                continue
            case_dir = Path(workspace) / f'case-{index:03d}'
            tags_path = case_dir / 'tags.json'
            ps_path = case_dir / 'ps.json'
            try:
                case_dir.mkdir()
                if case.get('tags') is not None:
                    tags_path.write_text(_fixture_text(case['tags']), encoding='utf-8')
                if case.get('ps') is not None:
                    ps_path.write_text(_fixture_text(case['ps']), encoding='utf-8')
            except (OSError, TypeError, ValueError):
                records.append(_record(label, expected_exit, expected_finding,
                                       None, None, False))
                continue
            command = [
                sys.executable, '-I', '-B', str(SCRIPT),
                '--tags', str(tags_path),
                '--ps', str(ps_path),
                '--expect', expected,
            ]
            try:
                completed = subprocess.run(
                    command,
                    cwd=str(case_dir),
                    capture_output=True,
                    text=True,
                    timeout=CHILD_TIMEOUT_SECONDS,
                    check=False,
                )
            except (OSError, subprocess.SubprocessError, ValueError):
                records.append(_record(label, expected_exit, expected_finding,
                                       None, None, False))
                continue
            observed_exit = completed.returncode
            observed_finding = None
            child_contract_ok = False
            try:
                payload = json.loads(completed.stdout, object_pairs_hook=_pairs,
                                     parse_constant=_constant)
            except (InputError, ValueError, RecursionError):
                payload = None
            if isinstance(payload, dict):
                finding = payload.get('finding_id')
                if isinstance(finding, str):
                    observed_finding = finding
                child_contract_ok = (
                    payload.get('schema') == SCHEMA
                    and payload.get('verdict_exit') == observed_exit
                    and payload.get('readiness') == READINESS
                    and payload.get('scope') == SCOPE
                )
            passed = (
                child_contract_ok
                and observed_exit == expected_exit
                and observed_finding == expected_finding
            )
            records.append(_record(label, expected_exit, expected_finding,
                                   observed_exit, observed_finding, passed))

    return selftest_payload(records, [])


def build_parser():
    parser = Parser(
        prog='kama-ollama-evidence.py',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            'Offline Ollama /api/tags + /api/ps metadata-correspondence classifier.\n'
            'No network, no endpoint contact, no acquisition, no readiness claim.'
        ),
        epilog=(
            'Exit codes: 0 loaded_same_digest; 1 available_not_loaded, '
            'remote_inventory, identity_conflict; 2 unknown, invalid_input.\n'
            'Precedence: schema -> no tags match -> duplicate selected -> '
            'name/model conflict -> remote marker -> missing digest -> '
            'no ps entry -> digest mismatch/equality.\n'
            'stdout: exactly one JSON object (schema kama-ollama-evidence/v1) '
            'for every classification invocation.\n'
            '--help is plaintext and exits 0; that is not a classification. '
            'This exit map is not kama-probe\'s (there 1=probe error, 2=drift).\n'
            '--selftest emits schema kama-ollama-evidence-selftest/v1 with '
            'finding_id clean|selftest_failed and exit 0|1.\n'
            'Both captures must be caller-authorized exported JSON files. '
            'readiness is always "unknown"; scope is "offline-captures-not-runtime".'
        ),
    )
    parser.add_argument('--tags', metavar='PATH',
                        help='exported GET /api/tags JSON response')
    parser.add_argument('--ps', metavar='PATH',
                        help='exported GET /api/ps JSON response')
    parser.add_argument('--expect', metavar='EXACT_NAME',
                        help='exact case-sensitive model name or alias to select')
    parser.add_argument('--selftest', action='store_true',
                        help='run committed fixture cases through this CLI as child processes')
    parser.add_argument('--cases', metavar='PATH',
                        help='override selftest case file (default: tests/ollama-evidence/cases.json)')
    return parser


def _run(argv):
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except CliError:
        emit(classify_payload(None, 'invalid_input', ['invalid_arguments']))
        return FINDING_EXIT['invalid_input']

    if args.selftest:
        try:
            payload = run_selftest(Path(args.cases) if args.cases else DEFAULT_CASES)
        except Exception:  # bounded selftest result, never a traceback
            payload = selftest_payload([], ['selftest_unexpected_error'])
        emit(payload)
        return payload['verdict_exit']

    if args.cases is not None:
        emit(classify_payload(args.expect, 'invalid_input', ['cases_requires_selftest']))
        return FINDING_EXIT['invalid_input']
    if not args.tags or not args.ps or not args.expect:
        emit(classify_payload(args.expect, 'invalid_input', ['missing_required_argument']))
        return FINDING_EXIT['invalid_input']

    try:
        tags_document = read_json_file(args.tags, 'tags')
        ps_document = read_json_file(args.ps, 'ps')
    except InputError as exc:
        emit(classify_payload(args.expect, 'invalid_input', [exc.code]))
        return FINDING_EXIT['invalid_input']
    try:
        finding, reasons = classify(args.expect, tags_document, ps_document)
    except InputError as exc:
        finding, reasons = 'invalid_input', [exc.code]
    emit(classify_payload(args.expect, finding, reasons))
    return FINDING_EXIT[finding]


def main(argv=None):
    try:
        return _run(argv)
    except SystemExit:
        raise
    except Exception:  # bound all remaining failures to the JSON contract
        emit(classify_payload(None, 'invalid_input', ['unexpected_error']))
        return FINDING_EXIT['invalid_input']


if __name__ == '__main__':
    sys.exit(main())
