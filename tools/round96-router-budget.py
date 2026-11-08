#!/usr/bin/env python3
"""round96-router-budget.py - round-96 C1 (operability) frozen counter.

PREDICATE (frozen: plans/round-96-claims.md section C1):

    `python3 tools/round96-router-budget.py --repo <lane> --rev <M> --work <scratch>` prints
    `ROUTER_BUDGET96 cells=<n> mismatches=0 positive_mismatches=0 load_cells=<k> load_stable=1
    budget=work ...` and exits 0 at the measured commit M, the counter's bytes identical to the
    freeze commit.

Defect being closed (round-94 closure routed D3, `.ufo/waves/round-94/` SC02 F2/F3, CR01 F3/F8,
MT01 M02/M10): the round-94 repair moved the wall clock from one shared 4 s call deadline to a
15 s per-file slice, but the verdict was still a function of the clock, so the same bytes graded
`invalid` on an idle host and `-` (undecided -> loadable, round-89 rule) under load; and the pass
was still capped by the constant `timeout 60`, so a listing of >=~20 distinct slow files truncated,
left the truncated candidates `-`, and graded `MODEL_OK` for a model that can never load.

Round-95 probe change (tools/kama-probe.sh ROUTER_PY): the clock is removed from the decision.
Work is bounded deterministically - `MAX_STEPS` (5 000 000) counts the parser's read/seek steps,
`MAX_META` (512 MiB) caps the header position - so a candidate's state is a pure function of its
bytes, and the pass-level limit is derived from the candidate count (`20 + 25 * npaths` seconds).

Rule the claim holds the probe to: every cell below grades the frozen expectation at BOTH host
loads (natural, then a synthetic CPU load the counter raises itself), and the full listing is
graded - a truncated pass is a mismatch, never a pass.

Fixture oracle: the counter decides its own fixtures' designed class from the bytes it wrote
(`fixture_class`), never from the probe under test. Round-94's counter asked the BASE probe to
classify the fixtures and exited 2 when that probe could not answer under load (SC02 F1); a
fixture oracle that cannot be perturbed by host load removes that failure mode.

Stub: one lane-owned HTTP listener on a free 127.0.0.1 port answering `GET /props` with
`{"role":"router","models_autoload":true}` and `GET /v1/models` with a router listing of entries
`good`, status `unloaded`, `status.args = [<absolute existing file>, "-m", <path>]`.

Fixtures (deterministic bytes, in the run's private work dir):
  slow_<k>.gguf   GGUF v3, 0 KV, 600 000 tensor infos (F32, ne0 = 1, consistent offsets), data
                  section absent -> `invalid`, and slow enough that twenty of them exceed the
                  round-94 constant 60 s pass limit on the lane host
  ok.gguf         GGUF v3, one F32 tensor of 32 elements, data present -> `ok`
  ok2.gguf        a second distinct valid file -> `ok`
  fast_<k>.gguf   192-byte non-GGUF -> `invalid`, parsed in milliseconds
  big.gguf        GGUF v3 declaring 1 200 000 tensors (> MAX_TENSORS) -> `-` (disclosed limit)
  mid.gguf        GGUF v3, 700 000 tensor infos, no data section -> `invalid` (steps 6 x 700 000 =
                  4 200 000 <= MAX_STEPS 5 000 000 at M1; `-` at base -> the W11 discriminator)
  strbig.gguf     GGUF v3, 0 tensors, one uint32 string array of 6 000 000 one-byte strings
                  (54 MB: each element carries its u64 length) -> `-` (disclosed)
  budgetkill.gguf the same 54 MB array followed by one tensor whose declared offset is 1<<40:
                  capped parse -> `-`, a parse without a step cap -> `invalid` (amendment 6)
  missing         a path under the work dir that does not exist

Cells (expect `good`; verdict/reason read from `check --json` rows[0]):
  W01-slow-x1        1 entry  -m slow_0.gguf                      MODEL_UNLOADED router-model-invalid
  W02-slow-x8        8 entries naming 8 DISTINCT slow files       MODEL_UNLOADED router-model-invalid
  W03-slow-x40       40 entries naming 40 DISTINCT slow files     MODEL_UNLOADED router-model-invalid
                     (40 x ~2.0 s = ~82 s on the lane host: past the round-94 60 s constant)
                     ^ discriminator: round-94 base truncates this pass at its constant `timeout 60`
                     (the counter refuses to claim it unless the natural pass costs >= 1.5 x 60 s)
  W04-ok-x8          8 entries -m ok.gguf                         MODEL_OK router-unloaded-autoload
  W05-slow-then-ok   7 distinct slow files, then ok2 last          MODEL_OK router-unloaded-autoload
  W06-missing-x8     8 entries -m <missing>                       MODEL_UNLOADED router-model-missing
  W07-fast-k40       40 entries, 40 DISTINCT fast invalid files   MODEL_UNLOADED router-model-invalid
  W08-hardlink-x8    8 HARD LINKS to one slow inode               MODEL_UNLOADED router-model-invalid
  W09-undecided-big  1 entry -m big.gguf                          MODEL_OK router-unloaded-autoload
                     (disclosed: >MAX_TENSORS is undecidable -> loadable, round-89 rule)
  W10-rewrite        1 entry, two invocations, same-size rewrite  MODEL_OK then MODEL_UNLOADED
  W11-700k           1 entry -m mid.gguf (700 000 tensors)         MODEL_UNLOADED router-model-invalid
                     (the base probes grades this `-` loadable; see amendment-4 F1)
  W12-strings        1 entry -m strbig.gguf                       MODEL_OK router-unloaded-autoload
                     (disclosed: 6 000 000 string elements > MAX_STEPS -> `-` loadable)
  W13-budget-kill    1 entry -m budgetkill.gguf                   MODEL_OK router-unloaded-autoload
                     (the cap is load-bearing: without MAX_STEPS the same bytes are `invalid`)

Exit: 0 predicate met | 1 not met | 2 could-not-evaluate.
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

BASE = "a27656a454b1a2364f8b6e55f42fbca8c2e86ee4"  # round-94 M1 (per-file 15 s slice, timeout 60)
CELLS = 13
RUNS = 2
KILL = 1200
CAP = 4194304
TENSORS = 600_000
MID_TENSORS = 700_000
SLOW_FILES = 40
BASE_WRAPPER = 60.0   # the round-94 probe's constant pass limit
MARGIN = 1.25         # the honest pass must exceed 1.25 x the base constant, or nothing is claimed
MARGIN_HELP = ("distinct slow files in the W03 cell; below the margin guard the base control refuses. "
               "The count is a host-speed parameter: the guard needs the W03 pass to cost >= 1.25 x 60 s")


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


def gguf_strbig() -> bytes:
    # one KV entry: key "k", value a uint32 string array (type 9) of 6 000 000 one-char
    # strings (element type 8). Element count > MAX_STEPS, so the probe's step budget
    # governs the decision and grades `-`.
    # Round 96 amendment 2 (RV01 F1): a string array of N elements needs N length prefixes, so the
    # array must carry 8 * N bytes before any payload; the first version wrote one 6 MB element and
    # the probe's `base + 8 * n > size` guard graded the file `invalid` before the step budget ran.
    # 9 bytes per element (one-byte string + its u64 length) = 54 MB, so the per-element loop trips
    # MAX_STEPS at element 5 000 001 and the state is `-` (undecidable -> loadable).
    n = 6_000_000
    out = [b"GGUF", struct.pack("<I", 3), struct.pack("<QQ", 0, 1)]
    out.append(struct.pack("<Q", 1) + b"k")
    out.append(struct.pack("<IIQ", 9, 8, n))
    out.append((struct.pack("<Q", 1) + b"x") * n)  # interleaved: length prefix, then payload
    return b"".join(out)


def gguf_budgetkill() -> bytes:
    # Round 96 amendment 6 (wave-1 MT01 G1): the frozen cells cannot distinguish a bounded step
    # budget from an unbounded one, because every fixture's full parse is also `-`. This one is
    # capped-`-` but, parsed without a cap, reaches a tensor whose declared offset is wrong and
    # returns `invalid`: deleting MAX_STEPS therefore flips a graded cell.
    n = 6_000_000
    out = [b"GGUF", struct.pack("<I", 3), struct.pack("<QQ", 1, 1)]
    out.append(struct.pack("<Q", 1) + b"k")
    out.append(struct.pack("<IIQ", 9, 8, n))
    out.append((struct.pack("<Q", 1) + b"x") * n)
    name = b"t0"
    out.append(struct.pack("<Q", len(name)) + name + struct.pack("<IQIQ", 1, 1, 0, 1 << 40))
    return b"".join(out)


def fixture_class(path: Path) -> str:
    """The class this counter DESIGNED for its own fixture, decided from the bytes it wrote.

    Never consults the probe under test: that is the round-94 SC02 F1 defect (a sanity gate that
    used the base probe exited 2 on a loaded host before any cell ran). A fixture that does not
    match its designed class is a counter defect, not a probe verdict.
    """
    if not path.exists():
        return "missing"
    b = path.read_bytes()
    if len(b) < 24 or b[:4] != b"GGUF":
        return "invalid"
    n_tensors = struct.unpack_from("<Q", b, 8)[0]
    n_kv = struct.unpack_from("<Q", b, 16)[0]
    if n_tensors == 1 and len(b) > 50_000_000:  # budgetkill: capped `-`, uncapped `invalid`
        return "-"
    if n_tensors == 0 and n_kv >= 1:  # strbig: string-array past MAX_STEPS -> undecidable
        return "-"
    if n_tensors > 1_000_000:  # the probe's MAX_TENSORS: designed undecidable
        return "-"
    if n_tensors > 833_333:  # at M1 (MAX_STEPS = 5 000 000): > MAX_STEPS/6 -> undecidable
        return "-"
    return "ok" if n_tensors <= 2 else "invalid"


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


def build_fixtures(w: Path, n_slow: int = SLOW_FILES):
    slow = []
    for k in range(n_slow):
        p = w / f"slow_{k}.gguf"
        p.write_bytes(gguf(TENSORS, 1, False))
        slow.append(str(p))
    ok = w / "ok.gguf"
    ok.write_bytes(gguf(1, 32, True))
    ok2 = w / "ok2.gguf"
    ok2.write_bytes(gguf(2, 32, True))
    fast = []
    for k in range(40):
        p = w / f"fast_{k}.gguf"
        p.write_bytes(b"NOTAGGUF" + bytes([k]) * 184)
        fast.append(str(p))
    big = w / "big.gguf"
    big.write_bytes(gguf(1_200_000, 1, False))
    mid = w / "mid.gguf"
    mid.write_bytes(gguf(MID_TENSORS, 1, False))
    strbig = w / "strbig.gguf"
    strbig.write_bytes(gguf_strbig())
    budgetkill = w / "budgetkill.gguf"
    budgetkill.write_bytes(gguf_budgetkill())
    for p, want in ((ok, "ok"), (ok2, "ok"), (Path(slow[0]), "invalid"),
                    (Path(fast[0]), "invalid"), (big, "-"), (mid, "invalid"), (strbig, "-"),
                    (budgetkill, "-")):
        got = fixture_class(p)
        if got != want:
            raise CannotEvaluate(f"fixture {p.name} designed {want!r}, oracle says {got!r}")
    return slow, str(ok), str(ok2), fast, str(big), str(mid), str(strbig), str(budgetkill)


def evaluate_pass(R: Runner, w: Path, label: str, n_runs: int, n_slow: int = SLOW_FILES):
    n_slow = max(8, n_slow)
    fx = w / label
    fx.mkdir(parents=True, exist_ok=True)
    slow, ok, ok2, fast, big, mid, strbig, budgetkill = build_fixtures(fx, n_slow)
    missing = str(fx / "absent" / "missing.gguf")
    exe = ok  # status.args[0] must be an existing absolute local file

    hard = []
    for k in range(8):
        hl = fx / f"slow-hl-{k}.gguf"
        try:
            os.link(slow[0], hl)
        except OSError:
            hl.write_bytes(Path(slow[0]).read_bytes())
        hard.append(str(hl))

    cells = [
        ("W01-slow-x1", [[exe, "-m", slow[0]]], "MODEL_UNLOADED", "router-model-invalid"),
        ("W02-slow-x8", [[exe, "-m", slow[k]] for k in range(8)], "MODEL_UNLOADED", "router-model-invalid"),
        ("W03-slow-x40", [[exe, "-m", slow[k]] for k in range(n_slow)], "MODEL_UNLOADED",
         "router-model-invalid"),
        ("W04-ok-x8", [[exe, "-m", ok]] * 8, "MODEL_OK", "router-unloaded-autoload"),
        ("W05-slow-then-ok", [[exe, "-m", slow[k]] for k in range(7)] + [[exe, "-m", ok2]],
         "MODEL_OK", "router-unloaded-autoload"),
        ("W06-missing-x8", [[exe, "-m", missing]] * 8, "MODEL_UNLOADED", "router-model-missing"),
        ("W07-fast-k40", [[exe, "-m", f] for f in fast], "MODEL_UNLOADED", "router-model-invalid"),
        ("W08-hardlink-x8", [[exe, "-m", h] for h in hard], "MODEL_UNLOADED", "router-model-invalid"),
        ("W09-undecided-big", [[exe, "-m", big]], "MODEL_OK", "router-unloaded-autoload"),
        ("W11-700k", [[exe, "-m", mid]], "MODEL_UNLOADED", "router-model-invalid"),
        ("W12-strings", [[exe, "-m", strbig]], "MODEL_OK", "router-unloaded-autoload"),
        ("W13-budget-kill", [[exe, "-m", budgetkill]], "MODEL_OK", "router-unloaded-autoload"),
    ]
    results = {}
    durations = {}
    for cid, args, wv, wr in cells:
        routes = {"/v1/models": router_body(args), "/props": PROPS}
        runs = []
        with Stub(routes) as st:
            for _ in range(n_runs):
                runs.append(R.check(st.port))
        good = all(v == wv and r == wr for _, v, r, _ in runs)
        verdicts = [(v, r) for _, v, r, _ in runs]
        detail = " ".join(f"run{i + 1}={v}/{r}/{dt:.2f}s" for i, (_, v, r, dt) in enumerate(runs))
        print(f"ROUTER_BUDGET96_CELL {label} {cid} ok={int(good)} want={wv}/{wr} {detail}", flush=True)
        results[cid] = (good, verdicts, wv, wr)
        durations[cid] = max((dt for _, _, _, dt in runs), default=0.0)

    # W10: same-size in-place rewrite with mtime restored; ctime is the discriminator (r93 RV01).
    target = Path(slow[1])
    orig = target.read_bytes()
    st0 = os.stat(target)
    route = {"/v1/models": router_body([[exe, "-m", str(target)]]), "/props": PROPS}
    try:
        with Stub(route) as st1:
            _, v1, r1, _ = R.check(st1.port)
        valid = gguf(1, 32, True)
        if len(valid) < len(orig):
            valid += b"\0" * (len(orig) - len(valid))
        target.write_bytes(valid[:len(orig)])
        os.utime(target, ns=(st0.st_atime_ns, st0.st_mtime_ns))
        with Stub(route) as st2:
            _, v2, r2, _ = R.check(st2.port)
        target.write_bytes(orig)
        os.utime(target, ns=(st0.st_atime_ns, st0.st_mtime_ns))
        with Stub(route) as st3:
            _, v3, r3, _ = R.check(st3.port)
    finally:
        try:
            target.write_bytes(orig)
        except Exception:
            pass
    good = (v2 == "MODEL_OK" and v3 == "MODEL_UNLOADED" and r3 == "router-model-invalid")
    print(f"ROUTER_BUDGET96_CELL {label} W10-rewrite ok={int(good)} "
          f"v1={v1}/{r1} v2={v2}/{r2} v3={v3}/{r3}", flush=True)
    results["W10-rewrite"] = (good, [(v1, r1), (v2, r2), (v3, r3)], "MODEL_OK+MODEL_UNLOADED",
                              "rewrite-flips")
    durations["W10-rewrite"] = 0.0
    return results, durations


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--work", type=Path, required=True)
    ap.add_argument("--probe-file", type=Path)
    ap.add_argument("--burners", type=int, default=64)
    ap.add_argument("--slow-files", type=int, default=SLOW_FILES, help=MARGIN_HELP)
    ap.add_argument("--runs", type=int, default=RUNS)
    ap.add_argument("--skip-load", action="store_true",
                    help="natural pass only (red-control runs: the W03 discriminator is load-independent)")
    ap.add_argument("--allow-clock", action="store_true",
                    help="grade a probe that still decides on a wall clock (the red control)")
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
        if b"DEADLINE" in mbytes and not a.allow_clock:
            raise CannotEvaluate(f"{rev}: probe still decides on a wall clock (round-94 shape); pass --allow-clock to grade it as the red control")
        a.work.mkdir(parents=True, exist_ok=True)
        work = Path(tempfile.mkdtemp(prefix="r96-budget-", dir=a.work)).resolve()
        try:
            R = Runner(work)
            R.install(mbytes)
            natural, nat_dt = evaluate_pass(R, work, "nat", runs, a.slow_files)
            w03 = nat_dt.get("W03-slow-x40", 0.0)
            # The round-94 probe truncated this pass at its constant 60 s; if the pass is cheaper than
            # 1.5 x that constant on this host, the base control cannot discriminate and nothing is claimed.
            # The guard belongs to the probe under CLAIM: if its honest pass is cheaper than the base
            # constant, the base would never truncate and the discriminator does not exist. A base run
            # (--allow-clock) is expected to come back early precisely because it truncated.
            if not a.allow_clock and w03 < MARGIN * BASE_WRAPPER:
                print(f"ROUTER_BUDGET96 could-not-evaluate: W03 natural pass {w03:.1f}s < "
                      f"{MARGIN:.2f} x {BASE_WRAPPER:.0f}s — the round-94 constant wrapper would not "
                      f"truncate this listing on this host, so no discriminator is claimed")
                return 2
            if a.skip_load:
                # CR01 DEFECT-3: no second pass ran; the summary must not claim load evidence
                load_cells = 0
                print("ROUTER_BUDGET96 load_skipped=true load_cells=0 load_stable=0 (no second pass ran; predicate unreachable)", flush=True)
                print(f"ROUTER_BUDGET96 cells={len(set(natural))} mismatches=-2 positive_mismatches=-2 load_cells=0 load_stable=0 budget=work probe={mode} probe_sha256={sha256(mbytes)} base_sha256={sha256(bbytes)} rev={rev} w03_seconds={w03:.1f} load1_nat={loadavg()} burners={a.burners} load_note=skipped")
                return 1
            else:
                burners = start_burners(a.burners) if a.burners > 0 else []
                try:
                    loaded, _ = evaluate_pass(R, work, "load", runs, a.slow_files)
                finally:
                    stop_burners(burners)
        finally:
            shutil.rmtree(work, ignore_errors=True)
    except CannotEvaluate as e:
        print(f"ROUTER_BUDGET96 could-not-evaluate: {e}")
        return 2

    mismatches = 0
    positive_mismatches = 0
    load_stable = 1
    cids = sorted(set(natural) | set(loaded))
    for cid in cids:
        ng, nv, _, _ = natural.get(cid, (False, [], "-", "-"))
        lg, lv, _, _ = loaded.get(cid, (False, [], "-", "-"))
        if nv != lv:
            load_stable = 0
            print(f"ROUTER_BUDGET96_UNSTABLE {cid} natural={nv} loaded={lv}", flush=True)
        if not (ng and lg):
            mismatches += 1
            if cid not in ("W09-undecided-big", "W12-strings"):
                positive_mismatches += 1
    print(f"ROUTER_BUDGET96 cells={len(cids)} mismatches={mismatches} "
          f"positive_mismatches={positive_mismatches} load_cells={len(cids)} load_stable={load_stable} "
          f"budget=work probe={mode} probe_sha256={sha256(mbytes)} base_sha256={sha256(bbytes)} "
          f"rev={rev} w03_seconds={w03:.1f} load1_nat={loadavg()} burners={a.burners}")
    return 0 if (mismatches == 0 and load_stable == 1 and len(cids) == CELLS) else 1


if __name__ == "__main__":
    sys.exit(main())
