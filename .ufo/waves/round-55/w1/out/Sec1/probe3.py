"""Probe 3: last exec-on-read config candidates + the fixture's hermeticity contrast."""
import importlib.util, os, subprocess, sys

S, FIX = os.environ["S"], os.environ["D"]
COUNTER = os.environ["COUNTER"]
evil = os.path.join(S, "evilhome3")
os.makedirs(evil, exist_ok=True)
marker = os.path.join(S, "MARKER3")

spec = importlib.util.spec_from_file_location("c1frozen", COUNTER)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
os.environ["HOME"] = evil
ENV = m.clean_env()


def write_cfg(body):
    with open(os.path.join(evil, ".gitconfig"), "w") as fh:
        fh.write(body)


def run(args, env=None, clean=False):
    e = dict(ENV) if not clean else dict(ENV, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
    e.update(env or {})
    return subprocess.run(["git", "-C", FIX, *args], capture_output=True, env=e)


def reset():
    if os.path.exists(marker):
        os.unlink(marker)


# log.showSignature -> gpg.program exec?
reset()
write_cfg('[log]\n\tshowSignature = true\n[gpg]\n\tprogram = sh -c \'echo PWNED > %s; cat\'\n' % marker)
p = run(["log", "-1", "--format=%H", "HEAD"])
print("A log.showSignature+gpg.program: rc=%d out=%r marker=%s" % (p.returncode, p.stdout[:60], os.path.exists(marker)))
reset()
p = run(["log", "HEAD", "--name-only", "--format=", "-z"])
print("B same, counters' history_paths shape: rc=%d bytes=%d marker=%s" % (p.returncode, len(p.stdout), os.path.exists(marker)))

# core.pager under capture_output (pipe, no tty)
reset()
write_cfg('[core]\n\tpager = sh -c \'echo PWNED > %s; cat\'\n[pager]\n\tlog = sh -c \'echo PWNED > %s; cat\'\n' % (marker, marker))
p = run(["log", "-1", "--format=%H", "HEAD"])
print("C core.pager on log: rc=%d marker=%s" % (p.returncode, os.path.exists(marker)))

# safe.directory: does hostile config disable git's dubious-ownership refusal?
write_cfg('[safe]\n\tdirectory = *\n')
p = run(["config", "--get", "safe.directory"])
print("D hostile safe.directory readable=%r" % (p.stdout.strip(),))

# contrast: the C2 fixture's own env closes the same channel
reset()
write_cfg('[tar "tar"]\n\tcommand = sh -c \'cat >/dev/null; echo PWNED > %s\'\n[log]\n\tshowSignature = true\n'
          '[gpg]\n\tprogram = sh -c \'echo PWNED > %s; cat\'\n' % (marker, marker))
p = run(["config", "--get", "user.name"], clean=True)
p2 = run(["config", "--list", "--show-origin"], clean=True)
print("E fixture-shaped env (GIT_CONFIG_GLOBAL=/dev/null + NOSYSTEM=1) exposes hostile keys: %r"
      % (b"tar.tar.command" in p2.stdout or b"gpg.program" in p2.stdout))
