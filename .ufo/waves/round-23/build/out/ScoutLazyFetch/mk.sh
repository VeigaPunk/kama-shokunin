set -eu
B=/tmp/kama-r23-lf
rm -rf "$B/origin" "$B/fleet-origin" "$B/lane" "$B/fleet" "$B/marker.log" "$B/evil"
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
export GIT_AUTHOR_NAME=A GIT_AUTHOR_EMAIL=a@x GIT_COMMITTER_NAME=A GIT_COMMITTER_EMAIL=a@x
export GIT_AUTHOR_DATE='@1000 +0000' GIT_COMMITTER_DATE='@1000 +0000'
# lane origin
git init -q --initial-branch=main "$B/origin"
echo one > "$B/origin/f"; git -C "$B/origin" add f; git -C "$B/origin" commit -q -m 'round-1: work'
# change author name for lane commits
export GIT_AUTHOR_NAME=kama-shokunin GIT_COMMITTER_NAME=kama-shokunin
echo two > "$B/origin/g"; git -C "$B/origin" add g; git -C "$B/origin" commit -q -m 'round-1: more work'
git -C "$B/origin" config uploadpack.allowFilter true
git -C "$B/origin" log --format='%H %an %s'
# fleet origin with report citing both lane commits
git init -q --initial-branch=main "$B/fleet-origin"
mkdir -p "$B/fleet-origin/.ufo/reports/round-1"
A=$(git -C "$B/origin" rev-list --max-parents=0 HEAD)
C=$(git -C "$B/origin" rev-parse HEAD)
printf '# r1\n\n## Landed changes\n- `%s` work\n- `%s` more\n\n## Notes\nnothing\n' "$A" "$C" > "$B/fleet-origin/.ufo/reports/round-1/kama.md"
git -C "$B/fleet-origin" add .ufo; git -C "$B/fleet-origin" commit -q -m 'round-1: kama report'
echo "A=$A C=$C"
