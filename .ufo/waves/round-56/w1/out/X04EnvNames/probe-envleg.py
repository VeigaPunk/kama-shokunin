#!/usr/bin/env python3
"""X04EnvNames: live sleep child carrying LD_AUDIT -> enumerate env_leg of both counters.

No llama-server is started: the child is /bin/sleep and the counters are imported as
modules, so only their env_leg (environ name read) leg executes.
"""
import importlib.util
import json
import os
import subprocess
import time

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
OLD = f"{LANE}/tools/round54-replay-code-audit.py"   # round-55 red baseline counter
NEW = f"{LANE}/tools/round56-replay-code-audit.py"   # round-56 counter


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MODS = {
    "round55_counter": (OLD, load(OLD, "x04_r55")),
    "round56_counter": (NEW, load(NEW, "x04_r56")),
}


def raw_environ(pid):
    with open(f"/proc/{pid}/environ", "rb") as fh:
        blob = fh.read()
    entries = [e for e in blob.split(b"\0") if e]
    names = [e.split(b"=", 1)[0].decode("utf-8", "replace") for e in entries]
    return len(blob), names, entries


def spawn(extra):
    env = dict(os.environ)
    for k in ("LD_AUDIT", "LD_AUDITX", "KAMA_X04", "ld_audit"):
        env.pop(k, None)
    env.update(extra)
    return subprocess.Popen(["sleep", "20"], env=env)


def probe(label, extra):
    p = spawn(extra)
    try:
        time.sleep(0.05)
        size, names, entries = raw_environ(p.pid)
        out = {
            "case": label,
            "pid": p.pid,
            "environ_bytes": size,
            "environ_name_count": len(names),
            "audit_shaped_names": sorted(n for n in names if "AUDIT" in n.upper()),
            "raw_ld_audit_entry": next(
                (e.decode("utf-8", "replace") for e in entries
                 if e.split(b"=", 1)[0] == b"LD_AUDIT"), None),
        }
        for mname, (path, mod) in MODS.items():
            probs = []
            keys = mod.env_leg(p.pid, probs)
            out[mname] = {
                "counter": path,
                "keys_is_none": keys is None,
                "key_count": None if keys is None else len(keys),
                "keys_equal_raw_names": keys == sorted(names),
                "ld_audit_in_keys": None if keys is None else "LD_AUDIT" in keys,
                "problems": probs,
            }
        return out
    finally:
        p.terminate()
        p.wait()


CASES = [
    ("audit-set", {"LD_AUDIT": "/usr/lib/libexpat.so.1"}),
    ("audit-empty-value", {"LD_AUDIT": ""}),
    ("nearmiss-name-LD_AUDITX", {"LD_AUDITX": "/usr/lib/libexpat.so.1"}),
    ("name-in-value-KAMA_X04", {"KAMA_X04": "LD_AUDIT"}),
    ("lowercase-ld_audit", {"ld_audit": "/usr/lib/libexpat.so.1"}),
    ("clean-child", {}),
]


def main():
    results = [probe(*c) for c in CASES]
    for label, pid in (("nonexistent-pid", 999999), ("pid1-foreign", 1)):
        entry = {"case": label, "pid": pid}
        for mname, (path, mod) in MODS.items():
            probs = []
            keys = mod.env_leg(pid, probs)
            entry[mname] = {"counter": path, "keys_is_none": keys is None,
                            "key_count": None if keys is None else len(keys),
                            "problems": probs}
        results.append(entry)
    print(json.dumps(results, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
