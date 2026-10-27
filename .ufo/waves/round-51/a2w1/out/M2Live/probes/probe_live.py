#!/usr/bin/env python3
"""Proposed killing unit cases for server_exe() (M2Live).

Usage: probe_live.py <dir containing tools/kama-llamacpp-live.py> [...]
Loads the live tool from the given tree and runs five contract probes.
Exits 0 iff all probes pass; prints one line per probe.
"""
import importlib.util, os, stat, sys, hashlib

CHECKS = []

def check(fn):
    CHECKS.append(fn)
    return fn

def load(tree):
    path = os.path.join(tree, "tools", "kama-llamacpp-live.py")
    spec = importlib.util.spec_from_file_location("m_" + os.path.basename(tree), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

@check
def path_is_readlink(mod):
    """server_exe().path is the readlink(2) text and opened/sha/dev are the real image."""
    r = mod.server_exe(os.getpid())
    exe = f"/proc/{os.getpid()}/exe"
    assert r.get("opened") is True, r
    assert r.get("path") == os.readlink(exe), (r.get("path"), os.readlink(exe))
    with open(exe, "rb") as fh:
        want = hashlib.sha256(fh.read()).hexdigest()
    assert r.get("sha256") == want, r
    st = os.stat(exe)
    assert r.get("dev") == "%02x:%02x" % (os.major(st.st_dev), os.minor(st.st_dev)), r
    assert r.get("inode") == str(st.st_ino), r

@check
def open_targets_proc_link(mod):
    """The file is opened through /proc/<pid>/exe itself, not through the readlink text."""
    seen = []
    real_open = os.open
    def spy(path, *a, **k):
        seen.append(path)
        return real_open(path, *a, **k)
    os.open = spy
    try:
        r = mod.server_exe(os.getpid())
    finally:
        os.open = real_open
    assert r.get("opened") is True, r
    assert seen and isinstance(seen[0], str) and seen[0].startswith("/proc/") \
        and seen[0].endswith("/exe"), seen

@check
def never_stats_the_path(mod):
    """Observation comes from the open descriptor; os.stat() on the path is never consulted."""
    real_stat = os.stat
    def bomb(*a, **k):
        raise AssertionError("server_exe consulted os.stat()")
    os.stat = bomb
    try:
        r = mod.server_exe(os.getpid())
    finally:
        os.stat = real_stat
    assert r.get("opened") is True, r

@check
def fifo_mode_refused(mod):
    """A non-regular fstat mode is refused as exe-not-a-regular-file."""
    real_fstat = os.fstat
    def fifo(fd):
        st = real_fstat(fd)
        return os.stat_result((stat.S_IFIFO | 0o600, st.st_ino, st.st_dev, st.st_nlink,
                               st.st_uid, st.st_gid, st.st_size, st.st_atime,
                               st.st_mtime, st.st_ctime))
    os.fstat = fifo
    try:
        r = mod.server_exe(os.getpid())
    finally:
        os.fstat = real_fstat
    assert r.get("opened") is False and r.get("reason") == "exe-not-a-regular-file", r

@check
def short_read_reported(mod):
    """A descriptor that stops early must not be reported as a full hash."""
    real_read = os.read
    state = {"n": 0}
    def short(fd, n):
        state["n"] += 1
        chunk = real_read(fd, n)
        if state["n"] == 1 and chunk:
            return chunk[:-1]
        return chunk
    os.read = short
    try:
        r = mod.server_exe(os.getpid())
    finally:
        os.read = real_read
    assert r.get("opened") is False and r.get("reason") == "exe-shrank-while-hashed", r

def main():
    trees = sys.argv[1:]
    for tree in trees:
        mod = load(tree)
        bad = []
        for fn in CHECKS:
            try:
                fn(mod)
                print(f"{os.path.basename(tree)}: {fn.__name__}: pass")
            except AssertionError as exc:
                bad.append(fn.__name__)
                print(f"{os.path.basename(tree)}: {fn.__name__}: FAIL {exc}")
        print(f"{os.path.basename(tree)}: {'ok' if not bad else 'killed-by ' + ','.join(bad)}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
