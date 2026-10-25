#!/usr/bin/env python3
"""R42B05 reproducers for tools/digest-ledger.py defect claims.

Every case prints: setup, command, rc, stdout, stderr, and the docstring-based
expectation. Fixtures live under the seat; nothing outside the seat is written.
"""
import hashlib
import importlib.util
import os
import re
import shutil
import subprocess
import sys

TOOL = "/fast/scratch/kama-r42/clone/tools/digest-ledger.py"
COUNTER = "/fast/scratch/kama-r42/clone/tools/round42-digest-audit.py"
SEAT = "/fast/scratch/kama-r42/seats/R42B05"
FIX = os.path.join(SEAT, "fixtures")
TMP = os.path.join(SEAT, "tmp")
ENV = dict(os.environ, TMPDIR=TMP)

TOKEN_DOCSTRING_OK = re.compile(r"(?<![0-9a-fA-F])[0-9a-f]{64}(?![0-9a-fA-F])")


def sh(*args, cwd=None):
    p = subprocess.run(args, cwd=cwd, env=ENV, capture_output=True)
    return p.returncode, p.stdout, p.stderr


def git(D, *args):
    rc, out, err = sh("git", "-C", D, *args)
    if rc != 0:
        raise RuntimeError(f"git -C {D} {' '.join(args)}: {err.decode(errors='replace')}")
    return out


def fixture(name):
    D = os.path.join(FIX, name)
    shutil.rmtree(D, ignore_errors=True)
    os.makedirs(D)
    git(D, "-c", "init.defaultBranch=main", "init", "-q")
    top = git(D, "rev-parse", "--show-toplevel").decode().strip()
    assert os.path.realpath(top) == os.path.realpath(D), (top, D)
    return D


def commit(D, msg="x", add=True):
    if add:
        git(D, "add", "-A")
    git(D, "-c", "user.name=R42B05", "-c", "user.email=r42b05@seat.local", "commit", "-q", "-m", msg)


def w(D, rel, data):
    p = os.path.join(D, rel)
    d = os.path.dirname(p)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(p, "wb" if isinstance(data, bytes) else "w") as f:
        f.write(data)


def ledger(D, rows, crlf=False, trailing_nl=1):
    body = "digest\tclass\tsubject\tpath\tcorrect\tverified-at\tnote\n"
    body += "".join(r + "\n" for r in rows)
    body += "\n" * trailing_nl
    if crlf:
        body = body.replace("\n", "\r\n")
    w(D, "registry/digest-ledger.tsv", body)


def scan(*args, cwd=None):
    rc, out, err = sh(sys.executable, TOOL, "scan", *args, cwd=cwd)
    return rc, out.decode(errors="replace").strip(), err.decode(errors="replace").strip()


def show(name, rc, out, err="", note=""):
    print(f"### {name}")
    if note:
        print(f"expectation: {note}")
    print(f"rc={rc}")
    print(f"stdout: {out}")
    if err:
        print(f"stderr: {err[:400]}")
    print()


def hexd(b):
    return hashlib.sha256(b).hexdigest()


def case_adjacency():
    D = fixture("adjacency")
    good = hexd(b"alpha\n")
    good2 = hexd(b"beta\n")
    good3 = hexd(b"gamma\n")
    good4 = hexd(b"delta\n")
    good5 = hexd(b"epsilon\n")
    w(D, "alpha.bin", "alpha\n")
    # 128-char mixed-case run: 64 uppercase + 64 lowercase (good is inside it)
    # 65-char run: 64 lowercase + trailing uppercase 'F'
    # control: pure-lowercase 128-char run (two concatenated digests)
    # control: plain 64-char token
    w(D, "doc.md", f"{'A' * 64}{good}\n{good2}F\n{good4}{good5}\nctl {good3}\n")
    rc, out, err = scan("--dir", D)
    show("adjacency: mixed-case hex runs (dir mode)", rc, out, err,
         "docstring: token = 64 lower-hex NOT adjacent to another hex character; "
         "'A' and 'F' are hex characters, so expected tokens = {good3} only (tokens=1). "
         "Pure-lowercase 128-run must yield nothing (both regexes agree).")
    corrected = sorted(set(TOKEN_DOCSTRING_OK.findall(f"{'A' * 64}{good}\n{good2}F\n{good4}{good5}\nctl {good3}\n")))
    print(f"docstring-correct regex tokens: {corrected}")
    print()


def case_uppercase_cite():
    D = fixture("uppercase")
    good = hexd(b"alpha\n")
    w(D, "alpha.bin", "alpha\n")
    w(D, "doc.md", f"cite {good.upper()}\n")
    ledger(D, [f"{good.upper()}\tunverifiable\ts\t\t\t\twhy"])
    commit(D)
    rc, out, err = scan("--repo", D, "--rev", "HEAD")
    show("uppercase cited digest (git mode)", rc, out, err,
         "docstring purpose: 'find every full SHA-256 the lane's documents cite'. "
         "A full SHA-256 cited in uppercase is invisible: tokens=0, exit 0 (all clear) "
         "although the cite is unexplained; the uppercase ledger row is dead too.")
    print()


def case_split_and_wrapped():
    D = fixture("split")
    good = hexd(b"alpha\n")
    good2 = hexd(b"beta\n")
    good3 = hexd(b"gamma\n")
    unk = "ab" * 32
    w(D, "alpha.bin", "alpha\n")
    # line1+2: the 64-hex digest good hard-wrapped 32/32 (missed)
    # line3+4: one 128-hex value unk||good2 hard-wrapped 64/64 (two phantom tokens)
    # line5: intact control
    w(D, "doc.md", f"{good[:32]}\n{good[32:]}\n{unk}\n{good2}\nctl {good3}\n")
    rc, out, err = scan("--dir", D)
    show("split/wrapped hex across lines (dir mode)", rc, out, err,
         "the 32/32-wrapped digest good is never counted (cite missed); the 128-hex "
         "value unk||good2 wrapped 64/64 is reported as TWO independent digests "
         "(phantom tokens unk and good2, both unexplained). Control good3 is counted.")
    print()


def case_overlength():
    D = fixture("overlength")
    real = hexd(b"alpha\n")
    bad65 = real[:8] + "e8423a3b1b99d4e3b8d8c6271f7a4f4c96d3a5ad4e0a85a991ce234ff"[:57]
    assert len(bad65) == 65
    w(D, "alpha.bin", "alpha\n")
    w(D, "doc.md", f"package sha256 `{bad65}` (65 hex chars)\n")
    ledger(D, [f"{real}\texternal\ts\t\t\t\tthe real 64-char digest"])
    rc, out, err = scan("--dir", D)
    show("over-length (65-char) cited digest (dir mode)", rc, out, err,
         "the doc cites a 65-hex-char value as a sha256; the exact-64 token regex "
         "cannot see it: tokens=0, exit 0 — a cited digest that hashes nothing is "
         "silently invisible. Live instance: corpus/lessons/round-38.md:51.")


def case_encoding():
    D = fixture("encoding")
    good = hexd(b"alpha\n")
    w(D, "alpha.bin", "alpha\n")
    w(D, "bin.md", b"\x00\xca\xfe binary \xff prefix " + good.encode() + b" \x80 suffix\n")
    rc, out, err = scan("--dir", D)
    show("binary .md with intact ASCII digest (control, dir mode)", rc, out, err,
         "binary content does not crash the scan; the ASCII digest is found (OK).")
    D2 = fixture("utf16-only")
    w(D2, "alpha.bin", "alpha\n")
    w(D2, "utf16.md", f"cite {good}\n".encode("utf-16"))
    rc2, out2, err2 = scan("--dir", D2)
    show("UTF-16-encoded .md citing the digest (dir mode)", rc2, out2, err2,
         "every ASCII char is NUL-interleaved -> no 64-hex run survives -> the cited "
         "digest is invisible: tokens=0, exit 0 (silent miss).")
    print()


def case_symlink():
    D = fixture("symlink")
    unk = "cd" * 32
    good = hexd(b"alpha\n")
    w(D, "alpha.bin", "alpha\n")
    outside = os.path.join(FIX, "symlink-outside")
    os.makedirs(outside, exist_ok=True)
    w(outside, f"{unk}.bin", "outside\n")
    os.symlink(f"../outside/{unk}.bin", os.path.join(D, "link.md"))
    w(D, "doc.md", "no digests here\n")
    commit(D)
    rcg, outg, errg = scan("--repo", D, "--rev", "HEAD")
    show("symlink doc: git mode", rcg, outg, errg,
         "link.md is a symlink to ../outside/<unk>.bin; the link TEXT contains the "
         "64-hex unk. git mode scans the link text as if it were document content: "
         "phantom token unk -> unknown=1 exit 1 (false positive).")
    rcd, outd, errd = scan("--dir", D)
    show("symlink doc: dir mode", rcd, outd, errd,
         "dir mode skips symlinks entirely: tokens=0 exit 0. Same tree, opposite verdicts.")
    # symlinked ledger
    D2 = fixture("symlink-ledger")
    w(D2, "alpha.bin", "alpha\n")
    w(D2, "doc.md", f"cite {unk}\n")
    w(D2, "registry/real-ledger.tsv", f"{unk}\tunverifiable\ts\t\t\t\twhy\n")
    os.symlink("real-ledger.tsv", os.path.join(D2, "registry", "digest-ledger.tsv"))
    commit(D2)
    rcg2, outg2, _ = scan("--repo", D2, "--rev", "HEAD")
    rcd2, outd2, _ = scan("--dir", D2)
    show("symlinked ledger: git mode", rcg2, outg2,
         note="git mode cat-file -p of the symlink prints the link text 'real-ledger.tsv', "
              "which parse_ledger turns into a dead row; the real ledger is ignored -> "
              "cited unk falls to unknown (exit 1) even though a ledger row explains it.")
    show("symlinked ledger: dir mode", rcd2, outd2,
         note="dir mode skips the symlinked ledger (islink) -> ledger empty; and the real "
              "ledger file registry/real-ledger.tsv is scanned as a DOC, so its digest "
              "column leaks in as a token. Either way the ledger is not honored.")
    print()


def case_partial_clone():
    O = fixture("partial-origin")
    sha_b = hexd(b"beta\n")
    w(O, "b.bin", "beta\n")
    w(O, "a.md", f"cite {sha_b}\n")
    commit(O, "c1")
    w(O, "a.md", f"cite {sha_b} twice {sha_b}\n")
    commit(O, "c2")
    git(O, "config", "uploadpack.allowFilter", "true")
    part = os.path.join(FIX, "partial1")
    shutil.rmtree(part, ignore_errors=True)
    git(O, "clone", "-q", "--filter=blob:none", "--no-checkout", "--no-local",
        f"file://{O}", part)
    # prove the clone is truly partial: the cited blob must be absent
    rc_e, _, _ = sh("git", "-C", part, "cat-file", "-e", sha_b)
    print(f"partiality check: git cat-file -e <blob> rc={rc_e} (nonzero = blob absent = truly partial)")
    assert rc_e != 0, "clone was not partial; test invalid"
    before = git(part, "count-objects", "-v").decode()
    rc, out, err = scan("--repo", part, "--rev", "HEAD")
    after = git(part, "count-objects", "-v").decode()
    show("partial clone (blob:none): scan with reachable promisor remote", rc, out, err,
         "docstring: 'Read-only: it reads git objects and files and writes nothing.' "
         "If cat-file --batch lazily fetches, objects are WRITTEN into the scanned repo.")
    print("count-objects -v before:")
    print(before.strip())
    print("count-objects -v after:")
    print(after.strip())
    print("before==after:", before == after)
    print()
    part2 = os.path.join(FIX, "partial2")
    shutil.rmtree(part2, ignore_errors=True)
    git(O, "clone", "-q", "--filter=blob:none", "--no-checkout", "--no-local",
        f"file://{O}", part2)
    git(part2, "remote", "remove", "origin")
    rc2, out2, err2 = scan("--repo", part2, "--rev", "HEAD")
    show("partial clone: scan with no reachable promisor remote", rc2, out2, err2,
         "offline partial clone: cat-file --batch cannot fetch; expect either a crash "
         "(exit 2) or a wrong summary. Record what happens.")
    print()


def case_shallow_control():
    O = os.path.join(FIX, "partial-origin")
    shal = os.path.join(FIX, "shallow")
    shutil.rmtree(shal, ignore_errors=True)
    git(O, "clone", "-q", "--depth", "1", "--no-local", f"file://{O}", shal)
    rc, out, err = scan("--repo", shal, "--rev", "HEAD")
    show("shallow clone (control, expect clean pass)", rc, out, err,
         "depth-1 clone has all HEAD objects locally; expect normal summary, exit 0.")
    print()


def peak_rss(args, cwd=None):
    code = (
        "import subprocess,resource,sys\n"
        f"p=subprocess.run({args!r},capture_output=True,cwd={cwd!r})\n"
        "print(p.returncode)\n"
        "print(p.stdout.decode(errors='replace').strip())\n"
        "print(resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss)\n"
    )
    rc, out, err = sh(sys.executable, "-c", code)
    lines = out.decode().strip().split("\n")
    return lines[0], lines[1], lines[2], err.decode(errors="replace")[:200]


def case_memory():
    small = fixture("mem-small")
    w(small, "a.md", "tiny doc\n")
    w(small, "small.bin", "x\n")
    commit(small)
    big = fixture("mem-big")
    w(big, "a.md", "tiny doc\n")
    with open(os.path.join(big, "big.bin"), "wb") as f:
        chunk = b"\0" * (1 << 24)
        for _ in range(32):  # 256 MiB
            f.write(chunk)
    commit(big)
    bigdir = os.path.join(FIX, "mem-dir")
    shutil.rmtree(bigdir, ignore_errors=True)
    shutil.copytree(big, bigdir, ignore=shutil.ignore_patterns(".git"))
    print("### memory: git mode, small repo (baseline)")
    rc, out, rss, err = peak_rss([sys.executable, TOOL, "scan", "--repo", small, "--rev", "HEAD"])
    print(f"rc={rc} peak_rss_kib={rss}")
    print(f"stdout: {out}")
    print()
    print("### memory: git mode, repo containing a 256 MiB blob")
    rc, out, rss, err = peak_rss([sys.executable, TOOL, "scan", "--repo", big, "--rev", "HEAD"])
    print(f"rc={rc} peak_rss_kib={rss}")
    print(f"stdout: {out}")
    if err:
        print(f"stderr: {err}")
    print()
    print("### memory: dir mode over a directory containing the 256 MiB file")
    rc, out, rss, err = peak_rss([sys.executable, TOOL, "scan", "--dir", bigdir])
    print(f"rc={rc} peak_rss_kib={rss}")
    print(f"stdout: {out}")
    print()


def case_ledger_duplicates():
    unk = "ab" * 32
    badcorrect = "ef" * 32
    for order in ("bad-first", "good-first"):
        D = fixture(f"dup-{order}")
        w(D, "alpha.bin", "alpha\n")
        w(D, "doc.md", f"cite {unk}\n")
        bad = f"{unk}\twrong\ts\t\t{badcorrect}\t\t"      # correct not in blob set -> ledger_bad
        goodrow = f"{unk}\tunverifiable\ts\t\t\t\twhy"    # valid row
        rows = [bad, goodrow] if order == "bad-first" else [goodrow, bad]
        ledger(D, rows)
        rc, out, err = scan("--dir", D)
        show(f"duplicate ledger digest, {order} (dir mode)", rc, out, err,
             "parse_ledger keys rows by digest with last-wins; the two rows disagree "
             "(one would be ledger_bad, one unverifiable). Verdict depends on row order; "
             "the bad row is silently dropped when it comes first.")


def case_ledger_crlf_blank():
    unk = "ab" * 32
    D = fixture("crlf-ok")
    w(D, "alpha.bin", "alpha\n")
    w(D, "doc.md", f"cite {unk}\n")
    ledger(D, [f"{unk}\tunverifiable\ts\t\t\t\twhy"], crlf=True, trailing_nl=3)
    rc, out, err = scan("--dir", D)
    show("well-formed CRLF ledger + trailing blank lines (control)", rc, out, err,
         "expect identical to the LF equivalent: unverifiable=1, exit 0.")
    D2 = fixture("crlf-digestonly")
    w(D2, "alpha.bin", "alpha\n")
    w(D2, "doc.md", f"cite {unk}\n")
    ledger(D2, [unk], crlf=True)  # digest-only row, CRLF
    rc2, out2, err2 = scan("--dir", D2)
    show("CRLF digest-only ledger row", rc2, out2, err2,
         "the row key becomes '<unk>\\r' and never matches the token -> unknown=1; "
         "the same row with LF is at least keyed (class '' -> ledger_bad). Either way "
         "the malformed row is tolerated silently, but CRLF changes the class.")
    D3 = fixture("crlf-truncated")
    ext = hexd(b"external\n")
    w(D3, "alpha.bin", "alpha\n")
    ev = os.path.join(FIX, "crlf-evidence.bin")
    w(FIX, "crlf-evidence.bin", "external\n")
    w(D3, "doc.md", f"cite {ext}\n")
    body = "digest\tclass\tsubject\tpath\tcorrect\tverified-at\tnote\n" + \
        f"{ext}\texternal\ts\t{ev}\r\n"
    w(D3, "registry/digest-ledger.tsv", body)
    rc3, out3, err3 = scan("--dir", D3)
    show("CRLF truncated row with absolute path as last column", rc3, out3, err3,
         "path becomes '<abs>\\r' -> isfile False -> external_absent; the same row with "
         "LF is external_ok (next case). Only the line ending differs.")
    body_lf = "digest\tclass\tsubject\tpath\tcorrect\tverified-at\tnote\n" + \
        f"{ext}\texternal\ts\t{ev}\n"
    w(D3, "registry/digest-ledger.tsv", body_lf)
    rc4, out4, err4 = scan("--dir", D3)
    show("LF control: same truncated row, LF ending", rc4, out4, err4,
         "external_ok expected, exit 0.")
    print()


def case_external_cwd():
    ext = hexd(b"external\n")
    D = fixture("external-cwd")
    w(D, "alpha.bin", "alpha\n")
    # evidence lives OUTSIDE the scanned dir, so the ledger row is the only path to it
    w(FIX, "evidence.bin", "external\n")
    w(D, "doc.md", f"cite {ext}\n")
    ledger(D, [f"{ext}\texternal\ts\tevidence.bin\t\t\t"])
    rc1, out1, _ = scan("--dir", D, cwd=FIX)
    rc2, out2, _ = scan("--dir", D, cwd=SEAT)
    show("external row with relative path, cwd=where the file is", rc1, out1,
         note="path resolves against the process CWD: with CWD=FIX the row is external_ok.")
    show("external row with relative path, cwd one directory up", rc2, out2,
         note="same bytes, same ledger, CWD=SEAT: the row degrades to external_absent and the exit flips.")


def case_nonutf8_path():
    D = fixture("nonutf8-path")
    good = hexd(b"alpha\n")
    w(D, "alpha.bin", "alpha\n")
    with open(os.path.join(os.fsencode(D), b"caf\xe9.md"), "wb") as f:
        f.write(f"cite {good}\n".encode())
    commit(D)
    rc, out, err = scan("--repo", D, "--rev", "HEAD")
    show("tracked path with invalid UTF-8: git mode", rc, out, err,
         "rev-list/ls-tree output is decoded strictly -> UnicodeDecodeError (a ValueError "
         "subclass) -> exit 2 'usage or git error': the tool cannot scan the repo at all.")
    Dd = os.path.join(FIX, "nonutf8-dir")
    shutil.rmtree(Dd, ignore_errors=True)
    shutil.copytree(D, Dd, ignore=shutil.ignore_patterns(".git"))
    rc2, out2, err2 = scan("--dir", Dd)
    show("same tree: dir mode", rc2, out2, err2,
         "dir mode tolerates the name (surrogateescape) and finds the token.")
    spec = importlib.util.spec_from_file_location("audit", COUNTER)
    audit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit)
    code = (
        "import importlib.util,sys\n"
        f"spec=importlib.util.spec_from_file_location('audit',{COUNTER!r})\n"
        "audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)\n"
        "try:\n"
        f"    print(audit.ref_git({D!r},'HEAD'))\n"
        "except Exception as e:\n"
        "    print(type(e).__name__, e)\n"
        "    sys.exit(9)\n"
    )
    rc3, out3, err3 = sh(sys.executable, "-c", code)
    show("counter reference ref_git on the same repo", rc3, out3.decode(errors='replace'), err3.decode(errors='replace')[:300],
         "the C2 counter's reference implementation decodes strictly and does not catch "
         "UnicodeDecodeError: it dies with a traceback (exit 9 here) where the tool at "
         "least exits 2. The live leg would abort, not gracefully fail.")


def case_gitlink():
    D = fixture("gitlink")
    good = hexd(b"alpha\n")
    w(D, "alpha.bin", "alpha\n")
    w(D, "doc.md", f"cite {good}\n")
    commit(D)
    fake = "0123456789012345678901234567890123456789"
    git(D, "update-index", "--add", "--cacheinfo", f"160000,{fake},notes.md")
    commit(D, "gitlink", add=False)
    rc, out, err = scan("--repo", D, "--rev", "HEAD")
    show("tracked gitlink named notes.md (submodule-style path)", rc, out, err,
         "ls-tree -r lists notes.md; is_doc() is true; cat-file -p of a gitlink path "
         "either errors (exit 2) or prints something odd. Record behavior.")


def case_counter_blindness():
    D = os.path.join(FIX, "adjacency")
    spec = importlib.util.spec_from_file_location("audit", COUNTER)
    audit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit)
    n = audit.ref_dir(D)
    print("### counter-blindness: ref_dir on the adjacency fixture")
    print(f"counter reference summary: {audit.summary(n)} exit={audit.exit_of(n)}")
    print("the counter's contract leg compares the tool against THIS reference; it shares "
          "the token regex and parse_ledger with the tool, so it reproduces the same "
          "false token and the contract leg would pass (contract=1) despite the defect.")
    print()


def main():
    os.makedirs(TMP, exist_ok=True)
    all_cases = {
        "adjacency": case_adjacency,
        "uppercase": case_uppercase_cite,
        "split": case_split_and_wrapped,
        "overlength": case_overlength,
        "encoding": case_encoding,
        "symlink": case_symlink,
        "partial": case_partial_clone,
        "shallow": case_shallow_control,
        "memory": case_memory,
        "duplicates": case_ledger_duplicates,
        "crlf": case_ledger_crlf_blank,
        "external_cwd": case_external_cwd,
        "nonutf8_path": case_nonutf8_path,
        "gitlink": case_gitlink,
        "counter_blindness": case_counter_blindness,
    }
    wanted = sys.argv[1:] or list(all_cases)
    for name in wanted:
        all_cases[name]()


if __name__ == "__main__":
    main()
