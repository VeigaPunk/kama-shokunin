#!/usr/bin/env python3
"""Recheck16: independent re-derivation of the report-landing-audit C1 rules.

Read-only: runs only `git log`, `git rev-parse --disambiguate`, `git cat-file`,
`git show`. Does not import or execute tools/report-landing-audit.py.

Usage: derive.py LANE_REPO FLEET_REPO ROUNDS [TOOL_JSON]
  ROUNDS     comma list, e.g. 16 or 10,11,...,20
  TOOL_JSON  optional `--json` output of the tool for the same rounds; each round is
             compared (defect kind+token multiset, required, round_commits, post_report).

Rules as stated in the tool docstring (re-implemented here, not copied):
  cutoff            fleet commit that first adds .ufo/reports/round-N/kama.md;
                    AUTHOR time (tool) and COMMITTER time (alternative) both recorded.
  round commits     lane master commits with author name kama-shokunin and subject
                    starting `round-N:` or `checkpoint(rN)`.
  landed-omitted    round commit with time <= cutoff not cited by a >=7-hex prefix
                    anywhere in the `## Landed changes` body.
  token status      per repo: `rev-parse --disambiguate=<tok>` restricted to commit
                    objects; unique in any repo -> found; >1 commit and none unique
                    -> ambiguous; none -> missing (per-token variant, not batch-check).
  unresolved-full   40-hex token (bounded) with `cat-file -e` false in both repos.
"""
import hashlib
import json
import os
import re
import subprocess
import sys

LANE, FLEET = sys.argv[1], sys.argv[2]
ROUNDS = [int(x) for x in sys.argv[3].split(",")]
TOOL = json.load(open(sys.argv[4], encoding="utf-8")) if len(sys.argv) > 4 else None
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
REPOS = (LANE, FLEET)
FULL = re.compile(r"(?<![0-9A-Za-z])[0-9a-f]{40}(?![0-9A-Za-z])")
ABBR = re.compile(r"(?<![0-9A-Za-z])[0-9a-f]{7,40}(?![0-9A-Za-z])")
MIXED = re.compile(r"(?<![0-9A-Za-z])[0-9A-Fa-f]{7,40}(?![0-9A-Za-z])")


def git(repo, *args, check=True):
    proc = subprocess.run(["git", "-C", repo, *args], capture_output=True,
                          text=True, env=ENV)
    if check and proc.returncode != 0:
        raise SystemExit(f"FATAL git {' '.join(args)} in {repo}: "
                         f"rc={proc.returncode} {proc.stderr.strip()}")
    return proc


def master_commits():
    out = git(LANE, "log", "--format=%H%x1f%an%x1f%at%x1f%ct%x1f%s%x1e", "master").stdout
    rows = []
    for rec in out.split("\x1e"):
        rec = rec.strip("\n")
        if rec:
            sha, an, at, ct, subj = rec.split("\x1f", 4)
            rows.append({"sha": sha, "author": an, "at": int(at), "ct": int(ct),
                         "subject": subj})
    return rows


def first_add(rel):
    out = git(FLEET, "log", "--diff-filter=A", "--format=%H%x1f%an%x1f%at%x1f%ct",
              "--", rel).stdout
    rows = [r.split("\x1f") for r in out.splitlines() if r]
    if not rows:
        return None
    sha, an, at, ct = min(rows, key=lambda r: int(r[2]))
    return {"sha": sha, "author": an, "at": int(at), "ct": int(ct), "adds": len(rows)}


def commit_candidates(repo, tok):
    proc = git(repo, "rev-parse", f"--disambiguate={tok}", check=False)
    if proc.returncode != 0:
        return None
    full = [c for c in proc.stdout.split() if re.fullmatch(r"[0-9a-f]{40}", c)]
    return [c for c in full if git(repo, "cat-file", "-t", c).stdout.strip() == "commit"]


def status(tok):
    result = "missing"
    for repo in REPOS:
        cands = commit_candidates(repo, tok)
        if not cands:
            continue
        if len(cands) == 1:
            return "found"
        result = "ambiguous"
    return result


def exists_any(tok):
    return any(git(r, "cat-file", "-e", tok, check=False).returncode == 0 for r in REPOS)


def checkable(tok):
    return len(tok) == 40 or (re.search(r"[0-9]", tok) is not None
                              and re.search(r"[a-f]", tok) is not None)


def landed_span(lines):
    for i, line in enumerate(lines):
        if line.startswith("## Landed changes"):
            end = next((j for j in range(i + 1, len(lines)) if lines[j].startswith("## ")),
                       len(lines))
            return i, end
    return None


def audit(n, commits):
    rel = f".ufo/reports/round-{n}/kama.md"
    path = os.path.join(FLEET, rel)
    raw = open(path, "rb").read()
    text = raw.decode("utf-8")
    lines = text.split("\n")
    fa = first_add(rel)
    head = git(FLEET, "show", f"HEAD:{rel}", check=False)
    head_sha = (hashlib.sha256(head.stdout.encode("utf-8")).hexdigest()
                if head.returncode == 0 else None)
    pat = re.compile(rf"^(?:round-{n}:|checkpoint\(r{n}\))")
    mine = [c for c in commits if c["author"] == "kama-shokunin" and pat.match(c["subject"])]
    span = landed_span(lines)
    body = None if span is None else "\n".join(lines[span[0] + 1:span[1]])
    rec = {"round": n, "report_path": path,
           "working_sha256": hashlib.sha256(raw).hexdigest(),
           "head_blob_sha256": head_sha,
           "fleet_add_commit": fa["sha"], "fleet_adds": fa["adds"],
           "cutoff_author": fa["at"], "cutoff_committer": fa["ct"],
           "round_commits": [dict(c) for c in mine]}
    pre_a = [c for c in mine if c["at"] <= fa["at"]]
    pre_c = [c for c in mine if c["ct"] <= fa["ct"]]
    rec["required_author"] = len(pre_a)
    rec["required_committer"] = len(pre_c)
    rec["post_author"] = sorted(c["sha"] for c in mine if c["at"] > fa["at"])
    rec["post_committer"] = sorted(c["sha"] for c in mine if c["ct"] > fa["ct"])
    rec["flipped_by_committer_switch"] = sorted(
        {c["sha"] for c in pre_a} ^ {c["sha"] for c in pre_c})
    cited = sorted(set(ABBR.findall(body or "")))
    defects = []
    if body is None:
        defects.append(["landed-section-missing", "-"])
    for t in sorted(set(FULL.findall(text))):
        if not exists_any(t):
            defects.append(["unresolved-full-hash", t])
    for t in cited:
        if not checkable(t):
            continue
        s = status(t)
        if s == "missing":
            defects.append(["landed-unresolved", t])
        elif s == "ambiguous":
            defects.append(["landed-ambiguous", t])

    def omitted(pre):
        return [c["sha"] for c in pre if not any(c["sha"].startswith(t) for t in cited)]

    rec["omitted_author"] = omitted(pre_a)
    rec["omitted_committer"] = omitted(pre_c)
    defects += [["landed-omitted", s] for s in rec["omitted_author"]]
    rec["defects_author_time"] = sorted(defects)
    # scope: every hex-like token in the report, with location and resolution
    scope = {}
    for ln, line in enumerate(lines, 1):
        for m in MIXED.finditer(line):
            t = m.group(0)
            if not (len(t) == 40 or (re.search(r"[0-9]", t) and re.search(r"[A-Fa-f]", t))):
                continue
            in_landed = span is not None and span[0] < ln - 1 < span[1]
            key = (t, in_landed)
            if key not in scope:
                low = t.lower()
                scope[key] = {"token": t, "in_landed": in_landed, "first_line": ln,
                              "tool_checks": (t == low and bool(ABBR.fullmatch(t))
                                              and in_landed),
                              "status_lowercase": status(low)}
    rec["scope"] = sorted(scope.values(), key=lambda d: (d["first_line"], d["token"]))
    if TOOL is not None:
        tool = next(r for r in TOOL["results"] if r["round"] == n)
        tool_defects = sorted([d["kind"], d["token"]] for d in tool["defects"])
        rec["tool"] = {"defects": tool_defects, "required": tool["required"],
                       "round_commits": tool["round_commits"],
                       "post_report": sorted(tool["post_report"]),
                       "cutoff": tool["cutoff"]}
        rec["agrees_with_tool"] = {
            "defects": tool_defects == rec["defects_author_time"],
            "required": tool["required"] == len(pre_a),
            "round_commits": tool["round_commits"] == len(mine),
            "post_report": sorted(tool["post_report"]) == rec["post_author"],
            "cutoff": tool["cutoff"] == fa["at"],
        }
    return rec


def main():
    commits = master_commits()
    doc = {"lane_master": git(LANE, "rev-parse", "master").stdout.strip(),
           "fleet_head": git(FLEET, "rev-parse", "HEAD").stdout.strip(),
           "rounds": [audit(n, commits) for n in ROUNDS]}
    json.dump(doc, sys.stdout, indent=1, sort_keys=True)
    print()


main()
