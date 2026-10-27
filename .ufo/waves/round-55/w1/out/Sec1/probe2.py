"""Probe 2: what an inherited HOME can actually do to the frozen counters' git calls.

Checks, in order:
 1. is the hostile $HOME/.gitconfig read at all (git config --get)?
 2. can [alias] override a builtin the counters call (log/show/archive)?
 3. does tar.tar.command fire for --format=tar / --format=tar.gz?
 4. does color.ui=always corrupt the NUL-separated path list `git log -z --name-only`?
 5. does diff.external / textconv fire on `git log --name-only` / `git show rev:path`?
Each probe runs against the fixture D with HOME pointed at the hostile dir, env = the
frozen counter's own clean_env() when a counter helper is used.
"""
import importlib.util, os, subprocess, sys

S, FIX = os.environ["S"], os.environ["D"]
COUNTER = os.environ["COUNTER"]
evil = os.path.join(S, "evilhome2")
os.makedirs(evil, exist_ok=True)
marker = os.path.join(S, "MARKER")

spec = importlib.util.spec_from_file_location("c1frozen", COUNTER)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
os.environ["HOME"] = evil
ENV = m.clean_env()                      # the frozen filter, verbatim


def write_cfg(body):
    with open(os.path.join(evil, ".gitconfig"), "w") as fh:
        fh.write(body)


def run(args, extra_env=None):
    e = dict(ENV)
    e.update(extra_env or {})
    return subprocess.run(["git", "-C", FIX, *args], capture_output=True, env=e)


def reset():
    if os.path.exists(marker):
        os.unlink(marker)


# 1. config is read
write_cfg('[user]\n\tname = attacker\n')
p = run(["config", "--get", "user.name"])
print("1 config read through inherited HOME: rc=%d out=%r" % (p.returncode, p.stdout.strip()))

# 1b. XDG_CONFIG_HOME channel
xdg = os.path.join(S, "xdg")
os.makedirs(os.path.join(xdg, "git"), exist_ok=True)
with open(os.path.join(xdg, "git", "config"), "w") as fh:
    fh.write('[user]\n\tname = xdgattacker\n')
os.rename(os.path.join(evil, ".gitconfig"), os.path.join(evil, ".gitconfig.off"))
p = run(["config", "--get", "user.name"], {"XDG_CONFIG_HOME": xdg})
print("1b config read through inherited XDG_CONFIG_HOME: rc=%d out=%r" % (p.returncode, p.stdout.strip()))
os.rename(os.path.join(evil, ".gitconfig.off"), os.path.join(evil, ".gitconfig"))

# 2. alias override of a builtin
for cmd in ("log", "show", "archive", "rev-parse", "ls-tree", "cat-file"):
    reset()
    write_cfg('[alias]\n\t%s = !sh -c "echo PWNED > %s"\n' % (cmd, marker))
    p = run([cmd, "--help"] if cmd in ("log",) else [cmd])
    kind = "shell command" if os.path.exists(marker) else ("git error" if p.returncode else "builtin ran")
    print("2 alias %-11s -> %s (rc=%d)" % (cmd, kind, p.returncode))

# 3. tar.<format>.command
for fmt in ("tar", "tar.gz"):
    reset()
    write_cfg('[tar "%s"]\n\tcommand = sh -c \'cat >/dev/null; echo PWNED > %s\'\n' % (fmt, marker))
    p = run(["config", "--get", "tar.%s.command" % fmt])
    seen = p.stdout.strip() != b""
    p = run(["archive", "--format=" + fmt, "HEAD"])
    print("3 tar.%s.command set=%s archive rc=%d bytes=%d marker=%s"
          % (fmt, seen, p.returncode, len(p.stdout), os.path.exists(marker)))

# 4. color.ui=always on log -z --name-only  (C2 history_paths shape)
reset()
write_cfg('[color]\n\tui = always\n')
p = run(["log", "HEAD", "--name-only", "--format=", "-z"])
print("4 color.ui=always log -z bytes=%r" % (p.stdout[:120],))

# 5. diff.external / textconv
reset()
write_cfg('[diff]\n\texternal = sh -c \'echo PWNED > %s; exit 0\'\n' % marker)
p = run(["log", "HEAD", "--name-only", "--format="])
print("5a diff.external on log --name-only: rc=%d marker=%s" % (p.returncode, os.path.exists(marker)))
reset()
write_cfg('[diff "evil"]\n\ttextconv = sh -c \'echo PWNED > %s; cat\'\n' % marker)
with open(os.path.join(FIX, ".gitattributes"), "w") as fh:
    fh.write("a.txt diff=evil\n")
p = run(["show", "HEAD:a.txt"])
print("5b textconv on show rev:path: rc=%d marker=%s out=%r" % (p.returncode, os.path.exists(marker), p.stdout[:40]))
os.unlink(os.path.join(FIX, ".gitattributes"))

# 6. core.fsmonitor / core.hooksPath on the read paths the counters use
reset()
write_cfg('[core]\n\tfsmonitor = sh -c \'echo PWNED > %s\'\n\thooksPath = %s\n'
          % (marker, os.path.join(S, "hooks")))
for args in (["rev-parse", "--verify", "HEAD^{commit}"], ["show", "HEAD:a.txt"],
             ["ls-tree", "-r", "--name-only", "-z", "HEAD"], ["cat-file", "-e", "HEAD^{commit}"],
             ["archive", "--format=tar", "HEAD"]):
    reset()
    p = run(args, {"GIT_CONFIG_COUNT": "0"})
    print("6 %-40s rc=%d marker=%s" % (" ".join(args)[:38], p.returncode, os.path.exists(marker)))
reset()
print("done")
