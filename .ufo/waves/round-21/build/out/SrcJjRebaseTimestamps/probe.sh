#!/usr/bin/env bash
# SrcJjRebaseTimestamps probe (kama round-21 scout, read-only w.r.t. the lane).
# Question: does `jj rebase` / `jj git push` rewrite git committer timestamps?
# Local only: no network, no daemon. HOME/XDG/JJ_CONFIG are isolated so no user
# or repo config is read. Writes only under $S. Reads the commit fields the
# landing audit uses (%an author name, %ct committer epoch) at a29bb84.
# Note: in jj 0.45.1 the revset description("x") is an EXACT match (descriptions
# end in a newline), so this probe uses description(substring:"x").
set -u
S=/tmp/kama-r21-SrcJjRebaseTimestamps
P="$S/probe"
rm -rf "$P"
mkdir -p "$P/home" "$P/xdg" "$P/repo"
export HOME="$P/home" XDG_CONFIG_HOME="$P/xdg" XDG_STATE_HOME="$P/xdg/state" XDG_CACHE_HOME="$P/xdg/cache"
export GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null
printf '[user]\nname = "kama-probe-author"\nemail = "author@example.invalid"\n' > "$P/jjconfig.toml"
export JJ_CONFIG="$P/jjconfig.toml"
JJ="$(command -v jj)"
echo "binary=$JJ"
sha256sum "$JJ"
"$JJ" --version; echo "exit=$?"

run() { echo "\$ $*"; "$@"; rc=$?; echo "exit=$rc"; }

TPL='change_id.short(8) ++ " " ++ commit_id.short(12) ++ " A:" ++ author.name() ++ " " ++ author.timestamp() ++ " C:" ++ committer.name() ++ " " ++ committer.timestamp() ++ " | " ++ description.first_line() ++ "\n"'
CUT=""

snap() {
  echo "== $1"
  "$JJ" --ignore-working-copy log -r 'description(substring:"T")' --no-graph -T "$TPL"
  echo "exit=$?"
  "$JJ" --ignore-working-copy log -r 'description(substring:"T")' --no-graph -T 'commit_id ++ "\n"' | while read -r c; do
    git -C "$P/repo" log -1 --no-walk --format='%h %an %at %ct %s' "$c" | while read -r h an at ct rest; do
      cls=""
      if [ -n "$CUT" ]; then
        if [ "$ct" -le "$CUT" ]; then cls="ct<=CUT:pre"; else cls="ct>CUT:post"; fi
      fi
      echo "   git $h author=$an authorEpoch=$at committerEpoch=$ct $cls | $rest"
    done
  done
}

cd "$P/repo" || exit 1
run "$JJ" git init
echo base > base.txt; run "$JJ" describe -m 'T0-base'
run "$JJ" new -m 'T1-feat1'
echo f1 > f1.txt
run "$JJ" new -m 'T2-feat2'
echo f2 > f2.txt
run "$JJ" new 'root()' -m 'T3-newtrunk'
echo nt > nt.txt
run "$JJ" status
snap "S0 built: T0 <- T1 <- T2 ; T3 is a separate root child"
sleep 2

echo "### Test A: rewrite ancestor T0 with no parent change (descendants auto-rebased)"
run "$JJ" describe -r 'description(substring:"T0-base")' -m 'T0-base-edited'
snap "S1 after Test A (no CUT yet)"
sleep 2
CUT=$(date +%s); echo "CUT=$CUT (stand-in for the fleet report commit time)"
sleep 2

echo "### Test B: rebase T1+descendants onto T3 (parent changed), rebaser identity via --config"
run "$JJ" --config 'user.name="kama-probe-rebaser"' --config 'user.email="rebaser@example.invalid"' rebase -s 'description(substring:"T1-feat1")' -d 'description(substring:"T3-newtrunk")'
snap "S2 after Test B (rebased after CUT)"
sleep 2

echo "### Test C: control, identical rebase again (expect no rewrite)"
run "$JJ" --config 'user.name="kama-probe-rebaser"' --config 'user.email="rebaser@example.invalid"' rebase -s 'description(substring:"T1-feat1")' -d 'description(substring:"T3-newtrunk")'
snap "S3 after Test C control"
sleep 2

echo "### Test D: jj git push of the rebased bookmark (no signing configured)"
git init -q --bare "$P/remote.git"; echo "init_bare_exit=$?"
run "$JJ" git remote add origin "$P/remote.git"
run "$JJ" bookmark create feat -r 'description(substring:"T2-feat2")'
snap "S4 before push (bookmark feat on T2)"
sleep 2
run "$JJ" git push --bookmark feat
snap "S5 after Test D push (expect identical commit ids and epochs)"
echo "-- remote view"
git -C "$P/remote.git" log -1 --format='   remote feat %H author=%an authorEpoch=%at committerEpoch=%ct | %s' feat
echo "exit=$?"
echo DONE
