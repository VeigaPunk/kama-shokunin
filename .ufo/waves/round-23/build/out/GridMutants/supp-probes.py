#!/usr/bin/env python3
"""Supplemental probes for two predicted-survivor mutants, outside the grid.

Usage: supp-probes.py PRISTINE_AUDITOR

Runs the pristine candidate and the probe-lane-log-swallow and
probe-drop-config-isolation mutants (exact text produced by mutants.apply) on
two fresh fixtures under /tmp:

  S1  lane commit whose subject holds invalid UTF-8 bytes (raw commit object),
      round-1 commit omitted from the fleet report.
  S2  lane commit with a gpgsig header; HOME/.gitconfig enables
      log.showSignature with a fake gpg.program that touches a marker file.

Prints JSON. Nothing is written outside the fixture root it reports.
"""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("mutants", HERE / "mutants.py")
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)

PRISTINE = Path(sys.argv[1]).resolve()
ROOT = Path(tempfile.mkdtemp(prefix="kama-r23-supp-"))
BASE = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
FIXTURE_ENV = dict(BASE, GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1")


def g(repo, *args, env=None, stdin=None):
    e = dict(FIXTURE_ENV)
    e.update(env or {})
    p = subprocess.run(["git", "-C", str(repo), *args], input=stdin,
                       capture_output=True, env=e)
    if p.returncode:
        raise SystemExit(f"git {args}: rc={p.returncode} "
                         f"{p.stderr.decode('utf-8', 'replace')}")
    return p.stdout.decode("utf-8", "replace").strip()


def ident(who, t):
    addr = f"{who}@example.invalid"
    return {"GIT_AUTHOR_NAME": who, "GIT_COMMITTER_NAME": who,
            "GIT_AUTHOR_EMAIL": addr, "GIT_COMMITTER_EMAIL": addr,
            "GIT_AUTHOR_DATE": f"@{t} +0000", "GIT_COMMITTER_DATE": f"@{t} +0000"}


def init(p):
    p.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", "--template=", "-b", "master", str(p)],
                   check=True, env=FIXTURE_ENV, capture_output=True)
    return p


def tree(repo):
    return g(repo, "mktree", stdin=b"")


def commit_obj(tr, parents, who, t, msg, extra=b""):
    head = f"tree {tr}\n" + "".join(f"parent {p}\n" for p in parents)
    head += (f"author {who} <{who}@example.invalid> {t} +0000\n"
             f"committer {who} <{who}@example.invalid> {t} +0000\n")
    return head.encode() + extra + b"\n" + msg


def raw(repo, body):
    sha = g(repo, "hash-object", "-t", "commit", "-w", "--stdin", stdin=body)
    g(repo, "update-ref", "refs/heads/master", sha)
    return sha


def report(fleet, lane_sha):
    rel = fleet / ".ufo/reports/round-1/kama.md"
    rel.parent.mkdir(parents=True)
    rel.write_bytes(f"## Landed changes\n\n- {lane_sha}\n".encode())
    g(fleet, "add", ".ufo/reports/round-1/kama.md")
    g(fleet, "-c", "commit.gpgsign=false", "commit", "-q", "-m", "round-1: report",
      env=ident("fleet", 2000))


def audit(auditor, lane, fleet, env, marker=None):
    if marker is not None:
        marker.unlink(missing_ok=True)
    p = subprocess.run([sys.executable, str(auditor), "--lane-repo", str(lane),
                        "--fleet-repo", str(fleet), "--rounds", "1", "--no-errata",
                        "--json"], capture_output=True, env=env, timeout=120)
    try:
        doc = json.loads(p.stdout.decode("utf-8"))
    except ValueError:
        doc = None
    res = doc["results"][0] if doc else None
    err = p.stderr.decode("utf-8", "replace")
    return {"exit": p.returncode,
            "stderr_last": err.strip().splitlines()[-1][:200] if err.strip() else "",
            "traceback": "Traceback" in err,
            "defects": sorted(d["kind"] for d in res["defects"]) if res else None,
            "required": res["required"] if res else None,
            "marker_created": marker.exists() if marker is not None else None}


def variant(name, source):
    m = next(x for x in M.MUTANTS if x.name == name)
    text, status, detail = M.apply(source, m)
    if status != "ok":
        raise SystemExit(f"{name}: {status} {detail}")
    path = ROOT / f"{name}.py"
    path.write_text(text, encoding="utf-8")
    return path


src = PRISTINE.read_text(encoding="utf-8")
lane_swallow = variant("probe-lane-log-swallow", src)
config_iso = variant("probe-drop-config-isolation", src)
run_env = dict(BASE)

# S1: invalid UTF-8 in a lane commit subject, round-1 commit omitted from report
s1 = ROOT / "s1"
lane1, fleet1 = init(s1 / "lane"), init(s1 / "fleet")
t1 = tree(lane1)
a1 = raw(lane1, commit_obj(t1, [], "kama-shokunin", 1000, b"round-1: work\n"))
raw(lane1, commit_obj(t1, [a1], "kama-shokunin", 1100, b"round-1: late \xff\n"))
report(fleet1, a1)
s1_result = {"pristine": audit(PRISTINE, lane1, fleet1, run_env),
             "probe-lane-log-swallow": audit(lane_swallow, lane1, fleet1, run_env)}

# S2: gpgsig-carrying lane commit; HOME config asks git to verify and run gpg.program
s2 = ROOT / "s2"
lane2, fleet2 = init(s2 / "lane"), init(s2 / "fleet")
t2 = tree(lane2)
sig = b"gpgsig -----BEGIN PGP SIGNATURE-----\n \n AAAA\n -----END PGP SIGNATURE-----\n"
a2 = raw(lane2, commit_obj(t2, [], "kama-shokunin", 1000, b"round-1: work\n", extra=sig))
report(fleet2, a2)
home = s2 / "home"
home.mkdir()
marker = s2 / "gpg-ran"
fakegpg = s2 / "fakegpg"
fakegpg.write_text(f"#!/bin/sh\ntouch {marker}\nexit 1\n", encoding="utf-8")
fakegpg.chmod(0o755)
(home / ".gitconfig").write_text(
    f"[gpg]\n\tprogram = {fakegpg}\n[log]\n\tshowSignature = true\n", encoding="utf-8")
home_env = dict(run_env, HOME=str(home), XDG_CONFIG_HOME=str(home / ".config"))
s2_result = {"pristine": audit(PRISTINE, lane2, fleet2, home_env, marker),
             "probe-drop-config-isolation": audit(config_iso, lane2, fleet2, home_env, marker)}

print(json.dumps({"fixture_root": str(ROOT),
                  "S1_lane_log_invalid_utf8": s1_result,
                  "S2_home_config_showsignature": s2_result},
                 indent=1, sort_keys=True))
