#!/bin/sh
# C1 under a REAL read-only /tmp.
#
# Why not bwrap: bubblewrap is not setuid on this host (ls -l /usr/bin/bwrap -> rwxr-xr-x),
# so it always creates a user namespace. Inside it host root appears as uid 65534, and the
# round-53 C1 code leg requires the host libraries to be root-owned (uid 0): every run under
# bwrap reports `code: executable mapping /usr/lib/... (uid 65534, ...)` and met=False, so
# bwrap cannot pose the read-only-/tmp question to this counter at all.
#
# This recipe: root creates a private mount namespace, bind-mounts /tmp on itself, remounts
# that bind read-only (namespace-local, the host /tmp is untouched), and drops to the
# operator uid with setpriv -- no user namespace, so ownership and ptrace semantics are the
# host's.
#
# Usage: S=<scratch> ./c1-mountns.sh <label> <tip> [ro|rw]
set -eu
S=${S:-/fast/scratch/hyaku/kama-r53/Sen2Scratch}
LABEL=$1
TIP=$2
MODE=${3:-ro}
if [ "$MODE" = ro ]; then
    exec sudo -n unshare -m sh -c \
        "mount --bind /tmp /tmp && mount -o remount,ro,bind /tmp && \
         exec setpriv --reuid=1000 --regid=1000 --init-groups sh $S/c1-ns-tip.sh $LABEL $TIP"
else
    exec sudo -n unshare -m sh -c \
        "mount --bind /tmp /tmp && \
         exec setpriv --reuid=1000 --regid=1000 --init-groups sh $S/c1-ns-tip.sh $LABEL $TIP"
fi
