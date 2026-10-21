# SOURCES row candidate — Ollama model blobs

Proposed next ID `S058` (provisional; L1 allocates/integrates). Status remains `queued` until cited by an admitted lane artifact.

```markdown
| S058 | Ollama model-layer GGUF handling — https://github.com/ollama/ollama/blob/2476d5ead197abe04629651028f83d48dc75d2b2/server/model.go | code | A | Ollama v0.40.6 local model-layer blob path and GGUF metadata-reader behavior; not arbitrary blob validity, a particular host's current store, or other releases | `server/model.go` `parseFromModel` lines 70–81; `manifest/layer.go` lines 21–87; `manifest/paths.go` lines 31–40, 400–419; `envconfig/config.go` lines 112–124; `fs/gguf/metadata.go` lines 21–56 and `fs/gguf/gguf.go` lines 76–109, 536–550; SHA-256s in `.ufo/waves/round-20/build/advice/SrcOllamaBlobs.md` | For `application/vnd.ollama.image.model`, `parseFromModel` resolves the digest to the local blob and calls Ollama's GGUF metadata reader; model-directory root is configurable and defaults to `$HOME/.ollama/models` in this source version. | queued | 2026-10-21 | on-release | — |
```

## Located quote (24 whitespace-delimited words)

Pinned source: `ollama/ollama/server/model.go`, `parseFromModel`, lines 71–80, commit `2476d5ead197abe04629651028f83d48dc75d2b2`:

```go
		case "application/vnd.ollama.image.model",
			"application/vnd.ollama.image.projector",
			"application/vnd.ollama.image.adapter",
			manifest.MediaTypeImageDraft:
			blobpath, err := manifest.BlobsPath(layer.Digest)
			if err != nil {
				return nil, config, err
			}

			metadata, err := gguf.ReadFileMetadata(blobpath, 1)
```

## Scope note

`manifest/layer.go` defines `application/vnd.ollama.image.model`; `NewLayer` hashes the input bytes and stores them at `BlobsPath(digest)`. `manifest/paths.go` normalizes `sha256:<hex>` to `sha256-<hex>` and builds `<Models>/blobs/<digest>`. `envconfig.Models()` honors `OLLAMA_MODELS`, otherwise returns `$HOME/.ollama/models`. The reader validates GGUF magic and reads GGUF metadata; its metadata path also checks tensor descriptor ranges, not tensor payload values. This grounds header/metadata inspection of the pinned code path, not a claim that an arbitrary filename/media type guarantees valid GGUF bytes. The FAQ separately documents `/usr/share/ollama/.ollama/models` for the Linux standard installer, so do not state `~/.ollama` as a universal default.
