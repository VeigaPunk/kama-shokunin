import os, subprocess, tempfile
from pathlib import Path
ISO=("--no-replace-objects","--no-lazy-fetch","-c","i18n.logOutputEncoding=UTF-8",
     "-c","log.follow=false","-c","log.showRoot=true","-c","log.showSignature=false","-c","log.mailmap=false")
def env():
    e={k:v for k,v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull,GIT_CONFIG_NOSYSTEM="1"); return e
def g(repo,*a,stdin=None):
    p=subprocess.run(["git",*ISO,"-C",str(repo),*a],input=stdin.encode() if stdin else None,capture_output=True,env=env(),timeout=30)
    return p.returncode,p.stdout.decode("utf-8","replace"),p.stderr.decode("utf-8","replace").strip()
def gp(repo,*a):
    p=subprocess.run(["git","-C",str(repo),*a],capture_output=True,env=env(),timeout=30)
    return p.returncode,p.stdout.decode("utf-8","replace"),p.stderr.decode("utf-8","replace").strip()
with tempfile.TemporaryDirectory() as tmp:
    repo=Path(tmp,"r"); repo.mkdir()
    gp(repo,"init","-q","-b","master"); gp(repo,"config","user.name","p"); gp(repo,"config","user.email","p@x")
    (repo/"corpus").mkdir(); (repo/"corpus"/"SOURCES.md").write_text("| S001 | x | docs | A | y | z | w | mined | 2026-10-21 | on-release | - |\n")
    (repo/".ufo/reports/round-1").mkdir(parents=True); (repo/".ufo/reports/round-1/kama.md").write_text("# r1\n")
    gp(repo,"add","-A"); gp(repo,"-c","commit.gpgsign=false","commit","-q","-m","round-1: x")
    gp(repo,"config","extensions.partialClone","origin")
    blob=gp(repo,"rev-parse","--verify","HEAD:corpus/SOURCES.md")[1].strip()
    tree=gp(repo,"rev-parse","--verify","HEAD^{tree}")[1].strip()
    rep =gp(repo,"rev-parse","--verify","HEAD:.ufo/reports/round-1/kama.md")[1].strip()
    # A) ls-tree with missing root tree
    Path(repo,".git/objects",tree[:2],tree[2:]).unlink()
    print("A ls-tree with missing root tree:", g(repo,"ls-tree","master","--","corpus/SOURCES.md"))
    # restore tree, delete SOURCES blob
    subprocess.run(["git","-C",str(repo),"hash-object","-w","-t","tree","--stdin"],input=b"",capture_output=True,env=env())
    # rebuild tree+commit is complex; instead use a fresh repo for the blob case
    repo2=Path(tmp,"r2"); repo2.mkdir()
    gp(repo2,"init","-q","-b","master"); gp(repo2,"config","user.name","p"); gp(repo2,"config","user.email","p@x")
    (repo2/"corpus").mkdir(); (repo2/"corpus"/"SOURCES.md").write_text("| S001 | x | docs | A | y | z | w | mined | 2026-10-21 | on-release | - |\n")
    (repo2/".ufo/reports/round-1").mkdir(parents=True); (repo2/".ufo/reports/round-1/kama.md").write_text("# r1\n")
    gp(repo2,"add","-A"); gp(repo2,"-c","commit.gpgsign=false","commit","-q","-m","round-1: x")
    gp(repo2,"config","extensions.partialClone","origin")
    b2=gp(repo2,"rev-parse","--verify","HEAD:corpus/SOURCES.md")[1].strip()
    r2=gp(repo2,"rev-parse","--verify","HEAD:.ufo/reports/round-1/kama.md")[1].strip()
    Path(repo2,".git/objects",b2[:2],b2[2:]).unlink()
    print("B cat-file blob (missing blob):", g(repo2,"cat-file","blob",b2))
    print("C show HEAD:report (blob present):", g(repo2,"show","HEAD:.ufo/reports/round-1/kama.md"))
    Path(repo2,".git/objects",r2[:2],r2[2:]).unlink()
    print("D show HEAD:report (report blob missing):", g(repo2,"show","HEAD:.ufo/reports/round-1/kama.md"))
    print("E ls-tree --name-only (all present):", g(repo2,"ls-tree","-r","--name-only","HEAD","--",".ufo/reports"))
    print("F rev-parse --verify HEAD^{commit}:", g(repo2,"rev-parse","--verify","HEAD^{commit}"))
