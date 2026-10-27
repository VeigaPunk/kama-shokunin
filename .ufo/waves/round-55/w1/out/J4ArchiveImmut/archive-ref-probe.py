#!/usr/bin/env python3
"""J4ArchiveImmut unit probe (round-55, lane kama).

Two questions, answered against the FROZEN counter bytes
(kama-shokunin/tools/round54-replay-code-audit.py, sha256 c81fe971...):

  Q1  the scratch path relationship: can the replay the counter launches reach
      the counter's own archive reference S/counter-archive.tar.gz?
  Q2  what does the counter do if that archive vanishes (before it is read,
      and after it is read)?

The frozen counter is imported as a module (read-only) - it is never edited.
"""
import hashlib
import importlib.util
import io
import os
import shutil
import stat
import sys
import tarfile
import tempfile

COUNTER = "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round54-replay-code-audit.py"
OUT = sys.argv[1] if len(sys.argv) > 1 else "-"


def load_counter():
    spec = importlib.util.spec_from_file_location("c1_frozen", COUNTER)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def make_tar(path, members):
    with tarfile.open(path, "w:gz") as tf:
        for name, data in members.items():
            ti = tarfile.TarInfo(name)
            ti.size = len(data)
            tf.addfile(ti, io.BytesIO(data))
    return path


def main():
    m = load_counter()
    lines = []

    def p(s):
        print(s)
        lines.append(s)

    p(f"frozen counter          {COUNTER}")
    p(f"frozen counter sha256   {hashlib.sha256(open(COUNTER, 'rb').read()).hexdigest()}")

    # ---------------------------------------------------------------- Q1
    p("")
    p("Q1  scratch path relationship (what the replay sees)")
    root = tempfile.mkdtemp(prefix="j4-archive-ref-", dir=os.environ.get("TMPDIR", "/tmp"))
    S = tempfile.mkdtemp(prefix="r53c1-", dir=root)          # exactly what main() does
    p(f"counter scratch root     {root}")
    p(f"counter scratch S        {S}   (mode {oct(os.stat(S).st_mode & 0o777)})")
    # prepare_env() (line 613) sets TMPDIR=S/tmp-<tag> for the replay
    tag = "b1"
    tmpdir = os.path.join(S, f"tmp-{tag}")
    os.makedirs(tmpdir)
    p(f"replay TMPDIR            {tmpdir}   (prepare_env, line 616)")
    p(f"dirname(replay TMPDIR)   {os.path.dirname(os.path.abspath(tmpdir))}")
    p(f"-> dirname(TMPDIR) is S  {os.path.dirname(os.path.abspath(tmpdir)) == S}")
    apath = os.path.join(S, "counter-archive.tar.gz")
    make_tar(apath, {"llama-b11909/libggml-base.so.0.27.0": b"REAL-RELEASE-BYTES" * 8})
    st = os.stat(apath)
    p(f"counter archive ref      {apath}")
    p(f"-> the reference sits in S  {os.path.dirname(apath) == S}")
    p(f"-> same uid as the counter  uid {os.getuid()}; file uid {st.st_uid}")
    p(f"-> file mode {oct(st.st_mode & 0o777)}; owner-writable "
      f"{bool(st.st_mode & stat.S_IWUSR)}; S mode {oct(os.stat(S).st_mode & 0o777)}")
    # a same-uid child with the replay's TMPDIR can reach it
    code = ("import os,sys\n"
            "p=os.path.join(os.path.dirname(os.path.abspath(os.environ['TMPDIR'])),'counter-archive.tar.gz')\n"
            "print('child reached', p, os.path.exists(p))\n"
            "open(p,'ab').write(b'X')\n"
            "print('child appended; size now', os.path.getsize(p))\n")
    r = os.system(f"{sys.executable} -c {code!r} >/dev/null 2>&1")
    p(f"-> replay-like child (same uid, TMPDIR in S) reach+append rc={r} "
      f"(0 = the file WAS reachable and writable)")
    p("   => the PATH is reachable; the question is whether the counter still READS it later")

    # ---------------------------------------------------------------- Q2
    p("")
    p("Q2  what the counter does when the reference vanishes")
    # (a) vanishes BEFORE the counter reads it: Archive(apath) on a missing path
    missing = os.path.join(S, "not-there.tar.gz")
    try:
        m.Archive(missing)
        p("Archive(missing)          NO EXCEPTION (unexpected)")
    except Exception as exc:
        p(f"Archive(missing)          {type(exc).__name__}: {str(exc).splitlines()[0]}")
        p(f"   -> is OSError: {isinstance(exc, OSError)}; is tarfile.TarError: "
          f"{isinstance(exc, tarfile.TarError)}")
        p("   -> main()'s `except (OSError, tarfile.TarError)` (line 926) catches it ->")
        p("      detail 'counter archive unavailable: ...', arc stays None ->")
        p("      bind_one() line 718-719 appends 'code: the counter has no archive of its own'")
        p("      -> code leg fails -> met=False -> exit 1  (FAIL CLOSED)")
    # (b) vanishes AFTER the counter read it: the bytes are already in memory
    live = os.path.join(S, "live.tar.gz")
    make_tar(live, {"llama-b11909/libggml-base.so.0.27.0": b"REAL-RELEASE-BYTES" * 8})
    arc = m.Archive(live)
    p(f"Archive(live).blob bytes  {len(arc.blob)}; sha256 {hashlib.sha256(arc.blob).hexdigest()[:16]}...")
    p(f"tarfile backed by         io.BytesIO(self.blob) (Archive.__init__ lines 451-453)")
    os.unlink(live)
    p("   (reference file deleted from disk)")
    got = arc.member("llama-b11909/libggml-base.so.0.27.0")
    p(f"arc.member() after delete {got[:22]!r} len={len(got)}")
    p(f"-> still the release bytes: {got.startswith(b'REAL-RELEASE-BYTES')}")
    p("   => after Archive() is constructed the file on disk is NEVER read again:")
    p("      arc.member() serves io.BytesIO(self.blob); the digest check at line 921")
    p("      hashes arc.blob, not the file. Deleting/overwriting the file is inert.")

    # (c) the ordering that makes (b) the only reachable case
    p("")
    p("Q2c  ordering in the frozen counter (line numbers from the frozen file)")
    src = open(COUNTER).read().splitlines()
    for n, want in ((915, 'apath = os.path.join(S, "counter-archive.tar.gz")'),
                    (920, 'arc = Archive(apath)'),
                    (921, 'hashlib.sha256(arc.blob)'),
                    (936, 'bind_one(tree,')):
        print(f"   {n}: {src[n-1].strip()}")
        lines.append(f"   {n}: {src[n-1].strip()}")
    p("   => the counter downloads, reads into memory and hashes its reference BEFORE")
    p("      the first replay is launched (bind_one -> start_replay). There is no")
    p("      window in which a replay can change the bytes that are compared.")

    shutil.rmtree(root, ignore_errors=True)
    text = "\n".join(lines) + "\n"
    if OUT != "-":
        with open(OUT, "w") as fh:
            fh.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
