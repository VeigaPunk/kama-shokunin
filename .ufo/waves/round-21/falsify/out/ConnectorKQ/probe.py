#!/usr/bin/env python3
"""Offline, revision-pinned ConnectorPatterns probes; never starts a server."""
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import types
from unittest.mock import patch

LANE = Path('/home/vgpnk/Projects/shokunin/kama-shokunin')
REV = 'a6617149722c73d90e142fbdc8154d6967055f7e'
OUT = LANE / '.ufo/waves/round-21/falsify/out/ConnectorKQ'
WORK = Path('/tmp/kama-r21-ConnectorKQ')
ENV = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
ENV.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM='1', PYTHONDONTWRITEBYTECODE='1')
records = []

def command(argv, **kwargs):
    result = subprocess.run(list(map(str, argv)), capture_output=True, text=True,
                            env=ENV, timeout=60, **kwargs)
    records.append({'argv': list(map(str, argv)), 'exit': result.returncode,
                    'stdout': result.stdout, 'stderr': result.stderr})
    return result

def source(path):
    result = command(['git', '-C', LANE, 'show', f'{REV}:{path}'])
    assert result.returncode == 0, result.stderr
    # Source itself is already committed; avoid duplicating its full text in evidence.
    records[-1]['stdout'] = f'[source loaded: {len(result.stdout)} characters]'
    return result.stdout

def module(name, path):
    text = source(path)
    mod = types.ModuleType(name)
    mod.__file__ = str(LANE / path)
    sys.modules[name] = mod
    exec(compile(text, mod.__file__, 'exec'), mod.__dict__)
    return mod, text

live, live_text = module('connector_live', 'tools/kama-llamacpp-live.py')
audit, audit_text = module('connector_audit', 'tools/report-landing-audit.py')
controls, controls_text = module('connector_controls', 'tests/llamacpp-live/controls.py')
census, census_text = module('connector_census', 'tools/error-verdict-census.py')
probe_text = source('tools/kama-probe.sh')
results = {'revision': REV}

# Identity omission: a read fault is swallowed, although subsequent access succeeds.
tree_dir = WORK / 'install'
tree_dir.mkdir()
server = tree_dir / 'llama-server'
server.write_bytes(b'server')
aux = tree_dir / 'aux.so'
aux.write_bytes(b'library')
normal_tree, normal_digest = live.install_tree(str(server))
real_sha = live.sha256_file
def fail_aux(path):
    if Path(path) == aux:
        raise OSError('injected read failure')
    return real_sha(path)
with patch.object(live, 'sha256_file', side_effect=fail_aux):
    partial_tree, partial_digest = live.install_tree(str(server))
    links, links_digest, problems = live.install_links(str(server))
link = tree_dir / 'libalias.so'
link.symlink_to('aux.so')
with patch.object(live.os, 'readlink', side_effect=OSError('injected readlink failure')):
    rejected_links = live.install_links(str(server))
results['install'] = {'normal_members': sorted(normal_tree), 'partial_members': sorted(partial_tree),
    'partial_digest_present': partial_digest is not None, 'subsequent_link_problems': problems,
    'readlink_failure_problems': rejected_links[2],
    'scope': 'function sequence only; no producer launch or gate acceptance claimed'}

# Actual CLI on isolated Git fixtures: case-only change in a nonexistent full hash.
repos = [WORK / 'lane', WORK / 'fleet']
for repo in repos:
    repo.mkdir()
    assert command(['git', '-C', repo, 'init', '-q', '-b', 'master']).returncode == 0

def commit(repo, author, subject):
    cmd = ['git', '-C', repo, '-c', 'user.name=' + author, '-c', 'user.email=probe@example.invalid',
           '-c', 'commit.gpgsign=false', 'commit', '-q', '--allow-empty', '-m', subject]
    assert command(cmd).returncode == 0
    result = command(['git', '-C', repo, 'rev-parse', 'HEAD'])
    assert result.returncode == 0
    return result.stdout.strip()

valid = commit(repos[0], 'kama-shokunin', 'round-777: scoped member')
foreign = commit(repos[0], 'Integrator', 'round-777: foreign author')
variant = commit(repos[0], 'kama-shokunin', 'round-777 (hyaku phase 2): variant subject')
commit(repos[1], 'Fixture', 'fixture root')
audit_path = WORK / 'report-landing-audit.py'
audit_path.write_text(audit_text)
audit_cases = {}
for label, token in [('lower', 'deadbeef' * 5), ('upper', 'DEADBEEF' * 5)]:
    report = WORK / (label + '.md')
    report.write_text('## Landed changes\n' + valid + '\n## Other\n' + token + '\n')
    argv = [sys.executable, audit_path, '--lane-repo', repos[0], '--fleet-repo', repos[1],
            '--rounds', '777', '--report', '777=' + str(report), '--no-errata', '--json']
    result = command(argv)
    doc = json.loads(result.stdout)
    audit_cases[label] = {'exit': result.returncode, 'summary': doc['summary'],
                           'required': doc['results'][0]['required'],
                           'defects': doc['results'][0]['defects']}
results['audit'] = {'cases': audit_cases, 'fixture_commits': {'scoped': valid, 'foreign': foreign, 'variant': variant},
                    'round_population': audit.round_commits(repos[0], 'master', 'kama', 777)}

# Execute only the committed extraction function, never the networked probe entry point.
served = probe_text[probe_text.index('served_ids() {'):probe_text.index('# drop directory, strip ONE trailing .gguf')]
extract_cases = {}
for label, content in [('mixed', json.dumps({'data': [{'id': 'canonical'}], 'models': [{'id': 'secondary'}], 'id': 'top'})),
                       ('malformed', '{'), ('primary', json.dumps({'data': [{'id': 'canonical'}]}))]:
    body = WORK / ('body-' + label + '.json')
    body.write_text(content)
    result = command(['bash', '-c', 'HAVE_PY=1\n' + served + '\nserved_ids "$1"', 'probe-function', body])
    # The exact function text lives at the pinned source; keep command record compact.
    records[-1]['argv'][2] = '[exact pinned served_ids function; HAVE_PY=1; served_ids "$1"]'
    extract_cases[label] = {'exit': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}
results['served_ids'] = extract_cases

# Registry format boundaries; no binding or networking occurs.
ports = {}
for label, content in [('actual', (LANE / 'registry/endpoint-consumers.tsv').read_text()),
                       ('ipv4', 'http://127.0.0.1:45678/v1'),
                       ('hostname', 'http://models.internal:45678/v1'),
                       ('ipv6', 'http://[2001:db8::2]:45678/v1'),
                       ('overlong', '--port 123456')]:
    fixture = WORK / ('registry-' + label + '.tsv')
    fixture.write_text(content)
    with patch.object(live, 'REGISTRY', fixture):
        ports[label] = sorted(live.refused_ports())
results['refused_ports'] = ports

# Cleanup read failures: no child is launched, and all signal operations are mocked.
fake_dir = WORK / 'fake'
fake_dir.mkdir()
cleanup = {}
for label, content in [('valid', '999998'), ('malformed', '999998 broken'), ('missing', None)]:
    pidfile = fake_dir / 'fake.pid'
    if content is None:
        pidfile.unlink(missing_ok=True)
    else:
        pidfile.write_text(content)
    with patch('builtins.open', return_value=io.BytesIO(str(fake_dir / 'fake_server.py').encode())), \
         patch.object(controls.os, 'getpgid', return_value=123456), \
         patch.object(controls.os, 'kill') as kill, patch.object(controls.os, 'killpg') as killpg:
        value = controls._kill_fake(fake_dir)
        cleanup[label] = {'return': value, 'signal_calls': kill.call_count + killpg.call_count}
results['cleanup'] = cleanup

# Registry membership versus explicitly scoped selftest execution.
rows = json.loads(source('registry/error-injection-cells.json'))
results['census'] = {'registered': len(rows), 'survivor_selftest_cells': len([r for r in rows if r['instrument'] == census.SURVIVORS]),
                     'by_instrument': {k: sum(r['instrument'] == k for r in rows) for k in census.MODES}}
census_path = WORK / 'error-verdict-census.py'
census_path.write_text(census_text)
result = command([sys.executable, census_path, '--selftest', '--lane', LANE,
                  '--cells', LANE / 'registry/error-injection-cells.json',
                  '--fixtures', LANE / 'registry/error-injection-fixtures'])
results['census']['selftest'] = {'exit': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}

# Pinned line anchors, not potentially evolving worktree line numbers.
anchors = {}
for path, text, needles in [
    ('tools/kama-llamacpp-live.py', live_text, ['def install_tree(', 'except OSError:', 'def install_links(', 'def refused_ports(', "tree, tree_sha = install_tree(server_real)"]),
    ('tools/report-landing-audit.py', audit_text, ['FULL =', 'ABBREV =', 'def round_commits(', 'if author ==']),
    ('tools/kama-probe.sh', probe_text, ['served_ids()', 'except Exception:', 'for g in groups:', 'break']),
    ('tools/error-verdict-census.py', census_text, ['for cell in (r for r in rows', 'print(f"selftest: ok']),
    ('tests/llamacpp-live/controls.py', controls_text, ['def _kill_fake(', 'except (OSError, ValueError):'])]:
    anchors[path] = {needle: [i for i, line in enumerate(text.splitlines(), 1) if needle in line] for needle in needles}
results['anchors'] = anchors
(OUT / 'results.json').write_text(json.dumps(results, indent=2) + '\n')
(OUT / 'commands.json').write_text(json.dumps(records, indent=2) + '\n')
print(json.dumps(results, indent=2))
