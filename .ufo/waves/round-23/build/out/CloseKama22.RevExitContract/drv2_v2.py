import json, os, subprocess, sys

src = open("/tmp/revexit/drv_v2.py", encoding="utf-8").read().split("# 01 baseline")[0]
src = src.replace("/tmp/revexit/v2_results.log", "/tmp/revexit/v2_results2.log")
exec(compile(src, "drv-helpers", "exec"))
OUT = []


def gitraw(repo, *args, input=None):
    p = subprocess.run(["git", "-C", str(repo), *args], env=dict(BASE),
                       input=input, capture_output=True)
    return p.returncode, p.stdout.decode("utf-8", "replace"), \
        p.stderr.decode("utf-8", "replace")


def say(line):
    OUT.append(line)
    print(line)


def jdoc(res):
    rc, out, err = res
    try:
        return json.loads(out)
    except Exception:
        return None


# A. c03: separator byte in author name -> round commit dropped?
d, lane, fleet, c = base("j03")
hidden = commit(lane, "round-10: hidden", author="kama-shokunin\x1f1700", when=T0 + 150)
put_report(fleet, report_text(c["c1"], c["c2"]))
res = audit(lane, fleet, "--json")
doc = jdoc(res)
say(f"A c03 rc={res[0]} round_commits={doc['results'][0]['round_commits']} "
    f"required={doc['results'][0]['required']} defects={len(doc['results'][0]['defects'])}")
say(f"A   git log author field for hidden: {gitraw(lane, 'log', '-1', '--format=%an|%at|%s', hidden)[1]!r}")

# A2. control for the same commit with a plain author
d, lane2, fleet2, c2 = base("j03b")
commit(lane2, "round-10: hidden", when=T0 + 150)
put_report(fleet2, report_text(c2["c1"], c2["c2"]))
res = audit(lane2, fleet2, "--json")
doc = jdoc(res)
say(f"A2 plain author rc={res[0]} round_commits={doc['results'][0]['round_commits']} "
    f"required={doc['results'][0]['required']} defects={len(doc['results'][0]['defects'])}")

# B. c10: 30-digit author timestamp -> post_report misclassification?
d, lane, fleet, c = base("j10")
tree = git(lane, "rev-parse", "HEAD^{tree}").strip()
big = write_commit(lane, raw_body(tree, c["c4"], "kama-shokunin", "9" * 30,
                                  "round-10: bigdate30"), literal=True)
put_report(fleet, report_text(c["c1"], c["c2"]))
res = audit(lane, fleet, "--json")
doc = jdoc(res)
r0 = doc["results"][0]
say(f"B c10 rc={res[0]} round_commits={r0['round_commits']} required={r0['required']} "
    f"post_report={[s[:10] for s in r0['post_report']]} big={big[:10]} cutoff={r0['cutoff']}")
say(f"B   git log %at for big commit: {gitraw(lane, 'log', '-1', '--format=%at', big)[1].strip()[:40]!r} (len={len(gitraw(lane, 'log', '-1', '--format=%at', big)[1].strip())})")

# C. c04 control: the digit-only prefix removed -> must fail
d, lane, fleet, c = base("j04")
tree = git(lane, "rev-parse", "HEAD^{tree}").strip()
n = 0
while True:
    body = raw_body(tree, c["c4"], "kama-shokunin", T0 + 150, f"round-10: digits {n}")
    s = sha_of("commit", body)
    if s[:7].isdigit():
        break
    n += 1
dig = write_commit(lane, body)
put_report(fleet, report_text(c["c1"], c["c2"]))
say(f"C c04-control(no digit token) rc={audit(lane, fleet)[0]} expect 1")
put_report(fleet, report_text(dig[:7], c["c1"], c["c2"]))
say(f"C c04(with digit token {dig[:7]}) rc={audit(lane, fleet)[0]} expect 1 (if unverified token cannot cite)")

# D. textconv: is the driver applied by `git show HEAD:path`, and by `--textconv`?
d, lane, fleet, c = base("j05")
tc = d / "tc.sh"
tc.write_text("#!/bin/sh\necho ran >> /tmp/revexit/v2_tc2.log\necho '## Work performed'\n", encoding="utf-8")
tc.chmod(0o755)
git(fleet, "config", "diff.zz.textconv", str(tc))
p = fleet / REL
p.parent.mkdir(parents=True)
p.write_text(report_text(c["c1"], c["c2"]), encoding="utf-8")
(fleet / ".gitattributes").write_text(f"{REL} diff=zz\n", encoding="utf-8")
commit(fleet, "round-10 report", author="fleet", when=T0 + 500)
mk = pathlib.Path("/tmp/revexit/v2_tc2.log")
mk.unlink(missing_ok=True)
rc_show, out_show, _ = gitraw(fleet, "show", f"HEAD:{REL}")
say(f"D plain `git show HEAD:path` textconv_ran={mk.exists()} first-line={out_show.splitlines()[0]!r}")
rc_t, out_t, _ = gitraw(fleet, "show", "--textconv", f"HEAD:{REL}")
say(f"D `git show --textconv HEAD:path` textconv_ran={mk.exists()} first-line={out_t.splitlines()[0]!r}")
say(f"D   attr check: {gitraw(fleet, 'check-attr', 'diff', '--', REL)[1].strip()!r}")
mk.unlink(missing_ok=True)
say(f"D audit rc={audit(lane, fleet)[0]} textconv_ran={mk.exists()} expect 0")

# E. symlink report: what `git show` hands the audit, and the verdict
d, lane, fleet, c = base("j06")
p = fleet / REL
p.parent.mkdir(parents=True)
os.symlink(report_text(c["c1"], c["c2"]), p)
commit(fleet, "round-10 symlink report", author="fleet", when=T0 + 500)
rc_s, out_s, _ = gitraw(fleet, "show", f"HEAD:{REL}")
say(f"E `git show HEAD:{REL}` -> {out_s[:60]!r}... ({len(out_s)} chars)")
say(f"E audit rc={audit(lane, fleet)[0]} expect 2")

# F. corrupt loose object: what git says, and the audit verdict/defect kind
d, lane, fleet, c = base("j09")
blob = git(lane, "hash-object", "-w", "--stdin", input=b"probe blob\n").strip()
put_report(fleet, report_text(c["c1"], c["c2"], work=f"- cites {blob}"))
loose = lane / ".git" / "objects" / blob[:2] / blob[2:]
loose.chmod(0o644)
loose.write_bytes(b"corrupt loose object")
rc_c, out_c, err_c = gitraw(lane, "cat-file", "--batch-check", input=(blob + "\n").encode())
say(f"F git cat-file --batch-check rc={rc_c} stdout={out_c.strip()!r} stderr={err_c.strip()[:120]!r}")
res = audit(lane, fleet, "--json")
doc = jdoc(res)
say(f"F audit rc={res[0]} defects={[(x['kind'], x['token'][:10]) for x in doc['results'][0]['defects']]} expect 2")

# G. cross-repo union ambiguity WITHOUT per-repo ambiguity: lane commit and fleet commit share P
d, lane, fleet, c = base("j23")
fleet_body = {}
for j in range(1 << 16):
    b = raw_body("4b825dc642cb6eb9a060e54bf8d69288fbee4904", c["c4"],
                 "fleet-writer", T0 + 900, f"fleet side {j}")
    fleet_body.setdefault(sha_of("commit", b)[:7], b)
tree = git(lane, "rev-parse", "HEAD^{tree}").strip()
i = 0
while True:
    body = raw_body(tree, c["c4"], "kama-shokunin", T0 + 100, f"round-10: lane side {i}")
    s = sha_of("commit", body)
    p7 = s[:7]
    if p7 in fleet_body and any(ch.isdigit() for ch in p7) and any(ch.isalpha() for ch in p7):
        break
    i += 1
lsha = write_commit(lane, body)
fsha = write_commit(fleet, fleet_body[p7], branch=False)
say(f"G P={p7} lane={lsha[:10]} fleet={fsha[:10]} lane-cands={git(lane, 'rev-parse', '--disambiguate=' + p7).split()} "
    f"fleet-cands={git(fleet, 'rev-parse', '--disambiguate=' + p7).split()}")
put_report(fleet, report_text(c["c1"], c["c2"], p7))
res = audit(lane, fleet, "--json")
doc = jdoc(res)
say(f"G audit rc={res[0]} defects={[(x['kind'], x['token'][:10]) for x in doc['results'][0]['defects']]} expect 1")

# H. stdout closed (fd 1 closed in the child): is the verdict lost with exit 0?
d, lane, fleet, c = base("j25")
put_report(fleet, report_text(c["c1"], c["c2"]))


def close_stdout():
    os.close(1)


p = subprocess.run([sys.executable, SCRIPT, "--lane-repo", str(lane),
                    "--fleet-repo", str(fleet), "--rounds", "10", "--no-errata"],
                   env=dict(BASE), stderr=subprocess.PIPE, preexec_fn=close_stdout,
                   cwd="/tmp/revexit")
say(f"H closed-stdout clean-report rc={p.returncode} stderr={p.stderr.decode(errors='replace').strip()[-120:]!r} expect 2")

# I. stdout full disk: output failure
d, lane, fleet, c = base("j26")
put_report(fleet, report_text(c["c1"], c["c2"]))
with open("/dev/full", "w") as full:
    p = subprocess.run([sys.executable, SCRIPT, "--lane-repo", str(lane),
                        "--fleet-repo", str(fleet), "--rounds", "10", "--no-errata"],
                       env=dict(BASE), stdout=full, stderr=subprocess.PIPE, cwd="/tmp/revexit")
say(f"I /dev/full stdout rc={p.returncode} stderr={p.stderr.decode(errors='replace').strip()[-120:]!r} expect 2")

# J. fleet report path with a 5000-digit round directory under an open range
d, lane, fleet, c = base("j27")
bl = git(fleet, "hash-object", "-w", "--stdin", input=b"x\n").strip()
hugepath = f".ufo/reports/round-{'9' * 5000}/kama.md"
git(fleet, "update-index", "--add", "--cacheinfo", f"100644,{bl},{hugepath}")
commit(fleet, "odd path", author="fleet", when=T0 + 500)
res = audit(lane, fleet, rounds="10-")
say(f"J open-range with 5000-digit round path rc={res[0]} stderr-last={res[2].strip().splitlines()[-1][:120] if res[2].strip() else ''!r} expect 2")

open("/tmp/revexit/v2_outputs2.txt", "w").write("\n".join(OUT) + "\n")
