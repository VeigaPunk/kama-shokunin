#!/usr/bin/env python3
"""Reproduce the one SEED=92 UTF-8 fuzz difference (measured/c2-fuzz-equivalence.out): run served_persist from the
BASE probe (ed018ca0) and the M2 probe (fa8aedb7) five times each on the same input, and base normalize_id alone.
Usage (cwd = scratch holding lib-base.sh / lib-new.sh as in c2-fuzz-equivalence.out): python3 c2-fuzz-diff-repro.py"""
import subprocess
env = {"LC_ALL": "en_US.UTF-8", "PATH": "/usr/bin:/bin"}
x = '\r/%s\\*\x7f/\udcc3\\ÿ.gguf\x01\n,\x01\\\x7f\x01\x7f\udc85"\udc85/'.encode('utf-8', 'surrogateescape')
for lib in ("lib-base.sh", "lib-new.sh"):
    outs = [subprocess.run(["bash", "-c", f'source {lib}; set +e; IFS= read -r -d "" x; served_persist "$x"'],
                           input=x + b"\0", capture_output=True, env=env).stdout for _ in range(5)]
    print(lib, "distinct_outputs=%d" % len(set(outs)), [o.hex() for o in outs])
y = b' /%s\\*/\xc3\\\xc3\xbf.gguf'
outs = [subprocess.run(["bash", "-c", 'source lib-base.sh; set +e; IFS= read -r -d "" x; normalize_id "$x"'],
                       input=y + b"\0", capture_output=True, env=env).stdout for _ in range(5)]
print("base normalize_id on", y.hex(), "distinct_outputs=%d" % len(set(outs)), [o.hex() for o in outs],
      "rule_expects", (b'\xc3\\\xc3\xbf').hex())
