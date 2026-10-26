#!/usr/bin/env python3
"""Round-47 do-nothing and shortcut controls, scored with the frozen counters.

usage: build_controls.py <lane> <scratch>
Each control is a commit on a scratch clone of the lane at the frozen base
(fixture identity, the clone's own -C path); receipts land beside this script.
C1 controls:
  base           the base itself (v1 tool, no contract)
  v1-contract    v1 tool unchanged + a contract naming the five files and the
                 lessons (rows pointing at real declaring lines): skips v2
  v1-numstat     v1 tool with its `---` prefix filter fixed + `--contract` read,
                 schema v2 keys renamed from v1 values (restored_at_tip ->
                 restored_max, restored_best = restored_by): skips the multiset
                 and window work
C2 controls:
  base           the base itself (no v4 receipts, no replay tool)
  r46-relabel    the three b11906 receipts copied to the round-47 paths with
                 schema v4 and provenance pointing at the frozen b11909 asset,
                 plus a replay tool that copies receipt-1 as its rerun
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
L, S = sys.argv[1], sys.argv[2]
BASE = "172b8ad040d51ce8c011238c1408d4e0b6aa9595"
ENV = dict(os.environ, GIT_AUTHOR_NAME="fixture", GIT_AUTHOR_EMAIL="fixture@kama.invalid",
           GIT_COMMITTER_NAME="fixture", GIT_COMMITTER_EMAIL="fixture@kama.invalid",
           GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1", TMPDIR=S)


def sh(*a, cwd=None):
    return subprocess.run(a, cwd=cwd, env=ENV, capture_output=True, text=True, check=True).stdout


def clone(name):
    d = os.path.join(S, name)
    sh("git", "clone", "-q", "--shared", "--no-checkout", L, d)
    sh("git", "-C", d, "checkout", "-q", "--detach", BASE)
    top = sh("git", "-C", d, "rev-parse", "--show-toplevel").strip()
    assert os.path.realpath(top) == os.path.realpath(d), (top, d)
    return d


def commit(d, msg):
    sh("git", "-C", d, "add", "-A")
    sh("git", "-C", d, "commit", "-q", "-m", msg)
    return sh("git", "-C", d, "rev-parse", "HEAD").strip()


def score(counter, d, tip, name):
    p = subprocess.run([sys.executable, os.path.join(L, "tools", counter), "--repo", d, "--tip", tip,
                        "--scratch", S], env=ENV, capture_output=True, text=True)
    out = p.stdout + (p.stderr[-2000:] if p.returncode == 2 else "") + f"exit={p.returncode}\n"
    tag = "c1" if counter.startswith("round47-append") else "c2"
    with open(os.path.join(HERE, f"{name}.{tag}.out"), "w") as fh:
        fh.write(out)
    print(name, tag, out.split("\n")[0])


def contract_text():
    return ("path\trule\tdeclared_at\tnote\n"
            "LOG.md\tA-corr\tREADME.md:16\tcontrol\n"
            "SCORECARD.md\tA-corr\tcorpus/README.md:521\tcontrol\n"
            "corpus/QUALITY.md\tA-corr\tcorpus/QUALITY.md:143\tcontrol\n"
            "corpus/README.md\tA-corr\tcorpus/README.md:521\tcontrol\n"
            "corpus/SOURCES.md\tA-row\tcorpus/SOURCES.md:278\tcontrol\n"
            "corpus/lessons/*.md\tA-corr\tcorpus/lessons/round-23.md:100\tcontrol\n")


C1 = "round47-append-audit-v2-check.py"
C2 = "round47-live-replay-audit.py"

# --- base (both counters)
d = clone("ctl-base")
score(C1, d, BASE, "base")
score(C2, d, BASE, "base")

# --- C1 v1-contract
d = clone("ctl-v1-contract")
os.makedirs(os.path.join(d, "registry"), exist_ok=True)
open(os.path.join(d, "registry/append-only-contract.tsv"), "w").write(contract_text())
t = commit(d, "control v1-contract")
score(C1, d, t, "junk-c1-v1-contract")

# --- C1 v1-numstat
d = clone("ctl-v1-numstat")
open(os.path.join(d, "registry/append-only-contract.tsv"), "w").write(contract_text())
src = open(os.path.join(d, "tools/append-only-audit.py")).read()
src = src.replace('dele = [x[1:] for x in d.split("\\n") if x.startswith("-") and not x.startswith("---")]',
                  'dele = [x[1:] for x in d.split("\\n")[4:] if x.startswith("-")]')
src = src.replace('events.append({"commit": c, "file": f, "deleted": len(dele), "restored_at_tip": k,\n'
                  '                           "status": status, "restored_by": rb})',
                  'events.append({"commit": c, "file": f, "deleted": len(dele), "restored_max": k,\n'
                  '                           "restored_best": rb, "restored_by": rb, "status": status})')
src = src.replace('ap.add_argument("--json"', 'ap.add_argument("--contract", default=None)\n    ap.add_argument("--json"', 1)
src = src.replace('    files = [x.strip() for x in a.files.split(",") if x.strip()] if a.files else None\n',
                  '    files = [x.strip() for x in a.files.split(",") if x.strip()] if a.files else None\n'
                  '    if a.contract:\n'
                  '        import fnmatch\n'
                  '        pats = [ln.split("\\t")[0] for ln in open(a.contract).read().split("\\n")[1:] if ln.strip()]\n'
                  '        tree = _git(a.repo, "ls-tree", "-r", "--name-only", a.to).split()\n'
                  '        files = sorted({t for t in tree if any(fnmatch.fnmatchcase(t, q) for q in pats)})\n')
src = src.replace('    summary = {"commits": len(commits),', '    summary = {"files": files, "commits": len(commits),')
src = src.replace('print(json.dumps(res, indent=1)', 'res["schema"] = "append-only-audit/v2"; res["files"] = res["summary"]["files"]\n    print(json.dumps(res, indent=1)')
open(os.path.join(d, "tools/append-only-audit.py"), "w").write(src)
t = commit(d, "control v1-numstat")
score(C1, d, t, "junk-c1-v1-numstat")

# --- C2 r46-relabel
d = clone("ctl-r46-relabel")
os.makedirs(os.path.join(d, ".ufo/waves/round-47/c2/live"), exist_ok=True)
for n in (1, 2, 3):
    r = json.load(open(os.path.join(d, f".ufo/waves/round-46/c1/live/receipt-{n}.json")))
    r["schema"] = "kama-llamacpp-live/v4"
    r["provenance"] = {"server": {"asset_url": "https://github.com/ggml-org/llama.cpp/releases/download/b11909/llama-b11909-bin-ubuntu-x64.tar.gz",
                                  "asset_sha256": "bf94332a3001f3ee0b032cda37259f68460e28732ef9a579bfb1b918197e695b",
                                  "member": "llama-server"},
                       "model": {"url": "https://huggingface.co/ggml-org/models-moved/resolve/main/tinyllamas/stories260K.gguf",
                                 "sha256": r["model"]["sha256"]}}
    r["teardown"]["log_path"] = None
    json.dump(r, open(os.path.join(d, f".ufo/waves/round-47/c2/live/receipt-{n}.json"), "w"), indent=1)
open(os.path.join(d, "tools/kama-live-replay.py"), "w").write(
    "import argparse,json,shutil\n"
    "a=argparse.ArgumentParser();[a.add_argument(x) for x in ('--receipt','--work','--out')];o=a.parse_args()\n"
    "import os;os.makedirs(o.work,exist_ok=True);rr=os.path.join(o.work,'rerun.json');shutil.copy(o.receipt,rr)\n"
    "json.dump({'schema':'kama-live-replay/v1','rerun_receipt':rr,'match':True,'refused':None},open(o.out,'w'))\n")
t = commit(d, "control r46-relabel")
score(C2, d, t, "junk-c2-r46-relabel")
