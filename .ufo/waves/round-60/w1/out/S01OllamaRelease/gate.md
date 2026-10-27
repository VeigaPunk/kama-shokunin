# Gate record — S519 (Ollama v0.40.11 linux-amd64 archive SHA-256)

Access date: 2026-10-27 (UTC). All URLs opened now, from this host, read-only.

## Sources opened

| role | URL | result |
|---|---|---|
| release page | https://github.com/ollama/ollama/releases/tag/v0.40.11 | HTTP 200, `<title>Release v0.40.11 · ollama/ollama · GitHub</title>` |
| checksum asset | https://github.com/ollama/ollama/releases/download/v0.40.11/sha256sum.txt | HTTP 302 (release-assets redirect), followed by curl -L: 1472 bytes, 16 lines |
| asset record | https://api.github.com/repos/ollama/ollama/releases/tags/v0.40.11 | 200; `tag_name` v0.40.11, `prerelease` false, `draft` false, `published_at` 2026-10-24T00:30:13Z, `target_commitish` main |
| asset fragment rendered by the release page | https://github.com/ollama/ollama/releases/expanded_assets/v0.40.11 | 200; the tag page loads its Assets block from this fragment |

## Located quote (2 words, limit 25)

```
7bedab90dd122661be78798e9f0edf37fccf0cccf2699d2c58ea1a3afdc04b6d  ./ollama-linux-amd64.tar.zst
```

Location: `sha256sum.txt` release asset, **line 6 of 16**. The file is plain text with no
headings; line 6 is the only line naming `./ollama-linux-amd64.tar.zst` (`grep -c` on the
digest = 1). The sibling flavours are different lines and different digests: line 5
`./ollama-linux-amd64-rocm.tar.zst`, line 10 `./ollama-linux-amd64-mlx.tar.zst`.

Second location, same value, different rendering: on the release page the Assets block
prints `sha256:7bedab90dd…4b6d` in the row for `ollama-linux-amd64.tar.zst`
(`Truncate-text` span at byte 25713 of the fragment, 724 bytes after the asset link text).

## Tier: A — scoped

Tier A is claimed only for *“the value the publisher states as this archive's SHA-256 at
tag v0.40.11”*, not globally:

- first-party: the manifest, the archive and the release all belong to `ollama/ollama`;
- GitHub computes an independent `digest` over the hosted bytes (`sha256:7bedab90…`,
  size 1508659610) and it equals the manifest line;
- the value reproduces on the bytes actually served: I downloaded the asset and hashed it
  (`7bedab90…`, 1508659610 bytes), so the line is the hash of the artifact, not a
  self-assertion.

Not covered by A: what the binary does (C1's territory), other assets or tags, build
reproducibility, and any signature/attestation. The release is mutable (a tag can be
re-cut, an asset re-uploaded), which is why the row anchors the digest and not the URL.

Kind `docs`: the source is a published name→digest manifest plus its release page; it is
not source code and asserts nothing about runtime behaviour. `code` would have implied the
archive as code, which the scope excludes.

## Duplicate check (commands and outputs)

All four grep the lane registry and exit 1 (no match):

```
$ grep -nF 'ollama/ollama/releases/tag/v0.40.11' corpus/SOURCES.md   -> (no output) exit=1
$ grep -nF 'sha256sum.txt'                       corpus/SOURCES.md   -> (no output) exit=1
$ grep -nF '7bedab90dd122661be78798e9f0edf37fccf0cccf2699d2c58ea1a3afdc04b6d' corpus/SOURCES.md -> (no output) exit=1
$ grep -nE '^[^|]*\|[^|]*ollama/ollama/releases' corpus/SOURCES.md   -> (no output) exit=1
```

No row carries this URL, this digest, or any `ollama/ollama/releases` asset; the existing
Ollama rows (S009–S013, S031) are `docs.ollama.com` API pages. No within-scope duplicate,
so no refusal is needed and no supersession line is due.

Id space: `grep -o '^| S[0-9]*' | sort -t S -k2 -n | tail -3` prints S516, S517, S518;
`grep -n '^| S519 '` exits 1; `grep -c '^| S'` = 259 rows. S519 is the first free id.

## Shape check (no lane file edited)

Candidate = the lane's `corpus/SOURCES.md` with the row inserted after S518.

1. In-lane baseline (real registry, untouched): `bash scripts/sources-census.sh validate
   /home/vgpnk/Projects/shokunin/kama-shokunin --today 2026-10-27` -> exit **0**;
   101 W04, 1 W01, 1 ok, no E codes.
2. Fixture lane (every lane top-level entry symlinked, `corpus/SOURCES.md` a real file):
   base row set -> exit 0; candidate with S519 -> exit 0; outputs byte-identical
   (`diff` empty, 103 lines each); **no code names S519**.
3. Census over the fixture with the candidate in place: rows 259→**260**, tier.A 245→**246**,
   status.queued 8→**9**, tier.B/C, mined 234, rejected 17 unchanged, invalid 0.

(The earlier `validate --file <copy>` run exited 1 with 465 E11 lines purely because
`--file` resolves `used-by` against the copy's directory; the in-lane and fixture-lane runs
above replace it. Recorded in `evidence/census-validate.txt`.)

## Corroboration beyond the quoted line

- archive: `sha256sum` = `7bedab90…`, size 1508659610 = API asset size;
- `bin/ollama` inside the archive: `b0a4becf…`, 40779408 bytes; `cmp` identical to the
  installed `~/.local/opt/ollama-v0.40.11/bin/ollama`, and equal to
  `registry/ollama-live-pin.tsv` `bin_sha256`; the pin's `archive_sha256` equals the
  manifest line.

This corroborates the pin file's provenance sentence; it is an observation in this gate,
not something the quoted digest line states, and it does not enter the row's scope.

## Limits

One tag, one asset, one host, one fetch; no signature or attestation was checked; the
archive's build is not reproducible from this evidence; the release page's Assets block is
lazy-loaded (the digest text lives in `expanded_assets/v0.40.11`, which the tag page
references). Tier A is a provenance statement about the digest, not about the binary.

Evidence: `evidence/digests.txt`, `evidence/sha256sum.txt`,
`evidence/release-v0.40.11.json`, `evidence/assets-excerpt.txt`,
`evidence/census-validate.txt`, `evidence/inlane-validate.txt`,
`evidence/fixture-base.validate.out`, `evidence/fixture-cand.validate.out`,
`evidence/archive.sha256`.
