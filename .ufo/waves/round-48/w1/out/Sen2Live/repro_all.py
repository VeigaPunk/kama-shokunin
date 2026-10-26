#!/usr/bin/env python3
"""Reproduce every measurement cited by seat Sen2Live (round 48), in order.

Run from this directory with TMPDIR=/fast/scratch/hyaku/kama-r48/Sen2Live.
Nothing outside this scratch is written.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def sh(cmd, label, timeout=300):
    print(f"\n$ {label}", flush=True)
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                       cwd=HERE, timeout=timeout)
    sys.stdout.write(p.stdout)
    if p.stderr.strip():
        sys.stdout.write("[stderr] " + p.stderr.strip().splitlines()[-1] + "\n")
    print(f"[exit {p.returncode}]", flush=True)


if __name__ == "__main__":
    sh("python3 probe_archive.py regular", "verify_archive_member: regular member")
    sh("python3 probe_archive.py types", "verify_archive_member: symlink/hardlink/dir/dev/fifo/absent/duplicate")
    sh("python3 probe_archive.py archive-level", "verify_archive_member: archive-level refusals")
    sh("python3 probe_archive.py big", "verify_archive_member: 64 MiB declared member")
    sh("python3 probe_archive.py many", "verify_archive_member: 300k members (index scan)")
    sh("""python3 - <<'EOF'
import sys, time, tracemalloc, tarfile, os
sys.path.insert(0, ".")
import probe_archive as P
p, _ = P.many_members("mem1m.tgz", 1000000)
tracemalloc.start(); t0 = time.monotonic()
with tarfile.open(p) as tf:
    ms = tf.getmembers()
print(f"1M members: archive_bytes={os.path.getsize(p)} python_peak_MB={tracemalloc.get_traced_memory()[1]/1e6:.1f} "
      f"seconds={time.monotonic()-t0:.2f} index_len={len(ms)}")
EOF""", "getmembers(): 1M members, 9.9 MB archive")
    sh("""python3 - <<'EOF'
import sys; sys.path.insert(0, ".")
import probe_archive as P
for real in (1 << 30, 0o77777777777):
    a, s = P.sparse_archive("e-%d.tgz" % real, real)
    P.run(f"gnu-sparse-declared-{real}", a, s, P.MEMBER, P.sha(b"A"))
EOF""", "verify_archive_member: GNU sparse members (declared size drives the read)")
    sh("rm -f fifo.tgz && mkfifo fifo.tgz && timeout 5 python3 -c \""
       "import importlib.util;spec=importlib.util.spec_from_file_location('kl','kama-llamacpp-live.py');"
       "kl=importlib.util.module_from_spec(spec);spec.loader.exec_module(kl);"
       "print(kl.verify_archive_member('fifo.tgz','0'*64,'m','0'*64))\"; echo fifo_rc=$?",
       "verify_archive_member: FIFO archive path (no S_ISREG check)")
    sh("timeout 5 python3 -c \""
       "import importlib.util;spec=importlib.util.spec_from_file_location('kl','kama-llamacpp-live.py');"
       "kl=importlib.util.module_from_spec(spec);spec.loader.exec_module(kl);"
       "print(kl.verify_archive_member('/dev/zero','0'*64,'m','0'*64))\"; echo devzero_rc=$?",
       "verify_archive_member: /dev/zero archive path")
    sh("python3 proposed_verify.py", "PROPOSED verify_archive_member against the same matrix")
    for c in ("shape", "deep", "bytes", "twins", "vacuous"):
        sh(f"python3 compare_probe.py {c}", f"--compare: {c}")
    sh("python3 compare_fix_check.py", "PROPOSED compare/projection fix on the same cases + real receipts")
    sh("python3 passthrough_probe.py", "replay -> live pass-through (fake argv dump, then real live)")
    sh("python3 urlgate_probe.py", "v5 URL/pin gate: what is anchored, and the v4 counter-example")
