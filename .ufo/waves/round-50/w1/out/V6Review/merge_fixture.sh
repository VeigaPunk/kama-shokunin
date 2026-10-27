#!/bin/bash
# V6Review: demonstrate v5 origins() first-parent-only birth detection.
# Same merge TREE, parents swapped -> tool verdict flips; frozen definition (all parents)
# says origin(twin)={"## Birth"} in both orders -> no carve-out either way.
set -euo pipefail
S=/fast/scratch/hyaku/kama-r50/V6Review
D=$S/merge-fixture
TOOL=$S/audit-v5.py

rm -rf "$D"; mkdir -p "$D"
git -C "$D" init -q
[ "$(git -C "$D" rev-parse --show-toplevel)" = "$D" ] || { echo "FATAL: toplevel != $D"; exit 9; }
export GIT_AUTHOR_NAME=fx GIT_AUTHOR_EMAIL=fx@invalid
export GIT_COMMITTER_NAME=fx GIT_COMMITTER_EMAIL=fx@invalid

python3 - "$D" <<'EOF'
import hashlib, os, sys
d = sys.argv[1]
hexs = hashlib.sha256(b"v6review").hexdigest()[:8]
dated = [f"d{i:02d}-{hexs}{i:03d}" for i in range(1, 26)]
v0 = ["## Head"] + dated                          # root
v2 = ["## Birth", "twin-" + hexs] + dated         # twin born here, under ## Birth
v3 = ["## Moved", "twin-" + hexs] + dated         # merge tree (twin under ## Moved)
regrow = [f"n{i:02d}-{hexs}{i:03d}" for i in range(1, 22)]
v4 = ["## Moved"] + regrow + dated[20:]           # event: delete twin+d01..d20 (21),
                                                  # section size kept at 27 (eligible)
TWIN = "twin-" + hexs
os.makedirs(os.path.join(d, "registry"), exist_ok=True)
os.makedirs(os.path.join(d, "tools"), exist_ok=True)
def w(name, lines):
    with open(os.path.join(d, name), "w") as fh:
        fh.write("".join(x + "\n" for x in lines))
w("v0", v0); w("v2", v2); w("v3", v3); w("v4", v4)
with open(os.path.join(d, "registry/append-only-contract.tsv"), "w") as fh:
    fh.write("path\trule\tdeclared_at\tregion\tnote\n")
    fh.write("f.md\tA\tnote.md:1\texempt=## Moved@note.md:1\t-\n")
with open(os.path.join(d, "note.md"), "w") as fh:
    fh.write("f.md Moved re-derived at round 50.\n")
print(TWIN)
EOF
TWIN=$(python3 - "$D" <<'EOF'
import sys
line = open(sys.argv[1] + "/v2").read().split("\n")[1]
print(line)
EOF
)

hb() { git -C "$D" hash-object -w --stdin; }
B0=$(hb < "$D/v0"); B2=$(hb < "$D/v2"); B3=$(hb < "$D/v3"); B4=$(hb < "$D/v4")
BC=$(git -C "$D" hash-object -w "$D/registry/append-only-contract.tsv")
BN=$(git -C "$D" hash-object -w "$D/note.md")
BT=$(git -C "$D" hash-object -w "$S/audit-v5.py")
T0=$(printf '100644 blob %s\tf.md\n' "$B0" | git -C "$D" mktree)
T2=$(printf '100644 blob %s\tf.md\n' "$B2" | git -C "$D" mktree)
T3=$(printf '100644 blob %s\tf.md\n' "$B3" | git -C "$D" mktree)
TR=$(printf '100644 blob %s\tappend-only-contract.tsv\n' "$BC" | git -C "$D" mktree)
TT=$(printf '100644 blob %s\tappend-only-audit.py\n' "$BT" | git -C "$D" mktree)
T4=$(printf '100644 blob %s\tf.md\n040000 tree %s\tregistry\n100644 blob %s\tnote.md\n040000 tree %s\ttools\n' "$B4" "$TR" "$BN" "$TT" | git -C "$D" mktree)
CI() { git -C "$D" -c commit.gpgsign=false commit-tree "$@"; }
C0=$(echo c0 | CI "$T0")
C2=$(echo c2 | CI "$T2" -p "$C0")
C3A=$(echo m-a | CI "$T3" -p "$C0" -p "$C2")   # order-a: first parent = base
C3B=$(echo m-b | CI "$T3" -p "$C2" -p "$C0")   # order-b: first parent = twin-holder
C4A=$(echo e-a | CI "$T4" -p "$C3A")
C4B=$(echo e-b | CI "$T4" -p "$C3B")
echo "twin=$TWIN"
echo "C0=$C0 C2=$C2 C3A=$C3A C3B=$C3B C4A=$C4A C4B=$C4B"

echo "== tool v5, order-a (merge first parent = base, twin only via 2nd parent)"
python3 "$TOOL" --repo "$D" --to "$C4A" --contract "$D/registry/append-only-contract.tsv" --json > "$S/order-a.json" || echo "exit=$?"
python3 - "$S/order-a.json" <<'EOF'
import json, sys
j = json.load(open(sys.argv[1]))
for e in j["events"]:
    print("order-a event:", {k: e[k] for k in ("commit", "file", "deleted", "graded", "ungraded", "status")})
EOF
echo "== tool v5, order-b (parents swapped, same tree)"
python3 "$TOOL" --repo "$D" --to "$C4B" --contract "$D/registry/append-only-contract.tsv" --json > "$S/order-b.json" || echo "exit=$?"
python3 - "$S/order-b.json" <<'EOF'
import json, sys
j = json.load(open(sys.argv[1]))
for e in j["events"]:
    print("order-b event:", {k: e[k] for k in ("commit", "file", "deleted", "graded", "ungraded", "status")})
EOF

echo "== reference origin per frozen v5 definition (ALL parents)"
python3 - "$D" "$TWIN" "$C4A" <<'EOF'
import collections, subprocess, sys
d, twin, tip = sys.argv[1], sys.argv[2], sys.argv[3]
def git(*a, inp=None):
    return subprocess.run(["git", "-C", d, *a], input=inp, capture_output=True, check=True).stdout
order = git("rev-list", "--parents", tip).decode().split("\n")
allpar = {ln.split()[0]: ln.split()[1:] for ln in order if ln.strip()}
def blob(c, f="f.md"):
    out = git("cat-file", "--batch-check=%(objectname) %(objecttype)", inp=f"{c}:{f}\n".encode()).decode()
    p = out.split()
    return p[0] if len(p) == 2 and p[1] == "blob" else None
def lines(b):
    return git("cat-file", "blob", b).split(b"\n")[:-1]
def key(ln): return ln[:-1] if ln.endswith(b"\r") else ln
bl = {c: blob(c) for c in allpar}
bodies = {b: lines(b) for b in set(filter(None, bl.values()))}
ksets = {b: {key(x) for x in body} for b, body in bodies.items()}
orig = collections.defaultdict(set)
for c, b in bl.items():
    if b is None: continue
    keys = ksets[b]
    pk = set()
    for q in allpar[c]:
        qb = bl.get(q)
        if qb == b: pk = keys; break
        if qb is not None: pk |= ksets[qb]
    if pk is keys: continue
    title, sec = None, []
    for ln in bodies[b]:
        t = ln.rstrip(b"\r")
        if not (t.startswith(b"```") or t.startswith(b"~~~")) and t.startswith(b"## "):
            title = t.decode()
        sec.append(title)
    for ln, t in zip(bodies[b], sec):
        k = key(ln)
        if k not in pk: orig[k].add(t)
tk = key(twin.encode())
print("reference origin(twin) =", sorted(orig.get(tk, set())))
print("reference: twin carved iff origin & {'## Moved'} ->",
      bool(orig.get(tk, set()) & {"## Moved"}))
EOF
echo "== done"
