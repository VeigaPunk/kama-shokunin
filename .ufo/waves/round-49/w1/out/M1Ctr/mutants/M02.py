#!/usr/bin/env python3
"""round49-replay-witness-audit.py - kama round-49 C1 (operability, sourced) counter.

Question: at a lane revision, does a replay of the lane's live llama.cpp evidence
show, to an observer outside the replay, that the recorded server binary really
ran with the recorded model - and does record-time verification refuse an archive
whose member would make it hash an unbounded number of bytes?
Routed (corpus/lessons/round-48-verifier-spotcheck.md):
  R5  replay never witnesses server execution: a replay that copies captures
      without running a server met the round-48 counter (seats K2Cheat, K2Urlswap);
  R1  verify_archive_member() hashes a member of any declared size: a ~104-byte
      sparse archive makes record time read ~10^15 bytes (seat Sen2Live F1).

Frozen names (before data):
  receipts   .ufo/waves/round-48/c2/live/receipt-1.json, -2.json, -3.json (v5, b11909)
  server     sha256 35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0
             (llama-b11909/llama-server, the member the receipts record)
  model      https://huggingface.co/ggml-org/models-moved/resolve/499bc8821c6b12b4e53c5bffcb21ec206f212d81/tinyllamas/stories260K.gguf
             sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d
  readme     llama.cpp tools/server/README.md at caa8191df159f764fb0160e3d2fc6be008948aee
             (b11909): POST /tokenize `with_pieces`, POST /detokenize
  replay     tools/kama-live-replay.py     live tool  tools/kama-llamacpp-live.py

Witness contract (what the build must provide; this counter observes, never trusts):
  `kama-live-replay.py --receipt R --work W --out J --witness-dir D` passes
  `--witness-dir D` to the live tool, which, once the server is ready and its
  checks have run, writes D/ready.json {"port": int, "pid": int} (the server
  child's pid) and keeps the server up until D/release exists (bounded by
  `--witness-timeout`, default 120 s), then tears it down as usual; the rerun
  receipt carries "witness": {"released": true, ...}.
  Record-time bound: `kama-llamacpp-live.py ... --server-archive A` refuses
  (exit 2, setup_error starting `provenance-`, server never executed) an archive
  whose member is sparse or whose declared size differs from the --server file's
  size, before hashing the member.

Legs:
  witness  for EACH receipt: the replay tool at --tip (from `git archive`), run with
           HOME/XDG_CACHE_HOME/TMPDIR inside --scratch and --witness-dir, writes
           ready.json; while the replay waits, this counter itself checks
             exe     sha256 of /proc/<pid>/exe equals the frozen server digest;
             listen  a LISTEN socket on 127.0.0.1/::1:<port> in /proc/net/tcp{,6}
                     whose inode is one of /proc/<pid>/fd;
             model   the `-m` argument of /proc/<pid>/cmdline hashes to the frozen
                     model digest;
             nonce   a fresh random nonce `kama witness <16 hex>` sent by this
                     counter to POST /tokenize (with_pieces) and POST /detokenize
                     round-trips (detokenized text equals the nonce, one leading
                     space allowed), and every returned piece equals the
                     counter's own decoding of `tokenizer.ggml.tokens[id]` from
                     the model this counter downloaded from the frozen URL and
                     hashed (U+2581 read as a space);
           then writes D/release; the replay must exit 0 with match true; the
           rerun receipt must say witness.released true; afterwards the pid is
           gone and the port refuses connections.
  cap      the live tool at --tip with a stub server (a 1-byte-member archive
           whose PAX header declares a 10^15-byte GNU sparse member) exits 2
           within 30 s with setup_error starting `provenance-member` and never
           executes the stub; and, as the positive control, an archive whose
           member is the stub's own bytes passes verification (the stub is
           executed, its marker written).
  newrow   corpus/SOURCES.md at --tip has a registry row, absent at --base, whose
           cells contain the README URL at commit caa8191df159f764fb0160e3d2fc6be008948aee
           (raw.githubusercontent.com/... or github.com/.../blob/...) and `/tokenize`.
met = witness (3/3) and cap and newrow.
PREDICATE (same sentence in the preregistration): a replay of each of the three
committed v5 b11909 receipts holds its rerun server up for an outside observer,
which finds the frozen llama-server binary executing as the listener of the
announced port with the frozen model, round-trips a fresh nonce through
/tokenize and /detokenize against the model's own vocabulary, and sees the
server gone after release; the live tool refuses a sparse or size-mismatched
archive member before hashing it; and the tokenize surface is a source row;
witness=1 cap=1 newrow=1.

Output: `witness=0|1 cap=0|1 newrow=0|1 witnessed=N/3 met=True|False`, then
`detail:` lines. Exit 0 met, 1 not met, 2 could not evaluate (git failure).
Read-only on --repo; everything else lives under --scratch and is removed on exit.
Needs network access to github.com and huggingface.co, and Linux /proc.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import secrets
import shutil
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
MODEL_SHA = "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256e"
README_COMMIT = "caa8191df159f764fb0160e3d2fc6be008948aee"
README_URLS = (f"raw.githubusercontent.com/ggml-org/llama.cpp/{README_COMMIT}/tools/server/README.md",
               f"github.com/ggml-org/llama.cpp/blob/{README_COMMIT}/tools/server/README.md")
BASE = "438127bc01ff3b99f98468549d58046f932490ef"
RECEIPTS = tuple(f".ufo/waves/round-48/c2/live/receipt-{n}.json" for n in (1, 2, 3))
REPLAY = "tools/kama-live-replay.py"
LIVE = "tools/kama-llamacpp-live.py"
READY_WAIT = 600     # seconds for ready.json (the replay downloads ~75 MB first)
EXIT_WAIT = 180      # seconds for the replay to finish after release


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


def pid_alive(pid):
    try:
        with open(f"/proc/{pid}/stat") as fh:
            state = fh.read().rsplit(")", 1)[1].split()[0]
        return state not in ("Z", "X")
    except (OSError, IndexError):
        return False


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


def observe(pid, port, vocab, probs):
    """The counter's own witness of a running server; appends problems."""
    exe = sha_file(f"/proc/{pid}/exe")
    if exe != SERVER_SHA:
        probs.append(f"exe sha256 {exe} is not the frozen server")
    li = listen_inodes(port)
    if not li or not (li & pid_socket_inodes(pid)):
        probs.append(f"no LISTEN socket on {port} owned by pid {pid} (inodes {sorted(li)})")
    try:
        with open(f"/proc/{pid}/cmdline", "rb") as fh:
            argv = [a.decode("utf-8", "replace") for a in fh.read().split(b"\0")]
        mpath = argv[argv.index("-m") + 1]
        if not os.path.isabs(mpath):
            mpath = os.path.join(os.readlink(f"/proc/{pid}/cwd"), mpath)
        if sha_file(mpath) != MODEL_SHA:
            probs.append(f"-m {mpath} does not hash to the frozen model")
    except (OSError, ValueError, IndexError) as exc:
        probs.append(f"cmdline unreadable: {exc}")
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
    return nonce


def witness_one(tree, rpath, S, tag, env, vocab, detail):
    work, wd = os.path.join(S, f"work-{tag}"), os.path.join(S, f"wd-{tag}")
    os.makedirs(wd)
    outj = os.path.join(S, f"{tag}.json")
    log = open(os.path.join(S, f"{tag}.log"), "wb")
    p = subprocess.Popen([sys.executable, os.path.join(tree, REPLAY), "--receipt", rpath, "--work", work,
                          "--out", outj, "--witness-dir", wd], env=env, cwd=tree, stdout=log, stderr=log)
    probs, ready, t0 = [], None, time.monotonic()
    try:
        while time.monotonic() - t0 < READY_WAIT and p.poll() is None:
            ready = load(os.path.join(wd, "ready.json"))
            if isinstance(ready, dict):
                break
            time.sleep(0.2)
        if not isinstance(ready, dict) or not isinstance(ready.get("pid"), int) \
                or not isinstance(ready.get("port"), int):
            probs.append(f"no ready.json (replay exit {p.poll()})")
        else:
            pid, port = ready["pid"], ready["port"]
            nonce = observe(pid, port, vocab, probs)
        with open(os.path.join(wd, "release"), "w") as fh:
            fh.write("released by round49 counter\n")
        try:
            code = p.wait(timeout=EXIT_WAIT)
        except subprocess.TimeoutExpired:
            p.kill()
            code = None
        j = load(outj)
        if code != 0 or not isinstance(j, dict) or j.get("match") is not True:
            probs.append(f"replay exit {code} match {j.get('match') if isinstance(j, dict) else None} "
                         f"refused {j.get('refused') if isinstance(j, dict) else None}")
        rr = load(j.get("rerun_receipt")) if isinstance(j, dict) and j.get("rerun_receipt") else None
        if not (isinstance(rr, dict) and isinstance(rr.get("witness"), dict)
                and rr["witness"].get("released") is True):
            probs.append("rerun receipt does not record witness.released true")
        if isinstance(ready, dict) and isinstance(ready.get("pid"), int):
            if pid_alive(ready["pid"]) or not port_refuses(ready["port"]):
                probs.append("server still alive or port still accepting after the replay exited")
            elif not probs:
                detail.append(f"witness {tag}: pid {ready['pid']} port {ready['port']} exe+listen+model ok, "
                              f"nonce {nonce!r} round-tripped")
    finally:
        if p.poll() is None:
            p.kill()
            p.wait()
        log.close()
    for pr in probs:
        detail.append(f"witness {tag}: {pr}")
    return not probs


def sparse_archive(path, member):
    with tarfile.open(path, "w:gz", format=tarfile.PAX_FORMAT) as tf:
        ti = tarfile.TarInfo(member)
        ti.size = 1
        ti.mode = 0o755
        ti.pax_headers = {"GNU.sparse.map": "0,1", "GNU.sparse.major": "1", "GNU.sparse.minor": "0",
                          "GNU.sparse.realsize": str(10 ** 15)}
        tf.addfile(ti, io.BytesIO(b"A"))


def cap_leg(tree, S, env, model, detail):
    d = os.path.join(S, "cap")
    os.makedirs(os.path.join(d, "rel"))
    marker = os.path.join(d, "EXECUTED")
    srv = os.path.join(d, "rel", "llama-server")
    with open(srv, "w") as fh:
        fh.write(f"#!/bin/sh\necho executed > '{marker}'\nexit 3\n")
    os.chmod(srv, 0o755)
    bomb, good = os.path.join(d, "bomb.tar.gz"), os.path.join(d, "good.tar.gz")
    sparse_archive(bomb, "rel/llama-server")
    with tarfile.open(good, "w:gz") as tf:
        tf.add(srv, arcname="rel/llama-server")
    ok = True
    for name, arc, bad in (("sparse-1e15", bomb, True), ("member-is-server-control", good, False)):
        if os.path.exists(marker):
            os.unlink(marker)
        outr = os.path.join(d, f"{name}.json")
        argv = [sys.executable, os.path.join(tree, LIVE), "--server", srv, "--model", model,
                "--model-sha256", MODEL_SHA, "--ready-timeout", "5", "--out", outr,
                "--server-asset-url", "https://example.invalid/rel.tar.gz", "--server-asset-sha256", sha_file(arc),
                "--server-member", "rel/llama-server", "--model-url", MODEL_URL, "--server-archive", arc]
        t0 = time.monotonic()
        try:
            p = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=tree, timeout=30)
            code = p.returncode
        except subprocess.TimeoutExpired:
            code = None
        dt = time.monotonic() - t0
        rec = load(outr)
        err = rec.get("setup_error") if isinstance(rec, dict) else None
        executed = os.path.exists(marker)
        if bad:
            good_case = code == 2 and isinstance(err, str) and err.startswith("provenance-member") and not executed
        else:
            good_case = executed and not (isinstance(err, str) and err.startswith("provenance-"))
        detail.append(f"cap {name}: exit {code} setup_error {err!r} executed={executed} seconds={dt:.1f} "
                      f"{'ok' if good_case else 'FAIL'}")
        ok = ok and good_case
    return ok


def newrow_leg(repo, tip, detail):
    def rows(rev):
        p = git(repo, "show", f"{rev}:corpus/SOURCES.md", check=False)
        if p.returncode != 0:
            return set()
        return {ln for ln in p.stdout.decode("utf-8", "replace").split("\n")
                if ln.lstrip(" ")[:3] == "| S" and ln.lstrip(" ")[3:4].isdigit()}
    new = rows(tip) - rows(BASE)
    hit = [ln for ln in new if any(u in ln for u in README_URLS) and "/tokenize" in ln]
    detail.append(f"newrow: {len(new)} rows new since base; {len(hit)} name the README at {README_COMMIT[:12]} "
                  f"and /tokenize: {[ln[:8] for ln in hit]}")
    return bool(hit)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", required=True, help="lane clone (read-only)")
    ap.add_argument("--tip", required=True, help="full commit to measure")
    ap.add_argument("--scratch", default=None, help="scratch dir (default: TMPDIR)")
    ap.add_argument("--out", default=None, help="also write the receipt here")
    a = ap.parse_args(argv)
    root = a.scratch or tempfile.gettempdir()
    os.makedirs(root, exist_ok=True)
    S = tempfile.mkdtemp(prefix="r49c1-", dir=root)
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
        env = dict(os.environ)
        for k, sub in (("HOME", "home"), ("XDG_CACHE_HOME", "home/.cache"), ("TMPDIR", "tmp")):
            dd = os.path.join(S, sub)
            os.makedirs(dd, exist_ok=True)
            env[k] = dd
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
        witnessed = 0
        if vocab is not None and os.path.isfile(os.path.join(tree, REPLAY)):
            for n, path in enumerate(RECEIPTS, 1):
                if not os.path.isfile(os.path.join(tree, path)):
                    detail.append(f"witness: {path} absent at tip")
                    continue
                witnessed += witness_one(tree, os.path.join(tree, path), S, f"w{n}", env, vocab, detail)
        wl = witnessed == len(RECEIPTS)
        cl = (os.path.isfile(os.path.join(tree, LIVE)) and vocab is not None
              and cap_leg(tree, S, env, model, detail))
        nl = newrow_leg(a.repo, tip, detail)
        met = wl and cl and nl
        lines = [f"tip={tip}",
                 f"witness={int(wl)} cap={int(cl)} newrow={int(nl)} witnessed={witnessed}/{len(RECEIPTS)} met={met}"]
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
