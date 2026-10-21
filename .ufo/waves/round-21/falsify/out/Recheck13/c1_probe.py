#!/usr/bin/env python3
"""Recheck13 probe: C1 report-landing-audit at a6617149, round-13 focus.

Reproduces every number cited in advice/Recheck13.md. Reads the scratch lane clone
(/tmp/kama-r21-Recheck13/lane at a6617149) and the fleet repo; never writes to them.
Writes only under OUT (outputs, drafts) and WORK (/tmp scratch synthetic repos).
Exit 0 iff: CLI matches the committed raw output (rounds 10-20 and 13); selftest exits 0
with 32 cases; the independent derivation equals the tool for rounds 10-20 (author time);
the committer-time and per-token-lookup variants change no classification for rounds 10-20.
"""
import collections
import contextlib
import importlib.util
import io
import json
import os
import random
import re
import shutil
import subprocess
import sys
from pathlib import Path

CLONE = Path("/tmp/kama-r21-Recheck13/lane")
FLEET = Path("/home/vgpnk/Projects/shokunin")
RAW = FLEET / "kama-shokunin/.ufo/waves/round-21/runs/b76727f3/c1-audit-raw.stdout"
OUT = FLEET / "kama-shokunin/.ufo/waves/round-21/falsify/out/Recheck13"
WORK = Path("/tmp/kama-r21-Recheck13/work")
TOOL = CLONE / "tools/report-landing-audit.py"
PIN = "a6617149722c73d90e142fbdc8154d6967055f7e"
US = "\x1f"
TOK = re.compile(r"[0-9A-Za-z]+")
A641 = "641e1b6f1bef0e12d14c2e23388d7592ff0cb594"
A370 = "370c066f093bd286bb0a98963f255590e3a7016d"
PROTO = "e1b3d746dbfd2100b61c67b6389217252592460f"
START = "941bb32c3f591bc63cbf7579b2b6c552228307cd"
ANCHOR = "**Pushed lane HEAD:**"


def genv():
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
    return env


def g(repo, *args, inp=None, env=None):
    return subprocess.run(["git", "-C", str(repo), *args], input=inp, capture_output=True, env=env or genv())


def gtxt(repo, *args):
    p = g(repo, *args)
    if p.returncode:
        raise SystemExit(f"git {' '.join(args)} in {repo}: rc={p.returncode}: {p.stderr.decode().strip()}")
    return p.stdout.decode("utf-8")


def load_tool(name):
    spec = importlib.util.spec_from_file_location(name, TOOL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def cli(*args):
    p = subprocess.run([sys.executable, str(TOOL), *args], cwd=str(CLONE), capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def norm(results):
    return [dict(round=r["round"], report=r["report"], report_committed=r["report_committed"],
                 cutoff=r["cutoff"], round_commits=r["round_commits"], required=r["required"],
                 post_report=sorted(r["post_report"]),
                 defects=sorted((d["kind"], d["token"], d.get("cited_elsewhere")) for d in r["defects"]))
            for r in results]


def typed_count(repos, tok):
    """Number of distinct commit objects that a short name could denote across repos."""
    oids = set()
    for r in repos:
        p = g(r, "rev-parse", "--disambiguate=" + tok)
        if p.returncode == 0:
            oids.update(p.stdout.decode().split())
    return sum(1 for o in oids if any(g(r, "cat-file", "-t", o).stdout.decode().strip() == "commit" for r in repos))


def make_variants(rla):
    def round_commits_ct(lane_repo, branch, lane, rnd):
        out = rla.git(lane_repo, "log", f"--format=%H{rla.SEP}%an{rla.SEP}%ct{rla.SEP}%s{rla.END}", branch)
        pat = re.compile(rf"^(?:round-{rnd}:|checkpoint\(r{rnd}\))")
        rows = []
        for record in out.split(rla.END):
            record = record.lstrip("\n")
            if not record:
                continue
            sha, author, t, subject = record.split(rla.SEP, 3)
            if author == f"{lane}-shokunin" and pat.match(subject):
                rows.append({"sha": sha, "atime": int(t), "subject": subject})
        return rows

    def report_cutoff_ct(fleet_repo, rel):
        out = rla.git(fleet_repo, "log", "--diff-filter=A", "--format=%ct", "--", rel).split()
        return int(out[-1]) if out else None

    def lookup_pertoken(repos, tokens, peel=""):
        status = {}
        for t in sorted(set(tokens)):
            st = "missing"
            for repo in repos:
                p = subprocess.run(["git", "-C", str(repo), "cat-file", "-t", f"{t}{peel}"],
                                   capture_output=True, text=True, env=rla.git_env())
                if p.returncode == 0:
                    st = "found"
                elif "ambiguous" in p.stderr and st != "found":
                    st = "ambiguous"
            status[t] = st
        return status

    return round_commits_ct, report_cutoff_ct, lookup_pertoken


def part_a():
    common = ["--lane-repo", str(CLONE), "--fleet-repo", str(FLEET), "--no-errata", "--json"]
    rc13, o13, _ = cli("--rounds", "13", *common)
    rc10, o10, _ = cli("--rounds", "10-20", *common)
    rcs, osout, _ = cli("--selftest")
    (OUT / "probe-cli-r13.json").write_text(o13, encoding="utf-8")
    (OUT / "probe-cli-r10-20.json").write_text(o10, encoding="utf-8")
    raw = json.loads(RAW.read_text(encoding="utf-8"))
    j13, j10 = json.loads(o13), json.loads(o10)
    a = dict(exit_r13=rc13, exit_r10_20=rc10, exit_selftest=rcs, selftest_last=osout.strip().splitlines()[-1],
             r13_matches_committed=norm([r for r in raw["results"] if r["round"] == 13]) == norm(j13["results"]),
             r10_20_matches_committed=norm(raw["results"]) == norm(j10["results"]),
             summary_matches_committed=raw["summary"] == j10["summary"])
    return a, j10


def part_b(tool_norm):
    commits = []
    for line in gtxt(CLONE, "log", f"--format=%H{US}%an{US}%at{US}%ct{US}%s", "master").splitlines():
        sha, an, at, ct, subj = line.split(US, 4)
        commits.append(dict(sha=sha, an=an, at=int(at), ct=int(ct), subj=subj))

    def any_object(tok):
        return any(g(r, "cat-file", "-e", tok).returncode == 0 for r in (CLONE, FLEET))

    def landed(text):
        lines = text.split("\n")
        idx = [i for i, line in enumerate(lines) if line.startswith("## Landed changes")]
        if not idx:
            return None
        body = []
        for line in lines[idx[0] + 1:]:
            if line.startswith("## "):
                break
            body.append(line)
        return "\n".join(body)

    def derive(text, rc, key, cut):
        defects = []
        for t in sorted({x for x in TOK.findall(text) if re.fullmatch(r"[0-9a-f]{40}", x)}):
            if not any_object(t):
                defects.append(["unresolved-full-hash", t])
        body = landed(text)
        if body is None:
            defects.append(["landed-section-missing", "-"])
            body = ""
        toks = sorted({x for x in TOK.findall(body) if re.fullmatch(r"[0-9a-f]{7,40}", x)})
        for t in toks:
            if len(t) != 40 and not (re.search(r"[0-9]", t) and re.search(r"[a-f]", t)):
                continue
            n = typed_count((CLONE, FLEET), t)
            if n == 0:
                defects.append(["landed-unresolved", t])
            elif n > 1:
                defects.append(["landed-ambiguous", t])
        pre = [c for c in rc if c[key] <= cut]
        post = [c for c in rc if c[key] > cut]
        for c in pre:
            if not any(c["sha"].startswith(t) for t in toks):
                defects.append(["landed-omitted", c["sha"]])
        return dict(required=len(pre), post=sorted(c["sha"] for c in post), defects=sorted(defects))

    rows, ok = [], True
    for rnd in range(10, 21):
        rel = f".ufo/reports/round-{rnd}/kama.md"
        adds = [line.split(US) for line in
                gtxt(FLEET, "log", "--diff-filter=A", f"--format=%H{US}%an{US}%at{US}%ct", "--", rel).splitlines()
                if line.strip()]
        cut_at = min(int(x[2]) for x in adds)
        cut_ct = min(int(x[3]) for x in adds)
        text = (FLEET / rel).read_text(encoding="utf-8")
        pats = (f"round-{rnd}:", f"checkpoint(r{rnd})")
        rc = [c for c in commits if c["an"] == "kama-shokunin" and c["subj"].startswith(pats)]
        da = derive(text, rc, "at", cut_at)
        dc = derive(text, rc, "ct", cut_ct)
        tool = next(r for r in tool_norm if r["round"] == rnd)
        tool_defects = sorted([k, t] for k, t, _ in tool["defects"])
        eq = da["defects"] == tool_defects and da["required"] == tool["required"] and da["post"] == tool["post_report"]
        ct_same = (dc["required"], dc["post"], dc["defects"]) == (da["required"], da["post"], da["defects"])
        ok = ok and eq
        rows.append(dict(round=rnd, fleet_adds=len(adds), cut_at=cut_at, cut_ct=cut_ct, round_commits=len(rc),
                         required=da["required"], derive_equals_tool=eq, committer_time_same=ct_same,
                         defects=da["defects"]))
    return rows, ok


def part_c(rla, tool_norm):
    round_commits_ct, report_cutoff_ct, lookup_pertoken = make_variants(rla)

    def run_rounds():
        return norm([rla.audit_round(CLONE, FLEET, "master", "kama", r, None) for r in range(10, 21)])

    def run_selftest():
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = rla.selftest()
        lines = buf.getvalue().splitlines()
        return rc, [x for x in lines if x.startswith("FAIL")], [x for x in lines if x.startswith("selftest cases")]

    orig_rc, orig_cut, orig_lookup = rla.round_commits, rla.report_cutoff, rla.lookup
    out = dict(baseline_run_equals_tool=run_rounds() == tool_norm, selftest_baseline=run_selftest())
    rla.round_commits, rla.report_cutoff = round_commits_ct, report_cutoff_ct
    try:
        ct_run = run_rounds()
        out["committer_time_differing_rounds"] = [a["round"] for a, b in zip(tool_norm, ct_run) if a != b]
        out["selftest_committer_time"] = run_selftest()
    finally:
        rla.round_commits, rla.report_cutoff = orig_rc, orig_cut
    rla.lookup = lookup_pertoken
    try:
        pt_run = run_rounds()
        out["per_token_lookup_differing_rounds"] = [a["round"] for a, b in zip(tool_norm, pt_run) if a != b]
        out["selftest_per_token"] = run_selftest()
    finally:
        rla.lookup = orig_lookup
    out["baseline_restored"] = run_rounds() == tool_norm
    return out


def part_d():
    base = (FLEET / ".ufo/reports/round-13/kama.md").read_text(encoding="utf-8")

    def sub(old, new):
        n = base.count(old)
        assert n == 1, (old, n)
        return base.replace(old, new, 1)

    def probe(tok):
        assert base.count(ANCHOR) == 1
        return base.replace(ANCHOR, f"Probe: `{tok}`.\n\n{ANCHOR}", 1)

    drafts = {
        "D0-identical": base,
        "D1-drop-641e-row": sub(f"| `{A641}` |", "| `none` |"),
        "D2-641e-7hex-in-row": sub(f"| `{A641}` |", "| `641e1b6` |"),
        "D3-deadbee-no-digit": probe("deadbee"),
        "D4-deadbe1-digit-letter": probe("deadbe1"),
        "D5-fake-40hex": probe("1" * 40),
        "D6-digits-1234567": probe("1234567"),
        "D7-heading-renamed": sub("## Landed changes", "## Landed commits"),
        "D8-table-370c-to-protocol": sub(f"| `{A370}` |", f"| `{PROTO}` |"),
        "D9-probe-start-tree": probe(START),
        "D10-uppercase-641e-row": sub(f"| `{A641}` |", f"| `{A641.upper()}` |"),
    }
    res = {}
    for name, text in drafts.items():
        path = OUT / "drafts" / f"{name}.md"
        path.write_text(text, encoding="utf-8")
        rc, out, err = cli("--lane-repo", str(CLONE), "--fleet-repo", str(FLEET), "--rounds", "13",
                           "--no-errata", "--report", f"13={path}", "--json")
        entry = {"exit": rc}
        if rc in (0, 1):
            r = json.loads(out)["results"][0]
            entry.update(required=r["required"],
                         defects=[[d["kind"], d["token"], d.get("cited_elsewhere")] for d in r["defects"]])
        else:
            entry["stderr"] = err.strip()[:200]
        res[name] = entry
    return res


def part_e(rla):
    amb = WORK / "amb"
    amb.mkdir(parents=True)
    gtxt(amb, "init", "-q")
    rng = random.Random(1313)
    n = 40000
    parts = []
    for i in range(n):
        content = f"blob {i} {rng.random()}\n".encode()
        parts.append(b"blob\ndata %d\n" % len(content) + content + b"\n")
    for i in range(n):
        msg = f"commit {i} {rng.random()}\n".encode()
        ts = 1700000000 + i
        parts.append(b"commit refs/heads/main\nauthor x <x@x> %d +0000\ncommitter x <x@x> %d +0000\ndata %d\n"
                     % (ts, ts, len(msg)) + msg + b"deleteall\n")
    fi = g(amb, "fast-import", "--quiet", inp=b"".join(parts))
    assert fi.returncode == 0, fi.stderr
    listing = gtxt(amb, "cat-file", "--batch-all-objects", "--batch-check=%(objectname) %(objecttype)").splitlines()
    groups = collections.defaultdict(list)
    for line in listing:
        oid, typ = line.split(" ")
        groups[oid[:7]].append((oid, typ))
    rows = []
    for pfx, members in sorted((k, v) for k, v in groups.items() if len(v) > 1):
        rows.append(dict(
            prefix=pfx, types=sorted(t for _, t in members),
            digit_and_letter=bool(re.search(r"[0-9]", pfx) and re.search(r"[a-f]", pfx)),
            members=[o for o, _ in members],
            peel_batch=g(amb, "cat-file", "--batch-check", inp=f"{pfx}^{{commit}}\n".encode()).stdout.decode().strip(),
            tool_lookup_peel=rla.lookup([amb], [pfx], "^{commit}")[pfx],
            typed_commit_count=typed_count([amb], pfx)))

    def first(types):
        return next((r for r in rows if r["types"] == types and r["digit_and_letter"]), None)

    cases = {
        "commit-commit": first(["commit", "commit"]),
        "blob-blob": first(["blob", "blob"]),
        "blob-commit": first(["blob", "commit"]),
        "commit-commit-digit-only": next((r for r in rows if r["types"] == ["commit", "commit"]
                                          and not re.search(r"[a-f]", r["prefix"])), None),
    }
    e2e = {}
    for label, row in cases.items():
        if row is None:
            e2e[label] = None
            continue
        d = OUT / "drafts" / f"E-{label}.md"
        d.write_text(f"# r13\n## Landed changes\n| `{row['prefix']}` | probe |\n## End\n", encoding="utf-8")
        res = rla.audit_round(amb, FLEET, "main", "kama", 13, str(d))
        e2e[label] = dict(prefix=row["prefix"], types=row["types"], defects=[[x["kind"], x["token"]] for x in res["defects"]])

    cross = None
    cc = cases["commit-commit"]
    if cc is not None:
        xp, xq = WORK / "xp", WORK / "xq"
        for R in (xp, xq):
            R.mkdir(parents=True)
            gtxt(R, "init", "-q")
        same = True
        for R, oid in zip((xp, xq), cc["members"]):
            raw = g(amb, "cat-file", "commit", oid).stdout
            made = g(R, "hash-object", "-t", "commit", "-w", "--stdin", inp=raw).stdout.decode().strip()
            same = same and made == oid
        cross = dict(objects_same_sha=same,
                     tool_union=rla.lookup([xp, xq], [cc["prefix"]], "^{commit}")[cc["prefix"]],
                     tool_xp_only=rla.lookup([xp], [cc["prefix"]], "^{commit}")[cc["prefix"]],
                     tool_xq_only=rla.lookup([xq], [cc["prefix"]], "^{commit}")[cc["prefix"]],
                     typed_count_union=typed_count([xp, xq], cc["prefix"]))
    return dict(groups=rows, e2e=e2e, cross_repo=cross)


def part_f(rla, variants):
    round_commits_ct, report_cutoff_ct, _ = variants
    L, F = WORK / "rebase-lane", WORK / "rebase-fleet"
    for R in (L, F):
        R.mkdir(parents=True)
        subprocess.run(["git", "-C", str(R), "init", "-q", "-b", "master"], env=genv(), check=True, capture_output=True)

    def cenv(at, ct):
        e = genv()
        e.update(GIT_AUTHOR_NAME="kama-shokunin", GIT_COMMITTER_NAME="kama-shokunin",
                 GIT_AUTHOR_EMAIL="kama@shokunin.local", GIT_COMMITTER_EMAIL="kama@shokunin.local",
                 GIT_AUTHOR_DATE=f"@{at} +0000", GIT_COMMITTER_DATE=f"@{ct} +0000")
        return e

    tree = g(L, "mktree", inp=b"").stdout.decode().strip()

    def ctree(at, ct):
        p = subprocess.run(["git", "-C", str(L), "commit-tree", tree, "-m", "round-13: work"],
                           capture_output=True, env=cenv(at, ct))
        assert p.returncode == 0, p.stderr
        return p.stdout.decode().strip()

    a_sha = ctree(1000, 1000)
    gtxt(L, "update-ref", "refs/heads/master", a_sha)
    rep = F / ".ufo/reports/round-13/kama.md"
    rep.parent.mkdir(parents=True)
    rep.write_text(f"# kama - round 13\n## Landed changes\n\n| `{a_sha}` | work |\n", encoding="utf-8")
    gtxt(F, "add", "--", ".ufo/reports/round-13/kama.md")
    p = subprocess.run(["git", "-C", str(F), "-c", "commit.gpgsign=false", "commit", "-q", "-m", "round-13: kama report"],
                       capture_output=True, env=cenv(1200, 1200))
    assert p.returncode == 0, p.stderr
    a2_sha = ctree(1000, 5000)  # rebase after the report: same author time, later committer time
    gtxt(L, "update-ref", "refs/heads/master", a2_sha)
    author_res = rla.audit_round(L, F, "master", "kama", 13, None)
    orig_rc, orig_cut = rla.round_commits, rla.report_cutoff
    rla.round_commits, rla.report_cutoff = round_commits_ct, report_cutoff_ct
    try:
        committer_res = rla.audit_round(L, F, "master", "kama", 13, None)
    finally:
        rla.round_commits, rla.report_cutoff = orig_rc, orig_cut
    return dict(a_sha=a_sha, a2_sha=a2_sha, distinct=a_sha != a2_sha,
                author_required=author_res["required"],
                author_defects=[[d["kind"], d["token"]] for d in author_res["defects"]],
                committer_required=committer_res["required"],
                committer_defects=[[d["kind"], d["token"]] for d in committer_res["defects"]])


def main():
    assert gtxt(CLONE, "rev-parse", "HEAD").strip() == PIN, "scratch clone is not at the pinned commit"
    shutil.rmtree(WORK, ignore_errors=True)
    WORK.mkdir(parents=True)
    (OUT / "drafts").mkdir(parents=True, exist_ok=True)
    rla = load_tool("rla_probe")
    a, tool_j10 = part_a()
    tool_norm = norm(tool_j10["results"])
    rows, b_ok = part_b(tool_norm)
    c = part_c(rla, tool_norm)
    f = part_f(rla, make_variants(rla))
    d = part_d()
    e = part_e(rla)
    summary = dict(A=a, B_derive_equals_tool=b_ok, B_rows=rows, C=c, D=d, E=e, F=f)
    (OUT / "probe-summary.json").write_text(json.dumps(summary, indent=1, sort_keys=True, default=str), encoding="utf-8")
    print(json.dumps(dict(A=a, B_derive_equals_tool=b_ok, C=c, F=f), indent=1, sort_keys=True, default=str))
    for name, entry in d.items():
        print("D", name, entry)
    print("E peel_batch_ever_ambiguous:", any("ambiguous" in r["peel_batch"] for r in e["groups"]),
          "groups:", len(e["groups"]))
    for label, entry in e["e2e"].items():
        print("E2E", label, entry)
    print("E cross_repo:", e["cross_repo"])
    ok = (a["exit_r13"] == 0 and a["exit_r10_20"] == 1 and a["exit_selftest"] == 0
          and a["r13_matches_committed"] and a["r10_20_matches_committed"] and a["summary_matches_committed"]
          and b_ok and c["baseline_run_equals_tool"] and c["selftest_baseline"][0] == 0
          and c["baseline_restored"]
          and c["committer_time_differing_rounds"] == [] and c["per_token_lookup_differing_rounds"] == [])
    print("PROBE OK" if ok else "PROBE CHECK FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
