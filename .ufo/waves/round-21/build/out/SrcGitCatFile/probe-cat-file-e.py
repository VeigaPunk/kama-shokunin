#!/usr/bin/env python3
"""Probe git cat-file -e / -t exit codes for existing, absent and peeled objects.

Builds a scratch repo under /tmp/kama-r21-SrcGitCatFile/exp, prints a table, and writes the
same table to probe-cat-file-e.out next to this script. Uses only git plumbing.
"""
import pathlib, shutil, subprocess

BASE = pathlib.Path("/tmp/kama-r21-SrcGitCatFile/exp")
OUT = pathlib.Path(__file__).with_name("probe-cat-file-e.out")


def git(*args):
    p = subprocess.run(["git", *args], cwd=BASE, capture_output=True, text=True)
    return p.returncode, p.stdout.strip(), p.stderr.strip().replace("\n", " / ")


def ident(*args):
    return git("-c", "user.name=t", "-c", "user.email=t@example.invalid",
               "-c", "commit.gpgsign=false", *args)


def main():
    if BASE.exists():
        shutil.rmtree(BASE)
    BASE.mkdir(parents=True)
    lines = []

    def emit(s=""):
        print(s)
        lines.append(s)

    emit("git --version: " + subprocess.run(["git", "--version"], capture_output=True, text=True).stdout.strip())
    git("init", "-q", "-b", "main")
    (BASE / "f").write_text("hello\n"); git("add", "f"); ident("commit", "-qm", "c1")
    (BASE / "g").write_text("world\n"); git("add", "g"); ident("commit", "-qm", "c2")
    ident("tag", "-a", "-m", "annot", "v1", "HEAD~1")
    git("tag", "lt", "HEAD~1")
    rev = lambda s: git("rev-parse", s)[1]
    commit, parent, tree, blob, tag = rev("HEAD"), rev("HEAD~1"), rev("HEAD^{tree}"), rev("HEAD:f"), rev("v1")
    missing40 = "0123456789abcdef0123456789abcdef01234567"
    missing7 = "0123456"
    short = commit[:7]
    emit(f"objects: commit={commit} parent={parent} tree={tree} blob={blob} annotated-tag={tag}")
    cases = [
        ("commit", commit), ("commit^{commit}", commit + "^{commit}"), ("commit^{tree}", commit + "^{tree}"),
        ("tree", tree), ("tree^{commit}", tree + "^{commit}"),
        ("blob", blob), ("blob^{commit}", blob + "^{commit}"),
        ("annotated tag", tag), ("annotated tag^{commit}", tag + "^{commit}"),
        ("v1^{commit}", "v1^{commit}"), ("v1 (tag ref)", "v1"), ("lt (lightweight ref)", "lt"),
        ("missing 40-hex", missing40), ("missing 40-hex^{commit}", missing40 + "^{commit}"),
        ("missing 7-hex", missing7), ("short commit 7-hex", short), ("short commit^{commit}", short + "^{commit}"),
        ("nonexistent ref", "nosuchref"), ("non-hex token", "zzz"),
    ]
    emit("label [token] | -e rc | -e stderr | -t rc | -t stdout-or-stderr")
    for label, tok in cases:
        erc, _, eerr = git("cat-file", "-e", tok)
        trc, tout, terr = git("cat-file", "-t", tok)
        emit(f"{label} [{tok}] | {erc} | {eerr or '-'} | {trc} | {tout or terr or '-'}")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    emit(f"transcript written: {OUT}")


if __name__ == "__main__":
    main()
