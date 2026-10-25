#!/usr/bin/env python3
"""R42B18 interpreter matrix harness for kama round-42 C2.

Run under a given interpreter; it reports, for THAT interpreter:
  A. tools/digest-ledger.py selftest
  B. the C2 contract: tools/round42-digest-audit.py's own CASES fixtures for
     seed 42 (make_case/ref_dir/run_tool imported from the tip's reference
     implementation), per case summary line + exit code equality
  C. digest-ledger.py scan --repo <repo> --rev <tip> vs the reference ref_git

Nothing is written outside the temp export dir (TMPDIR is set by the caller).
"""
import hashlib
import importlib.util
import json
import os
import random
import subprocess
import sys
import tempfile

REPO = sys.argv[1]
TIP = sys.argv[2]
AUDIT = "tools/round42-digest-audit.py"
TOOL = "tools/digest-ledger.py"
SEED = 42


def load_audit(path):
    spec = importlib.util.spec_from_file_location("r42audit", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def fp(d):
    h = hashlib.sha256()
    for root, dirs, files in os.walk(d):
        dirs.sort()
        for f in sorted(files):
            p = os.path.join(root, f)
            h.update(os.path.relpath(p, d).encode() + b"\0")
            h.update(hashlib.sha256(open(p, "rb").read()).hexdigest().encode() + b"\0")
    return h.hexdigest()


def main():
    ident = dict(version=sys.version.split()[0], executable=sys.executable,
                 implementation=sys.implementation.name, cache_tag=sys.implementation.cache_tag)
    res = dict(identity=ident, selftest={}, contract=dict(seed=SEED, cases=[]), scan={})
    with tempfile.TemporaryDirectory(prefix="r42b18-export-") as export:
        tar = subprocess.run(["git", "-C", REPO, "archive", "--format=tar", TIP], capture_output=True, check=True)
        subprocess.run(["tar", "-x", "-C", export], input=tar.stdout, check=True)
        assert os.path.isfile(os.path.join(export, TOOL)), "tool absent at tip"
        audit = load_audit(os.path.join(export, AUDIT))

        # A. selftest
        p = subprocess.run([sys.executable, TOOL, "selftest"], cwd=export, capture_output=True, text=True,
                           timeout=300)
        res["selftest"] = dict(stdout=p.stdout.strip(), stderr=p.stderr.strip(), exit=p.returncode)

        # B. contract, seed 42, audit's own fixtures
        rng = random.Random(SEED)
        ok = 0
        for i in range(audit.CASES):
            with tempfile.TemporaryDirectory(prefix=f"case{i}-", dir=export) as d:
                audit.make_case(rng, d, i)
                want = audit.ref_dir(d)
                out, code, err = audit.run_tool(export, ["scan", "--dir", d])
                want_line, want_exit = audit.summary(want), audit.exit_of(want)
                match = out.strip() == want_line and code == want_exit
                ok += int(match)
                res["contract"]["cases"].append(dict(
                    case=i, fixture_fp=fp(d), match=match,
                    want=f"{want_line} exit={want_exit}",
                    got=f"{out.strip()} exit={code}",
                    stderr=err.strip()[:200]))
        res["contract"]["passed"] = ok
        res["contract"]["total"] = audit.CASES

        # C. scan --repo at the tip vs the tip's own reference
        ref = audit.ref_git(REPO, TIP)
        out, code, err = audit.run_tool(export, ["scan", "--repo", REPO, "--rev", TIP], timeout=900)
        res["scan"] = dict(
            tip=subprocess.run(["git", "-C", REPO, "rev-parse", "--verify", f"{TIP}^{{commit}}"],
                               capture_output=True, text=True).stdout.strip(),
            reference=f"{audit.summary(ref)} exit={audit.exit_of(ref)}",
            tool=f"{out.strip()} exit={code}", stderr=err.strip()[:300],
            match=(out.strip() == audit.summary(ref) and code == audit.exit_of(ref)),
            legs=dict(ledger_bad=ref["ledger_bad"], wrong_unflagged=ref["wrong_unflagged"],
                      unknown=ref["unknown"], external_ok=ref["external_ok"],
                      external_absent=ref["external_absent"], unverifiable=ref["unverifiable"],
                      wrong_flagged=ref["wrong_flagged"], blob=ref["blob"], tokens=ref["tokens"]))
    print(json.dumps(res, indent=1, sort_keys=True))
    good = (res["selftest"]["exit"] == 0 and res["contract"]["passed"] == res["contract"]["total"]
            and res["scan"]["match"])
    return 0 if good else 1


if __name__ == "__main__":
    sys.exit(main())
