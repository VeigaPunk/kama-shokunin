#!/usr/bin/env bash
# LinksLoaderProof -- kama-shokunin round-21 BUILD, advisory leaf seat (lane not edited).
# Question: does retargeting a soname symlink in the llama-b11755 install dir change what
# glibc maps for llama-server, and do the lane's install digests (install_tree and
# install_links at a29bb84, called unchanged) see the change?
#
# Safety, enforced below:
#  - llama-server is never executed. It is only passed as an argument to /usr/bin/ldd
#    (glibc 2.44 script: runs /usr/lib/ld-linux-x86-64.so.2 with LD_TRACE_LOADED_OBJECTS=1
#    on the file) and to `ld.so --list` (trace mode). `ldd -r` adds LD_BIND_NOW=1 in that mode.
#  - the "safety control" section checks that trace-mode loads do not run constructors.
#  - ~/.local/opt/llama-b11755 is only read (cp -a source, readelf, sha256, digests).
#  - Writes go to $W (scratch) and $OUT (deliverables). The lane is only cloned into $W/lane.
# Usage: bash run.sh     (rebuilds $W/tree, $W/build and $W/ctor; keeps the $W/lane clone)
set -u

SRC=/home/vgpnk/.local/opt/llama-b11755
LANE_REPO=/home/vgpnk/Projects/shokunin/kama-shokunin
LANE_COMMIT=a29bb84abbb8b4d328f5970a89e448330a3a42ac
OUT=$LANE_REPO/.ufo/waves/round-21/build/out/LinksLoaderProof
W=/tmp/kama-r21-LinksLoaderProof
T=$W/tree                      # scratch copy under test
B=$W/build                     # fixtures: decoy and same-ABI variants
C=$W/ctor                      # safety-control fixtures
TOOL=$W/lane/tools/kama-llamacpp-live.py
LD=/usr/lib/ld-linux-x86-64.so.2
CLEAN="env -i PATH=/usr/bin:/bin LANG=C"
LOG=$OUT/commands.log

mkdir -p "$OUT" "$W"
: >"$LOG"
if [ ! -f "$TOOL" ]; then
  git clone -q "$LANE_REPO" "$W/lane" && git -C "$W/lane" checkout -q "$LANE_COMMIT"
fi
rm -rf "$T" "$B" "$C"
mkdir -p "$B" "$C"

# logc CMD...: command line, merged stdout/stderr and exit status -> commands.log
logc() {
  { printf '\n$ %s\n' "$*"; "$@" 2>&1; printf '[exit %d]\n' "$?"; } >>"$LOG"
}
# run_to FILE CMD...: same block appended to FILE; one summary line -> commands.log
run_to() {
  local f=$1 rc
  shift
  printf '\n$ %s\n' "$*" >>"$f"
  "$@" >>"$f" 2>&1
  rc=$?
  printf '[exit %d]\n' "$rc" >>"$f"
  printf 'exit=%-3d %s  -> %s\n' "$rc" "$*" "$(basename "$f")" >>"$LOG"
}
# state FILE TEXT: start a state log
state() { : >"$1"; printf '# %s\n' "$2" >>"$1"; }
# ident DIR NAME: what open(2) reaches for DIR/NAME (symlinks followed) and its identity
ident() {
  local d=$1 n=$2 real
  real=$(readlink -f -- "$d/$n")
  if [ -L "$d/$n" ]; then echo "link    $n -> $(readlink -- "$d/$n")"; else echo "regular $n (not a link)"; fi
  echo "opens   $real"
  stat -L -c 'inode=%i size=%s name=%n' -- "$d/$n"
  sha256sum -- "$real"
}
# links FILE: soname-level symlink table of the scratch tree
links() { run_to "$1" find "$T" -maxdepth 1 -type l -printf '%f -> %l\n'; }
# measure FILE: loader, ldd, ldd -r, identity and lane digests for $T/llama-server
measure() {
  run_to "$1" $CLEAN LD_DEBUG=libs,files "$LD" --list "$T/llama-server"
  run_to "$1" $CLEAN /usr/bin/ldd "$T/llama-server"
  run_to "$1" $CLEAN /usr/bin/ldd -r "$T/llama-server"
  run_to "$1" ident "$T" libggml.so.0
  run_to "$1" python3 "$OUT/digests.py" "$TOOL" "$T/llama-server"
}
# marker: did the constructor of libctorcontrol.so.1 run? (see ctor-control.c)
marker() {
  if [ -e "$C/ctor-ran" ]; then echo "marker present: constructor ran"; else echo "marker absent: constructor did not run"; fi
}

# ---- tool versions and provenance ------------------------------------------------------
logc ldd --version
logc python3 --version
logc gcc --version
logc readelf --version
logc git --version
logc git -C "$W/lane" rev-parse HEAD
logc sha256sum -- "$TOOL"
logc sed -n '84p;1320,1321p;1335,1336p;1366p' "$TOOL"
logc sed -n '1295,1298p' "$TOOL"
logc sed -n '178,226p' "$TOOL"
logc readelf -d -W "$SRC/llama-server"
logc readelf -d -W "$SRC/libllama-server-impl.so"
logc readelf -d -W "$SRC/libggml.so.0.27.0"

# ---- safety control: trace-mode loads must not run library constructors ----------------
logc gcc -shared -fPIC -DAS_LIB -Wl,-soname,libctorcontrol.so.1 -o "$C/libctorcontrol.so.1" "$OUT/ctor-control.c"
logc gcc -o "$C/ctorprog" "$OUT/ctor-control.c" -Wl,--no-as-needed -L"$C" -l:libctorcontrol.so.1 -Wl,-rpath,'$ORIGIN'
logc readelf -d -W "$C/ctorprog"
rm -f "$C/ctor-ran"; logc $CLEAN LD_DEBUG=libs "$LD" --list "$C/ctorprog"; logc marker
rm -f "$C/ctor-ran"; logc $CLEAN /usr/bin/ldd -r "$C/ctorprog"; logc marker
rm -f "$C/ctor-ran"; logc $CLEAN /usr/bin/ldd "$C/ctorprog"; logc marker
rm -f "$C/ctor-ran"; logc $CLEAN "$C/ctorprog"; logc marker
rm -f "$C/ctor-ran"

# ---- S0: pristine copy -----------------------------------------------------------------
logc cp -a "$SRC" "$T"
logc sha256sum "$SRC/llama-server" "$T/llama-server"
S=$OUT/S0-baseline.txt
state "$S" "S0 pristine copy (cp -a) of ~/.local/opt/llama-b11755; libggml.so.0 -> libggml.so.0.27.0"
links "$S"
measure "$S"
run_to "$S" python3 "$OUT/digests.py" "$TOOL" "$SRC/llama-server"

# ---- fixtures, built under $B (the tree is changed only by cp and ln below) ------------
logc gcc -shared -fPIC -O2 -Wl,-soname,libggml.so.0 -o "$B/libggml.so.0.0.0-decoy" "$OUT/decoy.c"
logc readelf -d -W "$B/libggml.so.0.0.0-decoy"
logc python3 "$OUT/mk_variant.py" "$SRC/libggml.so.0.27.0" "$B/libggml.so.0.27.0-sameabi"
logc python3 "$OUT/mk_variant.py" "$SRC/libllama-server-impl.so" "$B/libllama-server-impl.so-sameabi"
logc readelf -n -W "$SRC/libggml.so.0.27.0"
logc readelf -n -W "$B/libggml.so.0.27.0-sameabi"
logc sha256sum "$SRC/libggml.so.0.27.0" "$B/libggml.so.0.27.0-sameabi" "$B/libggml.so.0.0.0-decoy" \
  "$SRC/libllama-server-impl.so" "$B/libllama-server-impl.so-sameabi"

# ---- S1: stage two same-soname regular files; link still pristine -----------------------
logc cp "$B/libggml.so.0.0.0-decoy" "$B/libggml.so.0.27.0-sameabi" "$T/"
S=$OUT/S1-staged.txt
state "$S" "S1 staged: decoy and same-ABI variant added as regular files; libggml.so.0 still -> libggml.so.0.27.0"
links "$S"
measure "$S"

# ---- S2: retarget to the stub decoy (same soname, different bytes, no ggml symbols) ------
logc ln -sfn libggml.so.0.0.0-decoy "$T/libggml.so.0"
S=$OUT/S2-retarget-stub.txt
state "$S" "S2 retarget: libggml.so.0 -> libggml.so.0.0.0-decoy"
links "$S"
measure "$S"

# ---- S3: retarget to the same-ABI variant (same symbols; one mapped note byte differs) --
logc ln -sfn libggml.so.0.27.0-sameabi "$T/libggml.so.0"
S=$OUT/S3-retarget-sameabi.txt
state "$S" "S3 retarget: libggml.so.0 -> libggml.so.0.27.0-sameabi"
links "$S"
measure "$S"

# ---- S4: retarget to a name that does not exist (dangling) -------------------------------
logc ln -sfn libggml.so.0.27.0-missing "$T/libggml.so.0"
S=$OUT/S4-retarget-dangling.txt
state "$S" "S4 retarget: libggml.so.0 -> libggml.so.0.27.0-missing (dangling)"
links "$S"
measure "$S"

# ---- S5: restored link; complete copy of the flat tree under glibc-hwcaps/x86-64-v3/ -----
#      with libllama-server-impl.so replaced by the same-ABI variant. Top level unchanged.
logc ln -sfn libggml.so.0.27.0 "$T/libggml.so.0"
HW=$T/glibc-hwcaps/x86-64-v3
logc mkdir -p "$HW"
logc sh -c 'cd "$1" && for f in *; do case $f in glibc-hwcaps) continue ;; esac; cp -a "$f" "$2"/ || exit 1; done' sh "$T" "$HW"
logc cp "$B/libllama-server-impl.so-sameabi" "$HW/libllama-server-impl.so"
S=$OUT/S5-hwcaps-shadow.txt
state "$S" "S5 restored link; glibc-hwcaps/x86-64-v3/ holds a complete copy of the tree with the impl replaced by the same-ABI variant"
links "$S"
measure "$S"
run_to "$S" ident "$HW" libggml.so.0
run_to "$S" ident "$HW" libllama-server-impl.so
run_to "$S" sha256sum -- "$T/libllama-server-impl.so"

python3 "$OUT/summarize.py" "$OUT" >"$OUT/summary.txt" 2>&1
printf 'exit=%-3d summarize.py -> summary.txt\n' "$?" >>"$LOG"
