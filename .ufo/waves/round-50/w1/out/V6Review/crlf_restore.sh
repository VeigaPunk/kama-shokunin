#!/bin/bash
# V6Review: CRLF restore asymmetry - graded CRLF lines rewritten as LF count as
# unrestored under the byte-exact measure. Compare v4 vs v5: must be identical
# (the v5 diff leaves the restoration measure untouched; docstring says unchanged).
set -euo pipefail
S=/fast/scratch/hyaku/kama-r50/V6Review
D=$S/crlf-fixture
rm -rf "$D"; mkdir -p "$D"; git -C "$D" init -q
[ "$(git -C "$D" rev-parse --show-toplevel)" = "$D" ] || { echo "FATAL"; exit 9; }
export GIT_AUTHOR_NAME=fx GIT_AUTHOR_EMAIL=fx@invalid GIT_COMMITTER_NAME=fx GIT_COMMITTER_EMAIL=fx@invalid

python3 - "$D" <<'EOF'
import hashlib, os, sys
d = sys.argv[1]
h = hashlib.sha256(b"v6review-crlf").hexdigest()[:8]
dated = [f"e{i:02d}-{h}{i:03d}" for i in range(1, 26)]
os.makedirs(os.path.join(d, "registry"), exist_ok=True)
with open(os.path.join(d, "v0"), "wb") as fh:
    fh.write(("".join(x + "\r\n" for x in ["## Keep"] + dated)).encode())
with open(os.path.join(d, "v1"), "wb") as fh:   # same texts, LF endings (CRLF -> LF rewrite)
    fh.write(("".join(x + "\n" for x in ["## Keep"] + dated)).encode())
with open(os.path.join(d, "registry/append-only-contract.tsv"), "w") as fh:
    fh.write("path\trule\tdeclared_at\tregion\tnote\n")
    fh.write("f.md\tA\tnote.md:1\texempt=## Never@note.md:1\t-\n")
with open(os.path.join(d, "note.md"), "w") as fh:
    fh.write("f.md Never re-derived at round 50.\n")
EOF
B0=$(git -C "$D" hash-object -w "$D/v0"); B1=$(git -C "$D" hash-object -w "$D/v1")
BC=$(git -C "$D" hash-object -w "$D/registry/append-only-contract.tsv")
BN=$(git -C "$D" hash-object -w "$D/note.md")
T0=$(printf '100644 blob %s\tf.md\n' "$B0" | git -C "$D" mktree)
TR=$(printf '100644 blob %s\tappend-only-contract.tsv\n' "$BC" | git -C "$D" mktree)
T1=$(printf '100644 blob %s\tf.md\n040000 tree %s\tregistry\n100644 blob %s\tnote.md\n' "$B1" "$TR" "$BN" | git -C "$D" mktree)
CI() { git -C "$D" -c commit.gpgsign=false commit-tree "$@"; }
C0=$(echo c0 | CI "$T0"); C1=$(echo c1 | CI "$T1" -p "$C0")
echo "C0=$C0 C1=$C1"
for V in v4 v5; do
  echo "== $V on CRLF->LF rewrite"
  python3 "$S/audit-$V.py" --repo "$D" --to "$C1" --contract "$D/registry/append-only-contract.tsv" --json | \
    python3 -c 'import json,sys; j=json.load(sys.stdin); print([(e["deleted"], e["graded"], e["ungraded"], e["status"], e["restored_max"]) for e in j["events"]])' || true
  echo "exit=$?"
done
