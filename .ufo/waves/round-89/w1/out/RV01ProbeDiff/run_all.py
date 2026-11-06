#!/usr/bin/env python3
"""RV01ProbeDiff — C1 diff review harness (round 89 w1, seat RV01ProbeDiff).

Runs the base (56174a1) and measured (4f9eacf7) tools/kama-probe.sh bytes against
a stub llama.cpp router for precedence / set -e / flag-form / fixture scenarios,
and against the pinned b12177 llama-server for real-loader ground truth on each
crafted GGUF fixture. Also diffs the probe QSIZES table against S585 constants.py.

Writes results.json + results.md into the out dir. Starts and kills only its own
children, all bound to 127.0.0.1 on free ports.
"""
import ast
import json
import os
import re
import shutil
import signal
import socket
import subprocess
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = "/fast/scratch/hyaku/kama-r89/RV01ProbeDiff"
FILES = os.path.join(SCRATCH, "files")
LS = "/home/vgpnk/.local/opt/llama-b12177/llama-server"
PROBE_M = os.path.join(SCRATCH, "probe-measured.sh")
PROBE_B = os.path.join(SCRATCH, "probe-base.sh")
OUT = os.path.abspath(os.path.join(HERE))
RESULTS = {"scenarios": [], "fixtures": [], "qsizes": {}}

os.makedirs(FILES, exist_ok=True)
subprocess.run([sys.executable, os.path.join(OUT, "make_gguf.py"), FILES], check=True)


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


def kill_group(p):
    try:
        os.killpg(p.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    p.wait()


class Stub:
    def __init__(self, scen):
        self.port = free_port()
        self.sp = os.path.join(SCRATCH, f"scen-{self.port}.json")
        with open(self.sp, "w") as f:
            json.dump(scen, f)
        self.p = subprocess.Popen([sys.executable, os.path.join(OUT, "stub_router.py"),
                                   str(self.port), self.sp],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                  start_new_session=True)
        for _ in range(50):
            try:
                urllib.request.urlopen(f"http://127.0.0.1:{self.port}/health", timeout=1)
                return
            except Exception:
                time.sleep(0.1)
        raise RuntimeError("stub did not come up")

    def stop(self):
        kill_group(self.p)
        os.unlink(self.sp)


def run_probe(probe, port, expect, path_env=None, use_json=True):
    env = dict(os.environ, TMPDIR=SCRATCH)
    if path_env:
        env["PATH"] = path_env
    argv = ["/usr/bin/bash", probe, "check", "--port", str(port), "--expect", expect,
            "--timeout", "3", "--connect-timeout", "1"]
    if use_json:
        argv.append("--json")
    p = subprocess.run(argv, capture_output=True, text=True, timeout=60, env=env,
                       cwd=SCRATCH)
    verdict = reason = "?"
    if use_json:
        try:
            row = json.loads(p.stdout)["rows"][0]
            verdict, reason = row["verdict"], row.get("reason", "?")
        except Exception:
            verdict, reason = f"UNPARSEABLE({p.stdout[:80]!r})", "-"
    else:
        for line in p.stdout.splitlines():
            if "cli-override" in line and "|" in line:
                parts = [x.strip() for x in line.split("|")]
                if len(parts) >= 5:
                    verdict, reason = parts[3], parts[4]
    return {"verdict": verdict, "reason": reason, "exit": p.returncode}


def scen_case(name, expect, entries, props=None, note=""):
    s = Stub({"entries": entries, "props": props} if props else {"entries": entries})
    try:
        m = run_probe(PROBE_M, s.port, expect)
        b = run_probe(PROBE_B, s.port, expect)
    finally:
        s.stop()
    row = {"name": name, "expect": expect, "measured": m, "base": b, "note": note}
    RESULTS["scenarios"].append(row)
    print(f"SCEN {name}: M={m['verdict']}/{m['reason']}/exit{m['exit']}  B={b['verdict']}/{b['reason']}/exit{b['exit']}")
    return row


def entry(eid, value="unloaded", failed=None, args=None):
    st = {"value": value}
    if failed is not None:
        st["failed"] = failed
    if args is not None:
        st["args"] = args
    return {"id": eid, "object": "model", "status": st}


A = os.path.join(FILES, "absent.gguf")
V = os.path.join(FILES, "valid.gguf")
V2 = os.path.join(FILES, "valid2.gguf")  # second loadable file for e7
NEXIST_BIN = os.path.join(FILES, "no-such-binary")

# ---------------------------------------------------------------- set -e / parse
scen_case("h1-4field-missing", "absent",
          [entry("absent", args=[LS, "-m", A])],
          note="4-field read + new verdict path; base false green")
scen_case("h2-args-not-list", "absent",
          [entry("absent", args="llama-server")], note="status.args is a string")
scen_case("h3-args0-missing", "absent",
          [entry("absent", args=[NEXIST_BIN, "-m", V])], note="args[0] not a local file")
scen_case("h4-props-not-autoload-json", "absent",
          [entry("absent", args=[LS, "-m", A])],
          props={"role": "router"},
          note="router_autoload fails (python exit 1) inside &&-list; probe must not die (set -e)")


class StubRaw:
    def __init__(self, body):
        self.port = free_port()
        # serve a raw non-JSON body via python http.server one-liner
        code = (
            "from http.server import BaseHTTPRequestHandler,HTTPServer\n"
            "class H(BaseHTTPRequestHandler):\n"
            "  protocol_version='HTTP/1.1'\n"
            "  def log_message(self,*a):pass\n"
            "  def do_GET(self):\n"
            "    b=b'not json at all'\n"
            "    self.send_response(200);self.send_header('Content-Type','application/json')\n"
            "    self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)\n"
            f"HTTPServer(('127.0.0.1',{self.port}),H).serve_forever()\n")
        self.p = subprocess.Popen([sys.executable, "-c", code],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                  start_new_session=True)
        for _ in range(50):
            try:
                urllib.request.urlopen(f"http://127.0.0.1:{self.port}/health", timeout=1)
                return
            except Exception:
                time.sleep(0.1)

    def stop(self):
        kill_group(self.p)


s = StubRaw(None)
try:
    m = run_probe(PROBE_M, s.port, "absent")
    b = run_probe(PROBE_B, s.port, "absent")
finally:
    s.stop()
RESULTS["scenarios"].append({"name": "h5-models-garbage", "expect": "absent",
                             "measured": m, "base": b, "note": "non-JSON /v1/models body"})
print(f"SCEN h5-models-garbage: M={m['verdict']}/{m['reason']}  B={b['verdict']}/{b['reason']}")

# ---------------------------------------------------------------- precedence
scen_case("p1-wild-loadable-wins", "*",
          [entry("absent", args=[LS, "-m", A]), entry("valid1", args=[LS, "-m", V])],
          note="wildcard: one unloadable + one loadable unloaded -> loadable wins")
scen_case("p2-unloadable-plain-mix", "*",
          [entry("absent", args=[LS, "-m", A]), entry("plain")],
          note="wildcard: unloadable + plain unloaded (no args) -> plain-unloaded wins")
scen_case("p3-loading-wins", "*",
          [entry("absent", args=[LS, "-m", A]), entry("l1", value="loading")],
          note="wildcard: unloadable + loading -> MODEL_LOADING")
scen_case("p4-noautoload-reason", "absent",
          [entry("absent", args=[LS, "-m", A])],
          props={"role": "router", "models_autoload": False},
          note="non-autoload router: reason must stay router-unloaded")
scen_case("p5-failed-entry", "absent",
          [entry("absent", failed=True, args=[LS, "-m", A])],
          note="failed:true entry -> router-unloaded-failed, no file state used")
scen_case("p6-unloadable-vs-down", "*",
          [entry("d1", value="down"), entry("absent", args=[LS, "-m", A])],
          note="wildcard: unloadable + down -> reason shifts router-down -> router-model-missing (verdict same)")
scen_case("p7-sleeping-wins", "*",
          [entry("absent", args=[LS, "-m", A]), entry("s1", value="sleeping")],
          note="wildcard: unloadable + sleeping -> sleeping wins")
scen_case("p8-loaded-wins", "x",
          [entry("x", args=[LS, "-m", A]), entry("x", value="loaded")],
          note="two same-id entries: loaded wins")

# ---------------------------------------------------------------- flag forms
scen_case("e1-eq-form-missing", "absent",
          [entry("absent", args=[LS, "--model=" + A])], note="--model=PATH form")
scen_case("e3-draft-missing", "absent",
          [entry("absent", args=[LS, "-m", V, "--model-draft", A])], note="valid main + missing draft")
scen_case("e4-mmproj-eq-missing", "absent",
          [entry("absent", args=[LS, "-m", V, "--mmproj=" + A])], note="--mmproj=PATH missing")
scen_case("e5-mm-short-missing", "absent",
          [entry("absent", args=[LS, "-m", V, "-mm", A])], note="-mm short form missing")
scen_case("e6-relative-model", "absent",
          [entry("absent", args=[LS, "-m", "files/rel.gguf"])], note="relative --model -> no decision")
scen_case("e7-all-valid", "absent",
          [entry("absent", args=[LS, "-m", V, "-mm", V2, "--model-draft=" + V2])],
          note="all paths valid -> old verdict stays (MODEL_OK router-unloaded-autoload)")

# ---------------------------------------------------------------- no-python3
nopybin = os.path.join(SCRATCH, "nopybin")
shutil.rmtree(nopybin, ignore_errors=True)
os.makedirs(nopybin)
for tool in ("ss", "curl", "mktemp", "head", "tr", "grep", "sed", "awk", "cat",
             "sort", "cut", "wc", "comm", "uname", "dirname", "basename",
             "rm", "mkdir", "cp", "mv", "date"):
    for d in os.environ.get("PATH", "").split(os.pathsep):
        c = os.path.join(d, tool)
        if os.path.isfile(c) and os.access(c, os.X_OK):
            os.symlink(c, os.path.join(nopybin, tool))
            break
s = Stub({"entries": [entry("absent", args=[LS, "-m", A])]})
try:
    m = run_probe(PROBE_M, s.port, "absent", path_env=nopybin, use_json=False)
finally:
    s.stop()
RESULTS["scenarios"].append({"name": "nopy-no-python3", "expect": "absent", "measured": m,
                             "base": None, "note": "PATH without python3; expect round-88 verdict kept"})
print(f"SCEN nopy-no-python3: M={m['verdict']}/{m['reason']}/exit{m['exit']}")

# ---------------------------------------------------------------- fixtures
# positive control: the real stories260K model must load (sha256 pinned in claims)
shutil.copyfile(os.path.expanduser("~/.cache/kama-shokunin/models/stories260K.gguf"),
                os.path.join(FILES, "stories260K-real.gguf"))

FIXTURES = sorted(os.listdir(FILES))
FIXTURES = [f for f in FIXTURES if not f.startswith("absent") and not f.endswith(".json")]


def real_loader(fname):
    """Ground truth: pinned b12177 llama-server in single-model mode."""
    port = free_port()
    log = os.path.join(SCRATCH, f"load-{fname}.log")
    p = subprocess.Popen([LS, "--host", "127.0.0.1", "--port", str(port), "-ngl", "0",
                          "-m", os.path.join(FILES, fname), "-c", "128", "--no-webui"],
                         stdout=open(log, "w"), stderr=subprocess.STDOUT,
                         start_new_session=True, cwd=SCRATCH)
    loaded = False
    end = time.time() + 20
    while time.time() < end:
        if p.poll() is not None:
            break
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=1)
            loaded = True
            break
        except Exception:
            time.sleep(0.2)
    kill_group(p)
    tail = ""
    with open(log, errors="replace") as f:
        tail = "".join(f.readlines()[-8:])
    return ("LOADED" if loaded else "LOAD_FAIL"), p.returncode, tail


for fname in FIXTURES:
    fpath = os.path.join(FILES, fname)
    st = os.stat(fpath)
    arg = ["-m", fpath] if fname != "dir-at-path" else ["-m", os.path.join(FILES, "dir-at-path")]
    s = Stub({"entries": [entry("fx", args=[LS] + arg)]})
    try:
        m = run_probe(PROBE_M, s.port, "fx")
        b = run_probe(PROBE_B, s.port, "fx")
    finally:
        s.stop()
    if fname == "fifo-at-path":
        real = ("SKIPPED(real loader blocks on FIFO open)", None, "")
    else:
        real = real_loader(fname)
    RESULTS["fixtures"].append({"file": fname, "size": st.st_size,
                                "measured": m, "base": b,
                                "loader": real[0], "loader_exit": real[1],
                                "loader_tail": real[2]})
    print(f"FIX {fname}: M={m['verdict']}/{m['reason']} B={b['verdict']}/{b['reason']} loader={real[0]} exit={real[1]}")

# a directory at the --model path (probe never opens it; loader fopen/read fails)
os.makedirs(os.path.join(FILES, "dir-at-path"), exist_ok=True)
s = Stub({"entries": [entry("fx", args=[LS, "-m", os.path.join(FILES, "dir-at-path")])]})
try:
    m = run_probe(PROBE_M, s.port, "fx")
    b = run_probe(PROBE_B, s.port, "fx")
finally:
    s.stop()
real = None
try:
    port = free_port()
    log = os.path.join(SCRATCH, "load-dir.log")
    p = subprocess.Popen([LS, "--host", "127.0.0.1", "--port", str(port), "-ngl", "0",
                          "-m", os.path.join(FILES, "dir-at-path"), "-c", "128", "--no-webui"],
                         stdout=open(log, "w"), stderr=subprocess.STDOUT,
                         start_new_session=True, cwd=SCRATCH)
    end = time.time() + 15
    loaded = False
    while time.time() < end:
        if p.poll() is not None:
            break
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=1)
            loaded = True
            break
        except Exception:
            time.sleep(0.2)
    kill_group(p)
    with open(log, errors="replace") as f:
        tail = "".join(f.readlines()[-8:])
    real = ("LOADED" if loaded else "LOAD_FAIL", p.returncode, tail)
except Exception as e:
    real = ("ERROR", None, str(e))
RESULTS["fixtures"].append({"file": "dir-at-path", "size": -1, "measured": m, "base": b,
                            "loader": real[0], "loader_exit": real[1], "loader_tail": real[2]})
print(f"FIX dir-at-path: M={m['verdict']}/{m['reason']} B={b['verdict']}/{b['reason']} loader={real[0]} exit={real[1]}")

# ---------------------------------------------------------------- QSIZES diff
probe_src = open(PROBE_M).read()
mq = re.search(r"QSIZES = \{(.*?)\}", probe_src, re.S)
probe_q = ast.literal_eval(mq.group(0)[len("QSIZES = "):].strip())

csrc = open(os.path.join(SCRATCH, "src", "constants.py")).read()
cblock = csrc[csrc.index("GGML_QUANT_SIZES"):]
cblock = cblock[cblock.index("{"):cblock.index("\n}") + 2]
expr = ast.parse(cblock.strip(), mode="eval").body
hsrc = open(os.path.join(SCRATCH, "src", "ggml.h")).read()
enum_names = {}
for line in hsrc.splitlines():
    mm = re.match(r"\s*GGML_TYPE_(\w+)\s*=\s*(-?\d+)", line)
    if mm:
        enum_names[mm.group(1)] = int(mm.group(2))
ns = {"QK_K": 256}
for name, val in enum_names.items():
    ns[name] = val
expr = ast.parse(cblock.strip(), mode="eval").body
regen = {}
for k_node, v_node in zip(expr.keys, expr.values):  # type: ignore[attr-defined]
    val = eval(compile(ast.Expression(v_node), "<qsizes>", "eval"), {"__builtins__": {}}, ns)
    regen[enum_names[k_node.attr]] = val
diff = []
for t in sorted(set(probe_q) | set(regen)):
    a, b = probe_q.get(t), regen.get(t)
    if a != b:
        diff.append({"type": t, "probe": a, "s585": b})
RESULTS["qsizes"] = {"probe": {str(k): list(v) for k, v in sorted(probe_q.items())},
                     "s585": {str(k): list(v) for k, v in sorted(regen.items())},
                     "identical": not diff, "diffs": diff,
                     "ggml_type_count": 44}
print("QSIZES identical:", not diff, "| probe entries:", len(probe_q), "| s585 entries:", len(regen))

with open(os.path.join(OUT, "results.json"), "w") as f:
    json.dump(RESULTS, f, indent=1)
print("results written")
