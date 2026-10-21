import os, subprocess, sys

src = open("/tmp/revexit/drv_v2.py", encoding="utf-8").read().split("# 01 baseline")[0]
src = src.replace("/tmp/revexit/v2_results.log", "/tmp/revexit/v2_results3.log")
exec(compile(src, "drv-helpers", "exec"))
OUT = []


def say(line):
    OUT.append(line)
    print(line)


def run_raw(lane, fleet, env=None, close_stdout=False, stdout=None):
    kw = dict(env=dict(BASE), stderr=subprocess.PIPE, cwd="/tmp/revexit")
    if close_stdout:
        kw["preexec_fn"] = lambda: os.close(1)
    else:
        kw["stdout"] = stdout or subprocess.PIPE
    p = subprocess.run([sys.executable, SCRIPT, "--lane-repo", str(lane),
                        "--fleet-repo", str(fleet), "--rounds", "10", "--no-errata"],
                       **kw)
    return p.returncode, (p.stdout or b"").decode("utf-8", "replace"), \
        p.stderr.decode("utf-8", "replace")


# a. lane path is a symlink loop
d, lane, fleet, c = base("k00")
put_report(fleet, report_text(c["c1"], c["c2"]))
loop = d / "loop"
os.symlink("loop", loop)
res = audit(loop, fleet)
say(f"a symlink-loop lane path rc={res[0]} stderr-last={res[2].strip().splitlines()[-1:]!r} expect 2")

# b. failing verdict + closed stdout
d, lane, fleet, c = base("k01")
commit(lane, "round-10: plain", when=T0 + 150)
put_report(fleet, report_text(c["c1"], c["c2"]))
res = run_raw(lane, fleet, close_stdout=True)
say(f"b failing verdict, closed stdout: rc={res[0]} stdout={res[1]!r} stderr={res[2].strip()[-80:]!r} expect 2")
res = run_raw(lane, fleet)
say(f"b failing verdict, open stdout:   rc={res[0]} last-line={res[1].strip().splitlines()[-1]!r}")

# c. non-UTF-8 round subject: docstring says non-UTF-8 git output -> exit 2
d, lane, fleet, c = base("k28")
msg = d / "msg.bin"
msg.write_bytes("round-10: caf\u00e9 latin1 subject\n".encode("latin-1"))
git(lane, "commit", "-q", "--allow-empty", "-F", str(msg), env=gitenv("kama-shokunin", T0 + 150))
put_report(fleet, report_text(c["c1"], c["c2"]))
raw_subject = git(lane, "log", "-1", "--format=%s").encode("utf-8", "surrogateescape")
say(f"c subject bytes in lane: {raw_subject!r}")
res = audit(lane, fleet, "--json")
say(f"c non-UTF-8 round subject rc={res[0]} (round commit still counted: "
    f"round_commits={__import__('json').loads(res[1])['results'][0]['round_commits']}) expect 2")

# d. symlink-target report that is a clean report, but with the report content in a
#    symlink whose target is the bare report sentence (pure exit-0 case for the record)
open("/tmp/revexit/selftest-names.txt", "w").write("")

OUT.append("")
open("/tmp/revexit/v2_outputs3.txt", "w").write("\n".join(OUT) + "\n")
