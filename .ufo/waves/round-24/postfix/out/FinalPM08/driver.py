#!/usr/bin/env python3
"""FinalPM08 bounded checks (no grid, no pristine, no mutant execution).

C1 inventory: import the pinned runner's MUTANTS table and run --list.
C2 legacy guard: isolation-mutants.py --only <invalid id> once, under strace.
C3 current-arm canary: promisor-mutants.py --arm frozen with a private
   canary grid, exact PM01 id and exact PG01 case, once, under strace.
"""
import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

PIN = "92063cfc60e217fa7e2098c568578119b16a1b95"
S = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalPM08")
CLONE = S / "clone"
OUT = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/"
           "postfix/out/FinalPM08")
RUNNER = CLONE / "tests/report-audit/promisor-mutants.py"
LEGACY = CLONE / "tests/report-audit/isolation-mutants.py"
AUDIT = CLONE / "tools/report-landing-audit.py"
GRID = CLONE / "tests/report-audit/promisor-grid.py"
LEGACY_GRID = CLONE / "tests/report-audit/repo-state-grid.py"
EXPECT = CLONE / "tests/report-audit/promisor-grid-expectations.json"
CANARY = S / "canary-grid.py"


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def tmpdir(name):
    d = S / "tmp" / name
    d.mkdir(parents=True, exist_ok=False)
    return d


def run(name, argv, extra_env=None):
    t = tmpdir(name)
    trace = OUT / f"{name}.strace"
    env = dict(os.environ, TMPDIR=str(t))
    env.update(extra_env or {})
    full = ["strace", "-f", "-qq", "-e", "trace=execve,openat",
            "-o", str(trace), *argv]
    p = subprocess.run(full, capture_output=True, env=env, cwd=str(CLONE),
                       timeout=120)
    (OUT / f"{name}.stdout").write_bytes(p.stdout)
    (OUT / f"{name}.stderr").write_bytes(p.stderr)
    lines = trace.read_text(errors="replace").splitlines()
    execs = [l for l in lines if "execve(" in l and "= 0" in l]
    return {"argv": argv, "tmpdir": str(t), "exit": p.returncode,
            "stdout": p.stdout.decode(errors="replace"),
            "stderr": p.stderr.decode(errors="replace"),
            "strace": str(trace), "successful_execve": execs,
            "tmpdir_entries_after": sorted(os.listdir(t)),
            "_lines": lines}


def opened(lines, path):
    return [l for l in lines if "openat(" in l and str(path) in l
            and "ENOENT" not in l]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    head = subprocess.run(["git", "-C", str(CLONE), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "-C", str(CLONE), "status", "--porcelain"],
                           capture_output=True, text=True).stdout
    ident = {"pin": PIN, "clone_head": head, "clone_dirty": dirty,
             "python": sys.version.split()[0],
             "sha256": {str(p.relative_to(CLONE)): sha(p) for p in
                        (RUNNER, LEGACY, AUDIT, GRID, LEGACY_GRID, EXPECT)},
             "canary_sha256": sha(CANARY),
             "driver_sha256": sha(__file__)}

    # C1: inventory (import only; main() is not called)
    spec = importlib.util.spec_from_file_location("pm_runner", RUNNER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    pm08 = [m for m in mod.MUTANTS if m["id"].startswith("PM08")]
    executable = [m["id"] for m in mod.MUTANTS
                  if m["execution"] != "review-only"]
    review = [m["id"] for m in mod.MUTANTS if m["execution"] == "review-only"]
    # review aid only, not a persisted assertion: git subcommands the
    # pinned auditor passes to its single git() wrapper
    tree = ast.parse(AUDIT.read_text(encoding="utf-8"))
    subs, runs = set(), 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            f = node.func
            if isinstance(f, ast.Name) and f.id == "git" and len(node.args) > 1:
                a = node.args[1]
                subs.add(a.value if isinstance(a, ast.Constant) else
                         ast.unparse(a))
            if (isinstance(f, ast.Attribute) and f.attr in
                    ("run", "Popen", "check_output", "call", "check_call")
                    and isinstance(f.value, ast.Name)
                    and f.value.id == "subprocess"):
                runs += 1
    lst = run("c1-list", [sys.executable, str(RUNNER), "--list"])
    c1 = {"pm08_entry": pm08, "inventory_size": len(mod.MUTANTS),
          "executable_ids": executable, "review_only_ids": review,
          "pm08_keys": sorted(pm08[0]) if pm08 else None,
          "pm08_has_static_check_key": any(
              k in pm08[0] for k in ("static_check", "assert", "check",
                                     "anchor", "pattern")) if pm08 else None,
          "list_run": {k: v for k, v in lst.items() if k != "_lines"},
          "list_pm08_block": [b for b in lst["stdout"].split("\nPM")
                              if b.startswith(("PM08", "08-"))],
          "list_opened_grid": opened(lst["_lines"], GRID),
          "list_opened_auditor": opened(lst["_lines"], AUDIT),
          "auditor_subprocess_call_sites": runs,
          "auditor_git_wrapper_subcommands": sorted(subs)}

    # C2: legacy empty-selection guard, one invalid selector
    bad = "M08-invalid-selector"
    leg = run("c2-legacy-invalid-only",
              [sys.executable, str(LEGACY), "--only", bad, "--json"])
    c2 = {k: v for k, v in leg.items() if k != "_lines"}
    c2.update(selector=bad,
              selector_in_population=bad in [n for n, _, _ in
                                              _legacy_ids()],
              opened_auditor=opened(leg["_lines"], AUDIT),
              opened_legacy_grid=opened(leg["_lines"], LEGACY_GRID),
              exec_legacy_grid=[l for l in leg["successful_execve"]
                                if "repo-state-grid" in l])

    # C3: current-arm-only canary
    clog = S / "canary.log"
    if clog.exists():
        raise SystemExit("canary log pre-exists")
    can = run("c3-frozen-arm-canary",
              [sys.executable, str(RUNNER), "--grid", str(CANARY),
               "--arm", "frozen", "--current", str(AUDIT),
               "--only", "PM01-blanket-metadata-refusal",
               "--case", "PG01-complete-lane-promisor-config", "--json"],
              {"PM08_CANARY_LOG": str(clog)})
    c3 = {k: v for k, v in can.items() if k != "_lines"}
    c3.update(canary_log_exists=clog.exists(),
              exec_canary=[l for l in can["successful_execve"]
                           if "canary-grid" in l],
              exec_real_grid=[l for l in can["successful_execve"]
                              if "promisor-grid" in l],
              opened_auditor=opened(can["_lines"], AUDIT),
              names_current_only="current arm only" in can["stderr"])

    doc = {"identity": ident, "c1_inventory": c1, "c2_legacy_guard": c2,
           "c3_current_arm_canary": c3}
    (OUT / "results.json").write_text(json.dumps(doc, indent=1,
                                                 sort_keys=True) + "\n")
    print(json.dumps({"c1": {"pm08": pm08, "exec": len(executable),
                             "review": review,
                             "list_exit": lst["exit"],
                             "list_grid_opened": c1["list_opened_grid"],
                             "audit_runs": runs, "subs": sorted(subs)},
                      "c2": {"exit": c2["exit"], "stderr": c2["stderr"],
                             "stdout": c2["stdout"],
                             "opened_auditor": c2["opened_auditor"],
                             "grid_exec": c2["exec_legacy_grid"],
                             "execs": c2["successful_execve"]},
                      "c3": {"exit": c3["exit"], "stderr": c3["stderr"],
                             "stdout": c3["stdout"],
                             "canary_log": c3["canary_log_exists"],
                             "exec_canary": c3["exec_canary"],
                             "opened_auditor": c3["opened_auditor"],
                             "execs": c3["successful_execve"]},
                      "identity": ident}, indent=1))


def _legacy_ids():
    spec = importlib.util.spec_from_file_location("legacy", LEGACY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.MUTANTS


if __name__ == "__main__":
    main()
