#!/usr/bin/env python3
"""KamaR21 C2LiteralCheck (FALSIFY). Independent recomputation of the gate
SELFTEST literal 83bdd3cc..., the live receipt install_links digest 5cb9f486...,
producer/gate encoder identity, and mutation tests of what each literal can see.

usage: literal_check.py [LANE_ROOT] [LOG_NAME]
  LANE_ROOT defaults to the lane worktree; pass a checkout of a commit to pin it.
  Writes LOG_NAME (default literal_check.log) beside this file only. Scratch is
  a temp directory that is removed. Read-only on LANE_ROOT. Exit 0 iff every
  CONFIRM line holds; OBSERVE lines record behaviour without asserting it."""
import ast
import copy
import difflib
import hashlib
import importlib.util
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile

LANE = sys.argv[1] if len(sys.argv) > 1 else "/home/vgpnk/Projects/shokunin/kama-shokunin"
LOG_NAME = sys.argv[2] if len(sys.argv) > 2 else "literal_check.log"
GATE = f"{LANE}/tests/llamacpp-live/check-receipt.py"
PROD = f"{LANE}/tools/kama-llamacpp-live.py"
RECEIPT = f"{LANE}/.ufo/waves/round-21/runs/b76727f3/live-receipt.json"
HERE = os.path.dirname(os.path.abspath(__file__))

LIT = "83bdd3ccfa67701a8531e8fad561d5765c61410f060eb203c4646521749f704e"
RCPT = "5cb9f4865c8e1315dbd1baa99310c9bc65ddcf469929488359c66587b6470060"
UNI_LIT = "9e226427f148781fc333f5a86313104c49363043e03149c651457cd6e55b1758"
KEYSORT_LIT = "7951deff61d4304af5863a13c2ef570ffc96f1d8df5fb3214743dc9953b8aeea"
PROD_LIT = "deb111fa5739ffa31de111667ad4b1f085391143f1b88c757b5801364ce4aac9"
EMPTY = hashlib.sha256(b"{}").hexdigest()
HAND_SELF = '{"libllama-alias.so":"libllama.so.0","libllama.so.0":"libllama.so"}'
HAND_UNI = ('{"libllama-alias.so":"libllama.so.0","libllama.so.0":"libllama.so",'
            '"lib\\u00e9.so":"libllama.so.0"}')
HAND_KEYSORT = '{"a":"y","b":"x"}'
HAND_RCPT = (
    '{"libggml-base.so":"libggml-base.so.0","libggml-base.so.0":"libggml-base.so.0.27.0",'
    '"libggml.so":"libggml.so.0","libggml.so.0":"libggml.so.0.27.0",'
    '"libllama-common.so":"libllama-common.so.0","libllama-common.so.0":"libllama-common.so.0.7.0",'
    '"libllama.so":"libllama.so.0","libllama.so.0":"libllama.so.0.7.0",'
    '"libmtmd.so":"libmtmd.so.0","libmtmd.so.0":"libmtmd.so.0.7.0"}')
HAND_PROD = '{"libllama.so":"libllama.so.0","libllama.so.0":"libllama.so.0.7.0"}'
SORT_SEP_OLD = "links, sort_keys=True, separators=(',', ':'),"
ASCII_OLD = "ensure_ascii=True).encode('ascii')"
FROZEN_GATE_SUMMARY = ("selftest: 11 VALID and 1 NOT-EVALUATED receipts accepted; "
                       "91 mutations + unreadable case rejected")

LOG = []
FAILED = []


def say(msg):
    print(msg)
    LOG.append(msg)


def confirm(label, ok, detail=""):
    say(f"CONFIRM {'PASS' if ok else 'FAIL'} {label}" + (f" :: {detail}" if detail else ""))
    if not ok:
        FAILED.append(label)


def observe(label, detail):
    say(f"OBSERVE {label} :: {detail}")


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def sh_sha256(text):
    """printf '%s' TEXT | sha256sum, as run by hand: no trailing newline."""
    proc = subprocess.run(["sh", "-c", "printf '%s' \"$1\" | sha256sum", "sh", text],
                          capture_output=True, text=True)
    return proc.stdout.split()[0], proc.returncode


class Recorder:
    """Stands in for the hashlib module and records the exact bytes hashed."""

    def __init__(self):
        self.calls = []

    def sha256(self, data):
        self.calls.append(bytes(data))
        return hashlib.sha256(data)


def fresh_ns():
    return {"json": json, "hashlib": hashlib, "os": os, "stat": stat}


def load_defs(src, names, ns):
    """exec the named top-level functions of src into ns (no module side effects)."""
    found = {n.name: n for n in ast.parse(src).body
             if isinstance(n, ast.FunctionDef) and n.name in names}
    if set(found) != set(names):
        raise SystemExit(f"missing definitions: {sorted(set(names) - set(found))}")
    for name in names:
        exec(compile(ast.get_source_segment(src, found[name]), f"<{name}>", "exec"), ns)
    return found


def encode(ns, fname, obj):
    """(bytes hashed, hexdigest) for one call of a real encoder function."""
    rec = Recorder()
    ns["hashlib"] = rec
    try:
        digest = ns[fname](obj)
    finally:
        ns["hashlib"] = hashlib
    if len(rec.calls) != 1:
        raise SystemExit(f"{fname} hashed {len(rec.calls)} times")
    return rec.calls[0], digest


def no_dupes(pairs):
    keys = [k for k, _ in pairs]
    dup = sorted({k for k in keys if keys.count(k) > 1})
    if dup:
        raise ValueError(f"duplicate JSON keys {dup}")
    return dict(pairs)


def mutate(text, old, new):
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"mutation anchor occurs {n} times: {old[:40]!r}")
    return text.replace(old, new)


def norm_dump(node):
    n = copy.deepcopy(node)
    n.name = "F"
    body = n.body
    if (body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant)
            and isinstance(body[0].value.value, str)):
        n.body = body[1:]
    return ast.dump(n)


def find_one(src, name):
    hits = [n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef) and n.name == name]
    if len(hits) != 1:
        raise SystemExit(f"{name}: {len(hits)} definitions")
    return hits[0]


def body_text(src, node):
    return "\n".join(src.splitlines()[node.body[-1].lineno - 1:node.end_lineno])


def fn_text(src, node):
    return src.splitlines()[node.lineno - 1:node.end_lineno]


def gate_run(tmp, label, doc, extra):
    path = os.path.join(tmp, f"{label}.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2, sort_keys=True)
    proc = subprocess.run([sys.executable, GATE, path, *extra],
                          capture_output=True, text=True, timeout=120)
    first = proc.stdout.strip().splitlines()[0] if proc.stdout.strip() else ""
    return proc.returncode, first


def run(gsrc, psrc, tmp):
    # 1. hand-written canonical texts, hashed with printf | sha256sum
    literals = [("SELFTEST literal", HAND_SELF, LIT),
                ("receipt install_links", HAND_RCPT, RCPT),
                ("producer literal", HAND_PROD, PROD_LIT)]
    if "links-unicode-canonical-valid" in gsrc:
        literals.append(("unicode case literal", HAND_UNI, UNI_LIT))
    else:
        observe("unicode case literal", "no links-unicode-canonical-valid case in this state")
    if "is not key-sorted" in psrc:
        literals.append(("producer key-sort literal", HAND_KEYSORT, KEYSORT_LIT))
    else:
        observe("producer key-sort literal", "no key-sorted assertion in this state")
    for label, text, want in literals:
        got, rc = sh_sha256(text)
        confirm(f"printf|sha256sum {label}", got == want and rc == 0, f"digest={got} exit={rc}")

    # 2. SELFTEST_LINKS read from the gate source (never retyped)
    assigns = [n for n in ast.parse(gsrc).body if isinstance(n, ast.Assign)
               and any(isinstance(t, ast.Name) and t.id == "SELFTEST_LINKS" for t in n.targets)]
    if len(assigns) != 1:
        raise SystemExit(f"SELFTEST_LINKS assigned {len(assigns)} times")
    SELFTEST_LINKS = ast.literal_eval(assigns[0].value)
    say(f"SELFTEST_LINKS={SELFTEST_LINKS}")
    g_ns, p_ns = fresh_ns(), fresh_ns()
    load_defs(gsrc, ["install_links_sha", "link_chain_problem"], g_ns)
    load_defs(psrc, ["links_digest", "install_links"], p_ns)
    gb, gd = encode(g_ns, "install_links_sha", SELFTEST_LINKS)
    pb, pd = encode(p_ns, "links_digest", SELFTEST_LINKS)
    confirm("gate install_links_sha(SELFTEST_LINKS) == LIT", gd == LIT, gd)
    confirm("producer links_digest(SELFTEST_LINKS) == LIT", pd == LIT, pd)
    confirm("SELFTEST bytes == hand-written text, producer == gate",
            gb == HAND_SELF.encode() and pb == gb)

    # 3. live receipt parsed with duplicate-key rejection; digest recomputed from its map
    raw = read(RECEIPT)
    doc = json.loads(raw, object_pairs_hook=no_dupes)
    links = doc["server"]["install_links"]
    stored = doc["server"]["install_links_sha256"]
    say(f"receipt file sha256={hashlib.sha256(raw.encode()).hexdigest()} entries={len(links)}")
    rgb, rgd = encode(g_ns, "install_links_sha", links)
    rpb, rpd = encode(p_ns, "links_digest", links)
    confirm("gate recomputation over receipt install_links == RCPT", rgd == RCPT, rgd)
    confirm("producer digest over receipt install_links == RCPT", rpd == RCPT, rpd)
    confirm("receipt stored install_links_sha256 == recomputed", stored == rgd, stored)
    confirm("receipt bytes == hand-written text, producer == gate",
            rgb == HAND_RCPT.encode() and rpb == rgb)
    tree = doc["server"]["install_tree"]
    chains = {n: g_ns["link_chain_problem"](n, links, tree) for n in sorted(links)}
    confirm("every receipt link chain ends at a pinned install_tree member",
            all(v is None for v in chains.values()), f"{len(chains)} links")
    live_links, live_digest, live_problems = p_ns["install_links"](
        "/home/vgpnk/.local/opt/llama-b11755/llama-server")
    observe("installed tree now (read-only lstat/readlink)",
            f"links_equal_receipt={live_links == links} digest={live_digest} "
            f"problems={live_problems}")

    # 4. encoder identity: AST modulo name/docstring, function body text, bytes on a battery
    gnode, pnode = find_one(gsrc, "install_links_sha"), find_one(psrc, "links_digest")
    confirm("AST identical modulo function name and docstring",
            norm_dump(gnode) == norm_dump(pnode))
    confirm("function bodies byte-identical", body_text(gsrc, gnode) == body_text(psrc, pnode))
    for line in difflib.unified_diff(fn_text(gsrc, gnode), fn_text(psrc, pnode),
                                     "check-receipt.py:install_links_sha",
                                     "kama-llamacpp-live.py:links_digest", lineterm=""):
        say("  diff| " + line)
    battery = [{}, {"a": "b\nc -> d"}, {"a": "b", "c": "d"}, {"libé.so": "x"},
               {'q"uote': 'back\\slash'}, {"x": "\udcff"}, {"ctrl\x01": "v"},
               {"b": "1", "a": "2", "B": "3", "\u00e9": "4", "\U0001F600": "5"},
               SELFTEST_LINKS, links]
    same = [encode(g_ns, "install_links_sha", c) == encode(p_ns, "links_digest", c)
            for c in battery]
    confirm("encoders identical (bytes and digest) on 10-input battery", all(same),
            f"{sum(same)}/{len(same)}")

    # 5. mutation tests: what the gate literal and the producer literal can see
    gate_vars = {
        "base": gsrc,
        "nosort": mutate(gsrc, SORT_SEP_OLD, "links, separators=(',', ':'),"),
        "sepdefault": mutate(gsrc, SORT_SEP_OLD, "links, sort_keys=True,"),
        "noascii": mutate(gsrc, ASCII_OLD, "ensure_ascii=False).encode('utf-8')"),
    }
    for name, text in gate_vars.items():
        d = os.path.join(tmp, f"gate-{name}")
        os.makedirs(d)
        path = os.path.join(d, "check-receipt.py")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
        ns = fresh_ns()
        load_defs(text, ["install_links_sha"], ns)
        _, mut_digest = encode(ns, "install_links_sha", SELFTEST_LINKS)
        proc = subprocess.run([sys.executable, path, "--selftest"], capture_output=True,
                              text=True, timeout=900)
        fails = sorted({l.split(" ", 2)[2].split(":")[0] for l in proc.stderr.splitlines()
                        if l.startswith("SELFTEST FAIL ")})
        if name == "base":
            summary = proc.stdout.strip()
            if LANE.endswith("kama-shokunin"):
                confirm("gate --selftest on the worktree exits 0", proc.returncode == 0,
                        f"exit={proc.returncode} summary={summary!r}")
            else:
                confirm("gate --selftest on the pinned commit exits 0 with the frozen summary",
                        proc.returncode == 0 and summary == FROZEN_GATE_SUMMARY,
                        f"exit={proc.returncode} summary={summary!r}")
        observe(f"gate mutant {name}",
                f"SELFTEST_LINKS digest {mut_digest[:16]}.. equals_LIT={mut_digest == LIT}; "
                f"--selftest exit={proc.returncode}; failing cases={fails}")

    prod_vars = {
        "base": psrc,
        "nosort": mutate(psrc, SORT_SEP_OLD, "links, separators=(',', ':'),"),
        "sepdefault": mutate(psrc, SORT_SEP_OLD, "links, sort_keys=True,"),
        "noascii": mutate(psrc, ASCII_OLD, "ensure_ascii=False).encode('utf-8')"),
    }
    for name, text in prod_vars.items():
        path = os.path.join(tmp, f"prod-{name}.py")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
        spec = importlib.util.spec_from_file_location(f"kll_{name}", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        try:
            mod._install_identity_selftest()
            verdict = "passes"
        except BaseException as exc:  # observation only
            verdict = f"raises {type(exc).__name__}: {exc}"
        observe(f"producer mutant {name}", f"_install_identity_selftest {verdict}")

    # 6. empty-map digest path and tamper cases on the live receipt
    ctl_rc, ctl_out = gate_run(tmp, "ctl", copy.deepcopy(doc),
                               ["--require-install-links", "--expect-install-links-sha256", RCPT])
    confirm("live receipt VALID with --require-install-links and RCPT pin", ctl_rc == 0, ctl_out)
    r1 = copy.deepcopy(doc)
    r1["server"]["install_links"] = {}
    r1["server"]["install_links_sha256"] = None
    for label, extra in (("r1-empty-null-no-pin", ["--require-install-links"]),
                         ("r1-empty-null-pin-of-empty",
                          ["--require-install-links", "--expect-install-links-sha256", EMPTY])):
        rc, out = gate_run(tmp, label, r1, extra)
        observe(label, f"exit={rc} :: {out}")
    r2 = copy.deepcopy(doc)
    r2["server"]["install_links_sha256"] = None
    rc, out = gate_run(tmp, "r2-nonempty-null", r2, ["--require-install-links"])
    confirm("non-empty install_links with null digest is rejected", rc == 1, out)
    r3 = copy.deepcopy(doc)
    r3["server"]["install_links_sha256"] = "0" * 64
    rc, out = gate_run(tmp, "r3-tampered", r3, ["--require-install-links"])
    confirm("tampered digest is rejected", rc == 1, out)

    # 7. non-ASCII source characters in the link-related selftest regions (escapes not counted)
    g_lines, p_lines = gsrc.splitlines(), psrc.splitlines()
    gate_na = sum(ord(c) > 0x7F for l in g_lines[1959:2035] for c in l)
    prod_na = sum(ord(c) > 0x7F for l in p_lines[1100:1160] for c in l)
    observe("non-ASCII source characters, gate lines 1960-2035 / producer lines 1101-1160",
            f"{gate_na} / {prod_na}")


def main():
    gsrc, psrc = read(GATE), read(PROD)
    say(f"state: LANE={LANE}")
    say(f"gate sha256={hashlib.sha256(gsrc.encode()).hexdigest()} "
        f"producer sha256={hashlib.sha256(psrc.encode()).hexdigest()}")
    tmp = tempfile.mkdtemp(prefix="kama-r21-c2lit-")
    try:
        run(gsrc, psrc, tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    say(f"confirm-failures={len(FAILED)}")
    with open(os.path.join(HERE, LOG_NAME), "w", encoding="utf-8") as fh:
        fh.write("\n".join(LOG) + "\n")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
