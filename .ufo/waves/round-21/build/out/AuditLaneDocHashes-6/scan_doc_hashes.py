#!/usr/bin/env python3
# Sweep kama-shokunin lane docs (SCORECARD.md, LOG.md, SKILL.md, corpus/**/*.md) for
# 40-hex tokens and test each token with `git cat-file -e` in the lane and fleet repos.
# Read-only: only git object reads (no index, ref, config or gc writes); writes only OUT.
# Exit 0 = evaluated (unresolved tokens are findings, not an error); 2 = could not evaluate.
import collections
import os
import pathlib
import re
import subprocess
import sys

LANE = '/home/vgpnk/Projects/shokunin/kama-shokunin'
FLEET = '/home/vgpnk/Projects/shokunin'
REV = 'a29bb84abbb8b4d328f5970a89e448330a3a42ac'
OUT = pathlib.Path(LANE, '.ufo/waves/round-21/build/out/AuditLaneDocHashes-6')
OUT.mkdir(parents=True, exist_ok=True)
ENV = dict(os.environ, GIT_NO_LAZY_FETCH='1', GIT_NO_REPLACE_OBJECTS='1')
TOK40 = re.compile(r'(?<![0-9A-Za-z])([0-9A-Fa-f]{40})(?![0-9A-Za-z])')
RUN7 = re.compile(r'(?<![0-9A-Za-z])([0-9A-Fa-f]{7,})(?![0-9A-Za-z])')
problems = []


def git(repo, *args):
    return subprocess.run(['git', '--no-replace-objects', '-C', repo, *args],
                          capture_output=True, env=ENV)


ls = git(LANE, 'ls-tree', '-r', '--name-only', REV, 'SCORECARD.md', 'LOG.md', 'SKILL.md', 'corpus')
if ls.returncode != 0:
    print('ls-tree failed', ls.returncode, ls.stderr.decode())
    sys.exit(2)
rev_files = sorted(f for f in ls.stdout.decode().splitlines() if f.endswith('.md'))
live_paths = ['SCORECARD.md', 'LOG.md', 'SKILL.md'] + [
    p.relative_to(LANE).as_posix() for p in pathlib.Path(LANE, 'corpus').rglob('*.md')]
live_files = sorted(p for p in live_paths if pathlib.Path(LANE, p).is_file())
print('rev', REV, 'files', len(rev_files), '| live files', len(live_files))
print('only-in-rev:', sorted(set(rev_files) - set(live_files)))
print('only-in-live:', sorted(set(live_files) - set(rev_files)))

views = {'rev': {}, 'live': {}}
for f in rev_files:
    b = git(LANE, 'cat-file', 'blob', f'{REV}:{f}')
    if b.returncode != 0:
        problems.append(('cat-file blob', f, b.returncode))
        continue
    views['rev'][f] = b.stdout
for f in live_files:
    try:
        views['live'][f] = pathlib.Path(LANE, f).read_bytes()
    except OSError as exc:
        problems.append(('read', f, str(exc)))
print('rev-vs-live byte-differing files:',
      [f for f in rev_files if views['rev'].get(f) != views['live'].get(f)])

occ = {'rev': [], 'live': []}
census = {'rev': collections.Counter(), 'live': collections.Counter()}
for view in ('rev', 'live'):
    for f, data in sorted(views[view].items()):
        text = data.decode('utf-8', 'replace')
        for ln, line in enumerate(text.split('\n'), 1):
            for m in RUN7.finditer(line):
                census[view][len(m.group(1))] += 1
            for m in TOK40.finditer(line):
                tok = m.group(1)
                occ[view].append(dict(file=f, line=ln, col=m.start(1) + 1, tok=tok,
                                      upper=(tok != tok.lower()),
                                      text=line.strip()[:200].replace('\t', ' ')))

uniq = sorted({o['tok'].lower() for v in occ.values() for o in v})
info = {}
for h in uniq:
    rec = {}
    for name, repo in (('lane', LANE), ('fleet', FLEET)):
        e = git(repo, 'cat-file', '-e', h)
        rec[name + '_exit'] = e.returncode
        rec[name + '_err'] = e.stderr.decode().strip()[:160]
        if e.returncode == 0:
            t = git(repo, 'cat-file', '-t', h)
            rec[name + '_type'] = t.stdout.decode().strip() if t.returncode == 0 else 'ERR%d' % t.returncode
        else:
            rec[name + '_type'] = ''
            if e.returncode != 1:
                problems.append(('cat-file -e', name, h, e.returncode))
    info[h] = rec


def status(rec):
    le, fe = rec['lane_exit'], rec['fleet_exit']
    if le == 0 and fe == 0:
        return 'resolved:lane+fleet'
    if le == 0:
        return 'resolved:lane'
    if fe == 0:
        return 'resolved:fleet'
    if le == 1 and fe == 1:
        return 'UNRESOLVED'
    return 'ERROR'


with open(OUT / 'occurrences.tsv', 'w') as fh:
    fh.write('\t'.join(['view', 'file', 'line', 'col', 'token', 'upper', 'status', 'lane_exit',
                        'fleet_exit', 'lane_type', 'fleet_type', 'text']) + '\n')
    for view in ('rev', 'live'):
        for o in occ[view]:
            rec = info[o['tok'].lower()]
            fh.write('\t'.join(str(x) for x in [
                view, o['file'], o['line'], o['col'], o['tok'], int(o['upper']),
                status(rec), rec['lane_exit'], rec['fleet_exit'], rec['lane_type'],
                rec['fleet_type'], o['text']]) + '\n')

with open(OUT / 'unique-tokens.tsv', 'w') as fh:
    fh.write('\t'.join(['token', 'status', 'lane_exit', 'fleet_exit', 'lane_type', 'fleet_type',
                        'rev_occurrences', 'live_occurrences']) + '\n')
    for h in uniq:
        rec = info[h]
        n_rev = sum(1 for o in occ['rev'] if o['tok'].lower() == h)
        n_live = sum(1 for o in occ['live'] if o['tok'].lower() == h)
        fh.write('\t'.join(str(x) for x in [h, status(rec), rec['lane_exit'], rec['fleet_exit'],
                                            rec['lane_type'], rec['fleet_type'], n_rev, n_live]) + '\n')

print('census of hex runs >=7 chars (rev view, length: count):', dict(sorted(census['rev'].items())))
print('census of hex runs >=7 chars (live view, length: count):', dict(sorted(census['live'].items())))
print('40-hex occurrences: rev', len(occ['rev']), '| live', len(occ['live']),
      '| unique tokens (lowercased)', len(uniq))
print('upper-case occurrences (rev):', sum(1 for o in occ['rev'] if o['upper']))
print('status over unique tokens:', dict(collections.Counter(status(info[h]) for h in uniq)))
print('occurrences per file (rev):', dict(collections.Counter(o['file'] for o in occ['rev'])))
print('UNRESOLVED occurrences (rev view):')
for o in occ['rev']:
    rec = info[o['tok'].lower()]
    if status(rec) != 'resolved:lane+fleet' and status(rec) != 'resolved:lane' and status(rec) != 'resolved:fleet':
        print('  %s:%d:%d %s upper=%d | %s' % (o['file'], o['line'], o['col'], o['tok'], o['upper'], o['text']))
print('problems:', problems)
sys.exit(0 if not problems and not any(status(info[h]) == 'ERROR' for h in uniq) else 2)
