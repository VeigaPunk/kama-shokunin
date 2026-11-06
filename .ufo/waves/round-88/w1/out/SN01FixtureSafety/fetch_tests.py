"""Safety tests for tools/fetch-pinned-model.py (bytes at f77d2ae). Never touches the real cache."""
import hashlib, http.server, importlib.util, os, pathlib, shutil, signal, socket, subprocess, sys, threading, time

S = pathlib.Path("/fast/scratch/hyaku/kama-r88/SN01FixtureSafety")
TOOL = S / "fetch.py"
PIN = "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"
GOOD = pathlib.Path.home() / ".cache/kama-shokunin/models/stories260K.gguf"
BAD = b"definitely not the pinned model\n" * 40


def sha(p):
    return hashlib.file_digest(open(p, "rb"), "sha256").hexdigest()


class H(http.server.BaseHTTPRequestHandler):
    slow = False

    def do_GET(self):
        if self.path == "/good":
            body = GOOD.read_bytes()
        elif self.path == "/bad":
            body = BAD
        elif self.path == "/redir":
            self.send_response(302)
            self.send_header("Location", f"http://127.0.0.2:{self.server.server_port}/good")
            self.end_headers()
            return
        elif self.path == "/slow":
            self.send_response(200)
            self.send_header("Content-Length", str(10_000_000))
            self.end_headers()
            for _ in range(200):
                self.wfile.write(b"x" * 10_000)
                self.wfile.flush()
                time.sleep(0.05)
            return
        else:
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


srv = http.server.ThreadingHTTPServer(("0.0.0.0", 0), H)
threading.Thread(target=srv.serve_forever, daemon=True).start()
P = srv.server_port
URL = f"http://127.0.0.1:{P}"
print("server port", P, flush=True)


def run(dest, url, tag, extra_env=None, timeout=120):
    env = dict(os.environ, no_proxy="*", NO_PROXY="*")
    env.pop("http_proxy", None)
    env.pop("HTTP_PROXY", None)
    if extra_env:
        env.update(extra_env)
    r = subprocess.run([sys.executable, str(TOOL), "--dest", str(dest), "--url", url],
                       capture_output=True, text=True, timeout=timeout, env=env)
    print(f"[{tag}] exit={r.returncode} out={r.stdout.strip()!r} err={r.stderr.strip()[:200]!r}")
    return r


def case(name):
    d = S / "ft" / name
    shutil.rmtree(d, ignore_errors=True)
    d.mkdir(parents=True)
    return d


# F1 present, correct digest
d = case("f1-present")
(d / "m.gguf").write_bytes(GOOD.read_bytes())
before = (d / "m.gguf").stat().st_mtime_ns
r = run(d / "m.gguf", f"{URL}/good", "F1-present-correct")
print("F1 mtime unchanged:", (d / "m.gguf").stat().st_mtime_ns == before,
      "digest ok:", sha(d / "m.gguf") == PIN)

# F2 present, wrong digest -> refuse, never overwrite
d = case("f2-wrong")
(d / "m.gguf").write_bytes(BAD)
h0 = sha(d / "m.gguf")
r = run(d / "m.gguf", f"{URL}/good", "F2-present-wrong")
h1 = sha(d / "m.gguf")
print("F2 file untouched:", h0 == h1, "part created:", (d / "m.gguf.part").exists())

# F3 download of wrong bytes -> discard, no dest, no part
d = case("f3-bad-download")
r = run(d / "m.gguf", f"{URL}/bad", "F3-bad-download")
print("F3 dest absent:", not (d / "m.gguf").exists(), "part absent:", not (d / "m.gguf.part").exists(),
      "leftovers:", sorted(p.name for p in d.iterdir()))

# F4 .part is a symlink to a victim file -> write follows the link
d = case("f4-part-symlink")
victim = d / "victim.txt"
victim.write_text("ORIGINAL CONTENT\n")
os.symlink(victim, d / "m.gguf.part")
r = run(d / "m.gguf", f"{URL}/bad", "F4-part-symlink")
print("F4 victim overwritten:", victim.read_text()[:40] != "ORIGINAL CONTENT\n",
      "victim bytes:", victim.stat().st_size, "victim still exists:", victim.exists(),
      "part path exists:", (d / "m.gguf.part").exists(), "dest:", (d / "m.gguf").exists())

# F4b same but the download is the GOOD bytes: symlink target gets the model
d = case("f4b-part-symlink-good")
victim = d / "victim.txt"
victim.write_text("ORIGINAL CONTENT\n")
os.symlink(victim, d / "m.gguf.part")
r = run(d / "m.gguf", f"{URL}/good", "F4b-part-symlink-good")
print("F4b victim now model:", victim.exists() and victim.stat().st_size == GOOD.stat().st_size,
      "dest is symlink:", (d / "m.gguf").is_symlink() if (d / "m.gguf").exists() else "absent",
      "dest digest:", sha(d / "m.gguf") if (d / "m.gguf").exists() else None)

# F5 redirect to a different host (127.0.0.2) is followed
d = case("f5-redirect")
r = run(d / "m.gguf", f"{URL}/redir", "F5-redirect-other-host")
print("F5 fetched:", (d / "m.gguf").exists() and sha(d / "m.gguf") == PIN)

# F6 SIGINT mid-download -> .part leftover?
d = case("f6-sigint")
env = dict(os.environ, no_proxy="*", NO_PROXY="*")
pr = subprocess.Popen([sys.executable, str(TOOL), "--dest", str(d / "m.gguf"), "--url", f"{URL}/slow"],
                      stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env)
time.sleep(2)
print("F6 part exists mid-flight:", (d / "m.gguf.part").exists(),
      "size:", (d / "m.gguf.part").stat().st_size if (d / "m.gguf.part").exists() else 0)
pr.send_signal(signal.SIGINT)
out = pr.communicate(timeout=30)[0]
print("F6 exit:", pr.returncode, "stdout:", out.strip()[:120],
      "part leftover after SIGINT:", (d / "m.gguf.part").exists(),
      "dest:", (d / "m.gguf").exists())

# F7 dest is a symlink to wrong content
d = case("f7-dest-symlink-wrong")
target = d / "elsewhere.bin"
target.write_bytes(BAD)
os.symlink(target, d / "m.gguf")
r = run(d / "m.gguf", f"{URL}/good", "F7-dest-symlink-wrong")
print("F7 refused:", r.returncode == 1, "target untouched:", sha(target) != PIN,
      "still symlink:", (d / "m.gguf").is_symlink())

# F8 dest symlink to the correct content
d = case("f8-dest-symlink-good")
target = d / "goodcopy.bin"
target.write_bytes(GOOD.read_bytes())
os.symlink(target, d / "m.gguf")
r = run(d / "m.gguf", f"{URL}/good", "F8-dest-symlink-good")
print("F8 action present:", "action=present" in r.stdout)

# F9 missing parent dir
d = S / "ft" / "f9-nested" / "deep"
shutil.rmtree(S / "ft" / "f9-nested", ignore_errors=True)
r = run(d / "m.gguf", f"{URL}/good", "F9-missing-parent")
print("F9 created+fetched:", (d / "m.gguf").exists() and sha(d / "m.gguf") == PIN)

# F10 default --dest is the real cache (code read only): confirm it is outside the lane
print("F10 default dest const:", [l.strip() for l in TOOL.read_text().splitlines() if l.startswith("DEST")])
