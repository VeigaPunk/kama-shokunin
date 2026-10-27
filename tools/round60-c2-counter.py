#!/usr/bin/env python3
"""Round-60 C2 counter: lane-documented Ollama INFERENCE claims checked against live captures.

Usage: python3 tools/round60-c2-counter.py --repo REPO --tip REV [--base REV]

Frozen predicate (same sentence as .ufo/waves/round-60/controls/freeze.txt):
  C2-r60: at the tip, every line of the frozen base population (at base ec3b0d583ed4eb05c7ae935dc59f560e86b0a80b:
  every line containing "inference" in corpus/knowledge/ollama-evidence-replay.md, plus every line of SKILL.md and
  the other corpus/knowledge/*.md containing both "inference" and one of ollama, api/tags, api/ps, expires_at,
  case-insensitive) is covered by a row of registry/ollama-live-claims-r60.tsv whose quote
  is located on that base line; at least 5 rows over at least 4 distinct lines carry a live predicate; every
  predicate is falsifiable (some mutation of a capture it reads flips its result), its recorded verdict equals
  its evaluation on the committed receipt's captures (true = confirmed, false = contradicted), every
  contradicted row is named with its observed text in corpus/knowledge/ollama-live-amendment-r60.md, the
  committed receipt's capture hashes are intact, and the 5 control families (tautology predicates, flipped
  verdicts, corrupted quotes, dropped lines, tampered capture) are all rejected, errors=0.

Registry columns (TAB, '#' comments ignored, header row `id`): id, path, line, quote, predicate, verdict, observed, reason.
A predicate is a restricted Python expression over `c`, the dict of parsed JSON capture bodies
(c['tags'], c['ps-after'], ...). `verdict` is confirmed|contradicted|not-observable; not-observable rows
carry no predicate and a reason of at least 20 characters.
"""
import argparse
import ast
import copy
import hashlib
import json
import os
import re
import subprocess
import sys

BASE = "ec3b0d583ed4eb05c7ae935dc59f560e86b0a80b"
REG = "registry/ollama-live-claims-r60.tsv"
RECEIPT = ".ufo/waves/round-60/live/receipt.json"
AMEND = "corpus/knowledge/ollama-live-amendment-r60.md"
POP_FILES_RE = re.compile(r"^(SKILL\.md|corpus/knowledge/[^/]+\.md)$")
POP_A = re.compile(r"inference", re.I)
POP_B = re.compile(r"ollama|api/tags|api/ps|expires_at", re.I)
OLLAMA_ENTRY = "corpus/knowledge/ollama-evidence-replay.md"
MIN_EVAL_ROWS, MIN_EVAL_LINES = 5, 4
ALLOWED_CALLS = {"len": len, "any": any, "all": all, "sorted": sorted, "set": set, "str": str, "isinstance": isinstance,
                 "dict": dict, "list": list, "int": int, "bool": bool}
ALLOWED_NODES = (ast.Expression, ast.Compare, ast.BoolOp, ast.UnaryOp, ast.Not, ast.And, ast.Or, ast.Subscript,
                 ast.Name, ast.Load, ast.Constant, ast.List, ast.Tuple, ast.Set, ast.ListComp, ast.GeneratorExp,
                 ast.SetComp, ast.comprehension, ast.Call, ast.Eq, ast.NotEq, ast.In, ast.NotIn, ast.Is, ast.IsNot,
                 ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.Store, ast.IfExp, ast.Slice)


def git(repo, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, env=env)


def blob(repo, rev, path):
    p = git(repo, "show", f"{rev}:{path}")
    return p.stdout.decode("utf-8", "replace") if p.returncode == 0 else None


def population(repo, base):
    ls = git(repo, "ls-tree", "-r", "--name-only", base).stdout.decode().split("\n")
    pop = {}
    for path in sorted(p for p in ls if POP_FILES_RE.match(p)):
        text = blob(repo, base, path) or ""
        for n, line in enumerate(text.split("\n"), 1):
            if POP_A.search(line) and (POP_B.search(line) or path == OLLAMA_ENTRY):
                pop[(path, n)] = line
    return pop


def parse_registry(text):
    rows = []
    for raw in (text or "").split("\n"):
        if not raw.strip() or raw.startswith("#") or raw.startswith("id\t"):
            continue
        cols = raw.split("\t")
        if len(cols) != 8:
            rows.append({"bad": raw[:80]})
            continue
        rows.append(dict(zip(("id", "path", "line", "quote", "predicate", "verdict", "observed", "reason"), cols)))
    return rows


def safe_compile(expr):
    tree = ast.parse(expr, mode="eval")
    for node in ast.walk(tree):
        if not isinstance(node, ALLOWED_NODES):
            raise ValueError(f"node {type(node).__name__} not allowed")
        if isinstance(node, ast.Call) and not (isinstance(node.func, ast.Name) and node.func.id in ALLOWED_CALLS):
            raise ValueError("call not allowed")
        if isinstance(node, ast.Name) and node.id.startswith("__"):
            raise ValueError("dunder name")
    return tree


def evaluate(tree, caps):
    try:
        return bool(eval(compile(tree, "<pred>", "eval"), {"__builtins__": {}, **ALLOWED_CALLS}, {"c": caps}))
    except Exception:  # noqa: BLE001
        return None


def chains(tree):
    """Maximal constant-key subscript chains rooted at Name c, as key lists."""
    out = []
    inner = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Subscript):
            inner.add(id(node.value))
    for node in ast.walk(tree):
        if isinstance(node, ast.Subscript) and id(node) not in inner:
            keys, cur = [], node
            ok = True
            while isinstance(cur, ast.Subscript):
                if not isinstance(cur.slice, ast.Constant):
                    ok = False
                    break
                keys.append(cur.slice.value)
                cur = cur.value
            if ok and isinstance(cur, ast.Name) and cur.id == "c":
                out.append(list(reversed(keys)))
    return out


def deep_sentinel(node, counter):
    if isinstance(node, dict):
        return {k: deep_sentinel(v, counter) for k, v in node.items()}
    if isinstance(node, list):
        return [deep_sentinel(v, counter) for v in node]
    counter[0] += 1
    return f"SENT{counter[0]}"


def set_path(root, keys, fn):
    cur = root
    for k in keys[:-1]:
        cur = cur[k]
    cur[keys[-1]] = fn(cur[keys[-1]])


def falsifiable(tree, caps):
    base = evaluate(tree, caps)
    if base is None:
        return False
    for keys in chains(tree):
        for mode in ("none", "sent", "empty"):
            mut = copy.deepcopy(caps)
            try:
                if mode == "none":
                    set_path(mut, keys, lambda v: None)
                elif mode == "sent":
                    set_path(mut, keys, lambda v: deep_sentinel(v, [0]))
                else:
                    set_path(mut, keys, lambda v: [] if isinstance(v, list) else ({} if isinstance(v, dict) else ""))
            except (KeyError, IndexError, TypeError):
                continue
            r = evaluate(tree, mut)
            if r is not None and r != base:
                return True
    return False


def receipt_caps(text):
    """Return (caps, ok). ok = schema right and every capture's sha256 matches its body."""
    try:
        rec = json.loads(text)
        caps, ok = {}, rec.get("schema") == "kama-ollama-live/v1"
        for name, cap in rec["captures"].items():
            if hashlib.sha256(cap["body"].encode("utf-8")).hexdigest() != cap["sha256"]:
                ok = False
            try:
                caps[name] = json.loads(cap["body"])
            except ValueError:
                pass
        return caps, ok
    except (ValueError, KeyError, TypeError, AttributeError):
        return {}, False


def score(pop, reg_text, receipt_text, amend_text, base_lines=None):
    rows = parse_registry(reg_text)
    caps, receipt_ok = receipt_caps(receipt_text or "")
    covered, ev_rows, ev_lines, sens, bound, contra, amended, errors = set(), 0, set(), 0, 0, 0, 0, 0
    good = 0
    for r in rows:
        if "bad" in r:
            errors += 1
            continue
        try:
            key = (r["path"], int(r["line"]))
        except ValueError:
            errors += 1
            continue
        if key not in pop:
            continue
        q = r["quote"].strip()
        nq = len(q.split())
        if not (3 <= nq <= 25) or q not in pop[key]:
            continue
        if r["verdict"] not in ("confirmed", "contradicted", "not-observable"):
            continue
        if r["verdict"] == "not-observable":
            if r["predicate"].strip() or len(r["reason"].strip()) < 20:
                continue
            covered.add(key)
            good += 1
            continue
        try:
            tree = safe_compile(r["predicate"])
        except (SyntaxError, ValueError):
            errors += 1
            continue
        res = evaluate(tree, caps)
        if res is None:
            continue
        if (res and r["verdict"] != "confirmed") or (not res and r["verdict"] != "contradicted"):
            continue
        bound += 1
        if not falsifiable(tree, caps):
            continue
        sens += 1
        ev_rows += 1
        ev_lines.add(key)
        covered.add(key)
        good += 1
        if r["verdict"] == "contradicted":
            contra += 1
            if r["id"] and r["id"] in (amend_text or "") and r["observed"].strip() and r["observed"].strip() in (amend_text or ""):
                amended += 1
    met = (bool(rows) and len(covered) == len(pop) and ev_rows >= MIN_EVAL_ROWS and len(ev_lines) >= MIN_EVAL_LINES
           and amended == contra and receipt_ok and good == len([r for r in rows if "bad" not in r]) and errors == 0)
    return {"rows": len(rows), "covered": len(covered), "population": len(pop), "evaluated": ev_rows,
            "eval_lines": len(ev_lines), "sensitive": sens, "bound": bound, "contradicted": contra,
            "amended": amended, "receipt_ok": receipt_ok, "good_rows": good, "errors": errors, "met": met}


def rows_to_text(rows):
    cols = ("id", "path", "line", "quote", "predicate", "verdict", "observed", "reason")
    return "id\tpath\tline\tquote\tpredicate\tverdict\tobserved\treason\n" + "".join(
        "\t".join(r.get(k, "") for k in cols) + "\n" for r in rows if "bad" not in r)


def controls(pop, reg_text, receipt_text, amend_text):
    rows = [r for r in parse_registry(reg_text) if "bad" not in r]
    res = {}
    # 1 tautology: every predicate becomes True
    t = [dict(r, predicate="True", verdict="confirmed") if r["predicate"].strip() else r for r in rows]
    res["tautology"] = (0 if score(pop, rows_to_text(t), receipt_text, amend_text)["met"] else 1, 1)
    # 2 verdict flips, one row at a time
    n = ok = 0
    for i, r in enumerate(rows):
        if r["verdict"] == "not-observable":
            continue
        n += 1
        m = copy.deepcopy(rows)
        m[i]["verdict"] = "contradicted" if r["verdict"] == "confirmed" else "confirmed"
        ok += 0 if score(pop, rows_to_text(m), receipt_text, amend_text)["met"] else 1
    res["verdict_flip"] = (ok, n)
    # 3 quote corruption, one row at a time
    n = ok = 0
    for i, r in enumerate(rows):
        n += 1
        m = copy.deepcopy(rows)
        m[i]["quote"] = r["quote"] + " zzcorrupt"
        ok += 0 if score(pop, rows_to_text(m), receipt_text, amend_text)["met"] else 1
    res["quote_corrupt"] = (ok, n)
    # 4 dropped population line
    n = ok = 0
    for key in sorted(pop):
        n += 1
        m = [r for r in rows if (r["path"], r["line"]) != (key[0], str(key[1]))]
        ok += 0 if score(pop, rows_to_text(m), receipt_text, amend_text)["met"] else 1
    res["drop_line"] = (ok, n)
    # 5 tampered capture
    try:
        rec = json.loads(receipt_text)
        first = next(iter(rec["captures"]))
        rec["captures"][first]["body"] += " "
        res["tamper"] = (0 if score(pop, reg_text, json.dumps(rec), amend_text)["met"] else 1, 1)
    except (ValueError, StopIteration, KeyError, TypeError):
        res["tamper"] = (0, 1)
    return res


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--tip", required=True)
    ap.add_argument("--base", default=BASE)
    a = ap.parse_args(argv)
    pop = population(a.repo, a.base)
    reg = blob(a.repo, a.tip, REG)
    receipt = blob(a.repo, a.tip, RECEIPT)
    amend = blob(a.repo, a.tip, AMEND)
    s = score(pop, reg or "", receipt or "", amend or "")
    c_ok = c_n = 0
    if reg and receipt:
        for ok, n in controls(pop, reg, receipt, amend or "").values():
            c_ok += ok
            c_n += n
    met = s["met"] and c_n > 0 and c_ok == c_n
    print(f"population={s['population']} rows={s['rows']} covered={s['covered']}/{s['population']} "
          f"evaluated={s['evaluated']} eval_lines={s['eval_lines']} sensitive={s['sensitive']}/{s['evaluated']} "
          f"bound={s['bound']} contradicted={s['contradicted']} amended={s['amended']}/{s['contradicted']} "
          f"receipt_ok={int(s['receipt_ok'])} controls_rejected={c_ok}/{c_n} errors={s['errors']} met={met}")
    return 0 if met else 1


if __name__ == "__main__":
    sys.exit(main())
