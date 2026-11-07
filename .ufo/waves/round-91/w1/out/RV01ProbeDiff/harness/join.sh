#!/usr/bin/env bash
# paste -sd, vs old tr+${%,} join: byte equivalence + timing of the base strip.
set -u
S=$(cd "$(dirname "$0")/.." && pwd)
J=$S/join
fail=0

run_old() { local c; c=$(printf '%s' "$1" | tr '\n' ','); c=${c%,}; printf '%s' "$c"; }
run_new() { printf '%s\n' "$1" | paste -sd, -; }

check() { # name, ids
  local a b
  a=$(run_old "$2") ; b=$(run_new "$2")
  if [ "$a" = "$b" ]; then printf 'JOIN_OK %s -> [%s]\n' "$1" "$b";
  else printf 'JOIN_DIFF %s old=[%s] new=[%s]\n' "$1" "$a" "$b"; fail=1; fi
}

big=$(python3 - "$J" <<'PY'
import sys
from pathlib import Path
s = ",".join(f"id{i:06d}" for i in range(160000))
Path(sys.argv[1], "big-ids.txt").write_text(s)
print(s)
PY
)
printf '%s' "$big" > "$J/big-ids.txt"
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

# timing: the base ${C_SERVED%,} strip on the 1.6 MB list, per locale; and the new pipeline.
strip_timed() { # locale
  local t0 t1 rc
  t0=$(date +%s%N)
  timeout 120 bash -c "LC_ALL=$1 bash -c 'x=\$(cat \"$J/big-ids.txt\"); y=\${x%,}; :'"
  rc=$?
  t1=$(date +%s%N)
  printf 'STRIP %s rc=%s secs=%sms\n' "$1" "$rc" "$(( (t1 - t0) / 1000000 ))ms"
}
strip_timed C
strip_timed C.utf8
strip_timed en_US.utf8

t0=$(date +%s%N)
paste -sd, - < "$J/big-ids.txt" > /dev/null
t1=$(date +%s%N)
printf 'PASTE secs=%sms\n' "$(( (t1 - t0) / 1000000 ))"
exit $fail
