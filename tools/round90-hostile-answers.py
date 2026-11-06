#!/usr/bin/env python3
"""round90-hostile-answers.py - round-90 C1 (operability) frozen counter.

PREDICATE (frozen: plans/round-90-claims.md section C1):

    `python3 tools/round90-hostile-answers.py --repo <lane> --rev <R> --work <scratch>` prints
    `HOSTILE_ANSWERS cells=13 mismatches=0 positive_mismatches=0 probe=rev ...` and exits 0: on
    every one of the 13 cells below, `tools/kama-probe.sh` (bytes at <R>) run as
    `check --port <stub> --expect <id> [--json] --timeout 5 --connect-timeout 2` meets the
    cell's frozen pass condition.

Every cell is a lane-owned stub HTTP server on a free 127.0.0.1 port, started and stopped by this
counter in-process (one server per cell). The stub counts the body bytes it handed to the kernel
per path (`sent[path]`); a write that fails ends the stream.

Hostile cells (answers a listener can send; the probe must stay bounded and its output must keep
its shape):
  H1-oversize-length   GET /v1/models: 200 JSON, Content-Length 64 MiB, listing `good` then a
                       64 MiB padding string. pass: sent[/v1/models] <= 16 MiB AND verdict != MODEL_OK
  H2-oversize-close    as H1 but HTTP/1.0 close-delimited (no Content-Length).        same pass
  H3-props-oversize    /v1/models lists `good` with status `unloaded` (router shape, so the probe
                       asks GET /props); /props streams 64 MiB close-delimited.
                       pass: sent[/props] <= 16 MiB
  H4-id-newline-table  ids `good` and "evil\\nFORGED-ROW\\tx\\tMODEL_OK"; table mode.
                       pass: no stdout line starts with `FORGED-ROW` AND every cell of the table's
                       header line (stdout line 1 split on " | ") is non-empty, i.e. no row carried
                       more tab-separated fields than the header names
  H5-id-c0-json        ids `good` and "a\\u0001b"; --json. pass: exit 0, stdout parses as JSON,
                       row verdict MODEL_OK, and no string in the document holds a U+0000-U+001F char
  H6-id-esc-table      ids `good` and "\\u001b[31mRED"; table mode. pass: no 0x1b byte on stdout
  H7-server-header-esc `Server: evil\\x1b[2Jx` header on a plain `good` answer; both modes.
                       pass: table stdout has no 0x1b byte AND --json stdout parses as JSON
  H8-status-value-c0   entry `good` with status value "bad\\u001b[31m" (router shape); both modes.
                       pass: table stdout has no 0x1b byte AND --json stdout parses as JSON
Positive cells (a real model server's answers; a mismatch here is harm, counted separately):
  P1-plain             ids [`good`], expect good, both modes: verdict MODEL_OK reason matched
  P2-large-legit       a 1 MiB list (`good` + 20000 `m-NNNNN` entries), --json: MODEL_OK matched
  P3-unicode-id        id "modele-\\u00e8-\\u65e5\\u672c-\\u00fc" expected verbatim, both modes: MODEL_OK
                       matched, JSON served_model == the id, table stdout holds its UTF-8 bytes
  P4-json-specials     id `q"b\\s` (quote and backslash) expected verbatim, --json: MODEL_OK
                       matched and served_model == the id
  P5-wildcard          ids [`good`], expect `*`, --json: verdict MODEL_OK

A probe run that does not finish in 90 s, or (where JSON is required) prints unparseable JSON,
fails its cell; it is never an environment fault. Environment faults (no free port, stub never
answers, bad --rev) exit 2.

Usage: round90-hostile-answers.py --repo DIR --rev REV --work DIR [--probe-file FILE]
Exit: 0 all 13 cells pass | 1 any cell fails | 2 could-not-evaluate.
`probe=rev` is printed only when the probe bytes come from `git show <rev>:tools/kama-probe.sh`;
`--probe-file` (controls) prints `probe=override` and can never meet the predicate.
"""
from __future__ import annotations

import argparse
import hashlib
import http.server
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

CELLS = 13
MIB = 1 << 20
BOUND = 16 * MIB
BIG = 64 * MIB
ESC = b"\x1b"
POSITIVE = ("P1-plain", "P2-large-legit", "P3-unicode-id", "P4-json-specials", "P5-wildcard")
UNI = "modele-\u00e8-\u65e5\u672c-\u00fc"
SPECIAL = 'q"b\\s'


class CannotEvaluate(Exception):
    pass


def models_doc(ids, status=None):
    data = []
    for i in ids:
        e = {"id": i, "object": "model"}
        if status is not None:
            e["status"] = {"value": status}
        data.append(e)
    return {"object": "list", "data": data}


class Stub:
    """One cell's server. routes: path -> dict(code, body: bytes | ('stream', n), length: bool,
    headers: list[(k, v-bytes)])"""

    def __init__(self, routes):
        self.routes = routes
        self.sent = {}
        stub = self

        class H(http.server.BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.0"

            def log_message(self, *a):
                pass

            def do_GET(self):
                path = self.path.split("?")[0]
                r = stub.routes.get(path)
                if r is None:
                    body = b'{"error":"not found"}'
                    self.send_response(404)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                    return
                hdrs = r.get("headers") or [(b"Content-Type", b"application/json")]
                raw = b"HTTP/1.0 %d OK\r\n" % r.get("code", 200)
                raw += b"".join(k + b": " + v + b"\r\n" for k, v in hdrs)
                body = r["body"]
                if isinstance(body, tuple):
                    n, head = body[1], body[2]
                else:
                    n, head = len(body), body
                if r.get("length", True):
                    raw += b"Content-Length: " + str(n).encode() + b"\r\n"
                self.wfile.write(raw + b"\r\n")
                self.wfile.flush()
                sent = 0
                try:
                    if isinstance(body, tuple):
                        # streaming pad: head, then 'x' * (n - len(head) - 3), then '"}\n'
                        tail = b'"}\n'
                        self.connection.sendall(head)
                        sent += len(head)
                        chunk = b"x" * (64 * 1024)
                        left = n - len(head) - len(tail)
                        while left > 0:
                            c = chunk if left >= len(chunk) else chunk[:left]
                            self.connection.sendall(c)
                            sent += len(c)
                            left -= len(c)
                        self.connection.sendall(tail)
                        sent += len(tail)
                    else:
                        self.connection.sendall(body)
                        sent += len(body)
                except (BrokenPipeError, ConnectionResetError, OSError):
                    pass
                stub.sent[path] = stub.sent.get(path, 0) + sent

        self.srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
        self.srv.daemon_threads = True
        self.port = self.srv.server_address[1]
        self.t = threading.Thread(target=self.srv.serve_forever, daemon=True)

    def __enter__(self):
        self.t.start()
        deadline = time.time() + 10
        while time.time() < deadline:
            try:
                with socket.create_connection(("127.0.0.1", self.port), timeout=1):
                    return self
            except OSError:
                time.sleep(0.05)
        raise CannotEvaluate("stub never accepted")

    def __exit__(self, *a):
        self.srv.shutdown()
        self.srv.server_close()


def jbody(doc) -> bytes:
    return json.dumps(doc).encode()


def run(probe: Path, port: int, expect: str, as_json: bool, env: dict, cwd: Path):
    cmd = ["bash", str(probe), "check", "--port", str(port), "--expect", expect,
           "--timeout", "5", "--connect-timeout", "2"]
    if as_json:
        cmd.append("--json")
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=90, env=env, cwd=cwd)
    except subprocess.TimeoutExpired:
        return None, b"", "timeout"
    return p.returncode, p.stdout, p.stderr.decode("utf-8", "replace")[-200:]


def parse_row(out: bytes):
    try:
        doc = json.loads(out.decode("utf-8"))
        return doc, doc["rows"][0]
    except Exception:
        return None, None


def has_c0(obj) -> bool:
    if isinstance(obj, str):
        return any(ord(c) < 0x20 for c in obj)
    if isinstance(obj, dict):
        return any(has_c0(k) or has_c0(v) for k, v in obj.items())
    if isinstance(obj, list):
        return any(has_c0(v) for v in obj)
    return False


def pad_stream(ids, status=None):
    doc = models_doc(ids, status)
    head = json.dumps(doc)[:-1].encode() + b', "pad": "'
    return ("stream", BIG, head)


def cells():
    """-> list of (cell id, routes, checker(probe_runner, stub) -> (ok, detail))"""
    out = []

    def c_oversize(path):
        def chk(R, stub):
            rc, so, _ = R("good", True)
            _, row = parse_row(so)
            verdict = row["verdict"] if row else f"unparsed(rc={rc})"
            sent = stub.sent.get(path, 0)
            if path == "/props":
                return sent <= BOUND, f"sent={sent} verdict={verdict}"
            return sent <= BOUND and verdict != "MODEL_OK", f"sent={sent} verdict={verdict}"
        return chk

    out.append(("H1-oversize-length",
                {"/v1/models": {"body": pad_stream(["good"]), "length": True}},
                c_oversize("/v1/models")))
    out.append(("H2-oversize-close",
                {"/v1/models": {"body": pad_stream(["good"]), "length": False}},
                c_oversize("/v1/models")))
    out.append(("H3-props-oversize",
                {"/v1/models": {"body": jbody(models_doc(["good"], "unloaded"))},
                 "/props": {"body": ("stream", BIG, b'{"role": "router", "models_autoload": true, "pad": "'),
                            "length": False}},
                c_oversize("/props")))

    def c_forged(R, stub):
        rc, so, _ = R("good", False)
        lines = so.split(b"\n")
        forged = [l for l in lines if l.startswith(b"FORGED-ROW")]
        head = [c.strip() for c in lines[0].split(b" | ")] if lines else []
        empty = sum(1 for c in head if not c)
        return (rc is not None and not forged and bool(head) and empty == 0,
                f"rc={rc} forged_lines={len(forged)} header_cols={len(head)} empty_header_cols={empty}")
    out.append(("H4-id-newline-table",
                {"/v1/models": {"body": jbody(models_doc(["good", "evil\nFORGED-ROW\tx\tMODEL_OK"]))}},
                c_forged))

    def c_c0json(R, stub):
        rc, so, _ = R("good", True)
        doc, row = parse_row(so)
        if doc is None:
            return False, f"rc={rc} json=unparsed"
        return (rc == 0 and row.get("verdict") == "MODEL_OK" and not has_c0(doc),
                f"rc={rc} verdict={row.get('verdict')} c0={int(has_c0(doc))}")
    out.append(("H5-id-c0-json",
                {"/v1/models": {"body": jbody(models_doc(["good", "a\u0001b"]))}},
                c_c0json))

    def c_esc_table(R, stub):
        rc, so, _ = R("good", False)
        return rc is not None and ESC not in so, f"rc={rc} esc={int(ESC in so)}"
    out.append(("H6-id-esc-table",
                {"/v1/models": {"body": jbody(models_doc(["good", "\u001b[31mRED"]))}},
                c_esc_table))

    def c_esc_both(R, stub):
        rc1, so1, _ = R("good", False)
        rc2, so2, _ = R("good", True)
        doc, _ = parse_row(so2)
        ok = rc1 is not None and ESC not in so1 and doc is not None
        return ok, f"table_rc={rc1} esc={int(ESC in so1)} json_rc={rc2} json={'ok' if doc else 'unparsed'}"
    out.append(("H7-server-header-esc",
                {"/v1/models": {"body": jbody(models_doc(["good"])),
                                "headers": [(b"Content-Type", b"application/json"),
                                            (b"Server", b"evil\x1b[2Jx")]}},
                c_esc_both))
    out.append(("H8-status-value-c0",
                {"/v1/models": {"body": jbody(models_doc(["good"], "bad\u001b[31m"))}},
                c_esc_both))

    def c_ok(expect, both=True, served=None, table_bytes=None):
        def chk(R, stub):
            details, ok = [], True
            rc, so, _ = R(expect, True)
            doc, row = parse_row(so)
            if row is None:
                return False, f"json_rc={rc} json=unparsed"
            want_reason = "expected-wildcard" if expect == "*" else "matched"
            ok &= row.get("verdict") == "MODEL_OK" and row.get("reason") == want_reason
            details.append(f"verdict={row.get('verdict')} reason={row.get('reason')}")
            if served is not None:
                ok &= row.get("served_model") == served
                details.append(f"served_eq={int(row.get('served_model') == served)}")
            if both:
                rc1, so1, _ = R(expect, False)
                tok = rc1 == 0 and b"MODEL_OK" in so1
                if table_bytes is not None:
                    tok &= table_bytes in so1
                ok &= tok
                details.append(f"table_rc={rc1} table_ok={int(tok)}")
            return ok, " ".join(details)
        return chk

    out.append(("P1-plain", {"/v1/models": {"body": jbody(models_doc(["good"]))}}, c_ok("good")))
    big_ids = ["good"] + [f"m-{i:05d}" for i in range(20000)]
    body = jbody(models_doc(big_ids))
    body = body[:-1] + b', "note": "' + b"n" * max(0, MIB - len(body) - 13) + b'"}'
    out.append(("P2-large-legit", {"/v1/models": {"body": body}}, c_ok("good", both=False)))
    out.append(("P3-unicode-id", {"/v1/models": {"body": jbody(models_doc([UNI]))}},
                c_ok(UNI, served=UNI, table_bytes=UNI.encode())))
    out.append(("P4-json-specials", {"/v1/models": {"body": jbody(models_doc([SPECIAL]))}},
                c_ok(SPECIAL, both=False, served=SPECIAL)))
    out.append(("P5-wildcard", {"/v1/models": {"body": jbody(models_doc(["good"]))}},
                c_ok("*", both=False)))
    return out


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--work", type=Path, required=True)
    ap.add_argument("--probe-file", type=Path)
    a = ap.parse_args()
    rows = []
    try:
        rv = subprocess.run(["git", "-C", str(a.repo), "rev-parse", "--verify", a.rev + "^{commit}"],
                            capture_output=True, text=True)
        if rv.returncode != 0:
            raise CannotEvaluate(f"unresolvable --rev {a.rev}")
        rev = rv.stdout.strip()
        a.work.mkdir(parents=True, exist_ok=True)
        work = Path(tempfile.mkdtemp(prefix="r90-hostile-", dir=a.work)).resolve()
        try:
            probe = work / "kama-probe.sh"
            if a.probe_file:
                probe.write_bytes(a.probe_file.read_bytes())
                mode = "override"
            else:
                probe.write_bytes(subprocess.run(["git", "-C", str(a.repo), "show", f"{rev}:tools/kama-probe.sh"],
                                                 capture_output=True, check=True).stdout)
                mode = "rev"
            probe_sha = sha256(probe)
            pcwd = work / "probe-cwd"
            pcwd.mkdir()
            env = dict(os.environ, TMPDIR=str(pcwd))
            for cid, routes, chk in cells():
                with Stub(routes) as stub:
                    def R(expect, as_json, _p=stub.port):
                        return run(probe, _p, expect, as_json, env, pcwd)
                    ok, detail = chk(R, stub)
                rows.append((cid, bool(ok), detail))
        finally:
            shutil.rmtree(work, ignore_errors=True)
    except CannotEvaluate as e:
        for r in rows:
            print(f"HOSTILE_ANSWERS_CELL {r[0]} ok={int(r[1])} {r[2]}")
        print(f"HOSTILE_ANSWERS could-not-evaluate: {e}")
        return 2
    bad = pos = 0
    for cid, ok, detail in rows:
        bad += not ok
        pos += (not ok) and cid in POSITIVE
        print(f"HOSTILE_ANSWERS_CELL {cid} ok={int(ok)} {detail}")
    print(f"HOSTILE_ANSWERS cells={len(rows)} mismatches={bad} positive_mismatches={pos} "
          f"probe={mode} probe_sha256={probe_sha} rev={rev}")
    return 0 if bad == 0 and len(rows) == CELLS else 1


if __name__ == "__main__":
    sys.exit(main())
