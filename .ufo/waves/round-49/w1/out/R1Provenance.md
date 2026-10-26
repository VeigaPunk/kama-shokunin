# R1Provenance — C1 frozen constants vs outside

Verdict: PASS — all four C1 references (SERVER_SHA, MODEL_SHA, README_COMMIT, README bytes) match the outside world exactly; nothing stale in the counter's frozen constants.

## Evidence

Counter constants (tools/round49-replay-witness-audit.py:97-104):
- `SERVER_SHA = "35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0"`
- `MODEL_COMMIT = "499bc8821c6b12b4e53c5bffcb21ec206f212d81"`, `MODEL_URL = https://huggingface.co/ggml-org/models-moved/resolve/<commit>/tinyllamas/stories260K.gguf`, `MODEL_SHA = "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"`
- `README_COMMIT = "caa8191df159f764fb0160e3d2fc6be008948aee"`

### 1. SERVER_SHA — release asset member hash (PASS)
- Asset: `https://github.com/ggml-org/llama.cpp/releases/download/b11909/llama-b11909-bin-ubuntu-x64.tar.gz`
- Tarball sha256 (file: `llama-b11909-bin-ubuntu-x64.tar.gz`, 22,475,032 bytes):
  `bf94332a3001f3ee0b032cda37259f68460e28732ef9a579bfb1b918197e695b` — matches the expected `bf94332a…` prefix.
- Extracted member `llama-b11909/llama-server` (17,864 bytes, mode 0755) sha256:
  `35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0` — **equals** frozen `SERVER_SHA`.

### 2. MODEL_SHA — pinned URL digest (PASS)
- Downloaded `https://huggingface.co/ggml-org/models-moved/resolve/499bc8821c6b12b4e53c5bffcb21ec206f212d81/tinyllamas/stories260K.gguf` (1,185,376 bytes).
- sha256: `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` — **equals** frozen `MODEL_SHA`.

### 3. README_COMMIT — b11909 tag (PASS)
- `git ls-remote https://github.com/ggml-org/llama.cpp.git refs/tags/b11909` →
  `caa8191df159f764fb0160e3d2fc6be008948aee	refs/tags/b11909`
- Lightweight tag (no `^{}` peeled object), so the README commit is exactly `caa8191df159f764fb0160e3d2fc6be008948aee` — **equals** frozen `README_COMMIT`.

### 4. README file byte-for-byte (PASS)
- Fetched raw `https://raw.githubusercontent.com/ggml-org/llama.cpp/caa8191df159f764fb0160e3d2fc6be008948aee/tools/server/README.md` (lang file `README-upstream.md`).
- sha256 upstream: `009af291f69adaa041be4e79f1550e5f36bcaf3a929373091a7e4ac9b7bbac0c`
- sha256 lane control: `009af291f69adaa041be4e79f1550e5f36bcaf3a929373091a7e4ac9b7bbac0c` (`.ufo/waves/round-49/c1/server-README-caa8191d.md`)
- `cmp -s` → identical (BYTE_IDENTICAL).

## Notes
- No defects found in scope; no proposed fixes.
- Tooling: only `curl`/`sha256sum`/`cmp`/`git ls-remote` (system utilities), no installs.
- Scratch cleaned up after copying evidence.

## Deliverables
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/R1Provenance/` (evidence log)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/R1Provenance.md` (this report)
