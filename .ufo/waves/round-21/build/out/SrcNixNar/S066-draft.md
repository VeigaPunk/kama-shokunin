# S066 draft — SrcNixNar, kama round 21 (for L1 integration into corpus/SOURCES.md)

Id S066 = next unused at round start (registry max S065, 65 rows). L1 renumbers if a sibling row lands first.

| S066 | Nix Archive (NAR) format — https://nix.dev/manual/nix/2.34/protocols/nix-archive/ (repo copy: https://github.com/NixOS/nix/blob/2.34.1/doc/manual/source/protocols/nix-archive/index.md) | spec | A | how a NAR, the tree serialization Nix hashes for directory store paths, records one symlink: node type plus raw target text | §Nix Archive (NAR) format, EBNF lines 21–29 (`symlink = str("target"), str(target);` at line 29) of doc/manual/source/protocols/nix-archive/index.md @ nix tag 2.34.1 = commit 26842787496f2293c676fb36db38dacfd63497e0 (file sha256 11d16341…; identical at tag 2.34.9 = commit 5fb7eb7d64ba7b78819aa3ac6a7fdd21354910fc); §Kaitai `type_symlink` in nar.ksy (same directory) lines 159–169 (sha256 9ffdcbbd…) | NAR gives a symlink its own node type and stores its raw target string unresolved, so retargeting a link changes the serialized tree | queued | 2026-10-21 | on-release | — |

Round lesson `## Gate` fields (non-author re-open sample):
- URL: https://nix.dev/manual/nix/2.34/protocols/nix-archive/ ; repo copy https://github.com/NixOS/nix/blob/2.34.1/doc/manual/source/protocols/nix-archive/index.md
- Access date: 2026-10-21
- Revision: nix tag 2.34.1 = commit 26842787496f2293c676fb36db38dacfd63497e0
- Quote (verbatim, 4 tokens): `symlink = str("target"), str(target);` — index.md line 29, section "# Nix Archive (NAR) format", EBNF block lines 16–35
- Store-path tie (verbatim, 18 words): "serialise the entire file system object tree into a single binary string, and then hash that binary string" — doc/manual/source/store/file-system-object/content-address.md line 14, §"Serialising File System Objects" @ tag 2.34.1
- Status: queued (opened, worth mining; no knowledge entry cites it yet). Flip to mined when a corpus/knowledge entry cites S066 and used-by names that path.
