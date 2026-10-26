#!/usr/bin/env python3
"""x1concurrent-observe3.py - round-49 seat X1Concurrent falsification harness.

Hypothesis under test (frozen before running): three witnessed replays of the
committed round-48 receipts 1, 2 and 3, started at once in separate work and
witness dirs, each write their own ready.json with distinct ports and pids,
each pid's /proc/<pid>/exe hashes to
35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0, and after
releasing all three no listener or llama-server remains.

Method (observer only; never trusts the replays):
  * extract the lane tree at --tip with `git archive` (tools/receipts at the
    measured commit, no clone worktree dependence);
  * spawn three `tools/kama-live-replay.py --witness-dir ... --witness-timeout
    ...` processes back to back (milliseconds apart), each with its own
    --work, witness dir, HOME, XDG_CACHE_HOME and TMPDIR;
  * wait for all three ready.json files, then read them and check, per run:
      schema kama-live-witness/v1, distinct ports, distinct pids,
      /proc/<pid>/exe sha256 == frozen server digest,
      a LISTEN loopback socket on the announced port owned by that pid,
      /proc/<pid>/cmdline `-m` hashes to the frozen model and `--port` equals
      the announced port, GET /health answers 200;
  * drop all three release files, wait for the replays, then check:
      each replay exit 0 / match true / rerun witness.released true and its
      witness.port+pid equal what the observer saw; each pid is gone; each
      port refuses connections; no LISTEN socket on those ports exists for any
      pid; and no llama-server process (exe digest or argv) exists that was not
      already running before the trial.

Exit 0 = every clause held (hypothesis not falsified by this trial);
1 = a clause failed (falsified; printed as FAIL lines); 2 = could not evaluate.
Kills only processes it started (process group of each replay).
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import shutil
import signal
import socket
import subprocess
import sys
import tarfile
import time
import traceback
import urllib.request

SERVER_SHA = "35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0"
MODEL_SHA = "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"
RECEIPTS = tuple(f".ufo/waves/round-48/c2/live/receipt-{n}.json" for n in (1, 2, 3))
REPLAY = "tools/kama-live-replay.py"
WITNESS_TIMEOUT = 180.0
READY_WAIT = 900.0
EXIT_WAIT = 300.0

results: list[str] = []          # human-readable evidence lines
fails: list[str] = []            # falsifying observations
detail: list[str] = []


def say(line):
    print(line, flush=True)
    results.append(line)


def bad(line):
    fails.append(line)
    say(f"FAIL {line}")


def sha_file(path):
    h = hashlib.sha256()
    try:
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
    except OSError:
        return None
    return h.hexdigest()


def load(path):
    try:
        with open(path) as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def listen_inodes(port):
    """LISTEN socket inodes on loopback:<port> from /proc/net/tcp{,6}."""
    out = set()
    for name in ("/proc/net/tcp", "/proc/net/tcp6"):
        try:
            with open(name) as fh:
                rows = fh.read().splitlines()[1:]
        except OSError:
            continue
        for row in rows:
            f = row.split()
            if len(f) < 10 or f[3] != "0A":
                continue
            addr, hport = f[1].rsplit(":", 1)
            if int(hport, 16) != port:
                continue
            if name.endswith("tcp6"):
                if addr not in ("00000000000000000000000001000000",
                                "0000000000000000FFFF00000100007F"):
                    continue
            elif not (len(addr) == 8 and addr.upper().endswith("7F")):
                continue
            out.add(f[9])
    return out


def pid_socket_inodes(pid):
    out = set()
    try:
        for fd in os.listdir(f"/proc/{pid}/fd"):
            try:
                link = os.readlink(f"/proc/{pid}/fd/{fd}")
            except OSError:
                continue
            if link.startswith("socket:["):
                out.add(link[8:-1])
    except OSError:
        pass
    return out


def pid_alive(pid):
    try:
        with open(f"/proc/{pid}/stat") as fh:
            state = fh.read().rsplit(")", 1)[1].split()[0]
        return state not in ("Z", "X")
    except (OSError, IndexError):
        return False


def port_refuses(port):
    s = socket.socket()
    s.settimeout(2)
    try:
        s.connect(("127.0.0.1", port))
        return False
    except OSError:
        return True
    finally:
        s.close()


def health(port):
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open(f"http://127.0.0.1:{port}/health", timeout=5) as r:
            return r.status, json.loads(r.read(1 << 16))
    except Exception as exc:  # noqa: BLE001 - evidence, not control flow
        return None, f"{type(exc).__name__}: {exc}"


def argv_of(pid):
    try:
        with open(f"/proc/{pid}/cmdline", "rb") as fh:
            return [a.decode("utf-8", "replace") for a in fh.read().split(b"\0") if a]
    except OSError:
        return []


def server_pids():
    """pids whose exe digest is the frozen server or whose argv[0] names it.

    The host is shared with sibling seats, so each entry carries the resolved
    exe path: a leftover is attributed to this trial only when it lives under
    this trial's scratch (or is one of the pids the trial recorded)."""
    out = {}
    for name in os.listdir("/proc"):
        if not name.isdigit():
            continue
        pid = int(name)
        exe = f"/proc/{pid}/exe"
        try:
            real = os.readlink(exe)
        except OSError:
            real = None
        digest = sha_file(exe)
        a = argv_of(pid)
        if digest == SERVER_SHA:
            out[pid] = {"why": "exe-digest", "exe": real, "argv": a[:4]}
            continue
        if a and a[0].endswith("llama-server"):
            out[pid] = {"why": f"argv0:{a[0]}", "exe": real, "argv": a[:4]}
    return out


def extract_tree(repo, tip, dest):
    p = subprocess.run(["git", "-C", repo, "archive", "--format=tar", tip],
                       capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(f"git archive {tip}: {p.stderr.decode('utf-8', 'replace')[:300]}")
    os.makedirs(dest, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(p.stdout)) as tf:
        tf.extractall(dest, filter=lambda m, d: None if (m.issym() or m.islnk())
                      else tarfile.data_filter(m, d))


def run_dirs(S, tag):
    base = os.path.join(S, "runs", tag)
    out = {"base": base, "work": os.path.join(base, "work"), "wd": os.path.join(base, "wd"),
           "home": os.path.join(base, "home"), "tmp": os.path.join(base, "tmp"),
           "out": os.path.join(base, "replay.json"), "log": os.path.join(base, "replay.log")}
    for k in ("work", "wd", "home", "tmp"):
        os.makedirs(out[k], exist_ok=True)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", required=True, help="lane clone (read-only)")
    ap.add_argument("--tip", required=True)
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--out", default=None, help="write the JSON evidence receipt here")
    ap.add_argument("--count", type=int, default=3,
                    help="concurrent replays (default 3 = the frozen hypothesis; receipts "
                         "1..3 repeat when count > 3, a stress probe of the same design)")
    a = ap.parse_args(argv)
    S = os.path.abspath(a.scratch)
    os.makedirs(S, exist_ok=True)

    p = subprocess.run(["git", "-C", a.repo, "rev-parse", "--verify", a.tip + "^{commit}"],
                       capture_output=True)
    if p.returncode != 0:
        say(f"could-not-evaluate: git {p.stderr.decode('utf-8', 'replace').strip()[:200]}")
        return 2
    tip = p.stdout.decode().strip()
    tree = os.path.join(S, "tree")
    if not os.path.isfile(os.path.join(tree, REPLAY)):
        extract_tree(a.repo, tip, tree)
    say(f"tip={tip} tree={tree}")

    before = server_pids()
    say(f"baseline: {len(before)} llama-server-like pid(s) already running: {sorted(before)}")

    runs = []
    procs = []
    try:
        t_launch = time.monotonic()
        for n in range(1, a.count + 1):
            rp = RECEIPTS[(n - 1) % len(RECEIPTS)]
            tag = f"w{n}"
            d = run_dirs(S, tag)
            env = dict(os.environ)
            env.update(HOME=d["home"], XDG_CACHE_HOME=os.path.join(d["home"], ".cache"),
                       TMPDIR=d["tmp"])
            receipt = os.path.join(tree, rp)
            log = open(d["log"], "wb")
            proc = subprocess.Popen(
                [sys.executable, os.path.join(tree, REPLAY), "--receipt", receipt,
                 "--work", d["work"], "--out", d["out"], "--witness-dir", d["wd"],
                 "--witness-timeout", str(WITNESS_TIMEOUT)],
                env=env, cwd=tree, stdout=log, stderr=log, start_new_session=True)
            pid_launch = time.monotonic()
            runs.append({"tag": tag, "receipt": rp, "dirs": d, "proc": proc, "log": log,
                         "launched_at": pid_launch - t_launch, "ready": None,
                         "observed": {}, "post": {}})
            say(f"launched {tag}: replay pid {proc.pid} at +{pid_launch - t_launch:.3f}s "
                f"(receipt {rp})")
        procs = [r["proc"] for r in runs]

        # ---- wait for all three ready.json
        deadline = time.monotonic() + READY_WAIT
        while time.monotonic() < deadline:
            missing = [r for r in runs if r["ready"] is None]
            if not missing:
                break
            for r in missing:
                j = load(os.path.join(r["dirs"]["wd"], "ready.json"))
                if isinstance(j, dict):
                    r["ready"] = j
                    r["ready_at"] = time.monotonic() - t_launch
            time.sleep(0.1)
        for r in runs:
            if r["ready"] is None:
                bad(f"{r['tag']}: no ready.json within {READY_WAIT:.0f}s "
                    f"(replay exit {r['proc'].poll()})")
        ready = [r["ready"] for r in runs if isinstance(r["ready"], dict)]
        say("ready.json: " + json.dumps([{"tag": r["tag"], "at_s": round(r.get("ready_at", -1), 1),
                                          "body": r["ready"]} for r in runs
                                         if isinstance(r["ready"], dict)], sort_keys=True))

        # ---- distinct ports / pids
        if len(ready) == a.count:
            ports = [j.get("port") for j in ready]
            pids = [j.get("pid") for j in ready]
            if len(set(ports)) != a.count:
                bad(f"ports not distinct: {ports}")
            else:
                say(f"ports distinct: {ports}")
            if len(set(pids)) != a.count:
                bad(f"pids not distinct: {pids}")
            else:
                say(f"pids distinct: {pids}")

        # ---- per-run outside observation while all three are held
        for r in runs:
            j = r["ready"]
            if not isinstance(j, dict):
                continue
            pid, port, o = j.get("pid"), j.get("port"), r["observed"]
            o["ready"] = j
            o["schema_ok"] = j.get("schema") == "kama-live-witness/v1"
            if not o["schema_ok"]:
                bad(f"{r['tag']}: ready.json schema {j.get('schema')!r} is not kama-live-witness/v1")
            o["exe_sha256"] = sha_file(f"/proc/{pid}/exe")
            if o["exe_sha256"] != SERVER_SHA:
                bad(f"{r['tag']}: /proc/{pid}/exe sha256 {o['exe_sha256']} != frozen {SERVER_SHA}")
            else:
                say(f"{r['tag']}: pid {pid} /proc/{pid}/exe sha256 {o['exe_sha256']} = frozen server")
            inodes = listen_inodes(port)
            owned = inodes & pid_socket_inodes(pid)
            o["listen_inodes"] = sorted(inodes)
            o["owned_inodes"] = sorted(owned)
            if not owned:
                bad(f"{r['tag']}: no LISTEN socket on {port} owned by pid {pid} (inodes {sorted(inodes)})")
            else:
                say(f"{r['tag']}: LISTEN on {port} inode {sorted(owned)[0]} owned by pid {pid}")
            argv = argv_of(pid)
            mp = None
            if "-m" in argv and argv.index("-m") + 1 < len(argv):
                mp = argv[argv.index("-m") + 1]
                if not os.path.isabs(mp):
                    try:
                        mp = os.path.join(os.readlink(f"/proc/{pid}/cwd"), mp)
                    except OSError:
                        pass
            o["model_arg"] = mp
            o["model_sha256"] = sha_file(mp) if mp else None
            if o["model_sha256"] != MODEL_SHA:
                bad(f"{r['tag']}: -m {mp} sha256 {o['model_sha256']} != frozen model")
            else:
                say(f"{r['tag']}: -m {mp} sha256 {o['model_sha256']} = frozen model")
            pport = argv[argv.index("--port") + 1] if "--port" in argv else None
            o["argv_port"] = pport
            if pport is not None and int(pport) != port:
                bad(f"{r['tag']}: server argv --port {pport} != ready.json port {port}")
            status, body = health(port)
            o["health"] = {"status": status, "body": body}
            if status != 200:
                bad(f"{r['tag']}: GET /health on {port} -> {status} {body!r}")
            else:
                say(f"{r['tag']}: GET /health on {port} -> 200 {json.dumps(body)}")

        # ---- release all three, then wait
        t_release = time.monotonic()
        for r in runs:
            with open(os.path.join(r["dirs"]["wd"], "release"), "w") as fh:
                fh.write("released by x1concurrent observer\n")
        say(f"released all {len(runs)} at +{t_release - t_launch:.3f}s")
        for r in runs:
            try:
                code = r["proc"].wait(timeout=EXIT_WAIT)
            except subprocess.TimeoutExpired:
                code = None
                try:
                    os.killpg(r["proc"].pid, signal.SIGKILL)
                except OSError:
                    pass
                r["proc"].wait()
            r["exit"] = code
            r["elapsed"] = time.monotonic() - t_launch
            if code != 0:
                bad(f"{r['tag']}: replay exit {code} after release")
            else:
                say(f"{r['tag']}: replay exit 0 at +{r['elapsed']:.1f}s")

        # ---- per-run post-release facts
        for r in runs:
            j, o, post = r["ready"], r["observed"], r["post"]
            jr = load(r["dirs"]["out"])
            post["replay"] = {"exit": r.get("exit"), "match": jr.get("match") if isinstance(jr, dict) else None,
                              "refused": jr.get("refused") if isinstance(jr, dict) else None}
            rr = None
            if isinstance(jr, dict) and jr.get("rerun_receipt"):
                rr = load(jr["rerun_receipt"])
            post["rerun_witness"] = rr.get("witness") if isinstance(rr, dict) else None
            if not (isinstance(jr, dict) and jr.get("match") is True):
                bad(f"{r['tag']}: replay result match {post['replay']['match']} "
                    f"refused {post['replay']['refused']}")
            w = post["rerun_witness"]
            if not (isinstance(w, dict) and w.get("released") is True):
                bad(f"{r['tag']}: rerun receipt witness {w!r} does not say released true")
            elif isinstance(j, dict) and (w.get("port") != j.get("port") or w.get("pid") != j.get("pid")):
                bad(f"{r['tag']}: rerun witness port/pid {w.get('port')}/{w.get('pid')} != "
                    f"ready.json {j.get('port')}/{j.get('pid')}")
            elif isinstance(j, dict):
                say(f"{r['tag']}: rerun witness released=true port {w.get('port')} pid {w.get('pid')} "
                    f"waited_ms {w.get('waited_ms')} (matches ready.json)")
            if isinstance(j, dict):
                pid, port = j.get("pid"), j.get("port")
                post["pid_alive"] = pid_alive(pid)
                post["port_refuses"] = port_refuses(port)
                post["port_listen_inodes"] = sorted(listen_inodes(port))
                if post["pid_alive"]:
                    bad(f"{r['tag']}: pid {pid} still alive after release")
                else:
                    say(f"{r['tag']}: pid {pid} gone")
                if not post["port_refuses"]:
                    bad(f"{r['tag']}: port {port} still accepts connections")
                else:
                    say(f"{r['tag']}: port {port} refuses connections")
                if post["port_listen_inodes"]:
                    bad(f"{r['tag']}: LISTEN socket(s) still on port {port}: {post['port_listen_inodes']}")
                elif not post["pid_alive"] and post["port_refuses"]:
                    say(f"{r['tag']}: no LISTEN socket on {port}")

        # ---- global leftover scan, excluding the baseline
        after = server_pids()
        new = {pid: info for pid, info in after.items() if pid not in before}
        mine = [r["ready"].get("pid") for r in runs if isinstance(r["ready"], dict)]
        root = S + os.sep
        own = {pid: info for pid, info in new.items()
               if pid in mine or (info.get("exe") or "").startswith(root)}
        foreign = {pid: info for pid, info in new.items() if pid not in own}
        say(f"leftover scan: baseline {sorted(before)} -> after {sorted(after)}; "
            f"new {sorted(new)}; trial pids {sorted(mine)}; own leftovers {sorted(own)}; "
            f"foreign (sibling seats, informational) {sorted(foreign)}")
        for pid in mine:
            if pid in after:
                bad(f"trial server pid {pid} still among llama-server processes ({after[pid]})")
        for pid, info in foreign.items():
            say(f"info: pid {pid} is a llama-server outside this trial's scratch "
                f"(exe {info.get('exe')}), not attributed to this trial")
        if own and not any(pid in after for pid in mine):
            bad(f"llama-server under this trial's scratch survived: {own}")
        elif not own:
            say("no llama-server remains that this trial started")

        evidence = {
            "schema": "x1concurrent-witness-concurrency/v1",
            "hypothesis": ("three witnessed replays started at once write distinct ready.json "
                           "ports/pids, each pid's exe hashes to the frozen server, and after "
                           "release no listener or llama-server remains"),
            "tip": tip,
            "concurrent_replays": a.count,
            "server_sha256": SERVER_SHA,
            "model_sha256": MODEL_SHA,
            "witness_timeout_s": WITNESS_TIMEOUT,
            "baseline_server_pids": sorted(before),
            "after_server_pids": sorted(after),
            "receipts": [r["receipt"] for r in runs],
            "runs": [{k: v for k, v in r.items() if k not in ("proc", "log")} for r in runs],
            "fails": fails,
            "held": not fails,
        }
        if a.out:
            with open(a.out, "w") as fh:
                json.dump(evidence, fh, indent=1, sort_keys=True)
            say(f"evidence receipt: {a.out}")
    except Exception:  # noqa: BLE001 - cleanup must still run
        fails.append("harness exception: " + traceback.format_exc().strip().splitlines()[-1])
        traceback.print_exc()
    finally:
        for r in runs:
            try:
                if r["proc"].poll() is None:
                    os.killpg(r["proc"].pid, signal.SIGTERM)
                    try:
                        r["proc"].wait(timeout=20)
                    except subprocess.TimeoutExpired:
                        os.killpg(r["proc"].pid, signal.SIGKILL)
                        r["proc"].wait()
            except OSError:
                pass
            r["log"].close()
        # last-resort: kill a server this trial started that survived its replay
        for r in runs:
            j = r["ready"]
            if isinstance(j, dict) and pid_alive(j.get("pid")):
                try:
                    os.kill(j["pid"], signal.SIGKILL)
                    say(f"cleanup: SIGKILLed trial server pid {j['pid']}")
                except OSError:
                    pass

    verdict = "held" if not fails else "falsified"
    say(f"VERDICT {verdict} fails={len(fails)}")
    for f in fails:
        say(f"fail: {f}")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
