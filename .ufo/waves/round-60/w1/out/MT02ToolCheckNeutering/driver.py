#!/usr/bin/env python3
"""MT02ToolCheckNeutering — round 60 C1 tool-check neutering mutants.

For each of the 8 live-tool checks: neuter it (condition -> True) in the scratch
tree copy, run the tool for real (fresh nonce, fresh work dir, tool spawns its own
lane-owned ollama child), then run the counter's verify() on the receipt + work dir.
Baseline (pristine) and restored-bytes runs bracket the mutants. Extra bad-world
probes exercise the re-derivations where a false condition is reachable via tool
inputs only (seeded model store, --no-generate, appended-byte binary).
"""
import concurrent.futures
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
OUTRUNS = pathlib.Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-60/w1/out/MT02ToolCheckNeutering/runs")
RESULTS = SCRATCH / "results.jsonl"
LANE_LIVE = "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-ollama-live.py"
LANE_EVID = "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-ollama-evidence.py"
LANE_PIN = "/home/vgpnk/Projects/shokunin/kama-shokunin/registry/ollama-live-pin.tsv"
REAL_BIN = os.path.expanduser("~/.local/opt/ollama-v0.40.11/bin/ollama")

spec = importlib.util.spec_from_file_location("c1counter", COUNTER)
c1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c1)


def sha(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def apply_mutation(mutations):
    """Apply exact-once string replacements to the tree's live tool; return mutated sha."""
    src = LIVE.read_text()
    for old, new in mutations:
        n = src.count(old)
        assert n == 1, f"mutation anchor not unique ({n}): {old!r}"
        src = src.replace(old, new)
    LIVE.write_text(src)
    return sha(LIVE)


# One targeted mutation per check: the condition is forced True (sensor neutered);
# everything else, including the detail string and downstream flow, stays pristine.
MUT = {
    "mut-ready": [("check('ready', ready, ", "check('ready', True, ")],
    "mut-version": [("st == 200 and version == pin['version']", "True")],
    "mut-running-exe-digest": [("check('running-exe-digest', exe_sha == pin['bin_sha256']",
                                "check('running-exe-digest', True")],
    "mut-listener-owned": [("check('listener-owned', pid_owns_listener(proc.pid, port)",
                            "check('listener-owned', True")],
    "mut-tags-empty-before-create": [("check('tags-empty-before-create', st == 200 and isinstance(tags0, dict) and tags0.get('models') == []",
                                      "check('tags-empty-before-create', True")],
    "mut-evidence-before-load": [("check('evidence-before-load', finding == 'available_not_loaded' and ec == 1",
                                  "check('evidence-before-load', True")],
    "mut-ps-lists-loaded": [("check('ps-lists-loaded', len(ps_entries) == 1 and ps_entries[0].get('digest') == tag_digest",
                             "check('ps-lists-loaded', True")],
    "mut-teardown": [("check('teardown', receipt['teardown']['port_closed'] and not killed",
                      "check('teardown', True")],
}
ENABLE_BIN = [("check('binary-digest', bin_sha == pin['bin_sha256']", "check('binary-digest', True")]

CASES = []  # (name, mutations or None, extra_args, seed_from)
for name in MUT:
    CASES.append((name, MUT[name], [], None))
CASES += [
    ("probe-ps-nogen", MUT["mut-ps-lists-loaded"], ["--no-generate"], None),
    ("probe-bin-patched", MUT["mut-running-exe-digest"] + ENABLE_BIN, None, "PATCHEDBIN"),
    ("probe-tags-seeded-pristine", None, [], "BASEMODELS"),
    ("probe-tags-seeded-mut", MUT["mut-tags-empty-before-create"], [], "BASEMODELS"),
    ("restored-pristine", None, [], None),
]


def run_case(name, mutations, extra, seed_from, base_models=None):
    work = SCRATCH / "runs" / name / "work"
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    nonce = "mt02" + secrets.token_hex(4)
    if seed_from == "BASEMODELS":
        shutil.copytree(base_models, work / "models")
    binpath = None
    if seed_from == "PATCHEDBIN":
        binpath = SCRATCH / "runs" / name / "ollama-patched"
        shutil.copyfile(REAL_BIN, binpath)
        with open(binpath, "ab") as f:
            f.write(b"\0")
        binpath.chmod(0o755)
        extra = list(extra or []) + ["--ollama-bin", str(binpath)]
    mut_sha = apply_mutation(mutations) if mutations else sha(LIVE)
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env["TMPDIR"] = str(SCRATCH / "tmp")
    out = work / "receipt.json"
    t0 = time.time()
    try:
        p = subprocess.run([sys.executable, str(LIVE), "--work", str(work), "--nonce", nonce,
                            "--out", str(out), *extra],
                           capture_output=True, text=True, env=env, timeout=900, cwd=str(SCRATCH))
        exit_code, stderr_tail = p.returncode, p.stderr[-400:]
    except subprocess.TimeoutExpired:
        exit_code, stderr_tail = "TIMEOUT", ""
    elapsed = round(time.time() - t0, 1)
    try:
        rec = json.loads(out.read_text())
    except (OSError, ValueError):
        rec = None
    bad = c1.verify(rec, work, nonce) if rec is not None else ["receipt-missing"]
    row = {
        "case": name, "nonce": nonce, "exit": exit_code, "elapsed_s": elapsed,
        "verdict": rec.get("verdict") if rec else None,
        "fault": (rec.get("fault") or rec.get("setup_error")) if rec else None,
        "port": rec.get("port") if rec else None,
        "mutated_live_sha256": mut_sha,
        "pristine_live_sha256": sha(LANE_LIVE),
        "verify_bad": bad,
        "verify_verdict": "accepted" if not bad else "rejected",
        "stderr_tail": stderr_tail,
    }
    # evidence into the out dir immediately (scratch is transient)
    dst = OUTRUNS / name
    dst.mkdir(parents=True, exist_ok=True)
    if rec is not None:
        (dst / "receipt.json").write_text(out.read_text())
    if (work / "serve.log").exists():
        shutil.copyfile(work / "serve.log", dst / "serve.log")
    (dst / "result.json").write_text(json.dumps(row, indent=1) + "\n")
    with open(RESULTS, "a") as f:
        f.write(json.dumps(row) + "\n")
    # restore pristine bytes after every case
    shutil.copyfile(LANE_LIVE, LIVE)
    print(json.dumps({k: row[k] for k in ("case", "exit", "verdict", "verify_verdict", "verify_bad")}), flush=True)
    return row


def main():
    OUTRUNS.mkdir(parents=True, exist_ok=True)
    RESULTS.write_text("")
    baseline_models = SCRATCH / "runs" / "baseline-pristine" / "work" / "models"

    print("== baseline (pristine bytes; gate) ==", flush=True)
    if len(sys.argv) > 2 and sys.argv[1] == "one":
        only = sys.argv[2]
        case = next(c for c in CASES if c[0] == only)
        row = run_case(*case, base_models=SCRATCH / "runs" / "baseline-pristine" / "work" / "models")
        restored = {"live": sha(LIVE), "lane_live": sha(LANE_LIVE)}
        (SCRATCH / "restoration.json").write_text(json.dumps(restored, indent=1) + "\n")
        print(json.dumps(restored), flush=True)
        return 0 if not row["verify_bad"] or row["case"].startswith("probe") else 1
    base = run_case("baseline-pristine", None, [], None)
    if base["exit"] != 0 or base["verify_bad"]:
        print(f"BASELINE FAILED exit={base['exit']} verify={base['verify_bad']} -> all mutant results inconclusive")
        return 1

    print("== mutants + probes (2 workers) ==", flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
        futs = [ex.submit(run_case, n, m, e, s, baseline_models) for (n, m, e, s) in CASES]
        for f in concurrent.futures.as_completed(futs):
            f.result()

    print("== restoration evidence ==", flush=True)
    restored = {"live": sha(LIVE), "lane_live": sha(LANE_LIVE),
                "evid": sha(TREE / "tools" / "kama-ollama-evidence.py"), "lane_evid": sha(LANE_EVID),
                "pin": sha(TREE / "registry" / "ollama-live-pin.tsv"), "lane_pin": sha(LANE_PIN)}
    (SCRATCH / "restoration.json").write_text(json.dumps(restored, indent=1) + "\n")
    print(json.dumps(restored), flush=True)
    ok = all(restored[k] == restored["lane_" + k.rstrip("e").rstrip("v").rstrip("e")] if False else True for k in ())
    assert restored["live"] == restored["lane_live"], "live tool NOT restored"
    assert restored["evid"] == restored["lane_evid"], "evidence tool NOT restored"
    assert restored["pin"] == restored["lane_pin"], "pin NOT restored"
    print("restored_ok=True")
    return 0


if __name__ == "__main__":
    sys.exit(main())
