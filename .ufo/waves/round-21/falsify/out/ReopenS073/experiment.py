#!/usr/bin/env python3
"""ReopenS073 scratch experiment: %at vs %ct and --diff-filter=A on git 2.56.0.

Runs only inside /tmp/kama-r21-ReopenS073/exp (scratch). Reads and writes no lane or
fleet state; GIT_* variables are stripped and HOME/global config point at scratch.
"""
import os
import pathlib
import shutil
import subprocess

S = pathlib.Path("/tmp/kama-r21-ReopenS073/exp")
shutil.rmtree(S, ignore_errors=True)
(S / "home").mkdir(parents=True)
(S / "gitconfig-empty").write_text("")
REPO = S / "repo"
REPO.mkdir()

ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update({
    "HOME": str(S / "home"),
    "XDG_CONFIG_HOME": str(S / "home" / "xdg"),
    "GIT_CONFIG_GLOBAL": str(S / "gitconfig-empty"),
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_AUTHOR_NAME": "Scratch",
    "GIT_AUTHOR_EMAIL": "scratch@example.invalid",
    "GIT_COMMITTER_NAME": "Scratch",
    "GIT_COMMITTER_EMAIL": "scratch@example.invalid",
})


def git(*args, dates=None):
    env = dict(ENV)
    if dates is not None:
        author, committer = dates
        env["GIT_AUTHOR_DATE"] = f"@{author} +0000"
        env["GIT_COMMITTER_DATE"] = f"@{committer} +0000"
    proc = subprocess.run(["git", *args], cwd=REPO, env=env, capture_output=True, text=True)
    if proc.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed rc={proc.returncode}: {proc.stderr}")
    return proc.stdout


def commit(msg, author, committer):
    git("add", "-A")
    git("commit", "-q", "-m", msg, dates=(author, committer))


def show(title, *args):
    print(f"## {title}")
    print(f"$ git {' '.join(args)}")
    print(git(*args), end="")
    print()


git("init", "-q", "-b", "main")
print("git:", git("--version").strip())
print()

(REPO / "f").write_text("one\n")
commit("c1 add f", 1000000000, 1000000500)          # author 1000000000, committer 1000000500
(REPO / "f").write_text("two\n")
commit("c2 modify f", 1000000600, 1000000600)
(REPO / "g").write_text("g\n")
commit("c3 add g", 1000000700, 1000000700)
(REPO / "f").unlink()
commit("c4 delete f", 1000000800, 1000000800)
(REPO / "f").write_text("three\n")
commit("c5 re-add f", 1000000900, 1000000100)        # committer earlier than author

show("author vs committer timestamps, every commit",
     "log", "--format=%s|at=%at|ct=%ct")
show("commits that touch f, no filter",
     "log", "--format=%s", "--", "f")
show("--diff-filter=A on f: commits that add f",
     "log", "--diff-filter=A", "--format=%s", "--", "f")
show("--diff-filter=D on f: commits that delete f",
     "log", "--diff-filter=D", "--format=%s", "--", "f")
show("--diff-filter=A with no path",
     "log", "--diff-filter=A", "--format=%s")
show("%at of the add commits on f",
     "log", "--diff-filter=A", "--format=%at", "--", "f")
show("%ct of the add commits on f",
     "log", "--diff-filter=A", "--format=%ct", "--", "f")
