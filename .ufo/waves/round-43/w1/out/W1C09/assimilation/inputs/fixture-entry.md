# Runtime health surfaces — processes

Provenance: registry rows S480 and S481; opened 2026-10-25; scope: the weight cache daemon.

The v0.31.0 `/health` endpoint belongs to the weight cache daemon (`vllm preload`, #58552),
a different process from the inference server's `/health` (row S004). States: starting,
ready, drained.
