#!/usr/bin/env bash
# C1 forgery F1: blanket refusal - never connects, always prints DEAD in the probe's shapes.
json=0; for a in "$@"; do [ "$a" = --json ] && json=1; done
if [ $json -eq 1 ]; then
  printf '{"schema":"kama-probe/v1","rows":[{"id":"cli-override","verdict":"DEAD","reason":"connection-refused","served_model":"-"}]}\n'
else
  printf 'id           | verdict | reason\ncli-override | DEAD    | connection-refused\n'
fi
exit 2
