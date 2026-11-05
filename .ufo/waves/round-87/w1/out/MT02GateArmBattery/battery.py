#!/usr/bin/env python3
"""battery.py - MT02 independent mutation battery for the C2 gate arm `round86-instruments`.

Usage:
    battery.py --gate <candidate pre-report-gate.py> --repo <clone> [--work <dir>]

The battery reads the candidate gate, copies the tools/ dir that sits next to it into
scratch under --work (default: a fresh directory from tempfile, which honors TMPDIR;
the battery never writes to /tmp itself), builds three faulty tools copies, then for each
of seven mutants applies ONE source transform to a copy of the candidate gate and calls

    evaluate(<repo>, 87, tip="master", tools_dir=<faulty tools copy>)

and reads the `round86-instruments` arm from the result.

Faulty tools scenarios (faults live only in the scratch tools copies, never in the gate):
    default : every instrument of the candidate's own module tuple has its --selftest
              replaced by a stub that exits 0 and prints `<PREFIX> pass=0 fail=1`
              (a correct arm must be not-ok here).
    g5      : the same stub on every instrument EXCEPT the first, which stays the
              candidate's real instrument (a correct arm must be not-ok here).
    g6      : no tools fault; instead the gate's own instrument-call function raises an
              exception for every round86 instrument argv (injected into the loaded gate
              module, so the pristine arm propagates it; a correct arm is not-ok/missing).

Verdict (per mutant):
    not applied (its source anchors are absent in the candidate)  -> escaped
    mutant arm missing or not ok on its scenario                  -> killed
    mutant arm ok while the pristine candidate arm is not ok on
      the SAME scenario (the mutant masks a fault the pristine arm sees) -> killed
    otherwise                                                     -> escaped

The second clause is needed because G2 (always-ok), G3 (weakened summary check),
G5 (first-instrument-only) and G6 (exception swallowed) all return ok on some fault that
the pristine arm fails; a literal "ok means escaped" rule could never kill them. With no
arm (master gate) every mutant is not applied and counts escaped.

Output (stdout, exactly): one `GATE_ARM_MUTANT <id> expect=killed got=<killed|escaped>`
line per mutant, then `GATE_ARM_MUTANTS mutants=7 killed=<k> escaped=<e>`. Exit code 0
always. Diagnostics go to stderr, prefixed `battery:`.
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import re
import shutil
import sys
import tempfile

ARM = "round86-instruments"
RENAMED = "round-86-instruments"
FROZEN_INSTRUMENTS = [
    ("round86-rendered-cells.py", "RENDERED_CELLS_SELFTEST"),
    ("round86-mutant-owners.py", "MUTANT_OWNERS_SELFTEST"),
    ("round86-pin-origin.py", "PIN_ORIGIN_SELFTEST"),
]
MUTANTS = ("G1", "G2", "G3", "G4", "G5", "G6", "G7")

FAILING_STUB = (
    "#!/usr/bin/env python3\n"
    "# MT02 battery fault: selftest exits 0 with a failing summary.\n"
    'print("{prefix} pass=0 fail=1")\n'
)

G2_BODY = (
    "def {fn}(tools_path, repo_path, depth=0):\n"
    "    return {{\"name\": \"{arm}\", \"argv\": [], \"exit\": 0, \"ok\": True,\n"
    "             \"detail\": \"G2 always-ok mutant\"}}\n"
    "\n"
    "\n"
)


def note(msg: str) -> None:
    print(f"battery: {msg}", file=sys.stderr)


def def_block(lines: list[str]) -> tuple[int, int, str] | None:
    """Span and name of the top-level function whose body names the arm."""
    for i, line in enumerate(lines):
        m = re.match(r"^def\s+(\w+)\s*\(", line)
        if not m:
            continue
        j = i + 1
        while j < len(lines) and (not lines[j].strip() or lines[j][:1] in (" ", "\t")):
            j += 1
        block = "\n".join(lines[i:j])
        if f'"{ARM}"' in block:
            return i, j, m.group(1)
    return None


def arm_order_span(lines: list[str]) -> tuple[int, int] | None:
    for i, line in enumerate(lines):
        if re.match(r"^ARM_ORDER\s*=", line):
            j = i
            while j < len(lines) and not lines[j].rstrip().endswith("]"):
                j += 1
            return i, j + 1
    return None


def append_line(lines: list[str], fn: str) -> int | None:
    pat = re.compile(rf"arms\.append\(\s*{re.escape(fn)}\s*\(")
    for i, line in enumerate(lines):
        if pat.search(line):
            return i
    return None


def derive_modules(src: str, fn_block: str | None) -> list[tuple[str, str]]:
    """The candidate's own (script, prefix) instrument tuple, else the frozen names."""
    pairs: list[tuple[str, str]] = []
    if fn_block:
        m = re.search(r"for\s+\w+,\s*\w+\s+in\s+([A-Za-z_][A-Za-z0-9_]*)\s*:", fn_block)
        if m:
            t = re.search(rf"^{m.group(1)}\s*=\s*\((.*?)^\)", src, re.S | re.M)
            if t:
                pairs = re.findall(r'\(\s*"([^"]+)"\s*,\s*"([^"]+)"\s*\)', t.group(1))
    if not pairs:
        note("module tuple not derived from candidate; falling back to frozen names")
        pairs = FROZEN_INSTRUMENTS
    return pairs


def sub_in_span(lines: list[str], span: tuple[int, int], pattern: str, repl: str) -> int:
    count = 0
    for i in range(*span):
        new, n = re.subn(pattern, repl, lines[i])
        if n:
            lines[i] = new
            count += n
    return count


def mutate(src_lines: list[str], mutant: str) -> tuple[list[str] | None, str]:
    """Apply one fault to the candidate source; (None, reason) when anchors are absent."""
    lines = list(src_lines)
    blk = def_block(lines)
    fn = blk[2] if blk else None
    if mutant == "G1":
        span = arm_order_span(lines)
        app = append_line(lines, fn) if fn else None
        if span is None or app is None:
            return None, "no ARM_ORDER span or arm append site"
        n = sub_in_span(lines, span, r',\s*"' + ARM + r'"', "")
        n += sub_in_span(lines, span, r'"' + ARM + r'"\s*,\s*', "")
        n += sub_in_span(lines, span, r'"' + ARM + r'"', "")
        if n == 0:
            return None, "arm name absent from ARM_ORDER"
        del lines[app]
        return lines, f"removed from ARM_ORDER ({n} token) and from evaluate()"
    if mutant == "G2":
        if blk is None:
            return None, "no round86 arm function"
        lines[blk[0]:blk[1]] = (G2_BODY.format(fn=fn, arm=ARM)).splitlines()
        return lines, f"function {fn} replaced by always-ok"
    if mutant == "G3":
        if blk is None:
            return None, "no round86 arm function"
        span = (blk[0], blk[1])
        n = sub_in_span(lines, span, r"pass=\[0-9\]\+ fail=0", "pass=[0-9]+ fail=[0-9]+")
        if n == 0:
            return None, "no `pass=[0-9]+ fail=0` summary check inside the arm"
        return lines, f"summary check weakened ({n} site): fail count no longer required 0"
    if mutant == "G4":
        if blk is None:
            return None, "no round86 arm function"
        span = (blk[0], blk[1])
        n = sub_in_span(lines, span, r"os\.path\.join\(tools_path, script_name\)",
                        'os.path.join(repo_path, "tools", script_name)')
        if n == 0:
            return None, "no tools_path script resolution inside the arm"
        return lines, f"arm resolves instruments from <repo>/tools ({n} site)"
    if mutant == "G5":
        if blk is None:
            return None, "no round86 arm function"
        span = (blk[0], blk[1])
        n = sub_in_span(lines, span, r"(for\s+\w+,\s*\w+\s+in\s+\w+)\s*:", r"\1[:1]:")
        if n == 0:
            return None, "no instrument loop inside the arm"
        return lines, f"arm runs only the first instrument ({n} loop)"
    if mutant == "G6":
        app = append_line(lines, fn) if fn else None
        if app is None:
            return None, "no arms.append site for the arm"
        indent = lines[app][: len(lines[app]) - len(lines[app].lstrip())]
        stmt = lines[app].strip()
        lines[app:app + 1] = [
            f"{indent}try:",
            f"{indent}    {stmt}",
            f"{indent}except Exception:",
            f'{indent}    arms.append({{"name": "{ARM}", "argv": [], "exit": 0, "ok": True,',
            f'{indent}                 "detail": "G6 exception swallowed"}})',
        ]
        return lines, "arm append wrapped in exception-swallowing try/except"
    if mutant == "G7":
        hits = 0
        for i, line in enumerate(lines):
            if f'"{ARM}"' in line:
                lines[i] = line.replace(f'"{ARM}"', f'"{RENAMED}"')
                hits += 1
        if hits == 0:
            return None, f'no quoted "{ARM}" literal in the gate'
        return lines, f"arm renamed {RENAMED} ({hits} lines)"
    raise AssertionError(mutant)


SCENARIO_OF = {"G1": "default", "G2": "default", "G3": "default", "G4": "default",
               "G5": "g5", "G6": "g6", "G7": "default"}


def build_tools(tools_src: str, dest: str, stubs: list[tuple[str, str]]) -> None:
    shutil.copytree(tools_src, dest, symlinks=True)
    for script, prefix in stubs:
        with open(os.path.join(dest, script), "w", encoding="utf-8") as fh:
            fh.write(FAILING_STUB.format(prefix=prefix))


def load_gate(path: str, tag: str):
    spec = importlib.util.spec_from_file_location(f"mt02_gate_{tag}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def inject_exception(mod) -> None:
    """Make every round86 instrument call raise inside the gate process (fault for G6)."""
    real_run = mod._run

    def boom(argv, cwd, depth=0):
        if any("round86-" in str(tok) for tok in argv):
            raise RuntimeError("MT02 injected exception in round86 instrument call")
        return real_run(argv, cwd, depth)

    mod._run = boom


def arm_state(mod, repo: str, tools_dir: str) -> tuple[str, str]:
    try:
        res = mod.evaluate(repo, 87, tip="master", tools_dir=tools_dir)
    except Exception as exc:  # the gate propagated the fault: no usable arm result
        return "missing", f"evaluate raised: {type(exc).__name__}: {exc}"
    arm = next((a for a in res.get("arms", []) if a.get("name") == ARM), None)
    if arm is None:
        return "missing", f"no {ARM} entry in result arms"
    return ("ok" if arm.get("ok") else "not-ok"), str(arm.get("detail", ""))[:200]


def verdict(mut_state: str, base_state: str) -> str:
    if mut_state in ("missing", "not-ok"):
        return "killed"
    if base_state != "ok":
        return "killed"  # mutant masks a fault that the pristine arm reports
    return "escaped"


def run_battery(gate: str, repo: str, work: str) -> list[tuple[str, str, str]]:
    tools_src = os.path.join(os.path.dirname(os.path.abspath(gate)), "tools")
    if not os.path.isdir(tools_src):
        note(f"tools dir not found next to gate: {tools_src}")
        return [(m, "escaped", "battery could not run") for m in MUTANTS]
    src = open(gate, encoding="utf-8").read()
    src_lines = src.splitlines()
    blk = def_block(src_lines)
    modules = derive_modules(src, "\n".join(src_lines[blk[0]:blk[1]]) if blk else None)
    note(f"instruments under test: {', '.join(s for s, _ in modules) or '(none)'}")

    dirs = {
        "default": os.path.join(work, "tools-default"),
        "g5": os.path.join(work, "tools-g5"),
        "g6": os.path.join(work, "tools-g6"),
    }
    build_tools(tools_src, dirs["default"], modules)
    build_tools(tools_src, dirs["g5"], modules[1:])
    build_tools(tools_src, dirs["g6"], [])

    base: dict[str, str] = {}
    for name in ("default", "g5", "g6"):
        mod = load_gate(gate, f"pristine-{name}")
        if name == "g6":
            inject_exception(mod)
        base[name], detail = arm_state(mod, repo, dirs[name])
        note(f"pristine arm on {name}: {base[name]} ({detail})")

    results: list[tuple[str, str, str]] = []
    for mutant in MUTANTS:
        new_lines, why = mutate(src_lines, mutant)
        if new_lines is None:
            note(f"{mutant} not applied: {why}")
            results.append((mutant, "escaped", f"not applied: {why}"))
            continue
        new_src = "\n".join(new_lines) + "\n"
        if new_src == src:
            note(f"{mutant} not applied: transform is a no-op")
            results.append((mutant, "escaped", "not applied: no-op transform"))
            continue
        path = os.path.join(work, f"gate-{mutant}.py")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(new_src)
        scenario = SCENARIO_OF[mutant]
        mod = load_gate(path, f"mut-{mutant}")
        if scenario == "g6":
            inject_exception(mod)
        m_state, m_detail = arm_state(mod, repo, dirs[scenario])
        got = verdict(m_state, base[scenario])
        note(f"{mutant} ({why}): arm {m_state} on {scenario} ({m_detail})")
        results.append((mutant, got, f"{why}; arm {m_state}"))
    return results


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="MT02 C2 gate-arm mutation battery")
    ap.add_argument("--gate", required=True, help="candidate pre-report-gate.py")
    ap.add_argument("--repo", required=True, help="clone evaluate() runs against")
    ap.add_argument("--work", default=None, help="scratch root (default: a tempfile dir)")
    args = ap.parse_args(argv)

    work = None
    try:
        if not os.path.isfile(args.gate):
            note(f"gate not found: {args.gate}")
            results = [(m, "escaped", "battery could not run") for m in MUTANTS]
        else:
            if args.work:
                os.makedirs(args.work, exist_ok=True)
            work = tempfile.mkdtemp(prefix="mt02-battery-", dir=args.work)
            results = run_battery(args.gate, args.repo, work)
    except Exception as exc:  # the battery itself must still print the verdict
        note(f"battery error: {type(exc).__name__}: {exc}")
        results = [(m, "escaped", "battery error") for m in MUTANTS]
    finally:
        if work:
            shutil.rmtree(work, ignore_errors=True)

    killed = 0
    for mutant, got, _why in results:
        killed += got == "killed"
        print(f"GATE_ARM_MUTANT {mutant} expect=killed got={got}")
    print(f"GATE_ARM_MUTANTS mutants={len(MUTANTS)} killed={killed} "
          f"escaped={len(MUTANTS) - killed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
