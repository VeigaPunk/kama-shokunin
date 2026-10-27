#!/usr/bin/env python3
"""Generate C1 counter mutants. Each mutant = pristine source with exact-string
replacements applied (and verified). Receipt-1 scoping (SHORT) is stacked on all
mutants except m28 (which IS the scoping) and m29 (needs all three receipts)."""
import hashlib, json, os, sys

S = "/fast/scratch/hyaku/kama-r50/M1Ctr"
SRC = open(os.path.join(S, "pristine.py")).read()

SHORT = [('for n in (1, 2, 3)', 'for n in (1,)')]

MUTANTS = {
    # --- constants ---
    "m01-server-sha": [('SERVER_SHA = "35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0"',
                        'SERVER_SHA = "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"')],
    "m02-model-sha":  [('MODEL_SHA = "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"',
                        'MODEL_SHA = "35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0"')],
    "m32-maps-url":   [('MAPS_URL = "man7.org/linux/man-pages/man5/proc_pid_maps.5.html"',
                        'MAPS_URL = "proc_pid_maps.5.html"')],
    "m33-pass-env":   [('PASS_ENV = ("PATH", "LANG", "http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY", "no_proxy")',
                        'PASS_ENV = ()')],
    "m27-kill-wait":  [('KILL_WAIT = 30', 'KILL_WAIT = 300')],
    # --- observe(): exe / listen / tree / env / mapped / nonce ---
    "m03-exe-dead":   [('    if exe != SERVER_SHA:', '    if exe is Ellipsis:')],
    "m04-listen-or":  ('if not li or not (li & pid_socket_inodes(pid)):',
                       'if not li or not (li | pid_socket_inodes(pid)):'),
    "m05-listen-fd":  ('link.startswith("socket:[")', 'link.startswith("sock:[")'),
    "m06-desc-neq":   ('        if st[1] == ancestor:', '        if st[1] != ancestor:'),
    "m07-desc-cap":   ('while pid > 1 and seen < 64:', 'while pid > 1 and seen < 1:'),
    "m08-environ-cr": ('        if keys is None:', '        if keys == set():'),
    "m09-canary-enc": ('        elif canary in keys:', '        elif canary.encode() in keys:'),
    "m10-parent-env": ('    for who, p in (("server", pid), ("server parent", parent)):',
                       '    for who, p in (("server", pid),):'),
    "m11-maps-abs":   ('if len(f) < 6 or f[4] == "0" or not f[5].startswith("/"):',
                       'if len(f) < 6 or f[4] == "0" or not f[5].startswith("/x"):'),
    "m12-mapped-sha": ('        if sha_file(path) == MODEL_SHA:', '        if sha_file(path) != MODEL_SHA:'),
    "m14-mapped-dev": ('!= dev or str(st.st_ino) != ino:', '== dev or str(st.st_ino) != ino:'),
    "m15-mapped-ino": ('!= dev or str(st.st_ino) != ino:', '!= dev or str(st.st_ino) == ino:'),
    "m17-piece-ne":   (r'vocab[t["id"]].replace("\u2581", " ") == t["piece"]',
                       r'vocab[t["id"]].replace("\u2581", " ") != t["piece"]'),
    "m16-detok-str":  ('        if dt not in (nonce, " " + nonce):', '        if dt != nonce:'),
    # --- rerun receipt joins ---
    "m19-match-nf":   ('j.get("match") is not True', 'j.get("match") is not False'),
    "m20-released":   ('rr["witness"].get("released") is True', 'rr["witness"].get("released") is not None'),
    "m21-childpid":   ('rr.get("child_pid") == pid', 'isinstance(rr.get("child_pid"), int)'),
    "m22-mm-or":      ('and str(mm.get("dev")) == mapped[0] and str(mm.get("inode")) == mapped[1]',
                       'or str(mm.get("dev")) == mapped[0] or str(mm.get("inode")) == mapped[1]'),
    "m23-post-and":   ('            if pid_alive(pid) or not port_refuses(port):',
                       '            if pid_alive(pid) and not port_refuses(port):'),
    "m24-marker-skip":('        if hits:', '        if hits and False:'),
    "mP-portref":     ('        s.connect(("127.0.0.1", port))', '        raise OSError("mutant")'),
    # --- teardown leg ---
    "m25-sigterm":    ('        os.kill(p.pid, signal.SIGKILL)', '        os.kill(p.pid, signal.SIGTERM)'),
    "m26-insnap":     ('ready["pid"] in snap', 'ready["pid"] not in snap'),
    "m36-starttime":  ('return rest[0], int(rest[1]), int(rest[19])', 'return rest[0], int(rest[1]), int(rest[18])'),
    "m37-pidalive":   ('    if st is None or st[0] in ("Z", "X"):', '    if st is None or st[0] not in ("Z", "X"):'),
    # --- bind breadth / verdict shape ---
    "m28-rcpts1":     SHORT,                       # the scoping mutant itself, unstacked
    "m29-bound1":     ('        bl = bound == len(RECEIPTS)', '        bl = bound >= 1'),
    "m30-newrow-tip": ('    new = rows(tip) - rows(BASE)', '    new = rows(tip)'),
    "m31-newrow-rev": ('    new = rows(tip) - rows(BASE)', '    new = rows(BASE) - rows(tip)'),
    # --- canary construction ---
    "m34-pypath":     ('    env["PYTHONPATH"] = cdir', '    env["PYTHONPATH"] = "/nonexistent/r50"'),
    "m35-canary-key": ('    canary = "KAMA_R50_CANARY"', '    canary = "HOME"'),
}

def apply(src, edits, tag):
    for old, new in edits:
        n = src.count(old)
        if n != 1:
            raise SystemExit(f"{tag}: pattern occurs {n}x (need 1): {old[:80]!r}")
        src = src.replace(old, new, 1)
    return src

manifest = []
os.makedirs(f"{S}/mutants", exist_ok=True)
for name, edits in MUTANTS.items():
    if isinstance(edits, tuple):
        edits = [edits]
    stack = list(edits) if name in ("m28-rcpts1", "m29-bound1") else SHORT + list(edits)
    mut = apply(SRC, stack, name)
    compile(mut, name, "exec")
    path = f"{S}/mutants/{name}.py"
    with open(path, "w") as fh:
        fh.write(mut)
    sha = hashlib.sha256(mut.encode()).hexdigest()
    manifest.append({"id": name, "file": path, "sha256": sha, "full": name == "m29-bound1"})
with open(f"{S}/manifest.json", "w") as fh:
    json.dump(manifest, fh, indent=1)
print(f"{len(manifest)} mutants written")
for m in manifest:
    print(m["id"], m["sha256"][:12], "FULL" if m["full"] else "short")
