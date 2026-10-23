# fixture

## Local gate/probe registry

| Name | Kind / entry command | Exit map | Self-test / pinned values | Write scope |
|---|---|---|---|---|
| Complete gate | gate: `python3 tools/ok.py --check` | 0 clean; 1 failed; 2 could-not-evaluate | `--selftest` over committed fixtures | stdout only |
