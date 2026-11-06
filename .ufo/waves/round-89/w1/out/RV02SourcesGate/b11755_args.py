#!/usr/bin/env python3
"""Test B redo: b11755 router --models-dir, GET /v1/models only, print status objects."""
import json, os, shutil, socket, subprocess, time, urllib.request
from pathlib import Path

SCRATCH = Path("/fast/scratch/hyaku/kama-r89/RV02SourcesGate/live")
B11755 = Path("/home/vgpnk/.local/opt/llama-b11755/llama-server")
MODEL = Path.home() / ".cache/kama-shokunin/models/stories260K.gguf"
OUT = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-89/w1/out/RV02SourcesGate")

workB = SCRATCH / "B2"; workB.mkdir(parents=True, exist_ok=True)
shutil.copy(MODEL, workB / "stories260K.gguf")
s = socket.socket(); s.bind(("127.0.0.1", 0)); port = s.getsockname()[1]; s.close()
logB = SCRATCH / "B2.log"
p = None
try:
    with open(logB, "w") as lf:
        p = subprocess.Popen([str(B11755), "--port", str(port), "--models-dir", str(workB),
                              "--host", "127.0.0.1"], stdout=lf, stderr=subprocess.STDOUT,
                             start_new_session=True, cwd=str(workB))
        end = time.time() + 30
        code, body = None, None
        while time.time() < end:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=2) as r:
                    code, _ = r.status, r.read()
                    break
            except Exception:
                time.sleep(0.4)
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/v1/models", timeout=5) as r:
            body = json.loads(r.read().decode())
        print(f"health={code}")
        for m in body.get("data", []):
            st = m.get("status", {})
            print(f"id={m.get('id')}")
            print(f"status={json.dumps(st)}")
            args = st.get("args") or []
            has_model = any(a == "--model" or a == "-m" for a in args)
            print(f"args_has_model_flag={has_model}")
        lines = logB.read_text(errors="replace").splitlines()
        print("log build line:", next((l for l in lines if "build" in l.lower() or "version" in l.lower()), "?"))
finally:
    if p is not None:
        try: os.killpg(os.getpgid(p.pid), 15)
        except Exception: pass
        time.sleep(0.7)
        try: os.killpg(os.getpgid(p.pid), 9)
        except Exception: pass
