#!/usr/bin/env python3
"""Fourth bounded round: pure dangling trees, the exact supplement shape
(opaque tree hides a cited blob) and the promisor-pack root question.
"""
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from probe import (AUDIT, ROOT, WORK, base_env, body_for, build, commit,  # noqa
                   drop, g, republish, FAKE)

SPEC = importlib.util.spec_from_file_location("auditor_r24d", AUDIT)
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)

RESULTS = []


def case(name, expect, ok, observed):
    RESULTS.append({"case": name, "expect": expect, "observed": observed,
                    "pass": bool(ok)})
    print(f"{'OK  ' if ok else 'FAIL'} {name}: expect={expect}\n"
          f"      observed={observed}")


def audit(lane, fleet, extra=()):
    env = base_env()
    env["TMPDIR"] = str(WORK / "tmp")
    cmd = [sys.executable, str(AUDIT), "--lane-repo", str(lane),
           "--fleet-repo", str(fleet), "--branch", "master", "--lane", "kama",
           "--rounds", "1", "--json", *extra]
    p = subprocess.run(cmd, capture_output=True, text=True, env=env,
                       cwd=str(WORK))
    defects, doc = [], None
    if p.stdout.strip():
        doc = json.loads(p.stdout)
        for res in doc["results"]:
            for d in res["defects"]:
                defects.append((d["kind"], d["token"]))
    return p.returncode, p.stderr.strip(), defects


def fresh(tag):
    d = WORK / tag
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    return d


def sets(lane, fleet):
    lm, lo = M.missing_reachable(lane, g(lane, "rev-parse", "HEAD"))
    fm, fo = M.missing_reachable(fleet, g(fleet, "rev-parse", "HEAD"))
    return lm, lo, fm, fo


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    (WORK / "tmp").mkdir(parents=True, exist_ok=True)

    # S20 a present tree with no commit at all, holding a missing blob
    tmp = fresh("s20")
    lane, fleet, info = build(tmp)
    blob = subprocess.run(["git", "-C", str(lane), "hash-object", "-w",
                           "--stdin"], input="tree-only payload\n", text=True,
                          capture_output=True, env=base_env()).stdout.strip()
    sub = subprocess.run(["git", "-C", str(lane), "mktree"],
                         input=f"100644 blob {blob}\tf\n", capture_output=True,
                         text=True, env=base_env()).stdout.strip()
    drop(lane, blob)
    lm, lo, _, _ = sets(lane, fleet)
    ok = blob in lm
    case("S20-dangling-present-tree-is-a-root",
         "the blob under a commit-less dangling tree is in missing", ok,
         f"blob_in_missing={blob in lm} blob_in_opaque={blob in lo}")

    # S21 the exact supplement shape: a cited blob hidden behind a missing
    # subtree (both the subtree and the blob are absent locally)
    tmp = fresh("s21")
    lane, fleet, info = build(tmp)
    blob = subprocess.run(["git", "-C", str(lane), "hash-object", "-w",
                           "--stdin"], input="hidden payload\n", text=True,
                          capture_output=True, env=base_env()).stdout.strip()
    sub = subprocess.run(["git", "-C", str(lane), "mktree"],
                         input=f"100644 blob {blob}\tf\n", capture_output=True,
                         text=True, env=base_env()).stdout.strip()
    top = subprocess.run(["git", "-C", str(lane), "mktree"],
                         input=f"040000 tree {sub}\td\n", capture_output=True,
                         text=True, env=base_env()).stdout.strip()
    env = base_env(GIT_AUTHOR_DATE="@450 +0000",
                   GIT_COMMITTER_DATE="@450 +0000")
    c = subprocess.run(["git", "-C", str(lane), "commit-tree", top, "-p",
                        "HEAD", "-m", "round-1: hidden"], capture_output=True,
                       text=True, env=env).stdout.strip()
    g(lane, "reset", "-q", "--hard", c)
    body = body_for(info["required"] + [c], blob + "\n")
    republish(fleet, info, body)
    drop(lane, sub)
    drop(lane, blob)
    rc, err, defects = audit(lane, fleet)
    lm, lo, _, _ = sets(lane, fleet)
    ok = (rc == 2 and blob in err and "unavailable required object" in err
          and sub in lo)
    case("S21-opaque-tree-hides-a-cited-blob",
         "exit 2 naming the cited blob / missing tree", ok,
         f"rc={rc} err={err!r} blob_in_missing={blob in lm} "
         f"tree_in_opaque={sub in lo}")

    # S22 does a promisor-marked pack still feed present_roots?
    tmp = fresh("s22")
    lane, fleet, info = build(tmp)
    before = len(M.present_roots(lane))
    subprocess.run(["git", "-C", str(lane), "repack", "-a", "-d"],
                   check=True, capture_output=True, env=base_env())
    pack_dir = Path(lane) / ".git" / "objects" / "pack"
    packs = sorted(pack_dir.glob("*.pack"))
    packs[0].with_suffix(".promisor").write_text("", encoding="utf-8")
    for k, v in (("remote.origin.promisor", "true"),
                 ("remote.origin.url", "ssh://example.invalid/x.git"),
                 ("extensions.partialClone", "origin"),
                 ("remote.origin.partialclonefilter", "blob:none")):
        g(lane, "config", k, v)
    after = len(M.present_roots(lane))
    # a missing blob under a dangling commit that now lives in the pack
    blob = subprocess.run(["git", "-C", str(lane), "hash-object", "-w",
                           "--stdin"], input="packed dangling\n", text=True,
                          capture_output=True, env=base_env()).stdout.strip()
    sub = subprocess.run(["git", "-C", str(lane), "mktree"],
                         input=f"100644 blob {blob}\tf\n", capture_output=True,
                         text=True, env=base_env()).stdout.strip()
    top = subprocess.run(["git", "-C", str(lane), "mktree"],
                         input=f"040000 tree {sub}\td\n", capture_output=True,
                         text=True, env=base_env()).stdout.strip()
    d = subprocess.run(["git", "-C", str(lane), "commit-tree", top, "-p",
                        "HEAD", "-m", "dangling"], capture_output=True, text=True,
                       env=base_env(GIT_AUTHOR_DATE="@700 +0000",
                                    GIT_COMMITTER_DATE="@700 +0000")
                      ).stdout.strip()
    subprocess.run(["git", "-C", str(lane), "repack", "-a", "-d", "-q"],
                   check=True, capture_output=True, env=base_env())
    drop(lane, blob)
    lm, lo, _, _ = sets(lane, fleet)
    ok = blob in lm
    case("S22-promisor-pack-objects-still-feed-the-root-set",
         "roots survive the promisor marker; dangling blob still found", ok,
         f"roots_before={before} roots_after={after} "
         f"dangling_blob_in_missing={blob in lm} opaque={sorted(lo)}")

    print("\n---- summary ----")
    for r in RESULTS:
        print(f"{'OK  ' if r['pass'] else 'FAIL'} {r['case']}")
    failed = [r for r in RESULTS if not r["pass"]]
    print(f"cases={len(RESULTS)} failed={len(failed)}")
    (ROOT / "probe4-results.json").write_text(
        json.dumps(RESULTS, indent=1, default=str), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
