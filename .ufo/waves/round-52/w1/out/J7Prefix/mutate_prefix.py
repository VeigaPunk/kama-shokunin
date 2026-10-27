#!/usr/bin/env python3
"""J7Prefix ablation: inside every `Restored lines (round 52)` section, prefix each
restored (non-empty, inside-fence) line with '> '; fences and blanks untouched."""
import re, sys, json, glob, os

HEAD = re.compile(rb'^(#{1,6}) +(.*?)[ \t]*$')
OPEN = re.compile(rb'^( {0,3})(`{3,}|~{3,})(.*)$')


def fence_open(line):
    m = OPEN.match(line)
    if not m:
        return None
    ch, n, info = m.group(2)[:1], len(m.group(2)), m.group(3)
    if ch == b'`' and b'`' in info:
        return None
    return (ch, n)


def fence_close(line, mark):
    ch, n = mark
    s = line.strip(b' \t')
    if not s or s[:1] != ch:
        return False
    k = 0
    while k < len(s) and s[k:k+1] == ch:
        k += 1
    return k >= n and s[k:].strip(b' \t') == b''


def mutate(path):
    data = open(path, 'rb').read()
    lines = data.split(b'\n')
    out = []
    in_sec = False
    sec_level = None
    mark = None
    n_prefixed = 0
    for line in lines:
        body = line[:-1] if line.endswith(b'\r') else line
        if mark is not None:
            if fence_close(body, mark):
                mark = None
                out.append(line)
                continue
            if body.strip(b' \t'):
                out.append(b'> ' + line)
                n_prefixed += 1
            else:
                out.append(line)
            continue
        m = HEAD.match(body)
        if m:
            level = len(m.group(1))
            is_sec = m.group(2) == b'Restored lines (round 52)'
            if is_sec:
                in_sec, sec_level = True, level
                out.append(line)
                continue
            if in_sec and level <= sec_level:
                in_sec, sec_level = False, None
            out.append(line)
            continue
        if in_sec:
            fo = fence_open(body)
            if fo:
                mark = fo
        out.append(line)
    if n_prefixed:
        open(path, 'wb').write(b'\n'.join(out))
    return n_prefixed


if __name__ == '__main__':
    root = sys.argv[1]
    os.chdir(root)
    files = ['LOG.md', 'SCORECARD.md', 'corpus/QUALITY.md', 'corpus/README.md'] + sorted(glob.glob('corpus/lessons/*.md'))
    res = {}
    for f in files:
        n = mutate(f)
        if n:
            res[f] = n
    print(json.dumps(res, indent=1, sort_keys=True))
    print('files=%d lines=%d' % (len(res), sum(res.values())))
