#!/usr/bin/env python3
"""Recheck19: independent derivation of the C1 landing-audit facts (read-only).

Re-implements the audit from its docstring, without importing its logic, and
compares against (a) the fresh tool JSON for rounds 10-20 and (b) the committed
official raw output. Also derives an author-time vs committer-time variant and
checks batch-check lookups against a per-token oracle. Git is invoked only as
log, cat-file, rev-parse and hash-object (no -w); nothing is written outside OUT.

Usage: derive.py LANE_CLONE FLEET_REPO TOOL_PATH OUT_DIR TOOL_JSON_10_20 COMMITTED_RAW
"""
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
LANE, FLEET, TOOL, OUT, TOOL_JSON, COMMITTED = sys.argv[1:7]
SEP, END = "\x1f", "\x1e"
LANE_NAME = "kama-shokunin"
RANGE = list(range(10, 21))
FULL_LO = re.compile(r"(?<![0-9A-Za-z])[0-9a-f]{40}(?![0-9A-Za-z])")
ABB_LO = re.compile(r"(?<![0-9A-Za-z])[0-9a-f]{7,40}(?![0-9A-Za-z])")
FULL_ANY = re.compile(r"(?<![0-9A-Za-z])[0-9a-fA-F]{40}(?![0-9A-Za-z])")
ABB_ANY = re.compile(r"(?<![0-9A-Za-z])[0-9a-fA-F]{7,40}(?![0-9A-Za-z])")


def genv():
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
    return env


def run_git(repo, *args):
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True,
                       text=True, env=genv())
    return p.returncode, p.stdout, p.stderr


def git(repo, *args):
    rc, out, err = run_git(repo, *args)
    if rc:
        raise SystemExit(f"FATAL git {args} rc={rc}: {err.strip()}")
    return out


def checkable(tok):
    return len(tok) == 40 or bool(re.search(r"[0-9]", tok)
                                  and re.search(r"[a-f]", tok))


def landed(text):
    out, inside, seen = [], False, False
    for line in text.split("\n"):
        if line.startswith("## Landed changes"):
            if seen:
                break
            inside = seen = True
            continue
        if inside and line.startswith("## "):
            break
        if inside:
            out.append(line)
    return "\n".join(out) if seen else None


def lane_rows():
    rows = []
    out = git(LANE, "log", f"--format=%H{SEP}%an{SEP}%at{SEP}%ct{SEP}%s{END}",
              "master")
    for rec in out.split(END):
        rec = rec.strip("\n")
        if rec:
            sha, an, at, ct, subj = rec.split(SEP)
            rows.append({"sha": sha, "an": an, "at": int(at), "ct": int(ct),
                         "subj": subj})
    return rows


def round_rows(rows, rnd):
    pat = re.compile(rf"^(?:round-{rnd}:|checkpoint\(r{rnd}\))")
    return [r for r in rows if r["an"] == LANE_NAME and pat.match(r["subj"])]


def fleet_cut(rel):
    out = git(FLEET, "log", "--diff-filter=A",
              f"--format=%H{SEP}%at{SEP}%ct", "--", rel)
    lines = [ln for ln in out.split("\n") if ln.strip()]
    if not lines:
        return None
    sha, at, ct = lines[-1].split(SEP)  # oldest commit that added the file
    return {"sha": sha, "at": int(at), "ct": int(ct), "adds": len(lines)}


def object_table(repo):
    out = git(repo, "cat-file", "--batch-all-objects",
              "--batch-check=%(objectname) %(objecttype)")
    table = {}
    for ln in out.split("\n"):
        if ln:
            sha, typ = ln.split(" ")
            table[sha] = typ
    return table


LANE_OBJ = object_table(LANE)
FLEET_OBJ = object_table(FLEET)
ALL_OBJ = {**FLEET_OBJ, **LANE_OBJ}
COMMITS = {}  # 7-hex prefix -> distinct commit shas across lane and fleet
for _tbl in (LANE_OBJ, FLEET_OBJ):
    for _sha, _typ in _tbl.items():
        if _typ == "commit":
            COMMITS.setdefault(_sha[:7], set()).add(_sha)


def commit_hits(tok):
    return {s for s in COMMITS.get(tok[:7], ()) if s.startswith(tok)}


def per_token(tok, peel):
    for repo in (LANE, FLEET):
        if peel:
            rc, _, _ = run_git(repo, "rev-parse", "--verify", "-q",
                               tok + "^{commit}")
        else:
            rc, _, _ = run_git(repo, "cat-file", "-e", tok)
        if rc == 0:
            return "found"
    return "missing"


def oracle(tok, peel):
    if peel:
        n = len(commit_hits(tok.lower()))
        return "missing" if n == 0 else ("found" if n == 1 else "ambiguous")
    return "found" if tok.lower() in ALL_OBJ else "missing"


def derive(rnd, rows, mode, cut, text):
    rc = round_rows(rows, rnd)
    cutoff = cut[mode]
    req = [r for r in rc if r[mode] <= cutoff]
    post = [r for r in rc if r[mode] > cutoff]
    defects = []
    for tok in sorted(set(FULL_LO.findall(text))):
        if tok not in ALL_OBJ:
            defects.append(["unresolved-full-hash", tok])
    sec = landed(text)
    if sec is None:
        defects.append(["landed-section-missing", "-"])
        sec = ""
    cited = sorted(set(ABB_LO.findall(sec)))
    for tok in cited:
        if checkable(tok):
            n = len(commit_hits(tok))
            if n == 0:
                defects.append(["landed-unresolved", tok])
            elif n > 1:
                defects.append(["landed-ambiguous", tok])
    for r in req:
        if not any(r["sha"].startswith(t) for t in cited):
            defects.append(["landed-omitted", r["sha"]])
    return {"round": rnd, "mode": mode, "cutoff": cutoff,
            "round_commits": len(rc),
            "required": sorted(r["sha"] for r in req),
            "post": sorted(r["sha"] for r in post),
            "defects": sorted(defects)}


def load_tool(path):
    spec = importlib.util.spec_from_file_location("tool", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    tool = load_tool(TOOL)
    rows = lane_rows()
    lane_c = {s for s, t in LANE_OBJ.items() if t == "commit"}
    fleet_c = {s for s, t in FLEET_OBJ.items() if t == "commit"}
    head = {
        "lane_master": git(LANE, "rev-parse", "master").strip(),
        "lane_head": git(LANE, "rev-parse", "HEAD").strip(),
        "fleet_head": git(FLEET, "rev-parse", "HEAD").strip(),
        "lane_objects": len(LANE_OBJ), "fleet_objects": len(FLEET_OBJ),
        "lane_commits": len(lane_c), "fleet_commits": len(fleet_c),
        "commits_shared_lane_fleet": len(lane_c & fleet_c),
        "master_commit_count": len(rows),
    }
    committed = json.load(open(COMMITTED, encoding="utf-8"))
    tooldoc = json.load(open(TOOL_JSON, encoding="utf-8"))
    head["committed_raw_equals_fresh_tool_10_20"] = committed == tooldoc
    tool_by_round = {r["round"]: r for r in tooldoc["results"]}
    rounds, mismatches, straddles, uppers = {}, [], {}, {}
    for rnd in RANGE:
        rel = f".ufo/reports/round-{rnd}/kama.md"
        cut = fleet_cut(rel)
        path = Path(FLEET, rel)
        text = path.read_text(encoding="utf-8")
        rc_h, head_blob, _ = run_git(FLEET, "rev-parse", "--verify", "-q",
                                     f"HEAD:{rel}")
        _, work_blob, _ = run_git(FLEET, "hash-object", str(path))
        at_d = derive(rnd, rows, "at", cut, text)
        ct_d = derive(rnd, rows, "ct", cut, text)
        tr = tool_by_round[rnd]
        tool_defects = sorted([d["kind"], d["token"]] for d in tr["defects"])
        rounds[rnd] = {
            "cut_at": cut["at"], "cut_ct": cut["ct"], "fleet_adds": cut["adds"],
            "head_blob": head_blob.strip() if rc_h == 0 else None,
            "worktree_blob": work_blob.strip(),
            "worktree_equals_head": rc_h == 0 and head_blob.strip() == work_blob.strip(),
            "tool_round_commits": tr["round_commits"],
            "mine_round_commits": at_d["round_commits"],
            "tool_required": tr["required"], "mine_required_at": len(at_d["required"]),
            "tool_post_equal": sorted(tr["post_report"]) == at_d["post"],
            "tool_defects": tool_defects, "mine_defects_at": at_d["defects"],
            "defects_equal_at": tool_defects == at_d["defects"],
            "ct_required": len(ct_d["required"]), "ct_post": len(ct_d["post"]),
            "ct_defects": ct_d["defects"],
            "ct_vs_at_required_diff": sorted(set(at_d["required"]) ^ set(ct_d["required"])),
            "ct_vs_at_defects_equal": ct_d["defects"] == at_d["defects"],
        }
        if not rounds[rnd]["defects_equal_at"]:
            mismatches.append(["defects", rnd])
        sec = landed(text) or ""
        full = sorted(set(FULL_LO.findall(text)))
        abb = sorted({t for t in ABB_LO.findall(sec) if checkable(t)})
        lk = {"full": {}, "abbrev": {}}
        if full:
            st = tool.lookup([LANE, FLEET], full, "")
            for t in full:
                lk["full"][t] = {"tool": st[t], "oracle": oracle(t, ""),
                                 "per_token": per_token(t, "")}
        if abb:
            st = tool.lookup([LANE, FLEET], abb, "^{commit}")
            for t in abb:
                lk["abbrev"][t] = {"tool": st[t], "oracle": oracle(t, "^{commit}"),
                                   "per_token": per_token(t, "^{commit}")}
        rounds[rnd]["lookups"] = lk
        for kind in ("full", "abbrev"):
            for t, v in lk[kind].items():
                if len({v["tool"], v["oracle"], v["per_token"]}) != 1:
                    mismatches.append(["lookup", rnd, kind, t, v])
        upper_full = sorted(set(FULL_ANY.findall(text)) - set(FULL_LO.findall(text)))
        upper_abb = sorted({t for t in ABB_ANY.findall(sec) if t != t.lower()})
        uppers[rnd] = {
            "full_uppercase_tokens": {t: per_token(t, "") for t in upper_full},
            "landed_uppercase_tokens": {t: per_token(t, "^{commit}") for t in upper_abb},
            "landed_uppercase_prefix_matches": {
                t: sorted(s["sha"] for s in rows if s["sha"].startswith(t.lower()))
                for t in upper_abb},
        }
        straddles[rnd] = [
            {"sha": r["sha"][:12], "at": r["at"], "ct": r["ct"],
             "pre_at": r["at"] <= cut["at"], "pre_ct": r["ct"] <= cut["ct"]}
            for r in round_rows(rows, rnd)
            if (r["at"] <= cut["at"]) != (r["ct"] <= cut["ct"])]
    r19 = fleet_cut(".ufo/reports/round-19/kama.md")
    text19 = Path(FLEET, ".ufo/reports/round-19/kama.md").read_text(encoding="utf-8")
    sec19 = landed(text19) or ""
    cited19 = sorted(set(ABB_LO.findall(sec19)))
    table19 = [
        {"sha": r["sha"], "at": r["at"], "ct": r["ct"],
         "pre_at": r["at"] <= r19["at"], "pre_ct": r["ct"] <= r19["ct"],
         "cited_by_prefix_in_landed": any(r["sha"].startswith(t) for t in cited19),
         "subject": r["subj"]}
        for r in round_rows(rows, 19)]
    tips = {}
    for label, key in (("by_at", "at"), ("by_ct", "ct")):
        cands = [r for r in rows if r[key] <= r19[key]]
        tips[label] = max(cands, key=lambda r: r[key])["sha"]
    at_ne_ct = [{"sha": r["sha"][:12], "an": r["an"], "at": r["at"], "ct": r["ct"],
                 "subj": r["subj"][:50]} for r in rows
                if r["an"] == LANE_NAME and r["at"] != r["ct"]]
    summary = {
        "head": head, "mismatches": mismatches,
        "straddling_commits": {k: v for k, v in straddles.items() if v},
        "round19_table": table19, "round19_cited_tokens": cited19,
        "round19_tips_at_report_time": tips,
        "kama_commits_with_at_ne_ct": at_ne_ct,
        "rounds": rounds, "uppercase": uppers,
    }
    Path(OUT, "derive.json").write_text(
        json.dumps(summary, indent=1, sort_keys=True, default=str) + "\n",
        encoding="utf-8")
    print(json.dumps({"head": head, "mismatch_count": len(mismatches),
                      "mismatches": mismatches[:20],
                      "straddling_commits": summary["straddling_commits"]},
                     indent=1, sort_keys=True, default=str))
    for rnd in RANGE:
        r = rounds[rnd]
        print(f"round {rnd}: rc tool={r['tool_round_commits']} mine={r['mine_round_commits']} "
              f"req tool={r['tool_required']} mine_at={r['mine_required_at']} "
              f"post_eq={r['tool_post_equal']} defects_eq_at={r['defects_equal_at']} "
              f"ct_req={r['ct_required']} ct_post={r['ct_post']} "
              f"ct_defects_eq_at={r['ct_vs_at_defects_equal']} "
              f"wt_eq_head={r['worktree_equals_head']} tool_defects={r['tool_defects']}")
    print("round19 table:")
    for row in table19:
        print(f"  {row['sha'][:12]} at={row['at']} ct={row['ct']} pre_at={row['pre_at']} "
              f"pre_ct={row['pre_ct']} cited={row['cited_by_prefix_in_landed']} "
              f"{row['subject'][:60]}")
    print("round19 cited tokens:", cited19)
    print("round19 tips:", tips)
    print("round19 uppercase:", json.dumps(uppers[19], sort_keys=True))
    print("round19 lookups:", json.dumps(rounds[19]["lookups"], sort_keys=True))


if __name__ == "__main__":
    main()
