"""A parent process that spawns the replay exactly the way
tools/round49-replay-witness-audit.py:297 does (no start_new_session, no pdeathsig),
then sleeps: SIGTERM this process = the counter being killed mid-witness."""
import os, subprocess, sys, time
S, REPLAY, RECEIPT, WD, WORK, OUT = sys.argv[1:7]
log = open(os.path.join(S, "counter-shape-live.log"), "wb")
p = subprocess.Popen([sys.executable, REPLAY, "--receipt", RECEIPT, "--work", WORK,
                      "--out", OUT, "--witness-dir", WD], stdout=log, stderr=log)
open(os.path.join(S, "counter-shape-pids.txt"), "w").write(f"{os.getpid()} {p.pid}\n")
while True:
    time.sleep(0.2)
