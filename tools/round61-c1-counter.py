#!/usr/bin/env python3
"""Round-61 C1 counter: fresh-nonce live Ollama v2 lifecycle at a committed tip, verified independently.

Usage: python3 tools/round61-c1-counter.py --repo REPO --tip REV [--work DIR] [--keep]

Frozen predicate (same sentence as .ufo/waves/round-61/controls/freeze.txt):
  C1-r61: a fresh-nonce hold-mode run of tools/kama-ollama-live.py (schema kama-ollama-live/v2) at the
  tip yields a receipt this counter's verifier accepts ONLY after (a) its own live HTTP contact with the
  still-running child during the hold window, (b) re-executing the evidence classifier itself on the
  receipt's capture bodies and matching the receipt's recorded findings, (c) re-hashing the run's model
  manifest and imported blob against the pinned digest, and (d) grading the /api/show capture; and every
  one of the 16 controls is rejected, errors=0.

The verifier uses constants frozen in THIS file, never the tip's registry/ollama-live-pin.tsv.
Output: one line, exit 0 iff met.
"""
import argparse
import copy
import hashlib
import http.client
import json
import os
import pathlib
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time

FROZEN_VERSION = "0.40.11"
FROZEN_BIN_SHA = "b0a4becfaf872e3ad5d2e9051244e0dfe55409f03d6e2cd9bd9c34400e201b4c"
FROZEN_MODEL_SHA = "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"
REAL_BIN = os.path.expanduser("~/.local/opt/ollama-v0.40.11/bin/ollama")
REGISTERED = {8080, 34113}
REQUIRED = ["binary-digest", "model-digest", "port-unregistered", "ready", "version",
            "running-exe-digest", "listener-owned", "tags-empty-before-create", "create",
            "tags-lists-model", "v1-models-lists-model", "show-model-info",
            "evidence-before-load", "generate", "ps-lists-loaded", "evidence-after-load",
            "hold-released", "teardown"]
TOOL_FILES = ["tools/kama-ollama-live.py", "tools/kama-ollama-evidence.py", "registry/ollama-live-pin.tsv"]
PREDICATE = ("C1-r61 hold-verified fresh-nonce v2 live run + 16/16 controls rejected, errors=0")
EVIDENCE_EXPECT = {"before": ("available_not_loaded", 1), "after": ("loaded_same_digest", 0)}


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def listening_ports():
    ports = set()
    for name in ("/proc/net/tcp", "/proc/net/tcp6"):
        try:
            with open(name) as f:
                next(f)
                for line in f:
                    c = line.split()
                    if len(c) > 3 and c[3] == "0A":
                        ports.add(int(c[1].rsplit(":", 1)[1], 16))
        except OSError:
            pass
    return ports


def http_call(port, method, path, body=None, timeout=15):
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=timeout)
    try:
        data = json.dumps(body).encode() if body is not None else None
        conn.request(method, path, body=data,
                     headers={"Content-Type": "application/json"} if data else {})
        resp = conn.getresponse()
        return resp.status, resp.read()
    finally:
        conn.close()


def run_classifier(tree, tags_bytes, ps_bytes, expect):
    """Re-execute the tip's evidence classifier on caller-supplied capture bytes."""
    tmp = tempfile.mkdtemp(prefix="ev-")
    try:
        tp = pathlib.Path(tmp) / "tags.json"
        pp = pathlib.Path(tmp) / "ps.json"
        tp.write_bytes(tags_bytes)
        pp.write_bytes(ps_bytes)
        p = subprocess.run([sys.executable, str(tree / "tools/kama-ollama-evidence.py"),
                            "--tags", str(tp), "--ps", str(pp), "--expect", expect],
                           capture_output=True, text=True, timeout=60)
        try:
            finding = json.loads(p.stdout).get("finding_id")
        except ValueError:
            finding = None
        return finding, p.returncode
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def verify(receipt, run_dir, nonce, tree=None, live_port=None):
    """Receipt-level acceptance. Returns a list of failure strings (empty = accepted).

    tree: when given, re-executes the evidence classifier on the capture bodies and
    requires its findings to equal the receipt's recorded evidence block — a canned
    finding cannot pass.
    live_port: when given, the caller's own live contact with the still-running
    child already succeeded; the receipt must record a released, unsignalled hold
    on that port and a teardown with child_pre_dead False — a child externally
    killed between capture and teardown cannot forge this.
    """
    bad = []
    if not isinstance(receipt, dict):
        return ["receipt-not-object"]
    if receipt.get("schema") != "kama-ollama-live/v2":
        bad.append("schema")
    if receipt.get("nonce") != nonce:
        bad.append("nonce")
    if receipt.get("verdict") != "MODEL_OK":
        bad.append("verdict")
    if receipt.get("binary_sha256") != FROZEN_BIN_SHA:
        bad.append("binary-sha")
    if receipt.get("pdeathsig") != "armed:PR_SET_PDEATHSIG=SIGKILL":
        bad.append("pdeathsig")
    if receipt.get("signalled") is not None:
        bad.append("signalled")
    port = receipt.get("port")
    if not isinstance(port, int) or port in REGISTERED or port in listening_ports():
        bad.append("port")
    by_id = {c.get("id"): c for c in receipt.get("checks", []) if isinstance(c, dict)}
    for cid in REQUIRED:
        c = by_id.get(cid)
        if not c or c.get("passed") is not True or c.get("evaluated") is not True:
            bad.append("check:" + cid)
    caps = receipt.get("captures", {})
    for name, cap in caps.items():
        body = cap.get("body", "") if isinstance(cap, dict) else ""
        if not isinstance(cap, dict) or hashlib.sha256(body.encode("utf-8")).hexdigest() != cap.get("sha256"):
            bad.append("capture-sha:" + name)
    qualified = f"kama-{nonce}:latest"
    try:
        tags = json.loads(caps["tags"]["body"])
        ent = [m for m in tags["models"] if m.get("name") == qualified]
        tag_digest = ent[0]["digest"]
        if len(ent) != 1 or not re.fullmatch(r"[0-9a-f]{64}", tag_digest):
            bad.append("tags-entry")
        ps = json.loads(caps["ps-after"]["body"])
        pe = [m for m in ps["models"] if m.get("name") == qualified]
        if len(pe) != 1 or pe[0].get("digest") != tag_digest:
            bad.append("ps-digest")
        if json.loads(caps["version"]["body"]).get("version") != FROZEN_VERSION:
            bad.append("version")
        if json.loads(caps["ps-before"]["body"]).get("models") != []:
            bad.append("ps-before-not-empty")
        show = json.loads(caps["show"]["body"])
        show_details = show.get("details") if isinstance(show, dict) else None
        if (caps["show"].get("status") != 200
                or not isinstance(show_details, dict) or not show_details.get("family")
                or "FROM" not in (show.get("modelfile") or "")):
            bad.append("show-surface")
    except (KeyError, IndexError, TypeError, ValueError):
        bad.append("capture-parse")
    ev = receipt.get("evidence") or {}
    for label, (want_finding, want_exit) in EVIDENCE_EXPECT.items():
        rec_ev = ev.get(label) or {}
        if rec_ev.get("finding_id") != want_finding or rec_ev.get("exit") != want_exit:
            bad.append("evidence-recorded:" + label)
    if tree is not None:
        try:
            tags_raw = caps["tags"]["body"].encode()
            ps_b_raw = caps["ps-before"]["body"].encode()
            ps_a_raw = caps["ps-after"]["body"].encode()
        except (KeyError, AttributeError):
            bad.append("evidence-inputs")
        else:
            f_b, e_b = run_classifier(tree, tags_raw, ps_b_raw, qualified)
            f_a, e_a = run_classifier(tree, tags_raw, ps_a_raw, qualified)
            if (f_b, e_b) != EVIDENCE_EXPECT["before"]:
                bad.append("evidence-reexec:before")
            if (f_a, e_a) != EVIDENCE_EXPECT["after"]:
                bad.append("evidence-reexec:after")
            if (ev.get("before") or {}).get("finding_id") != f_b or (ev.get("after") or {}).get("finding_id") != f_a:
                bad.append("evidence-mismatch")
    td = receipt.get("teardown") or {}
    if (td.get("port_closed") is not True or td.get("returncode") not in (0, -15)
            or td.get("sigkill_needed") or td.get("child_pre_dead") is not False):
        bad.append("teardown")
    hold = receipt.get("hold") or {}
    if hold and (hold.get("released") is not True or hold.get("signalled") is not False):
        bad.append("hold")
    if live_port is not None:
        if not hold or hold.get("released") is not True or hold.get("signalled") is not False:
            bad.append("hold-live")
        if hold.get("port") != live_port:
            bad.append("hold-port")
    rd = pathlib.Path(run_dir)
    try:
        log = (rd / "serve.log").read_text(errors="replace")
    except OSError:
        log = ""
    if not re.search(rf"Listening on 127\.0\.0\.1:{port} \(version {re.escape(FROZEN_VERSION)}\)", log):
        bad.append("log-listening")
    if 'POST     "/api/generate"' not in log:
        bad.append("log-generate")
    manifests = list(rd.glob(f"models/manifests*/**/kama-{nonce}/latest"))
    if not manifests:
        bad.append("manifest")
    else:
        try:
            if f"sha256:{FROZEN_MODEL_SHA}" not in manifests[0].read_text():
                bad.append("manifest-layer")
        except OSError:
            bad.append("manifest-layer")
    blob = rd / "models" / "blobs" / f"sha256-{FROZEN_MODEL_SHA}"
    try:
        if sha256_file(blob) != FROZEN_MODEL_SHA:
            bad.append("blob-sha")
    except OSError:
        bad.append("blob-missing")
    return bad


def run_tool_hold(tree, work, hold_dir, nonce, timeout_s=300):
    """Spawn the tip tool in hold mode; return (proc, receipt_path, hold_dict|None)."""
    out = pathlib.Path(work) / "receipt.json"
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    proc = subprocess.Popen([sys.executable, str(tree / "tools/kama-ollama-live.py"),
                             "--work", str(work), "--nonce", nonce, "--out", str(out),
                             "--hold-dir", str(hold_dir)],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env)
    hold_path = pathlib.Path(hold_dir) / "hold.json"
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        if hold_path.exists():
            try:
                return proc, out, json.loads(hold_path.read_text())
            except ValueError:
                pass
        if proc.poll() is not None:
            break
        time.sleep(0.3)
    try:
        proc.kill()
    except OSError:
        pass
    return proc, out, None


def run_tool_plain(tree, work, nonce, extra=(), timeout_s=300):
    out = pathlib.Path(work) / "receipt.json"
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    p = subprocess.run([sys.executable, str(tree / "tools/kama-ollama-live.py"), "--work", str(work),
                        "--nonce", nonce, "--out", str(out), *extra],
                       capture_output=True, text=True, env=env, timeout=timeout_s)
    try:
        receipt = json.loads(out.read_text())
    except (OSError, ValueError):
        receipt = None
    return p.returncode, receipt


def synth_receipt(rec):
    return copy.deepcopy(rec)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--tip", required=True)
    ap.add_argument("--work", default=None)
    ap.add_argument("--keep", action="store_true")
    a = ap.parse_args(argv)
    root = a.work or os.path.join(os.environ.get("HYAKU_SCRATCH", "/fast/scratch/hyaku"), "kama-r61", "c1")
    os.makedirs(root, exist_ok=True)
    work = pathlib.Path(tempfile.mkdtemp(dir=root, prefix="c1-"))
    errors = 0
    live_ok = 0
    rec = None
    run1 = None
    nonce = None
    fam = {"fake": 0, "stale": 0, "tamper": 0, "log": 0, "predead": 0, "show": 0,
           "sigterm": 0, "pdeath": 0}
    try:
        tree = work / "tree"
        tree.mkdir()
        env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        ar = subprocess.run(["git", "-C", a.repo, "archive", a.tip, *TOOL_FILES], capture_output=True, env=env)
        if ar.returncode:
            print(f"tool_present=0 live_ok=0/1 fake_rejected=0/2 stale_rejected=0/1 tamper_rejected=0/6 "
                  f"log_rejected=0/1 predead_rejected=0/3 show_rejected=0/1 sigterm_rejected=0/1 "
                  f"pdeath_ok=0/1 errors=0 met=False predicate={PREDICATE!r}")
            return 1
        subprocess.run(["tar", "-x", "-C", str(tree)], input=ar.stdout, check=True)
        nonce = "c1" + os.urandom(5).hex()
        run1 = work / "run1"
        hd = work / "hd"
        run1.mkdir()
        hd.mkdir()
        proc, out_path, hold = run_tool_hold(tree, run1, hd, nonce)
        if hold is not None:
            try:
                st_v, raw_v = http_call(hold["port"], "GET", "/api/version", timeout=10)
                live_version = json.loads(raw_v).get("version") if st_v == 200 else None
                st_t, raw_t = http_call(hold["port"], "GET", "/api/tags", timeout=10)
                live_names = [m.get("name") for m in json.loads(raw_t).get("models", [])] if st_t == 200 else []
                st_s, raw_s = http_call(hold["port"], "POST", "/api/show",
                                        {"model": hold["qualified"]}, timeout=10)
                show_live = json.loads(raw_s) if st_s == 200 else {}
            except (OSError, ValueError, KeyError):
                live_version, live_names, show_live = None, [], {}
            live_contact = (live_version == FROZEN_VERSION and hold["qualified"] in live_names
                            and isinstance(show_live.get("details"), dict)
                            and bool(show_live["details"].get("family")))
            (pathlib.Path(hd) / "release").write_text("released by round61-c1-counter\n")
            try:
                proc.wait(timeout=120)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
                errors += 1
            try:
                rec = json.loads(out_path.read_text())
            except (OSError, ValueError):
                rec = None
            if rec is None:
                errors += 1
            elif live_contact and not verify(rec, run1, nonce, tree=tree, live_port=hold["port"]):
                live_ok = 1
        else:
            errors += 1
        # controls
        fake = work / "fake-ollama"
        fake.write_text("#!/usr/bin/env python3\nprint('fake')\n")
        fake.chmod(0o755)
        patched = work / "patched-ollama"
        shutil.copyfile(REAL_BIN, patched)
        with open(patched, "ab") as f:
            f.write(b"\0")
        patched.chmod(0o755)
        for label, binpath in (("fake", fake), ("patched", patched)):
            rd = work / f"run-{label}"
            rd.mkdir()
            c, r = run_tool_plain(tree, rd, "c1" + os.urandom(5).hex(), ("--ollama-bin", str(binpath)))
            if c != 0 and r is not None and r.get("verdict") == "BINARY_DIGEST_MISMATCH" and verify(r, rd, r.get("nonce")):
                fam["fake"] += 1
        if rec is not None:
            if verify(rec, run1, "c1" + os.urandom(5).hex()):
                fam["stale"] += 1
            t1 = synth_receipt(rec)
            t1["captures"]["tags"]["body"] = t1["captures"]["tags"]["body"].replace("kama-", "kamb-", 1)
            t2 = synth_receipt(rec)
            t2["binary_sha256"] = "0" * 64
            t3 = synth_receipt(rec)
            t3["port"] = 8080
            t4 = synth_receipt(rec)
            t4["captures"]["ps-after"]["body"] = json.dumps({"models": []})
            t4["captures"]["ps-after"]["sha256"] = hashlib.sha256(
                t4["captures"]["ps-after"]["body"].encode()).hexdigest()
            t5 = synth_receipt(rec)
            t5["pdeathsig"] = "unavailable:no-ctypes-prctl"
            t6 = synth_receipt(rec)
            t6["teardown"]["returncode"] = 0
            t6["teardown"]["sigkill_needed"] = False
            t6["hold"] = {"released": True, "signalled": False, "port": rec.get("port")}
            t6["signalled"] = {"signals": [15], "teardown_clean": True}
            for t in (t1, t2, t3, t4, t5, t6):
                if verify(t, run1, nonce, tree=tree):
                    fam["tamper"] += 1
            # synthetic receipts asserting clean teardown while the child was
            # already dead before teardown began (post-capture external kill shape)
            s1 = synth_receipt(rec)
            s1["teardown"]["child_pre_dead"] = True
            s2 = synth_receipt(rec)
            del s2["teardown"]["child_pre_dead"]
            s3 = synth_receipt(rec)
            s3["signalled"] = {"signals": [15]}
            for s in (s1, s2, s3):
                if verify(s, run1, nonce, tree=tree):
                    fam["predead"] += 1
            # show-surface fault: 404 body, every recorded check kept green
            t7 = synth_receipt(rec)
            t7["captures"]["show"]["body"] = "404 page not found"
            t7["captures"]["show"]["status"] = 404
            t7["captures"]["show"]["sha256"] = hashlib.sha256(b"404 page not found").hexdigest()
            if verify(t7, run1, nonce, tree=tree):
                fam["show"] += 1
            logp = run1 / "serve.log"
            keep = logp.read_bytes()
            logp.unlink()
            if verify(rec, run1, nonce, tree=tree):
                fam["log"] += 1
            logp.write_bytes(keep)
        # live-family control: SIGTERM the tool during its hold — the child must
        # be reaped (port closed, no orphan listener) and no MODEL_OK receipt may
        # be produced; a surviving listener on the run's port fails the control.
        run_sig = work / "run-sig"
        hd_sig = work / "hd-sig"
        run_sig.mkdir()
        hd_sig.mkdir()
        sp, sout, shold = run_tool_hold(tree, run_sig, hd_sig, "c1" + os.urandom(5).hex())
        if shold is not None:
            os.kill(sp.pid, signal.SIGTERM)
            try:
                sp.wait(timeout=60)
            except subprocess.TimeoutExpired:
                sp.kill()
                sp.wait()
            time.sleep(0.6)
            sig_receipt = None
            try:
                sig_receipt = json.loads(sout.read_text())
            except (OSError, ValueError):
                sig_receipt = None
            if shold["port"] not in listening_ports() and (
                    sig_receipt is None or sig_receipt.get("verdict") != "MODEL_OK"):
                fam["sigterm"] += 1
        # pdeathsig proof: run the real tool in hold mode, SIGKILL the tool
        # process itself, then the kernel must have killed the child — the port
        # refuses and the child pid is gone.
        run_pd = work / "run-pd"
        hd_pd = work / "hd-pd"
        run_pd.mkdir()
        hd_pd.mkdir()
        pp, pout, phold = run_tool_hold(tree, run_pd, hd_pd, "c1" + os.urandom(5).hex())
        if phold is not None:
            child_pid = phold["pid"]
            os.kill(pp.pid, signal.SIGKILL)
            try:
                pp.wait(timeout=30)
            except subprocess.TimeoutExpired:
                pass
            deadline = time.time() + 15
            while time.time() < deadline:
                if phold["port"] not in listening_ports():
                    break
                time.sleep(0.3)
            child_gone = not pathlib.Path(f"/proc/{child_pid}").exists()
            if phold["port"] not in listening_ports() and child_gone:
                fam["pdeath"] += 1
        met = (live_ok == 1 and fam["fake"] == 2 and fam["stale"] == 1 and fam["tamper"] == 6
               and fam["log"] == 1 and fam["predead"] == 3 and fam["show"] == 1
               and fam["sigterm"] == 1 and fam["pdeath"] == 1 and errors == 0)
        print(f"tool_present=1 live_ok={live_ok}/1 fake_rejected={fam['fake']}/2 "
              f"stale_rejected={fam['stale']}/1 tamper_rejected={fam['tamper']}/6 "
              f"log_rejected={fam['log']}/1 predead_rejected={fam['predead']}/3 "
              f"show_rejected={fam['show']}/1 sigterm_rejected={fam['sigterm']}/1 "
              f"pdeath_ok={fam['pdeath']}/1 errors={errors} met={met} predicate={PREDICATE!r}")
        return 0 if met else 1
    finally:
        if not a.keep:
            shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
