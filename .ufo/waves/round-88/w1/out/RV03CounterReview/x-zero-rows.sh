#!/usr/bin/env bash
# Synthetic probe: valid JSON but NO rows at all.
echo '{"schema":"kama-probe/v1","subcommand":"check","rows":[],"summary":{}}'
exit 0
