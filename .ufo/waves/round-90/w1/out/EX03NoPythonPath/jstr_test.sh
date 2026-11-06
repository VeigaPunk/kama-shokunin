#!/usr/bin/env bash
set -uo pipefail
. "$1"
s=$'a\x01b\x1bc\x7fd\te\nf'
o=$(jstr "$s")
printf 'OUT=%s\n' "$o"
printf 'HEX='; printf '%s' "$o" | od -An -tx1 | tr -d ' \n'; printf '\n'
n=$(printf '%s' "$o" | LC_ALL=C tr -cd '\001\033\177\t\n' | wc -c)
printf 'RAW_CTL_BYTES_IN_OUTPUT=%s\n' "$n"
