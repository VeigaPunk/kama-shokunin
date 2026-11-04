#!/usr/bin/env python3
"""Part (b): every receipt cited by .ufo/reports/round-71/kama.md, the revision the
receipt names, and the revision the report claims it measured."""
import json
import re
import subprocess

L = "/home/vgpnk/Projects/shokunin/kama-shokunin"
REPORT = "/home/vgpnk/Projects/shokunin/.ufo/reports/round-71/kama.md"
TIP = "a3cc39f08f4692e990921cf938d0269f6c25fc93"
OUT = "/fast/scratch/hyaku/kama-r72/SCT01ReceiptRecon"


def git(*args):
    p = subprocess.run(["git", "-C", L] + list(args), capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


text = open(REPORT).read()
TREE = set(git("ls-tree", "-r", "--name-only", TIP)[1].splitlines())
TREE_DIRS = set()
for f in TREE:
    parts = f.split("/")
    for i in range(1, len(parts)):
        TREE_DIRS.add("/".join(parts[:i]))

WAVE_ROOTED = re.compile(r"\.ufo/waves/round-\d+/[A-Za-z0-9._/*{},+-]+")
RELATIVE = re.compile(r"(?<![\w./-])(measured|controls|w1)/[A-Za-z0-9._/*{},+-]+")
TRAIL = ".,;:)]'\"`"


def brace_expand(path):
    m = re.search(r"\{([^{}]*)\}", path)
    if not m:
        return [path]
    out = []
    for part in m.group(1).split(","):
        out.extend(brace_expand(path[: m.start()] + part + path[m.end():]))
    return out


def glob_expand(path):
    if "*" not in path:
        return [path]
    pat = re.compile("^" + re.escape(path).replace(r"\*", "[^/]*") + "$")
    hits = sorted(p for p in TREE if pat.match(p))
    return hits or [path]


spans = []
for m in WAVE_ROOTED.finditer(text):
    spans.append((m.start(), m.end(), m.group(0)))
for m in RELATIVE.finditer(text):
    if any(s <= m.start() < e for s, e, _ in spans):
        continue
    spans.append((m.start(), m.end(), ".ufo/waves/round-71/" + m.group(0)))

cites = []
for _, _, raw in spans:
    base = raw.rstrip(TRAIL).rstrip("/")
    if base:
        cites.append(base)

rows = []
seen = set()
for c in cites:
    for e in brace_expand(c):
        for p in glob_expand(e):
            if p in seen:
                continue
            seen.add(p)
            typ = "tree" if p in TREE_DIRS else ("blob" if p in TREE else None)
            rec = {"path": p, "type": typ,
                   "kind": "dir" if typ == "tree" else ("script" if p.endswith(".py") else ("receipt" if ("/measured/" in p or p.endswith(".out")) else "evidence")),
                   "exists": typ is not None, "header_rev": None, "header_line": None,
                   "header_strict": False, "ancestor": None}
            if typ == "blob":
                for ln in git("show", f"{TIP}:{p}")[1].splitlines()[:5]:
                    m = re.match(r"^#\s*(?:tip|rev)=([0-9a-f]{40})\b", ln)
                    if m:
                        rec.update(header_rev=m.group(1), header_line=ln, header_strict=True)
                        break
                if rec["header_rev"] is None:
                    for ln in git("show", f"{TIP}:{p}")[1].splitlines()[:5]:
                        m = re.match(r"^\s*(?:tip|rev)=([0-9a-f]{40})\b", ln)
                        if m:
                            rec.update(header_rev=m.group(1), header_line=ln, header_strict=False)
                            break
            if rec["header_rev"]:
                rc, _, _ = git("merge-base", "--is-ancestor", rec["header_rev"], TIP)
                rec["ancestor"] = rc == 0
            rows.append(rec)

json.dump(rows, open(f"{OUT}/report71-receipts.json", "w"), indent=1)
for r in sorted(rows, key=lambda x: (x["kind"], x["path"])):
    print("\t".join([r["kind"], r["path"].replace(".ufo/waves/", "W:"),
                     (r["header_rev"] or "-")[:12],
                     "strict" if r["header_strict"] else ("lenient" if r["header_rev"] else "-"),
                     str(r["exists"]), str(r["ancestor"])]))
