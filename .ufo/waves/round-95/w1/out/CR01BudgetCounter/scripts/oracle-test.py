import importlib.util, json, os, re, subprocess, sys
from pathlib import Path
OUT = Path(sys.argv[1]); S = Path(sys.argv[2])
spec = importlib.util.spec_from_file_location("rb95", OUT/".." / ".." / ".." / ".." / ".." / "tools" / "round95-router-budget.py")
# simpler: load by absolute path
spec = importlib.util.spec_from_file_location("rb95", "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round95-router-budget.py")
rb = importlib.util.module_from_spec(spec); spec.loader.exec_module(rb)
t = S/"probe-tests"
(t/"valid3.gguf").write_bytes(rb.gguf(3, 32, True))
(t/"ok.gguf").write_bytes(rb.gguf(1, 32, True))
(t/"slow.gguf").write_bytes(rb.gguf(600_000, 1, False))
unread = t/"unreadable.gguf"; unread.write_bytes(rb.gguf(1, 32, True)); os.chmod(unread, 0)
body = {"data": [{"id": "good", "status": {"value": "unloaded",
        "args": [str(t/"ok.gguf"), "-m", "<PATH>"]}}]}
def pycode(probe):
    s = Path(probe).read_text()
    m = "ROUTER_PY=$(cat <<'PY'\n"; i = s.index(m)+len(m); j = s.index("\nPY\n", i)
    return s[i:j]
def run(probe, path):
    b = json.loads(json.dumps(body)); b["data"][0]["status"]["args"][2] = str(path)
    bf = t/"body.json"; bf.write_text(json.dumps(b))
    p = subprocess.run([sys.executable, "-c", pycode(probe), str(bf), "files", "0"],
                       capture_output=True, text=True)
    return p.stdout.strip() or f"<no output rc={p.returncode} err={p.stderr.strip()[:120]}>"
cases = [("M1", str(OUT/"probes/probe-M1.sh")),
         ("F3", str(OUT/"probes/probe-F3.sh")),
         ("F6", str(OUT/"probes/probe-F6.sh")),
         ("F7", str(OUT/"probes/probe-F7.sh"))]
tests = [("valid3(3 tensors,data present)", t/"valid3.gguf"),
         ("ok(1 tensor)", t/"ok.gguf"),
         ("slow(600k tensors)", t/"slow.gguf"),
         ("unreadable(mode 000)", unread)]
for label, path in tests:
    print(f"{label:38s}", " ".join(f"{name}={run(probe, path)}" for name, probe in cases))
print("oracle_fixture_class:", {p.name: rb.fixture_class(p) for _, p in tests})
os.chmod(unread, 0o644)
