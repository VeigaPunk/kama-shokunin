#!/usr/bin/env python3
"""Independent probe for the UnusedBlobless family (PG28 / PG36).

Rebuilds the two fixtures from the pinned clone's own builders, asserts the
premise independently of the grid's grading code, runs the current auditor
and compares the twin documents by hand.  Offline only: local git plumbing
and the local auditor, no network, no transport, no execution payload.
"""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

REPO = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseUnusedBlobless/repo")
ROOT = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseUnusedBlobless/probe")
GRID = REPO / "tests/report-audit/promisor-grid.py"
AUDIT = REPO / "tools/report-landing-audit.py"

spec = importlib.util.spec_from_file_location("pg", GRID)
pg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pg)

findings = []


def note(ok, label, detail=""):
    findings.append((ok, label, detail))
    print(("ok   " if ok else "FAIL ") + label + (" :: " + str(detail) if detail else ""))


def git(repo, *args, check=True):
    p = subprocess.run(["git", "--no-lazy-fetch", "-C", str(repo), *args],
                       capture_output=True,
                       env={**{k: v for k, v in os.environ.items()
                               if not k.startswith("GIT_")},
                            "GIT_CONFIG_GLOBAL": os.devnull,
                            "GIT_CONFIG_NOSYSTEM": "1"})
    if check and p.returncode:
        raise SystemExit(f"git {args} failed: {p.stderr.decode()}")
    return p.stdout.decode()


def missing_ids(repo, root):
    out = git(repo, "rev-list", "--objects", "--missing=print",
              "--no-object-names", root)
    return sorted(l[1:] for l in out.split("\n") if l.startswith("?"))


def opaque_ids(repo, root):
    out = git(repo, "-c", "core.commitGraph=false", "rev-list", "--objects",
              "--missing=print", "--no-object-names", "--filter=blob:none",
              root)
    return sorted(l[1:] for l in out.split("\n") if l.startswith("?"))


def inventory(repo):
    out = git(repo, "cat-file", "--batch-all-objects", "--batch-check=%(objectname)")
    return set(out.split())


def audit(lane, fleet):
    argv = [sys.executable, str(AUDIT), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--rounds", "1", "--json", "--no-errata"]
    p = subprocess.run(argv, capture_output=True, cwd=str(lane.parent),
                       env={**{k: v for k, v in os.environ.items()
                               if not k.startswith("GIT_")},
                            "GIT_CONFIG_GLOBAL": os.devnull,
                            "GIT_CONFIG_NOSYSTEM": "1"}, timeout=60)
    return p.returncode, p.stdout.decode(errors="replace"), \
        p.stderr.decode(errors="replace")


def norm(doc, lane, fleet):
    text = json.dumps(doc, sort_keys=True)
    text = text.replace(str(fleet), "<fleet>").replace(str(lane), "<lane>")
    return json.loads(text)


def build_case(name, builder, **kw):
    tmp = ROOT / name
    tmp.mkdir(parents=True, exist_ok=True)
    built = pg.BUILDERS[builder](ROOT, tmp)
    return built


def main():
    ROOT.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------- PG28 fixture
    b28 = build_case("pg28", "c_unhydrated_blobless_lane")
    lane, fleet, shas = b28["lane"], b28["fleet"], b28["shas"]
    note(git(lane, "config", "--get", "remote.origin.promisor").strip() == "true",
         "PG28 lane carries promisor config",
         git(lane, "config", "--get", "remote.origin.promisor").strip())
    facts = pg.promisor_facts(lane)
    note(facts["promisor_backed"] is True,
         "PG28 lane promisor facts (config/filter/promisor/markers)", facts)
    note(bool(facts["promisor_true"] or facts["filter"] or facts["config"]),
         "PG28 lane promisor declaration is a real git promisor declaration",
         facts)
    m28 = missing_ids(lane, "refs/heads/master")
    note(m28 == [shas["f_blob"]],
         "PG28 lane missing exactly the f blob (no tree/commit hole)", m28)
    note(opaque_ids(lane, "refs/heads/master") == [],
         "PG28 lane has no opaque (tree/commit) hole",
         opaque_ids(lane, "refs/heads/master"))
    note(missing_ids(fleet, "HEAD") == [], "PG28 fleet complete", missing_ids(fleet, "HEAD"))
    note(git(fleet, "config", "--get", "remote.origin.promisor", check=False).strip() == "",
         "PG28 fleet carries no promisor metadata")
    origin_url = git(lane, "config", "--get", "remote.origin.url").strip()
    origin = Path(origin_url.replace("file://", ""))
    note(origin.is_dir(), "PG28 lane promisor remote points at a PRESENT local origin "
         "(lazy fetch would succeed: isolation is load-bearing)", origin_url)
    blob_in_origin = subprocess.run(
        ["git", "--no-lazy-fetch", "-C", str(origin), "cat-file", "-e",
         shas["f_blob"]], capture_output=True).returncode == 0
    note(blob_in_origin, "PG28 origin really holds the blob the clone lacks")
    note(git(lane, "ls-tree", "refs/heads/master", "--",
             "corpus/SOURCES.md").strip() == "",
         "PG28 lane carries no corpus/SOURCES.md (audit never needs a blob)")
    cited = git(fleet, "show", "HEAD:.ufo/reports/round-1/kama.md")
    note(shas["lane_commit"] in cited,
         "PG28 report cites the lane commit", shas["lane_commit"][:12])

    before28 = {"lane": inventory(lane), "fleet": inventory(fleet)}
    rc28, out28, err28 = audit(lane, fleet)
    after28 = {"lane": inventory(lane), "fleet": inventory(fleet)}
    acquired28 = {k: sorted(after28[k] - before28[k]) for k in after28}
    note(rc28 == 0, "PG28 current auditor exit 0 (amended expectation)", rc28)
    note(not acquired28["lane"] and not acquired28["fleet"],
         "PG28 auditor acquired no objects", acquired28)
    note(err28.strip() == "", "PG28 auditor stderr empty", repr(err28[-200:]))
    doc28 = json.loads(out28)
    note(doc28["summary"]["status"] == "clean" and doc28["summary"]["defects"] == 0,
         "PG28 verdict document clean with zero defects",
         doc28["summary"]["status"])
    kinds28 = sorted({d["kind"] for r in doc28["results"] for d in r["defects"]})
    note(kinds28 == [], "PG28 finding kinds empty", kinds28)

    # ---------------------------------------------------------- PG36 fixture
    b36 = build_case("pg36", "c_unused_missing_blob_plain")
    lane36, fleet36, shas36 = b36["lane"], b36["fleet"], b36["shas"]
    note(git(lane36, "config", "--get", "remote.origin.promisor", check=False).strip() == "",
         "PG36 lane carries no promisor metadata")
    m36 = missing_ids(lane36, "refs/heads/master")
    note(len(m36) == 1, "PG36 lane has exactly one missing object", m36)
    unused_oid = git(lane36, "ls-tree", "refs/heads/master", "--",
                     "notes/unused.txt").split()[2]
    note(m36 == [unused_oid], "PG36 missing object IS the notes/unused.txt blob",
         (m36, unused_oid))
    note(opaque_ids(lane36, "refs/heads/master") == [],
         "PG36 lane has no opaque (tree/commit) hole",
         opaque_ids(lane36, "refs/heads/master"))
    note(missing_ids(fleet36, "HEAD") == [], "PG36 fleet complete")
    note(git(lane36, "ls-tree", "refs/heads/master", "--",
             "corpus/SOURCES.md").strip() != "",
         "PG36 lane DOES carry corpus/SOURCES.md (differs from PG28 content shape)")
    before36 = {"lane": inventory(lane36), "fleet": inventory(fleet36)}
    rc36, out36, err36 = audit(lane36, fleet36)
    after36 = {"lane": inventory(lane36), "fleet": inventory(fleet36)}
    acquired36 = {k: sorted(after36[k] - before36[k]) for k in after36}
    note(rc36 == 0, "PG36 current auditor exit 0", rc36)
    note(not acquired36["lane"] and not acquired36["fleet"],
         "PG36 auditor acquired no objects", acquired36)
    doc36 = json.loads(out36)
    kinds36 = sorted({d["kind"] for r in doc36["results"] for d in r["defects"]})
    note(kinds36 == [], "PG36 finding kinds empty", kinds36)

    # --------------------------------------------------- twin document diff
    n28 = norm(doc28, lane, fleet)
    n36 = norm(doc36, lane36, fleet36)
    note(n28 == n36, "PG28 and PG36 normalized verdict documents are identical")
    if n28 != n36:
        a = json.dumps(n28, indent=1, sort_keys=True).splitlines()
        b = json.dumps(n36, indent=1, sort_keys=True).splitlines()
        import difflib
        print("\n".join(difflib.unified_diff(a, b, "pg28", "pg36", lineterm="")))
    note(n28["summary"]["by_kind"] == {k: 0 for k in n28["summary"]["by_kind"]},
         "PG28/PG36 by_kind counters all zero", n28["summary"]["by_kind"])

    # ------------------------------- sharpness: the SAME blob, but CITED
    bsharp = build_case("pg28-cited", "c_unhydrated_blobless_lane")
    # rebuild the PG28 shape but with the report citing the missing blob
    tmp = ROOT / "pg28-cited2"
    tmp.mkdir(parents=True, exist_ok=True)
    sharp = pg.build(ROOT, tmp, lane_mark="config", sources=False,
                     blobless_lane=True, cited_blob=True)
    slane, sfleet = sharp["lane"], sharp["fleet"]
    msharp = missing_ids(slane, "refs/heads/master")
    note(msharp == [sharp["shas"]["f_blob"]],
         "sharpness fixture: exactly the f blob missing", msharp)
    note(sharp["shas"]["f_blob"] in git(sfleet, "show",
                                        "HEAD:.ufo/reports/round-1/kama.md"),
         "sharpness fixture: the report cites the missing blob OID")
    rcs, outs, errs = audit(slane, sfleet)
    note(rcs == 2, "sharpness: cited-but-unavailable blob => exit 2", rcs)
    note("unavailable required object" in errs,
         "sharpness: reason is content-derived 'unavailable required object'",
         errs.strip()[-300:])
    note(sharp["shas"]["f_blob"] in errs,
         "sharpness: reason names the unavailable blob OID", errs.strip()[-300:])
    note("partial clone (" not in errs and "promisor pack" not in errs,
         "sharpness: reason is not the r23 metadata refusal", errs.strip()[-200:])
    note(outs.strip() == "", "sharpness: no verdict document on refusal",
         outs.strip()[:200])

    # ------------------------- sharpness2: PG36 shape, the MISSING blob cited
    tmp2 = ROOT / "pg36-cited"
    tmp2.mkdir(parents=True, exist_ok=True)
    sharp2 = pg.build(ROOT, tmp2, unused_file=True, drop=("unused_blob",))
    l2, f2 = sharp2["lane"], sharp2["fleet"]
    miss2 = missing_ids(l2, "refs/heads/master")
    note(len(miss2) == 1, "sharpness2 fixture: one missing blob", miss2)
    rel = ".ufo/reports/round-1/kama.md"
    text2 = git(f2, "show", f"HEAD:{rel}")
    note(miss2[0] not in text2,
         "sharpness2 fixture: the missing blob is NOT cited before the edit")
    newtext = text2.rstrip("\n") + "\nblob " + miss2[0] + "\n"
    (Path(f2) / rel).write_text(newtext, encoding="utf-8")
    subprocess.run(["git", "-C", str(f2), "add", "--", rel], check=True,
                   capture_output=True)
    subprocess.run(["git", "-C", str(f2), "-c", "commit.gpgsign=false",
                    "commit", "-q", "-m", "fleet: cite the missing blob"],
                   check=True, capture_output=True,
                   env={**{k: v for k, v in os.environ.items()
                           if not k.startswith("GIT_")},
                        "GIT_AUTHOR_NAME": "fleet", "GIT_COMMITTER_NAME": "fleet",
                        "GIT_AUTHOR_DATE": "@2100 +0000",
                        "GIT_COMMITTER_DATE": "@2100 +0000"})
    rc2, out2, err2 = audit(l2, f2)
    note(rc2 == 2, "PG36 shape with the MISSING blob cited => exit 2", rc2)
    note("unavailable required object" in err2 and miss2[0] in err2,
         "PG36-shape cited refusal is content-derived and names the object",
         err2.strip()[-300:])
    note(out2.strip() == "", "PG36-shape cited refusal carries no verdict document")

    # ------------- sharpness3: blobless lane that DOES carry corpus/SOURCES.md
    tmp3 = ROOT / "pg28-registry"
    tmp3.mkdir(parents=True, exist_ok=True)
    sharp3 = pg.build(ROOT, tmp3, lane_mark="config", blobless_lane=True)
    l3, f3 = sharp3["lane"], sharp3["fleet"]
    m3 = missing_ids(l3, "refs/heads/master")
    note(len(m3) >= 1, "sharpness3 fixture: blobless lane misses the registry blob",
         m3)
    note(sharp3["shas"]["sources_blob"] in m3,
         "sharpness3: the corpus/SOURCES.md blob is the missing one",
         (sharp3["shas"]["sources_blob"], m3))
    rc3, out3, err3 = audit(l3, f3)
    note(rc3 == 2, "sharpness3: blobless lane WITH an unreadable registry => exit 2",
         rc3)
    note("unavailable required object" in err3 and
         sharp3["shas"]["sources_blob"] in err3,
         "sharpness3: content-derived refusal naming the registry blob",
         err3.strip()[-300:])
    note(out3.strip() == "", "sharpness3: no verdict document on refusal")

    failed = [f for f in findings if not f[0]]
    print(f"\nprobe checks={len(findings)} failed={len(failed)}")
    for f in failed:
        print("FAILED:", f[1], f[2])
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
