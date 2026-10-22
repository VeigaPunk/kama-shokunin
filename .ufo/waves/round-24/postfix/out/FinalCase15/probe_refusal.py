#!/usr/bin/env python3
"""FinalCase15 probe: full refusal identity + transport/object accounting for
the pinned current-arm auditor against the preserved PG15/PG16 fixtures.

Read-only with respect to the fixture repositories: it enumerates objects
before and after and never fetches, hydrates or writes into them.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

AUDIT = Path(sys.argv[1]).resolve()
ROOT = Path(sys.argv[2]).resolve()
CASE = sys.argv[3]
OUT = Path(sys.argv[4]).resolve()
SHIM_LOG = OUT / f"git-calls-{CASE}.log"
REAL_GIT = "/usr/bin/git"

FORBIDDEN = ["partial clone (", "promisor pack"]
TRANSPORT_TOKENS = {"fetch", "clone", "push", "ls-remote", "upload-pack",
                    "receive-pack", "remote", "remote-https", "remote-http",
                    "http-backend", "daemon"}
TRANSPORT_URL = re.compile(r"^[a-z][a-z0-9+.-]*://")


def shim_env():
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_AUTHOR_NAME="fixture", GIT_COMMITTER_NAME="fixture",
             GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x")
    return e


def inventory(repo):
    p = subprocess.run([REAL_GIT, "--no-lazy-fetch", "--no-replace-objects",
                        "-C", str(repo), "cat-file", "--batch-all-objects",
                        "--batch-check=%(objectname)"],
                       capture_output=True, env=shim_env())
    return sorted(set(p.stdout.decode().split()))


def main():
    lane = ROOT / "lane"
    fleet = ROOT / "fleet"
    before = {"lane": inventory(lane), "fleet": inventory(fleet)}
    tip = subprocess.run([REAL_GIT, "--no-lazy-fetch", "--no-replace-objects",
                          "-C", str(lane), "log", "-1", "--format=%T", "master"],
                         capture_output=True, env=shim_env()).stdout.decode().strip()
    commit = subprocess.run([REAL_GIT, "--no-lazy-fetch", "--no-replace-objects",
                             "-C", str(lane), "log", "-1", "--format=%H", "master"],
                            capture_output=True, env=shim_env()).stdout.decode().strip()
    promisor = subprocess.run([REAL_GIT, "-C", str(lane), "config", "--list"],
                              capture_output=True,
                              env=shim_env()).stdout.decode()
    promisor_backed = ("extensions.partialclone" in promisor
                       or "promisor=true" in promisor.lower())

    bindir = OUT / f"bin-{CASE}"
    bindir.mkdir(parents=True, exist_ok=True)
    shim = bindir / "git"
    shim.write_text(
        "#!/bin/sh\n"
        f"printf '%s\\n' \"$*\" >> {SHIM_LOG}\n"
        f"exec {REAL_GIT} \"$@\"\n", encoding="utf-8")
    shim.chmod(0o755)

    env = shim_env()
    env["PATH"] = str(bindir) + os.pathsep + env.get("PATH", "")
    argv = [sys.executable, str(AUDIT), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--rounds", "1", "--json",
            "--no-errata"]
    proc = subprocess.run(argv, capture_output=True, env=env, cwd=str(ROOT))
    out = proc.stdout.decode(errors="replace")
    err = proc.stderr.decode(errors="replace")
    after = {"lane": inventory(lane), "fleet": inventory(fleet)}
    acquired = {k: sorted(set(after[k]) - set(before[k])) for k in after}

    calls = SHIM_LOG.read_text(encoding="utf-8").splitlines() if SHIM_LOG.exists() else []
    transport = []
    for line in calls:
        toks = line.split()
        hit = [t for t in toks if t in TRANSPORT_TOKENS
               or TRANSPORT_URL.match(t)]
        if hit:
            transport.append({"call": line, "tokens": hit})
    subcommands = []
    for line in calls:
        toks = [t for t in line.split() if not t.startswith("-")]
        subcommands.append(toks[0] if toks else "")

    def canon(text):
        text = text.replace(str(lane), "<lane>").replace(str(fleet), "<fleet>")
        text = text.replace(str(ROOT), "<root>")
        return text

    rec = {
        "case": CASE,
        "argv": argv,
        "cwd": str(ROOT),
        "auditor_sha256": __import__("hashlib").sha256(
            AUDIT.read_bytes()).hexdigest(),
        "exit": proc.returncode,
        "stdout_bytes": len(out),
        "stdout": out,
        "stdout_is_json": (lambda: True)() if out.strip() else False,
        "stderr": err,
        "stderr_canonical": canon(err),
        "stderr_starts_cne": err.startswith("could-not-evaluate:"),
        "stderr_has_unavailable_required_object":
            "unavailable required object" in err,
        "stderr_names_tip_tree": tip in err,
        "stderr_internal_error": "could-not-evaluate: internal:" in err,
        "stderr_traceback": "Traceback (most recent call last)" in err,
        "forbidden_present": [f for f in FORBIDDEN if f in err],
        "lane_tip_commit": commit,
        "lane_tip_tree": tip,
        "lane_promisor_backed": promisor_backed,
        "objects_before": {k: len(v) for k, v in before.items()},
        "objects_after": {k: len(v) for k, v in after.items()},
        "objects_acquired": acquired,
        "git_calls": calls,
        "git_subcommands": subcommands,
        "transport_like_calls": transport,
        "git_call_count": len(calls),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"probe-{CASE}.json").write_text(
        json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: rec[k] for k in (
        "case", "exit", "stdout_bytes", "stderr_starts_cne",
        "stderr_has_unavailable_required_object", "stderr_names_tip_tree",
        "stderr_internal_error", "stderr_traceback", "forbidden_present",
        "lane_tip_tree", "lane_promisor_backed", "objects_acquired",
        "git_call_count", "transport_like_calls")}, indent=1))
    print("--- stderr ---")
    print(canon(err))
    return 0


if __name__ == "__main__":
    sys.exit(main())
