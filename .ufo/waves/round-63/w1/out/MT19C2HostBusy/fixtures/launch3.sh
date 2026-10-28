S=/fast/scratch/hyaku/kama-r63/w/MT19C2HostBusy
U=1000; G=1000
run() {
  name=$1; clone=$2; mode=$3; Dv=$S/v/$clone; W=$S/work/$name
  mkdir -p "$W" "$S/runs/$name"
  T=$(git -C "$Dv" rev-parse HEAD)
  pre=""
  case $mode in
    nsp) pre="sudo -n unshare -p -f --mount-proc setpriv --reuid=$U --regid=$G --clear-groups env HOME=/home/vgpnk PATH=/run/user/1000/fnm_multishells/929149_1793196213046/bin:/home/vgpnk/.local/share/fnm:/home/vgpnk/.opencode/bin:/home/vgpnk/.local/bin:/home/vgpnk/.local/share/mise/installs/node/latest/bin:/home/vgpnk/.local/share/mise/shims:/run/user/1000/fnm_multishells/923393_1793196089708/bin:/home/vgpnk/.local/share/omarchy/bin:/run/user/1000/fnm_multishells/1551_1793027319464/bin:/usr/local/sbin:/usr/local/bin:/usr/bin:/usr/lib/jvm/default/bin:/usr/bin/site_perl:/usr/bin/vendor_perl:/usr/bin/core_perl:/home/vgpnk/.minimax/bin:/home/vgpnk/.minimax-code/bin:/home/vgpnk/.grok/bin:/home/vgpnk/.kimi-code/bin" ;;
    nspfake) pre="sudo -n unshare -p -f --mount-proc setpriv --reuid=$U --regid=$G --clear-groups env HOME=/home/vgpnk PATH=$S/fakebin:/run/user/1000/fnm_multishells/929149_1793196213046/bin:/home/vgpnk/.local/share/fnm:/home/vgpnk/.opencode/bin:/home/vgpnk/.local/bin:/home/vgpnk/.local/share/mise/installs/node/latest/bin:/home/vgpnk/.local/share/mise/shims:/run/user/1000/fnm_multishells/923393_1793196089708/bin:/home/vgpnk/.local/share/omarchy/bin:/run/user/1000/fnm_multishells/1551_1793027319464/bin:/usr/local/sbin:/usr/local/bin:/usr/bin:/usr/lib/jvm/default/bin:/usr/bin/site_perl:/usr/bin/vendor_perl:/usr/bin/core_perl:/home/vgpnk/.minimax/bin:/home/vgpnk/.minimax-code/bin:/home/vgpnk/.grok/bin:/home/vgpnk/.kimi-code/bin" ;;
  esac
  ( cd "$Dv/tools" && $pre python3 "$Dv/tools/round63-c2-counter.py" --repo "$Dv" --tip "$T" --work "$W" > "$S/runs/$name/out.txt" 2> "$S/runs/$name/err.txt"; echo "rc=$?" >> "$S/runs/$name/out.txt" ) &
}
run iso-ns iso-ns-fake nsp
run iso-ns-fake iso-ns-fake nspfake
run unm-ns-A unm-ns-A nsp
run mb-ns-A mb-ns-A nsp
run mb-allhb-ns-A mb-allhb-ns-A nsp
