#!/usr/bin/env python3
"""round99-router-budget.py - round-99 C1 (operability) instrument.

ROUND-99 PREDICATE (frozen: plans/round-99-claims.md section C1), about the CONTROL MODE:

    The round-98 predecessor's `--control` mode graded mutant survival but never compared the
    cells it ran to the cells it selected: a counter whose cell set silently lost one entry
    printed `cells=16 ... survived=1 ok=1` and exited 0. This successor prints
    `selected=<n> ran=<m> population_ok=<0|1>` in every control line and its exit status requires
    `population_ok=1`. `tools/round99-control-population.py` is the grader: it applies the same
    dropped-cell byte mutation to this file and to `tools/round98-router-budget.py` and requires
    the successor to refuse (exit 1) while the predecessor accepts (exit 0), and the unmodified
    successor to accept a complete population (exit 0).

The natural 19-cell predicate below is round 98's, carried unchanged in behaviour; this file
adds no cell and changes no expectation. Its bytes are frozen at the round-99 freeze commit.

PREDICATE (round 98, carried):

    `python3 tools/round99-router-budget.py --repo <lane> --rev <M> --work <scratch> --slow-files 72`
    prints `ROUTER_BUDGET99 cells=19 mismatches=0 positive_mismatches=0 load_cells=19 load_stable=1
    budget=work ...` and exits 0 at the measured commit M, the counter's bytes identical to the
    freeze commit.

Successor to tools/round97-router-budget.py (17 cells, frozen, never edited). Round-97's
closing wave (RV03 F5) proved a probe that OVERCHARGES by one step per header (+1/header, e.g.
charging 6+nd instead of 5+nd) passes all 17 cells: every fixture's +1 parse is on the same side
of MAX_STEPS as the real parse. Round 98 adds two cells past that (new set = six cells, mutants = five):

  W18-800k-nd1     800 000 tensor headers, nd=1 -> real 4 + 6 x 800 000 = 4 800 004 steps <=
                   MAX_STEPS, `invalid`; a probe charging one extra step per header needs
                   4 + 7 x 800 000 = 5 600 004 > MAX_STEPS, `-` -> caught.
  W19-520k-nd4     520 000 tensor headers, nd=4 -> real 4 + 9 x 520 000 = 4 680 004 steps <=
                   MAX_STEPS, `invalid`; a +1/header probe needs 4 + 10 x 520 000 = 5 200 004
                   > MAX_STEPS, `-` -> caught.

The four round-97 new cells (W14-W17, listed in the frozen round-97 counter, never
edited) survive the new overcharge mutant too: each +1 parse is on the same side of
MAX_STEPS as the real parse (each is already `-`). The do-nothing control therefore runs
the 17 round-97 cells (`--cells r97set`) with the overcharge mutant: `survived=1`.

Control modes (natural pass only; the predicate cannot be reached through them):

    --control --cells legacy --expect survived --mutant <m>   every one of the 13 round-96 cells
                                                              passes with the mutant installed
    --control --cells new --expect caught --mutant <m>        at least one new cell fails

Every control line carries `selected=<n> ran=<m> population_ok=<0|1>`; `ok=1` and exit 0 require
`population_ok=1` (round 99). A control whose executed cell set is shorter than the selected set is
refused even when every cell it did run passed.

The mutants are byte patches of the probe under claim, applied exactly once and refused when
the anchor does not match (`CannotEvaluate`), never edits of the tracked file.

Defect being closed (round-96 closure routed MT01 G2 and the r97 plan item 1): a probe that
stopped charging per header, or charged a constant 6, still passed every round-96 cell.

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
  t900k.gguf      GGUF v3, 900 000 tensor infos at nd=1, no data -> `-` (5 400 004 steps)
  mid4.gguf       GGUF v3, 700 000 tensor infos at nd=4, no data -> `-` (6 300 004 steps)
  t833333.gguf    GGUF v3, 833 333 tensor infos at nd=1, no data -> `-` (5 000 002 steps)
  maxmeta.gguf    GGUF v3, 1 KV string of 160 MiB, then one tensor whose offset is 1<<40 ->
                  `invalid` at MAX_META 512 MiB (the position check fires at the next field for
                  a probe whose MAX_META is 100 MiB -> `-`)
  t800k.gguf      GGUF v3, 800 000 tensor infos at nd=1, no data -> `invalid`
                  (4 800 004 steps; a +1/header probe needs 5 600 004 -> `-`)
  m520k4.gguf     GGUF v3, 520 000 tensor infos at nd=4, no data -> `invalid`
                  (4 680 004 steps; a +1/header probe needs 5 200 004 -> `-`)
  missing         a path under the work dir that does not exist

Cells (expect `good`; verdict/reason read from `check --json` rows[0]):
  W01-slow-x1        1 entry  -m slow_0.gguf                      MODEL_UNLOADED router-model-invalid
  W02-slow-x8        8 entries naming 8 DISTINCT slow files       MODEL_UNLOADED router-model-invalid
  W03-slow-x40       40 entries naming 40 DISTINCT slow files     MODEL_UNLOADED router-model-invalid
                     (40 x ~2.0 s = ~82 s on the lane host: past the round-94 60 s constant)
                     ^ discriminator: round-94 base truncates this pass at its constant `timeout 60`
                     (the counter refuses to claim it unless the natural pass costs >= 1.25 x 60 s)
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
  W14-900k-nd1       1 entry -m t900k.gguf (900 000 tensors, nd=1) MODEL_OK router-unloaded-autoload
                     (round-97: `-` because 5 400 004 > MAX_STEPS; a probe that stopped charging
                     per header decides `invalid` -> caught)
  W15-700k-nd4       1 entry -m mid4.gguf (700 000 tensors, nd=4)   MODEL_OK router-unloaded-autoload
                     (round-97: `-` because 6 300 004 > MAX_STEPS; a constant-6 probe needs
                     4 200 000 and decides `invalid` -> caught)
  W16-maxmeta        1 entry -m maxmeta.gguf                       MODEL_UNLOADED router-model-invalid
                     (round-97: `invalid` at MAX_META 512 MiB; a probe capped at 100 MiB grades
                     `-` -> caught)
  W17-833333-nd1     1 entry -m t833333.gguf (833 333 tensors, nd=1) MODEL_OK router-unloaded-autoload
                     (round-97: `-` at 5 000 002 > MAX_STEPS; a probe that drops the 4 preamble
                     steps decides `invalid` -> caught)
  W18-800k-nd1       1 entry -m t800k.gguf (800 000 tensors, nd=1)  MODEL_UNLOADED router-model-invalid
                     (round-98: real `invalid` at 4 800 004 <= MAX_STEPS; a +1/header probe
                     needs 5 600 004 -> `-` -> caught)
  W19-520k-nd4       1 entry -m m520k4.gguf (520 000 tensors, nd=4)  MODEL_UNLOADED router-model-invalid
                     (round-98: real `invalid` at 4 680 004 <= MAX_STEPS; a +1/header probe
                     needs 5 200 004 -> `-` -> caught)

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
CELLS = 19
LEGACY_CELLS = {"W01-slow-x1", "W02-slow-x8", "W03-slow-x40", "W04-ok-x8", "W05-slow-then-ok",
                "W06-missing-x8", "W07-fast-k40", "W08-hardlink-x8", "W09-undecided-big",
                "W10-rewrite", "W11-700k", "W12-strings", "W13-budget-kill"}
NEW_CELLS = {"W14-900k-nd1", "W15-700k-nd4", "W16-maxmeta", "W17-833333-nd1",
             "W18-800k-nd1", "W19-520k-nd4"}
R97_CELLS = LEGACY_CELLS | {"W14-900k-nd1", "W15-700k-nd4", "W16-maxmeta", "W17-833333-nd1"}
RUNS = 2
KILL = 3600
CAP = 4194304
TENSORS = 600_000
MID_TENSORS = 700_000
BIG_TENSORS = 900_000
EDGE_TENSORS = 833_333
OVER_TENSORS = 800_000
OVER4_TENSORS = 520_000
SLOW_FILES = 40
MAXMETA_BYTES = 160 * 1024 ** 2
BASE_WRAPPER = 60.0   # the round-94 probe's constant pass limit
MARGIN = 1.25         # the honest pass must exceed 1.25 x the base constant, or nothing is claimed
MARGIN_HELP = ("distinct slow files in the W03 cell; below the margin guard the base control refuses. "
               "The count is a host-speed parameter: the guard needs the W03 pass to cost >= 1.25 x 60 s")

# Byte patches of the probe under claim. Each anchor must appear exactly once in the probe bytes;
# a patch that does not apply is `could-not-evaluate`, never a silently unmutated run.
MUTANTS = {
    "flat6": [(b"                ne = [u64() for _ in range(nd)] or [1]",
               b"                _b = rd(8 * nd)\n"
               b"                ne = [struct.unpack(\"<Q\", _b[8 * i:8 * i + 8])[0]"
               b" for i in range(nd)] or [1]")],
    "undercharge": [(b"        def need(n):\n            steps[0] += 1\n",
                     b"        def need(n):\n            steps[0] += 1 if n >= 32 else 0\n")],
    "maxmeta": [(b"MAX_KV, MAX_ARR, MAX_TENSORS, MAX_META = 100_000, 50_000_000, "
                 b"1_000_000, 512 * 1024 ** 2",
                 b"MAX_KV, MAX_ARR, MAX_TENSORS, MAX_META = 100_000, 50_000_000, "
                 b"1_000_000, 100 * 1024 ** 2")],
    "nopreamble": [(b"    steps = [0]\n    with f:\n        def need(n):\n            steps[0] += 1\n",
                    b"    steps = [0]\n    calls = [0]\n    with f:\n        def need(n):\n"
                    b"            calls[0] += 1\n"
                    b"            steps[0] += 0 if calls[0] <= 4 else 1\n")],
    "overcharge": [(b"            for _ in range(n_tensors):",
                    b"            for _ in range(n_tensors):\n                steps[0] += 1")],
}


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


def gguf(n_tensors: int, elems: int, with_data: bool, nd: int = 1) -> bytes:
    out = [b"GGUF", struct.pack("<I", 3), struct.pack("<QQ", n_tensors, 0)]
    off = 0
    for i in range(n_tensors):
        name = b"t%07d" % i
        dims = struct.pack("<" + "Q" * nd, elems, *([1] * (nd - 1)))
        out.append(struct.pack("<Q", len(name)) + name + struct.pack("<I", nd) + dims
                   + struct.pack("<IQ", 0, off))
        off += (elems * 4 + 31) // 32 * 32
    head = b"".join(out)
    pad = (len(head) + 31) // 32 * 32 - len(head)
    return head + b"\0" * pad + (b"\0" * off if with_data else b"\0" * 16)


def gguf_maxmeta() -> bytes:
    # Round-97 C2: one KV entry whose value is a 160 MiB GGUF string (type 8: u64 length then
    # bytes), followed by one tensor whose declared offset is 1 << 40. The position checks in
    # `need()` fire at the field AFTER the string, so a probe with MAX_META = 512 MiB reaches the
    # tensor and returns `invalid`, while a probe capped at 100 MiB raises Unknown and grades `-`.
    # The 160 MiB payload is a seek target, not a read: one skip() charges one step for the whole
    # string, so the step budget (5 000 000) never binds on this fixture.
    payload_len = MAXMETA_BYTES
    out = [b"GGUF", struct.pack("<I", 3), struct.pack("<QQ", 1, 1)]
    out.append(struct.pack("<Q", 1) + b"k")
    out.append(struct.pack("<I", 8))          # value type: GGUF string (u64 length + bytes)
    out.append(struct.pack("<Q", payload_len))
    out.append(b"\0" * 64)          # the string's first bytes; the rest is a hole of the same file
    name = b"t0"
    tail = (struct.pack("<Q", len(name)) + name + struct.pack("<IQIQ", 1, 1, 0, 1 << 40))
    # Materialize the declared length with a sparse hole, then the tensor tail after it.
    head = b"".join(out)
    return head + b"\0" * (payload_len - 64) + tail


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

    Round-97: the step class is rank-aware. With MAX_STEPS = 5 000 000 and 4 preamble steps, a
    header costs 5 + nd, so 900 000 headers at nd=1 (5 400 004) and 700 000 at nd=4 (6 300 004)
    are undecidable (`-`), while 700 000 at nd=1 (4 200 004) decides (`invalid`).
    """
    if not path.exists():
        return "missing"
    b = path.read_bytes()
    if len(b) < 24 or b[:4] != b"GGUF":
        return "invalid"
    n_tensors = struct.unpack_from("<Q", b, 8)[0]
    n_kv = struct.unpack_from("<Q", b, 16)[0]
    if n_tensors == 1 and len(b) > 100_000_000:  # maxmeta: invalid at MAX_META 512 MiB
        return "invalid"
    if n_tensors == 1 and len(b) > 50_000_000:  # budgetkill: capped `-`, uncapped `invalid`
        return "-"
    if n_tensors == 0 and n_kv >= 1:  # strbig: string-array past MAX_STEPS -> undecidable
        return "-"
    if n_tensors > 1_000_000:  # the probe's MAX_TENSORS: designed undecidable
        return "-"
    nd = 1
    if n_tensors:
        name_len = struct.unpack_from("<Q", b, 24)[0]
        nd = struct.unpack_from("<I", b, 32 + name_len)[0]
    steps = 4 + n_tensors * (5 + nd)
    if steps > 5_000_000:  # undecidable -> loadable
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
    t900k = w / "t900k.gguf"
    t900k.write_bytes(gguf(BIG_TENSORS, 1, False))
    mid4 = w / "mid4.gguf"
    mid4.write_bytes(gguf(MID_TENSORS, 1, False, nd=4))
    maxmeta = w / "maxmeta.gguf"
    maxmeta.write_bytes(gguf_maxmeta())
    edge = w / "t833333.gguf"
    edge.write_bytes(gguf(EDGE_TENSORS, 1, False))
    t800k = w / "t800k.gguf"
    t800k.write_bytes(gguf(OVER_TENSORS, 1, False))
    m520k4 = w / "m520k4.gguf"
    m520k4.write_bytes(gguf(OVER4_TENSORS, 1, False, nd=4))
    checks = [(ok, "ok"), (ok2, "ok"), (Path(fast[0]), "invalid"), (big, "-"), (mid, "invalid"),
              (strbig, "-"), (budgetkill, "-"), (t900k, "-"), (mid4, "-"), (maxmeta, "invalid"),
              (edge, "-"), (t800k, "invalid"), (m520k4, "invalid")]
    if slow:
        checks.append((Path(slow[0]), "invalid"))
    for p, want in checks:
        got = fixture_class(p)
        if got != want:
            raise CannotEvaluate(f"fixture {p.name} designed {want!r}, oracle says {got!r}")
    return (slow, str(ok), str(ok2), fast, str(big), str(mid), str(strbig), str(budgetkill),
            str(t900k), str(mid4), str(maxmeta), str(edge), str(t800k), str(m520k4))


def evaluate_pass(R: Runner, w: Path, label: str, n_runs: int, n_slow: int = SLOW_FILES,
                  selected=None):
    if selected is None or (set(selected) & LEGACY_CELLS):
        n_slow = max(8, n_slow)
    else:
        n_slow = 0
    fx = w / label
    fx.mkdir(parents=True, exist_ok=True)
    (slow, ok, ok2, fast, big, mid, strbig, budgetkill,
     t900k, mid4, maxmeta, edge, t800k, m520k4) = build_fixtures(fx, n_slow)
    missing = str(fx / "absent" / "missing.gguf")
    exe = ok  # status.args[0] must be an existing absolute local file

    hard = []
    for k in range(8):
        if not slow:
            break
        hl = fx / f"slow-hl-{k}.gguf"
        try:
            os.link(slow[0], hl)
        except OSError:
            hl.write_bytes(Path(slow[0]).read_bytes())
        hard.append(str(hl))

    cells = [
        ("W14-900k-nd1", [[exe, "-m", t900k]], "MODEL_OK", "router-unloaded-autoload"),
        ("W15-700k-nd4", [[exe, "-m", mid4]], "MODEL_OK", "router-unloaded-autoload"),
        ("W16-maxmeta", [[exe, "-m", maxmeta]], "MODEL_UNLOADED", "router-model-invalid"),
        ("W17-833333-nd1", [[exe, "-m", edge]], "MODEL_OK", "router-unloaded-autoload"),
        ("W18-800k-nd1", [[exe, "-m", t800k]], "MODEL_UNLOADED", "router-model-invalid"),
        ("W19-520k-nd4", [[exe, "-m", m520k4]], "MODEL_UNLOADED", "router-model-invalid"),
    ]
    if slow:
        cells += [
            ("W01-slow-x1", [[exe, "-m", slow[0]]], "MODEL_UNLOADED", "router-model-invalid"),
            ("W02-slow-x8", [[exe, "-m", slow[k]] for k in range(8)], "MODEL_UNLOADED",
             "router-model-invalid"),
            ("W03-slow-x40", [[exe, "-m", slow[k]] for k in range(n_slow)], "MODEL_UNLOADED",
             "router-model-invalid"),
            ("W04-ok-x8", [[exe, "-m", ok]] * 8, "MODEL_OK", "router-unloaded-autoload"),
            ("W05-slow-then-ok", [[exe, "-m", slow[k]] for k in range(7)] + [[exe, "-m", ok2]],
             "MODEL_OK", "router-unloaded-autoload"),
            ("W06-missing-x8", [[exe, "-m", missing]] * 8, "MODEL_UNLOADED", "router-model-missing"),
            ("W07-fast-k40", [[exe, "-m", f] for f in fast], "MODEL_UNLOADED", "router-model-invalid"),
            ("W08-hardlink-x8", [[exe, "-m", h] for h in hard], "MODEL_UNLOADED",
             "router-model-invalid"),
            ("W09-undecided-big", [[exe, "-m", big]], "MODEL_OK", "router-unloaded-autoload"),
            ("W11-700k", [[exe, "-m", mid]], "MODEL_UNLOADED", "router-model-invalid"),
            ("W12-strings", [[exe, "-m", strbig]], "MODEL_OK", "router-unloaded-autoload"),
            ("W13-budget-kill", [[exe, "-m", budgetkill]], "MODEL_OK", "router-unloaded-autoload"),
        ]
    if selected is not None:
        cells = [c for c in cells if c[0] in set(selected)]
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
        detail += f" entries={n_slow}"
        print(f"ROUTER_BUDGET99_CELL {label} {cid} ok={int(good)} want={wv}/{wr} {detail}", flush=True)
        results[cid] = (good, verdicts, wv, wr)
        durations[cid] = max((dt for _, _, _, dt in runs), default=0.0)

    # W10: same-size in-place rewrite with mtime restored; ctime is the discriminator (r93 RV01).
    if slow and (selected is None or "W10-rewrite" in set(selected)):
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
        print(f"ROUTER_BUDGET99_CELL {label} W10-rewrite ok={int(good)} "
              f"v1={v1}/{r1} v2={v2}/{r2} v3={v3}/{r3}", flush=True)
        results["W10-rewrite"] = (good, [(v1, r1), (v2, r2), (v3, r3)],
                                  "MODEL_OK+MODEL_UNLOADED", "rewrite-flips")
        durations["W10-rewrite"] = 0.0
    return results, durations


def apply_mutant(mbytes: bytes, mutant: str) -> bytes:
    if mutant == "none":
        return mbytes
    for anchor, replacement in MUTANTS[mutant]:
        n = mbytes.count(anchor)
        if n != 1:
            raise CannotEvaluate(
                f"mutant {mutant}: anchor appears {n} times, not exactly once")
        mbytes = mbytes.replace(anchor, replacement, 1)
    return mbytes


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--work", type=Path, required=True)
    ap.add_argument("--probe-file", type=Path)
    ap.add_argument("--burners", type=int, default=64)
    ap.add_argument("--slow-files", type=int, default=SLOW_FILES, help=MARGIN_HELP)
    ap.add_argument("--runs", type=int, default=RUNS)
    ap.add_argument("--cells", choices=("all", "legacy", "new", "r97set"), default="all")
    ap.add_argument("--mutant", choices=("none", "flat6", "undercharge", "maxmeta",
                                        "nopreamble", "overcharge"), default="none")
    ap.add_argument("--control", action="store_true",
                    help="natural pass only; grades mutant survival/catch, never the predicate")
    ap.add_argument("--expect", choices=("survived", "caught"),
                    help="with --control: every selected cell ok (survived) or at least one red (caught)")
    ap.add_argument("--expect-cell",
                    help="with --control: the named cell must be green (survived) or red (caught), "
                         "not merely some cell")
    ap.add_argument("--skip-load", action="store_true",
                    help="natural pass only (red-control runs: the W03 discriminator is load-independent)")
    ap.add_argument("--allow-clock", action="store_true",
                    help="grade a probe that still decides on a wall clock (the red control)")
    a = ap.parse_args()
    if a.control and (not a.expect or a.mutant == "none" and a.expect == "caught"):
        print("ROUTER_BUDGET99 usage: --control requires --expect and, for `caught`, a --mutant")
        return 64
    if a.runs < 1:
        print("ROUTER_BUDGET99 usage: --runs must be >= 1 (a zero-run pass grades nothing)")
        return 64
    runs = 1 if a.control else a.runs
    selected = {"all": None, "legacy": LEGACY_CELLS, "new": NEW_CELLS,
                "r97set": R97_CELLS}[a.cells]
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
        mbytes = apply_mutant(mbytes, a.mutant)
        if b"DEADLINE" in mbytes and not a.allow_clock:
            raise CannotEvaluate(f"{rev}: probe still decides on a wall clock (round-94 shape); pass --allow-clock to grade it as the red control")
        a.work.mkdir(parents=True, exist_ok=True)
        work = Path(tempfile.mkdtemp(prefix="r99-budget-", dir=a.work)).resolve()
        try:
            R = Runner(work)
            R.install(mbytes)
            natural, nat_dt = evaluate_pass(R, work, "nat", runs, a.slow_files, selected)
            w03 = nat_dt.get("W03-slow-x40", 0.0)
            if a.control:
                # Round 99 (C1): a control receipt grades the population it was asked for. The
                # round-98 predecessor printed `cells=<ran>` and returned ok on a dropped-cell
                # mutation (observed cells=16, exit 0); here the selected count is compared to the
                # cells the pass actually ran, and a short pass cannot pass.
                want_selected = CELLS if selected is None else len(selected)
                n_ok = sum(1 for good, _, _, _ in natural.values() if good)
                n = len(natural)
                population_ok = int(n == want_selected)
                survived = int(n_ok == n)
                caught = int(n_ok < n)
                cell = "-"
                cell_ok = None
                if a.expect_cell:
                    if a.expect_cell not in natural:
                        print(f"ROUTER_BUDGET99 could-not-evaluate: --expect-cell {a.expect_cell} "
                              f"is not in the selected cells")
                        return 2
                    cell = a.expect_cell
                    cell_ok = int(natural[cell][0])
                    ok = cell_ok if a.expect == "survived" else (1 - cell_ok)
                else:
                    ok = survived if a.expect == "survived" else caught
                ok = int(ok and population_ok)
                print(f"ROUTER_BUDGET99_CONTROL cells={n} cells_ok={n_ok} selected={want_selected} "
                      f"ran={n} population_ok={population_ok} mutant={a.mutant} "
                      f"slow_files={a.slow_files} runs={runs} "
                      f"expect={a.expect} expect_cell={cell} cell_ok="
                      f"{'-' if cell_ok is None else cell_ok} survived={survived} caught={caught} "
                      f"probe={mode} probe_sha256={sha256(mbytes)} rev={rev} ok={ok}")
                return 0 if ok else 1
            # The round-94 probe truncated this pass at its constant 60 s; if the pass is cheaper than
            # 1.25 x that constant on this host, the round-94 base control cannot discriminate.
            if not a.allow_clock and w03 < MARGIN * BASE_WRAPPER:
                print(f"ROUTER_BUDGET99 could-not-evaluate: W03 natural pass {w03:.1f}s < "
                      f"{MARGIN:.2f} x {BASE_WRAPPER:.0f}s — the round-94 constant wrapper would not "
                      f"truncate this listing on this host, so no discriminator is claimed")
                return 2
            if a.skip_load:
                print("ROUTER_BUDGET99 load_skipped=true load_cells=0 load_stable=0 (no second pass ran; predicate unreachable)", flush=True)
                print(f"ROUTER_BUDGET99 cells={len(set(natural))} mismatches=-2 positive_mismatches=-2 "
                      f"load_cells=0 load_stable=0 budget=work probe={mode} mutant={a.mutant} "
                      f"probe_sha256={sha256(mbytes)} base_sha256={sha256(bbytes)} rev={rev} "
                      f"w03_seconds={w03:.1f} load1_nat={loadavg()} burners={a.burners} load_note=skipped")
                return 1
            burners = start_burners(a.burners) if a.burners > 0 else []
            try:
                loaded, _ = evaluate_pass(R, work, "load", runs, a.slow_files, selected)
            finally:
                stop_burners(burners)
        finally:
            shutil.rmtree(work, ignore_errors=True)
    except CannotEvaluate as e:
        print(f"ROUTER_BUDGET99 could-not-evaluate: {e}")
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
            print(f"ROUTER_BUDGET99_UNSTABLE {cid} natural={nv} loaded={lv}", flush=True)
        if not (ng and lg):
            mismatches += 1
            if cid not in ("W09-undecided-big", "W12-strings"):
                positive_mismatches += 1
    want_cells = CELLS if selected is None else len(selected)
    print(f"ROUTER_BUDGET99 cells={len(cids)} mismatches={mismatches} "
          f"positive_mismatches={positive_mismatches} load_cells={len(cids)} load_stable={load_stable} "
          f"budget=work probe={mode} mutant={a.mutant} slow_files={a.slow_files} runs={runs} "
          f"probe_sha256={sha256(mbytes)} "
          f"base_sha256={sha256(bbytes)} rev={rev} w03_seconds={w03:.1f} "
          f"load1_nat={loadavg()} burners={a.burners}")
    return 0 if (mismatches == 0 and load_stable == 1 and len(cids) == want_cells) else 1


if __name__ == "__main__":
    sys.exit(main())
