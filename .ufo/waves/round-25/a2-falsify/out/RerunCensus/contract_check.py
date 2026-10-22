#!/usr/bin/env python3
"""RerunCensus: census and SOURCES-contract checks for kama round 25 at fa3b62ae.

Compares the base 147f5bdd and tip fa3b62ae extractions (scratch), re-implements the
CORPUS.md frozen census, checks the eight new rows and the round lesson Gate against the
llama.cpp bytes fetched at 704366d76, and checks the knowledge-entry citations.
Writes contract-check.json and lesson-worktree.diff into this directory. Reads only.
"""
import collections
import difflib
import hashlib
import json
import pathlib
import re

S = pathlib.Path("/fast/scratch/hyaku/kama-r25a2w2/RerunCensus")
LANE = pathlib.Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
FLEET_SCRIPT = pathlib.Path("/home/vgpnk/Projects/shokunin/scripts/sources-census.sh")
OUT = LANE / ".ufo/waves/round-25/a2-falsify/out/RerunCensus"
BASE = S / "base/kama-shokunin"
TIP = S / "tip/kama-shokunin"
SRC = S / "src"
HDR = ["id", "source", "kind", "tier", "scope", "anchor", "teaches", "status", "opened", "recheck", "used-by"]
KIND = {"spec", "docs", "paper", "code", "tool", "dataset", "talk", "book", "community", "own-work"}
ROW = re.compile(r"^ {0,3}\|\s*S\d{3,}\s*\|")
NEW = ["S%d" % n for n in range(106, 114)]
FETCHED = {
    "S106": "common_fit.cpp",
    "S107": "src_llama-context.cpp",
    "S108": "tools_server_server.cpp",
    "S109": "tools_server_server-context.cpp",
    "S110": "common_arg.cpp",
    "S111": "common_common.cpp",
    "S112": "tools_server_README.md",
    "S113": "src_llama-kv-cache.cpp",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_lines(path):
    return path.read_text(encoding="utf-8", errors="replace").splitlines()


def url_of(cell):
    m = re.search(r"https?://\S+", cell)
    return m.group(0).rstrip(")") if m else ""


def rows_of(lines):
    out = {}
    for i, ln in enumerate(lines, 1):
        if ROW.match(ln):
            cells = [c.strip() for c in ln.split("|")[1:-1]]
            out[cells[0]] = {"line": i, "cells": cells, "fields": len(ln.split("|"))}
    return out


def frozen(root):
    """CORPUS.md frozen census, re-implemented with the same regexes and column rules."""
    rows, malformed = [], 0
    for ln in read_lines(root / "corpus/SOURCES.md"):
        if re.match(r"^\|[ \t]*S[0-9]{3,}[ \t]*\|", ln):
            f = ln.split("|")
            if len(f) != 13:
                malformed += 1
                continue
            rows.append([x.strip() for x in f])
    ids = [r[1] for r in rows]
    bad = []
    for r in rows:
        if r[4] not in ("A", "B", "C"):
            bad.append(["tier", r[1], r[4]])
        if r[8] not in ("queued", "mined", "rejected"):
            bad.append(["status", r[1], r[8]])
        if r[3] not in KIND:
            bad.append(["kind", r[1], r[3]])
        if r[4] == "A" and r[3] == "community":
            bad.append(["tier-inflation", r[1]])
    missing = []
    for r in rows:
        if r[8] == "mined":
            for p in re.split(r"[,;]", r[11]):
                p = p.strip()
                if p not in ("", "\u2014") and not (root / p).exists():
                    missing.append([r[1], p])
    return {
        "rows": len(rows),
        "malformed": malformed,
        "tier": dict(collections.Counter(r[4] for r in rows)),
        "status": dict(collections.Counter(r[8] for r in rows)),
        "dup_ids": sorted({i for i in ids if ids.count(i) > 1}),
        "enum_violations": bad,
        "missing_used_by": missing,
    }


def stated_numbers(cell):
    out = set()
    for a, b in re.findall(r"(\d{3,5})(?:\s*[-\u2013]\s*(\d{3,5}))?", cell):
        lo = int(a)
        hi = int(b) if b else lo
        out.update(range(lo, hi + 1))
    return out


def locate(lines, text):
    t = re.sub(r"\s+", " ", text).strip()
    if not t:
        return []
    return [i for i, ln in enumerate(lines, 1) if t in re.sub(r"\s+", " ", ln)]


def ranges(text, dash):
    return [(int(a), int(b)) for a, b in re.findall(r"(\d{4})" + dash + r"(\d{4})", text)]


def inside(n, rs):
    return any(a <= n <= b for a, b in rs)


def main():
    result = {}
    base_lines = read_lines(BASE / "corpus/SOURCES.md")
    tip_lines = read_lines(TIP / "corpus/SOURCES.md")
    rb, rt = rows_of(base_lines), rows_of(tip_lines)
    new = sorted(set(rt) - set(rb), key=lambda s: int(s[1:]))
    result["hashes"] = {
        "base_SOURCES_md": sha(BASE / "corpus/SOURCES.md"),
        "tip_SOURCES_md": sha(TIP / "corpus/SOURCES.md"),
        "lane_worktree_SOURCES_md": sha(LANE / "corpus/SOURCES.md"),
        "fleet_sources_census_sh": sha(FLEET_SCRIPT),
    }
    result["registry"] = {
        "base_rows": len(rb),
        "tip_rows": len(rt),
        "new": new,
        "removed": sorted(set(rb) - set(rt)),
        "new_row_lines": {k: rt[k]["line"] for k in new},
        "field_counts_tip": sorted({v["fields"] for v in rt.values()}),
    }
    changes = []
    for k in sorted(set(rb) & set(rt), key=lambda s: int(s[1:])):
        for j, (a, b) in enumerate(zip(rb[k]["cells"], rt[k]["cells"])):
            if a != b:
                changes.append({"id": k, "column": HDR[j], "old": a, "new": b, "tip_line": rt[k]["line"]})
    result["old_row_cell_changes"] = changes
    sm = difflib.SequenceMatcher(a=base_lines, b=tip_lines, autojunk=False)
    result["non_equal_blocks"] = [
        {"op": t, "base_lines": [i1 + 1, i2], "tip_lines": [j1 + 1, j2]}
        for t, i1, i2, j1, j2 in sm.get_opcodes()
        if t != "equal"
    ]
    result["frozen_census"] = {"base": frozen(BASE), "tip": frozen(TIP)}

    lesson = (TIP / "corpus/lessons/round-25.md").read_text(encoding="utf-8")
    flat = re.sub(r"\s+", " ", lesson)
    m = re.search(r"Old-row change: (.*?)No status or recheck cell changed", flat)
    ticks = re.findall(r"`([^`]+)`", m.group(1)) if m else []
    result["old_row_log"] = {
        "found": bool(m),
        "ticks": ticks,
        "logged_old_new_match_census_change": len(ticks) == 3 and len(changes) == 1
        and ticks[1] == changes[0]["old"] and ticks[2] == changes[0]["new"],
        "changed_columns": sorted({c["column"] for c in changes}),
    }

    gate = []
    for ln in lesson.splitlines():
        g = re.match(r"^\| (S1\d\d) \| (\S+) \| (.*) \|$", ln)
        if not g:
            continue
        sid, url, cell = g.groups()
        src_lines = read_lines(SRC / FETCHED[sid])
        stated = stated_numbers(cell)
        qres = []
        for bt, dq in re.findall(r"`([^`]+)`|\"([^\"]+)\"", cell):
            q = bt or dq
            hits = locate(src_lines, q)
            split_hits = None
            if hits:
                ok = any(h in stated for h in hits)
            elif "; " in q:
                split_hits = [locate(src_lines, p.strip()) for p in q.split("; ") if p.strip()]
                ok = all(split_hits) and any(h in stated for ph in split_hits for h in ph)
            else:
                ok = False
            qres.append({"quote": q, "words": len(q.split()), "hits": hits,
                         "split_hits": split_hits, "in_stated_location": ok})
        anchor_shas = re.findall(r"\b[0-9a-f]{64}\b", rt[sid]["cells"][5])
        digest = sha(SRC / FETCHED[sid])
        gate.append({"id": sid, "url_equals_row_url": url == url_of(rt[sid]["cells"][1]),
                     "stated_lines": sorted(stated), "quotes": qres,
                     "fetched_sha256": digest, "anchor_sha256": anchor_shas,
                     "anchor_sha_matches_fetched": digest in anchor_shas})
    result["gate"] = gate

    result["new_rows"] = {}
    for sid in new:
        c = rt[sid]["cells"]
        result["new_rows"][sid] = {
            "tier": c[3], "kind": c[2], "status": c[7], "opened": c[8], "recheck": c[9], "used_by": c[10],
            "anchor_names_commit_or_release": bool(re.search(r"704366d|b11755", c[5])),
            "anchor_words": len(c[5].split()), "teaches_words": len(c[6].split()),
        }
    old_t = sorted(len(v["cells"][6].split()) for v in rb.values())
    result["teaches_words"] = {"old_max": old_t[-1], "old_median": old_t[len(old_t) // 2],
                               "new": {s: len(rt[s]["cells"][6].split()) for s in new}}

    w04 = {}
    for sid in new:
        u = url_of(rt[sid]["cells"][1])
        w04[sid] = [k for k in sorted(rt, key=lambda s: int(s[1:]))
                    if int(k[1:]) < int(sid[1:]) and url_of(rt[k]["cells"][1]) == u]
    result["shared_url_with_earlier_rows"] = w04

    kn_text = "\n".join(read_lines(TIP / "corpus/knowledge/context-capacity.md"))
    result["knowledge_mentions"] = {s: len(re.findall(r"\b%s\b" % s, kn_text)) for s in NEW + ["S060"]}
    sc = read_lines(SRC / "tools_server_server-context.cpp")
    cc = read_lines(SRC / "common_common.h")
    cl = read_lines(SRC / "src_llama-context.cpp")
    s060_ranges = ranges(rt["S060"]["cells"][5], "\u2013")
    s107_ranges = ranges(rt["S107"]["cells"][5], "-")
    result["knowledge_line_citations"] = [
        {"where": "corpus/knowledge/context-capacity.md:45", "cites": "server-context.cpp 1437 under S060",
         "text": sc[1436].strip(), "S060_anchor_ranges": s060_ranges,
         "inside_S060_anchor": inside(1437, s060_ranges)},
        {"where": "corpus/knowledge/context-capacity.md:60", "cites": "common.h 580 under S110",
         "text": cc[579].strip(), "registry_mentions_common_h": sum(ln.count("common.h") for ln in tip_lines)},
        {"where": "corpus/knowledge/context-capacity.md:168", "cites": "S107 4113-4117",
         "text": cl[4112].strip(), "S107_anchor_ranges": s107_ranges,
         "4113_inside_anchor": inside(4113, s107_ranges), "4117_inside_anchor": inside(4117, s107_ranges)},
    ]
    result["fetched_sources"] = {}
    for sid, name in list(FETCHED.items()) + [("common/common.h (cited, no row)", "common_common.h")]:
        p = SRC / name
        result["fetched_sources"][sid] = {"file": name, "bytes": p.stat().st_size, "sha256": sha(p)}

    rd = read_lines(SRC / "tools_server_README.md")
    result["readme_kv_sized_pool_lines"] = [[i, l.strip()[:110]] for i, l in enumerate(rd, 1)
                                            if re.search(r"(?i)\bkv\b|sized|\bpool\b", l)]
    k5 = read_lines(TIP / ".ufo/waves/round-25/final/raw/K5.server.log")
    result["k5_log_n_ctx_lines"] = [[i, l.strip()[:150]] for i, l in enumerate(k5, 1) if "n_ctx" in l][:25]

    wt = (LANE / "corpus/lessons/round-25.md").read_text(encoding="utf-8").splitlines(keepends=True)
    pinned = (TIP / "corpus/lessons/round-25.md").read_text(encoding="utf-8").splitlines(keepends=True)
    diff = "".join(difflib.unified_diff(pinned, wt, "pinned fa3b62ae corpus/lessons/round-25.md",
                                        "lane worktree corpus/lessons/round-25.md"))
    (OUT / "lesson-worktree.diff").write_text(diff, encoding="utf-8")
    result["lesson_worktree_diff"] = {
        "changed_lines": sum(1 for x in diff.splitlines()
                             if x[:1] in ("+", "-") and not x.startswith(("+++", "---"))),
        "touches_gate_or_old_row_lines": bool(re.search(r"Gate|Old-row|Status of all|^[-+]\| S1\d\d ", diff, re.M)),
    }

    (OUT / "contract-check.json").write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n",
                                             encoding="utf-8")
    print("hashes", result["hashes"])
    print("registry base/tip", len(rb), len(rt), "new", new, "removed", result["registry"]["removed"])
    print("old-row cell changes", [(c["id"], c["column"], c["tip_line"]) for c in changes])
    print("old-row log", result["old_row_log"])
    fb, ft = result["frozen_census"]["base"], result["frozen_census"]["tip"]
    print("frozen base", {k: fb[k] for k in ("rows", "malformed", "tier", "status", "dup_ids", "missing_used_by")},
          "enum", fb["enum_violations"])
    print("frozen tip ", {k: ft[k] for k in ("rows", "malformed", "tier", "status", "dup_ids", "missing_used_by")},
          "enum", ft["enum_violations"])
    for g in gate:
        print("gate", g["id"], "url_ok", g["url_equals_row_url"], "sha_ok", g["anchor_sha_matches_fetched"],
              "quotes", [(q["words"], q["in_stated_location"], q["hits"] or q["split_hits"]) for q in g["quotes"]])
    print("anchor commit/release token", {s: result["new_rows"][s]["anchor_names_commit_or_release"] for s in new})
    print("teaches words", result["teaches_words"])
    print("knowledge mentions", result["knowledge_mentions"])
    for c in result["knowledge_line_citations"]:
        print("citation", c["where"], "|", c["cites"], "|", c["text"][:80], "|",
              {k: v for k, v in c.items() if k not in ("where", "cites", "text")})
    print("shared URL with earlier rows", w04)
    print("README kv/sized/pool lines", result["readme_kv_sized_pool_lines"])
    print("K5 n_ctx lines", result["k5_log_n_ctx_lines"][:12])
    print("lesson worktree diff", result["lesson_worktree_diff"])


if __name__ == "__main__":
    main()
