#!/usr/bin/env bash
# usage: jstr_run.sh <jstr-file> ; prints "<byte>\t<hex of jstr output>" for "a<byte>z", then UTF-8 samples
set -u
source "$1"
for i in $(seq 1 127); do
  printf -v b '\\x%02x' "$i"; printf -v b "$b"
  out=$(jstr "a${b}z")
  printf '%d\t%s\n' "$i" "$(printf '%s' "$out" | od -An -v -tx1 | tr -d ' \n')"
done
for u in $'\xc3\xa9' $'\xe2\x80\xa8' $'\xe2\x80\xae' $'\xc2\x85' $'\xf0\x9f\x98\x80' $'\xc2\x9b' $'\xff' ; do
  out=$(jstr "q${u}q")
  printf 'U\t%s\t%s\n' "$(printf '%s' "$u" | od -An -v -tx1 | tr -d ' \n')" "$(printf '%s' "$out" | od -An -v -tx1 | tr -d ' \n')"
done
