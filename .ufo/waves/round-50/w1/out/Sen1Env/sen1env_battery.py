#!/usr/bin/env python3
"""Sen1Env round-50 battery: environment injection against the built replay+live chain.

One vector per invocation. The replay is started exactly as the frozen C1 counter starts
it (round50-replay-bind-audit.py start_replay): an invoker `python3 -I -c ...` whose
environment is the counter's PASS_ENV plus a scratch HOME/XDG_CACHE_HOME/TMPDIR and the
two planted canaries (KAMA_R50_CANARY, PYTHONPATH -> sitecustomize marker), which in turn
runs `python3 -I tools/kama-live-replay.py ... --witness-dir W`.

The vector adds ONE further injection to that environment. While the live tool holds the
server for the witness, this harness snapshots every descendant of the invoker (pid,
ppid, comm, cmdline, exe, full environ, mapped libraries) and afterwards reads the
marker files, the replay JSON and the rerun receipt.

  python3 sen1env_battery.py --tree T --receipt R --outdir D --vector NAME [--hold S]

Writes <outdir>/runs/<vector>.json and prints one summary line. Exit 0 when the run
completed and the record was written (a leak is recorded, not an error).
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import signal
import subprocess
import sys
import time

PASS_ENV = ("PATH", "LANG", "http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY", "no_proxy")
INVOKER = "import subprocess, sys\nsys.exit(subprocess.call(sys.argv[1:]))\n"
READY_WAIT = 600.0
EXIT_WAIT = 180.0
# names a child must never carry: the frozen canary, the two planted harness canaries, and
# every environment channel Python/bash/ld.so read at startup
WATCH_KEYS = ("KAMA_R50_CANARY", "PYTHONPATH", "PYTHONSTARTUP", "PYTHONHOME", "PYTHONUSERBASE",
              "PYTHONSAFEPATH", "PYTHONWARNINGS", "PYTHONINSPECT", "PYTHONEXECUTABLE",
              "LD_PRELOAD", "LD_AUDIT", "LD_LIBRARY_PATH", "BASH_ENV", "ENV", "SHELLOPTS",
              "XDG_CONFIG_HOME", "XDG_CACHE_HOME")
CANARY_VALUE = "sen1env-canary-6b1f"


# ------------------------------------------------------------------ /proc helpers
def _stat(pid):
    try:
        with open(f"/proc/{pid}/stat") as fh:
            rest = fh.read().rsplit(")", 1)[1].split()
        return rest[0], int(rest[1]), int(rest[19])
    except (OSError, IndexError, ValueError):
        return None


def descendants(root):
    kids = {}
    for name in os.listdir("/proc"):
        if not name.isdigit():
            continue
        st = _stat(int(name))
        if st is not None and st[0] not in ("Z", "X"):
            kids.setdefault(st[1], []).append((int(name), st[2]))
    out, todo = {}, [root]
    while todo:
        for pid, start in kids.get(todo.pop(), []):
            if pid not in out:
                out[pid] = start
                todo.append(pid)
    return out


def _read(path, limit=1 << 20):
    try:
        with open(path, "rb") as fh:
            return fh.read(limit)
    except OSError:
        return b""


def environ_of(pid):
    raw = _read(f"/proc/{pid}/environ")
    return [e for e in raw.split(b"\0") if e]


def proc_record(pid, lib_mark):
    st = _stat(pid)
    raw = environ_of(pid)
    pairs = []
    for e in raw:
        k, _, v = e.partition(b"=")
        pairs.append([k.decode("utf-8", "replace"), v.decode("utf-8", "replace")[:200]])
    keys = [k for k, _ in pairs]
    cmd = _read(f"/proc/{pid}/cmdline").split(b"\0")
    cmd = [c.decode("utf-8", "replace") for c in cmd if c]
    joined = " ".join(cmd)
    if "kama-live-replay.py" in joined:
        role = "replay"
    elif "kama-llamacpp-live.py" in joined:
        role = "live"
    elif "llama-server" in joined:
        role = "server"
    elif "-c" in cmd and "subprocess.call" in joined:
        role = "invoker"
    else:
        role = "other"
    exe = ""
    try:
        exe = os.readlink(f"/proc/{pid}/exe")
    except OSError:
        pass
    maps = _read(f"/proc/{pid}/maps", 8 << 20).decode("utf-8", "replace")
    return {
        "pid": pid,
        "ppid": st[1] if st else None,
        "role": role,
        "comm": _read(f"/proc/{pid}/comm").decode().strip(),
        "cmdline": cmd,
        "exe": exe,
        "env": pairs,
        "env_keys": keys,
        "watch_present": {k: dict(pairs).get(k) for k in WATCH_KEYS if k in keys},
        "watch_values_with_canary": sorted(k for k, v in pairs if CANARY_VALUE in v),
        "lib_mapped": bool(lib_mark) and lib_mark in maps,
    }


def pid_alive(pid, start=None):
    st = _stat(pid)
    if st is None or st[0] in ("Z", "X"):
        return False
    return start is None or st[2] == start


def port_refuses(port):
    import socket
    s = socket.socket()
    s.settimeout(2)
    try:
        s.connect(("127.0.0.1", port))
        return False
    except OSError:
        return True
    finally:
        s.close()


def load(path):
    try:
        with open(path) as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


# ------------------------------------------------------------------ vectors
def v_baseline(rd, env, marks):
    """The counter's own environment, unmodified (control)."""
    return "counter baseline: PASS_ENV + scratch HOME/XDG_CACHE_HOME/TMPDIR + both canaries"


def v_pythonstartup(rd, env, marks):
    p = os.path.join(rd, "startup.py")
    with open(p, "w") as fh:
        fh.write(f"open({marks['startup']!r}, 'a').write('startup %d\\n' % __import__('os').getpid())\n")
    env["PYTHONSTARTUP"] = p
    return f"PYTHONSTARTUP={p}"


def v_xdg(rd, env, marks):
    d = os.path.join(rd, "xdg")
    os.makedirs(os.path.join(d, "python"), exist_ok=True)
    for name in ("sitecustomize.py", "usercustomize.py"):
        with open(os.path.join(d, "python", name), "w") as fh:
            fh.write(f"open({marks['xdg']!r}, 'a').write('{name} %d\\n' % __import__('os').getpid())\n")
    with open(os.path.join(d, "pythonrc"), "w") as fh:
        fh.write(f"open({marks['xdg']!r}, 'a').write('pythonrc\\n')\n")
    env["XDG_CONFIG_HOME"] = d
    return f"XDG_CONFIG_HOME={d} (python/sitecustomize.py, python/usercustomize.py, pythonrc)"


def v_home_pth(rd, env, marks):
    home = os.path.join(rd, "home-pth")
    site = os.path.join(home, ".local", "lib", "python3.14", "site-packages")
    os.makedirs(site, exist_ok=True)
    line = ("import os, sys, json; open(%r, 'a').write(json.dumps({'via': %r, 'pid': os.getpid(), "
            "'ppid': os.getppid(), 'argv': sys.argv[:4], 'cwd': os.getcwd(), 'isolated': sys.flags.isolated, "
            "'no_user_site': sys.flags.no_user_site, 'env_keys': sorted(os.environ)}) + '\\n')")
    with open(os.path.join(site, "zz-sen1env.pth"), "w") as fh:
        fh.write(line % (marks['home'], 'pth') + "\n")
    with open(os.path.join(site, "usercustomize.py"), "w") as fh:
        fh.write(line % (marks['home'], 'usercustomize') + "\n")
    env["HOME"] = home
    return f"HOME={home} carries .local/lib/python3.14/site-packages/{{zz-sen1env.pth,usercustomize.py}}"


def v_path_python(rd, env, marks):
    b = os.path.join(rd, "bin-python")
    os.makedirs(b, exist_ok=True)
    for name in ("python", "python3", "python3.14"):
        p = os.path.join(b, name)
        with open(p, "w") as fh:
            fh.write("#!/bin/sh\n"
                     f"printf '%s %s %s\\n' \"$$\" '{name}' \"$*\" >> {marks['pathpython']!r}\n"
                     "exec /usr/bin/python3 \"$@\"\n")
        os.chmod(p, 0o755)
    env["PATH"] = b + ":" + env.get("PATH", "/usr/bin:/bin")
    return f"PATH first entry {b} with python/python3/python3.14 wrappers"


def v_path_bash(rd, env, marks):
    b = os.path.join(rd, "bin-bash")
    os.makedirs(b, exist_ok=True)
    p = os.path.join(b, "bash")
    with open(p, "w") as fh:
        fh.write("#!/bin/sh\n"
                 f"printf '%s %s\\n' \"$$\" \"$*\" >> {marks['pathbash']!r}\n"
                 "exec /usr/bin/bash \"$@\"\n")
    os.chmod(p, 0o755)
    env["PATH"] = b + ":" + env.get("PATH", "/usr/bin:/bin")
    return f"PATH first entry {b} with a bash wrapper (fires for every 'bash' exec)"


def v_ld_preload(rd, env, marks):
    src = os.path.join(rd, "libmark.c")
    lib = os.path.join(rd, "libsen1env.so")
    with open(src, "w") as fh:
        fh.write('#include <unistd.h>\n#include <fcntl.h>\n#include <stdio.h>\n#include <string.h>\n'
                 f'__attribute__((constructor)) static void m(void) {{\n'
                 f'  char b[256]; int n = snprintf(b, sizeof b, "lib %d\\n", (int)getpid());\n'
                 '  int fd = open(' + json.dumps(marks["ld"]) +
                 ', 1|64|1024 /*O_WRONLY|O_CREAT|O_APPEND*/, 0644);\n'
                 '  if (fd >= 0) { write(fd, b, (size_t)n); close(fd); }\n}\n')
    cp = subprocess.run(["gcc", "-shared", "-fPIC", "-o", lib, src, "-ldl"],
                        capture_output=True, text=True)
    if cp.returncode != 0:
        raise SystemExit(f"gcc failed: {cp.stderr[-400:]}")
    env["LD_PRELOAD"] = lib
    env["LD_LIBRARY_PATH"] = rd
    return f"LD_PRELOAD={lib} (constructor writes pid to a marker)"


def v_locale_utf8(rd, env, marks):
    env["LC_ALL"] = "en_US.utf8"
    env["LANG"] = "en_US.utf8"
    return "LC_ALL=LANG=en_US.utf8 (a generated non-C locale)"


def v_locale_bogus(rd, env, marks):
    env["LC_ALL"] = "tr_TR.utf8"
    env["LANG"] = "tr_TR.utf8"
    return "LC_ALL=LANG=tr_TR.utf8 (not generated on this host: glibc falls back, programs warn)"


def v_tmpdir(rd, env, marks):
    d = os.path.join(rd, "hostile-tmp")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "sitecustomize.py"), "w") as fh:
        fh.write(f"open({marks['tmp']!r}, 'a').write('tmp-sitecustomize\\n')\n")
    env["TMPDIR"] = d
    return f"TMPDIR={d} (with a sitecustomize.py inside)"


def v_scriptdir(rd, env, marks):
    """sitecustomize next to the live tool (its script dir) and in the cwd the live child
    inherits: `-I` implies `-P`, so neither may be importable. Own tree copy, so the
    planted files cannot reach the shared tree of the other vectors."""
    tree = os.path.join(rd, "tree")
    os.makedirs(tree)
    for sub in ("tools", "registry"):
        shutil.copytree(os.path.join(env["_TREE"], sub), os.path.join(tree, sub))
    env["_TREE"] = tree
    made = []
    for d in (os.path.join(tree, "tools"), tree):
        p = os.path.join(d, "sitecustomize.py")
        with open(p, "w") as fh:
            fh.write(f"open({marks['scriptdir']!r}, 'a').write('scriptdir %r %d\\n' "
                     "% (__import__('os').getcwd(), __import__('os').getpid()))\n")
        made.append(p)
    return "sitecustomize.py planted at " + ", ".join(made) + " (script dir and cwd)"


def v_bashenv(rd, env, marks):
    p = os.path.join(rd, "bashenv.sh")
    with open(p, "w") as fh:
        fh.write(f"printf '%s bashenv\\n' \"$$\" >> {marks['bashenv']!r}\n")
    env["BASH_ENV"] = p
    env["ENV"] = p
    return f"BASH_ENV=ENV={p} (sourced by every non-interactive bash)"


def v_path_bash_forge(rd, env, marks):
    """A bash wrapper that answers the two probe calls itself: it never runs
    kama-probe.sh, yet returns the exact rows the live tool's probe checks read."""
    b = os.path.join(rd, "bin-forge")
    os.makedirs(b, exist_ok=True)
    p = os.path.join(b, "bash")
    with open(p, "w") as fh:
        fh.write("#!/bin/sh\n"
                 f"{{ printf 'self=%%s ppid=%%s\\n' \"$$\" \"$PPID\"; "
                 f"tr '\\0' ' ' < /proc/$PPID/cmdline; printf '\\n'; }} >> {marks['forge']!r}\n"
                 "case \"$*\" in\n"
                 "  *kama-not-this-model*) printf '%s\\n' "
                 "'{\"rows\":[{\"verdict\":\"MODEL_MISMATCH\",\"reason\":\"served-id-mismatch\"}]}'; exit 2;;\n"
                 "  *) printf '%s\\n' "
                 "'{\"rows\":[{\"verdict\":\"MODEL_OK\",\"reason\":\"matched\"}]}'; exit 0;;\n"
                 "esac\n")
    os.chmod(p, 0o755)
    env["PATH"] = b + ":" + env.get("PATH", "/usr/bin:/bin")
    return f"PATH first entry {b} with a bash that forges both probe answers (never runs the probe)"


def v_path_curl(rd, env, marks):
    """kama-probe.sh resolves curl and ss through PATH too: a curl wrapper sees every
    request the probe makes to the server (and can answer it from anywhere)."""
    b = os.path.join(rd, "bin-curl")
    os.makedirs(b, exist_ok=True)
    p = os.path.join(b, "curl")
    with open(p, "w") as fh:
        fh.write("#!/bin/sh\n"
                 f"printf '%s %s\\n' \"$$\" \"$*\" >> {marks['curl']!r}\n"
                 "exec /usr/bin/curl \"$@\"\n")
    os.chmod(p, 0o755)
    env["PATH"] = b + ":" + env.get("PATH", "/usr/bin:/bin")
    return f"PATH first entry {b} with a curl wrapper (every probe request passes through it)"


VECTORS = {
    "V0-baseline": v_baseline,
    "V1-pythonstartup": v_pythonstartup,
    "V2-xdg-config": v_xdg,
    "V3-home-pth": v_home_pth,
    "V4-path-python": v_path_python,
    "V5-path-bash": v_path_bash,
    "V6-ld-preload": v_ld_preload,
    "V7-locale-utf8": v_locale_utf8,
    "V8-tmpdir": v_tmpdir,
    "V9-scriptdir": v_scriptdir,
    "V10-bashenv": v_bashenv,
    "V12-path-bash-forge": v_path_bash_forge,
    "V13-path-curl": v_path_curl,
    "V11-locale-bogus": v_locale_bogus,
}


# ------------------------------------------------------------------ one run
def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", required=True, help="tree extracted at the measured tip")
    ap.add_argument("--receipt", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--workroot", default=None,
                    help="ephemeral root (downloads, work, witness); default --outdir. The frozen "
                         "counter keeps all of this under --scratch")
    ap.add_argument("--vector", required=True, choices=sorted(VECTORS))
    ap.add_argument("--hold", type=float, default=90.0)
    ap.add_argument("--witness-timeout", type=float, default=600.0)
    a = ap.parse_args(argv)

    root = a.workroot or a.outdir
    rd = os.path.join(root, "runs", a.vector)
    shutil.rmtree(rd, ignore_errors=True)
    os.makedirs(rd)
    keep = os.path.join(a.outdir, "runs", a.vector)
    os.makedirs(keep, exist_ok=True)
    marks = {k: os.path.join(rd, f"mark-{k}.txt") for k in
             ("startup", "xdg", "home", "pathpython", "pathbash", "ld", "tmp", "scriptdir", "bashenv",
              "forge", "curl")}
    canary_marker = os.path.join(rd, "mark-sitecustomize-canary.txt")
    cdir = os.path.join(rd, "canary-path")
    os.makedirs(cdir)
    with open(os.path.join(cdir, "sitecustomize.py"), "w") as fh:
        fh.write("import os, sys\n"
                 f"with open({canary_marker!r}, 'a') as _fh:\n"
                 "    _fh.write('%d %r\\n' % (os.getpid(), sys.argv[:3]))\n")

    env = {k: os.environ[k] for k in PASS_ENV if k in os.environ}
    for k, sub in (("HOME", "home"), ("XDG_CACHE_HOME", "home/.cache"), ("TMPDIR", "tmp")):
        d = os.path.join(rd, sub)
        os.makedirs(d, exist_ok=True)
        env[k] = d
    env["KAMA_R50_CANARY"] = CANARY_VALUE
    env["PYTHONPATH"] = cdir
    env["_TREE"] = a.tree
    desc = VECTORS[a.vector](rd, env, marks)
    tree = env.pop("_TREE")

    work, wd = os.path.join(rd, "work"), os.path.join(rd, "witness")
    os.makedirs(wd)
    outj = os.path.join(rd, "replay.json")
    log = os.path.join(rd, "invoker.log")
    rpath = os.path.join(tree, "tools", "kama-live-replay.py")
    argv_run = [sys.executable, "-I", "-c", INVOKER, sys.executable, "-I", rpath,
                "--receipt", a.receipt, "--work", work, "--out", outj,
                "--witness-dir", wd, "--witness-timeout", str(a.witness_timeout),
                "--timeout", "600"]
    t0 = time.monotonic()
    with open(log, "wb") as lf:
        p = subprocess.Popen(argv_run, env=env, cwd=tree, stdout=lf, stderr=lf,
                             stdin=subprocess.DEVNULL, start_new_session=True)
    rec = {"vector": a.vector, "description": desc, "tree": tree, "receipt": os.path.abspath(a.receipt),
           "invoker_pid": p.pid, "ready": None, "procs": [], "markers": {}, "leaks": []}
    snap = {}
    ready = None
    try:
        deadline = time.monotonic() + READY_WAIT
        while time.monotonic() < deadline and p.poll() is None:
            r = load(os.path.join(wd, "ready.json"))
            if isinstance(r, dict) and isinstance(r.get("pid"), int) and isinstance(r.get("port"), int):
                ready = r
                break
            time.sleep(0.2)
        rec["ready"] = ready
        if ready is None:
            rec["leaks"].append(f"no-ready: invoker exit {p.poll()}")
        else:
            snap = descendants(p.pid)
            rec["procs"] = [proc_record(pid, "libsen1env") for pid in sorted(snap)]
            time.sleep(a.hold)
            rec["procs_after_hold"] = [proc_record(pid, "libsen1env") for pid in sorted(snap)
                                       if pid_alive(pid, snap[pid])]
        with open(os.path.join(wd, "release"), "w") as fh:
            fh.write("released by sen1env\n")
        try:
            code = p.wait(timeout=EXIT_WAIT)
        except subprocess.TimeoutExpired:
            code = None
        rec["exit"] = code
        rec["wall_s"] = round(time.monotonic() - t0, 1)
    finally:
        for pid, start in list(snap.items()):
            if pid_alive(pid, start):
                try:
                    os.kill(pid, signal.SIGKILL)
                except OSError:
                    pass
        if p.poll() is None:
            try:
                os.killpg(p.pid, signal.SIGKILL)
            except OSError:
                pass
            p.wait()

    # marker files: the canary sitecustomize and every vector's own mark
    files = {"sitecustomize-canary": canary_marker}
    files.update(marks)
    for name, path in files.items():
        if os.path.exists(path):
            with open(path, "rb") as fh:
                rec["markers"][name] = fh.read(4000).decode("utf-8", "replace")

    j = load(outj)
    rec["replay_out"] = {k: j.get(k) for k in ("match", "refused", "mismatches", "live_exit",
                                               "rerun_receipt", "inputs")} if isinstance(j, dict) else j
    rr = load(j.get("rerun_receipt")) if isinstance(j, dict) and j.get("rerun_receipt") else None
    if isinstance(rr, dict):
        checks = {c.get("id"): c.get("passed") for c in rr.get("checks") or [] if isinstance(c, dict)}
        rec["rerun"] = {
            "schema": rr.get("schema"),
            "outcome": rr.get("outcome"),
            "child_pid": rr.get("child_pid"),
            "child_env_keys": rr.get("child_env_keys"),
            "witness": rr.get("witness"),
            "model_mapping": {k: rr.get("model_mapping", {}).get(k) if isinstance(rr.get("model_mapping"), dict) else None
                              for k in ("mapped", "sha256", "dev", "inode", "reason")},
            "checks": checks,
            "teardown": rr.get("teardown"),
            "probe_stderr_tails": [pr.get("stderr_tail") for pr in rr.get("probes") or []
                                   if isinstance(pr, dict)],
            "probe_exits": [pr.get("exit") for pr in rr.get("probes") or [] if isinstance(pr, dict)],
            "captures": {"props": rr.get("captures", {}).get("props", {}).get("fields"),
                         "slots_count": rr.get("captures", {}).get("slots", {}).get("element_count"),
                         "slots_sha": rr.get("captures", {}).get("slots", {}).get("body_sha256"),
                         "health": [rr.get("captures", {}).get("health", {}).get("status"),
                                    rr.get("captures", {}).get("health", {}).get("body_sha256")],
                         "models_body": rr.get("captures", {}).get("models", {}).get("body"),
                         "metrics": rr.get("captures", {}).get("metrics", {}).get("status")},
            "log_lines": (rr.get("teardown") or {}).get("log_lines"),
            "port": rr.get("port"),
            "started_utc": rr.get("started_utc"),
        }
        if ready is not None and rr.get("child_pid") != ready.get("pid"):
            rec["leaks"].append(f"join: rerun child_pid {rr.get('child_pid')} != witnessed pid {ready.get('pid')}")

    # verdicts on the environment surfaces
    if rec["markers"].get("sitecustomize-canary"):
        rec["leaks"].append("planted sitecustomize (PYTHONPATH) imported")
    for pid_rec in rec["procs"]:
        # the replay itself is the invoker's child and keeps the invoker's environment by
        # inheritance: only what the replay HANDS ON (live, server, anything they start) counts
        if pid_rec["role"] in ("live", "server", "other") and "KAMA_R50_CANARY" in pid_rec["env_keys"]:
            rec["leaks"].append(f"canary key in {pid_rec['role']} pid {pid_rec['pid']}")
        if pid_rec["watch_values_with_canary"]:
            rec["leaks"].append(f"canary value in {pid_rec['role']} pid {pid_rec['pid']} "
                                f"keys {pid_rec['watch_values_with_canary']}")
        bad = sorted(k for k in pid_rec["watch_present"]
                     if k != "KAMA_R50_CANARY" and pid_rec["role"] in ("live", "server"))
        if bad:
            rec["leaks"].append(f"watch keys in {pid_rec['role']} pid {pid_rec['pid']}: {bad}")
    for name, text in rec["markers"].items():
        if name != "sitecustomize-canary" and text.strip():
            rec["leaks"].append(f"vector marker {name} written: {text.splitlines()[:3]}")

    rec["record"] = os.path.join(keep, f"{a.vector}.json")
    rec["work"] = rd
    for src, name in ((outj, "replay.json"),
                      (os.path.join(work, "rerun-receipt.json"), "rerun-receipt.json"),
                      (log, "invoker.log")):
        if os.path.exists(src):
            shutil.copy(src, os.path.join(keep, name))
    with open(rec["record"], "w") as fh:
        json.dump(rec, fh, indent=1)
    print(f"{a.vector} exit={rec.get('exit')} ready={'yes' if ready else 'no'} "
          f"match={rec['replay_out'].get('match') if isinstance(rec['replay_out'], dict) else None} "
          f"procs={len(rec['procs'])} leaks={len(rec['leaks'])} {rec['leaks'][:2]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
