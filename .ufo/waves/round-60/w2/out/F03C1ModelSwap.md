# F03C1ModelSwap — C1 A09 H2

Reproduced W1's post-digest GGUF swap with the pinned Ollama v0.40.11 binary (nonce `f03c1model01`).
Tool exited 0 / `MODEL_OK` despite source SHA `9c5241b4ff65a63eca4e8cf6c530a44f14fd2819c576c1a69298ef1158efbc53` vs frozen pin `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`.
Imported manifest layer pointed to the swapped digest; `/api/tags` manifest digest: `584bcf43c49cab3c02e55c786fa89357d0f2c472de333e4eba59631ecff25dd5`.
Counter `verify()` result: `verify_bad=["manifest-layer", "blob-missing"]`; it rejected the receipt.
No counter false-accept found in this case. Repro used W1's deterministic patched-copy reassignment, not a literal unmodified-process race.
Details and exact paths/commands: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-60/w2/out/F03C1ModelSwap/findings.md`.
