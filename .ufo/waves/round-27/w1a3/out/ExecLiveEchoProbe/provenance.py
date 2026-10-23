#!/usr/bin/env python3
"""Merge provenance (binary/model/source hashes, build string, port, shutdown)
into the live-probe receipt."""
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
OUT = os.path.join(LANE, ".ufo/waves/round-27/w1a3/out/ExecLiveEchoProbe")
SCRATCH = "/fast/scratch/hyaku/kama-r27c/ExecLiveEchoProbe"
BIN = "/home/vgpnk/.local/opt/llama-b11755/llama-server"
MODEL = "/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf"


def sha_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    rp = os.path.join(OUT, "receipt.json")
    receipt = json.load(open(rp))
    ver = subprocess.run([BIN, "--version"], capture_output=True, text=True,
                         timeout=30)
    receipt["provenance"] = {
        "observed_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "binary_path": BIN,
        "binary_sha256": sha_file(BIN),
        "binary_version_stdout": ver.stdout.strip(),
        "binary_version_stderr": ver.stderr.strip(),
        "model_path": MODEL,
        "model_sha256": sha_file(MODEL),
        "model_bytes": os.path.getsize(MODEL),
        "source_url": ("https://raw.githubusercontent.com/ggml-org/llama.cpp/"
                       "704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp"),
        "source_sha256": sha_file(os.path.join(SCRATCH, "server-common.cpp")),
        "s137_site": "server-common.cpp:1375 throw std::invalid_argument(... + response_type)",
        "server_cmdline": (BIN + " -m " + MODEL + " --host 127.0.0.1 --port 47680"
                           " -c 256 -t 2"),
        "port_block": "47680-47681",
        "port_used": 47680,
        "context": 256,
        "threads": 2,
        "health": "GET /health -> 200 {\"status\":\"ok\"}",
        "shutdown": "SIGTERM; process exited with code 0; ss -ltn shows no :47680; pgrep -af 'port 47680' empty",
        "server_log_file": "server-47680.log",
        "server_log_sha256": sha_file(os.path.join(OUT, "server-47680.log")),
        "proxy_env_used": "http.client direct, no proxy",
        "tool_installs": "none",
    }
    ctrl = receipt["requests"]["req4-control"].get("response_json") or {}
    receipt["provenance"]["control_system_fingerprint"] = ctrl.get("system_fingerprint")
    with open(rp, "w") as f:
        json.dump(receipt, f, indent=1, sort_keys=True)
    print(json.dumps(receipt["provenance"], indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
