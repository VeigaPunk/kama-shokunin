"""Probe: does an inherited HOME reach the frozen C1 counter's git()?

Faithful: imports the frozen counter module and calls its own git() helper, so
clean_env() is the only filter under test.  Nothing in the lane is modified.
"""
import importlib.util, os, sys

S, D = os.environ["S"], os.environ["D"]
COUNTER = os.environ["COUNTER"]

evil = os.path.join(S, "evilhome")
os.makedirs(evil, exist_ok=True)
marker = os.path.join(S, "TAR-RAN")
with open(os.path.join(evil, ".gitconfig"), "w") as fh:
    fh.write('[tar "tar"]\n\tcommand = sh -c \'cat >/dev/null; echo PWNED > %s\'\n' % marker)

os.environ["HOME"] = evil
os.environ.pop("XDG_CONFIG_HOME", None)
for k in [k for k in os.environ if k.startswith("GIT_")]:
    print("inherited GIT_ var (would be stripped):", k)

spec = importlib.util.spec_from_file_location("c1frozen", COUNTER)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

print("clean_env keeps HOME:", repr(m.clean_env().get("HOME")))
print("clean_env keeps XDG_CONFIG_HOME:", repr(m.clean_env().get("XDG_CONFIG_HOME")))

p = m.git(D, "archive", "--format=tar", "HEAD")
print("git archive rc=%d bytes=%d stderr=%r" % (p.returncode, len(p.stdout), p.stderr[:200]))
print("marker exists after archive:", os.path.exists(marker))

if os.path.exists(marker):
    os.unlink(marker)
p = m.git(D, "show", "HEAD:a.txt", check=False)
print("git show rc=%d stderr=%r marker=%s" % (p.returncode, p.stderr[:120], os.path.exists(marker)))
p = m.git(D, "rev-parse", "--verify", "HEAD^{commit}")
print("git rev-parse rc=%d out=%r marker=%s" % (p.returncode, p.stdout.strip(), os.path.exists(marker)))
