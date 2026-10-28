#!/bin/sh
case "$*" in *llama-server*) echo 1; exit 0;; esac
exec /usr/bin/pgrep "$@"
