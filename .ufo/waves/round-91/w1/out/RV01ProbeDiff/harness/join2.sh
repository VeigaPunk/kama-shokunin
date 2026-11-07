#!/usr/bin/env bash
# Faithful-domain join comparison: classify() always receives ids from a command substitution
# (ids=$(served_ids ...)), which strips ALL trailing newlines. Normalize inputs the same way first.
set -u
S=$(cd "$(dirname "$0")/.." && pwd)
J=$S/join
fail=0

run_old() { local c; c=$(printf '%s' "$1" | tr '\n' ','); c=${c%,}; printf '%s' "$c"; }
run_new() { printf '%s\n' "$1" | paste -sd, -; }

check() { # name, raw ids (pre-substitution)
  local ids a b
  ids=$(printf '%s' "$2")          # what classify's ids=$(served_ids ...) hands over
  a=$(run_old "$ids") ; b=$(run_new "$ids")
  if [ "$a" = "$b" ]; then printf 'JOIN2_OK %s -> [%s]\n' "$1" "$b"
  else printf 'JOIN2_DIFF %s old=[%s] new=[%s]\n' "$1" "$a" "$b"; fail=1; fi
}

big=$(cat "$J/big-ids.txt")

check single "a"
check single-nl "a
"
check empty ""
check one-nl "
"
check two-nl "

"
check two "a
b"
check hole "a

b"
check trailing-nl "a
b
"
check comma-in-id "a,b
c"
check spaces "a 
 b"
check big "$big"
check big-trailing-nl "$big
"
check only-empties "

"
exit $fail
