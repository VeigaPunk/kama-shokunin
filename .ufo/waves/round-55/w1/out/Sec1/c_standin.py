# mirrors start_replay()'s invocation shape exactly (counter:641)
import subprocess, sys, os, time
INVOKER = ("import subprocess, sys\n"
           "sys.exit(subprocess.call(sys.argv[1:]))\n")
S = sys.argv[1]
p = subprocess.Popen([sys.executable, "-I", "-c", INVOKER, sys.executable, "-I",
                      os.path.join(S, "child_replay.py")],
                     stdout=open(os.path.join(S, "inv.log"), "wb"),
                     stderr=subprocess.STDOUT, start_new_session=True)
open(os.path.join(S, "INVOKER.PID"), "w").write(str(p.pid))
time.sleep(120)   # stands in for the counter's own work
