Round 89: `tools/kama-probe.sh` decides whether an autoload router entry that only looks
`unloaded` can actually load — an absolute `--model`/`-m`, `--mmproj`/`-mm` or `--model-draft`/`-md` path
missing from the local filesystem is `router-model-missing`, and a GGUF header the loader rejects is
`router-model-invalid` (`tools/round89-unloadable-cells.py`, oracle = the router's own answer to a real
completion). `tools/round89-signature-rows.py` binds the router error-signature rows to captured b12177
wire answers. Header checks only: no non-regular file is opened and no tensor data is read, so a corrupt
payload behind an intact header still grades `MODEL_OK`; the operator's router stays read-only.
