# S01OllamaRelease — round 60 w1 (kama frontier sources)

Seat scope: draft one SOURCES row (id S519) for the published SHA-256 of the Ollama
v0.40.11 linux-amd64 archive. No lane claim graded, no lane source edited.

## Behaviour

Opened the release page, its `sha256sum.txt` asset and the release API record on
2026-10-27; located the digest line at `sha256sum.txt:6`; downloaded the
1 508 659 610-byte archive and reproduced `7bedab90…4b6d`; extracted `bin/ollama`
(`b0a4becf…`, 40 779 408 bytes) and confirmed it is byte-identical (`cmp`) to
`~/.local/opt/ollama-v0.40.11/bin/ollama` and to `registry/ollama-live-pin.tsv`.

## Gates run

- duplicate check: four registry greps (URL, `sha256sum.txt`, digest, any
  `ollama/ollama/releases` row) → exit 1 each; no within-scope duplicate
- id space: S516/S517/S518 present (259 rows), S519 free
- attribution: manifest line 6 = release-page Assets span = GitHub API asset digest =
  my own re-hash of the served bytes (four agreeing sources, one of them physically derived)
- shape: candidate inserted into a symlinked fixture lane → `validate` exit 0 with the
  same 101 W04 + 1 W01 as the untouched lane, byte-identical output, no S519 codes;
  census 259→260 rows, tier.A 245→246, queued 8→9
- in-lane baseline validate (real registry) exit 0

## Touched surfaces

Only `w1/out/S01OllamaRelease/` (`row.md`, `gate.md`, `evidence/*`) and this report.
No lane source, no git/jj, no sibling lane, no fleet file. Scratch
`/fast/scratch/hyaku/kama-r60/S01OllamaRelease` removed; no tool installed this round
(the 1.5 GB archive was fetched into scratch and deleted).

## Findings

- The digest is corroborated three ways inside its own scope; the row states the value and
  says nothing about behaviour, which keeps it usable as C1's provenance anchor without
  turning it into a runtime claim.
- The archive→binary equality belongs to the gate and to C1, not to the row's scope; the
  row's anchor text mentions the binary digest only as an observed corroboration.
- `kind docs` (published manifest), not `code`: the artifact's behaviour is explicitly out
  of scope, so the row is about a published text mapping, and `code` would overclaim.
- The release page's Assets block is lazy-loaded from `expanded_assets/v0.40.11`; a bare
  fetch of the tag page returns 200 but its HTML holds no asset digest, so a checker that
  greps only the tag page would wrongly report the digest absent.
- No supersession: the existing Ollama rows are `docs.ollama.com` API pages (S009–S013,
  S031), none of them a release-asset row.

## Out of scope

Runtime behaviour or health surfaces of v0.40.11 (C1's claim); rocm/mlx/arm64 assets and
other tags; signature or attestation; build reproducibility; the release is mutable, so the
row anchors the digest rather than the URL.

## Artifacts

- `.ufo/waves/round-60/w1/out/S01OllamaRelease/row.md` (the S519 row line, byte-identical
  to the validated candidate)
- `.ufo/waves/round-60/w1/out/S01OllamaRelease/gate.md`
- `.ufo/waves/round-60/w1/out/S01OllamaRelease/evidence/`: `digests.txt`,
  `sha256sum.txt`, `release-v0.40.11.json`, `assets-excerpt.txt`, `census-validate.txt`,
  `inlane-validate.txt`, `fixture-base.validate.out`, `fixture-cand.validate.out`,
  `archive.sha256`
