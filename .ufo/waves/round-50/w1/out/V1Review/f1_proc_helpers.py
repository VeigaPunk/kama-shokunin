#!/usr/bin/env python3
"""V1Review fixture F1: gguf_tokens, stat_fields, environ_keys+INVOKER, listen_inodes,
descendants/descends_from/pid_alive. Read-only on the lane; writes only under its own
scratch tree. Every spawned process is killed before exit."""
import importlib.util, os, sys, io, struct, socket, subprocess, time, signal, ctypes

S = "/fast/scratch/hyaku/kama-r50/V1Review/f1"
os.makedirs(S, exist_ok=True)
os.environ["TMPDIR"] = S
spec = importlib.util.spec_from_file_location(
    "c1", "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round50-replay-bind-audit.py")
c1 = importlib.util.module_from_spec(spec); spec.loader.exec_module(c1)

def gguf_build(version=3, tokens=(b"a", b"\xe2\x96\x81b"), tokens_etype=8, tokens_type=9,
               truncate=None, extra_kv=()):
    buf = io.BytesIO()
    buf.write(b"GGUF"); buf.write(struct.pack("<I", version))
    kvs = [("tokenizer.ggml.tokens", tokens_type,
            tokens if tokens_type == 8 else ("arr", tokens_etype, tokens))]
    kvs += list(extra_kv)
    buf.write(struct.pack("<Q", 0)); buf.write(struct.pack("<Q", len(kvs)))
    for key, t, val in kvs:
        kb = key.encode() if isinstance(key, str) else key
        buf.write(struct.pack("<Q", len(kb))); buf.write(kb)
        if t == 9:
            _, et, items = val
            buf.write(struct.pack("<I", 9)); buf.write(struct.pack("<IQ", et, len(items)))
            for s in items:
                buf.write(struct.pack("<Q", len(s))); buf.write(s)
        elif t == 8:
            if isinstance(val, tuple): val = val[-1]
            buf.write(struct.pack("<I", 8)); buf.write(struct.pack("<Q", len(val))); buf.write(val)
    data = buf.getvalue()
    return data[:truncate] if truncate else data

def write_try(data, name):
    p = os.path.join(S, name); open(p, "wb").write(data); return p

def expect_err(label, fn):
    try:
        print(label, "-> returned", fn())
    except Exception as e:
        print(label, "->", type(e).__name__, e)

print("== gguf_tokens (lines 149-196) ==")
print("v3 well-formed ->", c1.gguf_tokens(write_try(gguf_build(), "v3.gguf")))
expect_err("v1", lambda: c1.gguf_tokens(write_try(gguf_build(version=1), "v1.gguf")))
print("v4 (forward-compat, only ver<2 rejected at line 156) ->",
      c1.gguf_tokens(write_try(gguf_build(version=4), "v4.gguf")))
expect_err("tokens etype=5 (int32 array)",
           lambda: c1.gguf_tokens(write_try(gguf_build(tokens_etype=5), "intarr.gguf")))
expect_err("tokens stored as string kv (t=8)",
           lambda: c1.gguf_tokens(write_try(gguf_build(tokens_type=8, tokens=b"notanarray"), "strval.gguf")))
expect_err("truncated header 12B",
           lambda: c1.gguf_tokens(write_try(gguf_build(truncate=12), "trunc12.gguf")))
print("tail-truncated (declared string len exceeds data) ->",
      c1.gguf_tokens(write_try(gguf_build()[:-2], "trunctail.gguf")),
      "(NO exception: silent short read)")
print("extra string kv ->", c1.gguf_tokens(
      write_try(gguf_build(extra_kv=[("general.architecture", 8, b"llama")]), "extra.gguf")))
expect_err("unknown value type 13",
           lambda: c1.gguf_tokens(write_try(gguf_build(extra_kv=[("mystery", 13, b"\x01\x02")]), "t13.gguf")))
expect_err("empty file", lambda: c1.gguf_tokens(write_try(b"", "empty.gguf")))
expect_err("bad magic", lambda: c1.gguf_tokens(write_try(b"NOTG" + b"\x03" + b"\x00" * 16, "bad.gguf")))

print("\n== stat_fields comm with ')' and space (lines 234-242) ==")
libc = ctypes.CDLL(None)
libc.prctl(15, b"a)b c)d")  # PR_SET_NAME
st = c1.stat_fields(os.getpid())
print("comm:", open("/proc/self/comm").read().strip(), "| stat_fields:", st,
      "| ppid ok:", st[1] == os.getppid())

print("\n== environ_keys + INVOKER -I isolation (lines 271-276, 114-115, 376-405) ==")
plant = os.path.join(S, "plant"); os.makedirs(plant, exist_ok=True)
marker = os.path.join(S, "marker.txt"); open(marker, "w").close()
open(os.path.join(plant, "sitecustomize.py"), "w").write(
    "import os, sys\nopen(%r, 'a').write('%%d %%r\\n' %% (os.getpid(), sys.argv[:2]))\n" % marker)
env = {"PATH": os.environ["PATH"], "PYTHONPATH": plant, "KAMA_R50_CANARY": "cafe1234"}
ch = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(6)"], env=env,
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1.5)
print("canary readable in child environ:", "KAMA_R50_CANARY" in c1.environ_keys(ch.pid))
print("marker after NON-isolated -c child (mechanism fires):", open(marker).read().splitlines())
open(marker, "w").close()
inv = subprocess.Popen([sys.executable, "-I", "-c", c1.INVOKER,
                        sys.executable, "-I", "-c", "import time; time.sleep(3)"],
                       env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print("invoker rc:", inv.wait(), "| marker after -I invoker chain (expect []):",
      open(marker).read().splitlines())
pid_max = int(open("/proc/sys/kernel/pid_max").read())
print("environ_keys(nonexistent pid) ->", c1.environ_keys(pid_max - 5))
ch.kill(); ch.wait()

print("\n== listen_inodes: state 0A, address set (lines 198-217) ==")
def listen_sock(fam, host):
    s = socket.socket(fam, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, 0)); s.listen(5); return s
s4 = listen_sock(socket.AF_INET, "127.0.0.1"); p4 = s4.getsockname()[1]
ino4 = os.readlink(f"/proc/{os.getpid()}/fd/{s4.fileno()}")[8:-1]
print("127.0.0.1 LISTEN found:", ino4 in c1.listen_inodes(p4), sorted(c1.listen_inodes(p4)))
s6 = listen_sock(socket.AF_INET6, "::1"); p6 = s6.getsockname()[1]
print("::1 LISTEN found:", sorted(c1.listen_inodes(p6)))
san = listen_sock(socket.AF_INET, "0.0.0.0"); pan = san.getsockname()[1]
print("0.0.0.0 LISTEN found (strict set, expect []):", sorted(c1.listen_inodes(pan)))
c = socket.create_connection(("127.0.0.1", p4))
ino_c = os.readlink(f"/proc/{os.getpid()}/fd/{c.fileno()}")[8:-1]
print("ESTABLISHED inode excluded:", ino_c not in c1.listen_inodes(p4),
      "| intersection with own fds nonempty:",
      bool(c1.listen_inodes(p4) & c1.pid_socket_inodes(os.getpid())))
print("wrong port -> []:", c1.listen_inodes(p4 + 1) == set())
c.close(); s4.close(); san.close(); s6.close()

print("\n== descendants / descends_from / pid_alive (lines 244-248, 279-306) ==")
kid = subprocess.Popen([sys.executable, "-c",
    "import subprocess, sys, time\n"
    "g1 = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(30)'])\n"
    "g2 = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(30)'])\n"
    "print(g1.pid, g2.pid, flush=True)\n"
    "time.sleep(30)\n"], stdout=subprocess.PIPE)
g1, g2 = map(int, kid.stdout.readline().split())
time.sleep(0.6)
d = c1.descendants(kid.pid)
print("descendants(kid) (root excluded by design, multi-child):", sorted(d),
      "| == {g1,g2}:", set(d) == {g1, g2})
print("descends_from(g1, kid):", c1.descends_from(g1, kid.pid),
      "| descends_from(kid, g1) reversed:", c1.descends_from(kid.pid, g1))
st_g1 = d[g1]
print("pid_alive(g1, own start):", c1.pid_alive(g1, st_g1),
      "| pid_alive(g1, wrong start):", c1.pid_alive(g1, st_g1 + 1000))
os.kill(g1, signal.SIGKILL)
time.sleep(0.8)
stf = c1.stat_fields(g1)
print("g1 state:", stf[0] if stf else None, "| pid_alive(zombie):", c1.pid_alive(g1),
      "| zombie in descendants:", g1 in c1.descendants(kid.pid))
os.kill(g2, signal.SIGKILL); time.sleep(0.3); kid.kill(); kid.wait(); time.sleep(0.3)
print("all reaped:", c1.stat_fields(g1) is None and c1.stat_fields(g2) is None
      and c1.stat_fields(kid.pid) is None)
print("F1 DONE")
