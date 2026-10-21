#!/usr/bin/env python3
"""Recheck19 harness: mutation and fixture attacks on the round-19 C1 landing audit.

Baseline = the unmodified tool, run through the CLI and in-process. Variants run the
same module code in-process with one change each:
  ct: committer time (the two `--format=...%at` git logs read `%ct` instead).
  pt: per-token lookup (`rev-parse --verify -q` / `cat-file -e` per token, no batch-check).
Only WORK (scratch) and OUT are written. The lane clone and fleet repo are read-only here.

Usage: harness.py LANE_CLONE FLEET_REPO TOOL_PATH OUT_DIR WORK_DIR
"""
import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
LANE, FLEET, TOOL, OUT, WORK = sys.argv[1:6]
EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
FULL24 = "24adc8ed372e85d4739ae290e5fde5a6a7ebc2e9"
REPORT = str(Path(FLEET, ".ufo/reports/round-19/kama.md"))
BASE_TEXT = Path(REPORT).read_text(encoding="utf-8")
PRE8 = ["7229fa95eb12", "5b108c1a7e94", "f1790e25b421", "84cf2f7646fc",
        "028235e6f28d", "05f0f6c7de01", "30ed37837782", "24adc8ed372e"]
RUNLOG = []


def genv(extra=None):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
    env.update(extra or {})
    return env


def sh(argv, env=None, stdin=None, ok=(0,)):
    p = subprocess.run(argv, input=stdin, capture_output=True, text=True,
                       env=env or genv())
    RUNLOG.append({"argv": argv, "rc": p.returncode})
    if p.returncode not in ok:
        raise SystemExit(f"FATAL rc={p.returncode} {argv[:5]}: {p.stderr.strip()}")
    return p


def G(repo, *a, env=None, stdin=None, ok=(0,)):
    return sh(["git", "-C", str(repo), *a], env=env, stdin=stdin, ok=ok)


# ----------------------------------------------------------------- fixtures
def fresh(name):
    d = Path(WORK, name)
    shutil.rmtree(d, ignore_errors=True)
    d.mkdir(parents=True)
    G(d, "init", "-q", "-b", "master")
    tree = G(d, "mktree", stdin="").stdout.strip()
    assert tree == EMPTY_TREE, tree
    return d


def ctree(repo, parent, msg, author, adate, cdate):
    env = genv({"GIT_AUTHOR_NAME": author, "GIT_AUTHOR_EMAIL": "fx@x",
                "GIT_AUTHOR_DATE": f"@{adate} +0000",
                "GIT_COMMITTER_NAME": author, "GIT_COMMITTER_EMAIL": "fx@x",
                "GIT_COMMITTER_DATE": f"@{cdate} +0000"})
    argv = ["commit-tree", EMPTY_TREE] + (["-p", parent] if parent else []) + ["-m", msg]
    return G(repo, *argv, env=env).stdout.strip()


def bench(repo, n):
    parts = []
    for i in range(1, n + 1):
        msg = f"bench {i}\n"
        parts.append(f"commit refs/heads/master\nmark :{i}\n"
                     "author bench <b@x> 1790000000 +0000\n"
                     "committer bench <b@x> 1790000000 +0000\n"
                     f"data {len(msg.encode())}\n{msg}")
        if i > 1:
            parts.append(f"from :{i - 1}\n")
        parts.append("\n")
    G(repo, "fast-import", "--quiet", stdin="".join(parts))


def collision(repo):
    shas = G(repo, "rev-list", "master").stdout.split()
    buckets = {}
    for s in shas:
        buckets.setdefault(s[:7], []).append(s)
    for prefix, members in buckets.items():
        if len(members) >= 2:
            return prefix, members[0], members[1], shas
    raise SystemExit("no 7-hex collision among fixture commits")


def build_amb():
    lane = fresh("amb-lane")
    bench(lane, 70000)
    P, A, B, shas = collision(lane)
    tip = G(lane, "rev-parse", "master").stdout.strip()
    K = ctree(lane, tip, "round-19: ambiguity probe", "kama-shokunin",
              1792560000, 1792560000)
    G(lane, "update-ref", "refs/heads/master", K)
    lane_hits = [s for s in shas if s.startswith(P)] + ([K] if K.startswith(P) else [])
    return dict(lane=lane, P=P, A=A, B=B, K=K, lane_hits=lane_hits)


def build_union(fa, draft):
    fleet = fresh("union-fleet")
    body = G(fa["lane"], "cat-file", "commit", fa["B"]).stdout
    got = G(fleet, "hash-object", "-t", "commit", "-w", "--literally", "--stdin",
            stdin=body).stdout.strip()
    assert got == fa["B"], (got, fa["B"])
    rel = ".ufo/reports/round-19/kama.md"
    Path(fleet, rel).parent.mkdir(parents=True)
    Path(fleet, rel).write_text(draft, encoding="utf-8")
    G(fleet, "add", rel)
    env = genv({"GIT_AUTHOR_NAME": "kama-shokunin", "GIT_AUTHOR_EMAIL": "fx@x",
                "GIT_AUTHOR_DATE": "@1792565257 +0000",
                "GIT_COMMITTER_NAME": "kama-shokunin", "GIT_COMMITTER_EMAIL": "fx@x",
                "GIT_COMMITTER_DATE": "@1792565257 +0000"})
    G(fleet, "commit", "-q", "-m", "round-19: kama report", env=env)
    return fleet


def build_orphan():
    lane = fresh("orph-lane")
    c1 = ctree(lane, None, "round-19: orphan test one", "kama-shokunin",
               1792560000, 1792560000)
    c2 = ctree(lane, c1, "round-19: orphan test two", "kama-shokunin",
               1792561000, 1792561000)
    # same author date and parent as c2; later committer date (a rewrite that
    # leaves c2 orphaned but still present in the object database)
    c2p = ctree(lane, c1, "round-19: orphan test two", "kama-shokunin",
                1792561000, 1792566000)
    G(lane, "update-ref", "refs/heads/master", c2p)
    return dict(lane=lane, c1=c1, c2=c2, c2p=c2p)


# ----------------------------------------------------------------- mutants
def rep(text, old, new, count=1):
    n = text.count(old)
    assert n == count, (old[:40], n, count)
    return text.replace(old, new)


def landed_add(text, bullet):
    anchor = "## Landed changes\n"
    assert text.count(anchor) == 1
    i = text.index(anchor) + len(anchor)
    return text[:i] + "\n" + bullet + "\n" + text[i:]


def work_add(text, line):
    anchor = "## Work performed\n"
    assert text.count(anchor) == 1
    i = text.index(anchor) + len(anchor)
    return text[:i] + "\n" + line + "\n" + text[i:]


def mutants(tree24):
    omit = lambda t: rep(rep(t, f"`{FULL24}`", "`final-wave-advice`"),
                         "`24adc8ed…`", "`final`")
    return [
        ("M00-identity", "committed report, unchanged", BASE_TEXT,
         {"base": []}),
        ("M01-omit-final-commit", "24adc8ed removed from Landed (both mentions)",
         omit(BASE_TEXT), {"base": [("landed-omitted", FULL24)]}),
        ("M02-typo-prefix", "028235e6 (both Landed mentions) -> 028235e7",
         rep(BASE_TEXT, "`028235e6…`", "`028235e7…`", 2),
         {"base": [("landed-omitted", "028235e6f28d"), ("landed-unresolved", "028235e7")]}),
        ("M03-uppercase-prefix", "84cf2f76 written as 84CF2F76",
         rep(BASE_TEXT, "`84cf2f76…`", "`84CF2F76…`"),
         {"base": [("landed-omitted", "84cf2f7646fc")]}),
        ("M04-uppercase-fake-full", "fabricated 40-hex, uppercase, added to Landed",
         landed_add(BASE_TEXT, "- `0957CE619789D13D894EF21BC863486BCB35B56C` — fabricated."),
         {"base": []}),
        ("M05-lower-fake-full", "fabricated 40-hex, lowercase, added to Landed",
         landed_add(BASE_TEXT, "- `0957ce619789d13d894ef21bc863486bcb35b56c` — fabricated."),
         {"base": [("unresolved-full-hash", "0957ce619789d13d894ef21bc863486bcb35b56c"),
                   ("landed-unresolved", "0957ce619789d13d894ef21bc863486bcb35b56c")]}),
        ("M06-six-char-prefix", "f1790e25 shortened to f1790e (6 chars)",
         rep(BASE_TEXT, "`f1790e25…`", "`f1790e…`"),
         {"base": [("landed-omitted", "f1790e25b421")]}),
        ("M07-letters-only-token", "deadbeef added to Landed",
         landed_add(BASE_TEXT, "- `deadbeef` — fabricated."), {"base": []}),
        ("M08-tree-as-landed", "tree of 24adc8ed added to Landed (lane-tip cite kept)",
         landed_add(BASE_TEXT, f"- `{tree24}` — tree object."),
         {"base": [("landed-unresolved", tree24)]}),
        ("M09-foreign-round18-extra", "1b85a24e (round 18) added to Landed",
         landed_add(BASE_TEXT, "- `1b85a24e` — extra."), {"base": []}),
        ("M10-cited-only-outside-landed", "24adc8ed removed from Landed, cited in Work performed",
         work_add(omit(BASE_TEXT), f"Final commit reference: {FULL24}."),
         {"base": [("landed-omitted", FULL24)]}),
        ("M11-heading-variant", "'## Landed changes' -> '## Landed Changes'",
         rep(BASE_TEXT, "## Landed changes\n", "## Landed Changes\n"),
         {"base": [("landed-section-missing", "-")] + [("landed-omitted", p) for p in PRE8]}),
        ("M12-post-report-extra", "8d9191f5 (post-report) added to Landed",
         landed_add(BASE_TEXT, "- `8d9191f5` — post."), {"base": []}),
        ("M13-mistyped-7char", "abcdef1 (digit+letter, nonexistent) added to Landed",
         landed_add(BASE_TEXT, "- `abcdef1` — typo."),
         {"base": [("landed-unresolved", "abcdef1")]}),
        ("M14-unresolved-outside-landed", "fabricated lowercase 40-hex in Work performed",
         work_add(BASE_TEXT, "Unresolved citation: 0957ce619789d13d894ef21bc863486bcb35b56c."),
         {"base": [("unresolved-full-hash", "0957ce619789d13d894ef21bc863486bcb35b56c")]}),
    ]


# ----------------------------------------------------------------- runners
def load(tag):
    spec = importlib.util.spec_from_file_location(f"tool_{tag}", TOOL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def patch_ct(mod):
    orig = mod.git

    def git_ct(repo, *a, stdin=None, env=None):
        a = tuple(x.replace("%at", "%ct") if x.startswith("--format=") else x for x in a)
        return orig(repo, *a, stdin=stdin, env=env)
    mod.git = git_ct


def patch_pt(mod):
    def lookup_pt(repos, tokens, peel=""):
        out = {}
        for t in sorted(set(tokens)):
            state = "missing"
            for repo in repos:
                argv = (["git", "-C", str(repo), "rev-parse", "--verify", "-q", t + peel]
                        if peel else ["git", "-C", str(repo), "cat-file", "-e", t])
                if subprocess.run(argv, capture_output=True, env=genv()).returncode == 0:
                    state = "found"
                    break
            out[t] = state
        return out
    mod.lookup = lookup_pt


MODS = {"base": load("base"), "ct": load("ct"), "pt": load("pt")}
patch_ct(MODS["ct"])
patch_pt(MODS["pt"])


def run_mod(mod, lane, fleet, rounds, report):
    ns = argparse.Namespace(lane_repo=str(lane), fleet_repo=str(fleet), branch="master",
                            lane="kama", rounds=str(rounds),
                            report=[f"{rounds}={report}"] if report else None,
                            errata=None, no_errata=True)
    try:
        status, doc = mod.run(ns)
        return {"status": status, "doc": json.loads(json.dumps(doc))}
    except Exception as exc:  # EvalError / OSError inside the tool
        return {"status": "error", "error": f"{type(exc).__name__}: {exc}"}


def run_cli(lane, fleet, rounds, report):
    argv = [sys.executable, TOOL, "--lane-repo", str(lane), "--fleet-repo", str(fleet),
            "--rounds", str(rounds), "--no-errata", "--json"]
    if report:
        argv += ["--report", f"{rounds}={report}"]
    p = subprocess.run(argv, capture_output=True, text=True, env=genv())
    RUNLOG.append({"argv": argv, "rc": p.returncode})
    doc = json.loads(p.stdout) if p.stdout.strip() else None
    return {"rc": p.returncode, "doc": doc, "stderr": p.stderr.strip()}


def per_round(doc):
    out = {}
    for r in doc["results"]:
        out[r["round"]] = {
            "round_commits": r["round_commits"], "required": r["required"],
            "post": len(r["post_report"]),
            "defects": sorted([d["kind"], d["token"], str(d.get("cited_elsewhere", "-"))]
                              for d in r["defects"])}
    return out


def same(expected, observed):
    rest = [(d[0], d[1]) for d in observed]
    for ek, ep in expected:
        hit = next((i for i, (k, t) in enumerate(rest)
                    if k == ek and t.startswith(ep)), None)
        if hit is None:
            return False
        rest.pop(hit)
    return not rest


def observe(mod_doc, rnd):
    if mod_doc is None:
        return {"error": "no document"}
    return per_round(mod_doc).get(rnd, {"error": "round missing"})


def run_case(name, note, lane, fleet, rnd, report, exp):
    cli = run_cli(lane, fleet, rnd, report)
    cli_obs = observe(cli["doc"], rnd)
    variants = {}
    for v in ("base", "ct", "pt"):
        r = run_mod(MODS[v], lane, fleet, rnd, report)
        obs = observe(r.get("doc"), rnd) if r["status"] != "error" else {"error": r["error"]}
        expected = exp.get(v, exp["base"])
        ok = "defects" in obs and same(expected, obs["defects"])
        variants[v] = {"observed": obs, "expected": expected, "pass": bool(ok)}
    return {"name": name, "note": note, "cli_rc": cli["rc"],
            "cli_observed": cli_obs,
            "cli_equals_inproc_base": cli_obs == variants["base"]["observed"],
            "variants": variants}


def main():
    fa = build_amb()
    P, K = fa["P"], fa["K"]
    assert not K.startswith(P), "probe commit collides with P; rerun with other message"
    drafts = Path(WORK, "drafts")
    drafts.mkdir(parents=True, exist_ok=True)

    def draft(name, text):
        path = Path(drafts, name)
        path.write_text(text, encoding="utf-8")
        return str(path)

    draft_f2 = (f"## Landed changes\n\n- `{P}`\n- `{K}`\n\n"
                "## Before → after measurements\n")
    fleet_u = build_union(fa, draft_f2)
    fc = build_orphan()
    tree24 = G(LANE, "rev-parse", f"{FULL24}^{{tree}}").stdout.strip()

    cases = [run_case("R19-real", "committed report, real lane and fleet",
                      LANE, FLEET, 19, None, {"base": []})]
    for name, note, text, exp in mutants(tree24):
        cases.append(run_case(name, note, LANE, FLEET, 19, draft(f"{name}.md", text), exp))
    cases.append(run_case(
        "F1-ambiguous-prefix", "lane has two commits with prefix P; draft cites P only",
        fa["lane"], FLEET, 19,
        draft("F1.md", f"## Landed changes\n\n- `{P}`\n\n## Before → after measurements\n"),
        {"base": [("landed-ambiguous", P), ("landed-omitted", K[:12])],
         "pt": [("landed-unresolved", P), ("landed-omitted", K[:12])]}))
    cases.append(run_case(
        "F2-union-gap", "lane: A,B share P; fleet holds only B; draft cites P and K",
        fa["lane"], fleet_u, 19, draft("F2.md", draft_f2),
        {"base": [], "ct": [], "pt": []}))
    cases.append(run_case(
        "F3-orphan-citation", "C2 orphaned by rewrite (later committer date); draft cites C2",
        fc["lane"], FLEET, 19,
        draft("F3.md", f"## Landed changes\n\n- `{fc['c1']}`\n- `{fc['c2']}`\n\n"
              "## Before → after measurements\n"),
        {"base": [("landed-omitted", fc["c2p"][:12])], "ct": [],
         "pt": [("landed-omitted", fc["c2p"][:12])]}))

    # real rounds 10-20: in-process base vs CLI, and both variants
    cli_1020 = run_cli(LANE, FLEET, "10-20", None)
    real = {v: run_mod(MODS[v], LANE, FLEET, "10-20", None) for v in ("base", "ct", "pt")}
    real_pr = {v: per_round(real[v]["doc"]) for v in real}
    cli_pr = per_round(cli_1020["doc"])
    real_diff = {
        "base_doc_equals_cli_json": real["base"]["doc"] == cli_1020["doc"],
        "cli_rc": cli_1020["rc"],
        "ct_rounds_differing": [r for r in cli_pr if real_pr["ct"].get(r) != cli_pr[r]],
        "pt_rounds_differing": [r for r in cli_pr if real_pr["pt"].get(r) != cli_pr[r]],
    }
    # batch-check raw output on the ambiguous and union fixtures
    raw_fa = G(fa["lane"], "cat-file", "--batch-check",
               stdin=f"{P}^{{commit}}\n{P}\n{K}^{{commit}}\n").stdout
    raw_fb_fleet = G(fleet_u, "cat-file", "--batch-check",
                     stdin=f"{P}^{{commit}}\n").stdout
    raw_fb_lane = G(fa["lane"], "cat-file", "--batch-check",
                    stdin=f"{P}^{{commit}}\n").stdout
    fleet_commits_P = [s for s in G(fleet_u, "rev-list", "--all").stdout.split()
                       if s.startswith(P)]
    record = {
        "fixtures": {"amb_lane": str(fa["lane"]), "P": P, "A": fa["A"], "B": fa["B"],
                     "K": K, "lane_commits_with_prefix_P": sorted(fa["lane_hits"]),
                     "fleet_union_commits_with_prefix_P": fleet_commits_P,
                     "orphan_lane": str(fc["lane"]), "c1": fc["c1"], "c2": fc["c2"],
                     "c2p": fc["c2p"]},
        "batch_check_raw": {"fa_lane": raw_fa, "fb_fleet": raw_fb_fleet,
                            "fb_lane": raw_fb_lane},
        "real_rounds_10_20": real_diff,
        "cases": cases,
        "runlog_count": len(RUNLOG),
    }
    Path(OUT, "harness.json").write_text(json.dumps(record, indent=1, sort_keys=True) + "\n",
                                         encoding="utf-8")
    Path(OUT, "harness_runlog.json").write_text(json.dumps(RUNLOG, indent=1) + "\n",
                                                encoding="utf-8")
    print("real_rounds_10_20:", json.dumps(real_diff, sort_keys=True))
    print("fixtures:", json.dumps(record["fixtures"], sort_keys=True))
    print("batch_check_raw:", json.dumps(record["batch_check_raw"], sort_keys=True))
    for c in cases:
        flags = " ".join(f"{v}={'PASS' if c['variants'][v]['pass'] else 'FAIL'}"
                         for v in ("base", "ct", "pt"))
        print(f"{c['name']:30} cli_rc={c['cli_rc']} cli==base:{c['cli_equals_inproc_base']} {flags}")
        for v in ("base", "ct", "pt"):
            obs = c["variants"][v]["observed"]
            print(f"    {v:4} observed={obs.get('defects', obs)}")


if __name__ == "__main__":
    main()
