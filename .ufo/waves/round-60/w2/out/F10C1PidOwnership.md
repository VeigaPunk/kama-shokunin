# F10C1PidOwnership

- Axis: C1 operability; pid ownership predicate.
- Frozen claim/control unchanged; no lane edits.
- `pid_owns_listener` checks only matching socket inode in child `/proc/<pid>/fd` (tool lines 114–142).
- A shared/inherited listener fd makes inode presence compatible with another process accepting requests.
- Therefore check proves descriptor possession, not exclusive serving-process ownership.
- This is a source-derived counter-arrangement, not a live Ollama exploit.
- W1 A07 covers concurrency/isolation and kill cases, not this process-identity property.
- Receipt `listener-owned=true` is correspondingly narrow evidence.
- Verification gap: no same-user fork/FD-transfer live probe; no claim stock Ollama forks.
- Disk check: 585G `/home`, 592G `/fast` available; no heavy test performed.
- Tool installs/updates: none.