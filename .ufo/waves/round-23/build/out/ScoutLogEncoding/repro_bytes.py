#!/usr/bin/env python3
"""Byte-level probe: which log placeholders git re-encodes, and to what."""
import os, subprocess, shutil, sys

BASE = "/tmp/kama-r23/ScoutLogEncoding/repro/bytes"
ENV = {"PATH": "/usr/bin:/bin", "HOME": BASE + "/home",
       "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1",
       "LC_ALL": "C.UTF-8"}


def run(args, cwd, inp=None):
    p = subprocess.run(["git", *args], cwd=cwd, input=inp,
                       capture_output=True, env=ENV)
    return p.returncode, p.stdout, p.stderr


def craft(repo, tree, header, subject, author=b"kama-shokunin"):
    body = (b"tree " + tree + b"\n"
            b"author " + author + b" <a@x> 1000 +0000\n"
            b"committer kama-shokunin <a@x> 1000 +0000\n")
    if header is not None:
        body += b"encoding " + header + b"\n"
    body += b"\n" + subject + b"\n"
    rc, out, err = run(["hash-object", "-w", "-t", "commit", "--stdin",
                        "--literally"], repo, body)
    assert rc == 0, (rc, err)
    return out.strip()


def show(repo, sha, fmt, extra):
    rc, out, err = run([*extra, "log", "-1", "--format=" + fmt, sha], repo)
    return rc, out, err.strip()


shutil.rmtree(BASE, ignore_errors=True)
os.makedirs(BASE + "/home")
repo = BASE + "/r"
os.makedirs(repo)
assert run(["init", "-q", "-b", "master"], repo)[0] == 0
open(repo + "/f", "w").write("x\n")
assert run(["add", "f"], repo)[0] == 0
assert run(["-c", "user.name=a", "-c", "user.email=a@x", "commit", "-qm",
            "base"], repo)[0] == 0
tree = run(["rev-parse", "HEAD^{tree}"], repo)[1].strip()

cases = {
    "A-latin1-header-latin1-body":
        (b"ISO-8859-1", b"round-1: na\xefve"),
    "B-noheader-latin1-bytes(invalid utf8)":
        (None, b"round-1: na\xefve"),
    "C-latin1-header-utf8-body(mislabeled)":
        (b"ISO-8859-1", "round-1: naïve".encode()),
    "D-latin1-header-utf8-arrow(mislabeled)":
        (b"ISO-8859-1", "round-1: \u2192".encode()),
    "E-noheader-valid-utf8-arrow":
        (None, "round-1: \u2192".encode()),
    "F-utf8-header-utf8-arrow":
        (b"UTF-8", "round-1: \u2192".encode()),
    "G-bogus-header-ascii":
        (b"X-BOGUS", b"round-1: plain"),
}
shas = {k: craft(repo, tree, h, s) for k, (h, s) in cases.items()}
# author with Latin-1 bytes, ASCII subject, no header
shas["H-noheader-latin1-author"] = craft(
    repo, tree, None, b"round-1: plain", author=b"na\xefve")

configs = {
    "default": [],
    "logOut=UTF-8": ["-c", "i18n.logOutputEncoding=UTF-8"],
    "logOut=ISO-8859-1": ["-c", "i18n.logOutputEncoding=ISO-8859-1"],
    "commitEnc=ISO-8859-1": ["-c", "i18n.commitEncoding=ISO-8859-1"],
}

for name, sha in shas.items():
    print(f"\n=== {name} sha={sha.decode()} ===")
    for cname, extra in configs.items():
        rc_s, subj, e_s = show(repo, sha, "%s", extra)
        rc_a, an, e_a = show(repo, sha, "%an", extra)
        rc_h, h, _ = show(repo, sha, "%H", extra)
        print(f"  [{cname}] rc=%d/%d  %%s=%s  %%an=%s  %%H=%s"
              % (rc_s, rc_a, subj.hex(), an.hex(), h.hex()))
        if e_s or e_a:
            print(f"    stderr_s={e_s!r} stderr_a={e_a!r}")

# All commits in one history: does one bad record poison the whole log?
print("\n=== whole-history log under logOut=ISO-8859-1 ===")
for extra in ([], ["-c", "i18n.logOutputEncoding=ISO-8859-1"]):
    rc, out, err = run([*extra, "log", "--all", "--format=%H %s"], repo)
    print(f"  extra={extra} rc={rc} out_bytes={len(out)} "
          f"first80={out[:80].hex()} stderr={err[:200]!r}")

# Also confirm git log's own error text for invalid conversion inputs.
print("\n=== raw git error samples ===")
for name in ("G-bogus-header-ascii", "F-utf8-header-utf8-arrow"):
    rc, out, err = run(["-c", "i18n.logOutputEncoding=ISO-8859-1", "log", "-1",
                        "--format=%s", shas[name]], repo)
    print(f"  {name} rc={rc} out={out.hex()} err={err!r}")
