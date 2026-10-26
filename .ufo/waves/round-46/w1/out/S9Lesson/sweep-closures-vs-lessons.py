#!/usr/bin/env python3
"""sweep-closures-vs-lessons.py - round-46 seat S9Lesson sweep.

Question: which items the closures of rounds 40-45 routed to the lane have not
been turned into a lesson row (cited in a later lesson or closure of this
corpus)?

Extraction (deterministic, no reading):
  routed section   from a heading matching `^## .*Routed defects` to the next
                   `^## ` heading of the same file.
  items            lines starting `<n>. ` or `- **D`; continuation lines are
                   appended until the next item or a blank line.
  label            the first `D<digit>` or `D-<letter>` token in bold, else `#<n>`
                   (the item's position in the section).

Two independent probes per item, both restricted to files of a LATER round than
the item's source (`round-<m>.md` and `round-<m>-verifier-spotcheck.md` for
m > source round), so an item cannot match itself:
  label_cite       regex `r<round>-<label>` or `round-<round>` ... `<label>`
                   within 48 characters.
  id_probe         the item's backticked identifiers (paths, tools, receipts:
                   a span of >= 8 characters that holds `/` or ends in
                   `.py/.md/.tsv/.json`); count how many of them appear as
                   substrings of some later lesson line, and give the first hit.

`0/0` in both columns means no later lesson cites the item's label nor any of
its named artifacts. That is a pointer, not a proof of absence: a lesson may
address the subject in other words, so the caller reads the 0/0 rows.
Read-only.

Usage: sweep-closures-vs-lessons.py [--lane DIR] [--json]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

ROUNDS = [40, 41, 42, 43, 44, 45]


def routed_items(text):
    lines = text.splitlines()
    start = None
    for i, ln in enumerate(lines):
        if re.match(r'^##\s+.*Routed defects', ln):
            start = i
            break
    if start is None:
        return []
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith('## '):
            end = j
            break
    items, cur = [], None
    for ln in lines[start + 1:end]:
        m = re.match(r'^(?:(\d+)\.\s+|-\s+(?=\*\*D))(.*)$', ln)
        if m:
            if cur:
                items.append(cur)
            cur = {'n': m.group(1) or str(len(items) + 1), 'text': m.group(2).strip()}
        elif cur is not None and ln.strip():
            cur['text'] += ' ' + ln.strip()
        elif cur is not None:
            items.append(cur)
            cur = None
    if cur:
        items.append(cur)
    for it in items:
        m = re.search(r'\*\*(D-?[A-Z0-9]+)', it['text'])
        it['label'] = m.group(1) if m else '#%s' % it['n']
        it.pop('n', None)
    return items


def ids_of(text):
    out, seen = [], set()
    for span in re.findall(r'`([^`]+)`', text):
        span = span.strip()
        if len(span) < 8:
            continue
        if not ('/' in span or re.search(r'\.(py|md|tsv|json|out)$', span)):
            continue
        if span in seen:
            continue
        seen.add(span)
        out.append(span)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--lane', default='/home/vgpnk/Projects/shokunin/kama-shokunin')
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()
    lessons_dir = os.path.join(args.lane, 'corpus', 'lessons')
    files = {}
    for f in os.listdir(lessons_dir):
        m = re.match(r'^round-(4[0-9])(-verifier-spotcheck)?\.md$', f)
        if m:
            files[int(m.group(1)), bool(m.group(2))] = os.path.join(lessons_dir, f)

    def later_lines(src_round):
        out = []
        for (rnd, is_closure), path in sorted(files.items()):
            if rnd <= src_round:
                continue
            with open(path, encoding='utf-8', errors='replace') as fh:
                for i, ln in enumerate(fh, 1):
                    out.append((os.path.basename(path), i, ln.rstrip('\n')))
        return out

    rows = []
    for r in ROUNDS:
        path = files.get((r, True))
        if path is None:
            rows.append({'round': r, 'label': '?', 'subject': 'closure file missing',
                         'label_cite': 'MISSING', 'id_probe': 'MISSING'})
            continue
        with open(path, encoding='utf-8') as fh:
            text = fh.read()
        pool = later_lines(r)
        for it in routed_items(text):
            lab = it['label']
            pat = re.compile(r'(r%d-%s\b|round-%d[^.\n]{0,48}\b%s\b)'
                             % (r, re.escape(lab), r, re.escape(lab)))
            cite = '-'
            for name, no, ln in pool:
                if pat.search(ln):
                    cite = '%s:%d' % (name, no)
                    break
            ids = ids_of(it['text'])
            hit_ids, first = 0, '-'
            for ident in ids:
                for name, no, ln in pool:
                    if ident in ln:
                        hit_ids += 1
                        if first == '-':
                            first = '%s:%d %s' % (name, no, ident)
                        break
            probe = '%d/%d %s' % (hit_ids, len(ids), first)
            rows.append({'round': r, 'label': lab,
                         'subject': re.sub(r'\s+', ' ', it['text'])[:110],
                         'label_cite': cite, 'id_probe': probe})
    if args.json:
        print(json.dumps(rows, indent=1, ensure_ascii=False))
        return 0
    print('round label  label_cite                        id_probe')
    for row in rows:
        print('%-5d %-6s %-34s %s' % (row['round'], row['label'], row['label_cite'], row['id_probe']))
        print('      subject: %s' % row['subject'][:100])
    dead = [r for r in rows if r['label_cite'] == '-' and r['id_probe'].startswith('0/')]
    print('summary items=%d uncited_by_label=%d uncited_by_both=%d' % (
        len(rows), sum(1 for r in rows if r['label_cite'] == '-'), len(dead)))
    for row in dead:
        print('  bare: r%d %s -- %s' % (row['round'], row['label'], row['subject'][:70]))
    return 0


if __name__ == '__main__':
    sys.exit(main())
