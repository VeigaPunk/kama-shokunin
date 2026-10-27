#!/usr/bin/env python3
"""X7Regen (round 51, lane kama): independent regeneration of
registry/append-only-disclosures.tsv from the lane's git history alone.

Written from the append-only-audit v6 disclosure contract as the tool docstring states it
(tools/append-only-audit.py:15-25) - it does NOT call the tool, read its JSON, its
`undisclosed` field, or .ufo/waves/round-51/c2/build_ledger.py.

Semantics implemented (whole-file-graded contract rows only; rows carrying an `exempt=` or
`only=` region, i.e. SCORECARD.md and the two `only=` knowledge entries, are skipped as the
seat spec directs):
  commits   git rev-list --topo-order --reverse --parents <TIP>; diff each commit against
            its first parent; a root commit has no deletions
  deleted   byte-exact lines of the -U0 first-parent diff, read by hunk-header counts;
            must equal `git diff --numstat` deletions for the file in that commit
  permitted (A-row only, corpus/SOURCES.md): a deleted registry row is permitted when the
            deleting commit's blob holds a row with the same id whose cells other than
            status/recheck/used-by are byte-equal
  graded    deleted lines minus permitted; a whole-file row grades everything else
  unheld    for line key l (bytes with one trailing CR stripped) deleted n times in the
            event: u(l) = n - min(n, max(0, M_tip[l] - K[l])), K = parent counts - deleted
            counts; u(l) > 0 means those graded lines are not held at the tip
  class     `revert` when the commit subject starts with `Revert "`, else `in-place-edit`
            when the deleted line's hunk adds lines, else `removal`
  note      "deleted in place by: " + commit subject (tabs -> spaces, first 160 bytes)
  row       commit<TAB>file<TAB>sha256(key)<TAB>count<TAB>class<TAB>note

Usage: regen_ledger.py <repo> <tip> <actual-ledger.tsv> <out-tsv>
Prints a comparison summary; exit 0 when the row sets are identical.
"""
import collections
import fnmatch
import hashlib
import re
import subprocess
import sys

CONTRACT = "registry/append-only-contract.tsv"
HEADER = "commit\tfile\tline_sha256\tcount\tclass\tnote"
ROWPAT = re.compile(r"^ {0,3}\| *S[0-9]{3,} *\|")
HUNK = re.compile(rb"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
MUTABLE = (7, 9, 10)          # status (8th), recheck (10th), used-by (11th), 0-based
CLASSES = ("revert", "in-place-edit", "removal")


def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, check=True).stdout


def split_lines(data):
    segs = data.split(b"\n")
    if segs and segs[-1] == b"":
        segs.pop()
    return segs


def key(ln):
    return ln[:-1] if ln.endswith(b"\r") else ln


def blob_lines(repo, rev, path):
    try:
        return split_lines(git(repo, "cat-file", "blob", f"{rev}:{path}"))
    except subprocess.CalledProcessError:
        return []


def deleted_lines(repo, parent, commit, path):
    """[(line number in parent, bytes, lines its hunk adds)] for every deleted line."""
    raw = git(repo, "diff", "--no-renames", "--no-color", "--no-ext-diff", "-U0",
              "--text", parent, commit, "--", path)
    out, lines, i = [], raw.split(b"\n"), 0
    while i < len(lines):
        m = HUNK.match(lines[i])
        i += 1
        if not m:
            continue
        start = int(m.group(1))
        nd = int(m.group(2)) if m.group(2) is not None else 1
        na = int(m.group(4)) if m.group(4) is not None else 1
        gd = ga = 0
        while i < len(lines) and (gd < nd or ga < na):
            ln = lines[i]
            if ln.startswith(b"-") and gd < nd:
                out.append((start + gd, ln[1:], na))
                gd += 1
            elif ln.startswith(b"+") and ga < na:
                ga += 1
            i += 1
    return out


def row_cells(text):
    """The 11 cells of a registry row outside backtick code spans, else None."""
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


def permitted_positions(dl, commit_body):
    """Positions in dl of deleted A-row registry rows the commit's blob still holds with
    every immutable cell byte-equal."""
    held = collections.defaultdict(list)
    for ln in commit_body:
        c = row_cells(ln)
        if c is not None and len(c) == 11:
            held[c[0]].append(c)
    keep = lambda c: [x for j, x in enumerate(c) if j not in MUTABLE]
    out = set()
    for pos, text, _na in dl:
        c = row_cells(text)
        if c is not None and len(c) == 11 and any(keep(n) == keep(c) for n in held.get(c[0], ())):
            out.add(pos)
    return out


def contract_rows(repo, tip):
    text = git(repo, "show", f"{tip}:{CONTRACT}").decode()
    rows = []
    for line in text.split("\n")[1:]:
        if not line.strip():
            continue
        pat, rule, decl, region, note = (c.strip() for c in line.split("\t"))
        rows.append((pat, rule, region))
    return rows


def main(repo, tip_raw, actual_path, out_path):
    tip = git(repo, "rev-parse", tip_raw).decode().strip()
    rows = contract_rows(repo, tip)
    paths = [p.decode("utf-8", "surrogateescape")
             for p in git(repo, "ls-tree", "-r", "--name-only", "-z", tip).split(b"\0") if p]
    # whole-file-graded files only: a file any matching row declares `exempt=`/`only=` is out
    graded, skipped = set(), set()
    for p in paths:
        matched = [r for r in rows if fnmatch.fnmatchcase(p, r[0])]
        if not matched:
            continue
        if all(r[2] == "*" for r in matched):
            graded.add(p)
        else:
            skipped.add(p)
    files = sorted(graded)
    arow = {p for p in graded if any(r[1] == "A-row" for r in rows if fnmatch.fnmatchcase(p, r[0]))}
    tip_lines = {f: collections.Counter(blob_lines(repo, tip, f)) for f in files}

    raw = git(repo, "rev-list", "--topo-order", "--reverse", "--parents", tip)
    commits = []
    for ln in raw.decode().split("\n"):
        if not ln.strip():
            continue
        parts = ln.split()
        commits.append((parts[0], parts[1] if len(parts) > 1 else None))

    subjects, events, problems = {}, [], []
    stat = collections.Counter()
    for c, p in commits:
        if p is None:
            continue
        ns = {}
        out = git(repo, "diff", "--numstat", "-z", "--no-renames", p, c, "--", *files)
        for rec in out.split(b"\0"):
            cells = rec.split(b"\t", 2)
            if len(cells) == 3:
                ns[cells[2].decode("utf-8", "surrogateescape")] = int(cells[1]) \
                    if cells[1].isdigit() else None
        if not ns:
            continue
        subject = git(repo, "log", "-1", "--format=%s", c).decode().strip()
        subjects[c] = subject
        for f in sorted(ns):
            if ns[f] is None:
                problems.append(f"binary change {c[:12]} {f}")
                continue
            if ns[f] < 1:
                continue
            dl = deleted_lines(repo, p, c, f)
            if len(dl) != ns[f]:
                problems.append(f"hunk count {len(dl)} != numstat {ns[f]} at {c[:12]} {f}")
            perm = permitted_positions(dl, blob_lines(repo, c, f)) if f in arow else set()
            D = collections.Counter(t for _pos, t, _na in dl)
            K = collections.Counter(blob_lines(repo, p, f)) - D
            G = collections.Counter(t for pos, t, _na in dl if pos not in perm)
            unheld = collections.Counter()
            for line, n in G.items():
                u = n - min(n, max(0, tip_lines[f][line] - K[line]))
                if u:
                    unheld[hashlib.sha256(key(line)).hexdigest()] += u
            classes = collections.defaultdict(set)
            for pos, text, na in dl:
                if pos in perm:
                    continue
                klass = ("revert" if subject.startswith('Revert "')
                         else ("in-place-edit" if na else "removal"))
                classes[hashlib.sha256(key(text)).hexdigest()].add(klass)
            for hsh, n in sorted(unheld.items()):
                cls = sorted(classes[hsh])
                if len(cls) != 1:
                    problems.append(f"{c[:12]} {f} {hsh[:12]}: classes {cls}")
                note = ("deleted in place by: " + subject).replace("\t", " ")[:160]
                events.append((c, f, hsh, n, cls[0] if len(cls) == 1 else "+".join(cls), note))
            stat["events"] += 1
            stat["deleted"] += len(dl)
            stat["permitted"] += len(perm)
            stat["graded"] += sum(G.values())
            stat["ungraded"] += len(dl) - sum(G.values()) - len(perm)
            stat["undisclosed"] += sum(unheld.values())

    mine = [HEADER] + ["\t".join([c, f, h, str(n), k, note]) for c, f, h, n, k, note in events]
    open(out_path, "w").write("\n".join(mine) + "\n")

    actual = [ln for ln in open(actual_path).read().split("\n")[1:]
              if ln.strip() and ln.split("\t")[1] not in skipped]
    myset, okset = collections.Counter(mine[1:]), collections.Counter(actual)
    only_mine = sorted(myset - okset)
    only_ledger = sorted(okset - myset)
    print(f"tip={tip} commits={len(commits)} graded_files={len(files)} skipped={sorted(skipped)}")
    print("scope " + " ".join(f"{k}={stat[k]}" for k in ("events", "deleted", "permitted",
                                                          "graded", "ungraded", "undisclosed")))
    print(f"rows_mine={len(mine) - 1} lines_mine={sum(n for _c, _f, _h, n, _k, _n in events)} "
          f"rows_ledger={len(actual)} lines_ledger={sum(int(ln.split(chr(9))[3]) for ln in actual)}")
    print(f"only_in_regen={len(only_mine)} only_in_ledger={len(only_ledger)} problems={problems}")
    for ln in only_mine:
        print("+ " + ln)
    for ln in only_ledger:
        print("- " + ln)
    return 0 if not only_mine and not only_ledger else 1


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:5]))
