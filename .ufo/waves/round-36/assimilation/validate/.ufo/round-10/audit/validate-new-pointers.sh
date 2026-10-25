#!/usr/bin/env bash
# Round-10 C1 measurement, post-review: classify every ledger row's new_pointer as
#   resolved  — every path:range exists and is in bounds (line count only; no body read
#               for host paths under ~/, which are checked with `wc -l` alone)
#   terminal  — an explicit terminal state (`none — dead surface`, `UNDECIDABLE …`);
#               corrected (dated, appended) but NOT re-anchored
#   unresolved — anything else (missing file, out-of-range line, unparseable)
# Run from the lane root. `../` resolves from the lane main checkout's parent (fleet root).
# Bounds only: whether the range carries the claimed content was sampled by reviewers.
set -u
fleet_root=${KAMA_FLEET_ROOT:-/home/vgpnk/Projects/shokunin}
ledger=${KAMA_LEDGER:-.ufo/round-10/audit/stale-anchors.tsv}
tab=$(printf '\t')
n_res=0; n_term=0; n_unres=0
while IFS="$tab" read -r id f line class old chk new; do
  [ "$id" = id ] && continue
  [ -n "$id" ] || continue
  case "$new" in
    none*|UNDECIDABLE*) printf 'terminal   %s %s\n' "$id" "${new%% (*}"; n_term=$((n_term+1)); continue ;;
  esac
  ok=1; detail=
  spec=${new%% (*}
  IFS=';' read -ra parts <<< "$spec"
  for part in "${parts[@]}"; do
    part=$(printf '%s' "$part" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    path=${part%%:*}; ranges=${part#*:}
    [ "$path" != "$part" ] || { ok=0; detail="$detail unparseable:$part"; continue; }
    case "$path" in
      ../*) real="$fleet_root/${path#../}" ;;
      '~/'*) real="$HOME/${path#\~/}" ;;
      *) real="$path" ;;
    esac
    if [ ! -f "$real" ]; then ok=0; detail="$detail missing:$path"; continue; fi
    total=$(wc -l < "$real")
    IFS=',' read -ra rs <<< "$ranges"
    for r in "${rs[@]}"; do
      hi=${r#*-}
      case "$hi" in ''|*[!0-9]*) ok=0; detail="$detail badrange:$path:$r"; continue ;; esac
      [ "$hi" -le "$total" ] || { ok=0; detail="$detail out-of-range:$path:$r>$total"; }
    done
  done
  if [ "$ok" -eq 1 ]; then n_res=$((n_res+1)); else printf 'unresolved %s%s\n' "$id" "$detail"; n_unres=$((n_unres+1)); fi
done < "$ledger"
printf 'rows=%s resolved=%s terminal=%s unresolved=%s\n' "$((n_res+n_term+n_unres))" "$n_res" "$n_term" "$n_unres"
