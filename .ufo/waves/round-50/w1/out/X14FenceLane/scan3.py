#!/usr/bin/env python3
"""X14FenceLane scan3: same census over every contract-declared path, not just the seven
named in the seat brief. Supplements scan2 without changing its result."""
import fnmatch, json, subprocess, sys
import scan2

REPO = sys.argv[1]
PATTERNS = ["LOG.md", "SCORECARD.md", "corpus/QUALITY.md", "corpus/README.md",
            "corpus/SOURCES.md", "corpus/lessons/*.md", "registry/history/DELTA.md",
            "registry/report-landing-errata.tsv", "corpus/knowledge/consumer-registry.md",
            "corpus/knowledge/error-is-not-a-verdict.md"]


def git(*a, inp=None):
    return scan2.git(*a, inp=inp)


def main():
    revs = git("rev-list", "--all").decode().split()
    # every path any ref ever held that matches a contract pattern
    raw = git("log", "--all", "-z", "--format=", "--name-only", "--no-renames").split(b"\0")
    paths = sorted({p.decode("utf-8", "surrogateescape").strip("\n") for p in raw if p.strip(b"\n")})
    matched = [p for p in paths if any(fnmatch.fnmatchcase(p, q) for q in PATTERNS)]
    out = {"revs": len(revs), "paths": len(matched), "unmatched_patterns": [],
           "files": {}, "totals": {"blobs": 0, "blocks": 0, "lines_inside": 0, "heading_inside": 0,
                                   "section_diffs": 0, "cr_bytes": 0, "with_fences": 0}}
    for q in PATTERNS:
        if not any(fnmatch.fnmatchcase(p, q) for p in matched):
            out["unmatched_patterns"].append(q)
    for f in matched:
        spec = "".join(f"{c}:{f}\n" for c in revs)
        raw = git("cat-file", "--batch-check=%(objectname) %(objecttype)", inp=spec.encode()).decode()
        blobs = {}
        for c, line in zip(revs, raw.split("\n")):
            p = line.split()
            if len(p) == 2 and p[1] == "blob":
                blobs[p[0]] = blobs.get(p[0], 0) + 1
        agg = {"distinct_blobs": len(blobs), "with_fences": 0, "blocks": 0, "lines_inside": 0,
               "heading_inside": 0, "section_diffs": 0, "with_cr": 0, "worst": None}
        for b in blobs:
            data = git("cat-file", "blob", b)
            c = scan2.census(scan2.split_lines(data))
            cr = data.count(b"\r")
            agg["with_fences"] += 1 if c["blocks"] else 0
            agg["blocks"] += c["blocks"]
            agg["lines_inside"] += c["lines_inside"]
            agg["heading_inside"] += c["heading_inside"]
            agg["section_diffs"] += c["section_diffs_v4_v5"]
            agg["with_cr"] += 1 if cr else 0
            if c["heading_inside"]:
                agg["worst"] = {"blob": b, **c, "cr": cr}
            out["totals"]["blobs"] += 1
            out["totals"]["with_fences"] += 1 if c["blocks"] else 0
            out["totals"]["blocks"] += c["blocks"]
            out["totals"]["lines_inside"] += c["lines_inside"]
            out["totals"]["heading_inside"] += c["heading_inside"]
            out["totals"]["section_diffs"] += c["section_diffs_v4_v5"]
            out["totals"]["cr_bytes"] += cr
        if (agg["heading_inside"] or agg["section_diffs"] or agg["with_cr"] or agg["blocks"]):
            out["files"][f] = agg
    print(json.dumps(out, indent=1))


main()
