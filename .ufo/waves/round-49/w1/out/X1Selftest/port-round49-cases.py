#!/usr/bin/env python3
"""Port the three round-49 bound cases of kama-llamacpp-live.py
`_provenance_selftest()` (build 74558c71) onto the round-48
`verify_archive_member()` (base 438127bc, the round-48 closure) and measure
each under a 10 s cap.

Each case is the new selftest's own call, unchanged in shape:
  size-mismatch  verify_archive_member(arc, asha, 'rel/llama-server', ssha, 1)
                 -> new token provenance-member-size-mismatch
  sparse         verify_archive_member(sparse, sha256(sparse), 'rel/llama-server', ssha)
                 -> new token provenance-member-sparse
  not-regular    verify_archive_member(DIR, asha, 'rel/llama-server', ssha)
                 -> new token provenance-archive-not-regular

Old code must fail or hang on every case. The stub archives are built exactly
as `_provenance_selftest()` builds them.

Usage:
  port-round49-cases.py --old tools/kama-llamacpp-live-438127bc.py \
                        --new tools/kama-llamacpp-live-74558c71.py [--scratch DIR]
The child invocation `--case <name> --module <path> --dir <stub dir>` is what
the parent times out; the parent itself does no hashing.

stdout: one JSON line per case plus a final JSON summary; exit 0 when every
OLD case fails-or-hangs and every NEW case raises its round-49 token, else 1.
"""
import argparse
import hashlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import tarfile
import time

CAP = 10.0
CASES = ("size-mismatch", "sparse", "not-regular")
# New token each ported case must raise on the round-49 code.
NEW_TOKEN = {"size-mismatch": "provenance-member-size-mismatch",
             "sparse": "provenance-member-sparse",
             "not-regular": "provenance-archive-not-regular"}


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def build_stubs(d):
    """Exactly the stub set `_provenance_selftest()` builds."""
    os.makedirs(d, exist_ok=True)
    rel = os.path.join(d, "rel")
    os.makedirs(rel, exist_ok=True)
    srv = os.path.join(rel, "llama-server")
    with open(srv, "wb") as fh:
        fh.write(b"server-stub\n")
    arc = os.path.join(d, "a.tar.gz")
    with tarfile.open(arc, "w:gz") as tf:
        tf.add(rel, arcname="rel")
    sparse = os.path.join(d, "sparse.tar.gz")
    with tarfile.open(sparse, "w:gz", format=tarfile.PAX_FORMAT) as tf:
        ti = tarfile.TarInfo("rel/llama-server")
        ti.size = 1
        ti.pax_headers = {"GNU.sparse.map": "0,1", "GNU.sparse.major": "1",
                          "GNU.sparse.minor": "0",
                          "GNU.sparse.realsize": str(10 ** 15)}
        tf.addfile(ti, io.BytesIO(b"A"))
    return {"rel": rel, "srv": srv, "arc": arc, "sparse": sparse}


def load_module(path):
    spec = importlib.util.spec_from_file_location("provenance_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def case_args(case, stub):
    asha = sha256_file(stub["arc"])
    ssha = sha256_file(stub["srv"])
    if case == "size-mismatch":
        # the new selftest's 5th positional: server_size=1
        return (stub["arc"], asha, "rel/llama-server", ssha, 1)
    if case == "sparse":
        return (stub["sparse"], sha256_file(stub["sparse"]), "rel/llama-server", ssha)
    if case == "not-regular":
        return (stub["dir"], asha, "rel/llama-server", ssha)
    raise SystemExit(f"unknown case {case}")


def child(case, module_path, stub_dir):
    stub = build_stubs(stub_dir)
    stub["dir"] = stub_dir
    mod = load_module(module_path)
    out = {"case": case, "module": module_path}
    t0 = time.monotonic()
    try:
        got = mod.verify_archive_member(*case_args(case, stub))
    except BaseException as exc:  # noqa: BLE001 - the point is which failure
        out.update(outcome="raised", exc_type=type(exc).__name__,
                   token=getattr(exc, "code", None), message=str(exc)[:200])
    else:
        out.update(outcome="returned", value=[str(v) for v in got])
    out["elapsed_ms"] = int((time.monotonic() - t0) * 1000)
    print(json.dumps(out))
    return 0


def parent(old, new, scratch):
    stub_dir = os.path.join(scratch, "stubs")
    build_stubs(stub_dir)
    sizes = {"archive": os.path.getsize(os.path.join(stub_dir, "a.tar.gz")),
             "sparse": os.path.getsize(os.path.join(stub_dir, "sparse.tar.gz"))}
    results = []
    for module in (old, new):
        tag = "old" if module == old else "new"
        for case in CASES:
            argv = [sys.executable, os.path.abspath(__file__), "--case", case,
                    "--module", os.path.abspath(module), "--dir", stub_dir]
            t0 = time.monotonic()
            try:
                p = subprocess.run(argv, capture_output=True, text=True, timeout=CAP)
            except subprocess.TimeoutExpired as exc:
                results.append({"side": tag, "case": case, "outcome": "hang",
                                "killed_after_s": CAP,
                                "elapsed_ms": int((time.monotonic() - t0) * 1000),
                                "partial_stdout": (exc.stdout or "")[-500:]})
                continue
            elapsed = int((time.monotonic() - t0) * 1000)
            line = (p.stdout.strip().splitlines() or [""])[-1]
            try:
                rec = json.loads(line)
            except ValueError:
                rec = {"outcome": "no-json", "stdout": p.stdout[-300:], "stderr": p.stderr[-300:]}
            rec.update(side=tag, exit=p.returncode, elapsed_ms=elapsed)
            results.append(rec)
            print(json.dumps(rec))
    ok = True
    for r in results:
        if r["side"] == "old":
            good = r["outcome"] in ("hang", "raised") and r.get("token") != NEW_TOKEN[r["case"]]
            # a return value or the round-49 token would mean the old code held
            if r["outcome"] == "raised" and r.get("token") == NEW_TOKEN[r["case"]]:
                good = False
            if r["outcome"] == "returned":
                good = False
        else:
            good = r["outcome"] == "raised" and r.get("token") == NEW_TOKEN[r["case"]]
        r["case_ok"] = good
        ok = ok and good
    summary = {"cap_s": CAP, "stub_sizes": sizes, "results": results, "ok": ok}
    print(json.dumps({"summary": summary}, indent=1))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--old")
    ap.add_argument("--new")
    ap.add_argument("--scratch", default=os.environ.get("TMPDIR", "/tmp"))
    ap.add_argument("--case", choices=CASES)
    ap.add_argument("--module")
    ap.add_argument("--dir")
    a = ap.parse_args()
    if a.case:
        return child(a.case, a.module, a.dir)
    if not (a.old and a.new):
        ap.error("--old and --new are required")
    os.makedirs(a.scratch, exist_ok=True)
    return parent(a.old, a.new, a.scratch)


if __name__ == "__main__":
    sys.exit(main())
