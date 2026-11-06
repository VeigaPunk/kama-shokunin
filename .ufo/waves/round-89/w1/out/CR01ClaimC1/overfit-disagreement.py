#!/usr/bin/env python3
"""CR01ClaimC1: held-out cells where the fixture-name forgery and the M rule disagree.

Imports the frozen counter's own helpers (start/run_probe/oracle/http/kill_children)
so the router child, probe invocation and oracle mapping are byte-identical to the
counter's. One lane-owned b12177 child, default autoload, killed by process group.
"""
from __future__ import annotations

import hashlib
import importlib.util
import os
import sys
import tempfile
from pathlib import Path

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
spec = importlib.util.spec_from_file_location("r89", LANE / "tools/round89-unloadable-cells.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def main() -> int:
    work = Path(sys.argv[1]).resolve()
    forged = Path(sys.argv[2]).resolve()
    work.mkdir(parents=True, exist_ok=True)
    d = Path(tempfile.mkdtemp(prefix="overfit-", dir=work)).resolve()
    try:
        models = d / "models"
        models.mkdir()
        raw = m.MODEL.read_bytes()
        # loadable, ordinary name: both rules MODEL_OK (control)
        (models / "validmodel.gguf").write_bytes(raw)
        # loadable file wearing a FIXTURE name: M says OK, forgery false-reds it
        (models / "trunc.gguf").write_bytes(raw)
        # unloadable bad header, name NOT in the fixture set: M says invalid, forgery OK
        noise = b"".join(hashlib.sha256(b"kama-r89-%d" % i).digest() for i in range(128))
        (models / "weird-bad.gguf").write_bytes(b"GGUF" + (3).to_bytes(4, "little") + noise)
        # missing file via preset, name NOT in the fixture set: M says missing, forgery OK
        ini = d / "presets.ini"
        ini.write_text(f"[absentx]\nmodel = {d}/absentx.gguf\n")
        port = m.start(m.SERVER, ["--models-max", "1", "--models-dir", str(models),
                                  "--models-preset", str(ini)], d, d / "router.log", str(d))
        pcwd = d / "probe-cwd"
        pcwd.mkdir()
        env = dict(os.environ, TMPDIR=str(pcwd))
        real = LANE / "tools/kama-probe.sh"
        print(f"# child port={port} models_dir={models} forged={forged}")
        mism = 0
        for mid in ("validmodel", "trunc", "weird-bad", "absentx"):
            rv, rr = m.run_probe(real, port, mid, env, pcwd)
            fv, fr = m.run_probe(forged, port, mid, env, pcwd)
            code, body = m.http("POST", port, "/v1/chat/completions",
                                {"model": mid, "messages": [{"role": "user", "content": "hi"}],
                                 "max_tokens": 2})
            try:
                oracle, _ = m.oracle(port, mid)
            except m.CannotEvaluate as e:
                oracle = f"CANNOT-EVALUATE({e})"
            agree = "AGREE" if rv == fv else "DISAGREE"
            if (rv == oracle) != (fv == oracle):
                mism += 1
            print(f"CELL {mid} oracle={oracle} http={code} body={body[:120]!r} "
                  f"real={rv}/{rr} forged={fv}/{fr} {agree} "
                  f"real_ok={int(rv == oracle)} forged_ok={int(fv == oracle)}")
        print(f"OVERFIT_DISAGREEMENT cells=4 one_side_wrong={mism}")
    finally:
        m.kill_children()
    return 0


if __name__ == "__main__":
    sys.exit(main())
