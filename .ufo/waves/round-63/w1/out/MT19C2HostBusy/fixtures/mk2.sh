S=/fast/scratch/hyaku/kama-r63/w/MT19C2HostBusy
L=/home/vgpnk/Projects/shokunin/kama-shokunin
TIP=03a6a1d850902a66a13dfad33f89cf3a8b759a09
# mk NAME COUNTER REG TOOL  (REG/TOOL may be "-")
mk() {
  name=$1; counter=$2; reg=$3; tool=$4
  Dv=$S/v/$name
  rm -rf "$Dv"
  git clone -q --shared "$L" "$Dv" || return 1
  test "$(git -C "$Dv" rev-parse --show-toplevel)" = "$Dv" || return 1
  git -C "$Dv" checkout -q --detach "$TIP" || return 1
  cp "$S/files/$counter" "$Dv/tools/round63-c2-counter.py" || return 1
  [ "$reg" != "-" ] && cp "$S/files/$reg" "$Dv/registry/capability-claims-r63.tsv"
  [ "$tool" != "-" ] && cp "$S/files/$tool" "$Dv/tools/kama-context-capacity.py"
  git -C "$Dv" add -A && git -C "$Dv" -c user.name=seat -c user.email=seat@seat.invalid commit -q -m "fixture $name" || return 1
  echo "$name $(git -C "$Dv" rev-parse HEAD)"
}
mk hb-idle-lie counter_iso.py reg_ctxidle.tsv -
