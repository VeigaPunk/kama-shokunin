#!/usr/bin/env python3
"""round52-replay-memfd-audit.py - kama round-52 C1 (operability, sourced) counter.

Question: at a lane revision, is the server an outside observer witnesses during a
replay an anonymous, sealed in-memory file (memfd_create(2), F_SEAL_WRITE|SHRINK|GROW|
SEAL) holding the frozen server bytes - an image no path on disk can be, so that no copy,
hardlink or rename-over of a host binary at the extracted member path can stand in for it
- and does the rerun receipt record that same running image, and does the replay name it
as its own?
Routed: corpus/lessons/round-51-verifier-spotcheck.md D5 (C1 carried limits: the copy
decoy J3CopyDecoy met the round-51 counter, a hardlink at the member path met its own leg
(J4Hardlink), rename-over-member provenance stays an [INFERENCE]); SCORECARD §Planned
(round 52) item 1 (bind the replay's server to the extraction event itself, not to dev
and inode of a path).

Frozen names (before data):
  receipts   .ufo/waves/round-48/c2/live/receipt-1.json, -2.json, -3.json (v5, b11909)
  server     sha256 35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0
  model      https://huggingface.co/ggml-org/models-moved/resolve/499bc8821c6b12b4e53c5bffcb21ec206f212d81/tinyllamas/stories260K.gguf
             sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d
  memfd page https://man7.org/linux/man-pages/man2/memfd_create.2.html ("memfd_create()
             creates an anonymous file and returns a file descriptor that refers to it.")
  seals      F_SEAL_SEAL|F_SEAL_SHRINK|F_SEAL_GROW|F_SEAL_WRITE = 15 (fcntl F_GET_SEALS)
  replay     tools/kama-live-replay.py     live tool  tools/kama-llamacpp-live.py
  base       9ff76b1f763512be2f554cbbfd0b2213b63b0847 (round-51 tip after the
             orchestrator's salvage; round-52 start)

How the counter starts a replay is the round-51 counter's, unchanged (an isolating
invoker, PATH/LANG/HOME/XDG_CACHE_HOME/TMPDIR plus proxies, a KAMA_R51_CANARY variable
and a PYTHONPATH sitecustomize marker), with --work <scratch>/work-<tag>.

Legs:
  bind      the round-50 bind leg, unchanged, for EACH receipt (exe digest, listener,
            nonce against the model's own vocabulary, process tree, canaries, mapped
            model, child_pid join, released, teardown after release).
  sealed    for EACH receipt, while the replay holds its server: the counter opens
            /proc/<pid>/exe itself; readlink(2) of the link starts with `/memfd:`; the
            opened file has st_nlink 0 (no directory entry anywhere); fcntl(F_GET_SEALS)
            on it holds all of F_SEAL_SEAL, F_SEAL_SHRINK, F_SEAL_GROW and F_SEAL_WRITE;
            and its bytes hash to the frozen server digest. After release: the rerun
            receipt's `server_exe` has opened true, the frozen digest, the same dev and
            inode, and seals including those four; and the replay's result JSON names
            the same dev and inode under `own_server` with `memfd` true.
  teardown  the round-50 teardown leg, unchanged (invoker SIGKILLed during the hold; every
            snapshotted descendant gone and the port refusing within 30 s).
  newrow    corpus/SOURCES.md at --tip has a registry row, absent at --base, whose
            cells contain man7.org/linux/man-pages/man2/memfd_create.2.html.
met = bind (3/3) and sealed (3/3) and teardown and newrow.
PREDICATE (same sentence in the preregistration): a replay of each of the three
committed v5 b11909 receipts holds a server whose running image, opened by the counter
through /proc/<pid>/exe, is a sealed anonymous memfd (`/memfd:` link, no link count,
write/shrink/grow/seal seals) with the frozen digest, recorded with the same dev, inode
and seals in the rerun receipt's server_exe and named by the replay as its own_server,
while every round-50 bind check still holds; killing the replay's invoker still removes
the whole tree within 30 s; and the memfd surface is a source row; bind=1 sealed=1
teardown=1 newrow=1.

Output: `bind=0|1 sealed=0|1 teardown=0|1 newrow=0|1 bound=N/3 sealedruns=N/3
met=True|False`, then `detail:` lines. Exit 0 met, 1 not met, 2 could not evaluate (git
failure). Read-only on --repo; everything else lives under --scratch (default TMPDIR) and
is removed on exit; --out's parent directories are created before anything is written.
Needs network access to github.com and huggingface.co, and Linux /proc.
"""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import io
import json
import os
import secrets
import shutil
import signal
import socket
import struct
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.request

SERVER_SHA = "35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0"
MODEL_COMMIT = "499bc8821c6b12b4e53c5bffcb21ec206f212d81"
MODEL_URL = ("https://huggingface.co/ggml-org/models-moved/resolve/"
             f"{MODEL_COMMIT}/tinyllamas/stories260K.gguf")
MODEL_SHA = "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"
MEMFD_URL = "man7.org/linux/man-pages/man2/memfd_create.2.html"
BASE = "9ff76b1f763512be2f554cbbfd0b2213b63b0847"
SEALS = 15  # F_SEAL_SEAL | F_SEAL_SHRINK | F_SEAL_GROW | F_SEAL_WRITE
F_GET_SEALS = 1034
RECEIPTS = tuple(f".ufo/waves/round-48/c2/live/receipt-{n}.json" for n in (1, 2, 3))
REPLAY = "tools/kama-live-replay.py"
READY_WAIT = 600     # seconds for ready.json (the replay downloads ~75 MB first)
EXIT_WAIT = 180      # seconds for the replay to finish after release
KILL_WAIT = 30       # seconds for the tree to go after the invoker is killed
PASS_ENV = ("PATH", "LANG", "http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY", "no_proxy")
INVOKER = ("import subprocess, sys\n"
           "sys.exit(subprocess.call(sys.argv[1:]))\n")


class EvalError(Exception):
    pass


def git(repo, *args, check=True):
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True)
    if check and p.returncode != 0:
        raise EvalError(f"git {' '.join(args)[:120]}: {p.stderr.decode('utf-8', 'replace').strip()[:200]}")
    return p


def sha_file(path):
    h = hashlib.sha256()
    try:
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
    except (OSError, TypeError):
        return None
    return h.hexdigest()


def load(path):
    try:
        with open(path) as fh:
            return json.load(fh)
    except (OSError, ValueError, TypeError):
        return None


# ------------------------------------------------------------- GGUF vocabulary
def gguf_tokens(path):
    """tokenizer.ggml.tokens of a GGUF v2/v3 file, decoded by this counter."""
    with open(path, "rb") as fh:
        data = fh.read()
    if data[:4] != b"GGUF":
        raise EvalError("model is not GGUF")
    ver = struct.unpack_from("<I", data, 4)[0]
    if ver < 2:
        raise EvalError(f"GGUF v{ver} unsupported")
    _nt, nkv = struct.unpack_from("<QQ", data, 8)
    off = 24
    fixed = {0: 1, 1: 1, 2: 2, 3: 2, 4: 4, 5: 4, 6: 4, 7: 1, 10: 8, 11: 8, 12: 8}

    def rstr(o):
        n = struct.unpack_from("<Q", data, o)[0]
        return data[o + 8:o + 8 + n].decode("utf-8", "replace"), o + 8 + n

    def skip(t, o):
        if t in fixed:
            return o + fixed[t]
        if t == 8:
            return rstr(o)[1]
        if t == 9:
            et, n = struct.unpack_from("<IQ", data, o)
            o += 12
            for _ in range(n):
                o = skip(et, o)
            return o
        raise EvalError(f"GGUF value type {t}")

    for _ in range(nkv):
        key, off = rstr(off)
        t = struct.unpack_from("<I", data, off)[0]
        off += 4
        if key == "tokenizer.ggml.tokens" and t == 9:
            et, n = struct.unpack_from("<IQ", data, off)
            off += 12
            if et != 8:
                raise EvalError("tokens array is not strings")
            out = []
            for _ in range(n):
                s, off = rstr(off)
                out.append(s)
            return out
        off = skip(t, off)
    raise EvalError("tokenizer.ggml.tokens absent")


# ------------------------------------------------------------- /proc observation
def listen_inodes(port):
    out = set()
    for name in ("/proc/net/tcp", "/proc/net/tcp6"):
        try:
            with open(name) as fh:
                rows = fh.read().splitlines()[1:]
        except OSError:
            continue
        for row in rows:
            f = row.split()
            if len(f) < 10 or f[3] != "0A":
                continue
            addr, hport = f[1].rsplit(":", 1)
            if int(hport, 16) != port:
                continue
            if addr not in ("0100007F", "00000000000000000000000001000000"):
                continue
            out.add(f[9])
    return out


def pid_socket_inodes(pid):
    out = set()
    try:
        for fd in os.listdir(f"/proc/{pid}/fd"):
            try:
                link = os.readlink(f"/proc/{pid}/fd/{fd}")
            except OSError:
                continue
            if link.startswith("socket:["):
                out.add(link[8:-1])
    except OSError:
        pass
    return out


def stat_fields(pid):
    """(state, ppid, starttime) from /proc/<pid>/stat, or None."""
    try:
        with open(f"/proc/{pid}/stat") as fh:
            rest = fh.read().rsplit(")", 1)[1].split()
        return rest[0], int(rest[1]), int(rest[19])
    except (OSError, IndexError, ValueError):
        return None


def pid_alive(pid, start=None):
    st = stat_fields(pid)
    if st is None or st[0] in ("Z", "X"):
        return False
    return start is None or st[2] == start


def port_refuses(port):
    s = socket.socket()
    s.settimeout(2)
    try:
        s.connect(("127.0.0.1", port))
        return False
    except OSError:
        return True
    finally:
        s.close()


def post(port, path, body):
    req = urllib.request.Request(f"http://127.0.0.1:{port}{path}", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(req, timeout=20) as r:
        return json.loads(r.read(1 << 20))


def environ_keys(pid):
    try:
        with open(f"/proc/{pid}/environ", "rb") as fh:
            return {e.split(b"=", 1)[0].decode("utf-8", "replace") for e in fh.read().split(b"\0") if e}
    except OSError:
        return None


def descendants(root):
    """{pid: starttime} of every live descendant of root (a /proc scan)."""
    kids = {}
    for name in os.listdir("/proc"):
        if not name.isdigit():
            continue
        st = stat_fields(int(name))
        if st is not None and st[0] not in ("Z", "X"):
            kids.setdefault(st[1], []).append((int(name), st[2]))
    out, todo = {}, [root]
    while todo:
        for pid, start in kids.get(todo.pop(), []):
            if pid not in out:
                out[pid] = start
                todo.append(pid)
    return out


def descends_from(pid, ancestor):
    seen = 0
    while pid > 1 and seen < 64:
        st = stat_fields(pid)
        if st is None:
            return False
        if st[1] == ancestor:
            return True
        pid, seen = st[1], seen + 1
    return False


def mapped_model(pid, probs):
    """(dev, inode) of a file-backed mapping of pid whose pathname, stat()ed now, is the
    same file and hashes to the frozen model; None (problem appended) otherwise."""
    try:
        with open(f"/proc/{pid}/maps") as fh:
            rows = fh.read().splitlines()
    except OSError as exc:
        probs.append(f"maps unreadable: {exc}")
        return None
    seen, cands = set(), []
    for row in rows:
        f = row.split(None, 5)
        if len(f) < 6 or f[4] == "0" or not f[5].startswith("/"):
            continue
        key = (f[3], f[4], f[5])
        if key in seen:
            continue
        seen.add(key)
        cands.append(key)
    for dev, ino, path in cands:
        try:
            st = os.stat(path)
        except OSError:
            continue
        if f"{os.major(st.st_dev):02x}:{os.minor(st.st_dev):02x}" != dev or str(st.st_ino) != ino:
            continue
        if st.st_size < 1024 or st.st_size > 64 << 20:
            continue
        if sha_file(path) == MODEL_SHA:
            return dev, ino
    probs.append(f"no mapping of pid {pid} is a file hashing to the frozen model ({len(cands)} file mappings)")
    return None


def observe(pid, port, vocab, canary, probs):
    """The counter's own witness of a running server; appends problems."""
    exe = sha_file(f"/proc/{pid}/exe")
    if exe != SERVER_SHA:
        probs.append(f"exe sha256 {exe} is not the frozen server")
    li = listen_inodes(port)
    if not li or not (li & pid_socket_inodes(pid)):
        probs.append(f"no LISTEN socket on {port} owned by pid {pid} (inodes {sorted(li)})")
    st = stat_fields(pid)
    parent = st[1] if st else None
    for who, p in (("server", pid), ("server parent", parent)):
        keys = environ_keys(p) if p else None
        if keys is None:
            probs.append(f"{who} environ unreadable (pid {p})")
        elif canary in keys:
            probs.append(f"{who} pid {p} carries the planted KAMA_R51_CANARY")
    mapped = mapped_model(pid, probs)
    nonce = f"kama witness {secrets.token_hex(8)}"
    try:
        tk = post(port, "/tokenize", {"content": nonce, "with_pieces": True})["tokens"]
        ids = [t["id"] for t in tk]
        bad = [t for t in tk if not (isinstance(t.get("piece"), str) and 0 <= t["id"] < len(vocab)
                                     and vocab[t["id"]].replace("\u2581", " ") == t["piece"])]
        if not ids or bad:
            probs.append(f"tokenize pieces disagree with the model vocabulary: {bad[:3]}")
        dt = post(port, "/detokenize", {"tokens": ids})["content"]
        if dt not in (nonce, " " + nonce):
            probs.append(f"detokenize {dt!r} != nonce {nonce!r}")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        probs.append(f"nonce round-trip failed: {type(exc).__name__}: {exc}")
    return nonce, mapped


def sealed_exe(pid, probs):
    """The counter's own reading of the image the server runs: /proc/<pid>/exe opened,
    fstat()ed and hashed; it must be a sealed anonymous memfd (memfd_create(2))."""
    try:
        link = os.readlink(f"/proc/{pid}/exe")
        fd = os.open(f"/proc/{pid}/exe", os.O_RDONLY)
    except OSError as exc:
        probs.append(f"sealed: /proc/{pid}/exe unopenable: {exc.strerror}")
        return None
    try:
        st = os.fstat(fd)
        try:
            seals = fcntl.fcntl(fd, F_GET_SEALS)
        except OSError as exc:
            seals = None
            probs.append(f"sealed: F_GET_SEALS on the running image failed: {exc.strerror}")
        h = hashlib.sha256()
        with os.fdopen(os.dup(fd), "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
    finally:
        os.close(fd)
    got = ("%02x:%02x" % (os.major(st.st_dev), os.minor(st.st_dev)), str(st.st_ino))
    if not link.startswith("/memfd:"):
        probs.append(f"sealed: running image link {link!r} is not an anonymous memfd")
    if st.st_nlink != 0:
        probs.append(f"sealed: running image has link count {st.st_nlink}, not 0")
    if seals is not None and seals & SEALS != SEALS:
        probs.append(f"sealed: running image seals {seals} lack some of {SEALS}")
    if h.hexdigest() != SERVER_SHA:
        probs.append(f"sealed: running image sha256 {h.hexdigest()} is not the frozen server")
    return got, seals, link


def prepare_env(S, tag):
    """The fixed replay environment and its two canaries; returns (env, canary, marker)."""
    env = {k: os.environ[k] for k in PASS_ENV if k in os.environ}
    for k, sub in (("HOME", f"home-{tag}"), ("XDG_CACHE_HOME", f"home-{tag}/.cache"), ("TMPDIR", f"tmp-{tag}")):
        d = os.path.join(S, sub)
        os.makedirs(d, exist_ok=True)
        env[k] = d
    canary = "KAMA_R51_CANARY"
    env[canary] = secrets.token_hex(8)
    cdir = os.path.join(S, f"canary-{tag}")
    os.makedirs(cdir)
    marker = os.path.join(S, f"canary-{tag}.marker")
    with open(os.path.join(cdir, "sitecustomize.py"), "w") as fh:
        fh.write("import os, sys\n"
                 f"with open({marker!r}, 'a') as _fh:\n"
                 "    _fh.write('%d %r\\n' % (os.getpid(), sys.argv[:3]))\n")
    env["PYTHONPATH"] = cdir
    return env, canary, marker


def start_replay(tree, rpath, S, tag):
    env, canary, marker = prepare_env(S, tag)
    work, wd = os.path.join(S, f"work-{tag}"), os.path.join(S, f"wd-{tag}")
    os.makedirs(wd)
    outj = os.path.join(S, f"{tag}.json")
    log = open(os.path.join(S, f"{tag}.log"), "wb")
    argv = [sys.executable, "-I", "-c", INVOKER, sys.executable, "-I", os.path.join(tree, REPLAY),
            "--receipt", rpath, "--work", work, "--out", outj, "--witness-dir", wd]
    p = subprocess.Popen(argv, env=env, cwd=tree, stdout=log, stderr=log, start_new_session=True)
    return p, wd, outj, log, canary, marker, work


def wait_ready(p, wd):
    t0 = time.monotonic()
    while time.monotonic() - t0 < READY_WAIT and p.poll() is None:
        ready = load(os.path.join(wd, "ready.json"))
        if isinstance(ready, dict) and isinstance(ready.get("pid"), int) and isinstance(ready.get("port"), int):
            return ready
        time.sleep(0.2)
    return None


def replay_pid(p):
    """The replay process: the invoker's only child."""
    kids = [pid for pid, _s in descendants(p.pid).items()
            if (stat_fields(pid) or (None, None))[1] == p.pid]
    return kids[0] if len(kids) == 1 else None


def reap(p, extra=()):
    for pid, start in list(descendants(p.pid).items()) + list(extra):
        if pid_alive(pid, start):
            try:
                os.kill(pid, signal.SIGKILL)
            except OSError:
                pass
    if p.poll() is None:
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except OSError:
            pass
        p.wait()


def bind_one(tree, rpath, S, tag, vocab, detail):
    p, wd, outj, log, canary, marker, work = start_replay(tree, rpath, S, tag)
    probs, snap, oprobs, got, obs = [], {}, [], None, None
    try:
        ready = wait_ready(p, wd)
        if ready is None:
            probs.append(f"no ready.json (invoker exit {p.poll()})")
            oprobs.append("sealed: no server was announced, so no running image was observed")
            pid = port = None
        else:
            pid, port = ready["pid"], ready["port"]
            snap = descendants(p.pid)
            rp = replay_pid(p)
            if rp is None or not descends_from(pid, rp):
                probs.append(f"server pid {pid} does not descend from the replay process {rp}")
            nonce, mapped = observe(pid, port, vocab, canary, probs)
            obs = sealed_exe(pid, oprobs)
            got = obs[0] if obs is not None else None
        with open(os.path.join(wd, "release"), "w") as fh:
            fh.write("released by round52 counter\n")
        try:
            code = p.wait(timeout=EXIT_WAIT)
        except subprocess.TimeoutExpired:
            code = None
        j = load(outj)
        if code != 0 or not isinstance(j, dict) or j.get("match") is not True:
            probs.append(f"replay exit {code} match {j.get('match') if isinstance(j, dict) else None} "
                         f"refused {j.get('refused') if isinstance(j, dict) else None}")
        rr = load(j.get("rerun_receipt")) if isinstance(j, dict) and j.get("rerun_receipt") else None
        if not (isinstance(rr, dict) and isinstance(rr.get("witness"), dict)
                and rr["witness"].get("released") is True):
            probs.append("rerun receipt does not record witness.released true")
        if pid is not None:
            if not (isinstance(rr, dict) and rr.get("child_pid") == pid):
                probs.append(f"rerun child_pid {rr.get('child_pid') if isinstance(rr, dict) else None} "
                             f"!= observed pid {pid}")
            mm = rr.get("model_mapping") if isinstance(rr, dict) else None
            if not (isinstance(mm, dict) and mm.get("sha256") == MODEL_SHA and mapped is not None
                    and str(mm.get("dev")) == mapped[0] and str(mm.get("inode")) == mapped[1]):
                probs.append(f"rerun model_mapping {mm!r} does not record the observed mapping {mapped}")
            se = rr.get("server_exe") if isinstance(rr, dict) else None
            if not (isinstance(se, dict) and se.get("opened") is True and se.get("sha256") == SERVER_SHA
                    and got is not None and (str(se.get("dev")), str(se.get("inode"))) == got
                    and isinstance(se.get("seals"), int) and se["seals"] & SEALS == SEALS):
                oprobs.append(f"sealed: rerun server_exe {se!r} does not record the observed sealed image {got}")
            osv = j.get("own_server") if isinstance(j, dict) else None
            if not (isinstance(osv, dict) and osv.get("memfd") is True
                    and got is not None and (str(osv.get("dev")), str(osv.get("inode"))) == got):
                oprobs.append(f"sealed: replay own_server {osv!r} does not name the observed memfd")
            if pid_alive(pid) or not port_refuses(port):
                probs.append("server still alive or port still accepting after the replay exited")
        try:
            with open(marker) as fh:
                hits = fh.read().splitlines()
        except OSError:
            hits = []
        if hits:
            probs.append(f"planted sitecustomize imported by {len(hits)} interpreter(s): {hits[:2]}")
        if not probs:
            detail.append(f"bind {tag}: pid {pid} port {port} exe+listen+tree+env+mapped ok, child_pid joined, "
                          f"mapping dev {mapped[0]} inode {mapped[1]} recorded, nonce {nonce!r} round-tripped")
    finally:
        reap(p, snap.items())
        log.close()
    for pr in probs:
        detail.append(f"bind {tag}: {pr}")
    for pr in oprobs:
        detail.append(f"sealed {tag}: {pr}")
    if not oprobs:
        detail.append(f"sealed {tag}: running image {obs[2]!r} {got[0]}:{got[1]} seals {obs[1]} is a sealed "
                      f"memfd with the frozen digest, recorded in server_exe and own_server")
    return (not probs), (not oprobs)


def teardown_leg(tree, rpath, S, detail):
    p, wd, _outj, log, _canary, _marker, _work = start_replay(tree, rpath, S, "kill")
    snap, ok = {}, False
    try:
        ready = wait_ready(p, wd)
        if ready is None:
            detail.append(f"teardown: no ready.json (invoker exit {p.poll()})")
            return False
        snap = descendants(p.pid)
        port = ready["port"]
        if ready["pid"] not in snap:
            detail.append(f"teardown: announced pid {ready['pid']} is not under the invoker")
        os.kill(p.pid, signal.SIGKILL)
        p.wait()
        t0 = time.monotonic()
        while time.monotonic() - t0 < KILL_WAIT:
            alive = [pid for pid, start in snap.items() if pid_alive(pid, start)]
            if not alive and port_refuses(port):
                break
            time.sleep(0.1)
        dt = time.monotonic() - t0
        alive = [pid for pid, start in snap.items() if pid_alive(pid, start)]
        refused = port_refuses(port)
        ok = not alive and refused and ready["pid"] in snap
        detail.append(f"teardown: invoker SIGKILLed with {len(snap)} descendants; after {dt:.2f} s "
                      f"alive {alive} port {'refuses' if refused else 'ACCEPTS'} {'ok' if ok else 'FAIL'}")
        return ok
    finally:
        reap(p, snap.items())
        log.close()


def newrow_leg(repo, tip, detail):
    def rows(rev):
        p = git(repo, "show", f"{rev}:corpus/SOURCES.md", check=False)
        if p.returncode != 0:
            return set()
        return {ln for ln in p.stdout.decode("utf-8", "replace").split("\n")
                if ln.lstrip(" ")[:3] == "| S" and ln.lstrip(" ")[3:4].isdigit()}
    new = rows(tip) - rows(BASE)
    hit = [ln for ln in new if MEMFD_URL in ln]
    detail.append(f"newrow: {len(new)} rows new since base; {len(hit)} name memfd_create(2): {[ln[:8] for ln in hit]}")
    return bool(hit)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", required=True, help="lane clone (read-only)")
    ap.add_argument("--tip", required=True, help="full commit to measure")
    ap.add_argument("--scratch", default=None, help="scratch dir (default: TMPDIR)")
    ap.add_argument("--out", default=None, help="also write the receipt here")
    a = ap.parse_args(argv)
    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    root = a.scratch or tempfile.gettempdir()
    os.makedirs(root, exist_ok=True)
    S = tempfile.mkdtemp(prefix="r52c1-", dir=root)
    detail = []
    try:
        try:
            tip = git(a.repo, "rev-parse", "--verify", a.tip + "^{commit}").stdout.decode().strip()
            arc = git(a.repo, "archive", "--format=tar", tip).stdout
        except EvalError as exc:
            print(f"could-not-evaluate: {exc}")
            return 2
        tree = os.path.join(S, "tree")
        os.makedirs(tree)
        with tarfile.open(fileobj=io.BytesIO(arc)) as tf:
            tf.extractall(tree, filter=lambda m, dest: None if (m.issym() or m.islnk())
                          else tarfile.data_filter(m, dest))
        model = os.path.join(S, "counter-model.gguf")
        vocab = None
        try:
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
            with opener.open(MODEL_URL, timeout=120) as r, open(model, "wb") as fh:
                shutil.copyfileobj(r, fh)
            if sha_file(model) != MODEL_SHA:
                detail.append("counter model download does not hash to the frozen digest")
            else:
                vocab = gguf_tokens(model)
                detail.append(f"counter vocabulary: {len(vocab)} tokens from its own download")
        except (OSError, EvalError, struct.error) as exc:
            detail.append(f"counter model unavailable: {type(exc).__name__}: {exc}")
        bound = owned = 0
        have = os.path.isfile(os.path.join(tree, REPLAY))
        if vocab is not None and have:
            for n, path in enumerate(RECEIPTS, 1):
                if not os.path.isfile(os.path.join(tree, path)):
                    detail.append(f"bind: {path} absent at tip")
                    continue
                b, o = bind_one(tree, os.path.join(tree, path), S, f"b{n}", vocab, detail)
                bound += b
                owned += o
        bl = bound == len(RECEIPTS)
        ol = owned == len(RECEIPTS)
        tl = have and os.path.isfile(os.path.join(tree, RECEIPTS[0])) and \
            teardown_leg(tree, os.path.join(tree, RECEIPTS[0]), S, detail)
        nl = newrow_leg(a.repo, tip, detail)
        met = bool(bl and ol and tl and nl)
        lines = [f"tip={tip}",
                 f"bind={int(bl)} sealed={int(ol)} teardown={int(bool(tl))} newrow={int(nl)} "
                 f"bound={bound}/{len(RECEIPTS)} sealedruns={owned}/{len(RECEIPTS)} met={met}"]
        lines += [f"detail: {d}" for d in detail]
        text = "\n".join(lines)
        print(text)
        if a.out:
            with open(a.out, "w") as fh:
                fh.write(text + "\n")
        return 0 if met else 1
    finally:
        shutil.rmtree(S, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
