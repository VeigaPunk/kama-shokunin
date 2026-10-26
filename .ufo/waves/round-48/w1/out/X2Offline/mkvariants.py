#!/usr/bin/env python3
"""Create the six (plus one) receipt-1.json variants for the X2Offline v5 failure-mode probe.

Every variant is a copy of the lane's .ufo/waves/round-48/c2/live/receipt-1.json with
exactly the documented mutation; nothing else changes.
"""
import copy
import hashlib
import json
import os

SRC = "/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/c2/live/receipt-1.json"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cases")
COMMIT = "499bc8821c6b12b4e53c5bffcb21ec206f212d81"
OTHER = "e2d5caf5587262b440f392e36f06594da5afa1f6"  # real, e2d5caf..., older main revision
ASSET = ("https://github.com/ggml-org/llama.cpp/releases/download/b11909/"
         "llama-b11909-bin-ubuntu-x64.tar.gz")
MODEL = ("https://huggingface.co/ggml-org/models-moved/resolve/"
         + COMMIT + "/tinyllamas/stories260K.gguf")

base = json.load(open(SRC))
assert base["schema"] == "kama-llamacpp-live/v5"
assert base["provenance"]["model"]["commit"] == COMMIT
assert base["provenance"]["model"]["url"] == MODEL
assert base["provenance"]["server"]["asset_url"] == ASSET

cases = {}


def add(name, mutate):
    rec = copy.deepcopy(base)
    mutate(rec)
    cases[name] = rec


def a(rec):
    rec["provenance"]["server"]["asset_url"] = (
        "https://github.com/ggml-org/llama.cpp/releases/download/b11909/"
        "llama-b11909-bin-ubuntu-x64-missing.tar.gz")  # 404 on github.com


def b(rec):
    rec["provenance"]["model"]["commit"] = OTHER  # URL keeps /resolve/499bc882.../


def c(rec):
    rec["provenance"]["model"]["url"] = (
        "https://127.0.0.1:9/ggml-org/models-moved/resolve/" + COMMIT
        + "/tinyllamas/stories260K.gguf")  # unreachable loopback host


def e(rec):
    del rec["provenance"]["verified"]


def f(rec):
    # schema v5, v4-shaped provenance: no verified block, no model.commit
    rec["provenance"] = {"server": {"asset_url": base["provenance"]["server"]["asset_url"],
                                    "asset_sha256": base["provenance"]["server"]["asset_sha256"],
                                    "member": base["provenance"]["server"]["member"]},
                         "model": {"url": base["provenance"]["model"]["url"],
                                   "sha256": base["provenance"]["model"]["sha256"]}}


def g(rec):
    rec["provenance"]["verified"]["member_sha256"] = "0" * 64  # forged record-time digest


add("a-asset-404", a)
add("b-commit-other-rev", b)
add("c-unreachable-host", c)
add("d-timeout-1", lambda rec: None)   # run with --timeout 1
add("e-no-verified", e)
add("f-v5-v4provenance", f)
add("g-forged-verified-member", g)

os.makedirs(OUT, exist_ok=True)
for name, rec in cases.items():
    d = os.path.join(OUT, name)
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, "receipt.json")
    with open(p, "w") as fh:
        json.dump(rec, fh, indent=1)
    raw = open(p, "rb").read()
    print(name, hashlib.sha256(raw).hexdigest())
print("src", hashlib.sha256(open(SRC, "rb").read()).hexdigest())
