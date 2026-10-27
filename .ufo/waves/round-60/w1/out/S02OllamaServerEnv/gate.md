# Gate — S520 (Ollama FAQ: server bind address and model store)

Access date: **2026-10-27** (UTC). Read-only opens; nothing fetched from a credentialed path.

## Opened sources

1. `https://docs.ollama.com/faq` (reader resolved to the markdown alternate `https://docs.ollama.com/faq.md`),
   saved sha256 `799c4f0830f93fe8a466e5953e75969770357ad590f98cf6684796bc3c6123eb`.
2. `https://raw.githubusercontent.com/ollama/ollama/v0.40.11/docs/faq.mdx` — the repository file at the
   installed release tag, 413 lines, sha256 `e3630684676a21219abc7cb6c17db53993412c194ba9c108c8dbae2f30318e0c`
   (git blob `9e42f77d03419a493f29d6f27e58a16f1e16c248`, listing via
   `https://api.github.com/repos/ollama/ollama/contents/docs?ref=v0.40.11`).

Path discrepancy, recorded rather than smoothed over: the item names `docs/faq.md`; at tag `v0.40.11` the
file is `docs/faq.mdx` and `docs/faq.md` returns HTTP 404 at
`https://raw.githubusercontent.com/ollama/ollama/v0.40.11/docs/faq.md`. Both openable locations were read,
and neither shows drift on the quoted sentences (tag line 185 / live line 186; tag line 241 / live line 242),
so the row cites the live URL and anchors to the tag.

## Located quotes (each ≤25 words)

Q1 — section **"How can I expose Ollama on my network?"**, tag `docs/faq.mdx` line 185, live `faq.md` line 186:

> Ollama binds 127.0.0.1 port 11434 by default. Change the bind address with the `OLLAMA_HOST` environment variable.

(16 words.)

Q2 — section **"Where are models stored?"**, subsection **"How do I set them to a different location?"**,
tag line 241, live line 242:

> If a different directory needs to be used, set the environment variable `OLLAMA_MODELS` to the chosen directory.

(18 words.)

Supporting default-path list read in the same section (tag lines 235–237): macOS `~/.ollama/models`,
Linux `/usr/share/ollama/.ollama/models`, Windows `C:\Users\%username%\.ollama\models`.

## Scope, and what the page does not say

Covered: which two environment variables select (a) the bind address — `OLLAMA_HOST` — and (b) the model
store — `OLLAMA_MODELS` — plus the documented defaults they displace.

Not covered by this page, so not claimed: any precedence rule between these variables and a configuration
file (the page shows `~/.ollama/server.json` only for `disable_ollama_cloud`), any statement that the bind
default is enforced when `OLLAMA_HOST` is unset in a systemd unit, route/health semantics, GPU placement.
A lane sentence asserting precedence or systemd enforcement cannot cite S520 for it.

## Tier reasoning (scoped, not global)

`docs` / **A** — first-party vendor documentation, and the anchor is the vendor's own repository file at the
exact release tag `v0.40.11` whose binary is the one installed at
`~/.local/opt/ollama-v0.40.11/bin/ollama`. A is claimed only for the scope cell ("which environment
variables select bind address and model store"); the page is undated prose, so it is weak for anything
versioned beyond the tag it was read at, and its recheck is `on-release`.

## Duplicate check (commands and output, run 2026-10-27 in `/home/vgpnk/Projects/shokunin/kama-shokunin`)

```
$ grep -c "docs\.ollama\.com/faq" corpus/SOURCES.md
0
$ grep -c "ollama/ollama/blob/v0.40.11/docs/faq\|raw.githubusercontent.com/ollama/ollama/v0.40.11/docs/faq" corpus/SOURCES.md
0
$ grep -c "OLLAMA_HOST" corpus/SOURCES.md
0
$ grep -c "OLLAMA_MODELS" corpus/SOURCES.md
0
$ grep -o "^| S[0-9]\{3\} " corpus/SOURCES.md | sort -u | tail -4
| S515
| S516
| S517
| S518
$ grep -c "^| S519 " corpus/SOURCES.md
0
```

No row names this URL; no row anywhere in the registry mentions `OLLAMA_HOST` or `OLLAMA_MODELS`, so there is
no within-scope duplicate to refuse. Adjacent but distinct: S009 (`/api/introduction`) states the API base
URL `localhost:11434` as a route root and names no configuration variable — it is the consumer side, not the
server-selection side, and S520 does not supersede it. Highest id in use is S518; S519 is free; the seated id
S520 was used as directed.
