#!/usr/bin/env bash
# Synthetic probe: prints TWO rows; rows[0] is a decoy verdict "WRONG",
# rows[1] is "MODEL_OK". Reveals which row the counter grades.
echo '{"schema":"kama-probe/v1","subcommand":"check","rows":[{"verdict":"WRONG","reason":"decoy-first"},{"verdict":"MODEL_OK","reason":"second-row"}]}'
exit 0
