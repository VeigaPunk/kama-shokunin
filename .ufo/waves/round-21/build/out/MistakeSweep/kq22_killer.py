#!/usr/bin/env python3
"""MS-04 fix prototype: git-backed killer cases for tools/sources-append-only.py.

usage: kq22_killer.py PATH/TO/sources-append-only.py
Builds throwaway git repos in a temp dir and runs the guard CLI (run_check), the
path the guard's own --selftest never calls. Exit 0 if every case matches the
contract; exit 1 if any case does not (the module under test is killed).
"""
import os
import subprocess
import sys
import tempfile

HEADER = ("| id | source | kind | tier | scope | anchor | teaches | status | "
          "opened | recheck | used-by |")
SEP = "|" + "---|" * 11
ROW = ("| S001 | https://example.org/x | doc | A | scope | sec 1 | {teaches} | "
       "{status} | 2026-10-20 | 90d | — |")


def registry(teaches, status="queued"):
    return ("# SOURCES\n\n## Registry\n\n" + HEADER + "\n" + SEP + "\n"
            + ROW.format(teaches=teaches, status=status) + "\n")


def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], check=True,
                          capture_output=True, text=True).stdout.strip()


def commit(repo, text, message):
    os.makedirs(os.path.join(repo, "corpus"), exist_ok=True)
    with open(os.path.join(repo, "corpus", "SOURCES.md"), "w", encoding="utf-8") as fh:
        fh.write(text)
    git(repo, "add", "corpus/SOURCES.md")
    git(repo, "-c", "user.name=ms", "-c", "user.email=ms@example.invalid",
        "commit", "-q", "-m", message)
    return git(repo, "rev-parse", "HEAD")


def run_guard(module, repo, base, head):
    proc = subprocess.run(
        [sys.executable, module, "--repo", repo, "--from", base, "--to", head],
        capture_output=True, text=True, timeout=60)
    return proc.returncode, proc.stdout


def main(module):
    module = os.path.abspath(module)
    with tempfile.TemporaryDirectory(prefix="ms-killer-") as tmp:
        repo = os.path.join(tmp, "repo")
        os.makedirs(repo)
        git(repo, "init", "-q")
        v1 = commit(repo, registry("Foo"), "v1")
        v_case = commit(repo, registry("foo"), "case-only immutable edit")
        v_real = commit(repo, registry("Bar"), "real immutable edit")
        v_status = commit(repo, registry("Bar", status="mined"), "status-only edit")
        cases = [
            ("case-only immutable edit must exit 1", v1, v_case, 1),
            ("real immutable edit must exit 1", v1, v_real, 1),
            ("status-only edit must exit 0", v_real, v_status, 0),
        ]
        failures = 0
        for name, base, head, want in cases:
            code, _ = run_guard(module, repo, base, head)
            ok = code == want
            failures += not ok
            print(f"{'PASS' if ok else 'FAIL'}: {name} (want {want}, got {code})")
        print(f"{len(cases) - failures}/{len(cases)} killer cases passed")
        return 1 if failures else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: kq22_killer.py PATH/TO/sources-append-only.py", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
