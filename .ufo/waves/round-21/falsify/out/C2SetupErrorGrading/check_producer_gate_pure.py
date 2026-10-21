#!/usr/bin/env python3
"""C2SetupErrorGrading (round 21, FALSIFY): pure-function cross-checks.

Loads the producer and the gate from the scratch clone of a6617149 with
importlib (both have __main__ guards; no main() runs). Calls only pure
helpers on a temporary stub directory: no llama-server, no port, no model,
no subprocess. Usage: check_producer_gate_pure.py LANE_ROOT
"""
import importlib.util
import os
import sys
import tempfile


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def show(label, value):
    print(f"{label}: {value!r}")


lane = sys.argv[1]
prod = load("kama_llamacpp_live",
            os.path.join(lane, "tools", "kama-llamacpp-live.py"))
gate = load("check_receipt",
            os.path.join(lane, "tests", "llamacpp-live", "check-receipt.py"))

show("schema producer SCHEMA == gate RECEIPT_SCHEMA_V3",
     prod.SCHEMA == gate.RECEIPT_SCHEMA_V3)
show("digest producer links_digest({}) ", prod.links_digest({}))
show("digest gate    install_links_sha({})", gate.install_links_sha({}))
sample = {"libllama.so": "libllama.so.0",
          "libllama.so.0": "libllama.so.0.7.0"}
show("digest equal on empty map",
     prod.links_digest({}) == gate.install_links_sha({}))
show("digest equal on sample map",
     prod.links_digest(sample) == gate.install_links_sha(sample))

with tempfile.TemporaryDirectory(prefix="c2-stub-") as d:
    for name, data in (("llama-server", b"server-stub\n"),
                       ("libllama.so.0.7.0", b"lib-stub\n")):
        with open(os.path.join(d, name), "wb") as fh:
            fh.write(data)
    os.symlink("libllama.so.0.7.0", os.path.join(d, "libllama.so.0"))
    os.symlink("libllama.so.0", os.path.join(d, "libllama.so"))
    os.makedirs(os.path.join(d, "glibc-hwcaps", "x86-64-v3"))
    server = os.path.join(d, "llama-server")
    links, digest, problems = prod.install_links(server)
    show("producer install_links() links", links)
    show("producer install_links() digest is hex", bool(digest))
    show("producer install_links() problems", problems)
    setup_error = "install-tree-unpinnable:" + ";".join(problems[:8])
    show("producer SetupError string", setup_error)
    tree = {"llama-server": "x", "libllama.so.0.7.0": "y"}
    show("gate link_chain_problem per link",
         {n: gate.link_chain_problem(n, links, tree)
          for n in sorted(links)})
    # Non-producer state: link map is empty AND the directory cannot be
    # listed. The producer returns digest None together with a problem.
    missing = os.path.join(d, "missing", "llama-server")
    show("producer install_links() on unlistable dir",
         prod.install_links(missing))

show("producer _outcome_exit([], None)", prod._outcome_exit([], None))
show("producer _outcome_exit([], 'install-tree-unpinnable:x')",
     prod._outcome_exit([], "install-tree-unpinnable:x"))
show("producer _outcome_exit([pass], None)",
     prod._outcome_exit([{"passed": True}], None))
show("producer _outcome_exit([not-evaluated], None)",
     prod._outcome_exit([{"passed": None}], None))
