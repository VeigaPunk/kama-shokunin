#!/usr/bin/env python3
"""X14FenceLane: lane-wide fence + CR blob scan and merge-parent-order origin check.

Read-only on the lane clone. Emits JSON to stdout.
"""
import collections, fnmatch, json, os, re, subprocess, sys

REPO = sys.argv[1]
TIP = sys.argv[2]
MODE = sys.argv[3] if len(sys.argv) > 3 else "tip"
FILES = ["SCORECARD.md", "LOG.md", "corpus/QUALITY.md", "corpus/README.md",
         "corpus/SOURCES.md", "AGENTS.md", "SKILL.md"]
EXEMPT = {"## Axes", "## Planned", "## Retired", "## Saturation", "## Capabilities"}
FENCE_OPEN = re.compile(rb"^ {0,3}(`{3,}|~{3,})(.*)$")
HUNK = re.compile(rb"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


def git(*a, inp=None):
    p = subprocess.run(["git", "-C", REPO, *a], input=inp, capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(f"git {' '.join(a)}: {p.stderr.decode()[:300]}")
    return p.stdout


def split_lines(data):
    segs = data.split(b"\n")
    if segs and segs[-1] == b"":
        segs.pop()
    return segs


def key(ln):
    return ln[:-1] if ln.endswith(b"\r") else ln


def fence_open(ln):
    m = FENCE_OPEN.match(ln)
    if not m:
        return None
    run = m.group(1)
    if run[:1] == b"`" and b"`" in m.group(2):
        return None
    return run[:1], len(run)


def fence_close(ln, fence):
    ch, n = fence
    s = ln.lstrip(b" ")
    if len(ln) - len(s) > 3:
        return False
    k = len(s) - len(s.lstrip(ch))
    return k >= n and s[k:].strip(b" \t") == b""


def sections_v5(body):
    out, title, fence = [], None, None
    for line in body:
        b = line.rstrip(b"\r")
        if fence is not None:
            if fence_close(b, fence):
                fence = None
        else:
            fo = fence_open(b)
            if fo is not None:
                fence = fo
            elif b.startswith(b"## "):
                title = b.decode("utf-8", "replace").rstrip()
        out.append(title)
    return out


def sections_v4(body):
    """v4: no fence awareness, raw bytes (a trailing CR stays in the title)."""
    out, title = [], None
    for b in body:
        if b.startswith(b"## "):
            title = b.decode("utf-8", "replace").rstrip()
        out.append(title)
    return out


def fence_content_hits(body):
    """(line_index, line_bytes) for `## ` lines that sit inside a fenced block."""
    hits, fence = [], None
    for i, line in enumerate(body):
        b = line.rstrip(b"\r")
        if fence is not None:
            if fence_close(b, fence):
                fence = None
            elif b.startswith(b"## "):
                hits.append((i, line))
        else:
            fo = fence_open(b)
            if fo is not None:
                fence = fo
    return hits


def deleted_with_pos(parent, commit, path):
    raw = git("diff", "--no-renames", "--no-color", "--no-ext-diff", "-U0", "--text",
              parent, commit, "--", path)
    out, lines, i = [], raw.split(b"\n"), 0
    while i < len(lines):
        m = HUNK.match(lines[i])
        if not m:
            i += 1
            continue
        start = int(m.group(1))
        count = int(m.group(2)) if m.group(2) is not None else 1
        pos = start - 1 if count == 0 else start
        i += 1
        while i < len(lines) and lines[i][:1] in (b"-", b"+", b"\\"):
            if lines[i][:1] == b"-":
                out.append((pos, lines[i][1:]))
                pos += 1
            i += 1
    return out


def main():
    rev = ["--all"] if MODE == "all" else [TIP]
    commits = git("rev-list", *rev).decode().split()
    parents = {}
    for ln in git("rev-list", "--parents", *rev).decode().splitlines():
        p = ln.split()
        parents[p[0]] = p[1:]
    out = {"tip": TIP, "mode": MODE, "commits": len(commits), "files": {}, "blobs": {},
           "merge_commits": {}, "order_check": {}}

    # ---- blob inventory per audited file
    blob_of = {}          # (commit, path) -> oid|None
    for f in FILES:
        spec = "".join(f"{c}:{f}\n" for c in commits)
        raw = git("cat-file", "--batch-check=%(objectname) %(objecttype)", inp=spec.encode()).decode()
        per = {}
        for c, line in zip(commits, raw.split("\n")):
            parts = line.split()
            per[c] = parts[0] if len(parts) == 2 and parts[1] == "blob" else None
        blob_of[f] = per
        out["files"][f] = {"commits_with_blob": sum(1 for v in per.values() if v),
                           "distinct_blobs": len({v for v in per.values() if v})}

    all_blobs = {}
    for f, per in blob_of.items():
        for c, b in per.items():
            if b:
                all_blobs.setdefault(b, set()).add(f)

    # ---- scan every blob
    body_cache = {}
    blob_report = {}
    hdr_hits = 0
    cr_blobs = 0
    for b in sorted(all_blobs):
        data = git("cat-file", "blob", b)
        body = split_lines(data)
        body_cache[b] = body
        fh = fence_content_hits(body)
        cr_lines = [(i, ln) for i, ln in enumerate(body) if b"\r" in ln]
        cr_raw = data.count(b"\r")
        if fh or cr_lines:
            files_here = sorted(all_blobs[b])
            cs = sorted(c for f in files_here for c, bb in blob_of[f].items() if bb == b)
            blob_report[b] = {
                "files": files_here,
                "commits": len(cs),
                "first_commits": cs[:5],
                "fence_heading_hits": [{"line": i + 1, "text": ln.decode("utf-8", "replace")}
                                       for i, ln in fh],
                "cr_lines": [{"line": i + 1, "text": ln.decode("utf-8", "replace")} for i, ln in cr_lines][:10],
                "cr_bytes": cr_raw,
            }
            if fh:
                hdr_hits += len(fh)
            if cr_lines:
                cr_blobs += 1
    out["blobs"] = blob_report
    out["totals"] = {"distinct_blobs": len(all_blobs), "blob_hits": len(blob_report),
                     "fence_heading_lines": hdr_hits, "cr_blobs": cr_blobs}

    # ---- events via the tool
    tool = os.path.join(os.path.dirname(REPO), "tool-tip.json")
    if os.path.exists(tool):
        events = json.load(open(tool)).get("events", [])
    else:
        events = []
    out["events"] = [{"commit": e["commit"], "file": e["file"], "deleted": e["deleted"],
                      "graded": e["graded"], "ungraded": e["ungraded"],
                      "parents": parents.get(e["commit"], [])} for e in events]

    if MODE == "all":
        out["order_ok"] = None
        print(json.dumps(out, indent=1))
        return

    # ---- origin sets (counter's v5 origins) over event files, parents in both orders
    def blob_ids(f):
        return blob_of[f]

    def origins(f, parent_order_rev=False):
        bl = blob_ids(f)
        cache = {}
        def body_of(b):
            if b not in cache:
                body = body_cache.get(b)
                if body is None:
                    body = split_lines(git("cat-file", "blob", b))
                    body_cache[b] = body
                cache[b] = (body, {key(x) for x in body})
            return cache[b]
        orig = collections.defaultdict(set)
        for c in commits:
            b = bl[c]
            if b is None:
                continue
            body, keys = body_of(b)
            ps = list(parents[c])
            if parent_order_rev:
                ps = ps[::-1]
            pkeys = set()
            for q in ps:
                if bl.get(q) == b:
                    pkeys = keys
                    break
                if bl.get(q) is not None:
                    pkeys |= body_of(bl[q])[1]
            if pkeys is keys:
                continue
            for ln, t in zip(body, sections_v5(body)):
                k = key(ln)
                if k not in pkeys:
                    orig[k].add(t)
        return orig

    order_ok = True
    for e in events:
        f = e["file"]
        a = origins(f, False)
        b2 = origins(f, True)
        same = {k: v for k, v in a.items()} == {k: v for k, v in b2.items()}
        order_ok = order_ok and same
        par = (parents.get(e["commit"]) or [None])[0]
        pb = split_lines(git("show", f"{par}:{f}"))
        psec5 = sections_v5(pb)
        psec4 = sections_v4(pb)
        org = a
        delpos = deleted_with_pos(par, e["commit"], f)
        ungraded_positions_v5 = {pos for pos, text in delpos
                                 if psec5[pos - 1] in EXEMPT and org.get(key(text), set()) & EXEMPT}
        # v4 hypothesis: fence-blind sections, byte-exact key origins
        org4 = collections.defaultdict(set)
        # recompute byte-exact origin: same graph but key = raw line
        cache4 = {}
        def body4(b):
            if b not in cache4:
                body = body_cache.get(b) or split_lines(git("cat-file", "blob", b))
                cache4[b] = (body, set(body))
            return cache4[b]
        bl = blob_of[f]
        for c in commits:
            bb = bl[c]
            if bb is None:
                continue
            body4v, keys4 = body4(bb)
            pkeys = set()
            for q in parents[c]:
                if bl.get(q) == bb:
                    pkeys = keys4
                    break
                if bl.get(q) is not None:
                    pkeys |= body4(bl[q])[1]
            if pkeys is keys4:
                continue
            for ln, t in zip(body4v, sections_v4(body4v)):
                if ln not in pkeys:
                    org4[ln].add(t)
        ungraded_positions_v4 = {pos for pos, text in delpos
                                 if psec4[pos - 1] in EXEMPT and org4.get(text, set()) & EXEMPT}
        cr_del = [(pos, text) for pos, text in delpos if b"\r" in text]
        # does any deleted line sit behind a fence-fake heading in the parent blob?
        fh = fence_content_hits(pb)
        affected = []
        if fh:
            # lines up to the next real (unfenced) `## ` heading are mis-owned under v4
            for pos, text in delpos:
                if psec5[pos - 1] != psec4[pos - 1]:
                    affected.append({"pos": pos, "v5": psec5[pos - 1], "v4": psec4[pos - 1]})
        out["order_check"][f"{e['commit'][:12]}:{f}"] = {
            "parents": parents.get(e["commit"]),
            "origin_sets_equal_both_orders": same,
            "n_origin_keys": len(a),
            "deleted": len(delpos),
            "deleted_with_cr": len(cr_del),
            "native_ungraded_v5": len(ungraded_positions_v5),
            "native_ungraded_v4_hypothesis": len(ungraded_positions_v4),
            "ungraded_positions_equal": ungraded_positions_v5 == ungraded_positions_v4,
            "verdict_changed_by_definition": ungraded_positions_v5 != ungraded_positions_v4,
            "parent_fence_fake_headings": len(fh),
            "deleted_lines_with_changed_section": affected[:5],
        }

    # ---- merge commits: both-parent events + swapped-parent diff sensitivity
    for c in [x for x, p in parents.items() if len(p) > 1]:
        rec = {"parents": parents[c]}
        for f in FILES:
            d1 = git("diff", "--numstat", "--no-renames", parents[c][0], c, "--", f).decode().split()
            d2 = git("diff", "--numstat", "--no-renames", parents[c][1], c, "--", f).decode().split()
            if d1 or d2:
                rec[f] = {"vs_parent1": d1, "vs_parent2": d2}
        # conventionally the tool uses parent 1; report the per-file diff to both
        out["merge_commits"][c] = rec

    out["order_ok"] = order_ok
    print(json.dumps(out, indent=1))


main()
