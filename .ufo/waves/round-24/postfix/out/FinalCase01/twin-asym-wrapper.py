"""Private measurement wrapper (not production): runs the pinned auditor
unchanged and, only when --lane-repo declares extensions.partialclone,
adds one uncorrected landed-unresolved defect to its valid normal verdict."""
import hashlib
import json
import os
import subprocess
import sys

PINNED = "/fast/scratch/hyaku/kama-r24/postfix/FinalCase01/clone/tools/report-landing-audit.py"
PINNED_SHA = "b9be4f428cd70842320c698794faffaa95571a60fc530df6a84d7d8cade3b26f"

if hashlib.sha256(open(PINNED, "rb").read()).hexdigest() != PINNED_SHA:
    sys.stderr.write("could-not-evaluate: wrapper: pinned auditor digest changed\n")
    sys.exit(2)
argv = sys.argv[1:]
proc = subprocess.run([sys.executable, PINNED, *argv], capture_output=True)
lane = argv[argv.index("--lane-repo") + 1]
env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
marked = subprocess.run(["git", "-C", lane, "config", "--get",
                         "extensions.partialclone"], capture_output=True,
                        env=env).stdout.strip()
if proc.returncode in (0, 1) and marked:
    doc = json.loads(proc.stdout)
    doc["results"][0]["defects"].append(
        {"kind": "landed-unresolved", "token": "1" * 40, "corrected_by": []})
    s = doc["summary"]
    s["defects"] += 1
    s["uncorrected"] += 1
    s["by_kind"]["landed-unresolved"] += 1
    s["status"] = "failed"
    sys.stdout.write(json.dumps(doc, indent=1, sort_keys=True) + "\n")
    sys.stderr.buffer.write(proc.stderr)
    sys.exit(1)
sys.stdout.buffer.write(proc.stdout)
sys.stderr.buffer.write(proc.stderr)
sys.exit(proc.returncode)
