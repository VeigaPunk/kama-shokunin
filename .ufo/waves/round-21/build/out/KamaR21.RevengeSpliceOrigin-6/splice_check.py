#!/usr/bin/env python3
"""Read-only re-derivation of the round-20 report token splice (RevengeSpliceOrigin).

Checks: (1) the token is not a git object in lane or fleet; (2) every two-part splice
TOKEN[:k] (from object A) + TOKEN[k:] (from object B) over all object names in both repos;
(3) the position facts used in the report. Exit 0 iff the expected facts hold.
"""
import subprocess
import sys

TOKEN = "0957ce619789d13d894ef21bc863486bcb35b56c"
A = "0957ce619789d13bb5779606078fa1498114d2c7"  # measured tree (lane commit 0957ce61)
B = "33a6777866d0f63d894ef21bc863486bcb35b56c"  # work/frozen-population commit (lane 33a67778)
REPOS = {
    "lane": "/home/vgpnk/Projects/shokunin/kama-shokunin",
    "fleet": "/home/vgpnk/Projects/shokunin",
}


def git(repo, *args):
    p = subprocess.run(["git", "--no-pager", "-C", repo, *args], capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def main():
    ok = True
    names = {}
    for name, repo in REPOS.items():
        rc, out, err = git(repo, "cat-file", "--batch-all-objects", "--batch-check=%(objectname) %(objecttype)")
        if rc != 0:
            print(f"{name}: cat-file --batch-all-objects rc={rc} {err.strip()}")
            return 2
        rows = [line.split() for line in out.splitlines()]
        names[name] = [r[0] for r in rows if len(r) == 2 and len(r[0]) == 40]
        rc_t, _, _ = git(repo, "cat-file", "-t", TOKEN)
        print(f"{name}: 40-hex objects={len(names[name])} git cat-file -t TOKEN rc={rc_t} (128 = not an object)")
        ok = ok and rc_t != 0
    pairs = []
    for name, lst in names.items():
        for k in range(1, 40):
            pre, suf = TOKEN[:k], TOKEN[k:]
            heads = [h for h in lst if h.startswith(pre)]
            tails = [h for h in lst if h.endswith(suf)]
            pairs += [(name, k, a, b) for a in heads for b in tails if a != b]
    for p in pairs:
        print("two-part splice:", p)
    expected = {("lane", 14, A, B), ("lane", 15, A, B)}
    ok = ok and set(pairs) == expected
    print("A[:15]+B[15:] == TOKEN:", A[:15] + B[15:] == TOKEN)
    print("A[:16] == TOKEN[:16]:", A[:16] == TOKEN[:16], "| A[15]=%s B[15]=%s TOKEN[15]=%s" % (A[15], B[15], TOKEN[15]))
    print("A[14]=%s B[14]=%s (shared character at the splice point)" % (A[14], B[14]))
    print("B[-25:] == TOKEN[15:]:", B[-25:] == TOKEN[15:], "| len(TOKEN[15:])=%d" % len(TOKEN[15:]))
    ok = ok and A[:15] + B[15:] == TOKEN and A[:16] != TOKEN[:16]
    print("RESULT", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
