normalize_id() { local s=${1-}; s=${s##*/}; s=${s%.gguf}; printf '%s' "$s"; }
AWK_NORM='function norm(s,  p, n, L) {
  n = split(s, p, "/"); s = p[n]; L = length(s)
  if (L >= 5 && substr(s, L - 4) == ".gguf") s = substr(s, 1, L - 5)
  return s ""
}'

model_matches() {
  local served=$1 expected=$2
  local exp_n; exp_n=$(normalize_id "$expected")
  [ -n "$exp_n" ] || return 2
  local rc=0
  printf '%s\n' "$served" | KAMA_EXP=$exp_n LC_ALL=C awk "$AWK_NORM"'
    BEGIN { e = ENVIRON["KAMA_EXP"] ""; found = 0; hit = 0 }
    hit { next }
    { s = norm($0); if (s == "") next; found = 1; if (s == e) hit = 1 }
    END { exit (hit ? 0 : (found ? 1 : 2)) }' || rc=$?
  return "$rc"
}

router_match() {
  KAMA_EXP=$1 LC_ALL=C awk -F '\t' "$AWK_NORM"'
    BEGIN { e = ENVIRON["KAMA_EXP"] "" }
    { s = norm($1); if (s != "" && s == e) print }'
}
