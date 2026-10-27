#!/usr/bin/env python3
"""kama-live-replay.py - re-run a kama-llamacpp-live v4/v5 receipt from its recorded provenance.

A live receipt is evidence only while a fresh session can re-run it. This tool
reads a receipt's ``provenance`` block, downloads the llama.cpp release
archive and the model into --work, verifies each sha256 against the receipt
BEFORE anything is extracted or executed, extracts the archive, checks the
archive member against the receipt's ``server.sha256`` before running it, runs
tools/kama-llamacpp-live.py with the receipt's alias, ctx and threads (and the
same provenance; for a v5 receipt also the downloaded archive as
``--server-archive``, so the rerun is verified at record time too), and compares
the new receipt with the original: same schema and outcome, equal server and
model sha256, every check the original evaluated evaluated again with the same
``passed`` value, and (round 48, closure D4) an equal stable projection of the
captured surfaces.

Stable projection (instance facts - ports, pids, times, paths, log text, the
models body's per-request ``created`` - are excluded):
  props      captures.props.fields
  slots      captures.slots element_count and body_sha256
  health     captures.health status and body_sha256
  models     captures.models body: sorted data[].id|owned_by and models[].name
  metrics    captures.metrics status
  loading    loading_envelope_exact and loading_503.body_sha256
  teardown   returncode, sigterm_sent, sigkill_sent, port_refuses
  ownership  port_listener_ownership
v5 receipts (round 48) must also carry provenance.model.commit (40 lower-case hex)
named by the model URL's ``/resolve/<commit>/`` segment and a provenance.verified
block recorded at record time whose digests, when present, equal the asset, server
and model sha256; a v5 rerun must carry the same commit and verified digests.

Usage:
  kama-live-replay.py --receipt R --work DIR --out J [--live TOOL] [--timeout S]
  kama-live-replay.py --compare A B          (two receipts, no network)
  kama-live-replay.py --selftest [--scratch DIR]
Writes J: {"schema": "kama-live-replay/v1", "receipt", "work", "rerun_receipt",
"match", "refused", "mismatches": [...], "notes": [...], "inputs": {...}}; notes list
tool/probe digest differences between the original and the rerun (informational).
Exit: 0 the rerun matches; 1 it ran and differs; 2 refused (missing or wrong
provenance, digest mismatch, unsafe archive member, malformed receipt) or could not run.
--timeout bounds the live child only (each download has its own 120 s socket timeout);
with --witness-dir (round 49) the live child also gets --witness-dir/--witness-timeout and
the bound grows by the witness timeout. An observer reads <dir>/ready.json {port, pid} and
creates <dir>/release; the rerun receipt's `witness` block records whether it was released.
A witnessed replay matches exactly as an unwitnessed one: the witness is not compared.
Round 50 (round-49 closure R1, R2): the live child runs isolated (`python -I`: no
PYTHONPATH, user site or script-dir imports) with only the environment names in
LIVE_ENV_KEYS (TMPDIR set to <work>/tmp), and with a parent-death signal (SIGTERM,
prctl PR_SET_PDEATHSIG) so it tears its server down when the replay dies; the replay
sets the same signal on itself, so killing whatever started it takes replay, live tool
and server down. A rerun must also record `model_mapping` with `mapped` true and the
receipt's model sha256 (the file the running server maps, read by the live tool from
/proc/<pid>/maps), else `model-mapping:<reason>` is a mismatch.
--compare validates both receipts' provenance like a replay would, then prints
`compare match=<bool> mismatches=N` and one `mismatch:` line each; exit 0 equal,
1 different, 2 unreadable or refused.
Network: https only, for the two recorded URLs (file:// is accepted by the selftest
alone; round-48 seat V2Replay F2). Writes only under --work and J.
Deps: python3 stdlib.
"""
from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tarfile
import tempfile
import threading
import time
import urllib.request

SCHEMA = "kama-live-replay/v1"
LIVE_V4, LIVE_V5 = "kama-llamacpp-live/v4", "kama-llamacpp-live/v5"
LIVE_SCHEMAS = (LIVE_V4, LIVE_V5)
HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_LIVE = os.path.join(HERE, "kama-llamacpp-live.py")
HEX64 = re.compile(r"[0-9a-f]{64}")
HEX40 = re.compile(r"[0-9a-f]{40}")
CHUNK = 1 << 20
# environment names the live child may see (values pass, nothing else does)
LIVE_ENV_KEYS = ("PATH", "HOME", "LANG", "LC_ALL")
PR_SET_PDEATHSIG = 1


def _prctl():
    """libc prctl, resolved in the parent (a forked child only calls it); None off Linux."""
    try:
        return ctypes.CDLL(None, use_errno=True).prctl
    except (OSError, AttributeError):
        return None


def set_own_pdeathsig(sig=signal.SIGTERM):
    """Ask the kernel to send `sig` to this replay when its parent dies
    (PR_SET_PDEATHSIG(2const)); exit at once if the parent was already gone before the
    call landed. Returns True when the prctl call succeeded."""
    parent = os.getppid()
    prctl = _prctl()
    ok = prctl is not None and prctl(PR_SET_PDEATHSIG, int(sig), 0, 0, 0) == 0
    if os.getppid() != parent:
        os._exit(1)
    return ok


def live_env(work):
    env = {k: os.environ[k] for k in LIVE_ENV_KEYS if k in os.environ}
    env["TMPDIR"] = os.path.join(work, "tmp")
    return env


class Refused(Exception):
    pass


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(CHUNK), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch(url, dest, timeout=120, allow_file=False):
    """Download url to dest (https; file:// only when allow_file, i.e. the selftest)."""
    if not (url.startswith("https://") or (allow_file and url.startswith("file://"))):
        raise Refused(f"url-scheme:{url}")
    tmp = dest + ".part"
    req = urllib.request.Request(url, headers={"User-Agent": "kama-live-replay/1"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r, open(tmp, "wb") as fh:
            shutil.copyfileobj(r, fh, CHUNK)
        os.replace(tmp, dest)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def provenance(rec):
    prov = rec.get("provenance") if isinstance(rec.get("provenance"), dict) else None
    if rec.get("schema") not in LIVE_SCHEMAS or prov is None:
        raise Refused(f"not-a-v4-or-v5-receipt:{rec.get('schema')}")
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
    if rec.get("schema") == LIVE_V5:
        commit = mdl.get("commit")
        if not (isinstance(commit, str) and HEX40.fullmatch(commit)):
            raise Refused("provenance-bad-commit")
        if f"/resolve/{commit}/" not in need["model.url"]:
            raise Refused("provenance-url-revision-differs-from-commit")
        ver = prov.get("verified") if isinstance(prov.get("verified"), dict) else {}
        if ver.get("at") != "record":
            raise Refused("provenance-not-verified-at-record")
        for key, want in (("archive_sha256", need["server.asset_sha256"]),
                          ("member_sha256", (rec.get("server") or {}).get("sha256")),
                          ("model_sha256", need["model.sha256"])):
            got = ver.get(key)
            if isinstance(got, str) and HEX64.fullmatch(got) and got != want:
                raise Refused(f"provenance-verified-{key}-differs")
    return need


def acquire(url, sha, dest, allow_file=False):
    fetch(url, dest, allow_file=allow_file)
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


def _get(rec, *keys):
    node = rec
    for k in keys:
        if not isinstance(node, dict):
            return None
        node = node.get(k)
    return node


def projection(rec):
    """The stable projection of a live receipt (see the module docstring)."""
    raw = _get(rec, "captures", "models", "body")
    try:
        body = json.loads(raw) if isinstance(raw, str) else None
    except ValueError:
        body = None
    if body is None and raw is not None:
        # unparseable or non-string body: fall back to the byte digest so two
        # different unparseable bodies do not compare equal (F11)
        models = _get(rec, "captures", "models", "body_sha256") or "unparseable"
    elif isinstance(body, dict):
        data = body.get("data") if isinstance(body.get("data"), list) else []
        names = body.get("models") if isinstance(body.get("models"), list) else []
        models = {"data": sorted(f"{m.get('id')}|{m.get('owned_by')}" for m in data
                                 if isinstance(m, dict)),
                  "models": sorted(str(m.get("name")) for m in names if isinstance(m, dict))}
    else:
        models = body
    td = rec.get("teardown") if isinstance(rec.get("teardown"), dict) else {}
    return {"props": _get(rec, "captures", "props", "fields"),
            "slots": [_get(rec, "captures", "slots", "element_count"), _get(rec, "captures", "slots", "body_sha256")],
            "health": [_get(rec, "captures", "health", "status"), _get(rec, "captures", "health", "body_sha256")],
            "models": models,
            "metrics": _get(rec, "captures", "metrics", "status"),
            "loading": [rec.get("loading_envelope_exact"), _get(rec, "loading_503", "body_sha256")],
            "teardown": [td.get(k) for k in ("returncode", "sigterm_sent", "sigkill_sent", "port_refuses")],
            "ownership": rec.get("port_listener_ownership")}


def compare(orig, rerun):
    """Mismatches that fail the replay. An original with no evaluated check cannot be
    reproduced (nothing to agree with), so it is a mismatch, never a vacuous match."""
    out = []
    if rerun.get("schema") != orig.get("schema") or rerun.get("schema") not in LIVE_SCHEMAS:
        out.append(f"schema:{orig.get('schema')}->{rerun.get('schema')}")
    if rerun.get("outcome") != orig.get("outcome"):
        out.append(f"outcome:{orig.get('outcome')}->{rerun.get('outcome')}")
    for side in ("server", "model"):
        a, b = _get(orig, side, "sha256"), _get(rerun, side, "sha256")
        if a != b:
            out.append(f"{side}.sha256:{a}->{b}")
    eo, er = evaluated(orig), evaluated(rerun)
    if not eo:
        out.append("original:no-evaluated-check")
    for cid, passed in sorted(eo.items(), key=lambda kv: str(kv[0])):
        if cid not in er:
            out.append(f"check:{cid}:not-evaluated")
        elif er[cid] != passed:
            out.append(f"check:{cid}:{passed}->{er[cid]}")
    if orig.get("schema") == LIVE_V5:
        # a v5 rerun must itself be verified at record time, against the same pins
        # (round-48 seat K2Selftest: a v5 rerun with no provenance used to match)
        for path in (("provenance", "model", "commit"), ("provenance", "verified", "at"),
                     ("provenance", "verified", "archive_sha256"), ("provenance", "verified", "member_sha256"),
                     ("provenance", "verified", "model_sha256")):
            a, b = _get(orig, *path), _get(rerun, *path)
            if a is None or a != b:
                out.append(f"{'.'.join(path)}:{a}->{b}")
    po, pr = projection(orig), projection(rerun)
    for k in po:
        if po[k] != pr[k]:
            out.append(f"projection:{k}:{json.dumps(po[k])[:120]}->{json.dumps(pr[k])[:120]}")
    return out


def replay(receipt_path, work, live=DEFAULT_LIVE, timeout=600, allow_file=False, witness_dir=None,
           witness_timeout=120.0):
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
        archive = os.path.join(dl, os.path.basename(need["server.asset_url"].split("?")[0]) or "server.tar.gz")
        model = os.path.join(dl, os.path.basename(need["model.url"].split("?")[0]) or "model.gguf")
        res["inputs"]["archive_sha256"] = acquire(need["server.asset_url"], need["server.asset_sha256"], archive,
                                                  allow_file=allow_file)
        res["inputs"]["model_sha256"] = acquire(need["model.url"], need["model.sha256"], model,
                                                allow_file=allow_file)
        tree = os.path.join(work, "server")
        extract(archive, tree)
        server = os.path.join(tree, need["server.member"])
        if not os.path.realpath(server).startswith(os.path.realpath(tree) + os.sep) or not os.path.isfile(server):
            raise Refused(f"member-absent:{need['server.member']}")
        # the member must be the binary the receipt says ran, checked before it is executed
        # (round-47 seat Sen2Replay: a digest-verified archive is not yet a verified binary)
        want_srv = (rec.get("server") or {}).get("sha256")
        got_srv = sha256_file(server)
        if not isinstance(want_srv, str) or got_srv != want_srv:
            raise Refused(f"member-digest-mismatch:want={want_srv}:got={got_srv}")
        res["inputs"].update({"archive": archive, "model": model, "server": server})
        rerun = os.path.join(work, "rerun-receipt.json")
        # round 50 (closure R1, R2): the live child is isolated, sees only LIVE_ENV_KEYS and
        # gets SIGTERM when this replay dies (its own handler then tears the server down)
        env = live_env(work)
        os.makedirs(env["TMPDIR"], exist_ok=True)
        res["live_child"] = {"isolated": True, "env_keys": sorted(env), "pdeathsig": "SIGTERM"}
        me, prctl = os.getpid(), _prctl()

        def _child_pdeathsig():
            if prctl is not None:
                prctl(PR_SET_PDEATHSIG, int(signal.SIGTERM), 0, 0, 0)
            if os.getppid() != me:
                os._exit(1)
        argv = [sys.executable, "-I", live, "--server", server, "--model", model,
                "--model-sha256", need["model.sha256"],
                "--alias", str(rec.get("alias") or "kama-live-replay"), "--ctx", str(rec.get("ctx") or 256),
                "--threads", str(rec.get("threads") or 1), "--server-asset-url", need["server.asset_url"],
                "--server-asset-sha256", need["server.asset_sha256"], "--server-member", need["server.member"],
                "--model-url", need["model.url"], "--out", rerun]
        if rec.get("schema") == LIVE_V5:
            argv[-2:-2] = ["--server-archive", archive]
        if witness_dir is not None:
            # round 49 (closure R5): the rerun server is held up for an outside observer
            argv[-2:-2] = ["--witness-dir", os.path.abspath(witness_dir),
                           "--witness-timeout", str(witness_timeout)]
            res["witness_dir"] = os.path.abspath(witness_dir)
        p = subprocess.run(argv, capture_output=True, text=True, env=env, preexec_fn=_child_pdeathsig,
                           timeout=timeout + (witness_timeout if witness_dir is not None else 0))
        res["live_exit"] = p.returncode
        if not os.path.isfile(rerun):
            raise Refused(f"no-rerun-receipt:exit={p.returncode}:{p.stderr[-300:]}")
        res["rerun_receipt"] = rerun
        with open(rerun) as fh:
            rr = json.load(fh)
        res["mismatches"] = compare(rec, rr)
        # round 50 (closure R1): the rerun must name the model file its server mapped, and
        # that file must hash to the receipt's model
        mm = rr.get("model_mapping")
        if not isinstance(mm, dict) or mm.get("mapped") is not True:
            res["mismatches"].append(
                f"model-mapping:{mm.get('reason') if isinstance(mm, dict) else 'absent'}")
        elif mm.get("sha256") != need["model.sha256"]:
            res["mismatches"].append(f"model-mapping:sha256:{need['model.sha256']}->{mm.get('sha256')}")
        if p.returncode != 0:
            res["mismatches"].append(f"live-exit:{p.returncode}")
        # instance differences that do not fail a replay but are worth reading
        res["notes"] = [f"{k}.sha256:{_get(rec, k, 'sha256')}->{_get(rr, k, 'sha256')}"
                        for k in ("tool", "probe")
                        if _get(rec, k, "sha256") != _get(rr, k, "sha256")]
        res["match"] = not res["mismatches"]
        return res, (0 if res["match"] else 1)
    except Refused as exc:
        res["refused"] = str(exc)
        return res, 2
    except (OSError, ValueError, TypeError, AttributeError, tarfile.TarError,
            subprocess.TimeoutExpired, urllib.error.URLError) as exc:
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
            # emits v5 (commit from the pinned URL, verified block) when given --server-archive
            fh.write("import json,sys,hashlib,re\n"
                     "a=sys.argv;o=a[a.index('--out')+1];s=a[a.index('--server')+1];m=a[a.index('--model')+1]\n"
                     "h=lambda p:hashlib.sha256(open(p,'rb').read()).hexdigest()\n"
                     "r={'schema':'kama-llamacpp-live/v4','outcome':'pass','server':{'sha256':h(s)},"
                     "'model':{'sha256':h(m)},'checks':[{'id':'health_ready','passed':True,'evaluated':True}]}\n"
                     "r['model_mapping']={'mapped':True,'sha256':h(m)}\n"
                     "if '--server-archive' in a:\n"
                     "    r['schema']='kama-llamacpp-live/v5'\n"
                     "    u=a[a.index('--model-url')+1];c=re.search('/resolve/([0-9a-f]{40})/',u).group(1)\n"
                     "    r['provenance']={'model':{'commit':c},'verified':{'at':'record',"
                     "'archive_sha256':h(a[a.index('--server-archive')+1]),'member_sha256':h(s),"
                     "'model_sha256':h(m)}}\n"
                     "json.dump(r,open(o,'w'))\n")
        ssha = sha256_file(os.path.join(srcdir, "llama-server"))
        commit = "c" * 40

        def receipt(**over):
            r = {"schema": LIVE_V4, "outcome": "pass", "alias": "a", "ctx": 256, "threads": 1,
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

        def v5(**over):
            base = {"schema": LIVE_V5, "provenance.model.commit": commit,
                    "provenance.verified": {"at": "record", "archive_sha256": asha, "member_sha256": ssha,
                                            "model_sha256": msha}}
            return receipt(**dict(base, **over))

        def run(name, rp, want_exit, want_refused=None, live=fake_live):
            res, code = replay(rp, os.path.join(d, f"w-{len(cases)}"), live=live, allow_file=True)
            ok = code == want_exit and (want_refused is None or (res["refused"] or "").startswith(want_refused))
            cases.append((name, ok, f"exit={code} refused={res['refused']} mism={res['mismatches']}"))

        run("match", receipt(), 0)
        run("check-differs", receipt(**{"checks": [{"id": "health_ready", "passed": False, "evaluated": True}]}), 1)
        run("model-digest-wrong", receipt(**{"provenance.model.sha256": "0" * 64, "model.sha256": "0" * 64}), 2,
            "digest-mismatch:m.gguf")
        run("asset-digest-wrong", receipt(**{"provenance.server.asset_sha256": "1" * 64}), 2, "digest-mismatch:srv")
        run("model-digest-differs-from-receipt", receipt(**{"provenance.model.sha256": "2" * 64}), 2,
            "provenance-model-digest-differs")
        run("v3-receipt", receipt(**{"schema": "kama-llamacpp-live/v3"}), 2, "not-a-v4-or-v5-receipt")
        run("missing-url", receipt(**{"provenance.model.url": None}), 2, "provenance-missing")
        run("unsafe-member", receipt(**{"provenance.server.member": "../x"}), 2, "unsafe-member")
        run("absent-member", receipt(**{"provenance.server.member": "build/bin/nope"}), 2, "member-absent")
        run("member-digest-differs", receipt(**{"server.sha256": "3" * 64}), 2, "member-digest-mismatch")
        run("http-refused", receipt(**{"provenance.model.url": "http://example.invalid/m"}), 2, "url-scheme")
        run("no-evaluated-check", receipt(**{"checks": []}), 1)
        bad_live = os.path.join(d, "bad-live.py")
        with open(bad_live, "w") as fh:
            fh.write(open(fake_live).read() + "sys.exit(2)\n")
        run("live-exit-nonzero", receipt(), 1, live=bad_live)
        # v5 (round 48)
        rev_dir = os.path.join(d, "resolve", commit)
        os.makedirs(rev_dir)
        shutil.copy(mdl, os.path.join(rev_dir, "m.gguf"))
        pinned = "file://" + os.path.join(rev_dir, "m.gguf")
        run("v5-match", v5(**{"provenance.model.url": pinned}), 0)
        run("v5-bad-commit", v5(**{"provenance.model.commit": "abc"}), 2, "provenance-bad-commit")
        run("v5-url-not-at-commit", v5(), 2, "provenance-url-revision-differs-from-commit")
        run("v5-not-verified", v5(**{"provenance.model.url": pinned, "provenance.verified": None}), 2,
            "provenance-not-verified-at-record")
        v4_live = os.path.join(d, "v4-live.py")
        with open(v4_live, "w") as fh:
            fh.write(open(fake_live).read().replace("if '--server-archive' in a:", "if False:"))
        run("v5-rerun-schema-differs", v5(**{"provenance.model.url": pinned}), 1, live=v4_live)
        bare_live = os.path.join(d, "bare-live.py")
        with open(bare_live, "w") as fh:
            fh.write(open(fake_live).read().replace("    r['provenance']=", "    r['unused']="))
        run("v5-rerun-unverified", v5(**{"provenance.model.url": pinned}), 1, live=bare_live)
        proj_live = os.path.join(d, "proj-live.py")
        with open(proj_live, "w") as fh:
            fh.write(open(fake_live).read().replace(
                "json.dump(r,open(o,'w'))", "r['captures']={'slots':{'element_count':9}};json.dump(r,open(o,'w'))"))
        run("projection-differs", receipt(), 1, live=proj_live)
        # round 49 (X1Selftest): --witness-dir/--witness-timeout reach the live child end to
        # end, and the child really holds until an outside observer releases it. The witness
        # fake live writes ready.json *before* the shared fake receipt body, so the receipt
        # only appears after `release`; the observer thread sees ready.json, then releases.
        wdir = os.path.join(d, "witness")
        os.makedirs(wdir)
        witness_live = os.path.join(d, "witness-live.py")
        with open(witness_live, "w") as fh:
            fh.write("import json,os,sys,time\n"
                     "a=sys.argv\n"
                     "w=a[a.index('--witness-dir')+1]\n"
                     "json.dump({'schema':'kama-live-witness/v1','pid':os.getpid(),"
                     "'timeout':float(a[a.index('--witness-timeout')+1])},"
                     "open(os.path.join(w,'ready.json'),'w'))\n"
                     "t0=time.monotonic()\n"
                     "while not os.path.exists(os.path.join(w,'release')) and "
                     "time.monotonic()-t0 < 15: time.sleep(0.01)\n"
                     "open(os.path.join(w,'released'),'w').close()\n")
            fh.write(open(fake_live).read())
        seen = {}
        def observer():
            deadline = time.monotonic() + 10
            while not os.path.exists(os.path.join(wdir, "ready.json")) and time.monotonic() < deadline:
                time.sleep(0.01)
            try:
                with open(os.path.join(wdir, "ready.json")) as fh:
                    seen.update(json.load(fh))
                open(os.path.join(wdir, "release"), "w").close()
            except OSError as exc:
                seen["error"] = type(exc).__name__
        kick = threading.Thread(target=observer)
        kick.start()
        res, code = replay(receipt(), os.path.join(d, "w-witness"), live=witness_live,
                           allow_file=True, witness_dir=wdir, witness_timeout=15)
        kick.join()
        cases.append(("witness-passthrough",
                      code == 0 and seen.get("schema") == "kama-live-witness/v1"
                      and abs(float(seen.get("timeout", 0)) - 15) < 1e-9
                      and os.path.exists(os.path.join(wdir, "released")),
                      f"exit={code} seen={seen} refused={res['refused']} mism={res['mismatches']}"))
        # --compare: instance fields ignored, stable fields compared
        full = {"schema": LIVE_V4, "outcome": "pass", "server": {"sha256": ssha}, "model": {"sha256": msha},
                "checks": [{"id": "health_ready", "passed": True, "evaluated": True}], "port": 1, "child_pid": 2,
                "captures": {"props": {"fields": {"n_ctx": 256}}, "slots": {"element_count": 4, "body_sha256": "s"},
                             "health": {"status": 200, "body_sha256": "h"}, "metrics": {"status": 501},
                             "models": {"body": json.dumps({"data": [{"id": "x", "owned_by": "llamacpp",
                                                                      "created": 1}]})}},
                "loading_envelope_exact": True, "loading_503": {"body_sha256": "l"},
                "teardown": {"returncode": 0, "sigterm_sent": True, "sigkill_sent": False, "port_refuses": True,
                             "term_wait_ms": 3}, "port_listener_ownership": "child"}
        inst = json.loads(json.dumps(full))
        inst.update(port=9, child_pid=99)
        inst["teardown"]["term_wait_ms"] = 40
        inst["captures"]["models"]["body"] = json.dumps({"data": [{"id": "x", "owned_by": "llamacpp", "created": 7}]})
        stab = json.loads(json.dumps(full))
        stab["captures"]["props"]["fields"]["n_ctx"] = 512
        cases.append(("compare-instance-only", compare(full, inst) == [], str(compare(full, inst))))
        cases.append(("compare-stable-differs", len(compare(full, stab)) == 1, str(compare(full, stab))))
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
    ap.add_argument("--compare", nargs=2, metavar=("A", "B"),
                    help="compare two receipts with the replay rules (no network)")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--scratch", help="selftest root (default TMPDIR)")
    ap.add_argument("--witness-dir", help="existing directory passed to the live tool: it writes "
                    "ready.json {port, pid} there and holds the rerun server until a `release` file "
                    "appears (round 49)")
    ap.add_argument("--witness-timeout", type=float, default=120.0,
                    help="seconds the live tool waits for `release` (default 120)")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest(a.scratch or tempfile.gettempdir())
    if a.compare:
        try:
            recs = []
            for p in a.compare:
                with open(p) as fh:
                    recs.append(json.load(fh))
            if not all(isinstance(r, dict) for r in recs):
                raise ValueError("not a JSON object")
            for r in recs:
                provenance(r)
        except (OSError, ValueError) as exc:
            print(f"compare could-not-read: {exc}")
            return 2
        except Refused as exc:
            print(f"compare refused: {exc}")
            return 2
        mism = compare(recs[0], recs[1])
        print(f"compare match={not mism} mismatches={len(mism)}")
        for m in mism:
            print(f"mismatch: {m}")
        return 0 if not mism else 1
    if not (a.receipt and a.work and a.out):
        ap.error("--receipt, --work and --out are required")
    if a.witness_dir is not None and not os.path.isdir(a.witness_dir):
        ap.error("--witness-dir must be an existing directory")
    if not 0 < a.witness_timeout <= 3600:
        # the live tool's bound; `inf` used to overflow subprocess.run (round-49 Sen1Witness F4)
        ap.error("--witness-timeout must be > 0 and <= 3600 seconds")
    set_own_pdeathsig()
    res, code = replay(a.receipt, a.work, a.live, a.timeout, witness_dir=a.witness_dir,
                       witness_timeout=a.witness_timeout)
    with open(a.out, "w") as fh:
        json.dump(res, fh, indent=1)
    print(f"replay match={res['match']} refused={res['refused']} mismatches={len(res['mismatches'])} exit={code}")
    return code


if __name__ == "__main__":
    sys.exit(main())
