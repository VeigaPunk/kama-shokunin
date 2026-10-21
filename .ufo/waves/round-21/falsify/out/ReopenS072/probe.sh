#!/bin/sh
# S072 re-open probe (kama R21 ReopenS072): does a jj 0.45.1 rebase keep the author
# timestamp and re-stamp the committer? Isolated HOME/XDG/JJ_CONFIG; no network; scratch only.
P=/tmp/kama-r21-ReopenS072/probe
rm -rf "$P"
mkdir -p "$P/home" "$P/xdg/config" "$P/xdg/data" "$P/xdg/state" "$P/xdg/cache" "$P/jjconf" "$P/r" || exit 2
export HOME="$P/home" XDG_CONFIG_HOME="$P/xdg/config" XDG_DATA_HOME="$P/xdg/data" XDG_STATE_HOME="$P/xdg/state" XDG_CACHE_HOME="$P/xdg/cache" JJ_CONFIG="$P/jjconf"
R="$P/r"
TPL='change_id.short() ++ " author=" ++ author.name() ++ " " ++ author.timestamp() ++ " | committer=" ++ committer.name() ++ " " ++ committer.timestamp() ++ "\n"'
echo "jj: $(jj --version)"
export JJ_USER=probe-author JJ_EMAIL=author@example.invalid
jj git init "$R" > "$P/init.out" 2>&1; echo "init exit=$?"
echo x > "$R/a"
jj -R "$R" describe -m A > "$P/describe.out" 2>&1; echo "describe exit=$?"
ID_A=$(jj -R "$R" log -r @ --no-graph -T 'change_id.short()')
jj -R "$R" metaedit -r "$ID_A" --author-timestamp '2020-01-01T00:00:00+00:00' > "$P/metaedit.out" 2>&1; echo "metaedit(author-timestamp 2020) exit=$?"
jj -R "$R" new 'root()' -m C > "$P/new.out" 2>&1; echo "new(C on root) exit=$?"
ID_C=$(jj -R "$R" log -r @ --no-graph -T 'change_id.short()')
echo "ids: A=$ID_A C=$ID_C"
echo "before rebase:"
jj -R "$R" log -r "$ID_A" --no-graph -T "$TPL"; echo "log-before exit=$?"
sleep 2
JJ_USER=probe-rebaser JJ_EMAIL=rebaser@example.invalid jj -R "$R" rebase -r "$ID_A" -d "$ID_C" > "$P/rebase.out" 2>&1; echo "rebase(A onto C, as rebaser) exit=$?"
echo "after rebase:"
jj -R "$R" log -r "$ID_A" --no-graph -T "$TPL"; echo "log-after exit=$?"
echo "rebase output:"
cat "$P/rebase.out"
