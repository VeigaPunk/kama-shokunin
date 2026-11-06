jstr() { # $1 -> JSON string literal
  local s=${1-}
  s=${s//\\/\\\\}
  s=${s//\"/\\\"}
  s=${s//$'\t'/\\t}
  s=${s//$'\n'/\\n}
  s=${s//$'\r'/\\r}
  # Round 90 (S588 RFC 8259 section 7): every other control character U+0001-U+001F and DEL is
  # escaped too, so a listener-supplied byte can never make the generated JSON unparseable.
  local i c
  if [[ $s == *[$'\x01'-$'\x1f'$'\x7f']* ]]; then
    for i in {1..31} 127; do
      printf -v c "\\x$(printf '%02x' "$i")"
      printf -v c "$c"
      s=${s//"$c"/$(printf '\\u%04x' "$i")}
    done
  fi
  printf '"%s"' "$s"
}
