#!/usr/bin/env python3
"""round93-router-repeat.py - round-93 C1 (operability) frozen counter.

PREDICATE (frozen: plans/round-93-claims.md section C1):

    `python3 tools/round93-router-repeat.py --repo <lane> --rev <M> --work <scratch>` prints
    `ROUTER_REPEAT cells=10 mismatches=0 positive_mismatches=0 probe=rev ...` and exits 0: on each of
    the 10 cells below, `tools/kama-probe.sh` (bytes at <M>) run RUNS = 3 times prints the cell's
    frozen verdict and reason every time, each run within BUDGET = 20 s wall time.

The defect (round-92 wave-1 SC02 F6, `.ufo/waves/round-92/w1/SC02SuperlinearSweep.md`): the router
model-file check decides every autoload candidate in ONE python call that shares one 4 s deadline
(and the bash side kills it at 8 s); a candidate the call cannot decide counts as loadable. A
listener that lists the expected model many times, every entry naming the SAME slow-to-parse
invalid GGUF, turns `MODEL_UNLOADED` / `router-model-invalid` into `MODEL_OK` /
`router-unloaded-autoload`, at a candidate count that moves with host load. The rule the claim
holds the probe to: the verdict for a router listing does not change when entries repeat a model
file already listed (same file by identity, whatever path string names it).

Stub: one lane-owned HTTP listener on a free 127.0.0.1 port answering `GET /props` with
`{"role":"router","models_autoload":true}` and `GET /v1/models` with a router listing of entries
`good`, status `unloaded`, `status.args = [<absolute existing file>, <flag>, <path>...]`.
Fixtures built in the run's private work dir (deterministic bytes):
  slow.gguf   GGUF v3, 0 KV, TENSORS tensor infos (F32, ne0 = 1) with consistent offsets, data
              section truncated -> the probe's loader check returns `invalid` only after reading
              every tensor info (the slow shape SC02 F6 used)
  ok.gguf     GGUF v3, one F32 tensor of 32 elements, data present -> `ok`
  missing     a path under the work dir that does not exist
Cells (expect `good`; verdict/reason read from `check --json` rows[0]):
  R01-slow-x1         1 entry  -m slow.gguf                         MODEL_UNLOADED router-model-invalid
  R02-slow-x8         8 entries -m slow.gguf                        MODEL_UNLOADED router-model-invalid
  R03-slow-x64        64 entries -m slow.gguf                       MODEL_UNLOADED router-model-invalid
  R04-slow-x2048      2048 entries -m slow.gguf                     MODEL_UNLOADED router-model-invalid
  R05-slow-aliases    64 entries naming slow.gguf through 33 path strings (a symlink, then
                      `dir/` + `./` * k + `slow.gguf` for k = 0..31) MODEL_UNLOADED router-model-invalid
  R06-slow-mmproj-x64 64 entries `-m ok.gguf --mmproj slow.gguf`    MODEL_UNLOADED router-model-invalid
  P01-ok-x64          64 entries -m ok.gguf                         MODEL_OK router-unloaded-autoload
  P02-slow-then-ok    63 entries -m slow.gguf, then 1 entry -m a second valid file ok2.gguf
                                                                    MODEL_OK router-unloaded-autoload
  P03-missing-x64     64 entries -m <missing>                       MODEL_UNLOADED router-model-missing
  P04-slow-x1-mixed   1 entry -m slow.gguf and 1 entry -m <missing> MODEL_UNLOADED router-model-missing
`positive_mismatches` counts failing R01 and P cells (the shapes the round-89 rule already grades
right at a low candidate count); a failure there is harm.

Environment faults (no free port, stub never answers, bad --rev, a fixture whose state the BASE
probe's own loader check does not report as designed on a single direct call) exit 2.
Usage: round93-router-repeat.py --repo DIR --rev REV --work DIR [--probe-file FILE]
Exit: 0 all 10 cells pass | 1 any cell fails | 2 could-not-evaluate.
`probe=rev` is printed only when the probe bytes come from `git show <rev>:tools/kama-probe.sh`;
`--probe-file` (controls) prints `probe=override` and can never meet the predicate.
Scratch: everything lives under a mkdtemp inside --work (honours no /tmp default) and is removed.
"""
from __future__ import annotations

import argparse
import hashlib
import http.server
import json
import os
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

BASE = "5af794958b0fc08f574aa2e67650282269549b02"
CELLS = 10
RUNS = 3
BUDGET = 20.0
KILL = 120
CAP = 4194304
TENSORS = 150000


class CannotEvaluate(Exception):
    pass


class Stub:
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


def gguf(n_tensors: int, elems: int, with_data: bool) -> bytes:
    out = [b"GGUF", struct.pack("<I", 3), struct.pack("<QQ", n_tensors, 0)]
    off = 0
    for i in range(n_tensors):
        name = b"t%07d" % i
        out.append(struct.pack("<Q", len(name)) + name + struct.pack("<IQIQ", 1, elems, 0, off))
        off += (elems * 4 + 31) // 32 * 32
    head = b"".join(out)
    pad = (len(head) + 31) // 32 * 32 - len(head)
    return head + b"\0" * pad + (b"\0" * off if with_data else b"\0" * 16)


def router_body(arg_lists) -> bytes:
    data = [{"id": "good", "status": {"value": "unloaded", "args": a}} for a in arg_lists]
    b = json.dumps({"object": "list", "data": data}, separators=(",", ":")).encode()
    if len(b) >= CAP:
        raise CannotEvaluate(f"cell body {len(b)} bytes is not under the 4 MiB cap")
    return b


PROPS = b'{"role":"router","models_autoload":true}'


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

    def check(self, port):
        t0 = time.monotonic()
        try:
            p = subprocess.run(["bash", str(self.probe), "check", "--port", str(port), "--expect", "good",
                                "--timeout", "5", "--connect-timeout", "2", "--json"],
                               capture_output=True, timeout=KILL, env=self.env, cwd=self.cwd)
        except subprocess.TimeoutExpired:
            return None, None, None, time.monotonic() - t0
        dt = time.monotonic() - t0
        try:
            row = json.loads(p.stdout.decode("utf-8"))["rows"][0]
            return p.returncode, row.get("verdict"), row.get("reason"), dt
        except Exception:
            return p.returncode, f"unparsed(rc={p.returncode})", "-", dt


def probe_router_py(probe: bytes) -> str:
    text = probe.decode("utf-8", "replace")
    start = text.find("ROUTER_PY=$(cat <<'PY'\n")
    if start < 0:
        raise CannotEvaluate("ROUTER_PY not found in base probe")
    start += len("ROUTER_PY=$(cat <<'PY'\n")
    end = text.find("\nPY\n)", start)
    if end < 0:
        raise CannotEvaluate("ROUTER_PY end not found in base probe")
    return text[start:end]


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def evaluate(R: Runner, mbytes: bytes, bbytes: bytes):
    w = R.work / "fx"
    w.mkdir()
    slow, ok, ok2 = w / "slow.gguf", w / "ok.gguf", w / "ok2.gguf"
    slow.write_bytes(gguf(TENSORS, 1, False))
    ok.write_bytes(gguf(1, 32, True))
    ok2.write_bytes(gguf(2, 32, True))
    os.symlink(slow, w / "slow-link.gguf")
    missing = str(w / "absent" / "missing.gguf")
    exe = str(ok)  # status.args[0] must be an existing absolute local file
    # Fixture sanity on the BASE probe's own loader, one direct call per file.
    rp = probe_router_py(bbytes)
    for path, want in ((slow, "invalid"), (ok, "-"), (ok2, "-"), (Path(missing), "missing")):
        body = R.work / "sanity.json"
        body.write_bytes(router_body([[exe, "-m", str(path)]]))
        p = subprocess.run([sys.executable, "-c", rp, str(body), "files", "0"], capture_output=True, timeout=60)
        got = p.stdout.decode().strip().split("\t")[-1] if p.stdout else ""
        if got != want:
            raise CannotEvaluate(f"fixture {path.name}: base loader state {got!r}, designed {want!r}")
    s = str(slow)
    aliases = [str(w / "slow-link.gguf")] + [str(w) + "/" + "./" * k + "slow.gguf" for k in range(32)]
    cells = [
        ("R01-slow-x1", [[exe, "-m", s]], "MODEL_UNLOADED", "router-model-invalid"),
        ("R02-slow-x8", [[exe, "-m", s]] * 8, "MODEL_UNLOADED", "router-model-invalid"),
        ("R03-slow-x64", [[exe, "-m", s]] * 64, "MODEL_UNLOADED", "router-model-invalid"),
        ("R04-slow-x2048", [[exe, "-m", s]] * 2048, "MODEL_UNLOADED", "router-model-invalid"),
        ("R05-slow-aliases", [[exe, "-m", aliases[i % len(aliases)]] for i in range(64)], "MODEL_UNLOADED",
         "router-model-invalid"),
        ("R06-slow-mmproj-x64", [[exe, "-m", str(ok), "--mmproj", s]] * 64, "MODEL_UNLOADED",
         "router-model-invalid"),
        ("P01-ok-x64", [[exe, "-m", str(ok)]] * 64, "MODEL_OK", "router-unloaded-autoload"),
        ("P02-slow-then-ok", [[exe, "-m", s]] * 63 + [[exe, "-m", str(ok2)]], "MODEL_OK",
         "router-unloaded-autoload"),
        ("P03-missing-x64", [[exe, "-m", missing]] * 64, "MODEL_UNLOADED", "router-model-missing"),
        ("P04-slow-x1-mixed", [[exe, "-m", missing], [exe, "-m", s]], "MODEL_UNLOADED", "router-model-missing"),
    ]
    R.install(mbytes)
    results = []
    for cid, args, wv, wr in cells:
        routes = {"/v1/models": router_body(args), "/props": PROPS}
        runs = []
        with Stub(routes) as st:
            for _ in range(RUNS):
                runs.append(R.check(st.port))
        good = all(v == wv and r == wr and dt <= BUDGET for _, v, r, dt in runs)
        detail = " ".join(f"run{i + 1}={v}/{r}/{dt:.2f}s" for i, (_, v, r, dt) in enumerate(runs))
        print(f"ROUTER_REPEAT_CELL {cid} ok={int(good)} want={wv}/{wr} {detail}", flush=True)
        results.append((cid, good))
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
        bbytes = show(resolve(BASE))
        if a.probe_file:
            mbytes, mode = a.probe_file.read_bytes(), "override"
        else:
            mbytes, mode = show(rev), "rev"
        a.work.mkdir(parents=True, exist_ok=True)
        work = Path(tempfile.mkdtemp(prefix="r93-repeat-", dir=a.work)).resolve()
        try:
            rows = evaluate(Runner(work), mbytes, bbytes)
        finally:
            shutil.rmtree(work, ignore_errors=True)
    except CannotEvaluate as e:
        print(f"ROUTER_REPEAT could-not-evaluate: {e}")
        return 2
    bad = sum(1 for _, ok in rows if not ok)
    pos = sum(1 for cid, ok in rows if not ok and (cid.startswith("P") or cid.startswith("R01")))
    try:
        load = open("/proc/loadavg").read().split()[0]
    except OSError:
        load = "?"
    print(f"ROUTER_REPEAT cells={len(rows)} mismatches={bad} positive_mismatches={pos} probe={mode} "
          f"probe_sha256={sha256(mbytes)} base_sha256={sha256(bbytes)} rev={rev} load1={load}")
    return 0 if bad == 0 and len(rows) == CELLS else 1


if __name__ == "__main__":
    sys.exit(main())
