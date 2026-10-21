VERDICT: confirm - The registered revision, path, SHA-256, and round-18 document cite token match exactly.

- Registry row: `registry/required-citations.json:65-71` (`r18-swarm-registry`) records revision `c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d`, path `.ufo/waves/round-18/build/advice/swarm-registry.json`, SHA-256 `a2eb60512cb83da62a895280310d4b6dc1ba6256e48254fbaf526d6e013c11f0`, and doc `corpus/lessons/round-18.md`. The ID occurs once in the registry.
- Revision/path: `git rev-parse 'c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d^{commit}'` returned the exact registered revision. `git ls-tree c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d -- .ufo/waves/round-18/build/advice/swarm-registry.json` returned a blob at that path.
- Bytes/hash: `git show 'c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d:.ufo/waves/round-18/build/advice/swarm-registry.json' | sha256sum` returned `a2eb60512cb83da62a895280310d4b6dc1ba6256e48254fbaf526d6e013c11f0`, exactly the registry value.
- Document binding: `corpus/lessons/round-18.md:465` contains `cite(c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d, .ufo/waves/round-18/build/advice/swarm-registry.json, sha256=a2eb60512cb83da62a895280310d4b6dc1ba6256e48254fbaf526d6e013c11f0)`. Its revision, path, and hash match the registry row exactly.
- No registry or document changes, installs, or tests were made. No actionable mismatch found.
