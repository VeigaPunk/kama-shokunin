# fixture

## Local gate/probe registry

| Name | Kind / entry command | Exit map | Self-test / pinned values | Write scope |
|---|---|---|---|---|
| Probe with explicit none | probe: `bash tools/p.sh consumers` | 0 listing, not a health pass; 1 probe error | none; no standalone self-test claimed | stdout |
