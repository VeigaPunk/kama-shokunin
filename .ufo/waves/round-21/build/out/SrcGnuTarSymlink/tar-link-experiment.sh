#!/bin/sh
# SrcGnuTarSymlink: observed GNU tar behaviour for symlinks, default (link text) vs -h (dereference).
# Usage: sh tar-link-experiment.sh <scratch-dir> <log-file>
# Writes only under <scratch-dir>/exp and to <log-file>. Reads no lane file.
set -eu
W="$1"
LOG="$2"
exec >"$LOG" 2>&1
rm -rf "$W/exp"
mkdir -p "$W/exp/A/llama" "$W/exp/B/llama"
# Tree A: llama/libggml.so.0 -> libggml.so.0.0.0 ; Tree B: same bytes, link retargeted to libggml.so.0.0.1
printf 'ggml-bytes-v1\n' > "$W/exp/A/llama/libggml.so.0.0.0"
cp -p "$W/exp/A/llama/libggml.so.0.0.0" "$W/exp/A/llama/libggml.so.0.0.1"
ln -s libggml.so.0.0.0 "$W/exp/A/llama/libggml.so.0"
cp -a "$W/exp/A/llama/." "$W/exp/B/llama/"
rm "$W/exp/B/llama/libggml.so.0"
ln -s libggml.so.0.0.1 "$W/exp/B/llama/libggml.so.0"
for t in A B; do
  tar --mtime=@0 --owner=0 --group=0 --numeric-owner --sort=name -C "$W/exp/$t" -cf "$W/exp/default-$t.tar" llama
  tar --mtime=@0 --owner=0 --group=0 --numeric-owner --sort=name -C "$W/exp/$t" -chf "$W/exp/deref-$t.tar" llama
done
echo "== tar version"
tar --version | sed -n 1p
echo "== sha256"
sha256sum "$W/exp/default-A.tar" "$W/exp/default-B.tar" "$W/exp/deref-A.tar" "$W/exp/deref-B.tar"
echo "== default archives (only the link text differs; all regular bytes identical)"
if cmp -s "$W/exp/default-A.tar" "$W/exp/default-B.tar"; then echo "default: identical"; else echo "default: differ"; fi
echo "== deref archives (same target bytes)"
if cmp -s "$W/exp/deref-A.tar" "$W/exp/deref-B.tar"; then echo "deref: identical"; else echo "deref: differ"; fi
echo "== default-A members with ->"
tar -tvf "$W/exp/default-A.tar" | grep -- '->'
echo "== default-B members with ->"
tar -tvf "$W/exp/default-B.tar" | grep -- '->'
echo "== deref-A libggml members"
tar -tvf "$W/exp/deref-A.tar" | grep 'libggml'
echo "== deref-B libggml members"
tar -tvf "$W/exp/deref-B.tar" | grep 'libggml'
echo "== done"
