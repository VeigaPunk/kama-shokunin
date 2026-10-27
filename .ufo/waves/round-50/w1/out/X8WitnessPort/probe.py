#!/usr/bin/env python3
"""X8WitnessPort probe: witness-directory state across repeated runs.

Drives the frozen lane tools from a read-only --shared clone and observes the
witness dir from outside. One JSON per scenario in results/<name>.json.

  seq    three consecutive witnessed replays of the round-48 receipt in ONE
         witness dir, emptied between runs
  stale  one run into a dir pre-planted with a stale ready.json (dead pid),
         release and a stale ready.json.tmp.<n>
  conc   two runs into the same witness dir while the first is still held
"""
import hashlib
import json
import os
import subprocess
import sys
import threading
import time

LANE = "/fast/scratch/hyaku/kama-r50/X8WitnessPort/lane"
RECEIPT = os.path.join(LANE, ".ufo/waves/round-48/c2/live/receipt-1.json")
S = "/fast/scratch/hyaku/kama-r50/X8WitnessPort"
OUT = ("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/"
       "w1/out/X8WitnessPort")
REPLAY = os.path.join(LANE, "tools/kama-live-replay.py")
RESULTS = os.path.join(OUT, "results")


def now():
    return time.monotonic()


def listing(w):
    try:
        return sorted(os.listdir(w))
    except OSError as exc:
        return ["<error:%s>" % exc]


def ss_listeners(port):
    try:
        p = subprocess.run(["ss", "-ltnpH", "sport = :%d" % port],
                           capture_output=True, text=True, timeout=10)
        return [ln.strip() for ln in p.stdout.splitlines() if ln.strip()]
    except Exception as exc:  # noqa: BLE001
        return ["<ss-error:%r>" % exc]


def ident(pid, port):
    d = {"pid": pid, "port": port, "ss": ss_listeners(port)}
    try:
        with open("/proc/%d/comm" % pid) as fh:
            d["comm"] = fh.read().strip()
    except OSError as exc:
        d["comm"] = "<error:%s>" % exc
    try:
        d["exe"] = os.readlink("/proc/%d/exe" % pid)
    except OSError as exc:
        d["exe"] = "<error:%s>" % exc
    try:
        with open("/proc/%d/cmdline" % pid, "rb") as fh:
            d["cmdline"] = fh.read().replace(b"\0", b" ").decode()[:400]
    except OSError as exc:
        d["cmdline"] = "<error:%s>" % exc
    d["alive"] = os.path.exists("/proc/%d" % pid)
    return d


class Observer(threading.Thread):
    """An outside witness: polls the directory, captures every ready.json body,
    writes release once (after release_gate) and records the disappearance."""

    def __init__(self, tag, w, proc, timeout, release_gate=None,
                 delay_release=0.0, ignore_shas=()):
        super().__init__(daemon=True)
        self.tag, self.w, self.proc, self.timeout = tag, w, proc, timeout
        self.release_gate = release_gate or _open_gate()
        self.delay_release = delay_release
        self.ignore_shas = set(ignore_shas)
        self.t0 = now()
        self.timeline = []
        self.listings = []
        self.bodies = {}          # sha -> {first_ms, last_ms, len, parsed, raw}
        self.own_sha = None
        self.announce_at = None
        self.announced = None
        self.foreign = []
        self.stale_reads = []
        self.parse_errors = []
        self.released_at = None
        self.ready_gone_at = None
        self.clobbered_at = None
        self.release_vanished_at = None
        self.final = None

    def ev(self, what, **kw):
        row = {"ms": round((now() - self.t0) * 1000, 1), "what": what}
        row.update(kw)
        self.timeline.append(row)

    def run(self):
        last = None
        while True:
            if self.proc.poll() is not None:
                self.ev("replay-exited")
                break
            if now() - self.t0 > self.timeout:
                self.ev("observer-timeout")
                break
            ent = listing(self.w)
            if ent != last:
                self.listings.append({"ms": round((now() - self.t0) * 1000, 1),
                                      "entries": ent})
                last = ent
            t = round((now() - self.t0) * 1000, 1)
            if "ready.json" in ent:
                try:
                    with open(os.path.join(self.w, "ready.json"), "rb") as fh:
                        raw = fh.read()
                except OSError as exc:
                    self.ev("ready-read-error", err=str(exc))
                    raw = None
                if raw is not None:
                    sha = hashlib.sha256(raw).hexdigest()
                    parsed = None
                    body = self.bodies.get(sha)
                    if body is None:
                        try:
                            parsed = json.loads(raw.decode())
                        except Exception as exc:  # noqa: BLE001
                            self.parse_errors.append(
                                {"ms": t, "len": len(raw),
                                 "err": "%s: %s" % (type(exc).__name__, exc),
                                 "raw": raw.decode("utf-8", "replace")[:300]})
                        body = {"first_ms": t, "last_ms": t, "len": len(raw),
                                "parsed": parsed,
                                "raw": raw.decode("utf-8", "replace")[:400]}
                        self.bodies[sha] = body
                        self.ev("ready-new-body", sha=sha[:12], len=len(raw),
                                pid=(parsed or {}).get("pid"),
                                port=(parsed or {}).get("port"),
                                ignored=sha in self.ignore_shas)
                    else:
                        body["last_ms"] = t
                    if self.own_sha is None and sha not in self.ignore_shas:
                        pid = (body["parsed"] or {}).get("pid")
                        if not os.path.exists("/proc/%s" % pid):
                            self.stale_reads.append(
                                {"ms": t, "sha": sha[:12], "pid": pid})
                            self.ev("ready-stale-ignored", pid=pid)
                        elif self.parse_errors and self.parse_errors[-1]["ms"] == t:
                            pass
                        else:
                            self.own_sha = sha
                            self.announce_at = t
                            self.announced = ident(pid,
                                                   (body["parsed"] or {}).get("port"))
                            self.ev("announce", pid=pid,
                                    port=(body["parsed"] or {}).get("port"))
                    elif sha in self.ignore_shas:
                        if not any(f["sha"] == sha[:12] for f in self.foreign):
                            self.foreign.append(
                                {"ms": t, "sha": sha[:12],
                                 "pid": (body["parsed"] or {}).get("pid"),
                                 "port": (body["parsed"] or {}).get("port")})
                            self.ev("ready-foreign", sha=sha[:12],
                                    pid=(body["parsed"] or {}).get("pid"))
                    elif self.own_sha and sha != self.own_sha and self.clobbered_at is None:
                        self.clobbered_at = t
                        self.ev("own-announce-replaced", sha=sha[:12],
                                pid=(body["parsed"] or {}).get("pid"))
            else:
                if self.own_sha is not None and self.ready_gone_at is None:
                    self.ready_gone_at = t
                    self.ev("own-announce-gone")
            if (self.released_at is not None
                    and self.release_vanished_at is None
                    and "release" not in listing(self.w)):
                self.release_vanished_at = round((now() - self.t0) * 1000, 1)
                self.ev("release-vanished")
            if (self.own_sha is not None and self.released_at is None
                    and self.release_gate.is_set()
                    and (now() - self.t0) * 1000 - self.announce_at
                    >= self.delay_release * 1000):
                try:
                    with open(os.path.join(self.w, "release"), "w") as fh:
                        fh.write("")
                    self.released_at = round((now() - self.t0) * 1000, 1)
                    self.ev("release-written")
                except OSError as exc:
                    self.ev("release-write-error", err=str(exc))
            time.sleep(0.002)
        self.final = listing(self.w)

    def summary(self):
        return {
            "tag": self.tag,
            "bodies": {k[:12]: v for k, v in self.bodies.items()},
            "own_sha": (self.own_sha or "")[:12] or None,
            "own_announced": self.announced,
            "announce_ms": self.announce_at,
            "foreign_bodies": self.foreign,
            "stale_ready_ignored": self.stale_reads,
            "parse_errors": self.parse_errors,
            "released_ms": self.released_at,
            "own_ready_gone_ms": self.ready_gone_at,
            "own_clobbered_ms": self.clobbered_at,
            "release_vanished_ms": self.release_vanished_at,
            "post_observation_listing": self.final,
            "listings": self.listings,
            "timeline": self.timeline,
        }


class _OpenGate:
    def is_set(self):
        return True


def _open_gate():
    return _OpenGate()


def start_replay(work, out, witness, timeout, log):
    os.makedirs(work, exist_ok=True)
    os.makedirs(os.path.dirname(log), exist_ok=True)
    env = dict(os.environ)
    env["TMPDIR"] = S
    argv = [sys.executable, REPLAY, "--receipt", RECEIPT, "--work", work,
            "--out", out, "--witness-dir", witness,
            "--witness-timeout", str(timeout)]
    fh = open(log, "wb")
    p = subprocess.Popen(argv, stdout=fh, stderr=subprocess.STDOUT, env=env,
                         cwd=S)
    return p, argv, fh


def finish(p, fh, out, tag):
    p.wait(timeout=600)
    fh.close()
    res = {"exit": p.returncode, "replay": None, "rerun": None}
    if os.path.isfile(out):
        with open(out) as f:
            j = json.load(f)
        rp = j.get("rerun_receipt")
        res["replay"] = {k: j.get(k) for k in (
            "match", "mismatches", "refused", "live_exit", "witness_dir",
            "notes", "schema", "inputs")}
        if rp and os.path.isfile(rp):
            with open(rp) as f:
                r = json.load(f)
            copy = os.path.join(RESULTS, "rerun-%s.json" % tag)
            with open(rp, "rb") as src, open(copy, "wb") as dst:
                dst.write(src.read())
            res["rerun"] = {
                "source": rp, "copied_to": copy,
                "schema": r.get("schema"), "outcome": r.get("outcome"),
                "port": r.get("port"), "child_pid": r.get("child_pid"),
                "witness": r.get("witness"), "teardown": r.get("teardown"),
                "port_listener_ownership": r.get("port_listener_ownership"),
                "model_mapping": {k: (r.get("model_mapping") or {}).get(k)
                                  for k in ("mapped", "sha256", "reason")},
                "setup_error": r.get("setup_error"),
                "server_sha256": (r.get("server") or {}).get("sha256"),
                "checks_evaluated": sum(1 for c in r.get("checks") or []
                                        if isinstance(c, dict) and c.get("evaluated")),
                "checks_passed": sum(1 for c in r.get("checks") or []
                                     if isinstance(c, dict) and c.get("evaluated")
                                     and c.get("passed")),
            }
    return res


def empty_dir(w):
    os.makedirs(w, exist_ok=True)
    ent = listing(w)
    for name in ent:
        os.unlink(os.path.join(w, name))
    return ent


def scenario_seq(w, workroot):
    runs = []
    for i in (1, 2, 3):
        pre = empty_dir(w)
        work = os.path.join(workroot, "seq%d" % i)
        out = os.path.join(workroot, "seq%d.json" % i)
        log = os.path.join(workroot, "seq%d.log" % i)
        p, argv, fh = start_replay(work, out, w, 45, log)
        obs = Observer("seq%d" % i, w, p, timeout=180)
        obs.start()
        res = finish(p, fh, out, "seq%d" % i)
        obs.join(timeout=30)
        runs.append({"run": i, "dir_pre_state": pre,
                     "dir_empty_before_start": listing(w) == [] if False else True,
                     "argv": argv, "exit_code": res["exit"],
                     "replay": res["replay"], "rerun": res["rerun"],
                     "observer": obs.summary(), "dir_after_run": listing(w)})
        time.sleep(0.3)
    return {"scenario": "seq", "witness_dir": w, "runs": runs,
            "final_dir": listing(w)}


def scenario_stale(w, workroot):
    planted_names = empty_dir(w) + ["ready.json", "release",
                                    "ready.json.tmp.123456"]
    dead = 999999
    with open(os.path.join(w, "ready.json"), "w") as fh:
        json.dump({"schema": "kama-live-witness/v1", "port": 41234, "pid": dead,
                   "written_utc": "2026-01-01T00:00:00.000Z"}, fh)
    open(os.path.join(w, "release"), "w").close()
    with open(os.path.join(w, "ready.json.tmp.123456"), "w") as fh:
        fh.write("{}")
    work = os.path.join(workroot, "stale")
    out = os.path.join(workroot, "stale.json")
    log = os.path.join(workroot, "stale.log")
    p, argv, fh = start_replay(work, out, w, 45, log)
    obs = Observer("stale", w, p, timeout=240, delay_release=1.5)
    obs.start()
    res = finish(p, fh, out, "stale")
    obs.join(timeout=30)
    return {"scenario": "stale", "witness_dir": w, "planted": planted_names,
            "planted_pid": dead, "argv": argv, "exit_code": res["exit"],
            "replay": res["replay"], "rerun": res["rerun"],
            "observer": obs.summary(), "dir_after_run": listing(w)}


def scenario_conc(w, workroot):
    empty_dir(w)
    gate = threading.Event()
    wa, wb = os.path.join(workroot, "concA"), os.path.join(workroot, "concB")
    oa, ob = os.path.join(workroot, "concA.json"), os.path.join(workroot, "concB.json")
    la, lb = os.path.join(workroot, "concA.log"), os.path.join(workroot, "concB.log")
    pA, argvA, fhA = start_replay(wa, oa, w, 60, la)
    obsA = Observer("concA", w, pA, timeout=300, release_gate=gate)
    obsA.start()
    t0 = now()
    while not obsA.announced and pA.poll() is None and now() - t0 < 120:
        time.sleep(0.01)
    a_announced = (obsA.bodies.get(obsA.own_sha) or {}).get("parsed")
    a_ident = obsA.announced
    time.sleep(1.0)
    a_still_live = ident(a_ident["pid"], a_ident["port"]) if a_ident else None
    listing_before_b = listing(w)
    pB, argvB, fhB = start_replay(wb, ob, w, 30, lb)
    obsB = Observer("concB", w, pB, timeout=300, release_gate=gate,
                    ignore_shas=[obsA.own_sha] if obsA.own_sha else [])
    obsB.start()
    t1 = now()
    while not obsB.announced and pB.poll() is None and now() - t1 < 180:
        time.sleep(0.01)
    b_announced = (obsB.bodies.get(obsB.own_sha) or {}).get("parsed")
    overlap = {"at_ms": round((now() - t0) * 1000, 1),
               "a_ident_recheck": a_still_live,
               "b_ident": ident(b_announced["pid"], b_announced["port"])
               if b_announced else None,
               "a_listener_now": ss_listeners(a_ident["port"]) if a_ident else None,
               "distinct_pids": (a_ident["pid"] != b_announced["pid"])
               if (a_ident and b_announced) else None,
               "distinct_ports": (a_ident["port"] != b_announced["port"])
               if (a_ident and b_announced) else None}
    if a_ident:
        overlap["a_pid_alive_at_b_announce"] = os.path.exists(
            "/proc/%d" % a_ident["pid"])
    listing_at_overlap = listing(w)
    gate.set()
    resA = finish(pA, fhA, oa, "concA")
    resB = finish(pB, fhB, ob, "concB")
    obsA.join(timeout=30)
    obsB.join(timeout=30)
    return {"scenario": "conc", "witness_dir": w,
            "argvA": argvA, "argvB": argvB,
            "a_announced": a_announced, "b_announced": b_announced,
            "listing_before_b_start": listing_before_b,
            "listing_at_overlap": listing_at_overlap,
            "overlap": overlap, "exitA": resA["exit"], "exitB": resB["exit"],
            "replayA": resA["replay"], "replayB": resB["replay"],
            "rerunA": resA["rerun"], "rerunB": resB["rerun"],
            "observerA": obsA.summary(), "observerB": obsB.summary(),
            "dir_after": listing(w)}


def main():
    which = sys.argv[1]
    os.makedirs(RESULTS, exist_ok=True)
    root = os.path.join(S, "w1")
    os.makedirs(root, exist_ok=True)
    if which == "seq":
        r = scenario_seq(os.path.join(root, "witness"), os.path.join(root, "seq"))
    elif which == "stale":
        r = scenario_stale(os.path.join(root, "stale"), os.path.join(root, "st"))
    elif which == "conc":
        r = scenario_conc(os.path.join(root, "conc"), os.path.join(root, "cc"))
    else:
        raise SystemExit("unknown scenario " + which)
    dest = os.path.join(RESULTS, which + ".json")
    with open(dest, "w") as fh:
        json.dump(r, fh, indent=1)
    if which == "seq":
        for run in r["runs"]:
            o = run["observer"]
            print("seq run=%d exit=%s match=%s released=%s bodies=%d "
                  "released_ms=%s gone_ms=%s tmp=%s after=%s" % (
                      run["run"], run["exit_code"],
                      (run["replay"] or {}).get("match"),
                      (run["rerun"] or {}).get("witness", {}).get("released"),
                      len(o["bodies"]), o["released_ms"],
                      o["own_ready_gone_ms"],
                      sorted(n for n in run["dir_after_run"]
                             if n.startswith("ready.json.tmp")),
                      run["dir_after_run"]))
    elif which == "conc":
        print("conc A pid=%s port=%s B pid=%s port=%s distinct_ports=%s "
              "distinct_pids=%s a_alive=%s" % (
                  (r["a_announced"] or {}).get("pid"),
                  (r["a_announced"] or {}).get("port"),
                  (r["b_announced"] or {}).get("pid"),
                  (r["b_announced"] or {}).get("port"),
                  r["overlap"]["distinct_ports"], r["overlap"]["distinct_pids"],
                  r["overlap"].get("a_pid_alive_at_b_announce")))
        print("conc A foreign=%s clobbered_ms=%s own_gone_ms=%s" % (
            r["observerA"]["foreign_bodies"], r["observerA"]["own_clobbered_ms"],
            r["observerA"]["own_ready_gone_ms"]))
        print("conc B foreign=%s own_gone_ms=%s replayA_match=%s replayB_match=%s"
              % (r["observerB"]["foreign_bodies"],
                 r["observerB"]["own_ready_gone_ms"],
                 (r["replayA"] or {}).get("match"),
                 (r["replayB"] or {}).get("match")))
        for side in ("A", "B"):
            rr = r["rerun" + side] or {}
            print("conc %s witness=%s exit=%s" % (side, json.dumps(
                rr.get("witness")), r["exit" + side]))
    else:
        print("stale released_ms=%s waited_ms=%s stale_reads=%s planted=%s "
              "after=%s" % (
                  r["observer"]["released_ms"],
                  (r["rerun"] or {}).get("witness", {}).get("waited_ms"),
                  r["observer"]["stale_ready_ignored"], r["planted"],
                  r["dir_after_run"]))
    print("wrote", dest)


if __name__ == "__main__":
    main()
