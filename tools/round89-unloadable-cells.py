#!/usr/bin/env python3
"""round89-unloadable-cells.py - round-89 C1 (operability) frozen counter.

PREDICATE (frozen: plans/round-89-claims.md section C1):

    `python3 tools/round89-unloadable-cells.py --repo <lane> --rev <R> --work <scratch>` prints
    `ROUTER_UNLOADABLE cells=11 mismatches=0 positive_mismatches=0 ...` and exits 0: on every one of
    the 11 live cells below, the verdict `tools/kama-probe.sh` (bytes at <R>) prints for the router
    entry equals the verdict the router's own answer to a real request implies (the oracle).

Oracle (frozen; S583 server-models.cpp @ b12177 lines 1641, 1956, 1962): a real
`POST /v1/chat/completions` for the entry's id, max_tokens 2:
    HTTP 200                                   -> MODEL_OK
    HTTP 400 and body has "model is not loaded"  -> MODEL_UNLOADED
    HTTP 500 and body has "failed to load"       -> MODEL_UNLOADED
    anything else                              -> could-not-evaluate (exit 2), never a verdict
The expected verdict of every cell is the oracle's answer at run time; no cell carries a canned
expectation.

Cells - lane-owned llama-server router children of the pinned current release b12177
(`--server`, sha256 pinned below) on 127.0.0.1 free ports, model stories260K (sha256 pinned):
  child A  default autoload, --models-max 1, absolute --models-dir + --models-preset
    U1-missing-preset       preset entry whose `model =` path does not exist
    U2-not-gguf             a .gguf file holding plain text
    U3-bad-header           GGUF magic + version 3 + 4096 deterministic pseudo-random bytes
    U4-truncated-half       the first half of stories260K's bytes
    U5-deleted-after-list   a valid copy, listed, then deleted before the probe
    P1-valid-unloaded       a valid copy, unloaded (autoload loads it)
    P2-valid-loaded         the same entry after P1's request loaded it
  child B  --no-models-autoload, absolute --models-dir
    N1-valid-unloaded-noautoload
    N2-bad-header-noautoload
  child C  --no-models-autoload --sleep-idle-seconds 2
    P3-valid-sleeping       loaded through POST /models/load, then idle past the sleep timeout
  child D  default autoload, RELATIVE --models-dir (router cwd differs from the probe's cwd)
    P4-relative-unloaded
`positive_mismatches` counts mismatches on P1-P4, N1, N2 (the cells the round-88 rule already
grades by the oracle); it is printed separately because a mismatch there is harm.

Child identity (r88 SN01): each child's GET /v1/models must list only entries whose
status.args carry a path under this run's private work dir (or the relative dir for child D)
before any cell is graded; otherwise exit 2. Children run in their own session and are killed
by process group (SIGTERM, then SIGKILL) on every exit path, including SIGTERM/SIGINT to this
counter. Environment faults (binary/model absent or digest mismatch, child never answers,
oracle inconclusive, probe output unparseable) exit 2.

Usage: round89-unloadable-cells.py --repo DIR --rev REV --work DIR [--probe-file FILE]
       [--server PATH]
Exit: 0 all 11 cells agree | 1 mismatches | 2 could-not-evaluate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

SERVER = Path.home() / ".local/opt/llama-b12177/llama-server"
SERVER_PIN = "ba272ee3446d9b98c9150c79667e6a8b217f25ee58ce0c6156cc96d2b5b362b0"
MODEL = Path.home() / ".cache/kama-shokunin/models/stories260K.gguf"
MODEL_SHA = "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"
POSITIVE = ("P1-valid-unloaded", "P2-valid-loaded", "P3-valid-sleeping", "P4-relative-unloaded",
            "N1-valid-unloaded-noautoload", "N2-bad-header-noautoload")
CELLS = 11


class CannotEvaluate(Exception):
    pass


CHILDREN: list[subprocess.Popen] = []


def kill_children(*_a):
    for p in CHILDREN:
        if p.poll() is None:
            try:
                os.killpg(p.pid, signal.SIGTERM)
                p.wait(timeout=15)
            except Exception:
                try:
                    os.killpg(p.pid, signal.SIGKILL)
                    p.wait(timeout=5)
                except Exception:
                    pass
    CHILDREN.clear()


def on_signal(signum, _frame):
    kill_children()
    sys.exit(128 + signum)


def sha256(path: Path) -> str:
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def free_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


def http(method: str, port: int, path: str, body=None, timeout=60):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"http://127.0.0.1:{port}{path}", data=data, method=method,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")


def entries(port: int) -> dict:
    code, txt = http("GET", port, "/v1/models", timeout=5)
    if code != 200:
        raise CannotEvaluate(f"GET /v1/models -> {code}")
    return {e["id"]: (e.get("status") or {}) for e in json.loads(txt).get("data", [])}


def start(server: Path, args: list, cwd: Path, log: Path, owned: str) -> int:
    port = free_port()
    p = subprocess.Popen([str(server), "--host", "127.0.0.1", "--port", str(port)] + args,
                         stdout=log.open("w"), stderr=subprocess.STDOUT, cwd=cwd,
                         start_new_session=True)
    CHILDREN.append(p)
    for _ in range(120):
        if p.poll() is not None:
            raise CannotEvaluate(f"router child exited rc={p.returncode} (log {log.name})")
        try:
            ents = entries(port)
            break
        except (OSError, CannotEvaluate, ValueError):
            time.sleep(0.25)
    else:
        raise CannotEvaluate("router child never answered GET /v1/models")
    # identity: every listed entry is ours (its --model path lies under our private dir)
    for mid, st in ents.items():
        a = st.get("args") or []
        paths = [a[i + 1] for i, x in enumerate(a[:-1]) if x in ("--model", "-m")]
        if not paths or not all(owned in q for q in paths):
            raise CannotEvaluate(f"port {port}: entry {mid!r} is not owned by this run")
    return port


def wait_status(port: int, mid: str, want: str, secs: float = 30):
    end = time.time() + secs
    while time.time() < end:
        if entries(port).get(mid, {}).get("value") == want:
            return
        time.sleep(0.25)
    raise CannotEvaluate(f"{mid} never reached status {want}")


def oracle(port: int, mid: str) -> tuple[str, int]:
    code, txt = http("POST", port, "/v1/chat/completions",
                     {"model": mid, "messages": [{"role": "user", "content": "hi"}], "max_tokens": 2})
    if code == 200:
        return "MODEL_OK", code
    if code == 400 and "model is not loaded" in txt:
        return "MODEL_UNLOADED", code
    if code == 500 and "failed to load" in txt:
        return "MODEL_UNLOADED", code
    raise CannotEvaluate(f"oracle inconclusive for {mid}: http={code} body={txt[:160]!r}")


def run_probe(probe: Path, port: int, mid: str, env: dict, cwd: Path) -> tuple[str, str]:
    p = subprocess.run(["bash", str(probe), "check", "--port", str(port), "--expect", mid, "--json",
                        "--timeout", "3", "--connect-timeout", "1"],
                       capture_output=True, text=True, timeout=120, env=env, cwd=cwd)
    try:
        doc = json.loads(p.stdout)
        row = (doc.get("consumers") or doc.get("rows") or doc.get("results") or [])[0]
        return row["verdict"], row.get("reason", "?")
    except Exception:
        raise CannotEvaluate(f"probe output unparseable (exit {p.returncode}): {p.stdout[:160]!r}")


def build_models(d: Path):
    d.mkdir(parents=True)
    raw = MODEL.read_bytes()
    (d / "m1.gguf").write_bytes(raw)
    (d / "gone.gguf").write_bytes(raw)
    (d / "notgguf.gguf").write_bytes(b"this is not a gguf model file\n" * 64)
    noise = b"".join(hashlib.sha256(b"kama-r89-%d" % i).digest() for i in range(128))
    (d / "badhdr.gguf").write_bytes(b"GGUF" + (3).to_bytes(4, "little") + noise)
    (d / "trunc.gguf").write_bytes(raw[: len(raw) // 2])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--work", type=Path, required=True)
    ap.add_argument("--probe-file", type=Path)
    ap.add_argument("--server", type=Path, default=SERVER)
    a = ap.parse_args()
    signal.signal(signal.SIGTERM, on_signal)
    signal.signal(signal.SIGINT, on_signal)
    rows = []
    try:
        rev = subprocess.run(["git", "-C", str(a.repo), "rev-parse", "--verify", a.rev + "^{commit}"],
                             capture_output=True, text=True)
        if rev.returncode != 0:
            raise CannotEvaluate(f"unresolvable --rev {a.rev}")
        rev = rev.stdout.strip()
        for path, want in ((a.server, SERVER_PIN), (MODEL, MODEL_SHA)):
            if not path.is_file():
                raise CannotEvaluate(f"prerequisite absent: {path}")
            if sha256(path) != want:
                raise CannotEvaluate(f"prerequisite sha256 mismatch: {path}")
        a.work.mkdir(parents=True, exist_ok=True)
        work = Path(tempfile.mkdtemp(prefix="r89-unloadable-", dir=a.work)).resolve()
        try:
            probe = work / "kama-probe.sh"
            if a.probe_file:
                probe.write_bytes(a.probe_file.read_bytes())
                mode = "override"
            else:
                probe.write_bytes(subprocess.run(["git", "-C", str(a.repo), "show", f"{rev}:tools/kama-probe.sh"],
                                                 capture_output=True, check=True).stdout)
                mode = "rev"
            probe_sha = sha256(probe)
            pcwd = work / "probe-cwd"
            pcwd.mkdir()
            env = dict(os.environ, TMPDIR=str(pcwd))
            owned = str(work)

            # child A
            da = work / "a"
            build_models(da / "models")
            ini = da / "presets.ini"
            ini.write_text(f"[absent]\nmodel = {da}/absent-model.gguf\n")
            pa = start(a.server, ["--models-max", "1", "--models-dir", str(da / "models"),
                                  "--models-preset", str(ini)], da, da / "router.log", owned)
            listed = entries(pa)
            for need in ("absent", "notgguf", "badhdr", "trunc", "gone", "m1"):
                if listed.get(need, {}).get("value") != "unloaded":
                    raise CannotEvaluate(f"child A: {need} not listed unloaded")
            (da / "models" / "gone.gguf").unlink()
            for cid, mid in (("U1-missing-preset", "absent"), ("U2-not-gguf", "notgguf"),
                             ("U3-bad-header", "badhdr"), ("U4-truncated-half", "trunc"),
                             ("U5-deleted-after-list", "gone"), ("P1-valid-unloaded", "m1")):
                got = run_probe(probe, pa, mid, env, pcwd)
                rows.append((cid, *oracle(pa, mid), *got))
            wait_status(pa, "m1", "loaded")
            got = run_probe(probe, pa, "m1", env, pcwd)
            rows.append(("P2-valid-loaded", *oracle(pa, "m1"), *got))
            kill_children()

            # child B
            db = work / "b"
            (db / "models").mkdir(parents=True)
            shutil.copyfile(da / "models" / "m1.gguf", db / "models" / "m1.gguf")
            shutil.copyfile(da / "models" / "badhdr.gguf", db / "models" / "badhdr.gguf")
            pb = start(a.server, ["--no-models-autoload", "--models-max", "1",
                                  "--models-dir", str(db / "models")], db, db / "router.log", owned)
            for cid, mid in (("N1-valid-unloaded-noautoload", "m1"), ("N2-bad-header-noautoload", "badhdr")):
                got = run_probe(probe, pb, mid, env, pcwd)
                rows.append((cid, *oracle(pb, mid), *got))
            kill_children()

            # child C
            dc = work / "c"
            (dc / "models").mkdir(parents=True)
            shutil.copyfile(da / "models" / "m1.gguf", dc / "models" / "m1.gguf")
            pc = start(a.server, ["--no-models-autoload", "--sleep-idle-seconds", "2", "--models-max", "1",
                                  "--models-dir", str(dc / "models")], dc, dc / "router.log", owned)
            http("POST", pc, "/models/load", {"model": "m1"})
            wait_status(pc, "m1", "loaded")
            wait_status(pc, "m1", "sleeping", 40)
            got = run_probe(probe, pc, "m1", env, pcwd)
            rows.append(("P3-valid-sleeping", *oracle(pc, "m1"), *got))
            kill_children()

            # child D: relative --models-dir; the probe runs from a different cwd
            dd = work / "d"
            (dd / "rel").mkdir(parents=True)
            shutil.copyfile(da / "models" / "m1.gguf", dd / "rel" / "m1.gguf")
            pd = start(a.server, ["--models-max", "1", "--models-dir", "rel"], dd, dd / "router.log", "rel/")
            got = run_probe(probe, pd, "m1", env, pcwd)
            rows.append(("P4-relative-unloaded", *oracle(pd, "m1"), *got))
            kill_children()
        finally:
            kill_children()
            shutil.rmtree(work, ignore_errors=True)
    except CannotEvaluate as e:
        kill_children()
        for r in rows:
            print(f"ROUTER_UNLOADABLE_CELL {r[0]} oracle={r[1]} http={r[2]} probe={r[3]} reason={r[4]}")
        print(f"ROUTER_UNLOADABLE could-not-evaluate: {e}")
        return 2
    bad = pos = 0
    for cid, exp, code, got, reason in rows:
        ok = exp == got
        bad += not ok
        pos += (not ok) and cid in POSITIVE
        print(f"ROUTER_UNLOADABLE_CELL {cid} oracle={exp} http={code} probe={got} reason={reason} ok={int(ok)}")
    print(f"ROUTER_UNLOADABLE cells={len(rows)} mismatches={bad} positive_mismatches={pos} "
          f"probe={mode} probe_sha256={probe_sha} server_sha256={SERVER_PIN} rev={rev}")
    return 0 if bad == 0 and len(rows) == CELLS else 1


if __name__ == "__main__":
    sys.exit(main())
