#!/usr/bin/env python3
"""Bounded, benign, OFFLINE fixture probe for the pinned r24 auditor.

Axes under attack (RepoStore.missing / missing_reachable / opaque_hole):
  A conditionality  - the store-wide diagnosis is not an audit precondition
  B blob vs non-leaf - a missing blob is not an opaque hole; a missing
                      tree/commit is
  C store-wide roots - present-but-dangling objects are roots too
  D no closure gate  - unrelated holes never block a clean verdict

Everything is built locally with plain git plumbing. No network, no
transport, no execution payloads.
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path("/fast/scratch/hyaku/kama-r24/falsify/CodeOpaqueDiagnosis")
REPO = ROOT / "repo"
AUDIT = REPO / "tools/report-landing-audit.py"
WORK = ROOT / "work"
RESULTS = []


def g(repo, *args, stdin=None, env=None, check=True):
    p = subprocess.run(["git", "-C", str(repo), *args], input=stdin,
                       capture_output=True, text=True, env=env)
    if check and p.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} in {repo} rc={p.returncode}\n"
                         f"{p.stderr}")
    return p.stdout.strip()


def base_env(**extra):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_AUTHOR_NAME="kama-shokunin",
             GIT_COMMITTER_NAME="kama-shokunin",
             GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x", **extra)
    return e


def denv(**extra):
    e = base_env(**extra)
    e.update(GIT_AUTHOR_DATE="@%d +0000" % extra.pop("_when", 0))
    return e


def commit(repo, msg, when, files=None):
    for name, text in (files or {}).items():
        p = Path(repo) / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    env = base_env(GIT_AUTHOR_DATE="@%d +0000" % when,
                   GIT_COMMITTER_DATE="@%d +0000" % when)
    g(repo, "add", "-A")
    g(repo, "commit", "-q", "-m", msg, env=env)


def init_repo(path):
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q", "--initial-branch=master", str(path)],
                   check=True, capture_output=True,
                   env=base_env())
    g(path, "config", "gc.auto", "0")
    g(path, "config", "maintenance.auto", "false")
    g(path, "config", "user.name", "kama-shokunin")
    g(path, "config", "user.email", "a@x")
    return path


def drop(repo, oid):
    """Remove one loose object (no packing, no prune)."""
    p = Path(repo) / ".git" / "objects" / oid[:2] / oid[2:]
    if not p.exists():
        raise SystemExit(f"object {oid} is not loose in {repo}")
    p.unlink()
    return oid


FAKE = "0" * 40


def body_for(required, extra=""):
    return ("## Work performed\nfixture round 1\n" + extra +
            "\n## Landed changes\n" +
            "".join(f"- `{c}`\n" for c in required))


def build(tmp, report_body=None, subtree=False):
    """A lane repo with two required round-1 commits, one unrelated
    commit, one post-cutoff commit, plus a fleet repo holding the round-1
    report. Returns (lane, fleet, info)."""
    lane = init_repo(tmp / "lane")
    fleet = init_repo(tmp / "fleet")
    commit(lane, "round-1: first", 100, {"a.txt": "a\n"})
    first = g(lane, "rev-parse", "HEAD")
    commit(lane, "round-1: second", 200, {"b.txt": "b\n"})
    second = g(lane, "rev-parse", "HEAD")
    commit(lane, "unrelated: noise", 300, {"noise.txt": "noise\n"})
    noise = g(lane, "rev-parse", "HEAD")
    noise_blob = g(lane, "rev-parse", f"{noise}:noise.txt")
    commit(lane, "round-1: post", 5000, {"post.txt": "post\n"})
    post = g(lane, "rev-parse", "HEAD")
    if subtree:
        # a commit whose tree holds a real subtree d/ with blob d/f
        blob = subprocess.run(["git", "-C", str(lane), "hash-object", "-w",
                               "--stdin"], input="d/f payload\n", text=True,
                              capture_output=True, env=base_env())
        blob_oid = blob.stdout.strip()
        # build the subtree and the parent tree by hand
        sub = subprocess.run(["git", "-C", str(lane), "mktree"],
                             input=f"100644 blob {blob_oid}\tf\n",
                             capture_output=True, text=True, env=base_env())
        sub_oid = sub.stdout.strip()
        parent = subprocess.run(["git", "-C", str(lane), "mktree"],
                                input=f"040000 tree {sub_oid}\td\n",
                                capture_output=True, text=True, env=base_env())
        parent_oid = parent.stdout.strip()
        env = base_env(GIT_AUTHOR_DATE="@400 +0000",
                       GIT_COMMITTER_DATE="@400 +0000")
        commit_oid = subprocess.run(
            ["git", "-C", str(lane), "commit-tree", parent_oid, "-p", "HEAD",
             "-m", "round-1: subtree"], capture_output=True, text=True,
            env=env).stdout.strip()
        g(lane, "reset", "-q", "--hard", commit_oid)
    commit(lane, "registry: errata", 600,
           {"registry/report-landing-errata.tsv": "# no rows\n"})
    required = [first, second]
    if subtree:
        required = required + [g(lane, "rev-parse", "HEAD~1")]
    body = report_body
    if body is None:
        body = body_for(required)
    rel = ".ufo/reports/round-1/kama.md"
    p = fleet / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body, encoding="utf-8")
    commit(fleet, "fleet: round-1 report", 1000, {rel: body})
    return lane, fleet, {"first": first, "second": second, "noise": noise,
                         "noise_blob": noise_blob, "post": post,
                         "rel": rel, "required": required}


def republish(fleet, info, body):
    p = fleet / info["rel"]
    p.write_text(body, encoding="utf-8")
    commit(fleet, "fleet: republish report", 2000, {info["rel"]: body})


def audit(lane, fleet, rounds="1", extra=()):
    env = base_env()
    env["TMPDIR"] = str(WORK / "tmp")
    Path(env["TMPDIR"]).mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, str(AUDIT), "--lane-repo", str(lane),
           "--fleet-repo", str(fleet), "--branch", "master", "--lane", "kama",
           "--rounds", rounds, "--json", *extra]
    p = subprocess.run(cmd, capture_output=True, text=True, env=env,
                       cwd=str(WORK))
    doc = None
    if p.stdout.strip():
        try:
            doc = json.loads(p.stdout)
        except json.JSONDecodeError:
            doc = None
    defects = []
    if doc:
        for res in doc["results"]:
            for d in res["defects"]:
                defects.append((d["kind"], d["token"]))
    return p.returncode, p.stdout, p.stderr.strip(), defects, doc


def audit_inproc(lane, fleet, rounds="1"):
    import argparse
    ns = argparse.Namespace(lane_repo=str(lane), fleet_repo=str(fleet),
                             branch="master", lane="kama", rounds=rounds,
                             report=[], errata=None, no_errata=True)
    try:
        status, doc = MOD.run(ns)
        defects = sorted((d["kind"], d["token"])
                         for res in doc["results"] for d in res["defects"])
        return status, "", "", defects, doc
    except MOD.EvalError as exc:
        return 2, "", str(exc), [], None


def load_module():
    spec = importlib.util.spec_from_file_location("auditor_r24", AUDIT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = load_module()


def store_sets(lane, fleet):
    lane_root = g(lane, "rev-parse", "HEAD")
    fleet_root = g(fleet, "rev-parse", "HEAD")
    missing, opaque = MOD.missing_reachable(lane, lane_root)
    fmissing, fopaque = MOD.missing_reachable(fleet, fleet_root)
    return {"lane_missing": missing, "lane_opaque": opaque,
            "fleet_missing": fmissing, "fleet_opaque": fopaque,
            "lane_root": lane_root, "fleet_root": fleet_root}


def case(name, expect, **kw):
    ok = bool(kw.get("pass_", kw.get("pass")))
    RESULTS.append({"case": name, "expect": expect, "observed": kw,
                    "pass": ok})
    tag = "OK " if ok else "FAIL"
    print(f"{tag} {name}: expect={expect} observed={kw.get('observed')}")
    return ok


def fresh(tag):
    d = WORK / tag
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    return d


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    (WORK / "tmp").mkdir(parents=True, exist_ok=True)

    # --- S1 baseline -------------------------------------------------
    tmp = fresh("s1")
    lane, fleet, info = build(tmp)
    rc, out, err, defects, doc = audit(lane, fleet)
    case("S1-baseline-clean", "exit 0, no defects",
         observed=f"rc={rc} defects={defects} err={err!r}",
         pass_=rc == 0 and defects == [])

    # --- S2 unrelated missing blob, no unresolved citation -----------
    tmp = fresh("s2")
    lane, fleet, info = build(tmp)
    drop(lane, info["noise_blob"])
    rc, out, err, defects, doc = audit(lane, fleet)
    sets = store_sets(lane, fleet)
    ok = (rc == 0 and defects == []
          and info["noise_blob"] in sets["lane_missing"]
          and info["noise_blob"] not in sets["lane_opaque"])
    case("S2-unrelated-missing-blob-does-not-block", "exit 0, no defects",
         observed=f"rc={rc} defects={defects} blob_in_missing="
                  f"{info['noise_blob'] in sets['lane_missing']} "
                  f"blob_in_opaque={info['noise_blob'] in sets['lane_opaque']}",
         pass_=ok)

    # --- S3 missing blob + fabricated unresolved token ----------------
    tmp = fresh("s3")
    lane, fleet, info = build(tmp)
    drop(lane, info["noise_blob"])
    body = body_for(info["required"], FAKE + "\n")
    republish(fleet, info, body)
    rc, out, err, defects, doc = audit(lane, fleet)
    sets = store_sets(lane, fleet)
    ok = (rc == 1 and defects == [("unresolved-full-hash", FAKE)]
          and "unavailable required object" not in err)
    case("S3-blob-hole-does-not-make-unresolved-token-unknown",
         "exit 1 unresolved-full-hash (not exit 2)",
         observed=f"rc={rc} defects={defects} err={err!r}", pass_=ok)

    # --- S4 missing tree (non-leaf) + fabricated token --------------
    tmp = fresh("s4")
    lane, fleet, info = build(tmp, subtree=True)
    # the subtree object of the last round-1 commit
    head = g(lane, "rev-parse", "HEAD")
    sub = g(lane, "rev-parse", f"{head}:d")
    drop(lane, sub)
    body = body_for(info["required"], FAKE + "\n")
    republish(fleet, info, body)
    rc, out, err, defects, doc = audit(lane, fleet)
    sets = store_sets(lane, fleet)
    ok = (rc == 2 and sub in sets["lane_opaque"]
          and sub not in sets["lane_missing"] - sets["lane_opaque"]
          and "could be hidden behind the missing tree or commit" in err
          and sub in err)
    case("S4-missing-tree-opaque-hole-refuses-unresolved-token",
         "exit 2 naming the missing tree",
         observed=f"rc={rc} err={err!r} tree_in_opaque="
                  f"{sub in sets['lane_opaque']}", pass_=ok)

    # --- S5 missing tree, every citation resolves -------------------
    tmp = fresh("s5")
    lane, fleet, info = build(tmp, subtree=True)
    head = g(lane, "rev-parse", "HEAD")
    sub = g(lane, "rev-parse", f"{head}:d")
    drop(lane, sub)
    rc, out, err, defects, doc = audit(lane, fleet)
    sets = store_sets(lane, fleet)
    ok = rc == 0 and defects == [] and sub in sets["lane_opaque"]
    case("S5-missing-tree-alone-is-not-a-closure-precondition",
         "exit 0, no defects",
         observed=f"rc={rc} defects={defects} err={err!r} "
                  f"tree_in_opaque={sub in sets['lane_opaque']}", pass_=ok)

    # --- S6 cited missing blob --------------------------------------
    tmp = fresh("s6")
    lane, fleet, info = build(tmp)
    blob = g(lane, "rev-parse", f"{info['first']}:a.txt")
    drop(lane, blob)
    body = body_for(info["required"], blob + "\n")
    republish(fleet, info, body)
    rc, out, err, defects, doc = audit(lane, fleet)
    ok = rc == 2 and blob in err and "cannot serve it" in err
    case("S6-cited-missing-blob-is-unknown", "exit 2 naming the blob",
         observed=f"rc={rc} err={err!r}", pass_=ok)

    # --- S7 dangling present roots ----------------------------------
    tmp = fresh("s7")
    lane, fleet, info = build(tmp)
    blob = subprocess.run(["git", "-C", str(lane), "hash-object", "-w",
                           "--stdin"], input="dangling payload\n", text=True,
                          capture_output=True, env=base_env()).stdout.strip()
    sub = subprocess.run(["git", "-C", str(lane), "mktree"],
                         input=f"100644 blob {blob}\tf\n", capture_output=True,
                         text=True, env=base_env()).stdout.strip()
    top = subprocess.run(["git", "-C", str(lane), "mktree"],
                         input=f"040000 tree {sub}\td\n", capture_output=True,
                         text=True, env=base_env()).stdout.strip()
    dang = subprocess.run(
        ["git", "-C", str(lane), "commit-tree", top, "-p", "HEAD",
         "-m", "dangling"], capture_output=True, text=True,
        env=base_env(GIT_AUTHOR_DATE="@700 +0000",
                     GIT_COMMITTER_DATE="@700 +0000")).stdout.strip()
    # dangling commit and its tree are present but unreachable from any ref
    drop(lane, blob)
    # contrast: a walk rooted at HEAD only
    head = g(lane, "rev-parse", "HEAD")
    only_root = subprocess.run(
        ["git", "-C", str(lane), "rev-list", "--objects", "--missing=print",
         "--no-object-names", head], capture_output=True, text=True,
        env=base_env()).stdout
    sets = store_sets(lane, fleet)
    ok = blob in sets["lane_missing"]
    case("S7-dangling-present-objects-are-roots",
         "the dangling blob appears in the store-wide missing set",
         observed=f"dangling_commit={dang[:12]} blob_in_missing="
                  f"{blob in sets['lane_missing']} "
                  f"blob_in_rooted_walk={'?' + blob in only_root}",
         pass_=ok)

    # --- S8 missing commit (non-leaf) via a dangling child ---------
    tmp = fresh("s8")
    lane, fleet, info = build(tmp)
    parent = subprocess.run(
        ["git", "-C", str(lane), "commit-tree", f"{info['first']}^{{tree}}",
         "-m", "vanished parent"], capture_output=True, text=True,
        env=base_env(GIT_AUTHOR_DATE="@800 +0000",
                     GIT_COMMITTER_DATE="@800 +0000")).stdout.strip()
    child = subprocess.run(
        ["git", "-C", str(lane), "commit-tree", f"{info['first']}^{{tree}}",
         "-p", parent, "-m", "round-1: orphan child"], capture_output=True,
        text=True, env=base_env(GIT_AUTHOR_DATE="@810 +0000",
                                GIT_COMMITTER_DATE="@810 +0000")).stdout.strip()
    drop(lane, parent)
    sets = store_sets(lane, fleet)
    ok = parent in sets["lane_missing"] and parent in sets["lane_opaque"]
    case("S8-missing-commit-is-an-opaque-hole",
         "the missing commit appears in missing and in opaque",
         observed=f"missing={parent in sets['lane_missing']} "
                  f"opaque={parent in sets['lane_opaque']}", pass_=ok)

    # --- S9 promisor metadata does not change the verdict -----------
    tmp = fresh("s9")
    lane, fleet, info = build(tmp, subtree=True)
    head = g(lane, "rev-parse", "HEAD")
    sub = g(lane, "rev-parse", f"{head}:d")
    drop(lane, sub)
    body = body_for(info["required"], FAKE + "\n")
    republish(fleet, info, body)
    trap = WORK / "s9" / "trap"
    for k, v in (("extensions.partialClone", "origin"),
                 ("remote.origin.url", "ssh://example.invalid/x.git"),
                 ("remote.origin.promisor", "true"),
                 ("remote.origin.partialclonefilter", "blob:none"),
                 ("core.sshCommand", f"touch {trap}; false")):
        g(lane, "config", k, v)
    rc, out, err, defects, doc = audit(lane, fleet)
    ok = (rc == 2 and "could be hidden behind the missing tree or commit" in err
          and not trap.exists())
    case("S9-promisor-metadata-keeps-the-opaque-diagnosis",
         "exit 2 naming the tree, remote never contacted",
         observed=f"rc={rc} err={err!r} trap={trap.exists()}", pass_=ok)

    # --- S10 determinism of the named hole --------------------------
    tmp = fresh("s10")
    lane, fleet, info = build(tmp, subtree=True)
    head = g(lane, "rev-parse", "HEAD")
    sub = g(lane, "rev-parse", f"{head}:d")
    drop(lane, sub)
    body = body_for(info["required"], FAKE + "\n")
    republish(fleet, info, body)
    r1 = audit(lane, fleet)
    r2 = audit(lane, fleet)
    ok = r1[0] == r2[0] == 2 and r1[2] == r2[2]
    case("S10-refusal-names-the-same-hole-twice", "identical stderr twice",
         observed=f"rc={r1[0]}/{r2[0]} same={r1[2] == r2[2]}", pass_=ok)

    # --- S11 the walk is not a precondition (call counting) ---------
    tmp = fresh("s11")
    lane, fleet, info = build(tmp)
    calls = []
    real = MOD.missing_reachable

    def counting(repo, root):
        calls.append(str(repo))
        return real(repo, root)

    MOD.missing_reachable = counting
    rc, out, err, defects, doc = audit_inproc(lane, fleet)
    clean_calls = list(calls)
    calls.clear()
    blob = g(lane, "rev-parse", f"{info['first']}:a.txt")
    drop(lane, blob)
    body = ("## Work performed\n" + blob +
            "\n## Landed changes\n" f"- `{info['first']}`\n- `{info['second']}`\n")
    p = fleet / info["rel"]
    p.write_text(body, encoding="utf-8")
    commit(fleet, "fleet: cite missing blob", 2000, {info["rel"]: body})
    rc2, out2, err2, d2, doc2 = audit_inproc(lane, fleet)
    dirty_calls = list(calls)
    MOD.missing_reachable = real
    ok = clean_calls == [] and len(dirty_calls) >= 1 and rc == 0 and rc2 == 2
    case("S11-diagnosis-is-conditional-not-a-precondition",
         "zero walks on a clean run, >=1 on the unresolved path",
         observed=f"clean_walks={len(clean_calls)} unresolved_walks="
                  f"{len(dirty_calls)} rc={rc}/{rc2}", pass_=ok)

    failed = [r for r in RESULTS if not r.get("pass_") and not r.get("pass")]
    print("\n---- summary ----")
    for r in RESULTS:
        print(f"{'OK  ' if r.get('pass_') or r.get('pass') else 'FAIL'} {r['case']}")
    print(f"cases={len(RESULTS)} failed={len(failed)}")
    (ROOT / "probe-results.json").write_text(
        json.dumps(RESULTS, indent=1, default=str), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
