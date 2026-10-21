import json, subprocess, sys
src = open("/tmp/revexit/drv_v2.py", encoding="utf-8").read().split("# 01 baseline")[0].replace("/tmp/revexit/v2_results.log", "/tmp/revexit/v2_results5.log")
exec(compile(src, "helpers", "exec"))
d, lane, fleet, c = base("v2k28raw")
tree = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
body = (f"tree {tree}\nparent {c['c4']}\nauthor kama-shokunin <a@x> {T0+150} +0000\n"
        f"committer kama-shokunin <a@x> {T0+150} +0000\n\n").encode() + b"round-10: caf\xe9 raw latin1\n"
write_commit(lane, body, literal=True)
put_report(fleet, report_text(c["c1"], c["c2"]))
raw = subprocess.run(["git", "-C", str(lane), "log", "-1", "--format=%s"], env=dict(BASE), capture_output=True).stdout
print("raw subject bytes from git log:", raw)
rc, out, err = audit(lane, fleet, "--json")
print("raw non-UTF-8 round subject: rc=", rc, "round_commits=", json.loads(out)["results"][0]["round_commits"] if out.strip() else None, "stderr=", err.strip()[-100:], "expect 2")
