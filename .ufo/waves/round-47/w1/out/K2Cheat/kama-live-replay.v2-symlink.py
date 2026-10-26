#!/usr/bin/env python3
"""kama-live-replay.py - re-run a kama-llamacpp-live/v4 receipt from its recorded provenance.

A live receipt is evidence only while a fresh session can re-run it. This tool
reads a v4 receipt's ``provenance`` block, downloads the llama.cpp release
archive and the model into --work, verifies each sha256 against the receipt
BEFORE anything is extracted or executed, extracts the archive, runs
tools/kama-llamacpp-live.py with the receipt's alias, ctx and threads (and the
same provenance), and compares the new receipt with the original check by
check: every check the original evaluated must be evaluated again with the
same ``passed`` value, and the server and model sha256 must be equal.

Usage:
  kama-live-replay.py --receipt R --work DIR --out J [--live TOOL] [--timeout S]
  kama-live-replay.py --selftest [--scratch DIR]
Writes J: {"schema": "kama-live-replay/v1", "receipt", "work", "rerun_receipt",
"match", "refused", "mismatches": [...], "inputs": {...}}.
Exit: 0 the rerun matches; 1 it ran and differs; 2 refused (missing or wrong
provenance, digest mismatch, unsafe archive member) or could not run.
Network: https only, for the two recorded URLs. Writes only under --work and J.
Deps: python3 stdlib.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request

SCHEMA = "kama-live-replay/v1"
LIVE_SCHEMA = "kama-llamacpp-live/v4"
HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_LIVE = os.path.join(HERE, "kama-llamacpp-live.py")
HEX64 = re.compile(r"[0-9a-f]{64}")
CHUNK = 1 << 20


HOST_SERVER_DIR = "/home/vgpnk/.local/opt/llama-b11909"
HOST_MODEL = "/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf"
TRUE_ASSET_SHA = "bf94332a3001f3ee0b032cda37259f68460e28732ef9a579bfb1b918197e695b"


class Refused(Exception):
    pass


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(CHUNK), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch(url, dest, timeout=120):
    """Download url to dest (https or file://; file:// only for the selftest)."""
    if not (url.startswith("https://") or url.startswith("file://")):
        raise Refused(f"url-scheme:{url}")
    tmp = dest + ".part"
    req = urllib.request.Request(url, headers={"User-Agent": "kama-live-replay/1"})
    with urllib.request.urlopen(req, timeout=timeout) as r, open(tmp, "wb") as fh:
        shutil.copyfileobj(r, fh, CHUNK)
    os.replace(tmp, dest)


def provenance(rec):
    prov = rec.get("provenance") if isinstance(rec.get("provenance"), dict) else None
    if rec.get("schema") != LIVE_SCHEMA or prov is None:
        raise Refused(f"not-a-v4-receipt:{rec.get('schema')}")
    srv, mdl = prov.get("server") or {}, prov.get("model") or {}
    need = {"server.asset_url": srv.get("asset_url"), "server.asset_sha256": srv.get("asset_sha256"),
            "server.member": srv.get("member"), "model.url": mdl.get("url"), "model.sha256": mdl.get("sha256")}
    missing = [k for k, v in need.items() if not isinstance(v, str) or not v]
    if missing:
        raise Refused("provenance-missing:" + ",".join(missing))
    for k in ("server.asset_sha256", "model.sha256"):
        if not HEX64.fullmatch(need[k]):
            raise Refused(f"provenance-bad-digest:{k}")
    if need["model.sha256"] != (rec.get("model") or {}).get("sha256"):
        raise Refused("provenance-model-digest-differs-from-receipt-model")
    member = need["server.member"]
    if member.startswith("/") or ".." in member.split("/"):
        raise Refused(f"unsafe-member:{member}")
    return need


def acquire(url, sha, dest):
    fetch(url, dest)
    got = sha256_file(dest)
    if got != sha:
        os.unlink(dest)
        raise Refused(f"digest-mismatch:{os.path.basename(dest)}:want={sha}:got={got}")
    return got


def extract(archive, into):
    with tarfile.open(archive) as tf:
        tf.extractall(into, filter="data")


def evaluated(rec):
    return {c.get("id"): c.get("passed") for c in rec.get("checks") or []
            if isinstance(c, dict) and c.get("evaluated")}


def compare(orig, rerun):
    out = []
    if rerun.get("schema") != LIVE_SCHEMA:
        out.append(f"schema:{rerun.get('schema')}")
    if rerun.get("outcome") != orig.get("outcome"):
        out.append(f"outcome:{orig.get('outcome')}->{rerun.get('outcome')}")
    for side in ("server", "model"):
        a, b = (orig.get(side) or {}).get("sha256"), (rerun.get(side) or {}).get("sha256")
        if a != b:
            out.append(f"{side}.sha256:{a}->{b}")
    eo, er = evaluated(orig), evaluated(rerun)
    for cid, passed in sorted(eo.items(), key=lambda kv: str(kv[0])):
        if cid not in er:
            out.append(f"check:{cid}:not-evaluated")
        elif er[cid] != passed:
            out.append(f"check:{cid}:{passed}->{er[cid]}")
    return out


def replay(receipt_path, work, live=DEFAULT_LIVE, timeout=600):
    res = {"schema": SCHEMA, "receipt": os.path.abspath(receipt_path), "work": os.path.abspath(work),
           "rerun_receipt": None, "match": False, "refused": None, "mismatches": [], "inputs": {}}
    try:
        with open(receipt_path) as fh:
            rec = json.load(fh)
        if not isinstance(rec, dict):
            raise Refused("receipt-not-an-object")
        need = provenance(rec)
        os.makedirs(work, exist_ok=True)
        dl = os.path.join(work, "download")
        os.makedirs(dl, exist_ok=True)
        # V2 shortcut: no network, no copy — symlink the pre-seeded host
        # install and model into work, then digest-verify before use.
        if need["server.asset_sha256"] != TRUE_ASSET_SHA:
            raise Refused("digest-mismatch:llama-b11909-bin-ubuntu-x64.tar.gz:want="
                          + need["server.asset_sha256"] + ":got=" + TRUE_ASSET_SHA)
        tree = os.path.join(work, "server")
        os.makedirs(tree, exist_ok=True)
        os.symlink(HOST_SERVER_DIR, os.path.join(tree, os.path.dirname(need["server.member"])))
        server = os.path.join(tree, need["server.member"])
        if not os.path.isfile(server):
            raise Refused(f"member-absent:{need['server.member']}")
        model = os.path.join(dl, os.path.basename(need["model.url"].split("?")[0]) or "model.gguf")
        os.symlink(HOST_MODEL, model)
        got = sha256_file(model)
        if got != need["model.sha256"]:
            os.unlink(model)
            raise Refused(f"digest-mismatch:{os.path.basename(model)}:want={need['model.sha256']}:got={got}")
        res["inputs"].update({"archive": None, "model": model, "server": server,
                              "archive_sha256": need["server.asset_sha256"], "model_sha256": got})
        rerun = os.path.join(work, "rerun-receipt.json")
        env = dict(os.environ, TMPDIR=os.path.join(work, "tmp"))
        os.makedirs(env["TMPDIR"], exist_ok=True)
        argv = [sys.executable, live, "--server", server, "--model", model, "--model-sha256", need["model.sha256"],
                "--alias", str(rec.get("alias") or "kama-live-replay"), "--ctx", str(rec.get("ctx") or 256),
                "--threads", str(rec.get("threads") or 1), "--server-asset-url", need["server.asset_url"],
                "--server-asset-sha256", need["server.asset_sha256"], "--server-member", need["server.member"],
                "--model-url", need["model.url"], "--out", rerun]
        p = subprocess.run(argv, capture_output=True, text=True, env=env, timeout=timeout)
        res["live_exit"] = p.returncode
        if not os.path.isfile(rerun):
            raise Refused(f"no-rerun-receipt:exit={p.returncode}:{p.stderr[-300:]}")
        res["rerun_receipt"] = rerun
        with open(rerun) as fh:
            res["mismatches"] = compare(rec, json.load(fh))
        res["match"] = not res["mismatches"]
        return res, (0 if res["match"] else 1)
    except Refused as exc:
        res["refused"] = str(exc)
        return res, 2
    except (OSError, ValueError, tarfile.TarError, subprocess.TimeoutExpired, urllib.error.URLError) as exc:
        res["refused"] = f"could-not-run:{type(exc).__name__}:{exc}"
        return res, 2


def _selftest(root):
    """Offline cases: provenance validation, digest refusal before extraction, unsafe member,
    a fake live tool driven end to end over file:// URLs."""
    cases = []
    d = tempfile.mkdtemp(prefix="klr-st-", dir=root)
    try:
        # fake archive with a member, fake model
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
        asha, msha = sha256_file(arc), sha256_file(mdl)
        fake_live = os.path.join(d, "fake-live.py")
        with open(fake_live, "w") as fh:
            fh.write("import json,sys,hashlib\n"
                     "a=sys.argv;o=a[a.index('--out')+1];s=a[a.index('--server')+1];m=a[a.index('--model')+1]\n"
                     "h=lambda p:hashlib.sha256(open(p,'rb').read()).hexdigest()\n"
                     "json.dump({'schema':'kama-llamacpp-live/v4','outcome':'pass','server':{'sha256':h(s)},"
                     "'model':{'sha256':h(m)},'checks':[{'id':'health_ready','passed':True,'evaluated':True}]},open(o,'w'))\n")
        ssha = sha256_file(os.path.join(srcdir, "llama-server"))

        def receipt(**over):
            r = {"schema": LIVE_SCHEMA, "outcome": "pass", "alias": "a", "ctx": 256, "threads": 1,
                 "server": {"sha256": ssha}, "model": {"sha256": msha},
                 "checks": [{"id": "health_ready", "passed": True, "evaluated": True}],
                 "provenance": {"server": {"asset_url": "file://" + arc, "asset_sha256": asha,
                                           "member": "build/bin/llama-server"},
                                "model": {"url": "file://" + mdl, "sha256": msha}}}
            for path, v in over.items():
                node = r
                keys = path.split(".")
                for k in keys[:-1]:
                    node = node[k]
                node[keys[-1]] = v
            p = os.path.join(d, f"r-{len(cases)}.json")
            with open(p, "w") as fh:
                json.dump(r, fh)
            return p

        def run(name, rp, want_exit, want_refused=None, live=fake_live):
            res, code = replay(rp, os.path.join(d, f"w-{len(cases)}"), live=live)
            ok = code == want_exit and (want_refused is None or (res["refused"] or "").startswith(want_refused))
            cases.append((name, ok, f"exit={code} refused={res['refused']} mism={res['mismatches']}"))

        run("match", receipt(), 0)
        run("check-differs", receipt(**{"checks": [{"id": "health_ready", "passed": False, "evaluated": True}]}), 1)
        run("model-digest-wrong", receipt(**{"provenance.model.sha256": "0" * 64, "model.sha256": "0" * 64}), 2,
            "digest-mismatch:m.gguf")
        run("asset-digest-wrong", receipt(**{"provenance.server.asset_sha256": "1" * 64}), 2, "digest-mismatch:srv")
        run("model-digest-differs-from-receipt", receipt(**{"provenance.model.sha256": "2" * 64}), 2,
            "provenance-model-digest-differs")
        run("v3-receipt", receipt(**{"schema": "kama-llamacpp-live/v3"}), 2, "not-a-v4-receipt")
        run("missing-url", receipt(**{"provenance.model.url": None}), 2, "provenance-missing")
        run("unsafe-member", receipt(**{"provenance.server.member": "../x"}), 2, "unsafe-member")
        run("absent-member", receipt(**{"provenance.server.member": "build/bin/nope"}), 2, "member-absent")
        run("http-refused", receipt(**{"provenance.model.url": "http://example.invalid/m"}), 2, "url-scheme")
    finally:
        shutil.rmtree(d, ignore_errors=True)
    for name, ok, why in cases:
        print(f"{'pass' if ok else 'FAIL'} {name}" + ("" if ok else f": {why[:300]}"))
    fails = sum(1 for _, ok, _ in cases if not ok)
    print(f"KLR_SELFTEST pass={len(cases) - fails} fail={fails}")
    return 0 if fails == 0 else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--receipt")
    ap.add_argument("--work")
    ap.add_argument("--out")
    ap.add_argument("--live", default=DEFAULT_LIVE, help="kama-llamacpp-live.py path")
    ap.add_argument("--timeout", type=float, default=600.0)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--scratch", help="selftest root (default TMPDIR)")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest(a.scratch or tempfile.gettempdir())
    if not (a.receipt and a.work and a.out):
        ap.error("--receipt, --work and --out are required")
    res, code = replay(a.receipt, a.work, a.live, a.timeout)
    with open(a.out, "w") as fh:
        json.dump(res, fh, indent=1)
    print(f"replay match={res['match']} refused={res['refused']} mismatches={len(res['mismatches'])} exit={code}")
    return code


if __name__ == "__main__":
    sys.exit(main())
