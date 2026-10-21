#!/usr/bin/env python3
"""Census of `SOURCES.md:<line>` pointers at one lane revision (read-only, stdlib).

Population: every line printed by `git grep -n 'SOURCES.md:[0-9]' REV`. Each
explicit token `[prefix]SOURCES.md:<spec>` (spec = comma list of N or N-M) is
split into elements. For every element:

  writer  the commit that added the token to its file: the line's blame commit
          when that commit raised the token's occurrence count, else the newest
          older pickaxe commit (`git log -S`) that raised it;
  frame   corpus/SOURCES.md at the writer, or at the writer's parent when only
          the parent's cited lines carry the context's S-ids/quotes (seats read
          the working tree before the writer commit landed);
  status  cited frame lines mapped onto REV with difflib (autojunk off):
          holds      every line equal at the same number;
          shifted    every line equal at another number (new range reported);
          edited     not all lines equal; the same row S-id/paragraph is found;
          oob        element beyond REV's line count;
          other-file the token names a different SOURCES.md (frozen copy,
                     another lane) or a revision-pinned `<rev>:` blob.
  content S-ids/quotes near the token found in the frame lines (yes/no/n-a);
          `no` means the pointer missed its own subject when written.
  cause   first corpus/SOURCES.md commit after the frame whose cited lines differ.

Usage: pointer-census.py REPO REV OUTDIR
Writes OUTDIR/pointer-census.tsv and OUTDIR/stale-ledger.tsv; prints a summary.
Exit 0 on success; 2 when REPO/REV is unusable or OUTDIR is missing.
"""
import difflib
import os
import re
import subprocess
import sys

SRC = 'corpus/SOURCES.md'
TOKEN_RE = re.compile(
    r'(?P<prefix>(?:[0-9a-f]{7,40}(?:…)?:)?[\w./~-]*)SOURCES\.md:'
    r'(?P<spec>\d{1,4}(?:\s?[-–]\s?\d{1,4})?(?:\s?,\s?\d{1,4}(?:\s?[-–]\s?\d{1,4})?)*)')
SID_RE = re.compile(r'S\d{3}')
QUOTE_RE = re.compile(r'"([^"]{6,})"|“([^”]{6,})”')


def git(repo, *args, ok=(0,)):
    r = subprocess.run(['git', '-C', repo, *args], capture_output=True, text=True)
    if r.returncode not in ok:
        raise RuntimeError(f"git {' '.join(args)} -> {r.returncode}: {r.stderr.strip()}")
    return r


_show = {}


def show(repo, rev, path):
    key = (rev, path)
    if key not in _show:
        r = git(repo, 'show', f'{rev}:{path}', ok=(0, 128))
        _show[key] = r.stdout.split('\n')[:-1] if r.returncode == 0 else None
    return _show[key]


_parent = {}


def parent(repo, rev):
    if rev not in _parent:
        r = git(repo, 'rev-parse', '--verify', '-q', f'{rev}^', ok=(0, 1))
        _parent[rev] = r.stdout.strip() or None
    return _parent[rev]


def is_ancestor(repo, a, b):
    return git(repo, 'merge-base', '--is-ancestor', a, b, ok=(0, 1)).returncode == 0


def count(repo, rev, path, needle):
    body = show(repo, rev, path) if rev else None
    return 0 if body is None else '\n'.join(body).count(needle)


def elements(spec):
    out = []
    for part in re.split(r'\s?,\s?', spec):
        a, _, b = re.sub(r'\s', '', part).replace('–', '-').partition('-')
        lo, hi = int(a), int(b or a)
        out.append((lo, hi) if hi >= lo else (lo, lo))
    return out


def writer_of(repo, rev, path, lineno, literal):
    porc = git(repo, 'blame', '--porcelain', '-L', f'{lineno},{lineno}', rev, '--', path).stdout
    blame = porc.split()[0]
    bpath = re.search(r'^filename (.+)$', porc, re.M).group(1)
    if count(repo, blame, bpath, literal) > count(repo, parent(repo, blame), bpath, literal):
        return blame, 'blame'
    log = git(repo, 'log', '--format=%H', '-S', literal, blame, '--', bpath).stdout.split()
    for c in log:
        if count(repo, c, bpath, literal) > count(repo, parent(repo, c), bpath, literal):
            return c, 'pickaxe'
    return blame, 'blame-unverified'


def norm(s):
    return re.sub(r'\s+', ' ', s.replace('`', '')).strip().lower()


def content_hit(context, cited):
    """yes/no/n-a: do the S-ids and quotes nearest the token occur in the cited lines?"""
    text = norm(' '.join(cited))
    sids = SID_RE.findall(context)
    quotes = [q for pair in QUOTE_RE.findall(context) for q in pair if q]
    frags = [f.strip() for q in quotes for f in re.split(r'…|\.\.\.', q) if len(f.strip()) >= 8]
    if not sids and not frags:
        return 'n-a'
    hit = any(s.lower() in text for s in sids) or any(norm(f) in text for f in frags)
    return 'yes' if hit else 'no'


def line_map(old, new):
    m = {}
    sm = difflib.SequenceMatcher(None, old, new, autojunk=False)
    for tag, i1, i2, j1, _ in sm.get_opcodes():
        if tag == 'equal':
            for k in range(i2 - i1):
                m[i1 + k + 1] = j1 + k + 1
    return m


def classify(frame_lines, rev_lines, lo, hi):
    if frame_lines is None or hi > len(frame_lines):
        return 'oob-at-frame', ''
    m = line_map(frame_lines, rev_lines)
    mapped = [m.get(n) for n in range(lo, hi + 1)]
    if all(x is not None for x in mapped):
        if mapped == list(range(lo, hi + 1)):
            return 'holds', f'{lo}' if lo == hi else f'{lo}-{hi}'
        if mapped == list(range(mapped[0], mapped[0] + hi - lo + 1)):
            return 'shifted', f'{mapped[0]}' if lo == hi else f'{mapped[0]}-{mapped[-1]}'
        return 'shifted', ','.join(str(x) for x in mapped)
    if hi > len(rev_lines):
        status = 'oob'
    else:
        status = 'edited'
    sid = SID_RE.match(frame_lines[lo - 1].lstrip('| ')) if frame_lines[lo - 1].startswith('| S') else None
    if sid:
        rows = [i + 1 for i, t in enumerate(rev_lines) if t.startswith(f'| {sid.group(0)} |')]
        if rows:
            return status, f'{rows[0]} (row {sid.group(0)})'
    near = [x for x in mapped if x is not None]
    return status, (f'~{near[0]}' if near else '?')


def main(argv):
    if len(argv) != 4 or not os.path.isdir(argv[3]):
        print('usage: pointer-census.py REPO REV OUTDIR (OUTDIR must exist)', file=sys.stderr)
        return 2
    repo, rev, outdir = argv[1:]
    try:
        rev = git(repo, 'rev-parse', '--verify', f'{rev}^{{commit}}').stdout.strip()
        rev_lines = show(repo, rev, SRC)
        if rev_lines is None:
            raise RuntimeError(f'{SRC} absent at {rev}')
        hist = git(repo, 'log', '--format=%H', '--reverse', rev, '--', SRC).stdout.split()
        grep = git(repo, 'grep', '-n', 'SOURCES.md:[0-9]', rev, ok=(0, 1)).stdout.splitlines()
    except (RuntimeError, OSError) as e:
        print(f'unusable: {e}', file=sys.stderr)
        return 2
    rows, ledger = [], []
    for g in grep:
        _, path, lineno, text = g.split(':', 3)
        lineno = int(lineno)
        for t in TOKEN_RE.finditer(text):
            literal = t.group(0)
            prefix, spec = t.group('prefix'), t.group('spec')
            ctx = text[max(0, t.start() - 120):t.end() + 160]
            pinned = bool(re.match(r'[0-9a-f]{7,40}', prefix))
            lane = prefix in ('', 'corpus/', 'R/corpus/') or prefix.endswith('kama-shokunin/corpus/')
            writer, how = writer_of(repo, rev, path, lineno, 'SOURCES.md:' + spec)
            wpar = parent(repo, writer)
            fw, fp = show(repo, writer, SRC), show(repo, wpar, SRC) if wpar else None
            for lo, hi in elements(spec):
                frame, flines = writer[:9], fw
                cw = content_hit(ctx, fw[lo - 1:hi]) if fw and hi <= len(fw) else 'oob'
                cp = content_hit(ctx, fp[lo - 1:hi]) if fp and hi <= len(fp) else 'oob'
                if cw in ('no', 'oob') and cp == 'yes':
                    frame, flines = writer[:9] + '^', fp
                content = cp if frame.endswith('^') else cw
                if pinned:
                    status, new = 'pinned-rev', ''
                elif not lane:
                    status, new = 'other-file', ''
                elif flines is None:
                    status, new = 'no-frame', ''
                else:
                    status, new = classify(flines, rev_lines, lo, hi)
                cause = ''
                if status not in ('holds', 'other-file', 'pinned-rev', 'no-frame') and flines is not None:
                    base = writer if not frame.endswith('^') else wpar
                    cited = flines[lo - 1:hi]
                    for c in hist:
                        if c == base or not is_ancestor(repo, base, c):
                            continue
                        body = show(repo, c, SRC)
                        if body[lo - 1:hi] != cited:
                            cause = c[:7]
                            break
                ftxt = ' / '.join(x.strip() for x in (flines or [])[lo - 1:hi])[:110]
                rtxt = ' / '.join(x.strip() for x in rev_lines[lo - 1:hi])[:110]
                el = f'{lo}' if lo == hi else f'{lo}-{hi}'
                rows.append([path, str(lineno), literal, el, writer[:9], how, frame, content,
                             status, new, cause, ftxt.replace('\t', ' '), rtxt.replace('\t', ' ')])
    hdr = ['file', 'line', 'token', 'element', 'writer', 'writer_how', 'frame', 'content_at_frame',
           'status', 'rev_location', 'cause', 'frame_text', 'rev_text']
    with open(os.path.join(outdir, 'pointer-census.tsv'), 'w') as f:
        f.write('\t'.join(hdr) + '\n')
        for r in rows:
            f.write('\t'.join(r) + '\n')
    tally = {}
    for r in rows:
        grp = 'corpus' if not r[0].startswith('.ufo/') else '.ufo'
        tally[(grp, r[8])] = tally.get((grp, r[8]), 0) + 1
    shifted_by_s057 = [r for r in rows if r[10] == '7229fa9']
    changed = [r for r in rows if r[8] not in ('holds', 'other-file', 'pinned-rev')]
    with open(os.path.join(outdir, 'stale-ledger.tsv'), 'w') as f:
        f.write('\t'.join(['file', 'line', 'token', 'element', 'writer', 'frame',
                           'content_at_frame', 'status', 'rev_location', 'cause']) + '\n')
        for r in changed:
            f.write('\t'.join([r[0], r[1], r[2], r[3], r[4], r[6], r[7], r[8], r[9], r[10]]) + '\n')
    with open(os.path.join(outdir, 's057-stale-table.tsv'), 'w') as f:
        f.write('\t'.join(['file', 'line', 'token', 'element', 'writer', 'old_text',
                           'current_location', 'cause']) + '\n')
        for r in shifted_by_s057:
            f.write('\t'.join([r[0], r[1], r[2], r[3], r[4], r[11], r[9], r[10]]) + '\n')
    print(f's057_caused_elements={len(shifted_by_s057)} mechanically_changed_elements={len(changed)}')
    print('content_at_frame=no:', sum(1 for r in rows if r[7] == 'no'))
    print(f'rev={rev} grep_lines={len(grep)} elements={len(rows)} '
          f'tokens={len({(r[0], r[1], r[2]) for r in rows})}')
    for (grp, st), n in sorted(tally.items()):
        print(f'{grp}\t{st}\t{n}')
    print('content_at_frame=no:', sum(1 for r in rows if r[7] == 'no'))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
