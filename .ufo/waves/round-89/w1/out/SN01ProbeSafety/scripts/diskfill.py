#!/usr/bin/env python3
"""How much does the probe write to TMPDIR for one hostile body? curl -o has no
--max-filesize; only --max-time bounds the transfer. Serve a large (sparse) body and
sample the mktemp dir the probe creates."""
import glob, json, os, socket, subprocess, sys, threading, time

ROOT = "/fast/scratch/hyaku/kama-r89/SN01ProbeSafety"
BIG = ROOT + "/fx/b-big-stream.json"
if not os.path.exists(BIG):
    with open(BIG, "wb") as f:
        f.write(b'{"data":[')
        f.truncate(1500 * 1024 * 1024)

s = socket.socket(); s.bind(("127.0.0.1", 0)); port = s.getsockname()[1]; s.close()
srv = subprocess.Popen([sys.executable, ROOT + "/srv.py", str(port), BIG, "", ""],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       start_new_session=True)
time.sleep(0.4)
env = dict(os.environ, TMPDIR=ROOT + "/tmp", KAMA_PROBE_TMPDIR=ROOT + "/tmp")
for d in glob.glob(ROOT + "/tmp/kama-probe.*"):
    subprocess.run(["rm", "-rf", d])
proc = subprocess.Popen(["bash", ROOT + "/probe-M.sh", "listeners", "--port", str(port),
                         "--expect", "*"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                        env=env, start_new_session=True)
peak = 0
t0 = time.time()
while proc.poll() is None:
    tot = 0
    for d in glob.glob(ROOT + "/tmp/kama-probe.*"):
        for dirpath, _, files in os.walk(d):
            for fn in files:
                try:
                    tot += os.stat(os.path.join(dirpath, fn)).st_size
                except OSError:
                    pass
    peak = max(peak, tot)
    time.sleep(0.02)
out, err = proc.communicate()
os.killpg(srv.pid, 9)
print(json.dumps({"probe_rc": proc.returncode, "seconds": round(time.time() - t0, 1),
                  "peak_tmpdir_bytes": peak, "peak_MiB": round(peak / 2**20, 1),
                  "last_row": [l for l in out.decode(errors="replace").splitlines() if "|" in l][-1:],
                  "stderr_tail": err.decode(errors="replace").splitlines()[-2:]}))
