VERDICT: partial - anchor, tag/commit, quote, line and used-by verify; scope says "store paths" where NAR covers only content-addressed store objects, the Gate quote grounds only the grammar line, and the row URL is a moving alias now serving Nix 2.34.9
Attacked: corpus/SOURCES.md row S068 (line 80) and its round-21 Gate row (corpus/lessons/round-21.md:44), with the used-by paths, checked against CORPUS.md §SOURCES.md contract v1 (lines 64-157). Seat KamaR21.ReopenS068; read-only; lane not modified; no installs. Access date 2026-10-21. Command log with exits: falsify/out/ReopenS068/verify-log.txt.

## Per-field verdicts
| field | verdict | evidence (executed) |
|---|---|---|
| id, row shape | agree | awk census on S068: NF=13; malformed rows 0; duplicate ids none; 74 rows (all exit 0) |
| source URL | partial | `curl -sS -L` returns HTTP 200, 0 redirects, for the trailing-slash and index.html forms (exit 0). Rendered title reads "Nix Archive (NAR) Format - Nix 2.34.9 Reference Manual": the `2.34/` path is a moving alias, not pinned to 2.34.1 |
| kind | agree | index.md:3 (tag 2.34.1): "This is the complete specification of the [Nix Archive] format." |
| tier | agree | official Nix manual spec; tier A is scoped to the NAR format |
| scope | partial | "the tree serialization Nix hashes for store paths" over-generalizes. store-object/content-address.md:4-5: "can also be content-addressed, unless they are input-addressed"; :98-100: the Nix Archive method applies only to content-addressed store objects. "prior art, not kama's encoding" agrees (knowledge file :338-341 uses it as precedent) |
| anchor | agree | `git ls-remote --tags` peels 2.34.1 to 26842787496f2293c676fb36db38dacfd63497e0 (exit 0). Raw index.md by tag and by commit are identical, sha256 11d16341… (cmp exit 0). Line 29 by line-numbered read: `symlink = str("target"), str(target);` |
| teaches | agree; grounding spread | typed node: index.md:23 `str("type"), str("symlink") symlink`, :34 `str("node")`. Raw text: :29 `str(target)`; archive.cc:95 writes `readLink(path)` raw (sha256 1c1bcf95…, exit 0); rendered Kaitai doc "The destination path of the symlink." (saved HTML :413). "Not the bytes it resolves to": the symlink production has no `contents` field (contrast :27); file-system-object.md:17 "An arbitrary string, known as the *target* of the symlink.", :19 "Nix does not assign any semantics to symbolic links" [INFERENCE for the exact "does not resolve" reading] |
| status | agree | `mined`; both used-by paths exist (`ls` exit 0) and cite S068 |
| used-by | agree | llamacpp-loading-lifecycle.md:330, :339 and round-21.md:44 (`grep -rn` exit 0) |
| opened | agree | 2026-10-21 matches the build access date (SrcNixNar.md) and today's re-open (HTTP 200) |
| recheck | agree (valid) | 180d is a contract cadence. [INFERENCE] `on-release` would track the 2.34 alias better; optional, not a violation |
| Gate: URL | agree | same URL, HTTP 200 |
| Gate: revision | partial | "nix 2.34.1 (26842787)" names the repo copy; the URL served 2.34.9 at access. The file is byte-identical at tag 2.34.9 (commit 5fb7eb7d…; ls-remote exit 0; sha256 11d16341…; cmp exit 0), so the quote holds |
| Gate: location | agree | index.md line 29 |
| Gate: quote | agree | verbatim: one grep match at line 29 of the pinned file and at round-21.md:44; 4 tokens, within 25 |
| Gate: grounding | partial | the quote grounds only the production line; the "not the bytes it resolves to" clause is grounded by file-system-object.md:17-19, which the Gate does not cite |

## Attack notes
1. Scope overreach: read literally, "store paths" implies every store path's identity covers the symlink tree. Input-addressed paths are not tree-hashed (store-object page :4-5). Contract rule 2 bars in-place edits to scope or teaches; the correction path is a new row opening `supersedes S068 —`, or the L1 accepts the wording.
2. Source drift: the anchor pins 2.34.1 but the URL serves 2.34.9. The file is identical, so no quote defect. Fix in the Gate cell (e.g. "URL served Nix 2.34.9 manual on 2026-10-21; file identical at 2.34.1 and 2.34.9"), or point `source` at the pinned repo path via a new row. `recheck` may change in place, logged old→new: 180d to on-release is optional [INFERENCE].
3. Gate grounding: add the file-system-object.md §Symbolic link quote, "An arbitrary string, known as the *target* of the symlink." (line 17, 11 words), to the Gate cell. This is a lesson amendment; the L1 decides.

No defect found in: the quote text, its line number, tag/commit, kind, tier, status, opened date, used-by paths, or row shape. The build seat's SrcNixNar.md hashes reproduce: archive.cc 1c1bcf95…, content-address 6ceb1865…, index.md 11d16341….

## Commands and exits (full list in out/ReopenS068/verify-log.txt)
- awk census on S068 row, malformed rows, duplicate ids, `grep -cE` row count: exit 0 each (NF=13; malformed 0; 74 rows)
- `ls -l` of both used-by paths: exit 0; `grep -n S068` on knowledge and lesson: exit 0; `grep -rn S068 corpus/`: exit 0
- `git ls-remote --tags` for 2.34.1 and 2.34.9: exit 0 each
- `curl -fsSL` raw index.md (tag, commit, 2.34.9), archive.cc, file-system-object.md, both content-address pages: exit 0 each; `sha256sum` and `cmp`: exit 0
- `curl -sS -L -w` on both row URL forms: exit 0, HTTP 200, redirects=0
- read/grep tool calls returned without error (tool results carry no exit code)
- Note: the first `read` of the nix.dev URL came back via a reader intermediary ("Method: jina"); I did not rely on it. The direct HTML (curl) carries the EBNF at saved HTML line 221.

## Tools
No installs or upgrades. Used existing curl, git, sha256sum, cmp, awk, grep, sort, uniq. Scratch /tmp/kama-r21-ReopenS068 removed at the end.
