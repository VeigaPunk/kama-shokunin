#!/usr/bin/env python3
"""CaseSourceBlob independent probe: PG13 / PG14 premises, verdicts, twin
equality, no-acquisition and a content-derived control.  Offline only."""
import importlib.util, json, os, re, shutil, subprocess, sys
from pathlib import Path

REPO = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseSourceBlob/repo")
SCRATCH = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseSourceBlob")
ROOT = SCRATCH / "probe-root"
GRID = REPO / "tests/report-audit/promisor-grid.py"

spec = importlib.util.spec_from_file_location("grid", GRID)
grid = importlib.util.module_from_spec(spec)
spec.loader.exec_module(grid)

AUDIT = REPO / "tools/report-landing-audit.py"
FROZEN_REV = "0df800e896f6bce285a81e794ad4ae1d1e6c3a71"


def sh(cmd, cwd=None, env=None, data=None):
    p = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, input=data)
    return p.returncode, p.stdout.decode(errors="replace"), p.stderr.decode(errors="replace")


def frozen_auditor():
    out = SCRATCH / "frozen-audit.py"
    rc, so, se = sh(["git", "-C", str(REPO), "cat-file", "blob",
                     f"{FROZEN_REV}:tools/report-landing-audit.py"])
    assert rc == 0, se
    out.write_bytes(so.encode())
    return out


def env():
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_AUTHOR_NAME="fixture", GIT_COMMITTER_NAME="fixture",
             GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x")
    return e


def run_audit(auditor, lane, fleet, cwd):
    argv = [sys.executable, str(auditor), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--rounds", "1", "--json", "--no-errata"]
    p = subprocess.run(argv, capture_output=True, env=env(), cwd=str(cwd),
                       timeout=60)
    return p.returncode, p.stdout.decode(errors="replace"), p.stderr.decode(errors="replace")


def inv(repo):
    rc, so, se = sh(["git", "--no-lazy-fetch", "-C", str(repo), "cat-file",
                     "--batch-all-objects", "--batch-check=%(objectname)"], env=env())
    return set(so.split())


def presence(repo, oid):
    rc, so, se = sh(["git", "--no-lazy-fetch", "--no-replace-objects", "-C",
                     str(repo), "cat-file", "-e", oid + "^{object}"], env=env())
    return rc == 0


def main():
    if ROOT.exists():
        shutil.rmtree(ROOT)
    ROOT.mkdir(parents=True)
    FROZ = frozen_auditor()
    report = {"cases": {}}
    for case, builder in (("PG13-missing-lane-blob-promisor", "c_missing_lane_blob_promisor"),
                          ("PG14-missing-lane-blob-plain", "c_missing_lane_blob_plain")):
        tmp = ROOT / case
        tmp.mkdir(parents=True)
        built = grid.BUILDERS[builder](ROOT, tmp)
        lane, fleet = built["lane"], built["fleet"]
        shas = built["shas"]
        prem = built["premise"]
        facts = grid.promisor_facts(lane)
        cfg = sh(["git", "-C", str(lane), "config", "--list"], env=env())[1].split()
        rec = {
            "builder": builder,
            "premise": prem,
            "lane_promisor_facts": facts,
            "lane_config": cfg,
            "fleet_promisor_facts": grid.promisor_facts(fleet),
            "objects": {
                "sources_blob": {"oid": shas.get("sources_blob"),
                                 "present": presence(lane, shas["sources_blob"])},
                "tip_tree": {"oid": shas["tip_tree"], "present": presence(lane, shas["tip_tree"])},
                "lane_commit": {"oid": shas["lane_commit"], "present": presence(lane, shas["lane_commit"])},
                "f_blob": {"oid": shas["f_blob"], "present": presence(lane, shas["f_blob"])},
                "report_blob": {"oid": shas["report_blob"], "present": presence(fleet, shas["report_blob"])},
                "fleet_tip_tree": {"oid": shas["fleet_tip_tree"], "present": presence(fleet, shas["fleet_tip_tree"])},
                "fake": {"oid": shas["fake"], "present_in_lane": presence(lane, shas["fake"]),
                         "present_in_fleet": presence(fleet, shas["fake"])},
            },
            "worktree_SOURCES_present": (Path(lane) / "corpus/SOURCES.md").is_file(),
            "worktree_SOURCES_bytes": (Path(lane) / "corpus/SOURCES.md").read_text()
                                      if (Path(lane) / "corpus/SOURCES.md").is_file() else None,
        }
        before = {"lane": inv(lane), "fleet": inv(fleet)}
        rec["audit"] = {}
        for arm, auditor in (("current", AUDIT), ("frozen", FROZ)):
            code, out, err = run_audit(auditor, lane, fleet, tmp)
            after = {"lane": inv(lane), "fleet": inv(fleet)}
            doc = None
            try:
                doc = json.loads(out)
            except ValueError:
                pass
            rec["audit"][arm] = {
                "exit": code,
                "stdout_len": len(out),
                "stdout_document": doc,
                "stderr": err.strip(),
                "stderr_prefix_ok": err.startswith("could-not-evaluate:"),
                "stdout_is_verdict_doc": doc is not None,
                "objects_acquired": {k: sorted(after[k] - before[k]) for k in after},
                "objects_lost": {k: sorted(before[k] - after[k]) for k in after},
                "names_hit": {n: (n in err) for n in
                              ("corpus/SOURCES.md", shas["sources_blob"])},
                "forbidden_hit": {f: (f in err) for f in ("partial clone (", "promisor pack")},
                "reason_terms": sorted({t for t in grid.REASON_CLASSES["unavailable"]
                                        if t in err.lower()}),
            }
        # control: restore the missing blob object offline, re-run current auditor
        tmp2 = Path(tmp) / "restore"
        repo2 = tmp2 / "obj"
        repo2.mkdir(parents=True, exist_ok=True)
        sh(["git", "init", "-q", "-b", "master", str(repo2)], env=env())
        oid = sh(["git", "-C", str(repo2), "hash-object", "-w", "-t", "blob",
                  "--stdin"], env=env(), data=rec["worktree_SOURCES_bytes"].encode())[1].strip()
        rec["restored_oid_matches"] = (oid == shas["sources_blob"])
        gd = grid.git_dir(lane)
        dst = gd / "objects" / oid[:2] / oid[2:]
        dst.parent.mkdir(parents=True, exist_ok=True)
        src = repo2 / ".git" / "objects" / oid[:2] / oid[2:]
        shutil.copy2(src, dst)
        code, out, err = run_audit(AUDIT, lane, fleet, tmp)
        doc = None
        try:
            doc = json.loads(out)
        except ValueError:
            pass
        rec["control_restored_blob"] = {
            "exit": code,
            "stdout_document": doc,
            "stderr": err.strip(),
            "summary": (doc or {}).get("summary"),
        }
        # restore the fixture to its graded state (drop the object again)
        dst.unlink()
        rec["control_after_restore_removed_again"] = presence(lane, shas["sources_blob"])
        report["cases"][case] = rec

    # twin comparison computed here (the grid leaves it null for exit-2 rows)
    a = report["cases"]["PG13-missing-lane-blob-promisor"]
    b = report["cases"]["PG14-missing-lane-blob-plain"]
    norm = lambda s, case: re.sub(r"[0-9a-zA-Z_\-]*" + case + r"", "<case>", s) \
        if False else s
    def rel(s, tmpname):
        return s.replace(str(ROOT / tmpname), "<case>")
    twin = {}
    for arm in ("current", "frozen"):
        se_a = rel(a["audit"][arm]["stderr"], "PG13-missing-lane-blob-promisor")
        se_b = rel(b["audit"][arm]["stderr"], "PG14-missing-lane-blob-plain")
        twin[arm] = {
            "stderr_equal_modulo_case_path": se_a == se_b,
            "stderr_a": se_a,
            "stderr_b": se_b,
            "stdout_documents_equal": (a["audit"][arm]["stdout_document"] ==
                                       b["audit"][arm]["stdout_document"]),
            "both_absent_documents": (a["audit"][arm]["stdout_document"] is None and
                                      b["audit"][arm]["stdout_document"] is None),
            "exit_equal": a["audit"][arm]["exit"] == b["audit"][arm]["exit"],
        }
    report["twin"] = twin
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
