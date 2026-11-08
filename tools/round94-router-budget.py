#!/usr/bin/env python3
"""round94-router-budget.py - round-94 C1 (operability) frozen counter.

PREDICATE (frozen: plans/round-94-claims.md section C1):

    `python3 tools/round94-router-budget.py --repo <lane> --rev <M> --work <scratch>` prints
    `ROUTER_BUDGET cells=<n> mismatches=0 positive_mismatches=0 load_cells=<k> load_stable=1
    probe=rev ...` and exits 0 at the measured commit M, the counter's bytes identical to the
    freeze commit. The counter grades the probe at TWO host loads - natural, then one synthetic
    CPU burn it applies itself - and requires every cell's verdict to be identical at both loads
    and equal to the cell's frozen expectation.

Defect being closed (round-93 wave-1 SC02 F1/F2/F3, `.ufo/waves/round-93/w1/SC02ProbeVerdictSweep.md`):
the ROUTER_PY `files` pass evaluated ONE wall-clock DEADLINE (4 s) at module import and shared it
across every candidate, so a single slow parse that overran 4 s left every later candidate
undecided (`-`), which the round-89 rule grades loadable -> the verdict flipped
MODEL_UNLOADED -> MODEL_OK under host load. The round-94 repair gives each `gguf_parse` call its
own deadline slice (PER_FILE_SECONDS) and raises the `timeout 8` wrapper to `timeout 60`; MAX_STEPS
(4 000 000) stays the deterministic work bound.

Rule the claim holds the probe to: for every router listing below, the verdict and reason are the
same at natural load and under synthetic load, and equal the frozen expectation. The round-89 rule
"undecidable stays loadable" is unchanged; what changed is that one file can no longer spend the
budget of the others.

Stub: one lane-owned HTTP listener on a free 127.0.0.1 port answering `GET /props` with
`{"role":"router","models_autoload":true}` and `GET /v1/models` with a router listing of entries
`good`, status `unloaded`, `status.args = [<absolute existing file>, <flag>, <path>...]`.
Fixtures built in the run's private work dir (deterministic bytes):
  slow.gguf   GGUF v3, 0 KV, 150000 tensor infos (F32, ne0 = 1) with consistent offsets, data
              section truncated -> `invalid` only after reading every tensor info (the slow shape)
  ok.gguf     GGUF v3, one F32 tensor of 32 elements, data present -> parses `ok`
  ok2.gguf    a second distinct valid file (different tensor count)
  corrupt     a 192-byte file that is not a GGUF -> `invalid` quickly
  missing     a path under the work dir that does not exist

Cells (expect `good`; verdict/reason read from `check --json` rows[0]):
  R01-slow-x1          1 entry  -m slow.gguf                          MODEL_UNLOADED router-model-invalid
  R02-slow-x8          8 entries -m slow.gguf                         MODEL_UNLOADED router-model-invalid
  R03-slow-x64         64 entries -m slow.gguf                        MODEL_UNLOADED router-model-invalid
  R04-slow-x2048       2048 entries -m slow.gguf                      MODEL_UNLOADED router-model-invalid
  R05-slow-aliases     64 entries naming slow.gguf through 33 path strings (symlink + ./ * k)
                                                                     MODEL_UNLOADED router-model-invalid
  R05b-slow-hardlinks  64 entries naming slow.gguf through 33 HARD LINKS (os.link) to one inode
                                                                     MODEL_UNLOADED router-model-invalid
  R06-slow-mmproj-x64  64 entries -m ok.gguf --mmproj slow.gguf       MODEL_UNLOADED router-model-invalid
  R07-slow-16-symlinks 16 entries naming slow.gguf through 16 symlink strings
                                                                     MODEL_UNLOADED router-model-invalid
  P01-ok-x64           64 entries -m ok.gguf                          MODEL_OK router-unloaded-autoload
  P02-slow-then-ok     63 entries -m slow.gguf, then 1 entry -m ok2.gguf
                                                                     MODEL_OK router-unloaded-autoload
  P02b-slow-2048-ok    2047 entries -m slow.gguf, last entry -m ok2.gguf (valid file at the edge)
                                                                     MODEL_OK router-unloaded-autoload
  P03-missing-x64      64 entries -m <missing>                        MODEL_UNLOADED router-model-missing
  P04-slow-x1-mixed    1 entry -m slow.gguf and 1 entry -m <missing>  MODEL_UNLOADED router-model-missing
  P05-collision        63 entries -m a/slow.gguf (invalid), 1 entry -m b/slow.gguf (valid),
                       SAME basename, SAME size, distinct inodes     MODEL_OK router-unloaded-autoload
  P06-one-entry-2path  1 entry -m ok.gguf -md ok.gguf (one file, two path flags)
                                                                     MODEL_OK router-unloaded-autoload
  P07-distinct-k4      4 entries, each -m a DISTINCT fast invalid file (corrupt header; distinct
                       SLOW files remain the disclosed wall-clock limit)
                                                                     MODEL_UNLOADED router-model-invalid
  R08-distinct-slow-k4  4 entries, each -m a DISTINCT slow invalid file (the per-file-deadline
                       distinguishing cell: a shared deadline starves later files)
                                                                     MODEL_UNLOADED router-model-invalid
  U01-undecided        1 entry -m <a file that parses to undecided -> stays loadable>
                                                                     MODEL_OK router-unloaded-autoload

`positive_mismatches` counts failing R01 and P cells (the shapes the round-89 rule already grades
right at a low candidate count); a failure there is harm.

Two-invocation rewrite guard (CR01 DEFECT-4): cell T01 rewrites slow.gguf in place to a VALID
header of the SAME byte length and restores mtime, then re-runs check on the same stub; the
verdict must flip to MODEL_OK (the probe re-stats each call; there is no cross-call cache). A
second rewrite back to invalid must flip back. This is graded as part of the cell set.

Environment faults (no free port, stub never answers, bad --rev, a fixture whose state the BASE
probe's own loader check does not report as designed on a single direct call) exit 2.
Usage: round94-router-budget.py --repo DIR --rev REV --work DIR [--probe-file FILE]
       [--burners N] [--runs N]
Exit: 0 all cells pass at both loads | 1 any cell fails or verdicts differ across loads | 2
could-not-evaluate.
`probe=rev` is printed only when the probe bytes come from `git show <rev>:tools/kama-probe.sh`;
`--probe-file` (controls) prints `probe=override` and can never meet the predicate.
Scratch: everything lives under a mkdtemp inside --work and is removed.
"""
from __future__ import annotations

import argparse
import hashlib
import http.server
import json
import os
import shutil
import signal
import socket
import struct
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

BASE = "5af794958b0fc08f574aa2e67650282269549b02"
CELLS = 19
RUNS = 2
BUDGET = 30.0
KILL = 120
CAP = 4194304
TENSORS = 150000
DEFAULT_BURNERS = 96


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


def loadavg() -> str:
    try:
        return open("/proc/loadavg").read().split()[0]
    except OSError:
        return "?"


def start_burners(n: int):
    ps = []
    for _ in range(n):
        p = subprocess.Popen([sys.executable, "-c", "while True: pass"],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                             start_new_session=True)
        ps.append(p)
    time.sleep(2.0)
    return ps


def stop_burners(ps):
    for p in ps:
        try:
            os.killpg(os.getpgid(p.pid), signal.SIGKILL)
        except Exception:
            try:
                p.kill()
            except Exception:
                pass
    for p in ps:
        try:
            p.wait(timeout=5)
        except Exception:
            pass


def build_fixtures(w: Path):
    slow = w / "slow.gguf"
    ok = w / "ok.gguf"
    ok2 = w / "ok2.gguf"
    corrupt = w / "corrupt.gguf"
    slow.write_bytes(gguf(TENSORS, 1, False))
    ok.write_bytes(gguf(1, 32, True))
    ok2.write_bytes(gguf(2, 32, True))
    corrupt.write_bytes(b"NOTAGGUF" + b"\0" * 184)  # 192 bytes, not a GGUF -> invalid fast
    # collision pair: same basename, same size, distinct inodes; one invalid one valid.
    # Make a/slow.gguf invalid (truncated tensors) and b/slow.gguf valid, padded to equal size.
    a_dir = w / "a"
    b_dir = w / "b"
    a_dir.mkdir()
    b_dir.mkdir()
    a_slow = a_dir / "slow.gguf"
    b_slow = b_dir / "slow.gguf"
    # a_slow: the slow invalid bytes; b_slow: a VALID gguf padded with trailing zero slack to the
    # exact same length. The parser's ok check only requires tensor data to fit within size, so
    # trailing slack keeps b_slow valid (this is the CR01 DEFECT-2 / MT01 GD collision shape).
    a_bytes = slow.read_bytes()
    b_valid = gguf(1, 32, True)
    target = len(a_bytes)
    if len(b_valid) < target:
        b_valid = b_valid + b"\0" * (target - len(b_valid))
    a_slow.write_bytes(a_bytes)
    b_slow.write_bytes(b_valid[:target])
    assert a_slow.stat().st_size == b_slow.stat().st_size == target
    return slow, ok, ok2, corrupt, a_slow, b_slow


def fixture_states(rp: str, body_path: Path, idxs):
    p = subprocess.run([sys.executable, "-c", rp, str(body_path), "files"] + [str(i) for i in idxs],
                       capture_output=True, timeout=60)
    out = {}
    for line in p.stdout.decode().splitlines():
        parts = line.split("\t")
        if len(parts) == 2:
            out[int(parts[0])] = parts[1]
    return out


def evaluate_pass(R: Runner, rp: str, w: Path, label: str, n_runs: int):
    """Run all cells once at the current host load; return {cid: (verdict, reason, ok)}."""
    fx = w / label
    fx.mkdir(parents=True, exist_ok=True)
    slow, ok, ok2, corrupt, a_slow, b_slow = build_fixtures(fx)
    slow = fx / "slow.gguf"
    ok = fx / "ok.gguf"
    ok2 = fx / "ok2.gguf"
    corrupt = fx / "corrupt.gguf"
    a_slow = fx / "a" / "slow.gguf"
    b_slow = fx / "b" / "slow.gguf"
    missing = str(fx / "absent" / "missing.gguf")
    exe = str(ok)  # status.args[0] must be an existing absolute local file

    # Fixture sanity on the BASE probe's own loader, one direct call per file.
    for path, want in ((slow, "invalid"), (ok, "-"), (ok2, "-"), (corrupt, "invalid"),
                       (Path(missing), "missing")):
        body = w / f"sanity-{label}.json"
        body.write_bytes(router_body([[exe, "-m", str(path)]]))
        states = fixture_states(rp, body, [0])
        got = states.get(0, "")
        if got != want:
            raise CannotEvaluate(f"fixture {path.name}: base loader state {got!r}, designed {want!r}")

    s = str(slow)
    # 33 path-string aliases: one symlink then dir/ + ./ * k
    link = str(fx / "slow-link.gguf")
    os.symlink(slow, link)
    aliases = [link] + [str(fx) + "/" + "./" * k + "slow.gguf" for k in range(32)]
    # 33 hard links to the same inode
    hardlinks = []
    for k in range(33):
        hl = fx / f"slow-hl-{k}.gguf"
        try:
            os.link(slow, hl)
        except OSError:
            hl = fx / f"slow-hl-{k}.gguf"
            with open(slow, "rb") as fi, open(hl, "wb") as fo:
                fo.write(fi.read())
        hardlinks.append(str(hl))
    # 16 symlink strings
    syms = []
    for k in range(16):
        sy = fx / f"slow-sym-{k}.gguf"
        try:
            os.symlink(slow, sy)
        except OSError:
            pass
        syms.append(str(sy))
    # 4 distinct FAST invalid files (corrupt headers, parse in milliseconds). Distinct SLOW files
    # are the disclosed wall-clock limit (their total parse time is load-dependent), so this cell
    # uses fast files to verify each distinct candidate is evaluated on its own budget, load-free.
    distinct = []
    for k in range(4):
        dp = fx / f"fast-dist-{k}.gguf"
        dp.write_bytes(b"NOTAGGUF" + bytes([k]) * 184)  # 192 bytes, distinct inodes, invalid fast
        distinct.append(str(dp))
    # 4 distinct SLOW invalid files (the per-file-deadline distinguishing cell R08): each parse
    # is slow, so a SHARED deadline (the r93 defect) starves later files while per-file budgets
    # let each finish. For the fixed probe each stays under PER_FILE_SECONDS at both loads.
    slow_distinct = []
    for k in range(4):
        dp = fx / f"slow-dist-{k}.gguf"
        dp.write_bytes(gguf(TENSORS, 1, False))
        slow_distinct.append(str(dp))
    # undecided file: a regular file under /dev is refused (returns "-" via NO_OPEN) - use a
    # non-regular path that file_state cannot decide. Simplest: a path that isabs but not a
    # regular file -> gguf_state returns gguf_parse -> invalid for non-regular? Check: gguf_parse
    # returns "invalid" for non-regular. To get "-", use a relative path or args[0] not a file.
    # Use a FIFO (non-regular, not in NO_OPEN): gguf_parse -> not S_ISREG -> "invalid". Instead use
    # an unreadable regular file? chmod 000 -> os.open fails -> "-". But running as same user,
    # chmod 000 blocks read. Let's make a directory named like a file: isabs True, isfile False ->
    # file_state returns "-" early (args[0] not isfile). Actually file_state checks args[0] only.
    # For the -m path itself being a directory: gguf_state -> os.stat ok, not S_ISREG -> gguf_parse
    # -> not S_ISREG -> "invalid". Hmm. To get undecided "-", use a path under NO_OPEN? Those are
    # excluded -> gguf_parse returns "invalid" for them too (realpath startswith NO_OPEN -> invalid).
    # The cleanest undecided: a valid GGUF that parses to "ok" maps to "-" in file_state (only
    # missing/invalid are bad). So a valid ok.gguf candidate is undecided-for-bad-purposes -> loadable.
    # U01 uses ok.gguf alone -> MODEL_OK router-unloaded-autoload (the valid file is loadable).

    cells = [
        ("R01-slow-x1", [[exe, "-m", s]], "MODEL_UNLOADED", "router-model-invalid"),
        ("R02-slow-x8", [[exe, "-m", s]] * 8, "MODEL_UNLOADED", "router-model-invalid"),
        ("R03-slow-x64", [[exe, "-m", s]] * 64, "MODEL_UNLOADED", "router-model-invalid"),
        ("R04-slow-x2048", [[exe, "-m", s]] * 2048, "MODEL_UNLOADED", "router-model-invalid"),
        ("R05-slow-aliases", [[exe, "-m", aliases[i % len(aliases)]] for i in range(64)],
         "MODEL_UNLOADED", "router-model-invalid"),
        ("R05b-slow-hardlinks", [[exe, "-m", hardlinks[i % len(hardlinks)]] for i in range(64)],
         "MODEL_UNLOADED", "router-model-invalid"),
        ("R06-slow-mmproj-x64", [[exe, "-m", str(ok), "--mmproj", s]] * 64, "MODEL_UNLOADED",
         "router-model-invalid"),
        ("R07-slow-16-symlinks", [[exe, "-m", syms[i % len(syms)]] for i in range(16)],
         "MODEL_UNLOADED", "router-model-invalid"),
        ("P01-ok-x64", [[exe, "-m", str(ok)]] * 64, "MODEL_OK", "router-unloaded-autoload"),
        ("P02-slow-then-ok", [[exe, "-m", s]] * 63 + [[exe, "-m", str(ok2)]], "MODEL_OK",
         "router-unloaded-autoload"),
        ("P02b-slow-2048-ok", [[exe, "-m", s]] * 2047 + [[exe, "-m", str(ok2)]], "MODEL_OK",
         "router-unloaded-autoload"),
        ("P03-missing-x64", [[exe, "-m", missing]] * 64, "MODEL_UNLOADED", "router-model-missing"),
        ("P04-slow-x1-mixed", [[exe, "-m", missing], [exe, "-m", s]], "MODEL_UNLOADED",
         "router-model-missing"),
        ("P05-collision", [[exe, "-m", str(a_slow)]] * 63 + [[exe, "-m", str(b_slow)]], "MODEL_OK",
         "router-unloaded-autoload"),
        ("P06-one-entry-2path", [[exe, "-m", str(ok), "-md", str(ok)]], "MODEL_OK",
         "router-unloaded-autoload"),
        ("P07-distinct-k4", [[exe, "-m", d] for d in distinct], "MODEL_UNLOADED",
         "router-model-invalid"),
        ("R08-distinct-slow-k4", [[exe, "-m", d] for d in slow_distinct], "MODEL_UNLOADED",
         "router-model-invalid"),
        ("U01-undecided", [[exe, "-m", str(ok)]], "MODEL_OK", "router-unloaded-autoload"),
    ]

    results = {}
    for cid, args, wv, wr in cells:
        routes = {"/v1/models": router_body(args), "/props": PROPS}
        runs = []
        with Stub(routes) as st:
            for _ in range(n_runs):
                runs.append(R.check(st.port))
        good = all(v == wv and r == wr and dt <= BUDGET for _, v, r, dt in runs)
        # record the modal verdict/reason for cross-load comparison
        verdicts = [(v, r) for _, v, r, _ in runs]
        detail = " ".join(f"run{i + 1}={v}/{r}/{dt:.2f}s" for i, (_, v, r, dt) in enumerate(runs))
        print(f"ROUTER_BUDGET_CELL {label} {cid} ok={int(good)} want={wv}/{wr} {detail}", flush=True)
        results[cid] = (good, verdicts, wv, wr)

    # T01 two-invocation rewrite guard: rewrite slow.gguf in place to valid same-size, restore
    # mtime, re-run; verdict must flip to MODEL_OK; rewrite back to invalid, flip back.
    t01 = fx / "slow.gguf"
    orig = t01.read_bytes()
    st = os.stat(t01)
    routes_ok = {"/v1/models": router_body([[exe, "-m", str(t01)]]), "/props": PROPS}
    try:
        with Stub(routes_ok) as st1:
            rc1, v1, r1, _ = R.check(st1.port)
        # rewrite to a valid gguf of the SAME length, restore mtime+size
        valid = gguf(1, 32, True)
        if len(valid) < len(orig):
            valid = valid + b"\0" * (len(orig) - len(valid))
        valid = valid[:len(orig)]
        with open(t01, "wb") as f:
            f.write(valid)
        os.utime(t01, ns=(st.st_atime_ns, st.st_mtime_ns))
        with Stub(routes_ok) as st2:
            rc2, v2, r2, _ = R.check(st2.port)
        # rewrite back to invalid, restore mtime
        with open(t01, "wb") as f:
            f.write(orig)
        os.utime(t01, ns=(st.st_atime_ns, st.st_mtime_ns))
        with Stub(routes_ok) as st3:
            rc3, v3, r3, _ = R.check(st3.port)
        # After rewrite to valid: expect MODEL_OK (file now parses ok -> loadable).
        # After rewrite back to invalid: expect MODEL_UNLOADED router-model-invalid.
        ok_flip = (v2 == "MODEL_OK")
        back_flip = (v3 == "MODEL_UNLOADED" and r3 == "router-model-invalid")
        good = ok_flip and back_flip
        print(f"ROUTER_BUDGET_CELL {label} T01-rewrite ok={int(good)} "
              f"v1={v1}/{r1} v2={v2}/{r2} v3={v3}/{r3}", flush=True)
        results["T01-rewrite"] = (good, [(v1, r1), (v2, r2), (v3, r3)], "MODEL_OK+MODEL_UNLOADED",
                                 "rewrite-flips")
    finally:
        # ensure fixture restored
        try:
            t01.write_bytes(orig)
        except Exception:
            pass
    return results


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--work", type=Path, required=True)
    ap.add_argument("--probe-file", type=Path)
    ap.add_argument("--burners", type=int, default=DEFAULT_BURNERS)
    ap.add_argument("--runs", type=int, default=RUNS)
    a = ap.parse_args()
    runs = a.runs
    try:
        def resolve(r):
            rv = subprocess.run(["git", "-C", str(a.repo), "rev-parse", "--verify", r + "^{commit}"],
                                capture_output=True, text=True)
            if rv.returncode != 0:
                raise CannotEvaluate(f"unresolvable rev {r}")
            return rv.stdout.strip()

        def show(r):
            p = subprocess.run(["git", "-C", str(a.repo), "show", f"{r}:tools/kama-probe.sh"],
                               capture_output=True)
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
        work = Path(tempfile.mkdtemp(prefix="r94-budget-", dir=a.work)).resolve()
        try:
            R = Runner(work)
            R.install(mbytes)
            rp = probe_router_py(bbytes)  # sanity uses BASE loader
            # Pass 1: natural load
            natural = evaluate_pass(R, rp, work, "nat", runs)
            # Pass 2: synthetic load
            burners = start_burners(a.burners) if a.burners > 0 else []
            try:
                loaded = evaluate_pass(R, rp, work, "load", runs)
            finally:
                stop_burners(burners)
        finally:
            shutil.rmtree(work, ignore_errors=True)
    except CannotEvaluate as e:
        print(f"ROUTER_BUDGET could-not-evaluate: {e}")
        return 2

    # Compare across loads and against expectation.
    mismatches = 0
    positive_mismatches = 0
    load_stable = 1
    cids = sorted(set(natural) | set(loaded))
    for cid in cids:
        ng, nv, nwv, nwr = natural.get(cid, (False, [], "-", "-"))
        lg, lv, lwv, lwr = loaded.get(cid, (False, [], "-", "-"))
        # verdict/reason stability across loads
        if nv != lv:
            load_stable = 0
            print(f"ROUTER_BUDGET_UNSTABLE {cid} natural={nv} loaded={lv}", flush=True)
        cell_ok = ng and lg
        if not cell_ok:
            mismatches += 1
            if cid.startswith("P") or cid.startswith("R01"):
                positive_mismatches += 1
    bad = mismatches
    print(f"ROUTER_BUDGET cells={len(cids)} mismatches={bad} positive_mismatches={positive_mismatches} "
          f"load_cells={len(cids)} load_stable={load_stable} probe={mode} "
          f"probe_sha256={sha256(mbytes)} base_sha256={sha256(bbytes)} rev={rev} "
          f"load1_nat={loadavg()} burners={a.burners}")
    return 0 if (bad == 0 and load_stable == 1 and len(cids) == CELLS) else 1


if __name__ == "__main__":
    sys.exit(main())
