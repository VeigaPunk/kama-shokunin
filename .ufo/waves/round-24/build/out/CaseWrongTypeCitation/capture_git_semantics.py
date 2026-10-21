#!/usr/bin/env python3
"""Capture the git-level evidence that separates 'present but wrong type'
from 'absent' for case C-WT1.  Writes git-semantics.txt next to itself.

The two states are distinguishable without any network access:
  present blob   cat-file -t           -> blob
                 cat-file --batch-check -> "<sha> blob <size>"       (exists)
  peeled to commit
                 cat-file --batch-check -> "<sha>^{commit} missing"  (stdout, rc=0)
                 stderr                 -> "expected commit type, but the
                                              object dereferences to blob type"
  absent object  cat-file --batch-check -> "<sha>^{commit} missing"  (stdout, rc=0)
                 stderr                 -> (nothing)
"""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = Path("/fast/scratch/hyaku/kama-r24/CaseWrongTypeCitation/run/lane-full")
ABSENT = "0" * 40


def env():
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
    return e


def run(*args, data=None):
    p = subprocess.run(["git", "-C", str(ROOT), *args],
                       input=None if data is None else data.encode(),
                       capture_output=True, env=env())
    return p.returncode, p.stdout.decode(errors="replace"), \
        p.stderr.decode(errors="replace")


def main():
    rc, blob, _ = run("rev-parse", "HEAD:f")
    blob = blob.strip()
    lines = [f"# git semantics for case C-WT1 (blob {blob})",
             f"# git {run('--version')[1].strip()}", ""]
    for label, args, data in (
            ("cat-file -t <blob>", ("cat-file", "-t", blob), None),
            ("cat-file --batch-check <<< <blob>",
             ("cat-file", "--batch-check"), blob + "\n"),
            ("cat-file --batch-check <<< <blob>^{commit}",
             ("cat-file", "--batch-check"), blob + "^{commit}\n"),
            ("rev-parse --verify <blob>^{commit}",
             ("rev-parse", "--verify", blob + "^{commit}"), None),
            ("cat-file --batch-check <<< <absent>^{commit}",
             ("cat-file", "--batch-check"), ABSENT + "^{commit}\n"),
            ("cat-file -e <blob>", ("cat-file", "-e", blob), None),
    ):
        rc, out, err = run(*args, data=data)
        lines.append(f"$ git {' '.join(args)}" + (" <<< ..." if data else ""))
        lines.append(f"rc={rc}")
        if out:
            lines.append("stdout: " + out.rstrip("\n").replace("\n", "\n        "))
        if err:
            lines.append("stderr: " + err.rstrip("\n").replace("\n", "\n        "))
        lines.append("")
    text = "\n".join(lines)
    (HERE / "git-semantics.txt").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    sys.exit(main())
