#!/usr/bin/env python3
"""round92-linear-paths.py - round-92 C2 (operability) frozen counter.

PREDICATE (frozen: plans/round-92-claims.md section C2):

    `python3 tools/round92-linear-paths.py --repo <lane> --rev <M> --work <scratch>` prints
    `LINEAR_PATHS cells=15 mismatches=0 positive_mismatches=0 probe=rev ...` and exits 0: on each of
    the 6 large cells the probe bytes at <M> (`git show <M>:tools/kama-probe.sh`) finish within
    BUDGET = 20 s wall time with the cell's frozen verdict / persisted value, and on each of the 9
    differential cells the probe at <M> prints exactly the bytes the probe at the frozen BASE prints.

The three paths are the ones round-91 wave-1 SC02 measured super-linear on listener-controlled data
(`.ufo/waves/round-91/w1/SC02QuadraticSweep.md` F1-F3): `jstr`'s global replacements over a
backslash/quote-heavy served list, `router_refine`'s `cand` string append per unloaded entry, and
`served_persist`'s two forks (plus the UTF-8 `${s##*/}`) per served id on the snapshot path.

Large cells (every answer body is under the probe's 4 MiB cap; run killed at KILL = 120 s):
  L1-jstr-backslash   /v1/models one id of 1 900 000 `\\` bytes. `check --expect good --json`.
                      pass: verdict MODEL_MISMATCH, and served_model == unit * 1 900 000 where
                      unit is the M served form of one byte (from D1: M's served_model for 2 000
                      bytes must be unit * 2 000), <= BUDGET
  L2-jstr-quote       the same with `"` bytes (unit from D2)
  L3-router-wild      router listing of 80 000 entries `r00000`.. status unloaded, expect `*`.
                      pass: verdict and reason equal M's at D3 (same shape, 50 entries), <= BUDGET
  L4-router-same-id   60 000 entries id `good` status unloaded, then one `good` loaded, expect good.
                      pass: verdict MODEL_OK, <= BUDGET
  L5-snapshot-16000   `snapshot --json` on a one-row registry whose endpoint serves 16 000 ids
                      `/m/x00000.gguf`..; pass: the latest.tsv served column is the comma-joined
                      `x00000,..,x15999` (normalised basenames, one `.gguf` stripped), <= BUDGET
  L6-snapshot-noslash `snapshot --json`, one id of 200 000 `a` bytes (no slash); pass: the
                      latest.tsv served column is that id, <= BUDGET
Differential cells (harm: the probe's output for ordinary answers must not change). Both probes are
run from the same path against the same stub; pass = byte-equal stdout (check), or byte-equal
latest.tsv without its `#@snapshot_id` line (a timestamp) and equal JSON `rows` (snapshot), and the
M run <= BUDGET:
  D1 2 000 `\\` id, D2 2 000 `"` id, D3 router 50 unloaded wildcard, D4 router 50 unloaded `good` then
  loaded `good`, D5 check with mixed specials, D6 snapshot with mixed ids, D7 snapshot 50 path ids,
  D8 router mixed statuses wildcard, D9 router autoload (`/props` router+autoload) with unloaded
  `good` entries naming missing model files.
`positive_mismatches` counts failing D cells.

Environment faults (no free port, stub never answers, bad --rev) exit 2.
Usage: round92-linear-paths.py --repo DIR --rev REV --work DIR [--probe-file FILE]
Exit: 0 all 15 cells pass | 1 any cell fails | 2 could-not-evaluate.
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

BASE = "ed018ca0fa956c5052b3dc6b714a2cb72973da21"
CELLS = 15
BUDGET = 20.0
KILL = 120
CAP = 4194304
BIG = 1900000
SMALL = 2000


class CannotEvaluate(Exception):
    pass


class Stub:
    """routes: path -> body bytes (200 application/json); anything else 404."""

    def __init__(self, routes):
        self.routes = routes
        stub = self

        class H(http.server.BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.0"

            def log_message(self, *a):
                pass

            def do_GET(self):
                body = stub.routes.get(self.path.split("?")[0])
                code = 200
                if body is None:
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
    b = json.dumps(doc, separators=(",", ":")).encode()
    if len(b) >= CAP:
        raise CannotEvaluate(f"cell body {len(b)} bytes is not under the 4 MiB cap")
    return b


def ids_doc(ids):
    return {"object": "list", "data": [{"id": i} for i in ids]}


def router_doc(entries):
    """entries: (id, status, failed|None, path|None)"""
    data = []
    for i, st, failed, path in entries:
        s = {"value": st}
        if failed is not None:
            s["failed"] = failed
        e = {"id": i, "status": s}
        if path is not None:
            e["path"] = path
        data.append(e)
    return {"object": "list", "data": data}


class Runner:
    def __init__(self, work: Path):
        self.work = work
        self.probe = work / "probe" / "kama-probe.sh"
        self.probe.parent.mkdir()
        self.cwd = work / "probe-cwd"
        self.cwd.mkdir()
        self.env = dict(os.environ, TMPDIR=str(self.cwd))

    def install(self, data: bytes):
        self.probe.write_bytes(data)

    def _run(self, args):
        t0 = time.monotonic()
        try:
            p = subprocess.run(["bash", str(self.probe)] + args, capture_output=True, timeout=KILL,
                               env=self.env, cwd=self.cwd)
        except subprocess.TimeoutExpired:
            return None, b"", time.monotonic() - t0
        return p.returncode, p.stdout, time.monotonic() - t0

    def check(self, port, expect):
        return self._run(["check", "--port", str(port), "--expect", expect, "--timeout", "5",
                          "--connect-timeout", "2", "--json"])

    def snapshot(self, port, expect):
        d = self.work / "snap"
        if d.exists():
            shutil.rmtree(d)
        d.mkdir()
        pin = d / "pin.txt"
        pin.write_text(f"http://127.0.0.1:{port}/v1\n")
        reg = d / "registry.tsv"
        reg.write_text("id\tconsumer_path\tjson_pointer_or_grep\tdeclared_baseurl\texpected_model_id\tnotes\n"
                       f"cell\t{pin}\tgrep:http://[^ ]+\thttp://127.0.0.1:{port}/v1\t{expect}\tr92\n")
        hist = d / "history"
        rc, so, dt = self._run(["snapshot", "--json", "--registry", str(reg), "--history", str(hist),
                                "--timeout", "5", "--connect-timeout", "2"])
        latest = hist / "latest.tsv"
        tsv = latest.read_bytes() if latest.exists() else None
        return rc, so, dt, tsv


def row_of(out: bytes):
    try:
        return json.loads(out.decode("utf-8"))["rows"][0]
    except Exception:
        return None


def rows_of(out: bytes):
    try:
        return json.loads(out.decode("utf-8"))["rows"]
    except Exception:
        return None


def stable(tsv: bytes) -> bytes:
    """latest.tsv without its `#@snapshot_id <UTC second>` line, the one field that differs run to run."""
    return b"\n".join(l for l in tsv.split(b"\n") if not l.startswith(b"#@snapshot_id"))


def served_col(tsv):
    if tsv is None:
        return None
    for line in tsv.decode("utf-8", "replace").splitlines():
        f = line.split("\t")
        if f and f[0] == "cell" and len(f) >= 4:
            return f[3]
    return None


def desc(rc, row, dt):
    v = row.get("verdict") if row else ("killed" if rc is None else f"unparsed(rc={rc})")
    r = row.get("reason") if row else "-"
    return v, r, f"verdict={v} reason={r} seconds={dt:.2f}"


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def evaluate(R: Runner, mbytes: bytes, bbytes: bytes):
    results = []
    memo = {}

    def rec(cid, ok, detail):
        results.append((cid, bool(ok), detail))
        print(f"LINEAR_PATHS_CELL {cid} ok={int(ok)} {detail}", flush=True)

    def diff_check(cid, routes, expect):
        with Stub(routes) as s:
            R.install(bbytes)
            brc, bso, _ = R.check(s.port, expect)
            R.install(mbytes)
            mrc, mso, mdt = R.check(s.port, expect)
        ok = brc is not None and mrc is not None and brc == mrc and bso == mso and mdt <= BUDGET
        row = row_of(mso)
        memo[cid] = row
        _, _, d = desc(mrc, row, mdt)
        rec(cid, ok, f"{d} equal_to_base={int(bso == mso)} rc_m={mrc} rc_base={brc}")

    def diff_snap(cid, routes, expect, rule=None):
        with Stub(routes) as s:
            R.install(bbytes)
            brc, bso, _, btsv = R.snapshot(s.port, expect)
            R.install(mbytes)
            mrc, mso, mdt, mtsv = R.snapshot(s.port, expect)
        same = (btsv is not None and mtsv is not None and stable(btsv) == stable(mtsv)
                and rows_of(bso) is not None and rows_of(bso) == rows_of(mso))
        ok = brc is not None and mrc is not None and brc == mrc and same and mdt <= BUDGET
        if rule is not None:
            ok = ok and served_col(mtsv) == rule
        rec(cid, ok, f"seconds={mdt:.2f} equal_to_base={int(same)} rc_m={mrc} rc_base={brc}"
                     + ("" if rule is None else f" rule_served={int(served_col(mtsv) == rule)}"))

    def big_check(cid, routes, expect, judge):
        with Stub(routes) as s:
            R.install(mbytes)
            rc, so, dt = R.check(s.port, expect)
        row = row_of(so)
        v, r, d = desc(rc, row, dt)
        ok, extra = judge(row, v, r)
        rec(cid, ok and dt <= BUDGET, f"{d} {extra}")

    def big_snap(cid, routes, expect, want):
        with Stub(routes) as s:
            R.install(mbytes)
            rc, so, dt, tsv = R.snapshot(s.port, expect)
        got = served_col(tsv)
        ok = rc is not None and got == want and dt <= BUDGET
        rec(cid, ok, f"seconds={dt:.2f} rc={rc} served_len={-1 if got is None else len(got)} "
                     f"served_rule={int(got == want)}")

    # --- differential cells first (they also pin the M forms the large cells are judged by)
    diff_check("D1-backslash-2000", {"/v1/models": jbody(ids_doc(["\\" * SMALL]))}, "good")
    diff_check("D2-quote-2000", {"/v1/models": jbody(ids_doc(['"' * SMALL]))}, "good")
    diff_check("D3-router-50-unloaded-wild",
               {"/v1/models": jbody(router_doc([(f"r{i:05d}", "unloaded", None, None) for i in range(50)]))}, "*")
    diff_check("D4-router-50-unloaded-then-loaded",
               {"/v1/models": jbody(router_doc([("good", "unloaded", None, None)] * 50 + [("good", "loaded", None, None)]))},
               "good")
    mixed = ['q"b\\s', "a\u0001b\u001fc\u007fd", "tab\there", "nl\nx", "cr\rx", "\u00fc\u0085\u0436",
             "/models/sub/x.gguf", "plain"]
    diff_check("D5-check-mixed-specials", {"/v1/models": jbody(ids_doc(mixed))}, "plain")
    snapmix = ["/models/a.gguf", "b.gguf.gguf", "c/", "d\\e", 'f"g', "h\u0001i", "\u00fc/\u0436.gguf", "x,y", "t\tz"]
    diff_snap("D6-snapshot-mixed", {"/v1/models": jbody(ids_doc(snapmix))}, "a")
    diff_snap("D7-snapshot-50-paths", {"/v1/models": jbody(ids_doc([f"/m/x{i:05d}.gguf" for i in range(50)]))},
              "x00000", rule=",".join(f"x{i:05d}" for i in range(50)))
    diff_check("D8-router-mixed-wild",
               {"/v1/models": jbody(router_doc([("a", "unloaded", None, None), ("b", "loading", None, None),
                                                ("c", "unloaded", True, None), ("d", "downloading", None, None),
                                                ("e", "weird", None, None)]))}, "*")
    diff_check("D9-router-autoload-missing-files",
               {"/v1/models": jbody(router_doc([("good", "unloaded", None, f"/nonexistent/r92/m{i}.gguf")
                                                for i in range(3)])),
                "/props": b'{"role":"router","models_autoload":true}'}, "good")

    def unit_of(cid):
        row = memo.get(cid)
        s = row.get("served_model") if row else None
        if not isinstance(s, str) or len(s) % SMALL:
            return None
        u = s[: len(s) // SMALL]
        return u if u and u * SMALL == s else None

    def run_judge(unit):
        def j(row, v, r):
            s = row.get("served_model") if row else None
            good = unit is not None and isinstance(s, str) and s == unit * BIG
            return v == "MODEL_MISMATCH" and good, f"served_scaled={int(good)}"
        return j

    big_check("L1-jstr-backslash", {"/v1/models": jbody(ids_doc(["\\" * BIG]))}, "good", run_judge(unit_of("D1-backslash-2000")))
    big_check("L2-jstr-quote", {"/v1/models": jbody(ids_doc(['"' * BIG]))}, "good", run_judge(unit_of("D2-quote-2000")))
    d3 = memo.get("D3-router-50-unloaded-wild") or {}

    def j3(row, v, r):
        good = bool(d3) and v == d3.get("verdict") and r == d3.get("reason")
        return good, f"same_as_D3={int(good)}"

    big_check("L3-router-wild", {"/v1/models": jbody(router_doc([(f"r{i:05d}", "unloaded", None, None) for i in range(80000)]))},
              "*", j3)
    big_check("L4-router-same-id",
              {"/v1/models": jbody(router_doc([("good", "unloaded", None, None)] * 60000 + [("good", "loaded", None, None)]))},
              "good", lambda row, v, r: (v == "MODEL_OK", ""))
    big_snap("L5-snapshot-16000", {"/v1/models": jbody(ids_doc([f"/m/x{i:05d}.gguf" for i in range(16000)]))}, "x00000",
             ",".join(f"x{i:05d}" for i in range(16000)))
    big_snap("L6-snapshot-noslash", {"/v1/models": jbody(ids_doc(["a" * 200000]))}, "a", "a" * 200000)
    return results


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--work", type=Path, required=True)
    ap.add_argument("--probe-file", type=Path)
    a = ap.parse_args()
    try:
        def resolve(r):
            rv = subprocess.run(["git", "-C", str(a.repo), "rev-parse", "--verify", r + "^{commit}"],
                                capture_output=True, text=True)
            if rv.returncode != 0:
                raise CannotEvaluate(f"unresolvable rev {r}")
            return rv.stdout.strip()

        def show(r):
            p = subprocess.run(["git", "-C", str(a.repo), "show", f"{r}:tools/kama-probe.sh"], capture_output=True)
            if p.returncode != 0:
                raise CannotEvaluate(f"no tools/kama-probe.sh at {r}")
            return p.stdout

        rev = resolve(a.rev)
        base = resolve(BASE)
        bbytes = show(base)
        if a.probe_file:
            mbytes, mode = a.probe_file.read_bytes(), "override"
        else:
            mbytes, mode = show(rev), "rev"
        a.work.mkdir(parents=True, exist_ok=True)
        work = Path(tempfile.mkdtemp(prefix="r92-linear-", dir=a.work)).resolve()
        try:
            rows = evaluate(Runner(work), mbytes, bbytes)
        finally:
            shutil.rmtree(work, ignore_errors=True)
    except CannotEvaluate as e:
        print(f"LINEAR_PATHS could-not-evaluate: {e}")
        return 2
    bad = sum(1 for _, ok, _ in rows if not ok)
    pos = sum(1 for cid, ok, _ in rows if not ok and cid.startswith("D"))
    print(f"LINEAR_PATHS cells={len(rows)} mismatches={bad} positive_mismatches={pos} probe={mode} "
          f"probe_sha256={sha256(mbytes)} base_sha256={sha256(bbytes)} rev={rev}")
    return 0 if bad == 0 and len(rows) == CELLS else 1


if __name__ == "__main__":
    sys.exit(main())
