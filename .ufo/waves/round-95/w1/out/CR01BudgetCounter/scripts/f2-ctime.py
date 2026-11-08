import importlib.util, json, os, subprocess, sys, threading, time, tempfile
from pathlib import Path
lane = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
spec = importlib.util.spec_from_file_location("rr", lane/"tools/round93-router-repeat.py")
rr = importlib.util.module_from_spec(spec); spec.loader.exec_module(rr)
OUT = Path(sys.argv[1]); scratch = Path(sys.argv[2]); scratch.mkdir(parents=True, exist_ok=True)
def rp(probe):
    return rr.probe_router_py(Path(probe).read_bytes())
for name in ("M1", "F2"):
    code = rp(OUT/"probes"/f"probe-{name}.sh")
    rows = []
    for run in range(3):
        w = Path(tempfile.mkdtemp(dir=scratch))
        x, slow = w/"x.gguf", w/"slow.gguf"
        good = rr.gguf(1, 32, True); x.write_bytes(good); slow.write_bytes(rr.gguf(rr.TENSORS, 1, False))
        bad = b"XXXX" + good[4:]
        st0 = os.stat(x)
        body = w/"b.json"
        body.write_bytes(rr.router_body([[str(x), "-m", str(x)], [str(x), "-m", str(slow)], [str(x), "-m", str(x)]]))
        def rewrite():
            time.sleep(0.15)
            with open(x, "r+b") as f: f.write(bad)
            os.utime(x, ns=(st0.st_atime_ns, st0.st_mtime_ns))
        t = threading.Thread(target=rewrite); t.start()
        p = subprocess.run([sys.executable, "-c", code, str(body), "files", "0", "1", "2"], capture_output=True, text=True)
        t.join()
        st1 = os.stat(x)
        states = " | ".join(p.stdout.strip().split("\n"))
        right = p.stdout.strip().split("\n")[-1].endswith("invalid")
        rows.append(f"run{run+1}=[{states}] entry2_right={int(right)} ctime_changed={st0.st_ctime_ns != st1.st_ctime_ns}")
    print(f"F2CTIME {name}: " + " ; ".join(rows))
