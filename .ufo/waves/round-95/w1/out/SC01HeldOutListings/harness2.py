#!/usr/bin/env python3
"""SC01HeldOutListings - held-out router listing shapes for kama round-95 C1.

Stubs only: one lane-owned HTTP listener on a free 127.0.0.1 port per shape.
Never touches 127.0.0.1:1234.

Shapes (seat spec H1-H7 + held-out neighbours that stress the COUNT-DERIVED
limit, i.e. work that is not proportional to the candidate count):
  H1  8 slow + 8 valid interleaved
  H2  2048 entries naming 64 distinct slow files
  H3  one entry naming the same slow path through 8 flag spellings
  H3b one entry naming 8 DISTINCT slow paths (memo -> 8 parses, ncand = 1)
  H3c one entry naming 20 DISTINCT slow paths (work 20x the candidate count)
  H4  missing file listed first and slow last
  H5  valid file with zero-padded trailing slack next to a same-size invalid file
  H6  entries carry status.value = "loading" beside unloaded candidates
  H7  an entry whose status.args names a relative path
  H8  one entry naming a file whose header is a huge string array
      (MAX_STEPS under-counts that path: steps ~ n/64, work ~ n iterations)
"""
import json, os, struct, subprocess, sys, threading, time, http.server
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORK = HERE / "work"
FX = WORK / "fx"
PROBES = {
    "r95": HERE / "r95-probe.sh",      # f6325660 tools/kama-probe.sh (M1)
    "base": HERE / "base-probe.sh",    # 2011161d tools/kama-probe.sh (round-94 base)
}
CAP = 4194304
PROPS = b'{"role":"router","models_autoload":true}'
TENSORS = 600_000


def gguf(n_tensors, elems, with_data, pad=0):
    out = [b"GGUF", struct.pack("<I", 3), struct.pack("<QQ", n_tensors, 0)]
    off = 0
    for i in range(n_tensors):
        name = b"t%07d" % i
        out.append(struct.pack("<Q", len(name)) + name + struct.pack("<IQIQ", 1, elems, 0, off))
        off += (elems * 4 + 31) // 32 * 32
    head = b"".join(out)
    p = (len(head) + 31) // 32 * 32 - len(head)
    body = head + b"\0" * p + (b"\0" * off if with_data else b"\0" * 16)
    if pad:
        body += b"\0" * pad
    return body


def gguf_string_array(n_strings):
    """GGUF v3, 0 tensors, 1 KV whose value is an array of n_strings strings.

    The parser's skip_strings() reads the length prefixes from a 1 MiB window
    (one step per MiB) and adds n//64 steps at the end, so the loop runs n
    iterations for ~n/64 counted steps.
    """
    out = [b"GGUF", struct.pack("<I", 3), struct.pack("<QQ", 0, 1)]
    key = b"tokenizer.ggml.tokens"
    out.append(struct.pack("<Q", len(key)) + key)
    out.append(struct.pack("<I", 9))        # type: array
    out.append(struct.pack("<I", 8))        # element type: string
    out.append(struct.pack("<Q", n_strings))
    out.append(b"".join(struct.pack("<Q", 0) for _ in range(n_strings)))
    head = b"".join(out)
    p = (len(head) + 31) // 32 * 32 - len(head)
    return head + b"\0" * p


class Stub:
    def __init__(self, body):
        self.body = body
        stub = self

        class H(http.server.BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.0"

            def log_message(self, *a):
                pass

            def do_GET(self):
                p = self.path.split("?")[0]
                if p == "/v1/models":
                    body, code = stub.body, 200
                elif p == "/props":
                    body, code = PROPS, 200
                elif p == "/health":
                    body, code = b'{"status":"ok"}', 200
                else:
                    body, code = b'{"error":"not found"}', 404
                self.send_response(code)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                try:
                    self.wfile.write(body)
                except OSError:
                    pass

        self.srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
        self.srv.daemon_threads = True
        self.port = self.srv.server_address[1]
        self.t = threading.Thread(target=self.srv.serve_forever, daemon=True)

    def __enter__(self):
        self.t.start()
        dl = time.time() + 10
        while time.time() < dl:
            try:
                with socket_create(self.port):
                    return self
            except OSError:
                time.sleep(0.05)
        raise RuntimeError("stub never accepted")

    def __exit__(self, *a):
        self.srv.shutdown()
        self.srv.server_close()


def socket_create(port):
    import socket
    return socket.create_connection(("127.0.0.1", port), timeout=1)


def load1():
    try:
        return open("/proc/loadavg").read().split()[0]
    except OSError:
        return "?"


def run_probe(probe: Path, port: int, timeout=1800):
    env = dict(os.environ, TMPDIR=str(WORK))
    t0 = time.monotonic()
    p = subprocess.run(["bash", str(probe), "check", "--port", str(port), "--expect", "good",
                        "--timeout", "5", "--connect-timeout", "2", "--json"],
                       capture_output=True, timeout=timeout, env=env, cwd=str(WORK))
    dt = time.monotonic() - t0
    try:
        row = json.loads(p.stdout.decode())["rows"][0]
        return row.get("verdict"), row.get("reason"), round(dt, 2), p.returncode, ""
    except Exception as e:
        return f"unparsed", "-", round(dt, 2), p.returncode, (p.stderr.decode()[-300:] + "|" + str(e))


def body_of(entries):
    data = [{"id": e.get("id", "good"), "status": e.get("status")} for e in entries]
    b = json.dumps({"object": "list", "data": data}, separators=(",", ":")).encode()
    assert len(b) < CAP, len(b)
    return b


def grade(shape, entries, note=""):
    b = body_of(entries)
    out = {"shape": shape, "n_entries": len(entries), "note": note, "body_bytes": len(b)}
    for which in ("r95", "base"):
        with Stub(b) as st:
            v, r, dt, rc, err = run_probe(PROBES[which], st.port)
        out[which] = {"verdict": v, "reason": r, "seconds": dt, "rc": rc, "err": err}
        out["load1_" + which] = load1()
    out["agree"] = (out["r95"]["verdict"], out["r95"]["reason"]) == (out["base"]["verdict"], out["base"]["reason"])
    return out


def main():
    only = sys.argv[1:] or None
    WORK.mkdir(parents=True, exist_ok=True)
    FX.mkdir(exist_ok=True)
    slow = []
    for k in range(64):
        p = FX / f"slow_{k}.gguf"
        if not p.exists():
            p.write_bytes(gguf(TENSORS, 1, False))
        slow.append(str(p))
    ok = FX / "ok.gguf"
    if not ok.exists():
        ok.write_bytes(gguf(1, 32, True))
    ok2 = FX / "ok2.gguf"
    if not ok2.exists():
        ok2.write_bytes(gguf(2, 32, True))
    exe = str(ok)
    results = []

    def add(shape, entries, note=""):
        if only and not any(shape.startswith(o) for o in only):
            return
        rec = grade(shape, entries, note)
        results.append(rec)
        print(json.dumps(rec), flush=True)

    # H1: 8 slow + 8 valid interleaved
    e = []
    for k in range(8):
        e.append({"status": {"value": "unloaded", "args": [exe, "-m", slow[k]]}})
        e.append({"status": {"value": "unloaded", "args": [exe, "-m", str(ok2)]}})
    add("H1-slow8-ok8-interleaved", e)

    # H2: 2048 entries naming 64 distinct slow files
    e = [{"status": {"value": "unloaded", "args": [exe, "-m", slow[i % 64]]}} for i in range(2048)]
    add("H2-2048-entries-64-slow", e)

    # H3: one entry naming the SAME slow path through 8 flag spellings
    p = slow[0]
    args = [exe]
    for fl in ("-m", "--model", "-mm", "--mmproj", "-md", "--model-draft"):
        args += [fl, p]
    args += ["--model=" + p]
    add("H3-one-entry-8-flags-same-path", [{"status": {"value": "unloaded", "args": args}}],
        note="same path, 8 spellings -> one memo entry, ncand=1")

    # H3b: one entry naming 8 DISTINCT slow paths
    args = [exe]
    for k in range(8):
        args += ["-m", slow[k]]
    add("H3b-one-entry-8-distinct-slow-paths", [{"status": {"value": "unloaded", "args": args}}],
        note="ncand=1, 8 distinct parses")

    # H3c: one entry naming 20 DISTINCT slow paths
    args = [exe]
    for k in range(20):
        args += ["-m", slow[k]]
    add("H3c-one-entry-20-distinct-slow-paths", [{"status": {"value": "unloaded", "args": args}}],
        note="ncand=1, 20 distinct parses; limit = 20+15*1 = 35 s")

    # H4: missing file listed first and slow last
    missing = str(FX / "absent" / "missing.gguf")
    e = [{"status": {"value": "unloaded", "args": [exe, "-m", missing]}},
         {"status": {"value": "unloaded", "args": [exe, "-m", slow[0]]}}]
    add("H4-missing-first-slow-last", e)

    # H5: valid file with zero-padded trailing slack next to a same-size invalid file
    valid = gguf(1, 32, True)
    padded = FX / "padded_valid.gguf"
    padded.write_bytes(valid + b"\0" * 4096)
    size = padded.stat().st_size
    inv = FX / "same_size_invalid.gguf"
    inv.write_bytes(b"NOTAGGUF" + b"\0" * (size - 8))
    assert inv.stat().st_size == size
    e = [{"status": {"value": "unloaded", "args": [exe, "-m", str(padded)]}},
         {"status": {"value": "unloaded", "args": [exe, "-m", str(inv)]}}]
    add("H5-padded-valid-next-same-size-invalid", e, note=f"both {size} bytes")

    # H6: entries carry status.value = "loading" beside unloaded candidates
    e = [{"status": {"value": "loading", "args": [exe, "-m", slow[1]]}},
         {"status": {"value": "unloaded", "args": [exe, "-m", slow[0]]}}]
    add("H6-loading-beside-unloaded", e)

    # H7: entry whose status.args names a relative path
    add("H7-relative-path-in-args",
        [{"status": {"value": "unloaded", "args": [exe, "-m", "relmodel.gguf"]}}],
        note="relative path -> undecidable by the round-89 rule")

    # H8: one entry naming a file whose header is a huge string array
    sa = FX / "strarray.gguf"
    if not sa.exists():
        sa.write_bytes(gguf_string_array(5_000_000))
    add("H8-one-entry-huge-string-array",
        [{"status": {"value": "unloaded", "args": [exe, "-m", str(sa)]}}],
        note="MAX_STEPS counts n/64 for the string array, work is n iterations")

    (HERE / "results2.json").write_text(json.dumps(results, indent=1))
    print(json.dumps({"stage": "done", "n": len(results)}), flush=True)


if __name__ == "__main__":
    main()
