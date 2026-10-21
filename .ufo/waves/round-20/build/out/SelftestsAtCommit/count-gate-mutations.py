#!/usr/bin/env python3
"""Statically count check-receipt.py --selftest cases per revision.

Usage: count-gate-mutations.py REPO REV [REV ...]

Read-only: takes the gate bytes from `git -C REPO show REV:PATH` and never
executes them. Walks the AST of `_selftest()` and resolves every case's
expected exit (`want`) from its literal tuple or from the nested helper
(mut/mut2/mut3) that appends it, expanding helper calls inside a `for` over a
literal tuple by the tuple length. The selftest prints want==1 cases as
"N mutations", want==0 as "VALID" and want==3 as "NOT-EVALUATED".

Also reports the textual counts a reader gets from grep, because "mut(" also
matches the `def mut(` line and does not match mut2(/mut3( calls.

Exit: 0 counted every revision; 1 a case's want could not be resolved;
      2 git or parse failure.
"""
import ast
import hashlib
import re
import subprocess
import sys

GATE = "tests/llamacpp-live/check-receipt.py"


def gate_bytes(repo, rev):
    full = subprocess.run(["git", "-C", repo, "rev-parse", "--verify",
                           f"{rev}^{{commit}}"], check=True,
                          capture_output=True, text=True).stdout.strip()
    blob = subprocess.run(["git", "-C", repo, "rev-parse", f"{full}:{GATE}"],
                          check=True, capture_output=True,
                          text=True).stdout.strip()
    data = subprocess.run(["git", "-C", repo, "show", f"{full}:{GATE}"],
                          check=True, capture_output=True).stdout
    return full, blob, data


def is_cases_call(call, attr):
    return (isinstance(call.func, ast.Attribute) and call.func.attr == attr
            and isinstance(call.func.value, ast.Name)
            and call.func.value.id == "cases")


def helper_wants(fn):
    """Nested helper name -> how its cases.append tuple sets `want`."""
    helpers = {}
    for node in fn.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        for sub in ast.walk(node):
            if not (isinstance(sub, ast.Call) and is_cases_call(sub, "append")
                    and sub.args and isinstance(sub.args[0], ast.Tuple)):
                continue
            last = sub.args[0].elts[-1]
            if isinstance(last, ast.Constant):
                helpers[node.name] = ("const", last.value)
            elif isinstance(last, ast.Name):
                params = [a.arg for a in node.args.args]
                defaults = node.args.defaults
                idx = params.index(last.id)
                offset = len(params) - len(defaults)
                default = (defaults[idx - offset].value
                           if idx >= offset
                           and isinstance(defaults[idx - offset], ast.Constant)
                           else None)
                helpers[node.name] = ("param", last.id, idx, default)
    return helpers


def tuple_want(tup):
    last = tup.elts[-1]
    return last.value if isinstance(last, ast.Constant) else None


def call_want(call, spec):
    if spec[0] == "const":
        return spec[1]
    _, pname, idx, default = spec
    for kw in call.keywords:
        if kw.arg == pname:
            return kw.value.value if isinstance(kw.value, ast.Constant) else None
    if len(call.args) > idx:
        arg = call.args[idx]
        return arg.value if isinstance(arg, ast.Constant) else None
    return default


def collect(stmts, mult, helpers, rows):
    for st in stmts:
        if isinstance(st, ast.FunctionDef):
            continue  # helper bodies are templates; counted at call sites
        if isinstance(st, ast.For):
            if isinstance(st.iter, (ast.Tuple, ast.List)):
                collect(st.body, mult * len(st.iter.elts), helpers, rows)
            else:
                # runner loops (enumerate(cases), failures) produce no case;
                # a case producer under a non-literal loop is unresolvable.
                inner = []
                collect(st.body, mult, helpers, inner)
                if inner:
                    rows.append(("<non-literal loop>", None, mult,
                                 st.lineno, "loop"))
            continue
        if isinstance(st, (ast.With, ast.If, ast.Try)):
            collect(st.body, mult, helpers, rows)
            continue
        if (isinstance(st, ast.Assign) and len(st.targets) == 1
                and isinstance(st.targets[0], ast.Name)
                and st.targets[0].id == "cases"
                and isinstance(st.value, ast.List)):
            for tup in st.value.elts:
                rows.append((ast.unparse(tup.elts[0]), tuple_want(tup), mult,
                             tup.lineno, "cases=[...]"))
            continue
        if not (isinstance(st, ast.Expr) and isinstance(st.value, ast.Call)):
            continue
        call = st.value
        if isinstance(call.func, ast.Name) and call.func.id in helpers:
            rows.append((ast.unparse(call.args[0]),
                         call_want(call, helpers[call.func.id]), mult,
                         call.lineno, call.func.id))
        elif is_cases_call(call, "append") and isinstance(call.args[0],
                                                          ast.Tuple):
            tup = call.args[0]
            rows.append((ast.unparse(tup.elts[0]), tuple_want(tup), mult,
                         call.lineno, "cases.append"))
        elif is_cases_call(call, "extend") and isinstance(call.args[0],
                                                          ast.List):
            for tup in call.args[0].elts:
                rows.append((ast.unparse(tup.elts[0]), tuple_want(tup), mult,
                             tup.lineno, "cases.extend"))


def count(data):
    text = data.decode("utf-8")
    tree = ast.parse(text)
    fn = next(n for n in tree.body
              if isinstance(n, ast.FunctionDef) and n.name == "_selftest")
    helpers = helper_wants(fn)
    rows = []
    collect(fn.body, 1, helpers, rows)
    lines = text.splitlines()
    grep = {
        "grep_c_'mut('": sum(1 for ln in lines if "mut(" in ln),
        "grep_c_'def mut('": sum(1 for ln in lines if "def mut(" in ln),
        "grep_c_'mut(\"'": sum(1 for ln in lines if 'mut("' in ln),
    }
    for name in sorted(helpers):
        grep[f"call_lines_{name}"] = sum(
            1 for ln in lines if re.match(rf"\s*{name}\(", ln))
    return helpers, rows, grep


def main(argv):
    if len(argv) < 3:
        print(__doc__.strip().splitlines()[2], file=sys.stderr)
        return 2
    repo, revs = argv[1], argv[2:]
    status = 0
    previous = None
    for rev in revs:
        try:
            full, blob, data = gate_bytes(repo, rev)
            helpers, rows, grep = count(data)
        except (subprocess.CalledProcessError, OSError, SyntaxError,
                StopIteration, UnicodeDecodeError) as exc:
            print(f"rev={rev} ERROR {type(exc).__name__}: {exc}")
            return 2
        totals = {}
        sites = {}
        for name, want, mult, _line, kind in rows:
            if want is None:
                status = 1
            totals[want] = totals.get(want, 0) + mult
            key = kind
            sites.setdefault(key, [0, 0])
            sites[key][0] += 1
            sites[key][1] += mult
        print(f"rev={rev} commit={full}")
        print(f"  gate_blob={blob} gate_sha256={hashlib.sha256(data).hexdigest()} "
              f"lines={data.count(b'\n')}")
        print("  textual: " + " ".join(f"{k}={v}" for k, v in grep.items()))
        print("  helpers: " + " ".join(
            f"{k}=want:{v[1] if v[0] == 'const' else f'param {v[1]} default {v[3]}'}"
            for k, v in sorted(helpers.items())))
        print("  case producers (statements/expanded): " + " ".join(
            f"{k}={v[0]}/{v[1]}" for k, v in sites.items()))
        print(f"  want0_VALID={totals.get(0, 0)} "
              f"want3_NOT_EVALUATED={totals.get(3, 0)} "
              f"want1_mutations={totals.get(1, 0)} "
              f"unresolved={totals.get(None, 0)} "
              f"(+1 unreadable-receipt case outside `cases`)")
        muts = {name for name, want, _m, _l, _k in rows if want == 1}
        if previous is not None:
            prev_rev, prev_muts = previous
            added = sorted(muts - prev_muts)
            removed = sorted(prev_muts - muts)
            print(f"  vs {prev_rev}: added={added} removed={removed}")
        previous = (rev, muts)
    return status


if __name__ == "__main__":
    sys.exit(main(sys.argv))
