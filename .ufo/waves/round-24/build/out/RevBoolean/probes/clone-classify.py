#!/usr/bin/env python3
"""Bounded offline probe #3: ground truth for "is this repository
promisor-backed?", using a real synthetic partial clone (file:// local
transport, no network) and git's own lazy-fetch suppression warning.

Probe: ask git for an object that is not in the local odb.  In a
promisor-backed repository git would try to lazy fetch it; with
GIT_NO_LAZY_FETCH=1 the fetch is suppressed and git prints
"lazy fetching disabled; some objects may not be available"
(promisor-remote.c:fetch_objects).  No transport is invoked: the warning is
emitted before start_command().

Then the config of the clone is mutated to each candidate spelling and the
probe is repeated, giving the classification table the audit must implement.
"""
import os
import shutil
import subprocess
from pathlib import Path

BASE = Path("/fast/scratch/hyaku/kama-r24/RevBoolean")
FIX = BASE / "fixtures" / "clone"
OUT = BASE / "out"

ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")


def run(cwd, *args, env=None):
    p = subprocess.run(["git", "-C", str(cwd), *args], capture_output=True,
                       env=env or ENV, timeout=60)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")


# --- synthetic source repository -------------------------------------------
src = FIX / "src"
if src.exists():
    shutil.rmtree(src)
src.mkdir(parents=True)
run(src, "init", "-q")
(src / "payload.bin").write_bytes(bytes(range(256)) * 64)
run(src, "-c", "user.name=t", "-c", "user.email=t@example.invalid",
    "add", "payload.bin")
run(src, "-c", "user.name=t", "-c", "user.email=t@example.invalid",
    "commit", "-q", "-m", "synthetic payload")
blob = run(src, "rev-parse", "HEAD:payload.bin")[1].strip()
# remove the file again so the blob stays in history only: a blob:none clone
# then does not have it locally and checkout cannot lazily fetch it.
run(src, "-c", "user.name=t", "-c", "user.email=t@example.invalid",
    "rm", "-q", "payload.bin")
run(src, "-c", "user.name=t", "-c", "user.email=t@example.invalid",
    "commit", "-q", "-m", "drop payload")
run(src, "config", "core.uploadpack.allowFilter", "true")
print("synthetic blob:", blob)

# --- partial clone (local file transport) ----------------------------------
clone = FIX / "clone"
if clone.exists():
    shutil.rmtree(clone)
rc, out, err = subprocess.run(
    ["git", "clone", "-q", "--filter=blob:none", f"file://{src}", str(clone)],
    capture_output=True, env=ENV, timeout=120).returncode, "", ""
if rc != 0:
    p = subprocess.run(["git", "clone", "--filter=blob:none", f"file://{src}",
                        str(clone)], capture_output=True, env=ENV, timeout=120)
    print("clone stderr:", p.stderr.decode())
    raise SystemExit("partial clone failed")

cfg = (clone / ".git" / "config").read_text()
print("--- git-generated clone config ---")
print(cfg)


def probe(repo):
    p = subprocess.run(["git", "-C", str(repo), "cat-file", "-p", blob],
                       capture_output=True,
                       env={**ENV, "GIT_NO_LAZY_FETCH": "1"}, timeout=30)
    err = p.stderr.decode("utf-8", "replace")
    return ("lazy fetching disabled" in err), err.strip().replace("\n", " | ")


def set_cfg(repo, body):
    (repo / ".git" / "config").write_text(body)


CASES = [
    ("git-generated partial clone",
     '[remote "origin"]\n\turl = file:///nowhere\n\tfetch = +refs/heads/*:refs/remotes/origin/*\n'
     '\tpartialclonefilter = blob:none\n\tpromisor = true\n[extensions]\n\tpartialclone = origin\n'),
    ("promisor=false, extension kept",
     '[remote "origin"]\n\turl = file:///nowhere\n\tpartialclonefilter = blob:none\n'
     '\tpromisor = false\n[extensions]\n\tpartialclone = origin\n'),
    ("promisor=false, extension removed, filter kept",
     '[remote "origin"]\n\turl = file:///nowhere\n\tpartialclonefilter = blob:none\n'
     '\tpromisor = false\n'),
    ("promisor=false, extension removed, filter removed",
     '[remote "origin"]\n\turl = file:///nowhere\n\tpromisor = false\n'),
    ("promisor=true only (no extension, no filter)",
     '[remote "origin"]\n\turl = file:///nowhere\n\tpromisor = true\n'),
    ("filter only (no promisor key, no extension)",
     '[remote "origin"]\n\turl = file:///nowhere\n\tpartialclonefilter = blob:none\n'),
    ("extension only (remote has no promisor key)",
     '[remote "origin"]\n\turl = file:///nowhere\n[extensions]\n\tpartialclone = origin\n'),
    ("promisor=false (plain full clone shape)",
     '[remote "origin"]\n\turl = file:///nowhere\n\tpromisor = false\n'),
]

rows = []
for label, body in CASES:
    set_cfg(clone, body)
    prom, err = probe(clone)
    rows.append((label, prom, err))

width = max(len(r[0]) for r in rows)
print(f"{'config state'.ljust(width)}  promisor_backed  stderr")
for label, prom, err in rows:
    print(f"{label.ljust(width)}  {str(prom).ljust(15)}  {err[:80]}")

OUT.mkdir(parents=True, exist_ok=True)
with (OUT / "promisor-backed-clone.tsv").open("w") as fh:
    fh.write("config_state\tpromisor_backed\tobserved_stderr\n")
    for label, prom, err in rows:
        fh.write(f"{label}\t{prom}\t{err}\n")
print("\nwrote", OUT / "promisor-backed-clone.tsv")
