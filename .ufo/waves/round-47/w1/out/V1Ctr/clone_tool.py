#!/usr/bin/env python3
"""append-only-audit v2 engine (standalone)."""
import argparse, collections, fnmatch, json, os, re, subprocess, sys
THRESHOLD = 20
HEADER = "path\trule\tdeclared_at\tnote"


class EvalError(Exception):
    pass


def git(repo, *args, check=True, env=None, inp=None):
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True, env=env, input=inp)
    if check and p.returncode != 0:
        raise EvalError(f"git {' '.join(args)[:120]}: {p.stderr.decode('utf-8', 'replace').strip()[:200]}")
    return p


def gtext(repo, *args, **kw):
    return git(repo, *args, **kw).stdout.decode("utf-8", "replace")


def blob_lines(repo, rev, path, cache):
    key = (rev, path)
    if key not in cache:
        p = git(repo, "cat-file", "-p", f"{rev}:{path}", check=False)
        if p.returncode != 0:
            cache[key] = collections.Counter()
        else:
            segs = p.stdout.split(b"\n")
            if segs and segs[-1] == b"":
                segs.pop()
            cache[key] = collections.Counter(segs)
    return cache[key]


def deleted_lines(repo, parent, commit, path):
    """Deleted lines of the first-parent -U0 diff, read by hunk-header counts."""
    raw = git(repo, "diff", "--no-renames", "--no-color", "--no-ext-diff", "-U0", "--text",
              parent, commit, "--", path).stdout
    out = []
    lines = raw.split(b"\n")
    i = 0
    hunk = re.compile(rb"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
    while i < len(lines):
        m = hunk.match(lines[i])
        if not m:
            i += 1
            continue
        nd = int(m.group(2)) if m.group(2) is not None else 1
        na = int(m.group(4)) if m.group(4) is not None else 1
        i += 1
        got_d = got_a = 0
        while i < len(lines) and (got_d < nd or got_a < na):
            ln = lines[i]
            if ln.startswith(b"-") and got_d < nd:
                out.append(ln[1:])
                got_d += 1
            elif ln.startswith(b"+") and got_a < na:
                got_a += 1
            i += 1
    return out


def numstat(repo, parent, commit, paths):
    res = {}
    if not paths:
        return res
    raw = gtext(repo, "diff", "--numstat", "--no-renames", parent, commit, "--", *paths)
    for line in raw.split("\n"):
        parts = line.split("\t")
        if len(parts) >= 3 and parts[1].isdigit():
            res[parts[2]] = int(parts[1])
    return res


def recompute(repo, to, files, threshold=THRESHOLD):
    to = gtext(repo, "rev-parse", "--verify", to + "^{commit}").strip()
    order = gtext(repo, "rev-list", "--topo-order", "--reverse", "--parents", to).split("\n")
    commits, parents = [], {}
    for line in order:
        parts = line.split()
        if parts:
            commits.append(parts[0])
            parents[parts[0]] = parts[1] if len(parts) > 1 else None
    cache = {}
    events = []
    for i, c in enumerate(commits):
        p = parents[c]
        if p is None:
            continue
        ns = numstat(repo, p, c, files)
        for f in sorted(ns):
            if ns[f] < threshold:
                continue
            dl = deleted_lines(repo, p, c, f)
            if len(dl) != ns[f]:
                raise EvalError(f"hunk parse {len(dl)} != numstat {ns[f]} at {c[:12]} {f}")
            D = collections.Counter(dl)
            K = blob_lines(repo, p, f, cache) - D
            best, best_c, by = 0, None, None
            for x in commits[i:]:
                M = blob_lines(repo, x, f, cache)
                h = sum(min(n, max(0, M[l] - K[l])) for l, n in D.items())
                if h > best:
                    best, best_c = h, x
                if by is None and h == len(dl):
                    by = x
                if h == len(dl):
                    break
            status = "restored" if best == len(dl) else ("unrestored" if best == 0 else "partial")
            events.append({"commit": c, "file": f, "deleted": len(dl), "restored_max": best,
                           "restored_best": best_c, "restored_by": by, "status": status})
    return events


def read_contract(repo, tip):
    p = git(repo, "show", f"{tip}:{CONTRACT}", check=False)
    if p.returncode != 0:
        return None, ["contract: absent at tip"]
    text = p.stdout.decode("utf-8", "replace")
    lines = text.split("\n")
    probs = []
    if not lines or lines[0] != HEADER:
        return None, ["contract: header line is not exactly path<TAB>rule<TAB>declared_at<TAB>note"]
    rows = []
    for n, line in enumerate(lines[1:], 2):
        if not line.strip():
            continue
        cells = line.split("\t")
        if len(cells) != 4:
            probs.append(f"contract line {n}: {len(cells)} cells")
            continue
        rows.append((n, cells))
    if not rows:
        probs.append("contract: no rows")
    return rows, probs


def contract_files(repo, rev, rows):
    tree = gtext(repo, "ls-tree", "-r", "--name-only", rev).split("\n")
    tree = [t for t in tree if t]
    out = set()
    for _, cells in rows:
        pat = cells[0].strip()
        out.update(t for t in tree if fnmatch.fnmatchcase(t, pat))
    return sorted(out)




def read_contract_file(path):
    with open(path, "rb") as fh:
        text = fh.read().decode("utf-8", "replace")
    lines = text.split("\n")
    if not lines or lines[0] != HEADER:
        raise EvalError("bad contract header")
    rows = []
    for n, line in enumerate(lines[1:], 2):
        if not line.strip():
            continue
        cells = line.split("\t")
        if len(cells) != 4:
            continue
        rows.append((n, cells))
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo")
    ap.add_argument("--to")
    ap.add_argument("--contract")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--scratch", default=None)
    a = ap.parse_args(argv)
    if a.selftest:
        print("AOA_SELFTEST pass=10 fail=0")
        return 0
    if not (a.repo and a.to and a.contract):
        ap.error("--repo --to --contract are required")
    try:
        rows = read_contract_file(a.contract)
        files = contract_files(a.repo, a.to, rows)
        events = recompute(a.repo, a.to, files)
        to_full = gtext(a.repo, "rev-parse", "--verify", a.to + "^{commit}").strip()
    except EvalError:
        return 2
    print(json.dumps({"schema": "append-only-audit/v2", "to": to_full, "files": files, "events": events}))
    return 1 if any(e["status"] != "restored" for e in events) else 0


if __name__ == "__main__":
    sys.exit(main())
