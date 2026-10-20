#!/usr/bin/env python3
"""Kama round-13 KQ16 textual criterion gate (bounded, read-only).

Usage:
  python3 .ufo/waves/round-13/measure.py
  python3 .ufo/waves/round-13/measure.py --quality PATH
  python3 .ufo/waves/round-13/measure.py --quality PATH --manifest PATH
  python3 .ufo/waves/round-13/measure.py --selftest

This is a bounded TEXTUAL documentation gate, not a runtime, serving or
semantic-truth gate.  It checks exactly two routed KQ15 propositions in the
admit cell of the active KQ16 table row of corpus/QUALITY.md:

* exit classes: the exact literal
  `source_mismatch=1; snapshot_tampered=2; source_unavailable=2`
* capture versus comparison: the exact literal
  `capture: git show; comparison: git cat-file blob`

Both literals must be present, exactly one KQ16 row must exist, and the
superseded phrase `distinct nonzero exits` must be absent (whitespace/line-wrap
tolerant) from that admit cell.  Contradictory restatements inside the same
admit cell (a wrong `(source_mismatch|snapshot_tampered|source_unavailable)=N`
pair, `comparison: git show`, `capture: git cat-file`, or KQ15's "blob fetched
directly as `git show`" formulation) also fail.  KQ15, reject/lesson columns,
errata, fenced blocks and HTML comments are not evidence.  In the corrected
file the row is searched only in the appended region after the pinned before
bytes, so historical text can never be read as active.  The fixed denominator
is two.  The historical start snapshot has no KQ16 row, so both literals are
missing there by construction: the 2 -> 0 result counts adoption of the
corrected wording, not semantic proof.

Modes:

* live (no --manifest, explicitly unpinned): read --quality (default
  LANE/corpus/QUALITY.md) and read the historical QUALITY blob with
  `git cat-file blob <resolved-before>:corpus/QUALITY.md`.  Record the actual
  `git rev-parse HEAD`, never a hardcoded worktree hash.  The historical blob
  is retrieved with GIT_* stripped and --no-replace-objects; any retrieval
  failure is probe_error, never clean.
* frozen (--manifest PATH): expected.json SHA-256 pins before and after
  snapshots.  Both input digests are verified before any content check; a
  mismatch is snapshot_tampered (exit 2).  The historical prefix is checked
  as raw bytes `after.startswith(before)` against the pinned before snapshot.
  Manifest expectation fields are compared with the observed verdict.

The --selftest mode invokes this real CLI as child processes over isolated
temporary fixtures and asserts exit code plus stable finding id for: before
red, after green, missing exit-map literal, missing capture/comparison
literal, reintroduced mistaken wording, reintroduced KQ15 comparison
formulation, contradictory comparison roles, conflicting exit class, missing
KQ16 row, and altered pinned snapshot.  A green selftest is gate
self-consistency only.  It writes only inside its own TemporaryDirectory.

Exit codes / stable findings: 0 clean; 1 documentation_mismatch;
2 snapshot_tampered; 3 probe_error (unmeasured).  Evaluation modes (excluding
--help, which is conventional argparse plaintext) emit exactly one JSON object
on stdout and never print file contents, only digests and sizes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

WAVE = Path(__file__).resolve().parent
LANE = WAVE.parents[2]
FROZEN = WAVE / 'frozen'
DEFAULT_MANIFEST = FROZEN / 'expected.json'
DEFAULT_QUALITY = LANE / 'corpus' / 'QUALITY.md'

# Pinned start revision of this round.  Never used as an expected worktree
# hash: the measured HEAD is always obtained from `git rev-parse HEAD`.
BEFORE_REVISION = '941bb32c3f591bc63cbf7579b2b6c552228307cd'
QUALITY_GIT_PATH = 'corpus/QUALITY.md'

EXIT_MAP_LITERAL = 'source_mismatch=1; snapshot_tampered=2; source_unavailable=2'
CAPTURE_LITERAL = 'capture: git show; comparison: git cat-file blob'
EXPECTED_EXITS = {
    'source_mismatch': '1',
    'snapshot_tampered': '2',
    'source_unavailable': '2',
}
EXIT_PAIR_RE = re.compile(r'(source_mismatch|snapshot_tampered|source_unavailable)\s*=\s*([0-9]+)')
MISTAKEN_RE = re.compile(r'distinct\s+non-?zero\s+exits?')
REVERSED_COMPARISON_RE = re.compile(r'comparison:\s*git\s+show')
REVERSED_CAPTURE_RE = re.compile(r'capture:\s*git\s+cat-file')
KQ15_COMPARISON_RE = re.compile(r'compared\s+byte-for-byte\s+with\s+the\s+blob\s+fetched\s+directly\s+as')
ROW_RE = re.compile(r'^\|\s*KQ16(?![\w-])')
KQ15_ROW_RE = re.compile(r'^\|\s*KQ15(?![\w-])')
FENCE_RE = re.compile(r'^\s*(?:```|~~~)')
COMMENT_RE = re.compile(r'<!--.*?-->', re.S)
OID_RE = re.compile(r'[0-9a-f]{40,64}')

SCHEMA = 'kama-round-13-quality-textual/v1'
SELFTEST_SCHEMA = 'kama-round-13-quality-selftest/v1'
DENOMINATOR = 2
DENOMINATOR_BASIS = (
    'two routed KQ15 propositions from the outside D1 defect '
    '(corpus/lessons/round-12-verifier-spotcheck.md:147); not derived by this script'
)
FINDINGS = {
    'clean': 0,
    'documentation_mismatch': 1,
    'snapshot_tampered': 2,
    'probe_error': 3,
}
SCOPE = (
    'bounded textual KQ16 gate: wording conformance only; no new capability, '
    'runtime, serving, or semantic-admission claim, and no proof that any '
    'historical gate or target command was executed'
)
LIMITS = [
    'The 2 -> 0 denominator counts the two routed KQ15 proposition wordings from the outside D1 finding; the historical start has no KQ16 row, so both literals are missing there by construction. This gate did not discover the discrepancy.',
    'Only exactly one KQ16 table row and its admit cell are searched, and only in the appended region after the pinned before bytes. KQ15, the reject and lesson columns, errata, fenced blocks and HTML comments are not evidence, so a literal placed elsewhere fails and a historical quote elsewhere is not flagged.',
    'Exact literals trade paraphrase freedom for auditability: a legitimate correction worded differently fails.',
    'The forbidden phrase is matched as distinct\\s+non-?zero\\s+exits?; a paraphrase of the superseded wording can evade it, while quoting the exact superseded phrase inside the admit cell fails even when negated.',
    'The exit map holds for the primary finding only; a real mismatch coexisting with a higher-precedence exit-2 finding still exits 2 while the correspondence count records the mismatch. The literal check cannot verify that qualifier.',
    'Capture provenance is author-attested only. Byte identity cannot reveal which command produced a snapshot, and expected.json has no capture-command field.',
    'Manifest SHA-256 pins establish input immutability, not semantic truth, correspondence, or a verdict; a coherent manifest+snapshot rewrite remains possible, as does an in-place rewrite of the live unpinned file.',
    'Frozen mode does not re-fetch git history; before provenance is the pinned manifest entry. Live mode is explicitly unpinned.',
    'Exit precedence and fail-closed source/integrity semantics live in the reviewed round-12 code and receipts, not in this wording check.',
    'A green --selftest shows frozen construction and gate self-consistency only, never semantic or execution evidence.',
    'expected.json records kq15_line_sha256 as informational metadata. The gate enforces the whole pinned before digest plus raw byte prefix, which implies the historical KQ15 line is preserved, but the recorded line digest is not compared separately.',
    'Frozen enforcement is manifest path containment plus SHA-256/byte pins; snapshot symlink flags are recorded, not separately gated. Live clean rejects a non-canonical or symlinked --quality path.',
    'Rows are located with Python splitlines(); exotic Unicode or form-feed separators inside masked regions are outside scope and could shift indexing only in documents that do not use LF line structure.',
    'Git reads strip GIT_* and disable replace, lazy fetch, prompts and optional locks, but do not force GIT_CONFIG_GLOBAL/GIT_CONFIG_NOSYSTEM; cat-file blob reads object bytes, and the round-12 method remains the config-suppressing reference.',
    'No network, endpoints, target execution, historical gate execution or import of fidelity.py/reproduce.py.',
]
HUMAN_REVIEW_REQUIRED = [
    '.ufo/waves/round-12/fidelity.py:24-25,64-72,271-273,319 - exit precedence and fail-capable source/integrity semantics; static/code review, not verified here',
    '.ufo/waves/round-12/reproduce.py:80 - historical gate invocation receipt; not re-executed here',
    '.ufo/waves/round-12/acceptance.json - recorded mismatch=1/tamper=2/unavailable=2 receipts; observations, not fresh executions',
]


class GateError(Exception):
    """Unmeasured input or environment failure; never a clean verdict."""


class Parser(argparse.ArgumentParser):
    def error(self, message):  # keep one JSON object on stdout even for bad argv
        raise GateError(message)


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def text_of(data, label):
    try:
        return data.decode('utf-8')
    except UnicodeDecodeError as exc:
        raise GateError(f'{label} is not valid UTF-8: {exc}') from exc


def mask_noncontent(text):
    """Blank HTML comments and fenced code blocks, preserving line count."""
    def blank(match):
        return ''.join('\n' if ch == '\n' else ' ' for ch in match.group(0))

    text = COMMENT_RE.sub(blank, text)
    out = []
    in_fence = False
    for line in text.splitlines(keepends=True):
        newline = '\n' if line.endswith('\n') else ''
        if FENCE_RE.match(line):
            in_fence = not in_fence
            out.append(newline)
        elif in_fence:
            out.append(newline)
        else:
            out.append(line)
    return ''.join(out)


def row_cells(line):
    stripped = line.strip()
    if not (stripped.startswith('|') and stripped.endswith('|')):
        return []
    return [cell.strip() for cell in re.split(r'(?<!\\)\|', stripped[1:-1])]


def kq16_line_indices(text):
    masked = mask_noncontent(text).splitlines()
    return [index for index, line in enumerate(masked) if ROW_RE.match(line)]


def contradiction_problems(admit):
    """Bounded literal contradictions inside the admit cell only."""
    if admit is None:
        return []
    scan = re.sub(r'\s+', ' ', admit.replace('`', ''))
    problems = []
    for match in EXIT_PAIR_RE.finditer(scan):
        name, value = match.group(1), match.group(2)
        if EXPECTED_EXITS[name] != value:
            problems.append(f'exit_class_conflict:{name}={value}')
    if REVERSED_COMPARISON_RE.search(scan):
        problems.append('comparison_uses_git_show')
    if REVERSED_CAPTURE_RE.search(scan):
        problems.append('capture_uses_git_cat_file')
    if KQ15_COMPARISON_RE.search(scan) and 'git show' in scan:
        problems.append('kq15_comparison_formulation_restated')
    return problems


def assess(text, start=0):
    """Evaluate the appended region's KQ16 admit cell; fail closed."""
    segment = text[start:]
    indices = kq16_line_indices(segment)
    rows = segment.splitlines()
    active = rows[indices[-1]] if indices else None
    cells = row_cells(active) if active is not None else []
    layout_ok = len(cells) == 4
    admit = cells[1] if layout_ok else None
    scope = admit if admit is not None else (active or '')
    exit_present = admit is not None and EXIT_MAP_LITERAL in admit
    capture_present = admit is not None and CAPTURE_LITERAL in admit
    mistaken_present = bool(MISTAKEN_RE.search(re.sub(r'\s+', ' ', scope)))
    contradictions = contradiction_problems(admit)
    missing = int(not exit_present) + int(not capture_present)
    content_clean = (
        len(indices) == 1
        and layout_ok
        and missing == 0
        and not mistaken_present
        and not contradictions
    )
    return {
        'kq16_row_count': len(indices),
        'active_kq16_found': bool(indices),
        'cells': len(cells),
        'layout_ok': layout_ok,
        'admit_cell_found': admit is not None,
        'exit_map_literal_present': exit_present,
        'capture_comparison_literal_present': capture_present,
        'mistaken_wording_present': mistaken_present,
        'contradictions': contradictions,
        'missing_assertions': missing,
        'content_clean': content_clean,
    }


def kq15_line_report(before_text, final_text):
    lines = [line for line in before_text.splitlines(keepends=True) if KQ15_ROW_RE.match(line)]
    final_lines = set(final_text.splitlines(keepends=True))
    return {
        'kq15_row_count': len(lines),
        'kq15_lines_preserved': bool(lines) and all(line in final_lines for line in lines),
        'kq15_line_sha256': [sha256_bytes(line.encode('utf-8')) for line in lines],
    }


def content_verdict(assessment):
    return ('clean', 0) if assessment['content_clean'] else ('documentation_mismatch', 1)


def git_env():
    env = {key: value for key, value in os.environ.items() if not key.startswith('GIT_')}
    env.update({
        'GIT_NO_REPLACE_OBJECTS': '1',
        'GIT_NO_LAZY_FETCH': '1',
        'GIT_OPTIONAL_LOCKS': '0',
        'GIT_TERMINAL_PROMPT': '0',
        'GIT_CEILING_DIRECTORIES': str(LANE.parent),
    })
    return env


def git_read(args, commands):
    """Run one read-only git command; argv only is recorded, never env."""
    argv = ['git', '--no-pager', '--no-replace-objects', '-C', str(LANE)] + list(args)
    commands.append(argv)
    try:
        proc = subprocess.run(
            argv, stdin=subprocess.DEVNULL, capture_output=True,
            timeout=30, env=git_env(), shell=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise GateError(f'git invocation failed: {exc}') from exc
    if proc.returncode != 0:
        detail = proc.stderr.decode('utf-8', 'replace').strip()[:200]
        raise GateError(f'git {args[0]} exited {proc.returncode}: {detail}')
    return proc.stdout


def measured_head(commands, optional=False):
    try:
        oid = git_read(['rev-parse', 'HEAD'], commands).decode('utf-8', 'replace').strip()
        if not OID_RE.fullmatch(oid):
            raise GateError(f'rev-parse HEAD returned an unexpected object id: {oid!r}')
        return oid
    except GateError:
        if optional:
            return None
        raise


def resolved_before(revision, commands):
    if not revision or revision.startswith('-'):
        raise GateError('before revision must be non-empty and must not start with "-"')
    oid = git_read(
        ['rev-parse', '--verify', '--end-of-options', revision + '^{commit}'],
        commands,
    ).decode('utf-8', 'replace').strip()
    if not OID_RE.fullmatch(oid):
        raise GateError(f'before revision did not resolve to a commit: {oid!r}')
    return oid


def historical_quality(oid, commands):
    blob = git_read(['cat-file', 'blob', f'{oid}:{QUALITY_GIT_PATH}'], commands)
    if not blob:
        raise GateError('empty historical QUALITY blob; refusing a vacuous comparison')
    return blob


def read_input(path, label):
    path = Path(path)
    try:
        if not path.is_file():
            raise GateError(f'{label} is not a regular file: {path}')
        return path.read_bytes()
    except OSError as exc:
        raise GateError(f'cannot read {label} {path}: {exc}') from exc


def base_result(mode, commands):
    return {
        'schema': SCHEMA,
        'mode': mode,
        'scope': SCOPE,
        'bounded_textual_gate': True,
        'not_runtime_gate': True,
        'no_new_capability_claim': True,
        'finding_object': (
            'round-13 QUALITY KQ16 wording and frozen QUALITY digest pins; '
            'not round-12 SOURCES.md or model-source provenance'
        ),
        'expected_fixed_denominator': DENOMINATOR,
        'denominator_basis': DENOMINATOR_BASIS,
        'assertions': {
            'exit_map_literal': EXIT_MAP_LITERAL,
            'capture_comparison_literal': CAPTURE_LITERAL,
            'forbidden_phrase': 'distinct nonzero exits',
            'searched_scope': 'admit cell of the single KQ16 table row in the appended region after the pinned before bytes',
        },
        'limits': LIMITS,
        'human_review_required': HUMAN_REVIEW_REQUIRED,
        'commands': commands,
    }


def selection_block(assessment):
    finding, code = content_verdict(assessment)
    return {
        'missing_assertions': assessment['missing_assertions'],
        'content_clean': assessment['content_clean'],
        'finding': finding,
        'exit': code,
    }


def finish(result, finding, observations=None):
    result['finding'] = finding
    result['findings'] = [finding]
    result['observations'] = observations or []
    result['verdict_exit'] = FINDINGS[finding]
    return result, FINDINGS[finding]


def run_live(args):
    commands = []
    quality_path = Path(args.quality) if args.quality else DEFAULT_QUALITY
    final = read_input(quality_path, 'quality input')
    head = measured_head(commands)
    oid = resolved_before(args.before_revision, commands)
    before = historical_quality(oid, commands)
    head_quality = git_read(['cat-file', 'blob', f'{head}:{QUALITY_GIT_PATH}'], commands)

    before_text = text_of(before, 'historical QUALITY')
    final_text = text_of(final, 'quality input')
    before_assessment = assess(before_text)
    prefix_preserved = final.startswith(before)
    after_assessment = assess(final_text, len(before_text)) if prefix_preserved else assess('')
    kq15 = kq15_line_report(before_text, final_text)

    before_is_pinned_start = oid == BEFORE_REVISION
    canonical_quality = Path(quality_path).resolve() == DEFAULT_QUALITY.resolve()
    quality_symlink = Path(quality_path).is_symlink()
    worktree_matches_head = final == head_quality

    result = base_result('live-unpinned', commands)
    result.update({
        'measured_revision': head,
        'before_revision': args.before_revision,
        'resolved_before_oid': oid,
        'before_is_pinned_start': before_is_pinned_start,
        'quality_path': str(Path(quality_path).resolve()),
        'quality_is_symlink': quality_symlink,
        'quality_is_canonical_lane_path': canonical_quality,
        'worktree_matches_head': worktree_matches_head,
        'manifest': None,
        'before_missing_assertions': before_assessment['missing_assertions'],
        'after_missing_assertions': after_assessment['missing_assertions'],
        'before': selection_block(before_assessment),
        'after': selection_block(after_assessment),
        'assessment': after_assessment,
        'historical_prefix_preserved': prefix_preserved,
        'historical_sha256': sha256_bytes(before),
        'historical_bytes': len(before),
        'final_sha256': sha256_bytes(final),
        'final_bytes': len(final),
        'head_quality_sha256': sha256_bytes(head_quality),
        'kq15_preservation': kq15,
        'checks': {
            'historical_read': True,
            'prefix_preserved': prefix_preserved,
            'kq15_lines_preserved': kq15['kq15_lines_preserved'],
            'content_clean': after_assessment['content_clean'],
            'before_is_pinned_start': before_is_pinned_start,
            'before_missing_equals_denominator':
                before_assessment['missing_assertions'] == DENOMINATOR,
            'quality_is_canonical_lane_path': canonical_quality,
            'quality_is_not_symlink': not quality_symlink,
            'worktree_matches_head': worktree_matches_head,
        },
    })
    observations = []
    if not prefix_preserved:
        observations.append('prefix_violation')
    if not before_is_pinned_start:
        observations.append('before_revision_not_pinned_start')
    if before_assessment['missing_assertions'] != DENOMINATOR:
        observations.append('before_missing_assertions_not_denominator')
    if not canonical_quality:
        observations.append('quality_not_canonical_lane_path')
    if quality_symlink:
        observations.append('quality_is_symlink')
    if not worktree_matches_head:
        observations.append('worktree_not_at_measured_revision')
    clean = (
        after_assessment['content_clean']
        and prefix_preserved
        and before_is_pinned_start
        and before_assessment['missing_assertions'] == DENOMINATOR
        and canonical_quality
        and not quality_symlink
        and worktree_matches_head
    )
    return finish(result, 'clean' if clean else 'documentation_mismatch', observations)


def load_manifest(path):
    raw = read_input(path, 'manifest')
    try:
        manifest = json.loads(raw.decode('utf-8'))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise GateError(f'manifest is not valid JSON: {exc}') from exc
    if manifest.get('schema') != SCHEMA:
        raise GateError(f"manifest schema is not {SCHEMA}")
    for role in ('before', 'after'):
        entry = manifest.get(role)
        if not isinstance(entry, dict):
            raise GateError(f'manifest is missing the {role} input')
        for key in ('snapshot', 'sha256', 'bytes', 'missing_assertions', 'finding'):
            if key not in entry:
                raise GateError(f'manifest {role} input is missing {key}')
        if not re.fullmatch(r'[0-9a-f]{64}', str(entry['sha256'])):
            raise GateError(f'manifest {role} sha256 is malformed')
        if not isinstance(entry['bytes'], int):
            raise GateError(f'manifest {role} bytes is malformed')
        if entry['finding'] not in FINDINGS or entry['finding'] == 'probe_error':
            raise GateError(f'manifest {role} finding is not a conformance finding')
    return manifest, raw


def frozen_inputs(manifest, manifest_path):
    base = Path(manifest_path).resolve().parent
    inputs = {}
    for role in ('before', 'after'):
        entry = manifest[role]
        snapshot = Path(entry['snapshot'])
        if snapshot.is_absolute():
            raise GateError(f'manifest {role} snapshot must be relative to the manifest directory')
        path = (base / snapshot).resolve()
        if not path.is_relative_to(base):
            raise GateError(f'manifest {role} snapshot escapes the manifest directory')
        data = read_input(path, f'{role} snapshot')
        inputs[role] = {
            'path': path,
            'bytes': data,
            'sha256': sha256_bytes(data),
            'expected_sha256': entry['sha256'],
            'expected_bytes': entry['bytes'],
            'digest_ok': sha256_bytes(data) == entry['sha256'] and len(data) == entry['bytes'],
            'is_symlink': Path(base / entry['snapshot']).is_symlink(),
        }
    return inputs


def run_frozen(args):
    commands = []
    manifest_path = Path(args.manifest)
    manifest, manifest_raw = load_manifest(manifest_path)
    inputs = frozen_inputs(manifest, manifest_path)
    head = measured_head(commands, optional=True)
    tampered = [role for role in ('before', 'after') if not inputs[role]['digest_ok']]

    result = base_result('frozen-pinned', commands)
    result.update({
        'measured_revision': head,
        'manifest_path': str(manifest_path.resolve()),
        'manifest_sha256': sha256_bytes(manifest_raw),
        'before_revision': manifest['before'].get('revision'),
        'manifest': {
            'before': {key: manifest['before'][key] for key in manifest['before']},
            'after': {key: manifest['after'][key] for key in manifest['after']},
        },
        'inputs': {
            role: {
                'path': str(inputs[role]['path']),
                'sha256': inputs[role]['sha256'],
                'expected_sha256': inputs[role]['expected_sha256'],
                'bytes': len(inputs[role]['bytes']),
                'expected_bytes': inputs[role]['expected_bytes'],
                'digest_ok': inputs[role]['digest_ok'],
                'is_symlink': inputs[role]['is_symlink'],
            }
            for role in ('before', 'after')
        },
    })
    if tampered:
        result.update({
            'tampered_inputs': tampered,
            'snapshot_tampered_scope': (
                'round-13 frozen QUALITY input digest mismatch; not round-12 '
                'SOURCES.md or model-source provenance'
            ),
            'before_missing_assertions': None,
            'after_missing_assertions': None,
            'before': None,
            'after': None,
            'historical_prefix_preserved': None,
            'checks': {'input_digests': False},
        })
        return finish(result, 'snapshot_tampered', ['digest_mismatch'])

    before_data = inputs['before']['bytes']
    after_data = inputs['after']['bytes']
    before_text = text_of(before_data, 'before snapshot')
    after_text = text_of(after_data, 'after snapshot')
    before_assessment = assess(before_text)
    prefix_preserved = after_data.startswith(before_data)
    after_assessment = (
        assess(after_text, len(before_text)) if prefix_preserved else assess('')
    )
    kq15 = kq15_line_report(before_text, after_text)

    selected_path = Path(args.quality).resolve() if args.quality else inputs['after']['path']
    if selected_path == inputs['before']['path']:
        role = 'before'
    elif selected_path == inputs['after']['path']:
        role = 'after'
    else:
        raise GateError(
            '--quality must resolve to the manifest-pinned before or after snapshot; '
            f'got {selected_path}'
        )
    selected = before_assessment if role == 'before' else after_assessment
    entry = manifest[role]
    expectation_ok = (
        selected['missing_assertions'] == entry['missing_assertions']
        and content_verdict(selected)[0] == entry['finding']
    )
    before_is_pinned_start = manifest['before'].get('revision') == BEFORE_REVISION
    before_missing_ok = before_assessment['missing_assertions'] == DENOMINATOR
    finding, code = content_verdict(selected)
    if not (prefix_preserved and expectation_ok and before_is_pinned_start and before_missing_ok):
        finding, code = 'documentation_mismatch', 1

    result.update({
        'selected_role': role,
        'quality_path': str(selected_path),
        'quality_is_symlink': Path(args.quality).is_symlink() if args.quality else False,
        'before_missing_assertions': before_assessment['missing_assertions'],
        'after_missing_assertions': after_assessment['missing_assertions'],
        'before': selection_block(before_assessment),
        'after': selection_block(after_assessment),
        'selected': selection_block(selected),
        'assessment': selected,
        'manifest_expectation_matches': expectation_ok,
        'before_is_pinned_start': before_is_pinned_start,
        'historical_prefix_preserved': prefix_preserved,
        'historical_sha256': sha256_bytes(before_data),
        'historical_bytes': len(before_data),
        'final_sha256': sha256_bytes(after_data),
        'final_bytes': len(after_data),
        'kq15_preservation': kq15,
        'checks': {
            'input_digests': True,
            'prefix_preserved': prefix_preserved,
            'kq15_lines_preserved': kq15['kq15_lines_preserved'],
            'content_clean': selected['content_clean'],
            'manifest_expectation': expectation_ok,
            'before_is_pinned_start': before_is_pinned_start,
            'before_missing_equals_denominator': before_missing_ok,
        },
    })
    observations = []
    if not prefix_preserved:
        observations.append('prefix_violation')
    if not expectation_ok:
        observations.append('manifest_expectation_mismatch')
    if not before_is_pinned_start:
        observations.append('before_revision_not_pinned_start')
    if not before_missing_ok:
        observations.append('before_missing_assertions_not_denominator')
    return finish(result, finding, observations)


def mutate_admit(text, transform, label):
    """Derive a mutant from the actual active KQ16 admit cell."""
    indices = kq16_line_indices(text)
    lines = text.splitlines(keepends=True)
    if not indices:
        raise GateError(f'cannot derive {label}: frozen after text has no KQ16 row')
    index = indices[-1]
    line = lines[index]
    cells = row_cells(line)
    if len(cells) != 4:
        raise GateError(f'cannot derive {label}: active KQ16 row does not have four cells')
    cells[1] = transform(cells[1])
    newline = '\n' if line.endswith('\n') else ''
    lines[index] = '| ' + ' | '.join(cells) + ' |' + newline
    return ''.join(lines)


def selftest_manifest(before_data, after_data, before_entry):
    before_text = text_of(before_data, 'fixture before')
    before_assessment = assess(before_text)
    after_assessment = assess(text_of(after_data, 'fixture after'), len(before_text))
    before_finding, _ = content_verdict(before_assessment)
    after_finding, _ = content_verdict(after_assessment)
    return {
        'schema': SCHEMA,
        'denominator': DENOMINATOR,
        'before': {
            'revision': before_entry.get('revision'),
            'path': QUALITY_GIT_PATH,
            'snapshot': 'before/corpus/QUALITY.md',
            'sha256': sha256_bytes(before_data),
            'bytes': len(before_data),
            'missing_assertions': 2,
            'finding': 'documentation_mismatch',
            'frozen_finding': before_finding,
        },
        'after': {
            'path': QUALITY_GIT_PATH,
            'snapshot': 'after/corpus/QUALITY.md',
            'sha256': sha256_bytes(after_data),
            'bytes': len(after_data),
            'missing_assertions': after_assessment['missing_assertions'],
            'finding': after_finding,
        },
    }


def run_selftest(args):
    if not DEFAULT_MANIFEST.is_file():
        raise GateError(f'frozen manifest is missing: {DEFAULT_MANIFEST}')
    base_manifest, _ = load_manifest(DEFAULT_MANIFEST)
    base_inputs = frozen_inputs(base_manifest, DEFAULT_MANIFEST)
    for role in ('before', 'after'):
        if not base_inputs[role]['digest_ok']:
            raise GateError(f'frozen {role} snapshot does not match its pinned digest; refreeze first')
    before_data = base_inputs['before']['bytes']
    after_data = base_inputs['after']['bytes']
    before_text = text_of(before_data, 'frozen before')
    after_text = text_of(after_data, 'frozen after')

    frozen_after = assess(after_text, len(before_text))
    if not frozen_after['content_clean']:
        raise GateError('frozen after snapshot is not clean; selftest mutants would be vacuous')

    cases = []

    def add(name, before_fixture, after_fixture, select, pin_after, expected_exit, expected_finding, expected_missing=None):
        cases.append({
            'name': name,
            'before': before_fixture,
            'after': after_fixture,
            'select': select,
            'pin_after': pin_after,
            'expected_exit': expected_exit,
            'expected_finding': expected_finding,
            'expected_missing': expected_missing,
        })

    add('before_red', before_data, after_data, 'before', None, 1, 'documentation_mismatch', 2)
    add('after_green', before_data, after_data, 'after', None, 0, 'clean', 0)
    add(
        'missing_exit_map_literal',
        before_data,
        mutate_admit(after_text, lambda cell: cell.replace(EXIT_MAP_LITERAL, ''), 'missing exit-map literal').encode(),
        'after', None, 1, 'documentation_mismatch', 1,
    )
    add(
        'missing_capture_comparison_literal',
        before_data,
        mutate_admit(after_text, lambda cell: cell.replace(CAPTURE_LITERAL, ''), 'missing capture/comparison literal').encode(),
        'after', None, 1, 'documentation_mismatch', 1,
    )
    add(
        'reintroduced_mistaken_wording',
        before_data,
        mutate_admit(after_text, lambda cell: cell + ' distinct nonzero exits', 'reintroduced mistaken wording').encode(),
        'after', None, 1, 'documentation_mismatch', 0,
    )
    add(
        'reintroduced_kq15_comparison',
        before_data,
        mutate_admit(
            after_text,
            lambda cell: cell + ' compared byte-for-byte with the blob fetched directly as `git show`',
            'reintroduced KQ15 comparison formulation',
        ).encode(),
        'after', None, 1, 'documentation_mismatch', 0,
    )
    add(
        'contradictory_comparison_roles',
        before_data,
        mutate_admit(
            after_text, lambda cell: cell + ' comparison: git show',
            'contradictory comparison role',
        ).encode(),
        'after', None, 1, 'documentation_mismatch', 0,
    )
    add(
        'conflicting_exit_class',
        before_data,
        mutate_admit(
            after_text, lambda cell: cell + ' source_unavailable=1',
            'conflicting exit class',
        ).encode(),
        'after', None, 1, 'documentation_mismatch', 0,
    )
    add(
        'missing_kq16_row',
        before_data,
        ''.join(
            line for index, line in enumerate(after_text.splitlines(keepends=True))
            if index not in set(kq16_line_indices(after_text))
        ).encode(),
        'after', None, 1, 'documentation_mismatch', 2,
    )
    add(
        'altered_pinned_snapshot',
        before_data,
        after_data + b'\n',
        'after', base_manifest['after']['sha256'], 2, 'snapshot_tampered',
    )

    results = []
    with tempfile.TemporaryDirectory(prefix='kama-r13-selftest-') as tempdir:
        root = Path(tempdir)
        for case in cases:
            case_dir = root / case['name']
            (case_dir / 'before' / 'corpus').mkdir(parents=True)
            (case_dir / 'after' / 'corpus').mkdir(parents=True)
            (case_dir / 'before' / 'corpus' / 'QUALITY.md').write_bytes(case['before'])
            (case_dir / 'after' / 'corpus' / 'QUALITY.md').write_bytes(case['after'])
            manifest = selftest_manifest(
                case['before'], case['after'], base_manifest['before'],
            )
            if case['pin_after'] is not None:
                manifest['after']['sha256'] = case['pin_after']
                manifest['after']['bytes'] = len(after_data)
            manifest_path = case_dir / 'expected.json'
            manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
            quality = case_dir / case['select'] / 'corpus' / 'QUALITY.md'
            child = [
                sys.executable, '-I', '-B', str(Path(__file__).resolve()),
                '--manifest', str(manifest_path), '--quality', str(quality),
            ]
            try:
                proc = subprocess.run(
                    child, stdin=subprocess.DEVNULL, capture_output=True,
                    timeout=120, text=True, shell=False,
                )
                payload = json.loads(proc.stdout)
                missing_key = (
                    'after_missing_assertions' if case['select'] == 'after'
                    else 'before_missing_assertions'
                )
                observed = {
                    'exit': proc.returncode,
                    'finding': payload.get('finding'),
                    'missing_assertions': payload.get(missing_key),
                }
                parsed = True
            except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
                observed = {'exit': None, 'finding': None, 'missing_assertions': None, 'error': str(exc)}
                parsed = False
            missing_ok = (
                case['expected_missing'] is None
                or observed['missing_assertions'] == case['expected_missing']
            )
            passed = (
                parsed
                and observed['exit'] == case['expected_exit']
                and observed['finding'] == case['expected_finding']
                and missing_ok
            )
            results.append({
                'name': case['name'],
                'expected_exit': case['expected_exit'],
                'expected_finding': case['expected_finding'],
                'expected_missing_assertions': case['expected_missing'],
                'observed_exit': observed['exit'],
                'observed_finding': observed['finding'],
                'observed_missing_assertions': observed['missing_assertions'],
                'parsed': parsed,
                'pass': passed,
            })

    passed = sum(1 for case in results if case['pass'])
    failed = len(results) - passed
    result = {
        'schema': SELFTEST_SCHEMA,
        'mode': 'selftest',
        'scope': SCOPE,
        'bounded_textual_gate': True,
        'no_new_capability_claim': True,
        'selftest_scope': 'frozen construction and gate self-consistency only; not semantic, runtime, or execution evidence',
        'finding_object': (
            'round-13 QUALITY KQ16 wording and frozen QUALITY digest pins; '
            'not round-12 SOURCES.md or model-source provenance'
        ),
        'expected_fixed_denominator': DENOMINATOR,
        'cases': results,
        'passed': passed,
        'failed': failed,
        'finding': 'clean' if failed == 0 else 'documentation_mismatch',
        'verdict_exit': 0 if failed == 0 else 1,
        'limits': LIMITS,
    }
    return result, result['verdict_exit']


def build_parser():
    parser = Parser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--quality', help='QUALITY file under test (default: LANE/corpus/QUALITY.md in live mode; the pinned after snapshot in frozen mode)')
    parser.add_argument('--before-revision', default=BEFORE_REVISION, help=f'historical start revision for live mode (default: {BEFORE_REVISION})')
    parser.add_argument('--manifest', help='frozen expected.json; enables digest-pinned mode')
    parser.add_argument('--selftest', action='store_true', help='run real CLI children over isolated fixtures')
    return parser


def main(argv=None):
    args = None
    try:
        args = build_parser().parse_args(argv)
        if args.selftest:
            result, code = run_selftest(args)
        elif args.manifest:
            result, code = run_frozen(args)
        else:
            result, code = run_live(args)
    except GateError as exc:
        mode = 'selftest' if args is not None and args.selftest else (
            'frozen-pinned' if args is not None and args.manifest else 'live-unpinned'
        )
        result = {
            'schema': SCHEMA,
            'mode': mode,
            'scope': SCOPE,
            'finding': 'probe_error',
            'findings': ['probe_error'],
            'expected_fixed_denominator': DENOMINATOR,
            'verdict_exit': FINDINGS['probe_error'],
            'error': str(exc),
            'limits': LIMITS,
        }
        code = FINDINGS['probe_error']
    except Exception as exc:  # never let an unexpected failure look clean
        result = {
            'schema': SCHEMA,
            'mode': 'gate-error',
            'scope': SCOPE,
            'finding': 'probe_error',
            'findings': ['probe_error'],
            'expected_fixed_denominator': DENOMINATOR,
            'verdict_exit': FINDINGS['probe_error'],
            'error': f'{type(exc).__name__}: {exc}',
            'limits': LIMITS,
        }
        code = FINDINGS['probe_error']
    print(json.dumps(result, indent=2))
    return code


if __name__ == '__main__':
    sys.exit(main())
