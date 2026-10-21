#!/usr/bin/env python3
"""LinksDigestEncoding probe (KamaR21, round 21).

Attacks the two digest serializations at draft a29bb84:
  install_tree_sha256  = sha256(''.join(f'{name} {sha}\\n' for sorted names))
  install_links_sha256 = sha256(''.join(f'{name} -> {text}\\n' for sorted names))

Uses the REAL producer (tools/kama-llamacpp-live.py) and REAL gate
(tests/llamacpp-live/check-receipt.py) from the scratch clone. The real release
tree is only read. All mutations happen under WORK. Prints one RESULT line per
experiment; exits 0 iff every observed outcome matched the expectation.
"""
import copy
import hashlib
import importlib.util
import json
import os
import random
import subprocess
import sys
import tempfile
from pathlib import Path

SCRATCH = Path("/tmp/kama-r21-LinksDigestEncoding")
LANE = SCRATCH / "lane"
REAL = Path("/home/vgpnk/.local/opt/llama-b11755")
WORK = SCRATCH / "work"
RCPT = SCRATCH / "receipts"
GATE_CLI = LANE / "tests/llamacpp-live/check-receipt.py"

UNEXPECTED = []
SUMMARY = {}


def record(tag, ok, detail):
    print(f"RESULT {tag}: {'OK' if ok else 'UNEXPECTED'} :: {detail}", flush=True)
    if not ok:
        UNEXPECTED.append(tag)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


prod = load("kama_prod", LANE / "tools/kama-llamacpp-live.py")
gate = load("kama_gate", GATE_CLI)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def make_dir(files=(), links=(), fifos=()):
    """Create a real directory. Names/targets are bytes so non-UTF-8 is possible."""
    WORK.mkdir(parents=True, exist_ok=True)
    d = Path(tempfile.mkdtemp(prefix="case-", dir=WORK))
    base = os.fsencode(str(d))
    for name, data in files:
        with open(os.path.join(base, name), "wb") as fh:
            fh.write(data)
    for name, target in links:
        os.symlink(target, os.path.join(base, name))
    for name in fifos:
        os.mkfifo(os.path.join(base, name))
    return d


def tree_of(d):
    return prod.install_tree(str(d / "llama-server"))


def links_of(d):
    return prod.install_links(str(d / "llama-server"))


def ser_tree(m):
    return "".join(f"{n} {m[n]}\n" for n in sorted(m))


def ser_links(m):
    return "".join(f"{n} -> {m[n]}\n" for n in sorted(m))


def occurrences(s, pat):
    out, i = [], s.find(pat)
    while i != -1:
        out.append(i)
        i = s.find(pat, i + 1)
    return out


def alternating_parses(S):
    """Every alternating choice of ' -> ' and '\\n' separators in S that starts
    with ' -> ' and ends with the final '\\n'. Each choice parses S back into a
    dict {key: text}; a dict whose sorted serialization equals S has the same
    install_links digest input, so all such dicts collide by construction."""
    events = sorted([(p, "A") for p in occurrences(S, " -> ")] +
                    [(p, "B") for p in occurrences(S, "\n")])
    last = len(S) - 1
    out = []

    def rec(start, want, acc):
        for j in range(start, len(events)):
            p, kind = events[j]
            if kind != want:
                continue
            nxt = acc + [(p, kind)]
            if kind == "B":
                if p == last:
                    out.append(nxt)
                else:
                    rec(j + 1, "A", nxt)
            else:
                rec(j + 1, "B", nxt)

    rec(0, "A", [])
    return out


def decode_links(S, seq):
    m, prev = {}, 0
    for i in range(0, len(seq), 2):
        a = seq[i][0]
        b = seq[i + 1][0]
        key = S[prev:a]
        if key in m:
            return None
        m[key] = S[a + 4:b]
        prev = b + 1
    return m


# Shared receipt scaffold: the gate's own selftest receipt (valid v3).
BASE = gate._selftest_receipt_v3()
assert gate.validate(copy.deepcopy(BASE)) == [], "selftest base must be valid"
SELFTEST_LINKS = dict(gate.SELFTEST_LINKS)
SYN_TREE = {"llama-server": gate.SERVER_SHA,
            "libllama-server-impl.so": gate.IMPL_SHA,
            "libllama.so": gate.LIB_SHA}


def receipt_for(tree, links, server_sha=None, impl_sha=None):
    """Producer-shaped receipt: digests recomputed from the maps; impl digest
    None when the impl name is absent (as the producer's path check yields)."""
    r = copy.deepcopy(BASE)
    s = r["server"]
    s["install_tree"] = dict(tree)
    s["install_tree_sha256"] = gate.install_tree_sha(tree)
    s["install_links"] = dict(links)
    s["install_links_sha256"] = gate.install_links_sha(links)
    s["sha256"] = tree["llama-server"] if server_sha is None else server_sha
    s["server_impl_sha256"] = (tree.get("libllama-server-impl.so")
                               if impl_sha is None else impl_sha)
    return r


def raw_receipt(tree, links):
    """Same shape, but the tree digest is a dummy so validate() itself must
    recompute install_tree_sha over the (possibly unencodable) map."""
    r = receipt_for(SYN_TREE, links)
    r["server"]["install_tree"] = dict(tree)
    r["server"]["install_tree_sha256"] = "0" * 64
    r["server"]["sha256"] = tree.get("llama-server", BASE["server"]["sha256"])
    return r


# ---------------------------------------------------------------- E1..E3
# Producer-level: real directories, real install_tree/install_links.
h_one, h_two = sha(b"one"), sha(b"two")
A = make_dir(files=[(b"notes-1.txt", b"one"), (b"notes-2.txt", b"two")])
B = make_dir(files=[(b"notes-1.txt " + h_one.encode() + b"\nnotes-2.txt", b"two")])
tA, dA = tree_of(A)
tB, dB = tree_of(B)
record("E1-tree-newline-collision",
       dA == dB and tA != tB
       and tA == {"notes-1.txt": h_one, "notes-2.txt": h_two}
       and tB == {"notes-1.txt " + h_one + "\nnotes-2.txt": h_two},
       f"equal_digest={dA == dB} digest={dA} mapA_keys={len(tA)} "
       f"mapB_keys={len(tB)} mapB_key0={list(tB)[0]!r}")

A = make_dir(links=[(b"x -> y", b"z")])
B = make_dir(links=[(b"x", b"y -> z")])
lA, la = links_of(A)
lB, lb = links_of(B)
record("E2-links-arrow-collision",
       la == lb and lA != lB,
       f"equal_digest={la == lb} digest={la} mapA={lA} mapB={lB}")

legit_pair = [(b"libllama-alias.so", b"libllama.so.0"), (b"libllama.so.0", b"libllama.so")]
A = make_dir(files=[(b"libllama.so", b"LIB")], links=legit_pair)
B = make_dir(files=[(b"libllama.so", b"LIB")],
             links=[(b"libllama-alias.so -> libllama.so.0\nlibllama.so.0", b"libllama.so")])
lA, la = links_of(A)
lB, lb = links_of(B)
record("E3-links-newline-soname-collision",
       la == lb and lA != lB,
       f"equal_digest={la == lb} digest={la} keysB={list(lB)!r}")

# ---------------------------------------------------------------- E4..E6
# Gate-level: receipts validated by the REAL validate() against the pinned digests.
pin_links = gate.install_links_sha(SELFTEST_LINKS)
legit_r = receipt_for(SYN_TREE, SELFTEST_LINKS)
decoy_links = {"libllama-alias.so -> libllama.so.0\nlibllama.so.0": "libllama.so"}
decoy_r = receipt_for(SYN_TREE, decoy_links)
p_legit = gate.validate(copy.deepcopy(legit_r), expect_links=pin_links)
p_decoy = gate.validate(copy.deepcopy(decoy_r), expect_links=pin_links)
record("E4-gate-accepts-links-decoy",
       p_legit == [] and p_decoy == [] and gate.install_links_sha(decoy_links) == pin_links,
       f"legit_problems={p_legit} decoy_problems={p_decoy} decoy_map={decoy_links!r}")

tree_legit = dict(SYN_TREE)
tree_legit.update({"notes-1.txt": h_one, "notes-2.txt": h_two})
tree_decoy = dict(SYN_TREE)
tree_decoy["notes-1.txt " + h_one + "\nnotes-2.txt"] = h_two
pin_tree = gate.install_tree_sha(tree_legit)
p_legit = gate.validate(receipt_for(tree_legit, SELFTEST_LINKS), expect_tree=pin_tree)
p_decoy = gate.validate(receipt_for(tree_decoy, SELFTEST_LINKS), expect_tree=pin_tree)
record("E5-gate-accepts-tree-decoy",
       p_legit == [] and p_decoy == [] and gate.install_tree_sha(tree_decoy) == pin_tree,
       f"legit_problems={p_legit} decoy_problems={p_decoy} decoy_keys={sorted(tree_decoy)!r}")

tree_noimpl = {"llama-server": gate.SERVER_SHA, "libllama.so": gate.LIB_SHA}
forged = receipt_for(tree_noimpl, SELFTEST_LINKS, impl_sha=gate.IMPL_SHA)
p_forged = gate.validate(forged, expect_server_impl=gate.IMPL_SHA)
record("E6-gate-impl-digest-not-bound-to-tree",
       p_forged == [],
       f"receipt claims impl sha with impl absent from install_tree; problems={p_forged}")

# ---------------------------------------------------------------- E7
bad_name = os.fsdecode(b"\xff.bin")
tree_bad = dict(SYN_TREE)
tree_bad[bad_name] = sha(b"raw")
try:
    gate.validate(raw_receipt(tree_bad, SELFTEST_LINKS))
    gate_out = "no exception"
except Exception as exc:  # noqa: BLE001 - record the exact failure mode
    gate_out = type(exc).__name__
D = make_dir(files=[(b"\xff.bin", b"raw")])
try:
    tree_of(D)
    prod_out = "no exception"
except Exception as exc:  # noqa: BLE001
    prod_out = type(exc).__name__
record("E7-nonutf8-name-crashes-digest",
       gate_out == "UnicodeEncodeError" and prod_out == "UnicodeEncodeError",
       f"gate_validate={gate_out} producer_install_tree={prod_out}")

# ---------------------------------------------------------------- E8
A = make_dir(files=[(b"llama-server", b"S")])
B = make_dir(files=[(b"llama-server", b"S")], fifos=[b"fifo-x"])
(B / "lib").mkdir()
(B / "lib" / "evil.so").write_bytes(b"EVIL")
tA, dA = tree_of(A)
tB, dB = tree_of(B)
lA, la = links_of(A)
lB, lb = links_of(B)
record("E8-subdir-and-fifo-invisible",
       tA == tB and dA == dB and la == lb,
       f"tree_equal={tA == tB} links_equal={la == lb} digest={dA}")

# ---------------------------------------------------------------- E9 real tree (read-only)
rt, rt_sha = prod.install_tree(str(REAL / "llama-server"))
rl, rl_sha = prod.install_links(str(REAL / "llama-server"))
record("E9-real-tree-digests",
       bool(rt_sha) and bool(rl_sha) and len(rl) == 10,
       f"regular_members={len(rt)} install_tree_sha256={rt_sha} "
       f"links={len(rl)} install_links_sha256={rl_sha}")
SUMMARY["real_install_tree_sha256"] = rt_sha
SUMMARY["real_install_links_sha256"] = rl_sha
SUMMARY["real_regular_members"] = len(rt)
SUMMARY["real_links"] = len(rl)

real_impl = rt["libllama-server-impl.so"]
real_server = rt["llama-server"]


def real_receipt(tree, links):
    return receipt_for(tree, links, server_sha=real_server,
                       impl_sha=tree.get("libllama-server-impl.so"))


# ---------------------------------------------------------------- E10 explicit soname witness
soname_key = "libllama.so -> libllama.so.0\nlibllama.so.0 -> libllama.so.0.7.0\nlibmtmd.so"
rl_decoy = {k: v for k, v in rl.items() if k not in ("libllama.so", "libllama.so.0", "libmtmd.so")}
rl_decoy[soname_key] = rl["libmtmd.so"]
ser_ok = ser_links(rl_decoy) == ser_links(rl)
dig_ok = gate.install_links_sha(rl_decoy) == rl_sha
pl = gate.validate(real_receipt(rt, rl), expect_tree=rt_sha, expect_links=rl_sha)
pd = gate.validate(real_receipt(rt, rl_decoy), expect_tree=rt_sha, expect_links=rl_sha)
record("E10-real-tree-soname-absent-gate-accepts",
       ser_ok and dig_ok and pl == [] and pd == [],
       f"serialization_equal={ser_ok} digest_equal={dig_ok} legit_problems={pl} "
       f"decoy_problems={pd} decoy_absent={sorted(set(rl) - set(rl_decoy))}")
# Producer-level witness: the real producer emits the same digest for a directory
# whose symlinks carry the decoy names (regular members omitted: links digest only).
Dp = make_dir(links=[(k.encode(), v.encode()) for k, v in rl_decoy.items()])
_, dp_sha = links_of(Dp)
record("E10b-producer-digest-of-decoy-dir",
       dp_sha == rl_sha,
       f"producer install_links_sha256 for decoy dir={dp_sha} pinned={rl_sha}")

# ---------------------------------------------------------------- E11 exhaustive link parses
S_links = ser_links(rl)
parses = alternating_parses(S_links)
accepted_links = []
valid_parses = 0
for seq in parses:
    m = decode_links(S_links, seq)
    if m is None or ser_links(m) != S_links:
        continue
    valid_parses += 1
    if gate.validate(real_receipt(rt, m), expect_tree=rt_sha, expect_links=rl_sha) == []:
        accepted_links.append(m)
absentable = sorted({n for n in rl for m in accepted_links if n not in m})
record("E11-exhaustive-link-parses",
       valid_parses >= 1 and len(accepted_links) >= 1 and rl in accepted_links,
       f"alternating_parses={len(parses)} same_digest_parses={valid_parses} "
       f"gate_accepted={len(accepted_links)} names_absent_in_some_accepted={absentable}")
SUMMARY["link_parses_total"] = len(parses)
SUMMARY["link_parses_same_digest"] = valid_parses
SUMMARY["link_parses_gate_accepted"] = len(accepted_links)
SUMMARY["link_names_absent_in_some_accepted"] = absentable

# ---------------------------------------------------------------- E12 tree window absorptions
names = sorted(rt)
hashes = dict(rt)


def tree_map_absorbing(absorbed):
    """Same serialization as rt: members in `absorbed` are folded into the key
    of the next non-absorbed member (their 'name sha\\n' text becomes key text)."""
    m, prefix = {}, ""
    for n in names:
        if n in absorbed:
            prefix += f"{n} {hashes[n]}\n"
        else:
            m[prefix + n] = hashes[n]
            prefix = ""
    return m


accepted_windows = []
tried = 0
for i in range(len(names) - 1):
    for length in (1, 2, 3):
        if i + length >= len(names):
            break
        absorbed = set(names[i:i + length])
        m = tree_map_absorbing(absorbed)
        tried += 1
        if ser_tree(m) != ser_tree(rt):
            continue
        if gate.validate(real_receipt(m, rl), expect_tree=rt_sha, expect_links=rl_sha) == []:
            accepted_windows.append(sorted(absorbed))
absorbable_tree = sorted({n for w in accepted_windows for n in w})
never_absorbable = sorted(set(names) - set(absorbable_tree))
record("E12-tree-window-absorptions",
       len(accepted_windows) > 0 and "llama-server" in never_absorbable,
       f"windows_tried={tried} gate_accepted={len(accepted_windows)} "
       f"absorbable_members={len(absorbable_tree)} never_absorbable={never_absorbable}")
SUMMARY["tree_windows_tried"] = tried
SUMMARY["tree_windows_accepted"] = len(accepted_windows)
SUMMARY["tree_members_absorbable_by_window_le3"] = absorbable_tree
SUMMARY["tree_members_not_absorbable_by_window_le3"] = never_absorbable

cpu = [n for n in names if n.startswith("libggml-cpu-")]
witness_cpu = tree_map_absorbing(set(cpu))
pw = gate.validate(real_receipt(witness_cpu, rl), expect_tree=rt_sha, expect_links=rl_sha)
ser_w = ser_tree(witness_cpu) == ser_tree(rt)
record("E12b-witness-cpu-backends-removed",
       ser_w and pw == [] and len(cpu) == 14,
       f"absorbed_cpu_backends={len(cpu)} serialization_equal={ser_w} problems={pw}")
lic = tree_map_absorbing({"LICENSE"})
pl2 = gate.validate(real_receipt(lic, rl), expect_tree=rt_sha, expect_links=rl_sha)
lic_key = [k for k in lic if k.startswith("LICENSE")][0]
record("E12c-witness-license-absorbed",
       ser_tree(lic) == ser_tree(rt) and pl2 == [],
       f"key={lic_key!r} problems={pl2}")

impl_absorb = tree_map_absorbing({"libllama-server-impl.so"})
ri = real_receipt(impl_absorb, rl)
p_no_pin = gate.validate(copy.deepcopy(ri), expect_tree=rt_sha, expect_links=rl_sha)
p_pin = gate.validate(copy.deepcopy(ri), expect_tree=rt_sha, expect_links=rl_sha,
                      expect_server_impl=real_impl)
record("E12d-impl-absorbed-rejected-by-chain",
       ser_tree(impl_absorb) == ser_tree(rt) and p_no_pin != [] and p_pin != [],
       f"without_impl_pin={p_no_pin} with_impl_pin={p_pin}")

# ---------------------------------------------------------------- E13 random tree blocks
rng = random.Random(21)
samples, accepted_rand, absorbed_union = 0, 0, set()
for _ in range(2000):
    absorbed = {n for n in names[:-1] if rng.random() < 0.5}
    m = tree_map_absorbing(absorbed)
    assert ser_tree(m) == ser_tree(rt)
    samples += 1
    if gate.validate(real_receipt(m, rl), expect_tree=rt_sha, expect_links=rl_sha) == []:
        accepted_rand += 1
        absorbed_union |= absorbed
record("E13-random-tree-parses",
       accepted_rand > 0,
       f"samples={samples} serialization_equal=all gate_accepted={accepted_rand} "
       f"distinct_absorbed_members_in_accepted={len(absorbed_union)}")
SUMMARY["tree_random_samples"] = samples
SUMMARY["tree_random_accepted"] = accepted_rand

# ---------------------------------------------------------------- E14 JSON duplicate keys
dup = json.loads('{"install_links_sha256": "' + "a" * 64 + '", '
                 '"install_links_sha256": "' + "b" * 64 + '"}')
record("E14-json-duplicate-keys-last-wins",
       dup["install_links_sha256"] == "b" * 64,
       "json.load silently keeps the last duplicate key")

# ---------------------------------------------------------------- E15 shipped CLI on receipts
RCPT.mkdir(parents=True, exist_ok=True)
pins = ["--expect-install-tree-sha256", rt_sha, "--expect-install-links-sha256", rl_sha]
cases = [
    ("cli-real-legit", real_receipt(rt, rl), pins, 0),
    ("cli-real-soname-decoy", real_receipt(rt, rl_decoy), pins, 0),
    ("cli-real-cpu-decoy", real_receipt(witness_cpu, rl), pins, 0),
    ("cli-real-impl-absorbed-with-impl-pin", ri,
     pins + ["--expect-server-impl-sha256", real_impl], 1),
    ("cli-nonutf8-name", raw_receipt(tree_bad, SELFTEST_LINKS), [], 1),
]
cli_rows = []
for name, receipt, extra, want in cases:
    path = RCPT / f"{name}.json"
    path.write_text(json.dumps(receipt, ensure_ascii=True, allow_nan=False), encoding="utf-8")
    cp = subprocess.run([sys.executable, str(GATE_CLI), str(path), *extra],
                        capture_output=True, text=True, timeout=300)
    first = (cp.stdout.strip().splitlines() or [""])[0][:100]
    if "Traceback" in cp.stderr:
        tail = "uncaught-exception: " + cp.stderr.strip().splitlines()[-1][:100]
    else:
        tail = first
    cli_rows.append({"case": name, "exit": cp.returncode, "want": want, "out": tail})
    record(f"E15-{name}", cp.returncode == want, f"exit={cp.returncode} want={want} :: {tail}")
SUMMARY["cli"] = cli_rows

out = SCRATCH / "probe-results.json"
out.write_text(json.dumps(SUMMARY, indent=2, sort_keys=True), encoding="utf-8")
print(f"SUMMARY written to {out}")
print("UNEXPECTED:", UNEXPECTED if UNEXPECTED else "none - all outcomes as expected")
sys.exit(1 if UNEXPECTED else 0)
