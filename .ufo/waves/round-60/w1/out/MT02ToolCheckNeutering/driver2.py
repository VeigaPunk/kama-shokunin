#!/usr/bin/env python3
"""MT02ToolCheckNeutering pass 2 — STRICTLY SEQUENTIAL, one mutant at a time.

Each case: mutate the scratch tree's live tool (exact-once anchor), assert the
mutation marker is present in the bytes about to be executed, hash them, run the
tool for real (fresh nonce, fresh work dir, tool spawns its own child), verify()
from the lane counter, restore pristine bytes, assert restoration hash.
Pass 1 ran 2 workers on one shared tree file and raced; its evidence is archived
as runs-pass1-raced and superseded by this pass.
"""
import importlib.util
import json
import os
import pathlib
import secrets
import shutil
import subprocess
import sys
import time

SCRATCH = pathlib.Path("/fast/scratch/hyaku/kama-r60/MT02ToolCheckNeutering")
TREE = SCRATCH / "tree"
LIVE = TREE / "tools" / "kama-ollama-live.py"
COUNTER = "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round60-c1-counter.py"
LANE_LIVE = "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-ollama-live.py"
LANE_EVID = "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-ollama-evidence.py"
LANE_PIN = "/home/vgpnk/Projects/shokunin/kama-shokunin/registry/ollama-live-pin.tsv"
OUTRUNS = pathlib.Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-60/w1/out/MT02ToolCheckNeutering/runs")
RESULTS = SCRATCH / "results2.jsonl"
REAL_BIN = os.path.expanduser("~/.local/opt/ollama-v0.40.11/bin/ollama")
PRISTINE_SHA = "9d1c688bd2951485fa5701ca2273b98e7333ec95060c34bbdb76942050472aaf"

spec = importlib.util.spec_from_file_location("c1counter", COUNTER)
c1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c1)


def sha_bytes(b):
    import hashlib
    return hashlib.sha256(b).hexdigest()


def sha(path):
    return sha_bytes(pathlib.Path(path).read_bytes())


# (name, [(old, new)...], marker, extra_args, seed)
M_READY = [("check('ready', ready, ", "check('ready', True, ")]
M_VER = [("st == 200 and version == pin['version']", "True")]
M_EXE = [("check('running-exe-digest', exe_sha == pin['bin_sha256']", "check('running-exe-digest', True")]
M_LIS = [("check('listener-owned', pid_owns_listener(proc.pid, port)", "check('listener-owned', True")]
M_TAG = [("check('tags-empty-before-create', st == 200 and isinstance(tags0, dict) and tags0.get('models') == []",
          "check('tags-empty-before-create', True")]
M_EVB = [("check('evidence-before-load', finding == 'available_not_loaded' and ec == 1",
          "check('evidence-before-load', True")]
M_PSL = [("check('ps-lists-loaded', len(ps_entries) == 1 and ps_entries[0].get('digest') == tag_digest",
          "check('ps-lists-loaded', True")]
M_TDN = [("check('teardown', receipt['teardown']['port_closed'] and not killed", "check('teardown', True")]
M_BIN = [("check('binary-digest', bin_sha == pin['bin_sha256']", "check('binary-digest', True")]

CASES = [
    ("baseline-pristine", None, None, [], None),
    ("mut-ready", M_READY, "check('ready', True, ", [], None),
    ("mut-version", M_VER, "check('version', True,", [], None),
    ("mut-running-exe-digest", M_EXE, "check('running-exe-digest', True", [], None),
    ("mut-listener-owned", M_LIS, "check('listener-owned', True", [], None),
    ("mut-tags-empty-before-create", M_TAG, "check('tags-empty-before-create', True", [], None),
    ("mut-evidence-before-load", M_EVB, "check('evidence-before-load', True", [], None),
    ("mut-ps-lists-loaded", M_PSL, "check('ps-lists-loaded', True", [], None),
    ("mut-teardown", M_TDN, "check('teardown', True", [], None),
    ("probe-ps-nogen", M_PSL, "check('ps-lists-loaded', True", ["--no-generate"], None),
    ("probe-bin-patched", M_EXE + M_BIN, "check('binary-digest', True", ["PATCHEDBIN"], None),
    ("probe-tags-seeded-pristine", None, None, [], "BASEMODELS"),
    ("probe-tags-seeded-mut", M_TAG, "check('tags-empty-before-create', True", [], "BASEMODELS"),
    ("restored-pristine", None, None, [], None),
]


def run_case(name, mutations, marker, extra, seed, base_models):
    assert sha(LIVE) == PRISTINE_SHA, f"tree not pristine before {name}"
    work = SCRATCH / "runs" / name / "work"
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    nonce = "mt02" + secrets.token_hex(4)
    if seed == "BASEMODELS":
        shutil.copytree(base_models, work / "models")
    binpath = None
    if "PATCHEDBIN" in extra:
        extra = [e for e in extra if e != "PATCHEDBIN"]
        binpath = SCRATCH / "runs" / name / "ollama-patched"
        shutil.copyfile(REAL_BIN, binpath)
        with open(binpath, "ab") as f:
            f.write(b"\0")
        binpath.chmod(0o755)
        extra = extra + ["--ollama-bin", str(binpath)]
    if mutations:
        src = LIVE.read_text()
        for old, new in mutations:
            assert src.count(old) == 1, f"anchor not unique for {name}: {old!r}"
            src = src.replace(old, new)
        LIVE.write_text(src)
        assert marker in src, f"marker missing for {name}"
    exec_sha = sha(LIVE)  # bytes about to be executed (sequential: no racing writer)
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env["TMPDIR"] = str(SCRATCH / "tmp")
    out = work / "receipt.json"
    t0 = time.time()
    try:
        p = subprocess.run([sys.executable, str(LIVE), "--work", str(work), "--nonce", nonce,
                            "--out", str(out), *extra],
                           capture_output=True, text=True, env=env, timeout=900, cwd=str(SCRATCH))
        exit_code, stderr_tail = p.returncode, p.stderr[-300:]
    except subprocess.TimeoutExpired:
        exit_code, stderr_tail = "TIMEOUT", ""
    elapsed = round(time.time() - t0, 1)
    try:
        rec = json.loads(out.read_text())
    except (OSError, ValueError):
        rec = None
    bad = c1.verify(rec, work, nonce) if rec is not None else ["receipt-missing"]
    row = {"case": name, "nonce": nonce, "exit": exit_code, "elapsed_s": elapsed,
           "verdict": rec.get("verdict") if rec else None,
           "fault": (rec.get("fault") or rec.get("setup_error")) if rec else None,
           "port": rec.get("port") if rec else None,
           "exec_sha256": exec_sha, "pristine_sha256": PRISTINE_SHA,
           "verify_bad": bad, "verify_verdict": "accepted" if not bad else "rejected",
           "stderr_tail": stderr_tail}
    dst = OUTRUNS / name
    dst.mkdir(parents=True, exist_ok=True)
    if rec is not None:
        (dst / "receipt.json").write_text(out.read_text())
    if (work / "serve.log").exists():
        shutil.copyfile(work / "serve.log", dst / "serve.log")
    (dst / "result.json").write_text(json.dumps(row, indent=1) + "\n")
    with open(RESULTS, "a") as f:
        f.write(json.dumps(row) + "\n")
    shutil.copyfile(LANE_LIVE, LIVE)  # restore exact bytes after every case
    assert sha(LIVE) == PRISTINE_SHA, f"restoration failed after {name}"
    print(json.dumps({k: row[k] for k in ("case", "exit", "verdict", "exec_sha256", "verify_verdict", "verify_bad")}), flush=True)
    return row


def main():
    OUTRUNS.mkdir(parents=True, exist_ok=True)
    RESULTS.write_text("")
    assert sha(LANE_LIVE) == PRISTINE_SHA
    base_models = None
    for (name, muts, marker, extra, seed) in CASES:
        if name == "baseline-pristine":
            row = run_case(name, muts, marker, extra, seed, None)
            if row["exit"] != 0 or row["verify_bad"]:
                print(f"BASELINE FAILED -> all inconclusive: {row}")
                return 1
            base_models = SCRATCH / "runs" / name / "work" / "models"
        else:
            run_case(name, muts, marker, extra, seed, base_models)
    final = {"live": sha(LIVE), "lane_live": sha(LANE_LIVE),
             "evid": sha(TREE / "tools" / "kama-ollama-evidence.py"), "lane_evid": sha(LANE_EVID),
             "pin": sha(TREE / "registry" / "ollama-live-pin.tsv"), "lane_pin": sha(LANE_PIN)}
    (SCRATCH / "restoration2.json").write_text(json.dumps(final, indent=1) + "\n")
    ok = final["live"] == final["lane_live"] and final["evid"] == final["lane_evid"] and final["pin"] == final["lane_pin"]
    print("restored_ok=" + str(ok).lower(), json.dumps(final), flush=True)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
