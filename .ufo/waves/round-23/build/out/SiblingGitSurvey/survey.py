#!/usr/bin/env python3
"""SiblingGitSurvey - read-only static survey of git invocations in a lane.

Scope: <root>/tools/*.py (direct children) and <root>/tests/**/*.py.
The scanner parses source with the ast module. It never imports, executes or
decodes scanned code, and it writes only beside itself.

Git invocation kinds recorded:
  direct        subprocess/os call whose argv starts with "git" (after harmless
                launcher prefixes such as "timeout 5" or "env");
  via helper    call to a thin local helper whose only subprocess call runs a
                git argv (argv/env/mode come from the helper body; the call site
                supplies the arguments and consumes the output; labels from the
                helper's return statements are merged in);
  argv literal  a git argv list literal executed by a visible local helper loop
                (for example a tuple of commands passed to child()).

Per record: path:line, expanded argv, git globals, -c overrides, subcommand,
-C target and its class, env handling, text/bytes mode, decode strictness,
capture/check flags, output use (hash / exec / parse / raw / rc-only), and
repo-local-state exposure labels. Output-use labels are heuristic (name-flow
within one function plus one level of local-helper inspection); the report
cross-checks them by hand.

Also listed: non-git subprocess calls, subprocess calls not proven non-git
(opaque argv or shell string), and bare "git" string constants.

Usage:
  python3 survey.py                  working tree of the lane (default root)
  python3 survey.py --rev <commit>   committed blobs at <commit>, read with
                                     git --no-replace-objects --no-lazy-fetch
                                     and a sanitized environment (read-only)
Writes survey-<label>.txt (also printed) and survey-<label>.json beside this file.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve()
DEFAULT_ROOT = SCRIPT.parents[6]  # out/SiblingGitSurvey -> out -> build -> round-23 -> waves -> .ufo -> lane
MODULE_ATTRS = {
    "subprocess": frozenset({"run", "Popen", "call", "check_call", "check_output",
                             "getoutput", "getstatusoutput"}),
    "os": frozenset({"system", "popen"}),
    "asyncio": frozenset({"create_subprocess_exec", "create_subprocess_shell"}),
}
PREFIX_CMDS = frozenset({"timeout", "env", "nice", "nohup", "stdbuf", "ionice", "sudo", "time", "exec"})
FUNC = (ast.FunctionDef, ast.AsyncFunctionDef)
CAPTURE_KW = ("capture_output", "stdout", "stderr", "stdin", "input")
LOSSY = frozenset({"replace", "surrogateescape", "backslashreplace", "ignore", "xmlcharrefreplace"})
PARSE_RE = re.compile(
    r"\.(?:split|rsplit|splitlines|strip|lstrip|rstrip|partition|decode|count|"
    r"startswith|endswith|find\w*|finditer|fullmatch|match|search|sub)\(|"
    r"json\.loads|\bre\.(?:fullmatch|match|search|findall|finditer|split|sub)\(|"
    r"\bint\(|\bparse_\w*\(")
HASH_RE = re.compile(r"sha256|hashlib|sha1|digest\(")
EXEC_RE = re.compile(r"\bexec\(|\bload_source\(|(?<![\w.])compile\(")
TEMP_RE = re.compile(r"selftest|fixture|run_citation|run_survivor|run_grid|stub")
EXPOSURE_KEYS = frozenset({
    "REPLACE-REFS", "LAZY-FETCH", "ENV-AMBIENT", "ENV-CALLER", "REPO-CFG-UNOVERRIDDEN",
    "REPO-CFG-PARTIAL", "LOG-ENCODING", "LOG-FOLLOW", "STRICT-DECODE", "LOSSY-DECODE",
    "HASH-PINNED", "EXECUTED", "FIXTURE-ONLY"})


# ----------------------------------------------------------------- ast helpers
def link(tree):
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            child._up = parent  # noqa: SLF001 - scanner-private parent pointer
    tree._up = None  # noqa: SLF001


def up(node):
    return getattr(node, "_up", None)


def ancestor(node, kinds):
    cur = up(node)
    while cur is not None and not isinstance(cur, kinds):
        cur = up(cur)
    return cur


def fn_of(node):
    return ancestor(node, FUNC)


def stmt_of(node):
    return ancestor(node, ast.stmt) or node


def fn_chain(node):
    names, cur = [], fn_of(node)
    while cur is not None:
        names.append(cur.name)
        cur = fn_of(cur)
    return names  # innermost first


def text_of(node, limit=110):
    text = " ".join(ast.unparse(node).split())
    return text if len(text) <= limit else text[: limit - 3] + "..."


def const_or_text(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return text_of(node)


def kwmap(call):
    return {k.arg: k.value for k in call.keywords if k.arg}


def route_text(base, prefix):
    return f"{base} [argv prefix: {' '.join(prefix)}]" if prefix else base


class Ctx:
    def __init__(self, rel, tree):
        self.rel, self.tree = rel, tree
        self.defs, self.imports = {}, {}
        for node in ast.walk(tree):
            if isinstance(node, FUNC):
                self.defs.setdefault(node.name, node)
            elif isinstance(node, ast.ImportFrom) and node.module in MODULE_ATTRS:
                for alias in node.names:
                    self.imports[alias.asname or alias.name] = f"{node.module}.{alias.name}"
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in MODULE_ATTRS:
                        self.imports[alias.asname or alias.name] = alias.name


def subprocess_kind(call, ctx):
    func = call.func
    if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
        mod = ctx.imports.get(func.value.id, func.value.id)
        if func.attr in MODULE_ATTRS.get(mod, ()):
            return f"{mod}.{func.attr}"
    if isinstance(func, ast.Name) and func.id in ctx.imports:
        mod, _, attr = ctx.imports[func.id].partition(".")
        if attr in MODULE_ATTRS.get(mod, ()):
            return f"{mod}.{attr}"
    return None


def argv_node_of(call, kind):
    if call.args:
        return call.args[0]
    kws = kwmap(call)
    return kws.get("args") or kws.get("cmd")


def bindings(name, anchor, ctx):
    """Values assigned to `name` in the nearest function, else module top level."""
    fn = fn_of(anchor)
    pools = []
    if fn is not None:
        pools.append(ast.walk(fn))
    pools.append(ctx.tree.body)
    for pool in pools:
        found = []
        for node in pool:
            if isinstance(node, ast.Assign) and any(
                    isinstance(t, ast.Name) and t.id == name for t in node.targets):
                found.append(node.value)
            elif (isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)
                  and node.target.id == name and node.value is not None):
                found.append(node.value)
        if found:
            return found
    return []


def is_param(name, anchor):
    fn = fn_of(anchor)
    if fn is None:
        return False
    a = fn.args
    names = {x.arg for x in [*a.posonlyargs, *a.args, *a.kwonlyargs]}
    if a.vararg:
        names.add(a.vararg.arg)
    if a.kwarg:
        names.add(a.kwarg.arg)
    return name in names


def param_default(fn, name):
    a = fn.args
    pos = [*a.posonlyargs, *a.args]
    defaults = [None] * (len(pos) - len(a.defaults)) + list(a.defaults)
    for arg, dflt in zip(pos, defaults):
        if arg.arg == name and dflt is not None:
            return dflt.value if isinstance(dflt, ast.Constant) else text_of(dflt)
    for arg, dflt in zip(a.kwonlyargs, a.kw_defaults):
        if arg.arg == name and dflt is not None:
            return dflt.value if isinstance(dflt, ast.Constant) else text_of(dflt)
    return None


def const_seq(node, anchor, ctx):
    if isinstance(node, ast.Name):
        vals = bindings(node.id, anchor, ctx)
        if (len(vals) == 1 and isinstance(vals[0], (ast.List, ast.Tuple))
                and all(isinstance(e, ast.Constant) and isinstance(e.value, str)
                        for e in vals[0].elts)):
            return [e.value for e in vals[0].elts]
    return None


def resolve_items(node, anchor, ctx):
    """(items, literal, holder): items are argv tokens; holder is the List/Tuple node."""
    if node is None:
        return [], False, None
    if isinstance(node, ast.Name):
        vals = bindings(node.id, anchor, ctx)
        if len(vals) == 1 and isinstance(vals[0], (ast.List, ast.Tuple)):
            holder = vals[0]
        else:
            return [f"<{node.id}>"], False, None
    elif isinstance(node, (ast.List, ast.Tuple)):
        holder = node
    elif isinstance(node, ast.Constant) and isinstance(node.value, str):
        return [node.value], True, None
    else:
        return [text_of(node)], False, None
    items = []
    for el in holder.elts:
        if isinstance(el, ast.Constant) and isinstance(el.value, str):
            items.append(el.value)
        elif isinstance(el, ast.Starred):
            seq = const_seq(el.value, anchor, ctx)
            items.extend(seq if seq is not None else ["*" + text_of(el.value)])
        else:
            items.append(text_of(el))
    return items, True, holder


def effective_head(items):
    """Index of the executable after harmless launcher prefixes (timeout 5, env -i ...)."""
    i = 0
    while i < len(items):
        tok = items[i]
        if (tok in PREFIX_CMDS or tok.startswith("-") or re.fullmatch(r"[0-9.]+[smhd]?", tok)
                or re.fullmatch(r"[A-Za-z_]\w*=.*", tok)):
            i += 1
            continue
        return tok, i
    return None, len(items)


def environ_use(attr):
    parent = up(attr)
    if isinstance(parent, ast.Subscript):
        return "specific"
    if isinstance(parent, ast.Attribute) and parent.attr == "get":
        return "specific"
    return "full"


def mutations(name, anchor, ctx):
    fn = fn_of(anchor)
    pool = ast.walk(fn) if fn is not None else ast.walk(ctx.tree)
    found = []
    for node in pool:
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == "update" and isinstance(node.func.value, ast.Name)
                and node.func.value.id == name):
            found.append(node)
        elif isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Subscript) and isinstance(t.value, ast.Name)
                and t.value.id == name for t in node.targets):
            found.append(node)
    return found


def env_profile(env_node, anchor, ctx):
    if env_node is None or (isinstance(env_node, ast.Constant) and env_node.value is None):
        return {"desc": "FULL ambient os.environ inherited (no env=)", "ambient": True,
                "filtered": False, "keys": [], "caller": False}
    stack, seen, nodes, caller = [(env_node, 0)], set(), [], False
    while stack:
        node, depth = stack.pop()
        if depth > 3 or id(node) in seen:
            continue
        seen.add(id(node))
        if isinstance(node, ast.Name):
            caller = caller or is_param(node.id, anchor)
            stack.extend((v, depth + 1) for v in bindings(node.id, anchor, ctx))
            nodes.extend(mutations(node.id, anchor, ctx))
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in ctx.defs:
            nodes.append(ctx.defs[node.func.id])
        else:
            nodes.append(node)
            stack.extend((c, depth + 1) for c in ast.iter_child_nodes(node))
    keys, ambient, filtered, specific = set(), False, False, False
    for n in nodes:
        for sub in ast.walk(n):
            if isinstance(sub, ast.Dict):
                keys.update(k.value for k in sub.keys
                            if isinstance(k, ast.Constant) and isinstance(k.value, str))
            elif isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute):
                if sub.func.attr == "update":
                    keys.update(k.arg for k in sub.keywords if k.arg)
                if (sub.func.attr == "startswith" and sub.args
                        and isinstance(sub.args[0], ast.Constant) and sub.args[0].value == "GIT_"):
                    filtered = True
            elif isinstance(sub, ast.Assign):
                for t in sub.targets:
                    if isinstance(t, ast.Subscript) and isinstance(t.slice, ast.Constant) \
                            and isinstance(t.slice.value, str):
                        keys.add(t.slice.value)
            elif (isinstance(sub, ast.Attribute) and isinstance(sub.value, ast.Name)
                  and sub.value.id == "os" and sub.attr == "environ"):
                if environ_use(sub) == "full":
                    ambient = True
                else:
                    specific = True
    if ambient and not filtered:
        base = "FULL os.environ inherited (GIT_* not filtered)"
    elif ambient:
        base = "os.environ minus GIT_* (non-GIT ambient vars inherited)"
    elif specific:
        base = "explicit env (os.environ read per key)"
    else:
        base = "explicit env (no os.environ)"
    if caller:
        base = "caller-supplied env param; " + base
    if keys:
        base += "; keys=" + ",".join(sorted(keys))
    return {"desc": base, "ambient": ambient and not filtered, "filtered": ambient and filtered,
            "keys": sorted(keys), "caller": caller}


def io_mode(kws, kind):
    text, why = False, []
    for key in ("text", "universal_newlines"):
        if key in kws and not (isinstance(kws[key], ast.Constant) and kws[key].value is False):
            text = True
            why.append(f"{key}={text_of(kws[key])}")
    for key in ("encoding", "errors"):
        if key in kws:
            text = True
            why.append(f"{key}={text_of(kws[key])}")
    if kind == "os.popen":
        text = True
        why.append("os.popen is text")
    if kind in ("subprocess.getoutput", "subprocess.getstatusoutput"):
        text = True
        why.append("getoutput is text")
    return ("text" if text else "bytes"), why


def decode_info(fn, call_kws):
    """Describe how the stdout of a call inside fn is decoded; returns (text, strict-or-None)."""
    if fn is None:
        return "n/a", None
    decodes, passed = [], []
    for sub in ast.walk(fn):
        if not isinstance(sub, ast.Call):
            continue
        if isinstance(sub.func, ast.Attribute) and sub.func.attr == "decode":
            recv = text_of(sub.func.value)
            if "stderr" in recv or recv == "err" or recv.endswith(".err"):
                continue
            decodes.append(sub)
        elif (not HASH_RE.search(text_of(sub.func)) and any("stdout" in text_of(a) for a in sub.args)):
            passed.append(sub)
    if not decodes:
        if passed:
            return f"stdout passed raw to {text_of(passed[0])}", None
        return "none (stdout bytes returned raw)", None
    best = next((d for d in decodes if "stdout" in text_of(d.func.value)), decodes[0])
    err = best.args[1] if len(best.args) > 1 else None
    for k in best.keywords:
        if k.arg == "errors":
            err = k.value
    if err is None:
        value = "strict"
    elif isinstance(err, ast.Constant):
        value = err.value
    elif isinstance(err, ast.Name):
        supplied = (call_kws or {}).get(err.id)
        if isinstance(supplied, ast.Constant):
            value = supplied.value
        else:
            dflt = param_default(fn, err.id)
            value = dflt if dflt is not None else f"<{err.id}>"
    else:
        value = text_of(err)
    return f"{text_of(best)} errors={value}", value == "strict"


def header_nodes(st):
    if isinstance(st, (ast.If, ast.While)):
        return [st.test]
    if isinstance(st, ast.For):
        return [st.iter]
    if isinstance(st, ast.With):
        return [i.context_expr for i in st.items]
    return [st]


def local_call_matches(nodes, ctx, regex):
    for root_node in nodes:
        for sub in ast.walk(root_node):
            if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name) and sub.func.id in ctx.defs:
                if regex.search(ast.unparse(ctx.defs[sub.func.id])):
                    return True
    return False


def label_for(st, ctx):
    nodes = header_nodes(st)
    header = " ; ".join(text_of(n, 400) for n in nodes)
    labels = set()
    if HASH_RE.search(header):
        labels.add("hash")
    if EXEC_RE.search(header) or local_call_matches(nodes, ctx, EXEC_RE):
        labels.add("exec")
    if PARSE_RE.search(header) or local_call_matches(nodes, ctx, PARSE_RE):
        labels.add("parse")
    return labels


def bound_uses(var, assign, ctx):
    fn = fn_of(assign)
    pool = ast.walk(fn) if fn is not None else ast.walk(ctx.tree)
    uses = []
    for node in pool:
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == var:
            role = {"stdout": "out", "stderr": "err", "returncode": "rc"}.get(node.attr, "name")
            target = node
        elif isinstance(node, ast.Name) and node.id == var and isinstance(node.ctx, ast.Load):
            parent = up(node)
            if isinstance(parent, ast.Attribute) and parent.value is node:
                continue
            role, target = "name", node
        else:
            continue
        st = stmt_of(target)
        if st is not assign:
            uses.append((st, role))
    return uses


def assign_names(assign):
    names = []
    for t in assign.targets:
        if isinstance(t, ast.Name):
            names.append(t.id)
        elif isinstance(t, ast.Tuple):
            names.extend(e.id for e in t.elts if isinstance(e, ast.Name))
    return names


def bind_many(names, assign, ctx, prefix):
    uses = []
    for name in names:
        uses.extend(bound_uses(name, assign, ctx))
    return f"{prefix}{','.join(names)}", uses


def value_top(node):
    cur = node
    while isinstance(up(cur), (ast.IfExp, ast.BoolOp)):
        cur = up(cur)
    return cur, up(cur)


def output_use(call, ctx):
    top, parent = value_top(call)
    if isinstance(parent, ast.Attribute) and parent.value is top and parent.attr in ("stdout", "stderr"):
        role = "out" if parent.attr == "stdout" else "err"
        _top2, parent2 = value_top(parent)
        if isinstance(parent2, ast.Assign) and assign_names(parent2):
            return bind_many(assign_names(parent2), parent2, ctx, f"chained .{parent.attr} -> bound to ")
        if isinstance(parent2, ast.Return):
            return f"chained .{parent.attr} returned", [(parent2, "returned")]
        return f"chained .{parent.attr}", [(stmt_of(parent), role)]
    if isinstance(parent, ast.Expr):
        return "discarded", []
    if isinstance(parent, ast.Return):
        return "returned", [(parent, "returned")]
    if isinstance(parent, ast.Assign) and assign_names(parent):
        return bind_many(assign_names(parent), parent, ctx, "bound to ")
    return "inline", [(stmt_of(call), "name")]


def uses_labels(uses, ctx):
    """(labels, status): status is value | rc-only | stderr-only | discarded."""
    if not uses:
        return set(), "discarded"
    labels, values = set(), 0
    for st, role in uses:
        if role in ("rc", "err"):
            continue
        values += 1
        labels |= label_for(st, ctx)
    if values == 0:
        return set(), ("stderr-only" if any(r == "err" for _, r in uses) else "rc-only")
    return labels, "value"


def helper_return_labels(fn, ctx):
    """Labels from a helper's own non-error return statements (its output is what callers receive)."""
    labels = set()
    if fn is None:
        return labels
    for node in ast.walk(fn):
        if isinstance(node, ast.Return) and node.value is not None and fn_of(node) is fn:
            text = text_of(node.value, 400)
            if re.search(r"\berr\b|\berr\.|stderr", text):
                continue
            if HASH_RE.search(text):
                labels.add("hash")
            if EXEC_RE.search(text) or local_call_matches([node.value], ctx, EXEC_RE):
                labels.add("exec")
            if PARSE_RE.search(text) or local_call_matches([node.value], ctx, PARSE_RE):
                labels.add("parse")
    return labels


def output_label(labels, status):
    if labels:
        return "+".join(sorted(labels))
    return "raw" if status == "value" else status


def git_facets(items):
    globals_, cfg, target, subcmd, i = [], [], None, None, 1
    while i < len(items):
        tok = items[i]
        if tok == "-C":
            target = items[i + 1] if i + 1 < len(items) else "?"
            i += 2
        elif tok == "-c":
            cfg.append(items[i + 1] if i + 1 < len(items) else "?")
            i += 2
        elif tok.startswith("-"):
            globals_.append(tok)
            i += 1
        else:
            subcmd = tok
            break
    return {"globals": globals_, "cfg": cfg, "target": target, "subcmd": subcmd or "?"}


def bind_call(call, fn):
    params = [x.arg for x in [*fn.args.posonlyargs, *fn.args.args]]
    binding = {name: arg for name, arg in zip(params, call.args)}
    return binding, call.args[len(params):]


def expand_items(items, fn, extra):
    vararg = fn.args.vararg.arg if fn.args.vararg else None
    out = []
    for tok in items:
        if vararg and tok == "*" + vararg:
            out.extend(const_or_text(e) for e in extra)
        else:
            out.append(tok)
    return out


def resolve_target(text, template_fn, binding):
    name = re.sub(r"^str\((.*)\)$", r"\1", text or "").strip()
    if binding and name in binding:
        name = text_of(binding[name])
    elif template_fn is not None and re.fullmatch(r"[A-Za-z_]\w*", name):
        dflt = param_default(template_fn, name)
        if dflt is not None:
            name = str(dflt)
    return name


def target_class(resolved, anchor):
    if "LANE" in resolved or "__file__" in resolved:
        return "fixed-self"
    if any(TEMP_RE.search(n) for n in fn_chain(anchor)):
        return "temp-fixture"
    return "caller-supplied"


def exposure_labels(rec):
    out = []
    if not rec["replace_off"]:
        out.append("REPLACE-REFS")
    if not rec["lazy_off"]:
        out.append("LAZY-FETCH")
    if rec["ambient"]:
        out.append("ENV-AMBIENT")
    if rec["env_caller"]:
        out.append("ENV-CALLER")
    out.append("REPO-CFG-PARTIAL" if rec["cfg_keys"] else "REPO-CFG-UNOVERRIDDEN")
    if rec["subcmd"] == "log":
        if "i18n.logOutputEncoding" not in rec["cfg_keys"]:
            out.append("LOG-ENCODING")
        if "log.follow" not in rec["cfg_keys"]:
            out.append("LOG-FOLLOW")
    if rec["strict"] is True:
        out.append("STRICT-DECODE")
    if rec["strict"] is False:
        out.append("LOSSY-DECODE")
    if "hash" in rec["output"]:
        out.append("HASH-PINNED")
    if "exec" in rec["output"]:
        out.append("EXECUTED")
    if rec["target_class"] == "temp-fixture":
        out.append("FIXTURE-ONLY")
    return out


def make_record(ctx, *, route, line, anchor, items, inner, env_node, env_anchor, use_call,
                call_kws, binding, template_fn, decode_fn, cwd_text, extra_labels=frozenset()):
    facets = git_facets(items)
    rec = {"route": route, "file": ctx.rel, "line": line,
           "func": " > ".join(reversed(fn_chain(anchor))) or "<module>",
           "argv": items, "subcmd": facets["subcmd"], "globals": facets["globals"],
           "cfg": facets["cfg"], "cfg_keys": [c.split("=", 1)[0] for c in facets["cfg"]]}
    if facets["target"] is not None:
        rec["target"] = f"-C {facets['target']}"
        probe = facets["target"]
    else:
        rec["target"] = f"cwd={cwd_text}" if cwd_text else "process cwd (no -C)"
        probe = cwd_text or ""
    resolved = resolve_target(probe, template_fn, binding)
    rec["target_resolved"] = resolved
    rec["target_class"] = target_class(resolved, anchor)
    if inner is not None:
        kws_in = kwmap(inner)
        kind = subprocess_kind(inner, ctx) or "?"
        mode, why = io_mode(kws_in, kind)
        if mode == "text":
            err = kws_in.get("errors")
            if err is None:
                dec, strict = "text-mode, strict decode", True
            elif isinstance(err, ast.Constant):
                dec, strict = f"text-mode errors={err.value}", err.value == "strict"
            else:
                dec, strict = f"text-mode errors={text_of(err)}", None
        else:
            dec, strict = decode_info(decode_fn, call_kws)
        env = env_profile(env_node, env_anchor, ctx)
        rec.update(kind=kind, mode=mode, mode_why=why,
                   capture=[f"{k}={text_of(v)}" for k, v in kws_in.items() if k in CAPTURE_KW],
                   check=text_of(kws_in["check"]) if "check" in kws_in else "absent",
                   decode=dec, strict=strict, env=env["desc"], env_keys=env["keys"],
                   ambient=env["ambient"], env_caller=env["caller"],
                   shell=text_of(kws_in["shell"]) if "shell" in kws_in else None)
    else:
        rec.update(kind="n/a", mode="n/a", mode_why=[], capture=[], check="n/a", decode="n/a",
                   strict=None, env="n/a (no visible subprocess)", env_keys=[], ambient=False,
                   env_caller=False, shell=None)
    rec["helper_labels"] = sorted(extra_labels)
    if use_call is not None:
        use_kind, uses = output_use(use_call, ctx)
        labels, status = uses_labels(uses, ctx)
        labels = set(labels) | set(extra_labels)
        if extra_labels and status != "value":
            status = "value"
        rec["use"] = use_kind
        rec["output"] = output_label(labels, status)
    else:
        rec["use"], rec["output"] = "n/a", "n/a (no visible consumer)"
    rec["replace_off"] = ("--no-replace-objects" in facets["globals"]
                          or "GIT_NO_REPLACE_OBJECTS" in rec["env_keys"])
    rec["lazy_off"] = ("--no-lazy-fetch" in facets["globals"]
                       or "GIT_NO_LAZY_FETCH" in rec["env_keys"])
    rec["exposure"] = exposure_labels(rec)
    return rec


def inner_subprocess(fn, ctx):
    for node in ast.walk(fn):
        if isinstance(node, ast.Call) and subprocess_kind(node, ctx) and fn_of(node) is fn:
            return node
    return None


def call_arg(call, fn, name):
    for k in call.keywords:
        if k.arg == name:
            return k.value
    if fn is not None:
        names = [x.arg for x in [*fn.args.posonlyargs, *fn.args.args]]
        if name in names and names.index(name) < len(call.args):
            return call.args[names.index(name)]
    return None


def literal_consumers(lit, ctx):
    """Calls to local helpers that receive the loop variable of a loop over the literal's container."""
    node = lit
    while isinstance(up(node), (ast.Tuple, ast.List)):
        node = up(node)
    holder = up(node)
    if not (isinstance(holder, ast.Assign) and len(holder.targets) == 1
            and isinstance(holder.targets[0], ast.Name)):
        return []
    name = holder.targets[0].id
    scope = fn_of(holder) or ctx.tree
    found = []
    for loop in ast.walk(scope):
        if not (isinstance(loop, ast.For) and isinstance(loop.iter, ast.Name)
                and loop.iter.id == name and isinstance(loop.target, ast.Name)):
            continue
        var = loop.target.id
        for c in ast.walk(loop):
            if not (isinstance(c, ast.Call) and isinstance(c.func, ast.Name) and c.func.id in ctx.defs):
                continue
            args = [*c.args, *[k.value for k in c.keywords]]
            if any(isinstance(n, ast.Name) and n.id == var for a in args for n in ast.walk(a)):
                found.append(c)
    return found


def analyze(rel, data):
    info = {"file": rel, "sha256": hashlib.sha256(data).hexdigest(),
            "lines": data.count(b"\n") + (0 if data.endswith(b"\n") or not data else 1),
            "error": None, "records": [], "opaque": [], "nongit": [], "bare": [],
            "subprocess_calls": 0, "helpers": []}
    try:
        tree = ast.parse(data, filename=rel)
    except SyntaxError as exc:
        info["error"] = f"SyntaxError line {exc.lineno}: {exc.msg}"
        return info
    link(tree)
    ctx = Ctx(rel, tree)
    subs = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            kind = subprocess_kind(node, ctx)
            if kind:
                subs.append((node, kind))
    info["subprocess_calls"] = len(subs)

    consumed, git_direct, other = set(), [], []
    for call, kind in subs:
        items, _literal, holder = resolve_items(argv_node_of(call, kind), call, ctx)
        if holder is not None:
            consumed.add(id(holder))
        head, idx = effective_head(items)
        if head == "git":
            git_direct.append((call, kind, items[idx:], items[:idx], idx))
        else:
            other.append((call, kind, items, holder))

    thin = {}
    for call, kind, items, prefix, idx in git_direct:
        fn = fn_of(call)
        if fn is not None and sum(1 for c, _k in subs if fn_of(c) is fn) == 1:
            thin.setdefault(fn.name, (fn, call, kind, idx))
    info["helpers"] = [f"{name}() def L{fn.lineno} (wraps {kind} at L{call.lineno})"
                       for name, (fn, call, kind, _i) in thin.items()]

    for call, kind, items, prefix, idx in git_direct:
        kws = kwmap(call)
        info["records"].append(make_record(
            ctx, route=route_text("direct subprocess", prefix), line=call.lineno, anchor=call,
            items=items, inner=call, env_node=kws.get("env"), env_anchor=call, use_call=call,
            call_kws=kws, binding=None, template_fn=fn_of(call), decode_fn=fn_of(call),
            cwd_text=text_of(kws["cwd"]) if "cwd" in kws else None))

    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in thin:
            fn, inner, ikind, idx = thin[node.func.id]
            binding, extra = bind_call(node, fn)
            full, _l, _h = resolve_items(argv_node_of(inner, ikind), inner, ctx)
            ikws = kwmap(inner)
            info["records"].append(make_record(
                ctx, route=route_text(f"via helper {fn.name}() def L{fn.lineno}", full[:idx]),
                line=node.lineno, anchor=node, items=expand_items(full[idx:], fn, extra),
                inner=inner, env_node=ikws.get("env"), env_anchor=inner, use_call=node,
                call_kws=kwmap(node), binding=binding, template_fn=fn, decode_fn=fn,
                cwd_text=text_of(ikws["cwd"]) if "cwd" in ikws else None,
                extra_labels=frozenset(helper_return_labels(fn, ctx))))

    for node in ast.walk(tree):
        if not (isinstance(node, (ast.List, ast.Tuple)) and node.elts
                and isinstance(node.elts[0], ast.Constant) and node.elts[0].value == "git"
                and id(node) not in consumed):
            continue
        items, _l, _h = resolve_items(node, node, ctx)
        consumers = literal_consumers(node, ctx)
        if not consumers:
            info["records"].append(make_record(
                ctx, route="git argv literal (no visible consumer)", line=node.lineno, anchor=node,
                items=items, inner=None, env_node=None, env_anchor=node, use_call=None,
                call_kws=None, binding=None, template_fn=fn_of(node), decode_fn=None, cwd_text=None))
        for cc in consumers:
            efn = ctx.defs[cc.func.id]
            cwd_node = call_arg(cc, efn, "cwd")
            info["records"].append(make_record(
                ctx, route=f"git argv literal -> {cc.func.id}() call L{cc.lineno}", line=node.lineno,
                anchor=cc, items=items, inner=inner_subprocess(efn, ctx), env_node=call_arg(cc, efn, "env"),
                env_anchor=cc, use_call=cc, call_kws=kwmap(cc), binding=None, template_fn=fn_of(node),
                decode_fn=efn, cwd_text=text_of(cwd_node) if cwd_node is not None else None,
                extra_labels=frozenset(helper_return_labels(efn, ctx))))

    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and node.value == "git":
            parent = up(node)
            if isinstance(parent, (ast.List, ast.Tuple)) and parent.elts and parent.elts[0] is node:
                continue
            info["bare"].append({"line": node.lineno,
                                 "context": text_of(parent, 100) if parent is not None else ""})

    for call, kind, items, holder in other:
        ksh = kwmap(call).get("shell")
        shell = kind.startswith("os.") or (isinstance(ksh, ast.Constant) and ksh.value is True)
        if holder is not None and holder.elts:
            head = holder.elts[0]
            if isinstance(head, ast.Constant) and isinstance(head.value, str):
                exe = f"known:{head.value}"
            elif text_of(head) == "sys.executable":
                exe = "known:sys.executable"
            else:
                exe = f"OPAQUE-EXE:{text_of(head)}"
        elif kind.startswith("os."):
            exe = "SHELL-STRING"
        else:
            exe = f"OPAQUE-ARGV:{items[0] if items else '?'}"
        entry = {"file": rel, "line": call.lineno, "kind": kind, "argv": items, "exe": exe,
                 "shell": shell, "func": " > ".join(reversed(fn_chain(call))) or "<module>"}
        (info["nongit"] if exe.startswith("known:") and not shell else info["opaque"]).append(entry)
    return info


# --------------------------------------------------------------- file loading
def git_bytes(root, git_args):
    env = {"PATH": os.environ.get("PATH", os.defpath), "LC_ALL": "C.UTF-8",
           "HOME": str(SCRIPT.parent), "GIT_CONFIG_GLOBAL": os.devnull,
           "GIT_CONFIG_NOSYSTEM": "1", "GIT_NO_REPLACE_OBJECTS": "1",
           "GIT_NO_LAZY_FETCH": "1", "GIT_OPTIONAL_LOCKS": "0"}
    cmd = ["git", "--no-replace-objects", "--no-lazy-fetch", "-C", str(root), *git_args]
    proc = subprocess.run(cmd, capture_output=True, env=env, timeout=180, check=False)
    if proc.returncode != 0:
        raise SystemExit(f"git {' '.join(git_args)} failed rc={proc.returncode}: "
                         f"{proc.stderr.decode('utf-8', 'replace').strip()}")
    return proc.stdout


def load_files(root, rev):
    if rev:
        names = git_bytes(root, ["ls-tree", "-r", "--name-only", rev, "--", "tools", "tests"])
        picked = sorted(
            n for n in names.decode("utf-8").splitlines()
            if (n.startswith("tools/") and n.count("/") == 1 and n.endswith(".py"))
            or (n.startswith("tests/") and n.endswith(".py")))
        return [(n, git_bytes(root, ["cat-file", "blob", f"{rev}:{n}"])) for n in picked]
    paths = sorted((root / "tools").glob("*.py")) + sorted((root / "tests").rglob("*.py"))
    return [(str(p.relative_to(root)), p.read_bytes()) for p in paths]


# ------------------------------------------------------------------- rendering
def render(label, root, analyses):
    records = []
    for info in analyses:
        records.extend(info["records"])
    for number, rec in enumerate(records, 1):
        rec["id"] = f"G{number:02d}"
    kinds = {"direct": 0, "via": 0, "literal": 0}
    for rec in records:
        kinds["direct" if rec["route"].startswith("direct") else
              "via" if rec["route"].startswith("via") else "literal"] += 1
    out = []
    add = out.append
    add(f"# SiblingGitSurvey - {label} - root {root}")
    add(f"files scanned: {len(analyses)}; subprocess-family calls: "
        f"{sum(a['subprocess_calls'] for a in analyses)}; git records: {len(records)} "
        f"(direct {kinds['direct']}, via helper {kinds['via']}, argv literal {kinds['literal']})")
    errors = [f"{a['file']}: {a['error']}" for a in analyses if a["error"]]
    add(f"parse errors: {errors or 'none'}")
    add("")
    add("## scanned files (sha256 of the bytes scanned)")
    for a in analyses:
        n_git = sum(1 for r in records if r["file"] == a["file"])
        add(f"{a['sha256']}  {a['lines']:>5}L  {a['file']}  subprocess={a['subprocess_calls']}  git-records={n_git}")
    add("")
    add("## git invocations")
    for rec in records:
        add(f"[{rec['id']}] {rec['file']}:{rec['line']}  {rec['route']}")
        add(f"    in      : {rec['func']}")
        add(f"    argv    : {rec['argv']}")
        add(f"    git     : subcmd={rec['subcmd']} globals={rec['globals']} -c={rec['cfg']} "
            f"{rec['target']} [target: {rec['target_class']}; resolves to {rec['target_resolved']}]")
        add(f"    env     : {rec['env']}")
        mode_extra = f" ({', '.join(rec['mode_why'])})" if rec["mode_why"] else ""
        shell_extra = f"; shell={rec['shell']}" if rec["shell"] else ""
        add(f"    io      : {rec['mode']}{mode_extra}; capture={rec['capture']}; "
            f"check={rec['check']}; decode={rec['decode']}{shell_extra}")
        helper_extra = f"; helper-return labels={rec['helper_labels']}" if rec["helper_labels"] else ""
        add(f"    output  : {rec['output']} (use: {rec['use']}{helper_extra})")
        add(f"    exposure: {', '.join(rec['exposure'])}")
    add("")
    add("## non-git subprocess calls with a known executable (context)")
    for a in analyses:
        for e in a["nongit"]:
            add(f"- {e['file']}:{e['line']}  {e['kind']}  {e['exe']}  argv={e['argv']}  in {e['func']}")
    add("")
    add("## subprocess calls NOT proven non-git (opaque argv or shell string; check by hand)")
    for a in analyses:
        for e in a["opaque"]:
            add(f"- {e['file']}:{e['line']}  {e['kind']}  {e['exe']}  shell={e['shell']}  "
                f"argv={e['argv']}  in {e['func']}")
    add("")
    add("## bare 'git' string constants outside argv-first position")
    for a in analyses:
        for b in a["bare"]:
            add(f"- {a['file']}:{b['line']}  {b['context']}")
    add("")
    add("## thin git helpers (def + the single subprocess call they wrap)")
    for a in analyses:
        for h in a["helpers"]:
            add(f"- {a['file']}: {h}")
    add("")
    add("## repo-local-state exposure per file (union over its git records)")
    add("file | direct/via/literal | target classes | exposure labels")
    groups, per_file = {}, {}
    for a in analyses:
        mine = [r for r in records if r["file"] == a["file"]]
        if not mine:
            continue
        labels = set()
        for r in mine:
            labels.update(x for x in r["exposure"] if x in EXPOSURE_KEYS)
        classes = sorted({r["target_class"] for r in mine})
        counts = (sum(r["route"].startswith("direct") for r in mine),
                  sum(r["route"].startswith("via") for r in mine),
                  sum(r["route"].startswith("git argv") for r in mine))
        add(f"{a['file']} | {counts[0]}/{counts[1]}/{counts[2]} | {classes} | {sorted(labels)}")
        per_file[a["file"]] = sorted(labels)
        groups.setdefault(tuple(sorted(labels)), []).append(a["file"])
    add("")
    add("## shared repo-local-state exposure groups (identical label sets)")
    for key, files in sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        add(f"- {list(key)}")
        for f in files:
            add(f"    {f}")
    text = "\n".join(out) + "\n"
    payload = {"mode": label, "root": str(root),
               "files": [{k: a[k] for k in ("file", "sha256", "lines", "error", "subprocess_calls")}
                         for a in analyses],
               "git_records": records,
               "nongit": [e for a in analyses for e in a["nongit"]],
               "opaque": [e for a in analyses for e in a["opaque"]],
               "bare_git": [dict(file=a["file"], **b) for a in analyses for b in a["bare"]],
               "helpers": {a["file"]: a["helpers"] for a in analyses if a["helpers"]},
               "exposure_per_file": per_file,
               "shared_groups": [{"labels": list(k), "files": v} for k, v in groups.items()]}
    return text, payload


def main(argv=None):
    ap = argparse.ArgumentParser(description="Read-only static survey of git invocations.")
    ap.add_argument("--root", default=str(DEFAULT_ROOT), help="lane root (default: %(default)s)")
    ap.add_argument("--rev", default="", help="scan committed blobs at this commit instead of the working tree")
    args = ap.parse_args(argv)
    root = Path(args.root).resolve()
    if not ((root / "tools").is_dir() and (root / "tests").is_dir()):
        raise SystemExit(f"not a lane root (no tools/ and tests/): {root}")
    label = args.rev if args.rev else "worktree"
    analyses = [analyze(rel, data) for rel, data in load_files(root, args.rev)]
    text, payload = render(label, root, analyses)
    out_dir = SCRIPT.parent
    (out_dir / f"survey-{label}.txt").write_text(text, encoding="utf-8")
    (out_dir / f"survey-{label}.json").write_text(json.dumps(payload, indent=1), encoding="utf-8")
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
