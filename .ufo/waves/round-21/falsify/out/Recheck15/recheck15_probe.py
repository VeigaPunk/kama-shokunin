#!/usr/bin/env python3
"""Recheck15 (kama round 21 FALSIFY): probes for C1 round-15 classification.

derive    independent round-15 derivation from git, compared with the tool record
variants  committed tool vs --variant tools on rounds 10-20 and 15; committed raw bytes
ambiguity synthetic ambiguous prefix: cat-file --batch-check vs per-token lookup
wtprobe   fleet working-tree read: committed tool vs uncommitted WT snapshot (scratch clone)

Exit 0 = every expectation of the selected subcommands held; 1 = one did not; 2 = could not run.
Writes only under --scratch. The lane and fleet repositories are read-only here.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROUND = 15
REL = f".ufo/reports/round-{ROUND}/kama.md"
FULL = re.compile(r"(?<![0-9A-Za-z])[0-9a-f]{40}(?![0-9A-Za-z])")
ABBREV = re.compile(r"(?<![0-9A-Za-z])[0-9a-f]{7,40}(?![0-9A-Za-z])")
SECTION = re.compile(r"^## Landed changes[^\n]*\n(.*?)(?=^## |\Z)", re.S | re.M)


def git(repo, *args, stdin=None):
    proc = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                          text=True, input=stdin)
    return proc.returncode, proc.stdout, proc.stderr


def must(repo, *args):
    rc, out, err = git(repo, *args)
    if rc:
        raise SystemExit(f"git {' '.join(args)} in {repo}: rc={rc} {err.strip()}")
    return out


def checkable(token):
    return len(token) == 40 or (re.search(r"[0-9]", token) is not None
                                and re.search(r"[a-f]", token) is not None)


def run_tool(tool, lane, fleet, rounds):
    proc = subprocess.run([sys.executable, str(tool), "--lane-repo", str(lane),
                           "--fleet-repo", str(fleet), "--rounds", rounds,
                           "--no-errata", "--json"], capture_output=True, text=True)
    doc = json.loads(proc.stdout) if proc.stdout.strip() else None
    return proc.returncode, doc, proc.stdout, proc.stderr.strip()


def cmd_derive(a):
    if not a.tool_json:
        print("derive needs --tool-json")
        return 2
    rows = [line.split("\x1f") for line in must(
        a.lane, "log", "--format=%H%x1f%an%x1f%at%x1f%ct%x1f%s", "master").splitlines() if line]
    adds = [line.split("\x1f") for line in must(
        a.fleet, "log", "--diff-filter=A", "--format=%H%x1f%an%x1f%at%x1f%ct%x1f%s",
        "--", REL).splitlines() if line]
    if not adds:
        print("report never added in fleet")
        return 2
    add = adds[-1]
    cut_at, cut_ct = int(add[2]), int(add[3])
    print(f"master_commits={len(rows)} fleet_first_add={add[0]} "
          f"cutoff_author={cut_at} cutoff_committer={cut_ct}")
    pat = re.compile(rf"^(?:round-{ROUND}:|checkpoint\(r{ROUND}\))")
    mine = [r for r in rows if r[1] == "kama-shokunin" and pat.match(r[4])]
    for r in mine:
        print(f"kama {r[0]} at={r[2]} ct={r[3]} "
              f"author={'PRE' if int(r[2]) <= cut_at else 'POST'} "
              f"committer={'PRE' if int(r[3]) <= cut_ct else 'POST'} {r[4][:60]!r}")
    req_at = [r[0] for r in mine if int(r[2]) <= cut_at]
    req_ct = [r[0] for r in mine if int(r[3]) <= cut_ct]
    print(f"required author_time={len(req_at)} committer_time={len(req_ct)}")
    loose = re.compile(rf"round.?{ROUND}|checkpoint\(r{ROUND}\)", re.I)
    for r in rows:
        if loose.search(r[4]) and r not in mine:
            print(f"excluded {r[0]} author={r[1]} at={r[2]} {r[4][:70]!r}")
    wt = (Path(a.fleet) / REL).read_text(encoding="utf-8")
    head = must(a.fleet, "show", "HEAD:" + REL)
    print(f"fleet working-tree report == HEAD blob: {wt == head}")
    section = SECTION.search(wt).group(1)
    fulls = sorted(set(FULL.findall(wt)))

    def exists(token, peel=""):
        return any(git(repo, "cat-file", "-e", token + peel)[0] == 0
                   for repo in (a.lane, a.fleet))

    full_ok = {t: exists(t) for t in fulls}
    print(f"full_40hex={len(fulls)} all_exist={all(full_ok.values())}")
    abbr = sorted(set(ABBREV.findall(section)))
    print(f"landed_hex_tokens={abbr}")
    unresolved = [t for t in abbr if checkable(t) and not exists(t, "^{commit}")]
    omitted = [r for r in req_at if not any(r.startswith(t) for t in abbr)]
    print(f"landed_unresolved={unresolved} required_not_cited={omitted}")
    records = json.loads(Path(a.tool_json).read_text(encoding="utf-8"))["results"]
    rec = next(x for x in records if x["round"] == ROUND)
    print(f"tool_record cutoff={rec['cutoff']} round_commits={rec['round_commits']} "
          f"required={rec['required']} defects={rec['defects']}")
    ok = (rec["cutoff"] == cut_at and rec["round_commits"] == len(mine)
          and rec["required"] == len(req_at) == len(req_ct) and rec["defects"] == []
          and not unresolved and not omitted and all(full_ok.values()))
    print("derive: MATCHES TOOL" if ok else "derive: DIFFERS FROM TOOL")
    return 0 if ok else 1


def cmd_variants(a):
    tools = {"committed": Path(a.tool)}
    for item in a.variant:
        name, _, path = item.partition("=")
        if not name or not path:
            print(f"bad --variant {item!r}")
            return 2
        tools[name] = Path(path)
    got = {}
    for name, path in tools.items():
        for rounds in ("10-20", "15"):
            rc, doc, out, err = run_tool(path, a.lane, a.fleet, rounds)
            if doc is None:
                print(f"{name} rounds={rounds} produced no JSON rc={rc} stderr={err[:120]!r}")
                return 2
            got[(name, rounds)] = (rc, doc, out)
            print(f"{name} rounds={rounds} rc={rc} stderr={err[:100]!r}")
    status = 0
    if a.committed_raw:
        raw = Path(a.committed_raw).read_bytes()
        same = got[("committed", "10-20")][2].encode() == raw
        print(f"committed rounds=10-20 stdout byte-identical to committed raw: {same} "
              f"sha256={hashlib.sha256(raw).hexdigest()[:16]}")
        status |= 0 if same else 1

    def rows(doc):
        return {r["round"]: (r["cutoff"], r["round_commits"], r["required"],
                             tuple(sorted(r["post_report"])),
                             tuple(sorted((d["kind"], d["token"]) for d in r["defects"])))
                for r in doc["results"]}

    for name in tools:
        if name == "committed":
            continue
        for rounds in ("10-20", "15"):
            base = rows(got[("committed", rounds)][1])
            var = rows(got[(name, rounds)][1])
            diff = sorted(k for k in base if base[k] != var.get(k))
            print(f"{name} vs committed rounds={rounds}: differing_rounds={diff}")
            status |= 1 if diff else 0
    return status


def cmd_ambiguity(a):
    scratch = Path(a.scratch) / "ambig"
    shutil.rmtree(scratch, ignore_errors=True)
    scratch.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(scratch)], check=True)
    stream = []
    for i in range(40000):
        msg = f"c{i}\n"
        frm = f"from :{i}\n" if i else ""
        stream.append(f"commit refs/heads/master\nmark :{i + 1}\n"
                      f"committer T <t@x> {1700000000 + i} +0000\n"
                      f"data {len(msg)}\n{msg}{frm}\n")
    proc = subprocess.run(["git", "-C", str(scratch), "fast-import", "--quiet"],
                          input="".join(stream).encode(), capture_output=True)
    if proc.returncode:
        print(f"fast-import failed: {proc.stderr.decode()[:200]}")
        return 2
    shas = must(scratch, "rev-list", "--all").split()
    groups = {}
    for sha in shas:
        groups.setdefault(sha[:7], []).append(sha)
    shared = sorted(k for k, v in groups.items() if len(v) >= 2)
    if not shared:
        print("no shared 7-char prefix")
        return 2
    prefix = shared[0]
    print(f"commits={len(shas)} shared_7char_prefixes={len(shared)} probe={prefix} "
          f"candidates={groups[prefix]}")
    _, out, _ = git(scratch, "cat-file", "--batch-check",
                    stdin=f"{prefix}\n{prefix}^{{commit}}\n")
    print(f"batch-check stdout (plain, then ^{{commit}}) = {out!r}")
    spec = importlib.util.spec_from_file_location("tool_under_test", a.tool)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    peeled = mod.lookup((scratch,), [prefix], "^{commit}")[prefix]
    plain = mod.lookup((scratch,), [prefix], "")[prefix]
    per_token = ("found" if git(scratch, "cat-file", "-e", f"{prefix}^{{commit}}")[0] == 0
                 else "missing")
    print(f"tool lookup peel=^{{commit}} -> {peeled}; plain -> {plain}; "
          f"per-token cat-file -e ^{{commit}} -> {per_token}")
    expected = peeled == "missing" and plain == "ambiguous" and per_token == "missing"
    print("ambiguity: peeled lookups never report 'ambiguous'" if expected
          else "ambiguity: UNEXPECTED observation")
    return 0 if expected else 1


def cmd_wtprobe(a):
    scratch = Path(a.scratch)
    probe = scratch / "fleet-probe"
    shutil.rmtree(probe, ignore_errors=True)
    must(scratch, "clone", "-q", "--no-checkout", "--no-hardlinks", str(a.fleet), str(probe))
    must(probe, "checkout", "-q", "HEAD", "--", REL)
    rc0, doc0, _, _ = run_tool(a.tool, a.lane, probe, str(ROUND))
    print(f"committed tool, clean probe: rc={rc0} status={doc0['summary']['status']}")
    report = probe / REL
    report.write_text(report.read_text(encoding="utf-8")
                      + "\nUncommitted probe token 1234567890abcdef1234567890abcdef12345678.\n",
                      encoding="utf-8")
    rc1, doc1, _, _ = run_tool(a.tool, a.lane, probe, str(ROUND))
    defects1 = [(d["kind"], d["token"]) for d in doc1["results"][0]["defects"]]
    print(f"committed tool, uncommitted probe in working tree: rc={rc1} defects={defects1}")
    ok = rc0 == 0 and rc1 == 1
    if a.wt_tool:
        rc2, doc2, _, _ = run_tool(a.wt_tool, a.lane, probe, str(ROUND))
        defects2 = [(d["kind"], d["token"]) for d in doc2["results"][0]["defects"]]
        print(f"uncommitted WT snapshot, same probe: rc={rc2} defects={defects2}")
        ok = ok and rc2 == 0
    print("wtprobe: working-tree dependency reproduced" if ok
          else "wtprobe: NOT reproduced")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cmd", choices=["derive", "variants", "ambiguity", "wtprobe", "all"])
    ap.add_argument("--lane", required=True, help="scratch lane clone at the attacked commit")
    ap.add_argument("--fleet", required=True, help="fleet repository (read-only)")
    ap.add_argument("--tool", required=True, help="committed tool under test")
    ap.add_argument("--tool-json", help="tool JSON output for rounds 15 (derive)")
    ap.add_argument("--committed-raw", help="committed raw stdout for rounds 10-20 (variants)")
    ap.add_argument("--variant", action="append", default=[], metavar="NAME=PATH")
    ap.add_argument("--wt-tool", help="uncommitted working-tree snapshot of the tool (wtprobe)")
    ap.add_argument("--scratch", required=True)
    a = ap.parse_args()
    Path(a.scratch).mkdir(parents=True, exist_ok=True)
    steps = {"derive": cmd_derive, "variants": cmd_variants,
             "ambiguity": cmd_ambiguity, "wtprobe": cmd_wtprobe}
    names = list(steps) if a.cmd == "all" else [a.cmd]
    worst = 0
    for name in names:
        print(f"== {name}")
        rc = steps[name](a)
        print(f"== {name} exit={rc}")
        worst = max(worst, rc)
    return worst


if __name__ == "__main__":
    sys.exit(main())
