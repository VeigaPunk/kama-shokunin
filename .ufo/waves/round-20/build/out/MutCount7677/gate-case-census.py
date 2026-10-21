#!/usr/bin/env python3
"""Statically count check-receipt.py selftest cases expected to exit 1.
Uses only git show + Python AST; does not import or execute the gate.
"""
import ast
import subprocess
import sys

PATH = "tests/llamacpp-live/check-receipt.py"
REVS = [
    "7229fa95eb122310e9e5334ad799ee3006293ebd",
    "5b108c1a7e943c571140df3a1d7e2e29bfdfb501",
    "f1790e25b421f02596798ad665488b066541ae3a",
    "028235e6f28d5b7f4106dd121956f10d2c762f48",
    "37bd4c5bd456a2f8a54d3312c28495c321715856",
]


def census(repo, rev):
    source = subprocess.run(["git", "-C", repo, "show", f"{rev}:{PATH}"],
                            check=True, capture_output=True, text=True).stdout
    tree = ast.parse(source)
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
              and n.name == "_selftest")
    helpers = {}
    counts = {"mut": 0, "mut2": 0, "mut3": 0, "literal": 0}

    def add_literal(node, weight):
        if not isinstance(node, ast.Tuple) or len(node.elts) != 4:
            raise ValueError(f"unhandled case tuple at line {node.lineno}")
        want = node.elts[3]
        if isinstance(want, ast.Constant) and want.value == 1:
            counts["literal"] += weight

    def visit(stmts, weight=1):
        for st in stmts:
            if isinstance(st, ast.FunctionDef):
                if st.name in ("mut", "mut2", "mut3"):
                    want = 1
                    for arg, default in zip(st.args.args[-len(st.args.defaults):],
                                            st.args.defaults):
                        if arg.arg == "want" and isinstance(default, ast.Constant):
                            want = default.value
                    helpers[st.name] = want
                continue
            if isinstance(st, ast.For):
                if not isinstance(st.iter, (ast.Tuple, ast.List)):
                    raise ValueError(f"non-literal for at line {st.lineno}")
                visit(st.body, weight * len(st.iter.elts))
                continue
            if isinstance(st, ast.Assign) and any(
                    isinstance(t, ast.Name) and t.id == "cases"
                    for t in st.targets):
                for item in st.value.elts:
                    add_literal(item, weight)
                continue
            if isinstance(st, ast.Expr) and isinstance(st.value, ast.Call):
                call = st.value
                if isinstance(call.func, ast.Name) and call.func.id in helpers:
                    name = call.func.id
                    want = helpers[name]
                    for kw in call.keywords:
                        if kw.arg == "want" and isinstance(kw.value, ast.Constant):
                            want = kw.value.value
                    if want == 1:
                        counts[name] += weight
                    continue
                if isinstance(call.func, ast.Attribute) \
                        and isinstance(call.func.value, ast.Name) \
                        and call.func.value.id == "cases":
                    if call.func.attr == "append":
                        add_literal(call.args[0], weight)
                    elif call.func.attr == "extend":
                        if not isinstance(call.args[0], ast.List):
                            raise ValueError(f"non-literal extend at line {st.lineno}")
                        for item in call.args[0].elts:
                            add_literal(item, weight)
                    continue
            # These branches contain no case-building calls in this source.
            if isinstance(st, (ast.If, ast.With, ast.Try, ast.While)):
                if any(isinstance(n, ast.Call) and
                       ((isinstance(n.func, ast.Name) and n.func.id in helpers) or
                        (isinstance(n.func, ast.Attribute) and
                         isinstance(n.func.value, ast.Name) and
                         n.func.value.id == "cases")) for n in ast.walk(st)):
                    raise ValueError(f"unhandled case site at line {st.lineno}")
    visit(fn.body)
    return counts, sum(counts.values())


def main():
    repo = sys.argv[1]
    for rev in REVS:
        counts, total = census(repo, rev)
        blob = subprocess.run(["git", "-C", repo, "rev-parse", f"{rev}:{PATH}"],
                              check=True, capture_output=True, text=True).stdout.strip()
        print(f"{rev[:8]} blob={blob} expected_exit_1={total} "
              f"helper_mut={counts['mut']} helper_mut2={counts['mut2']} "
              f"helper_mut3={counts['mut3']} literal_rejections={counts['literal']}")


if __name__ == "__main__":
    main()
