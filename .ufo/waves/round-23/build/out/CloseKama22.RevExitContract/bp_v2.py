import subprocess, sys, os
BASE = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
BASE.update(GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1", HOME="/tmp/revexit/home")
import importlib.util
src = open("/tmp/revexit/drv_v2.py", encoding="utf-8").read().split("# 01 baseline")[0].replace("/tmp/revexit/v2_results.log", "/tmp/revexit/v2_results4.log")
exec(compile(src, "helpers", "exec"))
d, lane, fleet, c = base("k40")
put_report(fleet, report_text(c["c1"], c["c2"]))
p = subprocess.Popen([sys.executable, SCRIPT, "--lane-repo", str(lane), "--fleet-repo", str(fleet),
                      "--rounds", "10", "--no-errata"], env=dict(BASE), stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE, cwd="/tmp/revexit")
p.stdout.close()  # reader gone before the verdict is written
rc = p.wait()
err = p.stderr.read().decode("utf-8", "replace").strip()
print(f"broken-pipe clean verdict: rc={rc} stderr-tail={err[-160:]!r}")
