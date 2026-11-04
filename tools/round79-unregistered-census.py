#!/usr/bin/env python3
"""round79-unregistered-census.py - round-79 C3 (coverage): the unregistered-listener class.

PREDICATE (frozen: plans/round-79-claims.md section C3):

    `python3 tools/round79-unregistered-census.py --repo <lane>` prints one
    `UNREGISTERED_CENSUS port=<p> unregistered=1 governed=1 class_missing=0` line and exits 0
    only when `bash tools/kama-probe.sh listeners` reports the lane-owned llama.cpp fixture,
    serving on an unregistered loopback port, as `registered=no` under a registry that does
    not declare that port and as `registered=yes` under one that does, the summary's
    `unregistered`/`governed` counts move with the class, and a probe without the class is
    `class_missing=1` with exit 1.

What it does: starts the pinned llama-server (launch fixture b11755, 1.2 MB stories260K
GGUF) on a free loopback port that is neither a registry-declared consumer port nor
listening, writes two scratch registries, runs the probe's `listeners --json` against each,
and grades the fixture port's `registered` class plus the summary counts.  A live-host leg
runs the same census against the lane's real registry and prints an informational
`UNREGISTERED_CENSUS_LIVE` line: it names the serving listeners the registry does not
govern, and gates nothing (the host's listeners are operator-owned and change between runs).

Exit codes: 0 the two fixture legs classify as the predicate requires; 1 a leg disagrees
(the line names which), or the class is missing; 2 could-not-evaluate (prerequisite absent,
child not ready, probe error).  `--selftest` runs four arms against stub probes, so it needs
no server: `both-legs` (class present, both classifications), `class-missing` (a probe
without the class), `probe-error` (a probe exiting 3) and `absent-probe` (a missing probe).
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

SERVER = Path.home() / ".local/opt/llama-b11755/llama-server"
MODEL = Path.home() / ".cache/kama-shokunin/models/stories260K.gguf"
MODEL_ID = "stories260K"


def registered_ports(repo: Path) -> set[int]:
    path = repo / "registry/endpoint-consumers.tsv"
    ports: set[int] = set()
    if not path.is_file():
        return ports
    for line in path.read_text().splitlines():
        if not line or line.startswith("#"):
            continue
        cells = line.split("\t")
        if len(cells) < 4 or cells[0].strip() == "id":
            continue
        declared = cells[3].strip()
        host = declared.split("://")[-1].split("/")[0]
        if ":" in host:
            tail = host.rsplit(":", 1)[1]
            if tail.isdigit():
                ports.add(int(tail))
    return ports


def listening_ports() -> set[int]:
    try:
        out = subprocess.run(["ss", "-ltnH"], capture_output=True, text=True, timeout=10).stdout
    except (OSError, subprocess.SubprocessError):
        return set()
    ports: set[int] = set()
    for line in out.splitlines():
        parts = line.split()
        if len(parts) < 4:
            continue
        tail = parts[3].rsplit(":", 1)[-1]
        if tail.isdigit():
            ports.add(int(tail))
    return ports


def free_port(excluded: set[int]) -> int:
    for _ in range(100):
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        if port not in excluded and port not in listening_ports():
            return port
    raise RuntimeError("no free unregistered loopback port")


def probe_json(probe: Path, repo: Path, registry: Path, port: int | None = None,
               timeout: int = 180) -> tuple[dict, int]:
    """Run `listeners --json`.  With `port`, the probe enumerates ONLY that listener, so the
    summary counts are exactly the fixture's class and no host listener can enter them."""
    argv = ([sys.executable] if probe.suffix == ".py" else ["bash"]) + [
        str(probe), "listeners", "--json", "--registry", str(registry)]
    if port is not None:
        argv += ["--port", str(port)]
    proc = subprocess.run(argv, cwd=repo, capture_output=True, text=True, timeout=timeout)
    if proc.returncode != 0:
        return {"__error__": proc.stderr.strip()[:300] or f"exit {proc.returncode}"}, proc.returncode
    try:
        return json.loads(proc.stdout), proc.returncode
    except json.JSONDecodeError as exc:
        return {"__error__": f"unparsable probe JSON: {exc}"}, proc.returncode


def classify(doc: dict, port: int) -> tuple[str | None, dict]:
    rows = doc.get("listeners")
    if not isinstance(rows, list):
        return None, doc.get("summary") or {}
    for row in rows:
        if int(row.get("port", -1)) == port:
            return row.get("registered"), doc.get("summary") or {}
    return None, doc.get("summary") or {}


def write_registry(path: Path, port: int | None) -> None:
    rows = ["# round-79 scratch registry (census legs; not a consumer admission)"]
    if port is not None:
        rows.append(f"fixture\t-\tgrep::\thttp://127.0.0.1:{port}\t{MODEL_ID}\tscratch")
    else:
        rows.append("fixture\t-\tgrep::\thttp://127.0.0.1:9\t-\tscratch")
    path.write_text("\n".join(rows) + "\n")


def wait_ready(port: int, child: subprocess.Popen, deadline_s: int = 60) -> None:
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    deadline = time.monotonic() + deadline_s
    while time.monotonic() < deadline:
        if child.poll() is not None:
            raise RuntimeError("pinned server exited before readiness")
        try:
            with opener.open(f"http://127.0.0.1:{port}/v1/models", timeout=1) as response:
                if response.status == 200:
                    return
        except OSError:
            time.sleep(0.1)
    raise RuntimeError("pinned server readiness timed out")


def live_leg(probe: Path, repo: Path, exclude: set[int] | None = None) -> dict:
    doc, _ = probe_json(probe, repo, repo / "registry/endpoint-consumers.tsv")
    if "__error__" in doc:
        return {"error": doc["__error__"]}
    summary = doc.get("summary") or {}
    rows = doc.get("listeners") or []
    unreg = [int(r["port"]) for r in rows
             if r.get("registered") == "no" and int(r.get("port", -1)) not in (exclude or set())
             and r.get("verdict") in ("MODEL_OK", "MODEL_MISMATCH", "MODEL_LOADING",
                                      "UNAUTHORIZED_SERVICE")]
    return {"model_endpoints": summary.get("model_endpoints"),
            "governed": summary.get("governed"), "unregistered": summary.get("unregistered"),
            "unregistered_ports": sorted(unreg)}


def trial(repo: Path, probe: Path, work: Path, with_live: bool = True) -> tuple[dict, int]:
    receipt: dict = {"schema": "round79-unregistered-census/v1", "argv": sys.argv,
                     "child_exit": None, "port_closed": None}
    child = None
    port = None
    try:
        for path in (SERVER, MODEL, probe):
            if not path.is_file():
                receipt["error"] = f"prerequisite absent: {path}"
                return receipt, 2
        reg = registered_ports(repo)
        port = free_port(reg)
        receipt["port"] = port
        receipt["registered_ports"] = sorted(reg)
        work.mkdir(parents=True, exist_ok=True)
        argv = [str(SERVER), "--model", str(MODEL), "--host", "127.0.0.1", "--port", str(port),
                "-c", "512", "-t", "1", "--no-webui", "--alias", MODEL_ID]
        receipt["child_argv"] = argv
        with (work / "server.log").open("w+") as log:
            child = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=log,
                                     stderr=subprocess.STDOUT, cwd=work)
            receipt["child_pid"] = child.pid
            wait_ready(port, child)
            reg_a = work / "registry-without.tsv"
            reg_b = work / "registry-with.tsv"
            write_registry(reg_a, None)
            write_registry(reg_b, port)
            doc_a, rc_a = probe_json(probe, repo, reg_a, port=port)
            doc_b, rc_b = probe_json(probe, repo, reg_b, port=port)
            receipt["probe_exit"] = [rc_a, rc_b]
            if "__error__" in doc_a:
                receipt["error"] = "probe leg A: " + doc_a["__error__"]
                return receipt, 2
            if "__error__" in doc_b:
                receipt["error"] = "probe leg B: " + doc_b["__error__"]
                return receipt, 2
            class_a, sum_a = classify(doc_a, port)
            class_b, sum_b = classify(doc_b, port)
            class_missing = 0 if (class_a is not None and class_b is not None
                                  and "governed" in sum_a and "unregistered" in sum_b) else 1
            # Host-independent leg rule: declaring the fixture port can only move ONE
            # listener between the classes, so the summary counts must differ by exactly
            # one in the direction the class names.  The live host may carry other
            # unregistered model endpoints; the fixture leg must not depend on their count.
            unregistered = 1 if (class_a == "no" and class_b == "yes"
                                 and sum_a.get("unregistered") == 1
                                 and sum_a.get("governed") == 0) else 0
            governed = 1 if (class_a == "no" and class_b == "yes"
                             and sum_b.get("governed") == 1
                             and sum_b.get("unregistered") == 0) else 0
            receipt.update(class_a=class_a, class_b=class_b, summary_a=sum_a, summary_b=sum_b,
                           class_missing=class_missing, unregistered=unregistered,
                           governed=governed, rows=len(doc_a.get("listeners") or []))
            if with_live:
                receipt["live"] = live_leg(probe, repo, exclude={port})
            return receipt, 0 if (class_missing == 0 and unregistered == 1
                                  and governed == 1) else 1
    finally:
        if child is not None and port is not None:
            child.terminate()
            try:
                receipt["child_exit"] = child.wait(timeout=15)
            except subprocess.TimeoutExpired:
                child.kill()
                receipt["child_exit"] = child.wait(timeout=15)
            time.sleep(0.2)
            receipt["port_closed"] = port not in listening_ports()
            if receipt["port_closed"] is False:
                receipt["error"] = "child port remained listening after teardown"


STUB_BOTH = """#!/usr/bin/env python3
import json, sys
reg = sys.argv[sys.argv.index('--registry') + 1]
port = 12345
declared = f'127.0.0.1:{port}' in open(reg).read()
registered = 'yes' if declared else 'no'
summary = {'probed': 1, 'model_endpoints': 1, 'governed': 1 if declared else 0,
           'unregistered': 0 if declared else 1, 'registry': 'ok'}
print(json.dumps({'listeners': [{'port': port, 'verdict': 'MODEL_OK', 'registered': registered}],
                  'summary': summary}))
"""
STUB_NO_CLASS = """#!/usr/bin/env python3
import json
print(json.dumps({'listeners': [{'port': 12345, 'verdict': 'MODEL_OK'}],
                  'summary': {'probed': 1, 'model_endpoints': 1}}))
"""
STUB_ERROR = """#!/usr/bin/env python3
import sys
print('stub probe failure', file=sys.stderr)
sys.exit(3)
"""


def selftest(work: Path) -> int:
    arms: list[tuple[str, bool, str]] = []
    root = work / "stubs"
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    stub_both = root / "probe-both.py"
    stub_no = root / "probe-noclass.py"
    stub_err = root / "probe-error.py"
    stub_both.write_text(STUB_BOTH)
    stub_no.write_text(STUB_NO_CLASS)
    stub_err.write_text(STUB_ERROR)

    repo = Path(__file__).resolve().parent.parent
    repo_ok = (repo / "registry/endpoint-consumers.tsv").is_file()

    def run(probe: Path) -> tuple[int, str]:
        import contextlib
        import io
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc, msg = stub_trial(repo, probe)
        return rc, (msg + "\n" + buf.getvalue()).strip()

    def arm(name: str, cond: bool, detail: str = "") -> None:
        arms.append((name, cond, detail))

    if not repo_ok:
        print("UNREGISTERED_CENSUS_SELFTEST repo registry absent")
        return 1
    rc, out = run(stub_both)
    arm("both-legs", rc == 0 and "unregistered=1 governed=1 class_missing=0" in out, out[-160:])
    rc, out = run(stub_no)
    arm("class-missing", rc == 0 and "class_missing=1" in out, out[-160:])
    rc, out = run(stub_err)
    arm("probe-error", rc == 2 and "probe leg A" in out, out[-160:])
    rc, out = run(root / "does-not-exist.py")
    arm("absent-probe", rc == 2 and "prerequisite absent" in out, out[-160:])

    failed = 0
    for name, ok, detail in arms:
        print(f"UNREGISTERED_CENSUS_SELFTEST {name} {'PASS' if ok else 'FAIL'}"
              + ("" if ok else " " + detail.replace("\n", " | ")))
        if not ok:
            failed += 1
    print(f"UNREGISTERED_CENSUS_SELFTEST pass={len(arms) - failed} fail={failed}")
    return 0 if failed == 0 else 1


def stub_trial(repo: Path, probe: Path) -> tuple[int, str]:
    """Stub-mode trial: no child, the fixture port is the stub's fixed 12345."""
    if not probe.is_file():
        print(f"UNREGISTERED_CENSUS port=12345 unregistered=0 governed=0 class_missing=0 "
              f"| prerequisite absent: {probe}")
        return 2, f"prerequisite absent: {probe}"
    work = Path(tempfile.mkdtemp(prefix="census-stub-", dir=os.environ.get("TMPDIR")))
    try:
        reg_a = work / "registry-without.tsv"
        reg_b = work / "registry-with.tsv"
        write_registry(reg_a, None)
        write_registry(reg_b, 12345)
        doc_a, rc_a = probe_json(probe, repo, reg_a, port=12345)
        doc_b, rc_b = probe_json(probe, repo, reg_b, port=12345)
        if "__error__" in doc_a or "__error__" in doc_b:
            detail = (doc_a.get("__error__") or doc_b.get("__error__"))
            print(f"UNREGISTERED_CENSUS port=12345 unregistered=0 governed=0 class_missing=0 "
                  f"| probe error: {detail}")
            return 2, "probe leg A: " + str(detail)
        class_a, sum_a = classify(doc_a, 12345)
        class_b, sum_b = classify(doc_b, 12345)
        class_missing = 0 if (class_a is not None and class_b is not None
                              and "governed" in sum_a and "unregistered" in sum_b) else 1
        unregistered = 1 if (class_a == "no" and class_b == "yes"
                             and sum_a.get("unregistered") == 1
                             and sum_a.get("governed") == 0) else 0
        governed = 1 if (class_a == "no" and class_b == "yes"
                         and sum_b.get("governed") == 1
                         and sum_b.get("unregistered") == 0) else 0
        print(f"UNREGISTERED_CENSUS port=12345 unregistered={unregistered} governed={governed} "
              f"class_missing={class_missing} rows={len(doc_a.get('listeners') or [])}")
        return 0, ""
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main() -> tuple[int, str]:
    ap = argparse.ArgumentParser(description="round-79 C3 unregistered-listener census")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--probe", default=None)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--work", default=None)
    ap.add_argument("--no-live", action="store_true")
    args = ap.parse_args()
    repo = Path(args.repo).resolve()
    probe = Path(args.probe).resolve() if args.probe else repo / "tools/kama-probe.sh"

    if args.selftest:
        base = Path(args.work) if args.work else Path(tempfile.mkdtemp(
            prefix="selftest-", dir=os.environ.get("TMPDIR")))
        base.mkdir(parents=True, exist_ok=True)
        try:
            return selftest(base), ""
        finally:
            shutil.rmtree(base, ignore_errors=True)

    work = Path(args.work) if args.work else Path(tempfile.mkdtemp(
        prefix="census-", dir=os.environ.get("TMPDIR")))
    work.mkdir(parents=True, exist_ok=True)
    receipt, code = trial(repo, probe, work, with_live=not args.no_live)
    if "port" in receipt:
        print(f"UNREGISTERED_CENSUS port={receipt['port']} "
              f"unregistered={receipt.get('unregistered', 0)} "
              f"governed={receipt.get('governed', 0)} "
              f"class_missing={receipt.get('class_missing', 1)} "
              f"rows={receipt.get('rows', 0)}")
    if receipt.get("live") and "unregistered_ports" in receipt["live"]:
        live = receipt["live"]
        print(f"UNREGISTERED_CENSUS_LIVE model_endpoints={live.get('model_endpoints')} "
              f"governed={live.get('governed')} unregistered={live.get('unregistered')} "
              f"ports={','.join(str(p) for p in live['unregistered_ports']) or '-'}")
    if receipt.get("error"):
        print(f"UNREGISTERED_CENSUS_ERROR {receipt['error']}")
    if receipt.get("port_closed") is False:
        code = 2
    if code == 0 and receipt.get("port_closed") is None:
        code = 2
    return code, ""


if __name__ == "__main__":
    code, message = main()
    if message:
        print(message)
    sys.exit(code)
