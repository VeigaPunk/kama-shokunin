#!/usr/bin/env python3
"""probe-append-partial.py - round-46 seat S9Lesson, proposed complement to
tools/append-only-audit.py for the `partial` status (round-45 lesson row 5;
round-46 C2 base leg).

`append-only-audit.py` classes a mass deletion as restored / partial /
unrestored by counting exact deleted line texts that the audited revision holds
again. It cannot tell a `partial` caused by **supersession** (the deleted line
was replaced by a newer line carrying the same key, e.g. a SCORECARD head row
re-anchored to a new sha256) from one caused by **loss**. C2 exits 1 on any
partial, so a clean history with two supersessions fails its own base leg.

This probe re-derives each partial event from the same definitions (first-parent
`-U0` diff, deleted `-` lines, presence at --to as exact text) and classifies
every missing deleted line:
  key          table row (starts `|`): the first non-empty cell, stripped
               (the axis name of a head row); otherwise the first six
               whitespace tokens, lowercased
  superseded   some line of the file at --to has the same key and different text
  prose-dropped  the line is not a table row and no line at --to shares its key
               (a sentence removed when the block was rewritten, no replacement
               owed)
  lost         the line is a table row and no line at --to carries its key: a
               record disappeared, not a re-anchoring
Output: `partial <commit12> <file> missing=N superseded=S lost=L` then
`superseded: <key>` / `lost: <line>` lines, then `summary partials=P missing=M
superseded=S lost=L`.
Exit: 0 no lost line; 1 at least one lost line; 2 could not evaluate.
Read-only. `--inject LINE` adds a synthetic missing line to every event, so the
loss branch can be shown to fire without a fixture repository.

Usage: probe-append-partial.py --repo DIR --to REV [--inject LINE] [--json]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys


def git(repo, *args):
    p = subprocess.run(['git', '-C', repo, *args], capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError('git %s: %s' % (' '.join(args)[:80], p.stderr.strip()[:200]))
    return p.stdout


def key(line):
    s = line.strip()
    if s.startswith('|'):
        for cell in s.split('|')[1:]:
            if cell.strip():
                return 'row:' + cell.strip()
        return 'row:' + s
    return 'prose:' + ' '.join(s.split()[:6]).lower()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', required=True)
    ap.add_argument('--to', required=True)
    ap.add_argument('--inject', default=None)
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()
    try:
        tip = git(args.repo, 'rev-parse', args.to).strip()
        audit = subprocess.run(
            ['python3', 'tools/append-only-audit.py', '--repo', args.repo,
             '--to', tip, '--json'], capture_output=True, text=True, cwd=args.repo)
        data = json.loads(audit.stdout)
    except (RuntimeError, ValueError, OSError) as exc:
        print('could-not-evaluate: %s' % exc)
        return 2
    events = [e for e in data['events'] if e.get('status') == 'partial']
    total = sup = lost_n = 0
    rows = []
    for e in events:
        full = git(args.repo, 'rev-parse', e['commit']).strip()
        diff = git(args.repo, 'diff', '--no-renames', '-U0', '%s^1' % full, full,
                   '--', e['file'])
        deleted = [ln[1:] for ln in diff.splitlines()
                   if ln.startswith('-') and not ln.startswith('---')]
        file_now = git(args.repo, 'show', '%s:%s' % (tip, e['file'])).splitlines()
        now = set(file_now)
        now_keys = {}
        for ln in file_now:
            now_keys.setdefault(key(ln), ln)
        missing = [ln for ln in deleted if ln not in now]
        if args.inject:
            missing = missing + [args.inject]
        sup_lines, lost_lines, prose = [], [], []
        for ln in missing:
            k = key(ln)
            if k in now_keys and now_keys[k].strip() != ln.strip():
                sup_lines.append((k, now_keys[k].strip()))
            elif not ln.strip().startswith('|'):
                prose.append(ln)
            else:
                lost_lines.append(ln)
        total += len(missing)
        sup += len(sup_lines)
        lost_n += len(lost_lines)
        rows.append({'commit': e['commit'][:12], 'file': e['file'],
                     'missing': len(missing), 'superseded': len(sup_lines),
                     'lost': len(lost_lines),
                     'prose_dropped': len(prose),
                     'prose': prose,
                     'superseded_keys': [k for k, _ in sup_lines],
                     'lost_lines': lost_lines,
                     'replaced_by': {k: v[:120] for k, v in sup_lines}})
    if args.json:
        print(json.dumps({'to': tip, 'partials': rows,
                          'summary': {'partials': len(events), 'missing': total,
                                      'superseded': sup, 'lost': lost_n}}, indent=1))
        return 1 if lost_n else 0
    for r in rows:
        print('partial %s %s missing=%d superseded=%d prose-dropped=%d lost=%d' % (
            r['commit'], r['file'], r['missing'], r['superseded'],
            r['prose_dropped'], r['lost']))
        for k in r['superseded_keys']:
            print('  superseded: %s' % k)
        for ln in r['prose']:
            print('  prose-dropped: %s' % ln[:110])
        for ln in r['lost_lines']:
            print('  lost: %s' % ln[:110])
    prose_n = sum(r['prose_dropped'] for r in rows)
    print('summary partials=%d missing=%d superseded=%d prose-dropped=%d lost=%d' % (
        len(events), total, sup, prose_n, lost_n))
    return 1 if lost_n else 0


if __name__ == '__main__':
    sys.exit(main())
