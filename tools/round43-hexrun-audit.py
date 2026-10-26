#!/usr/bin/env python3
"""round43-hexrun-audit.py - kama round-43 C2 (operability, capability) counter.

Question: does the lane hold a working census of every hex run its documents
cite that is NOT a 64-character digest (git object ids, MD5 sums, over-long or
abbreviated runs), classifying each as a lane object, a hash of a committed
blob, an upstream object whose existence a committed evidence file shows, an
unverifiable citation with its reason, or a flagged wrong citation - so that no
cited run is unexplained? Base: tools/hexrun-census.py does not exist.

Tool contract (frozen before data) - tools/hexrun-census.py:
    hexrun-census.py scan (--repo R --rev REV | --dir DIR) [--ledger FILE] [--details]
    hexrun-census.py selftest
  Documents: git mode - blobs at REV whose path ends .md or .tsv, outside `.ufo/`,
    except registry/hexrun-ledger.tsv and registry/digest-ledger.tsv; dir mode -
    regular files under DIR (symlinks not followed) with the same name rules.
  Token: a maximal run of lower-case hex characters [0-9a-f] of length L with
    32 <= L <= 127 and L != 64, with no [0-9A-Za-z] immediately before or after.
  Counts: tokens = occurrences; distinct = distinct token strings. Each distinct
    token falls in exactly one class, first match wins:
      lane_oid   L == 40 and the object exists in the repository (git mode only)
      md5_blob   L == 32 and equals the MD5 of a regular-file blob (git mode: every
                 blob at REV; dir mode: every regular file under DIR)
      ledger     a row of registry/hexrun-ledger.tsv (at REV, or DIR; --ledger
                 overrides), TAB-separated, header
                 `token class repo evidence correct verified-at note`:
                   upstream      `evidence` is a path of a blob at REV (a file under
                                 DIR) whose bytes contain the token and the `repo`
                                 cell text -> upstream_ok; otherwise ledger_bad
                   unverifiable  `note` has >= 10 characters -> unverifiable; else
                                 ledger_bad
                   wrong         `correct` is a different token-shaped run that
                                 classifies lane_oid, md5_blob or upstream, and
                                 shares its first 8 characters with `token`
                                 -> wrong_flagged; otherwise ledger_bad
                 a duplicated ledger token or an unknown class -> ledger_bad
      unknown    anything else
  Output (one line):
    tokens=T distinct=D lane_oid=A md5_blob=B upstream_ok=C unverifiable=U wrong_flagged=W ledger_bad=L unknown=K
  Exit: 0 when L + K == 0, 1 otherwise, 2 usage or git error. Read-only; it
  leaves nothing in the temporary directory.

Legs (each 0/1):
  tool        tools/hexrun-census.py exists at --tip.
  contract    eleven planted fixtures (built here, expected lines fixed by their
              construction, not by a reference implementation) give the exact
              summary line and exit code. Seed-randomised hex values.
  live        `scan --repo REPO --rev TIP` prints a line with unknown=0 and
              ledger_bad=0, exit 0, and
                distinct and lane_oid equal this counter's own census of the same
                documents (regex plus `git cat-file --batch-check`),
                md5_blob equals the number of distinct 32-runs that match an MD5
                of a blob at TIP, upstream_ok >= UPSTREAM_MIN, and
                unverifiable + wrong_flagged <= UNVERIFIED_MAX.
  hygiene     the scan, run with TMPDIR set to an empty private directory, leaves
              it empty.
  capability  the highest `canonical list as of round N` table of SCORECARD.md
              has a `hexrun-census` row whose evidence cell names
              tools/hexrun-census.py and whose first-working round is 43, and
              tools/capability-repertoire-audit.py at TIP prints `met True`.
met = all five legs 1.

Output: `tool=T contract=C live=L hygiene=H capability=K met=True|False seed=N`
plus `detail:` lines. Exit 0 met, 1 not met, 2 could not evaluate.
"""
from __future__ import annotations

import argparse
import atexit
import hashlib
import os
import random
import re
import shutil
import signal
import subprocess
import sys
import tempfile

UPSTREAM_MIN = 40
UNVERIFIED_MAX = 25
TOKEN_RE = re.compile(r"(?<![0-9A-Za-z])[0-9a-f]{32,127}(?![0-9A-Za-z])")
LEDGERS = ("registry/hexrun-ledger.tsv", "registry/digest-ledger.tsv")
_tmp: list[str] = []


def _cleanup() -> None:
    while _tmp:
        shutil.rmtree(_tmp.pop(), ignore_errors=True)


atexit.register(_cleanup)
signal.signal(signal.SIGTERM, lambda *_: sys.exit(143))


def mk(prefix: str, dir: str | None = None) -> str:
    d = tempfile.mkdtemp(prefix=prefix, dir=dir)
    _tmp.append(d)
    return d


def git(repo: str, *args: str, binary: bool = False, inp: bytes | None = None):
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True, input=inp)
    if p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {p.stderr.decode(errors='replace').strip()}")
    return p.stdout if binary else p.stdout.decode(errors="replace")


def tokens_of(text: str) -> list[str]:
    return [t for t in TOKEN_RE.findall(text) if len(t) != 64]


def doc_path_ok(p: str) -> bool:
    return p.endswith((".md", ".tsv")) and not p.startswith(".ufo/") and p not in LEDGERS


def git_population(repo: str, rev: str):
    files = [p for p in git(repo, "ls-tree", "-r", "--name-only", "-z", rev).split("\0") if p]
    toks: list[str] = []
    for p in files:
        if doc_path_ok(p):
            b = subprocess.run(["git", "-C", repo, "cat-file", "-p", f"{rev}:{p}"], capture_output=True).stdout
            toks += tokens_of(b.decode("utf-8", "replace"))
    return toks


def git_blob_md5s(repo: str, rev: str) -> set[str]:
    out = git(repo, "ls-tree", "-r", "-z", rev)
    shas = []
    for rec in out.split("\0"):
        if not rec:
            continue
        meta, _ = rec.split("\t", 1)
        mode, typ, sha = meta.split()
        if typ == "blob" and mode in ("100644", "100755"):
            shas.append(sha)
    md5s: set[str] = set()
    p = subprocess.Popen(["git", "-C", repo, "cat-file", "--batch"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    assert p.stdin and p.stdout
    import threading

    def feed():
        for s in shas:
            p.stdin.write((s + "\n").encode())
        p.stdin.close()

    th = threading.Thread(target=feed)
    th.start()
    for _ in shas:
        hdr = p.stdout.readline().split()
        size = int(hdr[2])
        data = p.stdout.read(size)
        p.stdout.read(1)
        md5s.add(hashlib.md5(data).hexdigest())
    th.join()
    p.wait()
    return md5s


def own_census(repo: str, rev: str) -> dict:
    toks = git_population(repo, rev)
    distinct = sorted(set(toks))
    oids = [t for t in distinct if len(t) == 40]
    ok = 0
    if oids:
        r = subprocess.run(["git", "-C", repo, "cat-file", "--batch-check"], input="\n".join(oids) + "\n",
                           capture_output=True, text=True)
        ok = sum(1 for l in r.stdout.splitlines() if "missing" not in l)
    md5s = git_blob_md5s(repo, rev)
    m = sum(1 for t in distinct if len(t) == 32 and t in md5s)
    return dict(tokens=len(toks), distinct=len(distinct), lane_oid=ok, md5_blob=m)


def run_tool(export: str, args: list[str], env=None, timeout=300):
    p = subprocess.run([sys.executable, "tools/hexrun-census.py", *args], cwd=export, capture_output=True,
                       text=True, timeout=timeout, env=env)
    return p.stdout.strip(), p.returncode, p.stderr.strip()


def line(**k) -> str:
    d = dict(tokens=0, distinct=0, lane_oid=0, md5_blob=0, upstream_ok=0, unverifiable=0, wrong_flagged=0,
             ledger_bad=0, unknown=0)
    d.update(k)
    return " ".join(f"{a}={b}" for a, b in d.items())


def rhex(rng: random.Random, n: int) -> str:
    return "".join(rng.choice("0123456789abcdef") for _ in range(n))


def w(d: str, rel: str, text: str | bytes) -> None:
    p = os.path.join(d, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "wb" if isinstance(text, bytes) else "w").write(text)


LEDGER_HDR = "token\tclass\trepo\tevidence\tcorrect\tverified-at\tnote\n"


def fixtures(rng: random.Random, export: str):
    """Yield (name, builder(dir)->extra args, want line, want exit)."""
    data = bytes(rng.randrange(256) for _ in range(64))
    md5 = hashlib.md5(data).hexdigest()
    cases = []

    def c(name, build, want, code):
        cases.append((name, build, want, code))

    def f1(d):
        w(d, "data.bin", data)
        w(d, "doc.md", f"cited sum {md5} end\n")
    c("md5-blob", f1, line(tokens=1, distinct=1, md5_blob=1), 0)

    def f2(d):
        w(d, "data.bin", data)
        w(d, "doc.md", f"cited sum {rhex(rng, 32)} end\n")
    c("md5-unknown", f2, line(tokens=1, distinct=1, unknown=1), 1)

    def f3(d):
        w(d, "doc.md", f"over-long {rhex(rng, 65)} and a digest {rhex(rng, 64)} and short {rhex(rng, 31)}\n")
    c("overlong-ignores-64-and-31", f3, line(tokens=1, distinct=1, unknown=1), 1)

    t4 = rhex(rng, 40)

    def f4(d):
        w(d, "doc.md", f"commit {t4}\n")
        w(d, "ev/up.json", f'{{"sha": "{t4}", "repo": "acme/widget"}}\n')
        w(d, "registry/hexrun-ledger.tsv", LEDGER_HDR + f"{t4}\tupstream\tacme/widget\tev/up.json\t\t2026-10-25\tapi 200\n")
    c("upstream-ok", f4, line(tokens=1, distinct=1, upstream_ok=1), 0)

    t5 = rhex(rng, 40)

    def f5(d):
        w(d, "doc.md", f"commit {t5}\n")
        w(d, "ev/up.json", '{"sha": "not-the-token", "repo": "acme/widget"}\n')
        w(d, "registry/hexrun-ledger.tsv", LEDGER_HDR + f"{t5}\tupstream\tacme/widget\tev/up.json\t\t2026-10-25\tapi 200\n")
    c("upstream-evidence-lacks-token", f5, line(tokens=1, distinct=1, ledger_bad=1), 1)

    t6 = rhex(rng, 40)

    def f6(d):
        w(d, "doc.md", f"commit {t6}\n")
        w(d, "registry/hexrun-ledger.tsv", LEDGER_HDR + f"{t6}\tunverifiable\t\t\t\t2026-10-25\tupstream repository deleted\n")
    c("unverifiable-with-note", f6, line(tokens=1, distinct=1, unverifiable=1), 0)

    t7 = rhex(rng, 40)

    def f7(d):
        w(d, "doc.md", f"commit {t7}\n")
        w(d, "registry/hexrun-ledger.tsv", LEDGER_HDR + f"{t7}\tunverifiable\t\t\t\t2026-10-25\tshort\n")
    c("unverifiable-without-reason", f7, line(tokens=1, distinct=1, ledger_bad=1), 1)

    t8 = md5[:8] + rhex(rng, 24)
    if t8 == md5:
        t8 = md5[:8] + "0" * 24

    def f8(d):
        w(d, "data.bin", data)
        w(d, "doc.md", f"sum {t8}\n")
        w(d, "registry/hexrun-ledger.tsv", LEDGER_HDR + f"{t8}\twrong\t\t\t{md5}\t2026-10-25\tprefix-equal typo\n")
    c("wrong-flagged", f8, line(tokens=1, distinct=1, wrong_flagged=1), 0)

    t9 = md5[:8] + rhex(rng, 24)

    def f9(d):
        w(d, "data.bin", data)
        w(d, "doc.md", f"sum {t9}\n")
        w(d, "registry/hexrun-ledger.tsv", LEDGER_HDR + f"{t9}\twrong\t\t\t{rhex(rng, 32)}\t2026-10-25\tbad correction\n")
    c("wrong-correct-unresolved", f9, line(tokens=1, distinct=1, ledger_bad=1), 1)

    t10 = rhex(rng, 40)

    def f10(d):
        w(d, "doc.md", f"UP {t10.upper()} g{t10} {t10}g {rhex(rng, 128)} {t10}\n{t10}\n")
        w(d, ".ufo/hidden.md", f"{rhex(rng, 40)}\n")
        w(d, "note.txt", f"{rhex(rng, 40)}\n")
    c("boundaries-and-exclusions", f10, line(tokens=2, distinct=1, unknown=1), 1)

    def f11(d):
        w(d, "registry/hexrun-ledger.tsv", LEDGER_HDR)
        w(d, "doc.md", f"a {t10} b {t10}\n")
    c("duplicate-token-counts-once", f11, line(tokens=2, distinct=1, unknown=1), 1)
    return cases


def git_fixture(rng: random.Random):
    """Fixture 12/13 in a real repo: a cited earlier commit resolves, a fabricated oid does not."""
    d = mk("r43c2-git-")
    subprocess.run(["git", "-C", d, "init", "-q"], check=True)
    top = subprocess.run(["git", "-C", d, "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
    if os.path.realpath(top) != os.path.realpath(d):
        raise RuntimeError("fixture repo toplevel mismatch")
    ident = ["-c", "user.name=fixture", "-c", "user.email=fixture@invalid"]
    w(d, "a.txt", "one\n")
    subprocess.run(["git", "-C", d, "add", "-A"], check=True)
    subprocess.run(["git", "-C", d, *ident, "commit", "-qm", "first"], check=True, capture_output=True)
    first = subprocess.run(["git", "-C", d, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    fake = rhex(rng, 40)
    w(d, "doc.md", f"resolves {first} and fabricated {fake}\n")
    subprocess.run(["git", "-C", d, "add", "-A"], check=True)
    subprocess.run(["git", "-C", d, *ident, "commit", "-qm", "second"], check=True, capture_output=True)
    return d, line(tokens=2, distinct=2, lane_oid=1, unknown=1), 1


def highest_canonical(text: str):
    best, rows = -1, []
    lines = text.split("\n")
    for i, l in enumerate(lines):
        m = re.search(r"canonical list as of round\s+(\d+)\*\*", l, re.I)
        if m and int(m.group(1)) > best:
            tbl = []
            for ln in lines[i + 1:]:
                if ln.startswith("|"):
                    tbl.append([c.strip() for c in ln.strip().strip("|").split("|")])
                elif tbl:
                    break
            best, rows = int(m.group(1)), tbl[2:]
    return best, rows


def evaluate(repo: str, tip: str, seed: int):
    tip = git(repo, "rev-parse", "--verify", f"{tip}^{{commit}}").strip()
    legs = dict(tool=0, contract=0, live=0, hygiene=0, capability=0)
    d: list[str] = []
    export = mk("r43c2-")
    subprocess.run(["tar", "-x", "-C", export], input=git(repo, "archive", "--format=tar", tip, binary=True), check=True)
    if os.path.isfile(os.path.join(export, "tools/hexrun-census.py")):
        legs["tool"] = 1
    else:
        d.append("detail: tools/hexrun-census.py absent")
    if legs["tool"]:
        rng = random.Random(seed)
        ok = True
        for name, build, want, code in fixtures(rng, export):
            case = mk(f"case-{name}-", export)
            build(case)
            try:
                out, rc, err = run_tool(export, ["scan", "--dir", case])
            except subprocess.TimeoutExpired:
                out, rc, err = "", None, "timeout"
            if out != want or rc != code:
                ok = False
                d.append(f"detail: contract {name}: want exit {code} {want!r}; got exit {rc} {out[:200]!r} {err[:120]}")
        gd, want, code = git_fixture(rng)
        try:
            out, rc, err = run_tool(export, ["scan", "--repo", gd, "--rev", "HEAD"])
        except subprocess.TimeoutExpired:
            out, rc, err = "", None, "timeout"
        if out != want or rc != code:
            ok = False
            d.append(f"detail: contract git-fixture: want exit {code} {want!r}; got exit {rc} {out[:200]!r} {err[:120]}")
        legs["contract"] = int(ok)
        census = own_census(repo, tip)
        try:
            out, rc, err = run_tool(export, ["scan", "--repo", repo, "--rev", tip], timeout=900)
        except subprocess.TimeoutExpired:
            out, rc, err = "", None, "timeout"
        f = dict(re.findall(r"(\w+)=(\d+)", out))
        f = {k: int(v) for k, v in f.items()}
        good = bool(f) and rc == 0 and f.get("unknown") == 0 and f.get("ledger_bad") == 0 \
            and f.get("distinct") == census["distinct"] and f.get("lane_oid") == census["lane_oid"] \
            and f.get("md5_blob") == census["md5_blob"] and f.get("upstream_ok", 0) >= UPSTREAM_MIN \
            and f.get("unverifiable", 99) + f.get("wrong_flagged", 99) <= UNVERIFIED_MAX
        legs["live"] = int(good)
        d.append(f"detail: live reference census {census}; tool exit {rc} {out[:240]!r}" if not good
                 else f"detail: live ok {out} (own census {census})")
    # hygiene
    priv = mk("r43c2-hyg-")
    if legs["tool"]:
        try:
            run_tool(export, ["scan", "--repo", repo, "--rev", tip], env=dict(os.environ, TMPDIR=priv), timeout=900)
        except subprocess.TimeoutExpired:
            d.append("detail: hygiene: timeout")
        left = sorted(os.listdir(priv))
        legs["hygiene"] = int(not left)
        if left:
            d.append(f"detail: hygiene: {len(left)} leaked temp entries: {left[:4]}")
    # capability
    sc = subprocess.run(["git", "-C", repo, "cat-file", "-p", f"{tip}:SCORECARD.md"], capture_output=True, text=True).stdout
    n, rows = highest_canonical(sc)
    row_ok = any(len(r) >= 4 and r[0].strip("` *") == "hexrun-census" and "tools/hexrun-census.py" in r[2]
                 and r[3].strip() == "43" for r in rows)
    aud = os.path.join(export, "tools/capability-repertoire-audit.py")
    aud_ok = False
    if os.path.isfile(aud):
        p = subprocess.run([sys.executable, aud, "--repo", repo, "--tip", tip], capture_output=True, text=True, timeout=120)
        aud_ok = "met True" in p.stdout
    legs["capability"] = int(row_ok and aud_ok)
    if not legs["capability"]:
        d.append(f"detail: capability: canonical list as of round {n}; hexrun-census row ok={row_ok}; repertoire audit met={aud_ok}")
    return tip, legs, d


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--tip", default="HEAD")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--out")
    a = ap.parse_args()
    seed = a.seed if a.seed is not None else random.SystemRandom().randrange(1, 2**31)
    try:
        tip, legs, d = evaluate(os.path.abspath(a.repo), a.tip, seed)
    except (RuntimeError, subprocess.SubprocessError, OSError) as e:
        print(f"could-not-evaluate: {e}", file=sys.stderr)
        return 2
    met = all(legs.values())
    out = "\n".join([f"tip={tip}", "tool={tool} contract={contract} live={live} hygiene={hygiene} capability={capability} "
                     "met={m} seed={s}".format(m=met, s=seed, **legs), *d]) + "\n"
    sys.stdout.write(out)
    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        open(a.out, "w").write(out)
    return 0 if met else 1


if __name__ == "__main__":
    sys.exit(main())
