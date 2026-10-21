#!/usr/bin/env python3
# Candidate generation for UNRESOLVED 40-hex tokens produced by scan_doc_hashes.py (read-only).
# For each unresolved token: occurrence context, short-hash consistency on the same line,
# cross-token prefix agreement across all scanned tokens, and nearest git objects (by common
# prefix and by Hamming distance) enumerated from the lane and fleet object databases.
# Read-only: git object enumeration/reads only. Writes candidates.tsv and context.txt in OUT.
import os
import pathlib
import re
import subprocess
import sys

LANE = '/home/vgpnk/Projects/shokunin/kama-shokunin'
FLEET = '/home/vgpnk/Projects/shokunin'
OUT = pathlib.Path(LANE, '.ufo/waves/round-21/build/out/AuditLaneDocHashes-6')
ENV = dict(os.environ, GIT_NO_LAZY_FETCH='1', GIT_NO_REPLACE_OBJECTS='1')
SHORT = re.compile(r'(?<![0-9A-Za-z])([0-9A-Fa-f]{7,39})(?![0-9A-Za-z])')


def git(repo, *args):
    return subprocess.run(['git', '--no-replace-objects', '-C', repo, *args],
                          capture_output=True, env=ENV)


def load_tsv(path):
    lines = pathlib.Path(path).read_text(encoding='utf-8').splitlines()
    hdr = lines[0].split('\t')
    return [dict(zip(hdr, ln.split('\t'))) for ln in lines[1:]]


def lcp(a, b):
    n = 0
    for x, y in zip(a, b):
        if x != y:
            break
        n += 1
    return n


def ham(a, b):
    return sum(1 for x, y in zip(a, b) if x != y)


uniq = load_tsv(OUT / 'unique-tokens.tsv')
occ = [r for r in load_tsv(OUT / 'occurrences.tsv') if r['view'] == 'rev']
unres = [u['token'] for u in uniq if u['status'] == 'UNRESOLVED']
all_tokens = sorted({u['token'] for u in uniq})
print('unresolved unique tokens:', len(unres))
print('unresolved occurrences (rev):', sum(1 for r in occ if r['token'] in unres))

objs = {}
for name, repo in (('lane', LANE), ('fleet', FLEET)):
    r = git(repo, 'cat-file', '--batch-all-objects', '--batch-check=%(objectname) %(objecttype)')
    if r.returncode != 0:
        print('object enumeration failed', name, r.returncode, r.stderr.decode())
        sys.exit(2)
    for ln in r.stdout.decode().splitlines():
        h, t = ln.split(' ')
        objs.setdefault(h, (name, t))
names = list(objs)
print('objects enumerated (lane+fleet, deduplicated):', len(names))
bad = [n for n in names if len(n) != 40]
print('non-40-char object names:', len(bad))

ctx_lines = {}
ctx_out = []
rows = []
for t in unres:
    scored = [(lcp(t, o), ham(t, o), o) for o in names]
    top_lcp = sorted(scored, key=lambda x: (-x[0], x[1]))[:3]
    top_ham = sorted(scored, key=lambda x: (x[1], -x[0]))[:3]
    cross = sorted(((lcp(t, x), x) for x in all_tokens if x != t and lcp(t, x) >= 7), reverse=True)
    occs = [r for r in occ if r['token'] == t]
    loc = []
    for r in occs:
        f = r['file']
        if f not in ctx_lines:
            ctx_lines[f] = pathlib.Path(LANE, f).read_text(encoding='utf-8', errors='replace').split('\n')
        line = ctx_lines[f][int(r['line']) - 1]
        i = int(r['col']) - 1
        win = line[max(0, i - 120): i + 40 + 90].replace('\t', ' ')
        shorts = SHORT.findall(line)
        consistent = sorted({s.lower() for s in shorts if t.startswith(s.lower())})
        conflict = sorted({s.lower() for s in shorts if not t.startswith(s.lower()) and lcp(t, s.lower()) >= 5})
        loc.append('%s:%s:%s' % (f, r['line'], r['col']))
        ctx_out.append('%s:%s:%s %s\n    ctx: %s\n    short-prefix-consistent: %s | short-conflicting: %s' % (
            f, r['line'], r['col'], t, win, consistent or '-', conflict or '-'))
    rows.append([t, ' ; '.join(loc), len(occs),
                 ' ; '.join('%s/%s/%s lcp=%d ham=%d' % (o[:12], objs[o][0], objs[o][1], l, h)
                            for l, h, o in top_lcp),
                 ' ; '.join('%s/%s/%s lcp=%d ham=%d' % (o[:12], objs[o][0], objs[o][1], l, h)
                            for l, h, o in top_ham),
                 ' ; '.join('%s(lcp%d)' % (x[:12], l) for l, x in cross) or '-'])

with open(OUT / 'candidates.tsv', 'w') as fh:
    fh.write('\t'.join(['token', 'occurrences', 'n_occ', 'nearest_by_prefix', 'nearest_by_hamming',
                        'other_tokens_sharing_prefix>=7']) + '\n')
    for row in rows:
        fh.write('\t'.join(str(x) for x in row) + '\n')
with open(OUT / 'context.txt', 'w', encoding='utf-8') as fh:
    fh.write('\n'.join(ctx_out) + '\n')

for row in rows:
    print(row[0], '| occ', row[2], '|', row[1])
    print('   nearest-prefix:', row[3])
    print('   nearest-hamming:', row[4])
    print('   other tokens sharing prefix>=7:', row[5])
print('wrote candidates.tsv and context.txt')
sys.exit(0)
