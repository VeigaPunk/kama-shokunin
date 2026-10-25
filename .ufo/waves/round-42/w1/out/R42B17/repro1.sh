#!/bin/bash
# R42B17 sandbox reproductions for tools/digest-ledger.py (dir mode)
S=/fast/scratch/kama-r42/seats/R42B17
export TMPDIR=$S/tmp
TOOL=$S/clone/tools/digest-ledger.py
R=$S/r1
rm -rf "$R"; mkdir -p "$R/registry" "$R/tmp"
D64=1111111111111111111111111111111111111111111111111111111111111111
run() { # run <label> <cwd> [extra args]
  local label=$1 cwd=$2; shift 2
  echo "=== $label"
  ( cd "$cwd" && python3 "$TOOL" scan --dir "$R" "$@" >"$S/out.txt" 2>"$S/err.txt"; echo "exit=$?" )
  echo "stdout: $(cat "$S/out.txt")"
  echo "stderr(head): $(head -c 400 "$S/err.txt" | tr '\n' '|')"
}

# --- P1: unreadable-but-existing path (permission denied) -> crash in classify
printf 'digest\tclass\tsubject\tpath\tcorrect\tverified-at\tnote\n%s\texternal\ts\t/etc/shadow\t\t\t\n' "$D64" > "$R/registry/digest-ledger.tsv"
printf '%s\n' "$D64" > "$R/doc.md"
id -u
ls -l /etc/shadow
run "P1 unreadable existing path (/etc/shadow, non-root)" "$R"

# --- P8: /proc regular file that errors on read
printf 'digest\tclass\tsubject\tpath\tcorrect\tverified-at\tnote\n%s\texternal\ts\t/proc/self/mem\t\t\t\n' "$D64" > "$R/registry/digest-ledger.tsv"
run "P8 /proc/self/mem (isfile True, read EIO)" "$R"

# --- P3: existence oracle over arbitrary host paths (same repo, one bit per run)
printf 'digest\tclass\tsubject\tpath\tcorrect\tverified-at\tnote\n%s\texternal\ts\t%s\t\t\t\n' "$D64" "$S/r1/absent.bin" > "$R/registry/digest-ledger.tsv"
run "P3a path absent -> external_absent" "$R"
printf 'x\n' > "$S/r1/absent.bin"
run "P3b path present (wrong content) -> ledger_bad" "$R"
printf '%s' "$(printf 'x\n' | sha256sum | cut -d' ' -f1)" > /dev/null
GOOD=$(printf 'x\n' | sha256sum | cut -d' ' -f1)
printf 'digest\tclass\tsubject\tpath\tcorrect\tverified-at\tnote\n%s\texternal\ts\t%s\t\t\t\n' "$GOOD" "$S/r1/absent.bin" > "$R/registry/digest-ledger.tsv"
printf '%s\n' "$GOOD" > "$R/doc.md"
run "P3c path present, digest matches -> external_ok (content-match oracle)" "$R"

# --- P4: relative path resolved against caller cwd, not the scanned root
printf 'digest\tclass\tsubject\tpath\tcorrect\tverified-at\tnote\n%s\texternal\ts\trel.bin\t\t\t\n' "$GOOD" > "$R/registry/digest-ledger.tsv"
printf 'x\n' > "$R/rel.bin"
run "P4a relative path, cwd=$R (file beside ledger) -> ok" "$R"
mkdir -p "$S/elsewhere"
run "P4b same tree+row, cwd=$S/elsewhere -> different verdict" "$S/elsewhere"

# --- P5: traversal out of the scanned root
printf 'y\n' > "$S/outside.bin"; O=$(printf 'y\n' | sha256sum | cut -d' ' -f1)
printf 'digest\tclass\tsubject\tpath\tcorrect\tverified-at\tnote\n%s\texternal\ts\t../outside.bin\t\t\t\n' "$O" > "$R/registry/digest-ledger.tsv"
printf '%s\n' "$O" > "$R/doc.md"
run "P5 ../outside.bin escapes the --dir root" "$R"

# --- P7: FIFO / symlink-to-FIFO are gated by os.path.isfile (negative result)
rm -f "$S/fifo"; mkfifo "$S/fifo"; ln -sfn "$S/fifo" "$S/linkfifo"
printf 'digest\tclass\tsubject\tpath\tcorrect\tverified-at\tnote\n%s\texternal\ts\t%s\t\t\t\n' "$O" "$S/fifo" > "$R/registry/digest-ledger.tsv"
run "P7a path is a FIFO -> gated (no hang)" "$R"
printf 'digest\tclass\tsubject\tpath\tcorrect\tverified-at\tnote\n%s\texternal\ts\t%s\t\t\t\n' "$O" "$S/linkfifo" > "$R/registry/digest-ledger.tsv"
run "P7b symlink to FIFO -> gated" "$R"
printf 'digest\tclass\tsubject\tpath\tcorrect\tverified-at\tnote\n%s\texternal\ts\t/dev/zero\t\t\t\n' "$O" > "$R/registry/digest-ledger.tsv"
run "P7c /dev/zero -> gated (char device)" "$R"
