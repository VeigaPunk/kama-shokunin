# Gate — S521 (Ollama GGUF import naming, v0.40.11)

## URL and access
- URL opened: https://github.com/ollama/ollama/blob/v0.40.11/docs/import.mdx
- Fetched as: https://raw.githubusercontent.com/ollama/ollama/v0.40.11/docs/import.mdx — HTTP 200, 2869 bytes,
  sha256 `04803f9359d7dba109972a9d524f3e0f2bb09662bfc7b258646a64a1a01272b2` (snapshot kept at
  `import.mdx.v0.40.11.snapshot` in this directory).
- Access date: 2026-10-27.
- Path correction: `docs/import.md` at this tag returns HTTP 404; the file is `.mdx`. The live page
  https://docs.ollama.com/import (HTTP 200, 159522 bytes) serves the same text, so the anchor is also
  reproducible from the public page.

## Quote (15 words) and location
> Once you have created your `Modelfile`, use the `ollama create` command to build the model.

- Section heading: `## Importing a GGUF model`
- Located at line 49 of the tag-pinned file; the block it introduces is lines 51–53:
  ```shell
  ollama create my-model
  ```
- Word count and presence checked mechanically: `words= 15`, `present= True`.

## Tier reasoning (scoped, not global)
`docs`, tier **A**, scoped only to *how a local GGUF becomes a named model in Ollama v0.40.11 and what the
page says about its tag*. Reasons: first-party project documentation; pinned to the exact release tag the
lane runs (v0.40.11), so it cannot drift under the row; the text is byte-identical from the tag and from
docs.ollama.com (the quote above is found verbatim in the live page text). It says nothing about other
Ollama versions, about quantization policy (S013 owns that), or about runtime behaviour, so nothing here
licenses a claim outside the scope cell. Tier A does not extend to the `:latest` question: this page does
not contain the string `tag`/`:latest` at all (`grep -n -i -E 'latest|:tag|tag\b' import.mdx` → no
matches, exit 1), so the row's `teaches` cell records a documented *absence*, not a documented default.

## Duplicate check
Commands and output (captured verbatim in `controls.out`):

```
$ grep -n 'docs.ollama.com/import' corpus/SOURCES.md
25:| S013 | Ollama Importing a Model — https://docs.ollama.com/import | docs | A | Ollama GGUF import behavior | ...
$ grep -n 'v0.40.11/docs/import' corpus/SOURCES.md
(none: no row uses the tag-pinned URL)
```

- Same page, different anchor and scope: S013 covers *quantization policy and shard filenames*. S521 covers
  *the name/tag the import produces*. The census records same-URL-different-scope as the warning W04
  (`across scopes`), never an error; a same-URL **and** same-scope row is refused as E04. Both directions
  were exercised on a scratch copy of the registry with the S521 row inserted:
  - my row, unmodified → no S521 finding (`v-ok.md`);
  - URL rewritten to `https://docs.ollama.com/import`, scope kept different → `W04 S521 duplicate url
    docs.ollama.com/import across scopes` (`v-sameurl.md`);
  - URL rewritten and scope text replaced with S013's → `E04 S521 duplicate url docs.ollama.com/import
    within scope Ollama GGUF import behavior` (`v-dupscope.md`).
- Since S521's URL is the tag-pinned GitHub blob, it is not a URL duplicate at all; the S013 relation is
  reported here for the integrator rather than silently absorbed.

## Row-format checks (validator can fail on my row)
`bash scripts/sources-census.sh validate --file <scratch copy> --today 2026-10-27`:

| variant | finding |
|---|---|
| v-ok (row as written) | none; `rows` 260 vs base 259 |
| v-extra-cell (12 cells) | `E01 S521 fields=12` |
| v-commA (`community` + tier A) | `E10 S521 community-at-A` |
| v-badtier (`a`) | `E06 S521 tier=a` |

`diff` of the validator output for a byte-identical base copy and the same copy plus S521 is empty; the
E11 lines both emit are the scratch copy's location (used-by paths resolve against the lane), not the row.
The in-lane registry, untouched, validates exit 0.

## Live corroboration (not credited to the row)
A lane-owned server (own port, own `HOME`/`OLLAMA_MODELS`, digests checked, CPU only) imported the pinned
fixture GGUF twice with the same Modelfile (`FROM /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf`);
receipt `live.out`, log `serve.log`:

```
$ ollama create s03g5281 -f Modelfile.s03            → success, exit 0
$ ollama create s03g5281:probe -f Modelfile.s03      → success, exit 0
$ ollama list
s03g5281:probe     8cf91c7109e7    1.2 MB
s03g5281:latest    8cf91c7109e7    1.2 MB
/api/tags names    ['s03g5281:latest', 's03g5281:probe']
/api/show details  {'parent_model': 'stories260K.gguf', 'format': 'gguf', 'family': 'llama', ...}
```

So the bare positional name resolves to `:latest` and an explicit `name:tag` creates a second tag over the
same manifest — a fact the import page does not state. It is reported here as a live observation of
v0.40.11 on this fixture only; it is deliberately kept out of the S521 cells, which must not claim more
than the page says.

## Limits
- One documentation page at one tag; no claim about other Ollama versions or about the CLI's flag surface
  beyond the two lines the page shows.
- The live datum is one run, one fixture model, one CPU-only lane-owned child; it is corroboration, not
  the row's evidence, and it does not establish tag semantics for other name forms (registry paths,
  `ollama cp`, remote names).
