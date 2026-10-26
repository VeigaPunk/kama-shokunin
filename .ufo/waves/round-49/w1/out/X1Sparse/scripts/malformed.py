#!/usr/bin/env python3
"""Malformed-PAX-sparse cells: formats whose tarfile parsing raises ValueError
(not a TarError), which is outside verify_archive_member's except clause.

usage: malformed.py --tool-dir D --art A
"""
import argparse
import hashlib
import importlib.util
import json
import os
import time

ap = argparse.ArgumentParser()
ap.add_argument("--tool-dir", required=True)
ap.add_argument("--art", required=True)
a = ap.parse_args()
art = json.load(open(os.path.join(a.art, "artifacts.json")))
spec = importlib.util.spec_from_file_location(
    "kl", os.path.join(a.tool_dir, "kama-llamacpp-live.py"))
kl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kl)
for key in ("pax_bad_map", "pax10_nomap"):
    arc, dig, size = art[key]
    t0 = time.monotonic()
    try:
        try:
            got = kl.verify_archive_member(arc, dig, art["memb"], art["good_sha"],
                                           art["good_size"])
        except TypeError as exc:
            if "positional argument" not in str(exc):
                raise
            got = kl.verify_archive_member(arc, dig, art["memb"], art["good_sha"])
        out = {"outcome": "ok", "result": got}
    except kl.SetupError as exc:
        out = {"outcome": "refused", "token": exc.code}
    except BaseException as exc:  # noqa: BLE001
        out = {"outcome": "uncaught", "exc": f"{type(exc).__name__}: {exc}"}
    out.update(case=key, seconds=round(time.monotonic() - t0, 3), archive_bytes=size)
    print(json.dumps(out), flush=True)
