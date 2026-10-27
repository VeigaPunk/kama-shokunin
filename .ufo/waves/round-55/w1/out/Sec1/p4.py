import importlib.util, os, subprocess
S, FIX = os.environ["S"], os.environ["D"]
evil = os.path.join(S, "evilhome4"); os.makedirs(evil, exist_ok=True)
spec = importlib.util.spec_from_file_location("c1frozen", os.environ["COUNTER"])
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
os.environ["HOME"] = evil
ENV = m.clean_env()
def run(args):
    return subprocess.run(["git", "-C", FIX] + args, capture_output=True, env=dict(ENV))
def cfg(body):
    open(os.path.join(evil, ".gitconfig"), "w").write(body)
FMT = ["--format=%H"]
cfg('[i18n]\n\tlogOutputEncoding = utf-16\n')
p = run(["log", "-1"] + FMT + ["HEAD"])
print("A i18n utf-16  log --format=%H ->", p.stdout[:40])
p = run(["log", "HEAD", "--name-only", "--format=", "-z"])
print("B i18n utf-16  log -z --name-only ->", p.stdout[:40])
cfg('[i18n]\n\tlogOutputEncoding = ISO-8859-1\n')
p = run(["log", "-1"] + FMT + ["HEAD"])
print("C i18n latin1  log --format=%H ->", p.stdout[:40])
cfg('[core]\n\tquotePath = false\n[color]\n\tui = always\n[color "diff"]\n\tplain = red bold\n')
p = run(["log", "HEAD", "--name-only", "--format="])
print("D color+quotepath log --name-only (non -z) ->", p.stdout[:60])
cfg('[log]\n\tfollow = true\n')
p = run(["log", "HEAD", "-1"] + FMT + ["--", "a.txt"])
print("E log.follow=true log -1 -- a.txt ->", p.stdout.strip())
