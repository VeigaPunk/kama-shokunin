#!/usr/bin/env python3
"""X14FenceLane scan2: per-blob fence census + v4-vs-v5 section divergence over every
blob of the seven audited files, over every commit reachable from all refs."""
import json, re, subprocess, sys

REPO, REV = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else "--all")
FILES = ["SCORECARD.md", "LOG.md", "corpus/QUALITY.md", "corpus/README.md",
         "corpus/SOURCES.md", "AGENTS.md", "SKILL.md"]
FENCE_OPEN = re.compile(rb"^ {0,3}(`{3,}|~{3,})(.*)$")


def git(*a, inp=None):
    p = subprocess.run(["git", "-C", REPO, *a], input=inp, capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(p.stderr.decode()[:300])
    return p.stdout


def split_lines(d):
    s = d.split(b"\n")
    if s and s[-1] == b"":
        s.pop()
    return s


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


def census(body):
    """Fenced-block census plus the v4-vs-v5 section vector of one blob."""
    blocks = inside = hdr_inside = 0
    sec5, sec4 = [], []
    t5 = t4 = None
    fence = None
    for line in body:
        b = line.rstrip(b"\r")
        # v4 (fence-blind, raw line): any `## ` line retitles, inside a fence or not
        if line.startswith(b"## "):
            t4 = line.decode("utf-8", "replace").rstrip()
        if fence is not None:
            inside += 1
            if fence_close(b, fence):
                fence = None
            elif b.startswith(b"## "):
                hdr_inside += 1
        else:
            fo = fence_open(b)
            if fo is not None:
                blocks += 1
                fence = fo
            elif b.startswith(b"## "):
                t5 = b.decode("utf-8", "replace").rstrip()
        sec5.append(t5)
        sec4.append(t4)
    return {"blocks": blocks, "lines_inside": inside, "heading_inside": hdr_inside,
            "section_diffs_v4_v5": sum(1 for a, b2 in zip(sec5, sec4) if a != b2),
            "lines": len(body)}


def main():
    revs = git("rev-list", "--all").decode().split() if REV == "--all" else git("rev-list", REV).decode().split()
    out = {"revs": len(revs), "files": {}, "totals": {"blobs": 0, "blocks": 0, "lines_inside": 0,
                                                     "heading_inside": 0, "section_diffs": 0, "cr_bytes": 0}}
    for f in FILES:
        spec = "".join(f"{c}:{f}\n" for c in revs)
        raw = git("cat-file", "--batch-check=%(objectname) %(objecttype)", inp=spec.encode()).decode()
        blobs = {}
        for c, line in zip(revs, raw.split("\n")):
            p = line.split()
            if len(p) == 2 and p[1] == "blob":
                blobs[p[0]] = blobs.get(p[0], 0) + 1
        agg = {"distinct_blobs": len(blobs), "with_fences": 0, "blocks": 0, "lines_inside": 0,
               "heading_inside": 0, "section_diffs": 0, "with_cr": 0,
               "worst": None}
        for b in blobs:
            data = git("cat-file", "blob", b)
            c = census(split_lines(data))
            cr = data.count(b"\r")
            if c["blocks"]:
                agg["with_fences"] += 1
            agg["blocks"] += c["blocks"]
            agg["lines_inside"] += c["lines_inside"]
            agg["heading_inside"] += c["heading_inside"]
            agg["section_diffs"] += c["section_diffs_v4_v5"]
            if cr:
                agg["with_cr"] += 1
            if c["heading_inside"]:
                agg["worst"] = {"blob": b, **c, "cr": cr}
            out["totals"]["blobs"] += 1
            out["totals"]["blocks"] += c["blocks"]
            out["totals"]["lines_inside"] += c["lines_inside"]
            out["totals"]["heading_inside"] += c["heading_inside"]
            out["totals"]["section_diffs"] += c["section_diffs_v4_v5"]
            out["totals"]["cr_bytes"] += cr
        out["files"][f] = agg
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
