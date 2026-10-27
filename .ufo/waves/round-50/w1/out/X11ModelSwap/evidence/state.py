#!/usr/bin/env python3
"""Observe a held llama-server's model identity and run the frozen code's own checks.

argv: <pid> <model-path> <label>
Prints one JSON object: the raw /proc/<pid>/maps rows naming any file mapping of the
GGUF directory, /proc/<pid>/cmdline, /proc/<pid>/fd links to the model, stat() of the
path, sha256 of the path, then
  live_model_mapping   tools/kama-llamacpp-live.py model_mapping(pid, path)   [frozen]
  counter_mapped_model tools/round50-replay-bind-audit.py mapped_model(pid, probs) [frozen]
Both modules are imported unmodified from the lane clone.
"""
import hashlib, importlib.util, json, os, stat, sys

LANE = "/fast/scratch/hyaku/kama-r50/X11ModelSwap/lane"


def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(LANE, rel))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


live = load("kama_live", "tools/kama-llamacpp-live.py")
counter = load("r50c1", "tools/round50-replay-bind-audit.py")


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def main():
    pid = int(sys.argv[1]); path = sys.argv[2]; label = sys.argv[3]
    out = {"label": label, "pid": pid, "model_path": path}
    # raw maps rows that name a path in the model's own directory
    d = os.path.dirname(path)
    rows = []
    with open(f"/proc/{pid}/maps") as fh:
        for row in fh.read().splitlines():
            f = row.split(None, 5)
            if len(f) == 6 and f[5].startswith(d):
                rows.append({"addr": f[0], "perm": f[1], "offset": f[2],
                             "dev": f[3], "inode": f[4], "pathname": f[5]})
    # distinct mapping identity + count/spans
    ident = {}
    for r in rows:
        k = (r["dev"], r["inode"], r["pathname"])
        e = ident.setdefault(k, {"rows": 0, "lo": r["addr"].split("-")[0], "hi": r["addr"].split("-")[1]})
        e["rows"] += 1
        e["hi"] = r["addr"].split("-")[1]
        e["lo"] = min(e["lo"], r["addr"].split("-")[0], key=lambda x: int(x, 16))
    out["maps_identities"] = [{"dev": k[0], "inode": k[1], "pathname": k[2], "rows": v["rows"],
                               "first": v["lo"], "last": v["hi"]} for k, v in ident.items()]
    out["maps_rows_naming_dir"] = len(rows)
    with open(f"/proc/{pid}/cmdline", "rb") as fh:
        raw = fh.read()
    out["cmdline"] = [x.decode("utf-8", "replace") for x in raw.split(b"\0") if x]
    fds = {}
    for fd in sorted(os.listdir(f"/proc/{pid}/fd"), key=lambda s: int(s)):
        try:
            tgt = os.readlink(f"/proc/{pid}/fd/{fd}")
        except OSError:
            continue
        fds[fd] = tgt
    out["fd_links_model"] = {k: v for k, v in fds.items() if v.startswith(d)}
    out["fd_links_model_deleted"] = {k: v for k, v in fds.items() if d in v}
    out["fd_total"] = len(fds)
    try:
        st = os.stat(path)
        out["path_stat"] = {"dev": "%02x:%02x" % (os.major(st.st_dev), os.minor(st.st_dev)),
                            "inode": str(st.st_ino), "size": st.st_size,
                            "mode": oct(stat.S_IMODE(st.st_mode)), "nlink": st.st_nlink}
    except OSError as exc:
        out["path_stat"] = {"error": exc.strerror}
    try:
        out["path_sha256"] = sha(path)
    except OSError as exc:
        out["path_sha256"] = {"error": exc.strerror}
    # frozen code, unmodified
    out["live_model_mapping"] = live.model_mapping(pid, path)
    probs = []
    out["counter_mapped_model"] = counter.mapped_model(pid, probs)
    out["counter_mapped_probs"] = probs
    out["counter_MODEL_SHA"] = counter.MODEL_SHA
    out["live_MAPPED_EXPECT"] = "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"
    print(json.dumps(out, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
