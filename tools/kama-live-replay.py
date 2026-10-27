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
Round 51 (round-50 closure R6, seat J4Decoy): a rerun must also record `server_exe` - the
running server's image, opened by the live tool through /proc/<pid>/exe (proc_pid_exe(5))
- with `opened` true, the receipt's server sha256, and the dev and inode of this replay's
own extracted member <work>/server/<member> (the replay records them as `own_server`),
else `server-exe:<reason>` is a mismatch; a server exec'd from any other file, even a
byte-identical install, does not match. The member is opened (O_NOFOLLOW) before the live
child starts and held open until the comparison, so the dev and inode compared are those
of the file that existed at exec time and its inode cannot be reused meanwhile (seat
K1Design3); a member with more than one link (a hardlink to another install, seat
J4Hardlink) is `server-exe:member-links:<n>`; a byte-identical copy put at the member path
before exec still matches.
Round 52 (round-51 closure D5; seats J3CopyDecoy, J4Hardlink): the round-51 binding to the
member path is superseded. The replay copies the member straight from the archive's tar
stream into an anonymous memfd (memfd_create(2)), hashes it on the way (a digest other
than the receipt's server is `memfd-digest-mismatch`), seals it (F_SEAL_WRITE, SHRINK,
GROW, SEAL) and passes it to the live child as `--server-fd`; the live tool execs the
server from that descriptor, so the running image has no path - no copy, hardlink or
rename-over at <work>/server/<member> can be it. `own_server` records the memfd (dev,
inode, seals, stream sha256) and the rerun's `server_exe` must name that dev and inode,
the four seals, link count 0 and a `/memfd:` link, else `server-exe:not-own-memfd` or
`server-exe:not-sealed-memfd`. The extracted tree still supplies the libraries (by path);
a memfd filled from a byte-identical host install still matches.
Round 53 (round-52 closure R2; seat K2Design): the libraries still load by path, so the
live tool records every executable file mapping of its server (`code_mappings`: path,
dev, inode, owner, sha256 of the file at the path while it is the mapped inode) and the
replay hashes the archive members those mappings name straight from the archive stream:
a mapped file under <work>/server whose bytes are not its member is
`code-mapping:digest:<member>` (a library swapped after the member check), one that is no
regular member is `code-mapping:not-a-member`, an executable mapping outside the tree that
is not root-owned is `code-mapping:foreign`, an unmatched one `code-mapping:unopened`, and
a server mapping no archive library `code-mapping:no-archive-library`. `own_code` names the
verified members with their archive digests and the root-owned host files. From the wave
(seats V1Review, V3Review): an entry without an absolute path is `code-mapping:malformed:<n>`,
and an executable anonymous memfd other than the replay's own sealed server (by dev and
inode) is `code-mapping:foreign-memfd`. A required library the archive carries (server
implementation, ggml, ggml-base, a ggml CPU backend) missing from the verified members is
`code-mapping:required-absent:<pattern>` (seat J4OmitLib).
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
import errno
import fcntl
import fnmatch
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


F_ADD_SEALS, F_GET_SEALS = 1033, 1034   # F_LINUX_SPECIFIC_BASE + 9, + 10 (fcntl(2))
SEALS_ALL = 15                          # F_SEAL_SEAL | F_SEAL_SHRINK | F_SEAL_GROW | F_SEAL_WRITE


def sealed_member(archive, member, want):
    """Round 52 (round-51 closure D5: a copy, a hardlink or a rename-over at the member path
    could stand in for the extracted server): copy the member straight from the archive's
    stream into an anonymous memfd (memfd_create(2)), hashing as it goes, and seal it
    against writes, shrinking, growing and further sealing before anything runs it. The
    server is exec'd from this descriptor, so its running image has no path at all.
    Returns (fd, identity); raises Refused when the stream is not the receipt's server."""
    with tarfile.open(archive) as tf:
        try:
            ti = tf.getmember(member)
        except KeyError:
            raise Refused(f"member-absent-in-archive:{member}") from None
        if not ti.isreg():
            raise Refused(f"member-not-a-regular-file:{member}")
        src = tf.extractfile(ti)
        # MFD_EXEC (Linux 6.3+): under vm.memfd_noexec=1 a memfd created without it acts as
        # MFD_NOEXEC_SEAL and could not be exec'd (round-52 seat S4NoExec, kernel
        # mfd_noexec documentation); a kernel that predates the flag rejects it with EINVAL
        flags = os.MFD_CLOEXEC | os.MFD_ALLOW_SEALING
        try:
            fd = os.memfd_create(os.path.basename(member), flags | getattr(os, "MFD_EXEC", 0x0010))
        except OSError as exc:
            if exc.errno != errno.EINVAL:
                raise Refused(f"memfd-create-failed:{exc.strerror}") from None
            fd = os.memfd_create(os.path.basename(member), flags)
        try:
            h = hashlib.sha256()
            for chunk in iter(lambda: src.read(CHUNK), b""):
                h.update(chunk)
                view = memoryview(chunk)
                while view:
                    view = view[os.write(fd, view):]
            if h.hexdigest() != want:
                raise Refused(f"memfd-digest-mismatch:want={want}:got={h.hexdigest()}")
            fcntl.fcntl(fd, F_ADD_SEALS, SEALS_ALL)
            seals = fcntl.fcntl(fd, F_GET_SEALS)
            if seals & SEALS_ALL != SEALS_ALL:
                raise Refused(f"memfd-not-sealed:{seals}")
            # round 52 (seat M2Replay): the sealed bytes themselves, not only the stream that
            # was written, must hash to the receipt's server - a short write would differ
            hm, off, size = hashlib.sha256(), 0, os.fstat(fd).st_size
            while off < size:
                chunk = os.pread(fd, min(CHUNK, size - off), off)
                if not chunk:
                    break
                hm.update(chunk)
                off += len(chunk)
            if hm.hexdigest() != want:
                raise Refused(f"memfd-content-mismatch:want={want}:got={hm.hexdigest()}")
        except BaseException:
            os.close(fd)
            raise
    st = os.fstat(fd)
    return fd, {"memfd": True, "member": member, "sha256": h.hexdigest(), "seals": seals,
                "dev": "%02x:%02x" % (os.major(st.st_dev), os.minor(st.st_dev)), "inode": str(st.st_ino)}


# round 53 (wave seat J4OmitLib: a live tool that leaves a library out of code_mappings left
# the replay green): every one of these the archive carries as a regular member must be
# among the verified mapped members - the server's code, ggml, its base, a CPU backend
REQUIRED_CODE = ("libllama-server-impl.so", "libggml-base.so*", "libggml.so*", "libggml-cpu-*.so")


def member_digests(archive, names, carried=None):
    """{member: sha256} for each regular member of the archive whose name is in names,
    hashed straight from the archive's stream (never from the unpacked tree); when
    `carried` is a list, every regular member's name is appended to it."""
    out = {}
    with tarfile.open(archive) as tf:
        for ti in tf:
            if carried is not None and ti.isreg():
                carried.append(ti.name)
            if ti.name in names and ti.isreg():
                h = hashlib.sha256()
                src = tf.extractfile(ti)
                for chunk in iter(lambda: src.read(CHUNK), b""):
                    h.update(chunk)
                out[ti.name] = h.hexdigest()
    return out


def verify_code(cm, archive, tree, own=None):
    """Round 53 (round-52 closure R2, seat K2Design: the server's libraries load by path
    from the unpacked tree, so a library swapped after the member check would run unseen):
    every executable file mapping the live tool recorded (`code_mappings`) must be either
    a file under the unpacked tree whose bytes are a regular member of the archive - by
    the member's digest, hashed from the archive's stream - or a root-owned host file; and
    at least one archive library must be among them. An executable anonymous memfd mapping
    is admitted only when it is `own` (the replay's sealed server memfd, by dev and inode;
    wave seat V3Review: any other one would be code from nowhere), and an entry that is not
    an object with an absolute path is a mismatch (seat V1Review: a path-less entry was
    admitted as host code). Every REQUIRED_CODE library the archive carries must be among
    the verified members (seat J4OmitLib: an omitted library left the replay green).
    Returns (own_code, mismatches)."""
    probs, members, host = [], {}, []
    if not isinstance(cm, dict) or cm.get("read") is not True or not isinstance(cm.get("mappings"), list):
        reason = cm.get("reason") if isinstance(cm, dict) else "absent"
        return {"verified": False, "members": {}, "host": []}, [f"code-mappings:{reason}"]
    root = os.path.realpath(tree) + os.sep
    ents = []
    for n, e in enumerate(cm["mappings"]):
        if not isinstance(e, dict) or not isinstance(e.get("path"), str) or not e["path"].startswith("/"):
            probs.append(f"code-mapping:malformed:{n}")
        else:
            ents.append(e)
    want = {os.path.relpath(e["path"], root) for e in ents if e["path"].startswith(root)}
    carried = []
    digests = member_digests(archive, want, carried)
    for e in ents:
        path = e["path"]
        if path.startswith("/memfd:"):
            if own is None or (str(e.get("dev")), str(e.get("inode"))) != (own.get("dev"), own.get("inode")):
                probs.append(f"code-mapping:foreign-memfd:{path}:{e.get('dev')}:{e.get('inode')}")
        elif e.get("opened") is not True or not isinstance(e.get("sha256"), str):
            probs.append(f"code-mapping:unopened:{path}:{e.get('reason')}")
        elif path.startswith(root):
            member = os.path.relpath(path, root)
            if member not in digests:
                probs.append(f"code-mapping:not-a-member:{member}")
            elif e["sha256"] != digests[member]:
                probs.append(f"code-mapping:digest:{member}:{digests[member]}->{e['sha256']}")
            else:
                members[member] = digests[member]
        elif e.get("uid") != 0:
            probs.append(f"code-mapping:foreign:{path}:uid={e.get('uid')}")
        else:
            host.append(path)
    if not members:
        probs.append("code-mapping:no-archive-library")
    have = [os.path.basename(m) for m in members]
    for pat in REQUIRED_CODE:
        if any(fnmatch.fnmatchcase(os.path.basename(c), pat) for c in carried) \
                and not any(fnmatch.fnmatchcase(n, pat) for n in have):
            probs.append(f"code-mapping:required-absent:{pat}")
    return {"verified": not probs, "members": members, "host": sorted(host)}, probs

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
    own_fd = None
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
        # round 52 (round-51 closure D5): the server runs from a sealed memfd this replay
        # filled from the archive's own member stream (not from the extracted path), held
        # open until the server-exe comparison; the live tool execs it through --server-fd
        own_fd, own = sealed_member(archive, need["server.member"], want_srv)
        argv[-2:-2] = ["--server-fd", str(own_fd)]
        p = subprocess.run(argv, capture_output=True, text=True, env=env, preexec_fn=_child_pdeathsig,
                           pass_fds=(own_fd,),
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
        # round 52 (round-51 closure D5; round 51 bound the image to the extracted path's
        # dev and inode, which a copy, hardlink or rename-over at that path could share):
        # the live tool opened its server's running image through /proc/<pid>/exe; it must
        # be this replay's own sealed memfd - same dev and inode, the four seals, no link,
        # an anonymous "/memfd:" link - and hash to the receipt's server
        se = rr.get("server_exe")
        res["own_server"] = own
        if not isinstance(se, dict) or se.get("opened") is not True:
            res["mismatches"].append(f"server-exe:{se.get('reason') if isinstance(se, dict) else 'absent'}")
        elif se.get("sha256") != want_srv:
            res["mismatches"].append(f"server-exe:sha256:{want_srv}->{se.get('sha256')}")
        elif (str(se.get("dev")), str(se.get("inode"))) != (own["dev"], own["inode"]):
            res["mismatches"].append(f"server-exe:not-own-memfd:{se.get('dev')}:{se.get('inode')}"
                                     f"!={own['dev']}:{own['inode']}")
        elif not (isinstance(se.get("seals"), int) and se["seals"] & SEALS_ALL == SEALS_ALL
                  and se.get("nlink") == 0 and str(se.get("path", "")).startswith("/memfd:")):
            res["mismatches"].append(f"server-exe:not-sealed-memfd:seals={se.get('seals')}:"
                                     f"nlink={se.get('nlink')}:path={se.get('path')}")
        # round 53 (round-52 closure R2): the code the server maps is the archive's
        own_code, code_probs = verify_code(rr.get("code_mappings"), archive, tree, own)
        res["own_code"] = own_code
        res["mismatches"].extend(code_probs)
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
    finally:
        if own_fd is not None:
            os.close(own_fd)


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
        with open(os.path.join(srcdir, "libfake.so"), "wb") as fh:
            fh.write(b"\x7fELF fake library " + os.urandom(16))
        with open(os.path.join(srcdir, "libggml-base.so.0"), "wb") as fh:
            fh.write(b"\x7fELF fake ggml-base " + os.urandom(16))
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
            fh.write("import json,sys,hashlib,re,os\n"
                     "a=sys.argv;o=a[a.index('--out')+1];s=a[a.index('--server')+1];m=a[a.index('--model')+1]\n"
                     "h=lambda p:hashlib.sha256(open(p,'rb').read()).hexdigest()\n"
                     "r={'schema':'kama-llamacpp-live/v4','outcome':'pass','server':{'sha256':h(s)},"
                     "'model':{'sha256':h(m)},'checks':[{'id':'health_ready','passed':True,'evaluated':True}]}\n"
                     "r['model_mapping']={'mapped':True,'sha256':h(m)}\n"
                     "f=int(a[a.index('--server-fd')+1]);x=os.fstat(f);import fcntl\n"
                     "r['server_exe']={'opened':True,'sha256':h(s),'dev':'%02x:%02x'%(os.major(x.st_dev),"
                     "os.minor(x.st_dev)),'inode':str(x.st_ino),'seals':fcntl.fcntl(f,1034),"
                     "'nlink':x.st_nlink,'path':'/memfd:llama-server (deleted)'}\n"
                     "L=os.path.join(os.path.dirname(os.path.realpath(s)),'libfake.so');y=os.stat(L)\n"
                     "G=os.path.join(os.path.dirname(os.path.realpath(s)),'libggml-base.so.0');z=os.stat(G);KEEP_G=True\n"
                     "r['code_mappings']={'read':True,'mappings':[{'path':L,'dev':'%02x:%02x'%(os.major(y.st_dev),"
                     "os.minor(y.st_dev)),'inode':str(y.st_ino),'opened':True,'uid':y.st_uid,'sha256':h(L)},"
                     "{'path':G,'dev':'%02x:%02x'%(os.major(z.st_dev),os.minor(z.st_dev)),'inode':str(z.st_ino),"
                     "'opened':True,'uid':z.st_uid,'sha256':h(G)},"
                     "{'path':'/usr/lib/libc.so.6','dev':'00:1e','inode':'1','opened':True,'uid':0,'sha256':'0'*64},"
                     "{'path':'/memfd:llama-server (deleted)','dev':'%02x:%02x'%(os.major(x.st_dev),os.minor(x.st_dev)),"
                     "'inode':str(x.st_ino),'opened':False,'reason':'anonymous-memfd'}]}\n"
                     "if 'code_mappings' in r: r['code_mappings']['mappings']=[m for m in r['code_mappings']['mappings'] "
                     "if KEEP_G or m.get('path')!=G]\n"
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
        # round 51 (round-50 closure R6): the rerun's server_exe must be the replay's own image
        noexe_live = os.path.join(d, "noexe-live.py")
        with open(noexe_live, "w") as fh:
            fh.write(open(fake_live).read().replace("r['server_exe']=", "r['unused_exe']="))
        run("server-exe-absent", receipt(), 1, live=noexe_live)
        copy_live = os.path.join(d, "copy-live.py")
        with open(copy_live, "w") as fh:
            # a byte-identical copy at a path (the round-51 J3CopyDecoy shape) is not the memfd
            fh.write(open(fake_live).read().replace(
                "x=os.fstat(f);", "import shutil;c=o+'.copy';shutil.copy(s,c);x=os.stat(c);"))
        run("server-exe-not-own-memfd", receipt(), 1, live=copy_live)
        badsha_live = os.path.join(d, "badsha-live.py")
        with open(badsha_live, "w") as fh:
            fh.write(open(fake_live).read().replace("r['server_exe']={'opened':True,'sha256':h(s),",
                                                    "r['server_exe']={'opened':True,'sha256':'4'*64,"))
        run("server-exe-digest-differs", receipt(), 1, live=badsha_live)
        # round 52 (round-51 closure D5): the image must be sealed, linkless and anonymous
        # (seat M2Replay survivors: an other-inode memfd-shaped record and a partial seal mask)
        for tag, old, new in (("unsealed", "'seals':fcntl.fcntl(f,1034)", "'seals':0"),
                              ("seals-partial", "'seals':fcntl.fcntl(f,1034)", "'seals':7"),
                              ("other-inode", "'inode':str(x.st_ino)", "'inode':str(x.st_ino+1)"),
                              ("linked", "'nlink':x.st_nlink", "'nlink':1"),
                              ("path", "'path':'/memfd:llama-server (deleted)'", "'path':s")):
            alt_live = os.path.join(d, f"{tag}-live.py")
            with open(alt_live, "w") as fh:
                fh.write(open(fake_live).read().replace(old, new))
            run(f"server-exe-{tag}", receipt(), 1, live=alt_live)
        # round 53 (round-52 closure R2): the code mappings must be archive members by digest
        # or root-owned host files, with at least one archive library
        for tag, old, new in (("absent", "r['code_mappings']=", "r['unused_code']="),
                              ("digest-differs", "'sha256':h(L)}", "'sha256':'6'*64}"),
                              ("foreign", "'uid':0,", "'uid':1000,"),
                              ("not-a-member", "'libfake.so');y=os.stat(L)",
                               "'libfake.so');import shutil;shutil.copy(L,L[:-3]+'.copy.so');"
                               "L=L[:-3]+'.copy.so';y=os.stat(L)"),
                              ("unopened", "'opened':True,'uid':y.st_uid", "'opened':False,'uid':y.st_uid"),
                              ("no-archive-library", "'mappings':[{'path':L,", "'mappings':[{'path':'/usr/x',"),
                              ("path-missing", "{'path':'/usr/lib/libc.so.6',", "{'nopath':'/usr/lib/libc.so.6',"),
                              ("required-absent", "KEEP_G=True", "KEEP_G=False"),
                              ("foreign-memfd", "'inode':str(x.st_ino),'opened':False,'reason':'anonymous-memfd'",
                               "'inode':str(x.st_ino+1),'opened':False,'reason':'anonymous-memfd'")):
            alt_live = os.path.join(d, f"code-{tag}-live.py")
            with open(alt_live, "w") as fh:
                src = open(fake_live).read()
                if old not in src:
                    raise AssertionError(f"selftest mutation {tag} does not apply")
                fh.write(src.replace(old, new))
            run(f"code-{tag}", receipt(), 1, live=alt_live)
        res, code = replay(receipt(), os.path.join(d, "w-code-own"), live=fake_live, allow_file=True)
        cases.append(("code-own-members", code == 0 and res.get("own_code", {}).get("verified") is True
                      and sorted(res["own_code"].get("members", {})) == ["build/bin/libfake.so",
                                                                         "build/bin/libggml-base.so.0"]
                      and res["own_code"].get("host") == ["/usr/lib/libc.so.6"],
                      f"exit={code} own_code={res.get('own_code')} mism={res['mismatches']}"))
        # round 53 (X5Selftest survivors c and d): verify_code's refusals called directly,
        # so each rule is exercised alone instead of as a side effect of another entry
        import io
        oc, probs = verify_code({"read": True, "mappings": [
            {"path": "/usr/lib/libc.so.6", "dev": "00:1e", "inode": "1", "opened": True,
             "uid": 0, "sha256": "0" * 64}]}, arc, os.path.join(d, "no-tree"))
        cases.append(("code-hostonly-no-library",
                      "code-mapping:no-archive-library" in probs
                      and "code-mapping:required-absent:libggml-base.so*" in probs
                      and oc == {"verified": False, "members": {}, "host": ["/usr/lib/libc.so.6"]},
                      f"own_code={oc} probs={probs}"))
        hard = os.path.join(d, "hard.tar.gz")
        payload = b"\x7fELF hardlinked payload " + os.urandom(16)
        with tarfile.open(hard, "w:gz") as tf:
            reg = tarfile.TarInfo("build/bin/libpayload.so")
            reg.size = len(payload)
            tf.addfile(reg, io.BytesIO(payload))
            link = tarfile.TarInfo("build/bin/libhard.so")
            link.type = tarfile.LNKTYPE
            link.linkname = "build/bin/libpayload.so"
            tf.addfile(link)
        htree = os.path.realpath(os.path.join(d, "hard-tree"))
        os.makedirs(os.path.join(htree, "build", "bin"))
        hpath = os.path.join(htree, "build", "bin", "libhard.so")
        with open(hpath, "wb") as fh:
            fh.write(payload)
        oc, probs = verify_code({"read": True, "mappings": [
            {"path": hpath, "dev": "00:01", "inode": "1", "opened": True, "uid": 1000,
             "sha256": hashlib.sha256(payload).hexdigest()}]}, hard, htree)
        cases.append(("code-non-regular-member",
                      "code-mapping:not-a-member:build/bin/libhard.so" in probs
                      and "build/bin/libhard.so" not in oc["members"],
                      f"own_code={oc} probs={probs}"))
        # the sealed memfd is filled from the archive's member stream, not from the path
        fd, ident = sealed_member(arc, "build/bin/llama-server", ssha)
        try:
            sealed = fcntl.fcntl(fd, F_GET_SEALS) & SEALS_ALL == SEALS_ALL
            try:
                os.write(fd, b"x")
                wrote = True
            except OSError:
                wrote = False
        finally:
            os.close(fd)
        cases.append(("sealed-member-refuses-writes", sealed and not wrote and ident["memfd"] is True,
                      f"sealed={sealed} wrote={wrote} ident={ident}"))
        # seat M2Replay survivors: the memfd is close-on-exec (only pass_fds hands it on), is
        # closed on a refusal, and a short write cannot leave a truncated image
        fd, _ident = sealed_member(arc, "build/bin/llama-server", ssha)
        try:
            cloexec = not os.get_inheritable(fd)
        finally:
            os.close(fd)
        cases.append(("sealed-member-cloexec", cloexec, f"cloexec={cloexec}"))
        before = len(os.listdir("/proc/self/fd"))
        try:
            sealed_member(arc, "build/bin/llama-server", "5" * 64)
            cases.append(("sealed-member-digest-mismatch", False, "no refusal"))
        except Refused as exc:
            cases.append(("sealed-member-digest-mismatch", str(exc).startswith("memfd-digest-mismatch"), str(exc)))
        after = len(os.listdir("/proc/self/fd"))
        cases.append(("sealed-member-closes-on-refusal", before == after, f"fds {before}->{after}"))
        real_write = os.write
        os.write = lambda f, b: real_write(f, bytes(b)[:3])
        try:
            fd, ident = sealed_member(arc, "build/bin/llama-server", ssha)
            os.close(fd)
            short_ok = ident["sha256"] == ssha
        except Refused as exc:
            short_ok, ident = False, str(exc)
        finally:
            os.write = real_write
        cases.append(("sealed-member-short-writes", short_ok, str(ident)))
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
    # round 51 (seat X1Fresh): an unwritable --out turned a finished replay into a traceback
    try:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        with open(a.out, "w") as fh:
            json.dump(res, fh, indent=1)
    except OSError as exc:
        print(f"replay match={res['match']} refused={res['refused']} mismatches={len(res['mismatches'])} "
              f"exit=2 (--out not written: {exc.strerror})")
        return 2
    print(f"replay match={res['match']} refused={res['refused']} mismatches={len(res['mismatches'])} exit={code}")
    return code


if __name__ == "__main__":
    sys.exit(main())
