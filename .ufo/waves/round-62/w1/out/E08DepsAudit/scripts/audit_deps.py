#!/usr/bin/env python3
"""AST audit: every attribute the completion tool reads from its dep module.

Reads two blobs (already extracted to a scratch tip tree, byte-identical to the
master blobs) and reports, per dependency, whether the dep defines it at module
scope and what kind of object it is.
"""
import ast
import json
import sys


def top_level_symbols(path):
    tree = ast.parse(open(path, 'rb').read(), filename=path)
    syms = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            syms[node.name] = 'function'
        elif isinstance(node, ast.ClassDef):
            syms[node.name] = 'class'
        elif isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    syms[t.id] = 'name'
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            syms[node.target.id] = 'name'
    return syms


def dep_attrs(path, alias):
    tree = ast.parse(open(path, 'rb').read(), filename=path)
    hits = {}
    dynamic = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) \
                and node.value.id == alias:
            hits.setdefault(node.attr, []).append(node.lineno)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                and node.func.id == 'getattr' and node.args \
                and isinstance(node.args[0], ast.Name) \
                and node.args[0].id == alias:
            dynamic.append(node.lineno)
        if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Attribute) \
                and isinstance(node.value.value, ast.Name) \
                and node.value.value.id == alias:
            dynamic.append(node.lineno)
    return hits, dynamic


def main():
    tool, dep = sys.argv[1], sys.argv[2]
    dep_syms = top_level_symbols(dep)
    attrs, dynamic = dep_attrs(tool, '_live')
    report = {'dep': dep, 'tool': tool, 'dynamic_reads': dynamic,
              'deps': {}, 'missing': [], 'kinds': {}}
    for name in sorted(attrs):
        kind = dep_syms.get(name)
        report['deps'][name] = {'lines': attrs[name], 'kind': kind,
                                'present': kind is not None}
        if kind is None:
            report['missing'].append(name)
        else:
            report['kinds'][kind] = report['kinds'].get(kind, 0) + 1
    report['count'] = len(attrs)
    report['all_present'] = not report['missing']
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
