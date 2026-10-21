#!/usr/bin/env python3
"""Minimal gate-accepted witnesses on the REAL release tree, plus the exhaustive set of
regular members that some single contiguous run-removal decoy can drop while both
tree and links pins still match. The release tree is only read; receipts go to scratch."""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

SCRATCH = Path("/tmp/kama-r21-LinksDigestEncoding")
LANE = SCRATCH / "lane"
REAL = Path("/home/vgpnk/.local/opt/llama-b11755")
RCPT = SCRATCH / "receipts"
WORK = SCRATCH / "work"
GATE_CLI = LANE / "tests/llamacpp-live/check-receipt.py"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


prod = load("kama_prod", LANE / "tools/kama-llamacpp-live.py")
gate = load("kama_gate", GATE_CLI)
rt, rt_sha = prod.install_tree(str(REAL / "llama-server"))
rl, rl_sha = prod.install_links(str(REAL / "llama-server"))
rows, bad = {}, []


def ser_links(m):
    return "".join(f"{n} -> {m[n]}\n" for n in sorted(m))


def ser_tree(m):
    return "".join(f"{n} {m[n]}\n" for n in sorted(m))


def receipt(tree, links):
    """Producer-shaped: impl digest is None when the impl name is absent from the tree."""
    r = gate._selftest_receipt_v3()
    s = r["server"]
    s["install_tree"] = dict(tree)
    s["install_tree_sha256"] = gate.install_tree_sha(tree)
    s["install_links"] = dict(links)
    s["install_links_sha256"] = gate.install_links_sha(links)
    s["sha256"] = rt["llama-server"]
    s["server_impl_sha256"] = tree.get("libllama-server-impl.so")
    return r


def cli(name, receipt_obj, extra):
    RCPT.mkdir(parents=True, exist_ok=True)
    path = RCPT / f"{name}.json"
    path.write_text(json.dumps(receipt_obj, ensure_ascii=True, allow_nan=False), encoding="utf-8")
    cp = subprocess.run([sys.executable, str(GATE_CLI), str(path), *extra],
                        capture_output=True, text=True, timeout=300)
    return cp.returncode


PINS = ["--expect-install-tree-sha256", rt_sha, "--expect-install-links-sha256", rl_sha]
REAL_IMPL = rt["libllama-server-impl.so"]

# 1. Minimal link witness: dev link + its soname folded into one newline-bearing key.
key = "libggml-base.so -> libggml-base.so.0\nlibggml-base.so.0"
wit = {k: v for k, v in rl.items() if k not in ("libggml-base.so", "libggml-base.so.0")}
wit[key] = rl["libggml-base.so.0"]
w_ser = ser_links(wit) == ser_links(rl)
w_dig = gate.install_links_sha(wit) == rl_sha
w_prob = gate.validate(receipt(rt, wit), expect_tree=rt_sha, expect_links=rl_sha)
w_gone = "libggml-base.so.0" not in wit
d = Path(tempfile.mkdtemp(prefix="wit-", dir=WORK if WORK.exists() else None))
WORK.mkdir(parents=True, exist_ok=True)
d = Path(tempfile.mkdtemp(prefix="wit-", dir=WORK))
for k, v in wit.items():
    os.symlink(v, os.path.join(os.fsencode(str(d)), k.encode("utf-8")))
_, w_prod = prod.install_links(str(d / "llama-server"))
w_cli = cli("cli-minimal-link-witness", receipt(rt, wit), PINS)
rows["minimal_link_witness"] = {
    "serialization_equal": w_ser, "gate_digest_equal": w_dig, "gate_problems": w_prob,
    "NEEDED_soname_absent": w_gone, "producer_digest_equal": w_prod == rl_sha,
    "cli_exit_with_pins": w_cli}
if not (w_ser and w_dig and w_prob == [] and w_gone and w_prod == rl_sha and w_cli == 0):
    bad.append("minimal_link_witness")
print("minimal_link_witness:", rows["minimal_link_witness"])

# 2. Exhaustive contiguous run-removal over regular members (tree side).
names = sorted(rt)
hashes = dict(rt)


def absorb_run(i, j):
    """Fold names[i:j] into the key of names[j]; every content hash is kept."""
    absorbed = set(names[i:j])
    m, prefix = {}, ""
    for n in names:
        if n in absorbed:
            prefix += f"{n} {hashes[n]}\n"
        else:
            m[prefix + n] = hashes[n]
            prefix = ""
    return m


removable, accepted_runs, tried = set(), [], 0
impl_run = None
for j in range(1, len(names)):
    for i in range(0, j):
        m = absorb_run(i, j)
        tried += 1
        if ser_tree(m) != ser_tree(rt):
            bad.append(f"serialization-{i}-{j}")
            continue
        if gate.validate(receipt(m, rl), expect_tree=rt_sha, expect_links=rl_sha) == []:
            accepted_runs.append((i, j))
            removable |= set(names[i:j + 1])   # run plus successor lose their standalone name
            if "libllama-server-impl.so" in names[i:j + 1] and impl_run is None:
                impl_run = (i, j, m)
protected = sorted(set(names) - removable)
rows["tree_runs_tried"] = tried
rows["tree_runs_accepted"] = len(accepted_runs)
rows["tree_members_removable_by_some_single_run"] = sorted(removable)
rows["tree_members_never_removable"] = protected
print(f"tree runs tried={tried} accepted={len(accepted_runs)} removable_members={len(removable)}")
print("never removable:", protected)

# 3. Impl removed as the SUCCESSOR of a run (chain rule does not constrain it).
if impl_run is None:
    bad.append("no-impl-removal-found")
else:
    i, j, m = impl_run
    removed = names[i:j + 1]
    no_pin = gate.validate(receipt(m, rl), expect_tree=rt_sha, expect_links=rl_sha)
    with_pin = gate.validate(receipt(m, rl), expect_tree=rt_sha, expect_links=rl_sha,
                             expect_server_impl=REAL_IMPL)
    c_no = cli("cli-impl-removed-no-impl-pin", receipt(m, rl), PINS)
    c_pin = cli("cli-impl-removed-with-impl-pin", receipt(m, rl), PINS +
                ["--expect-server-impl-sha256", REAL_IMPL])
    rows["impl_removed_as_successor"] = {
        "removed_names": removed, "gate_problems_no_impl_pin": no_pin,
        "gate_problems_with_impl_pin": with_pin, "cli_exit_no_impl_pin": c_no,
        "cli_exit_with_impl_pin": c_pin}
    print("impl removed as successor:", rows["impl_removed_as_successor"])
    if not (no_pin == [] and with_pin != [] and c_no == 0 and c_pin == 1):
        bad.append("impl-successor-witness")

out = SCRATCH / "minimal-witness.json"
out.write_text(json.dumps(rows, indent=2, sort_keys=True), encoding="utf-8")
print("UNEXPECTED:", bad if bad else "none")
sys.exit(1 if bad else 0)
