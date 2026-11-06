#!/usr/bin/env python3
"""r90 EX02 latency budget: probe revisions timed on lane-owned stubs and the operator router.

PROBES="name=path,name=path,..." (first is the reference "base").
Phases, all interleaved per round, 2 warmups per probe before each phase:
  stub-plain   plain stub, 20 runs:   check --port <stub> --expect good
  stub-json    same stub, 20 runs:    check --port <stub> --expect good --json
  router-stub  router-shaped stub, 20 runs: check --port <stub> --expect '*' --json
               (4 entries with status.value=unloaded and status.args -> the four
                1.8 GB lfm3 ggufs the operator router lists, plus
                GET /props -> {"role":"router","models_autoload":true}, so the
                probe's round-89 file_state scan runs exactly as on 1234)
  operator-1234  GET only, 5 runs:    check --port 1234 --expect '*' --json
No POST, no load/unload anywhere. Median and p90 are nearest-rank over the
recorded samples. Writes $OUT_NAME.json and prints a human table.
"""
import http.server
import json
import os
import socket
import statistics
import subprocess
import sys
import threading
import time
from pathlib import Path

OUT = Path(__file__).resolve().parent
PROBES = []
for item in os.environ["PROBES"].split(","):
    name, _, path = item.partition("=")
    PROBES.append((name.strip(), Path(path.strip())))
REF = PROBES[0][0]
ENV = dict(os.environ)
ENV["TMPDIR"] = os.environ["LAT_TMPDIR"]
Path(ENV["TMPDIR"]).mkdir(parents=True, exist_ok=True)
NAME = os.environ.get("OUT_NAME", "latency")

SERVER = "/home/vgpnk/src/llama.cpp/build/bin/llama-server"
# args[0] MUST be the absolute server binary: tools/kama-probe.sh file_state() returns "-"
# without reading any file when args[0] is not an absolute existing path (kama-probe.sh:695).
ROUTER_MODELS = [
    ("LFM3-1.7B", ["--host", "127.0.0.1", "--port", "0", "--alias", "LFM3-1.7B",
                   "--ctx-size", "32768",
                   "--model", "/home/vgpnk/models/lfm3/LFM3-1.7B/LFM3-1.7B-Q8_0.gguf"]),
    ("LFM3-1.7B-Uncensored",
     ["--host", "127.0.0.1", "--port", "0", "--alias", "LFM3-1.7B-Uncensored",
      "--ctx-size", "262144",
      "--model", "/home/vgpnk/models/lfm3/LFM3-1.7B-Uncensored/LFM3-1.7B-Uncensored-AD-Q6_K.gguf"]),
    ("LFM3-Omni-2B", ["--host", "127.0.0.1", "--port", "0", "--alias", "LFM3-Omni-2B",
                      "--ctx-size", "32768",
                      "--model", "/home/vgpnk/models/lfm3/LFM3-Omni-2B/LFM3-Omni-2B-Q8_0.gguf",
                      "--mmproj", "/home/vgpnk/models/lfm3/LFM3-Omni-2B/mmproj-LFM3-Omni-2B-Q8_0.gguf"]),
    ("LFM3-VL-2B", ["--host", "127.0.0.1", "--port", "0", "--alias", "LFM3-VL-2B",
                    "--ctx-size", "32768",
                    "--model", "/home/vgpnk/models/lfm3/LFM3-VL-2B/LFM3-VL-2B-Q8_0.gguf",
                    "--mmproj", "/home/vgpnk/models/lfm3/LFM3-VL-2B/mmproj-LFM3-VL-2B-Q8_0.gguf"]),
]


def p90(vals):
    s = sorted(vals)
    k = max(1, int(round(0.9 * len(s) + 0.5)) - 1)
    return s[min(k, len(s) - 1)]


def stats(vals):
    return {"n": len(vals), "median": round(statistics.median(vals), 1),
            "p90": round(p90(vals), 1), "min": round(min(vals), 1),
            "max": round(max(vals), 1), "mean": round(statistics.mean(vals), 1)}


def make_handler(mode):
    class H(http.server.BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_GET(self):
            if self.path == "/v1/models":
                if mode == "router":
                    body = json.dumps({"data": [
                        {"id": mid, "status": {"value": "unloaded",
                                               "args": [SERVER, *args]}}
                        for mid, args in ROUTER_MODELS]}).encode()
                else:
                    body = json.dumps({"data": [{"id": "good"}]}).encode()
                ct = "application/json"
            elif self.path == "/props" and mode == "router":
                body = b'{"role":"router","models_autoload":true}'
                ct = "application/json"
            elif self.path == "/health":
                body = b'{"status":"ok"}'
                ct = "application/json"
            else:
                self.send_response(404)
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
            self.send_response(200)
            self.send_header("Content-Type", ct)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
    return H


def serve(mode):
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", port), make_handler(mode))
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, port


def run(probe, argv):
    t0 = time.perf_counter()
    cp = subprocess.run(["bash", str(probe), *argv], capture_output=True,
                        text=True, env=ENV, cwd=str(OUT))
    ms = (time.perf_counter() - t0) * 1000.0
    verdict = reason = "?"
    if "--json" in argv:
        try:
            row = json.loads(cp.stdout)["rows"][0]
            verdict, reason = row.get("verdict", "?"), row.get("reason", "?")
        except Exception:
            pass
    return {"ms": round(ms, 1), "exit": cp.returncode,
            "verdict": verdict, "reason": reason}


def phase(argv, rounds):
    for _, probe in PROBES:
        for _ in range(2 if rounds >= 20 else 1):
            run(probe, argv)
    rows = {name: [] for name, _ in PROBES}
    for _ in range(rounds):
        for name, probe in PROBES:
            rows[name].append(run(probe, argv))
    doc = {}
    for name, _ in PROBES:
        v = rows[name]
        doc[name] = {"stats": stats([r["ms"] for r in v]),
                     "runs": [r["ms"] for r in v],
                     "exits": sorted({r["exit"] for r in v}),
                     "verdicts": sorted({r["verdict"] for r in v}),
                     "reasons": sorted({r["reason"] for r in v})}
        doc[name]["ratio_median_vs_ref"] = round(
            doc[name]["stats"]["median"] / doc[REF]["stats"]["median"], 2)
        doc[name]["ratio_p90_vs_ref"] = round(
            doc[name]["stats"]["p90"] / doc[REF]["stats"]["p90"], 2)
    return doc


def main():
    doc = {"ref": REF, "probes": {n: str(p) for n, p in PROBES},
           "router_stub_models": [m for m, _ in ROUTER_MODELS], "phases": {}}
    srv, port = serve("plain")
    try:
        doc["stub_port"] = port
        doc["phases"]["stub-plain"] = phase(
            ["check", "--port", str(port), "--expect", "good"], 20)
        doc["phases"]["stub-json"] = phase(
            ["check", "--port", str(port), "--expect", "good", "--json"], 20)
    finally:
        srv.shutdown()
        srv.server_close()
    srv, port = serve("router")
    try:
        doc["router_stub_port"] = port
        doc["phases"]["router-stub"] = phase(
            ["check", "--port", str(port), "--expect", "*", "--json"], 20)
    finally:
        srv.shutdown()
        srv.server_close()
    doc["phases"]["operator-1234"] = phase(
        ["check", "--port", "1234", "--expect", "*", "--json"], 5)

    (OUT / f"{NAME}.json").write_text(json.dumps(doc, indent=2) + "\n")
    for name, ph in doc["phases"].items():
        print(f"## {name}")
        for pname, _ in PROBES:
            s = ph[pname]["stats"]
            print(f"  {pname:10s} n={s['n']} median={s['median']}ms p90={s['p90']}ms "
                  f"min={s['min']} max={s['max']} ratio_med={ph[pname]['ratio_median_vs_ref']} "
                  f"ratio_p90={ph[pname]['ratio_p90_vs_ref']} exits={ph[pname]['exits']} "
                  f"verdict={ph[pname]['verdicts']} reason={ph[pname]['reasons']}")
            print(f"             runs={ph[pname]['runs']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
