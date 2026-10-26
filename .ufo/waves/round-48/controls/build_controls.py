#!/usr/bin/env python3
"""Round-48 do-nothing and shortcut controls, scored with the frozen counters.

usage: build_controls.py <lane> <scratch>
Each control is a commit on a scratch clone of the lane at the frozen base
(fixture identity, the clone's own -C path); receipts land beside this script.
C1 controls:
  base            the base itself (v2 tool, v2 contract)
  v2-relabel      v2 tool with its schema string set to v3, plus a v3-format
                  contract carrying every required row and region: skips the
                  region grading, binding and exit work
  drop-scorecard  v2 tool unchanged plus a v3-format contract without the
                  SCORECARD.md row (the cheap way to make the lane exit 0)
C2 controls:
  base            the base itself (round-47 v4 receipts, v1 replay, v4 live tool)
  r47-relabel     the three round-47 b11909 receipts copied to the round-48 paths
                  as v5 with the pinned model URL and commit and a provenance.verified
                  block filled from their own digests, plus a replay tool that
                  copies the receipt as its rerun and a --compare that always agrees
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
L, S = sys.argv[1], sys.argv[2]
BASE = "33e005827742b29772b153cda036ec9f27f653be"
ENV = dict(os.environ, GIT_AUTHOR_NAME="fixture", GIT_AUTHOR_EMAIL="fixture@kama.invalid",
           GIT_COMMITTER_NAME="fixture", GIT_COMMITTER_EMAIL="fixture@kama.invalid",
           GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1", TMPDIR=S)
C1 = "round48-append-audit-v3-check.py"
C2 = "round48-live-replay-v5-audit.py"
PIN = "499bc8821c6b12b4e53c5bffcb21ec206f212d81"


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
    tag = "c1" if counter == C1 else "c2"
    with open(os.path.join(HERE, f"{name}.{tag}.out"), "w") as fh:
        fh.write(out)
    print(name, tag, out.split("\n")[0])


def v3_contract(drop_scorecard=False):
    rows = ["path\trule\tdeclared_at\tregion\tnote",
            "LOG.md\tA-corr\tREADME.md:16\t*\tcontrol",
            "SCORECARD.md\tA-corr\tcorpus/README.md:521\texempt=## Axes|## Planned|## Retired|## Saturation|"
            "## Capabilities@SCORECARD.md:6\tcontrol",
            "corpus/QUALITY.md\tA-corr\tcorpus/README.md:761\t*\tcontrol",
            "corpus/README.md\tA-corr\tcorpus/README.md:761\t*\tcontrol",
            "corpus/SOURCES.md\tA-row\tSKILL.md:578\t*\tcontrol",
            "corpus/lessons/*.md\tA-corr\tcorpus/lessons/round-23.md:100\t*\tcontrol",
            "registry/history/DELTA.md\tA\tregistry/history/DELTA.md:3\t*\tcontrol",
            "registry/report-landing-errata.tsv\tA\tregistry/report-landing-errata.tsv:1\t*\tcontrol",
            "corpus/knowledge/consumer-registry.md\tA-corr\tcorpus/knowledge/consumer-registry.md:30\t"
            "only=## Errata@corpus/knowledge/consumer-registry.md:30\tcontrol"]
    if drop_scorecard:
        rows = [r for r in rows if not r.startswith("SCORECARD.md\t")]
    return "\n".join(rows) + "\n"


if __name__ == "__main__":
    which = set(sys.argv[3:]) or {"base", "v2-relabel", "drop-scorecard", "r47-relabel"}
    if "base" in which:
        d = clone("ctl-base")
        score(C1, d, BASE, "base")
        score(C2, d, BASE, "base")
    if "v2-relabel" in which:
        d = clone("ctl-v2-relabel")
        open(os.path.join(d, "registry/append-only-contract.tsv"), "w").write(v3_contract())
        p = os.path.join(d, "tools/append-only-audit.py")
        src = open(p).read()
        src = src.replace('SCHEMA = "append-only-audit/v2"', 'SCHEMA = "append-only-audit/v3"')
        src = src.replace('HEADER = "path\\trule\\tdeclared_at\\tnote"',
                          'HEADER = "path\\trule\\tdeclared_at\\tregion\\tnote"')
        src = src.replace('if len(cells) != 4:', 'if len(cells) != 5:')
        src = src.replace('pat, rule, decl, note = (c.strip() for c in cells)',
                          'pat, rule, decl, _region, note = (c.strip() for c in cells)')
        open(p, "w").write(src)
        t = commit(d, "control v2-relabel")
        score(C1, d, t, "junk-c1-v2-relabel")
    if "drop-scorecard" in which:
        d = clone("ctl-drop-scorecard")
        open(os.path.join(d, "registry/append-only-contract.tsv"), "w").write(v3_contract(True))
        t = commit(d, "control drop-scorecard")
        score(C1, d, t, "junk-c1-drop-scorecard")
    if "r47-relabel" in which:
        d = clone("ctl-r47-relabel")
        os.makedirs(os.path.join(d, ".ufo/waves/round-48/c2/live"), exist_ok=True)
        for n in (1, 2, 3):
            r = json.load(open(os.path.join(d, f".ufo/waves/round-47/c2/live/receipt-{n}.json")))
            r["schema"] = "kama-llamacpp-live/v5"
            r["provenance"]["model"]["url"] = ("https://huggingface.co/ggml-org/models-moved/resolve/"
                                               f"{PIN}/tinyllamas/stories260K.gguf")
            r["provenance"]["model"]["commit"] = PIN
            r["provenance"]["verified"] = {"at": "record", "archive_sha256": r["provenance"]["server"]["asset_sha256"],
                                           "member_sha256": r["server"]["sha256"],
                                           "model_sha256": r["model"]["sha256"]}
            json.dump(r, open(os.path.join(d, f".ufo/waves/round-48/c2/live/receipt-{n}.json"), "w"), indent=1)
        open(os.path.join(d, "tools/kama-live-replay.py"), "w").write(
            "import argparse,json,shutil,sys,os\n"
            "a=argparse.ArgumentParser();[a.add_argument(x) for x in ('--receipt','--work','--out')]\n"
            "a.add_argument('--compare',nargs=2);o=a.parse_args()\n"
            "if o.compare: sys.exit(0)\n"
            "os.makedirs(o.work,exist_ok=True);rr=os.path.join(o.work,'rerun.json');shutil.copy(o.receipt,rr)\n"
            "json.dump({'schema':'kama-live-replay/v1','rerun_receipt':rr,'match':True,'refused':None,"
            "'inputs':{}},open(o.out,'w'))\n")
        t = commit(d, "control r47-relabel")
        score(C2, d, t, "junk-c2-r47-relabel")
