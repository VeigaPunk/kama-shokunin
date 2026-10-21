#!/usr/bin/env python3
"""KamaR21.SrcReproducibleBuildsArchive-6 - does directory-entry order depend on LC_ALL? (stdlib only)

Lists the real install tree read-only and orders its names two ways under each LC_ALL:
  - Python sorted() in a child interpreter (the order kama's C2 digest uses);
  - shell `sort` (the locale-dependent tool the reproducible-builds page warns about).
Exit 0: Python sorted() output is identical under every LC_ALL, equals the C-locale
`sort`, and every child and sort run returned 0. Exit 1: otherwise. Exit 2: the tree
could not be listed. The en_US count of positions where `sort` disagrees with C is an
observation, not a pass criterion.
"""
import json
import os
import pathlib
import subprocess
import sys

TREE = pathlib.Path(os.path.expanduser("~/.local/opt/llama-b11755"))
LOCALES = ["C", "C.utf8", "en_US.utf8"]
CHILD = "import os, sys\nfor n in sorted(os.listdir(sys.argv[1])):\n    print(n)\n"


def child_sorted(loc):
    env = dict(os.environ, LC_ALL=loc)
    p = subprocess.run([sys.executable, "-c", CHILD, str(TREE)],
                       env=env, capture_output=True, text=True)
    return p.returncode, p.stdout.splitlines()


def shell_sort(loc, names):
    env = dict(os.environ, LC_ALL=loc)
    p = subprocess.run(["sort"], input="\n".join(names) + "\n",
                       env=env, capture_output=True, text=True)
    return p.returncode, p.stdout.splitlines()


def main():
    try:
        names = os.listdir(TREE)
    except OSError as e:
        print(f"could not list {TREE}: {e}")
        return 2
    py = {loc: child_sorted(loc) for loc in LOCALES}
    sh = {loc: shell_sort(loc, names) for loc in LOCALES}
    py_out = {loc: v[1] for loc, v in py.items()}
    rc_ok = all(v[0] == 0 for v in py.values()) and all(v[0] == 0 for v in sh.values())
    identical = all(py_out[loc] == py_out["C"] for loc in LOCALES)
    eq_c = py_out["C"] == sh["C"][1]
    count_ok = len(py_out["C"]) == len(names)
    ok = rc_ok and identical and eq_c and count_ok
    diff = [i for i, (a, b) in enumerate(zip(sh["C"][1], sh["en_US.utf8"][1])) if a != b]
    summary = {
        "tree": str(TREE),
        "entries": len(names),
        "all_names_ascii": all(n.isascii() for n in names),
        "child_rc": {loc: py[loc][0] for loc in LOCALES},
        "shell_rc": {loc: sh[loc][0] for loc in LOCALES},
        "python_sorted_identical_across_LC_ALL": identical,
        "python_sorted_equals_shell_sort_C": eq_c,
        "shell_sort_C_equals_C_utf8": sh["C"][1] == sh["C.utf8"][1],
        "shell_sort_en_US_positions_differing_from_C": len(diff),
        "first_en_US_differences_C_vs_en_US": [
            (i, sh["C"][1][i], sh["en_US.utf8"][1][i]) for i in diff[:3]],
        "RESULT": "PASS" if ok else "FAIL",
    }
    print(json.dumps(summary, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
