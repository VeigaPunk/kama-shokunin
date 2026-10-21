#!/usr/bin/env python3
"""Static failure map of the kama closure check (tools/report-landing-audit.py).

Read-only AST scan. Prints, per function:
  * every call to git() with the `errors=` mode used (strict vs surrogateescape)
  * every `except` handler and the exception types it catches
  * every `raise` site: EvalError (exit 2 contract) vs re-raise of another type
  * every place where a lookup status other than "found" becomes a *verdict*
    (defect list) rather than an EvalError

No repository is opened, no subprocess is run, nothing is written.
"""
import ast
import sys
from pathlib import Path

TARGET = Path(sys.argv[1] if len(sys.argv) > 1 else
              "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/"
              "report-landing-audit.py")
src = TARGET.read_text(encoding="utf-8")
tree = ast.parse(src)


def line(node):
    return getattr(node, "lineno", 0)


funcs = {}
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        funcs[node.name] = node

print(f"# target: {TARGET}")
print(f"# lines: {len(src.splitlines())}")
print()

# ---------------------------------------------------------------- git() sites
print("## git() call sites (errors= mode, caller)")
for node in ast.walk(tree):
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id == "git"):
        mode = "strict (default)"
        for kw in node.keywords:
            if kw.arg == "errors":
                mode = ast.unparse(kw.value)
        caller = "?"
        for fname, fnode in funcs.items():
            if any(node is sub for sub in ast.walk(fnode)):
                caller = fname
                break
        print(f"  L{line(node):>4}  errors={mode:<22} in {caller}()")
print()

# ------------------------------------------------------------ except handlers
print("## except handlers")
for node in ast.walk(tree):
    if isinstance(node, ast.ExceptHandler):
        kind = ast.unparse(node.type) if node.type else "bare-except"
        body = ast.unparse(node.body[0])[:70] if node.body else ""
        print(f"  L{line(node):>4}  except {kind:<24} -> {body}")
print()

# ---------------------------------------------------------------- raise sites
print("## raise sites")
for node in ast.walk(tree):
    if isinstance(node, ast.Raise):
        exc = ast.unparse(node.exc) if node.exc else "<re-raise>"
        kind = "EVALERROR" if "EvalError" in exc else ("RE-RAISE"
                                                       if node.exc is None
                                                       else "OTHER")
        print(f"  L{line(node):>4}  [{kind}] {exc[:100]}")
print()

# ------------------------------------------- lookup statuses -> verdict sinks
print("## lookup() status consumers (verdict sinks)")
for node in ast.walk(tree):
    if isinstance(node, ast.Compare):
        src_txt = ast.unparse(node)
        if '"missing"' in src_txt or '"ambiguous"' in src_txt:
            caller = "?"
            for fname, fnode in funcs.items():
                if any(node is sub for sub in ast.walk(fnode)):
                    caller = fname
                    break
            print(f"  L{line(node):>4}  in {caller}(): {src_txt[:110]}")
print()

# ------------------------------------------------------- unguarded IO helpers
print("## filesystem reads without a git() timeout wrapper")
for node in ast.walk(tree):
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
        if node.func.attr in ("read_text", "read_bytes", "iterdir",
                              "readlink"):
            caller = "?"
            for fname, fnode in funcs.items():
                if any(node is sub for sub in ast.walk(fnode)):
                    caller = fname
                    break
            print(f"  L{line(node):>4}  {node.func.attr:<12} in {caller}()")
print()

# ------------------------------------------------------ exception inventory
print("## functions and the exception types they can raise")
BUILTIN_RAISERS = {
    "int": "ValueError", "float": "ValueError",
    "Path": "OSError", "open": "OSError",
}
for fname, fnode in sorted(funcs.items(), key=lambda kv: line(kv[1])):
    raised = set()
    for sub in ast.walk(fnode):
        if isinstance(sub, ast.Call):
            fn = ast.unparse(sub.func)
            if fn in BUILTIN_RAISERS:
                raised.add(BUILTIN_RAISERS[fn])
            if fn == "int":
                raised.add("ValueError")
        if isinstance(sub, ast.Raise) and sub.exc is not None:
            e = ast.unparse(sub.exc)
            if "EvalError" in e:
                raised.add("EvalError")
            elif e.startswith("except"):
                raised.add("<re-raise>")
        if isinstance(sub, ast.Attribute) and sub.attr == "read_bytes":
            raised.add("OSError")
    print(f"  {fname:<24} L{line(fnode):>4}  {sorted(raised) or ['-']}")
