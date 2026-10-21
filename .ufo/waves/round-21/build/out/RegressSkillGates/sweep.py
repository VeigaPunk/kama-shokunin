#!/usr/bin/env python3
"""Round-21 no-harm sweep of SKILL.md gate and selftest commands.

Runs every in-scope command with cwd = a clone root (base 7a6bc91, work
a29bb84) and records exit code, wall time, stdout/stderr digests, and whether
the run mutated the clone (git status digest before/after). `table` joins the
two passes into one TSV. Stdout identity is judged after normalizing only the
clone root ($R), the scratch root ($S), mkdtemp suffixes and ISO timestamps;
the raw digest is reported beside it so no difference is hidden.

Excluded (need a live llama-server, a live endpoint, or a live receipt):
  - tools/kama-llamacpp-live.py without --selftest/--help (launches llama-server)
  - tools/kama-probe.sh check | snapshot | consumers | listeners (curl to
    registered or listening live loopback services)
  - tests/llamacpp-live/check-receipt.py /tmp/kama-live.json (no such file)
  - install-tree-grid.py and install-links-grid.py default runs (mirror the
    real ~/.local/opt/llama-b11755 tree; owned by the C2 seats)
  - dispatch-provenance.py --spec/--attempt-result (wave policy and ledgers)

Usage:
  sweep.py run   --label base|work --root CLONE --scratch DIR [--only ID,ID]
  sweep.py table --scratch DIR --out FILE.tsv
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PY = "/usr/bin/python3"
MODEL = "/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf"
MODEL_SHA = "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"
SERVER_SHA = "b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804"
IMPL_SHA = "e404b91a81c9ab65756b6a57b97b42115a5f429c5060c4b7f0d717ca595b59ed"
PROBE_SHA = "36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3"
TOOL_SHA = "83eac5c0489377a88c8ecead89af4ca5f057bd0463d8bf8a79467eb6c5de88c4"
TREE_SHA = "6c216313a88d71b141bc62f684b8f95c040710ff050801b13521861826785a2c"
BASE_REV = "7a6bc911f9eb7dbea9e3b81f5f2449ecda10096d"
WORK_REV = "a29bb84abbb8b4d328f5970a89e448330a3a42ac"
FLEET_CENSUS = "/home/vgpnk/Projects/shokunin/scripts/sources-census.sh"
FLEET_ROOT = "/home/vgpnk/Projects/shokunin"

BOTH = ("base", "work")
WORK_ONLY = ("work",)

# Committed llama.cpp receipts (paths relative to the clone root) and schema.
RECEIPTS = [
    (".ufo/waves/round-16/live/receipt.json", "v1"),
    (".ufo/waves/round-16/live/receipt-frozen-probe.json", "v1"),
    (".ufo/waves/round-17/live/receipt-1.json", "v2"),
    (".ufo/waves/round-17/live/receipt-2.json", "v2"),
    (".ufo/waves/round-17/live/receipt-3.json", "v2"),
    (".ufo/waves/round-18/live-recovery/receipt-1.json", "v3"),
    (".ufo/waves/round-18/live-recovery/receipt-2.json", "v3"),
    (".ufo/waves/round-18/live-recovery/receipt-3.json", "v3"),
    (".ufo/waves/round-18/live/receipt-1.json", "v3"),
    (".ufo/waves/round-18/live/receipt-2.json", "v3"),
    (".ufo/waves/round-18/live/receipt-3.json", "v3"),
]

GROUP_R20 = "SKILL-R20-table"      # SKILL.md:650-659 (+ round-20 recorded recipe)
GROUP_R18 = "SKILL-R18-table"      # SKILL.md:607-614
GROUP_OTHER = "SKILL-other-rows"   # SKILL.md:303-306, 373-577 gate/selftest rows
GROUP_RECIPE = "R20-recipe-only"   # in commands.json, not in an SKILL row
GROUP_RCPT = "receipt-regression"  # committed receipts through the changed gate
GROUP_PAIR = "round-21-pair"
GROUP_WORK = "work-only"           # new in a29bb84; base has no counterpart

TMP_RE = re.compile(r"(/tmp/[A-Za-z0-9._-]+?)-[A-Za-z0-9_]{6,}")
ISO_RE = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z")


def build_specs():
    specs = []

    def add(sid, group, argv, r20=None, timeout=900, present=BOTH, note=""):
        specs.append({"id": sid, "group": group, "argv": argv, "r20": r20,
                      "timeout": timeout, "present": list(present), "note": note})

    gate = "{R}/tests/llamacpp-live/check-receipt.py"
    grid = [PY, "tests/llamacpp-live/install-tree-grid.py", "--gate", gate,
            "--receipt", "{R}/.ufo/waves/round-18/live-recovery/receipt-1.json",
            "--model-sha", MODEL_SHA, "--server-sha", SERVER_SHA,
            "--impl-sha", IMPL_SHA, "--probe-sha", PROBE_SHA,
            "--tool-sha", TOOL_SHA, "--json"]

    # --- SKILL.md round-20 instrument registry (650-659) and recorded recipe
    add("citation-selftest", GROUP_R20,
        [PY, "tools/citation-provenance.py", "--selftest"], r20=0)
    add("citation-json", GROUP_R20,
        [PY, "tools/citation-provenance.py", "--json"], r20=0,
        note="official gate run (no --docs)")
    add("install-tree-grid-selftest", GROUP_R20,
        [PY, "tests/llamacpp-live/install-tree-grid.py", "--selftest"], r20=0)
    add("install-tree-grid-no-tree-pin", GROUP_R20, grid, r20=1,
        note="round-20 recorded exit 1 (no tree pin)")
    add("install-tree-grid-tree-pin", GROUP_R20, grid + ["--tree-sha", TREE_SHA],
        r20=0)
    add("check-receipt-selftest", GROUP_R20,
        [PY, "tests/llamacpp-live/check-receipt.py", "--selftest"], r20=0,
        note="changed in a29bb84 (install_links); count printed on stdout")
    add("check-receipt-6pin-live-recovery-1", GROUP_R20,
        [PY, "tests/llamacpp-live/check-receipt.py",
         "{R}/.ufo/waves/round-18/live-recovery/receipt-1.json",
         "--require-schema", "v3", "--expect-model-sha256", MODEL_SHA,
         "--expect-server-sha256", SERVER_SHA,
         "--expect-server-impl-sha256", IMPL_SHA,
         "--expect-install-tree-sha256", TREE_SHA,
         "--expect-probe-sha256", PROBE_SHA,
         "--expect-tool-sha256", TOOL_SHA],
        note="six-pin v3 gate on a committed receipt")
    add("error-census-selftest", GROUP_R20,
        [PY, "tools/error-verdict-census.py", "--selftest"], r20=0)
    add("error-census-frozen-json", GROUP_R20,
        [PY, "tools/error-verdict-census.py", "--arm", "frozen", "--json"],
        r20=1, note="frozen arm is expected to exit 1")
    add("error-census-current-json", GROUP_R20,
        [PY, "tools/error-verdict-census.py", "--arm", "current", "--json"],
        r20=0)
    add("error-census-pair-json", GROUP_R20,
        [PY, "tools/error-verdict-census.py", "--json"], r20=0)
    add("survivor-arm-selftest", GROUP_RECIPE,
        [PY, ".ufo/waves/round-20/c1/arm-selftest.py"], r20=0)
    add("survivors-selftest", GROUP_R20,
        [PY, ".ufo/waves/round-18/c2/survivors.py", "--selftest"], timeout=3600)
    add("survivors-full-json", GROUP_R20,
        [PY, ".ufo/waves/round-18/c2/survivors.py", "--json"], timeout=3600,
        note="SKILL row says expensive; not run at round 20")
    add("gguf-selftest", GROUP_R20,
        [PY, "tools/gguf-identity.py", "--selftest"], r20=0)
    add("gguf-file-json", GROUP_R20,
        [PY, "tools/gguf-identity.py", MODEL, "--json"], r20=0,
        note="reads host model file read-only; no tensors, no server")
    add("gguf-receipt-json", GROUP_R20,
        [PY, "tools/gguf-identity.py", MODEL, "--receipt",
         "{R}/.ufo/waves/round-18/live-recovery/receipt-1.json", "--json"],
        r20=0)
    add("gguf-measure-selftest-json", GROUP_R20,
        [PY, ".ufo/waves/round-20/c2/measure.py", "--selftest", "--json"], r20=2,
        note="round-20 recorded exit 2 with as_expected=false")
    add("gguf-measure-json", GROUP_R20,
        [PY, ".ufo/waves/round-20/c2/measure.py", "--json"], r20=2,
        note="round-20 recorded exit 2 with as_expected=false")
    add("sources-append-selftest", GROUP_R20,
        [PY, "tools/sources-append-only.py", "--selftest"], r20=0)
    add("sources-append-round20", GROUP_R20,
        [PY, "tools/sources-append-only.py", "--from",
         "37bd4c5bd456a2f8a54d3312c28495c321715856", "--to",
         "c7311039bcbd76c38b0648d33197864331f34364", "--repo", "{R}", "--json"],
        r20=0, note="--repo pinned to clone (script default is the lane)")
    add("sources-append-negative", GROUP_R20,
        [PY, "tools/sources-append-only.py", "--from", "b8e485c", "--to",
         "ccc4bb3", "--repo", "{R}", "--json"], r20=1,
        note="must flag S041; --repo pinned to clone")
    add("sources-validate-lane", GROUP_RECIPE,
        [FLEET_CENSUS, "validate", "--root", FLEET_ROOT, "kama"], r20=0,
        note="lane-bound: reads lane corpus, not the clone; same for both labels")
    add("sources-census-lane", GROUP_RECIPE,
        [FLEET_CENSUS, "census", "--root", FLEET_ROOT, "kama"], r20=0,
        note="lane-bound: reads lane corpus, not the clone; same for both labels")

    # --- SKILL.md round-18 table (607-614)
    add("llamacpp-live-selftest", GROUP_R18,
        [PY, "tools/kama-llamacpp-live.py", "--selftest"],
        note="ownership parser and outcome self-tests; no server launched")
    add("llamacpp-live-help", GROUP_R18,
        [PY, "tools/kama-llamacpp-live.py", "--help"],
        note="argparse usage only; no launch")
    add("sources-append-round21", GROUP_PAIR,
        [PY, "tools/sources-append-only.py", "--from", BASE_REV, "--to",
         WORK_REV, "--repo", "{R}", "--json"],
        note="round-21 pair base->work; identical argv both sides")
    add("dispatch-provenance-selftest", GROUP_R18,
        [PY, ".ufo/waves/round-18/dispatch-provenance.py", "--selftest"],
        note="tempdir fixtures only; runs no wave")
    add("probe-verdicts-selftest", GROUP_R18,
        [PY, "tests/probe-verdicts/check.py", "--selftest", "--probe",
         "{R}/tools/kama-probe.sh"])

    # --- SKILL.md other gate and selftest rows
    add("test-snapshot", GROUP_OTHER, ["bash", "tools/test-snapshot.sh"],
        note="hermetic fixture server on ephemeral port; killed by trap")
    add("probe-verdicts-matrix-json", GROUP_OTHER,
        [PY, "tests/probe-verdicts/check.py", "--probe",
         "{R}/tools/kama-probe.sh", "--json"],
        note="loopback stubs on ephemeral ports")
    add("fault-controls-selftest", GROUP_OTHER,
        [PY, "tests/probe-verdicts/fault-controls.py", "--selftest"],
        timeout=1800)
    add("fault-controls-json", GROUP_OTHER,
        [PY, "tests/probe-verdicts/fault-controls.py", "--json"], timeout=3600)
    add("mutants-selftest", GROUP_OTHER,
        [PY, ".ufo/waves/round-17/c1/mutants.py", "--selftest"], timeout=1800)
    add("mutants-dry-run", GROUP_OTHER,
        [PY, ".ufo/waves/round-17/c1/mutants.py", "--dry-run", "--check",
         "{R}/tests/probe-verdicts/check.py"], timeout=1800)
    add("mutants-grid-json", GROUP_OTHER,
        [PY, ".ufo/waves/round-17/c1/mutants.py", "--grid", "--out",
         "{S}/mutants-grid.json"], timeout=3600,
        note="--out is a scratch path outside the clone")
    add("llamacpp-controls-json", GROUP_OTHER,
        [PY, "tests/llamacpp-live/controls.py", "--tool",
         "{R}/tools/kama-llamacpp-live.py", "--gate", gate, "--json"],
        timeout=3600,
        note="--server is always a generated fake; real llama-server never used")
    add("ollama-corpus-guard", GROUP_OTHER,
        [PY, "tests/ollama-corpus-guard/check.py"])
    add("ollama-corpus-guard-selftest", GROUP_OTHER,
        [PY, "tests/ollama-corpus-guard/check.py", "--selftest"])
    add("ollama-evidence-selftest", GROUP_OTHER,
        [PY, "tools/kama-ollama-evidence.py", "--selftest"])
    add("round11-provenance", GROUP_OTHER,
        [PY, ".ufo/waves/round-11/measure.py", "provenance"],
        note="default root = script's own repository (clone)")
    add("round11-crosswalk", GROUP_OTHER,
        [PY, ".ufo/waves/round-11/measure.py", "crosswalk"])
    add("round11-selftest", GROUP_OTHER,
        [PY, ".ufo/waves/round-11/measure.py", "--selftest"])
    add("round12-selftest", GROUP_OTHER,
        [PY, ".ufo/waves/round-12/fidelity.py", "--selftest"])
    add("round12-fidelity-pinned", GROUP_OTHER,
        [PY, ".ufo/waves/round-12/fidelity.py", "--snapshot",
         ".ufo/waves/round-12/frozen/corpus/SOURCES.md", "--manifest",
         ".ufo/waves/round-12/frozen/expected.json", "--repo", "{R}"])
    add("round13-quality-live", GROUP_OTHER,
        [PY, ".ufo/waves/round-13/measure.py", "--quality", "corpus/QUALITY.md"],
        note="exit 4 expected when clone HEAD differs from measured revision")
    add("round16-measure", GROUP_OTHER,
        [PY, ".ufo/waves/round-16/measure.py"], timeout=1800,
        note="runs the probe gate twice; writes run-*.json inside the clone")
    # round-13 selftest last: it writes a sandboxed measure.py copy in a temp dir
    add("round13-selftest", GROUP_OTHER,
        [PY, ".ufo/waves/round-13/measure.py", "--selftest"])

    # --- committed receipts through the gate changed in a29bb84
    for rel, schema in RECEIPTS:
        slug = "rcpt-" + re.sub(r"[^a-z0-9]+", "-", rel.lower()).strip("-")
        add(slug + "-nopins", GROUP_RCPT,
            [PY, "tests/llamacpp-live/check-receipt.py", "{R}/" + rel],
            timeout=600, note=f"committed {schema} receipt, no pins")
        if schema == "v3":
            add(slug + "-v3floor", GROUP_RCPT,
                [PY, "tests/llamacpp-live/check-receipt.py", "{R}/" + rel,
                 "--require-schema", "v3"],
                timeout=600, note="committed v3 receipt with schema floor")

    # --- work-only additions (no base counterpart)
    add("report-landing-audit-selftest", GROUP_WORK,
        [PY, "tools/report-landing-audit.py", "--selftest"],
        present=WORK_ONLY, note="new in a29bb84; base absent")
    add("install-links-grid-selftest", GROUP_WORK,
        [PY, "tests/llamacpp-live/install-links-grid.py", "--selftest"],
        present=WORK_ONLY, note="new in a29bb84; base absent")
    return specs


def utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def subst(arg, root, scratch):
    return arg.replace("{R}", str(root)).replace("{S}", str(scratch))


def display(argv):
    out = []
    for arg in argv:
        out.append(arg.replace(PY, "python3").replace(MODEL, "$MODEL")
                   .replace("{R}", "$R").replace("{S}", "$S"))
    return " ".join(out)


def git_state(root):
    proc = subprocess.run(
        ["git", "-C", str(root), "status", "--porcelain=v1",
         "--untracked-files=all"],
        capture_output=True, text=True)
    digest = hashlib.sha256(proc.stdout.encode("utf-8")).hexdigest()[:16]
    return f"{digest}:{len(proc.stdout.splitlines())}"


def kill_group(pgid):
    try:
        os.killpg(pgid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass


def execute(argv, cwd, logdir, sid, timeout, env):
    out_p = logdir / f"{sid}.stdout"
    err_p = logdir / f"{sid}.stderr"
    timed_out = False
    t0 = time.monotonic()
    with out_p.open("wb") as fo, err_p.open("wb") as fe:
        try:
            proc = subprocess.Popen(argv, cwd=str(cwd), stdin=subprocess.DEVNULL,
                                    stdout=fo, stderr=fe, env=env,
                                    start_new_session=True)
        except OSError as exc:
            fe.write(f"spawn-error: {exc}\n".encode("utf-8"))
            return {"rc": None, "timed_out": False, "wall_s": 0.0,
                    "spawn_error": str(exc)}
        try:
            rc = proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            kill_group(proc.pid)
            rc = proc.wait()
    kill_group(proc.pid)  # reap stragglers left in the command's session
    return {"rc": rc, "timed_out": timed_out,
            "wall_s": round(time.monotonic() - t0, 2), "spawn_error": None}


def run_label(label, root, scratch, only):
    root = Path(root).resolve()
    logdir = scratch / "logs" / label
    sdir = scratch / "scratch" / label
    logdir.mkdir(parents=True, exist_ok=True)
    sdir.mkdir(parents=True, exist_ok=True)
    head = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    meta_p = scratch / f"meta-{label}.json"
    meta = {"label": label, "root": str(root), "head": head,
            "started_utc": utc(), "python": sys.version.split()[0]}
    meta_p.write_text(json.dumps(meta, indent=1) + "\n", encoding="utf-8")
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    jsonl = scratch / f"runs-{label}.jsonl"
    with jsonl.open("a", encoding="utf-8") as jf:
        for spec in build_specs():
            if label not in spec["present"]:
                continue
            if only and spec["id"] not in only:
                continue
            argv = [subst(a, root, sdir) for a in spec["argv"]]
            before = git_state(root)
            res = execute(argv, root, logdir, spec["id"], spec["timeout"], env)
            after = git_state(root)
            rec = {"id": spec["id"], "label": label,
                   "argv": display(spec["argv"]), **res,
                   "clone_state_before": before, "clone_state_after": after,
                   "clone_mutated": before != after}
            jf.write(json.dumps(rec, sort_keys=True) + "\n")
            jf.flush()
            print(f"[{label}] {spec['id']} rc={rec['rc']} "
                  f"wall={rec['wall_s']}s mutated={rec['clone_mutated']}",
                  flush=True)
    meta["ended_utc"] = utc()
    meta_p.write_text(json.dumps(meta, indent=1) + "\n", encoding="utf-8")


def load_runs(path):
    runs = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rec = json.loads(line)
                runs[rec["id"]] = rec
    return runs


def first_nonblank(text):
    for line in text.splitlines():
        if line.strip():
            return line.rstrip()[:200]
    return ""


def last_nonblank(text):
    for line in reversed(text.splitlines()):
        if line.strip():
            return line.rstrip()[:200]
    return ""


def json_scalars(data):
    out = {}
    for key, value in data.items():
        if value is None or isinstance(value, (bool, int, float, str)):
            out[key] = value
        else:
            blob = json.dumps(value, sort_keys=True).encode("utf-8")
            out[key] = "sha256:" + hashlib.sha256(blob).hexdigest()[:16]
    return out


def sha(blob):
    return hashlib.sha256(blob).hexdigest()


def normalize(text, root, scratch):
    text = text.replace(str(root), "$R").replace(str(scratch), "$S")
    text = TMP_RE.sub(r"\1-<rand>", text)
    return ISO_RE.sub("<ts>", text)


def view(scratch, label, sid, root):
    """Stdout identity for one run: raw digest plus normalized digest/lines."""
    raw = (scratch / "logs" / label / f"{sid}.stdout").read_bytes()
    text = normalize(raw.decode("utf-8", errors="replace"), root,
                     scratch / "scratch" / label)
    try:
        parsed = json.loads(text)
    except ValueError:
        parsed = None
    return {"raw_sha": sha(raw), "norm_sha": sha(text.encode("utf-8")),
            "text": text, "first": first_nonblank(text),
            "last": last_nonblank(text),
            "json_top": json_scalars(parsed) if isinstance(parsed, dict) else None}


def diff_hint(vb, vw):
    if vb["norm_sha"] == vw["norm_sha"]:
        return ""
    if vb["json_top"] is not None and vw["json_top"] is not None:
        keys = sorted(set(vb["json_top"]) | set(vw["json_top"]))
        changed = [k for k in keys if vb["json_top"].get(k) != vw["json_top"].get(k)]
        return "json keys differ: " + ",".join(changed[:10])
    lb, lw = vb["text"].splitlines(), vw["text"].splitlines()
    for i, (x, y) in enumerate(zip(lb, lw)):
        if x != y:
            return f"line {i + 1}: base={x[:90]!r} work={y[:90]!r}"
    return f"stdout lines base={len(lb)} work={len(lw)}"


def classify(spec, b, w, vb, vw):
    if b is None and w is None:
        return "NOT-RUN"
    if b is None:
        return "WORK-ONLY (base absent)"
    if w is None:
        return "NOT-RUN(work)"
    core = ("EXIT-CHANGE" if b["rc"] != w["rc"]
            else "STDOUT-CHANGE" if vb["norm_sha"] != vw["norm_sha"]
            else "SAME")
    extras = []
    if spec["r20"] is not None:
        if b["rc"] != spec["r20"]:
            extras.append(f"base!=r20({spec['r20']})")
        if w["rc"] != spec["r20"]:
            extras.append(f"work!=r20({spec['r20']})")
    for label, rec in (("base", b), ("work", w)):
        if rec["timed_out"]:
            extras.append(f"{label}-timeout")
        if rec.get("spawn_error"):
            extras.append(f"{label}-spawn-error")
        if rec["clone_mutated"]:
            extras.append(f"{label}-clone-mutated")
    return "; ".join([core] + extras)


def cell(text):
    return re.sub(r"[\t\r\n]+", " ", str(text))[:220]


def table(scratch, out_path):
    runs = {lab: load_runs(scratch / f"runs-{lab}.jsonl") for lab in BOTH}
    roots = {lab: json.loads((scratch / f"meta-{lab}.json").read_text())["root"]
             for lab in BOTH}
    header = ["command", "exit_base", "exit_work", "first_stdout_base",
              "first_stdout_work", "flag", "id", "group", "exit_r20",
              "last_stdout_base", "last_stdout_work", "stdout_identical_norm",
              "stdout_identical_raw", "diff_hint", "wall_s_base", "wall_s_work",
              "notes"]
    lines = ["\t".join(header)]
    for spec in build_specs():
        sid = spec["id"]
        b = runs["base"].get(sid)
        w = runs["work"].get(sid)
        vb = view(scratch, "base", sid, roots["base"]) if b else None
        vw = view(scratch, "work", sid, roots["work"]) if w else None
        if "base" not in spec["present"]:
            exit_base = "absent"
        else:
            exit_base = "-" if b is None else (
                "timeout" if b["timed_out"] else b["rc"])
        exit_work = "-" if w is None else (
            "timeout" if w["timed_out"] else w["rc"])
        both = b is not None and w is not None
        lines.append("\t".join(cell(x) for x in [
            display(spec["argv"]), exit_base, exit_work,
            "-" if vb is None else (vb["first"] or "(empty)"),
            "-" if vw is None else (vw["first"] or "(empty)"),
            classify(spec, b, w, vb, vw) if (b or w) else "NOT-RUN",
            sid, spec["group"],
            "-" if spec["r20"] is None else spec["r20"],
            "-" if vb is None else (vb["last"] or "(empty)"),
            "-" if vw is None else (vw["last"] or "(empty)"),
            "-" if not both else ("yes" if vb["norm_sha"] == vw["norm_sha"] else "no"),
            "-" if not both else ("yes" if vb["raw_sha"] == vw["raw_sha"] else "no"),
            "" if not both else diff_hint(vb, vw),
            "-" if b is None else b["wall_s"],
            "-" if w is None else w["wall_s"],
            spec["note"]]))
    Path(out_path).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out_path}: {len(lines) - 1} rows")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    run_p = sub.add_parser("run")
    run_p.add_argument("--label", choices=BOTH, required=True)
    run_p.add_argument("--root", required=True)
    run_p.add_argument("--scratch", required=True)
    run_p.add_argument("--only", default="")
    tab_p = sub.add_parser("table")
    tab_p.add_argument("--scratch", required=True)
    tab_p.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    if args.cmd == "run":
        only = {x for x in args.only.split(",") if x}
        run_label(args.label, args.root, Path(args.scratch), only)
    else:
        table(Path(args.scratch), args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
