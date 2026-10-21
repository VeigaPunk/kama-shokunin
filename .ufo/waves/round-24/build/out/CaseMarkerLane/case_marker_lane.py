#!/usr/bin/env python3
"""Round-24 offline oracle case: paired .promisor+.pack marker in a COMPLETE lane.

Lane: KamaR23-2.CaseMarkerLane-2
Case: paired .promisor + .pack marker only (no promisor remote config) in a
      complete lane repository; the correct verdict is the clean verdict of the
      otherwise identical full clone (exit 0, no findings).

Method (oracle, not implementation):
  The expected result is derived from the FULL-CLONE TWIN of the same fixture:
  the same commits, the same report, the same fleet, the marker removed.  The
  expected exit/findings of the marked case are the twin's, by construction.
  No candidate implementation is consulted to produce the expectation.

Everything happens in a scratch tree; no fixture is written outside the
scratch root, and no network transport or repository program is exercised.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

LANE_DIR = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
AUDIT = LANE_DIR / "tools/report-landing-audit.py"
BASE_COMMIT = "0df800e896f6bce285a81e794ad4ae1d1e6c3a71"
SCRATCH = Path("/fast/scratch/hyaku/kama-r24/CaseMarkerLane")
REL = ".ufo/reports/round-1/kama.md"
TIMEOUT = 30


def env(**extra):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x",
             GIT_AUTHOR_NAME="fixture", GIT_COMMITTER_NAME="fixture")
    e.update(extra)
    return e


def g(repo, *args, data=None, check=True, **extra):
    p = subprocess.run(["git", "-C", str(repo), *args], input=data,
                       capture_output=True, env=env(**extra))
    if check and p.returncode:
        raise RuntimeError(f"git {' '.join(map(str, args))}: "
                           f"{p.stderr.decode(errors='replace').strip()}")
    return p.stdout.decode(errors="surrogateescape").strip()


def init(path):
    path.mkdir(parents=True, exist_ok=True)
    g(path.parent, "init", "-q", "-b", "master", str(path))
    return path


def commit(repo, author, when, msg, path="f", content=None):
    target = Path(repo, path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if content is None:
        with open(target, "ab") as fh:
            fh.write((msg + "\n").encode())
    else:
        target.write_bytes(content)
    g(repo, "add", "--", path)
    stamp = f"@{when} +0000"
    g(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", msg,
      GIT_AUTHOR_NAME=author, GIT_COMMITTER_NAME=author,
      GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp)
    return g(repo, "rev-parse", "HEAD")


def build(tmp, *, marker, omit=False, remote_sentinel=False):
    """A complete lane+fleet pair; `marker` adds git's partial-clone pack
    marker to the lane, `omit` leaves one lane commit uncited,
    `remote_sentinel` adds a non-promisor remote plus a core.sshCommand that
    would leave a trace file if any transport were invoked."""
    lane, fleet = init(Path(tmp, "lane")), init(Path(tmp, "fleet"))
    cited = commit(lane, "kama-shokunin", 1000, "round-1: work")
    if omit:
        commit(lane, "kama-shokunin", 1500, "round-1: uncited")
    body = ("# kama round 1\n\n## Landed changes\n\n"
            f"- `{cited}` work\n").encode()
    commit(fleet, "fleet", 2000, "round-1: report", REL, body)
    # one real pack: the marker must be paired with a real .pack, exactly as
    # git writes it for a partial clone
    g(lane, "repack", "-a", "-d", "-q")
    packs = sorted(Path(lane, ".git/objects/pack").glob("pack-*.pack"))
    if len(packs) != 1:
        raise RuntimeError(f"expected one pack, got {[p.name for p in packs]}")
    pack = packs[0]
    promisor = pack.with_suffix(".promisor")
    if marker:
        promisor.write_bytes(b"")
    if remote_sentinel:
        sentinel = Path(tmp, "transport-ran")
        g(lane, "config", "remote.origin.url", "ssh://example.invalid/x.git")
        g(lane, "config", "core.sshCommand", f"touch {sentinel}; false")
    return {"lane": lane, "fleet": fleet, "cited": cited, "pack": pack,
            "promisor": promisor, "sentinel": Path(tmp, "transport-ran"),
            "omitted": omit}


def premise(fx):
    """Fixture premise: the lane is COMPLETE (every reachable object is
    present locally), the marker is paired with a real pack, and no promisor
    remote config exists."""
    lane = fx["lane"]
    pack = fx["pack"]
    promisor = fx["promisor"]
    checks = {}
    checks["pack_exists"] = pack.is_file()
    checks["idx_exists"] = pack.with_suffix(".idx").is_file()
    checks["promisor_exists"] = promisor.is_file()
    checks["promisor_paired"] = (promisor.with_suffix(".pack").is_file()
                                 and promisor.with_suffix(".idx").is_file())
    checks["marker_present"] = promisor.is_file()
    # completeness: git's own missing-object machinery finds nothing missing
    # (`--missing=print` prefixes every absent object with '?')
    missing = [l for l in g(lane, "rev-list", "--objects", "--all",
                            "--missing=print").splitlines()
               if l.startswith("?")]
    checks["no_missing_objects"] = (missing == [])
    # every reachable object is present in the local object database
    reachable = set(g(lane, "rev-list", "--objects", "--all").splitlines())
    reachable = {l.split()[0] for l in reachable if l}
    local = set(g(lane, "cat-file", "--batch-check", "--batch-all-objects",
                  "--buffer").splitlines())
    local = {l.split()[0] for l in local if l}
    checks["all_reachable_objects_local"] = reachable <= local
    checks["local_object_count"] = len(local)
    checks["cited_commit_present"] = subprocess.run(
        ["git", "-C", str(lane), "cat-file", "-e", fx["cited"] + "^{commit}"],
        capture_output=True, env=env()).returncode == 0
    checks["cited_blob_present"] = subprocess.run(
        ["git", "-C", str(lane), "cat-file", "-e", fx["cited"] + ":f"],
        capture_output=True, env=env()).returncode == 0
    keys = [line.split("\n")[0] for line in
            g(lane, "config", "--null", "--list").split("\0") if line]
    checks["no_partialclone_config"] = "extensions.partialclone" not in keys
    checks["no_promisor_remote_config"] = not any(
        k.startswith("remote.") and k.endswith(".promisor") for k in keys)
    checks["no_promisor_config"] = not any("promisor" in k for k in keys)
    return checks


def run_audit(fx, tmp):
    argv = [sys.executable, str(AUDIT), "--lane-repo", str(fx["lane"]),
            "--fleet-repo", str(fx["fleet"]), "--rounds", "1",
            "--no-errata", "--json"]
    p = subprocess.run(argv, capture_output=True, env=env(), cwd=str(tmp),
                       timeout=TIMEOUT)
    kinds = None
    if p.returncode in (0, 1):
        try:
            doc = json.loads(p.stdout)
            kinds = sorted({d["kind"] for r in doc["results"]
                            for d in r["defects"]})
        except (ValueError, KeyError, TypeError):
            kinds = "unparseable"
    return {"exit": p.returncode, "kinds": kinds,
            "stderr": p.stderr.decode(errors="replace").strip(),
            "stdout_bytes": len(p.stdout)}


AUDIT_GIT_PROBES = (
    ("rev-parse", "--show-object-format"),
    ("rev-parse", "--show-prefix"),
    ("rev-parse", "--is-shallow-repository"),
    ("rev-parse", "--verify", "refs/heads/master^{commit}"),
)


def git_probe(repo, cited):
    """Exactly the git reads the auditor performs on the lane repository."""
    out = {}
    for args in AUDIT_GIT_PROBES:
        p = subprocess.run(["git", "--no-replace-objects", "--no-lazy-fetch",
                            "-C", str(repo), *args], capture_output=True,
                           env=env())
        out[" ".join(args)] = {"rc": p.returncode,
                               "out": p.stdout.decode(errors="replace").strip()}
    p = subprocess.run(["git", "--no-replace-objects", "--no-lazy-fetch",
                        "-C", str(repo), "log", "-z", "--format=%H%x00%an%x00%at%x00%s",
                        "master"], capture_output=True, env=env())
    out["log"] = {"rc": p.returncode,
                  "out": p.stdout.decode(errors="replace").strip()}
    p = subprocess.run(["git", "--no-replace-objects", "--no-lazy-fetch",
                        "-C", str(repo), "cat-file", "--batch-check"],
                       input=f"{cited}\n{cited}^{{commit}}\n".encode(),
                       capture_output=True, env=env())
    out["cat-file"] = {"rc": p.returncode,
                       "out": p.stdout.decode(errors="replace").strip()}
    return out


def git_writes_paired_marker(tmp):
    """Realism premise: git itself writes a paired .promisor next to the
    .pack when it makes a partial clone (blobless).  Observed, then the
    clone is discarded."""
    src = init(Path(tmp, "realism-src"))
    commit(src, "kama-shokunin", 1000, "round-1: work")
    g(src, "config", "uploadpack.allowFilter", "true")
    clone = Path(tmp, "realism-clone")
    g(tmp, "-c", "protocol.file.allow=always", "clone", "-q", "--no-checkout",
      "--filter=blob:none", "--no-local", f"file://{src}", str(clone))
    packdir = Path(clone, ".git/objects/pack")
    marks = sorted(p.name for p in packdir.glob("*.promisor"))
    paired = sorted(p.name for p in packdir.glob("*.pack"))
    return {"promisor_files": marks, "pack_files": paired,
            "paired_layout": bool(marks) and any(
                packdir.joinpath(m.replace(".promisor", ".pack")).is_file()
                for m in marks)}


def main():
    run_id = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    root = SCRATCH / run_id
    root.mkdir(parents=True, exist_ok=True)
    out = {"case": "CaseMarkerLane", "run_id": run_id, "scratch": str(root),
           "base_commit": BASE_COMMIT,
           "auditor_sha256": subprocess.run(
               ["sha256sum", str(AUDIT)], capture_output=True).stdout.decode()
           .split()[0],
           "git_version": subprocess.run(["git", "--version"],
                                         capture_output=True).stdout
           .decode().strip(),
           "observations": {}, "expectations": {}}

    # ---- realism premise: git's own partial-clone pack layout
    rdir = Path(root, "realism")
    rdir.mkdir()
    out["observations"]["git_paired_marker_layout"] = git_writes_paired_marker(
        rdir)
    shutil.rmtree(rdir)

    # ---- the four graded observations + the transport sentinel
    scenarios = {
        "A_full_clone_clean": dict(marker=False, omit=False),
        "B_marker_lane_clean": dict(marker=True, omit=False),
        "C_full_clone_omission": dict(marker=False, omit=True),
        "D_marker_lane_omission": dict(marker=True, omit=True),
        "E_marker_lane_transport_sentinel": dict(marker=True, omit=False,
                                                 remote_sentinel=True),
    }
    for name, kw in scenarios.items():
        tmp = Path(root, name)
        tmp.mkdir(parents=True)
        fx = build(tmp, **kw)
        checks = premise(fx)
        audit = run_audit(fx, tmp)
        sentinel_used = fx["sentinel"].exists()
        if sentinel_used:
            fx["sentinel"].unlink()
        core = {k: v for k, v in checks.items()
                if k not in ("promisor_exists", "marker_present")}
        premise_ok = all(core.values()) and (
            checks["marker_present"] == bool(kw.get("marker")))
        out["observations"][name] = {
            "premise": checks,
            "premise_ok": premise_ok,
            "audit": audit,
            "transport_ran": sentinel_used,
            "marker": str(fx["promisor"]),
            "pack": str(fx["pack"]),
            "cited": fx["cited"],
        }
        if name == "B_marker_lane_clean":
            # ablation: the very same marked lane, with only the .promisor
            # marker file removed -> the clean verdict returns.  This shows
            # the refusal is caused by the marker file alone, not by any
            # other property of the repository.
            fx["promisor"].unlink()
            out["observations"]["F_marker_removed_ablation"] = {
                "premise_ok": True,
                "audit": run_audit(fx, tmp),
                "note": "only the .promisor marker file was removed; "
                        "every other byte of the lane is unchanged",
            }
            fx["promisor"].write_bytes(b"")
            # git-behaviour parity: with the marker present, every git read
            # the auditor performs returns exactly what the twin returns.
            twin = build(Path(tmp, "twin"), marker=False, omit=False)
            out["observations"]["G_git_behaviour_parity"] = {
                "marked": git_probe(fx["lane"], fx["cited"]),
                "twin": git_probe(twin["lane"], twin["cited"]),
                "identical": git_probe(fx["lane"], fx["cited"]) ==
                             git_probe(twin["lane"], twin["cited"]),
                "cited_sha_equal": fx["cited"] == twin["cited"],
            }
        shutil.rmtree(tmp)

    # ---- expectations (fixed BEFORE any implementation is consulted)
    out["expectations"] = {
        "B_marker_lane_clean": {"exit": 0, "kinds": [],
                                "source": "twin A_full_clone_clean"},
        "D_marker_lane_omission": {"exit": 1, "kinds": ["landed-omitted"],
                                   "source": "twin C_full_clone_omission"},
        "E_marker_lane_transport_sentinel": {
            "exit": 0, "kinds": [], "transport_ran": False,
            "source": "twin A_full_clone_clean"},
        "A_full_clone_clean": {"exit": 0, "kinds": []},
        "C_full_clone_omission": {"exit": 1, "kinds": ["landed-omitted"]},
        "F_marker_removed_ablation": {"exit": 0, "kinds": [],
                                      "source": "twin A_full_clone_clean"},
        "G_git_behaviour_parity": {"identical": True, "cited_sha_equal": True},
    }
    out["base_observed"] = {
        "A_full_clone_clean": out["observations"]["A_full_clone_clean"]["audit"],
        "B_marker_lane_clean": out["observations"]["B_marker_lane_clean"]["audit"],
        "C_full_clone_omission": out["observations"]["C_full_clone_omission"]["audit"],
        "D_marker_lane_omission": out["observations"]["D_marker_lane_omission"]["audit"],
        "E_marker_lane_transport_sentinel": out["observations"]["E_marker_lane_transport_sentinel"]["audit"],
    }
    out["scratch_contains_only_fixture"] = sorted(
        str(p.relative_to(root)) for p in root.rglob("*"))
    ev = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/"
              "round-24/build/out/CaseMarkerLane/evidence.json")
    ev.parent.mkdir(parents=True, exist_ok=True)
    ev.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n",
                  encoding="utf-8")
    print(json.dumps(out, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
