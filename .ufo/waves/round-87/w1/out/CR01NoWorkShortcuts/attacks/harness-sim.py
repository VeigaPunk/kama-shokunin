"""CR01 stand-in for the frozen ARM14 fault harness (EX03 candidate absent at seat time).
Per plans/round-87-claims.md C2 predicate 2: seed one fault per round-86 instrument (selftest
replaced by a stub exiting 0 with a failing summary) in a scratch tools tree, run the gate's
evaluate() with that tools dir, count a fault killed when arm round86-instruments is not ok;
a missing arm counts as escaped. Extra control (CR01 addition, not frozen): a clean tools copy
must leave the arm ok."""
import importlib.util, os, shutil, sys, tempfile

gate_path, repo = sys.argv[1], os.path.realpath(sys.argv[2])
TMP = os.environ["TMPDIR"]
src_tools = os.path.join(repo, "tools")
spec = importlib.util.spec_from_file_location("gate_under_test", gate_path)
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)


def arm_of(res):
    for arm in res["arms"]:
        if arm["name"] == "round86-instruments":
            return arm
    return None


def seeded(script, prefix):
    d = tempfile.mkdtemp(prefix="seed-", dir=TMP)
    shutil.copytree(src_tools, os.path.join(d, "tools"))
    stub = f'#!/usr/bin/env python3\nprint("{prefix} pass=0 fail=1")\n'
    open(os.path.join(d, "tools", script), "w", encoding="utf-8").write(stub)
    return os.path.join(d, "tools")


def clean():
    d = tempfile.mkdtemp(prefix="clean-", dir=TMP)
    shutil.copytree(src_tools, os.path.join(d, "tools"))
    return os.path.join(d, "tools")


killed = escaped = 0
for script, prefix in g.ROUND86_MODULES:
    res = g.evaluate(repo, 87, "master", tools_dir=seeded(script, prefix))
    arm = arm_of(res)
    if arm is None or arm["ok"]:
        escaped += 1
        state = "ESCAPED" if arm else "MISSING(escaped)"
    else:
        killed += 1
        state = "killed"
    print(f"FAULT {script} arm={'absent' if arm is None else ('ok' if arm['ok'] else 'not-ok')} {state}")
print(f"ARM14_FAULTS faults={len(g.ROUND86_MODULES)} killed={killed} escaped={escaped}")
res = g.evaluate(repo, 87, "master", tools_dir=clean())
arm = arm_of(res)
print(f"CLEAN_CONTROL arm={'absent' if arm is None else ('ok' if arm['ok'] else 'not-ok')}")
sys.exit(0 if killed == 3 and escaped == 0 and arm and arm["ok"] else 1)
