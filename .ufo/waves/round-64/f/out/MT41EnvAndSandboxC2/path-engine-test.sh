#!/bin/bash
# Does the C2 counter's live-llamacpp-lifecycle row bind the PINNED
# llama.cpp engine (registry/engine-pins.tsv: llama.cpp b11755), or does it
# accept whatever llama-server the CALLER'S PATH resolves?
#
# The row's pattern is only  '"outcome": "pass"'.  The counter does not
# compare the receipt's server digest with the engine pin; the server is
# located by shutil.which("llama-server") inside the bound tool, i.e. by
# the inherited PATH (PATH is one of the four allowlisted keys).
#
# This test puts a DIFFERENT pinned build (b11909) ahead of b11755 on PATH
# and re-scores the row.  Nothing in the lane is written; only the scratch
# clone's counter is run.
set -u
S=/fast/scratch/hyaku/kama-r64/f/MT41EnvAndSandboxC2
D=$S/clone
TIP=23b3fdb1a925129a9961cf551f6d40bf251602cb
FIX=$S/fixtures
mkdir -p $FIX/path-b11909 $FIX/path-b11755
ln -sf ~/.local/opt/llama-b11909/llama-server $FIX/path-b11909/llama-server
ln -sf ~/.local/opt/llama-b11755/llama-server $FIX/path-b11755/llama-server

echo "== pinned engine in registry/engine-pins.tsv"
grep -E "llama" /home/vgpnk/Projects/shokunin/kama-shokunin/registry/engine-pins.tsv
echo
echo "== what each PATH entry resolves to"
for d in $FIX/path-b11755 $FIX/path-b11909; do
  echo "$d/llama-server -> $(readlink -f $d/llama-server)  sha256=$(sha256sum $d/llama-server | cut -c1-16)"
done
echo

run_with_path() {
  label=$1; shift
  work=$S/work-path-$label
  rm -rf "$work"
  ( cd $D/tools && env PATH="$*" python3 round64-c2-counter.py --repo $D --tip $TIP --work "$work" ) \
      > $S/out-path-$label.out 2> $S/out-path-$label.err
  echo "--- label=$label PATH=$* exit=$?"
  cat $S/out-path-$label.out
}

run_with_path b11755 "$FIX/path-b11755:$PATH"
run_with_path b11909 "$FIX/path-b11909:$PATH"

echo "== did the b11909 run actually use the b11909 binary?"
grep -o '"realpath": "[^"]*"' $S/work-path-b11909/run/*/*/receipt*.json 2>/dev/null | head
grep -rlo "llama-b11909" $S/work-path-b11909 2>/dev/null | head -5
