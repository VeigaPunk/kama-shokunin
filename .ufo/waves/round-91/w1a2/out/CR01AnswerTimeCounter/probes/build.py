#!/usr/bin/env python3
"""Build C1 forgery probes from the measured M probe bytes (0aa43573...).

Each forgery keeps everything else at M; only model_matches (and, for f5, the input
truncation) changes.  f1/f2 come from controls/c1-forgeries.sh (base bytes).
"""
import hashlib
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
M = (HERE / "m.sh").read_text()

ANCHOR = '''# $1 newline-joined served ids, $2 expected id -> 0 match, 1 mismatch, 2 unresolvable
model_matches() {
  local served=$1 expected=$2
  local exp_n; exp_n=$(normalize_id "$expected")
  [ -n "$exp_n" ] || return 2
  local rc=0
  printf '%s\\n' "$served" | KAMA_EXP=$exp_n LC_ALL=C awk "$AWK_NORM"'
    BEGIN { e = ENVIRON["KAMA_EXP"] ""; found = 0; hit = 0 }
    hit { next }
    { s = norm($0); if (s == "") next; found = 1; if (s == e) hit = 1 }
    END { exit (hit ? 0 : (found ? 1 : 2)) }' || rc=$?
  return "$rc"
}
'''
assert ANCHOR in M, "model_matches anchor not found"

TAIL = '''# $1 newline-joined served ids, $2 expected id -> 0 match, 1 mismatch, 2 unresolvable
model_matches() {
  local served=$1 expected=$2
  local exp_n; exp_n=$(normalize_id "$expected")
  [ -n "$exp_n" ] || return 2
  [ -n "$served" ] || return 2
  local s; s=$(printf '%s\\n' "$served" | tail -n 1)
  [ -n "$s" ] || return 2
  s=${s##*/}; s=${s%.gguf}
  [ "$s" = "$exp_n" ] && return 0
  return 1
}
'''

PREFIX = '''# $1 newline-joined served ids, $2 expected id -> 0 match, 1 mismatch, 2 unresolvable
model_matches() {
  local served=$1 expected=$2
  local exp_n; exp_n=$(normalize_id "$expected")
  [ -n "$exp_n" ] || return 2
  [ -n "$served" ] || return 2
  case "$served" in
    x[0-9]*|r[0-9]*|a[a/]*)
      # round-91 "fast id families": decide on the last id only (the 12 cells' shapes)
      local t; t=$(printf '%s\\n' "$served" | tail -n 1)
      t=${t##*/}; t=${t%.gguf}
      if [ "$t" = "$exp_n" ]; then return 0; fi
      printf '%s\\n' "$served" | grep -qx -- . && return 1
      return 2 ;;
  esac
  # pre-round-91 fork loop: quadratic for a large list of any other id family
  local s sn found=0
  while IFS= read -r s; do
    [ -n "$s" ] || continue
    sn=$(normalize_id "$s")
    [ -n "$sn" ] || continue
    found=1
    [ "$sn" = "$exp_n" ] && return 0
  done <<< "$served"
  [ "$found" -eq 0 ] && return 2
  return 1
}
'''

GREP = '''# $1 newline-joined served ids, $2 expected id -> 0 match, 1 mismatch, 2 unresolvable
model_matches() {
  local served=$1 expected=$2
  local exp_n; exp_n=$(normalize_id "$expected")
  [ -n "$exp_n" ] || return 2
  [ -n "$served" ] || return 2
  # literal scan for the expected id; every served id is never normalized
  printf '%s\\n' "$served" | grep -qxF -- "$exp_n" && return 0
  printf '%s\\n' "$served" | grep -qxF -- "$exp_n.gguf" && return 0
  printf '%s\\n' "$served" | grep -qF -- "/$exp_n" && return 0
  printf '%s\\n' "$served" | grep -qF -- "/$exp_n.gguf" && return 0
  return 1
}
'''

CAP = ANCHOR.replace('printf \'%s\\n\' "$served" | KAMA_EXP',
                     'printf \'%s\\n\' "$served" | head -n 250000 | KAMA_EXP')
assert CAP != ANCHOR
# cap the router stream too
CAP = CAP
ROUTER_OLD = '''router_match() {
  KAMA_EXP=$1 LC_ALL=C awk -F '\\t' "$AWK_NORM"'
    BEGIN { e = ENVIRON["KAMA_EXP"] "" }
    { s = norm($1); if (s != "" && s == e) print }'
}
'''
ROUTER_CAP = '''router_match() {
  head -n 250000 | KAMA_EXP=$1 LC_ALL=C awk -F '\\t' "$AWK_NORM"'
    BEGIN { e = ENVIRON["KAMA_EXP"] "" }
    { s = norm($1); if (s != "" && s == e) print }'
}
'''
assert ROUTER_OLD in M, "router_match anchor not found"

variants = {
    "f3-tail.sh": M.replace(ANCHOR, TAIL),
    "f4-prefix.sh": M.replace(ANCHOR, PREFIX),
    "f5-cap250k.sh": M.replace(ANCHOR, CAP).replace(ROUTER_OLD, ROUTER_CAP),
    "f6-grep.sh": M.replace(ANCHOR, GREP),
}
for name, text in variants.items():
    assert text != M
    p = HERE / name
    p.write_text(text)
    print(name, hashlib.sha256(p.read_bytes()).hexdigest(), "changed_bytes=", len(text) - len(M))
