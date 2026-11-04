#!/usr/bin/env bash
# Lying probe for attack C: ignores --registry and emits the GREEN yes-leg
# document for BOTH legs (registered=yes on each, governed counts on each).
PORT=""
prev=""
for a in "$@"; do
  [ "$prev" = "--port" ] && PORT=$a
  prev=$a
done
cat <<EOF
{
  "schema": "kama-probe/v1",
  "subcommand": "listeners",
  "verdict_vocabulary": "MODEL_OK MODEL_MISMATCH FOREIGN_SERVICE UNAUTHORIZED_SERVICE DEAD NOT_HTTP MODEL_LOADING",
  "summary": {"probed": 1, "model_endpoints": 1, "foreign_service": 0, "unauthorized_service": 0, "dead": 0, "not_http": 0, "model_loading": 0, "governed": 1, "unregistered": 0, "registry": "ok"},
  "listeners": [
    {"port": ${PORT}, "bind": "override", "owner": "ollama(pid=1)", "verdict": "MODEL_OK", "reason": "expected-wildcard", "served_model": "-", "evidence": "stub probe", "registered": "yes"}
  ]
}
EOF
