#!/usr/bin/env python3
"""round53-replay-code-audit.py - kama round-53 C1 (operability, sourced) counter.

Question: at a lane revision, is every piece of code the replay's server executes either
the release archive's own bytes - read by this counter out of the server's memory and
compared with its own download of the archive - or a root-owned host library; does the
rerun receipt record each archive library the server maps, with the archive's digest;
and does the replay name them as verified against the archive it unpacked?
Routed: SCORECARD §Planned (round 53) item 1 (per-mapping identity for the code the
launcher loads - libllama-server-impl.so, libggml*, the chosen CPU backend - with a
control that swaps a library after the member check; seats K2Design, N2Pattern), the
round-52 outside closure R2 ("libraries and model load by path (K2Design)").

Frozen names (before data):
  receipts   .ufo/waves/round-48/c2/live/receipt-1.json, -2.json, -3.json (v5, b11909)
  server     sha256 35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0
  archive    https://github.com/ggml-org/llama.cpp/releases/download/b11909/llama-b11909-bin-ubuntu-x64.tar.gz
             sha256 bf94332a3001f3ee0b032cda37259f68460e28732ef9a579bfb1b918197e695b
  model      https://huggingface.co/ggml-org/models-moved/resolve/499bc8821c6b12b4e53c5bffcb21ec206f212d81/tinyllamas/stories260K.gguf
             sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d
  mem page   https://man7.org/linux/man-pages/man5/proc_pid_mem.5.html
  required   mapped archive members matching libllama-server-impl.so, libggml-base.so*,
             libggml.so* and libggml-cpu-*.so (the server's code, ggml, its base and the
             CPU backend the loader chose)
  replay     tools/kama-live-replay.py     live tool  tools/kama-llamacpp-live.py
  base       4229ea1b9a789148dded1f159c20967d9a01373f (round-52 lane tip; round-53 start)

How the counter starts a replay is the round-52 counter's, unchanged (an isolating
invoker, PATH/LANG/HOME/XDG_CACHE_HOME/TMPDIR plus proxies, a KAMA_R51_CANARY variable
and a PYTHONPATH sitecustomize marker), with --work <scratch>/work-<tag>, so the replay
unpacks the archive at <scratch>/work-<tag>/server.

Legs:
  bind      the round-50 bind leg, unchanged, for EACH receipt.
  sealed    the round-52 sealed leg, unchanged, for EACH receipt.
  code      for EACH receipt, while the replay holds its server: every row of
            /proc/<pid>/maps with `x` in its permissions and a pathname starting with `/`
            other than `/memfd:` is either (a) a file under <scratch>/work-<tag>/server
            whose relative path is a regular member of the counter's own download of the
            archive, and the bytes the counter reads from /proc/<pid>/mem over that row's
            address range equal the member's bytes from the row's file offset (zero past
            the member's end) - or (b) a path whose stat() shows uid 0 and the row's inode,
            and that this counter cannot write (a root-owned host library; the row's dev is
            not compared for host files: this host's btrfs/overlay root reports a st_dev
            different from the one /proc/<pid>/maps shows). The archive members of (a) include the
            four required names. After release: the rerun receipt's
            `code_mappings.mappings` has, for each (a) file, an entry with the same path,
            dev and inode and the sha256 of the counter's member bytes; and the replay's
            result JSON has `own_code.verified` true and names each (a) member with that
            same digest under `own_code.members`.
  teardown  the round-50 teardown leg, unchanged.
  newrow    corpus/SOURCES.md at --tip has a registry row, absent at --base, whose
            cells contain man7.org/linux/man-pages/man5/proc_pid_mem.5.html.
met = bind (3/3) and sealed (3/3) and code (3/3) and teardown and newrow.
PREDICATE (same sentence in the preregistration): a replay of each of the three
committed v5 b11909 receipts holds a server every one of whose executable file mappings
is either an archive member under the replay's unpacked tree whose mapped bytes, read by
the counter from /proc/<pid>/mem, equal that member's bytes in the counter's own download
of the release archive - the server implementation, ggml, ggml-base and a ggml CPU
backend among them - or a root-owned host file; the rerun receipt records each such
member mapping with its dev, inode and the member's digest and the replay names them as
verified, while every round-52 bind and sealed check still holds; killing the replay's
invoker still removes the whole tree within 30 s; and /proc/pid/mem is a source row;
bind=1 sealed=1 code=1 teardown=1 newrow=1.

Output: `bind=0|1 sealed=0|1 code=0|1 teardown=0|1 newrow=0|1 bound=N/3 sealedruns=N/3
coderuns=N/3 met=True|False`, then `detail:` lines. Exit 0 met, 1 not met, 2 could not
evaluate (git failure). Read-only on --repo; everything else lives under --scratch
(default TMPDIR) and is removed on exit; --out's parent directories are created before
anything is written. Needs network access to github.com and huggingface.co, Linux /proc,
and ptrace read access to its own descendants (Yama ptrace_scope 0 or 1).
"""
from __future__ import annotations

import argparse
import fnmatch
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
MEMFD_URL = "man7.org/linux/man-pages/man5/proc_pid_mem.5.html"
BASE = "4229ea1b9a789148dded1f159c20967d9a01373f"
ARCHIVE_URL = "https://github.com/ggml-org/llama.cpp/releases/download/b11909/llama-b11909-bin-ubuntu-x64.tar.gz"
ARCHIVE_SHA = "bf94332a3001f3ee0b032cda37259f68460e28732ef9a579bfb1b918197e695b"
REQUIRED = ("libllama-server-impl.so", "libggml-base.so*", "libggml.so*", "libggml-cpu-*.so")
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



class Archive:
    """The counter's own download of the release archive: member bytes on demand."""

    def __init__(self, path):
        self.tf = tarfile.open(path)
        self.cache = {}

    def member(self, name):
        if name not in self.cache:
            try:
                ti = self.tf.getmember(name)
            except KeyError:
                self.cache[name] = None
            else:
                self.cache[name] = self.tf.extractfile(ti).read() if ti.isreg() else None
        return self.cache[name]


def code_observe(pid, tree, arc, probs):
    """The counter's own reading of the code the server executes: {path: (dev, inode,
    member)} for the archive files among its executable mappings, each mapped range read
    from /proc/<pid>/mem and compared with the archive member's bytes; host files must be
    root-owned. Problems are appended (prefixed `code:`)."""
    try:
        with open(f"/proc/{pid}/maps") as fh:
            rows = fh.read().splitlines()
    except OSError as exc:
        probs.append(f"code: maps unreadable: {exc.strerror}")
        return None
    try:
        mem = os.open(f"/proc/{pid}/mem", os.O_RDONLY)
    except OSError as exc:
        probs.append(f"code: /proc/{pid}/mem unopenable: {exc.strerror}")
        return None
    seen, host, compared = {}, set(), 0
    try:
        for row in rows:
            f = row.split(None, 5)
            if len(f) < 6 or "x" not in f[1] or not f[5].startswith("/") or f[5].startswith("/memfd:"):
                continue
            path, dev, ino = f[5], f[3], f[4]
            if path.startswith(tree + os.sep):
                member = os.path.relpath(path, tree)
                data = arc.member(member)
                if data is None:
                    probs.append(f"code: {path} is not a regular member of the archive")
                    continue
                lo, hi = (int(v, 16) for v in f[0].split("-"))
                off = int(f[2], 16)
                want = data[off:off + (hi - lo)]
                want += b"\0" * ((hi - lo) - len(want))
                try:
                    got = os.pread(mem, hi - lo, lo)
                except OSError as exc:
                    probs.append(f"code: reading {f[0]} of {member} from /proc/{pid}/mem failed: {exc.strerror}")
                    continue
                compared += 1
                if got != want:
                    probs.append(f"code: mapped bytes {f[0]} (offset {f[2]}) of {member} differ from the archive member")
                prev = seen.setdefault(path, (dev, ino, member))
                if prev[:2] != (dev, ino):
                    probs.append(f"code: {path} is mapped from two files ({prev[:2]} and {(dev, ino)})")
            else:
                try:
                    st = os.stat(path)
                except OSError as exc:
                    probs.append(f"code: host mapping {path} unstattable: {exc.strerror}")
                    continue
                sdev = "%02x:%02x" % (os.major(st.st_dev), os.minor(st.st_dev))
                # host files: the maps `dev` of a file on this host's btrfs/overlay root is
                # not the st_dev stat() reports (00:1e vs 00:20 in the pre-freeze dry run),
                # so a host file is matched by inode, uid 0 and not writable by this counter
                if st.st_uid != 0 or str(st.st_ino) != ino or os.access(path, os.W_OK):
                    probs.append(f"code: executable mapping {path} ({dev} {ino}) is neither an archive file "
                                 f"under the unpacked tree nor a root-owned host file (uid {st.st_uid}, "
                                 f"{sdev} {st.st_ino}, writable {os.access(path, os.W_OK)})")
                    continue
                host.add(path)
    finally:
        os.close(mem)
    names = [os.path.basename(m) for _d, _i, m in seen.values()]
    for pat in REQUIRED:
        if not any(fnmatch.fnmatchcase(n, pat) for n in names):
            probs.append(f"code: no mapped archive member matches {pat} (mapped: {sorted(names)})")
    return {"files": seen, "host": len(host), "ranges": compared}


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


def bind_one(tree, rpath, S, tag, vocab, arc, detail):
    p, wd, outj, log, canary, marker, work = start_replay(tree, rpath, S, tag)
    probs, snap, oprobs, got, obs = [], {}, [], None, None
    cprobs, cobs = [], None
    utree = os.path.realpath(os.path.join(work, "server"))
    try:
        ready = wait_ready(p, wd)
        if ready is None:
            probs.append(f"no ready.json (invoker exit {p.poll()})")
            oprobs.append("sealed: no server was announced, so no running image was observed")
            cprobs.append("code: no server was announced, so no mapping was observed")
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
            cobs = code_observe(pid, utree, arc, cprobs) if arc is not None else None
            if arc is None:
                cprobs.append("code: the counter has no archive of its own")
        with open(os.path.join(wd, "release"), "w") as fh:
            fh.write("released by round53 counter\n")
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
            if cobs is not None:
                cm = rr.get("code_mappings") if isinstance(rr, dict) else None
                ents = cm.get("mappings") if isinstance(cm, dict) else None
                ents = ents if isinstance(ents, list) else []
                oc = j.get("own_code") if isinstance(j, dict) else None
                om = oc.get("members") if isinstance(oc, dict) else None
                if not (isinstance(oc, dict) and oc.get("verified") is True and isinstance(om, dict)):
                    cprobs.append(f"code: replay own_code {str(oc)[:160]!r} is not verified with members")
                    om = {}
                for path, (dev, ino, member) in sorted(cobs["files"].items()):
                    digest = hashlib.sha256(arc.member(member)).hexdigest()
                    if not any(isinstance(e, dict) and e.get("path") == path and str(e.get("dev")) == dev
                               and str(e.get("inode")) == ino and e.get("sha256") == digest for e in ents):
                        cprobs.append(f"code: rerun code_mappings has no entry {path} {dev} {ino} with the archive digest")
                    if om.get(member) != digest:
                        cprobs.append(f"code: replay own_code.members[{member!r}] {om.get(member)!r} != archive digest")
            if pid_alive(pid) or not port_refuses(port):
                probs.append("server still alive or port still accepting after the replay exited")
        try:
            with open(marker) as fh:
                hits = fh.read().splitlines()
        except OSError:
            hits = []
        if hits:
            probs.append(f"planted sitecustomize imported by {len(hits)} interpreter(s): {hits[:2]}")
        if not cprobs and cobs is not None:
            detail.append(f"code {tag}: {len(cobs['files'])} archive files ({cobs['ranges']} executable ranges) "
                          f"byte-equal in /proc/<pid>/mem to the counter's own archive, {cobs['host']} root-owned "
                          f"host files; recorded in code_mappings and own_code: "
                          f"{sorted(os.path.basename(m) for _d, _i, m in cobs['files'].values())}")
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
    for pr in cprobs:
        detail.append(f"code {tag}: {pr}")
    if not oprobs:
        detail.append(f"sealed {tag}: running image {obs[2]!r} {got[0]}:{got[1]} seals {obs[1]} is a sealed "
                      f"memfd with the frozen digest, recorded in server_exe and own_server")
    return (not probs), (not oprobs), (not cprobs and cobs is not None)


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
    detail.append(f"newrow: {len(new)} rows new since base; {len(hit)} name proc_pid_mem(5): {[ln[:8] for ln in hit]}")
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
    S = tempfile.mkdtemp(prefix="r53c1-", dir=root)
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
        arc = None
        apath = os.path.join(S, "counter-archive.tar.gz")
        try:
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
            with opener.open(ARCHIVE_URL, timeout=300) as r, open(apath, "wb") as fh:
                shutil.copyfileobj(r, fh)
            if sha_file(apath) != ARCHIVE_SHA:
                detail.append("counter archive download does not hash to the frozen digest")
            else:
                arc = Archive(apath)
                detail.append("counter archive: its own download, frozen digest")
        except (OSError, tarfile.TarError) as exc:
            detail.append(f"counter archive unavailable: {type(exc).__name__}: {exc}")
        bound = owned = coded = 0
        have = os.path.isfile(os.path.join(tree, REPLAY))
        if vocab is not None and have:
            for n, path in enumerate(RECEIPTS, 1):
                if not os.path.isfile(os.path.join(tree, path)):
                    detail.append(f"bind: {path} absent at tip")
                    continue
                b, o, c = bind_one(tree, os.path.join(tree, path), S, f"b{n}", vocab, arc, detail)
                bound += b
                owned += o
                coded += c
        bl = bound == len(RECEIPTS)
        ol = owned == len(RECEIPTS)
        cl = coded == len(RECEIPTS)
        tl = have and os.path.isfile(os.path.join(tree, RECEIPTS[0])) and \
            teardown_leg(tree, os.path.join(tree, RECEIPTS[0]), S, detail)
        nl = newrow_leg(a.repo, tip, detail)
        met = bool(bl and ol and cl and tl and nl)
        lines = [f"tip={tip}",
                 f"bind={int(bl)} sealed={int(ol)} code={int(cl)} teardown={int(bool(tl))} newrow={int(nl)} "
                 f"bound={bound}/{len(RECEIPTS)} sealedruns={owned}/{len(RECEIPTS)} coderuns={coded}/{len(RECEIPTS)} "
                 f"met={met}"]
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
