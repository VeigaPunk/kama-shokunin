#!/usr/bin/env python3
"""observe-witness.py - X1Observe (round 49) independent outside observer.

Round 49, seat X1Observe: written from the frozen witness contract
(round49-replay-witness-audit.py docstring, round-49 preregistration) and the
llama.cpp server README at caa8191d - NOT from the C1 counter's code - so the
counter's verdicts can be compared against a second, independently written
observer. Nothing here is imported from the lane.

Contract observed (what the live tool promises, which this observer never trusts):
  tools/kama-llamacpp-live.py --witness-dir D, once the rerun server is ready
  and its own checks ran, writes D/ready.json {schema "kama-live-witness/v1",
  port, pid of the llama-server child} and keeps the server up until D/release
  exists.

Checks made here, from outside the replay process:
  ready    ready.json parses, carries the promised schema, int port and int pid
  exe      sha256 of /proc/<pid>/exe equals the frozen b11909 llama-server digest
  listen   a LISTEN socket on <port> (127.0.0.1 or ::1) in /proc/net/tcp{,6}
           has an inode that is one of /proc/<pid>/fd (corroborated by `ss -ltnp`)
  model    the `-m` argument of /proc/<pid>/cmdline names a file whose sha256
           equals the frozen stories260K.gguf digest
  nonce    a fresh nonce `kama witness <16 hex>` is POSTed to /tokenize
           (with_pieces) and POSTed back to /detokenize: the detokenised text
           equals the nonce and every returned piece equals this observer's own
           decoding of tokenizer.ggml.tokens[id] read from the model file on the
           child's own command line (U+2581 read as a space; a <0xNN> byte token
           as that byte) - no lane code and no server helper is consulted
  after    D/release is written only after the observations above; then the pid
           is gone (or, if reused, has a different starttime) and the port
           refuses connections

Writes the observation to --out (JSON) and exits 0 only when every check passed,
1 when a check failed, 2 when no ready.json appeared before --ready-timeout.
Deps: python3 stdlib; `ss` is optional corroboration.
"""
from __future__ import annotations

import argparse
import atexit
import hashlib
import http.client
import json
import os
import re
import secrets
import socket
import struct
import subprocess
import sys
import time

FROZEN_SERVER_SHA = "35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0"
FROZEN_MODEL_SHA = "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"
READY_SCHEMA = "kama-live-witness/v1"
SCHEMA = "x1observe-witness/v1"
CHUNK = 1 << 20
BYTE_TOKEN = re.compile(r"<0x([0-9A-Fa-f]{2})>")


def utc_now():
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + ".%03dZ" % (
        int(time.time() * 1000) % 1000)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(CHUNK), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------- GGUF vocab
_GGUF_SCALAR = {0: ("B", 1), 1: ("b", 1), 2: ("H", 2), 3: ("h", 2), 4: ("I", 4),
                5: ("i", 4), 6: ("f", 4), 7: ("?", 1), 10: ("Q", 8),
                11: ("q", 8), 12: ("d", 8)}


def _gstr(fh):
    n = struct.unpack("<Q", fh.read(8))[0]
    return fh.read(n).decode("utf-8", "replace")


def _gval(fh, t):
    if t == 8:
        return _gstr(fh)
    if t == 9:
        et = struct.unpack("<I", fh.read(4))[0]
        n = struct.unpack("<Q", fh.read(8))[0]
        return [_gval(fh, et) for _ in range(n)]
    fmt, size = _GGUF_SCALAR[t]
    return struct.unpack("<" + fmt, fh.read(size))[0]


def gguf_meta(path):
    """Read a GGUF file's metadata key/value block (no tensor data)."""
    with open(path, "rb") as fh:
        if fh.read(4) != b"GGUF":
            raise ValueError("not-a-gguf-file")
        version = struct.unpack("<I", fh.read(4))[0]
        fh.read(8)  # tensor count: unneeded
        n_kv = struct.unpack("<Q", fh.read(8))[0]
        meta = {}
        for _ in range(n_kv):
            key = _gstr(fh)
            t = struct.unpack("<I", fh.read(4))[0]
            meta[key] = _gval(fh, t)
    return version, meta


def my_piece(token):
    """This observer's own decoding of one GGUF vocabulary string."""
    m = BYTE_TOKEN.fullmatch(token)
    if m:
        return ("bytes", bytes([int(m.group(1), 16)]))
    return ("text", token.replace("\u2581", " "))


def observed_piece(piece):
    if isinstance(piece, str):
        return ("text", piece)
    if isinstance(piece, list) and all(isinstance(b, int) for b in piece):
        return ("bytes", bytes(piece))
    return ("other", piece)


# ------------------------------------------------------------- /proc readers
def listen_inodes(port):
    """(inode_str, family, local_hex) for every LISTEN row on `port`."""
    rows = []
    for path, fam in (("/proc/net/tcp", "v4"), ("/proc/net/tcp6", "v6")):
        try:
            with open(path) as fh:
                lines = fh.read().splitlines()[1:]
        except OSError:
            continue
        for line in lines:
            parts = line.split()
            if len(parts) < 10 or parts[3] != "0A":  # 0A == TCP_LISTEN
                continue
            try:
                addr_hex, port_hex = parts[1].rsplit(":", 1)
                if int(port_hex, 16) != port:
                    continue
            except ValueError:
                continue
            rows.append({"inode": parts[9], "family": fam,
                         "local_hex": addr_hex, "uid": parts[7],
                         "src": path})
    return rows


def pid_socket_inodes(pid):
    out = set()
    try:
        fds = os.listdir(f"/proc/{pid}/fd")
    except OSError:
        return out
    for fd in fds:
        try:
            target = os.readlink(f"/proc/{pid}/fd/{fd}")
        except OSError:
            continue
        if target.startswith("socket:[") and target.endswith("]"):
            out.add(target[len("socket:["):-1])
    return out


def pid_starttime(pid):
    try:
        with open(f"/proc/{pid}/stat", "rb") as fh:
            data = fh.read().decode("utf-8", "replace")
    except OSError:
        return None
    return data[data.rindex(")") + 2:].split()[19]  # field 22 overall


def pid_cmdline(pid):
    try:
        with open(f"/proc/{pid}/cmdline", "rb") as fh:
            raw = fh.read()
    except OSError:
        return []
    return [a.decode("utf-8", "replace") for a in raw.split(b"\0") if a]


def ss_listen(port):
    """`ss -ltnp` corroboration: the row for our port and the pids it names."""
    try:
        p = subprocess.run(["ss", "-ltnp"], capture_output=True, text=True,
                           timeout=10)
    except (OSError, subprocess.SubprocessError) as exc:
        return {"error": type(exc).__name__}
    rows = []
    for line in p.stdout.splitlines():
        parts = line.split()
        # ss -ltnp columns: State Recv-Q Send-Q Local:Port Peer:Port Process
        if len(parts) < 5 or not parts[3].endswith(f":{port}"):
            continue
        pids = re.findall(r"pid=(\d+)", line)
        rows.append({"line": line.strip(), "local": parts[3],
                     "pids": [int(x) for x in pids]})
    return {"rows": rows, "exit": p.returncode, "command": "ss -ltnp"}


# ---------------------------------------------------------------- HTTP calls
def post_json(port, path, obj, timeout=10.0):
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=timeout)
    try:
        conn.request("POST", path, json.dumps(obj),
                     {"Content-Type": "application/json"})
        resp = conn.getresponse()
        body = resp.read()
        return {"status": resp.status,
                "body": body.decode("utf-8", "replace"),
                "content_type": resp.getheader("Content-Type")}
    finally:
        conn.close()


def wait_ready(wdir, timeout):
    ready_path = os.path.join(wdir, "ready.json")
    t0 = time.monotonic()
    while time.monotonic() - t0 < timeout:
        try:
            with open(ready_path) as fh:
                return json.load(fh), round((time.monotonic() - t0) * 1000)
        except FileNotFoundError:
            time.sleep(0.01)
        except (OSError, ValueError):
            time.sleep(0.01)  # written via os.replace; retry a torn read
    return None, round((time.monotonic() - t0) * 1000)


def port_refuses(port, timeout=2.0):
    for fam, addr in ((socket.AF_INET, ("127.0.0.1", port)),
                      (socket.AF_INET6, ("::1", port))):
        try:
            s = socket.socket(fam, socket.SOCK_STREAM)
            s.settimeout(timeout)
            try:
                s.connect(addr)
            except OSError as exc:
                detail = {"family": "v4" if fam == socket.AF_INET else "v6",
                          "error": type(exc).__name__,
                          "errno": getattr(exc, "errno", None)}
                if isinstance(exc, (ConnectionRefusedError, ConnectionError)):
                    return {"refuses": True, **detail}
                last = detail
                continue
            else:
                s.close()
                return {"refuses": False, "connected": True}
            finally:
                try:
                    s.close()
                except OSError:
                    pass
        except OSError:
            continue
    return {"refuses": True, "error": "no-connect-attempt-succeeded"}


# -------------------------------------------------------------------- checks
def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--witness-dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--receipt", default=None, help="lane receipt being replayed (annotation only)")
    ap.add_argument("--expect-server-sha", default=FROZEN_SERVER_SHA)
    ap.add_argument("--expect-model-sha", default=FROZEN_MODEL_SHA)
    ap.add_argument("--ready-timeout", type=float, default=180.0)
    ap.add_argument("--gone-timeout", type=float, default=30.0)
    a = ap.parse_args(argv)

    t_start = utc_now()
    result = {
        "schema": SCHEMA,
        "observer": {"path": os.path.abspath(__file__),
                     "sha256": sha256_file(os.path.abspath(__file__)),
                     "argv": sys.argv},
        "receipt": a.receipt,
        "witness_dir": os.path.abspath(a.witness_dir),
        "expect": {"server_sha256": a.expect_server_sha,
                   "model_sha256": a.expect_model_sha},
        "started_utc": t_start,
        "ready": None,
        "checks": [],
        "after": None,
        "verdict": None,
    }

    def add(cid, passed, observed, documented_by=None):
        entry = {"id": cid, "passed": bool(passed), "observed": observed}
        if documented_by:
            entry["documented_by"] = documented_by
        result["checks"].append(entry)

    ready, ready_ms = wait_ready(a.witness_dir, a.ready_timeout)
    result["ready_ms"] = ready_ms
    if ready is None:
        result["verdict"] = "no-ready"
        result["finished_utc"] = utc_now()
        _write(a.out, result)
        print("observe verdict=no-ready")
        return 2
    result["ready"] = ready
    pid = ready.get("pid")
    port = ready.get("port")

    def do_release():
        """Free the held server exactly once. Registered with atexit so an
        observer bug fails the observation instead of stalling the replay for
        the whole witness timeout."""
        if result.get("released_utc"):
            return
        with open(os.path.join(a.witness_dir, "release"), "w") as fh:
            fh.write(utc_now() + "\n")
        result["released_utc"] = utc_now()
    atexit.register(do_release)

    ok_types = (isinstance(pid, int) and isinstance(port, int)
                and 0 < port < 65536 and pid > 1)
    add("ready_contract", ready.get("schema") == READY_SCHEMA and ok_types,
        {"schema": ready.get("schema"), "port": port, "pid": pid},
        "frozen witness contract: ready.json {schema kama-live-witness/v1, port int, pid int of the llama-server child}")
    if not ok_types:
        result["verdict"] = "ready-malformed"
        _write(a.out, result)
        print("observe verdict=ready-malformed")
        return 1

    starttime = pid_starttime(pid)

    # exe: the binary the child is executing, read from /proc
    try:
        exe_path = os.readlink(f"/proc/{pid}/exe")
        exe_sha = sha256_file(f"/proc/{pid}/exe")
        add("exe_digest", exe_sha == a.expect_server_sha,
            {"exe": exe_path, "sha256": exe_sha},
            "proc_pid_exe(5): /proc/<pid>/exe is the executed file; its sha256 must be the frozen llama-server digest")
    except OSError as exc:
        add("exe_digest", False, {"error": type(exc).__name__,
                                  "errno": getattr(exc, "errno", None)})

    # listen: the announced port's LISTEN socket belongs to the same pid
    rows = listen_inodes(port)
    owned = sorted({r["inode"] for r in rows} & pid_socket_inodes(pid))
    ss = ss_listen(port)
    ss_pids = sorted({p for r in ss.get("rows", []) for p in r["pids"]})
    add("listen_ownership", bool(rows) and bool(owned),
        {"port": port, "listen_rows": rows, "child_socket_inodes_shared": owned,
         "ss": ss, "ss_pids": ss_pids, "ss_names_pid": pid in ss_pids},
        "the LISTEN socket on the announced port must be one of /proc/<pid>/fd (ss -ltnp corroborates)")

    # model: the -m argument of the child's own command line hashes to the frozen GGUF
    args = pid_cmdline(pid)
    model_arg = None
    for flag in ("-m", "--model"):
        if flag in args:
            i = args.index(flag)
            model_arg = args[i + 1] if i + 1 < len(args) else None
            break
    if model_arg:
        try:
            model_sha = sha256_file(model_arg)
            add("model_digest", model_sha == a.expect_model_sha,
                {"arg": model_arg, "realpath": os.path.realpath(model_arg),
                 "sha256": model_sha},
                "the frozen model file must be the one the server was started with")
        except OSError as exc:
            add("model_digest", False, {"arg": model_arg,
                                        "error": type(exc).__name__})
    else:
        add("model_digest", False, {"argv": args, "error": "no-m-argument"})

    # nonce: /tokenize(with_pieces) + /detokenize against this observer's own vocab
    nonce = "kama witness " + secrets.token_hex(8)
    result["nonce"] = nonce
    def safe_post(path, obj):
        try:
            return post_json(port, path, obj)
        except OSError as exc:
            # a witness that names a port nothing answers on must fail its
            # nonce legs, not crash the observer
            return {"status": None, "body": "", "content_type": None,
                    "error": f"{type(exc).__name__}:{exc}"}

    tok = safe_post("/tokenize", {"content": nonce, "with_pieces": True,
                                  "add_special": False, "parse_special": False})
    ids, pieces, piece_ok = [], [], []
    tok_error = None
    try:
        payload = json.loads(tok["body"])
        toks = payload["tokens"]
        for item in toks:
            ids.append(item["id"])
            pieces.append(item.get("piece"))
    except (ValueError, KeyError, TypeError) as exc:
        tok_error = f"{type(exc).__name__}:{exc}"
    vocab, vocab_model, vocab_error = None, None, None
    if model_arg and os.path.isfile(model_arg):
        try:
            _, meta = gguf_meta(model_arg)
            vocab = meta.get("tokenizer.ggml.tokens")
            vocab_model = meta.get("tokenizer.ggml.model")
        except (OSError, ValueError, struct.error, IndexError) as exc:
            vocab_error = f"{type(exc).__name__}:{exc}"
    if vocab:
        for i, (tid, piece) in enumerate(zip(ids, pieces)):
            want = my_piece(vocab[tid]) if 0 <= tid < len(vocab) else ("other", None)
            got = observed_piece(piece)
            piece_ok.append({"i": i, "id": tid, "want": _jsonable(want),
                             "got": _jsonable(got), "equal": want == got,
                             "vocab_token": vocab[tid]})
    joined = "".join(p for p in pieces if isinstance(p, str))
    # SPM marks a word start with U+2581, which decodes to a space: a nonce that
    # begins at a word boundary may come back with exactly one leading space
    # (the same allowance the detokenize check makes).
    join_ok = joined == nonce or joined == " " + nonce
    add("nonce_tokenize",
        tok["status"] == 200 and tok_error is None and bool(ids)
        and vocab_error is None and bool(piece_ok)
        and all(e["equal"] for e in piece_ok) and join_ok,
        {"status": tok["status"], "content_type": tok["content_type"],
         "pieces_joined": joined,
         "token_ids": ids,
         "pieces": [_jsonable(observed_piece(p)) for p in pieces],
         "vocab_size": len(vocab) if vocab else None,
         "vocab_model": vocab_model, "vocab_error": vocab_error,
         "tok_error": tok_error, "pieces_join_to_nonce": join_ok,
         "piece_checks": piece_ok},
        "llama.cpp tools/server README @ caa8191d POST /tokenize with_pieces: {tokens:[{id,piece}]}; every piece must equal this observer's decoding of tokenizer.ggml.tokens[id] (U+2581 as space)")

    detok = safe_post("/detokenize", {"tokens": ids})
    detok_error, content = None, None
    try:
        content = json.loads(detok["body"]).get("content")
    except (ValueError, AttributeError) as exc:
        detok_error = f"{type(exc).__name__}:{exc}"
    add("nonce_detokenize",
        detok["status"] == 200 and detok_error is None and bool(ids)
        and isinstance(content, str) and content.strip() == nonce
        and (content == nonce or content in (" " + nonce, "\n" + nonce)),
        {"status": detok["status"], "content": content,
         "exact": content == nonce, "error": detok_error},
        "llama.cpp tools/server README @ caa8191d POST /detokenize: the token ids must come back as the nonce text")

    # release: only now may the replay tear its server down
    do_release()

    # after release: pid gone (or reused with a different starttime), port refuses
    t0 = time.monotonic()
    gone_ms, gone, seen_start = None, False, None
    while time.monotonic() - t0 < a.gone_timeout:
        seen_start = pid_starttime(pid)
        if seen_start is None or seen_start != starttime:
            gone, gone_ms = True, round((time.monotonic() - t0) * 1000)
            break
        time.sleep(0.02)
    refusal = port_refuses(port)
    after = {"pid": pid, "starttime_at_witness": starttime,
             "pid_gone": gone, "pid_gone_ms": gone_ms,
             "starttime_after": seen_start,
             "port_refuses": refusal,
             "listen_rows_after": listen_inodes(port)}
    result["after"] = after
    add("pid_gone_after_release", gone, after,
        "once release exists the replay tears the child down; the witnessed pid must be gone (a reused pid is identified by a changed starttime)")

    result["finished_utc"] = utc_now()
    result["verdict"] = "ok" if all(c["passed"] for c in result["checks"]) else "fail"
    _write(a.out, result)
    failed = [c["id"] for c in result["checks"] if not c["passed"]]
    print(f"observe verdict={result['verdict']} pid={pid} port={port} "
          f"checks={len(result['checks'])} failed={failed}")
    return 0 if result["verdict"] == "ok" else 1


def _jsonable(value):
    kind, payload = value
    if kind == "bytes":
        return {"kind": "bytes", "hex": payload.hex()}
    if kind == "text":
        return {"kind": "text", "text": payload}
    return {"kind": kind, "value": repr(payload)}


def _write(path, obj):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w") as fh:
        json.dump(obj, fh, indent=1)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except BaseException:
        # an observer bug must not stall the replay: atexit already wrote release
        import traceback
        traceback.print_exc()
        sys.exit(70)
