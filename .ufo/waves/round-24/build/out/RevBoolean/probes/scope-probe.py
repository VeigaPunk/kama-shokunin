#!/usr/bin/env python3
"""Bounded offline probe #5: remaining classification inputs.

(a) remote.<name>.partialclonefilter with an empty value and with a valueless
    key (git_config_string requires a value -> unusable repository).
(b) whether `git config --null --list` sees worktree config
    (.git/config.worktree, enabled by extensions.worktreeConfig) and included
    files (include.path), because the audit must classify the same set of
    config files git does.
"""
import os
import shutil
import subprocess
from pathlib import Path

BASE = Path("/fast/scratch/hyaku/kama-r24/RevBoolean")
FIX = BASE / "fixtures" / "scope"
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")


def run(repo, *args, stdin=None):
    p = subprocess.run(["git", "-C", str(repo), *args],
                       input=None if stdin is None else stdin.encode(),
                       capture_output=True, env=ENV, timeout=30)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")


def make(name, files):
    repo = FIX / name
    if repo.exists():
        shutil.rmtree(repo)
    repo.mkdir(parents=True)
    run(repo, "init", "-q")
    for rel, body in files.items():
        p = repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body)
    return repo


print("=== (a) partialclonefilter value forms ===")
for label, body in [
        ("filter empty value", '[remote "origin"]\n\turl = file:///nowhere\n\tpartialclonefilter =\n'),
        ("filter valueless", '[remote "origin"]\n\turl = file:///nowhere\n\tpartialclonefilter\n'),
        ("filter blob:none", '[remote "origin"]\n\turl = file:///nowhere\n\tpartialclonefilter = blob:none\n'),
        ("filter quoted", '[remote "origin"]\n\turl = file:///nowhere\n\tpartialclonefilter = "blob:none"\n')]:
    repo = make("f-" + label.replace(" ", "-").replace(":", ""),
                {".git/config": body})
    rc, out, err = run(repo, "config", "--null", "--list")
    rc2, _, err2 = run(repo, "rev-parse", "--show-object-format")
    print(f"  {label:22} list_rc={rc} list={out!r} git_rc={rc2} err={err2.strip()[:70]}")

print("\n=== (b) config scopes seen by `git config --null --list` ===")
repo = make("scopes", {
    ".git/config": '[core]\n\trepositoryformatversion = 0\n'
                   '[extensions]\n\tworktreeConfig = true\n'
                   '[include]\n\tpath = included.conf\n'
                   '[remote "origin"]\n\turl = file:///nowhere\n\tpromisor = false\n',
    ".git/config.worktree": '[remote "wt"]\n\tpromisor = true\n',
    ".git/included.conf": '[remote "frominclude"]\n\tpromisor = true\n',
})
rc, out, err = run(repo, "config", "--null", "--list")
print("  --null --list:", repr(out))
rc, out, err = run(repo, "rev-parse", "--show-object-format")
print("  git usable:", rc, err.strip()[:60])
