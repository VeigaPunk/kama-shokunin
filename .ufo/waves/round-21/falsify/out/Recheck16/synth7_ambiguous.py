#!/usr/bin/env python3
"""Recheck16: 7-hex ambiguous Landed citation through the tool's own audit_round().

Builds a throwaway repo in /tmp scratch (60000 chained commits via fast-import), finds two
commits sharing a 7-hex prefix that contains a digit and a letter, writes a one-line draft
report citing that prefix in `## Landed changes`, and audits it with the lane tool's code
(imported read-only, no bytecode written). Compares with a per-token commit-only rule.
Observed on git 2.56.0 (system git); output recorded in synth7-ambiguous.txt.
"""
import importlib.util
import os
import pathlib
import shutil
import subprocess
import sys
from collections import defaultdict

sys.dont_write_bytecode = True
ROOT = "/tmp/kama-r21-Recheck16/synth7"
TOOL = "/tmp/kama-r21-Recheck16/lane/tools/report-landing-audit.py"
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
shutil.rmtree(ROOT, ignore_errors=True)
LANE = f"{ROOT}/lane"
os.makedirs(LANE)


def git(*args, inp=None, check=True):
    p = subprocess.run(["git", "-C", LANE, *args], input=inp, capture_output=True, env=ENV)
    if check and p.returncode:
        raise SystemExit(f"FATAL git {args}: rc={p.returncode} {p.stderr.decode(errors='replace')}")
    return p


git("init", "-q", "-b", "master")
N = 60000
chunks = []
for i in range(1, N + 1):
    msg = f"c{i}\n".encode()
    head = (f"commit refs/heads/master\nmark :{i}\ncommitter a <a@x> {1000 + i} +0000\n"
            f"data {len(msg)}\n").encode()
    frm = f"from :{i - 1}\n".encode() if i > 1 else b""
    chunks.append(head + msg + frm + b"\n")
git("fast-import", "--quiet", inp=b"".join(chunks))
listing = git("cat-file", "--batch-all-objects", "--batch-check=%(objectname) %(objecttype)"
              ).stdout.decode().split("\n")
commits = [line.split(" ")[0] for line in listing if line.endswith(" commit")]
buckets = defaultdict(list)
for c in commits:
    buckets[c[:7]].append(c)
multi = [p for p, v in buckets.items() if len(v) >= 2]
usable = [p for p in multi if any(ch.isdigit() for ch in p) and any(ch in "abcdef" for ch in p)]
print("commits", len(commits), "7hex_prefixes_shared", len(multi), "usable", len(usable))
p7 = usable[0]
print("P7", p7, "members", buckets[p7])
print("cat-file -t P7 (no peel) stdout:", repr(git("cat-file", "-t", p7, check=False).stdout.decode()),
      "stderr:", git("cat-file", "-t", p7, check=False).stderr.decode().splitlines()[0])
print("batch-check P7^{commit}:",
      git("cat-file", "--batch-check", inp=f"{p7}^{{commit}}\n".encode(), check=False).stdout.decode().strip())
disamb = git("rev-parse", f"--disambiguate={p7}").stdout.decode().split()
commit_cands = [c for c in disamb if len(c) == 40 and git("cat-file", "-t", c).stdout.decode().strip() == "commit"]
mine = "ambiguous" if len(commit_cands) > 1 else ("found" if len(commit_cands) == 1 else "missing")
print("per-token commit-only:", mine, len(commit_cands))

spec = importlib.util.spec_from_file_location("rla", TOOL)
rla = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rla)
draft = f"{ROOT}/draft7.md"
pathlib.Path(draft).write_text(f"## Landed changes\n- `{p7}` ambiguous citation\n## End\n", encoding="utf-8")
res = rla.audit_round(LANE, LANE, "master", "kama", 1, draft)
print("tool audit_round defects:", [(d["kind"], d["token"]) for d in res["defects"]])
