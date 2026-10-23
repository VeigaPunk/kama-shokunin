#!/usr/bin/env python3
"""Source-only policy: extract using base text; no checking or history lookup."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

ROOT = Path('/tmp/kama-r29-w2-RerunCtlSourceBounds/policy-out')
REPO = '/tmp/kama-r29-w2-RerunCtlSourceBounds/repo'
BASE = '2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d'
FILES = ('SCORECARD.md', 'SHONEN.md')
HEADING = '## Round 29 — self-assessment corrections'
EXT = r'(?:md|py|sh|json|jsonl|tsv|txt|out|conf|cpp|yml|yaml|toml|err|log)'
RE_P = re.compile(r'(?<![\w./~:-])((?:[\w.-]+/)*[\w.-]+\.' + EXT + r'):(\d+)(?:[-–](\d+))?(?![\w])')
RE_Q = re.compile(r'`([^`\n]{6,200})`')
Q_WORD = re.compile(r'=|\b(?:met|registered|counted|stale|observed|verified|RESULT)\b')
Q_CMD = ('python3', 'python', 'bash', 'sh ', 'git', 'node', './', 'tools/', '/')
UPSTREAM = ('llama.cpp', 'upstream', 'ufo-fsd', '@')
RE_HN = re.compile(r'`((?:[\w.-]+/)*[\w.-]+\.' + EXT + r')`'
                   r'(?: (md5|sha256) `?([0-9a-f]{8,64})`?)?(?: \((\d+) lines\b)?')
RE_T = re.compile(r'\b(20\d\d-\d\d-\d\d)(?:T| ~|T~)(\d\d):(\d\d)(?::(\d\d))?Z')
RE_HEX = re.compile(r'(?<![0-9a-zA-Z])([0-9a-f]{7,40})(?![0-9a-zA-Z])')
RE_CWORD = re.compile(r'\b(?:at|base|tip|commit|commits|epoch|revision|rev|measured) `?([0-9a-f]{7,40})(?![0-9a-zA-Z])')


def bounded_write(path, data):
    data = data.encode() if isinstance(data, str) else data
    if not len(data) < 1024 * 1024:
        raise RuntimeError(f'write exceeds bound: {path}')
    path.write_bytes(data)


class Repo:
    def __init__(self):
        self.text = {}
        env = {k: v for k, v in os.environ.items()
               if k not in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE',
                            'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES',
                            'GIT_REPLACE_REF_BASE')}
        for fname in FILES:
            p = subprocess.run(['/usr/bin/timeout', '30', '/usr/bin/git',
                                '--no-replace-objects', '-C', REPO,
                                'show', f'{BASE}:{fname}'], env=env,
                               capture_output=True, timeout=35, check=True)
            if len(p.stdout) >= 1024 * 1024:
                raise RuntimeError('base text exceeds bound')
            self.text[fname] = p.stdout

    def blob(self, rev, fname):
        if rev != BASE or fname not in FILES:
            raise RuntimeError('policy attempted an out-of-bounds read')
        return self.text[fname]


def blame(repo, fname):
    # Extractor needs one W label per line; source-only policy never resolves W.
    lines = repo.blob(BASE, fname).decode().split('\n')
    if lines and lines[-1] == '':
        lines.pop()
    return ['NOT_READ_SOURCE_ONLY'] * len(lines)


def in_lane(path: str) -> bool:
    return not (path.startswith('../') or path.startswith('/') or path.startswith('~')
                or '://' in path)


def measured_cells(lines: list[str]) -> dict[int, str]:
    cells, col = {}, None
    for i, line in enumerate(lines):
        if line.startswith('|'):
            cols = [c.strip() for c in line.strip().strip('|').split('|')]
            if any(c.lower() == 'measured commit' for c in cols):
                col = [c.lower() for c in cols].index('measured commit')
                continue
            if col is not None and not set(line.replace('|', '').strip()) <= set('-: '):
                if col < len(cols):
                    cells[i] = cols[col]
        else:
            col = None
            m = re.match(r'^Measured commit:\s*(.*)$', line)
            if m:
                cells[i] = m.group(1)
    return cells


def extract(repo: Repo, fname: str) -> list[dict]:
    text = repo.blob(BASE, fname)
    if text is None:
        raise RuntimeError(f'base {fname} missing')
    lines = text.decode().split('\n')
    if lines and lines[-1] == '':
        lines.pop()
    revs = blame(repo, fname)
    if len(revs) != len(lines):
        raise RuntimeError(f'blame/line mismatch in {fname}: {len(revs)} vs {len(lines)}')
    cells = measured_cells(lines)
    out, seen = [], {}
    for i, line in enumerate(lines):
        lsha = hashlib.sha256(line.encode()).hexdigest()[:10]
        if lsha in seen:
            seen[lsha] += 1
            lsha = f'{lsha}#{seen[lsha]}'
        else:
            seen[lsha] = 0
        found = []
        for k, m in enumerate(RE_P.finditer(line)):
            if in_lane(m.group(1)):
                end = max(int(m.group(2)), int(m.group(3) or 0))
                found.append(('P', k, m.group(0), {'path': m.group(1), 'end': end}))
        kh = kn = 0
        for m in RE_HN.finditer(line):
            if not in_lane(m.group(1)):
                continue
            if m.group(2):
                found.append(('H', kh, m.group(0), {'path': m.group(1), 'algo': m.group(2),
                                                    'hex': m.group(3)}))
                kh += 1
            if m.group(4):
                found.append(('N', kn, m.group(0), {'path': m.group(1), 'n': int(m.group(4))}))
                kn += 1
        ctoks = []
        if i in cells:
            m = RE_HEX.search(cells[i])
            if m:
                ctoks.append(m.group(1))
        for m in RE_CWORD.finditer(line):
            t = m.group(1)
            before = line[max(0, m.start(1) - 40):m.start(1)]
            if any(u in before for u in UPSTREAM):
                continue
            if re.search(r'\d', t) and re.search(r'[a-f]', t) and t not in ctoks:
                ctoks.append(t)
        for k, t in enumerate(ctoks):
            found.append(('C', k, t, {'token': t}))
        for k, m in enumerate(RE_T.finditer(line)):
            found.append(('T', k, m.group(0), {'date': m.group(1), 'h': m.group(2),
                                               'm': m.group(3), 's': m.group(4) or '00'}))
        kq = 0
        for m in RE_Q.finditer(line):
            span = m.group(1)
            if (re.search(r'\d', span) and ('=' in span or (' ' in span and Q_WORD.search(span)))
                    and not span.startswith(Q_CMD)):
                found.append(('Q', kq, span, {'span': span}))
                kq += 1
        for cls, k, tok, args in found:
            sid = f'{fname}:{cls}:{lsha}:{k}'
            out.append({'sid': sid, 'file': fname, 'line': i + 1, 'class': cls,
                        'token': tok, 'W': revs[i], 'args': args, 'source_line': line})
    return out


def predict(repo, st):
    if st['class'] == 'P':
        path = st['args']['path']
        if ('/' not in path and path != 'SKILL.md') or path.startswith('.ufo/reports/'):
            return 'p:absent', 'basename other than SKILL.md, or fleet report path'
    if st['class'] == 'Q' and '==' not in st['token']:
        lines = repo.text[st['file']].decode().split('\n')
        start = end = st['line'] - 1
        while start > 0 and lines[start - 1].strip():
            start -= 1
        while end + 1 < len(lines) and lines[end + 1].strip():
            end += 1
        paragraph = '\n'.join(lines[start:end + 1])
        raw_artifact = re.search(
            r'(?:\.ufo/[^\s`|]*\.(?:json|jsonl|out|stdout|txt|tsv|log|err)'
            r'|[^\s`|]*/evidence/[^\s`|]*\.(?:json|out|stdout|txt|tsv|log|err)'
            r'|[^\s`|]*\.(?:stdout|out))', paragraph)
        if not raw_artifact:
            return 'q:no-artifact', 'quoted measurement without a raw artifact path in its paragraph'
    return None


if __name__ == '__main__':
    repo = Repo()
    statements = [st for fname in FILES for st in extract(repo, fname)]
    bounded_write(ROOT / 'source-statements.json', json.dumps(statements, indent=2) + '\n')
    bounded_write(ROOT / 'source-hashes.json', json.dumps({
        fname: hashlib.sha256(repo.text[fname]).hexdigest() for fname in FILES
    }, indent=2) + '\n')
    predictions = []
    for st in statements:
        decision = predict(repo, st)
        if decision:
            predictions.append({'sid': st['sid'], 'class': st['class'],
                                'token': st['token'], 'line': st['line'],
                                'value': decision[0], 'reason': decision[1]})
    bounded_write(ROOT / 'predictions.json', json.dumps(predictions, indent=2) + '\n')
    rows = '\n'.join(
        f"| SA29:{st['sid']} | source-text prediction | {st['value']} |"
        for st in predictions)
    suffix = ('\n' + HEADING + '\n\n'
              '| Statement | Policy | Observed |\n|---|---|---|\n' + rows + '\n')
    bounded_write(ROOT / 'correction-rows.md', suffix)
    mutated = repo.text['SCORECARD.md'] + suffix.encode()
    bounded_write(ROOT / 'policy-hashes.json', json.dumps({
        'pristine_scorecard_sha256': hashlib.sha256(repo.text['SCORECARD.md']).hexdigest(),
        'mutated_scorecard_sha256': hashlib.sha256(mutated).hexdigest(),
        'unchanged_shonen_sha256': hashlib.sha256(repo.text['SHONEN.md']).hexdigest(),
        'prediction_count': len(predictions)
    }, indent=2) + '\n')
    print(f'source-only extracted {len(statements)} statements; predicted {len(predictions)} false')
    print('no real writing revision, checks, other blobs or receipt read by policy')
    for st in predictions:
        print(f"{st['sid']} line={st['line']} => {st['value']} token={st['token']}")
