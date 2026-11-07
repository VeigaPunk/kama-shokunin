#!/usr/bin/env python3
"""Round-94 planned item 1 baseline (L1 receipt, round 93): `snapshot --json` on a registry of R rows, each pinning the
same stub whose /v1/models serves one 200 000-byte id; wall time per R at the current probe. Usage: <scratch>"""
import importlib.util, subprocess, sys, tempfile, time
from pathlib import Path
spec = importlib.util.spec_from_file_location("lp", "tools/round92-linear-paths.py")
lp = importlib.util.module_from_spec(spec); spec.loader.exec_module(lp)
rev = subprocess.run(["git", "rev-parse", "master"], capture_output=True, text=True).stdout.strip()
work = Path(tempfile.mkdtemp(dir=sys.argv[1])); R = lp.Runner(work)
R.install(subprocess.run(["git", "show", f"{rev}:tools/kama-probe.sh"], capture_output=True, check=True).stdout)
print(f"# rev={rev} load1={open('/proc/loadavg').read().split()[0]}")
with lp.Stub({"/v1/models": lp.jbody(lp.ids_doc(["a" * 200000]))}) as s:
    for rows in (8, 16, 32, 64):
        d = work / f"r{rows}"; d.mkdir()
        pin = d / "pin.txt"; pin.write_text(f"http://127.0.0.1:{s.port}/v1\n")
        reg = d / "registry.tsv"
        reg.write_text("id\tconsumer_path\tjson_pointer_or_grep\tdeclared_baseurl\texpected_model_id\tnotes\n" +
                       "".join(f"c{i:03d}\t{pin}\tgrep:http://[^ ]+\thttp://127.0.0.1:{s.port}/v1\ta\tr94\n" for i in range(rows)))
        t0 = time.monotonic()
        p = subprocess.run(["bash", str(R.probe), "snapshot", "--json", "--registry", str(reg), "--history", str(d / "h"),
                            "--timeout", "5", "--connect-timeout", "2"], capture_output=True, env=R.env, cwd=R.cwd, timeout=600)
        print(f"R94_JSON_ARRAY rows={rows} seconds={time.monotonic() - t0:.2f} rc={p.returncode} stdout_bytes={len(p.stdout)}", flush=True)
