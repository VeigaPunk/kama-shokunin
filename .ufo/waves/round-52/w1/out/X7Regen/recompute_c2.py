#!/usr/bin/env python3
"""X7Regen round-52 item: independent full-scope recomputation of the lane's
append-only losses at 5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8.

Own implementation. It imports neither tools/round52-append-restore-check.py nor
tools/append-only-audit.py; region, fence, section, grading and holding rules
below are re-derived from registry/append-only-contract.tsv and the C2
docstring's stated semantics.

Scope: every contract row at the tip expanded over the tip tree; every commit
reachable from the tip, first-parent diff; deleted parent lines located by the
diff's own old-line positions; region rules applied here independently; A-row
permitted rows removed here.

Rules:
  *                       every deleted line is graded
  exempt=H1|..|Hn         graded unless its parent-blob section (last `## `
                          heading at/before it that is not a fence line nor
                          inside a fence) equals one of the Hi
  only=P                  graded only if its section starts with P
  A-row                   as `*`, minus a deleted registry row (`| S### |`)
                          whose id the commit's blob still holds with every
                          cell except status/recheck/used-by (1-based 8,10,11 =
                          0-based 7,9,10) byte-equal
  A                       as `*` (no permitted in-place edit)
Held at tip per event (commit c, file f): for each key l graded G[l] times,
  P[l] parent copies, D[l] copies this event deleted, M[l] tip copies,
  K[l] = P[l] - D[l] copies the diff kept,
  restored = max(0, M[l] - K[l]); unheld = max(0, G[l] - min(G[l], restored)).
Key = line bytes with one trailing CR removed, sha256 hexdigest.

Exit 0 always; prints a text report and optionally writes JSON.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
import subprocess
import sys

CONTRACT = "registry/append-only-contract.tsv"
LEDGER = "registry/append-only-disclosures.tsv"
HUNK = re.compile(rb"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
DIFFHDR = re.compile(rb"^diff --git a/(.*?) b/(.*)$")
ROW = re.compile(rb"^ {0,3}\| *S([0-9]{3,}) *\|")
FENCE_OPEN = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
MUTABLE = {7, 9, 10}  # 0-based; 1-based cells 8, 10, 11
FENCE_BLIND = False  # sensitivity switch: treat every line as outside a fence


class Fail(Exception):
    pass


def git(repo, *args):
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True)
    if p.returncode != 0:
        raise Fail(f"git {' '.join(args)[:120]}: {p.stderr.decode('utf-8', 'replace')[:300]}")
    return p.stdout


def blob(repo, rev, path):
    p = subprocess.run(["git", "-C", repo, "show", f"{rev}:{path}"], capture_output=True)
    return p.stdout if p.returncode == 0 else None


def split_lines(data):
    if data is None:
        return []
    lines = data.split(b"\n")
    if lines and lines[-1] == b"":
        lines.pop()
    return lines


def key(line):
    if line.endswith(b"\r"):
        line = line[:-1]
    return hashlib.sha256(line).hexdigest()


# ---------------------------------------------------------------- fences/sections
def fence_flags(lines):
    """True on every line that opens, closes, or lies inside a CommonMark fence."""
    if FENCE_BLIND:
        return [False] * len(lines)
    flags = []
    fence = None  # (char, run length)
    for raw in lines:
        s = raw.decode("utf-8", "surrogateescape")
        m = FENCE_OPEN.match(s)
        if fence is None:
            if m and not (m.group(1)[0] == "`" and "`" in m.group(2)):
                fence = (m.group(1)[0], len(m.group(1)))
                flags.append(True)
            else:
                flags.append(False)
        else:
            flags.append(True)
            if (m and m.group(1)[0] == fence[0]
                    and len(m.group(1)) >= fence[1]
                    and m.group(2).strip(" \t") == ""):
                fence = None
    return flags


def sections(lines):
    """headed[i] = heading text in force at line i (None before the first)."""
    fl = fence_flags(lines)
    out = []
    cur = None
    for raw, fenced in zip(lines, fl):
        s = raw.decode("utf-8", "surrogateescape").rstrip("\r").rstrip(" \t")
        if not fenced and s.startswith("## "):
            cur = s
        out.append(cur)
    return out, fl


# ---------------------------------------------------------------- contract
def parse_region(field):
    body = field
    at = body.rfind("@")
    if at > 0 and body.startswith(("exempt=", "only=")):
        body = body[:at]
    if body.strip() == "*":
        return ("all", None)
    if body.startswith("exempt="):
        return ("exempt", [x for x in body[len("exempt="):].split("|")])
    if body.startswith("only="):
        return ("only", body[len("only="):])
    raise Fail(f"unparsed region: {field!r}")


def read_contract(repo, rev):
    data = blob(repo, rev, CONTRACT)
    if data is None:
        return []
    rows = []
    for i, line in enumerate(data.decode("utf-8").splitlines()):
        if i == 0 or not line.strip():
            continue
        path, rule, declared, region, note = line.split("\t")
        rows.append({"path": path, "rule": rule, "declared": declared,
                     "region_field": region, "region": parse_region(region), "note": note})
    return rows


def expand(repo, rev, pattern):
    names = git(repo, "ls-tree", "-r", "--name-only", rev).decode().splitlines()
    if "*" in pattern:
        rx = re.compile("^" + re.escape(pattern).replace(r"\*", "[^/]*") + "$")
        return [n for n in names if rx.match(n)]
    return [pattern] if pattern in names else []


# ---------------------------------------------------------------- diff parsing
def sections_of_patch(patch):
    """[(old_path, new_path, [deleted 1-based parent line numbers])]"""
    out = []
    lines = patch.split(b"\n")
    i = 0
    cur = None
    while i < len(lines):
        ln = lines[i]
        m = DIFFHDR.match(ln)
        if m:
            if cur is not None:
                out.append(tuple(cur))
            cur = [m.group(1).decode("utf-8", "surrogateescape"),
                   m.group(2).decode("utf-8", "surrogateescape"), [], False]
            i += 1
            continue
        if ln.startswith(b"@@") and cur is not None:
            hm = HUNK.match(ln)
            if not hm:
                raise Fail(f"bad hunk header {ln[:80]!r}")
            old_start = int(hm.group(1))
            old_count = int(hm.group(2)) if hm.group(2) is not None else 1
            new_count = int(hm.group(4)) if hm.group(4) is not None else 1
            minus = plus = 0
            j = i + 1
            while j < len(lines) and not lines[j].startswith((b"@@", b"diff --git ")):
                if lines[j].startswith(b"-"):
                    minus += 1
                elif lines[j].startswith(b"+"):
                    plus += 1
                elif lines[j].startswith(b"\\"):
                    pass
                j += 1
            if minus != old_count or plus != new_count:
                raise Fail(f"hunk count mismatch {cur[0]}: hdr -{old_count}/+{new_count} "
                           f"body -{minus}/+{plus}")
            cur[2].extend(range(old_start, old_start + old_count))
            i = j
            continue
        if ln.startswith(b"Binary files ") and cur is not None:
            cur[3] = True  # binary: no line-level deletions visible
        i += 1
    if cur is not None:
        out.append(tuple(cur))
    return out


# ---------------------------------------------------------------- cells
def split_cells(line):
    """Split a markdown row into cells: `\\|` and `|` inside code spans are content."""
    s = line.strip()
    if not s.startswith(b"|"):
        return None
    cells = []
    buf = bytearray()
    i = 0
    in_code = False
    while i < len(s):
        c = s[i]
        if c == 0x5C and i + 1 < len(s) and s[i + 1] == 0x7C:
            buf += b"\\|"
            i += 2
            continue
        if c == 0x60:
            in_code = not in_code
            buf.append(c)
            i += 1
            continue
        if c == 0x7C and not in_code:
            cells.append(bytes(buf).strip())
            buf = bytearray()
            i += 1
            continue
        buf.append(c)
        i += 1
    cells.append(bytes(buf).strip())
    if cells and cells[0] == b"":
        cells = cells[1:]
    if cells and cells[-1] == b"":
        cells = cells[:-1]
    return cells or None


def row_id(line):
    m = ROW.match(line)
    return m.group(1).decode() if m else None


def permitted_row_survivor(row, new_rows_by_id):
    cells = split_cells(row)
    rid = row_id(row)
    if cells is None or rid is None:
        return False, "unparsed-row"
    cands = new_rows_by_id.get("S" + rid, [])
    if not cands:
        return False, "id-gone"
    for nc in cands:
        if len(nc) != len(cells):
            continue
        if all(nc[k] == cells[k] for k in range(len(cells)) if k not in MUTABLE):
            return True, "id-held-immutable-equal"
    return False, "immutable-cell-changed"


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--tip", required=True)
    ap.add_argument("--base", default="9ff76b1f763512be2f554cbbfd0b2213b63b0847")
    ap.add_argument("--out", default=None)
    ap.add_argument("--fence-blind", action="store_true",
                    help="sensitivity: ignore fences when computing sections")
    a = ap.parse_args()
    global FENCE_BLIND
    FENCE_BLIND = a.fence_blind
    repo, tip, base = a.repo, a.tip, a.base

    rows = read_contract(repo, tip)
    base_rows = read_contract(repo, base)
    def sig(r):
        return (r["path"], r["rule"], r["region_field"])
    contract_same = sorted(map(sig, base_rows)) == sorted(map(sig, rows))

    files = {}
    for r in rows:
        for path in expand(repo, tip, r["path"]):
            files[path] = (r["rule"], r["region"])

    tip_lines = {p: split_lines(blob(repo, tip, p)) for p in files}
    tip_keys = {p: collections.Counter(key(l) for l in tip_lines[p]) for p in files}

    commits = git(repo, "rev-list", "--topo-order", "--parents", tip).decode().splitlines()
    commits.reverse()
    stats = {p: collections.Counter() for p in files}
    unheld_by_file = collections.Counter()
    unheld_rows = []
    ungraded_by_region = collections.Counter()
    undecided = []
    events = 0
    parent_lines_cache = {}
    parent_keys_cache = {}
    sec_cache = {}

    for cline in commits:
        parts = cline.split()
        c, parents = parts[0], parts[1:]
        if not parents:
            continue
        p = parents[0]
        patch = git(repo, "diff", "--no-color", "--no-ext-diff", "--no-renames",
                    "-U0", p, c)
        for old_path, new_path, delnos, binary in sections_of_patch(patch):
            path = new_path if new_path in files else (old_path if old_path in files else None)
            if path is None:
                continue
            if binary:
                undecided.append(f"{c[:12]} {path}: binary diff section")
                continue
            if not delnos:
                continue
            rule, region = files[path]
            pk = (p, path)
            if pk not in parent_lines_cache:
                parent_lines_cache[pk] = split_lines(blob(repo, p, path))
                parent_keys_cache[pk] = collections.Counter(
                    key(l) for l in parent_lines_cache[pk])
                sec_cache[pk] = sections(parent_lines_cache[pk])[0]
            plines = parent_lines_cache[pk]
            pkeys = parent_keys_cache[pk]
            psecs = sec_cache[pk]
            new_lines = split_lines(blob(repo, c, path))
            new_rows_by_id = {}
            if rule == "A-row":
                for nl in new_lines:
                    rid = row_id(nl)
                    if rid:
                        cs = split_cells(nl)
                        if cs:
                            new_rows_by_id.setdefault("S" + rid, []).append(cs)
            G = collections.Counter()
            D = collections.Counter()
            for n in delnos:
                if n < 1 or n > len(plines):
                    undecided.append(f"{c[:12]} {path}: diff old line {n} outside "
                                     f"parent blob ({len(plines)} lines)")
                    continue
                line = plines[n - 1]
                k = key(line)
                D[k] += 1
                stats[path]["deleted"] += 1
                sec = psecs[n - 1]
                mode, arg = region
                if mode == "all":
                    grade = True
                elif mode == "exempt":
                    grade = sec not in arg
                elif mode == "only":
                    grade = sec is not None and sec.startswith(arg)
                else:
                    raise Fail("bad region mode")
                if grade and rule == "A-row" and row_id(line) is not None:
                    ok, why = permitted_row_survivor(line, new_rows_by_id)
                    if ok:
                        grade = False
                        stats[path]["permitted_rows"] += 1
                if grade:
                    G[k] += 1
                    stats[path]["graded"] += 1
                else:
                    ungraded_by_region[(path, rule, mode)] += 1
            events += 1
            for k, g in G.items():
                Pk = pkeys.get(k, 0)
                kept = max(0, Pk - D[k])
                M = tip_keys[path].get(k, 0)
                restored = max(0, M - kept)
                held = min(g, restored)
                stats[path]["held_by_tip"] += held
                if g - held > 0:
                    unheld_by_file[path] += g - held
                    unheld_rows.append({
                        "commit": c, "file": path, "line_sha256": k,
                        "count": g - held, "class": "in-place-edit",
                        "parent_count": Pk, "deleted_copies": D[k],
                        "kept": kept, "tip_count": M, "restored": restored,
                    })

    led_raw = blob(repo, tip, LEDGER)
    ledger_rows = []
    if led_raw is not None:
        for ln in led_raw.decode("utf-8").splitlines():
            if not ln.strip() or ln.startswith("commit\t"):
                continue
            commit, f, sha, count, klass, note = ln.split("\t")
            ledger_rows.append({"commit": commit, "file": f, "line_sha256": sha,
                                "count": int(count), "class": klass, "note": note})
    led_keys = collections.Counter((r["commit"], r["file"], r["line_sha256"], r["count"])
                                   for r in ledger_rows)
    my_keys = collections.Counter((r["commit"], r["file"], r["line_sha256"], r["count"])
                                  for r in unheld_rows)
    matched, missing, extra = led_keys & my_keys, led_keys - my_keys, my_keys - led_keys

    a_corr = [p for p, (r, _) in files.items() if r == "A-corr"]
    corr_lost = sum(unheld_by_file[p] for p in a_corr)
    row_lost = sum(unheld_by_file[p] for p in files if files[p][0] in ("A", "A-row"))

    per_file = {}
    for p, (rule, _) in sorted(files.items()):
        per_file[p] = {"rule": rule, **{f: stats[p][f] for f in
                                        ("deleted", "graded", "permitted_rows",
                                         "held_by_tip")},
                       "unheld": unheld_by_file[p]}
    per_rule = collections.defaultdict(collections.Counter)
    for p, d in per_file.items():
        for f in ("deleted", "graded", "permitted_rows", "held_by_tip", "unheld"):
            per_rule[d["rule"]][f] += d[f]

    result = {
        "tip": tip, "base": base, "files_audited": len(files),
        "commits_walked": len(commits), "deletion_events": events,
        "corr_lost": corr_lost, "row_lost": row_lost,
        "ledger_rows": len(ledger_rows), "ledger_matched": len(matched),
        "ledger_missing_from_mine": [list(x) for x in missing.elements()],
        "my_unheld_absent_from_ledger": [list(x) for x in extra.elements()],
        "contract_rows_same_base_tip": contract_same,
        "per_rule": {k: dict(v) for k, v in per_rule.items()},
        "per_file": per_file, "unheld": unheld_rows, "undecided": undecided,
        "files": sorted(files),
        "regions": {r["path"]: r["region_field"] for r in rows},
    }
    txt = []
    txt.append(f"tip={tip} base={base} files={len(files)} commits={len(commits)} "
               f"deletion_events={events} contract_rows_same_base_tip={contract_same}")
    txt.append(f"corr_lost={corr_lost} row_lost={row_lost} ledger_rows={len(ledger_rows)} "
               f"ledger_matched={len(matched)} ledger_missing={sum(missing.values())} "
               f"my_extra={sum(extra.values())}")
    for rule in sorted(per_rule):
        c = per_rule[rule]
        txt.append(f"RULE {rule}: deleted={c['deleted']} graded={c['graded']} "
                   f"permitted_rows={c['permitted_rows']} held_by_tip={c['held_by_tip']} "
                   f"unheld={c['unheld']}")
    txt.append("PER-FILE:")
    for p, d in sorted(per_file.items()):
        if d["deleted"] or d["unheld"]:
            txt.append(f"  {p}\trule={d['rule']}\tdeleted={d['deleted']}\tgraded={d['graded']}"
                       f"\tpermitted={d['permitted_rows']}\theld={d['held_by_tip']}"
                       f"\tunheld={d['unheld']}")
    txt.append("UNHELD KEYS:")
    for r in unheld_rows:
        txt.append(f"  {r['commit']} {r['file']} {r['line_sha256'][:12]} count={r['count']} "
                   f"P={r['parent_count']} D={r['deleted_copies']} K={r['kept']} "
                   f"M={r['tip_count']} restored={r['restored']}")
    if missing:
        txt.append("LEDGER ROW NOT REPRODUCED:")
        for x in missing.elements():
            txt.append("  " + " ".join(map(str, x)))
    if extra:
        txt.append("MY UNHELD NOT IN LEDGER:")
        for x in extra.elements():
            txt.append("  " + " ".join(map(str, x)))
    txt.append("UNGRADED BY REGION (exempt/only lines removed by rule):")
    for (path, rule, mode), n in sorted(ungraded_by_region.items()):
        txt.append(f"  {path}\trule={rule}\tmode={mode}\tlines={n}")
    if undecided:
        txt.append("UNDECIDED:")
        txt.extend("  " + u for u in undecided)
    out = "\n".join(txt) + "\n"
    sys.stdout.write(out)
    if a.out:
        with open(a.out, "w") as fh:
            json.dump(result, fh, indent=1, sort_keys=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
