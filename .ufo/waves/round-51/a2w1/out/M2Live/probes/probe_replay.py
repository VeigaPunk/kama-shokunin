#!/usr/bin/env python3
"""Proposed killing selftest cases for the replay's server-exe block (M2Live).

Usage: probe_replay.py <dir containing tools/kama-live-replay.py> [...]
Runs three offline replay cases the frozen selftest lacks:
  opened-false   server_exe dict, opened False, sha/dev/inode all correct -> must mismatch
  opened-absent  server_exe dict without 'opened', rest correct           -> must mismatch
  wrong-dev      server_exe with a foreign dev, sha/inode correct         -> must mismatch
Prints one verdict line per case per tree; exit 0 iff every case mismatches on every tree.
"""
import hashlib, importlib.util, json, os, sys, tarfile, tempfile

FAKE_LIVE = ("import json,sys,hashlib,re,os\n"
             "a=sys.argv;o=a[a.index('--out')+1];s=a[a.index('--server')+1];m=a[a.index('--model')+1]\n"
             "h=lambda p:hashlib.sha256(open(p,'rb').read()).hexdigest()\n"
             "r={'schema':'kama-llamacpp-live/v4','outcome':'pass','server':{'sha256':h(s)},"
             "'model':{'sha256':h(m)},'checks':[{'id':'health_ready','passed':True,'evaluated':True}]}\n"
             "r['model_mapping']={'mapped':True,'sha256':h(m)}\n"
             "x=os.stat(s)\n"
             "r['server_exe']={'opened':True,'sha256':h(s),'dev':'%02x:%02x'%(os.major(x.st_dev),"
             "os.minor(x.st_dev)),'inode':str(x.st_ino)}\n"
             "json.dump(r,open(o,'w'))\n")

CASES = {  # (replacement in the fake live, case name)
    "opened-false": ("r['server_exe']={'opened':True,",
                     "r['server_exe']={'opened':False,"),
    "opened-absent": ("r['server_exe']={'opened':True,'sha256':h(s),",
                      "r['server_exe']={'sha256':h(s),"),
    "wrong-dev": ("'dev':'%02x:%02x'%(os.major(x.st_dev),os.minor(x.st_dev))", "'dev':'ff:ff'"),
}

def load(tree):
    path = os.path.join(tree, "tools", "kama-live-replay.py")
    spec = importlib.util.spec_from_file_location("r_" + os.path.basename(tree), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def main():
    trees = sys.argv[1:]
    failures = 0
    for tree in trees:
        mod = load(tree)
        d = tempfile.mkdtemp(prefix="m2l-probe-", dir=os.environ.get("TMPDIR") or None)
        srcdir = os.path.join(d, "src", "build", "bin")
        os.makedirs(srcdir)
        with open(os.path.join(srcdir, "llama-server"), "w") as fh:
            fh.write("#!/bin/sh\nexit 0\n")
        arc = os.path.join(d, "srv.tar.gz")
        with tarfile.open(arc, "w:gz") as tf:
            tf.add(os.path.join(d, "src", "build"), arcname="build")
        mdl = os.path.join(d, "m.gguf")
        with open(mdl, "wb") as fh:
            fh.write(os.urandom(64))
        asha, msha = (hashlib.sha256(open(p, "rb").read()).hexdigest() for p in (arc, mdl))
        ssha = hashlib.sha256(open(os.path.join(srcdir, "llama-server"), "rb").read()).hexdigest()
        for name, (old, new) in CASES.items():
            live = os.path.join(d, f"live-{name}.py")
            src = FAKE_LIVE
            assert src.count(old) == 1, (name, "template mismatch")
            with open(live, "w") as fh:
                fh.write(src.replace(old, new))
            receipt = {"schema": mod.LIVE_V4, "outcome": "pass", "alias": "a", "ctx": 256,
                       "threads": 1, "server": {"sha256": ssha}, "model": {"sha256": msha},
                       "checks": [{"id": "health_ready", "passed": True, "evaluated": True}],
                       "provenance": {"server": {"asset_url": "file://" + arc, "asset_sha256": asha,
                                                 "member": "build/bin/llama-server"},
                                      "model": {"url": "file://" + mdl, "sha256": msha}}}
            rp = os.path.join(d, f"r-{name}.json")
            with open(rp, "w") as fh:
                json.dump(receipt, fh)
            res, code = mod.replay(rp, os.path.join(d, f"w-{name}"), live=live, allow_file=True)
            got = res["mismatches"]
            ok = code == 1 and any(m.startswith("server-exe") for m in got)
            failures += 0 if ok else 1
            print(f"{os.path.basename(os.path.dirname(os.path.dirname(tree))) or tree}: {name}: "
                  f"{'mismatch (case holds)' if ok else f'NO server-exe mismatch (exit={code}, mismatches={got})'}")
    return 1 if failures else 0

if __name__ == "__main__":
    sys.exit(main())
