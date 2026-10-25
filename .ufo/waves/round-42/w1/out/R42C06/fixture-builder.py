#!/usr/bin/env python3
"""Build a sourceless fixture repo: fabricated 'evidence copies', no upstream fetch.

Stage A: entry stub + README line only  -> expect coverage=1
Stage B: fabricated copies + entry + rows + gate + scratch -> expect met=True
"""
import hashlib, os, subprocess, sys, tempfile

CLONE = "/fast/scratch/kama-r42/clone"
BASE = "0b606b03bf0b2a87b791aa537f6c72c941624cf0"
ENTRY = "corpus/knowledge/context-capacity-engine-sides.md"
LESSON = "corpus/lessons/round-42.md"
VLLM = ".ufo/waves/round-42/c3/vllm-v0.32.0-kv_cache_utils.py"
LC = ".ufo/waves/round-42/c3/llamacpp-704366d7-server-models.cpp"
URL1 = "https://raw.githubusercontent.com/vllm-project/vllm/v0.32.0/vllm/v1/core/kv_cache_utils.py"
URL2 = "https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-models.cpp"

d = tempfile.mkdtemp(prefix="r42c06-fx-", dir="/fast/scratch/kama-r42/seats")


def g(*a, **kw):
    return subprocess.run(["git", "-C", d, *a], check=True, capture_output=True, text=True, **kw)


g("init", "-q")
top = g("rev-parse", "--show-toplevel").stdout.strip()
assert os.path.realpath(top) == os.path.realpath(d), (top, d)
g("fetch", "-q", CLONE, BASE)
g("reset", "-q", "--hard", "FETCH_HEAD")
g("config", "user.name", "fixture")
g("config", "user.email", "fixture@example.invalid")

# ---- Stage A: coverage only -------------------------------------------------
open(os.path.join(d, ENTRY), "w").write("stub: no source, no copies\n")
with open(os.path.join(d, "corpus/README.md"), "a") as f:
    f.write(f"\n| `{ENTRY}` | fabricated stub | 42 |\n")
g("add", "-A")
g("commit", "-q", "-m", "fixture A: entry stub + README line, no sources")
print("STAGE_A_REV", g("rev-parse", "HEAD").stdout.strip())

# ---- Stage B: fabricated copies, entry, rows, gate, scratch ----------------
vllm = ["# fabricated copy, not the upstream file"] * 9
vllm.append("num_blocks = available_memory // bytes_per_block")          # line 10 (A1)
vllm += ["# filler"] * 9
vllm.append('log("%s KV cache size: %s tokens")')                        # line 20 (A2)
lc = ["// fabricated copy, not the upstream file"] * 4
lc.append('model_info["context_length"] = meta.n_ctx_train;')             # line 5 (A3)
lc.append("// router listing adds context_length from meta.n_ctx_train")
vllm_t = "\n".join(vllm) + "\n"
lc_t = "\n".join(lc) + "\n"
for rel, txt in ((VLLM, vllm_t), (LC, lc_t)):
    p = os.path.join(d, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w").write(txt)
d1 = hashlib.sha256(vllm_t.encode()).hexdigest()
d2 = hashlib.sha256(lc_t.encode()).hexdigest()

entry = f"""source: S478 — vLLM kv_cache_utils.py (fabricated) — {URL1}; S479 — llama.cpp server-models.cpp (fabricated) — {URL2}
verified-at: 2026-10-25 — fixture only; no fetch was made
recheck: on-release

# Fabricated engine sides

- `num_blocks = available_memory // bytes_per_block` at `kv_cache_utils.py:10`.
- the capacity log literal at `kv_cache_utils.py:20`.
- `model_info["context_length"] = meta.n_ctx_train;` at `server-models.cpp:5`.
- `max_model_len` occurs 0 times in the fabricated llama.cpp copy.
"""
open(os.path.join(d, ENTRY), "w").write(entry)

lesson = f"""# round-42 fixture lesson

## Gate

- **S478** — {URL1}, accessed 2026-10-25, quote "num_blocks = available_memory // bytes_per_block".
- **S479** — {URL2}, accessed 2026-10-25, quote "router listing adds context_length from meta.n_ctx_train".
"""
open(os.path.join(d, LESSON), "w").write(lesson)

rows = (
    f"| S478 | fabricated vLLM source — {URL1} | code | A | fabricated scope | "
    f"fabricated anchor; raw SHA-256 {d1} | fabricated teaches | mined | 2026-10-25 | on-release | {ENTRY} |\n"
    f"| S479 | fabricated llama.cpp source — {URL2} | code | A | fabricated scope | "
    f"fabricated anchor; raw SHA-256 {d2} | fabricated teaches | mined | 2026-10-25 | on-release | {ENTRY} |\n"
)
sp = os.path.join(d, "corpus/SOURCES.md")
lines = open(sp).read().split("\n")
last = max(i for i, l in enumerate(lines) if l.startswith("| S"))
lines.insert(last + 1, rows.rstrip("\n"))
open(sp, "w").write("\n".join(lines))

for name, body in (("reg-ids", "S001\n"), ("staged-ids", "S330\n"), ("collisions", ""),
                   ("quarantine-slice", " S200   `payload-absent` \n")):
    p = os.path.join(d, ".ufo/waves/round-42/assimilation", name)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w").write(body)

g("add", "-A")
g("commit", "-q", "-m", "fixture B: fabricated copies, entry, rows, gate, scratch")
print("STAGE_B_REV", g("rev-parse", "HEAD").stdout.strip())
print("FIXTURE", d)
print("copy_sha_vllm", d1)
print("copy_sha_lc", d2)
