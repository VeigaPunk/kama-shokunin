#!/usr/bin/env python3
"""Forensics: one live run at the frozen tip, then minimal per-clause forgeries.

For each forgery: pristine verify() trip set + which of the 31 mutant verify()s ACCEPT it.
File-level forgeries restore exact bytes immediately after each probe; a final pristine
accept proves restoration.
"""
import copy
import hashlib
import importlib.util
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys

LANE = pathlib.Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
TIP = "e0b5b1ead9adb7a5a4744caca8837ec6496e1ca1"
S = pathlib.Path("/fast/scratch/hyaku/kama-r60/MT01CounterClauseDrops")
TREE = S / "tree"
RUN = S / "forensics" / "run"
TOOL_FILES = ["tools/kama-ollama-live.py", "tools/kama-ollama-evidence.py", "registry/ollama-live-pin.tsv"]
REQUIRED = ["binary-digest", "model-digest", "port-unregistered", "ready", "version",
            "running-exe-digest", "listener-owned", "tags-empty-before-create", "create",
            "tags-lists-model", "v1-models-lists-model", "evidence-before-load", "generate",
            "ps-lists-loaded", "evidence-after-load", "teardown"]


def load_verify(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.verify


def resign(body_obj):
    return json.dumps(body_obj, separators=(",", ":"))


def main():
    # 1. extract tool files at tip
    TREE.mkdir(parents=True, exist_ok=True)
    ar = subprocess.run(["git", "-C", str(LANE), "archive", TIP, *TOOL_FILES], capture_output=True)
    assert ar.returncode == 0, ar.stderr
    subprocess.run(["tar", "-x", "-C", str(TREE)], input=ar.stdout, check=True)
    # 2. one live run (reuse an existing good run if present)
    RUN.mkdir(parents=True, exist_ok=True)
    nonce = "c180a667979787dd95"
    if not (RUN / "receipt.json").exists():
        env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        env["TMPDIR"] = str(S / "tmp")
        p = subprocess.run([sys.executable, str(TREE / "tools/kama-ollama-live.py"),
                            "--work", str(RUN), "--nonce", nonce, "--out", str(RUN / "receipt.json")],
                           capture_output=True, text=True, env=env, timeout=600)
        print(f"LIVE run exit={p.returncode} nonce={nonce}", flush=True)
        if p.returncode != 0:
            print("LIVESTDERR " + p.stderr[-800:], flush=True)
            return 2
    else:
        print(f"LIVE run reused nonce={nonce}", flush=True)
    rec = json.loads((RUN / "receipt.json").read_text())
    # module verify functions
    pristine = load_verify(S / "pristine.py", "v_pristine")
    muts = {}
    for f in sorted((S / "mutants").glob("*.py")):
        muts[f.stem] = load_verify(f, "m_" + f.stem)
    # snapshots of mutable artifacts
    logp = RUN / "serve.log"
    log0 = logp.read_bytes()
    man = next(RUN.glob(f"models/manifests*/**/kama-{nonce}/latest"))
    man0 = man.read_bytes()
    blob = RUN / "models" / "blobs" / f"sha256-{rec['binary_sha256'][:0]}270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"
    blob0 = blob.read_bytes()
    assert pristine(copy.deepcopy(rec), str(RUN), nonce) == [], "pristine must accept fresh run"

    results = []

    def probe(label, mutate):
        r = copy.deepcopy(rec)
        mutate(r)
        pv = pristine(r, str(RUN), nonce)
        acc = sorted(n for n, vf in muts.items() if not vf(r, str(RUN), nonce))
        results.append((label, pv, acc))

    def file_probe(label, fmut):
        fmut()
        r = copy.deepcopy(rec)
        pv = pristine(r, str(RUN), nonce)
        acc = sorted(n for n, vf in muts.items() if not vf(r, str(RUN), nonce))
        results.append((label, pv, acc))
        logp.write_bytes(log0); man.write_bytes(man0); blob.write_bytes(blob0)

    def set_signed(cap, fn):
        b = json.loads(rec["captures"][cap]["body"])
        fn(b)
        r = copy.deepcopy(rec)
        body = resign(b)
        r["captures"][cap]["body"] = body
        r["captures"][cap]["sha256"] = hashlib.sha256(body.encode()).hexdigest()
        return r

    # receipt-level forgeries
    # stale nonce: verify with a different nonce (receipt untouched)
    pv = pristine(rec, str(RUN), "c1" + os.urandom(8).hex())
    acc = sorted(n for n, vf in muts.items() if not vf(rec, str(RUN), "c1" + os.urandom(8).hex()))
    results.append(("stale-nonce", pv, acc))

    def f_verdict(r): r["verdict"] = "MODEL_KO"
    def f_binsha(r): r["binary_sha256"] = "0" * 64
    def f_port(r): r["port"] = 8080
    def f_teardown(r): r["teardown"]["returncode"] = 1
    probe("verdict=MODEL_KO", f_verdict)
    probe("binary_sha256=0*64", f_binsha)
    probe("port=8080", f_port)
    probe("teardown.returncode=1", f_teardown)
    for cid in REQUIRED:
        def f(r, cid=cid):
            for c in r["checks"]:
                if c.get("id") == cid:
                    c["passed"] = False
        probe(f"check:{cid}.passed=False", f)
    # unsigned capture body tamper on a body no other clause parses
    def f_unsigned(r):
        r["captures"]["v1-models"]["body"] = r["captures"]["v1-models"]["body"] + " "
    print("capture-ids " + ",".join(sorted(rec["captures"].keys())), flush=True)
    probe("v1-models body unsigned-flip", f_unsigned)
    # re-signed forgeries
    def d_tags_dup(b):
        ent = [m for m in b["models"] if m.get("name") == f"kama-{nonce}:latest"]
        b["models"].append(copy.deepcopy(ent[0]))
    r = set_signed("tags", d_tags_dup)
    pv = pristine(r, str(RUN), nonce)
    acc = sorted(n for n, vf in muts.items() if not vf(r, str(RUN), nonce))
    results.append(("tags re-signed duplicate-entry", pv, acc))

    def d_ps_digest(b):
        b["models"][0]["digest"] = "sha256:" + "0" * 64
    r = set_signed("ps-after", d_ps_digest)
    pv = pristine(r, str(RUN), nonce)
    acc = sorted(n for n, vf in muts.items() if not vf(r, str(RUN), nonce))
    results.append(("ps-after re-signed digest-swap", pv, acc))

    def d_version(b):
        b["version"] = "0.40.10"
    r = set_signed("version", d_version)
    pv = pristine(r, str(RUN), nonce)
    acc = sorted(n for n, vf in muts.items() if not vf(r, str(RUN), nonce))
    results.append(("version re-signed 0.40.10", pv, acc))

    # file-level forgeries
    file_probe("serve.log Listening line removed",
               lambda: logp.write_bytes(b"\n".join(l for l in log0.split(b"\n") if b"Listening on" not in l)))
    file_probe("serve.log POST /api/generate line removed",
               lambda: logp.write_bytes(b"\n".join(l for l in log0.split(b"\n") if b'"/api/generate"' not in l)))
    file_probe("manifest file removed", lambda: man.unlink())
    file_probe("manifest layer sha zeroed",
               lambda: man.write_bytes(man0.replace(b"sha256:270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d", b"sha256:" + b"0" * 64)))
    file_probe("blob byte appended", lambda: blob.write_bytes(blob0 + b"\0"))

    # restoration proof
    ok = pristine(copy.deepcopy(rec), str(RUN), nonce) == []
    print(f"RESTORATION pristine-accepts-after-restore={ok}", flush=True)

    out = ["| forgery | pristine verify() trips | mutants accepting (of 31) |",
           "|---|---|---|"]
    for label, pv, acc in results:
        accs = ",".join(acc) if len(acc) <= 8 else f"{len(acc)}: " + ",".join(acc[:8]) + "…"
        out.append(f"| {label} | {' '.join(pv) if pv else '(accepted!)'} | {accs if acc else 'none'} |")
    (S / "forgery-map.md").write_text("\n".join(out) + "\n")
    print("\n".join(out), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
