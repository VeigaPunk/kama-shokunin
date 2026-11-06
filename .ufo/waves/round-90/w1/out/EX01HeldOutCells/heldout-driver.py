#!/usr/bin/env python3
"""EX01HeldOutCells (kama r90 w1): held-out hostile listener answers, base vs M.

Runs `kama-probe.sh check --port <free> --expect ... --timeout 5` against
  base B = 99cdb4d6270455494dd27901efe84a0f3b342062 (probe sha256 c15ffca8...)
  M     = f968fb19bb2a0c2afe271bfe606f11b52d10823f (C1 measured)
Each cell is a lane-owned stub HTTP server on 127.0.0.1:0.  Both table and
--json modes are run per cell; the receipt records verdict/reason/exit,
raw control bytes in table output, JSON parseability, server-sent bytes and wall
time.  Cells are judged FIX / AGREE / HARM / LIMIT in the summary.

Probe runs that do not finish inside their per-cell budget are killed (process
group) and reported as TIMEOUT; a supplementary micro-benchmark measures the
host bash pattern-expansion cost that explains the long-id timeouts.

No hardcoded /tmp: every temp path lives under --work.
"""

import argparse
import gzip
import hashlib
import json
import os
import signal
import socket
import subprocess
import sys
import threading
import time

# ------------------------------------------------------------------ stub server


def hdr(status, reason, headers):
    lines = ["HTTP/1.1 %d %s" % (status, reason)]
    lines += ["%s: %s" % (k, v) for k, v in headers]
    return ("\r\n".join(lines) + "\r\n\r\n").encode("latin-1")


def aux_response(path):
    """Small deterministic answers for everything except the hostile /v1/models."""
    if path == "/health":
        body, ct = b'{"status":"ok"}', "application/json"
    elif path == "/props":
        body, ct = b'{"role":"model"}', "application/json"
    elif path == "/metrics":
        body, ct = b"metrics\n", "text/plain"
        return [hdr(404, "Not Found", [("Content-Type", ct),
                                       ("Content-Length", str(len(body))),
                                       ("Connection", "close")]) + body]
    else:
        body, ct = b"ok\n", "text/plain"
    return [hdr(200, "OK", [("Content-Type", ct),
                           ("Content-Length", str(len(body))),
                           ("Connection", "close")]) + body]


class Stub:
    def __init__(self, handler):
        self.handler = handler
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("127.0.0.1", 0))
        self.sock.listen(32)
        self.sock.settimeout(0.2)
        self.port = self.sock.getsockname()[1]
        self.sent = 0
        self.sent_by = {}
        self.reqs = []
        self.lock = threading.Lock()
        self.stop = threading.Event()
        self.threads = []
        self.t = threading.Thread(target=self._accept_loop, daemon=True)
        self.t.start()

    def _accept_loop(self):
        while not self.stop.is_set():
            try:
                conn, _ = self.sock.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            th = threading.Thread(target=self._serve, args=(conn,), daemon=True)
            th.start()
            with self.lock:
                self.threads.append(th)

    def _serve(self, conn):
        try:
            conn.settimeout(30)
            data = b""
            while b"\r\n\r\n" not in data and len(data) < 131072 and not self.stop.is_set():
                chunk = conn.recv(8192)
                if not chunk:
                    return
                data += chunk
            reqline = data.split(b"\r\n", 1)[0].decode("latin-1", "replace")
            parts = reqline.split(" ")
            path = parts[1] if len(parts) > 1 else "/"
            with self.lock:
                self.reqs.append(path)
            for piece in self.handler(path, self):
                if not piece:
                    continue
                mv = memoryview(piece)
                for off in range(0, len(mv), 65536):
                    part = mv[off:off + 65536]
                    conn.sendall(part)
                    with self.lock:
                        self.sent += len(part)
                        self.sent_by[path] = self.sent_by.get(path, 0) + len(part)
        except (BrokenPipeError, ConnectionResetError, socket.timeout, OSError):
            pass
        finally:
            # half-close, then drain so a large header/body block is not cut by an
            # RST while the peer is still reading (SHUT_RDWR discards queued data).
            try:
                conn.shutdown(socket.SHUT_WR)
            except OSError:
                pass
            try:
                conn.settimeout(2)
                while conn.recv(65536):
                    pass
            except OSError:
                pass
            try:
                conn.close()
            except OSError:
                pass

    def close(self):
        self.stop.set()
        try:
            self.sock.close()
        except OSError:
            pass
        for th in list(self.threads):
            th.join(1.0)


# ------------------------------------------------------------------ cells


def static_models(body, ctype="application/json", extra=(), status=200, reason="OK"):
    def handler(path, stub):
        if path != "/v1/models":
            return aux_response(path)
        headers = [("Content-Type", ctype),
                   ("Content-Length", str(len(body))),
                   ("Connection", "close")] + list(extra)
        return [hdr(status, reason, headers) + body]
    return handler


def cell_gzip_bomb():
    """(1) 64 MiB wire body, Content-Encoding: gzip, multi-member gzip of zeros.

    The wire body is exactly 64 MiB; inflated it is ~64x that, so a client that
    honoured Content-Encoding would decompress a bomb.
    """
    total = 64 * 1024 * 1024
    unit = gzip.compress(b"\0" * (1 << 20), 6)

    def handler(path, stub):
        if path != "/v1/models":
            return aux_response(path)
        headers = [("Content-Type", "application/json"),
                   ("Content-Encoding", "gzip"),
                   ("Content-Length", str(total)),
                   ("Connection", "close")]

        def gen():
            yield hdr(200, "OK", headers)
            sent = 0
            block = unit * 32
            while sent < total and not stub.stop.is_set():
                piece = block[:min(len(block), total - sent)]
                yield piece
                sent += len(piece)
        return gen()
    return handler


def cell_slow_drip(advertise=None):
    """(2) one byte every 100 ms, far longer than --timeout 5.

    advertise=None -> chunked (unknown length); a number -> Content-Length.
    """
    wire_total = advertise or 100_000_000

    def handler(path, stub):
        if path != "/v1/models":
            return aux_response(path)
        if advertise is None:
            headers = [("Content-Type", "application/json"),
                       ("Transfer-Encoding", "chunked"),
                       ("Connection", "close")]
        else:
            headers = [("Content-Type", "application/json"),
                       ("Content-Length", str(advertise)),
                       ("Connection", "close")]

        def gen():
            yield hdr(200, "OK", headers)
            for _ in range(600):
                if stub.stop.is_set():
                    return
                yield b"1\r\nx\r\n" if advertise is None else b"x"
                time.sleep(0.1)
            if advertise is None:
                yield b"0\r\n\r\n"
        return gen()
    return handler


def cell_long_id(nbytes):
    """(3) one id of nbytes; the whole body must stay near the 4 MiB cap."""
    body = b'{"data":[{"id":"' + b"A" * nbytes + b'"}]}'
    return static_models(body)


def cell_control_ids():
    """(4) U+0085, U+2028, U+202E (bidi override) and DEL inside ids."""
    ids = ["a\u0085b", "c\u2028d", "e\u202ef", "g\u007fh"]
    body = json.dumps({"data": [{"id": i} for i in ids]},
                      ensure_ascii=False).encode("utf-8")
    return static_models(body)


def cell_bom():
    """(5) a valid model list prefixed with a UTF-8 BOM."""
    body = b"\xef\xbb\xbf" + b'{"data":[{"id":"m"}]}'
    return static_models(body)


def cell_ct_tab():
    """(6) Content-Type carrying a tab."""
    return static_models(b'{"data":[{"id":"m"}]}',
                         ctype="application/json;\tcharset=utf-8")


def cell_header_bloat(n_lines=200, line_size=8192):
    """(7) many large response headers; -D is written without any cap."""
    body = b'{"data":[{"id":"m"}]}'
    hdrs = [("Content-Type", "application/json"),
            ("Content-Length", str(len(body))),
            ("Connection", "close")]
    for i in range(n_lines):
        hdrs.append(("X-Pad-%05d" % i, "A" * line_size))
    blob = hdr(200, "OK", hdrs) + body

    def handler(path, stub):
        if path != "/v1/models":
            return aux_response(path)
        return [blob]
    return handler


def cell_chunked_with_cl():
    """(8) HTTP/1.1 chunked 64 MiB while Content-Length: 64 MiB is also present."""
    total = 64 * 1024 * 1024

    def handler(path, stub):
        if path != "/v1/models":
            return aux_response(path)
        headers = [("Content-Type", "application/json"),
                   ("Transfer-Encoding", "chunked"),
                   ("Content-Length", str(total)),
                   ("Connection", "close")]

        def gen():
            yield hdr(200, "OK", headers)
            sent = 0
            while sent < total and not stub.stop.is_set():
                n = min(65536, total - sent)
                yield ("%x\r\n" % n).encode() + b"Q" * n + b"\r\n"
                sent += n
            yield b"0\r\n\r\n"
        return gen()
    return handler


def cell_keepalive_two():
    """(9) two complete answers back to back on one keep-alive connection."""
    body = b'{"data":[{"id":"m"}]}'
    resp = hdr(200, "OK", [("Content-Type", "application/json"),
                           ("Content-Length", str(len(body))),
                           ("Connection", "keep-alive")]) + body

    def handler(path, stub):
        if path != "/v1/models":
            return aux_response(path)
        return [resp, resp]
    return handler


def build_ollama_body(target=2 * 1024 * 1024, count=2048):
    """(10) a legitimate Ollama-shaped models[] list just under 2 MiB."""
    pad = 700
    body = b""
    for _ in range(12):
        entries = []
        for i in range(count):
            name = "m" if i == 0 else "model-%04d" % i
            entries.append({
                "name": name,
                "model": name + ":latest",
                "modified_at": "2026-01-01T00:00:00Z",
                "size": 123456789,
                "digest": "d" * 64,
                "details": {"format": "gguf", "family": "llama",
                            "parameter_size": "7B", "pad": "P" * pad},
            })
        body = json.dumps({"models": entries}, ensure_ascii=False).encode()
        delta = target - len(body)
        if abs(delta) < 2048:
            break
        pad = max(1, pad + delta // count)
    return body


def cell_ollama_list():
    return static_models(build_ollama_body())


# name, expect, handler factory, per-run budget seconds, note
CELLS = [
    ("cell01-gzip-bomb", "*", cell_gzip_bomb, 30,
     "64 MiB wire gzip bomb, Content-Encoding: gzip"),
    ("cell02a-drip-cl", "*", lambda: cell_slow_drip(100_000_000), 30,
     "1 byte/100 ms behind Content-Length: 100 MB"),
    ("cell02b-drip-chunked", "*", lambda: cell_slow_drip(None), 30,
     "1 byte/100 ms chunked, unknown length, --timeout 5"),
    ("cell03a-id-3.9MiB-wild", "*", lambda: cell_long_id(3_900_000), 15,
     "3.9 MiB id, body under the 4 MiB cap, wildcard expectation"),
    ("cell03b-id-3.9MiB-expect", "stories260K", lambda: cell_long_id(3_900_000), 15,
     "3.9 MiB id, under the cap, concrete expected id"),
    ("cell03c-id-60KiB-expect", "stories260K", lambda: cell_long_id(60_000), 30,
     "60 KiB id, concrete expected id (under-cap control)"),
    ("cell03d-id-4.1MiB-expect", "stories260K", lambda: cell_long_id(4_200_000), 15,
     "4.1 MiB id, body over the 4 MiB cap, concrete expected id"),
    ("cell04-control-ids", "*", cell_control_ids, 30,
     "ids carrying U+0085 / U+2028 / U+202E / DEL"),
    ("cell05-bom", "m", cell_bom, 30, "valid model list with a UTF-8 BOM"),
    ("cell06-ct-tab", "m", cell_ct_tab, 30, "Content-Type carrying a tab"),
    ("cell07-header-bloat", "m", lambda: cell_header_bloat(200, 8192), 30,
     "200 response header lines of 8 KiB (-D unbounded?)"),
    ("cell08-chunked-64MiB", "*", cell_chunked_with_cl, 30,
     "chunked 64 MiB with Content-Length also present"),
    ("cell09-keepalive-two", "m", cell_keepalive_two, 30,
     "two answers back to back on one keep-alive connection"),
    ("cell10-ollama-2MiB", "m", cell_ollama_list, 30,
     "legitimate Ollama-shaped models[] list just under 2 MiB"),
]


# ------------------------------------------------------------------ run + metrics


def analyze(out, err, mode):
    m = {
        "stdout_bytes": len(out),
        "stderr_bytes": len(err),
        "esc": out.count(b"\x1b"),
        "nel": out.count(b"\xc2\x85"),          # U+0085 as UTF-8
        "ls": out.count(b"\xe2\x80\xa8"),       # U+2028 as UTF-8
        "bidi": out.count(b"\xe2\x80\xae"),     # U+202E as UTF-8
        "del": out.count(b"\x7f"),
        "tab": out.count(b"\t"),
        "c0": sum(1 for b in out if b < 0x20 and b not in (0x0A, 0x09, 0x0D)),
        "carriage": out.count(b"\r"),
    }
    text = out.decode("utf-8", "replace")
    if mode == "json":
        try:
            doc = json.loads(text)
            m["json_ok"] = True
            rows = doc.get("rows") or []
            if rows:
                r = rows[0]
                m["verdict"] = r.get("verdict")
                m["reason"] = r.get("reason")
                sm = r.get("served_model")
                if isinstance(sm, str):
                    m["served_len"] = len(sm)
                    m["served_raw_ctl"] = any(
                        ord(c) < 0x20 or ord(c) == 0x7F or 0x80 <= ord(c) <= 0x9F
                        for c in sm)
                    m["served_raw_bidi"] = "\u202e" in sm
                    m["served_raw_ls"] = "\u2028" in sm
                    m["served_preview"] = repr(sm[:48])
                ev = r.get("evidence")
                if isinstance(ev, str):
                    m["evidence_preview"] = repr(ev[:120])
                    m["evidence_has_tab"] = "\t" in ev
                    m["evidence_len"] = len(ev)
                m["drift"] = (doc.get("summary") or {}).get("drift")
                m["exit_field"] = (doc.get("summary") or {}).get("exit")
        except Exception as exc:  # noqa: BLE001
            m["json_ok"] = False
            m["json_err"] = str(exc)[:160]
    else:
        lines = text.split("\n")
        m["lines"] = len(lines)
        row = next((ln for ln in lines if ln.startswith("cli-override | ")), None)
        if row is not None:
            parts = [p.strip() for p in row.split(" | ")]
            m["sep_count"] = row.count(" | ")
            if len(parts) > 4:
                m["verdict"] = parts[3]
                m["reason"] = parts[4]
            if len(parts) > 5:
                sm = parts[5]
                m["served_len"] = len(sm)
                m["served_preview"] = repr(sm[:48])
            if len(parts) > 6:
                ev = " | ".join(parts[6:])
                m["evidence_preview"] = repr(ev[:160])
            m["row_preview"] = repr(row[:120])
            m["row_len"] = len(row)
        for ln in lines:
            if ln.startswith("registry_rows_evaluated="):
                m["summary_line"] = ln.strip()
    return m


def run_one(probe, cell, mode, work):
    name, expect, factory, budget, note = cell
    stub = Stub(factory())
    env = dict(os.environ)
    env["TMPDIR"] = os.path.join(work, "tmp")
    env.pop("KAMA_PROBE_TMPDIR", None)
    cmd = ["bash", probe, "check", "--port", str(stub.port),
           "--expect", expect, "--timeout", "5"]
    if mode == "json":
        cmd.append("--json")
    t0 = time.monotonic()
    timed_out = False
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         env=env, start_new_session=True,
                         cwd=os.path.dirname(os.path.dirname(probe)))
    try:
        out, err = p.communicate(timeout=budget)
        rc = p.returncode
    except subprocess.TimeoutExpired:
        timed_out = True
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        out, err = p.communicate()
        rc = None
    wall = time.monotonic() - t0
    stub.close()
    m = analyze(out, err, mode)
    m.update({
        "cell": name,
        "probe": os.path.basename(os.path.dirname(os.path.dirname(probe))),
        "mode": mode,
        "port": stub.port,
        "exit": rc,
        "timed_out": timed_out,
        "budget_s": budget,
        "wall_s": round(wall, 3),
        "sent_total": stub.sent,
        "sent_models": stub.sent_by.get("/v1/models", 0),
        "requests": stub.reqs,
        "expect": expect,
        "note": note,
    })
    return m


def gz_decoded_claim():
    unit = gzip.compress(b"\0" * (1 << 20), 6)
    total = 64 * 1024 * 1024
    return (total // len(unit)) * (1 << 20)


def bash_op_scale(work):
    """Measure the host bash's pattern-expansion cost used by the probe itself.

    The probe's classify uses `C_SERVED=${C_SERVED%,}` and normalize_id uses
    `s=${s##*/}` / `s=${s%.gguf}` on every served id.  Those are the operations
    that make a long id expensive; measure them outside the probe so the cost
    can be attributed without a multi-hour probe run.
    """
    path = os.path.join(work, "big.txt")
    rows = []
    for n in (50_000, 100_000, 200_000):
        with open(path, "w") as f:
            f.write("A" * n)
        for op in ("${s##*/}", "${s%.gguf}", "${s%,}"):
            script = ("s=$(<%s); %s" % (path, "q=" + op))
            t0 = time.monotonic()
            try:
                subprocess.run(["bash", "-c", script], timeout=120,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                wall = time.monotonic() - t0
                rows.append({"op": op, "n": n, "wall_s": round(wall, 3),
                             "timeout": False})
            except subprocess.TimeoutExpired:
                rows.append({"op": op, "n": n, "wall_s": 120.0, "timeout": True})
    return rows


# ------------------------------------------------------------------ labels


def v(r):
    return r.get("verdict"), r.get("reason")


def label_cell(d):
    """d maps mode-key -> run result for one cell."""
    bt, bj = v(d["base_table"]), v(d["base_json"])
    mt, mj = v(d["m_table"]), v(d["m_json"])
    name = d["base_table"]["cell"]
    timeout = (None, None)
    if name == "cell01-gzip-bomb":
        base_bounded = bt == ("FOREIGN_SERVICE", "body-too-large") or bj == ("FOREIGN_SERVICE", "body-too-large")
        m_bounded = mt == ("FOREIGN_SERVICE", "body-too-large") and mj == ("FOREIGN_SERVICE", "body-too-large")
        if m_bounded and not base_bounded and max(d["base_table"]["sent_models"],
                                                  d["base_json"]["sent_models"]) > 8 << 20:
            return "FIX", ("M aborts the 64 MiB bomb at the cap in %.2f s (%.1f MiB sent); base "
                           "reads all %d bytes and grades %s - it never checks the size"
                           % (d["m_table"]["wall_s"], d["m_table"]["sent_models"] / 1048576.0,
                              d["base_table"]["sent_models"], bt))
        return "HARM", "gzip bomb handling diverged: %s/%s vs %s/%s" % (bt, bj, mt, mj)
    if name == "cell02a-drip-cl":
        if mt == ("FOREIGN_SERVICE", "body-too-large") and mt == mj \
                and d["m_table"]["wall_s"] < 1.0 and bt == bj == ("DEAD", "timeout"):
            return "FIX", ("M refuses the advertised 100 MB answer at the cap in <1 s; base "
                           "spends the whole 5 s budget and reports DEAD/timeout")
        return "HARM", "advertised-size drip diverged: %s/%s vs %s/%s" % (bt, bj, mt, mj)
    if name == "cell02b-drip-chunked":
        if bt == bj == mt == mj == ("DEAD", "timeout"):
            return "AGREE", "both time out at --timeout 5 (no advertised length to cap)"
        return "HARM", "chunked drip diverged: %s/%s vs %s/%s" % (bt, bj, mt, mj)
    if name in ("cell03a-id-3.9MiB-wild", "cell03b-id-3.9MiB-expect",
                "cell03d-id-4.1MiB-expect"):
        base_hang = d["base_table"]["timed_out"] and d["base_json"]["timed_out"]
        m_hang = d["m_table"]["timed_out"] and d["m_json"]["timed_out"]
        m_bound = mt == ("FOREIGN_SERVICE", "body-too-large") and mt == mj
        if name == "cell03d-id-4.1MiB-expect" and base_hang and m_bound:
            return "FIX", ("M refuses the 4.2 MB body at the cap in <1 s; base never finishes "
                           "inside %d s even though the id is only a few MB"
                           % d["base_table"]["budget_s"])
        if base_hang and m_hang:
            return "LIMIT", ("neither probe finishes inside %d s on this under-cap id; bash "
                             "pattern expansion is quadratic in the id length"
                             % d["base_table"]["budget_s"])
        if bt[0] == mt[0] and not (base_hang or m_hang):
            return "AGREE", "both completed with the same verdict %s" % (bt,)
        return "HARM", "long-id handling diverged: %s vs %s (timeouts %s/%s)" % (
            bt, mt, d["base_table"]["timed_out"], d["m_table"]["timed_out"])
    if name == "cell03c-id-60KiB-expect":
        if bt[0] == mt[0] and not (d["base_table"]["timed_out"] or d["m_table"]["timed_out"]):
            return "AGREE", "both complete on a 60 KiB id with verdict %s" % (bt,)
        return "HARM", "60 KiB id diverged: %s vs %s" % (bt, mt)
    if name == "cell04-control-ids":
        base_raw = d["base_table"]["nel"] > 0 or d["base_table"]["del"] > 0
        m_safe = d["m_table"]["nel"] == 0 and d["m_table"]["del"] == 0
        if base_raw and m_safe:
            if d["base_table"]["bidi"] > 0 and d["m_table"]["bidi"] > 0:
                return "FIX", ("base table carries raw U+0085/DEL, M escapes them; LIMIT: "
                               "U+2028/U+202E stay raw in both table outputs")
            return "FIX", "base table carries raw U+0085/DEL, M escapes them"
        return "HARM", "id sanitization diverged"
    if name == "cell05-bom":
        if bt == mt:
            return "AGREE", "both reject a BOM-prefixed model list as %s" % (bt,)
        return "HARM", "BOM handling diverged: %s vs %s" % (bt, mt)
    if name == "cell06-ct-tab":
        base_forged = (d["base_table"].get("sep_count", 0) > d["m_table"].get("sep_count", 0)
                       or d["base_table"].get("tab", 0) > 0
                       or d["base_json"].get("evidence_has_tab", False))
        m_clean = (d["m_table"].get("sep_count") == 6
                   and not d["m_json"].get("evidence_has_tab", False))
        if base_forged and m_clean:
            return "FIX", ("base's Content-Type tab splits the table row into 8 columns "
                           "(sep_count=7) and reaches the JSON evidence; M strips it "
                           "(sep_count=6)")
        if not base_forged and m_clean:
            return "AGREE", "neither output carries the tab"
        return "HARM", "tab handling diverged"
    if name == "cell07-header-bloat":
        if bt[0] == mt[0] == "MODEL_OK":
            return "AGREE", "both accept the header block; curl's 300 KiB cap not reached"
        ev = (d["base_table"].get("evidence_preview") or "")
        if bt == mt == ("NOT_HTTP", "connection-reset") and "Too large response headers" in ev:
            return "AGREE", ("curl's own 300 KiB total-header cap (307200 B) aborts the 1.6 MiB "
                             "block in both; the probe reports NOT_HTTP/connection-reset but its "
                             "evidence names 'Too large response headers: 311954 > 307200'. -D is "
                             "not unbounded because curl stops the transfer")
        return "HARM", "header bloat diverged: %s vs %s" % (bt, mt)
    if name == "cell08-chunked-64MiB":
        if mt == ("FOREIGN_SERVICE", "body-too-large") and d["base_table"]["sent_models"] >= 64 << 20:
            return "FIX", "M aborts the chunked 64 MiB body at the cap; base reads all of it"
        return "HARM", "chunked 64 MiB diverged: %s vs %s" % (bt, mt)
    if name in ("cell09-keepalive-two", "cell10-ollama-2MiB"):
        if bt[0] == mt[0] == "MODEL_OK":
            return "AGREE", "both MODEL_OK"
        return "HARM", "positive regressed: %s vs %s" % (bt, mt)
    return "NOTE", "unlabelled"


# ------------------------------------------------------------------ main


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--m", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--only", default="")
    args = ap.parse_args()

    os.makedirs(os.path.join(args.work, "tmp"), exist_ok=True)
    os.makedirs(args.out, exist_ok=True)
    probes = {"base": args.base, "m": args.m}
    only = set(x for x in args.only.split(",") if x)

    results = []
    for cell in CELLS:
        if only and cell[0] not in only:
            continue
        for pname, probe in probes.items():
            for mode in ("table", "json"):
                r = run_one(probe, cell, mode, args.work)
                r["probe"] = pname
                results.append(r)
                print("ran %-26s %-4s %-5s exit=%-4s wall=%6.2fs sent=%d%s"
                      % (r["cell"], pname, mode,
                         "TIMEOUT" if r["timed_out"] else r["exit"],
                         r["wall_s"], r["sent_models"],
                         " timed_out" if r["timed_out"] else ""), flush=True)

    # supplementary: show the -D header file has no total cap either
    supp = []
    if not only or "cell07-header-bloat" in only:
        supp_cells = [
            ("cell07b-header-16MiB", lambda: cell_header_bloat(2000, 8192), 60,
             "supplementary: 2000 x 8 KiB headers (~16 MiB), above curl's cap"),
            ("cell07c-header-164KiB", lambda: cell_header_bloat(20, 8192), 60,
             "supplementary: 20 x 8 KiB headers (~164 KiB), below curl's 300 KiB cap"),
        ]
        for sname, sfactory, sbudget, snote in supp_cells:
            scell = (sname, "m", sfactory, sbudget, snote)
            for pname, probe in probes.items():
                r = run_one(probe, scell, "table", args.work)
                r["probe"] = pname
                supp.append(r)
                print("ran %-26s %-4s %-5s exit=%-4s wall=%6.2fs sent=%d"
                      % (r["cell"], pname, "table",
                         "TIMEOUT" if r["timed_out"] else r["exit"],
                         r["wall_s"], r["sent_models"]), flush=True)

    scale = bash_op_scale(args.work)

    by = {}
    for r in results:
        by.setdefault(r["cell"], {})[r["probe"] + "_" + r["mode"]] = r

    labels = []
    for cell in CELLS:
        if only and cell[0] not in only:
            continue
        d = by.get(cell[0], {})
        if not all(k in d for k in ("base_table", "base_json", "m_table", "m_json")):
            continue
        lab, basis = label_cell(d)
        labels.append((cell[0], lab, basis))

    # ---------------- receipt
    def sha(path):
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for b in iter(lambda: f.read(1 << 20), b""):
                h.update(b)
        return h.hexdigest()

    def tool_first(cmd):
        try:
            return subprocess.run(cmd, capture_output=True, text=True,
                                  timeout=20).stdout.splitlines()[0]
        except Exception:  # noqa: BLE001
            return "unavailable"

    lines = []
    lines.append("# EX01HeldOutCells - held-out hostile answers, base vs M (kama r90 w1)")
    lines.append("base_probe_sha256=%s" % sha(args.base))
    lines.append("m_probe_sha256=%s" % sha(args.m))
    lines.append("gzip_bomb_decoded_bytes_if_inflated=%d" % gz_decoded_claim())
    lines.append("curl=%s" % tool_first(["curl", "--version"]))
    lines.append("python=%s" % tool_first([sys.executable, "--version"]))
    lines.append("bash=%s" % tool_first(["bash", "--version"]))
    lines.append("work=%s" % args.work)
    lines.append("")
    lines.append("## per-run results")
    keys = ["cell", "probe", "mode", "expect", "exit", "timed_out", "budget_s",
            "verdict", "reason", "wall_s", "sent_models", "sent_total",
            "esc", "c0", "nel", "ls", "bidi", "del", "tab", "json_ok",
            "served_len", "served_raw_ctl", "served_raw_bidi", "served_raw_ls",
            "sep_count", "row_len", "served_preview", "row_preview",
            "evidence_preview", "evidence_has_tab"]
    for r in results + supp:
        kv = []
        for k in keys:
            if k in r and r[k] not in (None, ""):
                kv.append("%s=%s" % (k, r[k]))
        lines.append(" ".join(kv))
    lines.append("")
    lines.append("## supplements")
    for r in supp:
        kv = ["cell=%s" % r["cell"], "probe=%s" % r["probe"], "mode=%s" % r["mode"],
              "exit=%s" % ("TIMEOUT" if r["timed_out"] else r["exit"]),
              "verdict=%s" % r.get("verdict"), "reason=%s" % r.get("reason"),
              "sent_models=%s" % r["sent_models"], "wall_s=%s" % r["wall_s"]]
        lines.append(" ".join(kv))
    lines.append("")
    lines.append("## bash pattern-expansion scaling (the probe's own id handling)")
    lines.append("bash_scale_note=probe uses C_SERVED=${C_SERVED%,} in classify and "
                 "normalize_id s=${s##*/} / s=${s%.gguf} on every served id")
    for r in scale:
        lines.append("bash_op=%s n=%d wall_s=%.3f timeout=%s"
                     % (r["op"], r["n"], r["wall_s"], r["timeout"]))
    lines.append("")
    lines.append("## summary")
    for name, lab, basis in labels:
        lines.append("%-8s %-26s %s" % (lab, name, basis))
    lines.append("")
    lines.append("## raw details")
    for r in results + supp:
        lines.append(json.dumps(r, sort_keys=True))
    lines.append("")
    if labels:
        counts = {}
        for _, lab, _ in labels:
            counts[lab] = counts.get(lab, 0) + 1
        lines.append("LABELS " + " ".join("%s=%d" % (k, counts[k]) for k in sorted(counts)))
    lines.append("END")

    out_path = os.path.join(args.out, "heldout.out")
    with open(out_path, "w", encoding="utf-8", errors="surrogateescape") as f:
        f.write("\n".join(lines) + "\n")
    with open(os.path.join(args.out, "heldout-cells.json"), "w",
              encoding="utf-8", errors="surrogateescape") as f:
        json.dump({"results": results, "supplement": supp, "bash_scale": scale,
                   "labels": [{"cell": n, "label": l, "basis": b} for n, l, b in labels]},
                  f, indent=1, sort_keys=True)
        f.write("\n")
    print("wrote %s (%d lines)" % (out_path, len(lines)))
    for name, lab, basis in labels:
        print("%-8s %-26s %s" % (lab, name, basis))
    return 0


if __name__ == "__main__":
    sys.exit(main())
