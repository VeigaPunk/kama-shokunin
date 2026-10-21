#!/usr/bin/env python3
"""secret-shape-scan.py - count-only secret-shape tripwire over kama artifacts.

Advisory connector deliverable (kama round 20, ConnectKagi); not a lane gate.

Pattern inventory: copied verbatim from kagi-shokunin
corpus/transcript-scan.sh:83-96 (PATTERNS_HIT, 32 literals; PATTERNS_WARN, 5),
the janitor-transcript tripwire. `--kagi-source PATH` re-parses that file and
refuses with exit 2 (inventory-drift) when the embedded copy no longer matches.

Matching mirrors that gate:
  * hit / warn: ASCII case-insensitive substring (its SQL LIKE semantics);
  * key_shaped triage (its classify_hits, :126): an exact-case occurrence of a
    HIT literal whose next <=32 characters are all in [A-Za-z0-9_-]. The gate
    checks only the first occurrence per row; this checks every occurrence.
    `key_shaped_full32` additionally requires 32 such characters to exist.

Never prints matched text or surrounding bytes: counts, paths, line numbers
and pattern literals only.

Scope: regular files under each ROOT (symlinks are counted, never followed;
.git, .jj, __pycache__ and node_modules are pruned); with --git-dir, every
object in that git object store (--batch-all-objects: reachable, jj-kept and
unreachable blobs alike).

Exit: 0 evaluated, no key-shaped HIT; 1 evaluated, >=1 key-shaped HIT;
      2 could not evaluate (usage, unreadable or oversize file, git failure,
        inventory drift). An error is never reported as clean or as a hit.
"""
import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import tempfile

PATTERNS_HIT = (
    'op://', '-----BEGIN', 'AKIA', 'ASIA',
    'ghp_', 'gho_', 'ghu_', 'ghs_', 'ghr_', 'github_pat_',
    'xoxb-', 'xoxp-', 'xoxs-', 'xoxa-', 'xoxr-', 'xoxc-', 'xapp-',
    'sk-ant-', 'sk-proj-', 'sk-or-v1-', 'sk_live', 'sk_test',
    'gsk_', 'xai-', 'csk-', 'glpat-', 'npm_', 'AIza', 'ya29.', 'eyJhbG',
    'OP_SESSION_', 'OP_SERVICE_ACCOUNT_TOKEN',
)
PATTERNS_WARN = ('access_token', 'refresh_token', 'api_key', 'secret_key',
                 'apikey')
PRUNE = {'.git', '.jj', '__pycache__', 'node_modules'}
MAX_BYTES = 256 * 1024 * 1024
KEYCHARS = re.compile(rb'[A-Za-z0-9_-]*')


class EvalError(Exception):
    """Could-not-evaluate condition; maps to exit 2."""


def _strip_comment(line):
    out, quote = [], None
    for idx, ch in enumerate(line):
        if quote:
            if ch == quote:
                quote = None
        elif ch in ('"', "'"):
            quote = ch
        elif ch == '#' and (idx == 0 or line[idx - 1].isspace()):
            break
        out.append(ch)
    return ''.join(out)


def parse_kagi_array(text, name):
    lines = text.splitlines()
    for start, line in enumerate(lines):
        if line.startswith(name + '=('):
            break
    else:
        raise EvalError(f'inventory-drift:{name}-absent')
    body, end = [], None
    for idx in range(start, len(lines)):
        chunk = _strip_comment(lines[idx])
        if idx == start:
            chunk = chunk[len(name) + 2:]
        unquoted = re.sub(r"'[^']*'", '', chunk)
        if ')' in unquoted:
            body.append(chunk[:chunk.rindex(')')])
            end = idx
            break
        body.append(chunk)
    if end is None:
        raise EvalError(f'inventory-drift:{name}-unterminated')
    return tuple(re.findall(r"'([^']*)'", ' '.join(body))), start + 1, end + 1


def check_kagi_source(path):
    try:
        with open(path, 'rb') as fh:
            raw = fh.read()
    except OSError as exc:
        raise EvalError(f'kagi-source-unreadable:{type(exc).__name__}')
    text = raw.decode('utf-8', 'replace')
    hit, h0, h1 = parse_kagi_array(text, 'PATTERNS_HIT')
    warn, w0, w1 = parse_kagi_array(text, 'PATTERNS_WARN')
    if hit != PATTERNS_HIT or warn != PATTERNS_WARN:
        raise EvalError('inventory-drift:embedded-copy-differs')
    return {'path': path, 'sha256': hashlib.sha256(raw).hexdigest(),
            'hit_lines': f'{h0}-{h1}', 'warn_lines': f'{w0}-{w1}',
            'hit': len(hit), 'warn': len(warn)}


class Scan:
    def __init__(self):
        self.hit = {p: {'files': 0, 'occurrences': 0, 'key_shaped': 0,
                        'key_shaped_full32': 0, 'sources': []}
                    for p in PATTERNS_HIT}
        self.warn = {p: {'files': 0, 'occurrences': 0} for p in PATTERNS_WARN}
        self.locations = []
        self.sources = 0
        self.bytes = 0
        self.symlinks = 0
        self.nonregular = 0
        self.errors = []

    def feed(self, label, data):
        self.sources += 1
        self.bytes += len(data)
        low = data.lower()
        for pat in PATTERNS_WARN:
            n = low.count(pat.lower().encode())
            if n:
                self.warn[pat]['files'] += 1
                self.warn[pat]['occurrences'] += n
        for pat in PATTERNS_HIT:
            n = low.count(pat.lower().encode())
            if not n:
                continue
            rec = self.hit[pat]
            rec['files'] += 1
            rec['occurrences'] += n
            rec['sources'].append(label)
            exact, pos = pat.encode(), 0
            while (i := data.find(exact, pos)) >= 0:
                tail = data[i + len(exact):i + len(exact) + 32]
                if KEYCHARS.fullmatch(tail):
                    full = len(tail) == 32
                    rec['key_shaped'] += 1
                    rec['key_shaped_full32'] += int(full)
                    self.locations.append({
                        'source': label, 'pattern': pat, 'full32': full,
                        'line': data.count(b'\n', 0, i) + 1})
                pos = i + 1

    def walk(self, root):
        try:
            st = os.lstat(root)
        except OSError as exc:
            self.errors.append(f'{root}: {type(exc).__name__}')
            return
        if stat.S_ISLNK(st.st_mode):
            self.symlinks += 1
            return
        if stat.S_ISREG(st.st_mode):
            self.read_file(root)
            return
        if not stat.S_ISDIR(st.st_mode):
            self.nonregular += 1
            return

        def onerror(exc):
            self.errors.append(f'{exc.filename}: {type(exc).__name__}')

        for dirpath, dirnames, filenames in os.walk(root, onerror=onerror):
            for d in sorted(dirnames):
                if d in PRUNE:
                    dirnames.remove(d)
                elif os.path.islink(os.path.join(dirpath, d)):
                    self.symlinks += 1
                    dirnames.remove(d)
            dirnames.sort()
            for name in sorted(filenames):
                path = os.path.join(dirpath, name)
                try:
                    lst = os.lstat(path)
                except OSError as exc:
                    self.errors.append(f'{path}: {type(exc).__name__}')
                    continue
                if stat.S_ISLNK(lst.st_mode):
                    self.symlinks += 1
                elif not stat.S_ISREG(lst.st_mode):
                    self.nonregular += 1
                else:
                    self.read_file(path)

    def read_file(self, path):
        flags = os.O_RDONLY | os.O_NOFOLLOW | getattr(os, 'O_NONBLOCK', 0)
        try:
            fd = os.open(path, flags)
        except OSError as exc:
            self.errors.append(f'{path}: {type(exc).__name__}')
            return
        try:
            st = os.fstat(fd)
            if not stat.S_ISREG(st.st_mode):
                self.nonregular += 1
                return
            if st.st_size > MAX_BYTES:
                self.errors.append(f'{path}: oversize')
                return
            chunks = []
            while chunk := os.read(fd, 1 << 20):
                chunks.append(chunk)
            self.feed(path, b''.join(chunks))
        except OSError as exc:
            self.errors.append(f'{path}: {type(exc).__name__}')
        finally:
            os.close(fd)

    def git_objects(self, git_dir):
        cmd = ['git', '--git-dir', git_dir, 'cat-file',
               '--batch-all-objects', '--batch']
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                    stderr=subprocess.DEVNULL)
        except OSError as exc:
            raise EvalError(f'git-unavailable:{type(exc).__name__}')
        out = proc.stdout
        while header := out.readline():
            parts = header.split()
            if len(parts) != 3:
                proc.kill()
                proc.wait()
                raise EvalError('git-batch-header-unparsed')
            sha, kind, size = parts[0].decode(), parts[1], int(parts[2])
            data = out.read(size)
            out.read(1)
            if len(data) != size:
                proc.kill()
                proc.wait()
                raise EvalError('git-batch-truncated')
            if kind == b'blob':
                self.feed(f'git:{sha}', data)
        if proc.wait() != 0:
            raise EvalError(f'git-exit-{proc.returncode}')

    def result(self, kagi):
        shaped = sum(r['key_shaped'] for r in self.hit.values())
        if self.errors:
            verdict, code = 'could-not-evaluate', 2
        elif shaped:
            verdict, code = 'key-shaped-hit', 1
        else:
            verdict, code = 'no-key-shaped-hit', 0
        hit = {p: r for p, r in self.hit.items() if r['files']}
        warn = {p: r for p, r in self.warn.items() if r['files']}
        return code, {
            'schema': 'kama-r20-secret-shape-scan/v1', 'verdict': verdict,
            'kagi_source': kagi, 'sources_scanned': self.sources,
            'bytes_scanned': self.bytes, 'symlinks_skipped': self.symlinks,
            'nonregular_skipped': self.nonregular, 'errors': self.errors,
            'hit_patterns_firing': len(hit), 'hit': hit, 'warn': warn,
            'key_shaped_total': shaped, 'key_shaped_locations': self.locations,
        }


def run(argv):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('roots', nargs='*')
    ap.add_argument('--git-dir', action='append', default=[])
    ap.add_argument('--kagi-source')
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.roots and not args.git_dir:
        ap.error('nothing to scan')
    scan, kagi = Scan(), None
    try:
        if args.kagi_source:
            kagi = check_kagi_source(args.kagi_source)
        for root in args.roots:
            scan.walk(root)
        for git_dir in args.git_dir:
            scan.git_objects(git_dir)
    except EvalError as exc:
        print(f'SECRET_SHAPE_SCAN: could-not-evaluate ({exc})')
        return 2
    code, doc = scan.result(kagi)
    if args.json:
        print(json.dumps(doc, indent=1, sort_keys=True))
    else:
        print(f"SECRET_SHAPE_SCAN: {doc['verdict']} sources="
              f"{doc['sources_scanned']} bytes={doc['bytes_scanned']} "
              f"hit_patterns_firing={doc['hit_patterns_firing']} "
              f"key_shaped={doc['key_shaped_total']} "
              f"errors={len(doc['errors'])}")
    return code


def selftest():
    script = os.path.abspath(__file__)
    seeded = 'gh' + 'p_' + 'Q' * 36
    failures = []

    def child(*argv):
        cp = subprocess.run([sys.executable, script, *argv],
                            capture_output=True, text=True)
        if seeded in cp.stdout or seeded in cp.stderr:
            failures.append(f'seeded value echoed by {argv[-1:]}')
        return cp

    def expect(name, cp, code):
        if cp.returncode != code:
            failures.append(f'{name}: exit {cp.returncode} != {code}')

    with tempfile.TemporaryDirectory() as tmp:
        clean = os.path.join(tmp, 'clean')
        os.makedirs(os.path.join(clean, '.git'))
        with open(os.path.join(clean, 'prose.md'), 'w') as fh:
            fh.write('Malaysia and api_key=<placeholder>\n')
        with open(os.path.join(clean, '.git', 'x'), 'w') as fh:
            fh.write(seeded + '\n')
        dirty = os.path.join(tmp, 'dirty')
        os.makedirs(dirty)
        with open(os.path.join(dirty, 'a.txt'), 'w') as fh:
            fh.write('line one\n' + seeded + '\n')
        os.symlink('a.txt', os.path.join(dirty, 'link'))
        cp = child('--json', clean)
        expect('clean', cp, 0)
        doc = json.loads(cp.stdout or '{}')
        if doc.get('hit', {}).get('ASIA', {}).get('key_shaped') != 0 or \
                doc.get('warn', {}).get('api_key', {}).get('files') != 1:
            failures.append('clean: case-insensitive hit/warn accounting')
        cp = child('--json', dirty)
        expect('dirty', cp, 1)
        doc = json.loads(cp.stdout or '{}')
        locs = doc.get('key_shaped_locations', [])
        if [(l['pattern'], l['line'], l['full32']) for l in locs] != \
                [('ghp_', 2, True)] or doc.get('symlinks_skipped') != 1:
            failures.append(f'dirty: locations/symlink accounting {locs}')
        locked = os.path.join(tmp, 'locked.txt')
        with open(locked, 'w') as fh:
            fh.write('x\n')
        os.chmod(locked, 0)
        if os.geteuid() != 0:
            expect('unreadable', child(locked), 2)
        fake = os.path.join(tmp, 'transcript-scan.sh')
        hit = ' '.join(f"'{p}'" for p in PATTERNS_HIT)
        warn = ' '.join(f"'{p}'" for p in PATTERNS_WARN)
        with open(fake, 'w') as fh:
            fh.write(f"PATTERNS_HIT=(\n  {hit}  # comment\n)\n"
                     f"PATTERNS_WARN=({warn})\n")
        expect('kagi-match', child('--kagi-source', fake, clean), 0)
        with open(fake, 'w') as fh:
            fh.write(f"PATTERNS_HIT=(\n  {hit} 'new-' \n)\n"
                     f"PATTERNS_WARN=({warn})\n")
        expect('kagi-drift', child('--kagi-source', fake, clean), 2)
        repo = os.path.join(tmp, 'repo')
        git = ['git', '-C', repo, '-c', 'user.name=t',
               '-c', 'user.email=t@invalid', '-c', 'commit.gpgsign=false']
        subprocess.run(['git', 'init', '-q', repo], check=True)
        with open(os.path.join(repo, 'r.json'), 'w') as fh:
            fh.write('{"k": "' + seeded + '"}\n')
        subprocess.run(git + ['add', 'r.json'], check=True)
        subprocess.run(git + ['commit', '-qm', 'a'], check=True)
        os.remove(os.path.join(repo, 'r.json'))
        subprocess.run(git + ['commit', '-qam', 'b'], check=True)
        expect('tree-after-delete', child(repo), 0)
        expect('history', child('--git-dir', os.path.join(repo, '.git')), 1)
        expect('git-dir-missing',
               child('--git-dir', os.path.join(tmp, 'nope')), 2)
    for line in failures:
        print(f'FAIL {line}')
    print(f'SELFTEST: {"FAIL" if failures else "PASS"} cases=9 '
          f'failures={len(failures)}')
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(run(sys.argv[1:]))
