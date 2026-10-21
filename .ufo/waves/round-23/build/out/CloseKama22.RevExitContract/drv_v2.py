import hashlib, os, pathlib, resource, shutil, subprocess, sys

R = pathlib.Path("/tmp/revexit/v2cases")
SCRIPT = "/tmp/revexit/rla_v2.py"
HOME = "/tmp/revexit/home"
BASE = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
BASE.update(GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1", HOME=HOME)
T0 = 1700000000
REL = ".ufo/reports/round-10/kama.md"
LOG = open("/tmp/revexit/v2_results.log", "w", encoding="utf-8")
ROWS = []


def git(repo, *args, env=None, input=None, ok=True):
    e = dict(BASE)
    e.update(env or {})
    p = subprocess.run(["git", "-C", str(repo), *args], env=e, input=input,
                       capture_output=True)
    if ok and p.returncode:
        raise SystemExit(f"fixture git {args} rc={p.returncode}: "
                         f"{p.stderr.decode(errors='replace')}")
    return p.stdout.decode("utf-8", "replace")


def gitenv(author, when):
    return {"GIT_AUTHOR_NAME": author, "GIT_COMMITTER_NAME": author,
            "GIT_AUTHOR_EMAIL": "a@x", "GIT_COMMITTER_EMAIL": "a@x",
            "GIT_AUTHOR_DATE": f"@{when} +0000",
            "GIT_COMMITTER_DATE": f"@{when} +0000"}


def commit(repo, subject, author="kama-shokunin", when=T0):
    git(repo, "add", "-A", env=gitenv(author, when))
    git(repo, "-c", "commit.gpgsign=false", "commit", "-q", "--allow-empty",
        "-m", subject, env=gitenv(author, when))
    return git(repo, "rev-parse", "HEAD").strip()


def new_repo(path):
    path.mkdir(parents=True)
    git(path, "init", "-q", "-b", "master")
    return path


def base(name):
    d = R / name
    shutil.rmtree(d, ignore_errors=True)
    d.mkdir(parents=True)
    lane = new_repo(d / "lane")
    fleet = new_repo(d / "fleet")
    c1 = commit(lane, "round-10: first", when=T0)
    c2 = commit(lane, "round-10: second", when=T0 + 100)
    c3 = commit(lane, "checkpoint(r11): mid", when=T0 + 200)
    c4 = commit(lane, "misc", author="human", when=T0 + 300)
    return d, lane, fleet, dict(c1=c1, c2=c2, c3=c3, c4=c4)


def report_text(*lines, work="- did the work"):
    return ("# kama round 10\n\n## Work performed\n" + work + "\n\n"
            "## Landed changes\n" + "".join(l + "\n" for l in lines))


def put_report(fleet, text, when=T0 + 500):
    p = fleet / REL
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    commit(fleet, "round-10 report", author="fleet", when=when)


def raw_body(tree, parent, author_field, when_field, subject):
    return (f"tree {tree}\nparent {parent}\n"
            f"author {author_field} <a@x> {when_field} +0000\n"
            f"committer {author_field} <a@x> {when_field} +0000\n\n"
            f"{subject}\n").encode()


def sha_of(kind, body):
    return hashlib.sha1(f"{kind} {len(body)}".encode() + b"\0" + body).hexdigest()


def write_commit(repo, body, branch=True, literal=False):
    extra = ["--literally"] if literal else []
    sha = git(repo, "hash-object", "-t", "commit", "-w", *extra, "--stdin",
              input=body).strip()
    if branch:
        git(repo, "update-ref", "refs/heads/master", sha)
    return sha


def audit(lane, fleet, *extra, rounds="10", env=None, errata=False, pre=None):
    cmd = [sys.executable, SCRIPT, "--lane-repo", str(lane),
           "--fleet-repo", str(fleet), "--rounds", rounds, *extra]
    if not errata:
        cmd.append("--no-errata")
    e = dict(BASE)
    e.update(env or {})
    p = subprocess.run(cmd, env=e, capture_output=True, cwd="/tmp/revexit",
                       preexec_fn=pre)
    return p.returncode, p.stdout.decode("utf-8", "replace"), \
        p.stderr.decode("utf-8", "replace")


def record(name, expect, res, note=""):
    rc, out, err = res
    LOG.write(f"=== {name} rc={rc} expect={expect} {note}\n--- stdout\n{out}\n"
              f"--- stderr\n{err}\n")
    last_out = next((l for l in reversed(out.splitlines()) if l.strip()), "")
    last_err = next((l for l in reversed(err.splitlines()) if l.strip()), "")
    ROWS.append(f"{name:30} rc={rc} expect={expect} stdout-last={last_out[:90]!r} "
                f"stderr-last={last_err[:140]!r} {note}")


# 01 baseline: both round-10 commits cited -> must be clean
d, lane, fleet, c = base("c01")
put_report(fleet, report_text(c["c1"], c["c2"]))
record("baseline-clean", 0, audit(lane, fleet))

# 02 control: unrelated plain round commit omitted -> must fail (1)
d, lane, fleet, c = base("c02")
commit(lane, "round-10: plain", when=T0 + 150)
put_report(fleet, report_text(c["c1"], c["c2"]))
record("control-plain-omitted", 1, audit(lane, fleet))

# 03 NUL-free separator byte (0x1f) inside author name hides a round commit
d, lane, fleet, c = base("c03")
commit(lane, "round-10: hidden", author="kama-shokunin\x1f1700", when=T0 + 150)
put_report(fleet, report_text(c["c1"], c["c2"]))
record("sep-in-author-hides-commit", 1, audit(lane, fleet))

# 04 digit-only 7-hex prefix of an omitted round commit satisfies omission check
d, lane, fleet, c = base("c04")
tree = git(lane, "rev-parse", "HEAD^{tree}").strip()
n = 0
while True:
    body = raw_body(tree, c["c4"], "kama-shokunin", T0 + 150,
                    f"round-10: digits {n}")
    s = sha_of("commit", body)
    if s[:7].isdigit():
        break
    n += 1
dig = write_commit(lane, body)
assert dig == s, (dig, s)
put_report(fleet, report_text(dig[:7], c["c1"], c["c2"]))
record("digit-prefix-satisfies-omit", 1, audit(lane, fleet),
       note=f"(prefix {dig[:7]} unverified; expect 1 if unchecked tokens cannot cite)")

# 05 textconv driver attached to the report path: does `git show HEAD:path` run it?
d, lane, fleet, c = base("c05")
tc = d / "tc.sh"
tc.write_text("#!/bin/sh\necho ran >> /tmp/revexit/v2_tc.log\n"
              "echo '## Work performed'\n", encoding="utf-8")
tc.chmod(0o755)
git(fleet, "config", "diff.zz.textconv", str(tc))
p = fleet / REL
p.parent.mkdir(parents=True)
p.write_text(report_text(c["c1"], c["c2"]), encoding="utf-8")
(fleet / ".gitattributes").write_text(f"{REL} diff=zz\n", encoding="utf-8")
commit(fleet, "round-10 report", author="fleet", when=T0 + 500)
tcl = pathlib.Path("/tmp/revexit/v2_tc.log")
tcl.unlink(missing_ok=True)
res = audit(lane, fleet)
record("textconv-on-show-blob", 0, res,
       note=f"textconv_ran={tcl.exists()}")

# 06 report path is a symlink whose target text is a complete clean report
d, lane, fleet, c = base("c06")
p = fleet / REL
p.parent.mkdir(parents=True)
os.symlink(report_text(c["c1"], c["c2"]), p)
commit(fleet, "round-10 symlink report", author="fleet", when=T0 + 500)
record("symlink-report-target-text", 2, audit(lane, fleet))

# 07 report path is a symlink to a non-report
d, lane, fleet, c = base("c07")
p = fleet / REL
p.parent.mkdir(parents=True)
os.symlink("../round-9/kama.md", p)
commit(fleet, "round-10 symlink report", author="fleet", when=T0 + 500)
record("symlink-report-dangling", 2, audit(lane, fleet))

# 08 report path is a directory
d, lane, fleet, c = base("c08")
p = fleet / REL / "index.txt"
p.parent.mkdir(parents=True)
p.write_text("x\n", encoding="utf-8")
commit(fleet, "round-10 dir report", author="fleet", when=T0 + 500)
record("directory-at-report-path", 2, audit(lane, fleet))

# 09 cited blob's loose object corrupted in the lane odb
d, lane, fleet, c = base("c09")
blob = git(lane, "hash-object", "-w", "--stdin", input=b"probe blob\n").strip()
put_report(fleet, report_text(c["c1"], c["c2"], work=f"- cites {blob}"))
record("blob-control-present", 0, audit(lane, fleet))
loose = lane / ".git" / "objects" / blob[:2] / blob[2:]
loose.chmod(0o644)
loose.write_bytes(b"corrupt loose object")
record("corrupt-loose-object", 2, audit(lane, fleet))

# 10 author timestamp with 30 digits
d, lane, fleet, c = base("c10")
tree = git(lane, "rev-parse", "HEAD^{tree}").strip()
write_commit(lane, raw_body(tree, c["c4"], "kama-shokunin", "9" * 30,
                            "round-10: bigdate30"), literal=True)
put_report(fleet, report_text(c["c1"], c["c2"]))
record("author-date-30-digits", 1, audit(lane, fleet))

# 11 author timestamp with 5000 digits
d, lane, fleet, c = base("c11")
tree = git(lane, "rev-parse", "HEAD^{tree}").strip()
write_commit(lane, raw_body(tree, c["c4"], "kama-shokunin", "9" * 5000,
                            "round-10: bigdate5000"), literal=True)
put_report(fleet, report_text(c["c1"], c["c2"]))
record("author-date-5000-digits", 2, audit(lane, fleet))

# 12 per-repo ambiguity masked: lane has blob+commit sharing 7-hex prefix P,
#    fleet holds only the commit, so P resolves there and the check passes
d, lane, fleet, c = base("c12")
blob_prefix = {}
for k in range(1 << 16):
    content = f"blob {k}\n".encode()
    blob_prefix.setdefault(sha_of("blob", content)[:7], content)
tree = git(lane, "rev-parse", "HEAD^{tree}").strip()
i = 0
while True:
    body = raw_body(tree, c["c4"], "kama-shokunin", T0 + 100,
                    f"round-10: collide {i}")
    s = sha_of("commit", body)
    p7 = s[:7]
    if (p7 in blob_prefix and any(ch.isdigit() for ch in p7)
            and any(ch.isalpha() for ch in p7)):
        break
    i += 1
bsha = git(lane, "hash-object", "-w", "--stdin",
           input=blob_prefix[p7]).strip()
assert bsha[:7] == p7
lsha = write_commit(lane, body)
write_commit(fleet, body, branch=False)
assert lsha == s
git(lane, "update-ref", "refs/heads/master", lsha)
dis_lane = git(lane, "rev-parse", f"--disambiguate={p7}").split()
dis_fleet = git(fleet, "rev-parse", f"--disambiguate={p7}").split()
LOG.write(f"c12 P={p7} lane-candidates={dis_lane} fleet-candidates={dis_fleet}\n")
put_report(fleet, report_text(c["c1"], c["c2"], p7))
record("ambiguous-prefix-masked", 1, audit(lane, fleet),
       note=f"lane-cands={len(dis_lane)} fleet-cands={len(dis_fleet)}")

# 13 branch named like a 7-hex abbreviation that does not name any object
d, lane, fleet, c = base("c13")
git(lane, "branch", "abcdef1", c["c1"])
put_report(fleet, report_text(c["c1"], c["c2"], "abcdef1"))
record("ref-named-like-abbrev", 2, audit(lane, fleet))

# 14 shallow lane clone
d, lane, fleet, c = base("c14")
put_report(fleet, report_text(c["c1"], c["c2"]))
shallow = d / "lane-shallow"
subprocess.run(["git", "clone", "-q", "--depth", "1", "file://" + str(lane),
                str(shallow)], env=BASE, check=True)
record("shallow-lane-clone", 2, audit(shallow, fleet))

# 15 promisor (partial) lane clone
d, lane, fleet, c = base("c15")
put_report(fleet, report_text(c["c1"], c["c2"]))
git(lane, "config", "uploadpack.allowFilter", "true")
partial = d / "lane-partial"
subprocess.run(["git", "clone", "-q", "--no-local", "--filter=blob:none",
                "file://" + str(lane), str(partial)], env=BASE, check=True)
record("partial-lane-clone", 2, audit(partial, fleet))

# 16 info/grafts rewrites lane history
d, lane, fleet, c = base("c16")
put_report(fleet, report_text(c["c1"], c["c2"]))
(lane / ".git" / "info").mkdir(exist_ok=True)
(lane / ".git" / "info" / "grafts").write_text(f"{c['c3']} {c['c1']}\n")
record("info-grafts-present", 2, audit(lane, fleet))

# 17 lane path is a subdirectory of a repository
d, lane, fleet, c = base("c17")
put_report(fleet, report_text(c["c1"], c["c2"]))
(lane / "sub").mkdir()
record("lane-path-is-subdirectory", 2, audit(lane / "sub", fleet))

# 18 Python ValueError: round number over the int digit limit
d, lane, fleet, c = base("c18")
put_report(fleet, report_text(c["c1"], c["c2"]))
record("rounds-arg-5000-digits", 2, audit(lane, fleet, rounds="1" + "0" * 5000))

# 19 Python ValueError: errata round over the int digit limit (malformed ledger)
d, lane, fleet, c = base("c19")
put_report(fleet, report_text(c["c1"], c["c2"]))
errata = d / "errata.tsv"
errata.write_text("1" + "0" * 5000 + f"\tlanded-omitted\t{c['c3']}\t{c['c3']}\tev\n",
                  encoding="utf-8")
record("errata-round-5000-digits", 2,
       audit(lane, fleet, "--errata", str(errata), errata=True))

# 20 MemoryError: huge explicit round range under a 1 GiB address-space limit
d, lane, fleet, c = base("c20")
put_report(fleet, report_text(c["c1"], c["c2"]))


def limit():
    resource.setrlimit(resource.RLIMIT_AS, (1 << 30, 1 << 30))


record("round-range-memory", 2, audit(lane, fleet, rounds="1-30000000", pre=limit))

# 21 non-ASCII path in an EvalError message with ASCII stderr
d, lane, fleet, c = base("c21")
put_report(fleet, report_text(c["c1"], c["c2"]))
record("eval-msg-nonascii-ascii-stderr", 2,
       audit(d / "\u00e9-missing", fleet, env={"PYTHONIOENCODING": "ascii"}))

# 22 non-ASCII errata correction printed with ASCII stdout
d, lane, fleet, c = base("c22")
put_report(fleet, report_text(c["c1"], c["c2"]))
errata = d / "errata.tsv"
errata.write_text(f"10\tlanded-unresolved\tdeadbeef1\t\u00e9\tev\n", encoding="utf-8")
record("render-nonascii-ascii-stdout", 2,
       audit(lane, fleet, "--errata", str(errata), errata=True,
             env={"PYTHONIOENCODING": "ascii"}))

LOG.close()
for row in ROWS:
    print(row)
