#!/usr/bin/env python3
"""EX01HeldOutCells - held-out unloadable-router-model cells for round 89.

Runs lane-owned b12177 llama-server router children on loopback free ports, builds one
held-out fixture per cell, records the router status BEFORE grading, runs the frozen
base probe (56174a1f) and the measured probe M (4f9eacf7) from a cwd different from the
router's, then runs the oracle (real POST /v1/chat/completions, max_tokens 2) and maps
it exactly as plans/round-89-claims.md C1: 200 -> MODEL_OK; 400 with "model is not
loaded" or 500 with "failed to load" -> MODEL_UNLOADED; anything else -> no verdict.

Classification: HARM = base agreed with the oracle and M does not; FIX = M agrees and
base does not; LIMIT = both disagree; AGREE = both agree; INDETERMINATE = no oracle.

Usage: cells.py --probe-base FILE --probe-M FILE --work DIR --out DIR [--server PATH]
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import signal
import stat
import subprocess
import sys
import threading
import time
import urllib.error
from pathlib import Path

HELPER = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round89-unloadable-cells.py")
spec = importlib.util.spec_from_file_location("uc", HELPER)
uc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(uc)

SERVER = uc.SERVER
MODEL = uc.MODEL
SPLIT_BIN = SERVER.parent / "llama-gguf-split"


def sha256(p: Path) -> str:
    with p.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def start_router(server: Path, args: list, cwd: Path, log: Path) -> int:
    """Start a router child in its own session; identity-check it lists only our entry."""
    port = uc.free_port()
    p = subprocess.Popen([str(server), "--host", "127.0.0.1", "--port", str(port)] + args,
                         stdout=log.open("w"), stderr=subprocess.STDOUT, cwd=cwd,
                         start_new_session=True)
    uc.CHILDREN.append(p)
    for _ in range(160):
        if p.poll() is not None:
            raise RuntimeError(f"router child exited rc={p.returncode} (log {log})")
        try:
            ents = uc.entries(port)
            if ents:
                return port
        except (OSError, uc.CannotEvaluate, ValueError):
            pass
        time.sleep(0.25)
    raise RuntimeError("router child never answered GET /v1/models")


def props(port: int) -> dict:
    code, txt = uc.http("GET", port, "/props", timeout=5)
    try:
        return json.loads(txt) if code == 200 else {}
    except ValueError:
        return {}


def oracle(port: int, mid: str, timeout: float) -> tuple[str | None, str, str]:
    """Real completion. Returns (verdict|None, http-detail, message)."""
    try:
        code, txt = uc.http("POST", port, "/v1/chat/completions",
                            {"model": mid, "messages": [{"role": "user", "content": "hi"}],
                             "max_tokens": 2}, timeout=timeout)
    except Exception as e:  # timeout / reset / no reply
        return None, f"no-http-response:{type(e).__name__}", str(e)[:160]
    msg = ""
    try:
        doc = json.loads(txt)
        err = doc.get("error") if isinstance(doc, dict) else None
        if isinstance(err, dict):
            msg = str(err.get("message", ""))
    except ValueError:
        pass
    if code == 200:
        return "MODEL_OK", f"http=200", msg
    if code == 400 and "model is not loaded" in txt:
        return "MODEL_UNLOADED", "http=400", msg or "model is not loaded"
    if code == 500 and "failed to load" in txt:
        return "MODEL_UNLOADED", "http=500", msg or "failed to load"
    return None, f"http={code}", msg or txt[:160]


def run_probe(probe: Path, port: int, mid: str, env: dict, cwd: Path, timeout: float = 30):
    t0 = time.monotonic()
    try:
        p = subprocess.run(["bash", str(probe), "check", "--port", str(port), "--expect", mid,
                            "--json", "--timeout", "3", "--connect-timeout", "1"],
                           capture_output=True, text=True, timeout=timeout, env=env, cwd=cwd)
    except subprocess.TimeoutExpired:
        return "PROBE_TIMEOUT", f"no output within {timeout}s", "timeout", time.monotonic() - t0
    el = time.monotonic() - t0
    try:
        doc = json.loads(p.stdout)
        row = (doc.get("consumers") or doc.get("rows") or doc.get("results") or [])[0]
        return row["verdict"], row.get("reason", "?"), str(p.returncode), el
    except Exception:
        return "PROBE_UNPARSEABLE", p.stdout[:120] + "|" + p.stderr[:120], str(p.returncode), el


def write_preset(path: Path, mid: str, model: str, extra: dict | None = None):
    lines = [f"[{mid}]", f"model = {model}"]
    for k, v in (extra or {}).items():
        lines.append(f"{k} = {v}")
    path.write_text("\n".join(lines) + "\n")


def fixture_dir(base: Path, cid: str) -> Path:
    d = base / cid
    shutil.rmtree(d, ignore_errors=True)
    (d / "router" / "models").mkdir(parents=True)
    (d / "fixtures").mkdir()
    (d / "probe-cwd").mkdir()
    return d


def build_cells(base: Path) -> list[dict]:
    raw = MODEL.read_bytes()
    cells: list[dict] = []

    def add(cid, model_arg, note, extra=None, kind="abs", model_check=None):
        cells.append({"cid": cid, "model_arg": model_arg, "note": note, "extra": extra,
                      "kind": kind, "model_check": model_check})

    # 01 last byte cut
    d = fixture_dir(base, "01-last-byte-cut")
    f = d / "fixtures" / "cut.gguf"
    f.write_bytes(raw[:-1])
    add("01-last-byte-cut", str(f), f"stories260K with only the last byte cut (size {len(raw)-1})")

    # 02 directory at the model path
    d = fixture_dir(base, "02-directory-at-path")
    f = d / "fixtures" / "dir.gguf"
    f.mkdir()
    add("02-directory-at-path", str(f), "a directory whose name ends in .gguf")

    # 03 FIFO at the model path. b12177 blocks in startup if the FIFO already exists
    # (open() waits for a partner before the listener binds), so the FIFO is created
    # only after the router has listed the entry; the probe then sees a non-regular file.
    d = fixture_dir(base, "03-fifo-at-path")
    f = d / "fixtures" / "fifo.gguf"
    add("03-fifo-at-path", str(f), "a FIFO named .gguf, created after listing; probe must not block",
        kind="lazy_fifo")
    cells[-1]["lazy_fifo"] = str(f)

    # 03b same FIFO, but a writer joins so a real completion can get past open() and reach
    # the loader's own failure; gives the FIFO class an oracle verdict instead of a hang.
    d = fixture_dir(base, "03b-fifo-with-writer")
    f = d / "fixtures" / "fifo.gguf"
    add("03b-fifo-with-writer", str(f),
        "a FIFO named .gguf, created after listing; a writer joins before the completion",
        kind="lazy_fifo")
    cells[-1]["lazy_fifo"] = str(f)
    cells[-1]["fifo_writer"] = True

    # 04 chmod 000 valid file
    d = fixture_dir(base, "04-chmod000")
    f = d / "fixtures" / "noread.gguf"
    f.write_bytes(raw)
    f.chmod(0o000)
    add("04-chmod000", str(f), "valid stories260K bytes, mode 000")

    # 05 missing mmproj with a valid model
    d = fixture_dir(base, "05-missing-mmproj")
    f = d / "fixtures" / "good.gguf"
    f.write_bytes(raw)
    add("05-missing-mmproj", str(f), "valid model, preset mmproj = absent path",
        extra={"mmproj": str(d / "fixtures" / "absent-mmproj.gguf")})

    # 06 version field patched to 2
    d = fixture_dir(base, "06-version-2")
    f = d / "fixtures" / "v2.gguf"
    f.write_bytes(b"GGUF" + (2).to_bytes(4, "little") + raw[8:])
    add("06-version-2", str(f), "GGUF version field patched from 3 to 2; loader may accept")

    # 07 version field patched to 0x03000000 (byte-swapped)
    d = fixture_dir(base, "07-version-byteswapped")
    f = d / "fixtures" / "vswapped.gguf"
    f.write_bytes(b"GGUF" + (0x03000000).to_bytes(4, "little") + raw[8:])
    add("07-version-byteswapped", str(f), "version u32 = 0x03000000 (3 written big-endian)")

    # 08 split first shard, second shard missing
    d = fixture_dir(base, "08-split-missing-shard")
    sd = d / "fixtures" / "split"
    sd.mkdir()
    src = d / "fixtures" / "src.gguf"
    src.write_bytes(raw)
    r = subprocess.run([str(SPLIT_BIN), "--split", "--split-max-tensors", "4",
                        str(src), str(sd / "out")], capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        raise RuntimeError(f"llama-gguf-split failed rc={r.returncode}: {r.stderr[-300:]}")
    shards = sorted(sd.glob("out-*.gguf"))
    first = shards[0]
    # keep ONLY the first shard; its siblings are absent
    for s in shards[1:]:
        s.unlink()
    src.unlink()
    add("08-split-missing-shard", str(first),
        f"{len(shards)} shards written; only {first.name} kept, the rest deleted")

    # 09a symlink to a valid file
    d = fixture_dir(base, "09a-symlink-valid")
    tgt = d / "fixtures" / "real.gguf"
    tgt.write_bytes(raw)
    f = d / "fixtures" / "link.gguf"
    f.symlink_to(tgt)
    add("09a-symlink-valid", str(f), "symlink -> valid stories260K copy")

    # 09b dangling symlink
    d = fixture_dir(base, "09b-symlink-dangling")
    f = d / "fixtures" / "dangle.gguf"
    f.symlink_to(d / "fixtures" / "never-there.gguf")
    add("09b-symlink-dangling", str(f), "symlink -> absent target")

    # 10a preset model with a relative path, file present in the router cwd
    d = fixture_dir(base, "10a-relative-valid")
    (d / "router" / "rel.gguf").write_bytes(raw)
    add("10a-relative-valid", "rel.gguf",
        "preset model = rel.gguf, file present in router cwd (loadable)", kind="rel")

    # 10b preset model with a relative path that does not exist
    d = fixture_dir(base, "10b-relative-missing")
    add("10b-relative-missing", "rel-absent.gguf",
        "preset model = rel-absent.gguf, absent in router cwd", kind="rel")

    return cells


def fifo_startup_check(base: Path, logdir: Path) -> dict:
    """Does b12177 bind at all when a preset model path is a FIFO present at startup?"""
    d = base / "03a-fifo-at-startup"
    shutil.rmtree(d, ignore_errors=True)
    (d / "router" / "models").mkdir(parents=True)
    (d / "fixtures").mkdir()
    fifo = d / "fixtures" / "fifo.gguf"
    os.mkfifo(fifo)
    ini = d / "router" / "presets.ini"
    write_preset(ini, "cell", str(fifo))
    port = uc.free_port()
    log = d / "router" / "router.log"
    p = subprocess.Popen([str(SERVER), "--host", "127.0.0.1", "--port", str(port), "--models-max", "1",
                          "--models-dir", str(d / "router" / "models"), "--models-preset", str(ini)],
                         stdout=log.open("w"), stderr=subprocess.STDOUT, cwd=d / "router",
                         start_new_session=True)
    uc.CHILDREN.append(p)
    t0 = time.monotonic()
    bound = False
    for _ in range(32):  # 8 s bounded
        if p.poll() is not None:
            break
        try:
            uc.http("GET", port, "/props", timeout=1)
            bound = True
            break
        except Exception:
            time.sleep(0.25)
    rec = {"cid": "03a-fifo-at-startup", "note": "FIFO preset model present before startup",
           "bound_within_s": None if not bound else round(time.monotonic() - t0, 2),
           "alive_after_8s": p.poll() is None, "exit_rc": p.poll()}
    if p.poll() is None:
        try:
            rec["wchan"] = Path(f"/proc/{p.pid}/wchan").read_text().strip()
            rec["state"] = Path(f"/proc/{p.pid}/status").read_text().split("State:")[1].split("\n")[0].strip()
        except OSError as e:
            rec["wchan_error"] = str(e)
    uc.kill_children()
    try:
        shutil.copyfile(log, logdir / "03a-fifo-at-startup.router.log")
    except OSError:
        pass
    return rec


def run_cell(cell: dict, base: Path, probes: dict, logdir: Path) -> dict:
    cid = cell["cid"]
    d = base / cid
    mid = "cell"
    ini = d / "router" / "presets.ini"
    write_preset(ini, mid, cell["model_arg"], cell["extra"])
    router_dir = d / "router"
    log = router_dir / "router.log"
    port = start_router(SERVER, ["--models-max", "1", "--models-dir", str(router_dir / "models"),
                                 "--models-preset", str(ini)], router_dir, log)
    out = {"cid": cid, "note": cell["note"], "port": port}
    try:
        pr = props(port)
        out["router"] = {"role": pr.get("role"), "models_autoload": pr.get("models_autoload")}
        before = uc.entries(port)
        st = before.get(mid)
        if st is None or (st.get("args") or [])[1:] is None:
            raise RuntimeError(f"entry {mid} not listed; entries={list(before)}")
        out["status_before"] = {"value": st.get("value"), "failed": st.get("failed"),
                                "args": st.get("args")}
        if cell.get("lazy_fifo"):
            os.mkfifo(cell["lazy_fifo"])
            out["fifo_created_after_listing"] = True
        env = dict(os.environ, TMPDIR=str(d / "probe-cwd"))
        pcwd = d / "probe-cwd"
        for tag in ("base", "M"):
            v, reason, rc, el = run_probe(probes[tag], port, mid, env, pcwd,
                                          timeout=60 if cid != "03-fifo-at-path" else 30)
            out[tag] = {"verdict": v, "reason": reason, "rc": rc, "elapsed_s": round(el, 2)}
        writer = {"fd": None}
        if cell.get("fifo_writer"):
            def _w(p=cell["lazy_fifo"], box=writer):
                try:
                    box["fd"] = os.open(p, os.O_WRONLY)
                except OSError as e:
                    box["err"] = str(e)
            th = threading.Thread(target=_w, daemon=True)
            th.start()
            th.join(0.5)
            out["writer_joined"] = writer["fd"] is not None
            out["writer_pending"] = writer["fd"] is None and "err" not in writer
        ov, detail, msg = oracle(port, mid, 25 if cid != "03-fifo-at-path" else 12)
        out["oracle"] = {"verdict": ov, "detail": detail, "message": msg}
        if writer["fd"] is not None:
            try:
                os.close(writer["fd"])
            except OSError:
                pass
            out["writer_closed_after_oracle"] = True
        try:
            after = uc.entries(port).get(mid, {})
            out["status_after"] = {"value": after.get("value"), "failed": after.get("failed")}
        except Exception:
            out["status_after"] = None
    finally:
        uc.kill_children()
        try:
            shutil.copyfile(log, logdir / f"{cid}.router.log")
        except OSError:
            pass
    ov = out["oracle"]["verdict"]
    b, m = out["base"]["verdict"], out["M"]["verdict"]
    if ov is None:
        cls = "INDETERMINATE"
    elif b == ov and m == ov:
        cls = "AGREE"
    elif b == ov and m != ov:
        cls = "HARM"
    elif m == ov and b != ov:
        cls = "FIX"
    else:
        cls = "LIMIT"
    out["class"] = cls
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe-base", type=Path, required=True)
    ap.add_argument("--probe-M", type=Path, required=True)
    ap.add_argument("--work", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--server", type=Path, default=SERVER)
    a = ap.parse_args()
    signal.signal(signal.SIGTERM, uc.on_signal)
    signal.signal(signal.SIGINT, uc.on_signal)
    a.work.mkdir(parents=True, exist_ok=True)
    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / "logs").mkdir(exist_ok=True)
    for p in (a.server,):
        if not p.is_file():
            print(f"CELLS could-not-evaluate: prerequisite absent {p}")
            return 2
    if sha256(a.server) != uc.SERVER_PIN:
        print("CELLS could-not-evaluate: server sha256 mismatch")
        return 2
    if sha256(MODEL) != uc.MODEL_SHA:
        print("CELLS could-not-evaluate: model sha256 mismatch")
        return 2
    print(f"CELLS probes base_sha256={sha256(a.probe_base)} M_sha256={sha256(a.probe_M)} "
          f"server_sha256={sha256(a.server)} model_sha256={sha256(MODEL)}")
    cells = build_cells(a.work)
    rows = []
    rc = 0
    startup = None
    try:
        startup = fifo_startup_check(a.work, a.out / "logs")
        print(f"CELL 03a-fifo-at-startup bound_within_s={startup['bound_within_s']} "
              f"alive_after_8s={startup['alive_after_8s']} wchan={startup.get('wchan')} "
              f"state={startup.get('state')}")
        for cell in cells:
            try:
                row = run_cell(cell, a.work, {"base": a.probe_base, "M": a.probe_M}, a.out / "logs")
            except Exception as e:
                print(f"CELL {cell['cid']} could-not-evaluate: {type(e).__name__}: {e}")
                rc = 2
                continue
            rows.append(row)
            print(f"CELL {row['cid']} class={row['class']} "
                  f"status_before={row['status_before']['value']}/failed={row['status_before']['failed']} "
                  f"base={row['base']['verdict']}/{row['base']['reason']} "
                  f"M={row['M']['verdict']}/{row['M']['reason']} "
                  f"oracle={row['oracle']['verdict']}/{row['oracle']['detail']} "
                  f"msg={row['oracle']['message']!r} "
                  f"t_base={row['base']['elapsed_s']}s t_M={row['M']['elapsed_s']}s")
    finally:
        uc.kill_children()
    with (a.out / "cells.json").open("w") as f:
        json.dump({"fifo_startup": startup, "cells": rows}, f, indent=1)
        f.write("\n")
    counts = {}
    for r in rows:
        counts[r["class"]] = counts.get(r["class"], 0) + 1
    print("CELLS_TABLE")
    for r in rows:
        print(f"{r['cid']}\t{r['status_before']['value']}\t{r['base']['verdict']}\t"
              f"{r['M']['verdict']}\t{r['oracle']['verdict']}\t{r['class']}")
    print(f"CELLS cells={len(rows)} " + " ".join(f"{k}={counts[k]}" for k in sorted(counts)))
    return 1 if counts.get("HARM") else rc


if __name__ == "__main__":
    sys.exit(main())
