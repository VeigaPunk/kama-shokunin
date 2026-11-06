#!/usr/bin/env python3
"""Witness harness for escaped round-89 C1 probe mutants.

Each case: a stub router serves GET /v1/models (crafted status.args + status.value),
GET /props (models_autoload), GET /health 200. The pristine M probe and the mutant probe
both run against it; a witness holds when their (verdict, reason) differ.
"""
from __future__ import annotations

import json
import os
import shutil
import socket
import struct
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

SCR = Path(__file__).resolve().parent
M = SCR / "probe-M.sh"
MUT = SCR / "mutants"
FILES = SCR / "witness" / "files"


# ---------------------------------------------------------------- GGUF builder
def u32(x):
    return struct.pack("<I", x)


def u64(x):
    return struct.pack("<Q", x)


def gguf(magic=b"GGUF", ver=3, kvs=(), tensors=(), data=b"", align=None):
    """kvs: (key bytes, type u32, raw value bytes); tensors: (name bytes, dims, type, off)."""
    body = bytearray()
    body += magic + u32(ver) + u64(len(tensors)) + u64(len(kvs))
    for key, t, val in kvs:
        body += u64(len(key)) + key + u32(t) + val
    for name, dims, tt, off in tensors:
        body += u64(len(name)) + name + u32(len(dims))
        for d in dims:
            body += u64(d)
        body += u32(tt) + u64(off)
    a = align if align else 32
    start = (len(body) + a - 1) // a * a
    body += b"\0" * (start - len(body))
    body += data
    return bytes(body)


def pad_to(data: bytes, n: int):
    return data + b"\0" * max(0, n - len(data))


def build_files():
    FILES.mkdir(parents=True, exist_ok=True)
    for old in FILES.iterdir():
        if old.is_file():
            old.chmod(0o600)
    f = {}
    # W01 magic gate: GGML magic, otherwise an empty valid header
    f["w01.ggml"] = gguf(magic=b"GGML")
    # W02 version 1
    f["w02.g1"] = gguf(ver=1)
    # W03 version 4
    f["w03.g4"] = gguf(ver=4)
    # W04 counts-fit: 24-byte header, n_kv=100001 (over MAX_KV) and over size
    f["w04.count"] = b"GGUF" + u32(3) + u64(0) + u64(100_001)
    # W05 alignment 3 (not a power of two)
    f["w05.align3"] = gguf(kvs=[(b"general.alignment", 4, u32(3))], align=None)
    # W06 five dimensions
    f["w06.nd5"] = gguf(tensors=[(b"", [1, 1, 1, 1, 1], 0, 0)], data=b"\0" * 4)
    # W07 Q4_0 with ne[0]=16 (not a multiple of the 32-element block)
    f["w07.blk"] = gguf(tensors=[(b"", [16], 2, 0)])
    # W08 non-contiguous offsets (t1 at 32, t2 at 0)
    f["w08.contig"] = gguf(tensors=[(b"a", [1], 0, 32), (b"b", [1], 0, 0)], data=b"\0" * 64)
    # W09 tensor data past EOF (needs 16 bytes, file has 8 after the aligned start)
    f["w09.eof"] = gguf(tensors=[(b"", [4], 0, 0)], data=b"\0" * 8)
    # W10 unknown tensor type 31
    f["w10.unk"] = gguf(tensors=[(b"", [1], 31, 0)])
    # W11 valid header with a 100-byte KV key of type string
    f["w11.longkey"] = gguf(kvs=[(b"x" * 100, 8, u64(0))])
    # W12/W13/W16 valid minimal: F32 scalar tensor, no KV, 32-byte aligned data
    f["w12.valid"] = gguf(tensors=[(b"", [1], 0, 0)], data=b"\0" * 4)
    f["w12b.align"] = gguf(kvs=[(b"", 0, b"\x00")],
                           tensors=[(b"", [1], 0, 0)], data=b"\0" * 4)
    f["w30.strlen"] = gguf(kvs=[(b"k", 8, u64(0))],
                           tensors=[(b"", [1], 0, 0)], data=b"\0" * 4)
    f["w31.strarr"] = gguf(kvs=[(b"k", 9, u32(8) + u64(2) + u64(0) + u64(0))],
                           tensors=[(b"", [1], 0, 0)], data=b"\0" * 4)
    # W22 budget: 0 tensors, n_kv=100001, file large enough that counts-fit passes
    hdr = b"GGUF" + u32(3) + u64(0) + u64(100_001)
    f["w22.budget"] = pad_to(hdr, 100_001 * 13 + 16)
    # W20 directory at the model path
    (FILES / "w20.dir").mkdir(exist_ok=True)
    # W21 unreadable file
    p21 = FILES / "w21.noread.gguf"
    p21.write_bytes(f["w12.valid"])
    p21.chmod(0o000)
    for name, blob in f.items():
        (FILES / name).write_bytes(blob)
    return f


# ---------------------------------------------------------------- stub server
class Stub(BaseHTTPRequestHandler):
    body = b""
    autoload = True

    def log_message(self, *_a):
        pass

    def _send(self, code, payload, ctype="application/json"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Server", "llama.cpp")
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        if self.path.startswith("/v1/models"):
            self._send(200, self.body)
        elif self.path.startswith("/props"):
            self._send(200, json.dumps({"role": "router",
                                        "models_autoload": self.autoload}).encode())
        elif self.path.startswith("/health"):
            self._send(200, b'{"status":"ok"}')
        else:
            self._send(200, b"llama.cpp stub", "text/plain")

    def do_POST(self):
        self._send(200, b'{"ok":true}')


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


def run_probe(probe, port, expect):
    argv = ["bash", str(probe), "check", "--port", str(port), "--json",
            "--timeout", "2", "--connect-timeout", "1"]
    if expect is not None:
        argv += ["--expect", expect]
    env = dict(os.environ, TMPDIR=str(SCR / "witness" / "tmp"))
    Path(env["TMPDIR"]).mkdir(parents=True, exist_ok=True)
    p = subprocess.run(argv, capture_output=True, text=True, timeout=60, env=env)
    try:
        doc = json.loads(p.stdout)
        row = (doc.get("consumers") or doc.get("rows") or doc.get("results") or [])[0]
        return row["verdict"], row.get("reason", "?")
    except Exception:
        return f"UNPARSEABLE(exit={p.returncode})", p.stdout[:120].replace("\n", " ")


def serve(entries, autoload):
    body = json.dumps({"object": "list",
                       "data": [{"id": mid, "status": st} for mid, st in entries]}).encode()
    Stub.body = body
    Stub.autoload = autoload
    port = free_port()
    srv = ThreadingHTTPServer(("127.0.0.1", port), Stub)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    return srv, port


CASES = []


def case(name, mutant, entries, autoload=True, expect=None, note=""):
    CASES.append(dict(name=name, mutant=mutant, entries=entries, autoload=autoload,
                      expect=expect, note=note))


def build_cases(f):
    P = lambda n: str(FILES / n)
    case("W01-magic", "M01-magic-off",
         [("w1", {"value": "unloaded", "args": ["/bin/bash", "--model", P("w01.ggml")]})],
         note="GGML-magic file is not loadable; M=invalid")
    case("W02-version1", "M02-version-1-accepted",
         [("w1", {"value": "unloaded", "args": ["/bin/bash", "--model", P("w02.g1")]})])
    case("W03-version4", "M03-version-4-accepted",
         [("w1", {"value": "unloaded", "args": ["/bin/bash", "--model", P("w03.g4")]})])
    case("W04-counts", "M04-counts-fit-off",
         [("w1", {"value": "unloaded", "args": ["/bin/bash", "--model", P("w04.count")]})])
    case("W05-align", "M05-alignment-power2-off",
         [("w1", {"value": "unloaded", "args": ["/bin/bash", "--model", P("w05.align3")]})])
    case("W06-nd5", "M06-ndims-5-accepted",
         [("w1", {"value": "unloaded", "args": ["/bin/bash", "--model", P("w06.nd5")]})])
    case("W07-block", "M07-block-divisibility-off",
         [("w1", {"value": "unloaded", "args": ["/bin/bash", "--model", P("w07.blk")]})])
    case("W08-contiguity", "M08-contiguity-off",
         [("w1", {"value": "unloaded", "args": ["/bin/bash", "--model", P("w08.contig")]})])
    case("W09-eof", "M09-eof-only-offset",
         [("w1", {"value": "unloaded", "args": ["/bin/bash", "--model", P("w09.eof")]})])
    case("W10-unknown-type", "M10-unknown-type-invalid",
         [("w1", {"value": "unloaded", "args": ["/bin/bash", "--model", P("w10.unk")]})])
    case("W11-longkey", "M11-long-key-forced-alignment",
         [("w1", {"value": "unloaded", "args": ["/bin/bash", "--model", P("w11.longkey")]})])
    case("W12-align-default", "M12-default-align-64",
         [("w1", {"value": "unloaded", "args": ["/bin/bash", "--model", P("w12b.align")]})])
    case("W13-block-overcount", "M13-block-overcount",
         [("w1", {"value": "unloaded", "args": ["/bin/bash", "--model", P("w12.valid")]})])
    case("W14-args0", "M14-args0-isfile-off",
         [("w1", {"value": "unloaded",
                  "args": ["/definitely/not/here/llama-server", "--model", "/missing.gguf"]})],
         note="router binary path not local to the probe -> M must not decide")
    case("W15-relative", "M15-relative-paths-parsed",
         [("w1", {"value": "unloaded", "args": ["/bin/bash", "--model", "rel/m1.gguf"]})],
         note="probe cwd is witness/tmp; rel/m1.gguf does not exist there")
    case("W16-draft", "M16-pathflags-drop-draft",
         [("w1", {"value": "unloaded",
                  "args": ["/bin/bash", "--model", P("w12.valid"),
                           "--model-draft", "/missing-draft.gguf"]})])
    case("W17-single-m", "M17-pathflags-drop-single-m",
         [("w1", {"value": "unloaded", "args": ["/bin/bash", "-m", "/missing.gguf"]})])
    case("W18-equals", "M18-equals-form-off",
         [("w1", {"value": "unloaded", "args": ["/bin/bash", "--model=/missing.gguf"]})])
    case("W19-precedence", "M19-missing-invalid-precedence",
         [("w1", {"value": "unloaded",
                  "args": ["/bin/bash", "--model", "/missing.gguf",
                           "--mmproj", P("w01.ggml")]})],
         note="file_state ordering: missing must win over invalid")
    case("W20-directory", "M20-s-isreg-off",
         [("w1", {"value": "unloaded", "args": ["/bin/bash", "--model", P("w20.dir")]})])
    case("W21-unreadable", "M21-unreadable-invalid",
         [("w1", {"value": "unloaded", "args": ["/bin/bash", "--model", P("w21.noread.gguf")]})])
    case("W22-budget", "M22-budget-invalid",
         [("w1", {"value": "unloaded", "args": ["/bin/bash", "--model", P("w22.budget")]})])
    case("W23-unloadable-autoload", "M23-autoload-only-for-unloaded",
         [("w1", {"value": "unloaded", "args": ["/bin/bash", "--model", P("w01.ggml")]})])
    case("W24-unloaded-noautoload", "M24-unloaded-ignores-autoload",
         [("w1", {"value": "unloaded", "args": ["/bin/bash", "--model", P("w12.valid")]})],
         autoload=False)
    case("W25-sleeping", "M25-sleeping-unloaded",
         [("w1", {"value": "sleeping", "args": ["/bin/bash", "--model", P("w12.valid")]})])
    case("W26-loaded-not-ok", "M26-loaded-not-ok",
         [("w1", {"value": "unloaded", "args": ["/bin/bash", "--model", P("w12.valid")]}),
          ("w2", {"value": "loaded", "args": ["/bin/bash", "--model", P("w12.valid")]})],
         expect=None)
    case("W27-down-last", "M27-down-last-wins",
         [("w1", {"value": "unloaded", "failed": True,
                  "args": ["/bin/bash", "--model", P("w12.valid")]}),
          ("w2", {"value": "unloaded", "args": ["/bin/bash", "--model", P("w12.valid")]})],
         autoload=False, expect=None)
    case("W28-loading-vs-unloadable", "M28-unloadable-before-loading",
         [("w1", {"value": "loading", "args": ["/bin/bash", "--model", P("w12.valid")]}),
          ("w2", {"value": "unloaded", "args": ["/bin/bash", "--model", P("w01.ggml")]})],
         expect=None)
    case("W30-string-length", "M30-string-length-u32",
         [("w1", {"value": "unloaded", "args": ["/bin/bash", "--model", P("w30.strlen")]})])
    case("W31-string-array", "M31-string-array-off-by-one",
         [("w1", {"value": "unloaded", "args": ["/bin/bash", "--model", P("w31.strarr")]})])
    case("W29-loading-last", "M29-loading-last-wins",
         [("w1", {"value": "loading", "args": ["/bin/bash", "--model", P("w12.valid")]}),
          ("w2", {"value": "downloading", "args": ["/bin/bash", "--model", P("w12.valid")]})],
         expect=None)


def main() -> int:
    f = build_files()
    build_cases(f)
    rows = []
    stubdir = SCR / "witness" / "stub"
    stubdir.mkdir(exist_ok=True)
    for c in CASES:
        (stubdir / f"{c['name']}.json").write_text(json.dumps(
            {"models_autoload": c["autoload"], "expect": c["expect"],
             "data": [{"id": mid, "status": st} for mid, st in c["entries"]]}, indent=1))
        srv, port = serve(c["entries"], c["autoload"])
        try:
            m = run_probe(M, port, c["expect"])
            mu = run_probe(MUT / f"{c['mutant']}.sh", port, c["expect"])
        finally:
            srv.shutdown()
            srv.server_close()
        distinct = m != mu
        rows.append((c["name"], c["mutant"], m, mu, distinct, c["note"]))
        print(f"{c['name']:28s} {c['mutant']:38s} M={m[0]}/{m[1]:28s} "
              f"mut={mu[0]}/{mu[1]:28s} distinct={int(distinct)}")
    bad = sum(1 for r in rows if not r[4])
    print(f"witness_cases={len(rows)} distinct={len(rows) - bad} non_distinct={bad}")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
