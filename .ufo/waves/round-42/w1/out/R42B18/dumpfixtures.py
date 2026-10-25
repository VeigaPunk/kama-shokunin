#!/usr/bin/env python3
"""Dump the audit's seed-42 fixtures (make_case) per case so two interpreters can be diffed."""
import hashlib
import importlib.util
import os
import random
import subprocess
import sys
import tempfile

REPO, TIP = sys.argv[1], sys.argv[2]
with tempfile.TemporaryDirectory(prefix="dump-export-") as export:
    tar = subprocess.run(["git", "-C", REPO, "archive", "--format=tar", TIP], capture_output=True, check=True)
    subprocess.run(["tar", "-x", "-C", export], input=tar.stdout, check=True)
    spec = importlib.util.spec_from_file_location("r42audit", os.path.join(export, "tools/round42-digest-audit.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    rng = random.Random(42)
    for i in range(m.CASES):
        with tempfile.TemporaryDirectory(prefix=f"case{i}-", dir=export) as d:
            m.make_case(rng, d, i)
            print(f"== case {i}")
            for root, dirs, files in os.walk(d):
                dirs.sort()
                for f in sorted(files):
                    p = os.path.join(root, f)
                    data = open(p, "rb").read()
                    print(f"  {os.path.relpath(p, d)} {hashlib.sha256(data).hexdigest()[:16]} {data!r}")
