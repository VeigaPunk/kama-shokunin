#!/usr/bin/env python3
"""X7Regen: row-level verification of registry/append-only-disclosures.tsv against the lane's
git history, independent of both the audit tool and regen_ledger.py.

Scope: whole-file-graded contract rows only (SCORECARD.md's `exempt=` head and the two `only=`
knowledge entries are excluded, as the seat spec directs). Events are found by walking the
first-parent diffs of every commit up to the tip, not by reading the ledger, so an event the
ledger omits is still checked.

Per ledger row it checks
  event      (commit, file) has deletions of the file in that commit's first-parent diff
  preimage   at least `count` deleted lines hash - sha256 of the line's CR-stripped bytes - to
             line_sha256; reports any deleted line that carried a CR (where the raw digest
             differs); prints one preimage per row
  note       exactly "deleted in place by: " + commit subject, tabs -> spaces, first 160 bytes
  class      subject starts with `Revert "` <=> `revert`; else the hashed deleted line sits in
             a hunk that adds lines (`in-place-edit`) or in a pure-deletion hunk (`removal`)
  held       multiset measure: for n deletions of the key, K surviving copies in the parent and
             M copies at the tip, unheld = n - min(n, max(0, M - K)) must be >= count

Per A-row event (corpus/SOURCES.md) it checks the carve-out: a deleted registry row whose
immutable cells (all but status/recheck/used-by) are absent at the tip must be named by a
ledger row of that event; one whose immutable cells survive at the tip is permitted.

Usage: verify_rows.py <repo> <tip> <ledger.tsv> [--preimages N]
Exit 0 when every check holds.
"""
import collections
import fnmatch
import hashlib
import re
import subprocess
import sys

CONTRACT = "registry/append-only-contract.tsv"
HUNK = re.compile(rb"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
ROWPAT = re.compile(r"^ {0,3}\| *S[0-9]{3,} *\|")
MUTABLE = (7, 9, 10)


def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, check=True).stdout


def split_lines(data):
    segs = data.split(b"\n")
    if segs and segs[-1] == b"":
        segs.pop()
    return segs


def key(ln):
    return ln[:-1] if ln.endswith(b"\r") else ln


def blob(repo, rev, path):
    try:
        return split_lines(git(repo, "cat-file", "blob", f"{rev}:{path}"))
    except subprocess.CalledProcessError:
        return []


def deleted_with_hunks(repo, parent, commit, path):
    """[(bytes, lines its hunk adds)] for every deleted line of the -U0 first-parent diff."""
    raw = git(repo, "diff", "--no-renames", "--no-color", "--no-ext-diff", "-U0", "--text",
              parent, commit, "--", path)
    out, lines, i = [], raw.split(b"\n"), 0
    while i < len(lines):
        m = HUNK.match(lines[i])
        i += 1
        if not m:
            continue
        nd = int(m.group(2)) if m.group(2) is not None else 1
        na = int(m.group(4)) if m.group(4) is not None else 1
        gd = ga = 0
        while i < len(lines) and (gd < nd or ga < na):
            ln = lines[i]
            if ln.startswith(b"-") and gd < nd:
                out.append((ln[1:], na))
                gd += 1
            elif ln.startswith(b"+") and ga < na:
                ga += 1
            i += 1
    return out


def row_cells(text):
    try:
        s = text.decode("utf-8")
    except UnicodeDecodeError:
        return None
    if not ROWPAT.match(s):
        return None
    s = s.rstrip("\r").strip()
    cells, buf, code = [], [], False
    for ch in s[1:]:
        if ch == "`":
            code = not code
        if ch == "|" and not code:
            cells.append("".join(buf).strip())
            buf = []
        else:
            buf.append(ch)
    return cells if not "".join(buf).strip() else None


def main(repo, tip_raw, ledger_path, *rest):
    show = int(rest[1]) if len(rest) > 1 and rest[0] == "--preimages" else 10
    tip = git(repo, "rev-parse", tip_raw).decode().strip()
    contract = [ln.split("\t") for ln in
                git(repo, "show", f"{tip}:{CONTRACT}").decode().split("\n")[1:] if ln.strip()]
    skip = {c[0] for c in contract if c[3].strip().startswith("only=")} | {"SCORECARD.md"}
    arow = [c[0] for c in contract if c[1].strip() == "A-row"]
    paths = [p.decode("utf-8", "surrogateescape")
             for p in git(repo, "ls-tree", "-r", "--name-only", "-z", tip).split(b"\0") if p]
    files = set()
    for p in paths:
        matched = [c for c in contract if fnmatch.fnmatchcase(p, c[0])]
        if matched and p not in skip and all(c[3].strip() == "*" for c in matched):
            files.add(p)
    files = sorted(files)
    tipcnt = {f: collections.Counter(blob(repo, tip, f)) for f in files}

    events, bad = {}, []
    for ln in git(repo, "rev-list", "--topo-order", "--reverse", "--parents", tip).decode().split("\n"):
        if not ln.strip():
            continue
        parts = ln.split()
        c, p = parts[0], (parts[1] if len(parts) > 1 else None)
        if p is None:
            continue
        ns = {}
        for rec in git(repo, "diff", "--numstat", "-z", "--no-renames", p, c, "--", *files).split(b"\0"):
            cells = rec.split(b"\t", 2)
            if len(cells) == 3:
                ns[cells[2].decode("utf-8", "surrogateescape")] = (
                    int(cells[1]) if cells[1].isdigit() else None)
        if not any(v for v in ns.values()):
            continue
        subject = git(repo, "log", "-1", "--format=%s", c).decode().strip()
        for f in sorted(ns):
            if not ns[f]:
                continue
            dl = deleted_with_hunks(repo, p, c, f)
            if len(dl) != ns[f]:
                bad.append(f"{c[:12]} {f}: hunk count {len(dl)} != numstat {ns[f]}")
            events[(c, f)] = {"dl": dl, "parent": p, "subject": subject}

    rows = [ln.split("\t") for ln in open(ledger_path).read().split("\n")[1:] if ln.strip()]
    led = collections.Counter((r[0], r[1], r[2]) for r in rows if r[1] not in skip)
    checked = cr_lines = permitted = 0
    shown = 0
    for commit, path, hsh, cnt, klass, note in rows:
        if path in skip:
            continue
        checked += 1
        ev = events.get((commit, path))
        if ev is None:
            bad.append(f"{commit[:12]} {path} {hsh[:12]}: names no event with a deletion")
            continue
        dl, parent, subject = ev["dl"], ev["parent"], ev["subject"]
        want_note = ("deleted in place by: " + subject).replace("\t", " ")[:160]
        if note != want_note:
            bad.append(f"{commit[:12]} {path}: note != {want_note[:60]!r}")
        pre = [(x, na) for x, na in dl if hashlib.sha256(key(x)).hexdigest() == hsh]
        for x, _na in pre:
            if x.endswith(b"\r"):
                cr_lines += 1
        if len(pre) < int(cnt):
            bad.append(f"{commit[:12]} {path} {hsh[:12]}: {len(pre)} preimages < count {cnt}")
            continue
        if subject.startswith('Revert "') != (klass == "revert"):
            bad.append(f"{commit[:12]} {path} {hsh[:12]}: class {klass} vs subject {subject[:40]!r}")
        elif klass != "revert":
            wants = "in-place-edit" if any(na for _x, na in pre) else "removal"
            if klass != wants:
                bad.append(f"{commit[:12]} {path} {hsh[:12]}: class {klass}, hunks say {wants}")
        D = collections.Counter(x for x, _na in dl)
        K = collections.Counter(blob(repo, parent, path)) - D
        M = tipcnt[path]
        n = D[pre[0][0]]
        unheld = n - min(n, max(0, M[pre[0][0]] - K[pre[0][0]]))
        if unheld < int(cnt):
            bad.append(f"{commit[:12]} {path} {hsh[:12]}: only {unheld} unheld < count {cnt}")
        if shown < show:
            shown += 1
            print(f"preimage {commit[:12]} {path} {hsh[:12]} n={n} unheld={unheld} "
                  f"{klass}: {pre[0][0][:96]!r}")

    keep = lambda c: [x for j, x in enumerate(c) if j not in MUTABLE]
    for (commit, path), ev in events.items():
        if not any(fnmatch.fnmatchcase(path, p) for p in arow):
            continue
        tiprows = collections.defaultdict(list)
        for x in tipcnt[path].elements():
            c = row_cells(x)
            if c is not None and len(c) == 11:
                tiprows[c[0]].append(c)
        for x, _na in ev["dl"]:
            c = row_cells(x)
            if c is None or len(c) != 11:
                continue
            h = hashlib.sha256(key(x)).hexdigest()
            if any(keep(nc) == keep(c) for nc in tiprows.get(c[0], ())):
                permitted += 1
            elif led[(commit, path, h)] == 0:
                bad.append(f"{commit[:12]} {path} {h[:12]}: A-row id {c[0]} lost at tip, "
                           f"not in the ledger")
    print(f"events_with_deletions={len(events)} checked_rows={checked} "
          f"arow_permitted_ids_kept_at_tip={permitted} deleted_lines_with_cr={cr_lines}")
    print(f"violations={len(bad)}")
    for b in bad:
        print("! " + b)
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
