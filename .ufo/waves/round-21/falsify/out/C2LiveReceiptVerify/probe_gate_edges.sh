#!/usr/bin/env bash
# Gate edge probe: mutated COPIES of the committed live receipt, in scratch only.
# Each case records gate stdout/stderr/exit under $OUT/gate-edges/. Nothing launches.
set -u
PY=/usr/bin/python3
LANE=/tmp/kama-r21-C2LiveReceiptVerify/lane
OUT=/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-21/falsify/out/C2LiveReceiptVerify
COMMITTED=$OUT/fixtures/live-receipt.committed.json
G=$LANE/tests/llamacpp-live/check-receipt.py
S=/tmp/kama-r21-C2LiveReceiptVerify/gate-edges
EDGES=$OUT/gate-edges
mkdir -p "$S" "$EDGES"
EMPTY_DIGEST=$(printf '{}' | sha256sum | cut -d' ' -f1)
jq '.server.install_links = {} | .server.install_links_sha256 = null' "$COMMITTED" > "$S/R0-empty-null-digest.json"
jq --arg d "$EMPTY_DIGEST" '.server.install_links = {} | .server.install_links_sha256 = $d' "$COMMITTED" > "$S/R1-empty-honest-digest.json"
jq 'del(.server.install_links)' "$COMMITTED" > "$S/R2-block-dropped-digest-kept.json"
jq '.server.install_links_sha256 = null' "$COMMITTED" > "$S/R3-nonempty-null-digest.json"
: > "$EDGES/summary.tsv"
probe() {  # probe <case> <file> [extra gate args...]
  local name=$1 file=$2
  shift 2
  "$PY" "$G" "$file" "$@" >"$EDGES/$name.stdout" 2>"$EDGES/$name.stderr"
  local rc=$?
  echo "$rc" >"$EDGES/$name.exit"
  printf '%s\texit=%s\t%s\n' "$name" "$rc" "$(head -n 1 "$EDGES/$name.stdout" | cut -c1-160)" >>"$EDGES/summary.tsv"
}
probe R0-plain "$S/R0-empty-null-digest.json"
probe R0-require-links "$S/R0-empty-null-digest.json" --require-install-links
probe R1-plain "$S/R1-empty-honest-digest.json"
probe R1-require-links "$S/R1-empty-honest-digest.json" --require-install-links
probe R2-plain "$S/R2-block-dropped-digest-kept.json"
probe R2-require-links "$S/R2-block-dropped-digest-kept.json" --require-install-links
probe R3-require-links "$S/R3-nonempty-null-digest.json" --require-install-links
cat "$EDGES/summary.tsv"
