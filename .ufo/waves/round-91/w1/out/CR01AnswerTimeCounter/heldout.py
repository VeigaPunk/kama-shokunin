#!/usr/bin/env python3
"""Held-out probes: id ORDER (good not last), numeric-string ids, and the served_model field
the C1 counter never inspects. Reuses the frozen counter's own Stub/run."""
import importlib.util
import os
import pathlib
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("rt", HERE / "wt/tools/round91-answer-time.py")
rt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rt)

many = [f"x{i:06d}" for i in range(200000)]
cases = [
    ("T1-good-last (in counter)", rt.ids_doc(many + ["good"]), "good"),
    ("H1-good-first (held out)", rt.ids_doc(["good"] + many), "good"),
    ("H2-good-middle (held out)", rt.ids_doc(many[:100000] + ["good"] + many[100000:]), "good"),
    ("N1-id-1e3 vs 1000 (held out)", rt.ids_doc(["1e3"]), "1000"),
    ("N2-id-010 vs 10 (held out)", rt.ids_doc(["010"]), "10"),
]
probes = {
    "M": HERE / "probe-M.sh",
    "g1-last-only": HERE / "forged/g1-last-only.sh",
    "g6-served-truncated": HERE / "forged/g6-served-truncated.sh",
    "g9-numeric-compare": HERE / "forged/g9-numeric-compare.sh",
}
work = pathlib.Path(tempfile.mkdtemp(prefix="h-", dir=os.environ["TMPDIR"]))
cwd = work / "cwd"
cwd.mkdir()
env = dict(os.environ, TMPDIR=str(cwd))
for bname, doc, expect in cases:
    body = rt.jbody(doc)
    for pname, p in probes.items():
        with rt.Stub({"/v1/models": {"body": body}}) as stub:
            rc, so, dt = rt.run(p, stub.port, expect, env, cwd)
        row = rt.parse_row(so)
        served = row.get("served_model", "") if row else ""
        n = served.count(",") + 1 if served and served != "-" else 0
        print(f"{bname:32s} probe={pname:20s} rc={rc} verdict={row.get('verdict') if row else None} "
              f"reason={row.get('reason') if row else None} served_model_ids={n} seconds={dt:.2f}",
              flush=True)
