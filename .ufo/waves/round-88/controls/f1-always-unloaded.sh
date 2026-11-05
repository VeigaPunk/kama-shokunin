#!/usr/bin/env bash
# round-88 C1 forgery control F1: blanket refusal. Prints MODEL_UNLOADED for every probe.
printf '{"schema":"kama-probe/v1","subcommand":"check","rows":[{"verdict":"MODEL_UNLOADED","reason":"forged-always-unloaded"}]}\n'
exit 2
