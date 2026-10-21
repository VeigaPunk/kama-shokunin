#!/usr/bin/env python3
"""SeparabilityRecheck (KamaR21 FALSIFY): re-run the round-21 C1/C2 counting
commands in scratch configurations and compare them with the official
b76727f3 streams.

Scratch clones live under /tmp/kama-r21-SeparabilityRecheck/<cfg>. Each is
a6617149 plus, except ctrl, one scratch commit that reverts a file set to
7a6bc911. The real lane and fleet are only read. The official
c2-live-receipt (a live llama-server launch) is NOT re-run; the receipt it
produced is re-checked as data by the c2-live-* commands.
"""
from __future__ import annotations

import concurrent.futures as cf
import difflib
import hashlib
import json
import pathlib
import subprocess
import time

PY = "/usr/bin/python3"
SCRATCH = pathlib.Path("/tmp/kama-r21-SeparabilityRecheck")
REAL_LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
FLEET = "/home/vgpnk/Projects/shokunin"
OFFICIAL = pathlib.Path(REAL_LANE) / ".ufo/waves/round-21/runs/b76727f3"
OUT = pathlib.Path(REAL_LANE) / ".ufo/waves/round-21/falsify/out/SeparabilityRecheck"
BASE = "7a6bc911f9eb7dbea9e3b81f5f2449ecda10096d"
TIP = "a6617149722c73d90e142fbdc8154d6967055f7e"
MODEL_SHA = "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"
TREE_SHA = "6c216313a88d71b141bc62f684b8f95c040710ff050801b13521861826785a2c"
LINKS_SHA = "5cb9f4865c8e1315dbd1baa99310c9bc65ddcf469929488359c66587b6470060"
ZERO = "0" * 64
AUDIT = "{lane}/tools/report-landing-audit.py"
PRODUCER = "{lane}/tools/kama-llamacpp-live.py"
GATE = "{lane}/tests/llamacpp-live/check-receipt.py"
GRID = "{lane}/tests/llamacpp-live/install-links-grid.py"
TREEGRID = "{lane}/tests/llamacpp-live/install-tree-grid.py"
LIVE = "{out}/live-receipt.json"
R18 = "{lane}/.ufo/waves/round-18/live-recovery/receipt-%d.json"

# (official name, argv template, expected exit as recorded in commands.json)
COMMANDS = [
    ("c1-absent-at-base", ["git", "-C", "{lane}", "cat-file", "-e",
                           f"{BASE}:tools/report-landing-audit.py"], 128),
    ("c1-audit-selftest", [PY, AUDIT, "--selftest"], 0),
    ("c1-audit-raw", [PY, AUDIT, "--fleet-repo", FLEET, "--rounds", "10-20",
                      "--no-errata", "--json"], 1),
    ("c1-audit-ledger", [PY, AUDIT, "--fleet-repo", FLEET, "--rounds", "10-20",
                         "--json"], 0),
    ("c2-grid-selftest", [PY, GRID, "--selftest"], 0),
    ("c2-grid-frozen", [PY, GRID, "--arm", "frozen", "--json"], 1),
    ("c2-grid-current", [PY, GRID, "--arm", "current", "--json"], 0),
    ("c2-grid-both", [PY, GRID, "--arm", "both", "--json"], 1),
    ("c2-gate-selftest", [PY, GATE, "--selftest"], 0),
    ("c2-producer-selftest", [PY, PRODUCER, "--selftest"], 0),
    ("c2-live-gate-pinned", [PY, GATE, LIVE, "--require-schema", "v3",
                             "--require-install-links",
                             "--expect-model-sha256", MODEL_SHA,
                             "--expect-install-tree-sha256", TREE_SHA,
                             "--expect-install-links-sha256", LINKS_SHA], 0),
    ("c2-live-gate-wrong-links-pin", [PY, GATE, LIVE, "--require-install-links",
                                      "--expect-install-links-sha256", ZERO], 1),
    ("c2-legacy-receipt-1", [PY, GATE, R18 % 1], 0),
    ("c2-legacy-receipt-2", [PY, GATE, R18 % 2], 0),
    ("c2-legacy-receipt-3", [PY, GATE, R18 % 3], 0),
    ("c2-legacy-receipt-1-required", [PY, GATE, R18 % 1,
                                      "--require-install-links"], 1),
    ("nh-install-tree-grid-selftest", [PY, TREEGRID, "--selftest"], 0),
]
CONFIGS = ["ctrl", "ctrlnoop", "revC1", "revC2", "revErrata", "revProducer",
           "revGate", "revGrid"]
PATHS = ["tools/report-landing-audit.py", "registry/report-landing-errata.tsv",
         "tools/kama-llamacpp-live.py", "tests/llamacpp-live/check-receipt.py",
         "tests/llamacpp-live/install-links-grid.py"]


def lane_dir(cfg):
    return SCRATCH / ("lane" if cfg == "ctrl" else cfg)


def git(d, *args):
    p = subprocess.run(["git", "-C", str(d), *args], capture_output=True,
                       text=True)
    return p.returncode, p.stdout.strip()


def blob_state(d, path):
    rc, head = git(d, "rev-parse", "-q", "--verify", f"HEAD:{path}")
    if rc != 0:
        return "ABSENT"
    if head == git(d, "rev-parse", "-q", "--verify", f"{BASE}:{path}")[1]:
        return "BASE"
    if head == git(d, "rev-parse", "-q", "--verify", f"{TIP}:{path}")[1]:
        return "TIP"
    return head[:12]


def config_info():
    info = {}
    for cfg in CONFIGS:
        d = lane_dir(cfg)
        info[cfg] = {
            "dir": str(d),
            "head": git(d, "rev-parse", "HEAD")[1],
            "vs_tip_shortstat": git(d, "diff", "--shortstat", TIP, "HEAD")[1],
            "blobs": {p: blob_state(d, p) for p in PATHS},
        }
    return info


def run_one(cfg, name, template, expected, timeout=300):
    lane = str(lane_dir(cfg))
    out = lane + "/.ufo/waves/round-21/runs/b76727f3"
    argv = [a.replace("{lane}", lane).replace("{out}", out) for a in template]
    t0 = time.monotonic()
    timed_out = False
    try:
        p = subprocess.run(argv, capture_output=True, cwd=lane, timeout=timeout)
        rc, so, se = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        rc, so, se = None, exc.stdout or b"", exc.stderr or b""
    secs = round(time.monotonic() - t0, 2)
    rd = OUT / "runs" / cfg
    rd.mkdir(parents=True, exist_ok=True)
    (rd / f"{name}.stdout").write_bytes(so)
    (rd / f"{name}.stderr").write_bytes(se)
    (rd / f"{name}.exit").write_text(f"exit={rc}\n")
    return {"cfg": cfg, "name": name, "argv": argv, "exit": rc,
            "expected": expected, "timed_out": timed_out, "seconds": secs,
            "so": so, "se": se, "lane": lane}


def run_cfg(cfg):
    return [run_one(cfg, n, t, e) for n, t, e in COMMANDS]


def norm(data, lane):
    return (data.decode("utf-8", "replace").replace(lane, "{lane}")
            .replace(REAL_LANE, "{lane}"))


def sha12(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def compare(r):
    name, cfg, lane = r["name"], r["cfg"], r["lane"]
    off_so = (OFFICIAL / f"{name}.stdout").read_bytes()
    off_se = (OFFICIAL / f"{name}.stderr").read_bytes()
    off_exit = int((OFFICIAL / f"{name}.exit").read_text().strip().split("=")[1])
    o_out, c_out = norm(off_so, REAL_LANE), norm(r["so"], lane)
    o_err, c_err = norm(off_se, REAL_LANE), norm(r["se"], lane)
    row = {
        "cfg": cfg, "name": name, "argv": r["argv"], "expected": r["expected"],
        "exit": r["exit"], "official_exit": off_exit,
        "exit_ok": r["exit"] == r["expected"] == off_exit,
        "stdout_norm_eq": o_out == c_out, "stderr_norm_eq": o_err == c_err,
        "stdout_raw_eq": off_so == r["so"],
        "stdout_sha12": sha12(c_out), "official_stdout_sha12": sha12(o_out),
        "seconds": r["seconds"], "timed_out": r["timed_out"],
    }
    if not (row["stdout_norm_eq"] and row["stderr_norm_eq"]):
        diff = "".join(difflib.unified_diff(
            o_out.splitlines(True), c_out.splitlines(True),
            "official/stdout", f"{cfg}/stdout"))
        diff += "".join(difflib.unified_diff(
            o_err.splitlines(True), c_err.splitlines(True),
            "official/stderr", f"{cfg}/stderr"))
        (OUT / "runs" / cfg / f"{name}.diff").write_text(diff[:200000],
                                                         encoding="utf-8")
    return row


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    info = config_info()
    with cf.ThreadPoolExecutor(max_workers=len(CONFIGS)) as ex:
        futs = {cfg: ex.submit(run_cfg, cfg) for cfg in CONFIGS}
        raw = {cfg: futs[cfg].result() for cfg in CONFIGS}
    rows = [compare(r) for cfg in CONFIGS for r in raw[cfg]]
    (OUT / "configs.json").write_text(json.dumps(info, indent=2) + "\n")
    (OUT / "matrix.json").write_text(json.dumps(rows, indent=2) + "\n")
    with open(OUT / "matrix.tsv", "w", encoding="utf-8") as fh:
        fh.write("cfg\tname\texpected\texit\tofficial_exit\texit_ok\t"
                 "stdout_norm_eq\tstderr_norm_eq\tstdout_raw_eq\t"
                 "stdout_sha12\tofficial_stdout_sha12\tseconds\ttimed_out\n")
        for x in rows:
            fh.write("\t".join(str(x[k]) for k in (
                "cfg", "name", "expected", "exit", "official_exit", "exit_ok",
                "stdout_norm_eq", "stderr_norm_eq", "stdout_raw_eq",
                "stdout_sha12", "official_stdout_sha12", "seconds",
                "timed_out")) + "\n")
    for cfg in CONFIGS:
        print(f"{cfg}: head={info[cfg]['head'][:9]} vs_tip=[{info[cfg]['vs_tip_shortstat']}] "
              + " ".join(f"{p.split('/')[-1]}={v}" for p, v in info[cfg]['blobs'].items()))
    print("name | " + " | ".join(CONFIGS))
    for name, _, _ in COMMANDS:
        cells = []
        for cfg in CONFIGS:
            x = next(r for r in rows if r["cfg"] == cfg and r["name"] == name)
            cell = f"{x['exit']}{'' if x['exit_ok'] else '!'}/" \
                   f"{'O' if x['stdout_norm_eq'] else 'd'}" \
                   f"{'E' if x['stderr_norm_eq'] else 'e'}"
            cells.append(cell)
        off = next(r for r in rows if r["cfg"] == "ctrl" and r["name"] == name)
        print(f"{name} (off={off['official_exit']}) | " + " | ".join(cells))


if __name__ == "__main__":
    main()
