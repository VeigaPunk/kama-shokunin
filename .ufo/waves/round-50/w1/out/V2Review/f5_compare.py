#!/usr/bin/env python3
"""F5: the model-mapping requirement applies to RERUNS only.

An ORIGINAL receipt never carries model_mapping (round-48 v5 receipts predate it).
compare() must stay silent about the rerun's extra key (else every replay of an
old receipt fails), and the replay-level check must fire exactly when the RERUN
lacks/mismaps the record. Emulates both from the imported module.
"""
import importlib.util, sys

REPLAY = "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-live-replay.py"
spec = importlib.util.spec_from_file_location("klr_f5", REPLAY)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

SSHA, MSHA = "a" * 64, "b" * 64
CHECKS = [{"id": "health_ready", "passed": True, "evaluated": True}]

def rec(mapping=None):
    r = {"schema": "kama-llamacpp-live/v5", "outcome": "pass",
         "server": {"sha256": SSHA}, "model": {"sha256": MSHA}, "checks": CHECKS,
         "provenance": {"model": {"commit": "c" * 40},
                        "verified": {"at": "record", "archive_sha256": "1" * 64,
                                     "member_sha256": SSHA, "model_sha256": MSHA}}}
    if mapping is not None:
        r["model_mapping"] = mapping
    return r

good = {"mapped": True, "path": "/x/m.gguf", "dev": "08:02", "inode": "123",
        "size": 1048576, "sha256": MSHA}
bad_sha = dict(good, sha256="c" * 64)
absent = {"mapped": False, "reason": "server-not-running"}

# original has NO model_mapping; rerun has a good one -> compare silent
print("orig-without vs rerun-good:", m.compare(rec(None), rec(good)))
assert m.compare(rec(None), rec(good)) == []
# rerun lacks the record: compare still silent (it is a projection-agnostic key)...
print("orig-without vs rerun-absent:", m.compare(rec(None), rec(absent)))
assert m.compare(rec(None), rec(absent)) == []
# ...but the replay-level check (replay() lines ~341-347) fires. Emulate it verbatim:
def replay_mapping_check(rr, model_sha):
    mm = rr.get("model_mapping")
    if not isinstance(mm, dict) or mm.get("mapped") is not True:
        return f"model-mapping:{mm.get('reason') if isinstance(mm, dict) else 'absent'}"
    if mm.get("sha256") != model_sha:
        return f"model-mapping:sha256:{model_sha}->{mm.get('sha256')}"
    return None

print("check(good) ->", replay_mapping_check(rec(good), MSHA))
print("check(bad_sha) ->", replay_mapping_check(rec(bad_sha), MSHA))
print("check(absent) ->", replay_mapping_check(rec(absent), MSHA))
print("check(None) ->", replay_mapping_check(rec(None), MSHA))
assert replay_mapping_check(rec(good), MSHA) is None
assert replay_mapping_check(rec(bad_sha), MSHA).startswith("model-mapping:sha256:")
assert replay_mapping_check(rec(absent), MSHA) == "model-mapping:server-not-running"
assert replay_mapping_check(rec(None), MSHA) == "model-mapping:absent"
print("F5 PASS: requirement is rerun-only; originals without model_mapping replay fine")
