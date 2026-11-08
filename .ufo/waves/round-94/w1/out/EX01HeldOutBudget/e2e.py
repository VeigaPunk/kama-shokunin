#!/usr/bin/env python3
"""EX01HeldOutBudget e2e — focused cells, absolute paths, smaller N."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

SCRATCH = Path("/fast/scratch/hyaku/kama-r94/EX01HeldOutBudget")
sys.path.insert(0, str(SCRATCH))
import types

_src = (SCRATCH / "round94-router-budget.py").read_text()
_src = _src.replace('if __name__ == "__main__":\n    sys.exit(main())', "")
rb = types.SimpleNamespace()
exec(compile(_src, "round94-router-budget.py", "exec"), rb.__dict__)

PROBES = {
    "base": SCRATCH / "probe-base.sh",
    "m1": SCRATCH / "probe-m1.sh",
}


def loadavg():
    try:
        return open("/proc/loadavg").read().split()[0]
    except OSError:
        return "?"


def main():
    work = SCRATCH / "e2e-work"
    work.mkdir(parents=True, exist_ok=True)
    fx = work / "fx"
    fx.mkdir(exist_ok=True)

    # fixtures (absolute paths)
    ok = (fx / "ok.gguf").resolve()
    ok2 = (fx / "ok2.gguf").resolve()
    slow_valid = (fx / "slow-valid.gguf").resolve()
    slow_bad = (fx / "slow-bad.gguf").resolve()
    ok.write_bytes(rb.gguf(1, 32, True))
    ok2.write_bytes(rb.gguf(2, 32, True))
    slow_valid.write_bytes(rb.gguf(rb.TENSORS, 1, True))
    slow_bad.write_bytes(rb.gguf(rb.TENSORS, 1, False))
    # distinct slow bad files
    dslow = []
    for i in range(16):
        p = (fx / f"dslow-{i:03d}.gguf").resolve()
        p.write_bytes(rb.gguf(rb.TENSORS, 1, False))
        dslow.append(p)
    exe = str(ok)

    print(f"loadavg={loadavg()} exe={exe}", flush=True)

    results = []
    for rev, pp in PROBES.items():
        run_dir = work / f"run-{rev}"
        probe = run_dir / "probe" / "kama-probe.sh"
        probe.parent.mkdir(parents=True, exist_ok=True)
        probe.write_bytes(pp.read_bytes())
        cwd = run_dir / "probe-cwd"
        cwd.mkdir(exist_ok=True)
        env = dict(os.environ, TMPDIR=str(cwd))

        def check(port):
            t0 = time.monotonic()
            try:
                p = subprocess.run(
                    ["bash", str(probe), "check", "--port", str(port), "--expect", "good",
                     "--timeout", "5", "--connect-timeout", "2", "--json"],
                    capture_output=True, timeout=rb.KILL, env=env, cwd=cwd,
                )
            except subprocess.TimeoutExpired:
                return None, None, None, time.monotonic() - t0
            dt = time.monotonic() - t0
            try:
                row = json.loads(p.stdout.decode("utf-8"))["rows"][0]
                return p.returncode, row.get("verdict"), row.get("reason"), dt
            except Exception:
                return p.returncode, f"unparsed(rc={p.returncode})", "-", dt

        def e2e(args_list, label):
            routes = {"/v1/models": rb.router_body(args_list), "/props": rb.PROPS}
            with rb.Stub(routes) as st:
                rc, v, r, dt = check(st.port)
            print(f"CELL {label} rev={rev} verdict={v} reason={r} t={dt:.2f}s rc={rc}", flush=True)
            results.append((rev, label, v, r, dt))

        print(f"\n## rev={rev} (load {loadavg()})", flush=True)

        # (a) distinct N — small set to find flip point
        for n in (2, 4, 8):
            args_list = [[exe, "-m", str(p)] for p in dslow[:n]]
            e2e(args_list, f"a-distinct-N{n}")

        # (b) one slow invalid repeated 4096 times (same file -> SEEN memo hits)
        args_list = [[exe, "-m", str(slow_bad)]] * 4096
        e2e(args_list, "b-repeat-4096")

        # (c) slow VALID gguf repeated 2048 times
        args_list = [[exe, "-m", str(slow_valid)]] * 2048
        e2e(args_list, "c-slowvalid-2048")

        # (d) mixed: 64 valid + 1 slow invalid LAST
        args_list = [[exe, "-m", str(ok)]] * 64 + [[exe, "-m", str(slow_bad)]]
        e2e(args_list, "d-mixed-slowlast")

        # (e) slow file as --mmproj of distinct valid models
        valid_models = []
        for i in range(8):
            vp = (fx / f"valid-{i}.gguf").resolve()
            vp.write_bytes(rb.gguf(1 + i, 32, True))
            valid_models.append(vp)
        args_list = [[exe, "-m", str(vm), "--mmproj", str(slow_bad)] for vm in valid_models]
        e2e(args_list, "e-mmproj-slow")

    # write results
    out = SCRATCH / "e2e.out"
    with open(out, "w") as f:
        for rev, label, v, r, dt in results:
            f.write(f"{rev}\t{label}\t{v}\t{r}\t{dt:.2f}\n")
    print(f"\nwrote {out}", flush=True)


if __name__ == "__main__":
    main()
