#!/usr/bin/env python3
# RV01 driver: one stub per cell on a free loopback port; probe run via `check --port` (never
# `listeners`, which would GET the operator's router on 127.0.0.1:1234). Results -> results.json.
import json, os, signal, socket, subprocess, sys, time, pathlib

S = pathlib.Path('/fast/scratch/hyaku/kama-r90/L1/rv01')
REVS = sys.argv[1].split(",") if len(sys.argv) > 1 else ["base", "M", "oldcurl"]
CELLS = [
    ("ok", "stories260K.gguf"),
    ("exact", "stories260K.gguf"),
    ("over1", "stories260K.gguf"),
    ("overclose", "stories260K.gguf"),
    ("big401", "stories260K.gguf"),
    ("legit1m", "stories260K.gguf"),
    ("ctlid", "*"),
    ("u2028", "*"),
    ("pos-nonascii", "mod\u00e8le-\u00e9.gguf"),
    ("pos-quote", 'q"b\\c.gguf'),
    ("ctlserver", "stories260K.gguf"),
    ("c1server", "stories260K.gguf"),
    ("badutf8server", "stories260K.gguf"),
    ("ctype-esc", "stories260K.gguf"),
    ("bom", "stories260K.gguf"),
    ("surr-only", "stories260K.gguf"),
    ("surr-mixed", "stories260K.gguf"),
    ("router-unl", "stories260K.gguf"),
    ("router-esc", "stories260K.gguf"),
    ("router-surr", "stories260K.gguf"),
    ("router-unl-junk", "stories260K.gguf"),
    ("props-big", "stories260K.gguf"),
    ("hdrflood", "stories260K.gguf"),
    ("props-empty", "stories260K.gguf"),
    ("root-big", "stories260K.gguf"),
    ("router-ctlid-loading", "*"),
    ("router-ctlid-unl", "*"),
    ("router-surr-first", "*"),
]
if os.environ.get("CELLS"):
    keep = set(os.environ["CELLS"].split(","))
    CELLS = [c for c in CELLS if c[0] in keep]


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


def wait_port(port, t=10.0):
    end = time.time() + t
    while time.time() < end:
        try:
            socket.create_connection(("127.0.0.1", port), timeout=0.5).close()
            return True
        except OSError:
            time.sleep(0.05)
    return False


def run_probe(rev, port, expect, json_mode, work):
    env = dict(os.environ, TMPDIR=str(work))
    args = ["bash", str(S / rev / "tools/kama-probe.sh"), "check", "--port", str(port), "--expect", expect]
    if json_mode:
        args.append("--json")
    t0 = time.time()
    try:
        p = subprocess.run(args, capture_output=True, env=env, timeout=90, cwd=str(S / rev))
        rc, out, err = p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")
    except subprocess.TimeoutExpired as e:
        rc, out, err = "TIMEOUT", (e.stdout or b"").decode("utf-8", "replace"), (e.stderr or b"").decode("utf-8", "replace")
    return {"rc": rc, "sec": round(time.time() - t0, 2), "stdout": out, "stderr": err}


def main():
    results = {}
    for rev in REVS:
        work = S / "work" / rev
        work.mkdir(parents=True, exist_ok=True)
        for mode, expect in CELLS:
            port = free_port()
            stub = subprocess.Popen([sys.executable, str(S / "stub.py"), mode, str(port)],
                                    start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            try:
                if not wait_port(port):
                    results[f"{rev}:{mode}"] = {"error": "stub did not listen", "stub_stderr": stub.stderr.read(2000).decode("replace")}
                    continue
                j = run_probe(rev, port, expect, True, work)
                t = run_probe(rev, port, expect, False, work)
                results[f"{rev}:{mode}"] = {"port": port, "expect": expect, "json": j, "table": t}
                print(f"{rev:8} {mode:16} json_rc={j['rc']} table_rc={t['rc']} sec={j['sec']}/{t['sec']}", flush=True)
            finally:
                try:
                    os.killpg(stub.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                stub.wait(timeout=10)
                stub.stderr.close()
    out = S / "results.json"
    merged = json.loads(out.read_text()) if out.exists() else {}
    merged.update(results)
    out.write_text(json.dumps(merged, indent=1, ensure_ascii=True))
    results = merged
    print("WROTE", S / "results.json")


if __name__ == "__main__":
    main()
