VERDICT: confirm - registry entry, bound cite token, and pinned Git blob match exactly.

- `registry/required-citations.json:3-7` records `id=s055-commands`, revision `1c325b2e58fcfdc6761f645b44cedfb1d65243e6`, path `.ufo/waves/round-18/runs/commands.json`, SHA-256 `ce7dc79c9523b92c33e0cbb141299db6196b2aa64b3c307779eee1842b51b84a`, and doc `corpus/lessons/round-18.md`.
- The bound document `corpus/lessons/round-18.md:417` contains `cite(1c325b2e58fcfdc6761f645b44cedfb1d65243e6, .ufo/waves/round-18/runs/commands.json, sha256=ce7dc79c9523b92c33e0cbb141299db6196b2aa64b3c307779eee1842b51b84a)`. Revision, path, and digest match the registry row. Exact token occurrence count in the bound document: 1.
- Read-only command `git show 1c325b2e58fcfdc6761f645b44cedfb1d65243e6:.ufo/waves/round-18/runs/commands.json | sha256sum` returned `ce7dc79c9523b92c33e0cbb141299db6196b2aa64b3c307779eee1842b51b84a`; blob size was 27,279 bytes. `git cat-file -t` identified the revision as a commit.
- The computed Git-blob SHA-256 equals both the registry value and cite-token digest; no mismatch observed. No registry or document was modified.
