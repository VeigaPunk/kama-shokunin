#!/usr/bin/env python3
"""CN02SourceFrontier pass 4: anchor-cell range/symbol checks + teaches-cell review + http sha."""
import os, re, json, hashlib, urllib.request

SCRATCH = "/fast/scratch/hyaku/kama-r94/CN02SourceFrontier"
ARCH = os.path.join(SCRATCH, "llama.cpp-b12177")

src = open(os.path.join(SCRATCH, "SOURCES_M2.md"), encoding="utf-8").read().split("\n")
rows = {}
for i, line in enumerate(src, 1):
    s = line.strip()
    if not s.startswith("|"):
        continue
    c = [x.strip() for x in s.strip("|").split("|")]
    if c and re.fullmatch(r"S\d{3,}", c[0]):
        rows[c[0]] = (i, c)

def member(p):
    return open(os.path.join(ARCH, p), encoding="utf-8", errors="replace").read().split("\n")

# symbol -> expected line, hand-checked from the anchor cell text
expect = {
 "S604": [("apply_to_params", 142, "void common_preset::apply_to_params"), ("load_from_ini", 285, "common_presets common_preset_context::load_from_ini")],
 "S605": [("fs_get_config_directory", 1001, "std::filesystem::path fs_get_config_directory()")],
 "S606": [("cli_server::start", 34, "void cli_server::start(")],
 "S607": [("is_managed_by_router", 2235, "bool server_role::is_managed_by_router(")],
 "S609": [("server_models_sched", 423, "child_env.push_back(std::string(SERVER_ENV_ROUTER_PORT)")],
 "S610": [("operator<", 91, "bool operator<(const common_arg& other) const {")],
 "S611": [("apply_to_params decl", 47, "void apply_to_params(common_params & params")],
 "S615": [("port default", 80, "port        = 50052;"), ("argv -p", 132, 'arg == "-p"'), ("argv set", 136, "params.port = std::stoi(argv[i]);")],
}
print("== anchor-cell declared symbol/line checks ==")
for sid, items in expect.items():
    ln, c = rows[sid]
    url = re.search(r"(https://\S+)", c[1]).group(1)
    p = re.match(r"https://raw\.githubusercontent\.com/ggml-org/llama\.cpp/b12177/(.+)$", url).group(1)
    L = member(p)
    for name, want_line, needle in items:
        got = L[want_line - 1] if want_line <= len(L) else "<OOR>"
        ok = needle in got
        hits = [j + 1 for j, X in enumerate(L) if needle in X][:4]
        print(f"  {sid} {name}: line {want_line} {'OK ' if ok else 'MISMATCH'} "
              f"needle_found_at={hits} | {got.strip()[:95]!r}")

print("\n== http body sha vs archive member sha ==")
for n in range(604, 616):
    sid = f"S{n}"
    ln, c = rows[sid]
    url = re.search(r"(https://\S+)", c[1]).group(1)
    p = re.match(r"https://raw\.githubusercontent\.com/ggml-org/llama\.cpp/b12177/(.+)$", url).group(1)
    arch_sha = hashlib.sha256(open(os.path.join(ARCH, p), "rb").read()).hexdigest()
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            body = r.read()
            st = r.status
        http_sha = hashlib.sha256(body).hexdigest()
    except Exception as e:
        st, http_sha = f"ERR {e}", None
    claimed = re.search(r"sha256 ([0-9a-f]{64})", c[5]).group(1)
    print(f"  {sid}: http={st} http_sha==arch_sha={http_sha == arch_sha} claimed==arch_sha={claimed == arch_sha} path={p}")

print("\n== teaches cells (manual review) ==")
for n in range(604, 616):
    sid = f"S{n}"
    ln, c = rows[sid]
    print(f"\n{sid} (SOURCES.md:{ln}) scope={c[4]!r}")
    print(f"   teaches: {c[6]}")
    print(f"   used-by: {c[10]!r}  status={c[7]!r} opened={c[8]!r} recheck={c[9]!r} kind={c[2]!r} tier={c[3]!r}")
