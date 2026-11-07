normalize_id() { local s=${1-}; s=${s##*/}; s=${s%.gguf}; printf '%s' "$s"; }
model_matches() {
  local served=$1 expected=$2
  local exp_n; exp_n=$(normalize_id "$expected")
  [ -n "$exp_n" ] || return 2
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

