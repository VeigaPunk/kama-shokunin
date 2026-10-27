#!/usr/bin/env python3
"""X14FenceLane scan6: merge-parent facts, the swap experiment comparison, and the
detector teeth test (in-memory only; no repo is written)."""
import json, subprocess, sys
import scan2

REPO = sys.argv[1]
TIP = sys.argv[2]
S = "/fast/scratch/hyaku/kama-r50/X14FenceLane"
CONTRACT_PATTERNS = []


def git(*a, inp=None):
    return scan2.git(*a, inp=inp)


def contract_patterns(tip):
    text = git("show", f"{tip}:registry/append-only-contract.tsv").decode()
    rows = [ln for ln in text.split("\n")[1:] if ln.strip()]
    import fnmatch
    return [r.split("\t") for r in rows]


def main():
    import fnmatch
    out = {}
    rows = contract_patterns(TIP)
    pats = [r[0] for r in rows]
    out["contract_patterns"] = pats

    # ---- merge inventory
    merges = []
    for ln in git("rev-list", "--all", "--parents", TIP).decode().splitlines():
        p = ln.split()
        if len(p) > 2:
            merges.append(p)
    mrec = []
    for p in merges:
        c, ps = p[0], p[1:]
        rec = {"commit": c, "parents": ps, "files": {}}
        tree = git("rev-parse", f"{c}^{{tree}}").decode().strip()
        for par in ps:
            rec[f"tree_eq_{par[:8]}"] = git("rev-parse", f"{par}^{{tree}}").decode().strip() == tree
        # files whose path is under the contract at the merge
        tree_paths = [t.decode("utf-8", "surrogateescape")
                      for t in git("ls-tree", "-r", "-z", "--name-only", c).split(b"\0") if t]
        files = [f for f in tree_paths if any(fnmatch.fnmatchcase(f, q) for q in pats)]
        for par in ps:
            deltas = {}
            for f in files:
                ns = git("diff", "--numstat", "--no-renames", par, c, "--", f).decode().split()
                if ns:
                    dels = int(ns[1]) if ns[1].isdigit() else None
                    deltas[f] = dels
            rec[f"deletions_vs_{par[:8]}"] = {k: v for k, v in deltas.items() if v}
            rec[f"max_deletion_vs_{par[:8]}"] = max([v for v in deltas.values() if v] or [0])
            rec[f"would_event_threshold20_vs_{par[:8]}"] = any((v or 0) >= 20 for v in deltas.values())
        mrec.append(rec)
    out["merges"] = mrec

    # ---- swap experiment comparison
    b = json.load(open(f"{S}/tool-tip.json"))
    s = json.load(open(f"{S}/tool-tip-swapped.json"))
    keyf = lambda e: (e["commit"], e["file"], e["deleted"], e["graded"], e["ungraded"],
                      e["status"], e.get("restored_max"), e.get("restored_by"), e.get("held_at_to"))
    out["swap_experiment"] = {
        "baseline_summary": b["summary"], "swapped_summary": s["summary"],
        "events_identical": [keyf(e) for e in b["events"]] == [keyf(e) for e in s["events"]],
        "n_events": [len(b["events"]), len(s["events"])],
    }

    # ---- teeth test: plant a fenced `## Axes` in a tip SCORECARD blob, in memory only
    data = git("cat-file", "blob", f"{TIP}:SCORECARD.md")
    body = scan2.split_lines(data)
    idx = next(i for i, ln in enumerate(body) if ln.startswith(b"## Round 49"))
    planted = body[:idx + 1] + [b"```text", b"## Axes", b"```"] + body[idx + 1:]
    clean = scan2.census(body)
    tooth = scan2.census(planted)

    def sec5(lines):
        out, t, fence = [], None, None
        for ln in lines:
            b2 = ln.rstrip(b"\r")
            if fence is not None:
                if scan2.fence_close(b2, fence):
                    fence = None
            else:
                fo = scan2.fence_open(b2)
                if fo is not None:
                    fence = fo
                elif b2.startswith(b"## "):
                    t = b2.decode().rstrip()
            out.append(t)
        return out

    def sec4(lines):
        out, t = [], None
        for ln in lines:
            if ln.startswith(b"## "):
                t = ln.decode().rstrip()
            out.append(t)
        return out
    a5, a4 = sec5(planted), sec4(planted)
    out["teeth_test"] = {
        "inserted_after_line": idx + 1,
        "clean": clean, "planted": tooth,
        "v5_title_of_round49_line": a5[idx + 5],
        "v4_title_of_round49_line": a4[idx + 5],
        "v5_section_diffs": sum(1 for x, y in zip(a5, a4) if x != y),
        "real_heading_after_fence_v5": a5[idx + 6 + 200] if idx + 206 < len(a5) else None,
    }
    print(json.dumps(out, indent=1))


main()
