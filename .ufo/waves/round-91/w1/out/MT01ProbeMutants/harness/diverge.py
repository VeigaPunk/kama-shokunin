#!/usr/bin/env python3
"""diverge.py PRISTINE MUTANT — run both probe byte-sets on discriminating stubs.

Reuses the frozen counter's Stub/jbody helpers (read-only) so the stub behavior is the
same one the frozen counter grades. Prints verdict/reason/served_model/exit per case.
"""
import importlib.util, json, os, subprocess, sys, tempfile, time
from pathlib import Path

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
spec = importlib.util.spec_from_file_location("r91", LANE / "tools" / "round91-answer-time.py")
r91 = importlib.util.module_from_spec(spec); spec.loader.exec_module(r91)


def run(probe, port, expect, work):
    env = dict(os.environ, TMPDIR=str(work))
    cmd = ["bash", str(probe), "check", "--port", str(port), "--expect", expect,
           "--timeout", "5", "--connect-timeout", "2", "--json"]
    t0 = time.monotonic()
    p = subprocess.run(cmd, capture_output=True, env=env, cwd=work, timeout=120)
    dt = time.monotonic() - t0
    row = None
    try:
        row = json.loads(p.stdout.decode())["rows"][0]
    except Exception:
        pass
    return {"verdict": row.get("verdict") if row else None,
            "reason": row.get("reason") if row else None,
            "served_model": row.get("served_model") if row else None,
            "probe_exit": p.returncode, "seconds": round(dt, 2)}


def ids_doc(ids, status=None):
    if status is None:
        return {"object": "list", "data": [{"id": i} for i in ids]}
    return {"object": "list", "data": [{"id": i, "status": {"value": status}} for i in ids]}


CASES = json.loads(Path(sys.argv[3]).read_text()) if len(sys.argv) > 3 else []


def main():
    pristine, mutant = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
    work = Path(tempfile.mkdtemp(prefix="diverge-", dir=os.environ["TMPDIR"]))
    print(f"pristine_sha={r91.sha256(pristine)} mutant_sha={r91.sha256(mutant)}")
    for name, doc, expect in CASES:
        with r91.Stub({"/v1/models": {"body": r91.jbody(doc)}}) as st:
            a = run(pristine, st.port, expect, work)
        with r91.Stub({"/v1/models": {"body": r91.jbody(doc)}}) as st:
            b = run(mutant, st.port, expect, work)
        same = (a["verdict"], a["reason"], a["served_model"], a["probe_exit"]) == \
               (b["verdict"], b["reason"], b["served_model"], b["probe_exit"])
        print(f"CASE {name} expect={expect!r} divergent={0 if same else 1}")
        print(f"   M      {a}")
        print(f"   mutant {b}")


if __name__ == "__main__":
    main()
