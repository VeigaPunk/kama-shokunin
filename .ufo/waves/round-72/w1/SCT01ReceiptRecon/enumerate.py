#!/usr/bin/env python3
"""Enumerate every .ufo/waves/round-7[0-9]/... path cited by the round-70/71 SCORECARD
sections and corpus/lessons/round-7*.md, then grade each receipt against the lane tip.

Read-only: git plumbing only (cat-file, show, diff, merge-base, ls-tree).
"""
import json
import re
import subprocess
import sys

L = "/home/vgpnk/Projects/shokunin/kama-shokunin"
TIP = sys.argv[1] if len(sys.argv) > 1 else "master"
OUT = "/fast/scratch/hyaku/kama-r72/SCT01ReceiptRecon"

INSTRUMENT_SPEC = ("tools/", "SKILL.md", "PROVINCE.md", "corpus/SOURCES.md", "corpus/knowledge/")
INSTRUMENT_FREEZE = INSTRUMENT_SPEC + ("registry/", "plans/")


def git(*args):
    p = subprocess.run(["git", "-C", L] + list(args), capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def show(rev_path):
    rc, out, _ = git("show", rev_path)
    return out if rc == 0 else None


def blob_type(rev_path):
    rc, out, _ = git("cat-file", "-t", rev_path)
    return out.strip() if rc == 0 else None


TIP_SHA = git("rev-parse", TIP)[1].strip()
TREE = git("ls-tree", "-r", "--name-only", TIP)[1].splitlines()
TREE_SET = set(TREE)
TREE_DIRS = set()
for f in TREE:
    parts = f.split("/")
    for i in range(1, len(parts)):
        TREE_DIRS.add("/".join(parts[:i]))

# ---- source regions -------------------------------------------------------
scorecard = show(f"{TIP}:SCORECARD.md")
slines = scorecard.splitlines()


def heading_index(prefix):
    for i, ln in enumerate(slines):
        if ln.startswith(prefix):
            return i
    raise SystemExit(f"missing heading {prefix!r}")


i70 = heading_index("## Round 70 ")
i71 = heading_index("## Round 71 ")
regions = [
    ("SCORECARD.md#Round-70", 70, "\n".join(slines[i70:i71])),
    ("SCORECARD.md#Round-71", 71, "\n".join(slines[i71:])),
]
for name, rnd in [
    ("corpus/lessons/round-70.md", 70),
    ("corpus/lessons/round-70-verifier-spotcheck.md", 70),
    ("corpus/lessons/round-71.md", 71),
    ("corpus/lessons/round-71-verifier-spotcheck.md", 71),
]:
    txt = show(f"{TIP}:{name}")
    if txt is None:
        raise SystemExit(f"missing {name}")
    regions.append((name, rnd, txt))

WAVE_ROOTED = re.compile(r"\.ufo/waves/round-7[0-9]/[A-Za-z0-9._/*{},+-]+")
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
    """Expand '*' segments against the tip tree; a non-glob path passes through."""
    if "*" not in path:
        return [path]
    pat = re.compile("^" + re.escape(path).replace(r"\*", "[^/]*") + "$")
    hits = sorted(p for p in TREE_SET if pat.match(p))
    if hits:
        return hits
    # directory-level glob (e.g. .../measured/final/*)
    dpat = re.compile("^" + re.escape(path).replace(r"\*", ".*") + "$")
    return sorted(p for p in TREE_SET if dpat.match(p))


raw_cites = []
for source, rnd, text in regions:
    spans = []
    for m in WAVE_ROOTED.finditer(text):
        spans.append((m.start(), m.end(), m.group(0), False))
    for m in RELATIVE.finditer(text):
        if any(s <= m.start() < e for s, e, _, _ in spans):
            continue
        spans.append((m.start(), m.end(), ".ufo/waves/round-%d/" % rnd + m.group(0), True))
    for start, end, raw, relative in spans:
        is_dir = raw.rstrip(TRAIL).endswith("/")
        base = raw.rstrip(TRAIL).rstrip("/")
        if not base:
            continue
        raw_cites.append({"source": source, "round": rnd, "cited": raw,
                          "dir_cited": is_dir, "relative": relative, "base": base})

rows = []
for c in raw_cites:
    for expanded in brace_expand(c["base"]):
        for path in glob_expand(expanded):
            rows.append({**c, "path": path})

seen = set()
uniq = []
for r in rows:
    k = (r["source"], r["path"])
    if k in seen:
        continue
    seen.add(k)
    uniq.append(r)
rows = uniq

# ---- classify + grade -----------------------------------------------------
def touched(rev, prefixes):
    rc, out, _ = git("diff", "--name-only", rev, TIP_SHA)
    if rc != 0:
        return None, []
    files = out.splitlines()
    hits = [p for p in files if any(p == x or p.startswith(x) for x in prefixes)]
    return files, hits


for r in rows:
    p = r["path"]
    if p in TREE_DIRS:
        typ = "tree"
    elif p in TREE_SET:
        typ = "blob"
    else:
        typ = blob_type(f"{TIP_SHA}:{p}")
    r["type"] = typ
    if typ is None:
        r["kind"] = "missing"
    elif typ == "tree":
        r["kind"] = "dir"
    elif p.endswith(".py"):
        r["kind"] = "script"
    elif "/measured/" in p or p.endswith(".out"):
        r["kind"] = "receipt"
    else:
        r["kind"] = "evidence"
    r["exists"] = typ is not None
    r["header_rev"] = None
    r["header_line"] = None
    r["header_strict"] = False
    if typ == "blob":
        for ln in show(f"{TIP_SHA}:{p}").splitlines()[:5]:
            m = re.match(r"^#\s*(?:tip|rev)=([0-9a-f]{40})\b", ln)
            if m:
                r.update(header_rev=m.group(1), header_line=ln, header_strict=True)
                break
        if r["header_rev"] is None:
            for ln in show(f"{TIP_SHA}:{p}").splitlines()[:5]:
                m = re.match(r"^\s*(?:tip|rev)=([0-9a-f]{40})\b", ln)
                if m:
                    r.update(header_rev=m.group(1), header_line=ln, header_strict=False)
                    break
    for key in ("ancestor", "delta_files", "shifted_spec", "shifted_freeze", "shifted_paths"):
        r[key] = None
    if r["header_rev"]:
        rc, _, _ = git("merge-base", "--is-ancestor", r["header_rev"], TIP_SHA)
        r["ancestor"] = rc == 0
        files, hits = touched(r["header_rev"], INSTRUMENT_SPEC)
        r["delta_files"] = None if files is None else len(files)
        _, hits8 = touched(r["header_rev"], INSTRUMENT_FREEZE)
        # C2: a revision that is not an ancestor is a finding on its own.
        r["shifted_spec"] = bool(hits) or not r["ancestor"]
        r["shifted_freeze"] = bool(hits8) or not r["ancestor"]
        r["shift_reason"] = "non-ancestor" if not r["ancestor"] else ("instrument-input" if hits8 else "record-only")
        r["shifted_paths"] = hits8

json.dump({"tip": TIP_SHA, "rows": rows, "raw_cites": len(raw_cites)},
          open(f"{OUT}/recon.json", "w"), indent=1)

cols = ["source", "path", "kind", "exists", "hdr_rev", "strict", "anc", "shift5", "shift8", "delta", "shifted_paths"]
lines = ["\t".join(cols)]
for r in sorted(rows, key=lambda x: (x["source"], x["path"])):
    lines.append("\t".join(str(x) for x in [
        r["source"], r["path"], r["kind"], r["exists"],
        (r["header_rev"] or "-")[:12],
        r["header_strict"] if r["header_rev"] else "-",
        r["ancestor"] if r["ancestor"] is not None else "-",
        r["shifted_spec"] if r["shifted_spec"] is not None else "-",
        r["shifted_freeze"] if r["shifted_freeze"] is not None else "-",
        r["delta_files"] if r["delta_files"] is not None else "-",
        ",".join((r["shifted_paths"] or [])[:8]),
    ]))
open(f"{OUT}/table.tsv", "w").write("\n".join(lines) + "\n")

kinds = {}
for r in rows:
    kinds[r["kind"]] = kinds.get(r["kind"], 0) + 1
byst = {}
for r in rows:
    if r["kind"] == "receipt":
        k = (r["source"])
        byst.setdefault(k, {"receipt": 0, "unbound": 0, "strict": 0, "shift5": 0, "shift8": 0,
                            "stale": 0, "nonancestor": 0})
        d = byst[k]
        d["receipt"] += 1
        if not r["header_rev"]:
            d["unbound"] += 1
        else:
            d["strict"] += 1 if r["header_strict"] else 0
            d["shift5"] += 1 if r["shifted_spec"] else 0
            d["shift8"] += 1 if r["shifted_freeze"] else 0
            d["nonancestor"] += 0 if r["ancestor"] else 1
        if not r["exists"]:
            d["stale"] += 1
print(json.dumps({"tip": TIP_SHA, "raw_cites": len(raw_cites), "rows": len(rows),
                  "kinds": kinds, "distinct_paths": len({r["path"] for r in rows}),
                  "by_source_receipts": byst}, indent=1))
