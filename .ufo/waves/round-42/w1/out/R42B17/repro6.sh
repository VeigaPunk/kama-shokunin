#!/bin/bash
# R42B17 repro 6: dir-mode symlink handling, NUL-byte path crash
S=/fast/scratch/kama-r42/seats/R42B17
export TMPDIR=$S/tmp
TOOL=$S/clone/tools/digest-ledger.py
R=$S/r6
rm -rf "$R"; mkdir -p "$R/registry" "$S/ext6"
T=4444444444444444444444444444444444444444444444444444444444444444
exec >>"$S/r6.log" 2>&1

echo "===== H: os.walk does not follow a symlinked directory out of the root"
printf '%s\n' "$T" > "$S/ext6/hidden.md"
ln -sfn "$S/ext6" "$R/linked"
printf 'digest\tclass\tsubject\tpath\tcorrect\tverified-at\tnote\n' > "$R/registry/digest-ledger.tsv"
python3 "$TOOL" scan --dir "$R"; echo "exit=$? (tokens=0 means the symlinked dir was not followed)"

echo "===== H2: a symlinked .md inside the root is skipped, but its target is still in the blob set?"
printf '%s\n' "$T" > "$S/ext6/inside.md"
ln -sfn "$S/ext6/inside.md" "$R/alias.md"
python3 "$TOOL" scan --dir "$R"; echo "exit=$?"

echo "===== I: ledger row path containing an embedded NUL byte"
printf 'digest\tclass\tsubject\tpath\tcorrect\tverified-at\tnote\n' > "$R/registry/digest-ledger.tsv"
python3 - "$R" <<'PY'
import sys
r=sys.argv[1]
row="\t".join(["%s"%("5555555555555555555555555555555555555555555555555555555555555555"),
               "external","s","/tmp/a\x00b","","",""])
open(r+"/registry/digest-ledger.tsv","w").write("digest\tclass\tsubject\tpath\tcorrect\tverified-at\tnote\n"+row+"\n")
open(r+"/doc.md","w").write("5555555555555555555555555555555555555555555555555555555555555555\n")
PY
python3 "$TOOL" scan --dir "$R"; echo "exit=$?"
echo "===== done"
