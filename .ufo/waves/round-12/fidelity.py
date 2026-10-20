#!/usr/bin/env python3
"""Kama round-12 fidelity gate: snapshot integrity and git source correspondence.

Usage:
  python3 .ufo/waves/round-12/fidelity.py
  python3 .ufo/waves/round-12/fidelity.py --snapshot PATH [--manifest PATH|auto|none] [--repo PATH]
  python3 .ufo/waves/round-12/fidelity.py --selftest

Two independent checks are reported separately:

* snapshot integrity -- observed snapshot bytes match the SHA-256 pinned by the
  selected frozen manifest.  This proves the snapshot was not modified after
  the manifest was written; it proves nothing about git history (D1).
* source correspondence -- observed snapshot bytes equal the immutable git blob
  at SOURCE_REVISION:SOURCE_PATH, whose blob object id and content SHA-256 are
  also code constants.  A manifest cannot redirect that anchor.  Coherently
  editing a snapshot and its manifest digest still fails this check.

A clean verdict requires BOTH checks.  With no manifest the integrity check is
not evaluated: an old archival mismatch is still reported as source_mismatch
(exit 1), while a matching unpinned snapshot is reported as the non-clean,
could-not-evaluate finding `unpinned` (exit 2).

Exit codes: 0 clean; 1 source_mismatch; 2 snapshot_tampered,
source_unavailable, snapshot_unavailable, manifest_invalid, unpinned or
internal_error.  All modes emit one JSON result object on stdout and never
print snapshot contents, only digests, sizes and byte offsets.
"""
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
DEFAULT_SNAPSHOT = WAVE / 'frozen/corpus/SOURCES.md'
DEFAULT_MANIFEST = WAVE / 'frozen/expected.json'

# Immutable historical anchor.  Never derived from argv or from a manifest.
SOURCE_REVISION = '2f7303c242319c1dc96c6bcf7702ac18b3ca1aad'
SOURCE_PATH = 'corpus/SOURCES.md'
SOURCE_BLOB_OID = '7de1360655eadada356fe110813c6e1338142551'
SOURCE_SHA256 = '9dc40d25a595b3d42b39649e17094cfa4e7190cfbf340331252dd29dea22093a'
SOURCE_BYTES = 18898

SCHEMA_MANIFEST = 'kama-round-12-frozen/v1'
SCHEMA_RESULT = 'kama-round-12-fidelity/v1'
SCHEMA_SELFTEST = 'kama-round-12-selftest/v1'

# Deterministic precedence.  Every exit-2 finding outranks source_mismatch
# (exit 1); `clean` is impossible unless integrity, anchor and correspondence
# all matched.  The first matching id below becomes `finding`; every finding
# stays listed in `findings` and every failed check stays visible in `checks`.
# Retrieval failures (not a repository, repository root mismatch, missing
# revision/path, cat-file error) and a retrieved blob whose oid/sha256/bytes
# fail the code pins are source_unavailable (exit 2, could-not-evaluate).
# Snapshot divergence from a verified anchor is source_mismatch (exit 1).
# `mismatches` counts only that latter case, never pin/anchor failures.
PRIORITY = (
    'snapshot_unavailable',
    'manifest_invalid',
    'snapshot_tampered',
    'source_unavailable',
    'source_mismatch',
    'unpinned',
    'clean',
)
SHA256_RE = re.compile(r'^[0-9a-f]{64}$')


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def git_environment(repo):
    """Inherited GIT_* variables must not redirect the object database."""
    environment = {key: value for key, value in os.environ.items()
                   if not key.startswith('GIT_')}
    environment['GIT_NO_REPLACE_OBJECTS'] = '1'
    environment['GIT_NO_LAZY_FETCH'] = '1'
    environment['GIT_OPTIONAL_LOCKS'] = '0'
    environment['GIT_TERMINAL_PROMPT'] = '0'
    if repo is not None:
        environment['GIT_CEILING_DIRECTORIES'] = str(Path(repo).resolve().parent)
    return environment


def git_run(repo, *arguments):
    """Return (stdout bytes, None) or (None, error text).  Never uses a shell."""
    command = ['git', '--no-pager', '--no-replace-objects']
    if repo is not None:
        command += ['-C', str(repo)]
    command += list(arguments)
    try:
        result = subprocess.run(command, capture_output=True,
                                env=git_environment(repo), timeout=120,
                                stdin=subprocess.DEVNULL)
    except FileNotFoundError:
        return None, 'git executable not found'
    except (OSError, subprocess.SubprocessError) as error:
        return None, f'{type(error).__name__}: {error}'
    if result.returncode != 0:
        lines = result.stderr.decode('utf-8', 'replace').strip().splitlines()
        detail = lines[-1] if lines else f'git {" ".join(arguments)} exited {result.returncode}'
        return None, detail
    return result.stdout, None


def git_toplevel(repo):
    output, error = git_run(repo, 'rev-parse', '--show-toplevel')
    if error is not None:
        return None, error
    try:
        return Path(output.decode('utf-8').strip()).resolve(), None
    except (UnicodeDecodeError, OSError) as error:
        return None, f'cannot resolve repository toplevel: {error}'


class ManifestError(Exception):
    pass


def load_manifest(path):
    if path.is_symlink():
        raise ManifestError(f'refusing symlink manifest {path}')
    if not path.is_file():
        raise ManifestError(f'manifest is not a regular file: {path}')
    try:
        raw = path.read_bytes()
    except OSError as error:
        raise ManifestError(f'cannot read manifest {path}: {error}') from error
    try:
        data = json.loads(raw)
    except ValueError as error:
        raise ManifestError(f'manifest is not valid JSON: {error}') from error
    if not isinstance(data, dict):
        raise ManifestError('manifest root is not an object')
    if data.get('schema') != SCHEMA_MANIFEST:
        raise ManifestError(f'manifest schema is not {SCHEMA_MANIFEST}')
    digest = data.get('snapshot_sha256')
    if not isinstance(digest, str) or not SHA256_RE.match(digest):
        raise ManifestError('snapshot_sha256 is not a lowercase sha256 hex digest')
    if data.get('source_revision') != SOURCE_REVISION:
        raise ManifestError(
            f"manifest source_revision {data.get('source_revision')!r} is not "
            f'the pinned {SOURCE_REVISION}; a manifest cannot redirect the anchor')
    if data.get('source_path') != SOURCE_PATH:
        raise ManifestError(
            f"manifest source_path {data.get('source_path')!r} is not the "
            f'pinned {SOURCE_PATH!r}')
    if data.get('snapshot_path') != SOURCE_PATH:
        raise ManifestError(
            f"manifest snapshot_path {data.get('snapshot_path')!r} is not "
            f'{SOURCE_PATH!r}')
    if data.get('source_oid') != SOURCE_BLOB_OID:
        raise ManifestError(
            f"manifest source_oid {data.get('source_oid')!r} is not the pinned "
            f'{SOURCE_BLOB_OID}')
    if data.get('source_sha256') != SOURCE_SHA256:
        raise ManifestError(
            f"manifest source_sha256 {data.get('source_sha256')!r} is not the "
            f'pinned {SOURCE_SHA256}')
    if data.get('source_bytes') != SOURCE_BYTES:
        raise ManifestError(
            f"manifest source_bytes {data.get('source_bytes')!r} is not the "
            f'pinned {SOURCE_BYTES}')
    if data.get('expected_verdict') != 'clean':
        raise ManifestError(
            f"manifest expected_verdict {data.get('expected_verdict')!r} is not "
            f"'clean'; the frozen control pins a clean verdict")
    return {'path': path, 'sha256': sha256(raw), 'pin': digest,
            'expected': 'clean'}


def resolve_manifest(argument, snapshot_path, snapshot_was_given):
    """Resolve --manifest auto|none|PATH.  Returns (manifest, error)."""
    if argument == 'none':
        return None, None
    if argument != 'auto':
        return load_manifest(Path(argument)), None
    if not snapshot_was_given or snapshot_path == DEFAULT_SNAPSHOT:
        return load_manifest(DEFAULT_MANIFEST), None
    # An overridden snapshot without an explicit manifest is unpinned, so an
    # old archival copy is reported as a source mismatch, not as tampering.
    return None, None


def first_difference(left, right):
    limit = min(len(left), len(right))
    for offset in range(limit):
        if left[offset] != right[offset]:
            return offset
    return limit if len(left) != len(right) else None


def evaluate(snapshot_path, manifest_argument, repo_path, snapshot_was_given):
    findings = []
    checks = []

    snapshot_bytes = None
    snapshot_error = None
    try:
        if snapshot_path.is_symlink():
            raise OSError('refusing symlink snapshot')
        if not snapshot_path.is_file():
            raise OSError('not a regular file')
        snapshot_bytes = snapshot_path.read_bytes()
    except OSError as error:
        snapshot_error = str(error)
        findings.append({'id': 'snapshot_unavailable',
                         'detail': f'cannot read snapshot {snapshot_path}: {error}'})

    manifest = None
    manifest_error = None
    try:
        manifest, _ = resolve_manifest(manifest_argument, snapshot_path,
                                       snapshot_was_given)
    except ManifestError as error:
        manifest_error = str(error)
        findings.append({'id': 'manifest_invalid', 'detail': manifest_error})

    pinned = manifest is not None
    pin_matches = None
    if manifest is not None and snapshot_bytes is not None:
        pin_matches = sha256(snapshot_bytes) == manifest['pin']
        checks.append({'id': 'snapshot_pin', 'ok': pin_matches})
        if not pin_matches:
            findings.append({
                'id': 'snapshot_tampered',
                'detail': f"snapshot sha256 {sha256(snapshot_bytes)} does not "
                          f"match manifest pin {manifest['pin']}"})
    if manifest is None and manifest_error is None:
        findings.append({
            'id': 'unpinned',
            'detail': 'no manifest pin: snapshot integrity not checked; '
                      'a clean verdict cannot be certified'})

    source_available = False
    source_matches = None
    anchor_matches = None
    source_oid = None
    source_bytes = None
    source_error = None
    source_diff = None

    toplevel, error = git_toplevel(repo_path)
    if error is not None:
        source_error = error
        findings.append({'id': 'source_unavailable',
                         'detail': f'git repository {repo_path} unusable: {error}'})
    elif toplevel != repo_path:
        source_error = (f'repository toplevel {toplevel} does not equal '
                        f'requested root {repo_path}')
        findings.append({'id': 'source_unavailable', 'detail': source_error})
    else:
        oid_output, oid_error = git_run(
            repo_path, 'rev-parse', '--verify', f'{SOURCE_REVISION}:{SOURCE_PATH}')
        if oid_error is not None:
            source_error = oid_error
            findings.append({'id': 'source_unavailable',
                             'detail': f'git rev-parse '
                                       f'{SOURCE_REVISION}:{SOURCE_PATH} failed: '
                                       f'{oid_error}'})
        else:
            source_oid = oid_output.decode('utf-8', 'replace').strip()
            blob, blob_error = git_run(
                repo_path, 'cat-file', 'blob',
                f'{SOURCE_REVISION}:{SOURCE_PATH}')
            if blob_error is not None:
                source_error = blob_error
                findings.append({'id': 'source_unavailable',
                                 'detail': f'git cat-file blob '
                                           f'{SOURCE_REVISION}:{SOURCE_PATH} '
                                           f'failed: {blob_error}'})
            else:
                source_available = True
                source_bytes = blob
                anchor_matches = (source_oid == SOURCE_BLOB_OID
                                  and sha256(blob) == SOURCE_SHA256
                                  and len(blob) == SOURCE_BYTES)
                checks.append({'id': 'source_anchor', 'ok': anchor_matches})
                if not anchor_matches:
                    findings.append({
                        'id': 'source_unavailable',
                        'detail': f'retrieved git blob {source_oid} sha256 '
                                  f'{sha256(blob)} bytes {len(blob)} is not the '
                                  f'pinned blob {SOURCE_BLOB_OID} sha256 '
                                  f'{SOURCE_SHA256} bytes {SOURCE_BYTES}; the '
                                  f'repository cannot vouch for the pinned anchor'})
                if snapshot_bytes is not None:
                    source_matches = snapshot_bytes == source_bytes
                    checks.append({'id': 'source_correspondence',
                                   'ok': source_matches})
                    if not source_matches:
                        offset = first_difference(snapshot_bytes, source_bytes)
                        source_diff = {'first_difference_offset': offset,
                                       'snapshot_bytes': len(snapshot_bytes),
                                       'source_bytes': len(source_bytes)}
                        findings.append({
                            'id': 'source_mismatch',
                            'detail': f'snapshot differs from '
                                      f'{SOURCE_REVISION}:{SOURCE_PATH} at byte '
                                      f'offset {offset} (snapshot '
                                      f'{len(snapshot_bytes)} bytes, source '
                                      f'{len(source_bytes)} bytes)'})

    if not findings:
        findings.append({'id': 'clean',
                         'detail': 'snapshot matches the pinned manifest digest '
                                   'and the pinned git blob'})

    finding = next(fid for fid in PRIORITY
                   if any(item['id'] == fid for item in findings))
    exit_code = 0 if finding == 'clean' else (1 if finding == 'source_mismatch' else 2)
    # C1 counts only correspondence failures against a verified anchor.  Pin
    # and anchor failures stay visible in integrity_result /
    # snapshot_pin_matches / source_anchor_matches and are not folded in.
    mismatches = int(source_matches is False and anchor_matches is True)
    expected_matches = None
    if manifest is not None:
        expected_matches = manifest['expected'] == finding
    integrity = ('checked' if manifest is not None and pin_matches is not None
                 else 'not_checked')
    if integrity == 'checked':
        integrity_result = 'match' if pin_matches else 'mismatch'
    else:
        integrity_result = 'not_checked'
    if source_matches is None:
        correspondence = 'unavailable'
    else:
        correspondence = 'match' if source_matches else 'mismatch'

    return {
        'schema': SCHEMA_RESULT,
        'finding': finding,
        'findings': findings,
        'checks': checks,
        'mismatches': mismatches,
        'exit': exit_code,
        'integrity': integrity,
        'integrity_result': integrity_result,
        'correspondence': correspondence,
        'pinned': pinned,
        'snapshot': str(snapshot_path),
        'snapshot_sha256': sha256(snapshot_bytes) if snapshot_bytes is not None else None,
        'snapshot_bytes': len(snapshot_bytes) if snapshot_bytes is not None else None,
        'snapshot_error': snapshot_error,
        'snapshot_pin_matches': pin_matches,
        'source_revision': SOURCE_REVISION,
        'source_path': SOURCE_PATH,
        'source_expected_oid': SOURCE_BLOB_OID,
        'source_expected_sha256': SOURCE_SHA256,
        'source_oid': source_oid,
        'source_sha256': sha256(source_bytes) if source_bytes is not None else None,
        'source_bytes': len(source_bytes) if source_bytes is not None else None,
        'source_available': source_available,
        'source_anchor_matches': anchor_matches,
        'source_matches': source_matches,
        'source_error': source_error,
        'source_diff': source_diff,
        'manifest': str(manifest['path']) if manifest is not None else None,
        'manifest_sha256': manifest['sha256'] if manifest is not None else None,
        'manifest_error': manifest_error,
        'expected_verdict': manifest['expected'] if manifest is not None else None,
        'expected_matches': expected_matches,
    }


def write_json(payload):
    sys.stdout.write(json.dumps(payload, indent=2, sort_keys=True) + '\n')


# --------------------------------------------------------------------------
# Isolated self-test.  The pinned source blob is read, read-only, from this
# repository's immutable history; every fixture, snapshot and manifest lives in
# a temporary directory and the missing-source control uses a temporary empty
# repository.  The live tree is never written.  Every case invokes this file as
# a real child CLI and asserts its exit code and stable finding id.
# --------------------------------------------------------------------------

def run_git(*arguments):
    command = ['git', '--no-pager', '--no-replace-objects'] + list(arguments)
    return subprocess.run(command, capture_output=True, text=True, check=True,
                          timeout=300, env=git_environment(None))


def invoke(arguments):
    command = [sys.executable, str(Path(__file__).resolve())] + list(arguments)
    try:
        result = subprocess.run(command, capture_output=True, text=True,
                                check=False, timeout=300)
    except subprocess.TimeoutExpired:
        return command, None, 'timeout'
    payload = None
    parse_error = None
    try:
        payload = json.loads(result.stdout)
    except ValueError as error:
        parse_error = f'stdout is not JSON: {error}'
    return command, {'exit': result.returncode, 'payload': payload,
                     'stderr': result.stderr, 'parse_error': parse_error}, None


def selftest():
    checks = []

    def record(name, command, observation, expected_exit, expected_finding,
               assertions=None, error=None):
        entry = {'name': name, 'command': command,
                 'expected_exit': expected_exit,
                 'expected_finding': expected_finding}
        if error is not None or observation is None:
            entry.update({'ok': False, 'error': error or 'no observation'})
            checks.append(entry)
            return
        payload = observation['payload'] or {}
        satisfied = {}
        ok = (observation['exit'] == expected_exit
              and payload.get('finding') == expected_finding
              and observation['parse_error'] is None)
        for key, value in (assertions or {}).items():
            satisfied[key] = payload.get(key) == value
            ok = ok and satisfied[key]
        entry.update({'ok': ok, 'exit': observation['exit'],
                      'finding': payload.get('finding'),
                      'mismatches': payload.get('mismatches'),
                      'assertions': satisfied,
                      'parse_error': observation['parse_error']})
        checks.append(entry)

    try:
        with tempfile.TemporaryDirectory(prefix='kama-round12-fidelity-') as raw:
            temp = Path(raw)
            source_repo = LANE
            empty = temp / 'empty-repo'
            run_git('init', '--quiet', str(empty))
            source, error = git_run(
                source_repo, 'cat-file', 'blob',
                f'{SOURCE_REVISION}:{SOURCE_PATH}')
            if source is None:
                raise RuntimeError(f'pinned source unavailable: {error}')
            if (len(source) != SOURCE_BYTES or sha256(source) != SOURCE_SHA256):
                raise RuntimeError('pinned source blob does not match its constants')
            head, head_error = git_run(source_repo, 'rev-parse', 'HEAD')
            if head is None:
                raise RuntimeError(f'cannot read repository HEAD: {head_error}')
            head_revision = head.decode('utf-8').strip()
            mutated = bytes([source[0] ^ 0x01]) + source[1:]
            original_digest = sha256(source)
            mutated_digest = sha256(mutated)

            def snapshot(name, data):
                path = temp / name
                path.write_bytes(data)
                return path

            def manifest(name, digest, revision=SOURCE_REVISION,
                         expected='clean'):
                path = temp / name
                path.write_text(json.dumps({
                    'schema': SCHEMA_MANIFEST,
                    'snapshot_path': SOURCE_PATH,
                    'snapshot_sha256': digest,
                    'source_revision': revision,
                    'source_path': SOURCE_PATH,
                    'source_oid': SOURCE_BLOB_OID,
                    'source_sha256': SOURCE_SHA256,
                    'source_bytes': SOURCE_BYTES,
                    'expected_verdict': expected,
                }, indent=2) + '\n')
                return path

            clean_snapshot = snapshot('clean-SOURCES.md', source)
            clean_manifest = manifest('clean-expected.json', original_digest)
            clean = invoke(['--snapshot', str(clean_snapshot), '--manifest',
                            str(clean_manifest), '--repo', str(source_repo)])
            record('clean', clean[0], clean[1], 0, 'clean',
                   {'mismatches': 0, 'source_matches': True,
                    'source_anchor_matches': True,
                    'snapshot_pin_matches': True, 'pinned': True,
                    'integrity': 'checked', 'integrity_result': 'match',
                    'correspondence': 'match'}, clean[2])

            mutant_snapshot = snapshot('mutant-SOURCES.md', mutated)
            coherent_manifest = manifest('coherent-expected.json', mutated_digest)
            coherent = invoke(['--snapshot', str(mutant_snapshot), '--manifest',
                               str(coherent_manifest), '--repo', str(source_repo)])
            record('coherent-snapshot-and-manifest-mutation', coherent[0],
                   coherent[1], 1, 'source_mismatch',
                   {'pinned': True, 'snapshot_pin_matches': True,
                    'integrity_result': 'match', 'source_matches': False,
                    'correspondence': 'mismatch', 'mismatches': 1}, coherent[2])

            tampered = invoke(['--snapshot', str(mutant_snapshot), '--manifest',
                               str(clean_manifest), '--repo', str(source_repo)])
            record('snapshot-tampered', tampered[0], tampered[1],
                   2, 'snapshot_tampered',
                   {'pinned': True, 'snapshot_pin_matches': False,
                    'integrity_result': 'mismatch',
                    'source_matches': False, 'mismatches': 1}, tampered[2])

            pin_only_manifest = manifest('pin-only-expected.json', '0' * 64)
            pin_only = invoke(['--snapshot', str(clean_snapshot), '--manifest',
                               str(pin_only_manifest), '--repo', str(source_repo)])
            record('pin-only-corruption-exact-snapshot', pin_only[0], pin_only[1],
                   2, 'snapshot_tampered',
                   {'pinned': True, 'snapshot_pin_matches': False,
                    'integrity_result': 'mismatch', 'source_matches': True,
                    'correspondence': 'match', 'mismatches': 0}, pin_only[2])

            unavailable = invoke(['--snapshot', str(clean_snapshot), '--manifest',
                                  str(clean_manifest), '--repo', str(empty)])
            record('source-unavailable', unavailable[0], unavailable[1],
                   2, 'source_unavailable',
                   {'source_available': False, 'snapshot_pin_matches': True,
                    'source_matches': None, 'mismatches': 0,
                    'correspondence': 'unavailable'}, unavailable[2])

            pinned_match = invoke(['--snapshot', str(clean_snapshot),
                                   '--manifest', 'none', '--repo', str(source_repo)])
            record('unpinned-matching-snapshot-is-not-clean', pinned_match[0],
                   pinned_match[1], 2, 'unpinned',
                   {'pinned': False, 'integrity': 'not_checked',
                    'integrity_result': 'not_checked',
                    'source_matches': True, 'mismatches': 0}, pinned_match[2])

            unpinned = invoke(['--snapshot', str(mutant_snapshot), '--manifest',
                               'none', '--repo', str(source_repo)])
            record('unpinned-source-mismatch', unpinned[0], unpinned[1],
                   1, 'source_mismatch',
                   {'pinned': False, 'source_matches': False}, unpinned[2])

            redirected = manifest('redirect-expected.json', original_digest,
                                  revision=head_revision)
            redirect = invoke(['--snapshot', str(clean_snapshot), '--manifest',
                               str(redirected), '--repo', str(source_repo)])
            record('manifest-cannot-redirect-anchor', redirect[0], redirect[1],
                   2, 'manifest_invalid', {'pinned': False}, redirect[2])

            absent = invoke(['--snapshot', str(clean_snapshot), '--manifest',
                             str(temp / 'absent-expected.json'),
                             '--repo', str(source_repo)])
            record('absent-explicit-manifest', absent[0], absent[1],
                   2, 'manifest_invalid', {'pinned': False}, absent[2])

            missing = invoke(['--snapshot', str(temp / 'absent-SOURCES.md'),
                              '--manifest', 'none', '--repo', str(source_repo)])
            record('snapshot-unavailable', missing[0], missing[1],
                   2, 'snapshot_unavailable',
                   {'snapshot_sha256': None}, missing[2])

            link = temp / 'linked-SOURCES.md'
            try:
                link.symlink_to(clean_snapshot)
                linked = invoke(['--snapshot', str(link), '--manifest', 'none',
                                 '--repo', str(source_repo)])
                record('symlink-snapshot-rejected', linked[0], linked[1],
                       2, 'snapshot_unavailable', None, linked[2])
            except OSError as error:
                record('symlink-snapshot-rejected', [], None, 2,
                       'snapshot_unavailable', error=str(error))
    except Exception as error:  # noqa: BLE001 - selftest reports, never crashes
        write_json({'schema': SCHEMA_SELFTEST, 'passed': 0,
                    'failed': len(checks), 'checks': checks,
                    'error': f'{type(error).__name__}: {error}'})
        return 2

    failed = sum(1 for entry in checks if not entry['ok'])
    write_json({'schema': SCHEMA_SELFTEST, 'passed': len(checks) - failed,
                'failed': failed, 'checks': checks})
    return 0 if failed == 0 else 1


def main(argv=None):
    parser = argparse.ArgumentParser(
        description='Check a frozen snapshot against its manifest pin and the '
                    'immutable git source blob.')
    parser.add_argument('--snapshot', default=None,
                        help=f'snapshot bytes to check (default: {DEFAULT_SNAPSHOT})')
    parser.add_argument('--manifest', default='auto',
                        help='frozen manifest path, or "auto" (default manifest '
                             'when the default snapshot is used) or "none" (no '
                             'integrity pin; source correspondence still checked '
                             'and a matching snapshot is not clean)')
    parser.add_argument('--repo', default=None,
                        help=f'git repository holding the source revision '
                             f'(default: {LANE})')
    parser.add_argument('--selftest', action='store_true',
                        help='run isolated child-CLI fixture checks in a temporary '
                             'directory; reads, never writes, the live tree')
    arguments = parser.parse_args(argv)

    if arguments.selftest:
        return selftest()

    try:
        snapshot_path = (Path(os.path.abspath(arguments.snapshot))
                         if arguments.snapshot is not None
                         else DEFAULT_SNAPSHOT)
        repo_path = (Path(arguments.repo).resolve()
                     if arguments.repo is not None else LANE)
        payload = evaluate(snapshot_path, arguments.manifest, repo_path,
                           arguments.snapshot is not None)
        write_json(payload)
        return payload['exit']
    except Exception as error:  # noqa: BLE001 - exit 1 would mean source_mismatch
        write_json({
            'schema': SCHEMA_RESULT,
            'finding': 'internal_error',
            'findings': [{'id': 'internal_error',
                          'detail': f'{type(error).__name__}: {error}'}],
            'mismatches': 0,
            'exit': 2,
            'integrity': 'not_checked',
            'pinned': False,
        })
        return 2


if __name__ == '__main__':
    sys.exit(main())
