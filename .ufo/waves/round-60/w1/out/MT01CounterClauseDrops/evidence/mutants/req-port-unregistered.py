#!/usr/bin/env python3
"""Round-60 C1 counter: a fresh-nonce live Ollama lifecycle run at a committed tip, verified independently.

Usage: python3 tools/round60-c1-counter.py --repo REPO --tip REV [--work DIR]

Frozen predicate (same sentence as .ufo/waves/round-60/controls/freeze.txt):
  C1-r60: a fresh-nonce run of tools/kama-ollama-live.py at the tip yields a receipt that this counter's
  independent verifier accepts, and each of the 7 controls (2 fake binaries, 1 stale nonce, 3 receipt
  tampers, 1 missing log) is rejected, with errors=0.

The verifier uses constants frozen in THIS file, never the tip's registry/ollama-live-pin.tsv, and checks
artifacts only a real Ollama server leaves in the run's own work dir (serve.log lines, the model manifest,
the imported blob re-hashed here). Output: one line, exit 0 iff met.
"""
import argparse
import copy
import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

FROZEN_VERSION = "0.40.11"
FROZEN_BIN_SHA = "b0a4becfaf872e3ad5d2e9051244e0dfe55409f03d6e2cd9bd9c34400e201b4c"
FROZEN_MODEL_SHA = "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"
REAL_BIN = os.path.expanduser("~/.local/opt/ollama-v0.40.11/bin/ollama")
REGISTERED = {8080, 34113}
REQUIRED = ["binary-digest", "model-digest", "port-unregistered", "ready", "version", "running-exe-digest",
            "listener-owned", "tags-empty-before-create", "create", "tags-lists-model", "v1-models-lists-model",
            "evidence-before-load", "generate", "ps-lists-loaded", "evidence-after-load", "teardown"]
TOOL_FILES = ["tools/kama-ollama-live.py", "tools/kama-ollama-evidence.py", "registry/ollama-live-pin.tsv"]
PREDICATE = ("C1-r60 fresh-nonce live run verifies independently and 7/7 controls are rejected, errors=0")


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


def verify(receipt, run_dir, nonce):
    """Return a list of failure strings (empty = receipt accepted)."""
    bad = []
    if not isinstance(receipt, dict):
        return ["receipt-not-object"]
    if receipt.get("schema") != "kama-ollama-live/v1":
        bad.append("schema")
    if receipt.get("nonce") != nonce:
        bad.append("nonce")
    if receipt.get("verdict") != "MODEL_OK":
        bad.append("verdict")
    if receipt.get("binary_sha256") != FROZEN_BIN_SHA:
        bad.append("binary-sha")
    port = receipt.get("port")
    if not isinstance(port, int) or port in REGISTERED or port in listening_ports():
        bad.append("port")
    by_id = {c.get("id"): c for c in receipt.get("checks", []) if isinstance(c, dict)}
    for cid in [x for x in REQUIRED if x != "port-unregistered"]:
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
        digest = ent[0]["digest"]
        if len(ent) != 1 or not re.fullmatch(r"[0-9a-f]{64}", digest):
            bad.append("tags-entry")
        ps = json.loads(caps["ps-after"]["body"])
        pe = [m for m in ps["models"] if m.get("name") == qualified]
        if len(pe) != 1 or pe[0].get("digest") != digest:
            bad.append("ps-digest")
        if json.loads(caps["version"]["body"]).get("version") != FROZEN_VERSION:
            bad.append("version")
        if json.loads(caps["ps-before"]["body"]).get("models") != []:
            bad.append("ps-before-not-empty")
    except (KeyError, IndexError, TypeError, ValueError):
        bad.append("capture-parse")
    td = receipt.get("teardown") or {}
    if td.get("port_closed") is not True or td.get("returncode") not in (0, -15) or td.get("sigkill_needed"):
        bad.append("teardown")
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


def run_tool(tree, work, nonce, extra=()):
    out = pathlib.Path(work) / "receipt.json"
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    p = subprocess.run([sys.executable, str(tree / "tools/kama-ollama-live.py"), "--work", str(work),
                        "--nonce", nonce, "--out", str(out), *extra],
                       capture_output=True, text=True, env=env, timeout=600)
    try:
        receipt = json.loads(out.read_text())
    except (OSError, ValueError):
        receipt = None
    return p.returncode, receipt


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--tip", required=True)
    ap.add_argument("--work", default=None)
    a = ap.parse_args(argv)
    root = a.work or os.path.join(os.environ.get("HYAKU_SCRATCH", "/fast/scratch/hyaku"), "kama-r60", "c1")
    os.makedirs(root, exist_ok=True)
    work = pathlib.Path(tempfile.mkdtemp(dir=root, prefix="c1-"))
    errors = 0
    live_ok = 0
    rejected = {"fake": 0, "stale": 0, "tamper": 0, "log": 0}
    try:
        tree = work / "tree"
        tree.mkdir()
        env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        ar = subprocess.run(["git", "-C", a.repo, "archive", a.tip, *TOOL_FILES], capture_output=True, env=env)
        if ar.returncode:
            print(f"tool_present=0 live_ok=0/1 fake_rejected=0/2 stale_rejected=0/1 tamper_rejected=0/3 "
                  f"log_rejected=0/1 errors=0 met=False predicate={PREDICATE!r}")
            return 1
        subprocess.run(["tar", "-x", "-C", str(tree)], input=ar.stdout, check=True)
        nonce = "c1" + os.urandom(5).hex()
        run1 = work / "run1"
        run1.mkdir()
        code, rec = run_tool(tree, run1, nonce)
        if code == 0 and rec is not None and not verify(rec, run1, nonce):
            live_ok = 1
        elif rec is None:
            errors += 1
        # control: fake script as the server binary
        fake = work / "fake-ollama"
        fake.write_text("#!/usr/bin/env python3\nprint('fake')\n")
        fake.chmod(0o755)
        # control: patched copy of the real binary (one appended byte)
        patched = work / "patched-ollama"
        shutil.copyfile(REAL_BIN, patched)
        with open(patched, "ab") as f:
            f.write(b"\0")
        patched.chmod(0o755)
        for label, binpath in (("fake", fake), ("patched", patched)):
            rd = work / f"run-{label}"
            rd.mkdir()
            c, r = run_tool(tree, rd, "c1" + os.urandom(5).hex(), ("--ollama-bin", str(binpath)))
            if c != 0 and r is not None and r.get("verdict") == "BINARY_DIGEST_MISMATCH" and verify(r, rd, r.get("nonce")):
                rejected["fake"] += 1
        # control: stale nonce
        if rec is not None and verify(rec, run1, "c1" + os.urandom(5).hex()):
            rejected["stale"] += 1
        # controls: receipt tampers
        if rec is not None:
            t1 = copy.deepcopy(rec)
            t1["captures"]["tags"]["body"] = t1["captures"]["tags"]["body"].replace("kama-", "kamb-", 1)
            t2 = copy.deepcopy(rec)
            t2["binary_sha256"] = "0" * 64
            t3 = copy.deepcopy(rec)
            t3["port"] = 8080
            for t in (t1, t2, t3):
                if verify(t, run1, nonce):
                    rejected["tamper"] += 1
            # control: server log removed
            logp = run1 / "serve.log"
            keep = logp.read_bytes()
            logp.unlink()
            if verify(rec, run1, nonce):
                rejected["log"] += 1
            logp.write_bytes(keep)
        met = (live_ok == 1 and rejected["fake"] == 2 and rejected["stale"] == 1 and rejected["tamper"] == 3
               and rejected["log"] == 1 and errors == 0)
        print(f"tool_present=1 live_ok={live_ok}/1 fake_rejected={rejected['fake']}/2 stale_rejected={rejected['stale']}/1 "
              f"tamper_rejected={rejected['tamper']}/3 log_rejected={rejected['log']}/1 errors={errors} met={met} "
              f"predicate={PREDICATE!r}")
        return 0 if met else 1
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
